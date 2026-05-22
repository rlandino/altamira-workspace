#!/usr/bin/env python3
"""Generate daily trade ideas from the current portfolio and watchlist.

The script reads `context/portfolio-details.md` and `context/watchlist.md`,
enriches the universe with FMP market data, optionally pulls Massive.com
options snapshots, writes a markdown report, and can send a concise version to
Telegram.
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
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python 3.8 fallback
    ZoneInfo = None  # type: ignore[assignment]


WORKSPACE = Path(__file__).resolve().parents[1]
CONTEXT = WORKSPACE / "context"
OUTPUTS = WORKSPACE / "outputs"
PORTFOLIO_PATH = CONTEXT / "portfolio-details.md"
WATCHLIST_PATH = CONTEXT / "watchlist.md"

FMP_BASE = "https://financialmodelingprep.com/api/v3"
MASSIVE_BASE = "https://api.massive.com/v3"
DEFAULT_TELEGRAM_CHAT_ID = "7830722515"


@dataclass
class Position:
    """Current portfolio position parsed from context."""

    symbol: str
    qty: float
    avg_price: float | None
    current: float | None
    market_value: float | None
    cost_basis: float | None
    weight: float | None


@dataclass
class WatchlistEntry:
    """Watchlist row parsed from context."""

    symbol: str
    score: float | None
    grade: str | None
    company: str
    status: str


@dataclass
class OptionCandidate:
    """Best matching option contract for an idea."""

    symbol: str
    contract_type: str
    strike: float
    expiration: str
    dte: int
    bid: float
    ask: float
    delta: float | None
    open_interest: int
    volume: int
    iv: float | None
    annualized_yield: float | None


@dataclass
class SymbolSnapshot:
    """Market and technical data for a symbol."""

    symbol: str
    price: float | None = None
    change_pct: float | None = None
    volume: int | None = None
    avg_volume: int | None = None
    market_cap: float | None = None
    price_avg_50: float | None = None
    price_avg_200: float | None = None
    year_high: float | None = None
    year_low: float | None = None
    pe: float | None = None
    sma_20: float | None = None
    sma_50: float | None = None
    rsi_14: float | None = None
    earnings_date: str | None = None
    earnings_days: int | None = None
    quote_error: str | None = None


@dataclass
class TradeIdea:
    """Generated trade idea."""

    rank: int
    strategy: str
    symbol: str
    action: str
    score: float
    rationale: list[str]
    risk_notes: list[str]
    option: OptionCandidate | None = None
    snapshot: SymbolSnapshot | None = None
    position: Position | None = None
    watchlist: WatchlistEntry | None = None
    management: list[str] = field(default_factory=list)


def money_to_float(value: str) -> float | None:
    """Convert a markdown currency/number cell to float."""

    cleaned = value.replace("$", "").replace(",", "").strip()
    cleaned = cleaned.replace("**", "")
    if not cleaned or cleaned in {"-", "—", "N/A"}:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    return float(match.group(0)) if match else None


def pct_to_float(value: str) -> float | None:
    """Convert a percent cell to float percentage points."""

    cleaned = value.replace("**", "").strip()
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    return float(match.group(0)) if match else None


def split_markdown_row(line: str) -> list[str]:
    """Split a markdown table row into stripped cells."""

    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_portfolio(path: Path = PORTFOLIO_PATH) -> tuple[dict[str, Position], float | None]:
    """Parse current equity positions and total market value."""

    if not path.exists():
        raise FileNotFoundError(f"Portfolio context not found: {path}")

    text = path.read_text(encoding="utf-8")
    total_match = re.search(r"Totals:\*\* MKT VALUE \$([\d,]+)", text)
    total_value = money_to_float(total_match.group(1)) if total_match else None

    positions: dict[str, Position] = {}
    in_positions = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("| SYMBOL |"):
            in_positions = True
            continue
        if in_positions and (not line or line.startswith("**Totals:**")):
            break
        if not in_positions or not line.startswith("|"):
            continue
        if set(line.replace("|", "").strip()) <= {"-"}:
            continue

        cells = split_markdown_row(line)
        if len(cells) < 9 or cells[0].upper() == "SYMBOL":
            continue
        symbol = cells[0].upper()
        qty = money_to_float(cells[1]) or 0.0
        positions[symbol] = Position(
            symbol=symbol,
            qty=qty,
            avg_price=money_to_float(cells[2]),
            current=money_to_float(cells[3]),
            market_value=money_to_float(cells[4]),
            cost_basis=money_to_float(cells[5]),
            weight=pct_to_float(cells[8]),
        )
    return positions, total_value


def parse_watchlist(path: Path = WATCHLIST_PATH) -> dict[str, WatchlistEntry]:
    """Parse the watchlist markdown table."""

    if not path.exists():
        raise FileNotFoundError(f"Watchlist context not found: {path}")

    entries: dict[str, WatchlistEntry] = {}
    in_table = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("| Ticker |"):
            in_table = True
            continue
        if in_table and (not line or line == "---"):
            break
        if not in_table or not line.startswith("|"):
            continue
        if set(line.replace("|", "").strip()) <= {"-"}:
            continue

        cells = split_markdown_row(line)
        if len(cells) < 5:
            continue
        symbol = cells[0].upper()
        score = money_to_float(cells[1])
        grade = cells[2].replace("*", "").strip() or None
        entries[symbol] = WatchlistEntry(
            symbol=symbol,
            score=score,
            grade=grade,
            company=cells[3],
            status=cells[4],
        )
    return entries


def get_et_now() -> datetime:
    """Return current time in America/New_York when zoneinfo is available."""

    if ZoneInfo is None:
        return datetime.now(timezone.utc)
    return datetime.now(ZoneInfo("America/New_York"))


def fetch_json(url: str, timeout: int = 15, retries: int = 2) -> Any:
    """Fetch JSON with light retry handling."""

    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "altamira-trade-idea-generator/1.0"},
            )
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(0.75 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch JSON: {last_error}")


def require_fmp_key() -> str:
    """Read the FMP API key from the environment."""

    key = os.environ.get("FMP_API_KEY")
    if not key:
        raise RuntimeError("FMP_API_KEY is required to generate live trade ideas.")
    return key


def get_massive_key() -> str | None:
    """Read the Massive.com API key from the environment if available."""

    return os.environ.get("MASSIVE_API_KEY")


def fmp_url(endpoint: str, api_key: str, params: dict[str, str] | None = None) -> str:
    """Build an FMP URL."""

    query = {"apikey": api_key}
    if params:
        query.update(params)
    return f"{FMP_BASE}/{endpoint}?{urllib.parse.urlencode(query)}"


def chunked(items: list[str], size: int) -> list[list[str]]:
    """Split items into chunks."""

    return [items[i : i + size] for i in range(0, len(items), size)]


def fetch_quotes(symbols: list[str], api_key: str) -> dict[str, SymbolSnapshot]:
    """Fetch FMP batch quotes."""

    snapshots: dict[str, SymbolSnapshot] = {s: SymbolSnapshot(symbol=s) for s in symbols}
    for group in chunked(symbols, 30):
        endpoint = "quote/" + ",".join(group)
        try:
            data = fetch_json(fmp_url(endpoint, api_key))
        except RuntimeError as exc:
            for symbol in group:
                snapshots[symbol].quote_error = str(exc)
            continue
        rows = data if isinstance(data, list) else [data]
        for row in rows:
            if not isinstance(row, dict) or not row.get("symbol"):
                continue
            symbol = str(row["symbol"]).upper()
            snap = snapshots.setdefault(symbol, SymbolSnapshot(symbol=symbol))
            snap.price = as_float(row.get("price"))
            snap.change_pct = as_float(row.get("changesPercentage"))
            snap.volume = as_int(row.get("volume"))
            snap.avg_volume = as_int(row.get("avgVolume"))
            snap.market_cap = as_float(row.get("marketCap"))
            snap.price_avg_50 = as_float(row.get("priceAvg50"))
            snap.price_avg_200 = as_float(row.get("priceAvg200"))
            snap.year_high = as_float(row.get("yearHigh"))
            snap.year_low = as_float(row.get("yearLow"))
            snap.pe = as_float(row.get("pe"))
    return snapshots


def as_float(value: Any) -> float | None:
    """Safely coerce a value to float."""

    if value is None or value == "":
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(result) or math.isinf(result):
        return None
    return result


def as_int(value: Any) -> int | None:
    """Safely coerce a value to int."""

    number = as_float(value)
    return int(number) if number is not None else None


def fetch_historical(symbol: str, api_key: str, days: int = 90) -> list[dict[str, Any]]:
    """Fetch recent historical prices from FMP."""

    endpoint = f"historical-price-full/{symbol}"
    try:
        data = fetch_json(fmp_url(endpoint, api_key, {"timeseries": str(days)}), timeout=12, retries=1)
    except RuntimeError:
        return []
    historical = data.get("historical", []) if isinstance(data, dict) else []
    return historical if isinstance(historical, list) else []


def compute_rsi(closes_chronological: list[float], period: int = 14) -> float | None:
    """Compute a simple RSI from chronological closes."""

    if len(closes_chronological) <= period:
        return None
    gains: list[float] = []
    losses: list[float] = []
    for previous, current in zip(closes_chronological[:-1], closes_chronological[1:]):
        change = current - previous
        gains.append(max(change, 0.0))
        losses.append(abs(min(change, 0.0)))
    recent_gains = gains[-period:]
    recent_losses = losses[-period:]
    avg_gain = sum(recent_gains) / period
    avg_loss = sum(recent_losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def enrich_technicals(snapshots: dict[str, SymbolSnapshot], api_key: str) -> None:
    """Attach SMA/RSI technicals to snapshots."""

    for symbol, snap in snapshots.items():
        history = fetch_historical(symbol, api_key)
        closes_latest_first = [as_float(row.get("close")) for row in history if isinstance(row, dict)]
        closes = [close for close in closes_latest_first if close is not None]
        if closes:
            snap.sma_20 = sum(closes[:20]) / min(20, len(closes)) if len(closes) >= 5 else None
            snap.sma_50 = sum(closes[:50]) / min(50, len(closes)) if len(closes) >= 20 else None
            snap.rsi_14 = compute_rsi(list(reversed(closes)), 14)


def fetch_earnings(symbols: set[str], api_key: str, today: date, days: int = 45) -> dict[str, tuple[str, int]]:
    """Fetch upcoming earnings dates for symbols."""

    end = today + timedelta(days=days)
    try:
        data = fetch_json(
            fmp_url(
                "earning_calendar",
                api_key,
                {"from": today.isoformat(), "to": end.isoformat()},
            ),
            timeout=15,
            retries=1,
        )
    except RuntimeError:
        return {}
    rows = data if isinstance(data, list) else []
    earnings: dict[str, tuple[str, int]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        symbol = str(row.get("symbol", "")).upper()
        if symbol not in symbols:
            continue
        date_str = row.get("date")
        if not date_str:
            continue
        try:
            event_date = datetime.strptime(str(date_str)[:10], "%Y-%m-%d").date()
        except ValueError:
            continue
        earnings[symbol] = (event_date.isoformat(), (event_date - today).days)
    return earnings


def massive_url(symbol: str, api_key: str, contract_type: str, today: date) -> str:
    """Build a Massive.com snapshot URL for 20-60 DTE contracts."""

    params = {
        "apiKey": api_key,
        "contract_type": contract_type,
        "expiration_date.gte": (today + timedelta(days=20)).isoformat(),
        "expiration_date.lte": (today + timedelta(days=60)).isoformat(),
        "limit": "250",
        "sort": "expiration_date",
        "order": "asc",
    }
    return f"{MASSIVE_BASE}/snapshot/options/{symbol}?{urllib.parse.urlencode(params)}"


def parse_option(row: dict[str, Any], spot_price: float, contract_type: str, today: date) -> OptionCandidate | None:
    """Normalize a Massive.com options snapshot row."""

    details = row.get("details") or {}
    quote = row.get("last_quote") or {}
    greeks = row.get("greeks") or {}
    day = row.get("day") or {}

    expiration = details.get("expiration_date")
    strike = as_float(details.get("strike_price"))
    bid = as_float(quote.get("bid"))
    ask = as_float(quote.get("ask"))
    if not expiration or strike is None or bid is None or ask is None or bid <= 0 or ask < bid:
        return None
    try:
        exp_date = datetime.strptime(str(expiration), "%Y-%m-%d").date()
    except ValueError:
        return None
    dte = (exp_date - today).days
    if dte <= 0:
        return None

    annualized_yield = None
    denominator = strike if contract_type == "put" else spot_price
    if denominator > 0:
        annualized_yield = (bid / denominator) * (365 / dte) * 100

    return OptionCandidate(
        symbol=str(details.get("ticker", "")),
        contract_type=contract_type,
        strike=strike,
        expiration=str(expiration),
        dte=dte,
        bid=bid,
        ask=ask,
        delta=as_float(greeks.get("delta")),
        open_interest=as_int(row.get("open_interest")) or 0,
        volume=as_int(day.get("volume")) or 0,
        iv=as_float(row.get("implied_volatility")),
        annualized_yield=annualized_yield,
    )


def find_option_candidate(
    symbol: str,
    spot_price: float | None,
    contract_type: str,
    today: date,
    target_delta: float = 0.25,
) -> OptionCandidate | None:
    """Find the best liquid 20-60 DTE contract near the target delta."""

    api_key = get_massive_key()
    if not api_key or spot_price is None:
        return None
    try:
        data = fetch_json(massive_url(symbol, api_key, contract_type, today), timeout=15, retries=1)
    except RuntimeError:
        return None

    results = data.get("results", []) if isinstance(data, dict) else []
    candidates: list[OptionCandidate] = []
    for row in results:
        if not isinstance(row, dict):
            continue
        option = parse_option(row, spot_price, contract_type, today)
        if option is None:
            continue
        if option.dte < 25 or option.dte > 55:
            continue
        if option.open_interest < 25:
            continue
        spread = option.ask - option.bid
        mid = (option.ask + option.bid) / 2
        if mid <= 0 or spread / mid > 0.25:
            continue
        if option.delta is not None:
            abs_delta = abs(option.delta)
            if abs_delta < 0.12 or abs_delta > 0.35:
                continue
        candidates.append(option)

    if not candidates:
        return None

    def score(option: OptionCandidate) -> float:
        delta = abs(option.delta) if option.delta is not None else target_delta
        delta_score = abs(delta - target_delta) * 100
        dte_score = abs(option.dte - 35) / 5
        spread_score = ((option.ask - option.bid) / max((option.ask + option.bid) / 2, 0.01)) * 10
        liquidity_bonus = min(option.open_interest / 500, 3) + min(option.volume / 100, 2)
        yield_bonus = (option.annualized_yield or 0) / 10
        return delta_score + dte_score + spread_score - liquidity_bonus - yield_bonus

    return sorted(candidates, key=score)[0]


def trend_score(snapshot: SymbolSnapshot) -> float:
    """Score technical trend from 0-30."""

    score = 0.0
    price = snapshot.price
    sma_20 = snapshot.sma_20 or snapshot.price_avg_50
    sma_50 = snapshot.sma_50 or snapshot.price_avg_50
    if price and sma_20 and price >= sma_20:
        score += 10
    if price and sma_50 and price >= sma_50:
        score += 10
    if snapshot.rsi_14 is not None:
        if 40 <= snapshot.rsi_14 <= 65:
            score += 8
        elif 30 <= snapshot.rsi_14 < 40 or 65 < snapshot.rsi_14 <= 72:
            score += 4
    if snapshot.change_pct is not None and -2 <= snapshot.change_pct <= 2.5:
        score += 2
    return min(score, 30)


def quality_score(watchlist: WatchlistEntry | None, position: Position | None) -> float:
    """Score symbol quality/fit from 0-35."""

    if watchlist and watchlist.score is not None:
        return min(max(watchlist.score / 2, 0), 35)
    if position and position.weight is not None:
        return 22 if position.weight >= 2 else 16
    return 12


def earnings_penalty(snapshot: SymbolSnapshot) -> float:
    """Return penalty for upcoming earnings proximity."""

    if snapshot.earnings_days is None:
        return 0
    if snapshot.earnings_days <= 10:
        return 40
    if snapshot.earnings_days <= 21:
        return 15
    if snapshot.earnings_days <= 45:
        return 5
    return 0


def generate_ideas(
    positions: dict[str, Position],
    watchlist: dict[str, WatchlistEntry],
    snapshots: dict[str, SymbolSnapshot],
    today: date,
    max_ideas: int,
) -> list[TradeIdea]:
    """Generate and rank trade ideas."""

    ideas: list[TradeIdea] = []

    # Covered call candidates for existing positions with at least 100 shares.
    for symbol, position in positions.items():
        snapshot = snapshots.get(symbol)
        if not snapshot or snapshot.price is None or position.qty < 100:
            continue
        if position.avg_price and snapshot.price < position.avg_price:
            continue

        call = find_option_candidate(symbol, snapshot.price, "call", today)
        option_score = 0.0
        if call and call.annualized_yield is not None:
            option_score = min(call.annualized_yield, 25)
        weight_bonus = min((position.weight or 0) * 1.2, 18)
        rsi_bonus = 8 if snapshot.rsi_14 and snapshot.rsi_14 > 65 else 0
        score = 35 + weight_bonus + rsi_bonus + option_score - earnings_penalty(snapshot)
        if score < 45:
            continue

        rationale = [
            f"Existing {position.qty:.0f}-share position; eligible to overwrite in 100-share lots.",
            f"Portfolio weight is {format_pct(position.weight)}; covered calls can monetize concentration.",
        ]
        if snapshot.rsi_14 is not None:
            rationale.append(f"RSI is {snapshot.rsi_14:.1f}, useful context for call overwrite timing.")
        risk_notes = []
        if snapshot.earnings_date:
            risk_notes.append(f"Earnings on {snapshot.earnings_date}; avoid expirations that intentionally carry event risk.")
        if call is None:
            risk_notes.append("No liquid option snapshot found; use manual chain lookup for a 0.20-0.30 delta call.")
        ideas.append(
            TradeIdea(
                rank=0,
                strategy="Covered Call",
                symbol=symbol,
                action="Sell call against existing shares",
                score=score,
                rationale=rationale,
                risk_notes=risk_notes,
                option=call,
                snapshot=snapshot,
                position=position,
                watchlist=watchlist.get(symbol),
                management=[
                    "Target 50% profit capture.",
                    "Roll up/out if short call is threatened and thesis remains intact.",
                ],
            )
        )

    # Cash-secured put candidates from watchlist and selected existing holdings.
    csp_symbols = set(watchlist) | {s for s, p in positions.items() if (p.weight or 0) < 5}
    for symbol in sorted(csp_symbols):
        snapshot = snapshots.get(symbol)
        if not snapshot or snapshot.price is None:
            continue
        watch = watchlist.get(symbol)
        position = positions.get(symbol)
        if snapshot.earnings_days is not None and snapshot.earnings_days <= 21:
            continue
        if snapshot.rsi_14 is not None and snapshot.rsi_14 > 75:
            continue

        put = find_option_candidate(symbol, snapshot.price, "put", today)
        option_score = 0.0
        if put and put.annualized_yield is not None:
            option_score = min(put.annualized_yield * 1.1, 30)
        score = quality_score(watch, position) + trend_score(snapshot) + option_score - earnings_penalty(snapshot)
        if watch and "Avoid" in watch.status:
            score -= 20
        if score < 40:
            continue

        rationale = []
        if watch:
            rationale.append(f"Watchlist grade {watch.grade or 'N/A'} with score {format_number(watch.score)} ({watch.status}).")
        if snapshot.sma_50 and snapshot.price:
            direction = "above" if snapshot.price >= snapshot.sma_50 else "below"
            rationale.append(f"Price ${snapshot.price:.2f} is {direction} 50-day SMA ${snapshot.sma_50:.2f}.")
        if snapshot.rsi_14 is not None:
            rationale.append(f"RSI is {snapshot.rsi_14:.1f}; avoids the most extended entry zones.")
        risk_notes = []
        if snapshot.earnings_date:
            risk_notes.append(f"Next earnings: {snapshot.earnings_date} ({snapshot.earnings_days} days).")
        if put is None:
            risk_notes.append("No liquid option snapshot found; use manual chain lookup for a 0.20-0.30 delta put.")
        ideas.append(
            TradeIdea(
                rank=0,
                strategy="Cash-Secured Put",
                symbol=symbol,
                action="Sell put only if willing to own shares at breakeven",
                score=score,
                rationale=rationale,
                risk_notes=risk_notes,
                option=put,
                snapshot=snapshot,
                position=position,
                watchlist=watch,
                management=[
                    "Size within 5% max position risk and keep total short-premium exposure under 30%.",
                    "Close at 50% max profit; stop or roll near 200% of credit.",
                ],
            )
        )

    # Equity add candidates for top watchlist names when options are unavailable or unattractive.
    for symbol, watch in watchlist.items():
        snapshot = snapshots.get(symbol)
        if not snapshot or snapshot.price is None or watch.score is None or watch.score < 58:
            continue
        if snapshot.earnings_days is not None and snapshot.earnings_days <= 10:
            continue
        score = quality_score(watch, positions.get(symbol)) + trend_score(snapshot) - earnings_penalty(snapshot)
        if score < 48:
            continue
        rationale = [
            f"Top watchlist candidate: {watch.company} ({watch.grade}, score {watch.score:.1f}).",
            "Use staged entry or put-selling as the preferred lower-basis implementation.",
        ]
        if snapshot.sma_20 and snapshot.price:
            rationale.append(f"Price ${snapshot.price:.2f} vs 20-day SMA ${snapshot.sma_20:.2f}.")
        ideas.append(
            TradeIdea(
                rank=0,
                strategy="Staged Equity Entry",
                symbol=symbol,
                action="Buy starter tranche or set limit near 20-day SMA",
                score=score,
                rationale=rationale,
                risk_notes=["Equity entries carry full downside; prefer tranche sizing."],
                snapshot=snapshot,
                position=positions.get(symbol),
                watchlist=watch,
                management=[
                    "Start small; add only after confirmation or a controlled pullback.",
                    "Reassess if price loses the 50-day SMA on volume.",
                ],
            )
        )

    ideas.sort(key=lambda item: item.score, reverse=True)
    selected: list[TradeIdea] = []
    seen_strategy_symbol: set[tuple[str, str]] = set()
    for idea in ideas:
        key = (idea.strategy, idea.symbol)
        if key in seen_strategy_symbol:
            continue
        if any(existing.symbol == idea.symbol and existing.strategy == idea.strategy for existing in selected):
            continue
        idea.rank = len(selected) + 1
        selected.append(idea)
        seen_strategy_symbol.add(key)
        if len(selected) >= max_ideas:
            break
    return selected


def format_number(value: float | None, decimals: int = 1) -> str:
    """Format a nullable number."""

    return f"{value:.{decimals}f}" if value is not None else "N/A"


def format_pct(value: float | None) -> str:
    """Format a nullable percent value."""

    return f"{value:.1f}%" if value is not None else "N/A"


def format_money(value: float | None) -> str:
    """Format a nullable dollar amount."""

    if value is None:
        return "N/A"
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:.2f}"


def option_line(option: OptionCandidate | None, fallback_price: float | None, strategy: str) -> str:
    """Format option contract details."""

    if option is None:
        if fallback_price is None:
            return "Contract: manual chain lookup required"
        if strategy == "Cash-Secured Put":
            target = fallback_price * 0.92
            return f"Contract: target 25-45 DTE put around ${target:.0f} strike / 0.20-0.30 delta"
        target = fallback_price * 1.07
        return f"Contract: target 25-45 DTE call around ${target:.0f} strike / 0.20-0.30 delta"
    ticker = option.symbol or ""
    delta = f"{option.delta:.2f}" if option.delta is not None else "N/A"
    annual = f"{option.annualized_yield:.1f}%" if option.annualized_yield is not None else "N/A"
    return (
        f"Contract: {ticker} {option.expiration} ${option.strike:g} "
        f"{option.contract_type.upper()} @ bid ${option.bid:.2f} "
        f"(delta {delta}, DTE {option.dte}, OI {option.open_interest}, ann. yield {annual})"
    )


def build_report(
    ideas: list[TradeIdea],
    positions: dict[str, Position],
    watchlist: dict[str, WatchlistEntry],
    snapshots: dict[str, SymbolSnapshot],
    portfolio_value: float | None,
    as_of: datetime,
) -> str:
    """Build the markdown report."""

    vix = snapshots.get("^VIX") or snapshots.get("VIX")
    spy = snapshots.get("SPY")
    lines = [
        f"# Trade Idea Generator - {as_of.date().isoformat()}",
        "",
        "> Educational trade planning output. Not financial advice. Verify quotes, liquidity, and portfolio risk before placing trades.",
        "",
        "## Market Context",
        "",
        f"- **As of:** {as_of.strftime('%Y-%m-%d %H:%M %Z')}",
        f"- **Portfolio value:** {format_money(portfolio_value)}",
        f"- **Universe:** {len(positions)} current positions + {len(watchlist)} watchlist names",
        f"- **SPY:** {format_money(spy.price if spy else None)} ({format_pct(spy.change_pct if spy else None)} today)",
        f"- **VIX:** {format_number(vix.price if vix else None)}",
        "",
        "## Top Trade Ideas",
        "",
    ]

    if not ideas:
        lines.extend(
            [
                "No qualifying ideas passed the quality, trend, liquidity, and earnings filters today.",
                "",
            ]
        )
    for idea in ideas:
        snap = idea.snapshot or SymbolSnapshot(symbol=idea.symbol)
        lines.extend(
            [
                f"### {idea.rank}. {idea.strategy}: {idea.symbol}",
                "",
                f"- **Action:** {idea.action}",
                f"- **Score:** {idea.score:.1f}",
                f"- **Price:** {format_money(snap.price)} | **Day change:** {format_pct(snap.change_pct)} | **RSI:** {format_number(snap.rsi_14)}",
                f"- **{option_line(idea.option, snap.price, idea.strategy)}",
                "- **Rationale:**",
            ]
        )
        for point in idea.rationale:
            lines.append(f"  - {point}")
        if idea.management:
            lines.append("- **Management:**")
            for point in idea.management:
                lines.append(f"  - {point}")
        if idea.risk_notes:
            lines.append("- **Risk notes:**")
            for point in idea.risk_notes:
                lines.append(f"  - {point}")
        lines.append("")

    excluded = [
        s
        for s in sorted(snapshots)
        if snapshots[s].earnings_days is not None and snapshots[s].earnings_days <= 21
    ]
    if excluded:
        lines.extend(["## Earnings Watch", ""])
        for symbol in excluded[:20]:
            snap = snapshots[symbol]
            lines.append(f"- {symbol}: {snap.earnings_date} ({snap.earnings_days} days)")
        lines.append("")

    lines.extend(
        [
            "## Process Notes",
            "",
            "- Inputs: `context/portfolio-details.md` and `context/watchlist.md`.",
            "- Market data: FMP quotes, historical prices, and earnings calendar.",
            "- Options data: Massive.com snapshots when `MASSIVE_API_KEY` is configured.",
            "- Filters favor 25-55 DTE, liquid contracts, 0.20-0.30 delta, no near-term earnings, and existing Altamira sizing rules.",
            "",
        ]
    )
    return "\n".join(lines)


def build_telegram_message(
    ideas: list[TradeIdea],
    snapshots: dict[str, SymbolSnapshot],
    portfolio_value: float | None,
    as_of: datetime,
) -> str:
    """Build a concise Telegram-safe message."""

    vix = snapshots.get("^VIX") or snapshots.get("VIX")
    spy = snapshots.get("SPY")
    lines = [
        f"TRADE IDEA GENERATOR - {as_of.date().isoformat()}",
        f"SPY {format_money(spy.price if spy else None)} ({format_pct(spy.change_pct if spy else None)}) | VIX {format_number(vix.price if vix else None)}",
        f"Portfolio: {format_money(portfolio_value)}",
        "",
    ]
    if not ideas:
        lines.append("No qualifying trade ideas passed today's filters.")
    for idea in ideas:
        snap = idea.snapshot or SymbolSnapshot(symbol=idea.symbol)
        lines.extend(
            [
                f"{idea.rank}) {idea.strategy.upper()} - {idea.symbol} (score {idea.score:.1f})",
                option_line(idea.option, snap.price, idea.strategy),
                f"Why: {'; '.join(idea.rationale[:2])}",
            ]
        )
        if idea.risk_notes:
            lines.append(f"Risk: {'; '.join(idea.risk_notes[:2])}")
        lines.append("")
    lines.extend(
        [
            "Rules: verify live quotes/liquidity; keep max position <=5%; total options <=30%; close at 50% profit or manage at 200% credit.",
            "Not financial advice.",
        ]
    )
    message = "\n".join(lines)
    if len(message) > 3900:
        return message[:3850] + "\n\n...truncated; see markdown report."
    return message


def send_telegram(message: str, chat_id: str) -> dict[str, Any]:
    """Send the message through the Telegram Bot API."""

    token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN or TELEGRAM_TOKEN is required to send Telegram alerts.")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "disable_web_page_preview": True,
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram send failed: HTTP {exc.code} {body}") from exc


def write_report(report: str, output_path: Path | None, as_of: datetime) -> Path:
    """Write the markdown report."""

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    if output_path is None:
        output_path = OUTPUTS / f"trade-idea-generator-{as_of.date().isoformat()}.md"
    output_path.write_text(report, encoding="utf-8")
    return output_path


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--portfolio", type=Path, default=PORTFOLIO_PATH, help="Portfolio markdown context path")
    parser.add_argument("--watchlist", type=Path, default=WATCHLIST_PATH, help="Watchlist markdown context path")
    parser.add_argument("--output", type=Path, default=None, help="Markdown report output path")
    parser.add_argument("--max-ideas", type=int, default=5, help="Maximum number of ideas to include")
    parser.add_argument("--send-telegram", action="store_true", help="Send the generated message to Telegram")
    parser.add_argument(
        "--telegram-chat-id",
        default=os.environ.get("TELEGRAM_CHAT_ID") or DEFAULT_TELEGRAM_CHAT_ID,
        help="Telegram destination chat ID or channel handle",
    )
    parser.add_argument("--print-message", action="store_true", help="Print the Telegram message to stdout")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""

    args = parse_args(argv or sys.argv[1:])
    as_of = get_et_now()
    today = as_of.date()

    try:
        api_key = require_fmp_key()
        positions, portfolio_value = parse_portfolio(args.portfolio)
        watchlist = parse_watchlist(args.watchlist)
        universe = sorted((set(positions) | set(watchlist) | {"SPY", "^VIX"}) - {""})
        snapshots = fetch_quotes(universe, api_key)
        enrich_technicals({k: v for k, v in snapshots.items() if k != "^VIX"}, api_key)
        earnings = fetch_earnings(set(universe), api_key, today)
        for symbol, (event_date, days) in earnings.items():
            snapshots.setdefault(symbol, SymbolSnapshot(symbol=symbol))
            snapshots[symbol].earnings_date = event_date
            snapshots[symbol].earnings_days = days

        ideas = generate_ideas(positions, watchlist, snapshots, today, max(1, args.max_ideas))
        report = build_report(ideas, positions, watchlist, snapshots, portfolio_value, as_of)
        output_path = write_report(report, args.output, as_of)
        message = build_telegram_message(ideas, snapshots, portfolio_value, as_of)

        if args.print_message:
            print(message)
            print()
        print(f"Wrote report: {output_path}")
        print(f"Generated ideas: {len(ideas)}")

        if args.send_telegram:
            response = send_telegram(message, args.telegram_chat_id)
            if not response.get("ok"):
                raise RuntimeError(f"Telegram API returned non-ok response: {response}")
            result = response.get("result", {})
            print(f"Telegram sent: message_id={result.get('message_id')}")
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI should report concise failure
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
