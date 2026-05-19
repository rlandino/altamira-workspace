#!/usr/bin/env python3
"""Generate daily trade ideas from portfolio/watchlist context and optionally send Telegram."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_PATH = REPO_ROOT / "context" / "portfolio-details.md"
WATCHLIST_PATH = REPO_ROOT / "context" / "watchlist.md"
OUTPUTS_DIR = REPO_ROOT / "outputs"
FMP_BASE = "https://financialmodelingprep.com/api"
MASSIVE_BASE = "https://api.massive.com/v3"
DEFAULT_CHAT_ID = "7830722515"
MAX_TELEGRAM_CHARS = 3900


@dataclass
class Holding:
    symbol: str
    quantity: float
    average_price: Optional[float]
    current_price: Optional[float]
    market_value: Optional[float]
    weight_pct: Optional[float]


@dataclass
class WatchlistItem:
    ticker: str
    score: Optional[float]
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
class OptionContract:
    ticker: str
    contract_type: str
    strike: float
    expiration: str
    bid: float
    ask: float
    delta: Optional[float]
    implied_volatility: Optional[float]
    open_interest: int
    volume: int
    source: str

    @property
    def mid(self) -> float:
        if self.bid > 0 and self.ask > 0:
            return (self.bid + self.ask) / 2
        return max(self.bid, self.ask, 0)


@dataclass
class TradeIdea:
    strategy: str
    ticker: str
    action: str
    score: float
    rationale: str
    contract: Optional[OptionContract] = None
    dte: Optional[int] = None
    underlying_price: Optional[float] = None
    annualized_return_pct: Optional[float] = None
    breakeven: Optional[float] = None
    contracts: Optional[int] = None
    collateral_or_notional: Optional[float] = None
    premium: Optional[float] = None
    risk_notes: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate trade ideas from context/portfolio-details.md and context/watchlist.md."
    )
    parser.add_argument("--portfolio", type=Path, default=PORTFOLIO_PATH)
    parser.add_argument("--watchlist", type=Path, default=WATCHLIST_PATH)
    parser.add_argument("--out-dir", type=Path, default=OUTPUTS_DIR)
    parser.add_argument("--date", default=dt.date.today().isoformat())
    parser.add_argument("--top", type=int, default=5, help="Number of trade ideas to include.")
    parser.add_argument("--fmp-api-key", default=os.environ.get("FMP_API_KEY"))
    parser.add_argument("--massive-api-key", default=os.environ.get("MASSIVE_API_KEY"))
    parser.add_argument("--telegram-token", default=os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN"))
    parser.add_argument("--telegram-chat-id", default=os.environ.get("TELEGRAM_CHAT_ID") or DEFAULT_CHAT_ID)
    parser.add_argument("--send-telegram", action="store_true")
    parser.add_argument("--skip-options", action="store_true", help="Skip options-chain calls and generate quote-only ideas.")
    parser.add_argument("--max-workers", type=int, default=8)
    return parser.parse_args()


def parse_money(value: str) -> Optional[float]:
    cleaned = value.strip().replace("$", "").replace(",", "").replace("%", "")
    cleaned = cleaned.replace("+", "").replace("(", "").replace(")", "")
    if cleaned in {"", "-", "--", "—", "N/A"}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_markdown_table(path: Path, section_heading: str) -> List[List[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    rows: List[List[str]] = []
    in_section = False
    for line in lines:
        if line.strip().startswith("## "):
            in_section = section_heading.lower() in line.lower()
            continue
        if not in_section or not line.strip().startswith("|"):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if not parts or all(set(p) <= {"-"} for p in parts):
            continue
        rows.append(parts)
    if rows and any("symbol" in col.lower() or "ticker" in col.lower() for col in rows[0]):
        return rows[1:]
    return rows


def load_holdings(path: Path) -> List[Holding]:
    rows = parse_markdown_table(path, "Current Positions")
    holdings: List[Holding] = []
    for row in rows:
        if len(row) < 9 or row[0].upper() in {"SYMBOL", "TOTALS"}:
            continue
        symbol = row[0].strip().upper()
        if not re.fullmatch(r"[A-Z.]{1,6}", symbol):
            continue
        quantity = parse_money(row[1]) or 0.0
        holdings.append(
            Holding(
                symbol=symbol,
                quantity=quantity,
                average_price=parse_money(row[2]),
                current_price=parse_money(row[3]),
                market_value=parse_money(row[4]),
                weight_pct=parse_money(row[8]),
            )
        )
    return holdings


def load_options_positions(path: Path) -> List[OptionPosition]:
    rows = parse_markdown_table(path, "Options / Short Premium Positions")
    positions: List[OptionPosition] = []
    for row in rows:
        if len(row) < 7 or row[0].lower() == "ticker":
            continue
        strike = parse_money(row[1])
        credit = parse_money(row[4])
        current = parse_money(row[5])
        contracts = parse_money(row[6])
        if strike is None or credit is None or current is None or contracts is None:
            continue
        positions.append(
            OptionPosition(
                ticker=row[0].upper(),
                strike=strike,
                option_type=row[2].title(),
                expiration=row[3],
                credit=credit,
                current=current,
                contracts=int(contracts),
            )
        )
    return positions


def load_watchlist(path: Path) -> List[WatchlistItem]:
    rows = parse_markdown_table(path, "Watchlist Tickers")
    items: List[WatchlistItem] = []
    for row in rows:
        if len(row) < 5 or row[0].lower() == "ticker":
            continue
        ticker = row[0].upper()
        if not re.fullmatch(r"[A-Z.]{1,6}", ticker):
            continue
        items.append(
            WatchlistItem(
                ticker=ticker,
                score=parse_money(row[1]),
                grade=re.sub(r"[*`]", "", row[2]).strip(),
                company=row[3],
                status=row[4],
            )
        )
    return items


def request_json(url: str, timeout: int = 15, retries: int = 2) -> Any:
    last_error: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AltamiraTradeIdeaGenerator/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                payload = response.read().decode("utf-8")
            return json.loads(payload)
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Request failed: {last_error}")


def fmp_url(path: str, api_key: str, params: Optional[Dict[str, str]] = None, version: str = "v3") -> str:
    query = dict(params or {})
    query["apikey"] = api_key
    return f"{FMP_BASE}/{version}/{path.lstrip('/')}?{urllib.parse.urlencode(query)}"


def fetch_quotes(symbols: Sequence[str], api_key: str) -> Dict[str, Dict[str, Any]]:
    quotes: Dict[str, Dict[str, Any]] = {}
    clean_symbols = [s for s in symbols if s and s != "FFOLX"]
    for i in range(0, len(clean_symbols), 50):
        batch = ",".join(clean_symbols[i : i + 50])
        data = request_json(fmp_url(f"quote/{batch}", api_key))
        if isinstance(data, dict):
            data = [data]
        for item in data or []:
            symbol = str(item.get("symbol", "")).upper()
            if symbol:
                quotes[symbol] = item
    return quotes


def fetch_earnings(symbols: Iterable[str], api_key: str, start: dt.date, end: dt.date) -> Dict[str, Dict[str, Any]]:
    url = fmp_url(
        "earning_calendar",
        api_key,
        {"from": start.isoformat(), "to": end.isoformat()},
    )
    data = request_json(url, timeout=20)
    wanted = set(symbols)
    earnings: Dict[str, Dict[str, Any]] = {}
    for row in data if isinstance(data, list) else []:
        symbol = str(row.get("symbol", "")).upper()
        if symbol in wanted and symbol not in earnings:
            earnings[symbol] = row
    return earnings


def normalize_float(*values: Any) -> Optional[float]:
    for value in values:
        if value is None or value == "":
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def normalize_int(*values: Any) -> int:
    value = normalize_float(*values)
    return int(value) if value is not None else 0


def normalize_fmp_contract(ticker: str, raw: Dict[str, Any]) -> Optional[OptionContract]:
    contract_type = str(raw.get("type") or raw.get("putCall") or raw.get("side") or raw.get("optionType") or "").lower()
    symbol_blob = str(raw.get("symbol") or raw.get("contractSymbol") or "").upper()
    if not contract_type:
        if "P" in symbol_blob[-15:]:
            contract_type = "put"
        elif "C" in symbol_blob[-15:]:
            contract_type = "call"
    if contract_type not in {"put", "call"}:
        return None
    strike = normalize_float(raw.get("strike"), raw.get("strikePrice"))
    expiration = raw.get("expiration") or raw.get("expirationDate") or raw.get("date")
    bid = normalize_float(raw.get("bid"), raw.get("bidPrice")) or 0.0
    ask = normalize_float(raw.get("ask"), raw.get("askPrice")) or 0.0
    if strike is None or not expiration:
        return None
    return OptionContract(
        ticker=ticker,
        contract_type=contract_type,
        strike=strike,
        expiration=str(expiration)[:10],
        bid=bid,
        ask=ask,
        delta=normalize_float(raw.get("delta")),
        implied_volatility=normalize_float(raw.get("impliedVolatility"), raw.get("iv")),
        open_interest=normalize_int(raw.get("openInterest"), raw.get("open_interest")),
        volume=normalize_int(raw.get("volume")),
        source="fmp",
    )


def normalize_massive_contract(ticker: str, raw: Dict[str, Any]) -> Optional[OptionContract]:
    details = raw.get("details") or {}
    quote = raw.get("last_quote") or {}
    day = raw.get("day") or {}
    greeks = raw.get("greeks") or {}
    contract_type = str(details.get("contract_type") or "").lower()
    strike = normalize_float(details.get("strike_price"))
    expiration = details.get("expiration_date")
    if contract_type not in {"put", "call"} or strike is None or not expiration:
        return None
    return OptionContract(
        ticker=ticker,
        contract_type=contract_type,
        strike=strike,
        expiration=str(expiration)[:10],
        bid=normalize_float(quote.get("bid")) or 0.0,
        ask=normalize_float(quote.get("ask")) or 0.0,
        delta=normalize_float(greeks.get("delta")),
        implied_volatility=normalize_float(raw.get("implied_volatility")),
        open_interest=normalize_int(raw.get("open_interest")),
        volume=normalize_int(day.get("volume")),
        source="massive",
    )


def fetch_options_for_ticker(ticker: str, fmp_api_key: Optional[str], massive_api_key: Optional[str]) -> Tuple[str, List[OptionContract], str]:
    errors: List[str] = []
    if massive_api_key:
        try:
            url = f"{MASSIVE_BASE}/snapshot/options/{ticker}?{urllib.parse.urlencode({'apiKey': massive_api_key, 'limit': '250'})}"
            data = request_json(url, timeout=20, retries=1)
            contracts = [
                contract
                for row in (data.get("results") or [])
                if (contract := normalize_massive_contract(ticker, row)) is not None
            ]
            if contracts:
                return ticker, contracts, "massive"
        except Exception as exc:  # noqa: BLE001
            errors.append(f"Massive: {exc}")
    if fmp_api_key:
        try:
            url = fmp_url(f"options-chain/{ticker}", fmp_api_key, version="v4")
            data = request_json(url, timeout=20, retries=1)
            rows = data if isinstance(data, list) else data.get("options", []) if isinstance(data, dict) else []
            contracts = [
                contract for row in rows if isinstance(row, dict) if (contract := normalize_fmp_contract(ticker, row)) is not None
            ]
            if contracts:
                return ticker, contracts, "fmp"
        except Exception as exc:  # noqa: BLE001
            errors.append(f"FMP: {exc}")
    return ticker, [], "; ".join(errors) or "No option-chain data"


def days_to_expiration(expiration: str, today: dt.date) -> Optional[int]:
    try:
        exp = dt.datetime.strptime(expiration[:10], "%Y-%m-%d").date()
    except ValueError:
        return None
    return (exp - today).days


def vix_regime(vix: Optional[float]) -> Tuple[str, int, str]:
    if vix is None:
        return "UNKNOWN", 75, "Use standard size until VIX quote is available."
    if vix < 15:
        return "LOW", 75, "Premium is thinner; be selective and reduce size."
    if vix <= 25:
        return "NORMAL", 100, "Standard premium-selling sizing is acceptable."
    if vix <= 35:
        return "ELEVATED", 50, "Prefer defined risk and reduce size."
    return "CRISIS", 25, "Spreads only; preserve cash."


def quality_score(ticker: str, watchlist_by_ticker: Dict[str, WatchlistItem], holdings_by_ticker: Dict[str, Holding]) -> float:
    item = watchlist_by_ticker.get(ticker)
    if item and item.score is not None:
        return max(0.0, min(100.0, item.score))
    if ticker in holdings_by_ticker:
        return 58.0
    return 50.0


def trend_score(quote: Dict[str, Any]) -> Tuple[float, List[str]]:
    price = normalize_float(quote.get("price"))
    sma50 = normalize_float(quote.get("priceAvg50"))
    sma200 = normalize_float(quote.get("priceAvg200"))
    change_pct = normalize_float(quote.get("changesPercentage"))
    score = 50.0
    notes: List[str] = []
    if price and sma50:
        if price >= sma50:
            score += 15
            notes.append("above 50-day average")
        else:
            score -= 15
            notes.append("below 50-day average")
    if price and sma200:
        if price >= sma200:
            score += 10
            notes.append("above 200-day average")
        else:
            score -= 10
            notes.append("below 200-day average")
    if change_pct is not None:
        if change_pct > 4:
            score -= 8
            notes.append("large up day; avoid chasing")
        elif change_pct < -4:
            score -= 6
            notes.append("large down day; wait for stabilization")
    return max(0.0, min(100.0, score)), notes


def liquidity_score(contract: OptionContract) -> float:
    spread = (contract.ask - contract.bid) / contract.mid if contract.mid > 0 and contract.ask >= contract.bid else 1.0
    score = 40.0
    if spread <= 0.05:
        score += 25
    elif spread <= 0.10:
        score += 15
    else:
        score -= 15
    if contract.open_interest >= 500:
        score += 25
    elif contract.open_interest >= 100:
        score += 15
    elif contract.open_interest < 50:
        score -= 20
    if contract.volume >= 50:
        score += 10
    elif contract.volume >= 10:
        score += 5
    return max(0.0, min(100.0, score))


def option_delta(contract: OptionContract, underlying_price: float) -> Optional[float]:
    if contract.delta is not None:
        return contract.delta
    if underlying_price <= 0:
        return None
    moneyness = contract.strike / underlying_price
    if contract.contract_type == "put":
        # Rough screening estimate only; report as unavailable if used.
        if 0.93 <= moneyness <= 0.98:
            return -0.30
        if 0.88 <= moneyness < 0.93:
            return -0.20
        if 0.82 <= moneyness < 0.88:
            return -0.12
    else:
        if 1.02 <= moneyness <= 1.08:
            return 0.30
        if 1.08 < moneyness <= 1.15:
            return 0.20
        if 1.15 < moneyness <= 1.25:
            return 0.12
    return None


def build_csp_ideas(
    ticker: str,
    quote: Dict[str, Any],
    contracts: Sequence[OptionContract],
    today: dt.date,
    portfolio_value: float,
    sizing_pct: int,
    watchlist_by_ticker: Dict[str, WatchlistItem],
    holdings_by_ticker: Dict[str, Holding],
    earnings: Dict[str, Dict[str, Any]],
) -> List[TradeIdea]:
    price = normalize_float(quote.get("price"))
    if not price or ticker in earnings:
        return []
    quality = quality_score(ticker, watchlist_by_ticker, holdings_by_ticker)
    trend, trend_notes = trend_score(quote)
    ideas: List[TradeIdea] = []
    max_allocation = portfolio_value * 0.05 * (sizing_pct / 100)
    for contract in contracts:
        if contract.contract_type != "put" or contract.bid <= 0:
            continue
        dte = days_to_expiration(contract.expiration, today)
        if dte is None or dte < 25 or dte > 60:
            continue
        delta = option_delta(contract, price)
        abs_delta = abs(delta) if delta is not None else None
        if abs_delta is not None and not 0.15 <= abs_delta <= 0.35:
            continue
        if contract.strike > price * 0.98 or contract.strike < price * 0.80:
            continue
        if contract.open_interest < 25:
            continue
        annualized = (contract.bid / contract.strike) * (365 / dte) * 100
        if annualized < 6:
            continue
        collateral_per_contract = contract.strike * 100
        max_contracts = int(max_allocation // collateral_per_contract)
        if max_contracts < 1:
            continue
        liq = liquidity_score(contract)
        premium_score = min(100.0, annualized * 2.5)
        score = (quality * 0.25) + (trend * 0.20) + (liq * 0.25) + (premium_score * 0.30)
        rationale = (
            f"Cash-secured put candidate with {annualized:.1f}% annualized premium, "
            f"{quality:.1f} quality/watchlist score, and {', '.join(trend_notes) or 'neutral trend'}."
        )
        delta_text = f"{delta:.2f}" if delta is not None else "estimated from moneyness"
        ideas.append(
            TradeIdea(
                strategy="Cash-secured put",
                ticker=ticker,
                action=f"Sell {max_contracts}x {ticker} {contract.strike:g}P {contract.expiration}",
                score=score,
                rationale=rationale,
                contract=contract,
                dte=dte,
                underlying_price=price,
                annualized_return_pct=annualized,
                breakeven=contract.strike - contract.bid,
                contracts=max_contracts,
                collateral_or_notional=collateral_per_contract * max_contracts,
                premium=contract.bid * max_contracts * 100,
                risk_notes=f"Delta {delta_text}; close at 50% profit, defend at 200% of credit.",
            )
        )
    ideas.sort(key=lambda idea: idea.score, reverse=True)
    return ideas[:2]


def build_covered_call_ideas(
    ticker: str,
    holding: Holding,
    quote: Dict[str, Any],
    contracts: Sequence[OptionContract],
    today: dt.date,
    earnings: Dict[str, Dict[str, Any]],
) -> List[TradeIdea]:
    if holding.quantity < 100 or ticker in earnings:
        return []
    price = normalize_float(quote.get("price")) or holding.current_price
    if not price:
        return []
    trend, trend_notes = trend_score(quote)
    covered_contracts = int(holding.quantity // 100)
    ideas: List[TradeIdea] = []
    weight = holding.weight_pct or 0
    for contract in contracts:
        if contract.contract_type != "call" or contract.bid <= 0:
            continue
        dte = days_to_expiration(contract.expiration, today)
        if dte is None or dte < 25 or dte > 60:
            continue
        delta = option_delta(contract, price)
        if delta is not None and not 0.15 <= delta <= 0.35:
            continue
        if contract.strike < price * 1.03 or contract.strike > price * 1.20:
            continue
        if contract.open_interest < 25:
            continue
        annualized = (contract.bid / price) * (365 / dte) * 100
        liq = liquidity_score(contract)
        trim_bonus = min(20.0, max(0.0, weight - 5.0) * 2)
        score = liq * 0.30 + trend * 0.25 + min(100.0, annualized * 4) * 0.25 + trim_bonus
        rationale = (
            f"Covered call candidate against {covered_contracts} covered lots; "
            f"position weight is {weight:.1f}% and trend is {', '.join(trend_notes) or 'neutral'}."
        )
        ideas.append(
            TradeIdea(
                strategy="Covered call",
                ticker=ticker,
                action=f"Sell {covered_contracts}x {ticker} {contract.strike:g}C {contract.expiration}",
                score=score,
                rationale=rationale,
                contract=contract,
                dte=dte,
                underlying_price=price,
                annualized_return_pct=annualized,
                breakeven=None,
                contracts=covered_contracts,
                collateral_or_notional=price * covered_contracts * 100,
                premium=contract.bid * covered_contracts * 100,
                risk_notes="Only sell against shares intended to hold or trim; buy back at 50% profit.",
            )
        )
    ideas.sort(key=lambda idea: idea.score, reverse=True)
    return ideas[:1]


def build_existing_position_notes(positions: Sequence[OptionPosition], today: dt.date) -> List[str]:
    notes: List[str] = []
    for pos in positions:
        dte = days_to_expiration(pos.expiration, today)
        if dte is not None and dte < 0:
            notes.append(f"{pos.ticker} {pos.strike:g}{pos.option_type[0]} expired {pos.expiration}; refresh options context before acting.")
            continue
        if pos.current <= pos.credit * 0.5:
            notes.append(
                f"{pos.ticker} {pos.strike:g}{pos.option_type[0]} {pos.expiration}: at ${pos.current:.2f} vs ${pos.credit:.2f} credit; consider closing at >=50% max profit."
            )
        elif pos.current >= pos.credit * 2:
            notes.append(
                f"{pos.ticker} {pos.strike:g}{pos.option_type[0]} {pos.expiration}: at ${pos.current:.2f} vs ${pos.credit:.2f} credit; risk stop/defense threshold is triggered."
            )
    return notes


def render_money(value: Optional[float]) -> str:
    if value is None or math.isnan(value):
        return "N/A"
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"${value:,.0f}"
    return f"${value:,.2f}"


def render_percent(value: Optional[float]) -> str:
    return "N/A" if value is None else f"{value:.1f}%"


def render_contract(contract: Optional[OptionContract]) -> str:
    if not contract:
        return "N/A"
    return (
        f"{contract.ticker} {contract.strike:g}{contract.contract_type[0].upper()} {contract.expiration} "
        f"bid/ask ${contract.bid:.2f}/${contract.ask:.2f}, OI {contract.open_interest}, vol {contract.volume}, source {contract.source}"
    )


def render_report(
    today: dt.date,
    holdings: Sequence[Holding],
    watchlist: Sequence[WatchlistItem],
    options_positions: Sequence[OptionPosition],
    quotes: Dict[str, Dict[str, Any]],
    vix: Optional[float],
    regime: str,
    sizing_pct: int,
    regime_note: str,
    earnings: Dict[str, Dict[str, Any]],
    ideas: Sequence[TradeIdea],
    option_errors: Dict[str, str],
    existing_notes: Sequence[str],
) -> str:
    portfolio_value = sum((h.market_value or 0.0) for h in holdings)
    lines = [
        f"# Trade Idea Generator - {today.isoformat()}",
        "",
        "> Generated from `context/portfolio-details.md` and `context/watchlist.md`.",
        "",
        "## Executive Summary",
        "",
        f"- Portfolio context value: {render_money(portfolio_value)} across {len(holdings)} holdings.",
        f"- Watchlist universe: {len(watchlist)} names; top candidates are included first.",
        f"- VIX regime: {render_percent(vix)} / **{regime}**; sizing guide: {sizing_pct}% of normal. {regime_note}",
        f"- Earnings conflicts in next 45 days: {len(earnings)} symbols blocked from new short-premium ideas.",
        "",
        "## Top Trade Ideas",
        "",
    ]
    if not ideas:
        lines.extend(
            [
                "No qualifying options trade ideas passed the liquidity, DTE, earnings, and sizing screens.",
                "",
            ]
        )
    else:
        for rank, idea in enumerate(ideas, start=1):
            lines.extend(
                [
                    f"### {rank}. {idea.strategy}: {idea.ticker}",
                    "",
                    f"- **Action:** {idea.action}",
                    f"- **Score:** {idea.score:.1f}/100",
                    f"- **Underlying:** {render_money(idea.underlying_price)}",
                    f"- **Contract:** {render_contract(idea.contract)}",
                    f"- **DTE:** {idea.dte if idea.dte is not None else 'N/A'}",
                    f"- **Premium:** {render_money(idea.premium)}",
                    f"- **Collateral / Notional:** {render_money(idea.collateral_or_notional)}",
                    f"- **Annualized premium return:** {render_percent(idea.annualized_return_pct)}",
                    f"- **Breakeven:** {render_money(idea.breakeven)}",
                    f"- **Rationale:** {idea.rationale}",
                    f"- **Risk / management:** {idea.risk_notes}",
                    "",
                ]
            )
    lines.extend(["## Existing Short-Premium Notes", ""])
    if existing_notes:
        lines.extend(f"- {note}" for note in existing_notes)
    else:
        lines.append("- No active option-position management notes from current context.")
    lines.extend(["", "## Earnings Blocks", ""])
    if earnings:
        for symbol, row in sorted(earnings.items()):
            lines.append(f"- {symbol}: {str(row.get('date', 'unknown'))[:10]}")
    else:
        lines.append("- None detected for scanned symbols.")
    lines.extend(["", "## Data Coverage Notes", ""])
    if option_errors:
        for symbol, error in sorted(option_errors.items()):
            lines.append(f"- {symbol}: {error}")
    else:
        lines.append("- Options chains returned for all scanned symbols.")
    lines.extend(
        [
            "",
            "## Disclaimers",
            "",
            "- This is not financial advice. Validate live bid/ask, open interest, earnings dates, buying power, and portfolio limits before entering any order.",
            "- Short options can lose substantially more than the initial credit; use defined-risk structures when volatility or portfolio concentration warrants.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_telegram_message(today: dt.date, vix: Optional[float], regime: str, ideas: Sequence[TradeIdea], report_path: Path) -> str:
    lines = [
        f"ALTAMIRA TRADE IDEAS - {today.isoformat()}",
        f"VIX: {render_percent(vix)} ({regime})",
        "",
    ]
    if not ideas:
        lines.append("No qualifying trade ideas passed today's screens.")
    else:
        for rank, idea in enumerate(ideas[:3], start=1):
            lines.append(f"{rank}) {idea.strategy.upper()} - {idea.ticker}")
            lines.append(f"   Action: {idea.action}")
            lines.append(
                f"   Credit: {render_money(idea.premium)} | DTE: {idea.dte} | Ann prem: {render_percent(idea.annualized_return_pct)}"
            )
            lines.append(f"   Score: {idea.score:.1f}/100")
            lines.append(f"   Manage: {idea.risk_notes}")
            lines.append("")
    lines.extend(
        [
            f"Report: {report_path.as_posix()}",
            "",
            "Not financial advice. Verify live chain, earnings, and risk limits before trading.",
        ]
    )
    message = "\n".join(lines).strip()
    if len(message) > MAX_TELEGRAM_CHARS:
        message = message[: MAX_TELEGRAM_CHARS - 80] + "\n\n... truncated; see report."
    return message


def send_telegram(token: str, chat_id: str, message: str) -> Dict[str, Any]:
    endpoint = f"https://api.telegram.org/bot{token}/sendMessage"
    body = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    req = urllib.request.Request(endpoint, data=body, method="POST")
    with urllib.request.urlopen(req, timeout=20) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def summarize_telegram_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Keep delivery evidence without persisting Telegram profile metadata."""
    result = response.get("result") or {}
    return {
        "ok": bool(response.get("ok")),
        "message_id": result.get("message_id"),
        "date": result.get("date"),
        "chat_id": (result.get("chat") or {}).get("id"),
    }


def build_universe(holdings: Sequence[Holding], watchlist: Sequence[WatchlistItem]) -> List[str]:
    portfolio_symbols = [h.symbol for h in holdings if h.symbol not in {"FFOLX"}]
    top_watchlist = [
        item.ticker
        for item in sorted(watchlist, key=lambda x: (x.score is not None, x.score or -1), reverse=True)
        if item.status.lower() != "avoid"
    ][:12]
    universe: List[str] = []
    for symbol in [*portfolio_symbols, *top_watchlist, "^VIX"]:
        if symbol not in universe:
            universe.append(symbol)
    return universe


def main() -> int:
    args = parse_args()
    today = dt.datetime.strptime(args.date, "%Y-%m-%d").date()
    if not args.fmp_api_key:
        print("FMP_API_KEY is required for live quote and earnings data.", file=sys.stderr)
        return 2

    holdings = load_holdings(args.portfolio)
    watchlist = load_watchlist(args.watchlist)
    options_positions = load_options_positions(args.portfolio)
    holdings_by_ticker = {h.symbol: h for h in holdings}
    watchlist_by_ticker = {w.ticker: w for w in watchlist}
    universe = build_universe(holdings, watchlist)
    quote_symbols = [s for s in universe if s != "^VIX"]

    quotes = fetch_quotes(universe, args.fmp_api_key)
    vix_quote = quotes.get("^VIX") or quotes.get("VIX")
    vix = normalize_float(vix_quote.get("price")) if vix_quote else None
    regime, sizing_pct, regime_note = vix_regime(vix)
    earnings = fetch_earnings(quote_symbols, args.fmp_api_key, today, today + dt.timedelta(days=45))

    option_chains: Dict[str, List[OptionContract]] = {}
    option_errors: Dict[str, str] = {}
    chain_symbols = [s for s in quote_symbols if s in quotes][:18]
    if not args.skip_options:
        with ThreadPoolExecutor(max_workers=max(1, args.max_workers)) as executor:
            futures = {
                executor.submit(fetch_options_for_ticker, ticker, args.fmp_api_key, args.massive_api_key): ticker
                for ticker in chain_symbols
            }
            for future in as_completed(futures):
                ticker, contracts, source = future.result()
                if contracts:
                    option_chains[ticker] = contracts
                else:
                    option_errors[ticker] = source

    portfolio_value = sum((h.market_value or 0.0) for h in holdings) or 100_000.0
    ideas: List[TradeIdea] = []
    for ticker in chain_symbols:
        chain = option_chains.get(ticker, [])
        quote = quotes.get(ticker, {})
        if not chain or not quote:
            continue
        ideas.extend(
            build_csp_ideas(
                ticker,
                quote,
                chain,
                today,
                portfolio_value,
                sizing_pct,
                watchlist_by_ticker,
                holdings_by_ticker,
                earnings,
            )
        )
        holding = holdings_by_ticker.get(ticker)
        if holding:
            ideas.extend(build_covered_call_ideas(ticker, holding, quote, chain, today, earnings))

    ideas.sort(key=lambda idea: idea.score, reverse=True)
    top_ideas = ideas[: args.top]
    existing_notes = build_existing_position_notes(options_positions, today)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.out_dir / f"trade-idea-generator-{today.isoformat()}.md"
    json_path = args.out_dir / f"trade-idea-generator-{today.isoformat()}.json"
    report = render_report(
        today,
        holdings,
        watchlist,
        options_positions,
        quotes,
        vix,
        regime,
        sizing_pct,
        regime_note,
        earnings,
        top_ideas,
        option_errors,
        existing_notes,
    )
    report_path.write_text(report, encoding="utf-8")
    telegram_message = render_telegram_message(today, vix, regime, top_ideas, report_path)
    payload = {
        "date": today.isoformat(),
        "report_path": report_path.as_posix(),
        "telegram_chat_id": args.telegram_chat_id,
        "telegram_message": telegram_message,
        "sent_telegram": False,
        "ideas": [
            {
                "rank": i + 1,
                "strategy": idea.strategy,
                "ticker": idea.ticker,
                "action": idea.action,
                "score": round(idea.score, 2),
                "premium": idea.premium,
                "collateral_or_notional": idea.collateral_or_notional,
                "annualized_return_pct": idea.annualized_return_pct,
                "risk_notes": idea.risk_notes,
            }
            for i, idea in enumerate(top_ideas)
        ],
        "option_errors": option_errors,
        "earnings_blocks": {ticker: row.get("date") for ticker, row in earnings.items()},
    }

    if args.send_telegram:
        if not args.telegram_token:
            payload["telegram_error"] = "TELEGRAM_BOT_TOKEN or TELEGRAM_TOKEN is not set."
        else:
            try:
                response = send_telegram(args.telegram_token, args.telegram_chat_id, html.escape(telegram_message))
                payload["sent_telegram"] = bool(response.get("ok"))
                payload["telegram_response"] = summarize_telegram_response(response)
            except Exception as exc:  # noqa: BLE001
                payload["telegram_error"] = str(exc)

    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Report written: {report_path}")
    print(f"JSON written: {json_path}")
    if args.send_telegram:
        if payload["sent_telegram"]:
            print(f"Telegram sent to chat {args.telegram_chat_id}")
        else:
            print(f"Telegram not sent: {payload.get('telegram_error', 'unknown error')}", file=sys.stderr)
            return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
