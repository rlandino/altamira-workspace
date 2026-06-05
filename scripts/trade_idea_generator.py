#!/usr/bin/env python3
"""
Altamira Capital trade idea generator.

Reads the existing portfolio and watchlist context, fetches current market and
options data when credentials are available, writes a markdown report, and can
send the top ideas to Telegram.

Usage:
    python scripts/trade_idea_generator.py --send-telegram
    python scripts/trade_idea_generator.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable


WORKSPACE = Path(__file__).resolve().parent.parent
CONTEXT = WORKSPACE / "context"
OUTPUTS = WORKSPACE / "outputs"
FMP_BASE = "https://financialmodelingprep.com/api/v3"
FMP_V4_BASE = "https://financialmodelingprep.com/api/v4"
MASSIVE_BASE = "https://api.massive.com/v3"
TELEGRAM_BASE = "https://api.telegram.org"


@dataclass
class Position:
    symbol: str
    quantity: float
    avg_price: float
    current_price: float
    market_value: float
    weight: float
    pnl_pct: float | None = None


@dataclass
class WatchlistEntry:
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
    expiration: str
    credit: float
    current: float
    contracts: int


@dataclass
class Quote:
    ticker: str
    price: float | None = None
    change_pct: float | None = None
    volume: int | None = None
    market_cap: float | None = None
    name: str | None = None


@dataclass
class Technicals:
    sma20: float | None = None
    sma50: float | None = None
    rsi14: float | None = None
    realized_vol_30d: float | None = None


@dataclass
class OptionContract:
    ticker: str
    option_type: str
    strike: float
    expiration: str
    dte: int
    bid: float
    ask: float
    mid: float
    delta: float | None
    iv: float | None
    open_interest: int
    volume: int
    source: str


@dataclass
class TradeIdea:
    rank_score: float
    ticker: str
    strategy: str
    action: str
    rationale: str
    strike: float | None = None
    expiration: str | None = None
    premium: float | None = None
    delta: float | None = None
    dte: int | None = None
    annualized_return: float | None = None
    max_contracts: int | None = None
    collateral: float | None = None
    breakeven: float | None = None
    risk_flags: list[str] = field(default_factory=list)
    source: str = "derived"


def clean_number(value: str) -> float:
    value = value.strip()
    value = value.replace("$", "").replace(",", "").replace("%", "")
    value = value.replace("+", "")
    if value in {"", "-", "—", "N/A"}:
        return 0.0
    return float(value)


def parse_pct_from_field(value: str) -> float | None:
    match = re.search(r"([+-]?\d+(?:\.\d+)?)%", value)
    return float(match.group(1)) if match else None


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_portfolio(path: Path) -> list[Position]:
    positions: list[Position] = []
    in_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| SYMBOL |"):
            in_table = True
            continue
        if not in_table:
            continue
        if line.startswith("|--------") or not line.startswith("|"):
            continue
        if line.startswith("| Ticker |") or line.startswith("**Totals:**"):
            break
        cells = split_table_row(line)
        if len(cells) < 9:
            continue
        symbol = cells[0].strip()
        if symbol.upper() == "SYMBOL":
            continue
        try:
            positions.append(
                Position(
                    symbol=symbol,
                    quantity=clean_number(cells[1]),
                    avg_price=clean_number(cells[2]),
                    current_price=clean_number(cells[3]),
                    market_value=clean_number(cells[4]),
                    weight=clean_number(cells[8]),
                    pnl_pct=parse_pct_from_field(cells[6]),
                )
            )
        except ValueError:
            continue
    return positions


def parse_watchlist(path: Path) -> list[WatchlistEntry]:
    entries: list[WatchlistEntry] = []
    in_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| Ticker | Score |"):
            in_table = True
            continue
        if not in_table:
            continue
        if line.startswith("|--------"):
            continue
        if not line.startswith("|"):
            break
        cells = split_table_row(line)
        if len(cells) < 5:
            continue
        score = None
        try:
            score = clean_number(cells[1])
        except ValueError:
            pass
        entries.append(
            WatchlistEntry(
                ticker=cells[0],
                score=score,
                grade=cells[2].replace("**", ""),
                company=cells[3],
                status=cells[4],
            )
        )
    return entries


def parse_option_positions(path: Path) -> list[OptionPosition]:
    positions: list[OptionPosition] = []
    in_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| Ticker | Strike |"):
            in_table = True
            continue
        if not in_table:
            continue
        if line.startswith("|--------"):
            continue
        if not line.startswith("|"):
            break
        cells = split_table_row(line)
        if len(cells) < 7:
            continue
        try:
            positions.append(
                OptionPosition(
                    ticker=cells[0],
                    strike=clean_number(cells[1]),
                    option_type=cells[2],
                    expiration=cells[3],
                    credit=clean_number(cells[4]),
                    current=clean_number(cells[5]),
                    contracts=int(clean_number(cells[6])),
                )
            )
        except ValueError:
            continue
    return positions


def discover_key(patterns: list[tuple[Path, str]]) -> tuple[str | None, str | None]:
    for path, pattern in patterns:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        match = re.search(pattern, text)
        if match:
            return match.group(1), f"repo default: {path.relative_to(WORKSPACE)}"
    return None, None


def get_fmp_key() -> tuple[str | None, str]:
    env_key = os.environ.get("FMP_API_KEY") or os.environ.get("FINANCIAL_MODELING_PREP_API_KEY")
    if env_key:
        return env_key, "FMP_API_KEY environment variable"
    key, source = discover_key(
        [
            (
                WORKSPACE / "scripts" / "thesis-generator.py",
                r'os\.environ\.get\("FMP_API_KEY",\s*"([^"]+)"\)',
            ),
            (
                WORKSPACE / "outputs" / "csp-daily-scan-fixed.json",
                r"FMP_API_KEY\s*=\s*'([^']+)'",
            ),
            (
                WORKSPACE / "outputs" / "n8n-workflow-csp-daily-scan.json",
                r"FMP_API_KEY\s*=\s*'([^']+)'",
            ),
        ]
    )
    return key, source or "not configured"


def get_massive_key() -> tuple[str | None, str]:
    env_key = os.environ.get("MASSIVE_API_KEY") or os.environ.get("POLYGON_API_KEY")
    if env_key:
        return env_key, "MASSIVE_API_KEY environment variable"
    key, source = discover_key(
        [
            (
                WORKSPACE / "outputs" / "n8n-workflow-csp-daily-scan.json",
                r"MASSIVE_API_KEY\s*=\s*'([^']+)'",
            ),
            (
                WORKSPACE / "outputs" / "csp-daily-scan-fixed.json",
                r"MASSIVE_API_KEY\s*=\s*'([^']+)'",
            ),
            (
                WORKSPACE / "scripts" / "stock-scorer.py",
                r'MASSIVE_API_KEY\s*=\s*"([^"]+)"',
            ),
        ]
    )
    return key, source or "not configured"


def get_telegram_chat_id() -> tuple[str | None, str]:
    env_chat = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("ALTAMIRA_TELEGRAM_CHAT_ID")
    if env_chat:
        return env_chat, "TELEGRAM_CHAT_ID environment variable"
    fixed = WORKSPACE / "outputs" / "csp-daily-scan-fixed.json"
    if fixed.exists():
        text = fixed.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r'"chatId"\s*:\s*"=?([^"]+)"', text)
        if match:
            return match.group(1), f"repo default: {fixed.relative_to(WORKSPACE)}"
    return None, "not configured"


def request_json(url: str, timeout: int = 20, retries: int = 2) -> Any:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AltamiraTradeIdeaGenerator/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                payload = response.read().decode("utf-8")
            return json.loads(payload)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Request failed for {url.split('?')[0]}: {last_error}")


def post_json(url: str, payload: dict[str, Any], timeout: int = 20) -> Any:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "AltamiraTradeIdeaGenerator/1.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        text = response.read().decode("utf-8")
    return json.loads(text)


def fmp_url(path: str, api_key: str, params: dict[str, Any] | None = None, base: str = FMP_BASE) -> str:
    params = dict(params or {})
    params["apikey"] = api_key
    return f"{base}/{path.lstrip('/')}?{urllib.parse.urlencode(params)}"


def fetch_quotes(tickers: Iterable[str], fmp_key: str | None) -> dict[str, Quote]:
    quotes: dict[str, Quote] = {}
    if not fmp_key:
        return quotes
    tickers_list = sorted({t.upper() for t in tickers if t})
    for idx in range(0, len(tickers_list), 50):
        batch = tickers_list[idx : idx + 50]
        try:
            data = request_json(fmp_url(f"quote/{','.join(batch)}", fmp_key))
        except RuntimeError as exc:
            print(f"Quote fetch warning: {exc}", file=sys.stderr)
            continue
        if isinstance(data, dict):
            data = [data]
        for item in data or []:
            symbol = (item.get("symbol") or "").upper()
            if not symbol:
                continue
            quotes[symbol] = Quote(
                ticker=symbol,
                price=to_float(item.get("price")),
                change_pct=to_float(item.get("changesPercentage")),
                volume=to_int(item.get("volume")),
                market_cap=to_float(item.get("marketCap")),
                name=item.get("name"),
            )
    return quotes


def fetch_historical(ticker: str, fmp_key: str | None) -> list[dict[str, Any]]:
    if not fmp_key:
        return []
    try:
        data = request_json(fmp_url(f"historical-price-full/{ticker}", fmp_key, {"timeseries": 70}))
    except RuntimeError:
        return []
    rows = data.get("historical", []) if isinstance(data, dict) else []
    rows.sort(key=lambda row: row.get("date", ""))
    return rows


def fetch_earnings(tickers: set[str], fmp_key: str | None, start: date, end: date) -> dict[str, str]:
    if not fmp_key:
        return {}
    try:
        data = request_json(
            fmp_url(
                "earning_calendar",
                fmp_key,
                {"from": start.isoformat(), "to": end.isoformat()},
            )
        )
    except RuntimeError:
        return {}
    earnings: dict[str, str] = {}
    for row in data or []:
        symbol = (row.get("symbol") or "").upper()
        if symbol in tickers:
            earnings[symbol] = row.get("date", "")
    return earnings


def fetch_vix(fmp_key: str | None) -> tuple[float | None, str]:
    if not fmp_key:
        return None, "UNKNOWN"
    quotes = fetch_quotes(["^VIX"], fmp_key)
    vix = quotes.get("^VIX", Quote("^VIX")).price
    if vix is None:
        return None, "UNKNOWN"
    if vix < 15:
        return vix, "LOW"
    if vix < 25:
        return vix, "NORMAL"
    if vix < 35:
        return vix, "ELEVATED"
    return vix, "CRISIS"


def to_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def to_int(value: Any) -> int | None:
    try:
        if value is None or value == "":
            return None
        return int(float(value))
    except (TypeError, ValueError):
        return None


def calculate_technicals(rows: list[dict[str, Any]]) -> Technicals:
    closes = [to_float(row.get("close")) for row in rows]
    closes = [c for c in closes if c is not None]
    if not closes:
        return Technicals()
    returns = [(closes[i] / closes[i - 1]) - 1 for i in range(1, len(closes)) if closes[i - 1]]
    realized = None
    if len(returns) >= 20:
        recent = returns[-30:]
        mean = sum(recent) / len(recent)
        variance = sum((r - mean) ** 2 for r in recent) / max(len(recent) - 1, 1)
        realized = math.sqrt(variance) * math.sqrt(252)
    return Technicals(
        sma20=sum(closes[-20:]) / 20 if len(closes) >= 20 else None,
        sma50=sum(closes[-50:]) / 50 if len(closes) >= 50 else None,
        rsi14=calculate_rsi(closes[-15:]) if len(closes) >= 15 else None,
        realized_vol_30d=realized,
    )


def calculate_rsi(closes: list[float]) -> float | None:
    if len(closes) < 15:
        return None
    gains = []
    losses = []
    for idx in range(1, len(closes)):
        change = closes[idx] - closes[idx - 1]
        gains.append(max(change, 0))
        losses.append(abs(min(change, 0)))
    avg_gain = sum(gains[-14:]) / 14
    avg_loss = sum(losses[-14:]) / 14
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def third_friday(year: int, month: int) -> date:
    current = date(year, month, 1)
    fridays = []
    while current.month == month:
        if current.weekday() == 4:
            fridays.append(current)
        current += timedelta(days=1)
    return fridays[2]


def target_expiration(today: date) -> date:
    for month_offset in range(0, 4):
        month = today.month + month_offset
        year = today.year + ((month - 1) // 12)
        month = ((month - 1) % 12) + 1
        exp = third_friday(year, month)
        if 30 <= (exp - today).days <= 55:
            return exp
    return today + timedelta(days=42)


def fetch_massive_options(
    ticker: str,
    contract_type: str,
    massive_key: str | None,
    start: date,
    end: date,
) -> list[OptionContract]:
    if not massive_key:
        return []
    params = {
        "apiKey": massive_key,
        "contract_type": contract_type,
        "expiration_date.gte": start.isoformat(),
        "expiration_date.lte": end.isoformat(),
        "limit": 250,
        "sort": "expiration_date",
        "order": "asc",
    }
    url = f"{MASSIVE_BASE}/snapshot/options/{ticker}?{urllib.parse.urlencode(params)}"
    try:
        data = request_json(url, retries=1)
    except RuntimeError as exc:
        print(f"Options fetch warning ({ticker} {contract_type}): {exc}", file=sys.stderr)
        return []
    contracts: list[OptionContract] = []
    today = date.today()
    for item in data.get("results", []) if isinstance(data, dict) else []:
        details = item.get("details") or {}
        quote = item.get("last_quote") or {}
        greeks = item.get("greeks") or {}
        day_data = item.get("day") or {}
        exp_raw = details.get("expiration_date")
        strike = to_float(details.get("strike_price"))
        bid = to_float(quote.get("bid")) or 0.0
        ask = to_float(quote.get("ask")) or 0.0
        if not exp_raw or strike is None or bid <= 0 or ask <= 0:
            continue
        exp_date = datetime.strptime(exp_raw[:10], "%Y-%m-%d").date()
        mid = (bid + ask) / 2
        contracts.append(
            OptionContract(
                ticker=ticker,
                option_type=contract_type,
                strike=strike,
                expiration=exp_date.isoformat(),
                dte=(exp_date - today).days,
                bid=bid,
                ask=ask,
                mid=mid,
                delta=to_float(greeks.get("delta")),
                iv=to_float(item.get("implied_volatility")),
                open_interest=to_int(item.get("open_interest")) or 0,
                volume=to_int(day_data.get("volume")) or 0,
                source="Massive snapshot",
            )
        )
    return contracts


def liquidity_score(contract: OptionContract) -> float:
    spread_pct = (contract.ask - contract.bid) / contract.mid if contract.mid else 1
    score = 0.0
    if spread_pct < 0.05:
        score += 4
    elif spread_pct < 0.10:
        score += 2.5
    else:
        score += 1
    if contract.open_interest > 500:
        score += 3
    elif contract.open_interest >= 100:
        score += 2
    elif contract.open_interest >= 50:
        score += 1
    if contract.volume > 50:
        score += 3
    elif contract.volume >= 10:
        score += 2
    return score


def choose_put_contract(contracts: list[OptionContract], price: float) -> OptionContract | None:
    candidates = [
        c
        for c in contracts
        if 25 <= c.dte <= 55
        and c.strike < price
        and c.open_interest >= 50
        and c.bid >= 0.05
        and (c.delta is None or -0.35 <= c.delta <= -0.12)
    ]
    if not candidates:
        return None
    candidates.sort(
        key=lambda c: (
            abs((c.delta if c.delta is not None else -0.25) + 0.25),
            -liquidity_score(c),
            -annualized_return(c.bid, c.strike, c.dte),
        )
    )
    return candidates[0]


def choose_call_contract(contracts: list[OptionContract], price: float) -> OptionContract | None:
    candidates = [
        c
        for c in contracts
        if 25 <= c.dte <= 55
        and c.strike > price
        and c.open_interest >= 50
        and c.bid >= 0.05
        and (c.delta is None or 0.12 <= c.delta <= 0.35)
    ]
    if not candidates:
        return None
    candidates.sort(
        key=lambda c: (
            abs((c.delta if c.delta is not None else 0.25) - 0.25),
            -liquidity_score(c),
            -c.bid,
        )
    )
    return candidates[0]


def annualized_return(premium: float, capital: float, dte: int | None) -> float | None:
    if not dte or dte <= 0 or capital <= 0:
        return None
    return (premium / capital) * (365 / dte) * 100


def estimate_put(price: float, ticker: str, today: date, realized_vol: float | None) -> OptionContract:
    exp = target_expiration(today)
    dte = (exp - today).days
    strike = round_to_increment(price * 0.90)
    vol = realized_vol or 0.28
    premium = max(price * vol * math.sqrt(dte / 365) * 0.13, price * 0.006)
    return OptionContract(
        ticker=ticker,
        option_type="put",
        strike=strike,
        expiration=exp.isoformat(),
        dte=dte,
        bid=round(premium, 2),
        ask=round(premium * 1.08, 2),
        mid=round(premium * 1.04, 2),
        delta=-0.25,
        iv=vol,
        open_interest=0,
        volume=0,
        source="heuristic estimate",
    )


def estimate_call(price: float, ticker: str, today: date, realized_vol: float | None) -> OptionContract:
    exp = target_expiration(today)
    dte = (exp - today).days
    strike = round_to_increment(price * 1.07)
    vol = realized_vol or 0.25
    premium = max(price * vol * math.sqrt(dte / 365) * 0.10, price * 0.004)
    return OptionContract(
        ticker=ticker,
        option_type="call",
        strike=strike,
        expiration=exp.isoformat(),
        dte=dte,
        bid=round(premium, 2),
        ask=round(premium * 1.10, 2),
        mid=round(premium * 1.05, 2),
        delta=0.25,
        iv=vol,
        open_interest=0,
        volume=0,
        source="heuristic estimate",
    )


def round_to_increment(value: float) -> float:
    if value >= 200:
        inc = 5
    elif value >= 50:
        inc = 2.5
    else:
        inc = 1
    return round(value / inc) * inc


def generate_ideas(
    positions: list[Position],
    watchlist: list[WatchlistEntry],
    option_positions: list[OptionPosition],
    quotes: dict[str, Quote],
    technicals: dict[str, Technicals],
    earnings: dict[str, str],
    massive_key: str | None,
    vix: float | None,
    vix_regime: str,
    max_tickers: int,
) -> tuple[list[TradeIdea], dict[str, Any]]:
    today = date.today()
    portfolio_value = sum(p.market_value for p in positions)
    open_put_tickers = {p.ticker.upper() for p in option_positions if p.option_type.lower() == "put"}
    position_by_symbol = {p.symbol.upper(): p for p in positions}
    ideas: list[TradeIdea] = []
    notes: dict[str, Any] = {"option_sources": {}, "excluded": []}

    covered_call_candidates = [
        p
        for p in positions
        if p.quantity >= 100
        and p.symbol.upper() not in {"FFOLX"}
        and (p.weight >= 3.5 or (p.pnl_pct is not None and p.pnl_pct > 30))
    ]
    covered_call_candidates.sort(key=lambda p: (p.weight, p.pnl_pct or 0), reverse=True)

    for pos in covered_call_candidates[:max_tickers]:
        ticker = pos.symbol.upper()
        quote = quotes.get(ticker)
        price = quote.price if quote and quote.price else pos.current_price
        tech = technicals.get(ticker, Technicals())
        contracts = fetch_massive_options(
            ticker,
            "call",
            massive_key,
            today + timedelta(days=20),
            today + timedelta(days=60),
        )
        contract = choose_call_contract(contracts, price) if contracts else None
        if contract is None:
            contract = estimate_call(price, ticker, today, tech.realized_vol_30d)
        notes["option_sources"][f"{ticker}-call"] = contract.source

        covered_contracts = int(pos.quantity // 100)
        annual = annualized_return(contract.bid, price, contract.dte)
        upside = ((contract.strike - price) / price) * 100 if price else 0
        risk_flags = []
        if ticker in earnings:
            risk_flags.append(f"earnings {earnings[ticker]}")
        if pos.weight > 12:
            risk_flags.append("large existing weight")
        score = 55 + min(pos.weight, 20) + min(pos.pnl_pct or 0, 100) * 0.05 + (annual or 0) * 0.7
        if tech.rsi14 and tech.rsi14 > 70:
            score += 4
            risk_flags.append("RSI extended")
        ideas.append(
            TradeIdea(
                rank_score=score,
                ticker=ticker,
                strategy="Covered call",
                action=f"Sell up to {covered_contracts} covered call(s)",
                strike=contract.strike,
                expiration=contract.expiration,
                premium=contract.bid,
                delta=contract.delta,
                dte=contract.dte,
                annualized_return=annual,
                max_contracts=covered_contracts,
                collateral=None,
                breakeven=None,
                rationale=(
                    f"Harvest premium against an existing {pos.weight:.1f}% weight; "
                    f"selected strike is {upside:.1f}% above spot."
                ),
                risk_flags=risk_flags,
                source=contract.source,
            )
        )

    top_watch = [
        w
        for w in watchlist
        if w.score is not None and w.score >= 58 and "Avoid" not in w.status
    ]
    top_watch.sort(key=lambda w: (w.score or 0), reverse=True)
    for entry in top_watch[:max_tickers]:
        ticker = entry.ticker.upper()
        if ticker in position_by_symbol and position_by_symbol[ticker].weight > 2:
            notes["excluded"].append(f"{ticker}: already a meaningful holding")
            continue
        quote = quotes.get(ticker)
        if not quote or not quote.price:
            notes["excluded"].append(f"{ticker}: no current quote")
            continue
        tech = technicals.get(ticker, Technicals())
        contracts = fetch_massive_options(
            ticker,
            "put",
            massive_key,
            today + timedelta(days=20),
            today + timedelta(days=60),
        )
        contract = choose_put_contract(contracts, quote.price) if contracts else None
        if contract is None:
            contract = estimate_put(quote.price, ticker, today, tech.realized_vol_30d)
        notes["option_sources"][f"{ticker}-put"] = contract.source

        annual = annualized_return(contract.bid, contract.strike, contract.dte)
        breakeven = contract.strike - contract.bid
        risk_flags = []
        if ticker in earnings:
            risk_flags.append(f"earnings {earnings[ticker]}")
        if ticker in open_put_tickers:
            risk_flags.append("existing short put exposure")
        if vix_regime in {"ELEVATED", "CRISIS"}:
            risk_flags.append("prefer defined-risk spread in elevated volatility")
        max_capital = portfolio_value * 0.05
        vix_sizing = {"LOW": 0.75, "NORMAL": 1.0, "ELEVATED": 0.5, "CRISIS": 0.25}.get(vix_regime, 0.75)
        max_contracts = max(1, int((max_capital * vix_sizing) // (contract.strike * 100)))
        collateral = max_contracts * contract.strike * 100
        score = (entry.score or 50) + (annual or 0) * 0.8 + liquidity_score(contract)
        if risk_flags:
            score -= 6
        ideas.append(
            TradeIdea(
                rank_score=score,
                ticker=ticker,
                strategy="Cash-secured put",
                action=f"Sell {max_contracts} put(s); use a bull put spread if risk budget is tight",
                strike=contract.strike,
                expiration=contract.expiration,
                premium=contract.bid,
                delta=contract.delta,
                dte=contract.dte,
                annualized_return=annual,
                max_contracts=max_contracts,
                collateral=collateral,
                breakeven=breakeven,
                rationale=(
                    f"Top watchlist candidate ({entry.grade}, score {entry.score:.1f}) with an entry "
                    f"basis near ${breakeven:.2f} if assigned."
                ),
                risk_flags=risk_flags,
                source=contract.source,
            )
        )

    if vix is not None and vix < 18 and portfolio_value > 0:
        spy = quotes.get("SPY")
        if spy and spy.price:
            hedge_strike = round_to_increment(spy.price * 0.95)
            exp = target_expiration(today)
            ideas.append(
                TradeIdea(
                    rank_score=58,
                    ticker="SPY",
                    strategy="Portfolio hedge watch",
                    action="Price a 45-DTE put spread only if market breadth deteriorates",
                    strike=hedge_strike,
                    expiration=exp.isoformat(),
                    premium=None,
                    dte=(exp - today).days,
                    rationale=(
                        "Portfolio remains equity-heavy and VIX is low enough to keep hedges on the watchlist."
                    ),
                    risk_flags=["watchlist only; not a default entry"],
                    source="portfolio risk overlay",
                )
            )

    ideas.sort(key=lambda idea: idea.rank_score, reverse=True)
    return ideas, notes


def money(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"${value:,.2f}"


def pct(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:.1f}%"


def format_report(
    ideas: list[TradeIdea],
    positions: list[Position],
    watchlist: list[WatchlistEntry],
    option_positions: list[OptionPosition],
    quotes: dict[str, Quote],
    earnings: dict[str, str],
    notes: dict[str, Any],
    fmp_source: str,
    massive_source: str,
    vix: float | None,
    vix_regime: str,
) -> str:
    today = date.today().isoformat()
    portfolio_value = sum(p.market_value for p in positions)
    top_positions = sorted(positions, key=lambda p: p.weight, reverse=True)[:5]
    top_watch = [w for w in watchlist if w.score is not None]
    top_watch.sort(key=lambda w: w.score or 0, reverse=True)

    lines = [
        f"# Trade Idea Generator - {today}",
        "",
        "> Educational scan only. These are not trade orders or investment advice. Verify live chains, liquidity, earnings, and portfolio limits before entry.",
        "",
        "## Dashboard",
        "",
        f"- Portfolio market value from context: **{money(portfolio_value)}**",
        f"- VIX: **{vix:.2f} ({vix_regime})**" if vix is not None else "- VIX: **N/A**",
        f"- Current equity positions scanned: **{len(positions)}**",
        f"- Watchlist names scanned: **{len(watchlist)}**",
        f"- Open short-premium positions: **{len(option_positions)}**",
        f"- Market data source: **{fmp_source}**",
        f"- Options data source: **{massive_source}**",
        "",
        "## Top Current Portfolio Weights",
        "",
        "| Ticker | Weight | Position Value | Current Price |",
        "|--------|--------|----------------|---------------|",
    ]
    for pos in top_positions:
        price = quotes.get(pos.symbol, Quote(pos.symbol, pos.current_price)).price or pos.current_price
        lines.append(f"| {pos.symbol} | {pos.weight:.1f}% | {money(pos.market_value)} | {money(price)} |")

    lines.extend(
        [
            "",
            "## Top Watchlist Candidates",
            "",
            "| Ticker | Score | Grade | Status | Quote |",
            "|--------|-------|-------|--------|-------|",
        ]
    )
    for entry in top_watch[:8]:
        quote = quotes.get(entry.ticker.upper())
        lines.append(
            f"| {entry.ticker} | {entry.score:.1f} | {entry.grade} | {entry.status} | {money(quote.price if quote else None)} |"
        )

    lines.extend(
        [
            "",
            "## Ranked Trade Ideas",
            "",
            "| Rank | Ticker | Strategy | Contract / Level | Premium | Ann. ROC | Action | Flags | Source |",
            "|------|--------|----------|------------------|---------|----------|--------|-------|--------|",
        ]
    )
    for idx, idea in enumerate(ideas[:8], start=1):
        contract = "N/A"
        if idea.strike and idea.expiration:
            suffix = "P" if "put" in idea.strategy.lower() else "C"
            if "hedge" in idea.strategy.lower():
                suffix = "P"
            contract = f"{idea.expiration} ${idea.strike:g}{suffix}"
        flags = "; ".join(idea.risk_flags) if idea.risk_flags else "None"
        lines.append(
            "| {rank} | {ticker} | {strategy} | {contract} | {premium} | {roc} | {action} | {flags} | {source} |".format(
                rank=idx,
                ticker=idea.ticker,
                strategy=idea.strategy,
                contract=contract,
                premium=money(idea.premium),
                roc=pct(idea.annualized_return),
                action=idea.action,
                flags=flags,
                source=idea.source,
            )
        )

    lines.extend(["", "## Idea Detail", ""])
    for idx, idea in enumerate(ideas[:5], start=1):
        lines.extend(
            [
                f"### {idx}. {idea.ticker} - {idea.strategy}",
                "",
                f"- **Action:** {idea.action}",
                f"- **Contract / level:** {idea.expiration or 'N/A'} {money(idea.strike)}",
                f"- **Premium:** {money(idea.premium)} | **Delta:** {idea.delta:.2f}" if idea.delta is not None else f"- **Premium:** {money(idea.premium)} | **Delta:** N/A",
                f"- **DTE:** {idea.dte or 'N/A'} | **Annualized ROC:** {pct(idea.annualized_return)}",
                f"- **Breakeven / collateral:** {money(idea.breakeven)} / {money(idea.collateral)}",
                f"- **Rationale:** {idea.rationale}",
                f"- **Risk flags:** {', '.join(idea.risk_flags) if idea.risk_flags else 'None'}",
                "",
            ]
        )

    if earnings:
        lines.extend(["## Earnings in Lookahead Window", ""])
        for ticker, earnings_date in sorted(earnings.items()):
            lines.append(f"- {ticker}: {earnings_date}")
        lines.append("")

    if notes.get("excluded"):
        lines.extend(["## Exclusions / Data Gaps", ""])
        for item in notes["excluded"][:12]:
            lines.append(f"- {item}")
        lines.append("")

    lines.extend(
        [
            "## Risk Checklist",
            "",
            "- Confirm no unplanned earnings exposure inside the intended holding period.",
            "- Keep any single idea within the 5% max-position rule and total options allocation within 30%.",
            "- Use 50% profit-taking and 200% credit stop discipline for short premium.",
            "- Recheck bid/ask spreads and open interest before entry; heuristic ideas require manual chain verification.",
            "",
            f"*Generated by scripts/trade_idea_generator.py on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} local time.*",
            "",
        ]
    )
    return "\n".join(lines)


def format_telegram(ideas: list[TradeIdea], vix: float | None, vix_regime: str, report_path: Path) -> str:
    today = date.today().isoformat()
    lines = [
        f"ALTAMIRA TRADE IDEAS - {today}",
        f"VIX: {vix:.2f} ({vix_regime})" if vix is not None else "VIX: N/A",
        "",
    ]
    if not ideas:
        lines.extend(
            [
                "No qualifying ideas generated from the current portfolio/watchlist.",
                "Review data source availability and options-chain liquidity.",
            ]
        )
    else:
        for idx, idea in enumerate(ideas[:5], start=1):
            contract = ""
            if idea.strike and idea.expiration:
                suffix = "P" if "put" in idea.strategy.lower() or "hedge" in idea.strategy.lower() else "C"
                contract = f" {idea.expiration} ${idea.strike:g}{suffix}"
            lines.append(f"{idx}. {idea.ticker} - {idea.strategy}{contract}")
            lines.append(
                f"   Premium: {money(idea.premium)} | Ann ROC: {pct(idea.annualized_return)} | DTE: {idea.dte or 'N/A'}"
            )
            lines.append(f"   Action: {idea.action}")
            if idea.risk_flags:
                lines.append(f"   Flags: {', '.join(idea.risk_flags)}")
            lines.append("")
    lines.extend(
        [
            "Risk: scan only, not an order. Verify live chain/liquidity/earnings before entry.",
            f"Report: {report_path.as_posix()}",
        ]
    )
    return "\n".join(lines).strip()


def split_telegram_message(text: str, limit: int = 3900) -> list[str]:
    if len(text) <= limit:
        return [text]
    parts = []
    current = ""
    for block in text.split("\n\n"):
        if len(current) + len(block) + 2 > limit:
            parts.append(current.strip())
            current = block
        else:
            current = f"{current}\n\n{block}" if current else block
    if current.strip():
        parts.append(current.strip())
    return parts


def send_telegram(bot_token: str, chat_id: str, text: str) -> list[Any]:
    url = f"{TELEGRAM_BASE}/bot{bot_token}/sendMessage"
    responses = []
    parts = split_telegram_message(text)
    for part in parts:
        responses.append(
            post_json(
                url,
                {
                    "chat_id": chat_id,
                    "text": part,
                    "disable_web_page_preview": True,
                },
            )
        )
    return responses


def build_universe(positions: list[Position], watchlist: list[WatchlistEntry]) -> set[str]:
    tickers = {p.symbol.upper() for p in positions if p.symbol and p.symbol.upper() != "FFOLX"}
    tickers.update(w.ticker.upper() for w in watchlist if w.ticker)
    tickers.update({"SPY", "^VIX"})
    return tickers


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate portfolio/watchlist trade ideas.")
    parser.add_argument("--send-telegram", action="store_true", help="Send the summary to Telegram.")
    parser.add_argument("--dry-run", action="store_true", help="Generate report but do not send Telegram.")
    parser.add_argument("--max-tickers", type=int, default=8, help="Max holdings/watchlist names to scan per strategy.")
    parser.add_argument("--out", type=Path, help="Override markdown output path.")
    args = parser.parse_args()

    positions = parse_portfolio(CONTEXT / "portfolio-details.md")
    watchlist = parse_watchlist(CONTEXT / "watchlist.md")
    option_positions = parse_option_positions(CONTEXT / "options-positions.md")

    fmp_key, fmp_source = get_fmp_key()
    massive_key, massive_source = get_massive_key()
    telegram_chat_id, telegram_chat_source = get_telegram_chat_id()
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")

    universe = build_universe(positions, watchlist)
    quotes = fetch_quotes(universe, fmp_key)
    for pos in positions:
        quotes.setdefault(
            pos.symbol.upper(),
            Quote(ticker=pos.symbol.upper(), price=pos.current_price, name=pos.symbol.upper()),
        )

    technicals: dict[str, Technicals] = {}
    prioritized = sorted(universe)
    for ticker in prioritized[: max(args.max_tickers * 2, 12)]:
        if ticker.startswith("^"):
            continue
        technicals[ticker] = calculate_technicals(fetch_historical(ticker, fmp_key))

    vix, vix_regime = fetch_vix(fmp_key)
    earnings = fetch_earnings(universe, fmp_key, date.today(), date.today() + timedelta(days=60))

    ideas, notes = generate_ideas(
        positions,
        watchlist,
        option_positions,
        quotes,
        technicals,
        earnings,
        massive_key,
        vix,
        vix_regime,
        max(1, args.max_tickers),
    )

    report = format_report(
        ideas,
        positions,
        watchlist,
        option_positions,
        quotes,
        earnings,
        notes,
        fmp_source,
        massive_source,
        vix,
        vix_regime,
    )
    OUTPUTS.mkdir(exist_ok=True)
    out_path = args.out or OUTPUTS / f"trade-idea-generator-{date.today().isoformat()}.md"
    out_path.write_text(report, encoding="utf-8")

    telegram_text = format_telegram(ideas, vix, vix_regime, out_path.relative_to(WORKSPACE))
    telegram_sent = False
    telegram_response_ids: list[int] = []
    if args.send_telegram and not args.dry_run:
        if not telegram_token:
            print("TELEGRAM_BOT_TOKEN is not set; report generated but Telegram was not sent.", file=sys.stderr)
        elif not telegram_chat_id:
            print("TELEGRAM_CHAT_ID is not set and no repo default was found; Telegram was not sent.", file=sys.stderr)
        else:
            responses = send_telegram(telegram_token, telegram_chat_id, telegram_text)
            telegram_sent = all(bool(resp.get("ok")) for resp in responses if isinstance(resp, dict))
            telegram_response_ids = [
                int(resp.get("result", {}).get("message_id"))
                for resp in responses
                if isinstance(resp, dict) and resp.get("result", {}).get("message_id") is not None
            ]

    summary = {
        "report": str(out_path.relative_to(WORKSPACE)),
        "ideas": len(ideas),
        "top": [f"{idea.ticker} {idea.strategy}" for idea in ideas[:3]],
        "telegram_requested": args.send_telegram,
        "telegram_sent": telegram_sent,
        "telegram_message_ids": telegram_response_ids,
        "telegram_chat_source": telegram_chat_source,
        "fmp_source": fmp_source,
        "massive_source": massive_source,
    }
    print(json.dumps(summary, indent=2))
    return 0 if (not args.send_telegram or args.dry_run or telegram_sent) else 2


if __name__ == "__main__":
    raise SystemExit(main())
