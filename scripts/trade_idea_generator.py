#!/usr/bin/env python3
"""Generate portfolio/watchlist trade ideas and optionally send to Telegram."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import textwrap
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_PATH = ROOT / "context" / "portfolio-details.md"
WATCHLIST_PATH = ROOT / "context" / "watchlist.md"
OUTPUTS_DIR = ROOT / "outputs"


@dataclass(frozen=True)
class Position:
    symbol: str
    quantity: float
    current: float
    market_value: float
    pnl_pct: float
    day_chg_pct: float
    weight: float


@dataclass(frozen=True)
class WatchlistItem:
    ticker: str
    score: float | None
    grade: str | None
    company: str
    status: str


def parse_money(value: str) -> float:
    cleaned = value.replace("$", "").replace(",", "").replace("+", "").strip()
    if cleaned in {"", "-", "\u2014"}:
        return 0.0
    return float(cleaned)


def parse_pct_from_text(value: str) -> float:
    match = re.search(r"([+-]?\d+(?:\.\d+)?)%", value)
    return float(match.group(1)) if match else 0.0


def parse_float(value: str) -> float:
    cleaned = value.replace(",", "").strip()
    return float(cleaned) if cleaned not in {"", "-", "\u2014"} else 0.0


def parse_positions(path: Path) -> list[Position]:
    positions: list[Position] = []
    in_table = False

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("| SYMBOL |"):
            in_table = True
            continue
        if in_table and (not line or line.startswith("**Totals:**")):
            break
        if not in_table or not line.startswith("|"):
            continue
        if set(line.replace("|", "").strip()) <= {"-"}:
            continue

        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 9 or cells[0] == "SYMBOL":
            continue

        try:
            positions.append(
                Position(
                    symbol=cells[0],
                    quantity=parse_float(cells[1]),
                    current=parse_money(cells[3]),
                    market_value=parse_money(cells[4]),
                    pnl_pct=parse_pct_from_text(cells[6]),
                    day_chg_pct=parse_pct_from_text(cells[7]),
                    weight=parse_pct_from_text(cells[8]),
                )
            )
        except ValueError:
            continue

    return positions


def parse_watchlist(path: Path) -> list[WatchlistItem]:
    items: list[WatchlistItem] = []
    in_table = False

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("| Ticker |"):
            in_table = True
            continue
        if in_table and (not line or line.startswith("---")):
            break
        if not in_table or not line.startswith("|"):
            continue
        if set(line.replace("|", "").strip()) <= {"-"}:
            continue

        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 5 or cells[0] == "Ticker":
            continue

        score = None
        if cells[1] not in {"", "\u2014"}:
            try:
                score = float(cells[1])
            except ValueError:
                score = None
        grade = re.sub(r"[*_]", "", cells[2]).strip() or None
        status = re.sub(r"[*_\u2b50]", "", cells[4]).strip()
        items.append(WatchlistItem(cells[0], score, grade, cells[3], status))

    return items


def extract_metric(path: Path, field: str) -> str | None:
    pattern = re.compile(rf"^\|\s*{re.escape(field)}\s*\|\s*(.*?)\s*\|")
    for line in path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line.strip())
        if match:
            return match.group(1).strip()
    return None


def read_workflow_chat_id(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        workflow = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None

    for node in workflow.get("nodes", []):
        params = node.get("parameters", {})
        chat_id = params.get("chatId")
        if isinstance(chat_id, str):
            chat_id = chat_id.strip()
            if chat_id and "$env" not in chat_id and "TELEGRAM_CHAT_ID" not in chat_id:
                return chat_id.lstrip("=")
    return None


def grade_rank(grade: str | None) -> int:
    ranks = {
        "A+": 10,
        "A": 9,
        "A-": 8,
        "B+": 7,
        "B": 6,
        "B-": 5,
        "C+": 4,
        "C": 3,
        "C-": 2,
        "D+": 1,
        "D": 0,
        "F": -1,
    }
    return ranks.get(grade or "", -2)


def ticker_set(positions: Iterable[Position]) -> set[str]:
    return {p.symbol for p in positions}


def generate_report(positions: list[Position], watchlist: list[WatchlistItem]) -> tuple[str, str]:
    today = date.today().isoformat()
    portfolio_value = extract_metric(PORTFOLIO_PATH, "**Total MKT VALUE**") or "N/A"
    cash_pct = extract_metric(PORTFOLIO_PATH, "Cash %") or "N/A"
    vix = extract_metric(PORTFOLIO_PATH, "VIX Close") or "N/A"
    spy = extract_metric(PORTFOLIO_PATH, "SPY Close") or "N/A"

    top_positions = sorted(positions, key=lambda p: p.weight, reverse=True)[:6]
    concentrated = [p for p in top_positions if p.weight >= 10.0]
    winners = sorted(
        [p for p in positions if p.weight >= 3.0 and p.pnl_pct >= 25.0],
        key=lambda p: (p.weight, p.pnl_pct),
        reverse=True,
    )
    owned = ticker_set(positions)
    top_watchlist = sorted(
        [w for w in watchlist if w.ticker not in owned and grade_rank(w.grade) >= 5],
        key=lambda w: (w.score if w.score is not None else -999),
        reverse=True,
    )

    ideas: list[dict[str, str]] = []

    if winners:
        p = winners[0]
        ideas.append(
            {
                "rank": "1",
                "ticker": p.symbol,
                "strategy": "Covered call / staged trim",
                "why": (
                    f"{p.weight:.1f}% portfolio weight and +{p.pnl_pct:.1f}% unrealized gain; "
                    "monetize upside while reducing concentration risk."
                ),
                "action": (
                    "Screen 30-45 DTE calls around 0.20-0.30 delta; if premium is thin, trim a small "
                    "piece instead of forcing an option sale."
                ),
                "risk": "Avoid selling calls through a known catalyst if assignment would disrupt the long-term thesis.",
            }
        )

    if len(winners) > 1:
        p = winners[1]
        ideas.append(
            {
                "rank": "2",
                "ticker": p.symbol,
                "strategy": "Covered call candidate",
                "why": (
                    f"{p.weight:.1f}% weight, +{p.pnl_pct:.1f}% unrealized gain, and "
                    f"{p.day_chg_pct:+.1f}% latest day move in repo snapshot."
                ),
                "action": "Look for 30-45 DTE 0.20-0.25 delta call credit; close at 50% max profit.",
                "risk": "If the position is core, keep strike above a level where assignment is acceptable.",
            }
        )

    for item in top_watchlist[:2]:
        rank = str(len(ideas) + 1)
        ideas.append(
            {
                "rank": rank,
                "ticker": item.ticker,
                "strategy": "Watchlist CSP entry",
                "why": (
                    f"{item.company} is a top watchlist candidate "
                    f"({item.score if item.score is not None else 'N/A'} score, {item.grade or 'N/A'} grade)."
                ),
                "action": "Only enter on a red/flat tape with acceptable IV: sell 30-45 DTE 0.20-0.30 delta put.",
                "risk": "Skip if earnings fall inside the expiration window or if bid/ask spread is wider than 10%.",
            }
        )

    if concentrated:
        p = concentrated[0]
        ideas.append(
            {
                "rank": str(len(ideas) + 1),
                "ticker": "Portfolio",
                "strategy": "Concentration check",
                "why": (
                    f"Largest line is {p.symbol} at {p.weight:.1f}%; top six positions are "
                    f"{', '.join(f'{x.symbol} {x.weight:.1f}%' for x in top_positions)}."
                ),
                "action": "Prioritize new premium trades outside the existing mega-cap tech/semiconductor cluster.",
                "risk": "Do not add correlated watchlist semiconductor exposure without reducing another tech sleeve.",
            }
        )

    report_lines = [
        f"# Trade Idea Generator - {today}",
        "",
        "> Generated from repository context files: `context/portfolio-details.md` and `context/watchlist.md`.",
        "",
        "## Portfolio Context",
        "",
        f"- Portfolio market value: **{portfolio_value}**",
        f"- Cash percentage: **{cash_pct}%**",
        f"- Repo snapshot SPY/VIX: **SPY {spy} / VIX {vix}**",
        f"- Top holdings: {', '.join(f'{p.symbol} ({p.weight:.1f}%)' for p in top_positions)}",
        "",
        "## Trade Ideas",
        "",
    ]

    for idea in ideas:
        report_lines.extend(
            [
                f"### {idea['rank']}. {idea['ticker']} - {idea['strategy']}",
                "",
                f"- **Why:** {idea['why']}",
                f"- **Action:** {idea['action']}",
                f"- **Risk control:** {idea['risk']}",
                "",
            ]
        )

    report_lines.extend(
        [
            "## Operating Rules",
            "",
            "- Keep each new options position at or below the portfolio's 5% position-risk guideline.",
            "- Close short premium at 50% max profit; reassess or stop at roughly 200% of original credit.",
            "- Avoid initiating short premium that carries through unplanned earnings.",
            "",
            "## Disclaimer",
            "",
            "This is an informational idea scan for research and risk review, not financial advice or an order ticket.",
        ]
    )

    telegram_lines = [
        f"Trade Idea Generator - {today}",
        f"Portfolio: {portfolio_value} | Cash: {cash_pct}% | Repo VIX: {vix}",
        "",
    ]
    for idea in ideas[:5]:
        telegram_lines.extend(
            [
                f"{idea['rank']}) {idea['ticker']} - {idea['strategy']}",
                f"Why: {idea['why']}",
                f"Action: {idea['action']}",
                "",
            ]
        )
    telegram_lines.append("Research only; verify live prices, options chain liquidity, and earnings before entry.")

    return "\n".join(report_lines), "\n".join(telegram_lines)


def send_telegram(token: str, chat_id: str, text: str) -> dict:
    data = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": text[:3900],
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate trade ideas from repository portfolio/watchlist context."
    )
    parser.add_argument("--send-telegram", action="store_true", help="Send the summary to Telegram.")
    parser.add_argument("--chat-id", help="Telegram chat/channel id. Defaults to TELEGRAM_CHAT_ID.")
    parser.add_argument(
        "--chat-id-workflow",
        default=str(ROOT / "outputs" / "csp-daily-scan-fixed.json"),
        help="Workflow JSON to read a fixed Telegram chat id from if TELEGRAM_CHAT_ID is unset.",
    )
    parser.add_argument(
        "--output",
        default=str(OUTPUTS_DIR / f"trade-idea-generator-{date.today().isoformat()}.md"),
        help="Markdown report output path.",
    )
    args = parser.parse_args()

    positions = parse_positions(PORTFOLIO_PATH)
    watchlist = parse_watchlist(WATCHLIST_PATH)
    if not positions:
        print(f"No positions parsed from {PORTFOLIO_PATH}", file=sys.stderr)
        return 1
    if not watchlist:
        print(f"No watchlist items parsed from {WATCHLIST_PATH}", file=sys.stderr)
        return 1

    report, telegram_text = generate_report(positions, watchlist)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report + "\n", encoding="utf-8")

    print(f"Wrote report: {output_path}")
    print()
    print(textwrap.shorten(telegram_text.replace("\n", " | "), width=500, placeholder=" ..."))

    if args.send_telegram:
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = args.chat_id or os.environ.get("TELEGRAM_CHAT_ID")
        if not chat_id:
            chat_id = read_workflow_chat_id(Path(args.chat_id_workflow))
        if not token:
            print("TELEGRAM_BOT_TOKEN is not set.", file=sys.stderr)
            return 1
        if not chat_id:
            print("Telegram chat id is not set and no fixed workflow chat id was found.", file=sys.stderr)
            return 1
        result = send_telegram(token, chat_id, telegram_text)
        if not result.get("ok"):
            print(f"Telegram send failed: {result}", file=sys.stderr)
            return 1
        print("Telegram message sent.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
