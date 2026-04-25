#!/usr/bin/env python3
"""Generate portfolio/watchlist trade ideas and optionally send Telegram alert."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import textwrap
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_PATH = ROOT / "context" / "portfolio-details.md"
WATCHLIST_PATH = ROOT / "context" / "watchlist.md"
OUTPUT_DIR = ROOT / "outputs"


@dataclass
class Position:
    symbol: str
    quantity: float
    current_price: Optional[float]
    market_value: Optional[float]
    weight: Optional[float]
    pnl_percent: Optional[float]


@dataclass
class OptionPosition:
    ticker: str
    strike: float
    option_type: str
    expiration: str
    credit: Optional[float]
    current: Optional[float]
    contracts: int


@dataclass
class WatchlistCandidate:
    ticker: str
    score: Optional[float]
    grade: str
    company: str
    status: str


@dataclass
class TradeIdea:
    rank: int
    ticker: str
    category: str
    action: str
    rationale: str
    setup: str
    risk: str
    score: float


def clean_cell(value: str) -> str:
    """Normalize markdown table cell content."""
    value = re.sub(r"\*\*", "", value.strip())
    value = value.replace("\u2b50", "").strip()
    return value


def parse_float(value: str) -> Optional[float]:
    """Parse a number from a markdown cell containing currency/percent text."""
    value = clean_cell(value)
    if value in {"", "-", "\u2014", "N/A"}:
        return None
    match = re.search(r"[-+]?\$?([0-9][0-9,]*(?:\.[0-9]+)?)", value)
    if not match:
        return None
    number = match.group(1).replace(",", "")
    try:
        parsed = float(number)
    except ValueError:
        return None
    if value.strip().startswith("-"):
        return -parsed
    return parsed


def parse_percent(value: str) -> Optional[float]:
    """Parse the first percentage from a markdown cell."""
    value = clean_cell(value)
    match = re.search(r"([-+]?[0-9][0-9,]*(?:\.[0-9]+)?)%", value)
    if not match:
        return None
    return float(match.group(1).replace(",", ""))


def markdown_rows(path: Path) -> Iterable[List[str]]:
    """Yield markdown table rows from a file as clean cell lists."""
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|") or set(line.replace("|", "").strip()) <= {"-"}:
            continue
        cells = [clean_cell(cell) for cell in line.strip("|").split("|")]
        if cells:
            yield cells


def load_positions(path: Path) -> List[Position]:
    positions: List[Position] = []
    in_positions = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## Current Positions"):
            in_positions = True
            continue
        if in_positions and line.startswith("## "):
            break
        if not in_positions or not line.startswith("|"):
            continue
        cells = [clean_cell(cell) for cell in line.strip().strip("|").split("|")]
        if not cells or cells[0] in {"SYMBOL", "--------"} or cells[0].startswith("Totals"):
            continue
        if len(cells) < 9:
            continue
        positions.append(
            Position(
                symbol=cells[0],
                quantity=parse_float(cells[1]) or 0.0,
                current_price=parse_float(cells[3]),
                market_value=parse_float(cells[4]),
                weight=parse_percent(cells[8]),
                pnl_percent=parse_percent(cells[6]),
            )
        )
    return positions


def load_options(path: Path) -> List[OptionPosition]:
    options: List[OptionPosition] = []
    in_options = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## Options / Short Premium Positions"):
            in_options = True
            continue
        if in_options and line.startswith("## "):
            break
        if not in_options or not line.startswith("|"):
            continue
        cells = [clean_cell(cell) for cell in line.strip().strip("|").split("|")]
        if not cells or cells[0] in {"Ticker", "--------"}:
            continue
        if len(cells) < 7:
            continue
        options.append(
            OptionPosition(
                ticker=cells[0],
                strike=parse_float(cells[1]) or 0.0,
                option_type=cells[2],
                expiration=cells[3],
                credit=parse_float(cells[4]),
                current=parse_float(cells[5]),
                contracts=int(parse_float(cells[6]) or 0),
            )
        )
    return options


def load_watchlist(path: Path) -> List[WatchlistCandidate]:
    candidates: List[WatchlistCandidate] = []
    for cells in markdown_rows(path):
        if len(cells) < 5 or cells[0] in {"Ticker", "--------"}:
            continue
        if cells[0].startswith("#"):
            continue
        score = None if cells[1] in {"\u2014", "-"} else parse_float(cells[1])
        candidates.append(
            WatchlistCandidate(
                ticker=cells[0],
                score=score,
                grade=cells[2],
                company=cells[3],
                status=cells[4],
            )
        )
    return candidates


def portfolio_value(positions: Sequence[Position]) -> float:
    return sum(position.market_value or 0.0 for position in positions)


def top_concentration(positions: Sequence[Position], count: int = 4) -> float:
    weights = sorted((position.weight or 0.0 for position in positions), reverse=True)
    return sum(weights[:count])


def generate_ideas(
    positions: Sequence[Position],
    options: Sequence[OptionPosition],
    watchlist: Sequence[WatchlistCandidate],
) -> List[TradeIdea]:
    held = {position.symbol for position in positions}
    ideas: List[TradeIdea] = []

    top_weights = sorted(
        [position for position in positions if position.weight is not None],
        key=lambda position: position.weight or 0,
        reverse=True,
    )
    concentrated = [position for position in top_weights if (position.weight or 0) >= 10]
    if concentrated:
        names = ", ".join(f"{p.symbol} {p.weight:.1f}%" for p in concentrated[:4])
        ideas.append(
            TradeIdea(
                rank=0,
                ticker="PORTFOLIO",
                category="Risk overlay",
                action="Harvest premium only where assignment/call-away risk is acceptable",
                rationale=(
                    f"Top concentration is elevated: {names}. Avoid adding fresh long exposure "
                    "to the largest holdings until weights normalize."
                ),
                setup=(
                    "Use 30-45 DTE 0.20-0.30 delta covered calls on 100-share lots for SPY, "
                    "AVGO, GOOGL, or AMAT only if the upside cap fits the portfolio plan."
                ),
                risk="Covered calls can cap upside; keep any new short-premium risk inside the 30% options allocation limit.",
                score=88.0,
            )
        )

    for option in options:
        if not option.expiration:
            continue
        try:
            expiration = dt.date.fromisoformat(option.expiration)
        except ValueError:
            continue
        if expiration < dt.date.today():
            ideas.append(
                TradeIdea(
                    rank=0,
                    ticker=option.ticker,
                    category="Options hygiene",
                    action="Reconcile stale options context before opening related exposure",
                    rationale=(
                        f"Repository still lists a {option.expiration} {option.strike:g} "
                        f"{option.option_type} with {option.contracts} contracts."
                    ),
                    setup="Refresh broker/export data, then decide whether to roll, close, or remove the stale record.",
                    risk="Do not size new premium trades from stale position data.",
                    score=84.0,
                )
            )

    watchlist_scores = [candidate for candidate in watchlist if candidate.score is not None]
    for candidate in sorted(watchlist_scores, key=lambda item: item.score or 0, reverse=True)[:8]:
        score = candidate.score or 0.0
        if candidate.ticker in held:
            score -= 8
        if candidate.status.lower().startswith("avoid"):
            score -= 30
        elif "top candidate" in candidate.status.lower():
            score += 8
        elif "consider" in candidate.status.lower():
            score += 4

        is_semi = candidate.ticker in {"LRCX", "NVDA", "TSM", "KLAC", "ASML", "MRVL"}
        if is_semi:
            score -= 5
            risk = "Semiconductor exposure is already meaningful via AVGO, AMAT, and ASML; size smaller than a normal starter."
        else:
            risk = "Respect valuation and earnings timing; avoid holding short options through unplanned earnings."

        action = "Consider starter entry or cash-secured put"
        if score < 65:
            action = "Watchlist only unless price/risk improves"

        setup = (
            "If options liquidity is acceptable, target a 30-45 DTE 0.20-0.30 delta cash-secured put; "
            "otherwise use a staged equity entry sized below 2% initial portfolio weight."
        )
        if candidate.ticker in held:
            setup = "Already held; add only on a portfolio-level rebalance or material valuation reset."

        ideas.append(
            TradeIdea(
                rank=0,
                ticker=candidate.ticker,
                category="Watchlist candidate",
                action=action,
                rationale=(
                    f"{candidate.company} is rated {candidate.grade} with a {candidate.score:.1f} "
                    f"stock score and status '{candidate.status}'."
                ),
                setup=setup,
                risk=risk,
                score=score,
            )
        )

    ranked = sorted(ideas, key=lambda idea: idea.score, reverse=True)
    for index, idea in enumerate(ranked, start=1):
        idea.rank = index
    return ranked


def report_header(date: dt.date, positions: Sequence[Position], watchlist: Sequence[WatchlistCandidate]) -> str:
    value = portfolio_value(positions)
    concentration = top_concentration(positions)
    return textwrap.dedent(
        f"""\
        # Trade Idea Generator - {date.isoformat()}

        **Inputs:** `context/portfolio-details.md` and `context/watchlist.md`

        **Portfolio market value from repository context:** ${value:,.0f}
        **Top-4 position concentration:** {concentration:.1f}%
        **Watchlist names reviewed:** {len(watchlist)}

        > This is an idea-generation report, not financial advice. Verify live quotes,
        > option chains, liquidity, earnings dates, tax impact, and portfolio constraints
        > before placing any trade.
        """
    )


def render_report(date: dt.date, ideas: Sequence[TradeIdea], positions: Sequence[Position], watchlist: Sequence[WatchlistCandidate]) -> str:
    lines = [report_header(date, positions, watchlist), "## Ranked Ideas", ""]
    for idea in ideas[:10]:
        lines.extend(
            [
                f"### {idea.rank}. {idea.ticker} - {idea.category}",
                "",
                f"- **Action:** {idea.action}",
                f"- **Score:** {idea.score:.1f}",
                f"- **Rationale:** {idea.rationale}",
                f"- **Setup:** {idea.setup}",
                f"- **Risk / guardrail:** {idea.risk}",
                "",
            ]
        )
    lines.extend(
        [
            "## Portfolio Context",
            "",
            "| Symbol | Weight | Current | Market Value | P&L |",
            "|--------|--------|---------|--------------|-----|",
        ]
    )
    for position in sorted(positions, key=lambda item: item.weight or 0.0, reverse=True):
        current = f"${position.current_price:,.2f}" if position.current_price is not None else "N/A"
        market_value = f"${position.market_value:,.0f}" if position.market_value is not None else "N/A"
        weight = f"{position.weight:.1f}%" if position.weight is not None else "N/A"
        pnl = f"{position.pnl_percent:+.1f}%" if position.pnl_percent is not None else "N/A"
        lines.append(f"| {position.symbol} | {weight} | {current} | {market_value} | {pnl} |")
    lines.extend(
        [
            "",
            "## Watchlist Top Scores",
            "",
            "| Ticker | Score | Grade | Company | Status |",
            "|--------|-------|-------|---------|--------|",
        ]
    )
    for candidate in sorted(
        [item for item in watchlist if item.score is not None],
        key=lambda item: item.score or 0,
        reverse=True,
    )[:12]:
        lines.append(
            f"| {candidate.ticker} | {candidate.score:.1f} | {candidate.grade} | "
            f"{candidate.company} | {candidate.status} |"
        )
    lines.append("")
    return "\n".join(lines)


def telegram_message(date: dt.date, ideas: Sequence[TradeIdea]) -> str:
    top = list(ideas[:5])
    lines = [
        f"Altamira Trade Idea Generator - {date.isoformat()}",
        "",
        "Top ideas from current portfolio + watchlist:",
    ]
    for idea in top:
        lines.append(f"{idea.rank}. {idea.ticker}: {idea.action} (score {idea.score:.1f})")
        lines.append(f"   Setup: {idea.setup}")
    lines.extend(
        [
            "",
            "Guardrail: verify live quotes, option chains, earnings, and sizing before trade entry.",
        ]
    )
    return "\n".join(lines)


def send_telegram(message: str, token: str, chat_id: str) -> dict:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    body = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def display_path(path: Path) -> str:
    """Return a workspace-relative path when possible."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--portfolio", type=Path, default=PORTFOLIO_PATH)
    parser.add_argument("--watchlist", type=Path, default=WATCHLIST_PATH)
    parser.add_argument("--out", type=Path, default=None, help="Report path. Defaults to outputs/trade-idea-generator-{date}.md")
    parser.add_argument("--send-telegram", action="store_true", help="Send the summary to Telegram")
    parser.add_argument("--telegram-chat-id", default=os.environ.get("TELEGRAM_CHAT_ID"))
    parser.add_argument("--telegram-token", default=os.environ.get("TELEGRAM_BOT_TOKEN"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    today = dt.date.today()
    output_path = args.out or OUTPUT_DIR / f"trade-idea-generator-{today.isoformat()}.md"

    positions = load_positions(args.portfolio)
    options = load_options(args.portfolio)
    watchlist = load_watchlist(args.watchlist)
    ideas = generate_ideas(positions, options, watchlist)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_report(today, ideas, positions, watchlist), encoding="utf-8")
    print(f"Wrote {display_path(output_path)}")

    if args.send_telegram:
        if not args.telegram_token or not args.telegram_chat_id:
            raise SystemExit("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID/--telegram-chat-id are required to send Telegram")
        response = send_telegram(telegram_message(today, ideas), args.telegram_token, args.telegram_chat_id)
        if not response.get("ok"):
            raise SystemExit(f"Telegram send failed: {response}")
        print("Sent Telegram alert")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
