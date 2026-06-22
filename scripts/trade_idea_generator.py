#!/usr/bin/env python3
"""Generate portfolio/watchlist trade ideas and optionally send them to Telegram.

The generator uses repository context as the source of truth:
- context/portfolio-details.md for holdings and open short-premium positions
- context/watchlist.md for scored candidates

Live quotes are optional and require FMP_API_KEY. Telegram delivery requires
TELEGRAM_BOT_TOKEN plus TELEGRAM_CHAT_ID, TELEGRAM_CHANNEL_ID, or TELEGRAM_CHANNEL.
If no chat id is configured, the script attempts to discover the latest bot chat
from Telegram updates.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


WORKSPACE = Path(__file__).resolve().parents[1]
CONTEXT_DIR = WORKSPACE / "context"
OUTPUTS_DIR = WORKSPACE / "outputs"
PORTFOLIO_PATH = CONTEXT_DIR / "portfolio-details.md"
WATCHLIST_PATH = CONTEXT_DIR / "watchlist.md"
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"
TELEGRAM_BASE_URL = "https://api.telegram.org"


@dataclass(frozen=True)
class Position:
    symbol: str
    quantity: float
    current_price: float | None
    market_value: float | None
    pnl_pct: float | None
    day_change_pct: float | None
    weight_pct: float | None


@dataclass(frozen=True)
class OptionPosition:
    ticker: str
    strike: float
    option_type: str
    expiration: str
    credit: float
    current: float
    contracts: int


@dataclass(frozen=True)
class WatchlistItem:
    ticker: str
    score: float | None
    grade: str | None
    company: str
    status: str


@dataclass(frozen=True)
class TradeIdea:
    ticker: str
    action: str
    strategy: str
    rationale: str
    risk: str
    priority: int


def clean_cell(value: str) -> str:
    """Remove markdown decoration from a table cell."""
    return (
        value.replace("**", "")
        .replace("⭐", "")
        .replace("&nbsp;", " ")
        .strip()
    )


def parse_float(value: str) -> float | None:
    """Parse a currency, percent, or plain numeric cell."""
    cleaned = clean_cell(value)
    if cleaned in {"", "-", "--", "—", "N/A"}:
        return None
    match = re.search(r"[-+]?\d[\d,]*\.?\d*", cleaned)
    if not match:
        return None
    try:
        return float(match.group(0).replace(",", ""))
    except ValueError:
        return None


def parse_int(value: str) -> int | None:
    parsed = parse_float(value)
    return int(parsed) if parsed is not None else None


def read_markdown_table(path: Path, header_prefix: str) -> list[list[str]]:
    """Return rows for the markdown table whose header starts with header_prefix."""
    if not path.exists():
        return []
    rows: list[list[str]] = []
    in_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith(header_prefix):
            in_table = True
            continue
        if not in_table:
            continue
        if not stripped.startswith("|"):
            if rows:
                break
            continue
        cells = [clean_cell(cell) for cell in stripped.strip("|").split("|")]
        if cells and all(set(cell.replace("-", "").strip()) == set() for cell in cells):
            continue
        if cells and not cells[0].startswith("---"):
            rows.append(cells)
    return rows


def parse_positions() -> list[Position]:
    rows = read_markdown_table(PORTFOLIO_PATH, "| SYMBOL |")
    positions: list[Position] = []
    for cells in rows:
        if len(cells) < 9 or cells[0].upper() in {"SYMBOL", "TOTALS"}:
            continue
        symbol = cells[0].upper()
        quantity = parse_float(cells[1])
        if not symbol or quantity is None:
            continue
        positions.append(
            Position(
                symbol=symbol,
                quantity=quantity,
                current_price=parse_float(cells[3]),
                market_value=parse_float(cells[4]),
                pnl_pct=parse_float(cells[6].split("(")[-1] if "(" in cells[6] else cells[6]),
                day_change_pct=parse_float(cells[7].split("(")[-1] if "(" in cells[7] else cells[7]),
                weight_pct=parse_float(cells[8]),
            )
        )
    return positions


def parse_option_positions() -> list[OptionPosition]:
    rows = read_markdown_table(PORTFOLIO_PATH, "| Ticker | Strike | Type | Expiration | Credit | Current | Contracts |")
    options: list[OptionPosition] = []
    for cells in rows:
        if len(cells) < 7 or cells[0].lower() == "ticker":
            continue
        strike = parse_float(cells[1])
        credit = parse_float(cells[4])
        current = parse_float(cells[5])
        contracts = parse_int(cells[6])
        if strike is None or credit is None or current is None or contracts is None:
            continue
        options.append(
            OptionPosition(
                ticker=cells[0].upper(),
                strike=strike,
                option_type=cells[2],
                expiration=cells[3],
                credit=credit,
                current=current,
                contracts=contracts,
            )
        )
    return options


def parse_watchlist() -> list[WatchlistItem]:
    rows = read_markdown_table(WATCHLIST_PATH, "| Ticker |")
    watchlist: list[WatchlistItem] = []
    for cells in rows:
        if len(cells) < 5 or cells[0].lower() == "ticker":
            continue
        watchlist.append(
            WatchlistItem(
                ticker=cells[0].upper(),
                score=parse_float(cells[1]),
                grade=clean_cell(cells[2]) or None,
                company=clean_cell(cells[3]),
                status=clean_cell(cells[4]),
            )
        )
    return watchlist


def http_json(url: str, payload: dict[str, Any] | None = None, timeout: int = 15) -> Any:
    data = None
    headers = {"User-Agent": "altamira-trade-idea-generator/1.0"}
    if payload is not None:
        data = urllib.parse.urlencode(payload).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    request = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def chunks(items: list[str], size: int) -> Iterable[list[str]]:
    for index in range(0, len(items), size):
        yield items[index : index + size]


def fetch_quotes(tickers: list[str], api_key: str | None) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Fetch FMP quotes when an API key is available."""
    if not api_key:
        return {}, ["FMP_API_KEY not set; using repository context without live quote refresh."]

    quotes: dict[str, dict[str, Any]] = {}
    warnings: list[str] = []
    clean_tickers = sorted({ticker for ticker in tickers if ticker and not ticker.endswith("X")})
    for chunk in chunks(clean_tickers, 50):
        symbol_path = ",".join(urllib.parse.quote(ticker, safe="^") for ticker in chunk)
        url = f"{FMP_BASE_URL}/quote/{symbol_path}?apikey={urllib.parse.quote(api_key)}"
        try:
            data = http_json(url)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            warnings.append(f"Quote fetch failed for {', '.join(chunk[:5])}: {exc}")
            continue
        if isinstance(data, list):
            for item in data:
                symbol = str(item.get("symbol") or "").upper()
                if symbol:
                    quotes[symbol] = item

    return quotes, warnings


def classify_vix(vix_level: float | None) -> tuple[str, str]:
    if vix_level is None:
        return "UNKNOWN", "Use base sizing until VIX is refreshed."
    if vix_level < 15:
        return "LOW", "Premium is thinner; use 75% of normal size and prioritize quality."
    if vix_level < 25:
        return "NORMAL", "Premium selling conditions are acceptable at normal size."
    if vix_level < 35:
        return "ELEVATED", "Prefer defined-risk spreads and 50% of normal size."
    return "CRISIS", "Sit mostly in cash; defined-risk only at 25% of normal size."


def quote_price(symbol: str, position: Position | None, quotes: dict[str, dict[str, Any]]) -> float | None:
    quote = quotes.get(symbol) or {}
    return parse_float(str(quote.get("price"))) or (position.current_price if position else None)


def generate_option_management_ideas(options: list[OptionPosition]) -> list[TradeIdea]:
    ideas: list[TradeIdea] = []
    for option in options:
        stop_level = option.credit * 2
        profit_level = option.credit * 0.5
        if option.current >= stop_level:
            ideas.append(
                TradeIdea(
                    ticker=option.ticker,
                    action="Manage immediately",
                    strategy=f"Review/roll {option.expiration} {option.strike:g}{option.option_type[0].upper()}",
                    rationale=(
                        f"Current option value ${option.current:.2f} is above the 2x credit stop "
                        f"(${stop_level:.2f}) on a ${option.credit:.2f} credit."
                    ),
                    risk="Do not add size before deciding whether to close, roll, or accept assignment risk.",
                    priority=100,
                )
            )
        elif option.current <= profit_level:
            ideas.append(
                TradeIdea(
                    ticker=option.ticker,
                    action="Take profits",
                    strategy=f"Buy to close {option.expiration} {option.strike:g}{option.option_type[0].upper()}",
                    rationale=(
                        f"Current option value ${option.current:.2f} is at or below the 50% profit target "
                        f"(${profit_level:.2f}) on a ${option.credit:.2f} credit."
                    ),
                    risk="Close winning premium instead of letting gamma/assignment risk rebuild.",
                    priority=95,
                )
            )
    return ideas


def generate_holding_ideas(
    positions: list[Position],
    quotes: dict[str, dict[str, Any]],
    vix_regime: str,
) -> list[TradeIdea]:
    ideas: list[TradeIdea] = []
    for position in positions:
        if position.symbol in {"SPY", "QQQ", "FFOLX"}:
            continue
        quote = quotes.get(position.symbol) or {}
        day_change = parse_float(str(quote.get("changesPercentage"))) or position.day_change_pct
        near_high = False
        price = quote_price(position.symbol, position, quotes)
        year_high = parse_float(str(quote.get("yearHigh")))
        if price and year_high:
            near_high = price >= year_high * 0.92
        overweight = (position.weight_pct or 0) >= 10
        large_gain = (position.pnl_pct or 0) >= 60
        has_lot = position.quantity >= 100

        if has_lot and (overweight or large_gain or near_high):
            urgency = 85 if overweight else 75
            ideas.append(
                TradeIdea(
                    ticker=position.symbol,
                    action="Sell covered call overlay",
                    strategy="30-45 DTE covered call, target 0.20-0.30 delta",
                    rationale=(
                        f"Holding is {position.weight_pct or 0:.1f}% of portfolio with "
                        f"{position.pnl_pct or 0:+.1f}% unrealized P&L"
                        + (f" and {day_change:+.1f}% latest day change" if day_change is not None else "")
                        + "."
                    ),
                    risk=(
                        "Cap only shares you are willing to trim; avoid selling calls through an earnings date."
                    ),
                    priority=urgency,
                )
            )
        elif overweight:
            ideas.append(
                TradeIdea(
                    ticker=position.symbol,
                    action="Trim or hedge concentration",
                    strategy="Reduce weight toward single-position risk limit",
                    rationale=f"Holding weight is {position.weight_pct or 0:.1f}%, above a 10% concentration watch level.",
                    risk="Use limit orders; preserve core exposure if tax or thesis considerations dominate.",
                    priority=80,
                )
            )

    if vix_regime in {"ELEVATED", "CRISIS"}:
        spy = next((position for position in positions if position.symbol == "SPY"), None)
        if spy and spy.quantity >= 100:
            ideas.append(
                TradeIdea(
                    ticker="SPY",
                    action="Hedge beta",
                    strategy="Defined-risk put spread or collar against SPY shares",
                    rationale=f"VIX regime is {vix_regime}; portfolio has {spy.weight_pct or 0:.1f}% SPY exposure.",
                    risk="Keep hedge debit small and avoid over-hedging long-term core exposure.",
                    priority=82,
                )
            )
    return ideas


def generate_watchlist_ideas(
    watchlist: list[WatchlistItem],
    quotes: dict[str, dict[str, Any]],
    vix_regime: str,
) -> list[TradeIdea]:
    ideas: list[TradeIdea] = []
    for item in watchlist:
        if item.score is None:
            continue
        is_top = "Top Candidate" in item.status or item.score >= 60
        if not is_top:
            continue
        quote = quotes.get(item.ticker) or {}
        day_change = parse_float(str(quote.get("changesPercentage")))
        strategy = "Cash-secured put, 30-45 DTE, target 0.20-0.25 delta"
        risk = "Only sell puts at a strike you would accept as a long-term entry; avoid earnings windows."
        if vix_regime in {"ELEVATED", "CRISIS"}:
            strategy = "Bull put spread, 30-45 DTE, target 0.20-0.25 short delta"
            risk = "Use defined risk and reduced size because volatility regime is elevated."
        rationale = f"Watchlist score {item.score:.1f} ({item.grade or 'N/A'}), status: {item.status}."
        if day_change is not None:
            rationale += f" Latest quote move: {day_change:+.1f}%."
        ideas.append(
            TradeIdea(
                ticker=item.ticker,
                action="Put-selling entry candidate",
                strategy=strategy,
                rationale=rationale,
                risk=risk,
                priority=70 + min(int(item.score - 55), 15),
            )
        )
    return ideas


def dedupe_and_rank(ideas: list[TradeIdea], limit: int) -> list[TradeIdea]:
    seen: set[tuple[str, str]] = set()
    ranked: list[TradeIdea] = []
    for idea in sorted(ideas, key=lambda item: item.priority, reverse=True):
        key = (idea.ticker, idea.action)
        if key in seen:
            continue
        seen.add(key)
        ranked.append(idea)
        if len(ranked) >= limit:
            break
    return ranked


def format_markdown_report(
    ideas: list[TradeIdea],
    positions: list[Position],
    options: list[OptionPosition],
    watchlist: list[WatchlistItem],
    warnings: list[str],
    vix_level: float | None,
    vix_regime: str,
    vix_guidance: str,
    generated_at: datetime,
) -> str:
    date_str = generated_at.strftime("%Y-%m-%d %H:%M UTC")
    top_holdings = sorted(positions, key=lambda item: item.weight_pct or 0, reverse=True)[:8]
    top_watchlist = sorted(
        [item for item in watchlist if item.score is not None],
        key=lambda item: item.score or 0,
        reverse=True,
    )[:8]

    lines = [
        "# Trade Idea Generator",
        "",
        f"**Generated:** {date_str}",
        f"**Inputs:** `{PORTFOLIO_PATH.relative_to(WORKSPACE)}` and `{WATCHLIST_PATH.relative_to(WORKSPACE)}`",
        "",
        "## Executive Summary",
        "",
        f"- **VIX regime:** {vix_regime}"
        + (f" ({vix_level:.2f})" if vix_level is not None else " (live VIX unavailable)"),
        f"- **Sizing guidance:** {vix_guidance}",
        f"- **Ideas generated:** {len(ideas)}",
        "",
        "## Top Trade Ideas",
        "",
    ]

    if not ideas:
        lines.append("No high-priority trade ideas were generated from the current context.")
    else:
        for idx, idea in enumerate(ideas, start=1):
            lines.extend(
                [
                    f"### {idx}. {idea.ticker} - {idea.action}",
                    "",
                    f"- **Strategy:** {idea.strategy}",
                    f"- **Rationale:** {idea.rationale}",
                    f"- **Risk / guardrail:** {idea.risk}",
                    "",
                ]
            )

    lines.extend(
        [
            "## Current Portfolio Concentration",
            "",
            "| Ticker | Weight | P&L % | Day Chg % | Quantity |",
            "|--------|--------|-------|-----------|----------|",
        ]
    )
    for position in top_holdings:
        lines.append(
            f"| {position.symbol} | {format_pct(position.weight_pct)} | "
            f"{format_pct(position.pnl_pct, signed=True)} | "
            f"{format_pct(position.day_change_pct, signed=True)} | {position.quantity:g} |"
        )

    lines.extend(
        [
            "",
            "## Open Short-Premium Checks",
            "",
            "| Ticker | Contract | Credit | Current | Status |",
            "|--------|----------|--------|---------|--------|",
        ]
    )
    for option in options:
        status = "Monitor"
        if option.current >= option.credit * 2:
            status = "Stop/roll review"
        elif option.current <= option.credit * 0.5:
            status = "50% profit target"
        lines.append(
            f"| {option.ticker} | {option.expiration} {option.strike:g}{option.option_type[0].upper()} | "
            f"${option.credit:.2f} | ${option.current:.2f} | {status} |"
        )

    lines.extend(
        [
            "",
            "## Top Watchlist Candidates",
            "",
            "| Ticker | Score | Grade | Status | Company |",
            "|--------|-------|-------|--------|---------|",
        ]
    )
    for item in top_watchlist:
        lines.append(
            f"| {item.ticker} | {item.score:.1f} | {item.grade or 'N/A'} | {item.status} | {item.company} |"
        )

    if warnings:
        lines.extend(["", "## Data Notes", ""])
        lines.extend(f"- {warning}" for warning in warnings)

    lines.extend(
        [
            "",
            "## Disclaimer",
            "",
            (
                "This is an internal idea-generation report, not financial advice. "
                "Validate prices, option chains, liquidity, earnings dates, tax impact, and portfolio risk "
                "before placing any trade."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def format_pct(value: float | None, signed: bool = False) -> str:
    if value is None:
        return "N/A"
    sign = "+" if signed and value > 0 else ""
    return f"{sign}{value:.1f}%"


def telegram_message(
    ideas: list[TradeIdea],
    vix_level: float | None,
    vix_regime: str,
    vix_guidance: str,
    output_path: Path,
) -> str:
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        f"Altamira Trade Ideas - {date_str}",
        "",
        "Internal research only; validate chain/liquidity before trading.",
        "",
        f"VIX: {vix_regime}" + (f" ({vix_level:.2f})" if vix_level is not None else ""),
        f"Sizing: {vix_guidance}",
        "",
        "Top ideas:",
    ]
    for idx, idea in enumerate(ideas[:5], start=1):
        lines.append(f"{idx}. {idea.ticker}: {idea.action}")
        lines.append(f"   {idea.strategy}")
        lines.append(f"   Why: {idea.rationale}")
        lines.append(f"   Guardrail: {idea.risk}")
    lines.extend(["", f"Report: {output_path.relative_to(WORKSPACE)}"])
    return "\n".join(lines)


def discover_telegram_chat_id(bot_token: str) -> str | None:
    url = f"{TELEGRAM_BASE_URL}/bot{urllib.parse.quote(bot_token)}/getUpdates?limit=20"
    try:
        data = http_json(url, timeout=12)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None
    if not data.get("ok"):
        return None
    for update in reversed(data.get("result") or []):
        message = (
            update.get("message")
            or update.get("channel_post")
            or update.get("edited_message")
            or update.get("edited_channel_post")
            or {}
        )
        chat = (
            message.get("chat")
            or (update.get("my_chat_member") or {}).get("chat")
            or (update.get("chat_member") or {}).get("chat")
        )
        if chat and chat.get("id") is not None:
            return str(chat["id"])
    return None


def send_telegram_message(message: str, chat_id: str | None, bot_token: str | None) -> tuple[bool, str]:
    if not bot_token:
        return False, "TELEGRAM_BOT_TOKEN not set."
    resolved_chat_id = chat_id or discover_telegram_chat_id(bot_token)
    if not resolved_chat_id:
        return (
            False,
            "Telegram chat id not configured and no prior bot chats were discoverable via getUpdates.",
        )
    url = f"{TELEGRAM_BASE_URL}/bot{urllib.parse.quote(bot_token)}/sendMessage"
    payload = {
        "chat_id": resolved_chat_id,
        "text": message[:3900],
        "disable_web_page_preview": "true",
    }
    try:
        data = http_json(url, payload=payload, timeout=15)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return False, f"Telegram send failed: {exc}"
    if not data.get("ok"):
        return False, f"Telegram send failed: {data}"
    return True, f"Telegram message sent to chat {resolved_chat_id}."


def resolve_chat_id(args: argparse.Namespace) -> str | None:
    return (
        args.telegram_chat_id
        or os.environ.get("TELEGRAM_CHAT_ID")
        or os.environ.get("TELEGRAM_CHANNEL_ID")
        or os.environ.get("TELEGRAM_CHANNEL")
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate Altamira portfolio/watchlist trade ideas.")
    parser.add_argument("--limit", type=int, default=8, help="Maximum ideas to include in the report.")
    parser.add_argument("--output-date", default=None, help="Override output date slug (YYYY-MM-DD).")
    parser.add_argument("--no-telegram", action="store_true", help="Generate report without Telegram delivery.")
    parser.add_argument("--telegram-required", action="store_true", help="Exit non-zero if Telegram delivery fails.")
    parser.add_argument("--telegram-chat-id", default=None, help="Telegram chat/channel id or @channel username.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    generated_at = datetime.now(timezone.utc)
    output_date = args.output_date or generated_at.strftime("%Y-%m-%d")

    positions = parse_positions()
    options = parse_option_positions()
    watchlist = parse_watchlist()
    universe = sorted({p.symbol for p in positions} | {w.ticker for w in watchlist} | {"^VIX"})
    quotes, warnings = fetch_quotes(universe, os.environ.get("FMP_API_KEY"))
    vix_quote = quotes.get("^VIX") or quotes.get("VIX") or {}
    vix_level = parse_float(str(vix_quote.get("price")))
    vix_regime, vix_guidance = classify_vix(vix_level)

    all_ideas = (
        generate_option_management_ideas(options)
        + generate_holding_ideas(positions, quotes, vix_regime)
        + generate_watchlist_ideas(watchlist, quotes, vix_regime)
    )
    ideas = dedupe_and_rank(all_ideas, max(args.limit, 1))

    OUTPUTS_DIR.mkdir(exist_ok=True)
    output_path = OUTPUTS_DIR / f"trade-idea-generator-{output_date}.md"
    report = format_markdown_report(
        ideas=ideas,
        positions=positions,
        options=options,
        watchlist=watchlist,
        warnings=warnings,
        vix_level=vix_level,
        vix_regime=vix_regime,
        vix_guidance=vix_guidance,
        generated_at=generated_at,
    )
    output_path.write_text(report, encoding="utf-8")

    print(f"Wrote {output_path.relative_to(WORKSPACE)}")
    print(f"Generated {len(ideas)} trade ideas.")

    if args.no_telegram:
        print("Telegram delivery skipped by --no-telegram.")
        return 0

    message = telegram_message(ideas, vix_level, vix_regime, vix_guidance, output_path)
    sent, status = send_telegram_message(
        message=message,
        chat_id=resolve_chat_id(args),
        bot_token=os.environ.get("TELEGRAM_BOT_TOKEN"),
    )
    print(status)
    if args.telegram_required and not sent:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
