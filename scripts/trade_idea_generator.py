#!/usr/bin/env python3
"""Generate Altamira trade ideas from the current portfolio and watchlist.

The script is intentionally data-light: it uses repository context as the
source of truth and optionally enriches with FMP quotes when FMP_API_KEY is set.
It writes a dated report, a Telegram message preview, and a Telegram send status.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

try:
    import requests
except ImportError:  # pragma: no cover - surfaced as a runtime setup issue.
    requests = None


WORKSPACE = Path(__file__).resolve().parent.parent
PORTFOLIO_PATH = WORKSPACE / "context" / "portfolio-details.md"
WATCHLIST_PATH = WORKSPACE / "context" / "watchlist.md"
OUTPUTS_DIR = WORKSPACE / "outputs"
FMP_BASE = "https://financialmodelingprep.com/api/v3"

SECTOR_MAP = {
    "AAPL": "Technology",
    "ABBV": "Health Care",
    "ABT": "Health Care",
    "ACN": "Information Technology",
    "ADBE": "Information Technology",
    "ADSK": "Information Technology",
    "AMAT": "Semiconductors",
    "AMZN": "Consumer Discretionary",
    "ANET": "Information Technology",
    "ASML": "Semiconductors",
    "AVGO": "Semiconductors",
    "CDNS": "Information Technology",
    "CMG": "Consumer Discretionary",
    "COST": "Consumer Staples",
    "CRM": "Information Technology",
    "CRWD": "Information Technology",
    "FFOLX": "Fund",
    "FICO": "Information Technology",
    "GD": "Industrials",
    "GOOGL": "Communication Services",
    "INTU": "Information Technology",
    "ISRG": "Health Care",
    "JPM": "Financials",
    "KLAC": "Semiconductors",
    "KMI": "Energy",
    "LLY": "Health Care",
    "LRCX": "Semiconductors",
    "MA": "Financials",
    "MELI": "Consumer Discretionary",
    "META": "Communication Services",
    "MRVL": "Semiconductors",
    "MSCI": "Financials",
    "MSFT": "Information Technology",
    "NFLX": "Communication Services",
    "NOW": "Information Technology",
    "NVDA": "Semiconductors",
    "PANW": "Information Technology",
    "PLTR": "Information Technology",
    "QQQ": "ETF",
    "SPGI": "Financials",
    "SPY": "ETF",
    "TSLA": "Consumer Discretionary",
    "TSM": "Semiconductors",
    "TMO": "Health Care",
    "V": "Financials",
    "WM": "Industrials",
}


@dataclass
class Holding:
    ticker: str
    quantity: float
    avg_price: float
    current_price: float
    market_value: float
    cost_basis: float
    pnl_pct: float
    day_change_pct: float
    weight_pct: float


@dataclass
class WatchlistEntry:
    ticker: str
    score: float | None
    grade: str
    company: str
    status: str


@dataclass
class OptionPosition:
    ticker: str
    strike: float
    option_type: str
    expiration: date
    credit: float
    current: float
    contracts: int


def clean_cell(value: str) -> str:
    """Strip markdown emphasis, emoji markers, and extra spacing."""
    value = value.strip()
    value = value.replace("**", "")
    value = value.replace("⭐", "").strip()
    return value


def to_float(value: str) -> float:
    cleaned = clean_cell(value)
    cleaned = cleaned.replace("$", "").replace(",", "").replace("%", "")
    cleaned = cleaned.replace("+", "").strip()
    if not cleaned or cleaned in {"—", "-"}:
        return 0.0
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    return float(match.group(0)) if match else 0.0


def parse_markdown_table(lines: Iterable[str], start_header: str) -> list[list[str]]:
    """Return rows from the markdown table whose header contains start_header."""
    rows: list[list[str]] = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and start_header in stripped:
            in_table = True
            continue
        if in_table:
            if not stripped.startswith("|"):
                break
            if re.fullmatch(r"\|[\s:\-|]+\|", stripped):
                continue
            rows.append([clean_cell(part) for part in stripped.strip("|").split("|")])
    return rows


def parse_portfolio(path: Path) -> tuple[list[Holding], list[OptionPosition], float | None, float | None]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    holdings: list[Holding] = []
    for row in parse_markdown_table(lines, "SYMBOL"):
        if len(row) < 9:
            continue
        holdings.append(
            Holding(
                ticker=row[0].upper(),
                quantity=to_float(row[1]),
                avg_price=to_float(row[2]),
                current_price=to_float(row[3]),
                market_value=to_float(row[4]),
                cost_basis=to_float(row[5]),
                pnl_pct=to_float(row[6].split("(")[-1]),
                day_change_pct=to_float(row[7].split("(")[-1]),
                weight_pct=to_float(row[8]),
            )
        )

    options: list[OptionPosition] = []
    for row in parse_markdown_table(lines, "Ticker | Strike"):
        if len(row) < 7:
            continue
        try:
            expiration = datetime.strptime(row[3], "%Y-%m-%d").date()
        except ValueError:
            continue
        options.append(
            OptionPosition(
                ticker=row[0].upper(),
                strike=to_float(row[1]),
                option_type=row[2],
                expiration=expiration,
                credit=to_float(row[4]),
                current=to_float(row[5]),
                contracts=int(to_float(row[6])),
            )
        )

    total_match = re.search(r"Total MKT VALUE\*\* \| \$?([\d,]+)", text)
    total_value = to_float(total_match.group(1)) if total_match else None
    cash_match = re.search(r"\| Cash % \| ([\d.]+)", text)
    cash_pct = to_float(cash_match.group(1)) if cash_match else None
    return holdings, options, total_value, cash_pct


def parse_watchlist(path: Path) -> list[WatchlistEntry]:
    rows = parse_markdown_table(path.read_text(encoding="utf-8").splitlines(), "Ticker | Score")
    entries: list[WatchlistEntry] = []
    for row in rows:
        if len(row) < 5:
            continue
        score = None if row[1] in {"—", "-"} else to_float(row[1])
        entries.append(
            WatchlistEntry(
                ticker=row[0].upper(),
                score=score,
                grade=row[2],
                company=row[3],
                status=row[4],
            )
        )
    return entries


def fetch_quotes(tickers: list[str]) -> dict[str, dict]:
    """Fetch optional FMP quote enrichment when the API key is configured."""
    api_key = os.environ.get("FMP_API_KEY")
    if not api_key or not requests or not tickers:
        return {}
    quotes: dict[str, dict] = {}
    chunk_size = 25
    for index in range(0, len(tickers), chunk_size):
        chunk = ",".join(tickers[index : index + chunk_size])
        try:
            response = requests.get(
                f"{FMP_BASE}/quote/{chunk}",
                params={"apikey": api_key},
                timeout=15,
            )
            response.raise_for_status()
            for item in response.json() or []:
                symbol = str(item.get("symbol", "")).upper()
                if symbol:
                    quotes[symbol] = item
        except Exception as exc:
            print(f"Warning: quote enrichment failed for {chunk}: {exc}", file=sys.stderr)
    return quotes


def weight_by_sector(holdings: list[Holding]) -> dict[str, float]:
    sectors: dict[str, float] = {}
    for holding in holdings:
        sector = SECTOR_MAP.get(holding.ticker, "Other")
        sectors[sector] = sectors.get(sector, 0.0) + holding.weight_pct
    return dict(sorted(sectors.items(), key=lambda item: item[1], reverse=True))


def concentration_notes(holdings: list[Holding], sector_weights: dict[str, float]) -> list[str]:
    notes: list[str] = []
    overweights = [h for h in holdings if h.weight_pct >= 10 and h.ticker not in {"SPY", "QQQ"}]
    if overweights:
        notes.append(
            "Single-name concentration: "
            + ", ".join(f"{h.ticker} {h.weight_pct:.1f}%" for h in overweights[:5])
            + "."
        )
    for sector, weight in list(sector_weights.items())[:3]:
        if weight >= 25:
            notes.append(f"{sector} exposure is elevated at {weight:.1f}%.")
    return notes


def active_options(options: list[OptionPosition], as_of: date) -> tuple[list[OptionPosition], list[OptionPosition]]:
    active = [pos for pos in options if pos.expiration >= as_of]
    expired = [pos for pos in options if pos.expiration < as_of]
    return active, expired


def score_watchlist(entry: WatchlistEntry, sector_weights: dict[str, float]) -> float:
    score = entry.score if entry.score is not None else 0.0
    sector = SECTOR_MAP.get(entry.ticker, "Other")
    if sector_weights.get(sector, 0.0) >= 25:
        score -= 6
    if "Top Candidate" in entry.status:
        score += 3
    if entry.grade.startswith("B"):
        score += 2
    if entry.grade.startswith("C"):
        score -= 2
    if "Avoid" in entry.status:
        score -= 20
    return score


def build_trade_ideas(
    holdings: list[Holding],
    watchlist: list[WatchlistEntry],
    options: list[OptionPosition],
    total_value: float | None,
    cash_pct: float | None,
    quotes: dict[str, dict],
    as_of: date,
) -> tuple[str, str]:
    sector_weights = weight_by_sector(holdings)
    top_holdings = sorted(holdings, key=lambda item: item.weight_pct, reverse=True)[:6]
    top_watchlist = sorted(
        watchlist,
        key=lambda item: score_watchlist(item, sector_weights),
        reverse=True,
    )[:6]
    active_opts, expired_opts = active_options(options, as_of)
    notes = concentration_notes(holdings, sector_weights)

    best_diversifier = next(
        (
            entry
            for entry in top_watchlist
            if sector_weights.get(SECTOR_MAP.get(entry.ticker, "Other"), 0.0) < 20
        ),
        top_watchlist[0] if top_watchlist else None,
    )
    best_quality = top_watchlist[0] if top_watchlist else None
    repair_candidates = sorted(
        [h for h in holdings if h.pnl_pct < 0],
        key=lambda item: item.pnl_pct,
    )

    ideas: list[dict[str, str]] = []
    if notes:
        trim_targets = [h for h in top_holdings if h.weight_pct >= 10 and h.ticker != "SPY"]
        if trim_targets:
            trim_text = ", ".join(f"{h.ticker} ({h.weight_pct:.1f}%)" for h in trim_targets[:3])
            ideas.append(
                {
                    "title": "Risk trim / rebalance",
                    "action": f"Trim or hedge oversized winners: {trim_text}.",
                    "why": "The repository risk framework emphasizes position and sector limits; current weights are concentrated before adding more beta.",
                    "risk": "Do not chase replacement trades in the same crowded sector unless total exposure is reduced first.",
                }
            )

    if best_diversifier:
        sector = SECTOR_MAP.get(best_diversifier.ticker, "Other")
        quote = quotes.get(best_diversifier.ticker, {})
        price = quote.get("price")
        change = quote.get("changesPercentage")
        price_note = (
            f" Current quote: ${price:.2f}, {change:+.2f}% today."
            if isinstance(price, (int, float)) and isinstance(change, (int, float))
            else ""
        )
        ideas.append(
            {
                "title": "Watchlist starter candidate",
                "action": f"Consider {best_diversifier.ticker} ({best_diversifier.grade}, {best_diversifier.company}) as the cleanest watchlist add on a pullback.",
                "why": f"It ranks near the top of the watchlist and adds {sector} exposure without worsening the largest portfolio concentration as much as another semiconductor add.{price_note}",
                "risk": "Use a small starter size only after confirming valuation, earnings date, and liquidity.",
            }
        )

    if best_quality and SECTOR_MAP.get(best_quality.ticker) == "Semiconductors":
        ideas.append(
            {
                "title": "Semiconductor rotation candidate",
                "action": f"Keep {best_quality.ticker} ({best_quality.grade}) on deck, but fund it by rotating from existing semiconductor exposure.",
                "why": "The watchlist score is strong, yet AVGO and AMAT already create a large semiconductor sleeve.",
                "risk": "Adding without a source of funds would increase correlated downside.",
            }
        )

    if repair_candidates:
        weakest = repair_candidates[0]
        ideas.append(
            {
                "title": "Thesis repair check",
                "action": f"Review {weakest.ticker}, currently {weakest.pnl_pct:.1f}% from cost and {weakest.weight_pct:.1f}% of the portfolio.",
                "why": "The position is small enough to fix thoughtfully, but persistent underperformance should have a written keep/add/exit thesis.",
                "risk": "Avoid averaging down until fundamentals and catalyst timing are refreshed.",
            }
        )

    if active_opts:
        expiring = sorted(active_opts, key=lambda item: item.expiration)[0]
        ideas.append(
            {
                "title": "Short-premium management",
                "action": f"Review {expiring.ticker} {expiring.strike:g}{expiring.option_type[0].upper()} expiring {expiring.expiration.isoformat()}.",
                "why": "Open short-premium rows should be checked before adding new options exposure.",
                "risk": "Close or roll based on delta, assignment tolerance, and remaining credit.",
            }
        )
    elif expired_opts:
        ideas.append(
            {
                "title": "Options data hygiene",
                "action": "Refresh option positions before making short-premium decisions.",
                "why": f"All {len(expired_opts)} option rows in context are expired as of {as_of.isoformat()}.",
                "risk": "Do not rely on stale contract rows for live trade entry.",
            }
        )

    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    report_lines = [
        f"# Trade Idea Generator — {as_of.isoformat()}",
        "",
        "> Informational only; not investment advice. Verify live prices, liquidity, earnings dates, and portfolio constraints before placing any trade.",
        "",
        "## Inputs",
        "",
        f"- Portfolio context: `{PORTFOLIO_PATH.relative_to(WORKSPACE)}`",
        f"- Watchlist context: `{WATCHLIST_PATH.relative_to(WORKSPACE)}`",
        f"- Generated: {generated_at}",
        f"- FMP quote enrichment: {'enabled' if quotes else 'not used'}",
        "",
        "## Portfolio Snapshot",
        "",
        f"- Total market value: {format_currency(total_value) if total_value else 'N/A'}",
        f"- Cash reserve from snapshot: {cash_pct:.1f}%" if cash_pct is not None else "- Cash reserve from snapshot: N/A",
        "- Largest holdings: " + ", ".join(f"{h.ticker} {h.weight_pct:.1f}%" for h in top_holdings),
        "- Sector weights: " + ", ".join(f"{sector} {weight:.1f}%" for sector, weight in list(sector_weights.items())[:8]),
        "",
        "## Risk Flags",
        "",
    ]
    if notes:
        report_lines.extend(f"- {note}" for note in notes)
    else:
        report_lines.append("- No major concentration flags found in the static snapshot.")
    if expired_opts:
        report_lines.append(f"- {len(expired_opts)} option rows are expired as of {as_of.isoformat()}; refresh before options trading.")
    report_lines.extend(["", "## Ranked Trade Ideas", ""])
    for index, idea in enumerate(ideas, start=1):
        report_lines.extend(
            [
                f"### {index}. {idea['title']}",
                "",
                f"- **Action:** {idea['action']}",
                f"- **Why:** {idea['why']}",
                f"- **Risk control:** {idea['risk']}",
                "",
            ]
        )
    report_lines.extend(
        [
            "## Watchlist Ranking Used",
            "",
            "| Rank | Ticker | Grade | Score | Sector | Status |",
            "|---:|---|---|---:|---|---|",
        ]
    )
    for index, entry in enumerate(top_watchlist, start=1):
        report_lines.append(
            f"| {index} | {entry.ticker} | {entry.grade} | "
            f"{entry.score if entry.score is not None else 'N/A'} | "
            f"{SECTOR_MAP.get(entry.ticker, 'Other')} | {entry.status} |"
        )
    report_lines.extend(
        [
            "",
            "## Next Checks Before Execution",
            "",
            "1. Confirm live bid/ask spreads and current trend.",
            "2. Check earnings dates; avoid unplanned options exposure through earnings.",
            "3. Keep any new starter position within the portfolio risk framework.",
        ]
    )
    report = "\n".join(report_lines) + "\n"

    telegram_lines = [
        f"TRADE IDEA GENERATOR -- {as_of.isoformat()}",
        "Informational only; verify live data before trading.",
        "",
        f"Portfolio: {format_currency(total_value) if total_value else 'N/A'} | Cash: {cash_pct:.1f}%" if cash_pct is not None else f"Portfolio: {format_currency(total_value) if total_value else 'N/A'}",
        "Top weights: " + ", ".join(f"{h.ticker} {h.weight_pct:.1f}%" for h in top_holdings[:4]),
    ]
    if notes:
        telegram_lines.append("Risk flags: " + " ".join(notes[:2]))
    telegram_lines.append("")
    for index, idea in enumerate(ideas[:4], start=1):
        telegram_lines.extend(
            [
                f"{index}) {idea['title']}",
                f"Action: {idea['action']}",
                f"Why: {idea['why']}",
                f"Risk: {idea['risk']}",
                "",
            ]
        )
    telegram_lines.append("Report saved in outputs/trade-idea-generator-YYYY-MM-DD.md")
    telegram = "\n".join(telegram_lines).strip() + "\n"
    return report, telegram


def format_currency(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"${value:,.0f}"


def resolve_chat_id(explicit: str | None = None) -> str | None:
    if explicit:
        return explicit
    env_chat = os.environ.get("TELEGRAM_CHAT_ID")
    if env_chat:
        return env_chat
    fallback_files = [
        WORKSPACE / "outputs" / "csp-daily-scan-fixed.json",
        WORKSPACE / "outputs" / "n8n-workflow-csp-daily-scan.json",
    ]
    for path in fallback_files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        match = re.search(r'"chatId"\s*:\s*"?=?(-?\d+)"?', text)
        if match:
            return match.group(1)
    return None


def send_telegram(message: str, chat_id: str | None) -> dict:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        return {"ok": False, "skipped": True, "error": "TELEGRAM_BOT_TOKEN is not set"}
    if not chat_id:
        return {"ok": False, "skipped": True, "error": "Telegram chat ID is not set and no fallback was found"}
    if not requests:
        return {"ok": False, "skipped": True, "error": "Install requests to send Telegram messages"}
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message[:4096],
        "disable_web_page_preview": True,
    }
    try:
        response = requests.post(url, json=payload, timeout=20)
        data = response.json() if response.content else {}
        return {
            "ok": response.ok and bool(data.get("ok", response.ok)),
            "status_code": response.status_code,
            "description": data.get("description", ""),
            "message_id": data.get("result", {}).get("message_id"),
            "chat_id": chat_id,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "chat_id": chat_id}


def write_outputs(report: str, telegram: str, status: dict, as_of: date) -> tuple[Path, Path, Path]:
    OUTPUTS_DIR.mkdir(exist_ok=True)
    report_path = OUTPUTS_DIR / f"trade-idea-generator-{as_of.isoformat()}.md"
    telegram_path = OUTPUTS_DIR / f"trade-idea-generator-telegram-{as_of.isoformat()}.txt"
    status_path = OUTPUTS_DIR / f"trade-idea-generator-telegram-status-{as_of.isoformat()}.json"
    report_path.write_text(report, encoding="utf-8")
    telegram_path.write_text(telegram, encoding="utf-8")
    status_path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report_path, telegram_path, status_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate trade ideas and optionally send them to Telegram.")
    parser.add_argument("--send-telegram", action="store_true", help="Send the Telegram summary via bot API.")
    parser.add_argument("--chat-id", help="Override Telegram chat ID.")
    parser.add_argument("--date", help="Override as-of date (YYYY-MM-DD).")
    args = parser.parse_args()

    as_of = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else date.today()
    holdings, options, total_value, cash_pct = parse_portfolio(PORTFOLIO_PATH)
    watchlist = parse_watchlist(WATCHLIST_PATH)
    if not holdings:
        print(f"No holdings parsed from {PORTFOLIO_PATH}", file=sys.stderr)
        return 1
    if not watchlist:
        print(f"No watchlist entries parsed from {WATCHLIST_PATH}", file=sys.stderr)
        return 1

    tickers = sorted({h.ticker for h in holdings} | {w.ticker for w in watchlist})
    quotes = fetch_quotes([ticker for ticker in tickers if ticker not in {"FFOLX"}])
    report, telegram = build_trade_ideas(
        holdings=holdings,
        watchlist=watchlist,
        options=options,
        total_value=total_value,
        cash_pct=cash_pct,
        quotes=quotes,
        as_of=as_of,
    )
    status = {"ok": None, "skipped": True, "reason": "send not requested"}
    if args.send_telegram:
        status = send_telegram(telegram, resolve_chat_id(args.chat_id))

    report_path, telegram_path, status_path = write_outputs(report, telegram, status, as_of)
    print(f"Wrote report: {report_path.relative_to(WORKSPACE)}")
    print(f"Wrote Telegram preview: {telegram_path.relative_to(WORKSPACE)}")
    print(f"Wrote Telegram status: {status_path.relative_to(WORKSPACE)}")
    if args.send_telegram:
        if status.get("ok"):
            print(f"Telegram send OK (message_id={status.get('message_id')})")
            return 0
        print(f"Telegram send failed: {status}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
