#!/usr/bin/env python3
"""Generate trade ideas from repository portfolio/watchlist context.

The generator intentionally works from checked-in context files so it can run
inside automation even when broker or market-data APIs are unavailable. If a
Telegram bot token is present, it can send the concise idea brief to Telegram.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_CHAT_FALLBACK = Path("outputs/csp-daily-scan-fixed.json")
TELEGRAM_LIMIT = 3900

SECTOR_BY_TICKER = {
    "AAPL": "Technology",
    "ABBV": "Health Care",
    "ABT": "Health Care",
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
    "FICO": "Technology",
    "GD": "Industrials",
    "GOOGL": "Communication Services",
    "INTU": "Technology",
    "ISRG": "Health Care",
    "JPM": "Financials",
    "KLAC": "Technology",
    "KMI": "Energy",
    "LLY": "Health Care",
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
    "TMO": "Health Care",
    "V": "Financials",
    "WM": "Industrials",
}


@dataclass
class Position:
    ticker: str
    quantity: float
    avg_price: float
    current_price: float
    market_value: float
    cost_basis: float
    pnl_pct: float | None
    day_change_pct: float | None
    weight_pct: float

    @property
    def sector(self) -> str:
        return SECTOR_BY_TICKER.get(self.ticker, "Other")


@dataclass
class WatchlistItem:
    ticker: str
    score: float | None
    grade: str
    company: str
    status: str

    @property
    def sector(self) -> str:
        return SECTOR_BY_TICKER.get(self.ticker, "Other")


@dataclass
class OptionPosition:
    ticker: str
    strike: float
    option_type: str
    expiration: dt.date
    credit: float
    current: float
    contracts: int

    def dte(self, today: dt.date) -> int:
        return (self.expiration - today).days

    @property
    def notional(self) -> float:
        return self.strike * 100 * self.contracts

    @property
    def premium_received(self) -> float:
        return self.credit * 100 * self.contracts

    @property
    def current_debit(self) -> float:
        return self.current * 100 * self.contracts


def parse_float(value: str) -> float:
    cleaned = value.strip().replace("$", "").replace(",", "").replace("%", "")
    cleaned = cleaned.replace("+", "").replace("(", "").replace(")", "")
    if cleaned in {"", "-", "--", "—"}:
        return 0.0
    return float(cleaned)


def parse_optional_float(value: str) -> float | None:
    value = value.strip()
    if value in {"", "-", "--", "—"}:
        return None
    return parse_float(value)


def pct_from_field(value: str) -> float | None:
    matches = re.findall(r"([+-]?\d+(?:\.\d+)?)%", value)
    if not matches:
        return None
    return float(matches[-1])


def markdown_rows(path: Path) -> Iterable[list[str]]:
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or all(set(cell) <= {"-", " "} for cell in cells):
            continue
        yield cells


def parse_positions(path: Path) -> list[Position]:
    positions: list[Position] = []
    for row in markdown_rows(path):
        if len(row) < 9 or row[0].upper() in {"SYMBOL", "FIELD", "SOURCE"}:
            continue
        ticker = row[0].upper()
        if not re.fullmatch(r"[A-Z][A-Z0-9.\-]*", ticker):
            continue
        try:
            positions.append(
                Position(
                    ticker=ticker,
                    quantity=parse_float(row[1]),
                    avg_price=parse_float(row[2]),
                    current_price=parse_float(row[3]),
                    market_value=parse_float(row[4]),
                    cost_basis=parse_float(row[5]),
                    pnl_pct=pct_from_field(row[6]),
                    day_change_pct=pct_from_field(row[7]),
                    weight_pct=parse_float(row[8]),
                )
            )
        except (IndexError, ValueError):
            continue
    return positions


def parse_watchlist(path: Path) -> list[WatchlistItem]:
    items: list[WatchlistItem] = []
    for row in markdown_rows(path):
        if len(row) < 5 or row[0].upper() == "TICKER":
            continue
        ticker = row[0].upper()
        if not re.fullmatch(r"[A-Z][A-Z0-9.\-]*", ticker):
            continue
        items.append(
            WatchlistItem(
                ticker=ticker,
                score=parse_optional_float(row[1]),
                grade=row[2].replace("*", "").strip(),
                company=row[3],
                status=row[4],
            )
        )
    return items


def parse_options(path: Path) -> list[OptionPosition]:
    options: list[OptionPosition] = []
    for row in markdown_rows(path):
        if len(row) < 7 or row[0].upper() == "TICKER":
            continue
        ticker = row[0].upper()
        if not re.fullmatch(r"[A-Z][A-Z0-9.\-]*", ticker):
            continue
        try:
            options.append(
                OptionPosition(
                    ticker=ticker,
                    strike=parse_float(row[1]),
                    option_type=row[2],
                    expiration=dt.date.fromisoformat(row[3]),
                    credit=parse_float(row[4]),
                    current=parse_float(row[5]),
                    contracts=int(parse_float(row[6])),
                )
            )
        except (IndexError, ValueError):
            continue
    return options


def currency(value: float) -> str:
    return f"${value:,.0f}"


def price(value: float) -> str:
    return f"${value:,.2f}"


def top_watchlist(items: list[WatchlistItem], limit: int = 5) -> list[WatchlistItem]:
    def sort_key(item: WatchlistItem) -> tuple[float, str]:
        return (item.score if item.score is not None else -1.0, item.ticker)

    qualified = [item for item in items if item.score is not None]
    return sorted(qualified, key=sort_key, reverse=True)[:limit]


def sector_exposure(positions: list[Position]) -> dict[str, float]:
    exposure: dict[str, float] = {}
    for pos in positions:
        exposure[pos.sector] = exposure.get(pos.sector, 0.0) + pos.weight_pct
    return dict(sorted(exposure.items(), key=lambda item: item[1], reverse=True))


def format_option_management(
    options: list[OptionPosition],
    positions_by_ticker: dict[str, Position],
    today: dt.date,
) -> list[str]:
    active = [option for option in options if option.dte(today) >= 0]
    if not active:
        return ["No active short-premium rows remain in context after skipping expired options."]

    lines: list[str] = []
    for opt in sorted(active, key=lambda item: (item.expiration, item.ticker)):
        dte = opt.dte(today)
        under = positions_by_ticker.get(opt.ticker)
        buffer = ""
        if under and under.current_price:
            distance = (under.current_price - opt.strike) / under.current_price * 100
            buffer = f" | buffer {distance:.1f}% vs repo price {price(under.current_price)}"
        mark_note = ""
        if opt.current > 0:
            capture = (opt.credit - opt.current) / opt.credit * 100 if opt.credit else 0
            mark_note = f" | repo mark {price(opt.current)} ({capture:.0f}% of credit captured)"
        lines.append(
            f"- {opt.ticker} {opt.strike:g}{opt.option_type[0].upper()} "
            f"{opt.expiration.isoformat()} ({dte} DTE){buffer}{mark_note}"
        )
    return lines


def build_idea_sections(
    positions: list[Position],
    watchlist: list[WatchlistItem],
    options: list[OptionPosition],
    today: dt.date,
) -> dict[str, list[str]]:
    positions_by_ticker = {pos.ticker: pos for pos in positions}
    exposures = sector_exposure(positions)
    top_positions = sorted(positions, key=lambda pos: pos.weight_pct, reverse=True)[:5]
    overweight = [pos for pos in positions if pos.weight_pct >= 10.0]
    top_candidates = top_watchlist(watchlist, 5)
    active_options = [opt for opt in options if opt.dte(today) >= 0]
    near_expiry = [opt for opt in active_options if opt.dte(today) <= 7]
    expired = [opt for opt in options if opt.dte(today) < 0]

    sections: dict[str, list[str]] = {}

    manage_lines: list[str] = []
    if near_expiry:
        manage_lines.append(
            "Priority: manage near-expiry short puts before adding new premium risk."
        )
        manage_lines.extend(format_option_management(near_expiry, positions_by_ticker, today))
    elif active_options:
        manage_lines.append("No options inside 7 DTE. Active short-premium book:")
        manage_lines.extend(format_option_management(active_options, positions_by_ticker, today))
    else:
        manage_lines.append("No active option rows in context.")
    if expired:
        skipped = ", ".join(
            f"{opt.ticker} {opt.strike:g}{opt.option_type[0].upper()} {opt.expiration.isoformat()}"
            for opt in expired
        )
        manage_lines.append(f"Skipped expired rows: {skipped}.")
    sections["Option management"] = manage_lines

    concentration_lines: list[str] = []
    if overweight:
        names = ", ".join(f"{pos.ticker} {pos.weight_pct:.1f}%" for pos in overweight)
        concentration_lines.append(
            f"Trim/covered-call candidates because single-name weights exceed 10%: {names}."
        )
    concentration_lines.append(
        "Top weights: "
        + ", ".join(f"{pos.ticker} {pos.weight_pct:.1f}%" for pos in top_positions)
        + "."
    )
    concentration_lines.append(
        "Largest sector/factor exposures: "
        + ", ".join(f"{sector} {weight:.1f}%" for sector, weight in list(exposures.items())[:4])
        + "."
    )
    if exposures.get("Technology", 0.0) >= 35.0:
        concentration_lines.append(
            "Technology exposure is above the 35% enhanced-monitoring threshold; size new tech ideas conservatively."
        )
    sections["Portfolio risk idea"] = concentration_lines

    watch_lines: list[str] = []
    if top_candidates:
        watch_lines.append(
            "Screen these watchlist names for 30-45 DTE CSP or put-spread entries: "
            + ", ".join(
                f"{item.ticker} ({item.grade}, score {item.score:.1f})"
                for item in top_candidates
                if item.score is not None
            )
            + "."
        )
        tech_watch = [item.ticker for item in top_candidates if item.sector == "Technology"]
        if tech_watch:
            watch_lines.append(
                "Because most top candidates are technology/semi names, prefer defined-risk put spreads or reduced CSP size."
            )
    else:
        watch_lines.append("No scored watchlist candidates found.")
    watch_lines.append(
        "Entry rules: require live chain liquidity, no near earnings event, bid/ask spread under 10%, and target 0.15-0.25 delta."
    )
    sections["New trade setup"] = watch_lines

    review_lines: list[str] = []
    losers = [pos for pos in positions if pos.pnl_pct is not None and pos.pnl_pct < -10.0]
    if losers:
        review_lines.append(
            "Review underperformers before adding capital: "
            + ", ".join(f"{pos.ticker} {pos.pnl_pct:.1f}%" for pos in losers)
            + "."
        )
    review_lines.append(
        "Use live broker quotes before entry; repository prices and option marks may be stale."
    )
    sections["Guardrails"] = review_lines

    return sections


def build_markdown_report(
    positions: list[Position],
    watchlist: list[WatchlistItem],
    options: list[OptionPosition],
    today: dt.date,
) -> str:
    sections = build_idea_sections(positions, watchlist, options, today)
    portfolio_value = sum(pos.market_value for pos in positions)
    exposures = sector_exposure(positions)
    active_notional = sum(opt.notional for opt in options if opt.dte(today) >= 0)
    top_candidates = top_watchlist(watchlist, 5)

    lines = [
        f"# Trade Idea Generator - {today.isoformat()}",
        "",
        "> Generated from repository context files: `context/portfolio-details.md`, "
        "`context/watchlist.md`, and `context/options-positions.md`.",
        "",
        "## Summary",
        "",
        f"- Portfolio market value from parsed positions: {currency(portfolio_value)}",
        f"- Positions parsed: {len(positions)}",
        f"- Watchlist names parsed: {len(watchlist)}",
        f"- Active short-premium notional in context: {currency(active_notional)}",
        "- Data source: repository snapshot; verify live prices/chains before trading.",
        "",
        "## Generated Ideas",
        "",
    ]

    for title, body in sections.items():
        lines.append(f"### {title}")
        lines.extend(body)
        lines.append("")

    lines.extend(
        [
            "## Top Portfolio Weights",
            "",
            "| Ticker | Weight | Current | P&L | Sector |",
            "|--------|--------|---------|-----|--------|",
        ]
    )
    for pos in sorted(positions, key=lambda item: item.weight_pct, reverse=True)[:10]:
        pnl = f"{pos.pnl_pct:.1f}%" if pos.pnl_pct is not None else "N/A"
        lines.append(
            f"| {pos.ticker} | {pos.weight_pct:.1f}% | {price(pos.current_price)} | {pnl} | {pos.sector} |"
        )

    lines.extend(
        [
            "",
            "## Sector / Factor Exposure",
            "",
            "| Exposure | Weight |",
            "|----------|--------|",
        ]
    )
    for sector, weight in exposures.items():
        lines.append(f"| {sector} | {weight:.1f}% |")

    lines.extend(
        [
            "",
            "## Top Watchlist Candidates",
            "",
            "| Ticker | Score | Grade | Company | Status |",
            "|--------|-------|-------|---------|--------|",
        ]
    )
    for item in top_candidates:
        score = f"{item.score:.1f}" if item.score is not None else "N/A"
        lines.append(
            f"| {item.ticker} | {score} | {item.grade} | {item.company} | {item.status} |"
        )

    lines.extend(
        [
            "",
            "## Disclaimer",
            "",
            "This is an automation-generated research brief, not financial advice. "
            "Confirm suitability, live prices, liquidity, earnings dates, and risk limits before placing any order.",
            "",
        ]
    )
    return "\n".join(lines)


def build_telegram_text(
    positions: list[Position],
    watchlist: list[WatchlistItem],
    options: list[OptionPosition],
    today: dt.date,
) -> str:
    sections = build_idea_sections(positions, watchlist, options, today)
    portfolio_value = sum(pos.market_value for pos in positions)
    top_candidates = top_watchlist(watchlist, 5)
    top_weights = sorted(positions, key=lambda item: item.weight_pct, reverse=True)[:4]
    active_options = [opt for opt in options if opt.dte(today) >= 0]
    near_expiry = [opt for opt in active_options if opt.dte(today) <= 7]

    lines = [
        f"TRADE IDEA GENERATOR - {today.isoformat()}",
        f"Portfolio context: {currency(portfolio_value)} | {len(positions)} positions | {len(watchlist)} watchlist names",
        "Source: repository snapshot. Verify live quotes/options before entry.",
        "",
        "1) MANAGE EXISTING OPTIONS",
    ]
    lines.extend(sections["Option management"][:4])
    if len(sections["Option management"]) > 4:
        lines.append(f"- Plus {len(sections['Option management']) - 4} additional option notes in the report.")

    lines.extend(
        [
            "",
            "2) PORTFOLIO RISK / INCOME IDEA",
            "- Top weights: " + ", ".join(f"{pos.ticker} {pos.weight_pct:.1f}%" for pos in top_weights),
        ]
    )
    if near_expiry:
        lines.append("- Keep new premium sizing light until near-expiry puts are closed, rolled, or expire.")
    tech_weight = sector_exposure(positions).get("Technology", 0.0)
    if tech_weight >= 35.0:
        lines.append(f"- Tech exposure is {tech_weight:.1f}%; prefer trims/covered calls or defined-risk structures over new naked tech CSPs.")

    if top_candidates:
        lines.extend(
            [
                "",
                "3) NEW SETUP TO SCREEN",
                "- Watchlist CSP/put-spread candidates: "
                + ", ".join(f"{item.ticker} {item.grade}/{item.score:.1f}" for item in top_candidates if item.score is not None),
                "- Filter: 30-45 DTE, 0.15-0.25 delta, no near earnings, tight bid/ask, risk <= 2% per idea.",
            ]
        )

    lines.extend(
        [
            "",
            "Not financial advice. Confirm live data and portfolio limits before trading.",
        ]
    )
    text = "\n".join(lines)
    if len(text) > TELEGRAM_LIMIT:
        text = text[: TELEGRAM_LIMIT - 120].rstrip() + "\n\n[Truncated; see generated markdown report.]"
    return text


def extract_fallback_chat_id(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        workflow = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    for node in workflow.get("nodes", []):
        if node.get("name") != "Send Telegram Alert":
            continue
        chat_id = str(node.get("parameters", {}).get("chatId", "")).strip()
        if not chat_id or "$env" in chat_id:
            continue
        return chat_id.lstrip("=").strip()
    return None


def resolve_chat_id(args: argparse.Namespace) -> str | None:
    return (
        args.telegram_chat_id
        or os.environ.get("TELEGRAM_CHAT_ID")
        or extract_fallback_chat_id(args.telegram_fallback)
    )


def send_telegram(token: str, chat_id: str, text: str) -> dict[str, object]:
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
            body = response.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Telegram request failed: {exc}") from exc


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--portfolio", type=Path, default=Path("context/portfolio-details.md"))
    parser.add_argument("--watchlist", type=Path, default=Path("context/watchlist.md"))
    parser.add_argument("--options", type=Path, default=Path("context/options-positions.md"))
    parser.add_argument("--out-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--date", type=dt.date.fromisoformat, default=dt.date.today())
    parser.add_argument("--send-telegram", action="store_true", help="Send the concise brief to Telegram.")
    parser.add_argument("--telegram-chat-id", help="Override TELEGRAM_CHAT_ID.")
    parser.add_argument("--telegram-fallback", type=Path, default=DEFAULT_CHAT_FALLBACK)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    missing = [path for path in [args.portfolio, args.watchlist, args.options] if not path.exists()]
    if missing:
        for path in missing:
            print(f"Missing required context file: {path}", file=sys.stderr)
        return 2

    positions = parse_positions(args.portfolio)
    watchlist = parse_watchlist(args.watchlist)
    options = parse_options(args.options)

    if not positions:
        print(f"No positions parsed from {args.portfolio}", file=sys.stderr)
        return 2
    if not watchlist:
        print(f"No watchlist rows parsed from {args.watchlist}", file=sys.stderr)
        return 2

    report = build_markdown_report(positions, watchlist, options, args.date)
    telegram_text = build_telegram_text(positions, watchlist, options, args.date)

    date_str = args.date.isoformat()
    report_path = args.out_dir / f"trade-idea-generator-{date_str}.md"
    telegram_path = args.out_dir / f"trade-idea-generator-{date_str}-telegram.txt"
    status_path = args.out_dir / f"trade-idea-generator-{date_str}-telegram-status.json"

    write_text(report_path, report)
    write_text(telegram_path, telegram_text)
    print(f"Wrote {report_path}")
    print(f"Wrote {telegram_path}")

    if args.send_telegram:
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = resolve_chat_id(args)
        if not token:
            print("TELEGRAM_BOT_TOKEN is not set.", file=sys.stderr)
            return 3
        if not chat_id:
            print(
                "TELEGRAM_CHAT_ID is not set and no fallback chat ID was found.",
                file=sys.stderr,
            )
            return 3
        response = send_telegram(token, chat_id, telegram_text)
        safe_status = {
            "sent": bool(response.get("ok")),
            "chat_id": chat_id,
            "date": date_str,
            "message_id": response.get("result", {}).get("message_id"),
            "telegram_ok": response.get("ok"),
        }
        write_text(status_path, json.dumps(safe_status, indent=2) + "\n")
        print(f"Telegram send ok: {safe_status['sent']} (message_id={safe_status['message_id']})")
        print(f"Wrote {status_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
