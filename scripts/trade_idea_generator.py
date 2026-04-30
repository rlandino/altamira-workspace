#!/usr/bin/env python3
"""Generate repo-context trade ideas and optionally send them to Telegram."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


WORKSPACE = Path(__file__).resolve().parents[1]
PORTFOLIO_PATH = WORKSPACE / "context" / "portfolio-details.md"
WATCHLIST_PATH = WORKSPACE / "context" / "watchlist.md"
OUTPUT_DIR = WORKSPACE / "outputs"
DEFAULT_CHAT_ID = "7830722515"


SECTOR_MAP = {
    "AAPL": "Technology",
    "MSFT": "Technology",
    "GOOGL": "Communication Services",
    "AMAT": "Technology",
    "AVGO": "Technology",
    "CRWD": "Technology",
    "NOW": "Technology",
    "SPGI": "Financials",
    "V": "Financials",
    "JPM": "Financials",
    "COST": "Consumer Staples",
    "AMZN": "Consumer Discretionary",
    "ABBV": "Health Care",
    "GD": "Industrials",
    "KMI": "Energy",
    "WM": "Industrials",
    "SPY": "Index",
    "QQQ": "Index",
    "LRCX": "Technology",
    "NVDA": "Technology",
    "TSM": "Technology",
    "KLAC": "Technology",
    "ADBE": "Technology",
    "ASML": "Technology",
    "LLY": "Health Care",
    "ACN": "Technology",
    "INTU": "Technology",
}


@dataclass
class Position:
    ticker: str
    quantity: float
    average_price: float
    current_price: float
    market_value: float
    cost_basis: float
    pnl_pct: float
    weight_pct: float


@dataclass
class OptionPosition:
    ticker: str
    strike: float
    option_type: str
    expiration: dt.date
    credit: float
    current: float
    contracts: int


@dataclass
class WatchlistEntry:
    ticker: str
    score: Optional[float]
    grade: str
    company: str
    status: str


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing required context file: {path}")
    return path.read_text(encoding="utf-8")


def parse_money(value: str) -> float:
    clean = value.replace("$", "").replace(",", "").replace("%", "").strip()
    if clean in {"", "-", "\u2014"}:
        return 0.0
    return float(clean)


def parse_pct_from_pnl(value: str) -> float:
    match = re.search(r"\(([+-]?[0-9.]+)%\)", value)
    return float(match.group(1)) if match else 0.0


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def iter_table_rows(text: str, header_startswith: str) -> Iterable[list[str]]:
    lines = text.splitlines()
    in_table = False
    for line in lines:
        if line.startswith(header_startswith):
            in_table = True
            continue
        if not in_table:
            continue
        if line.startswith("|---") or line.startswith("|--------"):
            continue
        if not line.startswith("|"):
            if in_table:
                break
            continue
        yield split_markdown_row(line)


def parse_positions(text: str) -> list[Position]:
    positions: list[Position] = []
    for row in iter_table_rows(text, "| SYMBOL |"):
        if len(row) < 9 or row[0].lower() in {"totals", "symbol"}:
            continue
        ticker = row[0].upper()
        if ticker == "SYMBOL":
            continue
        try:
            positions.append(
                Position(
                    ticker=ticker,
                    quantity=parse_money(row[1]),
                    average_price=parse_money(row[2]),
                    current_price=parse_money(row[3]),
                    market_value=parse_money(row[4]),
                    cost_basis=parse_money(row[5]),
                    pnl_pct=parse_pct_from_pnl(row[6]),
                    weight_pct=parse_money(row[8]),
                )
            )
        except (ValueError, IndexError):
            continue
    return positions


def parse_option_positions(text: str) -> list[OptionPosition]:
    options: list[OptionPosition] = []
    for row in iter_table_rows(text, "| Ticker | Strike |"):
        if len(row) < 7 or row[0].lower() == "ticker":
            continue
        try:
            options.append(
                OptionPosition(
                    ticker=row[0].upper(),
                    strike=parse_money(row[1]),
                    option_type=row[2],
                    expiration=dt.date.fromisoformat(row[3]),
                    credit=parse_money(row[4]),
                    current=parse_money(row[5]),
                    contracts=int(parse_money(row[6])),
                )
            )
        except (ValueError, IndexError):
            continue
    return options


def parse_watchlist(text: str) -> list[WatchlistEntry]:
    entries: list[WatchlistEntry] = []
    for row in iter_table_rows(text, "| Ticker | Score |"):
        if len(row) < 5 or row[0].lower() == "ticker":
            continue
        score = None
        if row[1] not in {"\u2014", "-", ""}:
            try:
                score = float(row[1])
            except ValueError:
                score = None
        entries.append(
            WatchlistEntry(
                ticker=row[0].upper(),
                score=score,
                grade=row[2].replace("*", ""),
                company=row[3],
                status=ascii_clean(row[4]),
            )
        )
    return entries


def ascii_clean(value: str) -> str:
    replacements = {
        "\u2b50": "Top",
        "\u2014": "-",
        "\u2013": "-",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value.encode("ascii", errors="ignore").decode("ascii").strip()


def extract_snapshot_date(text: str) -> Optional[str]:
    match = re.search(r"\| Date \| ([0-9]{4}-[0-9]{2}-[0-9]{2}) \|", text)
    return match.group(1) if match else None


def next_friday_near(target_dte: int, today: dt.date) -> dt.date:
    target = today + dt.timedelta(days=target_dte)
    days_until_friday = (4 - target.weekday()) % 7
    return target + dt.timedelta(days=days_until_friday)


def round_strike(price: float, direction: str) -> int:
    if price >= 500:
        increment = 10
    elif price >= 100:
        increment = 5
    else:
        increment = 1
    raw = price / increment
    if direction == "up":
        rounded = int(raw + 0.9999) * increment
    else:
        rounded = int(raw) * increment
    return max(increment, rounded)


def build_covered_call_ideas(positions: list[Position], expiration: dt.date) -> list[dict]:
    candidates = [
        p
        for p in positions
        if p.quantity >= 100
        and p.current_price > 0
        and p.ticker not in {"FFOLX"}
        and p.pnl_pct > 15
    ]
    candidates.sort(key=lambda p: (p.weight_pct, p.pnl_pct), reverse=True)
    ideas = []
    for p in candidates[:4]:
        contracts = min(int(p.quantity // 100), 3 if p.weight_pct >= 10 else 1)
        target_strike = round_strike(p.current_price * 1.08, "up")
        ideas.append(
            {
                "type": "Covered call / trim overlay",
                "ticker": p.ticker,
                "action": f"Sell up to {contracts} {p.ticker} {target_strike}C exp {expiration.isoformat()}",
                "rationale": (
                    f"{p.weight_pct:.1f}% portfolio weight, {p.pnl_pct:+.1f}% unrealized gain; "
                    "monetize upside while keeping most shares invested."
                ),
                "risk": "Only sell calls on shares you are willing to trim if assigned.",
            }
        )
    return ideas


def build_csp_management_ideas(
    positions: list[Position], options: list[OptionPosition], today: dt.date
) -> list[dict]:
    price_by_ticker = {p.ticker: p.current_price for p in positions}
    ideas: list[dict] = []
    active_options = [o for o in options if o.expiration >= today]
    for option in active_options:
        current_price = price_by_ticker.get(option.ticker)
        if current_price is None:
            continue
        moneyness = current_price / option.strike if option.strike else 0
        if option.current >= option.credit * 1.5 or moneyness < 1.03:
            ideas.append(
                {
                    "type": "Short put risk management",
                    "ticker": option.ticker,
                    "action": (
                        f"Review {option.contracts}x short {option.ticker} "
                        f"{option.strike:g}P exp {option.expiration.isoformat()}"
                    ),
                    "rationale": (
                        f"Mark ${option.current:.2f} vs ${option.credit:.2f} credit; "
                        f"underlying ${current_price:.2f}."
                    ),
                    "risk": "Close/roll per rules if loss reaches 2x credit or assignment is not desired.",
                }
            )
    return ideas[:3]


def build_watchlist_ideas(watchlist: list[WatchlistEntry], held_tickers: set[str]) -> list[dict]:
    candidates = [
        w
        for w in watchlist
        if w.score is not None and w.score >= 58 and w.ticker not in held_tickers
    ]
    candidates.sort(key=lambda w: w.score or 0, reverse=True)
    ideas = []
    for w in candidates[:5]:
        ideas.append(
            {
                "type": "Watchlist entry candidate",
                "ticker": w.ticker,
                "action": f"Run /options-scan {w.ticker}; target 0.20-0.30 delta put, 30-45 DTE.",
                "rationale": f"{w.company} is scored {w.score:.1f} ({w.grade}) and marked {w.status}.",
                "risk": "Do not sell premium through earnings; keep cash-secured or defined-risk sizing.",
            }
        )
    return ideas


def summarize_sector_exposure(positions: list[Position]) -> list[tuple[str, float]]:
    exposure: dict[str, float] = {}
    for p in positions:
        sector = SECTOR_MAP.get(p.ticker, "Other")
        exposure[sector] = exposure.get(sector, 0.0) + p.weight_pct
    return sorted(exposure.items(), key=lambda item: item[1], reverse=True)


def format_idea(idea: dict, index: int) -> str:
    return textwrap.dedent(
        f"""\
        {index}. {idea['ticker']} - {idea['type']}
           Action: {idea['action']}
           Rationale: {idea['rationale']}
           Risk: {idea['risk']}
        """
    ).rstrip()


def build_report(
    positions: list[Position],
    options: list[OptionPosition],
    watchlist: list[WatchlistEntry],
    snapshot_date: Optional[str],
    today: dt.date,
) -> tuple[str, str]:
    expiration = next_friday_near(42, today)
    held_tickers = {p.ticker for p in positions}
    covered_calls = build_covered_call_ideas(positions, expiration)
    csp_management = build_csp_management_ideas(positions, options, today)
    watchlist_entries = build_watchlist_ideas(watchlist, held_tickers)
    top_ideas = (covered_calls + csp_management + watchlist_entries)[:8]
    sector_exposure = summarize_sector_exposure(positions)
    expired_options = [o for o in options if o.expiration < today]

    lines = [
        f"# Trade Idea Generator - {today.isoformat()}",
        "",
        "> Source: repository context files (`context/portfolio-details.md` and `context/watchlist.md`).",
        "> This is not financial advice. Verify live prices, option chains, earnings dates, liquidity, and account constraints before trading.",
        "",
        "## Context Check",
        "",
        f"- Portfolio snapshot date in repo: {snapshot_date or 'unknown'}",
        f"- Equity positions parsed: {len(positions)}",
        f"- Watchlist entries parsed: {len(watchlist)}",
        f"- Option rows parsed: {len(options)}",
        f"- Target option idea expiration: {expiration.isoformat()} (weekly/monthly availability must be verified)",
        "",
        "## Portfolio Exposure Snapshot",
        "",
    ]
    for sector, weight in sector_exposure[:6]:
        lines.append(f"- {sector}: {weight:.1f}%")

    if expired_options:
        lines.extend(
            [
                "",
                "## Data Freshness Flags",
                "",
                f"- {len(expired_options)} option row(s) have expirations before {today.isoformat()}; refresh `context/options-positions.md` before acting on options-management rows.",
            ]
        )

    lines.extend(["", "## Top Trade Ideas", ""])
    if not top_ideas:
        lines.append("No trade ideas generated from the current repository context.")
    else:
        for idx, idea in enumerate(top_ideas, start=1):
            lines.append(format_idea(idea, idx))
            lines.append("")

    lines.extend(
        [
            "## Execution Checklist",
            "",
            "- Confirm latest quote and bid/ask spread before order entry.",
            "- Confirm no earnings event falls inside the option holding window.",
            "- Keep any new options exposure inside the 30% options allocation cap.",
            "- Close short premium at 50% profit; stop/roll around 200% of credit or short-strike breach.",
        ]
    )

    telegram_lines = [
        f"TRADE IDEA GENERATOR - {today.isoformat()}",
        f"Repo portfolio snapshot: {snapshot_date or 'unknown'}",
        "",
        "Top ideas:",
    ]
    if not top_ideas:
        telegram_lines.append("No ideas generated from repository context.")
    else:
        for idx, idea in enumerate(top_ideas[:6], start=1):
            telegram_lines.append(
                f"{idx}) {idea['ticker']} - {idea['type']}\n"
                f"   {idea['action']}\n"
                f"   Why: {idea['rationale']}"
            )
    if expired_options:
        telegram_lines.extend(
            [
                "",
                f"Freshness flag: {len(expired_options)} option row(s) are expired vs today; refresh option context before acting.",
            ]
        )
    telegram_lines.extend(
        [
            "",
            "Verify live prices, chains, earnings, and risk limits before trading. Not financial advice.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n", "\n".join(telegram_lines).rstrip()


def write_report(report: str, today: dt.date) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"trade-idea-generator-{today.isoformat()}.md"
    path.write_text(report, encoding="utf-8")
    return path


def split_telegram_message(message: str, limit: int = 3900) -> list[str]:
    if len(message) <= limit:
        return [message]
    chunks: list[str] = []
    remaining = message
    while len(remaining) > limit:
        split_at = remaining.rfind("\n", 0, limit)
        if split_at < limit // 2:
            split_at = limit
        chunks.append(remaining[:split_at].rstrip())
        remaining = remaining[split_at:].lstrip()
    if remaining:
        chunks.append(remaining)
    return chunks


def send_telegram(message: str, token: str, chat_id: str) -> list[dict]:
    responses: list[dict] = []
    for chunk in split_telegram_message(message):
        payload = urllib.parse.urlencode(
            {
                "chat_id": chat_id,
                "text": chunk,
                "disable_web_page_preview": "true",
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Telegram send failed: HTTP {exc.code}: {detail}") from exc
        responses.append(json.loads(raw))
    return responses


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=dt.date.today().isoformat(), help="Run date (YYYY-MM-DD).")
    parser.add_argument("--send-telegram", action="store_true", help="Send concise report to Telegram.")
    parser.add_argument("--telegram-token", default=os.environ.get("TELEGRAM_BOT_TOKEN", ""))
    parser.add_argument(
        "--telegram-chat-id",
        default=os.environ.get("TELEGRAM_CHAT_ID")
        or os.environ.get("ALTAMIRA_TELEGRAM_CHAT_ID")
        or DEFAULT_CHAT_ID,
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    today = dt.date.fromisoformat(args.date)

    portfolio_text = read_text(PORTFOLIO_PATH)
    watchlist_text = read_text(WATCHLIST_PATH)
    positions = parse_positions(portfolio_text)
    options = parse_option_positions(portfolio_text)
    watchlist = parse_watchlist(watchlist_text)
    snapshot_date = extract_snapshot_date(portfolio_text)

    report, telegram_message = build_report(positions, options, watchlist, snapshot_date, today)
    report_path = write_report(report, today)
    print(f"Wrote report: {report_path.relative_to(WORKSPACE)}")

    if args.send_telegram:
        if not args.telegram_token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is required when --send-telegram is used.")
        responses = send_telegram(telegram_message, args.telegram_token, args.telegram_chat_id)
        message_ids = [
            str(response.get("result", {}).get("message_id", "unknown"))
            for response in responses
            if response.get("ok")
        ]
        print(f"Sent Telegram message(s): {', '.join(message_ids) or 'unknown'}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
