#!/usr/bin/env python3
"""Generate trade ideas from portfolio/watchlist context and optionally send Telegram."""

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

import requests


WORKSPACE = Path(__file__).resolve().parent.parent
CONTEXT = WORKSPACE / "context"
OUTPUTS = WORKSPACE / "outputs"
PORTFOLIO_PATH = CONTEXT / "portfolio-details.md"
WATCHLIST_PATH = CONTEXT / "watchlist.md"
OPTIONS_PATH = CONTEXT / "options-positions.md"
CSP_WORKFLOW_PATH = OUTPUTS / "csp-daily-scan-fixed.json"
FMP_BASE = "https://financialmodelingprep.com/api/v3"


@dataclass
class Position:
    symbol: str
    quantity: float
    current: float
    market_value: float
    pnl_pct: float
    day_change_pct: float
    weight: float


@dataclass
class WatchlistItem:
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


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing required context file: {path}")
    return path.read_text(encoding="utf-8")


def parse_money(value: str) -> float:
    cleaned = value.replace("$", "").replace(",", "").replace("%", "").strip()
    if cleaned in {"", "-", "—"}:
        return 0.0
    return float(cleaned)


def first_percent(value: str) -> float:
    match = re.search(r"([+-]?\d+(?:\.\d+)?)%", value)
    return float(match.group(1)) if match else 0.0


def parse_markdown_rows(section_text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        rows.append(cells)
    return rows


def parse_positions(portfolio_text: str) -> list[Position]:
    marker = "## Current Positions"
    start = portfolio_text.find(marker)
    if start == -1:
        return []
    end = portfolio_text.find("## Options", start)
    section = portfolio_text[start:end if end != -1 else len(portfolio_text)]
    rows = parse_markdown_rows(section)
    positions: list[Position] = []
    for cells in rows[1:]:
        if len(cells) < 9 or cells[0].upper() in {"SYMBOL", "TOTALS:"}:
            continue
        try:
            positions.append(
                Position(
                    symbol=cells[0].upper(),
                    quantity=parse_money(cells[1]),
                    current=parse_money(cells[3]),
                    market_value=parse_money(cells[4]),
                    pnl_pct=first_percent(cells[6]),
                    day_change_pct=first_percent(cells[7]),
                    weight=parse_money(cells[8]),
                )
            )
        except ValueError:
            continue
    return positions


def parse_portfolio_value(portfolio_text: str) -> float:
    match = re.search(r"\*\*Total MKT VALUE\*\*\s*\|\s*\$?([\d,]+)", portfolio_text)
    return parse_money(match.group(1)) if match else 0.0


def parse_cash_pct(portfolio_text: str) -> float | None:
    match = re.search(r"\|\s*Cash %\s*\|\s*([\d.]+)", portfolio_text)
    return float(match.group(1)) if match else None


def parse_watchlist(watchlist_text: str) -> list[WatchlistItem]:
    rows = parse_markdown_rows(watchlist_text)
    items: list[WatchlistItem] = []
    for cells in rows[1:]:
        if len(cells) < 5 or cells[0].lower() == "ticker":
            continue
        score = None if cells[1] in {"—", "-", ""} else float(cells[1])
        grade = cells[2].replace("*", "").strip()
        status = cells[4].replace("⭐", "").strip()
        items.append(WatchlistItem(cells[0].upper(), score, grade, cells[3], status))
    return items


def parse_options(options_text: str) -> list[OptionPosition]:
    rows = parse_markdown_rows(options_text)
    positions: list[OptionPosition] = []
    for cells in rows[1:]:
        if len(cells) < 7 or cells[0].lower() == "ticker":
            continue
        try:
            positions.append(
                OptionPosition(
                    ticker=cells[0].upper(),
                    strike=parse_money(cells[1]),
                    option_type=cells[2],
                    expiration=datetime.strptime(cells[3], "%Y-%m-%d").date(),
                    credit=parse_money(cells[4]),
                    current=parse_money(cells[5]),
                    contracts=int(parse_money(cells[6])),
                )
            )
        except ValueError:
            continue
    return positions


def fetch_quotes(tickers: list[str]) -> dict[str, dict[str, Any]]:
    api_key = os.environ.get("FMP_API_KEY")
    if not api_key:
        return {}
    quotes: dict[str, dict[str, Any]] = {}
    for i in range(0, len(tickers), 20):
        batch = ",".join(tickers[i : i + 20])
        try:
            response = requests.get(
                f"{FMP_BASE}/quote/{batch}",
                params={"apikey": api_key},
                timeout=20,
            )
            response.raise_for_status()
            for item in response.json():
                symbol = str(item.get("symbol", "")).upper()
                if symbol:
                    quotes[symbol] = item
        except requests.RequestException as exc:
            print(f"[trade_idea_generator] quote fetch failed for {batch}: {exc}", file=sys.stderr)
    return quotes


def risk_regime(quotes: dict[str, dict[str, Any]]) -> tuple[str, float | None]:
    vix = quotes.get("^VIX", {}).get("price")
    if vix is None:
        return "UNKNOWN", None
    if vix < 15:
        return "LOW", float(vix)
    if vix < 25:
        return "NORMAL", float(vix)
    if vix < 35:
        return "ELEVATED", float(vix)
    return "CRISIS", float(vix)


def position_label(position: Position) -> str:
    if position.weight >= 12:
        return "concentration-management"
    if position.day_change_pct <= -1 and position.weight >= 3:
        return "buy-write or CSP-on-weakness"
    if position.pnl_pct < -10:
        return "review thesis / tax-loss candidate"
    if position.weight < 1:
        return "rounding position / monitor"
    return "hold / income overlay"


def build_ideas(
    positions: list[Position],
    watchlist: list[WatchlistItem],
    option_positions: list[OptionPosition],
    as_of: date,
    quotes: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    ideas: list[dict[str, Any]] = []
    held = {position.symbol for position in positions}
    top_watchlist = [
        item for item in watchlist if item.score is not None and item.score >= 60 and item.ticker not in held
    ][:5]

    for item in top_watchlist:
        quote = quotes.get(item.ticker, {})
        change = quote.get("changesPercentage")
        price = quote.get("price")
        ideas.append(
            {
                "ticker": item.ticker,
                "source": "watchlist",
                "action": "CSP / starter-position candidate",
                "setup": f"{item.grade} watchlist grade, {item.score:.1f} score, {item.status}",
                "price": price,
                "day_change_pct": change,
                "risk": "Use defined risk or small CSP sizing until earnings date and option liquidity are checked.",
                "rank_score": 70 + (item.score or 0) / 3,
            }
        )

    for position in sorted(positions, key=lambda p: p.weight, reverse=True):
        if position.symbol in {"FFOLX"}:
            continue
        label = position_label(position)
        if label == "hold / income overlay" and len(ideas) >= 8:
            continue
        quote = quotes.get(position.symbol, {})
        ideas.append(
            {
                "ticker": position.symbol,
                "source": "portfolio",
                "action": label,
                "setup": (
                    f"{position.weight:.1f}% weight, {position.pnl_pct:+.1f}% P&L, "
                    f"{position.day_change_pct:+.1f}% day change from repo snapshot"
                ),
                "price": quote.get("price") or position.current,
                "day_change_pct": quote.get("changesPercentage"),
                "risk": "Respect 5% new-risk cap and avoid adding to already concentrated names.",
                "rank_score": position.weight + max(position.pnl_pct / 20, 0),
            }
        )
        if len([idea for idea in ideas if idea["source"] == "portfolio"]) >= 6:
            break

    active_options = [opt for opt in option_positions if opt.expiration >= as_of]
    for opt in active_options:
        moneyness_note = "profitable/decaying" if opt.current < opt.credit else "under pressure"
        ideas.append(
            {
                "ticker": opt.ticker,
                "source": "open-options",
                "action": f"Manage {opt.expiration.isoformat()} {opt.strike:g}{opt.option_type[0].upper()}",
                "setup": (
                    f"Credit ${opt.credit:.2f}, current ${opt.current:.2f}, "
                    f"{opt.contracts} contracts: {moneyness_note}"
                ),
                "price": quotes.get(opt.ticker, {}).get("price"),
                "day_change_pct": quotes.get(opt.ticker, {}).get("changesPercentage"),
                "risk": "Close/roll per playbook if loss approaches 2x credit or short strike is threatened.",
                "rank_score": 60 if opt.current > opt.credit else 45,
            }
        )

    return sorted(ideas, key=lambda idea: idea["rank_score"], reverse=True)


def stale_option_notes(option_positions: list[OptionPosition], as_of: date) -> list[str]:
    notes = []
    for opt in option_positions:
        if opt.expiration < as_of:
            notes.append(
                f"{opt.ticker} {opt.expiration.isoformat()} {opt.strike:g}{opt.option_type[0].upper()} "
                "is past expiration in context; reconcile before acting."
            )
    return notes


def fmt_price(value: Any) -> str:
    return "N/A" if value is None else f"${float(value):,.2f}"


def fmt_pct(value: Any) -> str:
    return "N/A" if value is None else f"{float(value):+.2f}%"


def render_report(
    ideas: list[dict[str, Any]],
    positions: list[Position],
    watchlist: list[WatchlistItem],
    option_positions: list[OptionPosition],
    portfolio_value: float,
    cash_pct: float | None,
    regime: str,
    vix: float | None,
    as_of: date,
    quotes_used: bool,
) -> str:
    top_ideas = ideas[:10]
    concentration = sorted(positions, key=lambda item: item.weight, reverse=True)[:5]
    stale_notes = stale_option_notes(option_positions, as_of)
    vix_text = f"{vix:.2f} ({regime})" if vix is not None else f"{regime} (no live VIX; using repo context)"
    source_note = "FMP live quotes + repo context" if quotes_used else "repo context only (FMP_API_KEY not set)"

    lines = [
        f"# Trade Idea Generator — {as_of.isoformat()}",
        "",
        "> Informational only; not investment advice. Validate prices, earnings dates, options chains, and liquidity before trading.",
        "",
        "## Portfolio Context",
        "",
        f"- Portfolio value: ${portfolio_value:,.0f}" if portfolio_value else "- Portfolio value: N/A",
        f"- Cash: {cash_pct:.1f}%" if cash_pct is not None else "- Cash: N/A",
        f"- VIX / regime: {vix_text}",
        f"- Data source: {source_note}",
        "",
        "## Top Trade Ideas",
        "",
        "| Rank | Ticker | Source | Action | Setup | Price | Live Day Chg | Risk Note |",
        "|------|--------|--------|--------|-------|-------|--------------|-----------|",
    ]
    for idx, idea in enumerate(top_ideas, start=1):
        lines.append(
            "| {rank} | {ticker} | {source} | {action} | {setup} | {price} | {day_change} | {risk} |".format(
                rank=idx,
                ticker=idea["ticker"],
                source=idea["source"],
                action=idea["action"],
                setup=idea["setup"].replace("|", "/"),
                price=fmt_price(idea.get("price")),
                day_change=fmt_pct(idea.get("day_change_pct")),
                risk=idea["risk"].replace("|", "/"),
            )
        )

    lines.extend(
        [
            "",
            "## Concentration Dashboard",
            "",
            "| Ticker | Weight | Snapshot Day Chg | P&L | Overlay Bias |",
            "|--------|--------|------------------|-----|--------------|",
        ]
    )
    for position in concentration:
        lines.append(
            f"| {position.symbol} | {position.weight:.1f}% | {position.day_change_pct:+.1f}% | "
            f"{position.pnl_pct:+.1f}% | {position_label(position)} |"
        )

    lines.extend(["", "## Watchlist Focus", ""])
    for item in watchlist[:8]:
        score = "N/A" if item.score is None else f"{item.score:.1f}"
        lines.append(f"- **{item.ticker}** ({item.grade}, {score}) — {item.company}; {item.status}")

    lines.extend(["", "## Open Options Notes", ""])
    active = [opt for opt in option_positions if opt.expiration >= as_of]
    if active:
        for opt in active:
            status = "under pressure" if opt.current > opt.credit else "profitable/decaying"
            lines.append(
                f"- **{opt.ticker} {opt.expiration.isoformat()} {opt.strike:g}{opt.option_type[0].upper()}**: "
                f"credit ${opt.credit:.2f}, current ${opt.current:.2f}, {opt.contracts} contracts ({status})."
            )
    else:
        lines.append("- No active option positions in repo context for the as-of date.")
    if stale_notes:
        lines.append("")
        lines.append("### Reconciliation Flags")
        for note in stale_notes:
            lines.append(f"- {note}")

    lines.extend(
        [
            "",
            "## Execution Guardrails",
            "",
            "- Validate live chain, bid/ask spread, open interest, and earnings timing before placing any order.",
            "- Keep any single new risk allocation under 5% of portfolio value and total options exposure under 30%.",
            "- Prefer defined-risk spreads if VIX is elevated or if the underlying is near earnings.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_telegram(ideas: list[dict[str, Any]], portfolio_value: float, regime: str, vix: float | None, as_of: date) -> str:
    lines = [
        f"Trade Ideas - {as_of.isoformat()}",
        f"Portfolio: ${portfolio_value:,.0f} | VIX: {f'{vix:.2f}' if vix is not None else 'N/A'} ({regime})",
        "",
    ]
    for idx, idea in enumerate(ideas[:5], start=1):
        price = fmt_price(idea.get("price"))
        day_change = fmt_pct(idea.get("day_change_pct"))
        lines.extend(
            [
                f"{idx}. {idea['ticker']} — {idea['action']}",
                f"   {idea['setup']}",
                f"   Price: {price} | Day: {day_change}",
            ]
        )
    lines.extend(
        [
            "",
            "Guardrails: verify live options/earnings/liquidity; max 5% new risk; informational only.",
        ]
    )
    return "\n".join(lines)


def discover_telegram_chat_id() -> str | None:
    env_chat = os.environ.get("TELEGRAM_CHAT_ID")
    if env_chat:
        return env_chat
    if not CSP_WORKFLOW_PATH.exists():
        return None
    try:
        workflow = json.loads(CSP_WORKFLOW_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    for node in workflow.get("nodes", []):
        if node.get("name") == "Send Telegram Alert":
            chat_id = node.get("parameters", {}).get("chatId")
            if isinstance(chat_id, str) and chat_id:
                return chat_id.lstrip("=")
    return None


def send_telegram(text: str) -> dict[str, Any]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    chat_id = discover_telegram_chat_id()
    if not chat_id:
        raise RuntimeError("TELEGRAM_CHAT_ID is not set and no repo chatId could be discovered")
    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text, "disable_web_page_preview": True},
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        raise RuntimeError(f"Telegram API returned non-ok response: {payload}")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=date.today().isoformat(), help="As-of date (YYYY-MM-DD)")
    parser.add_argument("--send-telegram", action="store_true", help="Send top ideas to Telegram")
    parser.add_argument("--output", help="Optional markdown output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    as_of = datetime.strptime(args.date, "%Y-%m-%d").date()
    portfolio_text = read_text(PORTFOLIO_PATH)
    watchlist_text = read_text(WATCHLIST_PATH)
    options_text = read_text(OPTIONS_PATH)

    positions = parse_positions(portfolio_text)
    watchlist = parse_watchlist(watchlist_text)
    option_positions = parse_options(options_text)
    portfolio_value = parse_portfolio_value(portfolio_text)
    cash_pct = parse_cash_pct(portfolio_text)

    universe = sorted({p.symbol for p in positions} | {w.ticker for w in watchlist} | {"^VIX"})
    quotes = fetch_quotes(universe)
    regime, vix = risk_regime(quotes)
    ideas = build_ideas(positions, watchlist, option_positions, as_of, quotes)
    if not ideas:
        raise RuntimeError("No trade ideas generated from current context")

    OUTPUTS.mkdir(exist_ok=True)
    output_path = Path(args.output) if args.output else OUTPUTS / f"trade-idea-generator-{as_of.isoformat()}.md"
    report = render_report(
        ideas=ideas,
        positions=positions,
        watchlist=watchlist,
        option_positions=option_positions,
        portfolio_value=portfolio_value,
        cash_pct=cash_pct,
        regime=regime,
        vix=vix,
        as_of=as_of,
        quotes_used=bool(quotes),
    )
    output_path.write_text(report, encoding="utf-8")

    print(f"Wrote {output_path}")
    if args.send_telegram:
        telegram_text = render_telegram(ideas, portfolio_value, regime, vix, as_of)
        result = send_telegram(telegram_text)
        message_id = result.get("result", {}).get("message_id")
        print(f"Sent Telegram message_id={message_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
