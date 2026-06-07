#!/usr/bin/env python3
"""Generate portfolio/watchlist trade ideas and optionally send to Telegram.

The scanner reads the repository's portfolio and watchlist context, pulls live
FMP market/options data, ranks CSP/covered-call/watchlist ideas, and writes a
markdown report under outputs/.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


WORKSPACE = Path(__file__).resolve().parent.parent
CONTEXT = WORKSPACE / "context"
OUTPUTS = WORKSPACE / "outputs"
FMP_BASE_V3 = "https://financialmodelingprep.com/api/v3"
FMP_BASE_V4 = "https://financialmodelingprep.com/api/v4"
MASSIVE_BASE = "https://api.massive.com/v3"
DEFAULT_CHAT_ID = "7830722515"  # Existing CSP Daily Scan Telegram channel/chat.


SECTORS = {
    "AAPL": "Technology",
    "ABT": "Healthcare",
    "ABBV": "Healthcare",
    "ACN": "Technology",
    "ADBE": "Technology",
    "ADSK": "Technology",
    "AMAT": "Technology",
    "AMZN": "Consumer Cyclical",
    "ANET": "Technology",
    "ASML": "Technology",
    "AVGO": "Technology",
    "CDNS": "Technology",
    "CMG": "Consumer Cyclical",
    "COST": "Consumer Defensive",
    "CRM": "Technology",
    "CRWD": "Technology",
    "FFOLX": "Fund",
    "FICO": "Technology",
    "GD": "Industrials",
    "GOOGL": "Communication Services",
    "INTU": "Technology",
    "ISRG": "Healthcare",
    "JPM": "Financial",
    "KLAC": "Technology",
    "KMI": "Energy",
    "LLY": "Healthcare",
    "LRCX": "Technology",
    "MA": "Financial",
    "MELI": "Consumer Cyclical",
    "META": "Communication Services",
    "MRVL": "Technology",
    "MSCI": "Financial",
    "MSFT": "Technology",
    "NFLX": "Communication Services",
    "NOW": "Technology",
    "NVDA": "Technology",
    "PANW": "Technology",
    "PLTR": "Technology",
    "QQQ": "Index",
    "SPGI": "Financial",
    "SPY": "Index",
    "TMO": "Healthcare",
    "TSLA": "Consumer Cyclical",
    "TSM": "Technology",
    "V": "Financial",
    "WM": "Industrials",
}


@dataclass(frozen=True)
class Holding:
    ticker: str
    quantity: float
    current_price: float
    weight_pct: float
    pnl_pct: float | None


@dataclass(frozen=True)
class WatchlistEntry:
    ticker: str
    score: float | None
    grade: str
    company: str
    status: str


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"Missing required context file: {path}") from None


def parse_money(value: str) -> float:
    cleaned = value.replace("$", "").replace(",", "").replace("%", "").strip()
    if cleaned in {"", "-", "\u2014"}:
        return 0.0
    return float(cleaned)


def parse_percent_from_cell(value: str) -> float | None:
    match = re.search(r"\(([+-]?\d+(?:\.\d+)?)%\)", value)
    if match:
        return float(match.group(1))
    match = re.search(r"([+-]?\d+(?:\.\d+)?)%", value)
    return float(match.group(1)) if match else None


def parse_portfolio() -> tuple[dict[str, Holding], float, float]:
    text = read_text(CONTEXT / "portfolio-details.md")
    portfolio_value = 100000.0
    cash_pct = 0.0

    value_match = re.search(r"\*\*Total MKT VALUE\*\*\s*\|\s*\$?([\d,]+)", text)
    if value_match:
        portfolio_value = parse_money(value_match.group(1))

    cash_match = re.search(r"\|\s*Cash %\s*\|\s*([0-9.]+)", text)
    if cash_match:
        cash_pct = float(cash_match.group(1))

    holdings: dict[str, Holding] = {}
    in_positions = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("## Current Positions"):
            in_positions = True
            continue
        if in_positions and line.startswith("## "):
            break
        if not in_positions or not line.startswith("|"):
            continue
        if "SYMBOL" in line or "---" in line or "Totals" in line:
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) < 9:
            continue
        ticker = parts[0].upper()
        if not re.fullmatch(r"[A-Z.]{1,6}", ticker):
            continue
        try:
            holdings[ticker] = Holding(
                ticker=ticker,
                quantity=parse_money(parts[1]),
                current_price=parse_money(parts[3]),
                weight_pct=parse_money(parts[8]),
                pnl_pct=parse_percent_from_cell(parts[6]),
            )
        except ValueError:
            continue
    return holdings, portfolio_value, cash_pct


def parse_watchlist() -> dict[str, WatchlistEntry]:
    text = read_text(CONTEXT / "watchlist.md")
    entries: dict[str, WatchlistEntry] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("|") or "Ticker" in line or "---" in line:
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) < 5:
            continue
        ticker = parts[0].upper()
        if not re.fullmatch(r"[A-Z.]{1,6}", ticker):
            continue
        score = None
        if parts[1] not in {"", "-", "\u2014"}:
            try:
                score = float(parts[1])
            except ValueError:
                score = None
        entries[ticker] = WatchlistEntry(
            ticker=ticker,
            score=score,
            grade=parts[2].replace("*", ""),
            company=parts[3],
            status=parts[4].replace("\u2b50", "").strip(),
        )
    return entries


def http_json(url: str, timeout: int = 25) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": "AltamiraTradeIdeaGenerator/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"HTTP {exc.code} for {url.split('?')[0]}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error for {url.split('?')[0]}: {exc.reason}") from exc
    except TimeoutError as exc:
        raise RuntimeError(f"Timeout for {url.split('?')[0]}") from exc
    return json.loads(payload)


def fmp_url(base: str, path: str, api_key: str, params: dict[str, Any] | None = None) -> str:
    params = dict(params or {})
    params["apikey"] = api_key
    return f"{base}/{path.lstrip('/')}?{urllib.parse.urlencode(params)}"


def batched(items: list[str], size: int) -> list[list[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def get_quotes(tickers: list[str], api_key: str) -> dict[str, dict[str, Any]]:
    quotes: dict[str, dict[str, Any]] = {}
    for batch in batched(tickers, 25):
        url = fmp_url(FMP_BASE_V3, f"quote/{','.join(batch)}", api_key)
        data = http_json(url)
        if isinstance(data, dict):
            data = [data]
        for row in data or []:
            symbol = str(row.get("symbol", "")).upper()
            if symbol:
                quotes[symbol] = row
    return quotes


def get_earnings_exclusions(tickers: list[str], api_key: str, start: date, days: int = 45) -> dict[str, str]:
    end = start + timedelta(days=days)
    url = fmp_url(
        FMP_BASE_V3,
        "earning_calendar",
        api_key,
        {"from": start.isoformat(), "to": end.isoformat()},
    )
    data = http_json(url)
    wanted = set(tickers)
    exclusions: dict[str, str] = {}
    for row in data if isinstance(data, list) else []:
        symbol = str(row.get("symbol", "")).upper()
        if symbol in wanted and row.get("date"):
            exclusions[symbol] = str(row["date"])
    return exclusions


def normalize_option(raw: dict[str, Any]) -> dict[str, Any]:
    details = raw.get("details") or {}
    quote = raw.get("last_quote") or {}
    greeks = raw.get("greeks") or {}
    day = raw.get("day") or {}
    return {
        "type": str(
            details.get("contract_type")
            or raw.get("type")
            or raw.get("putCall")
            or raw.get("side")
            or raw.get("contractType")
            or ""
        ).lower(),
        "strike": details.get("strike_price") or raw.get("strike") or raw.get("strikePrice"),
        "bid": quote.get("bid") or raw.get("bid") or raw.get("bidPrice") or 0,
        "ask": quote.get("ask") or raw.get("ask") or raw.get("askPrice") or 0,
        "delta": greeks.get("delta") or raw.get("delta"),
        "iv": raw.get("implied_volatility") or raw.get("impliedVolatility") or raw.get("iv"),
        "open_interest": raw.get("open_interest") or raw.get("openInterest") or 0,
        "volume": day.get("volume") or raw.get("volume") or raw.get("totalVolume") or 0,
        "expiration": details.get("expiration_date") or raw.get("expiration") or raw.get("expirationDate") or raw.get("expiry"),
    }


def flatten_options(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("options", "data", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    rows: list[dict[str, Any]] = []
    for value in payload.values():
        if isinstance(value, list):
            rows.extend(item for item in value if isinstance(item, dict))
    return rows


def get_massive_options_chain(
    ticker: str,
    massive_key: str,
    today: date,
    price: float,
) -> list[dict[str, Any]]:
    if not massive_key:
        return []
    start = today + timedelta(days=20)
    end = today + timedelta(days=60)
    strike_min = max(1, math.floor(price * 0.80))
    strike_max = math.ceil(price * 1.20)
    rows: list[dict[str, Any]] = []
    for contract_type in ("put", "call"):
        params = {
            "apiKey": massive_key,
            "contract_type": contract_type,
            "expiration_date.gte": start.isoformat(),
            "expiration_date.lte": end.isoformat(),
            "strike_price.gte": strike_min,
            "strike_price.lte": strike_max,
            "limit": 250,
        }
        url = f"{MASSIVE_BASE}/snapshot/options/{ticker}?{urllib.parse.urlencode(params)}"
        try:
            payload = http_json(url, timeout=30)
        except RuntimeError as exc:
            print(f"Warning: Massive options unavailable for {ticker} {contract_type}: {exc}", file=sys.stderr)
            continue
        rows.extend(normalize_option(row) for row in flatten_options(payload))
    return rows


def get_options_chain(
    ticker: str,
    api_key: str,
    today: date,
    price: float,
    massive_key: str | None = None,
) -> list[dict[str, Any]]:
    massive_rows = get_massive_options_chain(ticker, massive_key or "", today, price)
    if massive_rows:
        return massive_rows
    url = fmp_url(FMP_BASE_V4, f"options-chain/{ticker}", api_key)
    try:
        return [normalize_option(row) for row in flatten_options(http_json(url, timeout=30))]
    except RuntimeError as exc:
        print(f"Warning: options chain unavailable for {ticker}: {exc}", file=sys.stderr)
        return []


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def dte(expiration: str | None, today: date) -> int | None:
    if not expiration:
        return None
    try:
        exp = datetime.fromisoformat(str(expiration)[:10]).date()
    except ValueError:
        return None
    return (exp - today).days


def estimate_put_delta(price: float, strike: float) -> float:
    if price <= 0:
        return 0.0
    moneyness = strike / price
    if moneyness >= 0.98:
        return -0.35
    if moneyness >= 0.95:
        return -0.27
    if moneyness >= 0.92:
        return -0.20
    return -0.12


def estimate_call_delta(price: float, strike: float) -> float:
    if price <= 0:
        return 0.0
    moneyness = strike / price
    if moneyness <= 1.02:
        return 0.35
    if moneyness <= 1.06:
        return 0.27
    if moneyness <= 1.10:
        return 0.20
    return 0.12


def vix_regime(vix: float) -> tuple[str, int, str]:
    if vix < 15:
        return "LOW", 75, "Premium is lean; be selective and avoid chasing low credits."
    if vix <= 25:
        return "NORMAL", 100, "Standard CSP/spread sizing is acceptable after risk checks."
    if vix <= 35:
        return "ELEVATED", 50, "Prefer defined-risk spreads and reduced size."
    return "CRISIS", 25, "Use spreads only or stand aside."


def score_quote(ticker: str, quote: dict[str, Any], watchlist: dict[str, WatchlistEntry], holding: Holding | None) -> float:
    price = safe_float(quote.get("price"))
    sma50 = safe_float(quote.get("priceAvg50"))
    year_high = safe_float(quote.get("yearHigh"))
    change_pct = safe_float(quote.get("changesPercentage"))
    score = 0.0
    if holding:
        score += 10
    if ticker in watchlist and watchlist[ticker].score is not None:
        score += min(25, watchlist[ticker].score or 0) / 25 * 20
    if price and sma50 and price >= sma50:
        score += 20
    if year_high and price:
        score += max(0, min(20, (price / year_high) * 20))
    if -2 <= change_pct <= 3:
        score += 10
    if change_pct < -2:
        score += 5
    return score


def candidate_universe(
    holdings: dict[str, Holding],
    watchlist: dict[str, WatchlistEntry],
    quotes: dict[str, dict[str, Any]],
    earnings: dict[str, str],
    limit: int,
) -> list[str]:
    scored: list[tuple[float, str]] = []
    for ticker, quote in quotes.items():
        if ticker in {"FFOLX"} or SECTORS.get(ticker) == "Fund":
            continue
        if ticker in earnings:
            continue
        holding = holdings.get(ticker)
        watch_entry = watchlist.get(ticker)
        if not holding and watch_entry:
            status = watch_entry.status.lower()
            if watch_entry.score is None or watch_entry.score < 55 or "low priority" in status or "avoid" in status:
                continue
        elif not holding:
            continue
        volume = safe_float(quote.get("volume"))
        price = safe_float(quote.get("price"))
        sma50 = safe_float(quote.get("priceAvg50"))
        if volume < 100000 or price <= 0:
            continue
        if sma50 and price < sma50:
            continue
        scored.append((score_quote(ticker, quote, watchlist, holding), ticker))
    scored.sort(reverse=True)
    return [ticker for _, ticker in scored[:limit]]


def find_csp_ideas(
    tickers: list[str],
    quotes: dict[str, dict[str, Any]],
    api_key: str,
    massive_key: str | None,
    today: date,
    portfolio_value: float,
    sizing_pct: int,
) -> tuple[list[dict[str, Any]], int]:
    ideas: list[dict[str, Any]] = []
    scanned = 0
    max_allocation = portfolio_value * 0.05 * (sizing_pct / 100)
    for ticker in tickers:
        price = safe_float(quotes.get(ticker, {}).get("price"))
        year_high = safe_float(quotes.get(ticker, {}).get("yearHigh"))
        for option in get_options_chain(ticker, api_key, today, price, massive_key):
            if option["type"] and "put" not in option["type"]:
                continue
            strike = safe_float(option["strike"])
            bid = safe_float(option["bid"])
            ask = safe_float(option["ask"])
            oi = safe_float(option["open_interest"])
            volume = safe_float(option["volume"])
            days = dte(option["expiration"], today)
            if not days or days < 20 or days > 60 or strike <= 0 or price <= 0:
                continue
            if strike > price * 0.98 or strike < price * 0.82 or bid <= 0 or oi < 10:
                continue
            delta = safe_float(option["delta"], estimate_put_delta(price, strike))
            abs_delta = abs(delta)
            if abs_delta < 0.12 or abs_delta > 0.35:
                continue
            scanned += 1
            collateral = strike * 100
            max_contracts = math.floor(max_allocation / collateral)
            if max_contracts < 1:
                continue
            annualized = (bid / strike) * (365 / days) * 100
            spread_pct = ((ask - bid) / ((ask + bid) / 2) * 100) if ask and bid else 99
            liquidity = min(30, oi / 100) + min(20, volume / 20) + max(0, 20 - min(20, spread_pct))
            trend = (price / year_high * 20) if year_high else 12
            delta_score = max(0, 15 - abs(abs_delta - 0.24) * 100)
            score = annualized * 0.9 + liquidity * 0.7 + trend + delta_score
            ideas.append(
                {
                    "strategy": "Cash-secured put",
                    "ticker": ticker,
                    "price": price,
                    "strike": strike,
                    "expiration": option["expiration"],
                    "dte": days,
                    "credit": bid,
                    "ask": ask,
                    "delta": delta,
                    "annualized_return": annualized,
                    "breakeven": strike - bid,
                    "contracts": max_contracts,
                    "collateral": collateral * max_contracts,
                    "premium": bid * 100 * max_contracts,
                    "score": score,
                    "liquidity_note": f"OI {int(oi)}, volume {int(volume)}, spread {spread_pct:.1f}%",
                    "management": f"Close at {bid * 0.5:.2f}; stop/adjust near {bid * 2:.2f}.",
                    "sector": SECTORS.get(ticker, "Unknown"),
                }
            )
    ideas.sort(key=lambda row: row["score"], reverse=True)
    return ideas[:5], scanned


def find_covered_call_ideas(
    holdings: dict[str, Holding],
    quotes: dict[str, dict[str, Any]],
    api_key: str,
    massive_key: str | None,
    today: date,
) -> tuple[list[dict[str, Any]], int]:
    ideas: list[dict[str, Any]] = []
    scanned = 0
    eligible = [h for h in holdings.values() if h.quantity >= 100 and h.ticker not in {"SPY", "QQQ", "FFOLX"}]
    eligible.sort(key=lambda h: h.weight_pct, reverse=True)
    for holding in eligible[:8]:
        ticker = holding.ticker
        price = safe_float(quotes.get(ticker, {}).get("price"), holding.current_price)
        for option in get_options_chain(ticker, api_key, today, price, massive_key):
            if option["type"] and "call" not in option["type"]:
                continue
            strike = safe_float(option["strike"])
            bid = safe_float(option["bid"])
            ask = safe_float(option["ask"])
            oi = safe_float(option["open_interest"])
            volume = safe_float(option["volume"])
            days = dte(option["expiration"], today)
            if not days or days < 20 or days > 60 or strike <= 0 or price <= 0:
                continue
            if strike < price * 1.02 or strike > price * 1.18 or bid <= 0 or oi < 10:
                continue
            delta = safe_float(option["delta"], estimate_call_delta(price, strike))
            if abs(delta) < 0.12 or abs(delta) > 0.35:
                continue
            scanned += 1
            contracts = int(holding.quantity // 100)
            annualized = (bid / price) * (365 / days) * 100
            upside = (strike / price - 1) * 100
            spread_pct = ((ask - bid) / ((ask + bid) / 2) * 100) if ask and bid else 99
            score = annualized * 1.2 + min(30, oi / 100) + min(15, upside) + max(0, 15 - min(15, spread_pct))
            ideas.append(
                {
                    "strategy": "Covered call",
                    "ticker": ticker,
                    "price": price,
                    "strike": strike,
                    "expiration": option["expiration"],
                    "dte": days,
                    "credit": bid,
                    "ask": ask,
                    "delta": delta,
                    "annualized_return": annualized,
                    "upside_cap_pct": upside,
                    "contracts": contracts,
                    "premium": bid * 100 * contracts,
                    "score": score,
                    "liquidity_note": f"OI {int(oi)}, volume {int(volume)}, spread {spread_pct:.1f}%",
                    "management": f"Close at {bid * 0.5:.2f}; roll if short strike is challenged.",
                    "sector": SECTORS.get(ticker, "Unknown"),
                }
            )
    ideas.sort(key=lambda row: row["score"], reverse=True)
    return ideas[:5], scanned


def watchlist_entry_ideas(
    watchlist: dict[str, WatchlistEntry],
    holdings: dict[str, Holding],
    quotes: dict[str, dict[str, Any]],
    earnings: dict[str, str],
) -> list[dict[str, Any]]:
    ideas: list[dict[str, Any]] = []
    for ticker, entry in watchlist.items():
        if ticker in holdings or ticker in earnings:
            continue
        quote = quotes.get(ticker, {})
        price = safe_float(quote.get("price"))
        sma50 = safe_float(quote.get("priceAvg50"))
        year_high = safe_float(quote.get("yearHigh"))
        change = safe_float(quote.get("changesPercentage"))
        if not price or not entry.score:
            continue
        trend_ok = price >= sma50 if sma50 else True
        pullback = (1 - price / year_high) * 100 if year_high else 0
        if entry.score < 55 or not trend_ok:
            continue
        score = entry.score + min(10, pullback / 2) - max(0, change - 3)
        ideas.append(
            {
                "strategy": "Watchlist entry review",
                "ticker": ticker,
                "company": entry.company,
                "grade": entry.grade,
                "status": entry.status,
                "price": price,
                "sma50": sma50,
                "year_high": year_high,
                "pullback_pct": pullback,
                "score": score,
                "rationale": "High watchlist score with price holding above 50-day average.",
            }
        )
    ideas.sort(key=lambda row: row["score"], reverse=True)
    return ideas[:5]


def fmt_money(value: float) -> str:
    return f"${value:,.2f}"


def fmt_pct(value: float) -> str:
    return f"{value:.1f}%"


def build_telegram_text(
    report_date: date,
    holdings: dict[str, Holding],
    watchlist: dict[str, WatchlistEntry],
    vix: float,
    regime: str,
    sizing_pct: int,
    csp: list[dict[str, Any]],
    covered_calls: list[dict[str, Any]],
    watch_entries: list[dict[str, Any]],
    earnings: dict[str, str],
    scanned_contracts: int,
) -> str:
    lines = [
        f"TRADE IDEA GENERATOR - {report_date.isoformat()}",
        f"Universe: {len(holdings)} portfolio holdings + {len(watchlist)} watchlist names",
        f"VIX: {vix:.1f} ({regime}) | Sizing: {sizing_pct}%",
        f"Contracts screened: {scanned_contracts}",
        "",
    ]

    if csp:
        lines.append("Top CSP ideas:")
        for idx, idea in enumerate(csp[:3], start=1):
            lines.append(
                f"{idx}. {idea['ticker']} {idea['strike']:.0f}P {idea['expiration']} "
                f"credit {fmt_money(idea['credit'])}, delta {idea['delta']:.2f}, DTE {idea['dte']}, "
                f"ann {fmt_pct(idea['annualized_return'])}, BE {fmt_money(idea['breakeven'])}"
            )
            lines.append(
                f"   Contracts {idea['contracts']}, collateral {fmt_money(idea['collateral'])}, "
                f"premium {fmt_money(idea['premium'])}; {idea['management']}"
            )
    else:
        lines.append("Top CSP ideas: none passed liquidity/DTE/delta filters.")
    lines.append("")

    if covered_calls:
        lines.append("Covered-call ideas on current holdings:")
        for idx, idea in enumerate(covered_calls[:3], start=1):
            lines.append(
                f"{idx}. {idea['ticker']} {idea['strike']:.0f}C {idea['expiration']} "
                f"credit {fmt_money(idea['credit'])}, delta {idea['delta']:.2f}, DTE {idea['dte']}, "
                f"upside cap {fmt_pct(idea['upside_cap_pct'])}"
            )
            lines.append(f"   Contracts {idea['contracts']}, premium {fmt_money(idea['premium'])}; {idea['management']}")
    else:
        lines.append("Covered-call ideas: none passed filters.")
    lines.append("")

    if watch_entries:
        lines.append("Watchlist entry reviews:")
        for idx, idea in enumerate(watch_entries[:3], start=1):
            lines.append(
                f"{idx}. {idea['ticker']} ({idea['grade']}, {idea['status']}): "
                f"price {fmt_money(idea['price'])}, pullback {fmt_pct(idea['pullback_pct'])} from high."
            )
    else:
        lines.append("Watchlist entry reviews: none passed trend/score filters.")

    if earnings:
        excluded = ", ".join(f"{ticker} {when}" for ticker, when in sorted(earnings.items())[:12])
        lines.extend(["", f"Earnings excluded within 45 days: {excluded}"])

    lines.extend(
        [
            "",
            "Risk note: scan output only, not trade orders. Confirm portfolio exposure, liquidity, earnings, and stops before entry.",
            "Financial disclaimer: for informational purposes only; not investment advice.",
        ]
    )
    return "\n".join(lines)[:3900]


def build_markdown_report(
    report_date: date,
    portfolio_value: float,
    cash_pct: float,
    holdings: dict[str, Holding],
    watchlist: dict[str, WatchlistEntry],
    vix: float,
    regime: str,
    sizing_pct: int,
    regime_note: str,
    candidates: list[str],
    csp: list[dict[str, Any]],
    covered_calls: list[dict[str, Any]],
    watch_entries: list[dict[str, Any]],
    earnings: dict[str, str],
    scanned_contracts: int,
    telegram_result: dict[str, Any] | None,
) -> str:
    lines = [
        f"# Trade Idea Generator - {report_date.isoformat()}",
        "",
        "Generated from `context/portfolio-details.md` and `context/watchlist.md`.",
        "",
        "## Summary",
        "",
        f"- Portfolio value: {fmt_money(portfolio_value)}",
        f"- Cash: {cash_pct:.1f}%",
        f"- Universe: {len(holdings)} portfolio holdings + {len(watchlist)} watchlist names",
        f"- VIX regime: {vix:.2f} ({regime}); sizing adjustment {sizing_pct}%",
        f"- Regime note: {regime_note}",
        f"- Option contracts screened: {scanned_contracts}",
        f"- Candidate option tickers screened: {', '.join(candidates) if candidates else 'None'}",
        "",
        "## Top Cash-Secured Put Ideas",
        "",
    ]
    if csp:
        lines.append("| Rank | Ticker | Contract | Credit | Delta | DTE | Annualized | Breakeven | Contracts | Collateral | Liquidity |")
        lines.append("|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|")
        for idx, idea in enumerate(csp, start=1):
            lines.append(
                f"| {idx} | {idea['ticker']} | {idea['strike']:.0f}P {idea['expiration']} | "
                f"{fmt_money(idea['credit'])} | {idea['delta']:.2f} | {idea['dte']} | "
                f"{fmt_pct(idea['annualized_return'])} | {fmt_money(idea['breakeven'])} | "
                f"{idea['contracts']} | {fmt_money(idea['collateral'])} | {idea['liquidity_note']} |"
            )
    else:
        lines.append("No CSP contracts passed the liquidity, DTE, delta, and sizing filters.")

    lines.extend(["", "## Covered-Call Ideas On Current Holdings", ""])
    if covered_calls:
        lines.append("| Rank | Ticker | Contract | Credit | Delta | DTE | Annualized | Upside Cap | Contracts | Premium | Liquidity |")
        lines.append("|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|")
        for idx, idea in enumerate(covered_calls, start=1):
            lines.append(
                f"| {idx} | {idea['ticker']} | {idea['strike']:.0f}C {idea['expiration']} | "
                f"{fmt_money(idea['credit'])} | {idea['delta']:.2f} | {idea['dte']} | "
                f"{fmt_pct(idea['annualized_return'])} | {fmt_pct(idea['upside_cap_pct'])} | "
                f"{idea['contracts']} | {fmt_money(idea['premium'])} | {idea['liquidity_note']} |"
            )
    else:
        lines.append("No covered-call contracts passed the liquidity, DTE, delta, and upside filters.")

    lines.extend(["", "## Watchlist Entry Reviews", ""])
    if watch_entries:
        lines.append("| Rank | Ticker | Grade | Status | Price | 50D Avg | Pullback From High | Rationale |")
        lines.append("|---:|---|---|---|---:|---:|---:|---|")
        for idx, idea in enumerate(watch_entries, start=1):
            lines.append(
                f"| {idx} | {idea['ticker']} | {idea['grade']} | {idea['status']} | "
                f"{fmt_money(idea['price'])} | {fmt_money(idea['sma50'])} | "
                f"{fmt_pct(idea['pullback_pct'])} | {idea['rationale']} |"
            )
    else:
        lines.append("No non-held watchlist entries passed score and trend filters.")

    lines.extend(["", "## Earnings Exclusions", ""])
    if earnings:
        lines.append("| Ticker | Earnings Date |")
        lines.append("|---|---|")
        for ticker, when in sorted(earnings.items()):
            lines.append(f"| {ticker} | {when} |")
    else:
        lines.append("No universe tickers had earnings inside the next 45 days.")

    lines.extend(["", "## Delivery", ""])
    if telegram_result:
        lines.append(f"- Telegram sent: {telegram_result.get('ok')}")
        result = telegram_result.get("result") or {}
        if result:
            lines.append(f"- Telegram message id: {result.get('message_id')}")
            chat = result.get("chat") or {}
            lines.append(f"- Telegram chat id: {chat.get('id')}")
    else:
        lines.append("- Telegram sent: false (dry run)")

    lines.extend(
        [
            "",
            "## Disclaimer",
            "",
            "This scan is for informational purposes only and is not investment advice or an order recommendation. "
            "Verify live option chains, liquidity, earnings dates, position sizing, and portfolio risk limits before taking action.",
            "",
        ]
    )
    return "\n".join(lines)


def send_telegram(token: str, chat_id: str, text: str) -> dict[str, Any]:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def positive_tickers(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [part.strip().upper() for part in raw.split(",") if part.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fmp-api-key", default=os.environ.get("FMP_API_KEY"), help="FMP API key")
    parser.add_argument("--massive-api-key", default=os.environ.get("MASSIVE_API_KEY"), help="Massive.com API key")
    parser.add_argument("--telegram-token", default=os.environ.get("TELEGRAM_BOT_TOKEN"), help="Telegram bot token")
    parser.add_argument(
        "--telegram-chat-id",
        default=os.environ.get("TELEGRAM_CHAT_ID") or DEFAULT_CHAT_ID,
        help="Telegram chat/channel id",
    )
    parser.add_argument("--send-telegram", action="store_true", help="Send the generated summary to Telegram")
    parser.add_argument("--max-option-tickers", type=int, default=14, help="Max tickers to fetch option chains for")
    parser.add_argument("--extra-tickers", default="", help="Comma-separated extra tickers to include")
    parser.add_argument("--date", default=date.today().isoformat(), help="Report date (YYYY-MM-DD)")
    args = parser.parse_args()

    if not args.fmp_api_key:
        raise SystemExit("Set FMP_API_KEY or pass --fmp-api-key.")

    report_date = datetime.fromisoformat(args.date).date()
    holdings, portfolio_value, cash_pct = parse_portfolio()
    watchlist = parse_watchlist()
    universe = sorted(set(holdings) | set(watchlist) | set(positive_tickers(args.extra_tickers)) | {"SPY", "^VIX"})
    quotes = get_quotes(universe, args.fmp_api_key)

    vix = safe_float(quotes.get("^VIX", {}).get("price"), 20.0)
    regime, sizing_pct, regime_note = vix_regime(vix)
    earnings = get_earnings_exclusions([ticker for ticker in universe if ticker != "^VIX"], args.fmp_api_key, report_date)
    candidates = candidate_universe(holdings, watchlist, quotes, earnings, args.max_option_tickers)
    csp, csp_scanned = find_csp_ideas(
        candidates,
        quotes,
        args.fmp_api_key,
        args.massive_api_key,
        report_date,
        portfolio_value,
        sizing_pct,
    )
    covered_calls, cc_scanned = find_covered_call_ideas(holdings, quotes, args.fmp_api_key, args.massive_api_key, report_date)
    watch_entries = watchlist_entry_ideas(watchlist, holdings, quotes, earnings)

    telegram_text = build_telegram_text(
        report_date,
        holdings,
        watchlist,
        vix,
        regime,
        sizing_pct,
        csp,
        covered_calls,
        watch_entries,
        earnings,
        csp_scanned + cc_scanned,
    )

    telegram_result = None
    if args.send_telegram:
        if not args.telegram_token:
            raise SystemExit("Set TELEGRAM_BOT_TOKEN or pass --telegram-token to send Telegram.")
        telegram_result = send_telegram(args.telegram_token, args.telegram_chat_id, telegram_text)

    report = build_markdown_report(
        report_date,
        portfolio_value,
        cash_pct,
        holdings,
        watchlist,
        vix,
        regime,
        sizing_pct,
        regime_note,
        candidates,
        csp,
        covered_calls,
        watch_entries,
        earnings,
        csp_scanned + cc_scanned,
        telegram_result,
    )

    OUTPUTS.mkdir(exist_ok=True)
    output_path = OUTPUTS / f"trade-idea-generator-{report_date.isoformat()}.md"
    output_path.write_text(report, encoding="utf-8")

    print(telegram_text)
    print()
    print(f"Report written: {output_path.relative_to(WORKSPACE)}")
    if telegram_result:
        result = telegram_result.get("result") or {}
        print(f"Telegram delivered: ok={telegram_result.get('ok')} message_id={result.get('message_id')}")
    else:
        print("Telegram delivered: false (dry run)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
