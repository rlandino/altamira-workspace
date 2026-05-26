#!/usr/bin/env python3
"""Generate portfolio/watchlist trade ideas and optionally send Telegram alert."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


WORKSPACE = Path(__file__).resolve().parents[1]
DEFAULT_PORTFOLIO = WORKSPACE / "context" / "portfolio-details.md"
DEFAULT_WATCHLIST = WORKSPACE / "context" / "watchlist.md"
DEFAULT_OUTPUTS = WORKSPACE / "outputs"
TELEGRAM_LIMIT = 3900


@dataclass
class Position:
    symbol: str
    quantity: float
    avg_price: float | None
    current: float | None
    market_value: float | None
    cost_basis: float | None
    pnl_pct: float | None
    weight: float | None


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
class WatchlistItem:
    ticker: str
    score: float | None
    grade: str
    company: str
    status: str


@dataclass
class Quote:
    symbol: str
    price: float | None = None
    previous_close: float | None = None
    change_pct: float | None = None
    sma50: float | None = None
    sma200: float | None = None
    high_52w: float | None = None
    low_52w: float | None = None
    source: str = "context"
    error: str | None = None


@dataclass
class Idea:
    ticker: str
    action: str
    priority: str
    score: float
    rationale: str
    trigger: str
    sizing: str
    source: str


def clean_cell(value: str) -> str:
    value = value.strip()
    value = re.sub(r"\*\*", "", value)
    value = value.replace("⭐", "").strip()
    return value


def parse_number(value: str) -> float | None:
    cleaned = clean_cell(value)
    cleaned = cleaned.replace("$", "").replace(",", "").replace("%", "")
    cleaned = cleaned.replace("+", "").strip()
    if not cleaned or cleaned in {"-", "—", "N/A"}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_pnl_pct(value: str) -> float | None:
    match = re.search(r"\(([-+]?\d+(?:\.\d+)?)%\)", value)
    if match:
        return float(match.group(1))
    return None


def parse_markdown_rows(path: Path) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        if re.match(r"^\|\s*-+\s*(\|\s*-+\s*)+\|?$", line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append(cells)
    return rows


def parse_portfolio(path: Path) -> tuple[list[Position], list[OptionPosition]]:
    rows = parse_markdown_rows(path)
    positions: list[Position] = []
    options: list[OptionPosition] = []
    current_table: str | None = None
    headers: list[str] = []

    for cells in rows:
        normalized = [clean_cell(c).upper() for c in cells]
        if "SYMBOL" in normalized and "WEIGHT" in normalized:
            current_table = "positions"
            headers = normalized
            continue
        if "TICKER" in normalized and "STRIKE" in normalized and "CONTRACTS" in normalized:
            current_table = "options"
            headers = normalized
            continue
        if not current_table or not headers:
            continue

        data = {headers[i]: cells[i] for i in range(min(len(headers), len(cells)))}
        if current_table == "positions" and data.get("SYMBOL", "").strip().upper() != "TOTALS:":
            symbol = clean_cell(data.get("SYMBOL", "")).upper()
            if symbol and symbol != "SYMBOL":
                positions.append(
                    Position(
                        symbol=symbol,
                        quantity=parse_number(data.get("QTY", "")) or 0.0,
                        avg_price=parse_number(data.get("AVG. PRICE", "")),
                        current=parse_number(data.get("CURRENT", "")),
                        market_value=parse_number(data.get("MKT VALUE", "")),
                        cost_basis=parse_number(data.get("COST BASIS", "")),
                        pnl_pct=parse_pnl_pct(data.get("P&L ($, %)", "")),
                        weight=parse_number(data.get("WEIGHT", "")),
                    )
                )
        elif current_table == "options":
            ticker = clean_cell(data.get("TICKER", "")).upper()
            strike = parse_number(data.get("STRIKE", ""))
            if ticker and strike is not None:
                options.append(
                    OptionPosition(
                        ticker=ticker,
                        strike=strike,
                        option_type=clean_cell(data.get("TYPE", "")),
                        expiration=clean_cell(data.get("EXPIRATION", "")),
                        credit=parse_number(data.get("CREDIT", "")) or 0.0,
                        current=parse_number(data.get("CURRENT", "")) or 0.0,
                        contracts=int(parse_number(data.get("CONTRACTS", "")) or 0),
                    )
                )
    return positions, options


def parse_watchlist(path: Path) -> list[WatchlistItem]:
    rows = parse_markdown_rows(path)
    items: list[WatchlistItem] = []
    current_table = False
    headers: list[str] = []
    for cells in rows:
        normalized = [clean_cell(c).upper() for c in cells]
        if "TICKER" in normalized and "SCORE" in normalized and "STATUS" in normalized:
            current_table = True
            headers = normalized
            continue
        if not current_table or not headers:
            continue
        data = {headers[i]: cells[i] for i in range(min(len(headers), len(cells)))}
        ticker = clean_cell(data.get("TICKER", "")).upper()
        if ticker and ticker != "TICKER":
            items.append(
                WatchlistItem(
                    ticker=ticker,
                    score=parse_number(data.get("SCORE", "")),
                    grade=clean_cell(data.get("GRADE", "")),
                    company=clean_cell(data.get("COMPANY", "")),
                    status=clean_cell(data.get("STATUS", "")),
                )
            )
    return items


def request_json(url: str, timeout: int = 12) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": "AltamiraTradeIdeaGenerator/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def average(values: list[float]) -> float | None:
    values = [v for v in values if v is not None and not math.isnan(v)]
    if not values:
        return None
    return sum(values) / len(values)


def fetch_yahoo_quote(symbol: str) -> Quote:
    yahoo_symbol = symbol
    if symbol == "BRK.B":
        yahoo_symbol = "BRK-B"
    encoded = urllib.parse.quote(yahoo_symbol, safe="")
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}?range=1y&interval=1d"
    try:
        data = request_json(url)
        result = (data.get("chart", {}).get("result") or [None])[0]
        if not result:
            return Quote(symbol=symbol, error="No Yahoo chart result")
        meta = result.get("meta", {})
        quote = (result.get("indicators", {}).get("quote") or [{}])[0]
        closes = [float(v) for v in quote.get("close", []) if isinstance(v, (int, float))]
        highs = [float(v) for v in quote.get("high", []) if isinstance(v, (int, float))]
        lows = [float(v) for v in quote.get("low", []) if isinstance(v, (int, float))]
        price = meta.get("regularMarketPrice")
        previous_close = meta.get("chartPreviousClose") or meta.get("previousClose")
        if price is None and closes:
            price = closes[-1]
        change_pct = None
        if price is not None and previous_close:
            change_pct = ((float(price) - float(previous_close)) / float(previous_close)) * 100
        return Quote(
            symbol=symbol,
            price=float(price) if price is not None else None,
            previous_close=float(previous_close) if previous_close is not None else None,
            change_pct=change_pct,
            sma50=average(closes[-50:]),
            sma200=average(closes[-200:]),
            high_52w=max(highs) if highs else None,
            low_52w=min(lows) if lows else None,
            source="yahoo",
        )
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError, ValueError) as exc:
        return Quote(symbol=symbol, error=str(exc))


def fetch_quotes(symbols: set[str], positions: list[Position], skip_live: bool) -> dict[str, Quote]:
    position_map = {p.symbol: p for p in positions}
    quotes: dict[str, Quote] = {}
    if not skip_live:
        for symbol in sorted(symbols):
            quotes[symbol] = fetch_yahoo_quote(symbol)
            time.sleep(0.05)
    for symbol in symbols:
        quote = quotes.get(symbol)
        if quote and quote.price is not None:
            continue
        pos = position_map.get(symbol)
        if pos and pos.current is not None:
            quotes[symbol] = Quote(
                symbol=symbol,
                price=pos.current,
                previous_close=None,
                source="context",
                error=quote.error if quote else None,
            )
        elif not quote:
            quotes[symbol] = Quote(symbol=symbol, error="No quote source available")
    return quotes


def fmt_money(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"${value:,.2f}"


def fmt_pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:+.1f}%"


def trend_label(quote: Quote) -> str:
    if quote.price is None:
        return "unknown trend"
    above_50 = quote.sma50 is not None and quote.price >= quote.sma50
    above_200 = quote.sma200 is not None and quote.price >= quote.sma200
    if above_50 and above_200:
        return "above 50/200-day trend"
    if above_50:
        return "above 50-day, below/unknown 200-day"
    if above_200:
        return "below 50-day, above 200-day"
    if quote.sma50 is not None or quote.sma200 is not None:
        return "below key trend"
    return "trend unavailable"


def distance_to_52w_high(quote: Quote) -> float | None:
    if quote.price is None or not quote.high_52w:
        return None
    return (quote.price / quote.high_52w - 1) * 100


def generate_watchlist_ideas(
    watchlist: list[WatchlistItem], positions: list[Position], quotes: dict[str, Quote]
) -> list[Idea]:
    held = {p.symbol for p in positions}
    ideas: list[Idea] = []
    for item in watchlist:
        if item.ticker in held or item.status.lower() in {"avoid", "low priority"}:
            continue
        if item.score is None or item.score < 55:
            continue
        quote = quotes.get(item.ticker, Quote(symbol=item.ticker))
        trend_bonus = 0.0
        if quote.price is not None and quote.sma50 is not None and quote.price >= quote.sma50:
            trend_bonus += 6
        if quote.price is not None and quote.sma200 is not None and quote.price >= quote.sma200:
            trend_bonus += 4
        high_dist = distance_to_52w_high(quote)
        if high_dist is not None and high_dist > -3:
            trend_bonus -= 3
        if high_dist is not None and -15 <= high_dist <= -5:
            trend_bonus += 4

        score = (item.score or 0) + trend_bonus
        action = "Starter buy candidate"
        trigger = "Enter in thirds; prefer pullbacks toward the 20/50-day area."
        if quote.price is not None and quote.sma50 is not None and quote.price < quote.sma50:
            action = "Wait for reclaim"
            trigger = f"Wait for a close back above 50-day near {fmt_money(quote.sma50)}."
        elif high_dist is not None and high_dist > -3:
            action = "Do not chase; sell put/pullback watch"
            trigger = "Use a pullback or defined-risk put spread instead of buying at highs."

        ideas.append(
            Idea(
                ticker=item.ticker,
                action=action,
                priority="High" if score >= 65 else "Medium",
                score=score,
                rationale=(
                    f"{item.company} is a {item.status.lower()} with score {item.score:.1f}; "
                    f"price {fmt_money(quote.price)} is {trend_label(quote)}."
                ),
                trigger=trigger,
                sizing="Starter size 1-2% of portfolio; cap single-name exposure near 5%.",
                source="Watchlist",
            )
        )
    return ideas


def generate_position_ideas(positions: list[Position], quotes: dict[str, Quote]) -> list[Idea]:
    ideas: list[Idea] = []
    for pos in positions:
        if pos.weight is None:
            continue
        quote = quotes.get(pos.symbol, Quote(symbol=pos.symbol, price=pos.current))
        if pos.weight >= 10:
            score = 55 + pos.weight * 2
            if pos.pnl_pct and pos.pnl_pct > 50:
                score += 5
            action = "Trim or overwrite candidate"
            trigger = "Trim into strength or sell conservative covered calls only if willing to reduce."
            if pos.symbol == "SPY":
                action = "Keep as core index ballast"
                trigger = "Add only after portfolio concentration is reduced elsewhere."
            ideas.append(
                Idea(
                    ticker=pos.symbol,
                    action=action,
                    priority="High" if pos.weight >= 12 else "Medium",
                    score=score,
                    rationale=(
                        f"Position is {pos.weight:.1f}% of portfolio with P&L {fmt_pct(pos.pnl_pct)}; "
                        f"latest price {fmt_money(quote.price)} is {trend_label(quote)}."
                    ),
                    trigger=trigger,
                    sizing="Avoid adding; target staged reduction toward a sub-10% weight unless thesis demands otherwise.",
                    source="Portfolio",
                )
            )
        elif pos.pnl_pct is not None and pos.pnl_pct < -10:
            score = 58 + abs(pos.pnl_pct) / 2
            ideas.append(
                Idea(
                    ticker=pos.symbol,
                    action="Review laggard thesis",
                    priority="Medium",
                    score=score,
                    rationale=(
                        f"Position is down {fmt_pct(pos.pnl_pct)} at {pos.weight:.1f}% weight; "
                        f"latest price {fmt_money(quote.price)} is {trend_label(quote)}."
                    ),
                    trigger="Hold only if the original thesis remains intact; otherwise harvest/redeploy.",
                    sizing="No add until trend and thesis improve.",
                    source="Portfolio",
                )
            )
    return ideas


def generate_option_ideas(options: list[OptionPosition], quotes: dict[str, Quote]) -> list[Idea]:
    ideas: list[Idea] = []
    for opt in options:
        quote = quotes.get(opt.ticker, Quote(symbol=opt.ticker))
        price = quote.price
        if price is None:
            continue
        cushion = (price / opt.strike - 1) * 100
        pnl_per_contract = (opt.credit - opt.current) * 100
        if cushion < 0 or opt.current > opt.credit * 1.5:
            ideas.append(
                Idea(
                    ticker=opt.ticker,
                    action=f"Manage challenged {opt.strike:g} {opt.option_type}",
                    priority="High",
                    score=78 + min(12, abs(cushion)),
                    rationale=(
                        f"Underlying {fmt_money(price)} vs strike {fmt_money(opt.strike)} "
                        f"({cushion:+.1f}% cushion); option marks {fmt_money(opt.current)} "
                        f"vs {fmt_money(opt.credit)} credit."
                    ),
                    trigger="Close/roll if thesis is broken, delta remains elevated, or loss breaches plan.",
                    sizing=f"{opt.contracts} contracts; current mark implies {pnl_per_contract:+.0f} dollars per contract before fees.",
                    source="Options",
                )
            )
        elif cushion < 8:
            ideas.append(
                Idea(
                    ticker=opt.ticker,
                    action=f"Monitor short {opt.strike:g} {opt.option_type}",
                    priority="Medium",
                    score=62 + (8 - cushion),
                    rationale=(
                        f"Underlying {fmt_money(price)} is only {cushion:+.1f}% above strike; "
                        f"option marks {fmt_money(opt.current)} vs {fmt_money(opt.credit)} credit."
                    ),
                    trigger="Avoid adding correlated short puts; consider rolling if spot approaches strike.",
                    sizing=f"{opt.contracts} contracts already open.",
                    source="Options",
                )
            )
    return ideas


def build_market_summary(quotes: dict[str, Quote]) -> str:
    spy = quotes.get("SPY")
    qqq = quotes.get("QQQ")
    vix = quotes.get("^VIX")
    parts = []
    if spy:
        parts.append(f"SPY {fmt_money(spy.price)} ({fmt_pct(spy.change_pct)})")
    if qqq:
        parts.append(f"QQQ {fmt_money(qqq.price)} ({fmt_pct(qqq.change_pct)})")
    if vix:
        parts.append(f"VIX {fmt_money(vix.price)} ({fmt_pct(vix.change_pct)})")
    if not parts:
        return "Market data unavailable; using repository context only."
    return "; ".join(parts)


def build_telegram_message(
    run_time: datetime,
    market_summary: str,
    ideas: list[Idea],
    positions: list[Position],
    watchlist: list[WatchlistItem],
    quote_sources: set[str],
) -> str:
    et_time = run_time.astimezone(ZoneInfo("America/New_York"))
    top = ideas[:5]
    lines = [
        f"TRADE IDEAS - {et_time:%Y-%m-%d %I:%M %p ET}",
        f"Market: {market_summary}",
        f"Universe: {len(positions)} holdings + {len(watchlist)} watchlist names",
        "",
        "Top actions:",
    ]
    for idx, idea in enumerate(top, start=1):
        lines.extend(
            [
                f"{idx}. {idea.ticker} - {idea.action} ({idea.priority}, score {idea.score:.0f})",
                f"   Why: {idea.rationale}",
                f"   Trigger: {idea.trigger}",
            ]
        )
    lines.extend(
        [
            "",
            "Portfolio note: existing holdings remain concentrated in SPY, AVGO, GOOGL, and AMAT; keep new single-name adds small until concentration is reduced.",
            f"Data: {', '.join(sorted(quote_sources)) or 'context'} + repository portfolio/watchlist.",
            "For research only; not financial advice. Confirm prices, earnings dates, liquidity, and risk limits before trading.",
        ]
    )
    message = "\n".join(lines)
    if len(message) > TELEGRAM_LIMIT:
        return message[: TELEGRAM_LIMIT - 80] + "\n\n... truncated; see full report in outputs."
    return message


def build_report(
    run_time: datetime,
    output_path: Path,
    market_summary: str,
    ideas: list[Idea],
    positions: list[Position],
    options: list[OptionPosition],
    watchlist: list[WatchlistItem],
    quotes: dict[str, Quote],
    telegram_status: str,
    telegram_message: str,
) -> str:
    et_time = run_time.astimezone(ZoneInfo("America/New_York"))
    top_weights = sorted([p for p in positions if p.weight is not None], key=lambda p: p.weight or 0, reverse=True)[:8]
    top_watchlist = sorted(
        [w for w in watchlist if w.score is not None], key=lambda w: w.score or 0, reverse=True
    )[:10]

    lines = [
        f"# Trade Idea Generator - {run_time:%Y-%m-%d}",
        "",
        f"**Generated:** {et_time:%Y-%m-%d %I:%M %p ET}",
        f"**Portfolio source:** `{DEFAULT_PORTFOLIO.relative_to(WORKSPACE)}`",
        f"**Watchlist source:** `{DEFAULT_WATCHLIST.relative_to(WORKSPACE)}`",
        f"**Telegram delivery:** {telegram_status}",
        "",
        "## Market Snapshot",
        "",
        market_summary,
        "",
        "## Top Trade Ideas",
        "",
    ]

    for idx, idea in enumerate(ideas[:10], start=1):
        lines.extend(
            [
                f"### {idx}. {idea.ticker} - {idea.action}",
                "",
                f"- **Priority / score:** {idea.priority} / {idea.score:.1f}",
                f"- **Source:** {idea.source}",
                f"- **Rationale:** {idea.rationale}",
                f"- **Trigger:** {idea.trigger}",
                f"- **Sizing:** {idea.sizing}",
                "",
            ]
        )

    lines.extend(
        [
            "## Portfolio Concentration Context",
            "",
            "| Symbol | Weight | P&L % | Price | Trend |",
            "|--------|--------|-------|-------|-------|",
        ]
    )
    for pos in top_weights:
        quote = quotes.get(pos.symbol, Quote(symbol=pos.symbol, price=pos.current))
        lines.append(
            f"| {pos.symbol} | {pos.weight:.1f}% | {fmt_pct(pos.pnl_pct)} | "
            f"{fmt_money(quote.price)} | {trend_label(quote)} |"
        )

    lines.extend(
        [
            "",
            "## Open Options Risk Check",
            "",
            "| Ticker | Position | Expiration | Credit | Current | Underlying | Cushion |",
            "|--------|----------|------------|--------|---------|------------|---------|",
        ]
    )
    for opt in options:
        quote = quotes.get(opt.ticker, Quote(symbol=opt.ticker))
        cushion = None
        if quote.price is not None:
            cushion = (quote.price / opt.strike - 1) * 100
        lines.append(
            f"| {opt.ticker} | {opt.contracts}x short {opt.strike:g} {opt.option_type} | "
            f"{opt.expiration} | {fmt_money(opt.credit)} | {fmt_money(opt.current)} | "
            f"{fmt_money(quote.price)} | {fmt_pct(cushion)} |"
        )

    lines.extend(
        [
            "",
            "## Watchlist Leaders",
            "",
            "| Ticker | Score | Grade | Status | Price | Trend |",
            "|--------|-------|-------|--------|-------|-------|",
        ]
    )
    for item in top_watchlist:
        quote = quotes.get(item.ticker, Quote(symbol=item.ticker))
        lines.append(
            f"| {item.ticker} | {item.score:.1f} | {item.grade} | {item.status} | "
            f"{fmt_money(quote.price)} | {trend_label(quote)} |"
        )

    lines.extend(
        [
            "",
            "## Telegram Message",
            "",
            "```text",
            telegram_message,
            "```",
            "",
            "## Data Caveats",
            "",
            "- Live quote data uses Yahoo Finance chart endpoints when available; otherwise repository context prices are used.",
            "- The portfolio file is a static export and may differ from brokerage reality.",
            "- This report is for research and education only and is not financial advice or a recommendation to trade.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report = "\n".join(lines) + "\n"
    output_path.write_text(report, encoding="utf-8")
    return report


def send_telegram(token: str, chat_id: str, message: str) -> str:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    request = urllib.request.Request(url, data=payload, method="POST")
    with urllib.request.urlopen(request, timeout=15) as response:
        data = json.loads(response.read().decode("utf-8"))
    if not data.get("ok"):
        raise RuntimeError(data.get("description", "Telegram API returned ok=false"))
    message_id = data.get("result", {}).get("message_id", "unknown")
    return f"sent (message_id {message_id})"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate trade ideas from portfolio/watchlist context.")
    parser.add_argument("--portfolio", type=Path, default=DEFAULT_PORTFOLIO)
    parser.add_argument("--watchlist", type=Path, default=DEFAULT_WATCHLIST)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--send-telegram", action="store_true", help="Send the Telegram summary.")
    parser.add_argument("--telegram-chat-id", default=os.environ.get("TELEGRAM_CHAT_ID"))
    parser.add_argument("--telegram-token", default=os.environ.get("TELEGRAM_BOT_TOKEN"))
    parser.add_argument("--skip-live-quotes", action="store_true", help="Use repository context prices only.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_time = datetime.now(timezone.utc)
    output_path = args.output or DEFAULT_OUTPUTS / f"trade-idea-generator-{run_time:%Y-%m-%d}.md"

    positions, options = parse_portfolio(args.portfolio)
    watchlist = parse_watchlist(args.watchlist)
    symbols = {p.symbol for p in positions}
    symbols.update({o.ticker for o in options})
    symbols.update({w.ticker for w in watchlist if w.score is not None and w.score >= 55})
    symbols.update({"SPY", "QQQ", "^VIX"})

    quotes = fetch_quotes(symbols, positions, args.skip_live_quotes)
    ideas = (
        generate_option_ideas(options, quotes)
        + generate_position_ideas(positions, quotes)
        + generate_watchlist_ideas(watchlist, positions, quotes)
    )
    ideas = sorted(ideas, key=lambda idea: idea.score, reverse=True)
    market_summary = build_market_summary(quotes)
    quote_sources = {q.source for q in quotes.values() if q.price is not None}
    telegram_message = build_telegram_message(run_time, market_summary, ideas, positions, watchlist, quote_sources)

    telegram_status = "not requested"
    exit_code = 0
    if args.send_telegram:
        if not args.telegram_token:
            telegram_status = "failed - TELEGRAM_BOT_TOKEN missing"
            exit_code = 2
        elif not args.telegram_chat_id:
            telegram_status = "failed - TELEGRAM_CHAT_ID/--telegram-chat-id missing"
            exit_code = 2
        else:
            try:
                telegram_status = send_telegram(args.telegram_token, args.telegram_chat_id, telegram_message)
            except Exception as exc:  # noqa: BLE001 - report API errors without exposing token.
                telegram_status = f"failed - {exc}"
                exit_code = 2

    build_report(
        run_time=run_time,
        output_path=output_path,
        market_summary=market_summary,
        ideas=ideas,
        positions=positions,
        options=options,
        watchlist=watchlist,
        quotes=quotes,
        telegram_status=telegram_status,
        telegram_message=telegram_message,
    )

    print(f"Report: {output_path}")
    print(f"Telegram: {telegram_status}")
    if ideas:
        print("Top idea:", f"{ideas[0].ticker} - {ideas[0].action}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
