#!/usr/bin/env python3
"""Generate a portfolio-aware trade idea and optionally send it to Telegram.

The command intentionally works from the repository's context files so it can
run in automation even when market-data credentials are unavailable.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_PATH = ROOT / "context" / "portfolio-details.md"
WATCHLIST_PATH = ROOT / "context" / "watchlist.md"
TELEGRAM_FALLBACK_PATH = ROOT / "outputs" / "csp-daily-scan-fixed.json"
OUTPUT_DIR = ROOT / "outputs"


BROAD_SECTOR = {
    "AAPL": "Technology",
    "ABT": "Healthcare",
    "ABBV": "Healthcare",
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
    "COST": "Consumer Staples",
    "CRM": "Technology",
    "CRWD": "Technology",
    "FFOLX": "Fund",
    "FICO": "Financials",
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

INDUSTRY = {
    "ADBE": "Software",
    "AMAT": "Semiconductor Equipment",
    "ASML": "Semiconductor Equipment",
    "AVGO": "Semiconductors",
    "KLAC": "Semiconductor Equipment",
    "LRCX": "Semiconductor Equipment",
    "NVDA": "Semiconductors",
    "TSM": "Semiconductors",
}


@dataclass(frozen=True)
class Position:
    symbol: str
    quantity: float
    current_price: float
    market_value: float
    weight: float
    pnl_percent: float | None


@dataclass(frozen=True)
class WatchlistCandidate:
    ticker: str
    score: float | None
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


def clean_cell(value: str) -> str:
    return (
        value.strip()
        .replace("**", "")
        .replace("<br>", " ")
        .replace("&nbsp;", " ")
    )


def split_markdown_row(line: str) -> list[str]:
    return [clean_cell(part) for part in line.strip().strip("|").split("|")]


def parse_number(value: str) -> float | None:
    text = clean_cell(value)
    text = text.replace("$", "").replace(",", "").replace("%", "")
    text = text.replace("+", "").strip()
    if text in {"", "-", "--", "—", "N/A"}:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return None
    return float(match.group(0))


def parse_positions(markdown: str) -> list[Position]:
    positions: list[Position] = []
    in_table = False
    for line in markdown.splitlines():
        if line.startswith("| SYMBOL | QTY |"):
            in_table = True
            continue
        if in_table and (not line.startswith("|") or line.startswith("|---")):
            if line.startswith("|---"):
                continue
            break
        if not in_table or not line.startswith("|"):
            continue

        cells = split_markdown_row(line)
        if len(cells) < 9 or cells[0].upper() in {"SYMBOL", "TOTALS:"}:
            continue
        symbol = cells[0].upper()
        quantity = parse_number(cells[1]) or 0.0
        current_price = parse_number(cells[3]) or 0.0
        market_value = parse_number(cells[4]) or 0.0
        weight = parse_number(cells[8]) or 0.0
        pnl_percent = None
        pnl_match = re.search(r"\(([-+]?\d+(?:\.\d+)?)%\)", cells[6])
        if pnl_match:
            pnl_percent = float(pnl_match.group(1))
        positions.append(
            Position(
                symbol=symbol,
                quantity=quantity,
                current_price=current_price,
                market_value=market_value,
                weight=weight,
                pnl_percent=pnl_percent,
            )
        )
    return positions


def parse_options(markdown: str, as_of: date) -> tuple[list[OptionPosition], list[OptionPosition]]:
    active: list[OptionPosition] = []
    expired: list[OptionPosition] = []
    in_table = False
    for line in markdown.splitlines():
        if line.startswith("| Ticker | Strike | Type | Expiration |"):
            in_table = True
            continue
        if in_table and (not line.startswith("|") or line.startswith("|---")):
            if line.startswith("|---"):
                continue
            break
        if not in_table or not line.startswith("|"):
            continue

        cells = split_markdown_row(line)
        if len(cells) < 7 or cells[0].lower() == "ticker":
            continue
        try:
            expiration = datetime.strptime(cells[3], "%Y-%m-%d").date()
        except ValueError:
            continue
        option = OptionPosition(
            ticker=cells[0].upper(),
            strike=parse_number(cells[1]) or 0.0,
            option_type=cells[2],
            expiration=expiration,
            credit=parse_number(cells[4]) or 0.0,
            current=parse_number(cells[5]) or 0.0,
            contracts=int(parse_number(cells[6]) or 0),
        )
        if expiration >= as_of:
            active.append(option)
        else:
            expired.append(option)
    return active, expired


def parse_watchlist(markdown: str) -> list[WatchlistCandidate]:
    candidates: list[WatchlistCandidate] = []
    in_table = False
    for line in markdown.splitlines():
        if line.startswith("| Ticker | Score | Grade | Company | Status |"):
            in_table = True
            continue
        if in_table and (not line.startswith("|") or line.startswith("|---")):
            if line.startswith("|---"):
                continue
            break
        if not in_table or not line.startswith("|"):
            continue

        cells = split_markdown_row(line)
        if len(cells) < 5 or cells[0].lower() == "ticker":
            continue
        candidates.append(
            WatchlistCandidate(
                ticker=cells[0].upper(),
                score=parse_number(cells[1]),
                grade=cells[2],
                company=cells[3],
                status=cells[4],
            )
        )
    candidates.sort(key=lambda item: item.score if item.score is not None else -1, reverse=True)
    return candidates


def get_portfolio_value(positions: Iterable[Position]) -> float:
    return sum(position.market_value for position in positions)


def sector_exposure(positions: Iterable[Position]) -> dict[str, float]:
    exposure: dict[str, float] = {}
    for position in positions:
        sector = BROAD_SECTOR.get(position.symbol, "Other")
        exposure[sector] = exposure.get(sector, 0.0) + position.weight
    return dict(sorted(exposure.items(), key=lambda item: item[1], reverse=True))


def select_watchlist_candidate(
    candidates: list[WatchlistCandidate],
    held_symbols: set[str],
    tech_weight: float,
) -> WatchlistCandidate | None:
    eligible = [
        candidate
        for candidate in candidates
        if candidate.ticker not in held_symbols
        and candidate.score is not None
        and "Avoid" not in candidate.status
        and candidate.grade not in {"D", "F"}
    ]
    if tech_weight >= 40:
        non_semi = [
            candidate
            for candidate in eligible
            if INDUSTRY.get(candidate.ticker, "") not in {"Semiconductors", "Semiconductor Equipment"}
        ]
        if non_semi:
            return non_semi[0]
    return eligible[0] if eligible else None


def money(value: float) -> str:
    return f"${value:,.0f}"


def percent(value: float) -> str:
    return f"{value:.1f}%"


def build_report(
    positions: list[Position],
    candidates: list[WatchlistCandidate],
    active_options: list[OptionPosition],
    expired_options: list[OptionPosition],
    as_of: date,
) -> tuple[str, str]:
    if not positions:
        raise ValueError(f"No positions found in {PORTFOLIO_PATH}")
    if not candidates:
        raise ValueError(f"No watchlist candidates found in {WATCHLIST_PATH}")

    portfolio_value = get_portfolio_value(positions)
    held_symbols = {position.symbol for position in positions}
    exposures = sector_exposure(positions)
    tech_weight = exposures.get("Technology", 0.0)
    oversized = [position for position in positions if position.weight >= 10.0]
    oversized.sort(key=lambda position: position.weight, reverse=True)
    top_candidate = select_watchlist_candidate(candidates, held_symbols, tech_weight)

    largest = oversized[0] if oversized else max(positions, key=lambda position: position.weight)
    trim_quantity = max(round(largest.quantity * 0.25), 1)
    trim_value = trim_quantity * largest.current_price
    post_value = max(largest.market_value - trim_value, 0.0)
    post_weight = (post_value / portfolio_value) * 100 if portfolio_value else 0.0

    candidate_line = "No eligible watchlist candidate found."
    candidate_action = "Keep proceeds in cash until the watchlist is refreshed."
    if top_candidate:
        candidate_sector = BROAD_SECTOR.get(top_candidate.ticker, "Other")
        candidate_industry = INDUSTRY.get(top_candidate.ticker, candidate_sector)
        starter_value = portfolio_value * 0.0075
        candidate_line = (
            f"{top_candidate.ticker} ({top_candidate.company}) - score "
            f"{top_candidate.score:.1f}, grade {top_candidate.grade}, "
            f"{candidate_industry}."
        )
        candidate_action = (
            f"Optional starter only after price/valuation refresh: cap at "
            f"0.75% of portfolio ({money(starter_value)})."
        )

    report_lines = [
        f"# Trade Idea Generator - {as_of.isoformat()}",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Data Source",
        "",
        f"- Portfolio: `{PORTFOLIO_PATH.relative_to(ROOT)}`",
        f"- Watchlist: `{WATCHLIST_PATH.relative_to(ROOT)}`",
        "- Market data: repository context only; verify live prices, spreads, liquidity, and tax impact before execution.",
        "",
        "## Portfolio Snapshot",
        "",
        f"- Portfolio market value parsed: {money(portfolio_value)}",
        f"- Largest weights: {', '.join(f'{p.symbol} {percent(p.weight)}' for p in oversized[:4])}",
        f"- Broad sector exposure: {', '.join(f'{sector} {percent(weight)}' for sector, weight in list(exposures.items())[:5])}",
        f"- Active short-premium rows in context: {len(active_options)}",
        f"- Expired option rows skipped: {len(expired_options)}",
        "",
        "## Primary Trade Idea",
        "",
        "**Risk-reduction rebalance before adding new tech exposure.**",
        "",
        (
            f"- Trim 25% of the largest overweight position: {largest.symbol} "
            f"({trim_quantity:,.0f} shares using the repository price "
            f"${largest.current_price:,.2f})."
        ),
        f"- Approximate proceeds: {money(trim_value)}.",
        f"- Estimated {largest.symbol} weight after trim: {percent(post_weight)} versus {percent(largest.weight)} now.",
        "- Keep proceeds in cash/T-bills until live market and tax checks confirm the next deployment.",
        "",
        "## Watchlist Deployment Candidate",
        "",
        f"- {candidate_line}",
        f"- {candidate_action}",
        (
            "- Reason: the portfolio is already concentrated in technology; "
            "new semiconductor exposure should wait until concentration is reduced."
        ),
        "",
        "## Risk Controls",
        "",
        "- Do not add to positions already above 10% weight without an explicit risk exception.",
        "- Refresh live quotes before acting; repository prices may be stale.",
        "- Re-check upcoming earnings before selling premium or opening a starter.",
        "- Treat this as an idea-generation output, not personalized financial advice.",
        "",
        "## Notes",
        "",
    ]

    if active_options:
        report_lines.append("Active option rows in context:")
        for option in active_options:
            report_lines.append(
                f"- {option.ticker} {option.strike:g}{option.option_type[0].upper()} "
                f"{option.expiration.isoformat()} x{option.contracts}"
            )
    else:
        report_lines.append("No active short-premium rows remain in the repository context as of the run date.")
    if expired_options:
        report_lines.append(
            f"Skipped expired option rows: {', '.join(f'{o.ticker} {o.expiration.isoformat()}' for o in expired_options)}."
        )

    telegram_lines = [
        f"TRADE IDEA - {as_of.isoformat()}",
        "",
        "Primary: risk-reduction rebalance before adding new tech exposure.",
        (
            f"Trim 25% of {largest.symbol}: {trim_quantity:,.0f} shares at repo "
            f"price ${largest.current_price:,.2f} = approx {money(trim_value)}."
        ),
        f"Estimated {largest.symbol} weight: {percent(largest.weight)} -> {percent(post_weight)}.",
        "",
        "Why:",
        f"- Portfolio parsed value: {money(portfolio_value)}",
        f"- Overweight names: {', '.join(f'{p.symbol} {percent(p.weight)}' for p in oversized[:4])}",
        f"- Tech exposure: {percent(tech_weight)}",
        "",
        f"Watchlist: {candidate_line}",
        candidate_action,
        "",
        f"Options context: {len(active_options)} active rows; {len(expired_options)} expired rows skipped.",
        "Verify live prices, spreads, earnings dates, liquidity, and tax impact before acting. Not financial advice.",
    ]

    return "\n".join(report_lines).rstrip() + "\n", "\n".join(telegram_lines).rstrip() + "\n"


def get_telegram_chat_id() -> str | None:
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if chat_id:
        return chat_id
    if not TELEGRAM_FALLBACK_PATH.exists():
        return None
    try:
        data = json.loads(TELEGRAM_FALLBACK_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    for node in data.get("nodes", []):
        params = node.get("parameters", {})
        raw_chat_id = params.get("chatId")
        if raw_chat_id:
            return str(raw_chat_id).lstrip("=")
    return None


def post_telegram_message(text: str) -> dict:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = get_telegram_chat_id()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    if not chat_id:
        raise RuntimeError("TELEGRAM_CHAT_ID is not set and fallback chat ID was not found")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Telegram request failed: {exc.reason}") from exc

    data = json.loads(response_body)
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {response_body}")
    return {
        "ok": True,
        "chat_id": chat_id,
        "message_id": data.get("result", {}).get("message_id"),
        "date": data.get("result", {}).get("date"),
    }


def run(send_telegram: bool, as_of: date) -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    portfolio_md = PORTFOLIO_PATH.read_text(encoding="utf-8")
    watchlist_md = WATCHLIST_PATH.read_text(encoding="utf-8")

    positions = parse_positions(portfolio_md)
    active_options, expired_options = parse_options(portfolio_md, as_of)
    candidates = parse_watchlist(watchlist_md)
    report, telegram_text = build_report(
        positions,
        candidates,
        active_options,
        expired_options,
        as_of,
    )

    report_path = OUTPUT_DIR / f"trade-idea-generator-{as_of.isoformat()}.md"
    telegram_path = OUTPUT_DIR / f"trade-idea-generator-telegram-{as_of.isoformat()}.txt"
    status_path = OUTPUT_DIR / f"trade-idea-generator-status-{as_of.isoformat()}.json"

    report_path.write_text(report, encoding="utf-8")
    telegram_path.write_text(telegram_text, encoding="utf-8")

    status = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "report_path": str(report_path.relative_to(ROOT)),
        "telegram_text_path": str(telegram_path.relative_to(ROOT)),
        "send_requested": send_telegram,
        "telegram": None,
    }
    if send_telegram:
        status["telegram"] = post_telegram_message(telegram_text)

    status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    status["status_path"] = str(status_path.relative_to(ROOT))
    return status


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--send-telegram",
        action="store_true",
        help="Send the generated trade idea to the configured Telegram channel.",
    )
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Run date in YYYY-MM-DD format; defaults to today.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        as_of = datetime.strptime(args.date, "%Y-%m-%d").date()
        status = run(send_telegram=args.send_telegram, as_of=as_of)
    except Exception as exc:
        print(f"trade_idea_generator error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
