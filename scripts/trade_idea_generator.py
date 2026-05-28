#!/usr/bin/env python3
"""
Generate actionable trade ideas from the workspace portfolio and watchlist.

The script is intentionally self-contained so the daily automation can run even
when external market-data credentials are unavailable. It reads the repository's
current context files, ranks portfolio management, short-premium, and watchlist
entry ideas, writes a dated markdown report plus Telegram-ready summary, and can
send the summary through the Telegram Bot API.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

try:
    import requests
except ImportError:  # pragma: no cover - handled for operator clarity
    requests = None


WORKSPACE = Path(__file__).resolve().parent.parent
CONTEXT_DIR = WORKSPACE / "context"
OUTPUTS_DIR = WORKSPACE / "outputs"

DEFAULT_TELEGRAM_CHAT_ID = "7830722515"

GRADE_SCORE = {
    "A+": 95,
    "A": 90,
    "A-": 85,
    "B+": 78,
    "B": 72,
    "B-": 66,
    "C+": 60,
    "C": 54,
    "C-": 48,
    "D+": 42,
    "D": 36,
    "F": 25,
}


@dataclass(frozen=True)
class Holding:
    symbol: str
    quantity: float
    avg_price: float
    current_price: float
    market_value: float
    pnl_pct: float
    day_change_pct: float
    weight_pct: float


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
    expiration: str
    credit: float
    current: float
    contracts: int


@dataclass(frozen=True)
class TradeIdea:
    rank_score: float
    ticker: str
    source: str
    strategy: str
    action: str
    rationale: str
    risk: str
    sizing: str

    @property
    def confidence(self) -> str:
        if self.rank_score >= 90:
            return "High"
        if self.rank_score >= 75:
            return "Medium-High"
        if self.rank_score >= 60:
            return "Medium"
        return "Watch"


def clean_cell(value: str) -> str:
    value = value.strip()
    value = value.replace("**", "")
    value = value.replace("⭐", "").strip()
    return value


def parse_money(value: str) -> float:
    cleaned = re.sub(r"[^0-9.\-]", "", value)
    return float(cleaned) if cleaned else 0.0


def parse_percent(value: str) -> float:
    matches = re.findall(r"([+\-]?\d+(?:\.\d+)?)%", value)
    if matches:
        return float(matches[-1])
    cleaned = re.sub(r"[^0-9.\-]", "", value)
    return float(cleaned) if cleaned else 0.0


def split_table_row(line: str) -> list[str]:
    return [clean_cell(cell) for cell in line.strip().strip("|").split("|")]


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Required context file not found: {path}")
    return path.read_text(encoding="utf-8")


def table_rows_after_heading(text: str, heading: str) -> Iterable[list[str]]:
    in_section = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            if in_section:
                break
            in_section = line.lower() == heading.lower()
            continue
        if not in_section or not line.startswith("|"):
            continue
        if set(line.replace("|", "").strip()) <= {"-", ":"}:
            continue
        cells = split_table_row(line)
        if cells and cells[0].lower() not in {"symbol", "ticker"}:
            yield cells


def parse_holdings() -> list[Holding]:
    text = read_text(CONTEXT_DIR / "portfolio-details.md")
    holdings: list[Holding] = []
    for cells in table_rows_after_heading(text, "## Current Positions (from app dashboard)"):
        if len(cells) < 9:
            continue
        try:
            holdings.append(
                Holding(
                    symbol=cells[0].upper(),
                    quantity=parse_money(cells[1]),
                    avg_price=parse_money(cells[2]),
                    current_price=parse_money(cells[3]),
                    market_value=parse_money(cells[4]),
                    pnl_pct=parse_percent(cells[6]),
                    day_change_pct=parse_percent(cells[7]),
                    weight_pct=parse_percent(cells[8]),
                )
            )
        except ValueError:
            continue
    return holdings


def parse_watchlist() -> list[WatchlistEntry]:
    text = read_text(CONTEXT_DIR / "watchlist.md")
    entries: list[WatchlistEntry] = []
    for cells in table_rows_after_heading(text, "## Watchlist Tickers"):
        if len(cells) < 5:
            continue
        score = None if cells[1] in {"-", "—", ""} else parse_money(cells[1])
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


def parse_options() -> list[OptionPosition]:
    path = CONTEXT_DIR / "options-positions.md"
    if not path.exists():
        return []
    text = read_text(path)
    positions: list[OptionPosition] = []
    for cells in table_rows_after_heading(text, "## Short Premium Positions"):
        if len(cells) < 7:
            continue
        try:
            positions.append(
                OptionPosition(
                    ticker=cells[0].upper(),
                    strike=parse_money(cells[1]),
                    option_type=cells[2],
                    expiration=cells[3],
                    credit=parse_money(cells[4]),
                    current=parse_money(cells[5]),
                    contracts=int(parse_money(cells[6])),
                )
            )
        except ValueError:
            continue
    return positions


def portfolio_ideas(holdings: list[Holding]) -> list[TradeIdea]:
    ideas: list[TradeIdea] = []
    for holding in holdings:
        if holding.symbol in {"FFOLX"}:
            continue

        if holding.weight_pct >= 10:
            trim_pct = min(max((holding.weight_pct - 10) / holding.weight_pct, 0.05), 0.30)
            ideas.append(
                TradeIdea(
                    rank_score=76 + min(holding.weight_pct, 18) + max(holding.day_change_pct, 0),
                    ticker=holding.symbol,
                    source="Portfolio concentration",
                    strategy="Covered call or partial trim",
                    action=(
                        f"Harvest {trim_pct:.0%} of position or sell a 30-45 DTE "
                        "0.20-0.30 delta covered call."
                    ),
                    rationale=(
                        f"{holding.symbol} is {holding.weight_pct:.1f}% of portfolio "
                        f"with {holding.pnl_pct:+.1f}% unrealized P&L."
                    ),
                    risk="Do not cap upside around known earnings/catalyst events unless premium compensates.",
                    sizing="Keep post-trade single-name exposure closer to 10-12% until risk limits are reset.",
                )
            )
        elif holding.pnl_pct >= 90 and holding.weight_pct >= 1:
            ideas.append(
                TradeIdea(
                    rank_score=68 + min(holding.pnl_pct / 10, 18),
                    ticker=holding.symbol,
                    source="Portfolio profit harvesting",
                    strategy="Scale-out or covered call",
                    action="Sell a modest covered call or trim 10-20% of the holding.",
                    rationale=(
                        f"Large embedded gain ({holding.pnl_pct:+.1f}%) can fund watchlist entries "
                        "without adding portfolio leverage."
                    ),
                    risk="Avoid over-trimming durable compounders unless thesis or valuation has deteriorated.",
                    sizing="Recycle proceeds into one or two highest-ranked watchlist entries only.",
                )
            )
        elif holding.pnl_pct <= -10 and holding.weight_pct <= 1:
            ideas.append(
                TradeIdea(
                    rank_score=66 + min(abs(holding.pnl_pct) / 2, 18),
                    ticker=holding.symbol,
                    source="Portfolio cleanup",
                    strategy="Exit review",
                    action="Review thesis; exit or tax-loss harvest if no refreshed catalyst exists.",
                    rationale=(
                        f"Small allocation ({holding.weight_pct:.1f}%) with {holding.pnl_pct:+.1f}% P&L "
                        "is not contributing meaningfully to portfolio objectives."
                    ),
                    risk="Confirm liquidity and tax impact before closing.",
                    sizing="No add until thesis is refreshed and rank improves versus watchlist alternatives.",
                )
            )
    return ideas


def watchlist_ideas(watchlist: list[WatchlistEntry]) -> list[TradeIdea]:
    ideas: list[TradeIdea] = []
    for entry in watchlist:
        grade_score = GRADE_SCORE.get(entry.grade, 45)
        status_boost = 8 if "Top Candidate" in entry.status else 4 if "Consider" in entry.status else 0
        if grade_score < 58 and status_boost == 0:
            continue
        score = entry.score if entry.score is not None else grade_score
        ideas.append(
            TradeIdea(
                rank_score=score + status_boost,
                ticker=entry.ticker,
                source=f"Watchlist: {entry.status}",
                strategy="Cash-secured put / starter entry",
                action=(
                    "Wait for a red day or support retest; sell a 30-45 DTE 0.20-0.25 delta CSP "
                    "or buy a 1-2% starter if no liquid options are available."
                ),
                rationale=(
                    f"{entry.company} is graded {entry.grade}"
                    + (f" with score {entry.score:.1f}" if entry.score is not None else "")
                    + " and ranks near the top of the current watchlist."
                ),
                risk="Skip if earnings fall inside the option window or bid/ask spread is wider than 10%.",
                sizing="Cap initial risk at 2-3% of portfolio; add only after assignment thesis is acceptable.",
            )
        )
    return ideas


def option_management_ideas(
    options: list[OptionPosition], holdings_by_symbol: dict[str, Holding]
) -> list[TradeIdea]:
    ideas: list[TradeIdea] = []
    for position in options:
        current_underlying = holdings_by_symbol.get(position.ticker)
        option_return = (
            (position.credit - position.current) / position.credit * 100
            if position.credit > 0
            else 0.0
        )
        notional = position.strike * 100 * position.contracts

        if position.current <= position.credit * 0.50:
            ideas.append(
                TradeIdea(
                    rank_score=92 + min(option_return / 10, 5),
                    ticker=position.ticker,
                    source="Open short premium",
                    strategy=f"Close profitable {position.expiration} {position.strike:g}{position.option_type[0]}",
                    action="Buy to close and release buying power.",
                    rationale=(
                        f"Premium captured is about {option_return:.0f}% "
                        f"(${position.credit:.2f} credit vs ${position.current:.2f} current)."
                    ),
                    risk="Re-open only if IV remains attractive and no earnings conflict exists.",
                    sizing=f"Releases roughly ${notional:,.0f} gross secured notional.",
                )
            )
            continue

        stop_hit = position.current >= position.credit * 2
        challenged = (
            current_underlying is not None
            and position.option_type.lower().startswith("put")
            and current_underlying.current_price < position.strike
        )
        if stop_hit or challenged:
            ideas.append(
                TradeIdea(
                    rank_score=90 if stop_hit else 82,
                    ticker=position.ticker,
                    source="Open short premium",
                    strategy=f"Manage {position.expiration} {position.strike:g}{position.option_type[0]}",
                    action="Evaluate roll/down-and-out or close per 200% premium stop rule.",
                    rationale=(
                        f"Option is marked ${position.current:.2f} vs ${position.credit:.2f} credit"
                        + (
                            f"; underlying ${current_underlying.current_price:.2f} is below strike."
                            if challenged and current_underlying
                            else "."
                        )
                    ),
                    risk="Do not add new correlated short puts until this risk is resolved.",
                    sizing=f"{position.contracts} contracts, roughly ${notional:,.0f} strike notional.",
                )
            )
        else:
            ideas.append(
                TradeIdea(
                    rank_score=62 + min(max(option_return, 0) / 8, 10),
                    ticker=position.ticker,
                    source="Open short premium",
                    strategy=f"Monitor {position.expiration} {position.strike:g}{position.option_type[0]}",
                    action="Hold unless premium reaches 50% profit target or risk doubles.",
                    rationale=(
                        f"Current mark ${position.current:.2f} vs ${position.credit:.2f} credit; "
                        "position is not yet at the standard close trigger."
                    ),
                    risk="Recheck liquidity, earnings, and portfolio options allocation before rolling.",
                    sizing=f"{position.contracts} contracts; avoid increasing size.",
                )
            )
    return ideas


def dedupe_and_rank(ideas: list[TradeIdea], max_ideas: int) -> list[TradeIdea]:
    # Keep distinct strategy/source combinations so the report can include both
    # portfolio-level and option-management ideas for the same ticker.
    keyed: dict[tuple[str, str, str], TradeIdea] = {}
    for idea in ideas:
        key = (idea.ticker, idea.source, idea.strategy)
        if key not in keyed or idea.rank_score > keyed[key].rank_score:
            keyed[key] = idea

    ranked = sorted(keyed.values(), key=lambda item: item.rank_score, reverse=True)
    selected: list[TradeIdea] = []

    def add_bucket(predicate, limit: int) -> None:
        for idea in ranked:
            if len([item for item in selected if predicate(item)]) >= limit:
                break
            if idea not in selected and predicate(idea):
                selected.append(idea)

    # The Telegram message should be balanced: urgent option management first,
    # then portfolio actions, then watchlist entries for new capital.
    add_bucket(lambda idea: idea.source == "Open short premium" and idea.rank_score >= 80, 2)
    add_bucket(lambda idea: idea.source.startswith("Portfolio"), 2)
    add_bucket(lambda idea: idea.source.startswith("Watchlist"), 3)

    for idea in ranked:
        if len(selected) >= max_ideas:
            break
        if idea not in selected:
            selected.append(idea)

    return selected[:max_ideas]


def format_markdown(
    ideas: list[TradeIdea],
    holdings: list[Holding],
    watchlist: list[WatchlistEntry],
    options: list[OptionPosition],
    now: datetime,
) -> str:
    total_value = sum(holding.market_value for holding in holdings)
    top_weights = sorted(holdings, key=lambda item: item.weight_pct, reverse=True)[:5]
    lines = [
        "# Trade Idea Generator",
        "",
        f"**Report date:** {now.date().isoformat()}",
        f"**Universe:** {len(holdings)} portfolio holdings, {len(watchlist)} watchlist names, {len(options)} open short-premium positions.",
        f"**Portfolio market value from context:** ${total_value:,.0f}",
        "",
        "> Educational research only, not investment advice. Verify live prices, option chains, liquidity, earnings dates, and tax impact before any trade.",
        "",
        "## Top Trade Ideas",
        "",
    ]
    for idx, idea in enumerate(ideas, start=1):
        lines.extend(
            [
                f"### {idx}. {idea.ticker} - {idea.strategy}",
                "",
                f"- **Confidence:** {idea.confidence} ({idea.rank_score:.1f})",
                f"- **Source:** {idea.source}",
                f"- **Action:** {idea.action}",
                f"- **Why now:** {idea.rationale}",
                f"- **Risk check:** {idea.risk}",
                f"- **Sizing:** {idea.sizing}",
                "",
            ]
        )
    lines.extend(
        [
            "## Concentration Snapshot",
            "",
            "| Ticker | Weight | P&L | Day Change |",
            "|--------|--------|-----|------------|",
        ]
    )
    for holding in top_weights:
        lines.append(
            f"| {holding.symbol} | {holding.weight_pct:.1f}% | {holding.pnl_pct:+.1f}% | {holding.day_change_pct:+.1f}% |"
        )
    lines.extend(
        [
            "",
            "## Process Notes",
            "",
            "- Portfolio ideas prioritize concentration reduction, profit harvesting, and cleanup of small underperformers.",
            "- Watchlist ideas prioritize B-/better and Consider/Top Candidate names from `context/watchlist.md`.",
            "- Short-premium ideas apply the workspace rules: close near 50% profit, manage near 200% of credit, and avoid earnings-window exposure.",
        ]
    )
    return "\n".join(lines) + "\n"


def format_telegram_message(ideas: list[TradeIdea], now: datetime) -> str:
    lines = [
        f"TRADE IDEA GENERATOR - {now.date().isoformat()}",
        "Portfolio + watchlist scan",
        "",
    ]
    for idx, idea in enumerate(ideas[:6], start=1):
        lines.extend(
            [
                f"{idx}. {idea.ticker} - {idea.strategy}",
                f"   Confidence: {idea.confidence} ({idea.rank_score:.0f})",
                f"   Action: {idea.action}",
                f"   Why: {idea.rationale}",
                f"   Risk: {idea.risk}",
                "",
            ]
        )
    lines.extend(
        [
            "Verify live prices/options/earnings before trading.",
            "Educational research only; not investment advice.",
        ]
    )
    message = "\n".join(lines)
    return message[:3900]


def resolve_chat_id(cli_chat_id: Optional[str]) -> Optional[str]:
    candidates = [
        cli_chat_id,
        os.environ.get("TELEGRAM_CHAT_ID"),
        os.environ.get("TELEGRAM_CHANNEL_ID"),
        os.environ.get("TELEGRAM_CHANNEL_USERNAME"),
        os.environ.get("TELEGRAM_DEFAULT_CHAT_ID"),
        DEFAULT_TELEGRAM_CHAT_ID,
    ]
    return next((candidate for candidate in candidates if candidate), None)


def send_telegram(message: str, chat_id: Optional[str]) -> dict:
    if requests is None:
        raise RuntimeError("The requests package is required for Telegram delivery.")
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set.")
    if not chat_id:
        raise RuntimeError("Telegram chat/channel id is not set.")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = requests.post(
        url,
        json={"chat_id": chat_id, "text": message, "disable_web_page_preview": True},
        timeout=20,
    )
    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError(f"Telegram returned non-JSON response: HTTP {response.status_code}") from exc
    if not response.ok or not payload.get("ok"):
        description = payload.get("description", f"HTTP {response.status_code}")
        raise RuntimeError(f"Telegram send failed for chat {chat_id}: {description}")
    return payload


def build_report(max_ideas: int) -> tuple[str, str, Path, Path, list[TradeIdea]]:
    now = datetime.now(timezone.utc)
    holdings = parse_holdings()
    watchlist = parse_watchlist()
    options = parse_options()
    holdings_by_symbol = {holding.symbol: holding for holding in holdings}

    ideas = dedupe_and_rank(
        portfolio_ideas(holdings)
        + watchlist_ideas(watchlist)
        + option_management_ideas(options, holdings_by_symbol),
        max_ideas=max_ideas,
    )
    if not ideas:
        raise RuntimeError("No trade ideas generated from current context files.")

    OUTPUTS_DIR.mkdir(exist_ok=True)
    date_label = now.date().isoformat()
    report_path = OUTPUTS_DIR / f"trade-idea-generator-{date_label}.md"
    message_path = OUTPUTS_DIR / f"trade-idea-generator-message-{date_label}.txt"

    report = format_markdown(ideas, holdings, watchlist, options, now)
    message = format_telegram_message(ideas, now)
    report_path.write_text(report, encoding="utf-8")
    message_path.write_text(message + "\n", encoding="utf-8")
    return report, message, report_path, message_path, ideas


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-ideas", type=int, default=10, help="Maximum ideas in the markdown report.")
    parser.add_argument("--send-telegram", action="store_true", help="Send Telegram summary after generating files.")
    parser.add_argument("--telegram-chat-id", help="Telegram chat id or channel username override.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    _, message, report_path, message_path, ideas = build_report(max_ideas=args.max_ideas)
    print(f"Generated {len(ideas)} trade ideas")
    print(f"Report: {report_path.relative_to(WORKSPACE)}")
    print(f"Telegram message: {message_path.relative_to(WORKSPACE)}")

    if args.send_telegram:
        chat_id = resolve_chat_id(args.telegram_chat_id)
        result = send_telegram(message, chat_id)
        message_id = result.get("result", {}).get("message_id")
        print(f"Telegram sent to {chat_id} (message_id={message_id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
