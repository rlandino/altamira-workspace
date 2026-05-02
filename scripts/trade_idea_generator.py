#!/usr/bin/env python3
"""Generate trade ideas from the local portfolio/watchlist context.

The script intentionally uses repository context files as the source of truth so
the daily automation can still run when live market-data keys are unavailable.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable


WORKSPACE = Path(__file__).resolve().parents[1]
PORTFOLIO_PATH = WORKSPACE / "context" / "portfolio-details.md"
WATCHLIST_PATH = WORKSPACE / "context" / "watchlist.md"
OUTPUT_DIR = WORKSPACE / "outputs"


@dataclass(frozen=True)
class Position:
    symbol: str
    qty: float
    avg_price: float
    current: float
    market_value: float
    pnl_pct: float
    day_chg_pct: float
    weight: float


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


def _clean_money(value: str) -> float:
    cleaned = value.replace("$", "").replace(",", "").replace("%", "").strip()
    if cleaned in {"", "-", "—"}:
        return 0.0
    return float(cleaned)


def _parse_qty(value: str) -> float:
    return float(value.replace(",", "").strip())


def _parse_pct_from_cell(value: str) -> float:
    match = re.search(r"\(([+-]?\d+(?:\.\d+)?)%\)", value)
    if match:
        return float(match.group(1))
    match = re.search(r"([+-]?\d+(?:\.\d+)?)%", value)
    return float(match.group(1)) if match else 0.0


def _markdown_rows(path: Path, section_header: str) -> Iterable[list[str]]:
    in_section = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            in_section = line == section_header
            continue
        if not in_section or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells or set(cells[0]) <= {"-"} or cells[0].lower() in {"symbol", "ticker"}:
            continue
        yield cells


def load_positions() -> list[Position]:
    positions: list[Position] = []
    for cells in _markdown_rows(PORTFOLIO_PATH, "## Current Positions (from app dashboard)"):
        if len(cells) < 9 or cells[0].lower().startswith("totals"):
            continue
        try:
            positions.append(
                Position(
                    symbol=cells[0],
                    qty=_parse_qty(cells[1]),
                    avg_price=_clean_money(cells[2]),
                    current=_clean_money(cells[3]),
                    market_value=_clean_money(cells[4]),
                    pnl_pct=_parse_pct_from_cell(cells[6]),
                    day_chg_pct=_parse_pct_from_cell(cells[7]),
                    weight=_clean_money(cells[8]),
                )
            )
        except (IndexError, ValueError):
            continue
    return positions


def load_options() -> list[OptionPosition]:
    options: list[OptionPosition] = []
    for cells in _markdown_rows(PORTFOLIO_PATH, "## Options / Short Premium Positions"):
        if len(cells) < 7:
            continue
        try:
            options.append(
                OptionPosition(
                    ticker=cells[0],
                    strike=_clean_money(cells[1]),
                    option_type=cells[2],
                    expiration=cells[3],
                    credit=_clean_money(cells[4]),
                    current=_clean_money(cells[5]),
                    contracts=int(float(cells[6])),
                )
            )
        except ValueError:
            continue
    return options


def load_watchlist() -> list[WatchlistItem]:
    items: list[WatchlistItem] = []
    for cells in _markdown_rows(WATCHLIST_PATH, "## Watchlist Tickers"):
        if len(cells) < 5:
            continue
        raw_score = cells[1].replace("—", "").replace("-", "").strip()
        raw_grade = re.sub(r"[*`]", "", cells[2]).replace("—", "").replace("-", "").strip()
        try:
            score = float(raw_score) if raw_score else None
        except ValueError:
            score = None
        items.append(
            WatchlistItem(
                ticker=cells[0],
                score=score,
                grade=raw_grade or None,
                company=cells[3],
                status=cells[4].replace("⭐", "").strip(),
            )
        )
    return items


def portfolio_summary(positions: list[Position]) -> dict[str, float]:
    total_value = sum(position.market_value for position in positions)
    tech_symbols = {
        "AAPL",
        "MSFT",
        "AVGO",
        "GOOGL",
        "AMAT",
        "AMZN",
        "CRWD",
        "NOW",
        "SPGI",
        "NFLX",
    }
    tech_weight = sum(position.weight for position in positions if position.symbol in tech_symbols)
    top_weight = sum(position.weight for position in sorted(positions, key=lambda p: p.weight, reverse=True)[:5])
    return {"total_value": total_value, "tech_weight": tech_weight, "top5_weight": top_weight}


def option_status(option: OptionPosition, positions: dict[str, Position]) -> str:
    spot = positions.get(option.ticker).current if option.ticker in positions else None
    if option.option_type.lower() == "put" and spot is not None:
        distance = (spot - option.strike) / spot * 100
        if distance < 0:
            return f"ITM by {abs(distance):.1f}%"
        return f"OTM cushion {distance:.1f}%"
    return "Review manually"


def build_report(
    positions: list[Position],
    options: list[OptionPosition],
    watchlist: list[WatchlistItem],
    as_of: str,
) -> tuple[str, str]:
    positions_by_symbol = {position.symbol: position for position in positions}
    summary = portfolio_summary(positions)
    overweight = [position for position in positions if position.weight >= 10]
    covered_call_candidates = [
        position
        for position in positions
        if position.qty >= 100 and position.pnl_pct >= 30 and position.weight >= 3
    ]
    challenged_options = [
        option
        for option in options
        if option.option_type.lower() == "put"
        and option.ticker in positions_by_symbol
        and positions_by_symbol[option.ticker].current < option.strike
    ]
    profitable_options = [
        option
        for option in options
        if option.current <= option.credit * 0.55
    ]
    top_watchlist = [
        item
        for item in watchlist
        if item.score is not None and item.grade in {"A+", "A", "A-", "B+", "B", "B-"}
    ][:6]

    top_ideas: list[tuple[str, str, str]] = []
    if challenged_options:
        option = challenged_options[0]
        spot = positions_by_symbol[option.ticker].current
        top_ideas.append(
            (
                f"Defend / roll {option.ticker} {option.strike:g}P exp {option.expiration}",
                "Risk management",
                (
                    f"Underlying is ${spot:.2f} vs ${option.strike:g} strike; current option "
                    f"${option.current:.2f} is above ${option.credit:.2f} credit. Prioritize roll, "
                    "close, or assignment decision before adding new risk."
                ),
            )
        )

    if covered_call_candidates:
        cc = covered_call_candidates[0]
        top_ideas.append(
            (
                f"Sell covered-call overlay on {cc.symbol}",
                "Income / trim concentration",
                (
                    f"{cc.symbol} is {cc.weight:.1f}% of the portfolio with +{cc.pnl_pct:.1f}% "
                    "unrealized gain and at least 100 shares. Use 30-45 DTE, 0.20-0.30 delta, "
                    "and only size against shares you would be willing to trim."
                ),
            )
        )

    if profitable_options:
        option = profitable_options[0]
        top_ideas.append(
            (
                f"Take profit on {option.ticker} {option.strike:g}P exp {option.expiration}",
                "Theta harvest",
                (
                    f"Current mark ${option.current:.2f} is at or below 55% of original ${option.credit:.2f} "
                    "credit. Consider closing near the 50% profit rule and redeploying after a fresh scan."
                ),
            )
        )

    if top_watchlist:
        candidate = top_watchlist[0]
        top_ideas.append(
            (
                f"Watchlist entry scan: {candidate.ticker}",
                "Potential new premium sale",
                (
                    f"{candidate.company} is a top watchlist candidate ({candidate.score:.1f}, "
                    f"{candidate.grade}). Prefer a defined-risk bull put spread or small CSP only "
                    "if sector exposure and earnings timing pass the options scan."
                ),
            )
        )

    if len(top_ideas) < 4 and overweight:
        ow = overweight[0]
        top_ideas.append(
            (
                f"Rebalance guardrail: {ow.symbol}",
                "Concentration control",
                (
                    f"{ow.symbol} is {ow.weight:.1f}% of portfolio. Avoid adding correlated exposure "
                    "until position size moves closer to the 5% single-name target."
                ),
            )
        )

    report_lines = [
        f"# Trade Idea Generator — {as_of}",
        "",
        "> Source: repository context files (`context/portfolio-details.md`, `context/watchlist.md`).",
        "> This is not financial advice. Verify live prices, option chains, liquidity, and earnings dates before placing trades.",
        "",
        "## Portfolio Snapshot",
        "",
        f"- Portfolio market value from context: ${summary['total_value']:,.0f}",
        f"- Top 5 holdings weight: {summary['top5_weight']:.1f}%",
        f"- Approximate tech/growth weight: {summary['tech_weight']:.1f}%",
        f"- Positions >=10% weight: {', '.join(f'{p.symbol} ({p.weight:.1f}%)' for p in overweight) or 'None'}",
        "",
        "## Top Trade Ideas",
        "",
        "| Rank | Idea | Type | Rationale / Action |",
        "|------|------|------|--------------------|",
    ]

    for idx, (idea, idea_type, rationale) in enumerate(top_ideas, start=1):
        report_lines.append(f"| {idx} | {idea} | {idea_type} | {rationale} |")

    report_lines.extend(
        [
            "",
            "## Open Short-Premium Checks",
            "",
            "| Ticker | Contract | Credit | Current | Status | Action Bias |",
            "|--------|----------|--------|---------|--------|-------------|",
        ]
    )
    for option in options:
        status = option_status(option, positions_by_symbol)
        if option.current <= option.credit * 0.55:
            action = "Consider close at profit target"
        elif "ITM" in status:
            action = "Manage first: roll/close/assignment decision"
        elif option.current >= option.credit * 2:
            action = "Review stop/roll rule"
        else:
            action = "Monitor"
        report_lines.append(
            f"| {option.ticker} | {option.strike:g}{option.option_type[0].upper()} {option.expiration} x{option.contracts} | "
            f"${option.credit:.2f} | ${option.current:.2f} | {status} | {action} |"
        )

    report_lines.extend(
        [
            "",
            "## Watchlist Premium-Sale Candidates",
            "",
            "| Ticker | Grade | Score | Company | Setup Note |",
            "|--------|-------|-------|---------|------------|",
        ]
    )
    for item in top_watchlist:
        score = f"{item.score:.1f}" if item.score is not None else "N/A"
        setup = "Run live options scan; prefer 30-45 DTE 0.20-0.30 delta, avoid earnings."
        if item.ticker in {"LRCX", "NVDA", "TSM", "KLAC", "ASML"}:
            setup = "High semiconductor overlap with AVGO/AMAT; use defined-risk or wait for pullback."
        report_lines.append(f"| {item.ticker} | {item.grade or 'N/A'} | {score} | {item.company} | {setup} |")

    report_lines.extend(
        [
            "",
            "## Execution Checklist",
            "",
            "1. Refresh live quotes and option chains before entry.",
            "2. Check earnings dates; do not hold short-dated premium through unplanned earnings.",
            "3. Keep new risk inside 5% single-position and 30% options-allocation guardrails.",
            "4. Close short premium at ~50% profit or manage at 2x credit / short-strike breach.",
            "",
        ]
    )

    telegram_lines = [
        f"Altamira Trade Ideas — {as_of}",
        "",
        f"Portfolio: ${summary['total_value']:,.0f}; top-5 weight {summary['top5_weight']:.1f}%; tech/growth approx {summary['tech_weight']:.1f}%.",
        "",
        "Top ideas:",
    ]
    for idx, (idea, idea_type, rationale) in enumerate(top_ideas[:4], start=1):
        telegram_lines.append(f"{idx}. {idea} [{idea_type}]")
        telegram_lines.append(f"   {rationale}")
    telegram_lines.extend(
        [
            "",
            "Guardrails: verify live chain/liquidity/earnings; not financial advice.",
        ]
    )

    return "\n".join(report_lines), "\n".join(telegram_lines)


def write_report(content: str, as_of: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"trade-idea-generator-{as_of}.md"
    path.write_text(content, encoding="utf-8")
    return path


def send_telegram(message: str, token: str, chat_id: str) -> dict[str, object]:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": message[:4090],
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Altamira trade ideas from repository context.")
    parser.add_argument("--date", default=datetime.now(UTC).date().isoformat(), help="Report date, YYYY-MM-DD.")
    parser.add_argument("--send-telegram", action="store_true", help="Send concise summary to Telegram.")
    parser.add_argument("--chat-id", default=os.environ.get("TELEGRAM_CHAT_ID", ""), help="Telegram chat/channel ID.")
    parser.add_argument("--print-message", action="store_true", help="Print Telegram message to stdout.")
    args = parser.parse_args()

    if not PORTFOLIO_PATH.exists():
        print(f"Missing portfolio context: {PORTFOLIO_PATH}", file=sys.stderr)
        return 1
    if not WATCHLIST_PATH.exists():
        print(f"Missing watchlist context: {WATCHLIST_PATH}", file=sys.stderr)
        return 1

    positions = load_positions()
    options = load_options()
    watchlist = load_watchlist()
    if not positions:
        print("No portfolio positions parsed from context/portfolio-details.md", file=sys.stderr)
        return 1
    if not watchlist:
        print("No watchlist rows parsed from context/watchlist.md", file=sys.stderr)
        return 1

    report, telegram_message = build_report(positions, options, watchlist, args.date)
    report_path = write_report(report, args.date)
    print(f"Wrote {report_path.relative_to(WORKSPACE)}")

    if args.print_message:
        print("\n--- Telegram message ---\n")
        print(telegram_message)

    if args.send_telegram:
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        if not token:
            print("TELEGRAM_BOT_TOKEN is not set", file=sys.stderr)
            return 1
        if not args.chat_id:
            print("Telegram chat ID missing. Set TELEGRAM_CHAT_ID or pass --chat-id.", file=sys.stderr)
            return 1
        result = send_telegram(telegram_message, token, args.chat_id)
        if not result.get("ok"):
            print(f"Telegram send failed: {result}", file=sys.stderr)
            return 1
        message_id = result.get("result", {}).get("message_id", "unknown")
        print(f"Telegram message sent (message_id={message_id})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
