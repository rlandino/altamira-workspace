#!/usr/bin/env python3
"""
Generate daily trade ideas from the current portfolio and watchlist context.

The script reads:
  - context/portfolio-details.md
  - context/watchlist.md
  - context/options-positions.md

It fetches live FMP market data, writes an audit report to outputs/, and can
send a concise Telegram-ready summary when TELEGRAM_BOT_TOKEN and
TELEGRAM_CHAT_ID are configured.
"""

from __future__ import annotations

import argparse
import json
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
from typing import Any, Iterable


WORKSPACE = Path(__file__).resolve().parent.parent
CONTEXT_DIR = WORKSPACE / "context"
OUTPUTS_DIR = WORKSPACE / "outputs"
FMP_BASE_V3 = "https://financialmodelingprep.com/api/v3"
FMP_BASE_V4 = "https://financialmodelingprep.com/api/v4"

PORTFOLIO_FILE = CONTEXT_DIR / "portfolio-details.md"
WATCHLIST_FILE = CONTEXT_DIR / "watchlist.md"
OPTIONS_FILE = CONTEXT_DIR / "options-positions.md"

SECTOR_BY_TICKER = {
    "AAPL": "Technology",
    "ABBV": "Healthcare",
    "ABT": "Healthcare",
    "ACN": "Technology",
    "ADBE": "Technology",
    "ADSK": "Technology",
    "AMAT": "Technology",
    "AMZN": "Consumer Discretionary",
    "ANET": "Technology",
    "ASML": "Technology",
    "AVGO": "Technology",
    "CDNS": "Technology",
    "CMG": "Consumer Discretionary",
    "COST": "Consumer Staples",
    "CRM": "Technology",
    "CRWD": "Technology",
    "FFOLX": "Fund",
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
    "MELI": "Consumer Discretionary",
    "META": "Communication Services",
    "MRVL": "Technology",
    "MSCI": "Financials",
    "MSFT": "Technology",
    "NFLX": "Communication Services",
    "NOW": "Technology",
    "NVDA": "Technology",
    "PANW": "Technology",
    "PLTR": "Technology",
    "QQQ": "ETF",
    "SPGI": "Financials",
    "SPY": "ETF",
    "TSLA": "Consumer Discretionary",
    "TSM": "Technology",
    "TMO": "Healthcare",
    "V": "Financials",
    "WM": "Industrials",
}


@dataclass
class Holding:
    ticker: str
    quantity: float
    avg_price: float
    current_context: float
    market_value: float
    cost_basis: float
    pnl_text: str
    day_change_text: str
    weight: float


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


def clean_number(value: str) -> float:
    text = value.replace("$", "").replace(",", "").replace("%", "").strip()
    if not text or text in {"-", "—"}:
        return 0.0
    return float(text)


def split_markdown_row(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def parse_portfolio(path: Path) -> list[Holding]:
    holdings: list[Holding] = []
    if not path.exists():
        return holdings

    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        cells = split_markdown_row(line)
        if len(cells) != 9 or cells[0] in {"SYMBOL", "--------"}:
            continue
        ticker = cells[0].upper()
        if ticker == "**TOTALS:**":
            continue
        try:
            holdings.append(
                Holding(
                    ticker=ticker,
                    quantity=clean_number(cells[1]),
                    avg_price=clean_number(cells[2]),
                    current_context=clean_number(cells[3]),
                    market_value=clean_number(cells[4]),
                    cost_basis=clean_number(cells[5]),
                    pnl_text=cells[6],
                    day_change_text=cells[7],
                    weight=clean_number(cells[8]),
                )
            )
        except ValueError:
            continue
    return holdings


def parse_watchlist(path: Path) -> list[WatchlistEntry]:
    entries: list[WatchlistEntry] = []
    if not path.exists():
        return entries

    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        cells = split_markdown_row(line)
        if len(cells) != 5 or cells[0] in {"Ticker", "--------"}:
            continue
        score = None
        if cells[1] not in {"—", "-"}:
            try:
                score = float(cells[1])
            except ValueError:
                score = None
        grade = cells[2].replace("*", "").strip()
        entries.append(
            WatchlistEntry(
                ticker=cells[0].upper(),
                score=score,
                grade=grade,
                company=cells[3],
                status=cells[4],
            )
        )
    return entries


def parse_options(path: Path) -> list[OptionPosition]:
    positions: list[OptionPosition] = []
    if not path.exists():
        return positions

    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        cells = split_markdown_row(line)
        if len(cells) != 7 or cells[0] in {"Ticker", "--------"}:
            continue
        try:
            positions.append(
                OptionPosition(
                    ticker=cells[0].upper(),
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


def option_expiration_date(position: OptionPosition) -> date | None:
    try:
        return datetime.strptime(position.expiration[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def load_fmp_key() -> str:
    env_key = os.environ.get("FMP_API_KEY")
    if env_key:
        return env_key

    # Local workspace scripts already expose a development fallback. Reuse it
    # without duplicating key material in this script.
    try:
        sys.path.insert(0, str(WORKSPACE / "scripts"))
        import market_data_api  # type: ignore

        key = getattr(market_data_api, "DEFAULT_KEY", "")
        if key:
            return key
    except Exception:
        pass

    for source in (WORKSPACE / "scripts" / "market_data_api.py", WORKSPACE / "scripts" / "stock-scorer.py"):
        if not source.exists():
            continue
        match = re.search(
            r"(?:DEFAULT_KEY|FMP_API_KEY)\s*=\s*(?:os\.environ\.get\([^,]+,\s*)?[\"']([^\"']+)[\"']",
            source.read_text(encoding="utf-8"),
        )
        if match:
            return match.group(1)

    raise RuntimeError("FMP_API_KEY is not set and no workspace fallback was available")


def http_get_json(url: str, timeout: int = 25) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": "AltamiraTradeIdeaGenerator/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fmp_url(path: str, params: dict[str, Any], api_key: str, base: str = FMP_BASE_V3) -> str:
    merged = dict(params)
    merged["apikey"] = api_key
    return f"{base}/{path.lstrip('/')}?{urllib.parse.urlencode(merged)}"


def fetch_quotes(symbols: Iterable[str], api_key: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    clean_symbols = [s for s in dict.fromkeys(symbols) if s]
    for i in range(0, len(clean_symbols), 40):
        batch = clean_symbols[i : i + 40]
        url = fmp_url(f"quote/{','.join(batch)}", {}, api_key)
        data = http_get_json(url)
        if isinstance(data, list):
            for row in data:
                symbol = str(row.get("symbol", "")).upper()
                if symbol:
                    result[symbol] = row
    return result


def fetch_historical(symbol: str, api_key: str, days: int = 90) -> list[dict[str, Any]]:
    end = date.today()
    start = end - timedelta(days=days * 2)
    url = fmp_url(
        f"historical-price-full/{symbol}",
        {"from": start.isoformat(), "to": end.isoformat(), "serietype": "line"},
        api_key,
    )
    try:
        data = http_get_json(url)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return []
    history = data.get("historical", []) if isinstance(data, dict) else []
    return history[:days]


def fetch_next_earnings(symbol: str, api_key: str) -> str | None:
    url = fmp_url(f"historical/earning_calendar/{symbol}", {}, api_key)
    try:
        data = http_get_json(url)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None
    if not isinstance(data, list):
        return None
    today = date.today()
    future_dates: list[date] = []
    for row in data:
        value = row.get("date")
        if not value:
            continue
        try:
            parsed = datetime.strptime(value[:10], "%Y-%m-%d").date()
        except ValueError:
            continue
        if parsed >= today:
            future_dates.append(parsed)
    if not future_dates:
        return None
    return min(future_dates).isoformat()


def fetch_option_chain(symbol: str, api_key: str, limit: int = 500) -> list[dict[str, Any]]:
    url = fmp_url(f"options-chain/{symbol}", {}, api_key, base=FMP_BASE_V4)
    try:
        data = http_get_json(url)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return []
    if isinstance(data, list):
        return data[:limit]
    if isinstance(data, dict):
        for key in ("options", "data", "result"):
            value = data.get(key)
            if isinstance(value, list):
                return value[:limit]
    return []


def sma(values: list[float], window: int) -> float | None:
    if len(values) < window:
        return None
    return sum(values[:window]) / window


def rsi(closes_newest_first: list[float], period: int = 14) -> float | None:
    if len(closes_newest_first) <= period:
        return None
    closes = list(reversed(closes_newest_first[: period + 1]))
    gains: list[float] = []
    losses: list[float] = []
    for previous, current in zip(closes, closes[1:]):
        change = current - previous
        gains.append(max(change, 0))
        losses.append(abs(min(change, 0)))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def pct_change(current: float, prior: float | None) -> float | None:
    if prior in (None, 0):
        return None
    return ((current - prior) / prior) * 100


def trend_metrics(symbol: str, quote: dict[str, Any], api_key: str) -> dict[str, Any]:
    history = fetch_historical(symbol, api_key)
    closes = [float(row.get("close", 0)) for row in history if row.get("close")]
    price = float(quote.get("price") or quote.get("previousClose") or 0)
    metrics: dict[str, Any] = {
        "price": price,
        "change_pct": float(quote.get("changesPercentage") or 0),
        "sma20": sma(closes, 20),
        "sma50": sma(closes, 50),
        "rsi14": rsi(closes),
        "change_20d": pct_change(price, closes[19] if len(closes) >= 20 else None),
        "change_60d": pct_change(price, closes[59] if len(closes) >= 60 else None),
    }
    if metrics["sma20"]:
        metrics["above_sma20"] = price > metrics["sma20"]
    else:
        metrics["above_sma20"] = None
    return metrics


def vix_regime(vix: float) -> tuple[str, int, str]:
    if vix < 15:
        return ("LOW", 75, "Premium is lean; sell smaller or favor covered calls.")
    if vix < 25:
        return ("NORMAL", 100, "Standard CSP/spread sizing is acceptable.")
    if vix < 35:
        return ("ELEVATED", 50, "Prefer defined-risk spreads and smaller size.")
    return ("CRISIS", 25, "Avoid naked premium; spreads only at minimal size.")


def grade_bonus(entry: WatchlistEntry | None) -> float:
    if not entry or entry.score is None:
        return 0.0
    return max(min((entry.score - 50) / 4, 6), -5)


def score_csp_candidate(
    symbol: str,
    metrics: dict[str, Any],
    watch_entry: WatchlistEntry | None,
    earnings: str | None,
    is_existing_holding: bool,
) -> tuple[float, list[str], list[str]]:
    score = 50.0
    positives: list[str] = []
    risks: list[str] = []

    change_pct = metrics.get("change_pct") or 0
    rsi_value = metrics.get("rsi14")
    change_20d = metrics.get("change_20d")
    above_sma20 = metrics.get("above_sma20")

    score += grade_bonus(watch_entry)
    if watch_entry and watch_entry.score is not None:
        positives.append(f"watchlist score {watch_entry.score:.1f} ({watch_entry.grade})")
    if is_existing_holding:
        score += 4
        positives.append("already approved portfolio name")
    if above_sma20:
        score += 6
        positives.append("price above 20-day trend")
    elif above_sma20 is False:
        score -= 6
        risks.append("below 20-day trend")
    if rsi_value is not None:
        if 40 <= rsi_value <= 65:
            score += 6
            positives.append(f"RSI balanced at {rsi_value:.0f}")
        elif rsi_value > 72:
            score -= 9
            risks.append(f"overbought RSI {rsi_value:.0f}")
        elif rsi_value < 35:
            score -= 4
            risks.append(f"weak RSI {rsi_value:.0f}")
    if change_20d is not None:
        if 0 <= change_20d <= 12:
            score += 4
            positives.append(f"constructive 20D move {change_20d:+.1f}%")
        elif change_20d > 18:
            score -= 6
            risks.append(f"extended 20D move {change_20d:+.1f}%")
        elif change_20d < -10:
            score -= 7
            risks.append(f"negative 20D trend {change_20d:+.1f}%")
    if change_pct < -2.5:
        score += 3
        positives.append(f"red-day premium setup {change_pct:+.1f}%")
    elif change_pct > 3:
        score -= 4
        risks.append(f"chasing after {change_pct:+.1f}% day")

    if earnings:
        try:
            days_to_earnings = (datetime.strptime(earnings, "%Y-%m-%d").date() - date.today()).days
        except ValueError:
            days_to_earnings = None
        if days_to_earnings is not None and days_to_earnings <= 45:
            score -= 12
            risks.append(f"earnings in {days_to_earnings} days ({earnings})")
        elif days_to_earnings is not None:
            positives.append(f"no near-term earnings conflict ({earnings})")

    return score, positives, risks


def select_put_contract(chain: list[dict[str, Any]], price: float) -> dict[str, Any] | None:
    today = date.today()
    candidates: list[tuple[float, dict[str, Any]]] = []
    for row in chain:
        contract_type = str(row.get("optionType") or row.get("type") or row.get("contractType") or "").lower()
        if contract_type and "put" not in contract_type:
            continue
        expiration = row.get("expirationDate") or row.get("expiration") or row.get("date")
        if not expiration:
            continue
        try:
            expiration_date = datetime.strptime(str(expiration)[:10], "%Y-%m-%d").date()
        except ValueError:
            continue
        dte = (expiration_date - today).days
        if dte < 20 or dte > 60:
            continue
        strike = float(row.get("strike") or row.get("strikePrice") or 0)
        if not strike or strike > price * 0.98 or strike < price * 0.80:
            continue
        bid = float(row.get("bid") or row.get("lastPrice") or row.get("price") or 0)
        ask = float(row.get("ask") or 0)
        volume = float(row.get("volume") or 0)
        open_interest = float(row.get("openInterest") or row.get("open_interest") or 0)
        delta = row.get("delta")
        delta_value = abs(float(delta)) if delta not in (None, "") else abs((price - strike) / price)
        if not 0.15 <= delta_value <= 0.35:
            continue
        if bid <= 0:
            continue
        spread_penalty = 0
        if ask and bid:
            mid = (bid + ask) / 2
            spread_penalty = ((ask - bid) / mid) * 10 if mid else 0
        score = (
            (1 - abs(delta_value - 0.25)) * 30
            + min(open_interest / 100, 10)
            + min(volume / 20, 8)
            + min((bid / strike) * 1000, 12)
            - spread_penalty
            - abs(dte - 35) / 3
        )
        candidates.append(
            (
                score,
                {
                    "strike": strike,
                    "expiration": expiration_date.isoformat(),
                    "dte": dte,
                    "bid": bid,
                    "ask": ask,
                    "delta": -delta_value,
                    "volume": volume,
                    "open_interest": open_interest,
                    "breakeven": strike - bid,
                    "annualized_return": (bid / strike) * (365 / dte) * 100 if strike and dte else None,
                },
            )
        )
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def format_money(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"${value:,.2f}"


def format_pct(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:+.1f}%"


def build_report(args: argparse.Namespace) -> tuple[str, str, dict[str, Any]]:
    api_key = load_fmp_key()
    holdings = parse_portfolio(PORTFOLIO_FILE)
    watchlist = parse_watchlist(WATCHLIST_FILE)
    today = date.today()
    parsed_options_positions = parse_options(OPTIONS_FILE)
    expired_options_positions = [
        position
        for position in parsed_options_positions
        if (option_expiration_date(position) or today) < today
    ]
    options_positions = [
        position
        for position in parsed_options_positions
        if (option_expiration_date(position) or today) >= today
    ]

    if not holdings and not watchlist:
        raise RuntimeError("No portfolio or watchlist entries were found in context/")

    holding_by_symbol = {holding.ticker: holding for holding in holdings}
    watch_by_symbol = {entry.ticker: entry for entry in watchlist}
    top_watch_symbols = [
        entry.ticker
        for entry in watchlist
        if entry.status.lower().startswith("⭐ top") or (entry.score is not None and entry.score >= 58)
    ]
    core_symbols = list(holding_by_symbol) + top_watch_symbols
    market_symbols = ["SPY", "QQQ", "^VIX"]

    quotes = fetch_quotes([*core_symbols, *market_symbols], api_key)
    vix_quote = quotes.get("^VIX") or quotes.get("VIX") or {}
    vix = float(vix_quote.get("price") or 0)
    regime, sizing_pct, regime_guidance = vix_regime(vix)

    metrics_by_symbol: dict[str, dict[str, Any]] = {}
    earnings_by_symbol: dict[str, str | None] = {}
    analysis_symbols = list(dict.fromkeys(core_symbols))
    for symbol in analysis_symbols:
        quote = quotes.get(symbol)
        if not quote:
            continue
        metrics_by_symbol[symbol] = trend_metrics(symbol, quote, api_key)
        if symbol not in {"SPY", "QQQ", "FFOLX"}:
            earnings_by_symbol[symbol] = fetch_next_earnings(symbol, api_key)

    csp_candidates: list[dict[str, Any]] = []
    csp_universe = list(dict.fromkeys(top_watch_symbols + ["MSFT", "AVGO", "COST", "GOOGL", "AAPL", "AMZN", "V"]))
    for symbol in csp_universe:
        metrics = metrics_by_symbol.get(symbol)
        if not metrics:
            continue
        score, positives, risks = score_csp_candidate(
            symbol,
            metrics,
            watch_by_symbol.get(symbol),
            earnings_by_symbol.get(symbol),
            symbol in holding_by_symbol,
        )
        price = metrics.get("price") or 0
        contract = None
        if args.include_options_chain and price:
            contract = select_put_contract(fetch_option_chain(symbol, api_key), price)
        csp_candidates.append(
            {
                "ticker": symbol,
                "score": score,
                "price": price,
                "metrics": metrics,
                "watch": watch_by_symbol.get(symbol),
                "earnings": earnings_by_symbol.get(symbol),
                "positives": positives,
                "risks": risks,
                "contract": contract,
            }
        )
    csp_candidates.sort(key=lambda row: row["score"], reverse=True)

    covered_call_candidates: list[dict[str, Any]] = []
    for holding in holdings:
        metrics = metrics_by_symbol.get(holding.ticker)
        if not metrics:
            continue
        rsi_value = metrics.get("rsi14")
        reasons: list[str] = []
        score = 0.0
        if holding.weight >= 10:
            score += holding.weight
            reasons.append(f"{holding.weight:.1f}% portfolio weight")
        if rsi_value is not None and rsi_value > 68:
            score += 8
            reasons.append(f"RSI elevated at {rsi_value:.0f}")
        if (metrics.get("change_20d") or 0) > 12:
            score += 6
            reasons.append(f"20D move {metrics['change_20d']:+.1f}%")
        if (metrics.get("change_pct") or 0) > 1.5:
            score += 3
            reasons.append(f"up {metrics['change_pct']:+.1f}% today")
        if score > 0:
            covered_call_candidates.append(
                {
                    "ticker": holding.ticker,
                    "score": score,
                    "holding": holding,
                    "metrics": metrics,
                    "reasons": reasons,
                }
            )
    covered_call_candidates.sort(key=lambda row: row["score"], reverse=True)

    risk_flags: list[str] = []
    total_tech_weight = sum(
        holding.weight for holding in holdings if SECTOR_BY_TICKER.get(holding.ticker) == "Technology"
    )
    if total_tech_weight > 35:
        risk_flags.append(f"Technology exposure is high at {total_tech_weight:.1f}% across listed holdings.")
    for holding in holdings:
        if holding.weight > 15:
            risk_flags.append(f"{holding.ticker} is above 15% single-name/ETF weight at {holding.weight:.1f}%.")
    for pos in options_positions:
        if pos.current > pos.credit * 1.8:
            risk_flags.append(
                f"{pos.ticker} {pos.expiration} {pos.strike:g}P is near/above stop review "
                f"({pos.current:.2f} current vs {pos.credit:.2f} credit)."
            )

    now = datetime.now(timezone.utc)
    today_str = today.isoformat()
    report_path = OUTPUTS_DIR / f"trade-idea-generator-{today_str}.md"
    json_path = OUTPUTS_DIR / f"trade-idea-generator-{today_str}.json"

    top_csp = csp_candidates[:5]
    top_calls = covered_call_candidates[:5]
    best_csp = top_csp[0] if top_csp else None
    best_call = top_calls[0] if top_calls else None

    telegram_lines = [
        f"Altamira Trade Ideas - {today_str}",
        f"Market: SPY {format_pct((quotes.get('SPY') or {}).get('changesPercentage'))} | "
        f"QQQ {format_pct((quotes.get('QQQ') or {}).get('changesPercentage'))} | "
        f"VIX {vix:.2f} ({regime})",
        f"Sizing: {sizing_pct}% of standard premium-selling size. {regime_guidance}",
        "",
    ]
    if best_csp:
        contract = best_csp.get("contract")
        if contract:
            action = (
                f"1) CSP idea: {best_csp['ticker']} {contract['expiration']} "
                f"{contract['strike']:g}P, bid {format_money(contract['bid'])}, "
                f"delta {contract['delta']:.2f}, breakeven {format_money(contract['breakeven'])}."
            )
        else:
            action = (
                f"1) CSP watch: {best_csp['ticker']} near {format_money(best_csp['price'])}; "
                "target 20-30 delta put, 30-45 DTE after chain check."
            )
        telegram_lines.append(action)
        telegram_lines.append("   Rationale: " + "; ".join(best_csp["positives"][:3]))
        if best_csp["risks"]:
            telegram_lines.append("   Risk: " + "; ".join(best_csp["risks"][:2]))
    if best_call:
        holding = best_call["holding"]
        telegram_lines.extend(
            [
                "",
                f"2) Covered-call/trim watch: {best_call['ticker']} at {holding.weight:.1f}% weight.",
                "   Rationale: " + "; ".join(best_call["reasons"][:3]),
            ]
        )
    if risk_flags:
        telegram_lines.extend(["", "Risk flags:"] + [f"- {flag}" for flag in risk_flags[:3]])
    if expired_options_positions:
        telegram_lines.extend(
            [
                "",
                f"Static options note: ignored {len(expired_options_positions)} expired short-premium rows from context/options-positions.md.",
            ]
        )
    telegram_lines.extend(
        [
            "",
            "Educational only - not financial advice. Verify quotes, greeks, liquidity, earnings, and order tickets before trading.",
        ]
    )
    telegram_text = "\n".join(telegram_lines)

    report_lines = [
        f"# Trade Idea Generator - {today_str}",
        "",
        f"Generated: {now.isoformat()}",
        "",
        "## Executive Summary",
        "",
        f"- **Market regime:** VIX {vix:.2f} ({regime}); {regime_guidance}",
        f"- **Sizing:** Use {sizing_pct}% of normal premium-selling size based on the VIX regime.",
        f"- **Universe:** {len(holdings)} portfolio holdings, {len(watchlist)} watchlist names, "
        f"{len(options_positions)} active short-premium positions.",
        "",
        "## Top Cash-Secured Put / Put-Spread Ideas",
        "",
        "| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |",
        "|---:|---|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for rank, row in enumerate(top_csp, start=1):
        metrics = row["metrics"]
        contract = row.get("contract")
        if contract:
            action = (
                f"Review {contract['expiration']} {contract['strike']:g}P "
                f"bid {format_money(contract['bid'])}, delta {contract['delta']:.2f}, "
                f"BE {format_money(contract['breakeven'])}"
            )
        else:
            action = "Review 20-30 delta put or defined-risk put spread, 30-45 DTE"
        report_lines.append(
            "| "
            + " | ".join(
                [
                    str(rank),
                    row["ticker"],
                    f"{row['score']:.1f}",
                    format_money(row["price"]),
                    format_pct(metrics.get("change_pct")),
                    f"{metrics.get('rsi14'):.0f}" if metrics.get("rsi14") is not None else "N/A",
                    format_pct(metrics.get("change_20d")),
                    row.get("earnings") or "N/A",
                    action,
                    "; ".join(row["risks"][:2]) or "None flagged",
                ]
            )
            + " |"
        )

    report_lines.extend(
        [
            "",
            "## Covered Call / Trim Watch",
            "",
            "| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |",
            "|---:|---|---:|---:|---:|---:|---|",
        ]
    )
    for rank, row in enumerate(top_calls, start=1):
        holding = row["holding"]
        metrics = row["metrics"]
        report_lines.append(
            "| "
            + " | ".join(
                [
                    str(rank),
                    row["ticker"],
                    f"{holding.weight:.1f}%",
                    format_money(metrics.get("price")),
                    format_pct(metrics.get("change_pct")),
                    f"{metrics.get('rsi14'):.0f}" if metrics.get("rsi14") is not None else "N/A",
                    "; ".join(row["reasons"]),
                ]
            )
            + " |"
        )

    report_lines.extend(
        [
            "",
            "## Existing Short-Premium Review",
            "",
            "| Ticker | Expiration | Strike | Credit | Current | Status |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for pos in options_positions:
        ratio = pos.current / pos.credit if pos.credit else 0
        if ratio >= 2:
            status = "Stop/roll review"
        elif ratio >= 1.5:
            status = "Monitor closely"
        elif ratio <= 0.5:
            status = "Profit-taking candidate"
        else:
            status = "Hold per plan"
        report_lines.append(
            f"| {pos.ticker} | {pos.expiration} | {pos.strike:g} | "
            f"{pos.credit:.2f} | {pos.current:.2f} | {status} |"
        )
    if not options_positions:
        report_lines.append("| - | - | - | - | - | No active rows after filtering expired static context |")

    report_lines.extend(
        [
            "",
            "## Portfolio Risk Flags",
            "",
        ]
    )
    if risk_flags:
        report_lines.extend([f"- {flag}" for flag in risk_flags])
    else:
        report_lines.append("- No major static risk flags found in repository context.")

    report_lines.extend(
        [
            "",
            "## Telegram Message",
            "",
            "```text",
            telegram_text,
            "```",
            "",
            "## Data Notes",
            "",
            "- Portfolio/watchlist positions are sourced from repository context files.",
            "- Live quotes and historical prices are sourced from FMP at runtime.",
            "- Option contracts are included only when the FMP options chain endpoint returns usable data.",
            f"- Expired static short-premium rows skipped: {len(expired_options_positions)}.",
            "- Financial calculations are estimates for research and workflow triage only.",
            "",
            "> Disclaimer: This report is for educational and operational planning purposes only. "
            "It is not financial advice. Verify live quotes, greeks, liquidity, earnings dates, "
            "portfolio exposure, and order tickets before placing any trade.",
            "",
        ]
    )

    report = "\n".join(report_lines)
    payload = {
        "generatedAt": now.isoformat(),
        "market": {
            "spyChangePct": (quotes.get("SPY") or {}).get("changesPercentage"),
            "qqqChangePct": (quotes.get("QQQ") or {}).get("changesPercentage"),
            "vix": vix,
            "regime": regime,
            "sizingPct": sizing_pct,
        },
        "topCsp": top_csp,
        "topCoveredCall": top_calls,
        "riskFlags": risk_flags,
        "skippedExpiredOptions": [
            {
                "ticker": position.ticker,
                "expiration": position.expiration,
                "strike": position.strike,
                "type": position.option_type,
            }
            for position in expired_options_positions
        ],
        "telegramText": telegram_text,
    }

    OUTPUTS_DIR.mkdir(exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    json_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

    return str(report_path), telegram_text, payload


def send_telegram(text: str, chat_id: str, token: str) -> dict[str, Any]:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(request, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Altamira portfolio/watchlist trade ideas.")
    parser.add_argument("--send-telegram", action="store_true", help="Send the summary to Telegram.")
    parser.add_argument("--telegram-chat-id", default=os.environ.get("TELEGRAM_CHAT_ID"))
    parser.add_argument("--telegram-token", default=os.environ.get("TELEGRAM_BOT_TOKEN"))
    parser.add_argument(
        "--include-options-chain",
        action="store_true",
        help="Try to include exact FMP option contracts when available.",
    )
    parser.add_argument(
        "--print-message",
        action="store_true",
        help="Print the Telegram message to stdout after generation.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        report_path, telegram_text, payload = build_report(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote report: {report_path}")
    print(f"Market regime: {payload['market']['regime']} | VIX {payload['market']['vix']:.2f}")
    if args.print_message:
        print("\n" + telegram_text)

    if args.send_telegram:
        if not args.telegram_token:
            print("ERROR: TELEGRAM_BOT_TOKEN is not set.", file=sys.stderr)
            return 2
        if not args.telegram_chat_id:
            wrapped = textwrap.fill(
                "ERROR: TELEGRAM_CHAT_ID is not set and no --telegram-chat-id was provided. "
                "Report generation succeeded, but Telegram delivery needs an explicit destination.",
                width=100,
            )
            print(wrapped, file=sys.stderr)
            return 2
        try:
            response = send_telegram(telegram_text, args.telegram_chat_id, args.telegram_token)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            print(f"ERROR: Telegram send failed ({exc.code}): {body}", file=sys.stderr)
            return 3
        except (urllib.error.URLError, TimeoutError) as exc:
            print(f"ERROR: Telegram send failed: {exc}", file=sys.stderr)
            return 3
        print(f"Telegram send ok: {response.get('ok')} message_id={response.get('result', {}).get('message_id')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
