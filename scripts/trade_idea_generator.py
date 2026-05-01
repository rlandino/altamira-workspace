#!/usr/bin/env python3
"""Generate portfolio/watchlist trade ideas and optionally send them to Telegram."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import textwrap
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_PATH = ROOT / "context" / "portfolio-details.md"
WATCHLIST_PATH = ROOT / "context" / "watchlist.md"
OUTPUT_DIR = ROOT / "outputs"
TELEGRAM_FALLBACK_WORKFLOW = ROOT / "outputs" / "csp-daily-scan-fixed.json"


@dataclass
class Position:
    symbol: str
    qty: float
    avg_price: float
    current: float
    market_value: float
    weight: float
    pnl_pct: float


@dataclass
class WatchlistItem:
    ticker: str
    score: float | None
    grade: str
    company: str
    status: str


@dataclass
class TradeIdea:
    rank: int
    ticker: str
    strategy: str
    action: str
    strike: float | None
    expiration: str
    contracts: int | None
    score: float
    rationale: str
    risk: str


def parse_money(value: str) -> float:
    cleaned = value.replace("$", "").replace(",", "").replace("%", "").strip()
    if cleaned in {"", "-", "—"}:
        return 0.0
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def parse_signed_pct(value: str) -> float:
    match = re.search(r"\(([+-]?[0-9.,]+)%\)", value)
    if match:
        return parse_money(match.group(1))
    return parse_money(value)


def table_rows(path: Path, header_name: str) -> list[list[str]]:
    rows: list[list[str]] = []
    in_table = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            if in_table and rows:
                break
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not in_table:
            if cells and cells[0].replace("*", "").strip().upper() == header_name.upper():
                in_table = True
            continue
        if cells and set(cells[0]) <= {"-", ":"}:
            continue
        rows.append(cells)
    return rows


def load_positions() -> list[Position]:
    positions: list[Position] = []
    for row in table_rows(PORTFOLIO_PATH, "SYMBOL"):
        if len(row) < 9 or row[0].lower().startswith("totals"):
            continue
        positions.append(
            Position(
                symbol=row[0].upper(),
                qty=parse_money(row[1]),
                avg_price=parse_money(row[2]),
                current=parse_money(row[3]),
                market_value=parse_money(row[4]),
                weight=parse_money(row[8]),
                pnl_pct=parse_signed_pct(row[6]),
            )
        )
    return positions


def load_watchlist() -> list[WatchlistItem]:
    items: list[WatchlistItem] = []
    for row in table_rows(WATCHLIST_PATH, "Ticker"):
        if len(row) < 5:
            continue
        score = None if row[1] in {"—", "-", ""} else parse_money(row[1])
        items.append(
            WatchlistItem(
                ticker=row[0].upper(),
                score=score,
                grade=row[2].replace("*", ""),
                company=row[3],
                status=row[4],
            )
        )
    return items


def portfolio_value(positions: Iterable[Position]) -> float:
    return sum(position.market_value for position in positions)


def fetch_yahoo_quotes(symbols: Iterable[str]) -> dict[str, float]:
    unique_symbols = sorted({symbol.upper() for symbol in symbols if symbol})
    quotes: dict[str, float] = {}
    for i in range(0, len(unique_symbols), 40):
        chunk = unique_symbols[i : i + 40]
        query = urllib.parse.urlencode({"symbols": ",".join(chunk)})
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?{query}"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 trade-idea-generator/1.0",
                "Accept": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=12) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - network failures should not stop report generation.
            print(f"Warning: quote lookup failed for {','.join(chunk)}: {exc}", file=sys.stderr)
            continue
        for quote in data.get("quoteResponse", {}).get("result", []):
            symbol = quote.get("symbol", "").upper()
            price = quote.get("regularMarketPrice") or quote.get("postMarketPrice")
            if symbol and isinstance(price, (int, float)):
                quotes[symbol] = float(price)
    return quotes


def next_weekly_expiration(today: date) -> date:
    candidate = today + timedelta(days=30)
    while candidate.weekday() != 4:
        candidate += timedelta(days=1)
    return candidate


def round_strike(value: float, direction: str) -> float:
    increment = 10 if value >= 500 else 5 if value >= 100 else 2.5
    scaled = value / increment
    if direction == "up":
        rounded = math.ceil(scaled) * increment
    elif direction == "down":
        rounded = math.floor(scaled) * increment
    else:
        rounded = round(scaled) * increment
    return round(rounded, 2)


def grade_bonus(grade: str) -> float:
    return {
        "A+": 18,
        "A": 16,
        "A-": 14,
        "B+": 12,
        "B": 10,
        "B-": 8,
        "C+": 4,
        "C": 0,
    }.get(grade.strip().upper(), -4)


def generate_covered_call_ideas(
    positions: list[Position], expiration: date, max_ideas: int
) -> list[TradeIdea]:
    ideas: list[TradeIdea] = []
    for position in positions:
        contracts_available = int(position.qty // 100)
        if contracts_available < 1:
            continue
        if position.symbol in {"SPY", "QQQ"} and position.weight < 5:
            continue
        strike_pct = 1.06 if position.pnl_pct > 40 else 1.08
        strike = round_strike(position.current * strike_pct, "up")
        contracts = min(contracts_available, 3)
        score = 55 + min(position.weight, 20) + min(max(position.pnl_pct, 0) / 10, 12)
        ideas.append(
            TradeIdea(
                rank=0,
                ticker=position.symbol,
                strategy="Covered call",
                action=f"Sell {contracts} {expiration.isoformat()} {strike:g}C against existing shares",
                strike=strike,
                expiration=expiration.isoformat(),
                contracts=contracts,
                score=score,
                rationale=(
                    f"{position.symbol} is {position.weight:.1f}% of portfolio and "
                    f"up {position.pnl_pct:.1f}%; harvest premium while trimming upside concentration."
                ),
                risk="Assignment caps upside above strike; avoid if a near-term catalyst changes conviction.",
            )
        )
    return sorted(ideas, key=lambda idea: idea.score, reverse=True)[:max_ideas]


def generate_csp_ideas(
    watchlist: list[WatchlistItem],
    quotes: dict[str, float],
    portfolio_total: float,
    expiration: date,
    max_ideas: int,
) -> list[TradeIdea]:
    ideas: list[TradeIdea] = []
    max_collateral = portfolio_total * 0.05
    top_candidates = [
        item
        for item in watchlist
        if "top candidate" in item.status.lower() or (item.score or 0) >= 60
    ]
    for item in top_candidates:
        price = quotes.get(item.ticker)
        if not price:
            continue
        strike = round_strike(price * 0.9, "down")
        collateral = strike * 100
        if collateral > max_collateral:
            strategy = "Bull put spread"
            action = (
                f"Sell {expiration.isoformat()} {strike:g}P / buy "
                f"{round_strike(strike * 0.94, 'down'):g}P"
            )
            risk = "Defined-risk spread because naked put collateral would exceed the 5% position cap."
        else:
            strategy = "Cash-secured put"
            action = f"Sell 1 {expiration.isoformat()} {strike:g}P if credit meets target"
            risk = "Assignment risk; only enter if willing to own shares at the breakeven."
        score = 50 + (item.score or 45) / 2 + grade_bonus(item.grade)
        ideas.append(
            TradeIdea(
                rank=0,
                ticker=item.ticker,
                strategy=strategy,
                action=action,
                strike=strike,
                expiration=expiration.isoformat(),
                contracts=1,
                score=score,
                rationale=(
                    f"{item.company} is a {item.status} with score "
                    f"{item.score if item.score is not None else 'n/a'} ({item.grade}); "
                    f"target entry is about 10% below the latest quote (${price:.2f})."
                ),
                risk=risk,
            )
        )
    return sorted(ideas, key=lambda idea: idea.score, reverse=True)[:max_ideas]


def rank_ideas(ideas: list[TradeIdea]) -> list[TradeIdea]:
    ranked: list[TradeIdea] = []
    for rank, idea in enumerate(sorted(ideas, key=lambda item: item.score, reverse=True), start=1):
        idea.rank = rank
        ranked.append(idea)
    return ranked


def load_telegram_chat_id() -> str | None:
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if chat_id:
        return chat_id
    if not TELEGRAM_FALLBACK_WORKFLOW.exists():
        return None
    try:
        data = json.loads(TELEGRAM_FALLBACK_WORKFLOW.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    for node in data.get("nodes", []):
        if "telegram" in node.get("type", "").lower():
            candidate = node.get("parameters", {}).get("chatId")
            if candidate:
                return str(candidate).lstrip("=")
    return None


def telegram_chunks(message: str, limit: int = 3900) -> list[str]:
    chunks: list[str] = []
    remaining = message
    while len(remaining) > limit:
        split_at = remaining.rfind("\n\n", 0, limit)
        if split_at < 1:
            split_at = limit
        chunks.append(remaining[:split_at])
        remaining = remaining[split_at:].lstrip()
    chunks.append(remaining)
    return chunks


def send_telegram(message: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = load_telegram_chat_id()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    if not chat_id:
        raise RuntimeError("TELEGRAM_CHAT_ID is not set and no workflow fallback was found")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    for index, chunk in enumerate(telegram_chunks(message), start=1):
        payload = {
            "chat_id": chat_id,
            "text": chunk if len(telegram_chunks(message)) == 1 else f"{chunk}\n\n({index})",
            "disable_web_page_preview": "true",
        }
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=15) as response:
            response_data = json.loads(response.read().decode("utf-8"))
        if not response_data.get("ok"):
            raise RuntimeError(f"Telegram send failed: {response_data}")


def idea_markdown(idea: TradeIdea) -> str:
    return textwrap.dedent(
        f"""
        ### {idea.rank}. {idea.ticker} - {idea.strategy}

        - **Action:** {idea.action}
        - **Score:** {idea.score:.1f}
        - **Rationale:** {idea.rationale}
        - **Primary risk:** {idea.risk}
        """
    ).strip()


def telegram_summary(ideas: list[TradeIdea], portfolio_total: float, as_of: date) -> str:
    lines = [
        f"Altamira Trade Ideas - {as_of.isoformat()}",
        f"Portfolio snapshot: ${portfolio_total:,.0f}",
        "",
    ]
    for idea in ideas[:6]:
        lines.extend(
            [
                f"{idea.rank}. {idea.ticker} - {idea.strategy}",
                f"   {idea.action}",
                f"   Why: {idea.rationale}",
                f"   Risk: {idea.risk}",
                "",
            ]
        )
    lines.extend(
        [
            "Execution checklist: confirm live bid/ask, earnings date, and liquidity before placing any order.",
            "Educational only; not financial advice.",
        ]
    )
    return "\n".join(lines)


def build_report(ideas: list[TradeIdea], positions: list[Position], watchlist: list[WatchlistItem], as_of: date) -> str:
    total = portfolio_value(positions)
    top_holdings = sorted(positions, key=lambda item: item.weight, reverse=True)[:6]
    top_watchlist = [item for item in watchlist if "top candidate" in item.status.lower()][:5]
    lines = [
        f"# Trade Idea Generator - {as_of.isoformat()}",
        "",
        "## Summary",
        "",
        f"- Portfolio market value from repository context: **${total:,.0f}**",
        f"- Current holdings parsed: **{len(positions)}**",
        f"- Watchlist names parsed: **{len(watchlist)}**",
        "- Live quote source: Yahoo Finance quote endpoint when available; otherwise repository snapshot prices.",
        "- Options premiums are not estimated without a live chain; confirm bid/ask before entry.",
        "",
        "## Top Portfolio Exposures",
        "",
        "| Ticker | Weight | Current | P&L % |",
        "|--------|--------|---------|-------|",
    ]
    for position in top_holdings:
        lines.append(
            f"| {position.symbol} | {position.weight:.1f}% | ${position.current:.2f} | {position.pnl_pct:.1f}% |"
        )
    lines.extend(["", "## Top Watchlist Candidates", "", "| Ticker | Score | Grade | Status |", "|--------|-------|-------|--------|"])
    for item in top_watchlist:
        score = "n/a" if item.score is None else f"{item.score:.1f}"
        lines.append(f"| {item.ticker} | {score} | {item.grade} | {item.status} |")
    lines.extend(["", "## Ranked Trade Ideas", ""])
    lines.extend(idea_markdown(idea) for idea in ideas)
    lines.extend(
        [
            "",
            "## Risk Notes",
            "",
            "- Keep single-trade risk within the 5% position cap and aggregate options exposure within the 30% options limit.",
            "- Do not sell premium through an unplanned earnings event.",
            "- Close short premium at 50% of max profit or stop at 200% of credit, consistent with the workspace risk framework.",
            "",
            "_Educational only; not financial advice._",
        ]
    )
    return "\n".join(lines) + "\n"


def run(send: bool) -> Path:
    as_of = datetime.now(timezone.utc).date()
    positions = load_positions()
    watchlist = load_watchlist()
    if not positions:
        raise RuntimeError(f"No positions parsed from {PORTFOLIO_PATH}")
    expiration = next_weekly_expiration(as_of)
    quote_symbols = [item.ticker for item in watchlist] + [position.symbol for position in positions]
    quotes = fetch_yahoo_quotes(quote_symbols)
    for position in positions:
        if position.symbol in quotes:
            position.current = quotes[position.symbol]
    total = portfolio_value(positions)
    ideas = rank_ideas(
        generate_covered_call_ideas(positions, expiration, max_ideas=4)
        + generate_csp_ideas(watchlist, quotes, total, expiration, max_ideas=5)
    )
    if not ideas:
        raise RuntimeError("No trade ideas generated")
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / f"trade-idea-generator-{as_of.isoformat()}.md"
    output_path.write_text(build_report(ideas, positions, watchlist, as_of), encoding="utf-8")
    message = telegram_summary(ideas, total, as_of)
    if send:
        send_telegram(message)
    print(f"Wrote {output_path.relative_to(ROOT)}")
    print(f"Generated {len(ideas)} trade ideas")
    if send:
        print("Telegram message sent")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--send-telegram", action="store_true", help="Send the summary to Telegram")
    args = parser.parse_args()
    try:
        run(send=args.send_telegram)
    except Exception as exc:  # noqa: BLE001 - CLI should return a concise failure.
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
