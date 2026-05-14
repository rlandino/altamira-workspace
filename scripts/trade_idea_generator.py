#!/usr/bin/env python3
"""Generate trade ideas from the repository portfolio and watchlist context."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import textwrap
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


WORKSPACE = Path(__file__).resolve().parent.parent
PORTFOLIO_PATH = WORKSPACE / "context" / "portfolio-details.md"
WATCHLIST_PATH = WORKSPACE / "context" / "watchlist.md"
OUTPUTS_DIR = WORKSPACE / "outputs"


SECTOR_BY_TICKER = {
    "AAPL": "Technology",
    "ABBV": "Healthcare",
    "ABT": "Healthcare",
    "ACN": "Technology",
    "ADBE": "Technology",
    "ADSK": "Technology",
    "AMAT": "Technology",
    "AMZN": "Consumer Discretionary",
    "ANET": "Technology",
    "ASML": "Technology",
    "AVGO": "Technology",
    "CDNS": "Technology",
    "CMG": "Consumer Discretionary",
    "COST": "Consumer Defensive",
    "CRM": "Technology",
    "CRWD": "Technology",
    "FFOLX": "Fund",
    "FICO": "Technology",
    "GD": "Industrials",
    "GOOGL": "Communication Services",
    "INTU": "Technology",
    "ISRG": "Healthcare",
    "JPM": "Financials",
    "KLAC": "Technology",
    "KMI": "Energy",
    "LLY": "Healthcare",
    "LRCX": "Technology",
    "MA": "Financials",
    "MELI": "Consumer Discretionary",
    "META": "Communication Services",
    "MRVL": "Technology",
    "MSCI": "Financials",
    "MSFT": "Technology",
    "NFLX": "Communication Services",
    "NOW": "Technology",
    "NVDA": "Technology",
    "PANW": "Technology",
    "PLTR": "Technology",
    "QQQ": "ETF",
    "SPGI": "Financials",
    "SPY": "ETF",
    "TSLA": "Consumer Discretionary",
    "TSM": "Technology",
    "TMO": "Healthcare",
    "V": "Financials",
    "WM": "Industrials",
}


@dataclass(frozen=True)
class Position:
    symbol: str
    quantity: float
    average_price: float
    current_price: float
    market_value: float
    weight: float


@dataclass(frozen=True)
class WatchlistEntry:
    ticker: str
    score: float | None
    grade: str | None
    company: str
    status: str


@dataclass(frozen=True)
class OptionPosition:
    ticker: str
    strike: float
    option_type: str
    expiration: dt.date
    credit: float
    current: float
    contracts: int


def parse_money(value: str) -> float:
    cleaned = value.replace("$", "").replace(",", "").strip()
    if cleaned in {"", "-"}:
        return 0.0
    return float(cleaned)


def parse_float(value: str) -> float:
    cleaned = value.replace(",", "").replace("%", "").strip()
    if cleaned in {"", "-", "—"}:
        return 0.0
    return float(cleaned)


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing required context file: {path}")
    return path.read_text(encoding="utf-8")


def parse_positions(markdown: str) -> list[Position]:
    positions: list[Position] = []
    in_table = False
    for line in markdown.splitlines():
        if line.startswith("| SYMBOL |"):
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and not line.startswith("|"):
            break
        if not in_table or not line.startswith("|"):
            continue

        cells = split_markdown_row(line)
        if len(cells) < 9 or cells[0].lower() in {"symbol", "totals:"}:
            continue
        symbol = cells[0].upper()
        if symbol == "TOTALS:":
            continue
        try:
            positions.append(
                Position(
                    symbol=symbol,
                    quantity=parse_float(cells[1]),
                    average_price=parse_money(cells[2]),
                    current_price=parse_money(cells[3]),
                    market_value=parse_money(cells[4]),
                    weight=parse_float(cells[8]),
                )
            )
        except ValueError:
            continue
    return positions


def parse_options(markdown: str, today: dt.date) -> tuple[list[OptionPosition], list[OptionPosition]]:
    active: list[OptionPosition] = []
    stale: list[OptionPosition] = []
    in_table = False
    for line in markdown.splitlines():
        if line.startswith("| Ticker | Strike | Type | Expiration |"):
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and not line.startswith("|"):
            break
        if not in_table or not line.startswith("|"):
            continue

        cells = split_markdown_row(line)
        if len(cells) < 7:
            continue
        try:
            option = OptionPosition(
                ticker=cells[0].upper(),
                strike=parse_float(cells[1]),
                option_type=cells[2],
                expiration=dt.date.fromisoformat(cells[3]),
                credit=parse_float(cells[4]),
                current=parse_float(cells[5]),
                contracts=int(parse_float(cells[6])),
            )
        except (ValueError, TypeError):
            continue
        if option.expiration < today:
            stale.append(option)
        else:
            active.append(option)
    return active, stale


def parse_watchlist(markdown: str) -> list[WatchlistEntry]:
    entries: list[WatchlistEntry] = []
    in_table = False
    for line in markdown.splitlines():
        if line.startswith("| Ticker | Score | Grade | Company | Status |"):
            in_table = True
            continue
        if in_table and line.startswith("|---"):
            continue
        if in_table and not line.startswith("|"):
            break
        if not in_table or not line.startswith("|"):
            continue

        cells = split_markdown_row(line)
        if len(cells) < 5:
            continue
        score = None if cells[1] in {"—", "-", ""} else parse_float(cells[1])
        grade_match = re.search(r"\*\*(.*?)\*\*|([A-F][+-]?)", cells[2])
        grade = (grade_match.group(1) or grade_match.group(2)) if grade_match else None
        status = re.sub(r"[^\w\s-]", "", cells[4]).strip()
        entries.append(
            WatchlistEntry(
                ticker=cells[0].upper(),
                score=score,
                grade=grade,
                company=cells[3],
                status=status,
            )
        )
    return entries


def format_currency(value: float) -> str:
    return f"${value:,.0f}"


def format_signed_pct(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.1f}%"


def total_value(positions: Iterable[Position]) -> float:
    return sum(position.market_value for position in positions)


def sector_weights(positions: Iterable[Position]) -> dict[str, float]:
    weights: dict[str, float] = {}
    for position in positions:
        sector = SECTOR_BY_TICKER.get(position.symbol, "Unknown")
        weights[sector] = weights.get(sector, 0.0) + position.weight
    return dict(sorted(weights.items(), key=lambda item: item[1], reverse=True))


def grade_rank(grade: str | None) -> int:
    order = {
        "A+": 12,
        "A": 11,
        "A-": 10,
        "B+": 9,
        "B": 8,
        "B-": 7,
        "C+": 6,
        "C": 5,
        "C-": 4,
        "D+": 3,
        "D": 2,
        "F": 1,
    }
    return order.get(grade or "", 0)


def choose_watchlist_candidates(
    watchlist: list[WatchlistEntry], current_symbols: set[str], limit: int = 5
) -> list[WatchlistEntry]:
    candidates = [entry for entry in watchlist if entry.ticker not in current_symbols]
    candidates.sort(
        key=lambda entry: (
            entry.score is not None,
            entry.score or 0.0,
            grade_rank(entry.grade),
        ),
        reverse=True,
    )
    return candidates[:limit]


def choose_trim_candidates(positions: list[Position], limit: int = 4) -> list[Position]:
    return sorted(
        [position for position in positions if position.weight >= 10.0],
        key=lambda position: position.weight,
        reverse=True,
    )[:limit]


def build_trade_ideas(
    positions: list[Position],
    watchlist: list[WatchlistEntry],
    active_options: list[OptionPosition],
    stale_options: list[OptionPosition],
    today: dt.date,
) -> tuple[str, str]:
    current_symbols = {position.symbol for position in positions}
    portfolio_value = total_value(positions)
    sectors = sector_weights(positions)
    top_positions = sorted(positions, key=lambda position: position.weight, reverse=True)[:5]
    watch_candidates = choose_watchlist_candidates(watchlist, current_symbols)
    trim_candidates = choose_trim_candidates(positions)

    tech_weight = sectors.get("Technology", 0.0) + sectors.get("ETF", 0.0) * 0.6
    concentration_flag = tech_weight > 35.0
    starter_pct = 1.5 if concentration_flag else 2.0
    starter_value = portfolio_value * starter_pct / 100.0

    top_candidate = watch_candidates[0] if watch_candidates else None
    second_candidate = watch_candidates[1] if len(watch_candidates) > 1 else None
    trim_primary = trim_candidates[0] if trim_candidates else None

    headline = (
        "prioritize de-risking oversized tech/semiconductor exposure before adding beta"
        if concentration_flag
        else "portfolio concentration is manageable; use staged additions from the highest-scored watchlist names"
    )

    message_lines = [
        f"Altamira Trade Idea Generator - {today.isoformat()}",
        "",
        f"Portfolio: {format_currency(portfolio_value)} across {len(positions)} holdings.",
        f"Read-through: {headline}.",
    ]

    if top_candidate:
        message_lines.extend(
            [
                "",
                f"Top add idea: {top_candidate.ticker} ({top_candidate.grade or 'N/A'}, score {top_candidate.score or 0:.1f})",
                f"- Action: starter allocation near {starter_pct:.1f}% ({format_currency(starter_value)}) only on a pullback or after confirming no near-term earnings conflict.",
                f"- Rationale: highest watchlist score outside current holdings; use staged entry instead of increasing existing concentration.",
            ]
        )
    if second_candidate:
        message_lines.extend(
            [
                "",
                f"Backup add idea: {second_candidate.ticker} ({second_candidate.grade or 'N/A'}, score {second_candidate.score or 0:.1f})",
                "- Action: keep as second ticket if the top candidate gaps higher; prefer defined-risk or staged equity entry.",
            ]
        )
    if trim_primary:
        message_lines.extend(
            [
                "",
                f"Risk-control idea: trim/hedge {trim_primary.symbol} ({trim_primary.weight:.1f}% weight).",
                "- Action: do not add more to top-weight positions; consider harvesting 1-2 percentage points from the largest winners to fund new ideas.",
            ]
        )

    if stale_options:
        message_lines.extend(
            [
                "",
                f"Options note: {len(stale_options)} option rows in context are expired as of today; refresh before opening or rolling short-premium trades.",
            ]
        )
    elif active_options:
        losing = [opt for opt in active_options if opt.current > opt.credit]
        if losing:
            tickers = ", ".join(sorted({opt.ticker for opt in losing}))
            message_lines.extend(
                [
                    "",
                    f"Options note: manage underwater short-premium positions first ({tickers}); avoid new correlated puts until risk is reduced.",
                ]
            )

    message_lines.extend(
        [
            "",
            "Disclosure: informational only, not financial advice. Validate prices, earnings dates, liquidity, and risk limits before trading.",
        ]
    )
    telegram_message = "\n".join(message_lines)

    sector_table = "\n".join(
        f"| {sector} | {weight:.1f}% |" for sector, weight in sectors.items()
    )
    top_position_rows = "\n".join(
        f"| {p.symbol} | {p.weight:.1f}% | {format_currency(p.market_value)} | "
        f"{format_signed_pct((p.current_price / p.average_price - 1) * 100 if p.average_price else 0)} |"
        for p in top_positions
    )
    watch_rows = "\n".join(
        f"| {entry.ticker} | {entry.score if entry.score is not None else 'N/A'} | "
        f"{entry.grade or 'N/A'} | {entry.company} | {entry.status} |"
        for entry in watch_candidates
    )
    trim_rows = "\n".join(
        f"| {p.symbol} | {p.weight:.1f}% | {format_currency(p.market_value)} | "
        f"{SECTOR_BY_TICKER.get(p.symbol, 'Unknown')} |"
        for p in trim_candidates
    ) or "| None | - | - | - |"

    option_note = "No active option rows found."
    if active_options:
        option_note = "\n".join(
            f"- {opt.ticker} {opt.strike:g}{opt.option_type[0].upper()} exp {opt.expiration}: "
            f"credit {opt.credit:.2f}, current {opt.current:.2f}, contracts {opt.contracts}"
            for opt in active_options
        )
    stale_note = (
        f"{len(stale_options)} option rows are expired relative to {today.isoformat()} and were excluded."
        if stale_options
        else "No stale option rows detected."
    )

    memo = f"""# Trade Idea Generator - {today.isoformat()}

> Source data: `context/portfolio-details.md` and `context/watchlist.md`.
> This report is informational only and is not financial advice. Validate live prices,
> earnings dates, liquidity, and risk limits before entering orders.

## Executive Summary

- Portfolio market value parsed from holdings: **{format_currency(portfolio_value)}**.
- Main read-through: **{headline.capitalize()}**.
- Highest-scored non-held watchlist candidate: **{top_candidate.ticker if top_candidate else 'N/A'}**.
- Primary risk-control candidate: **{trim_primary.symbol if trim_primary else 'N/A'}**.
- Options context: **{stale_note}**

## Portfolio Concentration

| Sector | Weight |
|--------|--------|
{sector_table}

## Top Current Holdings

| Ticker | Weight | Market Value | Gain/Loss vs Cost |
|--------|--------|--------------|-------------------|
{top_position_rows}

## Trade Ideas

### 1. Add candidate - {top_candidate.ticker if top_candidate else 'No candidate'}

{build_add_idea(top_candidate, starter_pct, starter_value, concentration_flag)}

### 2. Backup add candidate - {second_candidate.ticker if second_candidate else 'No candidate'}

{build_add_idea(second_candidate, starter_pct, starter_value, concentration_flag, backup=True)}

### 3. Risk-control / funding idea

{build_trim_idea(trim_primary)}

## Candidate Watchlist Snapshot

| Ticker | Score | Grade | Company | Status |
|--------|-------|-------|---------|--------|
{watch_rows}

## Trim / Hedge Candidates

| Ticker | Weight | Market Value | Sector |
|--------|--------|--------------|--------|
{trim_rows}

## Options Context

{option_note}

{stale_note}

## Telegram Summary Sent

```text
{telegram_message}
```
"""
    return memo, telegram_message


def build_add_idea(
    candidate: WatchlistEntry | None,
    starter_pct: float,
    starter_value: float,
    concentration_flag: bool,
    backup: bool = False,
) -> str:
    if candidate is None:
        return "No eligible non-held watchlist candidate found."

    entry_style = (
        "Use a staged equity entry or cash-secured put only after confirming earnings and options liquidity."
        if not backup
        else "Keep this as the alternate if the first candidate is extended or violates the entry checklist."
    )
    concentration_clause = (
        " Because current technology/semiconductor exposure is already high, fund the entry from trims rather than fresh concentration."
        if concentration_flag
        else ""
    )
    return textwrap.dedent(
        f"""\
        - Candidate: **{candidate.ticker}** ({candidate.company}); score **{candidate.score if candidate.score is not None else 'N/A'}**, grade **{candidate.grade or 'N/A'}**.
        - Ticket sizing: target a starter allocation near **{starter_pct:.1f}%** of parsed portfolio value, or about **{format_currency(starter_value)}**.
        - Entry rule: {entry_style}{concentration_clause}
        - Risk rule: do not enter if it would breach single-position, sector, cash-reserve, or near-term earnings constraints.
        """
    ).strip()


def build_trim_idea(position: Position | None) -> str:
    if position is None:
        return "No position exceeds the 10% concentration review threshold."
    return textwrap.dedent(
        f"""\
        - Candidate: **{position.symbol}**, currently **{position.weight:.1f}%** of parsed market value.
        - Action: pause additions; consider trimming or collaring 1-2 percentage points if adding a new watchlist position.
        - Rationale: position size is above the 10% review threshold and can be used as a funding source without raising portfolio gross exposure.
        """
    ).strip()


def send_telegram(message: str, token: str, chat_id: str) -> dict[str, object]:
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode()
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=data,
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = response.read().decode("utf-8")
    result = json.loads(payload)
    if not result.get("ok"):
        raise RuntimeError(f"Telegram send failed: {result}")
    return result


def resolve_today(value: str | None) -> dt.date:
    if not value:
        return dt.date.today()
    return dt.date.fromisoformat(value)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate trade ideas from portfolio/watchlist context."
    )
    parser.add_argument("--date", help="Report date in YYYY-MM-DD format.")
    parser.add_argument(
        "--send-telegram",
        action="store_true",
        help="Send the concise report to Telegram after writing the markdown output.",
    )
    parser.add_argument(
        "--telegram-chat-id",
        default=os.environ.get("TELEGRAM_CHAT_ID", ""),
        help="Telegram chat/channel ID. Defaults to TELEGRAM_CHAT_ID.",
    )
    parser.add_argument(
        "--telegram-token",
        default=os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN", ""),
        help="Telegram bot token. Defaults to TELEGRAM_BOT_TOKEN or TELEGRAM_TOKEN.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    today = resolve_today(args.date)

    portfolio_markdown = read_text(PORTFOLIO_PATH)
    watchlist_markdown = read_text(WATCHLIST_PATH)

    positions = parse_positions(portfolio_markdown)
    if not positions:
        raise RuntimeError(f"No positions parsed from {PORTFOLIO_PATH}")
    watchlist = parse_watchlist(watchlist_markdown)
    if not watchlist:
        raise RuntimeError(f"No watchlist entries parsed from {WATCHLIST_PATH}")
    active_options, stale_options = parse_options(portfolio_markdown, today)

    memo, telegram_message = build_trade_ideas(
        positions=positions,
        watchlist=watchlist,
        active_options=active_options,
        stale_options=stale_options,
        today=today,
    )

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUTS_DIR / f"trade-idea-generator-{today.isoformat()}.md"
    output_path.write_text(memo, encoding="utf-8")
    print(f"Wrote {output_path.relative_to(WORKSPACE)}")

    if args.send_telegram:
        if not args.telegram_token:
            raise RuntimeError("Missing Telegram bot token. Set TELEGRAM_BOT_TOKEN or pass --telegram-token.")
        if not args.telegram_chat_id:
            raise RuntimeError("Missing Telegram chat ID. Set TELEGRAM_CHAT_ID or pass --telegram-chat-id.")
        result = send_telegram(telegram_message, args.telegram_token, args.telegram_chat_id)
        message_id = result.get("result", {}).get("message_id")
        print(f"Sent Telegram message_id={message_id}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - CLI failure path
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
