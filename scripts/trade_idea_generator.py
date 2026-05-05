#!/usr/bin/env python3
"""Generate actionable trade ideas from the static portfolio/watchlist context.

The script intentionally works without market-data credentials so the cron can
still produce a useful brief from the repository source of truth. If Telegram
credentials are present, it sends the compact brief to the configured channel.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_PATH = ROOT / "context" / "portfolio-details.md"
WATCHLIST_PATH = ROOT / "context" / "watchlist.md"
OUTPUT_DIR = ROOT / "outputs"


@dataclass(frozen=True)
class Position:
    symbol: str
    qty: float
    avg_price: float
    current: float
    market_value: float
    cost_basis: float
    pnl_pct: float
    day_change_pct: float
    weight: float


@dataclass(frozen=True)
class OptionPosition:
    ticker: str
    strike: float
    kind: str
    expiration: str
    credit: float
    current: float
    contracts: int

    @property
    def unrealized_pnl(self) -> float:
        """Return open P&L in dollars for a short premium position."""
        return (self.credit - self.current) * 100 * self.contracts

    @property
    def capture_pct(self) -> float:
        if self.credit == 0:
            return 0.0
        return (self.credit - self.current) / self.credit * 100


@dataclass(frozen=True)
class WatchlistCandidate:
    ticker: str
    score: float | None
    grade: str
    company: str
    status: str


def parse_money(value: str) -> float:
    cleaned = value.replace("$", "").replace(",", "").replace("%", "").strip()
    if cleaned in {"", "-", "\u2014"}:
        return 0.0
    return float(cleaned)


def parse_first_pct(value: str) -> float:
    match = re.search(r"\(([+-]?\d+(?:\.\d+)?)%\)", value)
    if match:
        return float(match.group(1))
    match = re.search(r"([+-]?\d+(?:\.\d+)?)%", value)
    return float(match.group(1)) if match else 0.0


def markdown_rows(path: Path, section: str) -> Iterable[list[str]]:
    in_section = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_section = line.strip() == f"## {section}"
            continue
        if not in_section or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or cells[0] in {"SYMBOL", "Ticker", "--------"}:
            continue
        if set(cells[0]) == {"-"}:
            continue
        yield cells


def load_positions() -> list[Position]:
    positions: list[Position] = []
    for cells in markdown_rows(PORTFOLIO_PATH, "Current Positions (from app dashboard)"):
        if len(cells) < 9:
            continue
        try:
            positions.append(
                Position(
                    symbol=cells[0],
                    qty=parse_money(cells[1]),
                    avg_price=parse_money(cells[2]),
                    current=parse_money(cells[3]),
                    market_value=parse_money(cells[4]),
                    cost_basis=parse_money(cells[5]),
                    pnl_pct=parse_first_pct(cells[6]),
                    day_change_pct=parse_first_pct(cells[7]),
                    weight=parse_money(cells[8]),
                )
            )
        except ValueError:
            continue
    return positions


def load_option_positions() -> list[OptionPosition]:
    options: list[OptionPosition] = []
    for cells in markdown_rows(PORTFOLIO_PATH, "Options / Short Premium Positions"):
        if len(cells) < 7:
            continue
        try:
            options.append(
                OptionPosition(
                    ticker=cells[0],
                    strike=parse_money(cells[1]),
                    kind=cells[2],
                    expiration=cells[3],
                    credit=parse_money(cells[4]),
                    current=parse_money(cells[5]),
                    contracts=int(parse_money(cells[6])),
                )
            )
        except ValueError:
            continue
    return options


def load_watchlist() -> list[WatchlistCandidate]:
    candidates: list[WatchlistCandidate] = []
    for cells in markdown_rows(WATCHLIST_PATH, "Watchlist Tickers"):
        if len(cells) < 5:
            continue
        score = None if cells[1] in {"\u2014", "-"} else parse_money(cells[1])
        candidates.append(
            WatchlistCandidate(
                ticker=cells[0],
                score=score,
                grade=cells[2].replace("*", ""),
                company=cells[3],
                status=cells[4].replace("\u2b50 ", ""),
            )
        )
    return candidates


def find_position(positions: list[Position], ticker: str) -> Position | None:
    return next((position for position in positions if position.symbol == ticker), None)


def build_report(
    positions: list[Position],
    options: list[OptionPosition],
    watchlist: list[WatchlistCandidate],
    run_date: dt.date,
) -> tuple[str, str]:
    total_value = sum(position.market_value for position in positions)
    concentrated = sorted(
        [position for position in positions if position.weight >= 10],
        key=lambda position: position.weight,
        reverse=True,
    )
    profitable_short_premium = sorted(
        [option for option in options if option.capture_pct >= 50],
        key=lambda option: option.capture_pct,
        reverse=True,
    )
    challenged_short_premium = sorted(
        [option for option in options if option.unrealized_pnl < 0],
        key=lambda option: option.unrealized_pnl,
    )
    top_watchlist = [
        candidate for candidate in watchlist if candidate.status == "Top Candidate"
    ][:5]

    idea_blocks: list[str] = []
    telegram_lines: list[str] = [
        f"TRADE IDEA GENERATOR -- {run_date.isoformat()}",
        "Not financial advice. Verify live prices/options before trading.",
        "",
    ]

    if profitable_short_premium:
        option = profitable_short_premium[0]
        idea_blocks.append(
            textwrap.dedent(
                f"""
                ### 1. Harvest short-premium profit: {option.ticker} {option.strike:g}{option.kind[0].upper()} {option.expiration}

                - **Action:** Buy-to-close or roll only if the next credit is attractive.
                - **Current position:** {option.contracts} contracts, ${option.credit:.2f} credit, ${option.current:.2f} current mark.
                - **Open P&L:** ${option.unrealized_pnl:,.0f} ({option.capture_pct:.1f}% of original credit captured).
                - **Why now:** The position has reached the standard 50%+ profit-taking zone; closing reduces tail risk and frees buying power.
                - **Risk note:** Use live bid/ask and avoid replacing it with lower-quality risk just to stay active.
                """
            ).strip()
        )
        telegram_lines.extend(
            [
                f"1) BTC {option.ticker} {option.strike:g}{option.kind[0].upper()} {option.expiration}",
                f"   P&L ${option.unrealized_pnl:,.0f}; {option.capture_pct:.0f}% credit captured.",
                "",
            ]
        )

    if challenged_short_premium:
        option = challenged_short_premium[0]
        underlying = find_position(positions, option.ticker)
        underlying_text = (
            f"Underlying snapshot: ${underlying.current:.2f}, portfolio weight {underlying.weight:.1f}%."
            if underlying
            else "Underlying snapshot unavailable in context."
        )
        idea_blocks.append(
            textwrap.dedent(
                f"""
                ### 2. Manage challenged short premium: {option.ticker} {option.strike:g}{option.kind[0].upper()} {option.expiration}

                - **Action:** Review for roll-down/out or close if the thesis has weakened.
                - **Current position:** {option.contracts} contracts, ${option.credit:.2f} credit, ${option.current:.2f} current mark.
                - **Open P&L:** ${option.unrealized_pnl:,.0f} ({option.capture_pct:.1f}% of original credit).
                - **Context:** {underlying_text}
                - **Trigger:** Prioritize if short strike is ITM, if delta has expanded, or if assignment would create excess concentration.
                - **Risk note:** Do not roll for a debit; require enough net credit to compensate for longer duration and assignment risk.
                """
            ).strip()
        )
        telegram_lines.extend(
            [
                f"2) Manage {option.ticker} {option.strike:g}{option.kind[0].upper()} {option.expiration}",
                f"   Open P&L ${option.unrealized_pnl:,.0f}; review roll/close with live chain.",
                "",
            ]
        )

    if concentrated:
        top_names = ", ".join(
            f"{position.symbol} {position.weight:.1f}%" for position in concentrated[:4]
        )
        idea_blocks.append(
            textwrap.dedent(
                f"""
                ### 3. Monetize concentration with defined upside: covered calls or trim bands

                - **Action:** For outsized winners, consider 30-45 DTE covered calls 5-8% above spot, or set mechanical trim bands.
                - **Highest weights:** {top_names}.
                - **Portfolio value parsed:** ${total_value:,.0f}.
                - **Why now:** Multiple positions exceed the documented 5% single-position risk guideline, so premium harvesting or trims can reduce concentration without forcing an immediate thesis change.
                - **Risk note:** Avoid writing calls through catalysts where assignment would conflict with long-term conviction.
                """
            ).strip()
        )
        telegram_lines.extend(
            [
                "3) Concentration trade",
                f"   Consider 30-45 DTE CCs/trim bands on {top_names}.",
                "",
            ]
        )

    if top_watchlist:
        watchlist_line = ", ".join(
            f"{candidate.ticker} ({candidate.grade}, {candidate.score:.1f})"
            for candidate in top_watchlist
            if candidate.score is not None
        )
        idea_blocks.append(
            textwrap.dedent(
                f"""
                ### 4. Watchlist cash-secured put candidates

                - **Action:** Build live-chain CSP candidates only on red days or IV spikes; target 30-45 DTE, 0.15-0.25 delta, and premium that meets portfolio risk limits.
                - **Top scored names:** {watchlist_line}.
                - **Why now:** These are the highest-ranked non-portfolio candidates in the static watchlist and can diversify future option premium away from current mega-cap concentration.
                - **Risk note:** Re-check earnings dates before selling premium; do not hold short-dated options through unplanned earnings.
                """
            ).strip()
        )
        telegram_lines.extend(
            [
                "4) CSP watchlist",
                f"   Scan red-day entries: {watchlist_line}.",
                "",
            ]
        )

    positions_table = "\n".join(
        f"| {position.symbol} | {position.weight:.1f}% | ${position.current:.2f} | {position.pnl_pct:+.1f}% |"
        for position in sorted(positions, key=lambda p: p.weight, reverse=True)[:10]
    )
    options_table = "\n".join(
        f"| {option.ticker} | {option.strike:g} {option.kind} | {option.expiration} | ${option.credit:.2f} | ${option.current:.2f} | ${option.unrealized_pnl:,.0f} | {option.capture_pct:+.1f}% |"
        for option in options
    )

    report_sections = [
        f"# Trade Idea Generator - {run_date.isoformat()}",
        "",
        "> Generated from `context/portfolio-details.md` and `context/watchlist.md`.",
        "> This is not financial advice. Verify live prices, option chains, liquidity, earnings dates, tax impact, and portfolio constraints before entering any trade.",
        "",
        "## Executive Summary",
        "",
        f"- Parsed **{len(positions)} equity/ETF/fund positions**, **{len(options)} short-premium positions**, and **{len(watchlist)} watchlist candidates**.",
        f"- Portfolio value parsed from positions: **${total_value:,.0f}**.",
        "- Main themes: harvest mature option profit, actively manage challenged short premium, reduce concentration risk, and scan top watchlist names for disciplined CSP entries.",
        "",
        "## Trade Ideas",
        "",
        "\n\n".join(idea_blocks),
        "",
        "## Top Portfolio Weights",
        "",
        "| Symbol | Weight | Current | P&L |",
        "|--------|--------|---------|-----|",
        positions_table,
        "",
        "## Short Premium Dashboard",
        "",
        "| Ticker | Strike / Type | Expiration | Credit | Current | Open P&L | Capture |",
        "|--------|---------------|------------|--------|---------|----------|---------|",
        options_table,
        "",
        "## Execution Checklist",
        "",
        "1. Confirm live quotes and option chains before trading.",
        "2. Check earnings dates and ex-dividend dates.",
        "3. Keep single-name, sector, options notional, and cash-reserve limits in view.",
        "4. Prefer closing winners over adding correlated risk when VIX is low.",
        "5. Log any executed trade with `/paper-trade`.",
    ]
    report = "\n".join(report_sections).strip() + "\n"

    telegram_lines.append("Full report saved in outputs/.")
    return report, "\n".join(telegram_lines).strip() + "\n"


def send_telegram(message: str, chat_id: str, token: str) -> None:
    data = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode()
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=data,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status >= 400:
                raise RuntimeError(f"Telegram send failed with HTTP {response.status}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram send failed with HTTP {exc.code}: {detail}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=dt.date.today().isoformat())
    parser.add_argument("--send-telegram", action="store_true")
    parser.add_argument("--telegram-chat-id", default=os.environ.get("TELEGRAM_CHAT_ID"))
    parser.add_argument(
        "--telegram-token",
        default=os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN"),
    )
    args = parser.parse_args()

    run_date = dt.date.fromisoformat(args.date)
    positions = load_positions()
    options = load_option_positions()
    watchlist = load_watchlist()
    if not positions or not watchlist:
        print("Missing portfolio or watchlist data; cannot generate trade ideas.", file=sys.stderr)
        return 1

    report, telegram_message = build_report(positions, options, watchlist, run_date)
    OUTPUT_DIR.mkdir(exist_ok=True)
    report_path = OUTPUT_DIR / f"trade-idea-generator-{run_date.isoformat()}.md"
    telegram_path = OUTPUT_DIR / f"trade-idea-generator-telegram-{run_date.isoformat()}.txt"
    report_path.write_text(report, encoding="utf-8")
    telegram_path.write_text(telegram_message, encoding="utf-8")

    print(f"Wrote {report_path.relative_to(ROOT)}")
    print(f"Wrote {telegram_path.relative_to(ROOT)}")

    if args.send_telegram:
        if not args.telegram_chat_id:
            print(
                "Telegram send skipped: TELEGRAM_CHAT_ID or --telegram-chat-id is required.",
                file=sys.stderr,
            )
        elif not args.telegram_token:
            print(
                "Telegram send skipped: TELEGRAM_BOT_TOKEN or --telegram-token is required.",
                file=sys.stderr,
            )
        else:
            try:
                send_telegram(telegram_message, args.telegram_chat_id, args.telegram_token)
            except RuntimeError as exc:
                print(str(exc), file=sys.stderr)
            else:
                print("Telegram message sent.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
