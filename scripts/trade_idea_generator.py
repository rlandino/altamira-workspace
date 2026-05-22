#!/usr/bin/env python3
"""
Generate portfolio/watchlist trade ideas and optionally send them to Telegram.

The generator is intentionally self-contained so it can run from cron/Cursor
without depending on the local dashboard. It reads the repository context files,
uses FMP for live quotes/earnings, writes a markdown report plus Telegram text,
and sends through TELEGRAM_BOT_TOKEN when requested.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

try:
    import requests
except ImportError:  # pragma: no cover - handled at runtime in automation
    print("Install requests: pip install requests", file=sys.stderr)
    sys.exit(1)


WORKSPACE = Path(__file__).resolve().parent.parent
CONTEXT_DIR = WORKSPACE / "context"
OUTPUTS_DIR = WORKSPACE / "outputs"
PORTFOLIO_PATH = CONTEXT_DIR / "portfolio-details.md"
WATCHLIST_PATH = CONTEXT_DIR / "watchlist.md"
CSP_WORKFLOW_PATH = OUTPUTS_DIR / "csp-daily-scan-fixed.json"

FMP_API_KEY = os.environ.get("FMP_API_KEY", "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz")
FMP_BASE = "https://financialmodelingprep.com/api/v3"
FMP_V4_BASE = "https://financialmodelingprep.com/api/v4"

MAX_TELEGRAM_CHARS = 3900


@dataclass
class Position:
    ticker: str
    qty: float
    avg_price: float | None
    current: float | None
    market_value: float | None
    cost_basis: float | None
    weight_pct: float | None


@dataclass
class OptionPosition:
    ticker: str
    strike: float
    option_type: str
    expiration: date | None
    credit: float | None
    current: float | None
    contracts: int


@dataclass
class WatchlistItem:
    ticker: str
    score: float | None
    grade: str
    company: str
    status: str


@dataclass
class TradeIdea:
    idea_type: str
    ticker: str
    action: str
    setup: str
    rationale: str
    risk: str
    score: float
    contract: dict[str, Any] | None = None


def clean_cell(value: str) -> str:
    value = value.strip()
    value = value.replace("**", "")
    value = value.replace("⭐", "").strip()
    return value


def parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    text = str(value)
    if not text or text.strip() in {"—", "-", "N/A"}:
        return None
    match = re.search(r"-?\d+(?:,\d{3})*(?:\.\d+)?", text.replace("$", ""))
    if not match:
        return None
    try:
        return float(match.group(0).replace(",", ""))
    except ValueError:
        return None


def parse_percent(value: str | None) -> float | None:
    if value is None:
        return None
    match = re.search(r"(-?\d+(?:\.\d+)?)\s*%", value)
    if not match:
        return parse_float(value)
    return float(match.group(1))


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def read_lines(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Required context file not found: {path}")
    return path.read_text(encoding="utf-8").splitlines()


def extract_table_after_heading(path: Path, heading: str) -> list[dict[str, str]]:
    lines = read_lines(path)
    start = None
    for idx, line in enumerate(lines):
        if line.strip().lower() == heading.lower():
            start = idx + 1
            break
    if start is None:
        return []

    table_lines: list[str] = []
    seen_header = False
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            table_lines.append(stripped)
            seen_header = True
            continue
        if seen_header and stripped:
            continue
        if seen_header and not stripped:
            break

    if len(table_lines) < 2:
        return []

    headers = [clean_cell(part) for part in table_lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for raw_line in table_lines[2:]:
        parts = [clean_cell(part) for part in raw_line.strip("|").split("|")]
        if len(parts) != len(headers):
            continue
        rows.append(dict(zip(headers, parts)))
    return rows


def parse_portfolio_positions() -> list[Position]:
    rows = extract_table_after_heading(PORTFOLIO_PATH, "## Current Positions (from app dashboard)")
    positions: list[Position] = []
    for row in rows:
        ticker = row.get("SYMBOL", "").upper().strip()
        if not ticker or ticker == "TOTALS":
            continue
        qty = parse_float(row.get("QTY")) or 0.0
        if qty <= 0:
            continue
        positions.append(
            Position(
                ticker=ticker,
                qty=qty,
                avg_price=parse_float(row.get("AVG. PRICE")),
                current=parse_float(row.get("CURRENT")),
                market_value=parse_float(row.get("MKT VALUE")),
                cost_basis=parse_float(row.get("COST BASIS")),
                weight_pct=parse_percent(row.get("WEIGHT")),
            )
        )
    return positions


def parse_option_positions(today: date) -> tuple[list[OptionPosition], list[OptionPosition]]:
    rows = extract_table_after_heading(PORTFOLIO_PATH, "## Options / Short Premium Positions")
    active: list[OptionPosition] = []
    expired: list[OptionPosition] = []
    for row in rows:
        expiration = parse_date(row.get("Expiration"))
        option = OptionPosition(
            ticker=row.get("Ticker", "").upper().strip(),
            strike=parse_float(row.get("Strike")) or 0.0,
            option_type=row.get("Type", "").strip(),
            expiration=expiration,
            credit=parse_float(row.get("Credit")),
            current=parse_float(row.get("Current")),
            contracts=int(parse_float(row.get("Contracts")) or 0),
        )
        if expiration and expiration >= today:
            active.append(option)
        else:
            expired.append(option)
    return active, expired


def parse_watchlist() -> list[WatchlistItem]:
    rows = extract_table_after_heading(WATCHLIST_PATH, "## Watchlist Tickers")
    items: list[WatchlistItem] = []
    for row in rows:
        ticker = row.get("Ticker", "").upper().strip()
        if not ticker:
            continue
        items.append(
            WatchlistItem(
                ticker=ticker,
                score=parse_float(row.get("Score")),
                grade=row.get("Grade", "").strip(),
                company=row.get("Company", "").strip(),
                status=row.get("Status", "").strip(),
            )
        )
    return items


def chunked(values: list[str], size: int) -> Iterable[list[str]]:
    for idx in range(0, len(values), size):
        yield values[idx : idx + size]


def http_get_json(url: str, params: dict[str, Any] | None = None, timeout: int = 12) -> Any:
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def fetch_quotes(symbols: list[str]) -> dict[str, dict[str, Any]]:
    quotes: dict[str, dict[str, Any]] = {}
    valid_symbols = [s for s in symbols if re.fullmatch(r"[A-Z.^-]{1,12}", s)]
    for batch in chunked(sorted(set(valid_symbols)), 40):
        data = http_get_json(f"{FMP_BASE}/quote/{','.join(batch)}", {"apikey": FMP_API_KEY})
        if isinstance(data, dict):
            data = [data]
        for quote in data or []:
            symbol = str(quote.get("symbol", "")).upper()
            if symbol:
                quotes[symbol] = quote
    return quotes


def fetch_earnings(symbols: list[str], today: date, horizon_days: int = 45) -> dict[str, dict[str, Any]]:
    end = today + timedelta(days=horizon_days)
    try:
        data = http_get_json(
            f"{FMP_BASE}/earning_calendar",
            {
                "from": today.isoformat(),
                "to": end.isoformat(),
                "apikey": FMP_API_KEY,
            },
            timeout=15,
        )
    except Exception:
        return {}

    wanted = set(symbols)
    earnings: dict[str, dict[str, Any]] = {}
    for row in data or []:
        symbol = str(row.get("symbol", "")).upper()
        if symbol in wanted and symbol not in earnings:
            earnings[symbol] = row
    return earnings


def fetch_option_chain(ticker: str) -> list[dict[str, Any]]:
    try:
        data = http_get_json(f"{FMP_V4_BASE}/options-chain/{ticker}", {"apikey": FMP_API_KEY}, timeout=12)
    except Exception:
        return []
    return data if isinstance(data, list) else []


def option_side(raw: dict[str, Any]) -> str:
    return str(raw.get("type") or raw.get("putCall") or raw.get("side") or raw.get("contractType") or "").lower()


def option_expiration(raw: dict[str, Any]) -> date | None:
    return parse_date(str(raw.get("expiration") or raw.get("expirationDate") or raw.get("expiry") or ""))


def option_number(raw: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        if key in raw and raw[key] is not None:
            parsed = parse_float(str(raw[key]))
            if parsed is not None:
                return parsed
    return None


def find_contract(
    ticker: str,
    contract_type: str,
    target_strike: float,
    today: date,
    dte_min: int = 30,
    dte_max: int = 60,
) -> dict[str, Any] | None:
    contracts = []
    for raw in fetch_option_chain(ticker):
        side = option_side(raw)
        if contract_type not in side:
            continue
        exp = option_expiration(raw)
        if not exp:
            continue
        dte = (exp - today).days
        if dte < dte_min or dte > dte_max:
            continue
        strike = option_number(raw, "strike", "strikePrice")
        bid = option_number(raw, "bid", "bidPrice")
        ask = option_number(raw, "ask", "askPrice")
        if not strike or bid is None or bid <= 0:
            continue
        delta = option_number(raw, "delta")
        oi = option_number(raw, "openInterest", "open_interest") or 0
        volume = option_number(raw, "volume") or 0
        contracts.append(
            {
                "ticker": ticker,
                "type": contract_type,
                "expiration": exp.isoformat(),
                "dte": dte,
                "strike": strike,
                "bid": bid,
                "ask": ask,
                "delta": delta,
                "openInterest": oi,
                "volume": volume,
            }
        )

    if not contracts:
        return None

    def rank(contract: dict[str, Any]) -> tuple[float, float, float, float]:
        delta = contract.get("delta")
        delta_penalty = 0.0
        if delta is not None:
            target_delta = -0.25 if contract_type == "put" else 0.25
            delta_penalty = abs(abs(delta) - abs(target_delta)) * 100
        strike_penalty = abs(contract["strike"] - target_strike) / max(target_strike, 1) * 100
        dte_penalty = abs(contract["dte"] - 40)
        liquidity_bonus = math.log1p(contract["openInterest"] + contract["volume"])
        return (delta_penalty, strike_penalty, dte_penalty, -liquidity_bonus)

    return sorted(contracts, key=rank)[0]


def next_friday(today: date, min_days: int = 30, max_days: int = 45) -> date:
    for offset in range(min_days, max_days + 1):
        candidate = today + timedelta(days=offset)
        if candidate.weekday() == 4:
            return candidate
    return today + timedelta(days=35)


def round_strike(value: float) -> float:
    if value >= 500:
        step = 10
    elif value >= 100:
        step = 5
    elif value >= 50:
        step = 2.5
    else:
        step = 1
    return round(value / step) * step


def quote_price(quote: dict[str, Any] | None, fallback: float | None = None) -> float | None:
    if quote:
        price = parse_float(str(quote.get("price") or quote.get("previousClose") or ""))
        if price:
            return price
    return fallback


def quote_score(quote: dict[str, Any] | None, watch_score: float | None = None) -> float:
    if not quote:
        return watch_score or 0.0
    price = quote_price(quote)
    sma50 = parse_float(str(quote.get("priceAvg50") or ""))
    sma200 = parse_float(str(quote.get("priceAvg200") or ""))
    year_high = parse_float(str(quote.get("yearHigh") or ""))
    volume = parse_float(str(quote.get("volume") or ""))
    avg_volume = parse_float(str(quote.get("avgVolume") or ""))
    change_pct = parse_float(str(quote.get("changesPercentage") or ""))

    score = 50.0
    if price and sma50:
        score += 12 if price > sma50 else -10
    if price and sma200:
        score += 14 if price > sma200 else -14
    if sma50 and sma200:
        score += 10 if sma50 > sma200 else -8
    if price and year_high:
        distance_from_high = (year_high - price) / year_high
        if 0.04 <= distance_from_high <= 0.18:
            score += 8
        elif distance_from_high < 0.02:
            score -= 4
    if volume and avg_volume and avg_volume > 0:
        score += 5 if volume >= avg_volume * 0.6 else -4
    if change_pct is not None:
        if -2 <= change_pct <= 2:
            score += 4
        elif change_pct < -4:
            score -= 6
        elif change_pct > 5:
            score -= 4
    if watch_score is not None:
        score = score * 0.7 + watch_score * 0.3
    return round(max(0.0, min(100.0, score)), 1)


def clamp_score(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 1)


def has_near_earnings(ticker: str, earnings: dict[str, dict[str, Any]], today: date, days: int) -> bool:
    row = earnings.get(ticker)
    if not row:
        return False
    earnings_date = parse_date(str(row.get("date") or ""))
    return bool(earnings_date and 0 <= (earnings_date - today).days <= days)


def build_trade_ideas(
    positions: list[Position],
    watchlist: list[WatchlistItem],
    quotes: dict[str, dict[str, Any]],
    earnings: dict[str, dict[str, Any]],
    today: date,
    include_contracts: bool,
) -> list[TradeIdea]:
    expiration = next_friday(today)
    ideas: list[TradeIdea] = []
    position_tickers = {p.ticker for p in positions}

    covered_call_candidates = [
        p
        for p in positions
        if p.qty >= 100
        and p.ticker not in {"FFOLX"}
        and not has_near_earnings(p.ticker, earnings, today, 21)
    ]
    for position in covered_call_candidates:
        quote = quotes.get(position.ticker)
        price = quote_price(quote, position.current)
        if not price:
            continue
        sma50 = parse_float(str((quote or {}).get("priceAvg50") or ""))
        weight = position.weight_pct or 0.0
        extended = bool(sma50 and price > sma50 * 1.03)
        if not extended and weight < 4:
            continue
        target_strike = round_strike(price * (1.05 if weight >= 10 else 1.07))
        score = clamp_score(quote_score(quote) + min(weight, 15) * 0.8 + (8 if extended else 0))
        contract = find_contract(position.ticker, "call", target_strike, today) if include_contracts else None
        if contract:
            setup = (
                f"Sell covered call: {contract['expiration']} "
                f"${contract['strike']:g}C, bid ${contract['bid']:.2f}"
            )
        else:
            setup = f"Manual chain lookup: {expiration.isoformat()} ~${target_strike:g} covered call"
        ideas.append(
            TradeIdea(
                idea_type="Covered call",
                ticker=position.ticker,
                action="Harvest premium on existing shares",
                setup=setup,
                rationale=(
                    f"Holding has {position.qty:g} shares, {weight:.1f}% portfolio weight, "
                    f"and trades near ${price:.2f}."
                ),
                risk="Upside is capped above the short call; avoid if a near-term breakout is desired.",
                score=score,
                contract=contract,
            )
        )

    investable_status = {"top candidate", "consider", "monitor"}
    for item in watchlist:
        normalized_status = item.status.lower().replace("*", "").strip()
        if not any(status in normalized_status for status in investable_status):
            continue
        if item.ticker in position_tickers and (item.score or 0) < 60:
            continue
        if has_near_earnings(item.ticker, earnings, today, 30):
            continue
        quote = quotes.get(item.ticker)
        price = quote_price(quote)
        if not price:
            continue
        score = quote_score(quote, item.score)
        if score < 50 and (item.score or 0) < 60:
            continue
        target_strike = round_strike(price * 0.9)
        contract = find_contract(item.ticker, "put", target_strike, today) if include_contracts else None
        if contract:
            setup = (
                f"Sell cash-secured put: {contract['expiration']} "
                f"${contract['strike']:g}P, bid ${contract['bid']:.2f}"
            )
        else:
            setup = f"Manual chain lookup: {expiration.isoformat()} ~${target_strike:g} cash-secured put"
        ideas.append(
            TradeIdea(
                idea_type="Cash-secured put",
                ticker=item.ticker,
                action="Enter only at a price you want to own",
                setup=setup,
                rationale=(
                    f"Watchlist grade {item.grade or 'N/A'}, score {item.score if item.score is not None else 'N/A'}, "
                    f"status {item.status}; live trend score {score:.1f}."
                ),
                risk="Skip if bid/ask is wide, earnings date moves inside the option window, or sizing exceeds cash limits.",
                score=round(score, 1),
                contract=contract,
            )
        )

    for position in positions:
        weight = position.weight_pct or 0
        if weight < 12:
            continue
        quote = quotes.get(position.ticker)
        price = quote_price(quote, position.current)
        year_high = parse_float(str((quote or {}).get("yearHigh") or ""))
        near_high = bool(price and year_high and price >= year_high * 0.92)
        score = 55 + min(weight, 20) + (10 if near_high else 0)
        ideas.append(
            TradeIdea(
                idea_type="Risk rebalance",
                ticker=position.ticker,
                action="Review trim or collar",
                setup=f"Position weight {weight:.1f}% versus 5% single-name risk target.",
                rationale="Largest holdings are the main driver of portfolio variance and can fund higher-ranked watchlist entries.",
                risk="Trimming winners can create tax impact and opportunity cost; use limit orders and consider covered calls first.",
                score=round(score, 1),
            )
        )

    ideas.sort(key=lambda idea: idea.score, reverse=True)
    deduped: list[TradeIdea] = []
    seen: set[tuple[str, str]] = set()
    for idea in ideas:
        key = (idea.idea_type, idea.ticker)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(idea)
    return deduped[:10]


def market_regime(quotes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    vix_quote = quotes.get("^VIX") or quotes.get("VIX")
    spy_quote = quotes.get("SPY")
    vix = quote_price(vix_quote)
    spy_change = parse_float(str((spy_quote or {}).get("changesPercentage") or ""))
    if vix is None:
        label = "UNKNOWN"
        sizing = "normal"
    elif vix < 15:
        label = "LOW"
        sizing = "reduced premium, prefer patience"
    elif vix <= 25:
        label = "NORMAL"
        sizing = "standard premium selling size"
    elif vix <= 35:
        label = "ELEVATED"
        sizing = "defined-risk or half-size trades"
    else:
        label = "CRISIS"
        sizing = "cash/hedges; minimal new short premium"
    return {"vix": vix, "label": label, "sizing": sizing, "spy_change": spy_change}


def fmt_money(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"${value:,.0f}"


def render_markdown_report(
    report_date: date,
    positions: list[Position],
    active_options: list[OptionPosition],
    expired_options: list[OptionPosition],
    watchlist: list[WatchlistItem],
    ideas: list[TradeIdea],
    regime: dict[str, Any],
    earnings: dict[str, dict[str, Any]],
) -> str:
    portfolio_value = sum(p.market_value or 0 for p in positions) or None
    top_positions = sorted(positions, key=lambda p: p.weight_pct or 0, reverse=True)[:5]
    top_watchlist = sorted(watchlist, key=lambda w: w.score or -1, reverse=True)[:8]

    lines = [
        f"# Trade Idea Generator - {report_date.isoformat()}",
        "",
        "> For research and paper-trading workflow support only. This is not financial advice.",
        "",
        "## Market Regime",
        "",
        f"- **VIX:** {regime['vix']:.2f} ({regime['label']})" if regime.get("vix") is not None else "- **VIX:** N/A",
        f"- **SPY day change:** {regime['spy_change']:+.2f}%" if regime.get("spy_change") is not None else "- **SPY day change:** N/A",
        f"- **Sizing posture:** {regime['sizing']}",
        "",
        "## Portfolio Inputs",
        "",
        f"- **Parsed portfolio value:** {fmt_money(portfolio_value)}",
        f"- **Equity/fund positions parsed:** {len(positions)}",
        f"- **Active option rows:** {len(active_options)}",
        f"- **Expired option rows skipped:** {len(expired_options)}",
        "",
        "| Top holding | Weight | Market value | Current |",
        "|-------------|--------|--------------|---------|",
    ]
    for position in top_positions:
        lines.append(
            f"| {position.ticker} | {position.weight_pct or 0:.1f}% | "
            f"{fmt_money(position.market_value)} | "
            f"{f'${position.current:.2f}' if position.current is not None else 'N/A'} |"
        )

    lines.extend(
        [
            "",
            "## Top Trade Ideas",
            "",
            "| Rank | Type | Ticker | Score | Setup | Risk control |",
            "|------|------|--------|-------|-------|--------------|",
        ]
    )
    if ideas:
        for idx, idea in enumerate(ideas[:7], start=1):
            lines.append(
                f"| {idx} | {idea.idea_type} | {idea.ticker} | {idea.score:.1f} | "
                f"{idea.setup} | {idea.risk} |"
            )
    else:
        lines.append("| - | No qualifying idea | - | - | Re-run after market data/chain data is available. | - |")

    lines.extend(["", "## Idea Detail", ""])
    for idx, idea in enumerate(ideas[:7], start=1):
        lines.extend(
            [
                f"### {idx}. {idea.ticker} - {idea.idea_type}",
                "",
                f"- **Action:** {idea.action}",
                f"- **Setup:** {idea.setup}",
                f"- **Rationale:** {idea.rationale}",
                f"- **Risk:** {idea.risk}",
            ]
        )
        contract = idea.contract
        if contract:
            lines.extend(
                [
                    f"- **Option details:** DTE {contract.get('dte')}, delta {contract.get('delta')}, "
                    f"OI {contract.get('openInterest')}, volume {contract.get('volume')}",
                ]
            )
        earnings_row = earnings.get(idea.ticker)
        if earnings_row:
            lines.append(f"- **Upcoming earnings:** {earnings_row.get('date')}")
        lines.append("")

    lines.extend(
        [
            "## Watchlist Snapshot",
            "",
            "| Ticker | Score | Grade | Status |",
            "|--------|-------|-------|--------|",
        ]
    )
    for item in top_watchlist:
        lines.append(f"| {item.ticker} | {item.score if item.score is not None else 'N/A'} | {item.grade or 'N/A'} | {item.status} |")

    if active_options:
        lines.extend(["", "## Active Options Parsed", ""])
        for option in active_options:
            lines.append(
                f"- {option.ticker} {option.expiration} ${option.strike:g} {option.option_type}: "
                f"{option.contracts} contracts, credit {option.credit}"
            )

    if expired_options:
        lines.extend(["", "## Expired Option Rows Skipped", ""])
        for option in expired_options:
            lines.append(f"- {option.ticker} {option.expiration} ${option.strike:g} {option.option_type}")

    lines.extend(
        [
            "",
            "## Risk Notes",
            "",
            "- Keep single new position risk near the portfolio risk limits documented in the workspace.",
            "- Confirm option liquidity, bid/ask spread, and earnings date before placing any trade.",
            "- Short premium ideas assume willingness to own the underlying at the breakeven price.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_telegram_text(report_date: date, ideas: list[TradeIdea], regime: dict[str, Any]) -> str:
    lines = [
        f"TRADE IDEA GENERATOR - {report_date.isoformat()}",
        "",
        (
            f"Market: VIX {regime['vix']:.2f} ({regime['label']}), "
            f"SPY {regime['spy_change']:+.2f}%"
            if regime.get("vix") is not None and regime.get("spy_change") is not None
            else f"Market: {regime['label']}"
        ),
        f"Sizing posture: {regime['sizing']}",
        "",
    ]
    if not ideas:
        lines.extend(["No qualifying trade ideas today.", "Re-run after live quote/chain data is available."])
    else:
        lines.append("Top ideas:")
        for idx, idea in enumerate(ideas[:5], start=1):
            lines.extend(
                [
                    f"{idx}. {idea.ticker} - {idea.idea_type} (score {idea.score:.1f})",
                    f"   Setup: {idea.setup}",
                    f"   Why: {idea.rationale}",
                    f"   Risk: {idea.risk}",
                    "",
                ]
            )
    lines.extend(
        [
            "Checklist: confirm liquidity, earnings date, sizing, and price before entry.",
            "Research/paper-trading support only; not financial advice.",
        ]
    )
    text = "\n".join(lines).strip()
    if len(text) <= MAX_TELEGRAM_CHARS:
        return text
    return text[: MAX_TELEGRAM_CHARS - 80].rstrip() + "\n\n[Truncated; see markdown report for full detail.]"


def fallback_telegram_chat_id() -> str | None:
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if chat_id:
        return chat_id
    if not CSP_WORKFLOW_PATH.exists():
        return None
    try:
        data = json.loads(CSP_WORKFLOW_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    for node in data.get("nodes", []):
        if node.get("name") == "Send Telegram Alert":
            value = node.get("parameters", {}).get("chatId")
            if value:
                return str(value).lstrip("=")
    return None


def send_telegram(text: str, edit_message_id: str | None = None) -> dict[str, Any]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = fallback_telegram_chat_id()
    if not token:
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN is not set"}
    if not chat_id:
        return {"ok": False, "error": "TELEGRAM_CHAT_ID is not set and no workflow fallback was found"}

    method = "editMessageText" if edit_message_id else "sendMessage"
    payload: dict[str, Any] = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True,
    }
    if edit_message_id:
        payload["message_id"] = edit_message_id

    url = f"https://api.telegram.org/bot{token}/{method}"
    try:
        response = requests.post(url, json=payload, timeout=15)
        data = response.json()
    except Exception as exc:
        return {"ok": False, "error": str(exc), "method": method, "chat_id": chat_id}

    result = data.get("result") if isinstance(data, dict) else None
    result_summary: dict[str, Any] = {}
    if isinstance(result, dict):
        result_summary = {
            "message_id": result.get("message_id"),
            "date": result.get("date"),
            "edit_date": result.get("edit_date"),
        }
    telegram_summary = {
        "ok": data.get("ok") if isinstance(data, dict) else False,
        "description": data.get("description") if isinstance(data, dict) else None,
        "result": result_summary,
    }

    if response.status_code == 400 and edit_message_id and data.get("description", "").endswith("message is not modified"):
        return {"ok": True, "action": "unchanged", "method": method, "chat_id": chat_id, "telegram": telegram_summary}
    return {
        "ok": bool(data.get("ok")),
        "action": "edited" if edit_message_id else "sent",
        "method": method,
        "chat_id": chat_id,
        "status_code": response.status_code,
        "telegram": telegram_summary,
    }


def write_outputs(report_date: date, markdown: str, telegram_text: str, status: dict[str, Any] | None = None) -> dict[str, Path]:
    OUTPUTS_DIR.mkdir(exist_ok=True)
    stem = f"trade-idea-generator-{report_date.isoformat()}"
    paths = {
        "report": OUTPUTS_DIR / f"{stem}.md",
        "telegram": OUTPUTS_DIR / f"{stem}-telegram.txt",
        "status": OUTPUTS_DIR / f"{stem}-telegram-status.json",
    }
    paths["report"].write_text(markdown, encoding="utf-8")
    paths["telegram"].write_text(telegram_text + "\n", encoding="utf-8")
    if status is not None:
        paths["status"].write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate trade ideas from portfolio and watchlist context.")
    parser.add_argument("--send-telegram", action="store_true", help="Send the Telegram-formatted message.")
    parser.add_argument("--edit-message-id", help="Edit an existing Telegram message instead of sending a new one.")
    parser.add_argument("--skip-option-chain", action="store_true", help="Do not attempt to enrich ideas with option-chain contracts.")
    parser.add_argument("--date", help="Override report date (YYYY-MM-DD). Defaults to today.")
    args = parser.parse_args()

    report_date = parse_date(args.date) if args.date else date.today()
    if report_date is None:
        print("--date must be YYYY-MM-DD", file=sys.stderr)
        return 2

    positions = parse_portfolio_positions()
    active_options, expired_options = parse_option_positions(report_date)
    watchlist = parse_watchlist()

    universe = sorted(
        {
            *(p.ticker for p in positions),
            *(w.ticker for w in watchlist),
            "SPY",
            "^VIX",
        }
    )
    quotes = fetch_quotes(universe)
    earnings = fetch_earnings([s for s in universe if not s.startswith("^")], report_date)
    regime = market_regime(quotes)
    ideas = build_trade_ideas(
        positions=positions,
        watchlist=watchlist,
        quotes=quotes,
        earnings=earnings,
        today=report_date,
        include_contracts=not args.skip_option_chain,
    )

    markdown = render_markdown_report(
        report_date=report_date,
        positions=positions,
        active_options=active_options,
        expired_options=expired_options,
        watchlist=watchlist,
        ideas=ideas,
        regime=regime,
        earnings=earnings,
    )
    telegram_text = render_telegram_text(report_date, ideas, regime)

    status: dict[str, Any] | None = None
    if args.send_telegram or args.edit_message_id:
        status = send_telegram(telegram_text, edit_message_id=args.edit_message_id)

    paths = write_outputs(report_date, markdown, telegram_text, status)
    print(f"Wrote report: {paths['report']}")
    print(f"Wrote Telegram text: {paths['telegram']}")
    if status is not None:
        print(f"Wrote Telegram status: {paths['status']}")
        print(json.dumps(status, indent=2, sort_keys=True))
        return 0 if status.get("ok") else 1
    print("Telegram send skipped; use --send-telegram to deliver.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
