#!/usr/bin/env python3
"""
Generate concise trade ideas from the current Altamira portfolio and watchlist.

The script is intentionally conservative: it reads the repository's context
files first, optionally enriches symbols with live FMP quotes when
FMP_API_KEY is set, writes a markdown report, and can send the concise
summary to Telegram when TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are
available. If TELEGRAM_CHAT_ID is not set, it can reuse a fixed chat id from
the existing n8n workflow export in outputs/csp-daily-scan-fixed.json.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable, Optional
from urllib import error, parse, request


ROOT = Path(__file__).resolve().parents[1]
CONTEXT = ROOT / "context"
OUTPUTS = ROOT / "outputs"


@dataclass
class Position:
    ticker: str
    qty: float
    avg_price: Optional[float]
    current_price: Optional[float]
    market_value: Optional[float]
    cost_basis: Optional[float]
    pnl_text: str
    day_change_text: str
    weight_pct: Optional[float]


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
class WatchlistCandidate:
    ticker: str
    score: Optional[float]
    grade: str
    company: str
    status: str


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def parse_number(value: str) -> Optional[float]:
    cleaned = value.strip()
    if not cleaned or cleaned in {"-", "--", "—"}:
        return None
    cleaned = re.sub(r"\*\*|,|\$|%|\+", "", cleaned)
    cleaned = cleaned.replace("−", "-")
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    return float(match.group(0)) if match else None


def parse_int(value: str) -> int:
    number = parse_number(value)
    return int(number) if number is not None else 0


def clean_status(value: str) -> str:
    """Normalize watchlist status labels that may include emoji or markdown."""
    cleaned = re.sub(r"\*+", "", value).strip()
    cleaned = re.sub(r"[^A-Za-z /-]+", "", cleaned).strip()
    return re.sub(r"\s+", " ", cleaned)


def parse_markdown_tables(text: str) -> list[tuple[list[str], list[list[str]]]]:
    tables: list[tuple[list[str], list[list[str]]]] = []
    current: list[str] = []
    for line in text.splitlines() + [""]:
        if line.strip().startswith("|") and line.strip().endswith("|"):
            current.append(line.strip())
            continue
        if len(current) >= 2:
            header = [cell.strip() for cell in current[0].strip("|").split("|")]
            rows: list[list[str]] = []
            for row_line in current[2:]:
                row = [cell.strip() for cell in row_line.strip("|").split("|")]
                if len(row) == len(header):
                    rows.append(row)
            tables.append((header, rows))
        current = []
    return tables


def find_table(text: str, required_headers: set[str]) -> tuple[list[str], list[list[str]]]:
    for header, rows in parse_markdown_tables(text):
        normalized = {h.strip().lower() for h in header}
        if {h.lower() for h in required_headers}.issubset(normalized):
            return header, rows
    return [], []


def row_dict(header: list[str], row: list[str]) -> dict[str, str]:
    return {header[i].strip(): row[i].strip() for i in range(min(len(header), len(row)))}


def load_positions() -> list[Position]:
    text = read_text(CONTEXT / "portfolio-details.md")
    header, rows = find_table(text, {"SYMBOL", "QTY", "CURRENT", "MKT VALUE", "WEIGHT"})
    positions: list[Position] = []
    for row in rows:
        item = row_dict(header, row)
        ticker = item.get("SYMBOL", "").strip().upper()
        if not ticker:
            continue
        positions.append(
            Position(
                ticker=ticker,
                qty=parse_number(item.get("QTY", "")) or 0,
                avg_price=parse_number(item.get("AVG. PRICE", "")),
                current_price=parse_number(item.get("CURRENT", "")),
                market_value=parse_number(item.get("MKT VALUE", "")),
                cost_basis=parse_number(item.get("COST BASIS", "")),
                pnl_text=item.get("P&L ($, %)", ""),
                day_change_text=item.get("DAY CHG ($, %)", ""),
                weight_pct=parse_number(item.get("WEIGHT", "")),
            )
        )
    return positions


def load_option_positions() -> list[OptionPosition]:
    text = read_text(CONTEXT / "options-positions.md")
    header, rows = find_table(text, {"Ticker", "Strike", "Type", "Expiration", "Credit", "Current", "Contracts"})
    options: list[OptionPosition] = []
    for row in rows:
        item = row_dict(header, row)
        ticker = item.get("Ticker", "").strip().upper()
        strike = parse_number(item.get("Strike", ""))
        credit = parse_number(item.get("Credit", ""))
        current = parse_number(item.get("Current", ""))
        if not ticker or strike is None or credit is None or current is None:
            continue
        options.append(
            OptionPosition(
                ticker=ticker,
                strike=strike,
                option_type=item.get("Type", "").strip().title(),
                expiration=item.get("Expiration", "").strip(),
                credit=credit,
                current=current,
                contracts=parse_int(item.get("Contracts", "")),
            )
        )
    return options


def load_watchlist() -> list[WatchlistCandidate]:
    text = read_text(CONTEXT / "watchlist.md")
    header, rows = find_table(text, {"Ticker", "Score", "Grade", "Company", "Status"})
    candidates: list[WatchlistCandidate] = []
    for row in rows:
        item = row_dict(header, row)
        ticker = item.get("Ticker", "").strip().upper()
        if not ticker:
            continue
        candidates.append(
            WatchlistCandidate(
                ticker=ticker,
                score=parse_number(item.get("Score", "")),
                grade=re.sub(r"\*+", "", item.get("Grade", "")).strip(),
                company=item.get("Company", "").strip(),
                status=clean_status(item.get("Status", "")),
            )
        )
    return candidates


def last_monday(year: int, month: int) -> date:
    cursor = date(year, month + 1, 1) - timedelta(days=1)
    while cursor.weekday() != 0:
        cursor -= timedelta(days=1)
    return cursor


def first_monday(year: int, month: int) -> date:
    cursor = date(year, month, 1)
    while cursor.weekday() != 0:
        cursor += timedelta(days=1)
    return cursor


def fourth_thursday(year: int, month: int) -> date:
    cursor = date(year, month, 1)
    count = 0
    while True:
        if cursor.weekday() == 3:
            count += 1
            if count == 4:
                return cursor
        cursor += timedelta(days=1)


def market_calendar_note(today: date) -> str:
    fixed = {(1, 1): "New Year's Day", (7, 4): "Independence Day", (12, 25): "Christmas Day"}
    if (today.month, today.day) in fixed:
        return f"US market holiday likely ({fixed[(today.month, today.day)]}); treat ideas as planning candidates."
    floating = {
        last_monday(today.year, 5): "Memorial Day",
        first_monday(today.year, 9): "Labor Day",
        fourth_thursday(today.year, 11): "Thanksgiving Day",
    }
    if today in floating:
        return f"US market holiday likely ({floating[today]}); treat ideas as planning candidates."
    if today.weekday() >= 5:
        return "Weekend; treat ideas as planning candidates for the next regular session."
    return "Market status not verified by exchange calendar; confirm liquidity and news before entry."


def fetch_fmp_quotes(symbols: Iterable[str], api_key: Optional[str]) -> dict[str, dict]:
    if not api_key:
        return {}
    unique = [s for s in dict.fromkeys(symbols) if s and re.match(r"^[A-Z.^-]+$", s)]
    quotes: dict[str, dict] = {}
    for i in range(0, len(unique), 40):
        chunk = unique[i : i + 40]
        url = "https://financialmodelingprep.com/api/v3/quote/" + ",".join(parse.quote(s) for s in chunk)
        url += "?" + parse.urlencode({"apikey": api_key})
        try:
            with request.urlopen(url, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (error.URLError, error.HTTPError, TimeoutError, json.JSONDecodeError):
            continue
        if isinstance(payload, list):
            for quote in payload:
                symbol = str(quote.get("symbol", "")).upper()
                if symbol:
                    quotes[symbol] = quote
    return quotes


def quote_price(ticker: str, positions_by_ticker: dict[str, Position], quotes: dict[str, dict]) -> Optional[float]:
    quote = quotes.get(ticker)
    if quote and quote.get("price") is not None:
        try:
            return float(quote["price"])
        except (TypeError, ValueError):
            pass
    pos = positions_by_ticker.get(ticker)
    return pos.current_price if pos else None


def quote_change_pct(ticker: str, quotes: dict[str, dict]) -> Optional[float]:
    quote = quotes.get(ticker)
    if not quote:
        return None
    value = quote.get("changesPercentage")
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fmt_money(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    return f"${value:,.2f}"


def fmt_pct(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    return f"{value:.1f}%"


def score_option_status(option: OptionPosition, price: Optional[float]) -> tuple[str, str]:
    profit_pct = (option.credit - option.current) / option.credit if option.credit else 0
    moneyness_note = ""
    if price and option.option_type.lower() == "put":
        if option.strike > price:
            moneyness_note = f" strike is above spot {fmt_money(price)}"
        elif option.strike >= price * 0.95:
            moneyness_note = f" strike is within 5% of spot {fmt_money(price)}"
    if profit_pct >= 0.50:
        return "Close / harvest", f"{option.ticker} {option.strike:g}{option.option_type[0]} {option.expiration}: {profit_pct:.0%} of credit captured; close per 50% profit rule."
    if option.current >= option.credit * 2:
        suffix = f"; {moneyness_note.strip()}" if moneyness_note else "."
        return "Risk review", f"{option.ticker} {option.strike:g}{option.option_type[0]} {option.expiration}: current mark is >=2x credit; review stop/roll plan{suffix}"
    if moneyness_note:
        return "Monitor", f"{option.ticker} {option.strike:g}{option.option_type[0]} {option.expiration}:{moneyness_note}; do not add correlated risk until managed."
    return "Hold / monitor", f"{option.ticker} {option.strike:g}{option.option_type[0]} {option.expiration}: current mark {fmt_money(option.current)} vs credit {fmt_money(option.credit)}."


def candidate_watchlist(watchlist: list[WatchlistCandidate]) -> list[WatchlistCandidate]:
    priority = {"Top Candidate": 0, "Consider": 1, "Monitor": 2, "Low Priority": 3, "Avoid": 4}
    return sorted(
        [c for c in watchlist if "Avoid" not in c.status],
        key=lambda c: (priority.get(c.status, 2), -(c.score or -999)),
    )[:6]


def build_reports(
    positions: list[Position],
    options: list[OptionPosition],
    watchlist: list[WatchlistCandidate],
    quotes: dict[str, dict],
    today: date,
) -> tuple[str, str]:
    positions_by_ticker = {p.ticker: p for p in positions}
    total_value = sum(p.market_value or 0 for p in positions)
    source_note = "live FMP quotes where available plus repository context" if quotes else "repository context snapshot only"
    holiday_note = market_calendar_note(today)

    overweight = sorted(
        [p for p in positions if (p.weight_pct or 0) > 5],
        key=lambda p: p.weight_pct or 0,
        reverse=True,
    )
    top_watch = candidate_watchlist(watchlist)

    option_actions = []
    for option in options:
        price = quote_price(option.ticker, positions_by_ticker, quotes)
        option_actions.append(score_option_status(option, price))

    close_actions = [detail for action, detail in option_actions if action == "Close / harvest"]
    risk_actions = [detail for action, detail in option_actions if action == "Risk review"]
    monitor_actions = [detail for action, detail in option_actions if action not in {"Close / harvest", "Risk review"}]

    covered_call_targets = []
    for pos in overweight[:4]:
        price = quote_price(pos.ticker, positions_by_ticker, quotes)
        target = price * 1.08 if price else None
        change = quote_change_pct(pos.ticker, quotes)
        covered_call_targets.append(
            {
                "ticker": pos.ticker,
                "weight": pos.weight_pct,
                "price": price,
                "target": target,
                "change": change,
            }
        )

    watchlist_ideas = []
    for candidate in top_watch:
        price = quote_price(candidate.ticker, positions_by_ticker, quotes)
        put_target = price * 0.90 if price else None
        watchlist_ideas.append(
            {
                "ticker": candidate.ticker,
                "score": candidate.score,
                "grade": candidate.grade,
                "company": candidate.company,
                "status": candidate.status,
                "price": price,
                "put_target": put_target,
                "change": quote_change_pct(candidate.ticker, quotes),
            }
        )

    top_focus = []
    if close_actions:
        top_focus.append(close_actions[0])
    if risk_actions:
        top_focus.append(risk_actions[0])
    if covered_call_targets:
        cc = covered_call_targets[0]
        top_focus.append(
            f"{cc['ticker']}: overweight at {fmt_pct(cc['weight'])}; consider 30-45 DTE covered calls near {fmt_money(cc['target'])} only on shares you would trim."
        )
    if watchlist_ideas:
        wl = watchlist_ideas[0]
        if wl["put_target"]:
            top_focus.append(
                f"{wl['ticker']}: top watchlist candidate ({wl['score']:.1f}, {wl['grade']}); consider 30-45 DTE CSP around {fmt_money(wl['put_target'])} or 0.20-0.25 delta after earnings/liquidity check."
            )
        else:
            top_focus.append(
                f"{wl['ticker']}: top watchlist candidate ({wl['score']:.1f}, {wl['grade']}); screen 30-45 DTE CSP at 0.20-0.25 delta after earnings/liquidity check."
            )

    message_lines = [
        f"ALTAMIRA TRADE IDEAS - {today.isoformat()}",
        "-" * 34,
        f"Data: {source_note}.",
        holiday_note,
        "",
        "Priority actions:",
    ]
    for idx, idea in enumerate(top_focus[:4], start=1):
        message_lines.append(f"{idx}. {idea}")
    message_lines.extend(["", "Portfolio setup:"])
    if total_value:
        message_lines.append(f"- Context equity market value: {fmt_money(total_value)}.")
    if overweight:
        message_lines.append(
            "- Concentration watch: "
            + ", ".join(f"{p.ticker} {fmt_pct(p.weight_pct)}" for p in overweight[:5])
            + "."
        )
    if close_actions:
        message_lines.append(f"- Harvest candidate: {close_actions[0]}")
    if risk_actions:
        message_lines.append(f"- Risk item: {risk_actions[0]}")
    message_lines.extend(
        [
            "",
            "New-entry screen:",
            "- Prefer defined-risk spreads/CSPs only after confirming 30-45 DTE liquidity, IV rank >30, earnings outside the hold window, and portfolio risk limits.",
            "- This is a planning scan, not financial advice.",
        ]
    )
    telegram_message = "\n".join(message_lines)

    md: list[str] = [
        f"# Trade Idea Generator - {today.isoformat()}",
        "",
        "> Generated from `context/portfolio-details.md`, `context/options-positions.md`, and `context/watchlist.md`.",
        "",
        "## Summary",
        "",
        f"- **Data source:** {source_note}.",
        f"- **Calendar note:** {holiday_note}",
        f"- **Portfolio market value in context:** {fmt_money(total_value) if total_value else 'N/A'}",
        f"- **Portfolio positions parsed:** {len(positions)}",
        f"- **Short premium positions parsed:** {len(options)}",
        f"- **Watchlist candidates parsed:** {len(watchlist)}",
        "",
        "## Priority Trade Ideas",
        "",
    ]
    for idx, idea in enumerate(top_focus[:4], start=1):
        md.append(f"{idx}. {idea}")
    md.extend(["", "## Existing Short Premium Review", ""])
    if option_actions:
        md.append("| Action | Detail |")
        md.append("| ------ | ------ |")
        for action, detail in option_actions:
            md.append(f"| {action} | {detail} |")
    else:
        md.append("No short premium positions found in context/options-positions.md.")
    md.extend(["", "## Covered Call / Trim Candidates", ""])
    if covered_call_targets:
        md.append("| Ticker | Weight | Price | Planning Call Target | Note |")
        md.append("| ------ | ------ | ----- | -------------------- | ---- |")
        for item in covered_call_targets:
            md.append(
                f"| {item['ticker']} | {fmt_pct(item['weight'])} | {fmt_money(item['price'])} | {fmt_money(item['target'])} | "
                "Use 30-45 DTE, 0.20-0.30 delta, only on shares acceptable to trim. |"
            )
    else:
        md.append("No positions above the 5% concentration threshold were found.")
    md.extend(["", "## Watchlist Entry Candidates", ""])
    if watchlist_ideas:
        md.append("| Ticker | Score | Grade | Status | Price | Planning CSP Target |")
        md.append("| ------ | ----- | ----- | ------ | ----- | ------------------- |")
        for item in watchlist_ideas:
            score = f"{item['score']:.1f}" if item["score"] is not None else "N/A"
            md.append(
                f"| {item['ticker']} | {score} | {item['grade'] or 'N/A'} | {item['status']} | "
                f"{fmt_money(item['price'])} | {fmt_money(item['put_target']) if item['put_target'] else 'Use 0.20-0.25 delta'} |"
            )
    else:
        md.append("No watchlist candidates found.")
    md.extend(
        [
            "",
            "## Risk Rules Before Entry",
            "",
            "- Confirm 30-45 DTE option liquidity, bid/ask spread, open interest, and IV rank before entry.",
            "- Avoid holding short premium through unplanned earnings.",
            "- Keep single-position risk within the portfolio's risk framework and preserve at least the required cash reserve.",
            "- Close short premium at 50% of max profit or reassess at 200% of credit, consistent with the workspace strategy.",
            "",
            "## Telegram Message",
            "",
            "```text",
            telegram_message,
            "```",
            "",
            "_Educational planning scan only; not financial advice._",
            "",
        ]
    )
    return "\n".join(md), telegram_message


def discover_telegram_chat_id() -> Optional[str]:
    explicit = os.environ.get("TELEGRAM_CHAT_ID")
    if explicit:
        return explicit
    workflow = OUTPUTS / "csp-daily-scan-fixed.json"
    if not workflow.exists():
        return None
    try:
        payload = json.loads(workflow.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    for node in payload.get("nodes", []):
        chat_id = node.get("parameters", {}).get("chatId")
        if isinstance(chat_id, str):
            cleaned = chat_id.strip()
            if cleaned.startswith("="):
                cleaned = cleaned[1:].strip()
            if cleaned and "TELEGRAM_CHAT_ID" not in cleaned:
                return cleaned
    return None


def send_telegram(message: str, token: str, chat_id: str) -> None:
    chunks: list[str] = []
    remaining = message
    while len(remaining) > 3900:
        split_at = remaining.rfind("\n", 0, 3900)
        if split_at < 500:
            split_at = 3900
        chunks.append(remaining[:split_at])
        remaining = remaining[split_at:].lstrip()
    chunks.append(remaining)

    for idx, chunk in enumerate(chunks, start=1):
        text = chunk if len(chunks) == 1 else f"{chunk}\n\n({idx}/{len(chunks)})"
        body = json.dumps(
            {
                "chat_id": chat_id,
                "text": text,
                "disable_web_page_preview": True,
            }
        ).encode("utf-8")
        req = request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Telegram send failed with HTTP {exc.code}: {details}") from exc
        except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Telegram send failed: {exc}") from exc
        if not payload.get("ok"):
            raise RuntimeError(f"Telegram send failed: {payload}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate trade ideas from the current portfolio and watchlist.")
    parser.add_argument("--send-telegram", action="store_true", help="Send the concise trade idea summary to Telegram.")
    parser.add_argument("--telegram-chat-id", help="Override TELEGRAM_CHAT_ID for this run.")
    parser.add_argument("--out", help="Output markdown path. Defaults to outputs/trade-idea-generator-YYYY-MM-DD.md.")
    parser.add_argument("--date", help="Override report date, YYYY-MM-DD.")
    args = parser.parse_args()

    today = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else date.today()
    positions = load_positions()
    options = load_option_positions()
    watchlist = load_watchlist()
    symbols = [p.ticker for p in positions] + [c.ticker for c in candidate_watchlist(watchlist)]
    quotes = fetch_fmp_quotes(symbols, os.environ.get("FMP_API_KEY"))

    report, telegram_message = build_reports(positions, options, watchlist, quotes, today)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    out_path = Path(args.out) if args.out else OUTPUTS / f"trade-idea-generator-{today.isoformat()}.md"
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    out_path.write_text(report, encoding="utf-8")
    print(f"Wrote {out_path.relative_to(ROOT)}")

    if args.send_telegram:
        token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
        chat_id = args.telegram_chat_id or discover_telegram_chat_id()
        if not token:
            print("TELEGRAM_BOT_TOKEN is not set; cannot send Telegram message.", file=sys.stderr)
            return 2
        if not chat_id:
            print("TELEGRAM_CHAT_ID is not set and no repository fallback was found.", file=sys.stderr)
            return 2
        send_telegram(telegram_message, token, chat_id)
        print("Sent Telegram trade idea summary.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
