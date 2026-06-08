#!/usr/bin/env python3
"""
Generate Altamira trade ideas from the repository portfolio and watchlist.

The script is intentionally self-contained so it can be run from cron/Cursor
automation without an n8n runtime. It reads context/portfolio-details.md and
context/watchlist.md, fetches market/options data, writes a dated report, and
optionally sends a concise summary to Telegram.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests


WORKSPACE = Path(__file__).resolve().parent.parent
FMP_BASE = "https://financialmodelingprep.com/api/v3"
MASSIVE_BASE = "https://api.massive.com/v3"
DEFAULT_FMP_KEY = "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz"
DEFAULT_MASSIVE_KEY = "kEnhZTIYm_UZZSfpSPuYQgsW_kG0vPHp"
SKIP_OPTION_SYMBOLS = {"FFOLX"}


@dataclass
class Holding:
    symbol: str
    qty: float = 0.0
    current: float = 0.0
    market_value: float = 0.0
    weight: float = 0.0


@dataclass
class WatchlistItem:
    symbol: str
    score: float | None = None
    grade: str = ""
    company: str = ""
    status: str = ""


@dataclass
class OptionPosition:
    symbol: str
    strike: float
    option_type: str
    expiration: str
    contracts: int


@dataclass
class MarketContext:
    price: float = 0.0
    change_pct: float = 0.0
    volume: int = 0
    sma20: float | None = None
    sma50: float | None = None
    rsi14: float | None = None
    trend: str = "Unknown"
    next_earnings: str | None = None


@dataclass
class TradeIdea:
    ticker: str
    strategy: str
    action: str
    expiration: str
    dte: int
    strike: float
    credit: float
    delta: float | None
    annualized_return: float
    breakeven: float
    max_risk: float
    score: float
    rationale: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def clean_number(value: str) -> float:
    text = value.replace("$", "").replace(",", "").replace("%", "").strip()
    text = text.replace("+", "")
    if not text or text in {"—", "-"}:
        return 0.0
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(match.group(0)) if match else 0.0


def split_md_row(line: str) -> list[str]:
    return [cell.strip().replace("**", "") for cell in line.strip().strip("|").split("|")]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def parse_holdings(path: Path) -> dict[str, Holding]:
    holdings: dict[str, Holding] = {}
    lines = read_text(path).splitlines()
    in_table = False

    for line in lines:
        if line.startswith("| SYMBOL |"):
            in_table = True
            continue
        if in_table and (line.startswith("|--------") or not line.strip()):
            continue
        if in_table and line.startswith("**Totals:**"):
            break
        if not in_table or not line.startswith("|"):
            continue

        cells = split_md_row(line)
        if len(cells) < 9:
            continue
        symbol = cells[0].upper()
        if symbol == "SYMBOL":
            continue
        holdings[symbol] = Holding(
            symbol=symbol,
            qty=clean_number(cells[1]),
            current=clean_number(cells[3]),
            market_value=clean_number(cells[4]),
            weight=clean_number(cells[8]),
        )

    return holdings


def parse_watchlist(path: Path) -> dict[str, WatchlistItem]:
    items: dict[str, WatchlistItem] = {}
    lines = read_text(path).splitlines()
    in_table = False

    for line in lines:
        if line.startswith("| Ticker | Score |"):
            in_table = True
            continue
        if in_table and (line.startswith("|--------") or not line.strip()):
            continue
        if in_table and line.startswith("---"):
            break
        if not in_table or not line.startswith("|"):
            continue

        cells = split_md_row(line)
        if len(cells) < 5:
            continue
        symbol = cells[0].upper()
        score = None if cells[1] in {"—", "-"} else clean_number(cells[1])
        items[symbol] = WatchlistItem(
            symbol=symbol,
            score=score,
            grade=cells[2],
            company=cells[3],
            status=cells[4].replace("⭐", "").strip(),
        )

    return items


def parse_option_positions(path: Path) -> list[OptionPosition]:
    positions: list[OptionPosition] = []
    lines = read_text(path).splitlines()
    in_table = False

    for line in lines:
        if line.startswith("| Ticker | Strike |"):
            in_table = True
            continue
        if in_table and (line.startswith("|--------") or not line.strip()):
            continue
        if not in_table or not line.startswith("|"):
            continue

        cells = split_md_row(line)
        if len(cells) < 7:
            continue
        positions.append(
            OptionPosition(
                symbol=cells[0].upper(),
                strike=clean_number(cells[1]),
                option_type=cells[2],
                expiration=cells[3],
                contracts=int(clean_number(cells[6])),
            )
        )

    return positions


def fmp_get(session: requests.Session, path: str, params: dict[str, Any] | None = None) -> Any:
    api_key = os.environ.get("FMP_API_KEY", DEFAULT_FMP_KEY)
    query = dict(params or {})
    query["apikey"] = api_key
    response = session.get(f"{FMP_BASE}{path}", params=query, timeout=20)
    response.raise_for_status()
    return response.json()


def massive_get(
    session: requests.Session,
    ticker: str,
    contract_type: str,
    start: date,
    end: date,
) -> list[dict[str, Any]]:
    api_key = os.environ.get("MASSIVE_API_KEY", DEFAULT_MASSIVE_KEY)
    params = {
        "apiKey": api_key,
        "limit": 250,
        "contract_type": contract_type,
        "expiration_date.gte": start.isoformat(),
        "expiration_date.lte": end.isoformat(),
        "sort": "expiration_date",
        "order": "asc",
    }
    try:
        response = session.get(
            f"{MASSIVE_BASE}/snapshot/options/{ticker}",
            params=params,
            timeout=25,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException:
        return []
    return payload.get("results") or []


def fetch_quotes(session: requests.Session, symbols: list[str]) -> dict[str, dict[str, Any]]:
    quotes: dict[str, dict[str, Any]] = {}
    for i in range(0, len(symbols), 20):
        chunk = symbols[i : i + 20]
        try:
            rows = fmp_get(session, f"/quote/{','.join(chunk)}")
        except requests.RequestException:
            continue
        for row in rows if isinstance(rows, list) else []:
            symbol = str(row.get("symbol", "")).upper()
            if symbol:
                quotes[symbol] = row
    return quotes


def fetch_vix(session: requests.Session) -> tuple[float, str, int]:
    try:
        rows = fmp_get(session, "/quote/%5EVIX")
        vix = float(rows[0].get("price", 20)) if rows else 20.0
    except Exception:
        vix = 20.0
    if vix < 15:
        return vix, "LOW", 75
    if vix < 25:
        return vix, "NORMAL", 100
    if vix < 35:
        return vix, "ELEVATED", 50
    return vix, "CRISIS", 25


def fetch_market_contexts(
    session: requests.Session,
    symbols: list[str],
    quotes: dict[str, dict[str, Any]],
    earnings: dict[str, str],
) -> dict[str, MarketContext]:
    contexts: dict[str, MarketContext] = {}
    today = date.today()
    start = today - timedelta(days=120)

    for symbol in symbols:
        quote = quotes.get(symbol, {})
        closes: list[float] = []
        try:
            hist = fmp_get(
                session,
                f"/historical-price-full/{symbol}",
                {"from": start.isoformat(), "to": today.isoformat()},
            )
            rows = list(reversed(hist.get("historical", []))) if isinstance(hist, dict) else []
            closes = [float(row["close"]) for row in rows if row.get("close")]
        except Exception:
            closes = []

        sma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else None
        sma50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else None
        rsi14 = calculate_rsi(closes, 14) if len(closes) >= 15 else None
        price = float(quote.get("price") or (closes[-1] if closes else 0.0))
        trend = classify_trend(price, sma20, sma50, rsi14)
        contexts[symbol] = MarketContext(
            price=price,
            change_pct=float(quote.get("changesPercentage") or 0.0),
            volume=int(quote.get("volume") or 0),
            sma20=sma20,
            sma50=sma50,
            rsi14=rsi14,
            trend=trend,
            next_earnings=earnings.get(symbol),
        )
    return contexts


def calculate_rsi(closes: list[float], period: int) -> float | None:
    if len(closes) <= period:
        return None
    gains: list[float] = []
    losses: list[float] = []
    for prev, curr in zip(closes[-period - 1 : -1], closes[-period:]):
        change = curr - prev
        gains.append(max(change, 0.0))
        losses.append(abs(min(change, 0.0)))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def classify_trend(
    price: float,
    sma20: float | None,
    sma50: float | None,
    rsi14: float | None,
) -> str:
    if not price or sma20 is None:
        return "Unknown"
    if rsi14 is not None and rsi14 >= 75:
        return "Overbought"
    if rsi14 is not None and rsi14 <= 30:
        return "Oversold"
    if sma50 is not None and price > sma20 > sma50:
        return "Bullish"
    if sma50 is not None and price < sma20 < sma50:
        return "Bearish"
    if price > sma20:
        return "Constructive"
    return "Weak"


def fetch_earnings(session: requests.Session, symbols: set[str], days: int = 60) -> dict[str, str]:
    today = date.today()
    end = today + timedelta(days=days)
    earnings: dict[str, str] = {}
    try:
        rows = fmp_get(
            session,
            "/earning_calendar",
            {"from": today.isoformat(), "to": end.isoformat()},
        )
    except Exception:
        return earnings
    if not isinstance(rows, list):
        return earnings
    for row in rows:
        symbol = str(row.get("symbol", "")).upper()
        earning_date = row.get("date")
        if symbol in symbols and earning_date and symbol not in earnings:
            earnings[symbol] = str(earning_date)[:10]
    return earnings


def option_mid(contract: dict[str, Any]) -> tuple[float, float, float]:
    quote = contract.get("last_quote") or {}
    bid = float(quote.get("bid") or contract.get("bid") or 0.0)
    ask = float(quote.get("ask") or contract.get("ask") or 0.0)
    mid = (bid + ask) / 2 if bid and ask else bid or ask
    return bid, ask, mid


def option_details(contract: dict[str, Any]) -> tuple[float, str, str]:
    details = contract.get("details") or {}
    strike = float(details.get("strike_price") or contract.get("strike") or 0.0)
    expiration = str(details.get("expiration_date") or contract.get("expirationDate") or "")
    option_type = str(details.get("contract_type") or contract.get("optionType") or "").lower()
    return strike, expiration, option_type


def option_delta(contract: dict[str, Any]) -> float | None:
    greeks = contract.get("greeks") or {}
    value = greeks.get("delta") or contract.get("delta")
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def option_iv(contract: dict[str, Any]) -> float:
    try:
        return float(contract.get("implied_volatility") or contract.get("iv") or 0.0)
    except (TypeError, ValueError):
        return 0.0


def option_liquidity(contract: dict[str, Any], bid: float, ask: float) -> tuple[int, int, int]:
    day = contract.get("day") or {}
    volume = int(day.get("volume") or contract.get("volume") or 0)
    open_interest = int(contract.get("open_interest") or contract.get("openInterest") or 0)
    spread_pct = ((ask - bid) / ((ask + bid) / 2)) if bid and ask else 1.0
    score = 2
    if open_interest >= 500:
        score += 3
    elif open_interest >= 100:
        score += 2
    elif open_interest >= 25:
        score += 1
    if volume >= 100:
        score += 3
    elif volume >= 25:
        score += 2
    elif volume >= 5:
        score += 1
    if spread_pct <= 0.05:
        score += 2
    elif spread_pct <= 0.10:
        score += 1
    else:
        score -= 1
    return max(1, min(score, 10)), volume, open_interest


def dte_from_expiration(expiration: str) -> int:
    try:
        return (datetime.strptime(expiration[:10], "%Y-%m-%d").date() - date.today()).days
    except ValueError:
        return 0


def is_expired(expiration: str) -> bool:
    try:
        return datetime.strptime(expiration[:10], "%Y-%m-%d").date() < date.today()
    except ValueError:
        return False


def has_earnings_conflict(next_earnings: str | None, expiration: str) -> bool:
    if not next_earnings:
        return False
    try:
        earnings_date = datetime.strptime(next_earnings[:10], "%Y-%m-%d").date()
        expiration_date = datetime.strptime(expiration[:10], "%Y-%m-%d").date()
    except ValueError:
        return False
    return date.today() <= earnings_date <= expiration_date


def build_universe(
    holdings: dict[str, Holding],
    watchlist: dict[str, WatchlistItem],
    max_tickers: int,
) -> list[str]:
    ranked: list[tuple[float, str]] = []
    for symbol, holding in holdings.items():
        if symbol in SKIP_OPTION_SYMBOLS:
            continue
        ranked.append((1000 + holding.weight, symbol))
    for symbol, item in watchlist.items():
        if symbol in holdings or symbol in SKIP_OPTION_SYMBOLS:
            continue
        score = item.score if item.score is not None else 0.0
        ranked.append((score, symbol))
    ranked.sort(reverse=True)
    return [symbol for _, symbol in ranked[:max_tickers]]


def scan_options(
    session: requests.Session,
    symbols: list[str],
    holdings: dict[str, Holding],
    watchlist: dict[str, WatchlistItem],
    option_positions: list[OptionPosition],
    contexts: dict[str, MarketContext],
    vix_regime: str,
) -> tuple[list[TradeIdea], dict[str, int]]:
    start = date.today() + timedelta(days=20)
    end = date.today() + timedelta(days=60)
    ideas: list[TradeIdea] = []
    stats = {"put_contracts": 0, "call_contracts": 0, "tickers_with_options": 0}
    existing_puts = {
        pos.symbol
        for pos in option_positions
        if pos.option_type.lower() == "put" and not is_expired(pos.expiration)
    }

    for symbol in symbols:
        context = contexts.get(symbol, MarketContext())
        if context.price <= 0:
            continue

        puts = massive_get(session, symbol, "put", start, end)
        calls = massive_get(session, symbol, "call", start, end) if holdings.get(symbol, Holding(symbol)).qty >= 100 else []
        if puts or calls:
            stats["tickers_with_options"] += 1
        stats["put_contracts"] += len(puts)
        stats["call_contracts"] += len(calls)

        ideas.extend(
            score_put_ideas(
                symbol,
                puts,
                holdings,
                watchlist,
                context,
                vix_regime,
                symbol in existing_puts,
            )
        )
        ideas.extend(score_call_ideas(symbol, calls, holdings, watchlist, context, vix_regime))

    ideas.sort(key=lambda idea: idea.score, reverse=True)
    return ideas, stats


def quality_score(symbol: str, holdings: dict[str, Holding], watchlist: dict[str, WatchlistItem]) -> float:
    if symbol in watchlist and watchlist[symbol].score is not None:
        return min(max(watchlist[symbol].score or 0.0, 0.0), 100.0)
    if symbol in holdings:
        return 62.0
    return 50.0


def trend_score(context: MarketContext, strategy: str) -> float:
    mapping = {
        "Bullish": 18,
        "Constructive": 15,
        "Oversold": 12,
        "Unknown": 10,
        "Weak": 6,
        "Bearish": 3,
        "Overbought": 4 if strategy == "CSP" else 14,
    }
    return float(mapping.get(context.trend, 8))


def score_put_ideas(
    symbol: str,
    contracts: list[dict[str, Any]],
    holdings: dict[str, Holding],
    watchlist: dict[str, WatchlistItem],
    context: MarketContext,
    vix_regime: str,
    has_existing_put: bool,
) -> list[TradeIdea]:
    ideas: list[TradeIdea] = []
    for contract in contracts:
        strike, expiration, _ = option_details(contract)
        bid, ask, mid = option_mid(contract)
        delta = option_delta(contract)
        dte = dte_from_expiration(expiration)
        if not 20 <= dte <= 60 or strike <= 0 or bid < 0.05:
            continue
        moneyness = strike / context.price if context.price else 0
        delta_pass = delta is not None and -0.35 <= delta <= -0.15
        moneyness_pass = delta is None and 0.85 <= moneyness <= 0.97
        if not delta_pass and not moneyness_pass:
            continue

        liquidity, volume, open_interest = option_liquidity(contract, bid, ask)
        if open_interest < 10 and volume < 5:
            continue
        if has_earnings_conflict(context.next_earnings, expiration):
            continue

        annualized = (bid / strike) * (365 / max(dte, 1))
        breakeven = strike - bid
        iv = option_iv(contract)
        score = (
            min(annualized / 0.35, 1.0) * 35
            + liquidity * 2.0
            + trend_score(context, "CSP")
            + quality_score(symbol, holdings, watchlist) * 0.20
            + min(iv / 0.70, 1.0) * 10
        )
        warnings: list[str] = []
        if has_existing_put:
            score -= 12
            warnings.append("Existing short put exposure in context/options-positions.md")
        if vix_regime in {"ELEVATED", "CRISIS"}:
            warnings.append("Prefer defined-risk spread sizing in elevated volatility")
        if context.trend in {"Bearish", "Weak"}:
            warnings.append(f"Technical trend is {context.trend}")

        ideas.append(
            TradeIdea(
                ticker=symbol,
                strategy="CSP",
                action="Sell cash-secured put",
                expiration=expiration[:10],
                dte=dte,
                strike=strike,
                credit=bid,
                delta=delta,
                annualized_return=annualized,
                breakeven=breakeven,
                max_risk=breakeven * 100,
                score=score,
                rationale=[
                    f"{annualized:.1%} annualized premium yield",
                    f"Liquidity score {liquidity}/10 (OI {open_interest}, volume {volume})",
                    f"{context.trend} technical setup",
                ],
                warnings=warnings,
            )
        )
    return ideas


def score_call_ideas(
    symbol: str,
    contracts: list[dict[str, Any]],
    holdings: dict[str, Holding],
    watchlist: dict[str, WatchlistItem],
    context: MarketContext,
    vix_regime: str,
) -> list[TradeIdea]:
    holding = holdings.get(symbol)
    if not holding or holding.qty < 100:
        return []

    ideas: list[TradeIdea] = []
    for contract in contracts:
        strike, expiration, _ = option_details(contract)
        bid, ask, _ = option_mid(contract)
        delta = option_delta(contract)
        dte = dte_from_expiration(expiration)
        if not 20 <= dte <= 60 or strike <= 0 or bid < 0.05:
            continue
        moneyness = strike / context.price if context.price else 0
        delta_pass = delta is not None and 0.15 <= delta <= 0.35
        moneyness_pass = delta is None and 1.03 <= moneyness <= 1.18
        if not delta_pass and not moneyness_pass:
            continue

        liquidity, volume, open_interest = option_liquidity(contract, bid, ask)
        if open_interest < 10 and volume < 5:
            continue

        annualized = (bid / max(context.price, 1)) * (365 / max(dte, 1))
        if_called_return = ((strike - context.price) + bid) / max(context.price, 1)
        score = (
            min(annualized / 0.25, 1.0) * 30
            + min(if_called_return / 0.12, 1.0) * 20
            + liquidity * 2.0
            + trend_score(context, "CALL")
            + quality_score(symbol, holdings, watchlist) * 0.15
        )
        warnings: list[str] = []
        if context.trend in {"Bullish", "Constructive"}:
            warnings.append("Covered call may cap upside in constructive trend")
        if vix_regime == "LOW":
            warnings.append("Low VIX can reduce call premium richness")

        ideas.append(
            TradeIdea(
                ticker=symbol,
                strategy="Covered Call",
                action="Sell covered call against existing shares",
                expiration=expiration[:10],
                dte=dte,
                strike=strike,
                credit=bid,
                delta=delta,
                annualized_return=annualized,
                breakeven=context.price - bid,
                max_risk=0.0,
                score=score,
                rationale=[
                    f"{annualized:.1%} annualized option income on spot",
                    f"{if_called_return:.1%} if-called return before taxes/fees",
                    f"Liquidity score {liquidity}/10 (OI {open_interest}, volume {volume})",
                ],
                warnings=warnings,
            )
        )
    return ideas


def fmt_money(value: float) -> str:
    return f"${value:,.2f}"


def fmt_delta(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}"


def select_top_ideas(ideas: list[TradeIdea], limit: int) -> list[TradeIdea]:
    """Pick the highest-scored ideas while avoiding a same-ticker top list."""
    selected: list[TradeIdea] = []
    used_tickers: set[str] = set()
    for idea in ideas:
        if idea.ticker in used_tickers:
            continue
        selected.append(idea)
        used_tickers.add(idea.ticker)
        if len(selected) >= limit:
            return selected
    for idea in ideas:
        if idea in selected:
            continue
        selected.append(idea)
        if len(selected) >= limit:
            break
    return selected


def render_report(
    output_path: Path,
    holdings: dict[str, Holding],
    watchlist: dict[str, WatchlistItem],
    option_positions: list[OptionPosition],
    symbols: list[str],
    contexts: dict[str, MarketContext],
    ideas: list[TradeIdea],
    stats: dict[str, int],
    vix: float,
    vix_regime: str,
    sizing_pct: int,
    telegram_status: str,
) -> str:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    top = select_top_ideas(ideas, 8)
    lines = [
        f"# Trade Idea Generator - {date.today().isoformat()}",
        "",
        f"Generated: {generated_at}",
        "",
        "## Summary",
        "",
        f"- Universe scanned: {len(symbols)} tickers from current portfolio and watchlist.",
        f"- VIX: {vix:.1f} ({vix_regime}); suggested premium-selling size multiplier: {sizing_pct}%.",
        f"- Options contracts inspected: {stats.get('put_contracts', 0)} puts and {stats.get('call_contracts', 0)} calls.",
        f"- Qualifying trade ideas: {len(ideas)}.",
        f"- Telegram status: {telegram_status}.",
        "",
        "## Top Trade Ideas",
        "",
    ]

    if not top:
        lines.extend(
            [
                "No qualifying option trade ideas passed the liquidity, DTE, delta/moneyness, and earnings filters.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "| Rank | Ticker | Strategy | Exp | DTE | Strike | Credit | Delta | Ann. Yield | Breakeven | Score |",
                "|------|--------|----------|-----|-----|--------|--------|-------|------------|-----------|-------|",
            ]
        )
        for idx, idea in enumerate(top, start=1):
            lines.append(
                "| {rank} | {ticker} | {strategy} | {exp} | {dte} | {strike} | {credit} | {delta} | {ann} | {be} | {score:.1f} |".format(
                    rank=idx,
                    ticker=idea.ticker,
                    strategy=idea.strategy,
                    exp=idea.expiration,
                    dte=idea.dte,
                    strike=fmt_money(idea.strike),
                    credit=fmt_money(idea.credit),
                    delta=fmt_delta(idea.delta),
                    ann=f"{idea.annualized_return:.1%}",
                    be=fmt_money(idea.breakeven),
                    score=idea.score,
                )
            )
        lines.append("")
        for idx, idea in enumerate(top[:5], start=1):
            lines.extend(
                [
                    f"### {idx}. {idea.ticker} - {idea.strategy}",
                    "",
                    f"- Action: {idea.action}.",
                    f"- Contract: {idea.expiration} {idea.strike:g} strike for approx. {fmt_money(idea.credit)} credit.",
                    f"- Rationale: {'; '.join(idea.rationale)}.",
                ]
            )
            if idea.warnings:
                lines.append(f"- Risk notes: {'; '.join(idea.warnings)}.")
            lines.append("")

    lines.extend(
        [
            "## Ticker Context",
            "",
            "| Ticker | Source | Price | Trend | RSI | Next Earnings | Portfolio Weight | Watch Score |",
            "|--------|--------|-------|-------|-----|---------------|------------------|-------------|",
        ]
    )
    for symbol in symbols:
        context = contexts.get(symbol, MarketContext())
        source = []
        if symbol in holdings:
            source.append("Portfolio")
        if symbol in watchlist:
            source.append("Watchlist")
        lines.append(
            "| {ticker} | {source} | {price} | {trend} | {rsi} | {earnings} | {weight} | {score} |".format(
                ticker=symbol,
                source="+".join(source),
                price=fmt_money(context.price) if context.price else "n/a",
                trend=context.trend,
                rsi=f"{context.rsi14:.1f}" if context.rsi14 is not None else "n/a",
                earnings=context.next_earnings or "n/a",
                weight=f"{holdings[symbol].weight:.1f}%" if symbol in holdings else "-",
                score=f"{watchlist[symbol].score:.1f}" if symbol in watchlist and watchlist[symbol].score is not None else "-",
            )
        )

    lines.extend(
        [
            "",
            "## Existing Short Premium Exposure",
            "",
        ]
    )
    if option_positions:
        lines.extend(
            [
                "| Ticker | Type | Expiration | Strike | Contracts | Status |",
                "|--------|------|------------|--------|-----------|--------|",
            ]
        )
        for pos in option_positions:
            status = "Expired/stale in repo context" if is_expired(pos.expiration) else "Active per repo context"
            lines.append(
                f"| {pos.symbol} | {pos.option_type} | {pos.expiration} | {fmt_money(pos.strike)} | {pos.contracts} | {status} |"
            )
    else:
        lines.append("No existing option positions found in context/options-positions.md.")

    lines.extend(
        [
            "",
            "## Methodology and Disclaimer",
            "",
            "- Inputs: context/portfolio-details.md, context/watchlist.md, context/options-positions.md.",
            "- Market data: FMP quotes/history/earnings and Massive.com option snapshots.",
            "- Filters: 20-60 DTE, liquid bid, open interest/volume checks, target 0.15-0.35 delta or comparable moneyness, and no known earnings before expiration for CSP ideas.",
            "- These are scan results, not trade orders or financial advice. Confirm all quotes, greeks, liquidity, tax impacts, and risk limits in the broker before placing any order.",
            "",
        ]
    )

    report = "\n".join(lines)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    return report


def build_telegram_message(
    ideas: list[TradeIdea],
    symbols: list[str],
    vix: float,
    vix_regime: str,
    sizing_pct: int,
    report_path: Path,
) -> str:
    lines = [
        f"Altamira Trade Ideas - {date.today().isoformat()}",
        f"VIX {vix:.1f} ({vix_regime}) | Sizing {sizing_pct}% | Universe {len(symbols)} tickers",
        "",
    ]
    top_ideas = select_top_ideas(ideas, 3)
    if not top_ideas:
        lines.append("No qualifying options ideas passed today's filters.")
    else:
        for idx, idea in enumerate(top_ideas, start=1):
            warn = f" Risk: {'; '.join(idea.warnings[:2])}" if idea.warnings else ""
            lines.extend(
                [
                    f"{idx}) {idea.ticker} {idea.strategy}",
                    f"   {idea.expiration} {idea.strike:g} strike | credit {fmt_money(idea.credit)} | delta {fmt_delta(idea.delta)}",
                    f"   ann. yield {idea.annualized_return:.1%} | breakeven {fmt_money(idea.breakeven)} | score {idea.score:.1f}{warn}",
                ]
            )
    lines.extend(
        [
            "",
            f"Report: {report_path}",
            "Scan only - not financial advice. Confirm in broker before trading.",
        ]
    )
    return "\n".join(lines)[:3900]


def infer_telegram_chat_id(session: requests.Session, bot_token: str) -> str | None:
    try:
        response = session.get(
            f"https://api.telegram.org/bot{bot_token}/getUpdates",
            params={"limit": 20},
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException:
        return None

    chats: set[str] = set()
    for update in payload.get("result") or []:
        chat = None
        for key in ("message", "channel_post", "edited_message", "edited_channel_post"):
            if isinstance(update.get(key), dict):
                chat = update[key].get("chat")
                break
        if isinstance(chat, dict) and chat.get("id") is not None:
            chats.add(str(chat["id"]))
    return next(iter(chats)) if len(chats) == 1 else None


def send_telegram(session: requests.Session, message: str, chat_id: str | None) -> tuple[bool, str]:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        return False, "TELEGRAM_BOT_TOKEN is not set"
    destination = chat_id or os.environ.get("TELEGRAM_CHAT_ID") or infer_telegram_chat_id(session, bot_token)
    if not destination:
        return False, "TELEGRAM_CHAT_ID is not set and no unique chat could be inferred from bot updates"

    try:
        response = session.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data={"chat_id": destination, "text": message, "disable_web_page_preview": "true"},
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        return False, f"Telegram send failed: {exc}"

    if not payload.get("ok"):
        return False, f"Telegram API returned ok=false: {payload}"
    return True, "sent"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> int:
    session = requests.Session()
    holdings = parse_holdings(WORKSPACE / "context" / "portfolio-details.md")
    watchlist = parse_watchlist(WORKSPACE / "context" / "watchlist.md")
    option_positions = parse_option_positions(WORKSPACE / "context" / "options-positions.md")
    symbols = build_universe(holdings, watchlist, args.max_tickers)

    if not symbols:
        print("No tickers found in portfolio/watchlist context.", file=sys.stderr)
        return 1

    quotes = fetch_quotes(session, symbols)
    vix, vix_regime, sizing_pct = fetch_vix(session)
    earnings = fetch_earnings(session, set(symbols), days=60)
    contexts = fetch_market_contexts(session, symbols, quotes, earnings)
    ideas, stats = scan_options(
        session,
        symbols,
        holdings,
        watchlist,
        option_positions,
        contexts,
        vix_regime,
    )

    report_path = args.output or WORKSPACE / "outputs" / f"trade-idea-generator-{date.today().isoformat()}.md"
    status = "not requested"
    message = build_telegram_message(ideas, symbols, vix, vix_regime, sizing_pct, report_path)
    sent = False
    error = ""
    if args.send:
        sent, error = send_telegram(session, message, args.chat_id)
        status = "sent" if sent else f"not sent - {error}"

    render_report(
        report_path,
        holdings,
        watchlist,
        option_positions,
        symbols,
        contexts,
        ideas,
        stats,
        vix,
        vix_regime,
        sizing_pct,
        status,
    )
    meta_path = report_path.with_suffix(".json")
    write_json(
        meta_path,
        {
            "date": date.today().isoformat(),
            "report": str(report_path),
            "universe": symbols,
            "idea_count": len(ideas),
            "top_ideas": [
                {
                    "ticker": idea.ticker,
                    "strategy": idea.strategy,
                    "expiration": idea.expiration,
                    "strike": idea.strike,
                    "credit": idea.credit,
                    "score": round(idea.score, 2),
                }
                for idea in select_top_ideas(ideas, 5)
            ],
            "telegram": {"requested": bool(args.send), "sent": sent, "status": status},
            "stats": stats,
        },
    )

    print(f"Report written: {report_path}")
    print(f"Metadata written: {meta_path}")
    print(f"Trade ideas: {len(ideas)}")
    print(f"Telegram: {status}")
    if args.send and not sent:
        return 2
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate portfolio/watchlist trade ideas.")
    parser.add_argument("--send", action="store_true", help="Send the concise summary to Telegram.")
    parser.add_argument("--chat-id", help="Telegram chat/channel ID override.")
    parser.add_argument("--max-tickers", type=int, default=32, help="Maximum tickers to scan.")
    parser.add_argument("--output", type=Path, help="Markdown report output path.")
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(run(parse_args()))
