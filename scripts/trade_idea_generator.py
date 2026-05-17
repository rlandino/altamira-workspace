#!/usr/bin/env python3
"""Generate portfolio/watchlist trade ideas and optionally send to Telegram."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


WORKSPACE = Path(__file__).resolve().parent.parent
CONTEXT = WORKSPACE / "context"
OUTPUTS = WORKSPACE / "outputs"


@dataclass
class GeneratedReport:
    markdown_path: Path
    telegram_text_path: Path
    status_path: Path | None
    telegram_sent: bool
    telegram_error: str | None


def clean_cell(value: str) -> str:
    """Normalize markdown table cell contents."""
    return re.sub(r"\s+", " ", value.replace("**", "").strip())


def slug_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", clean_cell(value).lower()).strip("_")


def parse_markdown_tables(text: str) -> list[list[dict[str, str]]]:
    """Parse simple pipe-delimited markdown tables into row dictionaries."""
    lines = text.splitlines()
    tables: list[list[dict[str, str]]] = []
    idx = 0
    while idx < len(lines):
        line = lines[idx].strip()
        if not line.startswith("|"):
            idx += 1
            continue

        block: list[str] = []
        while idx < len(lines) and lines[idx].strip().startswith("|"):
            block.append(lines[idx].strip())
            idx += 1

        if len(block) < 2:
            continue

        headers = [slug_header(cell) for cell in block[0].strip("|").split("|")]
        rows: list[dict[str, str]] = []
        for raw_row in block[1:]:
            cells = [clean_cell(cell) for cell in raw_row.strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", cell.replace(" ", "")) for cell in cells):
                continue
            if len(cells) != len(headers):
                continue
            rows.append(dict(zip(headers, cells)))
        if rows:
            tables.append(rows)
    return tables


def load_table(path: Path, required_headers: set[str]) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    for table in parse_markdown_tables(text):
        if required_headers.issubset(table[0].keys()):
            return table
    return []


def parse_number(value: str) -> float | None:
    cleaned = re.sub(r"[^0-9.\-]", "", value)
    if cleaned in {"", "-", "."}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_pct(value: str) -> float | None:
    match = re.search(r"([-+]?\d+(?:\.\d+)?)\s*%", value)
    if match:
        return float(match.group(1))
    return parse_number(value)


def money(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"${value:,.0f}"


def pct(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:.1f}%"


def parse_expiration(value: str) -> date | None:
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def get_portfolio_value(positions: list[dict[str, str]]) -> float:
    total = 0.0
    for row in positions:
        total += parse_number(row.get("mkt_value", "")) or 0.0
    return total


def get_top_positions(positions: list[dict[str, str]], minimum_weight: float = 5.0) -> list[dict[str, Any]]:
    normalized = []
    for row in positions:
        weight = parse_pct(row.get("weight", ""))
        if weight is None or weight < minimum_weight:
            continue
        normalized.append(
            {
                "symbol": row.get("symbol", ""),
                "weight": weight,
                "current": parse_number(row.get("current", "")),
                "mkt_value": parse_number(row.get("mkt_value", "")),
                "day_chg": row.get("day_chg", ""),
                "pnl": row.get("p_l", row.get("p_l_", "")),
            }
        )
    return sorted(normalized, key=lambda item: item["weight"], reverse=True)


def normalize_watchlist(watchlist: list[dict[str, str]]) -> list[dict[str, Any]]:
    rows = []
    for row in watchlist:
        ticker = row.get("ticker", "").upper()
        if not ticker:
            continue
        rows.append(
            {
                "ticker": ticker,
                "score": parse_number(row.get("score", "")),
                "grade": row.get("grade", ""),
                "company": row.get("company", ""),
                "status": row.get("status", ""),
            }
        )
    return rows


def grade_rank(grade: str) -> int:
    order = {
        "A+": 1,
        "A": 2,
        "A-": 3,
        "B+": 4,
        "B": 5,
        "B-": 6,
        "C+": 7,
        "C": 8,
        "C-": 9,
        "D+": 10,
        "D": 11,
        "F": 12,
    }
    return order.get(grade.strip().upper(), 99)


def get_top_watchlist(watchlist: list[dict[str, Any]], owned_symbols: set[str], limit: int = 5) -> list[dict[str, Any]]:
    candidates = [
        row
        for row in watchlist
        if row["ticker"] not in owned_symbols
        and (
            "Top Candidate" in row["status"]
            or (row["score"] is not None and row["score"] >= 60)
            or grade_rank(row["grade"]) <= grade_rank("B-")
        )
    ]
    candidates.sort(key=lambda row: (-(row["score"] or -1), grade_rank(row["grade"]), row["ticker"]))
    return candidates[:limit]


def get_low_priority_watchlist(watchlist: list[dict[str, Any]], limit: int = 4) -> list[dict[str, Any]]:
    avoid = [
        row
        for row in watchlist
        if "Avoid" in row["status"] or "Low Priority" in row["status"] or grade_rank(row["grade"]) >= grade_rank("D+")
    ]
    avoid.sort(key=lambda row: (row["score"] if row["score"] is not None else 999, row["ticker"]))
    return avoid[:limit]


def get_expired_options(options_rows: list[dict[str, str]], as_of: date) -> list[dict[str, str]]:
    expired = []
    for row in options_rows:
        expiration = parse_expiration(row.get("expiration", ""))
        if expiration and expiration < as_of:
            expired.append(row)
    return expired


def get_active_options(options_rows: list[dict[str, str]], as_of: date) -> list[dict[str, str]]:
    active = []
    for row in options_rows:
        expiration = parse_expiration(row.get("expiration", ""))
        if expiration and expiration >= as_of:
            active.append(row)
    return active


def build_markdown_report(
    positions: list[dict[str, str]],
    options_rows: list[dict[str, str]],
    watchlist_rows: list[dict[str, Any]],
    as_of: date,
) -> tuple[str, str]:
    portfolio_value = get_portfolio_value(positions)
    owned_symbols = {row.get("symbol", "").upper() for row in positions if row.get("symbol")}
    top_positions = get_top_positions(positions)
    concentrated = [row for row in top_positions if row["weight"] >= 10.0]
    top_watchlist = get_top_watchlist(watchlist_rows, owned_symbols)
    avoid_watchlist = get_low_priority_watchlist(watchlist_rows)
    expired_options = get_expired_options(options_rows, as_of)
    active_options = get_active_options(options_rows, as_of)

    top_names = ", ".join(
        f"{row['symbol']} {pct(row['weight'])}" for row in top_positions[:5]
    )
    new_candidates = ", ".join(
        f"{row['ticker']} ({row['score']:.1f}, {row['grade']})" if row["score"] is not None else f"{row['ticker']} ({row['grade']})"
        for row in top_watchlist
    )

    lines = [
        f"# Trade Idea Generator - {as_of.isoformat()}",
        "",
        "## Dashboard",
        "",
        f"- **Portfolio value represented in context:** {money(portfolio_value)}",
        f"- **Holdings parsed:** {len(positions)}",
        f"- **Watchlist names parsed:** {len(watchlist_rows)}",
        f"- **Top concentration:** {top_names or 'N/A'}",
        f"- **Active option rows:** {len(active_options)}",
        f"- **Expired option rows skipped:** {len(expired_options)}",
        "",
        "## Top Trade Ideas",
        "",
        "### 1. Manage concentration before adding new gross exposure",
        "",
    ]

    if concentrated:
        lines.append(
            "The portfolio is led by several positions above 10% weight. Treat these as risk-budget "
            "decisions first, then look for incremental buys."
        )
        lines.append("")
        lines.append("| Ticker | Weight | Market Value | Idea |")
        lines.append("|--------|--------|--------------|------|")
        for row in concentrated[:4]:
            overlay = "Trim 5-10% on strength or sell covered calls only if comfortable capping upside"
            lines.append(f"| {row['symbol']} | {pct(row['weight'])} | {money(row['mkt_value'])} | {overlay} |")
    else:
        lines.append("No position above the 10% concentration threshold was found in the context file.")

    lines.extend(
        [
            "",
            "### 2. New-money watchlist candidates",
            "",
        ]
    )
    if top_watchlist:
        lines.append(
            "Use these as the first names for fresh capital or cash-secured-put watch, subject to live "
            "chain validation and earnings checks."
        )
        lines.append("")
        lines.append("| Rank | Ticker | Score | Grade | Company | Suggested Action |")
        lines.append("|------|--------|-------|-------|---------|------------------|")
        for idx, row in enumerate(top_watchlist, start=1):
            score = f"{row['score']:.1f}" if row["score"] is not None else "N/A"
            action = "Starter buy on pullback or 20-30 delta CSP if IV rank/liquidity qualify"
            lines.append(f"| {idx} | {row['ticker']} | {score} | {row['grade']} | {row['company']} | {action} |")
    else:
        lines.append("No unowned watchlist entries met the B-/60+ score threshold.")

    lines.extend(
        [
            "",
            "### 3. Short-premium housekeeping",
            "",
        ]
    )
    if expired_options:
        expired_summary = ", ".join(
            f"{row.get('ticker')} {row.get('strike')}{row.get('type', '')[0:1]} {row.get('expiration')}"
            for row in expired_options
        )
        lines.append(
            f"All option rows in context are expired as of {as_of.isoformat()} or earlier: "
            f"{expired_summary}. Reconcile broker records before opening the next short-premium set."
        )
    elif active_options:
        lines.append("Active option rows exist in context; review P&L versus close/roll rules before new entries.")
    else:
        lines.append("No option rows were found in context.")

    lines.extend(
        [
            "",
            "### 4. Avoid / low-priority watchlist names",
            "",
        ]
    )
    if avoid_watchlist:
        lines.append("| Ticker | Score | Grade | Status | Action |")
        lines.append("|--------|-------|-------|--------|--------|")
        for row in avoid_watchlist:
            score = f"{row['score']:.1f}" if row["score"] is not None else "N/A"
            lines.append(f"| {row['ticker']} | {score} | {row['grade']} | {row['status']} | Do not allocate until score/thesis improves |")
    else:
        lines.append("No avoid/low-priority watchlist names were flagged.")

    lines.extend(
        [
            "",
            "## Execution Checklist",
            "",
            "- Confirm live prices, spreads, earnings dates, and liquidity before entering any trade.",
            "- Respect the portfolio risk framework: avoid increasing concentration while top names remain outsized.",
            "- For CSPs or spreads, validate 20-60 DTE, 0.20-0.30 delta, IV rank above threshold, and acceptable bid/ask spread.",
            "- This is an idea screen, not financial advice or an execution instruction.",
            "",
        ]
    )

    telegram_lines = [
        f"Altamira Trade Ideas - {as_of.isoformat()}",
        "",
        f"Portfolio context: {money(portfolio_value)} across {len(positions)} holdings.",
        f"Top weights: {top_names or 'N/A'}.",
        "",
        "1) Manage concentration first:",
    ]
    if concentrated:
        for row in concentrated[:4]:
            telegram_lines.append(
                f"- {row['symbol']} {pct(row['weight'])}: trim 5-10% on strength or use covered calls only if willing to cap upside."
            )
    else:
        telegram_lines.append("- No >10% positions found.")

    telegram_lines.extend(["", "2) New-money watchlist:"])
    if top_watchlist:
        for row in top_watchlist:
            score = f"{row['score']:.1f}" if row["score"] is not None else "N/A"
            telegram_lines.append(
                f"- {row['ticker']} ({score}, {row['grade']}): starter/pullback buy or 20-30 delta CSP after live chain + earnings check."
            )
    else:
        telegram_lines.append("- No unowned B-/60+ candidates found.")

    telegram_lines.extend(["", "3) Options housekeeping:"])
    if expired_options:
        telegram_lines.append(
            f"- {len(expired_options)} option rows in context are expired; reconcile broker records before opening new premium trades."
        )
    elif active_options:
        telegram_lines.append("- Review active short-premium rows against close/roll rules.")
    else:
        telegram_lines.append("- No option rows found.")

    if avoid_watchlist:
        avoid_text = ", ".join(row["ticker"] for row in avoid_watchlist)
        telegram_lines.extend(["", f"Avoid/low-priority: {avoid_text}."])
    telegram_lines.extend(["", "Not financial advice; confirm live market data before execution."])

    return "\n".join(lines), "\n".join(telegram_lines)


def resolve_telegram_chat_id() -> str | None:
    env_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if env_chat_id:
        return env_chat_id.strip()

    fallback_path = OUTPUTS / "csp-daily-scan-fixed.json"
    if not fallback_path.exists():
        return None
    try:
        data = json.loads(fallback_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    for node in data.get("nodes", []):
        params = node.get("parameters", {})
        chat_id = str(params.get("chatId", "")).strip()
        if chat_id:
            return chat_id.lstrip("=")
    return None


def send_telegram_message(text: str) -> dict[str, Any]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = resolve_telegram_chat_id()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    if not chat_id:
        raise RuntimeError("TELEGRAM_CHAT_ID is not set and no fallback chatId was found")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text[:4000],
        "disable_web_page_preview": True,
    }
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram API HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise RuntimeError(f"Telegram API connection failed: {exc}") from exc
    return json.loads(body)


def sanitize_telegram_status(result: dict[str, Any]) -> dict[str, Any]:
    """Keep proof of delivery without storing Telegram profile details."""
    message = result.get("result", {}) if isinstance(result, dict) else {}
    chat = message.get("chat", {}) if isinstance(message, dict) else {}
    return {
        "ok": bool(result.get("ok")) if isinstance(result, dict) else False,
        "message_id": message.get("message_id"),
        "date": message.get("date"),
        "chat_id": chat.get("id"),
        "chat_type": chat.get("type"),
    }


def run(send_telegram: bool) -> GeneratedReport:
    OUTPUTS.mkdir(exist_ok=True)
    as_of = date.today()
    portfolio_path = CONTEXT / "portfolio-details.md"
    watchlist_path = CONTEXT / "watchlist.md"
    options_path = CONTEXT / "options-positions.md"

    positions = load_table(portfolio_path, {"symbol", "qty", "mkt_value", "weight"})
    options_rows = load_table(options_path, {"ticker", "strike", "type", "expiration"})
    watchlist = normalize_watchlist(load_table(watchlist_path, {"ticker", "score", "grade", "company", "status"}))

    if not positions:
        raise RuntimeError(f"No positions table found in {portfolio_path}")
    if not watchlist:
        raise RuntimeError(f"No watchlist table found in {watchlist_path}")

    markdown, telegram_text = build_markdown_report(positions, options_rows, watchlist, as_of)
    markdown_path = OUTPUTS / f"trade-idea-generator-{as_of.isoformat()}.md"
    telegram_text_path = OUTPUTS / f"trade-idea-generator-telegram-{as_of.isoformat()}.txt"
    status_path = OUTPUTS / f"trade-idea-generator-telegram-status-{as_of.isoformat()}.json"

    markdown_path.write_text(markdown + "\n", encoding="utf-8")
    telegram_text_path.write_text(telegram_text + "\n", encoding="utf-8")

    sent = False
    error = None
    if send_telegram:
        try:
            result = send_telegram_message(telegram_text)
            sent = bool(result.get("ok"))
            status_path.write_text(json.dumps(sanitize_telegram_status(result), indent=2) + "\n", encoding="utf-8")
        except Exception as exc:  # pragma: no cover - status file is for operations.
            error = str(exc)
            status_path.write_text(json.dumps({"ok": False, "error": error}, indent=2) + "\n", encoding="utf-8")
            raise

    return GeneratedReport(markdown_path, telegram_text_path, status_path if send_telegram else None, sent, error)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate trade ideas from context/portfolio-details.md and context/watchlist.md."
    )
    parser.add_argument("--send-telegram", action="store_true", help="Send the Telegram summary after generating it.")
    args = parser.parse_args()

    try:
        result = run(send_telegram=args.send_telegram)
    except Exception as exc:
        print(f"trade_idea_generator failed: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote report: {result.markdown_path}")
    print(f"Wrote Telegram text: {result.telegram_text_path}")
    if args.send_telegram:
        status = "sent" if result.telegram_sent else "not sent"
        print(f"Telegram status: {status} ({result.status_path})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
