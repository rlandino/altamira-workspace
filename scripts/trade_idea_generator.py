#!/usr/bin/env python3
"""Generate repository-based trade ideas and optionally send them to Telegram.

The generator intentionally uses the portfolio/watchlist context already stored
in this workspace. That keeps the daily cron useful even when live market-data
API keys are not present in the runtime environment.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

try:
    import requests
except ImportError:  # pragma: no cover - handled at runtime for clean CLI errors
    requests = None


WORKSPACE = Path(__file__).resolve().parent.parent
PORTFOLIO_PATH = WORKSPACE / "context" / "portfolio-details.md"
WATCHLIST_PATH = WORKSPACE / "context" / "watchlist.md"
OUTPUTS_DIR = WORKSPACE / "outputs"

STRICT_POSITION_LIMIT = 5.0
TACTICAL_POSITION_LIMIT = 10.0
SECTOR_LIMIT = 25.0

SECTOR_MAP = {
    "AAPL": "Technology",
    "ABBV": "Health Care",
    "ABT": "Health Care",
    "ACN": "Information Technology",
    "ADBE": "Software",
    "ADSK": "Software",
    "AMAT": "Semiconductors",
    "AMZN": "Consumer Discretionary",
    "ANET": "Information Technology",
    "ASML": "Semiconductors",
    "AVGO": "Semiconductors",
    "CDNS": "Software",
    "CMG": "Consumer Discretionary",
    "COST": "Consumer Staples",
    "CRM": "Software",
    "CRWD": "Software",
    "FFOLX": "Fund",
    "FICO": "Financial Technology",
    "GD": "Industrials",
    "GOOGL": "Communication Services",
    "INTU": "Software",
    "ISRG": "Health Care",
    "JPM": "Financials",
    "KLAC": "Semiconductors",
    "KMI": "Energy",
    "LLY": "Health Care",
    "LRCX": "Semiconductors",
    "MA": "Financial Technology",
    "MELI": "Consumer Discretionary",
    "META": "Communication Services",
    "MRVL": "Semiconductors",
    "MSCI": "Financial Technology",
    "MSFT": "Software",
    "NFLX": "Communication Services",
    "NOW": "Software",
    "NVDA": "Semiconductors",
    "PANW": "Software",
    "PLTR": "Software",
    "QQQ": "ETF",
    "SPGI": "Financials",
    "SPY": "ETF",
    "TSLA": "Consumer Discretionary",
    "TSM": "Semiconductors",
    "TMO": "Health Care",
    "V": "Financial Technology",
    "WM": "Industrials",
}


@dataclass(frozen=True)
class Position:
    symbol: str
    quantity: float
    current_price: float
    market_value: float
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

    @property
    def mark_vs_credit(self) -> float:
        if self.credit == 0:
            return 0.0
        return self.current / self.credit

    def is_expired(self, as_of: date) -> bool:
        """Return whether the option expiration is before the report date."""
        try:
            return date.fromisoformat(self.expiration) < as_of
        except ValueError:
            return False


@dataclass(frozen=True)
class WatchlistEntry:
    ticker: str
    score: float | None
    grade: str
    company: str
    status: str


def clean_cell(value: str) -> str:
    """Normalize a markdown table cell."""
    value = value.strip()
    value = value.replace("**", "")
    value = value.replace("⭐", "").strip()
    return value


def money_to_float(value: str) -> float:
    """Convert a currency-like string to a float."""
    cleaned = re.sub(r"[^0-9.\-]", "", value)
    return float(cleaned) if cleaned else 0.0


def pct_to_float(value: str) -> float:
    """Convert a percent-like string to a float."""
    cleaned = re.sub(r"[^0-9.\-]", "", value)
    return float(cleaned) if cleaned else 0.0


def split_markdown_row(line: str) -> list[str]:
    """Split a markdown table row into cells."""
    return [clean_cell(cell) for cell in line.strip().strip("|").split("|")]


def parse_portfolio(path: Path = PORTFOLIO_PATH) -> tuple[list[Position], list[OptionPosition], float]:
    """Parse portfolio and options tables from context/portfolio-details.md."""
    text = path.read_text(encoding="utf-8")
    positions: list[Position] = []
    options: list[OptionPosition] = []
    total_value = 0.0

    total_match = re.search(r"\*\*Total MKT VALUE\*\*\s*\|\s*\$?([0-9,]+)", text)
    if total_match:
        total_value = money_to_float(total_match.group(1))

    in_positions = False
    in_options = False
    for line in text.splitlines():
        if line.startswith("## Current Positions"):
            in_positions = True
            in_options = False
            continue
        if line.startswith("## Options / Short Premium Positions"):
            in_positions = False
            in_options = True
            continue
        if line.startswith("## ") and not line.startswith("## Options / Short Premium Positions"):
            if in_options:
                in_options = False

        if in_positions and line.startswith("|") and not re.match(r"^\|[-\s|]+$", line):
            cells = split_markdown_row(line)
            if not cells or cells[0] in {"SYMBOL", "Totals:"}:
                continue
            if len(cells) < 9:
                continue
            positions.append(
                Position(
                    symbol=cells[0].upper(),
                    quantity=money_to_float(cells[1]),
                    current_price=money_to_float(cells[3]),
                    market_value=money_to_float(cells[4]),
                    weight=pct_to_float(cells[8]),
                )
            )

        if in_options and line.startswith("|") and not re.match(r"^\|[-\s|]+$", line):
            cells = split_markdown_row(line)
            if not cells or cells[0] == "Ticker" or len(cells) < 7:
                continue
            options.append(
                OptionPosition(
                    ticker=cells[0].upper(),
                    strike=money_to_float(cells[1]),
                    option_type=cells[2],
                    expiration=cells[3],
                    credit=money_to_float(cells[4]),
                    current=money_to_float(cells[5]),
                    contracts=int(money_to_float(cells[6])),
                )
            )

    if not total_value and positions:
        total_value = sum(p.market_value for p in positions)
    return positions, options, total_value


def parse_watchlist(path: Path = WATCHLIST_PATH) -> list[WatchlistEntry]:
    """Parse the watchlist ticker table from context/watchlist.md."""
    entries: list[WatchlistEntry] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = split_markdown_row(line)
        if not cells or cells[0] in {"Ticker", "--------"} or len(cells) < 5:
            continue
        raw_score = cells[1]
        score = None if raw_score in {"-", "--", "—", ""} else money_to_float(raw_score)
        entries.append(
            WatchlistEntry(
                ticker=cells[0].upper(),
                score=score,
                grade=cells[2],
                company=cells[3],
                status=cells[4],
            )
        )
    return entries


def sector_weights(positions: Iterable[Position]) -> dict[str, float]:
    """Aggregate current weights by sector/theme."""
    weights: dict[str, float] = {}
    for position in positions:
        sector = SECTOR_MAP.get(position.symbol, "Other")
        weights[sector] = weights.get(sector, 0.0) + position.weight
    return dict(sorted(weights.items(), key=lambda item: item[1], reverse=True))


def fmt_money(value: float) -> str:
    """Format a dollar amount without cents."""
    return f"${value:,.0f}"


def fmt_pct(value: float) -> str:
    """Format a percentage with one decimal."""
    return f"{value:.1f}%"


def build_ideas(
    run_date: date,
    positions: list[Position],
    options: list[OptionPosition],
    watchlist: list[WatchlistEntry],
    total_value: float,
) -> list[dict[str, str]]:
    """Create ranked, repository-based trade ideas."""
    overweight = [p for p in positions if p.weight > TACTICAL_POSITION_LIMIT]
    strict_overweight = [p for p in positions if p.weight > STRICT_POSITION_LIMIT]
    active_options = [o for o in options if not o.is_expired(run_date)]
    expired_options = [o for o in options if o.is_expired(run_date)]
    underwater_options = [o for o in active_options if o.current > o.credit]
    profitable_options = [o for o in active_options if o.current <= o.credit]
    top_watchlist = [w for w in watchlist if w.score is not None and w.score >= 60]
    top_watchlist = sorted(top_watchlist, key=lambda w: w.score or 0.0, reverse=True)
    semis = [w for w in top_watchlist if SECTOR_MAP.get(w.ticker) == "Semiconductors"]
    non_semis = [w for w in top_watchlist if SECTOR_MAP.get(w.ticker) != "Semiconductors"]

    ideas: list[dict[str, str]] = []

    if overweight:
        names = ", ".join(f"{p.symbol} {fmt_pct(p.weight)}" for p in overweight)
        excess_to_tactical = sum(
            max(0.0, p.market_value - total_value * TACTICAL_POSITION_LIMIT / 100.0)
            for p in overweight
        )
        excess_to_strict = sum(
            max(0.0, p.market_value - total_value * STRICT_POSITION_LIMIT / 100.0)
            for p in strict_overweight
        )
        ideas.append(
            {
                "priority": "1",
                "title": "Risk-down overweight winners",
                "action": "Trim, collar, or sell covered calls before adding new long exposure.",
                "candidates": names,
                "rationale": (
                    f"{len(strict_overweight)} positions exceed the {fmt_pct(STRICT_POSITION_LIMIT)} "
                    f"single-position guardrail. Tactical excess above {fmt_pct(TACTICAL_POSITION_LIMIT)} "
                    f"is about {fmt_money(excess_to_tactical)}; strict excess is about {fmt_money(excess_to_strict)}."
                ),
                "risk_control": "Do not add correlated tech/semi exposure until position weights are back inside the chosen cap.",
            }
        )

    if expired_options:
        expired_rows = ", ".join(
            f"{o.ticker} {o.strike:g}{o.option_type[0].upper()} {o.expiration}"
            for o in expired_options
        )
        active_review_rows = ", ".join(
            f"{o.ticker} {o.strike:g}{o.option_type[0].upper()} {o.expiration} "
            f"mark {o.current:.2f} vs {o.credit:.2f} credit"
            for o in underwater_options
        )
        candidates = f"Expired rows: {expired_rows}"
        if active_review_rows:
            candidates += f"; active marks to verify: {active_review_rows}"
        ideas.append(
            {
                "priority": "2",
                "title": "Refresh stale options context",
                "action": "Refresh the portfolio export, then review any still-active short puts whose marks are above entry credit.",
                "candidates": candidates,
                "rationale": (
                    f"{len(expired_options)} option rows have expirations before {run_date.isoformat()}, "
                    "so the repository options snapshot needs verification before live option execution."
                ),
                "risk_control": "Refresh broker or Google Sheets context, then rerun options scans before entering or rolling premium trades.",
            }
        )
    elif underwater_options:
        problem_rows = ", ".join(
            f"{o.ticker} {o.strike:g}{o.option_type[0].upper()} {o.expiration} "
            f"mark {o.current:.2f} vs {o.credit:.2f} credit"
            for o in underwater_options
        )
        win_rows = ", ".join(
            f"{o.ticker} {o.strike:g}{o.option_type[0].upper()} mark {o.current:.2f} vs {o.credit:.2f} credit"
            for o in profitable_options
        )
        ideas.append(
            {
                "priority": "2",
                "title": "Short-premium triage",
                "action": "Review loss-control rules on short puts with marks above entry credit; harvest winners near 50% profit.",
                "candidates": problem_rows,
                "rationale": (
                    "Several short puts are marked above entry credit, so risk review should come before new premium sales. "
                    f"Current winners/less-stressed contracts: {win_rows or 'none'}."
                ),
                "risk_control": "Use the standing 50% profit / 200% credit stop framework; avoid adding contracts in the same correlated names.",
            }
        )

    if semis:
        semi_names = ", ".join(f"{w.ticker} {w.score:.1f} {w.grade}" for w in semis)
        current_semi_weight = sum(p.weight for p in positions if SECTOR_MAP.get(p.symbol) == "Semiconductors")
        ideas.append(
            {
                "priority": "3",
                "title": "Watchlist semiconductor entry only after risk budget is freed",
                "action": "Keep LRCX/NVDA/TSM/KLAC on the buy-list, but use starter sizing or cash-secured puts only after trimming existing semi winners.",
                "candidates": semi_names,
                "rationale": (
                    f"Top watchlist scores cluster in semiconductors while current semi exposure is {fmt_pct(current_semi_weight)} "
                    f"before including broad ETF overlap."
                ),
                "risk_control": f"Cap semiconductor exposure near {fmt_pct(SECTOR_LIMIT)} unless explicitly overriding the sector limit.",
            }
        )

    if non_semis:
        non_semi_names = ", ".join(f"{w.ticker} {w.score:.1f} {w.grade}" for w in non_semis)
        ideas.append(
            {
                "priority": "4",
                "title": "Diversifying watchlist starter",
                "action": "Prefer a small starter or put-sale setup in the highest-scored non-semi candidate.",
                "candidates": non_semi_names,
                "rationale": "This adds watchlist quality without increasing the already crowded semiconductor sleeve.",
                "risk_control": "Starter size 1-2% until the name earns a higher conviction score and the portfolio has available risk budget.",
            }
        )

    covered_call_candidates = [
        p
        for p in positions
        if p.quantity >= 100 and p.weight >= 4.0 and p.symbol not in {"FFOLX"}
    ]
    if covered_call_candidates:
        candidates = ", ".join(f"{p.symbol} {int(p.quantity)} sh" for p in covered_call_candidates[:8])
        ideas.append(
            {
                "priority": "5",
                "title": "Covered-call income on large share lots",
                "action": "For shares you are willing to trim, price 30-45 DTE calls around 0.20 delta instead of deploying new cash.",
                "candidates": candidates,
                "rationale": "This monetizes existing long exposure while naturally reducing oversized positions if called away.",
                "risk_control": "Only sell calls at strikes where assignment is acceptable; skip around earnings if the call caps desired upside.",
            }
        )

    return ideas


def markdown_table(rows: list[list[str]]) -> str:
    """Render a compact markdown table."""
    if not rows:
        return ""
    header = rows[0]
    sep = ["---"] * len(header)
    rendered = ["| " + " | ".join(header) + " |", "| " + " | ".join(sep) + " |"]
    for row in rows[1:]:
        rendered.append("| " + " | ".join(row) + " |")
    return "\n".join(rendered)


def build_report(
    run_date: str,
    positions: list[Position],
    options: list[OptionPosition],
    watchlist: list[WatchlistEntry],
    total_value: float,
    ideas: list[dict[str, str]],
) -> str:
    """Build the markdown report."""
    sectors = sector_weights(positions)
    top_positions = sorted(positions, key=lambda p: p.weight, reverse=True)[:10]
    top_watchlist = sorted(
        [w for w in watchlist if w.score is not None],
        key=lambda w: w.score or 0.0,
        reverse=True,
    )[:10]
    avoid_watchlist = [w for w in watchlist if "avoid" in w.status.lower() or w.grade.upper() == "F"]

    idea_rows = [["Priority", "Idea", "Action", "Candidates", "Risk Control"]]
    for idea in ideas:
        idea_rows.append(
            [
                idea["priority"],
                idea["title"],
                idea["action"],
                idea["candidates"],
                idea["risk_control"],
            ]
        )

    position_rows = [["Symbol", "Weight", "Market Value", "Sector/Theme"]]
    for position in top_positions:
        position_rows.append(
            [
                position.symbol,
                fmt_pct(position.weight),
                fmt_money(position.market_value),
                SECTOR_MAP.get(position.symbol, "Other"),
            ]
        )

    sector_rows = [["Sector/Theme", "Weight", "Limit Check"]]
    for sector, weight in sectors.items():
        check = "BREACH" if sector not in {"ETF", "Fund"} and weight > SECTOR_LIMIT else "OK"
        sector_rows.append([sector, fmt_pct(weight), check])

    watch_rows = [["Ticker", "Score", "Grade", "Status", "Theme"]]
    for entry in top_watchlist:
        watch_rows.append(
            [
                entry.ticker,
                f"{entry.score:.1f}" if entry.score is not None else "N/A",
                entry.grade,
                entry.status,
                SECTOR_MAP.get(entry.ticker, "Other"),
            ]
        )

    option_rows = [["Ticker", "Contract", "Credit", "Current", "Status"]]
    as_of = date.fromisoformat(run_date)
    for option in options:
        if option.is_expired(as_of):
            status = "Expired/stale in repository"
        elif option.current <= option.credit * 0.5:
            status = "Profit target zone"
        elif option.current > option.credit * 2:
            status = "Stop-review zone"
        elif option.current > option.credit:
            status = "Underwater - monitor"
        else:
            status = "Working"
        option_rows.append(
            [
                option.ticker,
                f"{option.strike:g}{option.option_type[0].upper()} {option.expiration}",
                f"{option.credit:.2f}",
                f"{option.current:.2f}",
                status,
            ]
        )

    avoid_text = ", ".join(f"{w.ticker} ({w.grade}, {w.status})" for w in avoid_watchlist) or "None flagged"

    lines = [
        f"# Trade Idea Generator - {run_date}",
        "",
        "Repository-based scan of the current Altamira portfolio and watchlist.",
        "",
        "## Source Files",
        "",
        f"- Portfolio: `{PORTFOLIO_PATH.relative_to(WORKSPACE)}`",
        f"- Watchlist: `{WATCHLIST_PATH.relative_to(WORKSPACE)}`",
        "- Market data: static repository snapshot; no live quote API was required for this run.",
        "",
        "## Portfolio Snapshot",
        "",
        f"- Total market value: **{fmt_money(total_value)}**",
        f"- Equity/fund positions parsed: **{len(positions)}**",
        f"- Short-premium positions parsed: **{len(options)}**",
        f"- Single-position guardrail: **{fmt_pct(STRICT_POSITION_LIMIT)}** strict / **{fmt_pct(TACTICAL_POSITION_LIMIT)}** tactical",
        f"- Sector guardrail: **{fmt_pct(SECTOR_LIMIT)}**",
        "",
        markdown_table(position_rows),
        "",
        "## Sector / Theme Exposure",
        "",
        markdown_table(sector_rows),
        "",
        "## Ranked Trade Ideas",
        "",
        markdown_table(idea_rows),
        "",
        "## Short-Premium Review",
        "",
        markdown_table(option_rows),
        "",
        "## Watchlist Ranking",
        "",
        markdown_table(watch_rows),
        "",
        "## Avoid / Low Priority Flags",
        "",
        f"- {avoid_text}",
        "",
        "## Execution Notes",
        "",
        "- Treat these as idea-generation outputs, not trade orders.",
        "- Confirm live prices, bid/ask spreads, earnings dates, and portfolio cash before placing trades.",
        "- For options, verify the chain and follow the standing 50% profit / 200% credit stop framework.",
        "- Financial calculations are based on static repository data and may be stale.",
        "",
        "## Disclaimer",
        "",
        "This report is for research and workflow automation only. It is not financial advice or a recommendation to buy, sell, or hold any security.",
        "",
    ]
    return "\n".join(lines)


def build_telegram_message(
    run_date: str,
    positions: list[Position],
    options: list[OptionPosition],
    watchlist: list[WatchlistEntry],
    total_value: float,
    ideas: list[dict[str, str]],
    report_path: Path,
) -> str:
    """Build a concise Telegram-ready summary."""
    top_positions = sorted(positions, key=lambda p: p.weight, reverse=True)[:4]
    top_watchlist = sorted(
        [w for w in watchlist if w.score is not None],
        key=lambda w: w.score or 0.0,
        reverse=True,
    )[:5]
    as_of = date.fromisoformat(run_date)
    expired_options = [o for o in options if o.is_expired(as_of)]
    underwater_options = [o for o in options if not o.is_expired(as_of) and o.current > o.credit]

    lines = [
        f"ALTAMIRA TRADE IDEAS - {run_date}",
        "",
        f"Source: repo portfolio + watchlist snapshot ({fmt_money(total_value)} portfolio).",
        "Not trade orders; verify live prices/chain before execution.",
        "",
        "Top exposures:",
        ", ".join(f"{p.symbol} {fmt_pct(p.weight)}" for p in top_positions),
        "",
        "Today's priorities:",
    ]
    for idea in ideas[:5]:
        lines.append(f"{idea['priority']}) {idea['title']}")
        lines.append(f"   Action: {idea['action']}")
        lines.append(f"   Names: {idea['candidates']}")

    if expired_options:
        lines.extend(
            [
                "",
                "Options context:",
                f"{len(expired_options)} listed option rows are expired/stale in the repo snapshot. Refresh positions before trading options.",
            ]
        )
        if underwater_options:
            lines.append(
                "Active marks to verify after refresh: "
                + ", ".join(
                    f"{o.ticker} {o.strike:g}{o.option_type[0].upper()} {o.current:.2f} vs {o.credit:.2f}"
                    for o in underwater_options
                )
            )
    elif underwater_options:
        lines.extend(
            [
                "",
                "Options requiring review:",
                ", ".join(
                    f"{o.ticker} {o.strike:g}{o.option_type[0].upper()} {o.current:.2f} vs {o.credit:.2f}"
                    for o in underwater_options
                ),
            ]
        )

    lines.extend(
        [
            "",
            "Top watchlist:",
            ", ".join(f"{w.ticker} {w.score:.1f} {w.grade}" for w in top_watchlist),
            "",
            f"Report: {report_path.relative_to(WORKSPACE)}",
            "",
            "Disclaimer: research automation only, not financial advice.",
        ]
    )
    return "\n".join(lines)


def write_output(run_date: str, report: str) -> Path:
    """Write the markdown report and return its path."""
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUTS_DIR / f"trade-idea-generator-{run_date}.md"
    path.write_text(report, encoding="utf-8")
    return path


def send_telegram(message: str, bot_token: str, chat_id: str) -> None:
    """Send a plain-text Telegram message."""
    if requests is None:
        raise RuntimeError("The requests package is required for Telegram delivery.")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "disable_web_page_preview": True,
    }
    response = requests.post(url, json=payload, timeout=20)
    try:
        body = response.json()
    except ValueError:
        body = {"description": response.text}
    if response.status_code >= 400 or not body.get("ok", False):
        description = html.unescape(str(body.get("description", response.text)))
        raise RuntimeError(f"Telegram delivery failed: {description}")


def positive_date(value: str) -> str:
    """Validate an ISO date string for argparse."""
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Date must be YYYY-MM-DD") from exc
    return value


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate trade ideas from repository portfolio/watchlist data.",
    )
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        type=positive_date,
        help="Report date in YYYY-MM-DD format. Defaults to today.",
    )
    parser.add_argument(
        "--send-telegram",
        action="store_true",
        help="Send the generated summary to Telegram.",
    )
    parser.add_argument(
        "--telegram-chat-id",
        default=os.environ.get("TELEGRAM_CHAT_ID"),
        help="Telegram chat/channel id. Defaults to TELEGRAM_CHAT_ID.",
    )
    parser.add_argument(
        "--telegram-token-env",
        default="TELEGRAM_BOT_TOKEN",
        help="Environment variable containing the Telegram bot token.",
    )
    parser.add_argument(
        "--print-message",
        action="store_true",
        help="Print the Telegram summary to stdout.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    positions, options, total_value = parse_portfolio()
    watchlist = parse_watchlist()
    if not positions:
        print(f"ERROR: No portfolio positions found in {PORTFOLIO_PATH}", file=sys.stderr)
        return 1
    if not watchlist:
        print(f"ERROR: No watchlist entries found in {WATCHLIST_PATH}", file=sys.stderr)
        return 1

    report_date = date.fromisoformat(args.date)
    ideas = build_ideas(report_date, positions, options, watchlist, total_value)
    report = build_report(args.date, positions, options, watchlist, total_value, ideas)
    report_path = write_output(args.date, report)
    telegram_message = build_telegram_message(
        args.date,
        positions,
        options,
        watchlist,
        total_value,
        ideas,
        report_path,
    )

    print(f"Report written: {report_path.relative_to(WORKSPACE)}")

    if args.print_message:
        print("\n--- Telegram Message ---")
        print(telegram_message)

    if args.send_telegram:
        token = os.environ.get(args.telegram_token_env)
        if not token:
            print(
                f"ERROR: {args.telegram_token_env} is not set; cannot send Telegram message.",
                file=sys.stderr,
            )
            return 1
        if not args.telegram_chat_id:
            print(
                "ERROR: Telegram chat id missing. Set TELEGRAM_CHAT_ID or pass --telegram-chat-id.",
                file=sys.stderr,
            )
            return 1
        send_telegram(telegram_message, token, args.telegram_chat_id)
        print("Telegram message sent.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
