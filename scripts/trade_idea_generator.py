#!/usr/bin/env python3
"""Generate portfolio/watchlist trade ideas and optionally post to Telegram.

The generator intentionally works from repository context first so scheduled
automations still produce a report when live brokerage/API exports are stale.
If TELEGRAM_CHAT_ID or TELEGRAM_CHANNEL_ID is set, the summary is sent through
the bot token in TELEGRAM_BOT_TOKEN.
"""

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
from datetime import date, datetime
from pathlib import Path
from typing import Iterable


WORKSPACE = Path(__file__).resolve().parents[1]
CONTEXT = WORKSPACE / "context"
OUTPUTS = WORKSPACE / "outputs"


@dataclass
class EquityPosition:
    symbol: str
    qty: float
    avg_price: float | None
    current: float | None
    market_value: float | None
    pnl_pct: float | None
    weight_pct: float | None


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
class WatchlistEntry:
    ticker: str
    score: float | None
    grade: str
    company: str
    status: str


@dataclass
class TradeIdea:
    priority: int
    ticker: str
    strategy: str
    action: str
    rationale: str
    risk: str
    follow_up: str

    @property
    def rank_key(self) -> tuple[int, str]:
        return (-self.priority, self.ticker)


def parse_money(value: str) -> float | None:
    value = value.strip().replace("$", "").replace(",", "")
    if not value or value in {"—", "-"}:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_float(value: str) -> float | None:
    cleaned = re.sub(r"[^0-9.\-]", "", value.strip())
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_pct_from_cell(value: str) -> float | None:
    matches = re.findall(r"([+\-]?\d+(?:\.\d+)?)%", value)
    if not matches:
        return None
    return float(matches[-1])


def strip_markdown(value: str) -> str:
    return value.replace("**", "").replace("⭐", "").strip()


def iter_markdown_table_rows(text: str, header_starts_with: str) -> Iterable[list[str]]:
    """Yield rows for the table whose header line starts with header_starts_with."""
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if line.strip().startswith(header_starts_with):
            row_idx = idx + 2
            while row_idx < len(lines):
                row = lines[row_idx].strip()
                if not row.startswith("|"):
                    break
                cells = [cell.strip() for cell in row.strip("|").split("|")]
                if cells and not all(set(cell) <= {"-"} for cell in cells):
                    yield cells
                row_idx += 1
            break


def read_portfolio() -> tuple[list[EquityPosition], list[OptionPosition], dict[str, str]]:
    path = CONTEXT / "portfolio-details.md"
    text = path.read_text(encoding="utf-8")

    equities: list[EquityPosition] = []
    for cells in iter_markdown_table_rows(text, "| SYMBOL |"):
        if len(cells) < 9 or cells[0].lower().startswith("total"):
            continue
        equities.append(
            EquityPosition(
                symbol=strip_markdown(cells[0]),
                qty=parse_float(cells[1]) or 0,
                avg_price=parse_money(cells[2]),
                current=parse_money(cells[3]),
                market_value=parse_money(cells[4]),
                pnl_pct=parse_pct_from_cell(cells[6]),
                weight_pct=parse_pct_from_cell(cells[8]),
            )
        )

    options: list[OptionPosition] = []
    for cells in iter_markdown_table_rows(text, "| Ticker | Strike | Type | Expiration |"):
        if len(cells) < 7:
            continue
        options.append(
            OptionPosition(
                ticker=strip_markdown(cells[0]),
                strike=parse_float(cells[1]) or 0,
                option_type=strip_markdown(cells[2]),
                expiration=strip_markdown(cells[3]),
                credit=parse_float(cells[4]) or 0,
                current=parse_float(cells[5]) or 0,
                contracts=int(parse_float(cells[6]) or 0),
            )
        )

    summary: dict[str, str] = {}
    for cells in iter_markdown_table_rows(text, "| Metric | Value |"):
        if len(cells) >= 2:
            summary[strip_markdown(cells[0])] = strip_markdown(cells[1])

    return equities, options, summary


def read_watchlist() -> list[WatchlistEntry]:
    text = (CONTEXT / "watchlist.md").read_text(encoding="utf-8")
    entries: list[WatchlistEntry] = []
    for cells in iter_markdown_table_rows(text, "| Ticker | Score | Grade |"):
        if len(cells) < 5:
            continue
        entries.append(
            WatchlistEntry(
                ticker=strip_markdown(cells[0]),
                score=parse_float(cells[1]),
                grade=strip_markdown(cells[2]),
                company=strip_markdown(cells[3]),
                status=strip_markdown(cells[4]),
            )
        )
    return entries


def days_to_expiration(expiration: str, today: date) -> int | None:
    try:
        exp = datetime.strptime(expiration, "%Y-%m-%d").date()
    except ValueError:
        return None
    return (exp - today).days


def describe_dte(dte: int | None) -> str:
    if dte is None:
        return "DTE unavailable"
    if dte < 0:
        return f"expired {abs(dte)} day{'s' if abs(dte) != 1 else ''} ago"
    if dte == 0:
        return "expires today"
    return f"{dte} DTE"


def build_ideas(
    equities: list[EquityPosition],
    options: list[OptionPosition],
    watchlist: list[WatchlistEntry],
    today: date,
) -> list[TradeIdea]:
    ideas: list[TradeIdea] = []
    equity_by_symbol = {p.symbol: p for p in equities}

    for opt in options:
        dte = days_to_expiration(opt.expiration, today)
        underlying = equity_by_symbol.get(opt.ticker)
        stop = opt.credit * 2
        profit_target = opt.credit * 0.5
        dte_text = describe_dte(dte)
        underlying_price = underlying.current if underlying else None
        moneyness = ""
        if underlying_price and opt.option_type.lower() == "put":
            if underlying_price < opt.strike:
                moneyness = f" Underlying snapshot ${underlying_price:.2f} is below strike ${opt.strike:.2f}."
            else:
                cushion = (underlying_price - opt.strike) / underlying_price * 100
                moneyness = f" Snapshot cushion to strike: {cushion:.1f}%."

        if dte is not None and dte < 0:
            ideas.append(
                TradeIdea(
                    priority=100,
                    ticker=opt.ticker,
                    strategy=f"Reconcile expired short {opt.option_type}",
                    action=(
                        f"Refresh broker context for {opt.contracts}x {opt.strike:g} {opt.option_type} "
                        f"{opt.expiration}; repository expiration is already past."
                    ),
                    rationale=f"The option table shows this position {dte_text}; live status must be confirmed before acting.{moneyness}",
                    risk="Using stale option rows can create false close/roll signals and inaccurate portfolio risk.",
                    follow_up="Run the portfolio refresh/export before entering any new trade and remove expired rows after reconciliation.",
                )
            )
            continue

        if opt.current <= profit_target and opt.credit > 0:
            ideas.append(
                TradeIdea(
                    priority=98,
                    ticker=opt.ticker,
                    strategy=f"Manage short {opt.option_type}",
                    action=(
                        f"Close or roll {opt.contracts}x {opt.strike:g} {opt.option_type} "
                        f"{opt.expiration}; current ${opt.current:.2f} is below 50% "
                        f"profit target ${profit_target:.2f}."
                    ),
                    rationale=f"Winner is past the planned 50% profit capture level ({dte_text}).{moneyness}",
                    risk="Leaving the short option open gives back locked-in theta profits and keeps gap risk on the book.",
                    follow_up="If reopening exposure, re-sell only after checking current IV/rank and earnings timing.",
                )
            )
        elif opt.current >= stop and opt.credit > 0:
            ideas.append(
                TradeIdea(
                    priority=100,
                    ticker=opt.ticker,
                    strategy=f"Risk-control short {opt.option_type}",
                    action=(
                        f"Review close/roll for {opt.contracts}x {opt.strike:g} {opt.option_type} "
                        f"{opt.expiration}; current ${opt.current:.2f} exceeds 200% stop ${stop:.2f}."
                    ),
                    rationale=f"Position has breached the documented stop-loss rule ({dte_text}).{moneyness}",
                    risk="Rule breach can turn a planned premium sale into an unmanaged directional position.",
                    follow_up="Use broker Greeks/chain before action; avoid adding size to a losing short premium position.",
                )
            )
        elif dte is not None and dte <= 21:
            ideas.append(
                TradeIdea(
                    priority=90,
                    ticker=opt.ticker,
                    strategy=f"DTE management short {opt.option_type}",
                    action=(
                        f"Plan exit or roll for {opt.contracts}x {opt.strike:g} {opt.option_type} "
                        f"{opt.expiration}; position is inside 21 DTE."
                    ),
                    rationale=f"Gamma risk accelerates late in the option cycle ({dte_text}).{moneyness}",
                    risk="Late-cycle short puts can move from manageable theta trades to assignment/gamma risk quickly.",
                    follow_up="Roll only if thesis and earnings calendar remain clean; otherwise close.",
                )
            )

    for pos in equities:
        if pos.qty < 100 or pos.weight_pct is None:
            continue
        if (pos.weight_pct >= 4.0 and (pos.pnl_pct or 0) >= 25.0) or pos.weight_pct >= 10.0:
            contracts = int(pos.qty // 100)
            priority = 88 + min(10, int(pos.weight_pct or 0))
            ideas.append(
                TradeIdea(
                    priority=priority,
                    ticker=pos.symbol,
                    strategy="Covered call / trim overlay",
                    action=(
                        f"Evaluate selling up to {contracts} covered call contract(s) against shares, "
                        "or trim if portfolio concentration is above target."
                    ),
                    rationale=(
                        f"Position weight {pos.weight_pct:.1f}% with P&L "
                        f"{pos.pnl_pct:+.1f}% creates a monetization opportunity without adding downside exposure."
                    ),
                    risk="Covered calls cap upside; trimming can create tax/friction considerations. Avoid calls through earnings unless intentional.",
                    follow_up="Target 0.20-0.30 delta, 30-45 DTE calls after confirming current chain liquidity.",
                )
            )

    top_watchlist = [
        item
        for item in watchlist
        if item.score is not None and item.score >= 60 and "Avoid" not in item.status
    ]
    for item in sorted(top_watchlist, key=lambda i: i.score or 0, reverse=True)[:5]:
        priority = int(70 + min(20, (item.score or 0) - 55))
        ideas.append(
            TradeIdea(
                priority=priority,
                ticker=item.ticker,
                strategy="Watchlist put spread / staged entry",
                action=(
                    f"Screen {item.ticker} for a defined-risk bull put spread or cash-secured put entry; "
                    "prefer a pullback instead of chasing."
                ),
                rationale=(
                    f"{item.company} is marked {item.status.strip()} with score {item.score:.1f} "
                    f"({item.grade}), making it one of the highest-ranked watchlist candidates."
                ),
                risk="Portfolio is already growth/semiconductor heavy; use defined risk if the setup increases sector concentration.",
                follow_up=f"Run /options-scan {item.ticker}; avoid expirations crossing earnings.",
            )
        )

    for pos in equities:
        if (pos.pnl_pct or 0) < -10 and (pos.weight_pct or 0) <= 1.0:
            ideas.append(
                TradeIdea(
                    priority=72,
                    ticker=pos.symbol,
                    strategy="Thesis review",
                    action="Review whether to exit, hold, or rebuild only after a fresh thesis update.",
                    rationale=f"Small position is down {pos.pnl_pct:.1f}% and may be consuming attention without enough portfolio impact.",
                    risk="Adding to losers without a refreshed thesis can compound opportunity cost.",
                    follow_up=f"Run /company-growth {pos.symbol} or /thesis {pos.symbol} before increasing exposure.",
                )
            )

    deduped: dict[tuple[str, str, str], TradeIdea] = {}
    for idea in ideas:
        key = (idea.ticker, idea.strategy, idea.action)
        existing = deduped.get(key)
        if existing is None or idea.priority > existing.priority:
            deduped[key] = idea
    return sorted(deduped.values(), key=lambda i: i.rank_key)


def format_report(
    ideas: list[TradeIdea],
    equities: list[EquityPosition],
    options: list[OptionPosition],
    watchlist: list[WatchlistEntry],
    summary: dict[str, str],
    generated_on: date,
) -> str:
    top = ideas[:10]
    lines = [
        f"# Trade Idea Generator — {generated_on.isoformat()}",
        "",
        "> Financial disclaimer: This is a research workflow for Altamira Capital paper/portfolio monitoring. It is not investment advice or an order ticket. Verify live prices, liquidity, Greeks, earnings dates, and risk limits before trading.",
        "",
        "## Inputs",
        "",
        f"- Equity positions parsed: {len(equities)}",
        f"- Short-premium positions parsed: {len(options)}",
        f"- Watchlist entries parsed: {len(watchlist)}",
        f"- Portfolio value context: {summary.get('Total MKT VALUE') or summary.get('Portfolio Value') or 'Unavailable'}",
        "",
        "## Top Trade Ideas",
        "",
    ]

    if not top:
        lines.extend(
            [
                "No trade ideas were generated from the current repository context.",
                "",
            ]
        )
    else:
        for idx, idea in enumerate(top, start=1):
            lines.extend(
                [
                    f"### {idx}. {idea.ticker} — {idea.strategy} (priority {idea.priority})",
                    "",
                    f"**Action:** {idea.action}",
                    "",
                    f"**Rationale:** {idea.rationale}",
                    "",
                    f"**Risk:** {idea.risk}",
                    "",
                    f"**Follow-up:** {idea.follow_up}",
                    "",
                ]
            )

    lines.extend(
        [
            "## Portfolio Concentration Snapshot",
            "",
            "| Ticker | Weight | P&L | Current |",
            "|--------|--------|-----|---------|",
        ]
    )
    for pos in sorted(equities, key=lambda p: p.weight_pct or 0, reverse=True)[:10]:
        lines.append(
            f"| {pos.symbol} | {pos.weight_pct:.1f}% | {pos.pnl_pct:+.1f}% | ${pos.current:.2f} |"
            if pos.weight_pct is not None and pos.pnl_pct is not None and pos.current is not None
            else f"| {pos.symbol} | n/a | n/a | n/a |"
        )

    lines.extend(
        [
            "",
            "## Existing Short Premium Positions",
            "",
            "| Ticker | Strike | Type | Expiration | Credit | Current | Contracts |",
            "|--------|--------|------|------------|--------|---------|-----------|",
        ]
    )
    for opt in options:
        lines.append(
            f"| {opt.ticker} | {opt.strike:g} | {opt.option_type} | {opt.expiration} | "
            f"${opt.credit:.2f} | ${opt.current:.2f} | {opt.contracts} |"
        )

    lines.extend(
        [
            "",
            "## Telegram Delivery",
            "",
            "Telegram delivery is attempted by the script when `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` or `TELEGRAM_CHANNEL_ID` are configured.",
            "",
        ]
    )
    return "\n".join(lines)


def format_telegram(ideas: list[TradeIdea], generated_on: date, limit: int = 5) -> str:
    lines = [
        f"TRADE IDEA GENERATOR -- {generated_on.isoformat()}",
        "Research only. Verify live chain, earnings, and risk limits before trading.",
        "",
    ]
    for idx, idea in enumerate(ideas[:limit], start=1):
        lines.extend(
            [
                f"{idx}. {idea.ticker} -- {idea.strategy}",
                f"Action: {idea.action}",
                f"Why: {idea.rationale}",
                f"Next: {idea.follow_up}",
                "",
            ]
        )
    if not ideas:
        lines.append("No qualifying ideas generated from repository context.")
    return "\n".join(lines).strip()


def telegram_chat_id_from_updates(token: str) -> str | None:
    params = urllib.parse.urlencode(
        {
            "limit": 10,
            "allowed_updates": json.dumps(["message", "channel_post", "my_chat_member"]),
        }
    )
    url = f"https://api.telegram.org/bot{token}/getUpdates?{params}"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            payload = json.load(resp)
    except Exception:
        return None
    for update in payload.get("result", []):
        for key in ("channel_post", "message", "my_chat_member"):
            chat = (update.get(key) or {}).get("chat") or {}
            chat_id = chat.get("id")
            if chat_id:
                return str(chat_id)
    return None


def send_telegram(message: str, required: bool = False) -> tuple[bool, str]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
    chat_id = (
        os.environ.get("TELEGRAM_CHAT_ID")
        or os.environ.get("TELEGRAM_CHANNEL_ID")
        or os.environ.get("TG_CHAT_ID")
    )
    if token and not chat_id:
        chat_id = telegram_chat_id_from_updates(token)
    if not token:
        status = "TELEGRAM_BOT_TOKEN is not configured."
        if required:
            raise RuntimeError(status)
        return False, status
    if not chat_id:
        status = "Telegram bot token is configured, but no chat/channel id is available."
        if required:
            raise RuntimeError(status)
        return False, status

    chunks = textwrap.wrap(message, width=3900, replace_whitespace=False, drop_whitespace=False)
    if not chunks:
        chunks = [message]
    for chunk in chunks:
        data = urllib.parse.urlencode(
            {
                "chat_id": chat_id,
                "text": chunk,
                "disable_web_page_preview": "true",
            }
        ).encode("utf-8")
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        with urllib.request.urlopen(url, data=data, timeout=20) as resp:
            payload = json.load(resp)
        if not payload.get("ok"):
            raise RuntimeError(f"Telegram send failed: {payload}")
    return True, f"Sent {len(chunks)} Telegram message chunk(s)."


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Altamira trade ideas from repo context.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Report date, YYYY-MM-DD.")
    parser.add_argument("--send-telegram", action="store_true", help="Attempt Telegram delivery.")
    parser.add_argument(
        "--require-telegram",
        action="store_true",
        help="Exit non-zero if Telegram delivery is requested but unavailable.",
    )
    parser.add_argument("--top", type=int, default=5, help="Number of ideas to include in Telegram summary.")
    args = parser.parse_args()

    try:
        generated_on = datetime.strptime(args.date, "%Y-%m-%d").date()
    except ValueError as exc:
        raise SystemExit(f"Invalid --date value: {args.date}") from exc

    equities, options, summary = read_portfolio()
    watchlist = read_watchlist()
    ideas = build_ideas(equities, options, watchlist, generated_on)
    report = format_report(ideas, equities, options, watchlist, summary, generated_on)
    telegram_message = format_telegram(ideas, generated_on, limit=args.top)

    OUTPUTS.mkdir(exist_ok=True)
    report_path = OUTPUTS / f"trade-idea-generator-{generated_on.isoformat()}.md"
    telegram_path = OUTPUTS / f"trade-idea-generator-telegram-{generated_on.isoformat()}.txt"
    report_path.write_text(report + "\n", encoding="utf-8")
    telegram_path.write_text(telegram_message + "\n", encoding="utf-8")

    print(f"Wrote report: {report_path.relative_to(WORKSPACE)}")
    print(f"Wrote Telegram summary: {telegram_path.relative_to(WORKSPACE)}")
    print(f"Generated {len(ideas)} ideas; top {min(args.top, len(ideas))} prepared for Telegram.")

    if args.send_telegram:
        try:
            sent, status = send_telegram(telegram_message, required=args.require_telegram)
        except Exception as exc:
            print(f"Telegram delivery failed: {exc}", file=sys.stderr)
            return 2
        print(f"Telegram delivery: {status}")
        if args.require_telegram and not sent:
            return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
