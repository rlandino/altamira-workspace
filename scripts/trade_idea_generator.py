#!/usr/bin/env python3
"""Generate daily portfolio/watchlist trade ideas and optionally send Telegram.

The script intentionally uses only the Python standard library so it can run in
fresh cloud automation environments without installing dependencies.
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
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTEXT_DIR = ROOT / "context"
OUTPUTS_DIR = ROOT / "outputs"
FMP_BASE = "https://financialmodelingprep.com/api/v3"
MASSIVE_BASE = "https://api.massive.com/v3"

EXCLUDED_SYMBOLS = {"FFOLX"}
SECTOR_MAP = {
    "AAPL": "Technology",
    "ABBV": "Healthcare",
    "ABT": "Healthcare",
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
    "FICO": "Technology",
    "GD": "Industrials",
    "GOOGL": "Communication Services",
    "INTU": "Technology",
    "ISRG": "Healthcare",
    "JPM": "Financials",
    "KLAC": "Technology",
    "KMI": "Energy",
    "LLY": "Healthcare",
    "LRCX": "Technology",
    "MA": "Financials",
    "MELI": "Consumer Cyclical",
    "META": "Communication Services",
    "MRVL": "Technology",
    "MSCI": "Financials",
    "MSFT": "Technology",
    "NFLX": "Communication Services",
    "NOW": "Technology",
    "NVDA": "Technology",
    "PANW": "Technology",
    "PLTR": "Technology",
    "QQQ": "Index ETF",
    "SPGI": "Financials",
    "SPY": "Index ETF",
    "TSLA": "Consumer Cyclical",
    "TSM": "Technology",
    "TMO": "Healthcare",
    "V": "Financials",
    "WM": "Industrials",
}


@dataclass
class Holding:
    symbol: str
    quantity: float = 0.0
    avg_price: float | None = None
    current_price: float | None = None
    market_value: float | None = None
    cost_basis: float | None = None
    pnl_pct: float | None = None
    weight_pct: float | None = None


@dataclass
class WatchlistEntry:
    symbol: str
    score: float | None = None
    grade: str = ""
    company: str = ""
    status: str = ""


@dataclass
class ShortPremiumPosition:
    ticker: str
    strike: float
    option_type: str
    expiration: str
    credit: float
    current: float
    contracts: int


@dataclass
class MarketSnapshot:
    price: float | None = None
    change_pct: float | None = None
    sma50: float | None = None
    sma200: float | None = None
    volume: float | None = None
    avg_volume: float | None = None
    market_cap: float | None = None
    year_high: float | None = None
    year_low: float | None = None
    rsi14: float | None = None
    return_20d_pct: float | None = None


@dataclass
class OptionContract:
    option_type: str
    strike: float
    expiration: str
    dte: int
    bid: float
    ask: float
    mid: float
    delta: float | None
    theta: float | None
    iv: float | None
    open_interest: int
    volume: int
    ticker: str = ""

    @property
    def spread_pct(self) -> float | None:
        if self.mid <= 0:
            return None
        return (self.ask - self.bid) / self.mid


@dataclass
class Candidate:
    symbol: str
    source: str
    sector: str
    market: MarketSnapshot
    holding: Holding | None = None
    watchlist: WatchlistEntry | None = None
    has_open_short_premium: bool = False
    earnings_date: str | None = None
    score: float = 0.0
    reasons: list[str] = field(default_factory=list)
    cautions: list[str] = field(default_factory=list)


@dataclass
class TradeIdea:
    rank_score: float
    symbol: str
    strategy: str
    action: str
    thesis: str
    risk: str
    sizing: str
    contract: OptionContract | None = None
    hedge_contract: OptionContract | None = None
    candidate: Candidate | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate trade ideas from context/portfolio-details.md and context/watchlist.md."
    )
    parser.add_argument("--send-telegram", action="store_true", help="Send the summary to Telegram.")
    parser.add_argument("--no-telegram", action="store_true", help="Do not send Telegram, even if configured.")
    parser.add_argument("--chat-id", default=os.environ.get("TELEGRAM_CHAT_ID"), help="Telegram chat/channel ID.")
    parser.add_argument("--max-tickers", type=int, default=24, help="Maximum symbols to evaluate.")
    parser.add_argument("--max-ideas", type=int, default=5, help="Maximum trade ideas to include.")
    parser.add_argument("--out", default=None, help="Markdown report path. Defaults to outputs/trade-idea-generator-DATE.md")
    return parser.parse_args()


def clean_cell(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value).replace("**", "").replace("⭐", "").strip()


def parse_float(value: str) -> float | None:
    text = clean_cell(value).replace("$", "").replace(",", "").replace("%", "").strip()
    text = text.replace("+", "")
    if not text or text in {"—", "-", "N/A"}:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def split_markdown_row(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def parse_portfolio(path: Path) -> list[Holding]:
    if not path.exists():
        return []
    rows: list[Holding] = []
    in_table = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.startswith("| SYMBOL |"):
            in_table = True
            continue
        if in_table and raw.startswith("|---"):
            continue
        if in_table:
            if not raw.startswith("|") or raw.strip() == "|":
                break
            cells = split_markdown_row(raw)
            if len(cells) < 9:
                continue
            symbol = clean_cell(cells[0]).upper()
            if symbol in EXCLUDED_SYMBOLS:
                continue
            rows.append(
                Holding(
                    symbol=symbol,
                    quantity=parse_float(cells[1]) or 0.0,
                    avg_price=parse_float(cells[2]),
                    current_price=parse_float(cells[3]),
                    market_value=parse_float(cells[4]),
                    cost_basis=parse_float(cells[5]),
                    pnl_pct=parse_float(cells[6]),
                    weight_pct=parse_float(cells[8]),
                )
            )
    return rows


def parse_watchlist(path: Path) -> list[WatchlistEntry]:
    if not path.exists():
        return []
    entries: list[WatchlistEntry] = []
    in_table = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.startswith("| Ticker |"):
            in_table = True
            continue
        if in_table and raw.startswith("|---"):
            continue
        if in_table:
            if not raw.startswith("|") or raw.strip() == "|":
                break
            cells = split_markdown_row(raw)
            if len(cells) < 5:
                continue
            entries.append(
                WatchlistEntry(
                    symbol=clean_cell(cells[0]).upper(),
                    score=parse_float(cells[1]),
                    grade=clean_cell(cells[2]),
                    company=clean_cell(cells[3]),
                    status=clean_cell(cells[4]),
                )
            )
    return entries


def parse_short_premium(path: Path) -> list[ShortPremiumPosition]:
    if not path.exists():
        return []
    rows: list[ShortPremiumPosition] = []
    in_table = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.startswith("| Ticker | Strike |"):
            in_table = True
            continue
        if in_table and raw.startswith("|---"):
            continue
        if in_table:
            if not raw.startswith("|") or raw.strip() == "|":
                break
            cells = split_markdown_row(raw)
            if len(cells) < 7:
                continue
            rows.append(
                ShortPremiumPosition(
                    ticker=clean_cell(cells[0]).upper(),
                    strike=parse_float(cells[1]) or 0.0,
                    option_type=clean_cell(cells[2]),
                    expiration=clean_cell(cells[3]),
                    credit=parse_float(cells[4]) or 0.0,
                    current=parse_float(cells[5]) or 0.0,
                    contracts=int(parse_float(cells[6]) or 0),
                )
            )
    return rows


def legacy_constant(name: str) -> str | None:
    """Read an existing workspace-local API constant without duplicating it here."""
    for path in [ROOT / "scripts" / "stock-scorer.py", ROOT / "scripts" / "thesis-generator.py"]:
        if not path.exists():
            continue
        match = re.search(rf"{re.escape(name)}\s*=\s*[\"']([^\"']+)", path.read_text(encoding="utf-8"))
        if match:
            return match.group(1)
    return None


def fmp_key() -> str | None:
    return os.environ.get("FMP_API_KEY") or legacy_constant("FMP_API_KEY")


def massive_key() -> str | None:
    return os.environ.get("MASSIVE_API_KEY") or legacy_constant("MASSIVE_API_KEY")


def fallback_chat_id() -> str | None:
    fixed = ROOT / "outputs" / "csp-daily-scan-fixed.json"
    if not fixed.exists():
        return None
    try:
        data = json.loads(fixed.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    for node in data.get("nodes", []):
        chat_id = node.get("parameters", {}).get("chatId")
        if chat_id and "$env" not in str(chat_id) and "TELEGRAM_CHAT_ID" not in str(chat_id):
            return str(chat_id).lstrip("=")
    return None


def http_json(url: str, timeout: int = 20) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": "AltamiraTradeIdeaGenerator/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def post_form(url: str, payload: dict[str, str], timeout: int = 20) -> Any:
    data = urllib.parse.urlencode(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_quotes(symbols: list[str], key: str) -> dict[str, MarketSnapshot]:
    snapshots: dict[str, MarketSnapshot] = {}
    for i in range(0, len(symbols), 25):
        chunk = symbols[i : i + 25]
        url = f"{FMP_BASE}/quote/{','.join(chunk)}?{urllib.parse.urlencode({'apikey': key})}"
        try:
            data = http_json(url)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            print(f"Warning: quote fetch failed for {chunk}: {exc}", file=sys.stderr)
            continue
        for row in data if isinstance(data, list) else []:
            symbol = str(row.get("symbol", "")).upper()
            snapshots[symbol] = MarketSnapshot(
                price=row.get("price"),
                change_pct=row.get("changesPercentage"),
                sma50=row.get("priceAvg50"),
                sma200=row.get("priceAvg200"),
                volume=row.get("volume"),
                avg_volume=row.get("avgVolume"),
                market_cap=row.get("marketCap"),
                year_high=row.get("yearHigh"),
                year_low=row.get("yearLow"),
            )
    return snapshots


def fetch_historical_indicators(symbol: str, key: str, today: date) -> tuple[float | None, float | None]:
    start = today - timedelta(days=45)
    params = urllib.parse.urlencode({"from": start.isoformat(), "to": today.isoformat(), "apikey": key})
    url = f"{FMP_BASE}/historical-price-full/{symbol}?{params}"
    try:
        data = http_json(url)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None, None
    rows = data.get("historical", []) if isinstance(data, dict) else []
    closes = [float(row["close"]) for row in reversed(rows) if row.get("close") is not None]
    if len(closes) < 15:
        return None, None
    rsi = compute_rsi(closes[-15:])
    return_20d = None
    if len(closes) >= 21 and closes[-21] > 0:
        return_20d = ((closes[-1] / closes[-21]) - 1) * 100
    return rsi, return_20d


def compute_rsi(closes: list[float]) -> float | None:
    if len(closes) < 15:
        return None
    gains: list[float] = []
    losses: list[float] = []
    for prev, curr in zip(closes[:-1], closes[1:]):
        change = curr - prev
        gains.append(max(change, 0.0))
        losses.append(abs(min(change, 0.0)))
    avg_gain = sum(gains[-14:]) / 14
    avg_loss = sum(losses[-14:]) / 14
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def fetch_earnings(symbols: list[str], key: str, today: date, days: int = 45) -> dict[str, str]:
    end = today + timedelta(days=days)
    params = urllib.parse.urlencode({"from": today.isoformat(), "to": end.isoformat(), "apikey": key})
    url = f"{FMP_BASE}/earning_calendar?{params}"
    try:
        data = http_json(url, timeout=25)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"Warning: earnings fetch failed: {exc}", file=sys.stderr)
        return {}
    wanted = set(symbols)
    out: dict[str, str] = {}
    for row in data if isinstance(data, list) else []:
        symbol = str(row.get("symbol", "")).upper()
        if symbol in wanted and row.get("date"):
            out.setdefault(symbol, str(row["date"])[:10])
    return out


def normalize_option(row: dict[str, Any], option_type: str, today: date) -> OptionContract | None:
    details = row.get("details") or {}
    quote = row.get("last_quote") or {}
    greeks = row.get("greeks") or {}
    expiration = details.get("expiration_date") or row.get("expiration_date")
    strike = details.get("strike_price") or row.get("strike")
    if not expiration or strike is None:
        return None
    try:
        exp_date = datetime.strptime(str(expiration)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None
    bid = float(quote.get("bid") or row.get("bid") or 0.0)
    ask = float(quote.get("ask") or row.get("ask") or 0.0)
    midpoint = quote.get("midpoint")
    if midpoint is None:
        midpoint = (bid + ask) / 2 if bid or ask else 0.0
    mid = float(midpoint or 0.0)
    if bid <= 0 or ask <= 0 or ask < bid:
        return None
    return OptionContract(
        option_type=option_type,
        strike=float(strike),
        expiration=exp_date.isoformat(),
        dte=(exp_date - today).days,
        bid=bid,
        ask=ask,
        mid=mid,
        delta=greeks.get("delta") if greeks.get("delta") is not None else row.get("delta"),
        theta=greeks.get("theta") if greeks.get("theta") is not None else row.get("theta"),
        iv=row.get("implied_volatility") or row.get("impliedVolatility"),
        open_interest=int(row.get("open_interest") or row.get("openInterest") or 0),
        volume=int((row.get("day") or {}).get("volume") or row.get("volume") or 0),
        ticker=str(details.get("ticker") or ""),
    )


def fetch_options(symbol: str, price: float, option_type: str, key: str, today: date) -> list[OptionContract]:
    from_date = today + timedelta(days=25)
    to_date = today + timedelta(days=60)
    if option_type == "put":
        strike_min = max(1, price * 0.70)
        strike_max = price * 0.99
    else:
        strike_min = price * 1.01
        strike_max = price * 1.35
    params = {
        "contract_type": option_type,
        "expiration_date.gte": from_date.isoformat(),
        "expiration_date.lte": to_date.isoformat(),
        "strike_price.gte": f"{strike_min:.2f}",
        "strike_price.lte": f"{strike_max:.2f}",
        "limit": "250",
        "apiKey": key,
    }
    url = f"{MASSIVE_BASE}/snapshot/options/{symbol}?{urllib.parse.urlencode(params)}"
    try:
        data = http_json(url, timeout=25)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"Warning: options fetch failed for {symbol} {option_type}: {exc}", file=sys.stderr)
        return []
    contracts = []
    for row in data.get("results", []) if isinstance(data, dict) else []:
        contract = normalize_option(row, option_type, today)
        if contract:
            contracts.append(contract)
    return contracts


def liquidity_score(contract: OptionContract) -> float:
    spread = contract.spread_pct
    score = 0.0
    if spread is not None:
        score += max(0.0, 25 * (1 - min(spread, 0.5) / 0.5))
    score += min(contract.open_interest / 500, 1) * 20
    score += min(contract.volume / 50, 1) * 10
    return score


def pick_contract(contracts: list[OptionContract], target_delta: float, option_type: str) -> OptionContract | None:
    candidates = []
    for contract in contracts:
        if not (25 <= contract.dte <= 60):
            continue
        if contract.open_interest < 25:
            continue
        spread = contract.spread_pct
        if spread is not None and spread > 0.45:
            continue
        delta = contract.delta
        if delta is None:
            moneyness = contract.strike / max(contract.strike, 1)
            delta_penalty = 0.2 + abs(moneyness - 1)
        else:
            delta_penalty = abs(abs(float(delta)) - abs(target_delta))
        if delta is not None:
            if option_type == "put" and not (-0.35 <= float(delta) <= -0.12):
                continue
            if option_type == "call" and not (0.12 <= float(delta) <= 0.35):
                continue
        score = liquidity_score(contract) - (delta_penalty * 80) + min(contract.bid / max(contract.strike, 1) * 1000, 20)
        candidates.append((score, contract))
    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1] if candidates else None


def pick_spread_long_put(contracts: list[OptionContract], short_put: OptionContract, price: float) -> OptionContract | None:
    target_width = max(5.0, min(25.0, price * 0.04))
    same_exp = [
        c
        for c in contracts
        if c.expiration == short_put.expiration
        and c.strike < short_put.strike
        and c.ask > 0
        and c.strike <= short_put.strike - min(2.5, target_width / 2)
    ]
    if not same_exp:
        return None
    same_exp.sort(key=lambda c: abs((short_put.strike - c.strike) - target_width))
    return same_exp[0]


def portfolio_value(holdings: list[Holding]) -> float:
    total = sum(h.market_value or 0 for h in holdings)
    return total if total > 0 else 100000.0


def build_universe(holdings: list[Holding], watchlist: list[WatchlistEntry], max_tickers: int) -> list[str]:
    symbols: list[str] = []
    for holding in sorted(holdings, key=lambda h: h.market_value or 0, reverse=True):
        if holding.symbol not in EXCLUDED_SYMBOLS:
            symbols.append(holding.symbol)
    top_watchlist = sorted(
        [w for w in watchlist if (w.score or 0) >= 58 or "Top Candidate" in w.status],
        key=lambda w: w.score or 0,
        reverse=True,
    )
    for entry in top_watchlist:
        symbols.append(entry.symbol)
    deduped: list[str] = []
    for symbol in symbols:
        if symbol and symbol not in deduped and symbol not in EXCLUDED_SYMBOLS:
            deduped.append(symbol)
    return deduped[:max_tickers]


def score_candidate(candidate: Candidate) -> None:
    market = candidate.market
    score = 50.0
    if market.price and market.sma50:
        if market.price > market.sma50:
            score += 8
            candidate.reasons.append("price above 50-day average")
        else:
            score -= 8
            candidate.cautions.append("price below 50-day average")
    if market.price and market.sma200:
        if market.price > market.sma200:
            score += 6
        else:
            score -= 6
            candidate.cautions.append("price below 200-day average")
    if market.rsi14 is not None:
        if 45 <= market.rsi14 <= 65:
            score += 8
            candidate.reasons.append(f"RSI balanced at {market.rsi14:.0f}")
        elif 65 < market.rsi14 <= 72:
            score += 2
            candidate.reasons.append(f"momentum firm with RSI {market.rsi14:.0f}")
        elif market.rsi14 > 72:
            score -= 8
            candidate.cautions.append(f"overbought RSI {market.rsi14:.0f}")
        elif market.rsi14 < 35:
            score -= 3
            candidate.cautions.append(f"weak RSI {market.rsi14:.0f}")
    if market.return_20d_pct is not None:
        if -2 <= market.return_20d_pct <= 8:
            score += 5
        elif market.return_20d_pct > 12:
            score -= 4
            candidate.cautions.append(f"extended 20-day move {market.return_20d_pct:.1f}%")
        elif market.return_20d_pct < -8:
            score -= 5
            candidate.cautions.append(f"weak 20-day move {market.return_20d_pct:.1f}%")
    if candidate.watchlist and candidate.watchlist.score is not None:
        score += max(0, min(12, (candidate.watchlist.score - 50) / 2))
        if "Top Candidate" in candidate.watchlist.status:
            score += 4
            candidate.reasons.append(f"watchlist top candidate ({candidate.watchlist.grade})")
    if candidate.holding:
        weight = candidate.holding.weight_pct or 0
        if weight > 10:
            score -= 3
            candidate.cautions.append(f"portfolio weight already {weight:.1f}%")
        elif 0 < weight < 5:
            score += 3
    if candidate.has_open_short_premium:
        score -= 5
        candidate.cautions.append("existing short-premium exposure open")
    if candidate.earnings_date:
        score -= 18
        candidate.cautions.append(f"earnings within 45 days ({candidate.earnings_date})")
    candidate.score = score


def classify_vix(vix: float | None) -> tuple[str, str]:
    if vix is None:
        return "UNKNOWN", "Use normal sizing until live VIX is confirmed."
    if vix < 15:
        return "LOW", "Premium is thinner; favor covered calls or smaller CSPs."
    if vix <= 25:
        return "NORMAL", "CSPs, bull put spreads, and covered calls are acceptable with standard sizing."
    if vix <= 35:
        return "ELEVATED", "Favor defined-risk spreads and reduced size."
    return "CRISIS", "Spreads only; minimal size."


def make_trade_ideas(
    candidates: list[Candidate],
    massive_api_key: str | None,
    today: date,
    account_value: float,
    max_ideas: int,
    vix_regime: str,
) -> list[TradeIdea]:
    ideas: list[TradeIdea] = []
    option_cache: dict[tuple[str, str], list[OptionContract]] = {}

    def get_options(symbol: str, price: float, option_type: str) -> list[OptionContract]:
        key = (symbol, option_type)
        if key not in option_cache:
            option_cache[key] = fetch_options(symbol, price, option_type, massive_api_key, today) if massive_api_key else []
        return option_cache[key]

    for candidate in sorted(candidates, key=lambda c: c.score, reverse=True)[:14]:
        price = candidate.market.price
        if price is None or price <= 0:
            continue
        holding = candidate.holding
        contracts_text = "Size so max loss stays below 5% of portfolio; prefer 1-3 contracts unless liquidity is exceptional."
        if vix_regime in {"ELEVATED", "CRISIS"}:
            contracts_text = "Use reduced size and defined risk due to elevated volatility."

        if holding and holding.quantity >= 100 and ((holding.weight_pct or 0) >= 6 or (candidate.market.rsi14 or 0) >= 65):
            calls = get_options(candidate.symbol, price, "call")
            call = pick_contract(calls, 0.25, "call")
            if call:
                premium = call.bid * 100
                upside = (call.strike / price - 1) * 100
                ideas.append(
                    TradeIdea(
                        rank_score=candidate.score + 6,
                        symbol=candidate.symbol,
                        strategy="Covered call",
                        action=f"Sell {call.expiration} ${call.strike:g} call near {abs(call.delta or 0):.2f} delta for ~${call.bid:.2f} credit.",
                        thesis=(
                            f"Overlay premium on an existing {holding.weight_pct or 0:.1f}% portfolio position; "
                            f"shares have strong embedded gains and {', '.join(candidate.reasons[:2]) or 'positive trend context'}."
                        ),
                        risk=(
                            f"Caps upside about {upside:.1f}% above spot through expiration; avoid if willing to add more directional exposure."
                        ),
                        sizing=f"One contract per 100 shares; indicative premium ${premium:,.0f}/contract. {contracts_text}",
                        contract=call,
                        candidate=candidate,
                    )
                )
                continue

        if candidate.earnings_date:
            continue

        if candidate.has_open_short_premium and holding:
            open_note = "Existing CSP should be managed before adding another short-put line."
            ideas.append(
                TradeIdea(
                    rank_score=candidate.score - 2,
                    symbol=candidate.symbol,
                    strategy="Manage existing premium",
                    action="Hold/monitor existing short premium; avoid adding a new CSP today.",
                    thesis=f"{candidate.symbol} remains in the portfolio universe, but current option exposure is already open.",
                    risk=open_note,
                    sizing="No incremental risk until existing position is closed, rolled, or reduced.",
                    candidate=candidate,
                )
            )
            continue

        puts = get_options(candidate.symbol, price, "put")
        short_put = pick_contract(puts, -0.25, "put")
        if not short_put:
            continue

        long_put = pick_spread_long_put(puts, short_put, price)
        spread_credit = None
        max_loss = None
        if long_put and short_put.bid > long_put.ask:
            spread_credit = short_put.bid - long_put.ask
            max_loss = (short_put.strike - long_put.strike - spread_credit) * 100

        use_spread = (
            candidate.sector == "Technology"
            or candidate.symbol in {"SPY", "QQQ"}
            or vix_regime in {"ELEVATED", "CRISIS"}
            or (short_put.strike * 100) > account_value * 0.05
        ) and long_put is not None and spread_credit is not None and spread_credit > 0

        if use_spread:
            pop = max(0, min(100, (1 - abs(short_put.delta or -0.25)) * 100))
            ideas.append(
                TradeIdea(
                    rank_score=candidate.score + 4,
                    symbol=candidate.symbol,
                    strategy="Bull put spread",
                    action=(
                        f"Sell {short_put.expiration} ${short_put.strike:g}/${long_put.strike:g} put spread "
                        f"for ~${spread_credit:.2f} net credit."
                    ),
                    thesis=f"Defined-risk bullish premium setup; {', '.join(candidate.reasons[:3]) or 'quality/watchlist context is constructive'}.",
                    risk=(
                        f"Max loss about ${max_loss:,.0f}/spread before commissions; short strike has approx {pop:.0f}% delta-implied OTM probability."
                    ),
                    sizing=f"Keep total spread max loss below 1-2% of account; {contracts_text}",
                    contract=short_put,
                    hedge_contract=long_put,
                    candidate=candidate,
                )
            )
        else:
            cash_required = short_put.strike * 100
            max_contracts = max(1, math.floor((account_value * 0.05) / cash_required))
            ideas.append(
                TradeIdea(
                    rank_score=candidate.score,
                    symbol=candidate.symbol,
                    strategy="Cash-secured put",
                    action=f"Sell {short_put.expiration} ${short_put.strike:g} put for ~${short_put.bid:.2f} credit.",
                    thesis=f"Potential entry on a quality portfolio/watchlist name; {', '.join(candidate.reasons[:3]) or 'setup passes trend screen'}.",
                    risk=f"Assignment cost basis about ${short_put.strike - short_put.bid:.2f}; do not sell through unexpected earnings.",
                    sizing=f"Cash required about ${cash_required:,.0f}/contract; 5% cap implies up to {max_contracts} contract(s).",
                    contract=short_put,
                    candidate=candidate,
                )
            )

    deduped: dict[tuple[str, str], TradeIdea] = {}
    for idea in ideas:
        key = (idea.symbol, idea.strategy)
        if key not in deduped or idea.rank_score > deduped[key].rank_score:
            deduped[key] = idea
    return sorted(deduped.values(), key=lambda idea: idea.rank_score, reverse=True)[:max_ideas]


def money(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"${value:,.2f}"


def pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.1f}%"


def report_contract(contract: OptionContract | None) -> str:
    if not contract:
        return "No liquid contract selected."
    delta = f"{contract.delta:.2f}" if contract.delta is not None else "n/a"
    iv = f"{contract.iv * 100:.1f}%" if contract.iv is not None and contract.iv < 3 else pct(contract.iv)
    spread = pct((contract.spread_pct or 0) * 100) if contract.spread_pct is not None else "n/a"
    return (
        f"{contract.expiration} {contract.option_type.upper()} ${contract.strike:g}; "
        f"bid/ask ${contract.bid:.2f}/${contract.ask:.2f}; delta {delta}; "
        f"IV {iv}; OI {contract.open_interest}; vol {contract.volume}; spread {spread}"
    )


def build_report(
    today: date,
    holdings: list[Holding],
    watchlist: list[WatchlistEntry],
    shorts: list[ShortPremiumPosition],
    candidates: list[Candidate],
    ideas: list[TradeIdea],
    vix: float | None,
    spy: MarketSnapshot | None,
    vix_regime: str,
    vix_guidance: str,
) -> str:
    account_value = portfolio_value(holdings)
    tech_weight = sum((h.weight_pct or 0) for h in holdings if SECTOR_MAP.get(h.symbol) == "Technology")
    top_holdings = sorted(holdings, key=lambda h: h.weight_pct or 0, reverse=True)[:5]
    top_watch = sorted(watchlist, key=lambda w: w.score or 0, reverse=True)[:5]
    excluded_earnings = [c for c in candidates if c.earnings_date]

    lines: list[str] = []
    lines.append(f"# Trade Idea Generator — {today.isoformat()}")
    lines.append("")
    lines.append("> Generated from `context/portfolio-details.md`, `context/options-positions.md`, and `context/watchlist.md`.")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"- Portfolio value used for sizing: **${account_value:,.0f}**.")
    lines.append(f"- VIX: **{vix:.2f} ({vix_regime})** — {vix_guidance}" if vix is not None else f"- VIX: **{vix_regime}** — {vix_guidance}")
    if spy:
        lines.append(f"- SPY: **{money(spy.price)}**, day change **{pct(spy.change_pct)}**, 20-day return **{pct(spy.return_20d_pct)}**.")
    lines.append(f"- Technology exposure estimate from mapped holdings: **{tech_weight:.1f}%**; prefer defined-risk adds for incremental tech exposure.")
    lines.append("- Financial calculation disclaimer: these are trade candidates for review, not personalized investment advice or an order ticket.")
    lines.append("")
    lines.append("## Top Trade Ideas")
    lines.append("")
    if not ideas:
        lines.append("No actionable ideas passed the current filters. Re-run during market hours or loosen liquidity/earnings constraints.")
    for idx, idea in enumerate(ideas, 1):
        candidate = idea.candidate
        price = candidate.market.price if candidate else None
        score = candidate.score if candidate else idea.rank_score
        lines.append(f"### {idx}. {idea.symbol} — {idea.strategy}")
        lines.append("")
        lines.append(f"- **Action:** {idea.action}")
        lines.append(f"- **Underlying:** {money(price)}; setup score **{score:.1f}**.")
        lines.append(f"- **Contract:** {report_contract(idea.contract)}")
        if idea.hedge_contract:
            lines.append(f"- **Long leg:** {report_contract(idea.hedge_contract)}")
        lines.append(f"- **Thesis:** {idea.thesis}")
        lines.append(f"- **Risk:** {idea.risk}")
        lines.append(f"- **Sizing:** {idea.sizing}")
        if candidate and candidate.cautions:
            lines.append(f"- **Cautions:** {'; '.join(candidate.cautions[:4])}.")
        lines.append("")
    lines.append("## Portfolio Context")
    lines.append("")
    lines.append("| Symbol | Weight | P&L % | Sector | Note |")
    lines.append("|---|---:|---:|---|---|")
    for h in top_holdings:
        note = "overlay/trim candidate" if (h.weight_pct or 0) >= 10 else "core holding"
        lines.append(f"| {h.symbol} | {pct(h.weight_pct)} | {pct(h.pnl_pct)} | {SECTOR_MAP.get(h.symbol, 'Unknown')} | {note} |")
    lines.append("")
    lines.append("## Watchlist Inputs")
    lines.append("")
    lines.append("| Ticker | Score | Grade | Status |")
    lines.append("|---|---:|---|---|")
    for w in top_watch:
        lines.append(f"| {w.symbol} | {w.score if w.score is not None else 'n/a'} | {w.grade or 'n/a'} | {w.status} |")
    lines.append("")
    lines.append("## Open Short Premium")
    lines.append("")
    if shorts:
        lines.append("| Ticker | Strike | Expiration | Credit | Current | Contracts | Status |")
        lines.append("|---|---:|---|---:|---:|---:|---|")
        for pos in shorts:
            status = "profit-taking zone" if pos.current <= pos.credit * 0.5 else "defensive/monitor" if pos.current >= pos.credit * 1.5 else "hold zone"
            lines.append(
                f"| {pos.ticker} | ${pos.strike:g} {pos.option_type} | {pos.expiration} | ${pos.credit:.2f} | ${pos.current:.2f} | {pos.contracts} | {status} |"
            )
    else:
        lines.append("No open short-premium positions found in context.")
    lines.append("")
    lines.append("## Earnings / Avoid List")
    lines.append("")
    if excluded_earnings:
        lines.append("| Ticker | Earnings date | Reason |")
        lines.append("|---|---|---|")
        for c in excluded_earnings:
            lines.append(f"| {c.symbol} | {c.earnings_date} | Avoid fresh short premium through event window |")
    else:
        lines.append("No evaluated ticker had an FMP earnings date inside the 45-day option window.")
    lines.append("")
    lines.append("## Method")
    lines.append("")
    lines.append(
        "Scoring blends trend (price vs 50/200-day averages), RSI, 20-day return, watchlist grade, portfolio concentration, existing short-premium exposure, and earnings proximity. "
        "Options candidates target 25-60 DTE, roughly 0.20-0.30 delta, and basic liquidity filters."
    )
    lines.append("")
    lines.append("**Risk protocol:** close short premium at ~50% profit, stop/adjust near 200% of credit, avoid unplanned earnings exposure, and keep sizing within Altamira risk limits.")
    lines.append("")
    lines.append("*This report is informational and educational. It is not financial, investment, tax, or legal advice.*")
    lines.append("")
    return "\n".join(lines)


def build_telegram_message(today: date, ideas: list[TradeIdea], vix: float | None, vix_regime: str, report_path: Path) -> str:
    lines = [f"Altamira Trade Ideas - {today.isoformat()}"]
    if vix is not None:
        lines.append(f"VIX {vix:.2f} ({vix_regime})")
    else:
        lines.append(f"VIX regime: {vix_regime}")
    lines.append("")
    if not ideas:
        lines.append("No actionable ideas passed today's filters.")
    for idx, idea in enumerate(ideas[:5], 1):
        contract_line = ""
        if idea.contract:
            contract_line = f" | {idea.contract.expiration} ${idea.contract.strike:g} {idea.contract.option_type}"
            if idea.hedge_contract:
                contract_line += f"/${idea.hedge_contract.strike:g}"
        lines.append(f"{idx}) {idea.symbol} - {idea.strategy}{contract_line}")
        lines.append(f"   {idea.action}")
        if idea.candidate and idea.candidate.cautions:
            lines.append(f"   Watch: {idea.candidate.cautions[0]}")
    lines.append("")
    lines.append(f"Report: {report_path.as_posix()}")
    lines.append("Review before trading. Not financial advice.")
    return "\n".join(lines)


def send_telegram(message: str, chat_id: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    chunks = textwrap.wrap(message, width=3800, replace_whitespace=False, drop_whitespace=False)
    if not chunks:
        chunks = [message]
    for idx, chunk in enumerate(chunks, 1):
        payload = {"chat_id": chat_id, "text": chunk, "disable_web_page_preview": "true"}
        result = post_form(url, payload)
        if not result.get("ok"):
            raise RuntimeError(f"Telegram send failed for chunk {idx}: {result}")


def main() -> int:
    args = parse_args()
    today = datetime.now(timezone.utc).date()
    output_path = Path(args.out) if args.out else OUTPUTS_DIR / f"trade-idea-generator-{today.isoformat()}.md"
    if not output_path.is_absolute():
        output_path = ROOT / output_path

    holdings = parse_portfolio(CONTEXT_DIR / "portfolio-details.md")
    watchlist = parse_watchlist(CONTEXT_DIR / "watchlist.md")
    shorts = parse_short_premium(CONTEXT_DIR / "options-positions.md")
    symbols = build_universe(holdings, watchlist, args.max_tickers)
    if not symbols:
        raise SystemExit("No portfolio/watchlist symbols found.")

    key = fmp_key()
    if not key:
        raise SystemExit("FMP_API_KEY is required (environment preferred).")
    quotes = fetch_quotes(sorted(set(symbols + ["^VIX", "SPY"])), key)

    for symbol in symbols:
        if symbol in quotes:
            rsi, ret20 = fetch_historical_indicators(symbol, key, today)
            quotes[symbol].rsi14 = rsi
            quotes[symbol].return_20d_pct = ret20
    if "SPY" in quotes and quotes["SPY"].return_20d_pct is None:
        rsi, ret20 = fetch_historical_indicators("SPY", key, today)
        quotes["SPY"].rsi14 = rsi
        quotes["SPY"].return_20d_pct = ret20

    earnings = fetch_earnings(symbols, key, today)
    holding_map = {h.symbol: h for h in holdings}
    watch_map = {w.symbol: w for w in watchlist}
    short_symbols = {s.ticker for s in shorts}

    candidates: list[Candidate] = []
    for symbol in symbols:
        market = quotes.get(symbol)
        if not market or market.price is None:
            continue
        source_parts = []
        if symbol in holding_map:
            source_parts.append("portfolio")
        if symbol in watch_map:
            source_parts.append("watchlist")
        candidate = Candidate(
            symbol=symbol,
            source="+".join(source_parts) or "universe",
            sector=SECTOR_MAP.get(symbol, "Unknown"),
            market=market,
            holding=holding_map.get(symbol),
            watchlist=watch_map.get(symbol),
            has_open_short_premium=symbol in short_symbols,
            earnings_date=earnings.get(symbol),
        )
        score_candidate(candidate)
        candidates.append(candidate)

    vix_snapshot = quotes.get("^VIX") or quotes.get("VIX")
    vix = vix_snapshot.price if vix_snapshot else None
    vix_regime, vix_guidance = classify_vix(vix)
    ideas = make_trade_ideas(candidates, massive_key(), today, portfolio_value(holdings), args.max_ideas, vix_regime)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    report = build_report(today, holdings, watchlist, shorts, candidates, ideas, vix, quotes.get("SPY"), vix_regime, vix_guidance)
    output_path.write_text(report, encoding="utf-8")

    telegram_message = build_telegram_message(today, ideas, vix, vix_regime, output_path.relative_to(ROOT))
    chat_id = args.chat_id or fallback_chat_id()
    should_send = args.send_telegram and not args.no_telegram
    if should_send:
        if not chat_id:
            raise SystemExit("Telegram send requested but no chat ID is configured.")
        send_telegram(telegram_message, chat_id)
        print(f"Telegram sent to {chat_id}.")
    else:
        print("Telegram not sent.")
    print(f"Report written: {output_path.relative_to(ROOT)}")
    print("\n" + telegram_message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
