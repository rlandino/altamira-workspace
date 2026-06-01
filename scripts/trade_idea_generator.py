#!/usr/bin/env python3
"""Generate portfolio/watchlist trade ideas and optionally send to Telegram."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import re
import sys
import textwrap
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_PATH = ROOT / "context" / "portfolio-details.md"
WATCHLIST_PATH = ROOT / "context" / "watchlist.md"
OUTPUTS_DIR = ROOT / "outputs"


@dataclass
class Holding:
    symbol: str
    quantity: float
    average_price: float
    current_price: float
    market_value: float
    weight: float
    pnl_percent: float | None = None


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


def clean_cell(value: str) -> str:
    value = re.sub(r"\*\*", "", value.strip())
    value = value.replace("\u2b50", "").strip()
    return value


def parse_money(value: str) -> float:
    value = clean_cell(value)
    value = value.replace("$", "").replace(",", "").replace("%", "")
    value = value.replace("\u2014", "")
    if not value:
        return 0.0
    return float(value)


def parse_percent_from_cell(value: str) -> float | None:
    match = re.search(r"\(([+-]?[0-9,.]+)%\)", value)
    if not match:
        match = re.search(r"([+-]?[0-9,.]+)%", value)
    return float(match.group(1).replace(",", "")) if match else None


def parse_markdown_table(lines: list[str], header_startswith: str) -> list[list[str]]:
    """Return rows for the first markdown table whose header starts with text."""
    for idx, line in enumerate(lines):
        if line.strip().startswith(header_startswith):
            rows: list[list[str]] = []
            for row in lines[idx + 2 :]:
                if not row.strip().startswith("|"):
                    break
                cells = [clean_cell(cell) for cell in row.strip().strip("|").split("|")]
                rows.append(cells)
            return rows
    return []


def load_portfolio(path: Path) -> tuple[float, list[Holding], list[OptionPosition]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    total_match = re.search(r"\*\*Total MKT VALUE\*\*\s*\|\s*\$?([0-9,]+)", text)
    portfolio_value = float(total_match.group(1).replace(",", "")) if total_match else 0.0

    holdings: list[Holding] = []
    for cells in parse_markdown_table(lines, "| SYMBOL |"):
        if len(cells) < 9 or cells[0].lower() == "totals:":
            continue
        try:
            holdings.append(
                Holding(
                    symbol=cells[0],
                    quantity=parse_money(cells[1]),
                    average_price=parse_money(cells[2]),
                    current_price=parse_money(cells[3]),
                    market_value=parse_money(cells[4]),
                    weight=parse_money(cells[8]),
                    pnl_percent=parse_percent_from_cell(cells[6]),
                )
            )
        except ValueError:
            continue

    if not portfolio_value:
        portfolio_value = sum(holding.market_value for holding in holdings)

    options: list[OptionPosition] = []
    for cells in parse_markdown_table(lines, "| Ticker | Strike | Type |"):
        if len(cells) < 7:
            continue
        try:
            options.append(
                OptionPosition(
                    ticker=cells[0],
                    strike=parse_money(cells[1]),
                    option_type=cells[2],
                    expiration=cells[3],
                    credit=parse_money(cells[4]),
                    current=parse_money(cells[5]),
                    contracts=int(parse_money(cells[6])),
                )
            )
        except ValueError:
            continue

    return portfolio_value, holdings, options


def load_watchlist(path: Path) -> list[WatchlistEntry]:
    lines = path.read_text(encoding="utf-8").splitlines()
    entries: list[WatchlistEntry] = []
    for cells in parse_markdown_table(lines, "| Ticker | Score |"):
        if len(cells) < 5:
            continue
        score = None if cells[1] in {"\u2014", "-", ""} else float(cells[1])
        entries.append(
            WatchlistEntry(
                ticker=cells[0],
                score=score,
                grade=cells[2],
                company=cells[3],
                status=cells[4],
            )
        )
    return entries


def next_friday_between(start: dt.date, min_days: int = 35, max_days: int = 45) -> dt.date:
    candidates = [start + dt.timedelta(days=days) for days in range(min_days, max_days + 1)]
    fridays = [day for day in candidates if day.weekday() == 4]
    if fridays:
        target = start + dt.timedelta(days=(min_days + max_days) // 2)
        return min(fridays, key=lambda day: abs((day - target).days))
    day = start + dt.timedelta(days=min_days)
    return day + dt.timedelta(days=(4 - day.weekday()) % 7)


def round_strike(price: float, multiplier: float, option_type: str) -> float:
    raw = price * multiplier
    if price >= 500:
        increment = 10
    elif price >= 100:
        increment = 5
    elif price >= 25:
        increment = 2.5
    else:
        increment = 1
    rounded = round(raw / increment) * increment
    if option_type == "call" and rounded <= price:
        rounded += increment
    if option_type == "put" and rounded >= price:
        rounded -= increment
    return rounded


def format_strike(value: float) -> str:
    return f"{value:.0f}" if float(value).is_integer() else f"{value:.2f}"


def market_status(today: dt.date) -> str:
    if today.weekday() >= 5:
        return "Market closed today; treat ideas as prep for the next regular session."
    return "Market day; verify live bid/ask, delta, IV rank, earnings, and liquidity before entry."


def option_management_ideas(options: list[OptionPosition]) -> list[str]:
    ideas: list[str] = []
    for position in options:
        if position.credit <= 0:
            continue
        ratio = position.current / position.credit
        label = (
            f"{position.ticker} {format_strike(position.strike)} {position.expiration} "
            f"{position.option_type.upper()} x{position.contracts}"
        )
        if ratio >= 2.0:
            ideas.append(
                f"HIGH - Close or roll {label}: option marks {ratio:.1f}x original credit "
                f"(${position.current:.2f} vs ${position.credit:.2f}), breaching the 200% stop rule."
            )
        elif ratio <= 0.5:
            ideas.append(
                f"MEDIUM - Take profit on {label}: current mark is {ratio:.1f}x credit "
                f"(${position.current:.2f} vs ${position.credit:.2f}); consider closing at/near 50% max profit."
            )
        else:
            ideas.append(
                f"MONITOR - Hold/roll review for {label}: mark is {ratio:.1f}x credit; no automatic exit trigger."
            )
    return ideas


def covered_call_ideas(holdings: list[Holding], expiration: dt.date) -> list[str]:
    candidates = [
        holding
        for holding in holdings
        if holding.quantity >= 100 and holding.current_price > 0 and holding.weight >= 4.0
    ]
    candidates.sort(key=lambda holding: holding.weight, reverse=True)

    ideas: list[str] = []
    for holding in candidates[:5]:
        contracts_available = int(holding.quantity // 100)
        starter_contracts = max(1, math.ceil(contracts_available / 2))
        strike = round_strike(holding.current_price, 1.08, "call")
        ideas.append(
            f"MEDIUM - Covered call candidate {holding.symbol}: sell up to {starter_contracts} of "
            f"{contracts_available} available contracts around the {format_strike(strike)} call, "
            f"target expiration {expiration.isoformat()} (~30-45 DTE). Position weight {holding.weight:.1f}% "
            f"supports premium harvesting without fully capping the holding."
        )
    return ideas


def watchlist_ideas(watchlist: list[WatchlistEntry], expiration: dt.date) -> list[str]:
    ranked = [
        entry
        for entry in watchlist
        if entry.score is not None and entry.grade in {"A+", "A", "A-", "B+", "B", "B-"}
    ]
    ranked.sort(key=lambda entry: entry.score or 0, reverse=True)

    ideas: list[str] = []
    for entry in ranked[:5]:
        strategy = "cash-secured put or defined-risk bull put spread"
        if entry.score and entry.score < 62:
            strategy = "defined-risk bull put spread first, CSP only at a valuation discount"
        ideas.append(
            f"LOW - Watchlist entry setup {entry.ticker} ({entry.grade}, score {entry.score:.1f}): "
            f"use {strategy}; target 0.20-0.25 delta, 30-45 DTE near {expiration.isoformat()}, "
            f"and skip if earnings fall inside the expiration window."
        )
    return ideas


def concentration_notes(holdings: list[Holding]) -> list[str]:
    notes: list[str] = []
    overweight = [holding for holding in holdings if holding.weight >= 10.0]
    if overweight:
        formatted = ", ".join(f"{h.symbol} {h.weight:.1f}%" for h in overweight)
        notes.append(f"Concentration watch: {formatted}. Prefer covered calls/trim discipline before adding correlated tech risk.")
    losers = [holding for holding in holdings if holding.pnl_percent is not None and holding.pnl_percent <= -10.0]
    if losers:
        formatted = ", ".join(f"{h.symbol} {h.pnl_percent:.1f}%" for h in losers)
        notes.append(f"Underwater holdings to review before adding: {formatted}. Confirm thesis and trend before averaging down.")
    return notes


def build_report(
    today: dt.date,
    portfolio_value: float,
    holdings: list[Holding],
    options: list[OptionPosition],
    watchlist: list[WatchlistEntry],
) -> str:
    expiration = next_friday_between(today)
    top_holdings = sorted(holdings, key=lambda holding: holding.weight, reverse=True)[:6]
    option_ideas = option_management_ideas(options)
    call_ideas = covered_call_ideas(holdings, expiration)
    new_ideas = watchlist_ideas(watchlist, expiration)
    notes = concentration_notes(holdings)

    total_options_notional = sum(position.strike * 100 * position.contracts for position in options)
    options_pct = (total_options_notional / portfolio_value * 100) if portfolio_value else 0.0

    sections = [
        "# Altamira Trade Idea Generator",
        "",
        f"Generated: {today.isoformat()}",
        f"Sources: {PORTFOLIO_PATH.relative_to(ROOT)}, {WATCHLIST_PATH.relative_to(ROOT)}",
        f"Status: {market_status(today)}",
        "",
        "## Portfolio Snapshot",
        "",
        f"- Portfolio value in repository snapshot: ${portfolio_value:,.0f}",
        f"- Open short-premium notional: ${total_options_notional:,.0f} ({options_pct:.1f}% of portfolio value)",
        "- Largest weights: "
        + ", ".join(f"{holding.symbol} {holding.weight:.1f}%" for holding in top_holdings),
        "",
        "## Priority Trade Ideas",
        "",
    ]

    priority_ideas = [idea for idea in option_ideas if idea.startswith(("HIGH", "MEDIUM"))]
    priority_ideas.extend(call_ideas[:4])
    priority_ideas.extend(new_ideas[:3])

    for idx, idea in enumerate(priority_ideas, start=1):
        sections.append(f"{idx}. {idea}")

    sections.extend(["", "## Monitor List", ""])
    monitor_items = [idea for idea in option_ideas if idea.startswith("MONITOR")]
    monitor_items.extend(call_ideas[4:])
    monitor_items.extend(new_ideas[3:])
    for item in monitor_items:
        sections.append(f"- {item}")

    if notes:
        sections.extend(["", "## Risk Notes", ""])
        for note in notes:
            sections.append(f"- {note}")

    sections.extend(
        [
            "",
            "## Execution Checklist",
            "",
            "- Confirm live option chain, bid/ask spread under 10%, open interest above 50, and volume above 10.",
            "- Do not open or hold short premium through unplanned earnings.",
            "- Keep single-trade max loss within 5% of portfolio and total options allocation within the 30% risk limit.",
            "- Close winners around 50% of max profit; close or roll losers at 200% of original credit.",
            "",
            "Disclaimer: This is an automated research and risk-management note, not financial advice. Verify live prices, liquidity, tax impact, and suitability before trading.",
            "",
        ]
    )
    return "\n".join(sections)


def telegram_chunks(message: str, limit: int = 3900) -> Iterable[str]:
    if len(message) <= limit:
        yield message
        return

    paragraphs = message.split("\n\n")
    current = ""
    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip()
        if len(candidate) <= limit:
            current = candidate
            continue
        if current:
            yield current
        current = paragraph
    if current:
        yield current


def send_telegram(message: str, bot_token: str, chat_id: str) -> None:
    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    chunks = list(telegram_chunks(message))
    for idx, chunk in enumerate(chunks, start=1):
        prefix = f"[{idx}/{len(chunks)}]\n" if len(chunks) > 1 else ""
        payload = urllib.parse.urlencode(
            {
                "chat_id": chat_id,
                "text": prefix + chunk,
                "disable_web_page_preview": "true",
            }
        ).encode("utf-8")
        request = urllib.request.Request(api_url, data=payload, method="POST")
        with urllib.request.urlopen(request, timeout=20) as response:
            body = json.loads(response.read().decode("utf-8"))
        if not body.get("ok"):
            raise RuntimeError(f"Telegram API returned non-ok response for chunk {idx}: {body}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--portfolio", type=Path, default=PORTFOLIO_PATH, help="Portfolio markdown path")
    parser.add_argument("--watchlist", type=Path, default=WATCHLIST_PATH, help="Watchlist markdown path")
    parser.add_argument("--out", type=Path, default=None, help="Output markdown path")
    parser.add_argument("--send-telegram", action="store_true", help="Send report to Telegram")
    parser.add_argument("--telegram-chat-id", default=os.environ.get("TELEGRAM_CHAT_ID", ""), help="Telegram chat/channel id")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    today = dt.date.today()
    output_path = args.out or OUTPUTS_DIR / f"trade-idea-generator-{today.isoformat()}.md"

    try:
        portfolio_value, holdings, options = load_portfolio(args.portfolio)
        watchlist = load_watchlist(args.watchlist)
        report = build_report(today, portfolio_value, holdings, options, watchlist)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")

        if args.send_telegram:
            bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
            chat_id = args.telegram_chat_id
            if not bot_token:
                raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
            if not chat_id:
                raise RuntimeError("Telegram chat id is required via --telegram-chat-id or TELEGRAM_CHAT_ID")
            send_telegram(report, bot_token, chat_id)

        print(f"Wrote {output_path.relative_to(ROOT)}")
        if args.send_telegram:
            print("Sent report to Telegram")
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI should surface actionable errors.
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
