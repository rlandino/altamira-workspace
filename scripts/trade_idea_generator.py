#!/usr/bin/env python3
"""Generate portfolio/watchlist trade ideas and optionally send to Telegram.

The generator uses the repository context files as its universe, then fetches
live quotes and option snapshots to produce a concise short-premium idea alert.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import math
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


WORKSPACE = Path(__file__).resolve().parents[1]
CONTEXT_DIR = WORKSPACE / "context"
OUTPUTS_DIR = WORKSPACE / "outputs"
OPTIONS_SCAN_COMMAND = WORKSPACE / ".claude" / "commands" / "options-scan.md"
CSP_FIXED_WORKFLOW = WORKSPACE / "outputs" / "csp-daily-scan-fixed.json"
CSP_WORKFLOW = WORKSPACE / "outputs" / "n8n-workflow-csp-daily-scan.json"

PORTFOLIO_FILE = CONTEXT_DIR / "portfolio-details.md"
WATCHLIST_FILE = CONTEXT_DIR / "watchlist.md"
OPTIONS_POSITIONS_FILE = CONTEXT_DIR / "options-positions.md"

FMP_BASE = "https://financialmodelingprep.com/api/v3"
MASSIVE_BASE = "https://api.massive.com/v3"
TELEGRAM_BASE = "https://api.telegram.org"

MAX_POSITION_PCT = 0.05
OPTIONS_ALLOCATION_LIMIT = 0.30
TARGET_MIN_DTE = 30
TARGET_MAX_DTE = 45
CHAIN_MIN_DTE = 20
CHAIN_MAX_DTE = 60


@dataclass
class Holding:
    symbol: str
    qty: float
    avg_price: float | None
    weight: float | None


@dataclass
class WatchlistItem:
    symbol: str
    score: float | None
    grade: str
    status: str


@dataclass
class ShortPremiumPosition:
    ticker: str
    strike: float
    option_type: str
    expiration: str
    credit: float
    current: float
    contracts: int


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def parse_money(value: str) -> float | None:
    cleaned = value.strip().replace("$", "").replace(",", "").replace("%", "")
    if cleaned in {"", "-", "--", "—"}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_holdings() -> tuple[float, list[Holding]]:
    text = read_text(PORTFOLIO_FILE)
    portfolio_value = 100000.0
    holdings: list[Holding] = []

    match = re.search(r"\*\*Total MKT VALUE\*\*\s*\|\s*\$?([0-9,]+)", text)
    if match:
        parsed = parse_money(match.group(1))
        if parsed:
            portfolio_value = parsed

    in_positions = False
    for line in text.splitlines():
        if line.startswith("| SYMBOL |"):
            in_positions = True
            continue
        if in_positions and (not line.strip() or line.startswith("**Totals:**")):
            break
        if not in_positions or not line.startswith("|") or set(line.strip()) <= {"|", "-", " "}:
            continue

        cells = table_cells(line)
        if len(cells) < 9:
            continue
        symbol = cells[0].upper()
        qty = parse_money(cells[1])
        avg_price = parse_money(cells[2])
        weight = parse_money(cells[8])
        if qty is None or not re.fullmatch(r"[A-Z.]{1,6}", symbol):
            continue
        holdings.append(Holding(symbol=symbol, qty=qty, avg_price=avg_price, weight=weight))

    return portfolio_value, holdings


def parse_watchlist() -> list[WatchlistItem]:
    text = read_text(WATCHLIST_FILE)
    items: list[WatchlistItem] = []
    in_table = False

    for line in text.splitlines():
        if line.startswith("| Ticker |"):
            in_table = True
            continue
        if in_table and (not line.strip() or line.startswith("---")):
            break
        if not in_table or not line.startswith("|") or set(line.strip()) <= {"|", "-", " "}:
            continue
        cells = table_cells(line)
        if len(cells) < 5:
            continue
        symbol = cells[0].upper()
        score = parse_money(cells[1])
        grade = re.sub(r"[*`]", "", cells[2]).strip()
        status = cells[4].replace("⭐", "").strip()
        if re.fullmatch(r"[A-Z.]{1,6}", symbol):
            items.append(WatchlistItem(symbol=symbol, score=score, grade=grade, status=status))

    return items


def parse_short_premium_positions() -> list[ShortPremiumPosition]:
    text = read_text(OPTIONS_POSITIONS_FILE)
    positions: list[ShortPremiumPosition] = []
    in_table = False

    for line in text.splitlines():
        if line.startswith("| Ticker |"):
            in_table = True
            continue
        if in_table and (not line.strip() or line.startswith("**")):
            break
        if not in_table or not line.startswith("|") or set(line.strip()) <= {"|", "-", " "}:
            continue
        cells = table_cells(line)
        if len(cells) < 7:
            continue
        strike = parse_money(cells[1])
        credit = parse_money(cells[4])
        current = parse_money(cells[5])
        contracts = parse_money(cells[6])
        if strike is None or credit is None or current is None or contracts is None:
            continue
        positions.append(
            ShortPremiumPosition(
                ticker=cells[0].upper(),
                strike=strike,
                option_type=cells[2],
                expiration=cells[3],
                credit=credit,
                current=current,
                contracts=int(contracts),
            )
        )

    return positions


def extract_backticked_key(text: str, label: str) -> str | None:
    pattern = rf"{re.escape(label)}.*?\(key:\s*`([^`]+)`\)"
    match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else None


def credential_candidates() -> tuple[str | None, list[str]]:
    command_text = read_text(OPTIONS_SCAN_COMMAND)
    fmp_key = os.environ.get("FMP_API_KEY") or extract_backticked_key(command_text, "FMP API")

    massive_candidates: list[str] = []
    if os.environ.get("MASSIVE_API_KEY"):
        massive_candidates.append(os.environ["MASSIVE_API_KEY"])
    workflow_text = read_text(CSP_FIXED_WORKFLOW) + "\n" + read_text(CSP_WORKFLOW)
    for key in re.findall(r"MASSIVE_API_KEY\s*=\s*'([^']+)'", workflow_text):
        massive_candidates.append(key)
    for key in re.findall(r"apiKey=([A-Za-z0-9_\-]+)", workflow_text):
        massive_candidates.append(key)
    doc_key = extract_backticked_key(command_text, "Massive.com API")
    if doc_key:
        massive_candidates.append(doc_key)

    deduped: list[str] = []
    for key in massive_candidates:
        if key and key not in deduped:
            deduped.append(key)
    return fmp_key, deduped


def telegram_chat_id() -> str | None:
    if os.environ.get("TELEGRAM_CHAT_ID"):
        return os.environ["TELEGRAM_CHAT_ID"]
    workflow_text = read_text(CSP_FIXED_WORKFLOW)
    match = re.search(r'"chatId"\s*:\s*"=?(-?\d+)"', workflow_text)
    return match.group(1) if match else None


def http_json(url: str, timeout: int = 20, method: str = "GET", payload: dict[str, Any] | None = None) -> Any:
    data = None
    headers = {"User-Agent": "Altamira trade idea generator"}
    if payload is not None:
        data = urllib.parse.urlencode(payload).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
    return json.loads(raw)


def fmp_url(path: str, api_key: str, params: dict[str, Any] | None = None) -> str:
    query = dict(params or {})
    query["apikey"] = api_key
    return f"{FMP_BASE}/{path.lstrip('/')}?{urllib.parse.urlencode(query)}"


def massive_url(ticker: str, api_key: str, params: dict[str, Any]) -> str:
    query = dict(params)
    query["apiKey"] = api_key
    return f"{MASSIVE_BASE}/snapshot/options/{ticker}?{urllib.parse.urlencode(query)}"


def fetch_quotes(symbols: list[str], fmp_key: str) -> dict[str, dict[str, Any]]:
    quotes: dict[str, dict[str, Any]] = {}
    chunk_size = 45
    for i in range(0, len(symbols), chunk_size):
        chunk = symbols[i : i + chunk_size]
        data = http_json(fmp_url(f"quote/{','.join(chunk)}", fmp_key), timeout=20)
        if isinstance(data, list):
            for item in data:
                symbol = item.get("symbol")
                if symbol:
                    quotes[str(symbol).upper()] = item
    return quotes


def fetch_vix(fmp_key: str) -> tuple[float, str, int]:
    vix = 20.0
    try:
        data = http_json(fmp_url("quote/%5EVIX", fmp_key), timeout=15)
        if isinstance(data, list) and data:
            vix = float(data[0].get("price") or vix)
    except Exception:
        pass

    if vix < 15:
        return vix, "LOW", 75
    if vix <= 25:
        return vix, "NORMAL", 100
    if vix <= 35:
        return vix, "ELEVATED", 50
    return vix, "CRISIS", 25


def fetch_earnings(fmp_key: str, start: date, end: date) -> dict[str, str]:
    try:
        data = http_json(
            fmp_url(
                "earning_calendar",
                fmp_key,
                {"from": start.isoformat(), "to": end.isoformat()},
            ),
            timeout=25,
        )
    except Exception:
        return {}

    earnings: dict[str, str] = {}
    if isinstance(data, list):
        for item in data:
            symbol = str(item.get("symbol") or "").upper()
            item_date = item.get("date")
            if symbol and item_date:
                earnings[symbol] = str(item_date)
    return earnings


def calc_dte(expiration: str) -> int | None:
    try:
        exp = datetime.strptime(expiration, "%Y-%m-%d").date()
    except ValueError:
        return None
    return (exp - date.today()).days


def normalize_contract(contract: dict[str, Any]) -> dict[str, Any]:
    details = contract.get("details") or {}
    quote = contract.get("last_quote") or {}
    greeks = contract.get("greeks") or {}
    day = contract.get("day") or {}

    bid = quote.get("bid")
    ask = quote.get("ask")
    if bid is None:
        bid = contract.get("bid") or contract.get("bidPrice") or 0
    if ask is None:
        ask = contract.get("ask") or contract.get("askPrice") or 0

    expiration = details.get("expiration_date") or contract.get("expiration") or contract.get("expirationDate")
    dte = calc_dte(expiration) if expiration else None

    return {
        "ticker": details.get("ticker") or contract.get("ticker"),
        "type": details.get("contract_type") or contract.get("contract_type"),
        "strike": details.get("strike_price") or contract.get("strike") or contract.get("strikePrice"),
        "expiration": expiration,
        "dte": dte,
        "bid": float(bid or 0),
        "ask": float(ask or 0),
        "delta": greeks.get("delta") if greeks.get("delta") is not None else contract.get("delta"),
        "theta": greeks.get("theta") if greeks.get("theta") is not None else contract.get("theta"),
        "iv": contract.get("implied_volatility") or contract.get("impliedVolatility") or contract.get("iv"),
        "open_interest": contract.get("open_interest") or contract.get("openInterest") or 0,
        "volume": day.get("volume") or contract.get("volume") or contract.get("totalVolume") or 0,
    }


def fetch_option_snapshot(
    ticker: str,
    option_type: str,
    spot: float,
    massive_keys: list[str],
    min_dte: int = CHAIN_MIN_DTE,
    max_dte: int = CHAIN_MAX_DTE,
) -> tuple[list[dict[str, Any]], str]:
    if option_type == "put":
        strike_min = max(1.0, spot * 0.75)
        strike_max = spot * 1.02
    else:
        strike_min = spot * 0.98
        strike_max = spot * 1.25

    start = date.today() + timedelta(days=min_dte)
    end = date.today() + timedelta(days=max_dte)
    params = {
        "contract_type": option_type,
        "expiration_date.gte": start.isoformat(),
        "expiration_date.lte": end.isoformat(),
        "strike_price.gte": round(strike_min, 2),
        "strike_price.lte": round(strike_max, 2),
        "limit": 250,
    }

    last_error = "not attempted"
    for key in massive_keys:
        try:
            data = http_json(massive_url(ticker, key, params), timeout=8)
            contracts = data.get("results") if isinstance(data, dict) else None
            if isinstance(contracts, list):
                return [normalize_contract(c) for c in contracts], "massive"
            last_error = "unexpected response"
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code}"
            if exc.code not in {401, 403}:
                break
        except Exception as exc:
            last_error = str(exc)
    return [], last_error


def spread_pct(contract: dict[str, Any]) -> float | None:
    bid = contract["bid"]
    ask = contract["ask"]
    if bid <= 0 or ask <= 0:
        return None
    mid = (bid + ask) / 2
    return ((ask - bid) / mid) * 100 if mid > 0 else None


def iv_rank_proxy(iv: float | None) -> float:
    if iv is None:
        return 50.0
    return max(0.0, min(100.0, ((iv - 0.15) / (0.60 - 0.15)) * 100))


def quote_priority(
    symbol: str,
    holding_map: dict[str, Holding],
    watchlist_map: dict[str, WatchlistItem],
) -> float:
    priority = 0.0
    holding = holding_map.get(symbol)
    if holding:
        priority += 100 + (holding.weight or 0)
    watch = watchlist_map.get(symbol)
    if watch:
        priority += watch.score or 20
        if "Top Candidate" in watch.status:
            priority += 25
        elif "Consider" in watch.status:
            priority += 10
    return priority


def quality_screen(
    symbol: str,
    quote: dict[str, Any],
    earnings: dict[str, str],
) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    price = float(quote.get("price") or 0)
    avg50 = quote.get("priceAvg50")
    volume = float(quote.get("volume") or 0)
    day_change = quote.get("changesPercentage")

    if price <= 0:
        reasons.append("missing price")
    if avg50 and price < float(avg50):
        reasons.append("below 50-day average")
    if day_change is not None and float(day_change) > 8:
        reasons.append("single-day move above +8%")
    if volume < 100000 and symbol not in {"SPY", "QQQ"}:
        reasons.append("low quote volume")
    if symbol in earnings:
        reasons.append(f"earnings within 45 days ({earnings[symbol]})")

    return not reasons, reasons


def score_csp(
    symbol: str,
    quote: dict[str, Any],
    contracts: list[dict[str, Any]],
    portfolio_value: float,
    sizing_pct: int,
    source: str,
) -> list[dict[str, Any]]:
    price = float(quote.get("price") or 0)
    year_high = quote.get("yearHigh")
    opportunities: list[dict[str, Any]] = []

    for c in contracts:
        dte = c.get("dte")
        delta = c.get("delta")
        strike = c.get("strike")
        if dte is None or strike is None or delta is None:
            continue
        abs_delta = abs(float(delta))
        if dte < TARGET_MIN_DTE or dte > TARGET_MAX_DTE:
            continue
        if abs_delta < 0.20 or abs_delta > 0.30:
            continue
        if c["bid"] <= 0 or float(c.get("open_interest") or 0) < 50:
            continue
        spread = spread_pct(c)
        if spread is None or spread > 25:
            continue

        strike_float = float(strike)
        collateral = strike_float * 100
        max_allocation = portfolio_value * MAX_POSITION_PCT * (sizing_pct / 100)
        contracts_allowed = math.floor(max_allocation / collateral)
        if contracts_allowed < 1:
            continue

        bid = float(c["bid"])
        annualized_return = (bid / strike_float) * (365 / dte) * 100
        iv_proxy = iv_rank_proxy(float(c["iv"]) if c.get("iv") is not None else None)
        if iv_proxy < 25:
            continue

        return_score = max(0.0, min(100.0, ((annualized_return - 8) / 35) * 100))
        iv_score = iv_proxy
        oi_score = min(100.0, float(c.get("open_interest") or 0) / 10)
        vol_score = min(100.0, float(c.get("volume") or 0) * 2)
        liquidity_score = (oi_score + vol_score) / 2
        trend_score = 70.0
        if year_high and price:
            trend_score = min(100.0, (price / float(year_high)) * 100)
        composite = return_score * 0.40 + iv_score * 0.25 + liquidity_score * 0.25 + trend_score * 0.10

        opportunities.append(
            {
                "strategy": "CSP",
                "symbol": symbol,
                "source": source,
                "strike": strike_float,
                "expiration": c["expiration"],
                "dte": dte,
                "bid": bid,
                "ask": c["ask"],
                "delta": float(delta),
                "iv": c.get("iv"),
                "open_interest": int(c.get("open_interest") or 0),
                "volume": int(c.get("volume") or 0),
                "spread_pct": spread,
                "annualized_return": annualized_return,
                "breakeven": strike_float - bid,
                "contracts": contracts_allowed,
                "premium": bid * 100 * contracts_allowed,
                "collateral": collateral * contracts_allowed,
                "score": composite,
            }
        )

    return opportunities


def score_covered_calls(
    symbol: str,
    holding: Holding,
    quote: dict[str, Any],
    contracts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    price = float(quote.get("price") or 0)
    covered_contracts = math.floor(holding.qty / 100)
    if covered_contracts < 1:
        return []

    opportunities: list[dict[str, Any]] = []
    for c in contracts:
        dte = c.get("dte")
        delta = c.get("delta")
        strike = c.get("strike")
        if dte is None or strike is None or delta is None:
            continue
        delta_float = float(delta)
        if dte < TARGET_MIN_DTE or dte > TARGET_MAX_DTE:
            continue
        if delta_float < 0.20 or delta_float > 0.30:
            continue
        if c["bid"] <= 0 or float(c.get("open_interest") or 0) < 50:
            continue
        strike_float = float(strike)
        if strike_float <= price:
            continue
        spread = spread_pct(c)
        if spread is None or spread > 25:
            continue

        bid = float(c["bid"])
        premium_yield = (bid / price) * 100 if price else 0
        annualized_yield = premium_yield * (365 / dte)
        upside_cap = ((strike_float - price) / price) * 100 if price else 0
        if_called_return = None
        if holding.avg_price:
            if_called_return = ((strike_float + bid - holding.avg_price) / holding.avg_price) * 100
        liquidity_score = min(100.0, float(c.get("open_interest") or 0) / 10)
        score = min(100.0, annualized_yield * 2) * 0.45 + min(100.0, upside_cap * 8) * 0.30 + liquidity_score * 0.25

        opportunities.append(
            {
                "strategy": "Covered Call",
                "symbol": symbol,
                "source": "portfolio",
                "strike": strike_float,
                "expiration": c["expiration"],
                "dte": dte,
                "bid": bid,
                "ask": c["ask"],
                "delta": delta_float,
                "iv": c.get("iv"),
                "open_interest": int(c.get("open_interest") or 0),
                "volume": int(c.get("volume") or 0),
                "spread_pct": spread,
                "annualized_yield": annualized_yield,
                "upside_cap": upside_cap,
                "if_called_return": if_called_return,
                "contracts": covered_contracts,
                "premium": bid * 100 * covered_contracts,
                "score": score,
            }
        )

    return opportunities


def money(value: float) -> str:
    return f"${value:,.0f}"


def pct(value: float) -> str:
    return f"{value:.1f}%"


def build_management_alerts(positions: list[ShortPremiumPosition]) -> list[str]:
    alerts: list[str] = []
    for pos in positions:
        ratio = pos.current / pos.credit if pos.credit else 0
        label = "Monitor"
        if pos.current <= pos.credit * 0.50:
            label = "Take profit candidate"
        elif pos.current >= pos.credit * 2.00:
            label = "Defense/stop review"
        alerts.append(
            f"{label}: {pos.ticker} {pos.strike:g}{pos.option_type[0].upper()} "
            f"{pos.expiration} is {ratio:.1f}x credit (credit ${pos.credit:.2f}, current ${pos.current:.2f})."
        )
    return alerts


def report_lines(
    generated_at: datetime,
    portfolio_value: float,
    holdings: list[Holding],
    watchlist: list[WatchlistItem],
    short_positions: list[ShortPremiumPosition],
    vix: float,
    regime: str,
    sizing_pct: int,
    total_universe: int,
    option_symbols: list[str],
    csp_ideas: list[dict[str, Any]],
    call_ideas: list[dict[str, Any]],
    rejected: dict[str, list[str]],
    chain_errors: dict[str, str],
) -> tuple[str, str]:
    option_notional = sum(p.strike * 100 * p.contracts for p in short_positions)
    option_notional_pct = option_notional / portfolio_value if portfolio_value else 0
    risk_gate = option_notional_pct <= OPTIONS_ALLOCATION_LIMIT

    management = build_management_alerts(short_positions)
    action_line = (
        "New CSPs are eligible under the 30% options allocation gate."
        if risk_gate
        else "New CSPs should be watchlist-only until short-put notional is reduced below the 30% cap."
    )

    msg: list[str] = [
        f"Altamira Trade Ideas - {generated_at.strftime('%Y-%m-%d %H:%M UTC')}",
        f"Universe: {total_universe} repo symbols ({len(holdings)} holdings, {len(watchlist)} watchlist).",
        f"VIX: {vix:.1f} ({regime}); sizing multiplier: {sizing_pct}%.",
        f"Options notional: {money(option_notional)} ({pct(option_notional_pct * 100)} of portfolio).",
        f"Risk note: {action_line}",
        "",
    ]

    if management:
        msg.append("Position management:")
        for line in management[:3]:
            msg.append(f"- {line}")
        msg.append("")

    msg.append("Top CSP candidates:")
    if csp_ideas:
        for index, idea in enumerate(csp_ideas[:3], 1):
            eligibility = "ENTRY" if risk_gate else "WATCHLIST"
            msg.append(
                f"{index}) {idea['symbol']} {idea['strike']:g}P {idea['expiration']} "
                f"credit ${idea['bid']:.2f}, delta {idea['delta']:.2f}, DTE {idea['dte']}, "
                f"ann {idea['annualized_return']:.1f}%, {eligibility}."
            )
    else:
        msg.append("- No CSP passed the delta/DTE/liquidity/earnings screen.")

    msg.append("")
    msg.append("Top covered-call candidates:")
    if call_ideas:
        for index, idea in enumerate(call_ideas[:3], 1):
            msg.append(
                f"{index}) {idea['symbol']} {idea['strike']:g}C {idea['expiration']} "
                f"credit ${idea['bid']:.2f}, delta {idea['delta']:.2f}, DTE {idea['dte']}, "
                f"ann yield {idea['annualized_yield']:.1f}%."
            )
    else:
        msg.append("- No covered call passed the delta/DTE/liquidity/earnings screen.")

    msg.extend(
        [
            "",
            f"Options chains fetched for {len(option_symbols)} prioritized symbols.",
            "Not financial advice. Validate liquidity, earnings dates, and order prices before trading.",
        ]
    )

    md: list[str] = [
        f"# Trade Idea Generator - {generated_at.strftime('%Y-%m-%d')}",
        "",
        "> Generated from the current repository portfolio and watchlist context. Not financial advice.",
        "",
        "## Summary",
        "",
        f"- Generated at: {generated_at.isoformat()}",
        f"- Portfolio value used: {money(portfolio_value)}",
        f"- Holdings parsed: {len(holdings)}",
        f"- Watchlist names parsed: {len(watchlist)}",
        f"- Universe symbols: {total_universe}",
        f"- Option chains fetched: {len(option_symbols)} ({', '.join(option_symbols)})",
        f"- VIX regime: {vix:.2f} ({regime}), sizing multiplier {sizing_pct}%",
        f"- Current short-put notional: {money(option_notional)} ({pct(option_notional_pct * 100)} of portfolio)",
        f"- Risk gate: {action_line}",
        "",
        "## Position Management Alerts",
        "",
    ]
    md.extend(f"- {line}" for line in management)
    if not management:
        md.append("- No short-premium positions found in context/options-positions.md.")

    md.extend(["", "## Top CSP Candidates", ""])
    if csp_ideas:
        md.append("| Rank | Symbol | Source | Contract | Credit | Delta | DTE | Ann. Return | Breakeven | Contracts | Collateral | Score |")
        md.append("|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")
        for index, idea in enumerate(csp_ideas[:10], 1):
            md.append(
                f"| {index} | {idea['symbol']} | {idea['source']} | "
                f"{idea['strike']:g}P {idea['expiration']} | ${idea['bid']:.2f} | "
                f"{idea['delta']:.2f} | {idea['dte']} | {idea['annualized_return']:.1f}% | "
                f"${idea['breakeven']:.2f} | {idea['contracts']} | {money(idea['collateral'])} | {idea['score']:.1f} |"
            )
    else:
        md.append("No CSP candidates passed the scan.")

    md.extend(["", "## Top Covered-Call Candidates", ""])
    if call_ideas:
        md.append("| Rank | Symbol | Contract | Credit | Delta | DTE | Ann. Yield | Upside Cap | Contracts | Premium | Score |")
        md.append("|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")
        for index, idea in enumerate(call_ideas[:10], 1):
            md.append(
                f"| {index} | {idea['symbol']} | {idea['strike']:g}C {idea['expiration']} | "
                f"${idea['bid']:.2f} | {idea['delta']:.2f} | {idea['dte']} | "
                f"{idea['annualized_yield']:.1f}% | {idea['upside_cap']:.1f}% | "
                f"{idea['contracts']} | {money(idea['premium'])} | {idea['score']:.1f} |"
            )
    else:
        md.append("No covered-call candidates passed the scan.")

    md.extend(["", "## Screen Rejections", ""])
    if rejected:
        for symbol, reasons in sorted(rejected.items()):
            md.append(f"- {symbol}: {', '.join(reasons)}")
    else:
        md.append("- None.")

    md.extend(["", "## Chain Fetch Notes", ""])
    if chain_errors:
        for symbol, reason in sorted(chain_errors.items()):
            md.append(f"- {symbol}: {reason}")
    else:
        md.append("- No chain fetch errors.")

    md.extend(
        [
            "",
            "## Risk Reminders",
            "",
            "- Target entries remain 30-45 DTE and 0.20-0.30 delta.",
            "- Close short premium at 50% profit and review/defend at 200% of credit.",
            "- Avoid opening short premium through unplanned earnings.",
            "- Keep single positions within 5% max position sizing and total options allocation near the framework cap.",
        ]
    )

    return "\n".join(msg), "\n".join(md) + "\n"


def send_telegram(text: str, bot_token: str, chat_id: str) -> dict[str, Any]:
    url = f"{TELEGRAM_BASE}/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text[:3900],
        "disable_web_page_preview": "true",
    }
    return http_json(url, timeout=20, method="POST", payload=payload)


def generate(max_options_tickers: int) -> tuple[str, str, Path, dict[str, Any]]:
    fmp_key, massive_keys = credential_candidates()
    if not fmp_key:
        raise RuntimeError("FMP_API_KEY is not set and no existing FMP key was found in command docs.")
    if not massive_keys:
        raise RuntimeError("MASSIVE_API_KEY is not set and no existing Massive key was found in command docs.")

    generated_at = datetime.now(timezone.utc)
    portfolio_value, holdings = parse_holdings()
    watchlist = parse_watchlist()
    short_positions = parse_short_premium_positions()

    holding_map = {h.symbol: h for h in holdings}
    watchlist_map = {w.symbol: w for w in watchlist}
    symbols = sorted(set(holding_map) | set(watchlist_map))
    symbols = [s for s in symbols if s not in {"FFOLX"}]

    quotes = fetch_quotes(symbols, fmp_key)
    vix, regime, sizing_pct = fetch_vix(fmp_key)
    earnings = fetch_earnings(fmp_key, date.today(), date.today() + timedelta(days=45))

    rejected: dict[str, list[str]] = {}
    cleared: list[str] = []
    for symbol in symbols:
        quote = quotes.get(symbol)
        if not quote:
            rejected[symbol] = ["missing FMP quote"]
            continue
        passed, reasons = quality_screen(symbol, quote, earnings)
        if passed:
            cleared.append(symbol)
        else:
            rejected[symbol] = reasons

    option_symbols = sorted(
        cleared,
        key=lambda s: quote_priority(s, holding_map, watchlist_map),
        reverse=True,
    )[:max_options_tickers]

    csp_ideas: list[dict[str, Any]] = []
    call_ideas: list[dict[str, Any]] = []
    chain_errors: dict[str, str] = {}

    def process_symbol(symbol: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, str]]:
        quote = quotes[symbol]
        spot = float(quote.get("price") or 0)
        source = "portfolio" if symbol in holding_map else "watchlist"
        local_csp: list[dict[str, Any]] = []
        local_calls: list[dict[str, Any]] = []
        local_errors: dict[str, str] = {}

        puts, put_source = fetch_option_snapshot(symbol, "put", spot, massive_keys)
        if puts:
            local_csp.extend(score_csp(symbol, quote, puts, portfolio_value, sizing_pct, source))
        else:
            local_errors[f"{symbol} puts"] = put_source

        holding = holding_map.get(symbol)
        if holding and holding.qty >= 100:
            calls, call_source = fetch_option_snapshot(symbol, "call", spot, massive_keys)
            if calls:
                local_calls.extend(score_covered_calls(symbol, holding, quote, calls))
            else:
                local_errors[f"{symbol} calls"] = call_source

        return local_csp, local_calls, local_errors

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        future_map = {executor.submit(process_symbol, symbol): symbol for symbol in option_symbols}
        for future in concurrent.futures.as_completed(future_map):
            local_csp, local_calls, local_errors = future.result()
            csp_ideas.extend(local_csp)
            call_ideas.extend(local_calls)
            chain_errors.update(local_errors)

    csp_ideas.sort(key=lambda idea: idea["score"], reverse=True)
    call_ideas.sort(key=lambda idea: idea["score"], reverse=True)

    message, markdown = report_lines(
        generated_at=generated_at,
        portfolio_value=portfolio_value,
        holdings=holdings,
        watchlist=watchlist,
        short_positions=short_positions,
        vix=vix,
        regime=regime,
        sizing_pct=sizing_pct,
        total_universe=len(symbols),
        option_symbols=option_symbols,
        csp_ideas=csp_ideas,
        call_ideas=call_ideas,
        rejected=rejected,
        chain_errors=chain_errors,
    )

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUTS_DIR / f"trade-idea-generator-{date.today().isoformat()}.md"
    output_path.write_text(markdown, encoding="utf-8")

    metadata = {
        "portfolio_value": portfolio_value,
        "holdings": len(holdings),
        "watchlist": len(watchlist),
        "universe": len(symbols),
        "option_symbols": option_symbols,
        "csp_ideas": len(csp_ideas),
        "covered_call_ideas": len(call_ideas),
        "rejections": len(rejected),
        "chain_errors": len(chain_errors),
    }
    return message, markdown, output_path, metadata


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Altamira portfolio/watchlist trade ideas.")
    parser.add_argument("--send-telegram", action="store_true", help="Send the concise alert to Telegram.")
    parser.add_argument("--chat-id", default=None, help="Telegram chat ID override.")
    parser.add_argument("--max-options-tickers", type=int, default=24, help="Max prioritized symbols for option chain fetches.")
    args = parser.parse_args()

    try:
        message, _markdown, output_path, metadata = generate(args.max_options_tickers)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(message)
    print()
    print(f"Report written: {output_path.relative_to(WORKSPACE)}")
    print(f"Metadata: {json.dumps(metadata, sort_keys=True)}")

    if args.send_telegram:
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = args.chat_id or telegram_chat_id()
        if not token:
            print("ERROR: TELEGRAM_BOT_TOKEN is not set.", file=sys.stderr)
            return 1
        if not chat_id:
            print("ERROR: TELEGRAM_CHAT_ID is not set and no fallback chatId was found.", file=sys.stderr)
            return 1
        try:
            response = send_telegram(message, token, chat_id)
        except Exception as exc:
            print(f"ERROR: Telegram send failed: {exc}", file=sys.stderr)
            return 1
        if not response.get("ok"):
            print(f"ERROR: Telegram rejected message: {response}", file=sys.stderr)
            return 1
        print(f"Telegram sent: message_id={response.get('result', {}).get('message_id')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
