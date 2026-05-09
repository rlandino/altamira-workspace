#!/usr/bin/env python3
"""
Generate a daily trade idea memo from the repository portfolio/watchlist context.

The script intentionally uses the checked-in context files as the source of
truth. Live quote integrations can be layered on later, but the cron request
that triggers this command is specifically asking for the portfolio and
watchlist currently in the repository.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Optional

try:
    import requests
except ImportError:  # pragma: no cover - surfaced clearly at runtime
    requests = None


WORKSPACE = Path(__file__).resolve().parent.parent
CONTEXT = WORKSPACE / "context"
OUTPUTS = WORKSPACE / "outputs"


@dataclass(frozen=True)
class Position:
    symbol: str
    qty: float
    avg_price: Optional[float]
    current_price: Optional[float]
    market_value: Optional[float]
    pnl_pct: Optional[float]
    day_pct: Optional[float]
    weight_pct: Optional[float]


@dataclass(frozen=True)
class WatchlistEntry:
    ticker: str
    score: Optional[float]
    grade: str
    company: str
    status: str


@dataclass(frozen=True)
class OptionPosition:
    ticker: str
    strike: float
    option_type: str
    expiration: date
    credit: float
    current: float
    contracts: int


def parse_number(value: str) -> Optional[float]:
    """Parse a markdown table value like '$1,234', '+43.3%', or '—'."""
    cleaned = value.strip().replace("$", "").replace(",", "").replace("%", "")
    cleaned = cleaned.replace("+", "").replace("(", "").replace(")", "")
    cleaned = cleaned.replace("**", "").strip()
    if not cleaned or cleaned in {"—", "-", "N/A", "n/a"}:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def parse_int(value: str) -> int:
    parsed = parse_number(value)
    return int(parsed or 0)


def parse_percent(value: str) -> Optional[float]:
    """Parse the last percentage in a cell, e.g. '+$62,187 (+43.3%)' -> 43.3."""
    matches = re.findall(r"([+-]?\d+(?:\.\d+)?)\s*%", value)
    if not matches:
        return None
    try:
        return float(matches[-1])
    except ValueError:
        return None


def markdown_rows(path: Path, heading: str) -> list[list[str]]:
    """Return markdown table rows immediately following a given section heading."""
    rows: list[list[str]] = []
    in_section = False
    in_table = False

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            if in_section and in_table:
                break
            in_section = line.lower() == heading.lower()
            in_table = False
            continue
        if not in_section:
            continue
        if line.startswith("|") and line.endswith("|"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", cell) for cell in cells):
                continue
            rows.append(cells)
            in_table = True
        elif in_table and line:
            break

    if rows and all(cell.isupper() or cell.istitle() or cell for cell in rows[0]):
        return rows[1:]
    return rows


def read_positions(path: Path) -> list[Position]:
    positions: list[Position] = []
    for cells in markdown_rows(path, "## Current Positions (from app dashboard)"):
        if len(cells) < 9:
            continue
        symbol = cells[0].strip().upper()
        if symbol in {"SYMBOL", "TOTALS"}:
            continue
        positions.append(
            Position(
                symbol=symbol,
                qty=parse_number(cells[1]) or 0,
                avg_price=parse_number(cells[2]),
                current_price=parse_number(cells[3]),
                market_value=parse_number(cells[4]),
                pnl_pct=parse_percent(cells[6]),
                day_pct=parse_percent(cells[7]),
                weight_pct=parse_number(cells[8]),
            )
        )
    return positions


def read_watchlist(path: Path) -> list[WatchlistEntry]:
    entries: list[WatchlistEntry] = []
    for cells in markdown_rows(path, "## Watchlist Tickers"):
        if len(cells) < 5:
            continue
        ticker = cells[0].strip().upper()
        if ticker == "TICKER":
            continue
        entries.append(
            WatchlistEntry(
                ticker=ticker,
                score=parse_number(cells[1]),
                grade=cells[2].replace("*", "").strip(),
                company=cells[3].strip(),
                status=cells[4].replace("⭐", "").strip(),
            )
        )
    return entries


def read_options(path: Path) -> list[OptionPosition]:
    positions: list[OptionPosition] = []
    if not path.exists():
        return positions
    for cells in markdown_rows(path, "## Short Premium Positions"):
        if len(cells) < 7:
            continue
        try:
            expiration = datetime.strptime(cells[3].strip(), "%Y-%m-%d").date()
        except ValueError:
            continue
        positions.append(
            OptionPosition(
                ticker=cells[0].strip().upper(),
                strike=parse_number(cells[1]) or 0,
                option_type=cells[2].strip().title(),
                expiration=expiration,
                credit=parse_number(cells[4]) or 0,
                current=parse_number(cells[5]) or 0,
                contracts=parse_int(cells[6]),
            )
        )
    return positions


def grade_rank(grade: str) -> int:
    ranks = {
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
    return ranks.get(grade.upper(), 0)


def option_status(option: OptionPosition, spot: Optional[float], as_of: date) -> str:
    dte = (option.expiration - as_of).days
    if dte < 0:
        return f"Expired {abs(dte)} days ago; reconcile broker status before acting."
    if spot is None or spot <= 0:
        return f"{dte} DTE; spot unavailable in repository snapshot."
    if option.option_type == "Put":
        distance_pct = (spot - option.strike) / spot * 100
        if distance_pct >= 8:
            tone = "comfortably OTM"
        elif distance_pct >= 3:
            tone = "OTM but within monitoring range"
        elif distance_pct >= 0:
            tone = "near short strike"
        else:
            tone = "ITM / assignment-risk zone"
    else:
        distance_pct = (option.strike - spot) / spot * 100
        tone = "OTM" if distance_pct > 0 else "ITM / assignment-risk zone"
    pnl_per_contract = (option.credit - option.current) * 100
    pnl_total = pnl_per_contract * option.contracts
    return (
        f"{dte} DTE, {tone}, distance {distance_pct:.1f}%, "
        f"mark P/L about ${pnl_total:,.0f}."
    )


def sector_for(symbol: str) -> str:
    sectors = {
        "AAPL": "Mega-cap tech",
        "MSFT": "Mega-cap tech",
        "GOOGL": "Mega-cap tech",
        "AMZN": "Mega-cap tech",
        "META": "Mega-cap tech",
        "NVDA": "Semiconductors",
        "AVGO": "Semiconductors",
        "AMAT": "Semiconductors",
        "LRCX": "Semiconductors",
        "TSM": "Semiconductors",
        "KLAC": "Semiconductors",
        "ASML": "Semiconductors",
        "ADBE": "Software",
        "NOW": "Software",
        "CRWD": "Software",
        "PANW": "Software",
        "CRM": "Software",
        "CDNS": "Software",
        "COST": "Consumer staples",
        "WM": "Industrials",
        "GD": "Industrials",
        "JPM": "Financials",
        "V": "Payments",
        "MA": "Payments",
        "ABBV": "Healthcare",
        "LLY": "Healthcare",
        "SPY": "Index ETF",
        "QQQ": "Index ETF",
    }
    return sectors.get(symbol.upper(), "Other")


def summarize_sector_exposure(positions: Iterable[Position]) -> dict[str, float]:
    exposure: dict[str, float] = {}
    for pos in positions:
        if pos.weight_pct is None:
            continue
        exposure[sector_for(pos.symbol)] = exposure.get(sector_for(pos.symbol), 0.0) + pos.weight_pct
    return dict(sorted(exposure.items(), key=lambda item: item[1], reverse=True))


def build_report(
    positions: list[Position],
    watchlist: list[WatchlistEntry],
    options: list[OptionPosition],
    as_of: date,
) -> tuple[str, str]:
    positions_by_symbol = {position.symbol: position for position in positions}
    portfolio_value = sum(position.market_value or 0 for position in positions)
    overweight = [p for p in positions if (p.weight_pct or 0) >= 10]
    top_watchlist = sorted(
        [entry for entry in watchlist if entry.score is not None and grade_rank(entry.grade) >= grade_rank("B-")],
        key=lambda entry: entry.score or 0,
        reverse=True,
    )
    non_held_watchlist = [entry for entry in top_watchlist if entry.ticker not in positions_by_symbol]
    sector_exposure = summarize_sector_exposure(positions)
    active_options = sorted(options, key=lambda opt: opt.expiration)
    dated_title = f"Trade Idea Generator — {as_of.isoformat()}"

    lines: list[str] = [
        f"# {dated_title}",
        "",
        "Source: repository snapshots in `context/portfolio-details.md`, "
        "`context/options-positions.md`, and `context/watchlist.md`.",
        "",
        "> Execution note: this is a repo-snapshot idea memo, not a broker order ticket. "
        "Verify live quotes, option chains, earnings dates, liquidity, and account buying power before trading.",
        "",
        "## Portfolio Snapshot",
        "",
        f"- Positions parsed: {len(positions)}",
        f"- Approximate equity market value parsed: ${portfolio_value:,.0f}",
        f"- Watchlist entries parsed: {len(watchlist)}",
        f"- Short-premium rows parsed: {len(options)}",
        "",
        "### Top Weights",
        "",
        "| Symbol | Weight | Current | P&L | Day Change |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]

    for pos in sorted(positions, key=lambda p: p.weight_pct or 0, reverse=True)[:8]:
        lines.append(
            f"| {pos.symbol} | {pos.weight_pct or 0:.1f}% | "
            f"${pos.current_price or 0:,.2f} | {pos.pnl_pct or 0:+.1f}% | {pos.day_pct or 0:+.1f}% |"
        )

    lines.extend(["", "### Sector / Factor Concentration", ""])
    for sector, weight in list(sector_exposure.items())[:8]:
        flag = " - concentration flag" if weight >= 25 else ""
        lines.append(f"- {sector}: {weight:.1f}%{flag}")

    lines.extend(
        [
            "",
            "## Top Trade Ideas",
            "",
            "### 1) Risk-first portfolio overlay: write calls or trim concentrated winners",
            "",
        ]
    )
    if overweight:
        names = ", ".join(f"{p.symbol} ({p.weight_pct:.1f}%)" for p in overweight)
        lines.extend(
            [
                f"- Concentrated positions above 10% weight: {names}.",
                "- Idea: for holdings you are willing to reduce, sell 30-45 DTE covered calls around "
                "0.20 delta, or place staged trims back toward the target weight.",
                "- Priority: AVGO, GOOGL, AMAT, and SPY because they dominate portfolio risk. "
                "Avoid adding new semiconductor beta until the concentration is intentionally accepted.",
                "- Risk control: do not overwrite shares needed for long-term tax/conviction reasons; "
                "use limit orders and only sell calls at strikes where assignment is acceptable.",
            ]
        )
    else:
        lines.append("- No position is above 10% weight in the parsed repository snapshot.")

    lines.extend(
        [
            "",
            "### 2) Manage near-term short premium before adding new risk",
            "",
            "| Ticker | Contract | Status | Action Bias |",
            "| --- | --- | --- | --- |",
        ]
    )
    if active_options:
        for opt in active_options:
            spot = positions_by_symbol.get(opt.ticker, Position(opt.ticker, 0, None, None, None, None, None, None)).current_price
            dte = (opt.expiration - as_of).days
            if dte < 0:
                action = "Reconcile/close stale row"
            elif dte <= 10:
                action = "Monitor daily; close/roll if strike test or target profit"
            else:
                action = "Hold with normal risk checks"
            lines.append(
                f"| {opt.ticker} | {opt.expiration.isoformat()} {opt.strike:g}{opt.option_type[0]} x{opt.contracts} | "
                f"{option_status(opt, spot, as_of)} | {action} |"
            )
    else:
        lines.append("| - | - | No short-premium rows found. | - |")

    lines.extend(
        [
            "",
            "### 3) New watchlist entries: use defined-risk entries first",
            "",
            "| Rank | Ticker | Score | Grade | Status | Suggested Setup |",
            "| ---: | --- | ---: | --- | --- | --- |",
        ]
    )
    for idx, entry in enumerate(non_held_watchlist[:5], start=1):
        setup = "30-45 DTE bull put spread or 0.20-0.25 delta CSP after earnings check"
        if sector_for(entry.ticker) == "Semiconductors":
            setup = "Defined-risk bull put spread only unless semiconductor exposure is reduced"
        lines.append(
            f"| {idx} | {entry.ticker} | {entry.score:.1f} | {entry.grade} | {entry.status} | {setup} |"
        )
    if not non_held_watchlist:
        lines.append("| - | - | - | - | - | No B- or better non-held watchlist candidates found. |")

    avoided = [entry for entry in watchlist if entry.status.lower() == "avoid" or grade_rank(entry.grade) <= grade_rank("F")]
    lines.extend(
        [
            "",
            "### 4) No-trade / avoid list",
            "",
        ]
    )
    if avoided:
        lines.append(
            "- Keep out of the trade queue until re-scored or a thesis changes: "
            + ", ".join(f"{entry.ticker} ({entry.grade})" for entry in avoided)
            + "."
        )
    else:
        lines.append("- No avoid-rated names found in the parsed watchlist.")

    lines.extend(
        [
            "",
            "## Execution Checklist",
            "",
            "- Confirm market is open and use live bid/ask quotes.",
            "- Check earnings dates before any 30-45 DTE option sale.",
            "- Respect the risk framework: position size, sector concentration, options allocation, and cash reserve.",
            "- Prefer defined-risk spreads when VIX is elevated or when adding exposure to already concentrated sectors.",
            "- This output is educational and operational planning support, not individualized financial advice.",
            "",
        ]
    )

    telegram_lines = [
        f"TRADE IDEA GENERATOR - {as_of.isoformat()}",
        "Source: repo portfolio/watchlist snapshot. Verify live quotes before trading.",
        "",
        "Top ideas:",
    ]
    if overweight:
        telegram_lines.append(
            "1) Overlay/trim concentrated winners: "
            + ", ".join(f"{p.symbol} {p.weight_pct:.1f}%" for p in overweight[:4])
            + ". Use 30-45 DTE ~0.20 delta covered calls only where assignment is acceptable."
        )
    else:
        telegram_lines.append("1) No >10% single-position concentration found in the repo snapshot.")

    near_term_options = [opt for opt in active_options if (opt.expiration - as_of).days <= 10]
    if near_term_options:
        telegram_lines.append(
            "2) Manage near-term short puts before adding risk: "
            + ", ".join(f"{opt.ticker} {opt.strike:g}P {opt.expiration.isoformat()}" for opt in near_term_options[:4])
            + ". Close/roll if strike test or target profit; reconcile expired rows."
        )
    else:
        telegram_lines.append("2) No short-premium contracts inside 10 DTE in the repo snapshot.")

    if non_held_watchlist:
        telegram_lines.append(
            "3) Watchlist entry queue: "
            + ", ".join(f"{entry.ticker} {entry.grade}/{entry.score:.1f}" for entry in non_held_watchlist[:5])
            + ". Favor defined-risk spreads first, especially semis."
        )
    else:
        telegram_lines.append("3) No B- or better non-held watchlist candidates available.")

    if sector_exposure:
        top_sector, top_weight = next(iter(sector_exposure.items()))
        telegram_lines.extend(["", f"Risk flag: {top_sector} exposure is {top_weight:.1f}%."])
    telegram_lines.extend(
        [
            "Checklist: live quotes, earnings check, liquidity, buying power, position/sector limits.",
            "Not financial advice.",
        ]
    )

    return "\n".join(lines), "\n".join(telegram_lines)


def send_telegram(text: str, token: str, chat_id: str) -> None:
    if requests is None:
        raise RuntimeError("The requests package is required for Telegram delivery.")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    chunks = [text[i : i + 3500] for i in range(0, len(text), 3500)]
    for chunk in chunks:
        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": chunk,
                "disable_web_page_preview": True,
            },
            timeout=30,
        )
        if not response.ok:
            raise RuntimeError(f"Telegram send failed: HTTP {response.status_code} {response.text}")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate and optionally send daily trade ideas.")
    parser.add_argument("--portfolio", default=str(CONTEXT / "portfolio-details.md"))
    parser.add_argument("--watchlist", default=str(CONTEXT / "watchlist.md"))
    parser.add_argument("--options", default=str(CONTEXT / "options-positions.md"))
    parser.add_argument("--out", default="")
    parser.add_argument("--date", default=date.today().isoformat(), help="As-of date, YYYY-MM-DD.")
    parser.add_argument("--send-telegram", action="store_true", help="Send concise summary to Telegram.")
    parser.add_argument("--telegram-chat-id", default=os.environ.get("TELEGRAM_CHAT_ID", ""))
    parser.add_argument("--telegram-token-env", default="TELEGRAM_BOT_TOKEN")
    args = parser.parse_args(argv)

    try:
        as_of = datetime.strptime(args.date, "%Y-%m-%d").date()
    except ValueError:
        print("--date must be YYYY-MM-DD", file=sys.stderr)
        return 2

    portfolio_path = Path(args.portfolio)
    watchlist_path = Path(args.watchlist)
    options_path = Path(args.options)
    if not portfolio_path.exists():
        print(f"Portfolio file not found: {portfolio_path}", file=sys.stderr)
        return 1
    if not watchlist_path.exists():
        print(f"Watchlist file not found: {watchlist_path}", file=sys.stderr)
        return 1

    positions = read_positions(portfolio_path)
    watchlist = read_watchlist(watchlist_path)
    options = read_options(options_path)
    report, telegram_text = build_report(positions, watchlist, options, as_of)

    OUTPUTS.mkdir(exist_ok=True)
    out_path = Path(args.out) if args.out else OUTPUTS / f"trade-idea-generator-{as_of.isoformat()}.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"Wrote {out_path}")
    print("\n--- Telegram summary ---")
    print(telegram_text)

    if args.send_telegram:
        token = os.environ.get(args.telegram_token_env, "")
        if not token:
            print(f"{args.telegram_token_env} is not set; cannot send Telegram message.", file=sys.stderr)
            return 1
        if not args.telegram_chat_id:
            print("TELEGRAM_CHAT_ID or --telegram-chat-id is required for Telegram delivery.", file=sys.stderr)
            return 1
        send_telegram(telegram_text, token, args.telegram_chat_id)
        print("Telegram message sent.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
