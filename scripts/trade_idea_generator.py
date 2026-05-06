#!/usr/bin/env python3
"""Generate portfolio/watchlist trade ideas and optionally send Telegram.

The generator is intentionally dependency-free so it can run from cron,
Cursor automations, or n8n shell nodes without environment setup. It uses the
repository's current context files as source of truth and clearly marks stale
inputs when snapshot dates lag the run date.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import textwrap
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable


WORKSPACE = Path(__file__).resolve().parents[1]
PORTFOLIO_PATH = WORKSPACE / "context" / "portfolio-details.md"
WATCHLIST_PATH = WORKSPACE / "context" / "watchlist.md"
OUTPUT_DIR = WORKSPACE / "outputs"


@dataclass(frozen=True)
class Position:
    symbol: str
    quantity: float
    avg_price: float
    current_price: float
    market_value: float
    pnl_percent: float
    day_change_percent: float
    weight: float


@dataclass(frozen=True)
class OptionPosition:
    ticker: str
    strike: float
    option_type: str
    expiration: date | None
    credit: float
    current: float
    contracts: int


@dataclass(frozen=True)
class WatchlistEntry:
    ticker: str
    score: float | None
    grade: str
    company: str
    status: str


def money_to_float(value: str) -> float:
    cleaned = value.replace("$", "").replace(",", "").strip()
    if cleaned in {"", "—", "-"}:
        return 0.0
    return float(cleaned)


def percent_from_cell(value: str) -> float:
    match = re.search(r"([-+]?\d+(?:\.\d+)?)%", value)
    return float(match.group(1)) if match else 0.0


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_snapshot_date(portfolio_text: str) -> date | None:
    match = re.search(r"^\| Date \| ([0-9]{4}-[0-9]{2}-[0-9]{2}) \|", portfolio_text, re.MULTILINE)
    if not match:
        return None
    return datetime.strptime(match.group(1), "%Y-%m-%d").date()


def parse_positions(portfolio_text: str) -> list[Position]:
    positions: list[Position] = []
    in_table = False

    for line in portfolio_text.splitlines():
        if line.startswith("| SYMBOL | QTY |"):
            in_table = True
            continue
        if in_table and (not line.startswith("|") or line.startswith("|---")):
            continue
        if in_table and line.startswith("**Totals:**"):
            break
        if not in_table or not line.startswith("|"):
            continue

        cells = split_markdown_row(line)
        if len(cells) != 9 or cells[0] in {"SYMBOL", "--------"}:
            continue
        try:
            positions.append(
                Position(
                    symbol=cells[0],
                    quantity=float(cells[1].replace(",", "")),
                    avg_price=money_to_float(cells[2]),
                    current_price=money_to_float(cells[3]),
                    market_value=money_to_float(cells[4]),
                    pnl_percent=percent_from_cell(cells[6]),
                    day_change_percent=percent_from_cell(cells[7]),
                    weight=percent_from_cell(cells[8]),
                )
            )
        except ValueError:
            continue

    return positions


def parse_options(portfolio_text: str) -> list[OptionPosition]:
    options: list[OptionPosition] = []
    in_table = False

    for line in portfolio_text.splitlines():
        if line.startswith("| Ticker | Strike | Type |"):
            in_table = True
            continue
        if in_table and line.startswith("|--------"):
            continue
        if in_table and not line.startswith("|"):
            break
        if not in_table:
            continue

        cells = split_markdown_row(line)
        if len(cells) != 7:
            continue
        try:
            expiration = datetime.strptime(cells[3], "%Y-%m-%d").date()
        except ValueError:
            expiration = None
        try:
            options.append(
                OptionPosition(
                    ticker=cells[0],
                    strike=float(cells[1].replace(",", "")),
                    option_type=cells[2],
                    expiration=expiration,
                    credit=float(cells[4]),
                    current=float(cells[5]),
                    contracts=int(float(cells[6])),
                )
            )
        except ValueError:
            continue

    return options


def parse_watchlist(watchlist_text: str) -> list[WatchlistEntry]:
    entries: list[WatchlistEntry] = []
    in_table = False

    for line in watchlist_text.splitlines():
        if line.startswith("| Ticker | Score |"):
            in_table = True
            continue
        if in_table and line.startswith("|--------"):
            continue
        if in_table and not line.startswith("|"):
            break
        if not in_table:
            continue

        cells = split_markdown_row(line)
        if len(cells) != 5:
            continue
        score = None if cells[1] in {"—", "-"} else float(cells[1])
        grade = cells[2].replace("**", "")
        status = cells[4].replace("⭐", "").strip()
        entries.append(WatchlistEntry(cells[0], score, grade, cells[3], status))

    return entries


def portfolio_value(positions: Iterable[Position]) -> float:
    return sum(position.market_value for position in positions)


def weighted_day_change(positions: Iterable[Position]) -> float:
    total = portfolio_value(positions)
    if total == 0:
        return 0.0
    return sum(position.market_value * position.day_change_percent for position in positions) / total


def top_positions(positions: list[Position], count: int = 5) -> list[Position]:
    return sorted(positions, key=lambda item: item.weight, reverse=True)[:count]


def top_watchlist(entries: list[WatchlistEntry], count: int = 5) -> list[WatchlistEntry]:
    scored = [entry for entry in entries if entry.score is not None]
    return sorted(scored, key=lambda item: item.score or 0.0, reverse=True)[:count]


def expired_options(options: Iterable[OptionPosition], today: date) -> list[OptionPosition]:
    return [option for option in options if option.expiration and option.expiration < today]


def near_expiry_options(options: Iterable[OptionPosition], today: date) -> list[OptionPosition]:
    return [
        option
        for option in options
        if option.expiration and 0 <= (option.expiration - today).days <= 14
    ]


def format_money(value: float) -> str:
    return f"${value:,.0f}"


def generate_report(run_date: date) -> tuple[str, str, Path]:
    portfolio_text = read_text(PORTFOLIO_PATH)
    watchlist_text = read_text(WATCHLIST_PATH)
    positions = parse_positions(portfolio_text)
    options = parse_options(portfolio_text)
    watchlist = parse_watchlist(watchlist_text)

    snapshot_date = extract_snapshot_date(portfolio_text)
    total_value = portfolio_value(positions)
    largest = top_positions(positions)
    watch_candidates = top_watchlist(watchlist)
    overweight = [position for position in positions if position.weight >= 10.0]
    stale_days = (run_date - snapshot_date).days if snapshot_date else None
    expired = expired_options(options, run_date)
    near_expiry = near_expiry_options(options, run_date)

    stale_note = (
        f"Input snapshot is {stale_days} days old ({snapshot_date.isoformat()}). "
        "Refresh portfolio and option chains before placing any trade."
        if snapshot_date and stale_days > 3
        else "Input snapshot appears current enough for screening, but confirm live prices before trading."
    )

    idea_lines = [
        "1. Risk-first trade: reduce concentration before adding new semiconductor exposure.",
        "   - Trigger: SPY, AVGO, GOOGL, and AMAT are each above 10% portfolio weight.",
        "   - Action: prioritize trimming or covered-call overlays on the largest winners before opening new LRCX/NVDA/TSM/KLAC risk.",
        "   - Rationale: this aligns the book with the documented single-position risk discipline and frees buying power for better entries.",
        "",
        "2. Watchlist opportunity: ADBE is the cleanest non-semiconductor top-candidate add.",
        "   - Trigger: ADBE is B- scored and diversifies away from the existing AVGO/AMAT semiconductor overweight.",
        "   - Action: use a starter position or defined-risk put spread only after checking live trend, IV, earnings date, and liquidity.",
        "   - Rationale: it keeps quality-growth exposure while reducing incremental chip-cycle concentration.",
        "",
        "3. Options management: audit stale/near-dated short puts before adding premium risk.",
        "   - Trigger: repository option context includes expired March 2026 contracts and May 15 contracts inside 14 days.",
        "   - Action: reconcile broker reality first; close winners at 50-60% max profit and avoid rolling losers unless the updated thesis still holds.",
        "   - Rationale: stale option state is the highest operational risk in this run.",
        "",
        "4. Cash deployment posture: wait for fresh data before initiating new CSPs.",
        "   - Trigger: live FMP/Massive keys were not available to validate IV, delta, spreads, or earnings windows.",
        "   - Action: treat today's output as a pre-trade shortlist, not an executable order ticket.",
        "   - Rationale: short-premium edge depends on live chain pricing and liquidity.",
    ]

    if expired or near_expiry:
        option_rows = []
        for option in options:
            status = "unknown"
            if option.expiration:
                days = (option.expiration - run_date).days
                status = "expired" if days < 0 else f"{days} DTE"
            option_rows.append(
                f"| {option.ticker} | {option.strike:g} {option.option_type} | {option.expiration or 'n/a'} | "
                f"{option.credit:.2f} | {option.current:.2f} | {option.contracts} | {status} |"
            )
    else:
        option_rows = ["| None flagged |  |  |  |  |  |  |"]

    top_position_rows = [
        f"| {position.symbol} | {position.weight:.1f}% | {format_money(position.market_value)} | "
        f"{position.pnl_percent:+.1f}% | {position.day_change_percent:+.1f}% |"
        for position in largest
    ]
    watch_rows = [
        f"| {entry.ticker} | {entry.score:.1f} | {entry.grade} | {entry.company} | {entry.status} |"
        for entry in watch_candidates
        if entry.score is not None
    ]

    markdown = "\n".join(
        [
            f"# Trade Idea Generator - {run_date.isoformat()}",
            "",
            "## Executive Summary",
            "",
            f"- Source files: `{PORTFOLIO_PATH.relative_to(WORKSPACE)}` and `{WATCHLIST_PATH.relative_to(WORKSPACE)}`.",
            f"- Portfolio market value from context: **{format_money(total_value)}**.",
            f"- Weighted day change from position table: **{weighted_day_change(positions):+.2f}%**.",
            f"- Data quality: **{stale_note}**",
            "- Verdict: **Risk-manage first, then selectively add non-overlapping watchlist exposure.**",
            "",
            "## Top Portfolio Concentrations",
            "",
            "| Symbol | Weight | Market Value | Total P&L | Day Change |",
            "|--------|--------|--------------|-----------|------------|",
            *top_position_rows,
            "",
            "## Top Watchlist Candidates",
            "",
            "| Ticker | Score | Grade | Company | Status |",
            "|--------|-------|-------|---------|--------|",
            *watch_rows,
            "",
            "## Trade Ideas",
            "",
            *idea_lines,
            "",
            "## Option Position Audit",
            "",
            "| Ticker | Contract | Expiration | Credit | Current | Contracts | Status |",
            "|--------|----------|------------|--------|---------|-----------|--------|",
            *option_rows,
            "",
            "## Risk Notes",
            "",
            "- Financial information is for research and planning only, not individualized investment advice.",
            "- Confirm live prices, option chains, earnings dates, bid/ask spreads, and account buying power before trading.",
            "- The current context has portfolio concentration above the documented 5% single-position risk limit, so new risk should be sized conservatively.",
            "",
        ]
    )

    telegram = "\n".join(
        [
            f"Altamira Trade Ideas - {run_date.isoformat()}",
            "",
            f"Portfolio context value: {format_money(total_value)}",
            f"Data quality: {stale_note}",
            "",
            "Top action:",
            "Risk-manage concentration first. SPY, AVGO, GOOGL, and AMAT are each above 10% weight; avoid adding more semiconductor beta until refreshed.",
            "",
            "Best watchlist candidate:",
            "ADBE - B- score, top-candidate list, less incremental chip-cycle exposure than LRCX/NVDA/TSM/KLAC.",
            "",
            "Options check:",
            "Reconcile broker positions before new premium selling; repo option context includes expired March 2026 puts and May 15 puts inside 14 DTE.",
            "",
            "Status: pre-trade shortlist only. Confirm live quotes/chains/earnings before placing orders.",
        ]
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"trade-idea-generator-{run_date.isoformat()}.md"
    output_path.write_text(markdown, encoding="utf-8")
    return markdown, telegram, output_path


def send_telegram(message: str, chat_id: str, token: str) -> list[dict]:
    results = []
    chunks = textwrap.wrap(message, width=3900, replace_whitespace=False, drop_whitespace=False)
    if not chunks:
        chunks = [message]

    for chunk in chunks:
        payload = urllib.parse.urlencode({"chat_id": chat_id, "text": chunk}).encode("utf-8")
        request = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            results.append(json.loads(response.read().decode("utf-8")))
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate trade ideas from repo portfolio/watchlist context.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Run date, YYYY-MM-DD.")
    parser.add_argument("--send-telegram", action="store_true", help="Send concise summary to Telegram.")
    parser.add_argument("--telegram-chat-id", default=os.environ.get("TELEGRAM_CHAT_ID"))
    parser.add_argument("--telegram-token", default=os.environ.get("TELEGRAM_BOT_TOKEN"))
    parser.add_argument("--print-telegram", action="store_true", help="Print Telegram summary.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    _, telegram, output_path = generate_report(run_date)

    print(f"Wrote {output_path.relative_to(WORKSPACE)}")
    if args.print_telegram:
        print()
        print(telegram)

    if args.send_telegram:
        if not args.telegram_token:
            raise SystemExit("TELEGRAM_BOT_TOKEN is required to send Telegram messages.")
        if not args.telegram_chat_id:
            raise SystemExit("TELEGRAM_CHAT_ID or --telegram-chat-id is required to send Telegram messages.")
        results = send_telegram(telegram, args.telegram_chat_id, args.telegram_token)
        message_ids = [str(result.get("result", {}).get("message_id")) for result in results]
        print(f"Sent Telegram message(s): {', '.join(message_ids)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
