#!/usr/bin/env python3
"""
Generate daily trade ideas from the current portfolio and watchlist.

The generator is intentionally aligned with the existing CSP Daily Scan workflow:
- Use repository context files as the universe source.
- Pull live quotes, VIX, earnings calendar, and options snapshots.
- Rank cash-secured put candidates by return, IV, liquidity, trend, and context.
- Write a markdown report and optionally send a concise Telegram alert.

Financial output is informational only and is not investment advice.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import textwrap
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import requests

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover - Python <3.9 fallback
    ZoneInfo = None  # type: ignore


WORKSPACE = Path(__file__).resolve().parent.parent
CONTEXT = WORKSPACE / "context"
OUTPUTS = WORKSPACE / "outputs"

DEFAULT_FMP_API_KEY = "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz"
DEFAULT_MASSIVE_API_KEY = "kEnhZTIYm_UZZSfpSPuYQgsW_kG0vPHp"

FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"
MASSIVE_BASE_URL = "https://api.massive.com/v3"

MAX_POSITION_PCT = 0.05
MAX_TOTAL_COLLATERAL_PCT = 0.20
MIN_DTE = 30
MAX_DTE = 45
MIN_ABS_DELTA = 0.20
MAX_ABS_DELTA = 0.30
MIN_OPEN_INTEREST = 20
MAX_IDEAS = 5


@dataclass
class UniverseItem:
    ticker: str
    source: str
    weight: Optional[float] = None
    watchlist_score: Optional[float] = None
    watchlist_grade: Optional[str] = None
    status: Optional[str] = None


def today_et() -> date:
    if ZoneInfo is None:
        return datetime.now(timezone.utc).date()
    return datetime.now(ZoneInfo("America/New_York")).date()


def money(value: Optional[float], decimals: int = 0) -> str:
    if value is None:
        return "N/A"
    return f"${value:,.{decimals}f}"


def pct(value: Optional[float], decimals: int = 1) -> str:
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}%"


def clean_cell(cell: str) -> str:
    return re.sub(r"\*\*|⭐", "", cell).strip()


def parse_markdown_table(path: Path, required_first_header: str) -> List[Dict[str, str]]:
    if not path.exists():
        return []

    lines = path.read_text(encoding="utf-8").splitlines()
    rows: List[Dict[str, str]] = []
    headers: Optional[List[str]] = None
    in_table = False

    for line in lines:
        if not line.startswith("|"):
            if in_table:
                break
            continue

        parts = [clean_cell(p) for p in line.strip().strip("|").split("|")]
        if not parts:
            continue

        if headers is None:
            if parts[0].upper() == required_first_header.upper():
                headers = parts
                in_table = True
            continue

        if all(set(part) <= {"-", ":"} for part in parts):
            continue

        if len(parts) != len(headers):
            continue

        rows.append(dict(zip(headers, parts)))

    return rows


def parse_float(text: str) -> Optional[float]:
    cleaned = re.sub(r"[^0-9.\-]", "", text or "")
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def load_portfolio_value() -> float:
    path = CONTEXT / "portfolio-details.md"
    if not path.exists():
        return 100_000.0
    match = re.search(r"\|\s*\*\*Total MKT VALUE\*\*\s*\|\s*\$?([0-9,]+)", path.read_text(encoding="utf-8"))
    if not match:
        return 100_000.0
    return float(match.group(1).replace(",", ""))


def load_universe() -> Dict[str, UniverseItem]:
    universe: Dict[str, UniverseItem] = {}

    for row in parse_markdown_table(CONTEXT / "portfolio-details.md", "SYMBOL"):
        ticker = row.get("SYMBOL", "").upper().strip()
        if not re.fullmatch(r"[A-Z]{1,5}", ticker):
            continue
        universe[ticker] = UniverseItem(
            ticker=ticker,
            source="Portfolio",
            weight=parse_float(row.get("WEIGHT", "")),
        )

    for row in parse_markdown_table(CONTEXT / "watchlist.md", "Ticker"):
        ticker = row.get("Ticker", "").upper().strip()
        if not re.fullmatch(r"[A-Z]{1,5}", ticker):
            continue
        score = parse_float(row.get("Score", ""))
        item = universe.get(ticker)
        if item is None:
            universe[ticker] = UniverseItem(
                ticker=ticker,
                source="Watchlist",
                watchlist_score=score,
                watchlist_grade=row.get("Grade") or None,
                status=row.get("Status") or None,
            )
        else:
            item.source = "Portfolio + Watchlist"
            item.watchlist_score = score
            item.watchlist_grade = row.get("Grade") or None
            item.status = row.get("Status") or None

    # Skip mutual funds and tickers unlikely to have equity option chains.
    universe.pop("FFOLX", None)
    return dict(sorted(universe.items()))


def request_json(url: str, *, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, timeout: int = 20) -> Any:
    response = requests.get(url, params=params, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.json()


def chunks(items: Sequence[str], size: int) -> Iterable[Sequence[str]]:
    for idx in range(0, len(items), size):
        yield items[idx : idx + size]


def fetch_quotes(tickers: Sequence[str], fmp_key: str) -> Dict[str, Dict[str, Any]]:
    quotes: Dict[str, Dict[str, Any]] = {}
    for group in chunks(list(tickers), 30):
        url = f"{FMP_BASE_URL}/quote/{','.join(group)}"
        data = request_json(url, params={"apikey": fmp_key})
        for item in data if isinstance(data, list) else []:
            symbol = item.get("symbol")
            if symbol:
                quotes[str(symbol).upper()] = item
    return quotes


def fetch_earnings(tickers: Sequence[str], fmp_key: str, start: date, days: int = 45) -> Dict[str, str]:
    end = start + timedelta(days=days)
    url = f"{FMP_BASE_URL}/earning_calendar"
    data = request_json(url, params={"from": start.isoformat(), "to": end.isoformat(), "apikey": fmp_key}, timeout=30)
    wanted = set(tickers)
    earnings: Dict[str, str] = {}
    for item in data if isinstance(data, list) else []:
        symbol = str(item.get("symbol", "")).upper()
        if symbol in wanted and item.get("date"):
            earnings[symbol] = str(item["date"])
    return earnings


def vix_regime(vix: Optional[float]) -> Tuple[str, int]:
    if vix is None:
        return "UNKNOWN", 75
    if vix < 15:
        return "LOW", 75
    if vix <= 25:
        return "NORMAL", 100
    if vix <= 35:
        return "ELEVATED", 50
    return "CRISIS", 25


def dte(expiration: str, as_of: date) -> Optional[int]:
    try:
        exp = datetime.strptime(expiration, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None
    return (exp - as_of).days


def normalize_option(raw: Dict[str, Any], as_of: date) -> Optional[Dict[str, Any]]:
    details = raw.get("details") or {}
    quote = raw.get("last_quote") or {}
    greeks = raw.get("greeks") or {}
    day = raw.get("day") or {}

    expiration = details.get("expiration_date") or raw.get("expiration_date")
    strike = details.get("strike_price") or raw.get("strike_price")
    if not expiration or strike is None:
        return None

    bid = quote.get("bid")
    ask = quote.get("ask")
    if bid is None:
        bid = raw.get("bid") or day.get("close") or 0
    if ask is None:
        ask = raw.get("ask") or 0

    return {
        "expiration": expiration,
        "dte": dte(str(expiration), as_of),
        "strike": float(strike),
        "bid": float(bid or 0),
        "ask": float(ask or 0),
        "delta": greeks.get("delta") if greeks.get("delta") is not None else raw.get("delta"),
        "theta": greeks.get("theta") if greeks.get("theta") is not None else raw.get("theta"),
        "iv": raw.get("implied_volatility") or raw.get("impliedVolatility"),
        "open_interest": int(raw.get("open_interest") or raw.get("openInterest") or 0),
        "volume": int(day.get("volume") or raw.get("volume") or 0),
        "ticker": details.get("ticker") or raw.get("ticker"),
    }


def fetch_put_options(ticker: str, massive_key: str, as_of: date) -> List[Dict[str, Any]]:
    start = as_of + timedelta(days=MIN_DTE)
    end = as_of + timedelta(days=MAX_DTE)
    url = f"{MASSIVE_BASE_URL}/snapshot/options/{ticker}"
    headers = {"Authorization": f"Bearer {massive_key}"}
    params = {
        "contract_type": "put",
        "expiration_date.gte": start.isoformat(),
        "expiration_date.lte": end.isoformat(),
        "limit": 250,
    }

    data = request_json(url, params=params, headers=headers, timeout=25)
    results = data.get("results", []) if isinstance(data, dict) else []
    normalized = [normalize_option(item, as_of) for item in results]
    return [item for item in normalized if item is not None]


def trend_score(quote: Dict[str, Any]) -> float:
    price = quote.get("price") or 0
    avg50 = quote.get("priceAvg50") or 0
    year_high = quote.get("yearHigh") or 0
    score = 50.0
    if price and avg50:
        score += 20 if price >= avg50 else -20
    if price and year_high:
        score += min(30, max(0, (price / year_high) * 30))
    return max(0, min(100, score))


def context_score(item: UniverseItem) -> float:
    score = 50.0
    if item.source.startswith("Portfolio"):
        score += 5
    if item.watchlist_score is not None:
        score += max(-10, min(15, (item.watchlist_score - 50) / 2))
    if item.status and "top candidate" in item.status.lower():
        score += 8
    return max(0, min(100, score))


def screen_quality(quote: Dict[str, Any]) -> List[str]:
    reasons: List[str] = []
    price = quote.get("price")
    avg50 = quote.get("priceAvg50")
    change_pct = quote.get("changesPercentage")
    volume = quote.get("volume")

    if not price or price < 20:
        reasons.append("price below $20 or missing")
    if avg50 and price and price < avg50:
        reasons.append(f"below 50-day SMA ({money(price, 2)} < {money(avg50, 2)})")
    if change_pct and change_pct > 8:
        reasons.append(f"single-day move too extended ({change_pct:.1f}%)")
    if not volume or volume < 100_000:
        reasons.append("low/no volume")
    return reasons


def score_options(
    universe: Dict[str, UniverseItem],
    quotes: Dict[str, Dict[str, Any]],
    earnings: Dict[str, str],
    massive_key: str,
    portfolio_value: float,
    sizing_pct: int,
    as_of: date,
) -> Tuple[List[Dict[str, Any]], List[str], List[Tuple[str, str]]]:
    opportunities: List[Dict[str, Any]] = []
    excluded: List[str] = []
    fetch_errors: List[Tuple[str, str]] = []

    max_allocation = portfolio_value * MAX_POSITION_PCT * sizing_pct / 100

    for ticker, item in universe.items():
        quote = quotes.get(ticker)
        if not quote:
            excluded.append(f"{ticker}: no quote data")
            continue

        reasons = screen_quality(quote)
        if reasons:
            excluded.append(f"{ticker}: {', '.join(reasons)}")
            continue

        if ticker in earnings:
            excluded.append(f"{ticker}: earnings {earnings[ticker]} within {MAX_DTE}D window")
            continue

        try:
            contracts = fetch_put_options(ticker, massive_key, as_of)
        except Exception as exc:
            fetch_errors.append((ticker, str(exc)[:120]))
            continue

        for contract in contracts:
            contract_dte = contract.get("dte")
            strike = contract["strike"]
            bid = contract["bid"]
            delta = contract.get("delta")
            oi = contract.get("open_interest") or 0

            if contract_dte is None or contract_dte < MIN_DTE or contract_dte > MAX_DTE:
                continue
            if delta is None or not (MIN_ABS_DELTA <= abs(float(delta)) <= MAX_ABS_DELTA):
                continue
            if bid <= 0.05 or oi < MIN_OPEN_INTEREST:
                continue

            collateral_per_contract = strike * 100
            max_contracts = int(max_allocation // collateral_per_contract)
            if max_contracts < 1:
                continue

            annualized_return = (bid / strike) * (365 / contract_dte) * 100
            iv = contract.get("iv")
            if iv is not None:
                iv_rank_proxy = max(0, min(100, ((float(iv) - 0.15) / 0.35) * 100))
            else:
                iv_rank_proxy = max(0, min(100, (bid / strike) * 1500))
            if iv_rank_proxy < 25:
                continue

            return_score = max(0, min(100, (annualized_return - 8) / 32 * 100))
            liquidity_score = max(0, min(100, (oi / 1000) * 50 + ((contract.get("volume") or 0) / 100) * 50))
            technical_score = trend_score(quote)
            ctx_score = context_score(item)
            composite = (
                return_score * 0.35
                + iv_rank_proxy * 0.25
                + liquidity_score * 0.20
                + technical_score * 0.10
                + ctx_score * 0.10
            )

            premium = bid * max_contracts * 100
            total_collateral = collateral_per_contract * max_contracts
            opportunities.append(
                {
                    "ticker": ticker,
                    "source": item.source,
                    "status": item.status,
                    "current_price": quote.get("price"),
                    "strike": strike,
                    "expiration": contract["expiration"],
                    "dte": contract_dte,
                    "bid": bid,
                    "ask": contract.get("ask") or 0,
                    "delta": float(delta),
                    "theta": contract.get("theta"),
                    "iv": iv,
                    "open_interest": oi,
                    "volume": contract.get("volume") or 0,
                    "annualized_return": annualized_return,
                    "breakeven": strike - bid,
                    "max_contracts": max_contracts,
                    "premium": premium,
                    "collateral": total_collateral,
                    "score": composite,
                    "return_score": return_score,
                    "iv_score": iv_rank_proxy,
                    "liquidity_score": liquidity_score,
                    "trend_score": technical_score,
                    "context_score": ctx_score,
                    "profit_target": bid * 0.50,
                    "stop_loss": bid * 2.00,
                }
            )

    opportunities.sort(key=lambda item: item["score"], reverse=True)

    selected: List[Dict[str, Any]] = []
    ticker_seen: set[str] = set()
    total_collateral = 0.0
    max_total_collateral = portfolio_value * MAX_TOTAL_COLLATERAL_PCT * sizing_pct / 100
    for opp in opportunities:
        if opp["ticker"] in ticker_seen:
            continue
        if total_collateral + opp["collateral"] > max_total_collateral:
            continue
        opp["rank"] = len(selected) + 1
        selected.append(opp)
        ticker_seen.add(opp["ticker"])
        total_collateral += opp["collateral"]
        if len(selected) >= MAX_IDEAS:
            break

    return selected, excluded, fetch_errors


def build_equity_watchlist(
    universe: Dict[str, UniverseItem],
    quotes: Dict[str, Dict[str, Any]],
    earnings: Dict[str, str],
) -> List[Dict[str, Any]]:
    ideas: List[Dict[str, Any]] = []
    for ticker, item in universe.items():
        quote = quotes.get(ticker)
        if not quote:
            continue
        price = quote.get("price")
        avg50 = quote.get("priceAvg50")
        avg200 = quote.get("priceAvg200")
        if not price or not avg50:
            continue
        distance_50 = ((price - avg50) / avg50) * 100 if avg50 else None
        distance_200 = ((price - avg200) / avg200) * 100 if avg200 else None
        score = trend_score(quote) * 0.5 + context_score(item) * 0.5
        if ticker in earnings:
            score -= 10
        ideas.append(
            {
                "ticker": ticker,
                "source": item.source,
                "status": item.status,
                "price": price,
                "change_pct": quote.get("changesPercentage"),
                "distance_50": distance_50,
                "distance_200": distance_200,
                "year_high": quote.get("yearHigh"),
                "earnings": earnings.get(ticker),
                "score": score,
            }
        )
    ideas.sort(key=lambda item: item["score"], reverse=True)
    return ideas[:8]


def render_report(
    as_of: date,
    portfolio_value: float,
    universe: Dict[str, UniverseItem],
    quotes: Dict[str, Dict[str, Any]],
    vix: Optional[float],
    regime: str,
    sizing_pct: int,
    top_options: List[Dict[str, Any]],
    equity_watchlist: List[Dict[str, Any]],
    excluded: List[str],
    fetch_errors: List[Tuple[str, str]],
) -> str:
    lines: List[str] = [
        f"# Trade Idea Generator - {as_of.isoformat()}",
        "",
        "> Informational output only; not investment advice. Validate liquidity, earnings dates, and risk limits before placing any trade.",
        "",
        "## Summary",
        "",
        f"- **Universe:** {len(universe)} portfolio/watchlist tickers",
        f"- **Portfolio value used for sizing:** {money(portfolio_value)}",
        f"- **VIX:** {vix:.2f} ({regime})" if vix is not None else f"- **VIX:** N/A ({regime})",
        f"- **Sizing multiplier:** {sizing_pct}%",
        f"- **Max per idea:** {pct(MAX_POSITION_PCT * 100)} of portfolio collateral before VIX adjustment",
        "",
        "## Top CSP Trade Ideas",
        "",
    ]

    if not top_options:
        lines.extend(["No qualifying 30-45 DTE, 20-30 delta CSP opportunities passed the filters.", ""])
    else:
        lines.append(
            "| Rank | Ticker | Source | Trade | Credit | Delta | DTE | Ann. Return | Breakeven | Contracts | Premium | Collateral | Score |"
        )
        lines.append(
            "|------|--------|--------|-------|--------|-------|-----|-------------|-----------|-----------|---------|------------|-------|"
        )
        for opp in top_options:
            trade = f"{opp['strike']:.0f}P {opp['expiration']}"
            lines.append(
                f"| {opp['rank']} | {opp['ticker']} | {opp['source']} | {trade} | "
                f"{money(opp['bid'], 2)} | {opp['delta']:.3f} | {opp['dte']} | "
                f"{pct(opp['annualized_return'], 1)} | {money(opp['breakeven'], 2)} | "
                f"{opp['max_contracts']} | {money(opp['premium'])} | {money(opp['collateral'])} | {opp['score']:.1f} |"
            )
        lines.extend(["", "### Management Rules", ""])
        for opp in top_options:
            lines.append(
                f"- **{opp['ticker']} {opp['strike']:.0f}P:** close near {money(opp['profit_target'], 2)} "
                f"(50% profit); stop/adjust near {money(opp['stop_loss'], 2)} (2x credit)."
            )
        lines.append("")

    lines.extend(["## Equity / Watchlist Momentum Checks", ""])
    if equity_watchlist:
        lines.append("| Ticker | Source | Price | Day % | vs 50D | vs 200D | Earnings | Note |")
        lines.append("|--------|--------|-------|-------|--------|---------|----------|------|")
        for item in equity_watchlist:
            note = item.get("status") or ("Existing holding" if item["source"].startswith("Portfolio") else "Watchlist")
            lines.append(
                f"| {item['ticker']} | {item['source']} | {money(item['price'], 2)} | "
                f"{pct(item.get('change_pct'), 1)} | {pct(item.get('distance_50'), 1)} | "
                f"{pct(item.get('distance_200'), 1)} | {item.get('earnings') or '-'} | {note} |"
            )
        lines.append("")

    if excluded:
        lines.extend(["## Key Exclusions", ""])
        for reason in excluded[:20]:
            lines.append(f"- {reason}")
        if len(excluded) > 20:
            lines.append(f"- ... {len(excluded) - 20} more exclusions")
        lines.append("")

    if fetch_errors:
        lines.extend(["## Data Gaps", ""])
        for ticker, error in fetch_errors[:15]:
            lines.append(f"- {ticker}: options fetch failed ({error})")
        if len(fetch_errors) > 15:
            lines.append(f"- ... {len(fetch_errors) - 15} more fetch errors")
        lines.append("")

    lines.extend(
        [
            "## Data Sources",
            "",
            "- Portfolio: `context/portfolio-details.md`",
            "- Watchlist: `context/watchlist.md`",
            "- Quotes and earnings: Financial Modeling Prep",
            "- Options snapshots: Massive.com",
            "",
        ]
    )
    return "\n".join(lines)


def telegram_message(as_of: date, vix: Optional[float], regime: str, sizing_pct: int, top_options: List[Dict[str, Any]], output_path: Path) -> str:
    lines = [
        f"TRADE IDEA GENERATOR - {as_of.isoformat()}",
        f"VIX: {vix:.1f} ({regime}) | Sizing: {sizing_pct}%" if vix is not None else f"VIX: N/A ({regime}) | Sizing: {sizing_pct}%",
        "",
    ]
    if not top_options:
        lines.append("No qualifying CSP opportunities passed today's filters.")
    else:
        for opp in top_options:
            lines.append(
                f"#{opp['rank']} {opp['ticker']} {opp['strike']:.0f}P {opp['expiration']} - "
                f"credit {money(opp['bid'], 2)}, delta {opp['delta']:.2f}, DTE {opp['dte']}, "
                f"ann {pct(opp['annualized_return'], 1)}, score {opp['score']:.1f}"
            )
            lines.append(
                f"  BE {money(opp['breakeven'], 2)} | contracts {opp['max_contracts']} | "
                f"premium {money(opp['premium'])} | collateral {money(opp['collateral'])}"
            )
    lines.extend(["", "Validate earnings/liquidity before trading.", f"Report: {output_path.name}"])
    return "\n".join(lines)


def send_telegram(text: str, bot_token: str, chat_id: str) -> Dict[str, Any]:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    response = requests.post(
        url,
        json={"chat_id": chat_id, "text": text, "disable_web_page_preview": True},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate portfolio/watchlist trade ideas and optionally send to Telegram.")
    parser.add_argument("--date", default=None, help="As-of date in YYYY-MM-DD format; defaults to America/New_York today.")
    parser.add_argument("--send-telegram", action="store_true", help="Send the compact output to Telegram.")
    parser.add_argument("--telegram-chat-id", default=os.environ.get("TELEGRAM_CHAT_ID"), help="Telegram channel/chat id.")
    parser.add_argument("--telegram-token", default=os.environ.get("TELEGRAM_BOT_TOKEN"), help="Telegram bot token.")
    parser.add_argument("--fmp-key", default=os.environ.get("FMP_API_KEY", DEFAULT_FMP_API_KEY), help="FMP API key.")
    parser.add_argument("--massive-key", default=os.environ.get("MASSIVE_API_KEY", DEFAULT_MASSIVE_API_KEY), help="Massive.com API key.")
    parser.add_argument("--out", default=None, help="Markdown output path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    as_of = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else today_et()
    OUTPUTS.mkdir(exist_ok=True)

    universe = load_universe()
    if not universe:
        print("No portfolio/watchlist universe found.", file=sys.stderr)
        return 1

    portfolio_value = load_portfolio_value()
    quote_symbols = sorted(set(universe) | {"SPY", "^VIX"})
    quotes = fetch_quotes(quote_symbols, args.fmp_key)
    vix = None
    if "^VIX" in quotes:
        vix = quotes["^VIX"].get("price")
    regime, sizing_pct = vix_regime(vix)
    earnings = fetch_earnings(list(universe), args.fmp_key, as_of, days=MAX_DTE)

    top_options, excluded, fetch_errors = score_options(
        universe=universe,
        quotes=quotes,
        earnings=earnings,
        massive_key=args.massive_key,
        portfolio_value=portfolio_value,
        sizing_pct=sizing_pct,
        as_of=as_of,
    )
    equity_watchlist = build_equity_watchlist(universe, quotes, earnings)

    report = render_report(
        as_of=as_of,
        portfolio_value=portfolio_value,
        universe=universe,
        quotes=quotes,
        vix=vix,
        regime=regime,
        sizing_pct=sizing_pct,
        top_options=top_options,
        equity_watchlist=equity_watchlist,
        excluded=excluded,
        fetch_errors=fetch_errors,
    )

    output_path = Path(args.out) if args.out else OUTPUTS / f"trade-idea-generator-{as_of.isoformat()}.md"
    if not output_path.is_absolute():
        output_path = WORKSPACE / output_path
    output_path.write_text(report + "\n", encoding="utf-8")

    telegram_text = telegram_message(as_of, vix, regime, sizing_pct, top_options, output_path)
    telegram_path = OUTPUTS / f"trade-idea-generator-telegram-{as_of.isoformat()}.txt"
    telegram_path.write_text(telegram_text + "\n", encoding="utf-8")

    print(f"Wrote report: {output_path.relative_to(WORKSPACE)}")
    print(f"Wrote Telegram text: {telegram_path.relative_to(WORKSPACE)}")
    print("")
    print(textwrap.shorten(telegram_text.replace("\n", " | "), width=500, placeholder=" ..."))

    if args.send_telegram:
        if not args.telegram_token:
            print("TELEGRAM_BOT_TOKEN is not set; cannot send.", file=sys.stderr)
            return 2
        if not args.telegram_chat_id:
            print("TELEGRAM_CHAT_ID/--telegram-chat-id is not set; cannot send.", file=sys.stderr)
            return 2
        result = send_telegram(telegram_text, args.telegram_token, args.telegram_chat_id)
        if not result.get("ok"):
            print(json.dumps(result, indent=2), file=sys.stderr)
            return 3
        print("Telegram send: ok")

    return 0


if __name__ == "__main__":
    sys.exit(main())
