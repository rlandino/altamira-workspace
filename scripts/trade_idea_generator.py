#!/usr/bin/env python3
"""Generate portfolio/watchlist trade ideas and optionally send to Telegram.

The generator is intentionally lightweight: it reads the repository's static
portfolio and watchlist context, enriches it with FMP quote/earnings data when
available, writes a markdown report, and sends a concise summary to Telegram.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_PATH = WORKSPACE_ROOT / "context" / "portfolio-details.md"
WATCHLIST_PATH = WORKSPACE_ROOT / "context" / "watchlist.md"
OUTPUTS_DIR = WORKSPACE_ROOT / "outputs"
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"
MAX_TELEGRAM_CHARS = 3900


@dataclass
class Position:
    symbol: str
    quantity: float
    average_price: float
    current_price: float
    market_value: float
    pnl_pct: float
    day_change_pct: float
    weight_pct: float


@dataclass
class OptionPosition:
    ticker: str
    strike: float
    option_type: str
    expiration: str
    credit: float
    current: float
    contracts: int


@dataclass
class WatchlistEntry:
    ticker: str
    score: float | None
    grade: str
    company: str
    status: str


@dataclass
class TradeIdea:
    priority: int
    ticker: str
    strategy: str
    action: str
    rationale: str
    risk: str
    reference: str


def clean_number(value: str) -> float:
    """Convert markdown money/percent strings to float."""
    cleaned = (
        value.replace("$", "")
        .replace(",", "")
        .replace("%", "")
        .replace("+", "")
        .strip()
    )
    if cleaned in {"", "-", "—"}:
        return 0.0
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    return float(match.group(0)) if match else 0.0


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_portfolio(path: Path) -> list[Position]:
    positions: list[Position] = []
    in_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| SYMBOL |"):
            in_table = True
            continue
        if in_table and (not line.startswith("|") or line.startswith("|---")):
            continue
        if in_table and line.startswith("|"):
            cells = split_markdown_row(line)
            if len(cells) < 9 or cells[0].lower().startswith("totals"):
                continue
            symbol = cells[0].strip()
            if not re.fullmatch(r"[A-Z.]+", symbol):
                continue
            positions.append(
                Position(
                    symbol=symbol,
                    quantity=clean_number(cells[1]),
                    average_price=clean_number(cells[2]),
                    current_price=clean_number(cells[3]),
                    market_value=clean_number(cells[4]),
                    pnl_pct=clean_number(cells[6].split("(")[-1]),
                    day_change_pct=clean_number(cells[7].split("(")[-1]),
                    weight_pct=clean_number(cells[8]),
                )
            )
            continue
        if in_table and line.startswith("**Totals:**"):
            break
    return positions


def parse_options(path: Path) -> list[OptionPosition]:
    options: list[OptionPosition] = []
    in_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| Ticker | Strike | Type |"):
            in_table = True
            continue
        if in_table and (not line.startswith("|") or line.startswith("|---")):
            continue
        if in_table and line.startswith("|"):
            cells = split_markdown_row(line)
            if len(cells) < 7:
                continue
            options.append(
                OptionPosition(
                    ticker=cells[0],
                    strike=clean_number(cells[1]),
                    option_type=cells[2],
                    expiration=cells[3],
                    credit=clean_number(cells[4]),
                    current=clean_number(cells[5]),
                    contracts=int(clean_number(cells[6])),
                )
            )
            continue
        if in_table and line.startswith("**Last updated:**"):
            break
    return options


def parse_watchlist(path: Path) -> list[WatchlistEntry]:
    watchlist: list[WatchlistEntry] = []
    in_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| Ticker | Score | Grade |"):
            in_table = True
            continue
        if in_table and (not line.startswith("|") or line.startswith("|---")):
            continue
        if in_table and line.startswith("|"):
            cells = split_markdown_row(line)
            if len(cells) < 5:
                continue
            score = None if cells[1] in {"—", "-"} else clean_number(cells[1])
            watchlist.append(
                WatchlistEntry(
                    ticker=cells[0],
                    score=score,
                    grade=cells[2].replace("*", ""),
                    company=cells[3],
                    status=cells[4],
                )
            )
            continue
        if in_table and line.startswith("---"):
            break
    return watchlist


def extract_fmp_key() -> str | None:
    """Resolve FMP key from env, then existing repo workflow/command config."""
    if os.environ.get("FMP_API_KEY"):
        return os.environ["FMP_API_KEY"]

    candidates = [
        WORKSPACE_ROOT / "outputs" / "csp-daily-scan-fixed.json",
        WORKSPACE_ROOT / "outputs" / "n8n-workflow-csp-daily-scan.json",
        WORKSPACE_ROOT / ".claude" / "commands" / "options-scan.md",
    ]
    patterns = [
        r'"name":\s*"apikey",\s*"value":\s*"=?([A-Za-z0-9_-]{20,})"',
        r"apikey=([A-Za-z0-9_-]{20,})",
        r"FMP API.*?key:\s*`([A-Za-z0-9_-]{20,})`",
    ]
    for candidate in candidates:
        if not candidate.exists():
            continue
        text = candidate.read_text(encoding="utf-8")
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1)
    return None


def extract_telegram_chat_id() -> str | None:
    if os.environ.get("TELEGRAM_CHAT_ID"):
        return os.environ["TELEGRAM_CHAT_ID"]
    fixed_workflow = WORKSPACE_ROOT / "outputs" / "csp-daily-scan-fixed.json"
    if fixed_workflow.exists():
        match = re.search(
            r'"chatId":\s*"=?(-?\d+|@[A-Za-z0-9_]+)"',
            fixed_workflow.read_text(encoding="utf-8"),
        )
        if match:
            return match.group(1)
    return None


def http_json(url: str, timeout: int = 20) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": "AltamiraTradeIdeaGenerator/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def fetch_quotes(symbols: list[str], api_key: str | None) -> dict[str, dict[str, Any]]:
    if not api_key or not symbols:
        return {}
    quotes: dict[str, dict[str, Any]] = {}
    for index in range(0, len(symbols), 50):
        batch = symbols[index : index + 50]
        encoded = urllib.parse.quote(",".join(batch), safe=",^")
        url = f"{FMP_BASE_URL}/quote/{encoded}?apikey={urllib.parse.quote(api_key)}"
        try:
            data = http_json(url)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            print(f"Warning: quote fetch failed for {','.join(batch)}: {exc}", file=sys.stderr)
            continue
        if isinstance(data, list):
            for item in data:
                symbol = str(item.get("symbol", "")).replace("^", "")
                if symbol:
                    quotes[symbol] = item
    return quotes


def fetch_earnings(symbols: list[str], api_key: str | None, today: date) -> dict[str, str]:
    if not api_key:
        return {}
    end = today + timedelta(days=45)
    url = (
        f"{FMP_BASE_URL}/earning_calendar?"
        f"from={today.isoformat()}&to={end.isoformat()}&apikey={urllib.parse.quote(api_key)}"
    )
    try:
        data = http_json(url)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"Warning: earnings fetch failed: {exc}", file=sys.stderr)
        return {}
    wanted = set(symbols)
    earnings: dict[str, str] = {}
    if isinstance(data, list):
        for item in data:
            symbol = item.get("symbol")
            if symbol in wanted and symbol not in earnings:
                earnings[symbol] = str(item.get("date", ""))
    return earnings


def next_target_expiration(today: date) -> date:
    candidate = today + timedelta(days=38)
    while candidate.weekday() != 4:
        candidate += timedelta(days=1)
    return candidate


def round_strike(value: float) -> float:
    if value >= 500:
        increment = 10
    elif value >= 100:
        increment = 5
    else:
        increment = 2.5
    return round(value / increment) * increment


def quote_price(ticker: str, quotes: dict[str, dict[str, Any]], fallback: float = 0.0) -> float:
    quote = quotes.get(ticker, {})
    return float(quote.get("price") or fallback or 0.0)


def build_option_management_ideas(options: list[OptionPosition]) -> list[TradeIdea]:
    ideas: list[TradeIdea] = []
    for option in options:
        if option.credit <= 0:
            continue
        ratio = option.current / option.credit
        ref = f"{option.contracts}x {option.ticker} {option.strike:g}{option.option_type[0].upper()} {option.expiration}"
        if ratio <= 0.50:
            ideas.append(
                TradeIdea(
                    priority=95,
                    ticker=option.ticker,
                    strategy="Manage existing short put",
                    action=f"Consider closing {ref}; current mark is {ratio:.0%} of original credit.",
                    rationale=(
                        f"Credit ${option.credit:.2f}, current ${option.current:.2f}. "
                        "This meets the 50% profit-taking rule used in the workspace."
                    ),
                    risk="Re-open only if the new trade still clears earnings, liquidity, and allocation checks.",
                    reference=ref,
                )
            )
        elif ratio >= 2.00:
            ideas.append(
                TradeIdea(
                    priority=100,
                    ticker=option.ticker,
                    strategy="Risk-control existing short put",
                    action=f"Review close/roll for {ref}; current mark is {ratio:.0%} of original credit.",
                    rationale=(
                        f"Credit ${option.credit:.2f}, current ${option.current:.2f}. "
                        "This breaches the 200% stop-loss rule in the workspace."
                    ),
                    risk="Confirm assignment willingness and avoid increasing notional in the same ticker.",
                    reference=ref,
                )
            )
    return ideas


def build_watchlist_entry_ideas(
    watchlist: list[WatchlistEntry],
    positions: dict[str, Position],
    quotes: dict[str, dict[str, Any]],
    earnings: dict[str, str],
    expiration: date,
) -> list[TradeIdea]:
    ideas: list[TradeIdea] = []
    for entry in watchlist:
        if entry.score is None or entry.score < 58:
            continue
        ticker = entry.ticker
        quote = quotes.get(ticker, {})
        price = quote_price(ticker, quotes)
        if price <= 0:
            continue
        score = entry.score
        price_avg_50 = float(quote.get("priceAvg50") or 0)
        price_avg_200 = float(quote.get("priceAvg200") or 0)
        change_pct = float(quote.get("changesPercentage") or 0)
        if price_avg_50 and price >= price_avg_50:
            score += 5
        elif price_avg_50:
            score -= 5
        if price_avg_200 and price >= price_avg_200:
            score += 3
        if change_pct <= -2:
            score += 3
        if change_pct >= 5:
            score -= 5
        if ticker in earnings:
            score -= 12
        if ticker in positions and positions[ticker].weight_pct >= 5:
            score -= 8
        if score < 58:
            continue

        strike = round_strike(price * 0.92)
        strategy = "Cash-secured put / bull put spread"
        action = (
            f"Watch {ticker} around ${price:.2f}; target a {expiration.isoformat()} "
            f"{strike:g}P or defined-risk put spread at 0.20-0.30 delta."
        )
        if ticker in earnings:
            action = f"Defer new premium sale until after earnings on {earnings[ticker]}."
        ideas.append(
            TradeIdea(
                priority=int(score),
                ticker=ticker,
                strategy=strategy,
                action=action,
                rationale=(
                    f"{entry.company} is a {entry.grade} watchlist candidate "
                    f"(score {entry.score:.1f}, status: {entry.status}). "
                    f"Price vs 50D/200D: ${price_avg_50:.2f}/${price_avg_200:.2f}; "
                    f"day change {change_pct:.1f}%."
                ),
                risk=(
                    "Keep risk defined if VIX is elevated or if sector exposure is already high; "
                    "do not hold short premium through earnings."
                ),
                reference=f"watchlist score {entry.score:.1f}",
            )
        )
    return ideas


def build_portfolio_overlay_ideas(
    positions: list[Position],
    quotes: dict[str, dict[str, Any]],
    expiration: date,
) -> list[TradeIdea]:
    ideas: list[TradeIdea] = []
    for position in positions:
        if position.quantity < 100 or position.weight_pct < 4.0:
            continue
        price = quote_price(position.symbol, quotes, position.current_price)
        if price <= 0:
            continue
        priority = int(min(92, 50 + position.weight_pct * 2 + max(position.pnl_pct, 0) / 10))
        if position.weight_pct >= 10:
            strike = round_strike(price * 1.08)
            action = (
                f"Consider a covered-call overwrite or staged trim: "
                f"{expiration.isoformat()} {strike:g}C as an upside-cap candidate."
            )
            rationale = (
                f"{position.symbol} is {position.weight_pct:.1f}% of portfolio with "
                f"{position.pnl_pct:.1f}% unrealized gain."
            )
        else:
            strike = round_strike(price * 1.10)
            action = (
                f"Optional covered-call candidate if premium is attractive: "
                f"{expiration.isoformat()} {strike:g}C."
            )
            rationale = (
                f"{position.symbol} has at least 100 shares and a {position.weight_pct:.1f}% weight; "
                f"covered calls can add income without adding downside notional."
            )
        ideas.append(
            TradeIdea(
                priority=priority,
                ticker=position.symbol,
                strategy="Covered call / rebalance overlay",
                action=action,
                rationale=rationale,
                risk="Only overwrite shares you are willing to have called away; avoid caps before major catalysts.",
                reference=f"{position.quantity:g} shares, {position.weight_pct:.1f}% weight",
            )
        )
    return ideas


def render_report(
    today: date,
    positions: list[Position],
    watchlist: list[WatchlistEntry],
    ideas: list[TradeIdea],
    quotes: dict[str, dict[str, Any]],
    earnings: dict[str, str],
) -> str:
    portfolio_value = sum(position.market_value for position in positions)
    top_positions = sorted(positions, key=lambda pos: pos.weight_pct, reverse=True)[:5]
    top_watchlist = [entry for entry in watchlist if entry.score is not None][:8]
    quote_status = "live FMP quotes fetched" if quotes else "live quotes unavailable; using context snapshot"

    lines = [
        f"# Trade Idea Generator - {today.isoformat()}",
        "",
        "> Informational analysis only, not financial advice. Confirm live prices, option chains, liquidity, and account risk before trading.",
        "",
        "## Inputs",
        "",
        f"- Portfolio positions: {len(positions)} from `context/portfolio-details.md`",
        f"- Watchlist names: {len(watchlist)} from `context/watchlist.md`",
        f"- Data status: {quote_status}",
        f"- Portfolio market value in context: ${portfolio_value:,.0f}",
        "",
        "## Top Portfolio Weights",
        "",
        "| Ticker | Weight | P&L % | Market Value |",
        "|--------|--------|-------|--------------|",
    ]
    for position in top_positions:
        lines.append(
            f"| {position.symbol} | {position.weight_pct:.1f}% | "
            f"{position.pnl_pct:.1f}% | ${position.market_value:,.0f} |"
        )

    lines.extend(
        [
            "",
            "## Highest-Ranked Ideas",
            "",
            "| Rank | Ticker | Strategy | Action | Rationale | Risk |",
            "|------|--------|----------|--------|-----------|------|",
        ]
    )
    for rank, idea in enumerate(ideas[:10], start=1):
        lines.append(
            f"| {rank} | {idea.ticker} | {idea.strategy} | {idea.action} | "
            f"{idea.rationale} | {idea.risk} |"
        )

    if earnings:
        lines.extend(["", "## Earnings Conflicts (Next 45 Days)", "", "| Ticker | Date |", "|--------|------|"])
        for ticker, earnings_date in sorted(earnings.items()):
            lines.append(f"| {ticker} | {earnings_date} |")

    lines.extend(["", "## Watchlist Snapshot", "", "| Ticker | Score | Grade | Status |", "|--------|-------|-------|--------|"])
    for entry in top_watchlist:
        score = f"{entry.score:.1f}" if entry.score is not None else "-"
        lines.append(f"| {entry.ticker} | {score} | {entry.grade} | {entry.status} |")

    lines.extend(
        [
            "",
            "## Execution Checklist",
            "",
            "- Verify bid/ask spreads and open interest before placing any option trade.",
            "- Respect the 5% max position and 25% sector exposure limits from the risk framework.",
            "- Close short premium at 50% profit; stop or roll at 200% of original credit.",
            "- Avoid initiating short premium that overlaps an unplanned earnings event.",
            "",
        ]
    )
    return "\n".join(lines)


def render_telegram(today: date, ideas: list[TradeIdea], quotes: dict[str, dict[str, Any]], report_path: Path) -> str:
    lines = [
        f"Altamira Trade Ideas - {today.isoformat()}",
        "Portfolio + watchlist scan",
        "",
    ]
    for rank, idea in enumerate(ideas[:5], start=1):
        quote = quotes.get(idea.ticker, {})
        price = quote.get("price")
        price_text = f" @ ${float(price):.2f}" if price else ""
        lines.extend(
            [
                f"{rank}. {idea.ticker}{price_text} - {idea.strategy}",
                f"   Action: {idea.action}",
                f"   Why: {idea.rationale}",
                f"   Risk: {idea.risk}",
                "",
            ]
        )
    if not ideas:
        lines.append("No qualifying ideas generated from the current context.")
        lines.append("")
    lines.extend(
        [
            f"Report: {report_path.name}",
            "Informational only; verify live option chain/liquidity before trading.",
        ]
    )
    return "\n".join(lines)


def send_telegram(message: str, token: str, chat_id: str) -> dict[str, Any]:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    request = urllib.request.Request(url, data=payload, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def chunk_message(message: str) -> list[str]:
    if len(message) <= MAX_TELEGRAM_CHARS:
        return [message]
    chunks: list[str] = []
    current: list[str] = []
    length = 0
    for line in message.splitlines():
        projected = length + len(line) + 1
        if current and projected > MAX_TELEGRAM_CHARS:
            chunks.append("\n".join(current))
            current = []
            length = 0
        current.append(line)
        length += len(line) + 1
    if current:
        chunks.append("\n".join(current))
    return chunks


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Altamira portfolio/watchlist trade ideas.")
    parser.add_argument("--dry-run", action="store_true", help="Generate report without sending Telegram.")
    parser.add_argument("--date", help="Override report date (YYYY-MM-DD).")
    parser.add_argument("--out", help="Output report path. Defaults to outputs/trade-ideas-YYYY-MM-DD.md.")
    args = parser.parse_args()

    today = date.fromisoformat(args.date) if args.date else datetime.utcnow().date()
    positions = parse_portfolio(PORTFOLIO_PATH)
    option_positions = parse_options(PORTFOLIO_PATH)
    watchlist = parse_watchlist(WATCHLIST_PATH)
    if not positions:
        raise SystemExit(f"No positions parsed from {PORTFOLIO_PATH}")
    if not watchlist:
        raise SystemExit(f"No watchlist entries parsed from {WATCHLIST_PATH}")

    symbols = sorted({pos.symbol for pos in positions} | {entry.ticker for entry in watchlist} | {"^VIX", "SPY"})
    fmp_key = extract_fmp_key()
    quotes = fetch_quotes(symbols, fmp_key)
    earnings = fetch_earnings(symbols, fmp_key, today)
    expiration = next_target_expiration(today)
    positions_by_symbol = {position.symbol: position for position in positions}

    ideas = []
    ideas.extend(build_option_management_ideas(option_positions))
    ideas.extend(build_watchlist_entry_ideas(watchlist, positions_by_symbol, quotes, earnings, expiration))
    ideas.extend(build_portfolio_overlay_ideas(positions, quotes, expiration))
    ideas.sort(key=lambda idea: idea.priority, reverse=True)

    out_path = Path(args.out) if args.out else OUTPUTS_DIR / f"trade-ideas-{today.isoformat()}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    report = render_report(today, positions, watchlist, ideas, quotes, earnings)
    out_path.write_text(report, encoding="utf-8")

    telegram_message = render_telegram(today, ideas, quotes, out_path)
    print(f"Report written: {out_path.relative_to(WORKSPACE_ROOT)}")
    print(f"Ideas generated: {len(ideas)}")

    if args.dry_run:
        print("Dry run: Telegram send skipped.")
        print("")
        print(telegram_message)
        return 0

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = extract_telegram_chat_id()
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set; cannot send Telegram message.")
    if not chat_id:
        raise SystemExit("TELEGRAM_CHAT_ID is not set and no repo fallback chat ID was found.")

    last_response: dict[str, Any] | None = None
    for chunk in chunk_message(telegram_message):
        last_response = send_telegram(chunk, token, chat_id)
        if not last_response.get("ok"):
            raise SystemExit(f"Telegram send failed: {last_response}")

    result = last_response.get("result", {}) if last_response else {}
    print(
        "Telegram delivery: ok=True "
        f"message_id={result.get('message_id', 'unknown')} "
        f"chat_type={result.get('chat', {}).get('type', 'unknown')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
