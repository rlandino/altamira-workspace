#!/usr/bin/env python3
"""
Altamira Capital trade idea generator.

Builds a daily trade idea report from the current repository portfolio and
watchlist context, then optionally sends a concise summary to Telegram.

Usage:
    python3 scripts/trade_idea_generator.py
    python3 scripts/trade_idea_generator.py --send-telegram
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any


WORKSPACE = Path(__file__).resolve().parent.parent
CONTEXT_DIR = WORKSPACE / "context"
OUTPUTS_DIR = WORKSPACE / "outputs"
PORTFOLIO_FILE = CONTEXT_DIR / "portfolio-details.md"
WATCHLIST_FILE = CONTEXT_DIR / "watchlist.md"
STOCK_SCORER_FILE = WORKSPACE / "scripts" / "stock-scorer.py"
FMP_BASE = "https://financialmodelingprep.com/api/v3"
MASSIVE_BASE = "https://api.massive.com/v3"
USER_AGENT = "Altamira Trade Idea Generator/1.0"


@dataclass
class Position:
    symbol: str
    quantity: float
    avg_price: float | None
    current: float | None
    market_value: float | None
    cost_basis: float | None
    pnl_text: str
    day_change_text: str
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
    rank: int
    ticker: str
    category: str
    action: str
    setup: str
    rationale: str
    risk: str
    data: dict[str, Any]
    score: float


def clean_money(value: str) -> float | None:
    value = value.strip()
    if not value or value in {"-", "N/A"}:
        return None
    neg = value.startswith("-")
    cleaned = re.sub(r"[^0-9.]", "", value)
    if not cleaned:
        return None
    try:
        number = float(cleaned)
    except ValueError:
        return None
    return -number if neg else number


def clean_float(value: str) -> float | None:
    value = value.strip().replace("%", "").replace(",", "")
    value = value.replace("$", "")
    if not value or value in {"-", "N/A", "—"}:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_markdown_table(lines: list[str], header_starts: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    header: list[str] | None = None
    in_table = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(header_starts):
            header = [cell.strip() for cell in stripped.strip("|").split("|")]
            in_table = True
            continue

        if in_table and stripped.startswith("|") and "---" in stripped:
            continue

        if in_table and stripped.startswith("|") and header:
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if len(cells) != len(header):
                continue
            rows.append(dict(zip(header, cells)))
            continue

        if in_table and not stripped.startswith("|"):
            break

    return rows


def parse_portfolio() -> tuple[list[Position], list[OptionPosition], float | None]:
    if not PORTFOLIO_FILE.exists():
        raise FileNotFoundError(f"Missing {PORTFOLIO_FILE}")

    lines = PORTFOLIO_FILE.read_text(encoding="utf-8").splitlines()
    total_value: float | None = None
    for line in lines:
        if line.strip().startswith("| **Total MKT VALUE**"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) >= 2:
                total_value = clean_money(cells[1])
            break

    position_rows = parse_markdown_table(lines, "| SYMBOL |")
    positions: list[Position] = []
    for row in position_rows:
        symbol = row.get("SYMBOL", "").strip().upper()
        if not symbol:
            continue
        positions.append(
            Position(
                symbol=symbol,
                quantity=clean_float(row.get("QTY", "")) or 0.0,
                avg_price=clean_money(row.get("AVG. PRICE", "")),
                current=clean_money(row.get("CURRENT", "")),
                market_value=clean_money(row.get("MKT VALUE", "")),
                cost_basis=clean_money(row.get("COST BASIS", "")),
                pnl_text=row.get("P&L ($, %)", ""),
                day_change_text=row.get("DAY CHG ($, %)", ""),
                weight_pct=clean_float(row.get("WEIGHT", "")),
            )
        )

    option_rows = parse_markdown_table(lines, "| Ticker | Strike | Type |")
    options: list[OptionPosition] = []
    for row in option_rows:
        ticker = row.get("Ticker", "").strip().upper()
        strike = clean_float(row.get("Strike", ""))
        credit = clean_money(row.get("Credit", ""))
        current = clean_money(row.get("Current", ""))
        contracts = int(clean_float(row.get("Contracts", "")) or 0)
        if not ticker or strike is None or credit is None or current is None:
            continue
        options.append(
            OptionPosition(
                ticker=ticker,
                strike=strike,
                option_type=row.get("Type", "").strip(),
                expiration=row.get("Expiration", "").strip(),
                credit=credit,
                current=current,
                contracts=contracts,
            )
        )

    return positions, options, total_value


def parse_watchlist() -> list[WatchlistEntry]:
    if not WATCHLIST_FILE.exists():
        raise FileNotFoundError(f"Missing {WATCHLIST_FILE}")

    lines = WATCHLIST_FILE.read_text(encoding="utf-8").splitlines()
    rows = parse_markdown_table(lines, "| Ticker | Score |")
    entries: list[WatchlistEntry] = []
    for row in rows:
        ticker = row.get("Ticker", "").strip().upper()
        if not ticker:
            continue
        grade = row.get("Grade", "").replace("*", "").strip()
        entries.append(
            WatchlistEntry(
                ticker=ticker,
                score=clean_float(row.get("Score", "")),
                grade=grade,
                company=row.get("Company", "").strip(),
                status=row.get("Status", "").replace("⭐", "").strip(),
            )
        )
    return entries


def read_repo_constant(name: str) -> str | None:
    if not STOCK_SCORER_FILE.exists():
        return None
    text = STOCK_SCORER_FILE.read_text(encoding="utf-8")
    match = re.search(rf"^{name}\s*=\s*[\"']([^\"']+)[\"']", text, flags=re.MULTILINE)
    return match.group(1) if match else None


def get_api_key(env_name: str, repo_constant: str) -> str | None:
    return os.environ.get(env_name) or read_repo_constant(repo_constant)


def http_json(url: str, timeout: int = 20) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
    return json.loads(raw)


def fetch_fmp(path: str, params: dict[str, Any] | None = None) -> Any:
    key = get_api_key("FMP_API_KEY", "FMP_API_KEY")
    if not key:
        raise RuntimeError("FMP_API_KEY is not configured")
    query = params.copy() if params else {}
    query["apikey"] = key
    url = f"{FMP_BASE}/{path.lstrip('/')}?{urllib.parse.urlencode(query)}"
    return http_json(url)


def chunks(items: list[str], size: int) -> list[list[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def fetch_quotes(symbols: list[str]) -> dict[str, dict[str, Any]]:
    quotes: dict[str, dict[str, Any]] = {}
    unique_symbols = [s for s in dict.fromkeys(symbols) if s and s != "FFOLX"]
    for group in chunks(unique_symbols, 40):
        try:
            data = fetch_fmp(f"quote/{','.join(group)}")
        except Exception as exc:
            print(f"Warning: quote fetch failed for {','.join(group)}: {exc}", file=sys.stderr)
            continue
        if isinstance(data, dict):
            data = [data]
        for item in data or []:
            symbol = item.get("symbol")
            if symbol:
                quotes[str(symbol).upper()] = item
    return quotes


def fetch_earnings(symbols: list[str], start: date, end: date) -> dict[str, dict[str, Any]]:
    calendar: dict[str, dict[str, Any]] = {}
    try:
        data = fetch_fmp(
            "earning_calendar",
            {"from": start.isoformat(), "to": end.isoformat()},
        )
    except Exception as exc:
        print(f"Warning: earnings calendar fetch failed: {exc}", file=sys.stderr)
        return calendar

    wanted = set(symbols)
    for item in data or []:
        symbol = str(item.get("symbol", "")).upper()
        if symbol in wanted and symbol not in calendar:
            calendar[symbol] = item
    return calendar


def parse_expiration(expiration: str | None) -> date | None:
    if not expiration:
        return None
    try:
        return datetime.strptime(expiration[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def dte(expiration: str | None, today: date) -> int | None:
    exp = parse_expiration(expiration)
    if not exp:
        return None
    return (exp - today).days


def option_value(data: dict[str, Any], *paths: str, default: Any = None) -> Any:
    for path in paths:
        current: Any = data
        ok = True
        for part in path.split("."):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                ok = False
                break
        if ok and current is not None:
            return current
    return default


def normalize_contract(raw: dict[str, Any]) -> dict[str, Any]:
    bid = option_value(
        raw,
        "last_quote.bid",
        "last_quote.bid_price",
        "last_quote.bp",
        "bid",
        "bidPrice",
        default=0,
    )
    ask = option_value(
        raw,
        "last_quote.ask",
        "last_quote.ask_price",
        "last_quote.ap",
        "ask",
        "askPrice",
        default=0,
    )
    expiration = option_value(
        raw,
        "details.expiration_date",
        "expirationDate",
        "expiration",
        "expiry",
    )
    return {
        "strike": option_value(raw, "details.strike_price", "strike", "strikePrice"),
        "expiration": expiration,
        "bid": float(bid or 0),
        "ask": float(ask or 0),
        "delta": option_value(raw, "greeks.delta", "delta"),
        "theta": option_value(raw, "greeks.theta", "theta"),
        "iv": option_value(raw, "implied_volatility", "impliedVolatility", "iv"),
        "open_interest": option_value(raw, "open_interest", "openInterest", default=0) or 0,
        "volume": option_value(raw, "day.volume", "volume", "totalVolume", default=0) or 0,
    }


def fetch_massive_options(
    ticker: str,
    contract_type: str,
    start: date,
    end: date,
) -> list[dict[str, Any]]:
    key = get_api_key("MASSIVE_API_KEY", "MASSIVE_API_KEY")
    if not key:
        return []

    params = {
        "apiKey": key,
        "contract_type": contract_type,
        "expiration_date.gte": start.isoformat(),
        "expiration_date.lte": end.isoformat(),
        "limit": 250,
        "sort": "expiration_date",
        "order": "asc",
    }
    url = f"{MASSIVE_BASE}/snapshot/options/{ticker}?{urllib.parse.urlencode(params)}"
    try:
        data = http_json(url, timeout=25)
    except Exception as exc:
        print(f"Warning: options fetch failed for {ticker} {contract_type}: {exc}", file=sys.stderr)
        return []

    results = data.get("results") if isinstance(data, dict) else data
    if not isinstance(results, list):
        return []
    return [normalize_contract(item) for item in results if isinstance(item, dict)]


def pct(value: float | None, default: str = "N/A") -> str:
    return default if value is None else f"{value:.1f}%"


def money(value: float | None, default: str = "N/A") -> str:
    if value is None:
        return default
    if abs(value) >= 1000:
        return f"${value:,.0f}"
    return f"${value:,.2f}"


def round_strike(price: float, direction: str) -> float:
    if price >= 500:
        step = 5
    elif price >= 100:
        step = 2.5
    else:
        step = 1
    raw = price / step
    rounded = math.ceil(raw) * step if direction == "up" else math.floor(raw) * step
    return round(rounded, 2)


def choose_csp_contract(
    ticker: str,
    price: float,
    today: date,
) -> dict[str, Any] | None:
    contracts = fetch_massive_options(ticker, "put", today + timedelta(days=28), today + timedelta(days=52))
    candidates: list[tuple[float, dict[str, Any]]] = []
    for contract in contracts:
        strike = contract.get("strike")
        if not strike:
            continue
        strike = float(strike)
        days = dte(contract.get("expiration"), today)
        if not days or days < 28 or days > 52:
            continue
        if strike / price < 0.82 or strike / price > 0.97:
            continue
        bid = float(contract.get("bid") or 0)
        ask = float(contract.get("ask") or 0)
        if bid <= 0:
            continue
        delta = contract.get("delta")
        abs_delta = abs(float(delta)) if delta is not None else abs(strike / price - 1) * 2.5
        if delta is not None and not (0.18 <= abs_delta <= 0.35):
            continue
        oi = float(contract.get("open_interest") or 0)
        volume = float(contract.get("volume") or 0)
        if oi < 10:
            continue
        annual_return = (bid / strike) * (365 / days) * 100
        spread_penalty = ((ask - bid) / ((ask + bid) / 2)) * 10 if ask and ask > bid else 0
        score = annual_return + min(12, oi / 150) + min(5, volume / 50) - abs(abs_delta - 0.25) * 20 - spread_penalty
        enriched = contract.copy()
        enriched.update(
            {
                "strike": strike,
                "dte": days,
                "annual_return": annual_return,
                "abs_delta": abs_delta,
                "breakeven": strike - bid,
            }
        )
        candidates.append((score, enriched))
    if not candidates:
        strike = round_strike(price * 0.9, "down")
        exp = today + timedelta(days=38)
        return {
            "strike": strike,
            "expiration": exp.isoformat(),
            "dte": 38,
            "bid": None,
            "ask": None,
            "delta": None,
            "annual_return": None,
            "breakeven": None,
            "source": "target-only",
        }
    return sorted(candidates, key=lambda item: item[0], reverse=True)[0][1]


def choose_call_contract(
    ticker: str,
    price: float,
    today: date,
) -> dict[str, Any] | None:
    contracts = fetch_massive_options(ticker, "call", today + timedelta(days=28), today + timedelta(days=52))
    candidates: list[tuple[float, dict[str, Any]]] = []
    for contract in contracts:
        strike = contract.get("strike")
        if not strike:
            continue
        strike = float(strike)
        days = dte(contract.get("expiration"), today)
        if not days or days < 28 or days > 52:
            continue
        if strike / price < 1.03 or strike / price > 1.15:
            continue
        bid = float(contract.get("bid") or 0)
        ask = float(contract.get("ask") or 0)
        if bid <= 0:
            continue
        delta = contract.get("delta")
        abs_delta = abs(float(delta)) if delta is not None else abs(strike / price - 1) * 2.5
        if delta is not None and not (0.18 <= abs_delta <= 0.35):
            continue
        oi = float(contract.get("open_interest") or 0)
        volume = float(contract.get("volume") or 0)
        if oi < 10:
            continue
        income_yield = (bid / price) * 100
        spread_penalty = ((ask - bid) / ((ask + bid) / 2)) * 10 if ask and ask > bid else 0
        score = income_yield * 10 + min(10, oi / 150) + min(5, volume / 50) - abs(abs_delta - 0.25) * 20 - spread_penalty
        enriched = contract.copy()
        enriched.update(
            {
                "strike": strike,
                "dte": days,
                "income_yield": income_yield,
                "abs_delta": abs_delta,
            }
        )
        candidates.append((score, enriched))
    if not candidates:
        strike = round_strike(price * 1.08, "up")
        exp = today + timedelta(days=38)
        return {
            "strike": strike,
            "expiration": exp.isoformat(),
            "dte": 38,
            "bid": None,
            "ask": None,
            "delta": None,
            "income_yield": None,
            "source": "target-only",
        }
    return sorted(candidates, key=lambda item: item[0], reverse=True)[0][1]


def quote_price(symbol: str, quotes: dict[str, dict[str, Any]], fallback: float | None = None) -> float | None:
    quote = quotes.get(symbol, {})
    price = quote.get("price") or quote.get("previousClose")
    try:
        return float(price)
    except (TypeError, ValueError):
        return fallback


def has_near_earnings(symbol: str, earnings: dict[str, dict[str, Any]], today: date, max_days: int = 45) -> bool:
    item = earnings.get(symbol)
    exp = parse_expiration(str(item.get("date", ""))) if item else None
    return bool(exp and 0 <= (exp - today).days <= max_days)


def build_trade_ideas(
    positions: list[Position],
    option_positions: list[OptionPosition],
    watchlist: list[WatchlistEntry],
    quotes: dict[str, dict[str, Any]],
    earnings: dict[str, dict[str, Any]],
    portfolio_value: float | None,
    today: date,
) -> list[TradeIdea]:
    ideas: list[TradeIdea] = []
    portfolio_value = portfolio_value or sum(p.market_value or 0 for p in positions) or 100000

    # 1. Manage existing short premium first because it changes risk immediately.
    for opt in option_positions:
        exp_days = dte(opt.expiration, today)
        if exp_days is not None and exp_days < 0:
            continue
        price = quote_price(opt.ticker, quotes)
        if price is None:
            continue
        credit_capture = (opt.credit - opt.current) / opt.credit if opt.credit > 0 else 0
        distance = (price - opt.strike) / opt.strike if opt.strike else 0
        if credit_capture >= 0.5:
            action = "Close or roll to lock in premium"
            setup = f"Buy back {opt.ticker} {opt.strike:g}P {opt.expiration} near {money(opt.current)}"
            rationale = f"Position has captured about {credit_capture * 100:.0f}% of original credit."
            score = 94 + min(4, credit_capture * 4)
        elif distance < 0:
            action = "Defensive roll/close review"
            setup = f"{opt.ticker} {opt.strike:g}P {opt.expiration} is in the money versus spot {money(price)}"
            rationale = "Short put is below strike; reduce assignment risk before gamma accelerates."
            score = 90
        elif exp_days is not None and exp_days <= 14 and distance < 0.06:
            action = "Watch closely; prepare roll"
            setup = f"{opt.ticker} {opt.strike:g}P expires in {exp_days} days"
            rationale = f"Spot is only {distance * 100:.1f}% above strike."
            score = 82
        else:
            continue
        ideas.append(
            TradeIdea(
                rank=0,
                ticker=opt.ticker,
                category="Risk management",
                action=action,
                setup=setup,
                rationale=rationale,
                risk="Rolling extends duration; closing realizes current mark. Do not add correlated risk until this is addressed.",
                data={"credit": opt.credit, "current": opt.current, "contracts": opt.contracts, "spot": price},
                score=score,
            )
        )

    # 2. Covered call ideas on large profitable equity holdings.
    eligible_calls = [
        p for p in positions
        if p.quantity >= 100 and (p.weight_pct or 0) >= 4 and p.symbol not in {"SPY", "QQQ"}
    ]
    eligible_calls.sort(key=lambda p: (p.weight_pct or 0), reverse=True)
    for pos in eligible_calls[:8]:
        price = quote_price(pos.symbol, quotes, pos.current)
        if price is None:
            continue
        if has_near_earnings(pos.symbol, earnings, today, 35):
            continue
        quote = quotes.get(pos.symbol, {})
        if quote.get("priceAvg50") and price < float(quote["priceAvg50"]):
            continue
        contract = choose_call_contract(pos.symbol, price, today)
        if not contract:
            continue
        strike = contract["strike"]
        bid = contract.get("bid")
        exp = contract.get("expiration")
        shares_covered = int(pos.quantity // 100) * 100
        contracts = int(pos.quantity // 100)
        income = bid * 100 * contracts if bid else None
        rationale = (
            f"Large {pct(pos.weight_pct)} portfolio weight with gains; monetizes upside while keeping core exposure."
        )
        if bid:
            rationale += f" Estimated premium is {money(income)} across {contracts} contracts."
        score = 70 + min(14, (pos.weight_pct or 0) / 1.5)
        ideas.append(
            TradeIdea(
                rank=0,
                ticker=pos.symbol,
                category="Covered call",
                action="Sell covered call"
                if bid else "Check covered call chain",
                setup=f"{pos.symbol} {strike:g}C {exp} ({contract.get('dte')} DTE), target 0.20-0.30 delta",
                rationale=rationale,
                risk=f"Caps upside above {money(strike)} on {shares_covered} shares; avoid selling through unexpected event risk.",
                data={"strike": strike, "expiration": exp, "bid": bid, "contracts": contracts, "spot": price},
                score=score + (5 if bid else 0),
            )
        )

    # 3. CSP ideas from top watchlist candidates, avoiding near-term earnings.
    top_watchlist = [
        item for item in watchlist
        if item.score is not None and item.score >= 58 and not has_near_earnings(item.ticker, earnings, today, 45)
    ]
    top_watchlist.sort(key=lambda item: item.score or 0, reverse=True)
    for entry in top_watchlist[:8]:
        price = quote_price(entry.ticker, quotes)
        if price is None:
            continue
        quote = quotes.get(entry.ticker, {})
        if quote.get("changesPercentage") and float(quote["changesPercentage"]) > 8:
            continue
        contract = choose_csp_contract(entry.ticker, price, today)
        if not contract:
            continue
        strike = contract["strike"]
        bid = contract.get("bid")
        exp = contract.get("expiration")
        collateral = strike * 100
        max_contracts = max(1, int((portfolio_value * 0.02) // collateral))
        score = (entry.score or 0) + (8 if bid else 0)
        rationale = f"Watchlist grade {entry.grade} ({entry.score:.1f}) and no earnings conflict inside the target DTE window."
        if bid:
            rationale += f" Bid implies about {contract.get('annual_return', 0):.1f}% annualized return on collateral."
        ideas.append(
            TradeIdea(
                rank=0,
                ticker=entry.ticker,
                category="Cash-secured put",
                action="Sell CSP"
                if bid else "Check CSP chain",
                setup=f"{entry.ticker} {strike:g}P {exp} ({contract.get('dte')} DTE), target 0.20-0.30 delta",
                rationale=rationale,
                risk=f"Assignment creates long stock exposure at {money(contract.get('breakeven')) if bid else 'strike less credit'}; cap size at {max_contracts} contract(s) unless approved.",
                data={"strike": strike, "expiration": exp, "bid": bid, "max_contracts": max_contracts, "spot": price},
                score=score,
            )
        )

    # 4. Concentration trim ideas when a single equity sleeve is oversized.
    for pos in sorted(positions, key=lambda p: p.weight_pct or 0, reverse=True)[:6]:
        if (pos.weight_pct or 0) < 12:
            continue
        price = quote_price(pos.symbol, quotes, pos.current)
        target_weight = 10.0 if pos.symbol != "SPY" else 15.0
        reduce_weight = max(0.0, (pos.weight_pct or 0) - target_weight)
        if reduce_weight <= 0:
            continue
        trim_value = portfolio_value * reduce_weight / 100
        shares = int(trim_value / price) if price else 0
        ideas.append(
            TradeIdea(
                rank=0,
                ticker=pos.symbol,
                category="Portfolio construction",
                action="Trim overweight sleeve",
                setup=f"Trim about {shares} shares to move {pos.symbol} toward {target_weight:.0f}% target weight",
                rationale=f"{pos.symbol} is {pct(pos.weight_pct)} of the portfolio, above the concentration guide.",
                risk="Trimming can create tax impact and may reduce upside in a continued trend.",
                data={"shares": shares, "trim_value": trim_value, "spot": price},
                score=64 + min(20, reduce_weight * 3),
            )
        )

    ideas.sort(key=lambda idea: idea.score, reverse=True)
    for idx, idea in enumerate(ideas, start=1):
        idea.rank = idx
    return ideas


def market_context(quotes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    vix_quote = quotes.get("^VIX") or quotes.get("VIX") or {}
    spy_quote = quotes.get("SPY") or {}
    vix = vix_quote.get("price")
    regime = "UNKNOWN"
    try:
        vix_float = float(vix)
        if vix_float < 15:
            regime = "LOW"
        elif vix_float <= 25:
            regime = "NORMAL"
        elif vix_float <= 35:
            regime = "ELEVATED"
        else:
            regime = "CRISIS"
    except (TypeError, ValueError):
        vix_float = None
    return {
        "vix": vix_float,
        "regime": regime,
        "spy_price": spy_quote.get("price"),
        "spy_change_pct": spy_quote.get("changesPercentage"),
    }


def render_markdown(
    ideas: list[TradeIdea],
    positions: list[Position],
    watchlist: list[WatchlistEntry],
    option_positions: list[OptionPosition],
    context: dict[str, Any],
    earnings: dict[str, dict[str, Any]],
    output_date: date,
) -> str:
    lines: list[str] = [
        f"# Trade Idea Generator - {output_date.isoformat()}",
        "",
        "> Source: `context/portfolio-details.md` and `context/watchlist.md`, with live quote/options/earnings lookups when available.",
        "",
        "## Executive Summary",
        "",
        f"- Portfolio holdings reviewed: {len(positions)}",
        f"- Open short premium positions reviewed: {len(option_positions)}",
        f"- Watchlist tickers reviewed: {len(watchlist)}",
        f"- VIX regime: {context.get('regime')} ({context.get('vix'):.2f})" if context.get("vix") is not None else f"- VIX regime: {context.get('regime')}",
        f"- SPY: {money(context.get('spy_price'))}, day change {pct(context.get('spy_change_pct'))}",
        "",
        "## Top Trade Ideas",
        "",
    ]

    if not ideas:
        lines.extend([
            "No qualifying trade ideas passed today's filters.",
            "",
        ])
    else:
        lines.append("| Rank | Ticker | Category | Action | Setup | Score |")
        lines.append("|------|--------|----------|--------|-------|-------|")
        for idea in ideas[:10]:
            lines.append(
                f"| {idea.rank} | {idea.ticker} | {idea.category} | {idea.action} | {idea.setup} | {idea.score:.1f} |"
            )
        lines.append("")

        for idea in ideas[:10]:
            lines.extend(
                [
                    f"### {idea.rank}. {idea.ticker} - {idea.category}",
                    "",
                    f"**Action:** {idea.action}",
                    "",
                    f"**Setup:** {idea.setup}",
                    "",
                    f"**Rationale:** {idea.rationale}",
                    "",
                    f"**Risk / management:** {idea.risk}",
                    "",
                ]
            )

    if earnings:
        lines.extend(["## Earnings Conflicts Detected", ""])
        lines.append("| Ticker | Date | EPS Estimate | Revenue Estimate |")
        lines.append("|--------|------|--------------|------------------|")
        for symbol, item in sorted(earnings.items()):
            lines.append(
                f"| {symbol} | {item.get('date', 'N/A')} | {item.get('epsEstimated', 'N/A')} | {item.get('revenueEstimated', 'N/A')} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Notes",
            "",
            "- CSP and covered-call contracts target 28-52 DTE and 0.20-0.30 delta where option-chain data is available.",
            "- Expired short-premium rows in the static portfolio context are ignored for actionable ideas.",
            "- Target-only ideas mean the chain lookup did not return a liquid exact contract; confirm bid/ask, open interest, and earnings before entry.",
            "- Financial calculations are for decision support only and are not investment advice.",
            "",
        ]
    )
    return "\n".join(lines)


def render_telegram(ideas: list[TradeIdea], context: dict[str, Any], report_path: Path, output_date: date) -> str:
    lines = [
        f"TRADE IDEA GENERATOR - {output_date.isoformat()}",
        f"VIX: {context.get('vix'):.2f} ({context.get('regime')})" if context.get("vix") is not None else f"VIX: {context.get('regime')}",
        f"SPY: {money(context.get('spy_price'))}, {pct(context.get('spy_change_pct'))}",
        "",
        "Top ideas:",
    ]
    if not ideas:
        lines.append("No qualifying ideas passed today's filters.")
    else:
        for idea in ideas[:5]:
            bid = idea.data.get("bid")
            extra = f" credit {money(bid)}" if bid else ""
            lines.append(f"{idea.rank}. {idea.ticker} - {idea.action}: {idea.setup}{extra}")
    lines.extend(
        [
            "",
            f"Report: {report_path.as_posix()}",
            "Decision support only; confirm liquidity, earnings, and risk before trading.",
        ]
    )
    text = "\n".join(lines)
    return text[:3900]


def send_telegram(text: str, chat_id: str | None = None) -> tuple[bool, str]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
    target = chat_id or os.environ.get("TELEGRAM_CHAT_ID") or discover_repo_telegram_chat()
    if not token:
        return False, "TELEGRAM_BOT_TOKEN is not set"
    if not target:
        return False, "TELEGRAM_CHAT_ID is not set and no repository fallback chat ID was found"

    payload = urllib.parse.urlencode(
        {
            "chat_id": target,
            "text": text,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return False, f"Telegram HTTP {exc.code}: {body}"
    except Exception as exc:
        return False, f"Telegram send failed: {exc}"

    if not result.get("ok"):
        return False, f"Telegram API returned not ok: {result}"
    return True, f"sent to {target}"


def discover_repo_telegram_chat() -> str | None:
    """Use existing workflow metadata as a fallback chat target."""
    candidates = [
        OUTPUTS_DIR / "csp-daily-scan-fixed.json",
        OUTPUTS_DIR / "n8n-workflow-csp-daily-scan.json",
    ]
    for path in candidates:
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        nodes = data.get("nodes", []) if isinstance(data, dict) else []
        for node in nodes:
            if not isinstance(node, dict):
                continue
            name = str(node.get("name", "")).lower()
            if "telegram" not in name:
                continue
            chat_id = node.get("parameters", {}).get("chatId")
            if chat_id:
                return str(chat_id).lstrip("=")
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate portfolio/watchlist trade ideas.")
    parser.add_argument("--send-telegram", action="store_true", help="Send concise summary to Telegram.")
    parser.add_argument("--telegram-chat-id", help="Override TELEGRAM_CHAT_ID.")
    parser.add_argument("--date", help="Override report date (YYYY-MM-DD).")
    args = parser.parse_args()

    output_date = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else date.today()
    OUTPUTS_DIR.mkdir(exist_ok=True)

    positions, option_positions, portfolio_value = parse_portfolio()
    watchlist = parse_watchlist()

    symbols = [p.symbol for p in positions] + [w.ticker for w in watchlist] + ["SPY", "^VIX"]
    quotes = fetch_quotes(symbols)
    earnings = fetch_earnings([s for s in symbols if s not in {"^VIX", "FFOLX"}], output_date, output_date + timedelta(days=45))
    context = market_context(quotes)
    ideas = build_trade_ideas(
        positions=positions,
        option_positions=option_positions,
        watchlist=watchlist,
        quotes=quotes,
        earnings=earnings,
        portfolio_value=portfolio_value,
        today=output_date,
    )

    report_path = OUTPUTS_DIR / f"trade-idea-generator-{output_date.isoformat()}.md"
    report = render_markdown(
        ideas=ideas,
        positions=positions,
        watchlist=watchlist,
        option_positions=option_positions,
        context=context,
        earnings=earnings,
        output_date=output_date,
    )
    report_path.write_text(report, encoding="utf-8")

    telegram_text = render_telegram(ideas, context, report_path.relative_to(WORKSPACE), output_date)
    telegram_path = OUTPUTS_DIR / f"trade-idea-generator-telegram-{output_date.isoformat()}.txt"
    telegram_path.write_text(telegram_text + "\n", encoding="utf-8")

    print(f"Wrote {report_path.relative_to(WORKSPACE)}")
    print(f"Wrote {telegram_path.relative_to(WORKSPACE)}")
    print("")
    print(telegram_text)

    if args.send_telegram:
        ok, message = send_telegram(telegram_text, args.telegram_chat_id)
        status_path = OUTPUTS_DIR / f"trade-idea-generator-telegram-status-{output_date.isoformat()}.txt"
        status_path.write_text(f"{datetime.now(UTC).isoformat()} {message}\n", encoding="utf-8")
        print("")
        print(f"Telegram: {message}")
        if not ok:
            return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
