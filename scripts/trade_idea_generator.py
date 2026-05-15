#!/usr/bin/env python3
"""Generate daily trade ideas from portfolio/watchlist context and send Telegram.

The generator reads the repository's current portfolio and watchlist markdown,
fetches live market/options data, ranks short-premium candidates, writes a
markdown report, and optionally sends the top ideas through Telegram.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


WORKSPACE = Path(__file__).resolve().parent.parent
FMP_BASE = "https://financialmodelingprep.com/api/v3"
MASSIVE_BASE = "https://api.massive.com/v3"
DEFAULT_CHAT_ID_PATH = WORKSPACE / "outputs" / "csp-daily-scan-fixed.json"
EXCLUDED_TICKERS = {"FFOLX"}


@dataclass
class UniverseEntry:
    ticker: str
    source: str
    score: Optional[float] = None
    grade: Optional[str] = None
    company: Optional[str] = None
    status: Optional[str] = None
    weight: Optional[float] = None


@dataclass
class OptionIdea:
    ticker: str
    source: str
    strategy: str
    strike: float
    expiration: str
    dte: int
    bid: float
    ask: float
    delta: Optional[float]
    iv: Optional[float]
    open_interest: int
    volume: int
    current_price: float
    annualized_return: float
    breakeven: float
    cushion_pct: float
    score: float
    rationale: str
    earnings_date: Optional[str]


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _clean_money(value: str) -> Optional[float]:
    cleaned = value.replace("$", "").replace(",", "").replace("%", "").strip()
    if not cleaned or cleaned in {"-", "—"}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_portfolio(path: Path) -> List[UniverseEntry]:
    text = _read_text(path)
    entries: List[UniverseEntry] = []
    in_positions = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("## Current Positions"):
            in_positions = True
            continue
        if in_positions and line.startswith("## "):
            break
        if not in_positions or not line.startswith("|"):
            continue
        if "SYMBOL" in line or set(line.replace("|", "").strip()) <= {"-"}:
            continue

        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 9:
            continue
        ticker = cells[0].upper()
        if not re.fullmatch(r"[A-Z.]{1,6}", ticker) or ticker in EXCLUDED_TICKERS:
            continue
        weight = _clean_money(cells[8])
        entries.append(
            UniverseEntry(
                ticker=ticker,
                source="portfolio",
                weight=weight,
                company=ticker,
            )
        )
    return entries


def parse_watchlist(path: Path) -> List[UniverseEntry]:
    text = _read_text(path)
    entries: List[UniverseEntry] = []
    in_watchlist = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("## Watchlist Tickers"):
            in_watchlist = True
            continue
        if in_watchlist and line.startswith("## "):
            break
        if not in_watchlist or not line.startswith("|"):
            continue
        if "Ticker" in line or set(line.replace("|", "").strip()) <= {"-"}:
            continue

        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 5:
            continue
        ticker = cells[0].upper()
        if not re.fullmatch(r"[A-Z.]{1,6}", ticker) or ticker in EXCLUDED_TICKERS:
            continue
        score = _clean_money(cells[1])
        grade = re.sub(r"[*`]", "", cells[2]).strip() or None
        entries.append(
            UniverseEntry(
                ticker=ticker,
                source="watchlist",
                score=score,
                grade=grade,
                company=cells[3] or ticker,
                status=cells[4] or None,
            )
        )
    return entries


def merge_universe(entries: Iterable[UniverseEntry]) -> Dict[str, UniverseEntry]:
    merged: Dict[str, UniverseEntry] = {}
    for entry in entries:
        ticker = entry.ticker.upper()
        existing = merged.get(ticker)
        if existing is None:
            merged[ticker] = entry
            continue
        sources = set(existing.source.split("+")) | set(entry.source.split("+"))
        existing.source = "+".join(sorted(sources))
        existing.score = existing.score if existing.score is not None else entry.score
        existing.grade = existing.grade or entry.grade
        existing.company = existing.company or entry.company
        existing.status = existing.status or entry.status
        existing.weight = existing.weight if existing.weight is not None else entry.weight
    return merged


def load_key_from_docs(label: str) -> Optional[str]:
    """Read existing command docs for keys without adding secrets to this script."""
    options_doc = _read_text(WORKSPACE / ".claude" / "commands" / "options-scan.md")
    patterns = {
        "fmp": r"FMP API\*\* \(key:\s*`?([A-Za-z0-9_-]+)`?\)",
        "massive": r"Massive\.com API\*\* \(key:\s*`?([A-Za-z0-9_-]+)`?\)",
    }
    match = re.search(patterns[label], options_doc)
    return match.group(1) if match else None


def get_fmp_key() -> str:
    key = os.environ.get("FMP_API_KEY") or load_key_from_docs("fmp")
    if not key:
        raise RuntimeError("FMP_API_KEY is not set and no workspace FMP key was found.")
    return key


def get_massive_key() -> Optional[str]:
    return os.environ.get("MASSIVE_API_KEY") or os.environ.get("POLYGON_API_KEY") or load_key_from_docs("massive")


def http_json(url: str, timeout: int = 20, retries: int = 2) -> Any:
    last_error: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            req = Request(url, headers={"User-Agent": "AltamiraTradeIdeaGenerator/1.0"})
            with urlopen(req, timeout=timeout) as response:
                payload = response.read().decode("utf-8")
                return json.loads(payload) if payload else None
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"HTTP request failed: {url}: {last_error}")


def fmp_get(endpoint: str, params: Dict[str, Any], api_key: str) -> Any:
    query = {**params, "apikey": api_key}
    return http_json(f"{FMP_BASE}/{endpoint}?{urlencode(query)}")


def fetch_quotes(tickers: Sequence[str], api_key: str) -> Dict[str, Dict[str, Any]]:
    quotes: Dict[str, Dict[str, Any]] = {}
    for start in range(0, len(tickers), 50):
        batch = [ticker for ticker in tickers[start : start + 50] if ticker]
        if not batch:
            continue
        data = fmp_get(f"quote/{','.join(batch)}", {}, api_key)
        if isinstance(data, list):
            for item in data:
                symbol = str(item.get("symbol", "")).upper()
                if symbol:
                    quotes[symbol] = item
    return quotes


def fetch_upcoming_earnings(tickers: Sequence[str], api_key: str, horizon_days: int = 45) -> Dict[str, str]:
    today = date.today()
    end = today + timedelta(days=horizon_days)
    params = {"from": today.isoformat(), "to": end.isoformat()}
    data = fmp_get("earning_calendar", params, api_key)
    wanted = set(tickers)
    out: Dict[str, str] = {}
    if isinstance(data, list):
        for item in data:
            symbol = str(item.get("symbol", "")).upper()
            if symbol in wanted and symbol not in out:
                out[symbol] = str(item.get("date", ""))[:10]
    return out


def fetch_vix(api_key: str) -> Tuple[Optional[float], str, int]:
    data = fmp_get("quote/%5EVIX", {}, api_key)
    vix = None
    if isinstance(data, list) and data:
        raw = data[0].get("price")
        try:
            vix = float(raw)
        except (TypeError, ValueError):
            vix = None
    if vix is None:
        return None, "UNKNOWN", 75
    if vix < 15:
        return vix, "LOW", 75
    if vix <= 25:
        return vix, "NORMAL", 100
    if vix <= 35:
        return vix, "ELEVATED", 50
    return vix, "CRISIS", 25


def calc_dte(expiration: str) -> Optional[int]:
    if not expiration:
        return None
    try:
        exp = datetime.strptime(expiration[:10], "%Y-%m-%d").date()
    except ValueError:
        return None
    return (exp - date.today()).days


def normalize_massive_contract(raw: Dict[str, Any]) -> Dict[str, Any]:
    details = raw.get("details") or {}
    greeks = raw.get("greeks") or {}
    quote = raw.get("last_quote") or {}
    day = raw.get("day") or {}
    return {
        "strike": details.get("strike_price") or raw.get("strike"),
        "expiration": details.get("expiration_date") or raw.get("expiration"),
        "contract_type": details.get("contract_type") or raw.get("contract_type"),
        "bid": quote.get("bid") or raw.get("bid") or 0,
        "ask": quote.get("ask") or raw.get("ask") or 0,
        "delta": greeks.get("delta") if greeks.get("delta") is not None else raw.get("delta"),
        "iv": raw.get("implied_volatility") or raw.get("impliedVolatility") or raw.get("iv"),
        "open_interest": raw.get("open_interest") or raw.get("openInterest") or 0,
        "volume": day.get("volume") or raw.get("volume") or raw.get("totalVolume") or 0,
    }


def normalize_fmp_contract(raw: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "strike": raw.get("strike") or raw.get("strikePrice"),
        "expiration": raw.get("expiration") or raw.get("expirationDate"),
        "contract_type": raw.get("type") or raw.get("putCall") or raw.get("side"),
        "bid": raw.get("bid") or raw.get("bidPrice") or 0,
        "ask": raw.get("ask") or raw.get("askPrice") or 0,
        "delta": raw.get("delta") or (raw.get("greeks") or {}).get("delta"),
        "iv": raw.get("impliedVolatility") or raw.get("iv"),
        "open_interest": raw.get("openInterest") or raw.get("open_interest") or 0,
        "volume": raw.get("volume") or raw.get("totalVolume") or 0,
    }


def fetch_massive_puts(ticker: str, massive_key: str) -> List[Dict[str, Any]]:
    start = (date.today() + timedelta(days=20)).isoformat()
    end = (date.today() + timedelta(days=60)).isoformat()
    params = {
        "apiKey": massive_key,
        "contract_type": "put",
        "expiration_date.gte": start,
        "expiration_date.lte": end,
        "limit": 250,
    }
    url = f"{MASSIVE_BASE}/snapshot/options/{ticker}?{urlencode(params)}"
    data = http_json(url, timeout=20, retries=1)
    if not isinstance(data, dict):
        return []
    results = data.get("results") or []
    return [normalize_massive_contract(item) for item in results if isinstance(item, dict)]


def fetch_fmp_puts(ticker: str, api_key: str) -> List[Dict[str, Any]]:
    url = f"https://financialmodelingprep.com/api/v4/options-chain/{ticker}?{urlencode({'apikey': api_key})}"
    try:
        data = http_json(url, timeout=20, retries=1)
    except RuntimeError:
        return []
    if not isinstance(data, list):
        return []
    normalized = [normalize_fmp_contract(item) for item in data if isinstance(item, dict)]
    return [item for item in normalized if str(item.get("contract_type", "")).lower() == "put"]


def grade_bonus(entry: UniverseEntry) -> float:
    grade = (entry.grade or "").replace("+", "").replace("-", "").upper()
    if grade == "A":
        return 8
    if grade == "B":
        return 6
    if grade == "C":
        return 2
    if grade in {"D", "F"}:
        return -8
    if entry.score is not None:
        return max(-6, min(8, (entry.score - 50) / 3))
    return 2 if "portfolio" in entry.source else 0


def score_contract(
    contract: Dict[str, Any],
    entry: UniverseEntry,
    quote: Dict[str, Any],
    earnings_date: Optional[str],
) -> Optional[OptionIdea]:
    try:
        strike = float(contract.get("strike"))
        bid = float(contract.get("bid") or 0)
        ask = float(contract.get("ask") or 0)
        price = float(quote.get("price") or 0)
        open_interest = int(contract.get("open_interest") or 0)
        volume = int(contract.get("volume") or 0)
    except (TypeError, ValueError):
        return None

    expiration = str(contract.get("expiration") or "")
    dte = calc_dte(expiration)
    if not dte or dte < 20 or dte > 60 or price <= 0:
        return None
    if earnings_date and earnings_date <= expiration[:10]:
        return None
    if bid <= 0 or open_interest < 25:
        return None

    raw_delta = contract.get("delta")
    delta = None
    try:
        delta = float(raw_delta) if raw_delta is not None else None
    except (TypeError, ValueError):
        delta = None
    abs_delta = abs(delta) if delta is not None else None
    if abs_delta is not None and not 0.15 <= abs_delta <= 0.35:
        return None

    if not price * 0.75 <= strike <= price * 0.98:
        return None

    annualized_return = (bid / strike) * (365 / dte) * 100
    breakeven = strike - bid
    cushion_pct = ((price - breakeven) / price) * 100
    spread_pct = ((ask - bid) / ((ask + bid) / 2) * 100) if ask and ask > bid else 10

    return_score = max(0.0, min(35.0, annualized_return * 1.1))
    cushion_score = max(0.0, min(20.0, cushion_pct * 1.25))
    liquidity_score = max(0.0, min(15.0, (open_interest / 500) * 10 + (volume / 100) * 5))
    delta_score = 10.0
    if abs_delta is not None:
        delta_score = max(0.0, 10 - abs(abs_delta - 0.22) * 45)
    spread_penalty = 0 if spread_pct <= 10 else min(10, (spread_pct - 10) / 2)
    trend_bonus = 0.0
    try:
        sma50 = float(quote.get("priceAvg50") or 0)
        if sma50 and price > sma50:
            trend_bonus += 6
        day_change = float(quote.get("changesPercentage") or 0)
        if day_change > 5:
            trend_bonus -= 4
    except (TypeError, ValueError):
        pass
    total_score = (
        return_score
        + cushion_score
        + liquidity_score
        + delta_score
        + trend_bonus
        + grade_bonus(entry)
        - spread_penalty
    )

    if total_score < 30:
        return None

    iv = contract.get("iv")
    try:
        iv_float = float(iv) if iv is not None else None
    except (TypeError, ValueError):
        iv_float = None

    rationale_bits = []
    if cushion_pct >= 8:
        rationale_bits.append(f"{cushion_pct:.1f}% breakeven cushion")
    if annualized_return >= 15:
        rationale_bits.append(f"{annualized_return:.1f}% annualized premium yield")
    if entry.grade:
        rationale_bits.append(f"watchlist grade {entry.grade}")
    if "portfolio" in entry.source:
        rationale_bits.append("existing holding")
    rationale = "; ".join(rationale_bits) or "balanced premium, liquidity, and trend score"

    return OptionIdea(
        ticker=entry.ticker,
        source=entry.source,
        strategy="Cash-secured put",
        strike=strike,
        expiration=expiration[:10],
        dte=dte,
        bid=bid,
        ask=ask,
        delta=delta,
        iv=iv_float,
        open_interest=open_interest,
        volume=volume,
        current_price=price,
        annualized_return=annualized_return,
        breakeven=breakeven,
        cushion_pct=cushion_pct,
        score=round(total_score, 1),
        rationale=rationale,
        earnings_date=earnings_date,
    )


def rank_universe_for_options(
    universe: Dict[str, UniverseEntry],
    quotes: Dict[str, Dict[str, Any]],
    max_tickers: int,
) -> List[UniverseEntry]:
    ranked: List[Tuple[float, UniverseEntry]] = []
    for ticker, entry in universe.items():
        quote = quotes.get(ticker)
        if not quote:
            continue
        score = 0.0
        score += grade_bonus(entry)
        if "portfolio" in entry.source:
            score += 3
        if entry.weight is not None and entry.weight < 5:
            score += 2
        try:
            price = float(quote.get("price") or 0)
            sma50 = float(quote.get("priceAvg50") or 0)
            year_high = float(quote.get("yearHigh") or 0)
            day_change = float(quote.get("changesPercentage") or 0)
            if sma50 and price > sma50:
                score += 5
            if year_high and price < year_high * 0.98:
                score += 2
            if day_change > 6:
                score -= 5
        except (TypeError, ValueError):
            pass
        ranked.append((score, entry))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [entry for _, entry in ranked[:max_tickers]]


def generate_ideas(max_tickers: int, max_ideas: int) -> Tuple[List[OptionIdea], Dict[str, Any]]:
    fmp_key = get_fmp_key()
    massive_key = get_massive_key()

    portfolio = parse_portfolio(WORKSPACE / "context" / "portfolio-details.md")
    watchlist = parse_watchlist(WORKSPACE / "context" / "watchlist.md")
    universe = merge_universe([*portfolio, *watchlist])
    tickers = sorted(universe)
    if not tickers:
        raise RuntimeError("No portfolio/watchlist tickers found.")

    quotes = fetch_quotes(tickers, fmp_key)
    earnings = fetch_upcoming_earnings(tickers, fmp_key)
    vix, regime, sizing_pct = fetch_vix(fmp_key)
    scan_targets = rank_universe_for_options(universe, quotes, max_tickers=max_tickers)

    ideas: List[OptionIdea] = []
    source_counts = {"massive": 0, "fmp": 0, "failed": 0}
    for entry in scan_targets:
        quote = quotes.get(entry.ticker)
        if not quote:
            continue
        contracts: List[Dict[str, Any]] = []
        if massive_key:
            try:
                contracts = fetch_massive_puts(entry.ticker, massive_key)
                source_counts["massive"] += 1 if contracts else 0
            except RuntimeError:
                contracts = []
        if not contracts:
            contracts = fetch_fmp_puts(entry.ticker, fmp_key)
            source_counts["fmp"] += 1 if contracts else 0
        if not contracts:
            source_counts["failed"] += 1
            continue
        for contract in contracts:
            idea = score_contract(contract, entry, quote, earnings.get(entry.ticker))
            if idea:
                ideas.append(idea)

    ideas.sort(key=lambda item: item.score, reverse=True)
    deduped: List[OptionIdea] = []
    seen_tickers = set()
    for idea in ideas:
        if idea.ticker in seen_tickers:
            continue
        seen_tickers.add(idea.ticker)
        deduped.append(idea)
        if len(deduped) >= max_ideas:
            break

    context = {
        "portfolio_count": len(portfolio),
        "watchlist_count": len(watchlist),
        "universe_count": len(tickers),
        "quoted_count": len(quotes),
        "scanned_count": len(scan_targets),
        "source_counts": source_counts,
        "vix": vix,
        "regime": regime,
        "sizing_pct": sizing_pct,
        "earnings_exclusions": {ticker: dt for ticker, dt in earnings.items() if ticker in {e.ticker for e in scan_targets}},
        "scan_targets": [entry.ticker for entry in scan_targets],
    }
    return deduped, context


def fmt_money(value: float) -> str:
    return f"${value:,.2f}"


def write_report(ideas: Sequence[OptionIdea], context: Dict[str, Any], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    out_path = out_dir / f"trade-idea-generator-{today}.md"
    lines = [
        f"# Trade Idea Generator — {today}",
        "",
        "Generated from the current repository portfolio and watchlist context.",
        "",
        "## Market Regime",
        "",
        f"- VIX: {context['vix']:.2f}" if context.get("vix") is not None else "- VIX: unavailable",
        f"- Regime: {context.get('regime', 'UNKNOWN')}",
        f"- Suggested option sizing: {context.get('sizing_pct', 75)}% of normal risk budget",
        "- Earnings rule: excludes contracts expiring after a known earnings date in the scan window",
        "",
        "## Universe",
        "",
        f"- Portfolio tickers: {context['portfolio_count']}",
        f"- Watchlist tickers: {context['watchlist_count']}",
        f"- Combined unique tickers: {context['universe_count']}",
        f"- Quotes retrieved: {context['quoted_count']}",
        f"- Option chains scanned: {context['scanned_count']} tickers",
        f"- Chain sources: {context['source_counts']}",
        "",
        "## Top Trade Ideas",
        "",
    ]

    if not ideas:
        lines.extend(
            [
                "No qualifying trade ideas passed the liquidity, DTE, delta, premium, and risk filters today.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "| Rank | Ticker | Source | Strategy | Contract | Credit | Delta | DTE | Breakeven | Ann. Yield | Score | Rationale |",
                "|------|--------|--------|----------|----------|--------|-------|-----|-----------|------------|-------|-----------|",
            ]
        )
        for idx, idea in enumerate(ideas, start=1):
            delta = f"{idea.delta:.3f}" if idea.delta is not None else "N/A"
            contract = f"{idea.strike:g}P {idea.expiration}"
            lines.append(
                "| {rank} | {ticker} | {source} | {strategy} | {contract} | {credit} | {delta} | {dte} | {breakeven} | {yield_pct:.1f}% | {score:.1f} | {rationale} |".format(
                    rank=idx,
                    ticker=idea.ticker,
                    source=idea.source,
                    strategy=idea.strategy,
                    contract=contract,
                    credit=fmt_money(idea.bid),
                    delta=delta,
                    dte=idea.dte,
                    breakeven=fmt_money(idea.breakeven),
                    yield_pct=idea.annualized_return,
                    score=idea.score,
                    rationale=idea.rationale,
                )
            )
        lines.append("")

    if context.get("earnings_exclusions"):
        lines.extend(["## Earnings Within Scan Window", ""])
        for ticker, earnings_date in sorted(context["earnings_exclusions"].items()):
            lines.append(f"- {ticker}: {earnings_date}")
        lines.append("")

    lines.extend(
        [
            "## Risk Notes",
            "",
            "- Trade ideas are research outputs, not orders.",
            "- Confirm live bid/ask, liquidity, earnings dates, portfolio exposure, and risk limits before entry.",
            "- Standard management: consider closing short premium at 50% of max profit; define a stop or adjustment trigger before entry.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def telegram_chat_id_from_workspace() -> Optional[str]:
    env_chat = os.environ.get("TELEGRAM_CHAT_ID")
    if env_chat:
        return env_chat
    try:
        payload = json.loads(_read_text(DEFAULT_CHAT_ID_PATH))
    except json.JSONDecodeError:
        return None
    for node in payload.get("nodes", []):
        if node.get("name") == "Send Telegram Alert":
            raw = (node.get("parameters") or {}).get("chatId")
            if isinstance(raw, str):
                return raw.lstrip("=")
    return None


def build_telegram_message(ideas: Sequence[OptionIdea], context: Dict[str, Any], report_path: Path) -> str:
    today = date.today().isoformat()
    vix_text = f"{context['vix']:.1f}" if context.get("vix") is not None else "N/A"
    lines = [
        f"Altamira Trade Ideas - {today}",
        f"Universe: {context['universe_count']} portfolio/watchlist tickers | VIX {vix_text} ({context.get('regime', 'UNKNOWN')})",
        "Earnings filter: excludes contracts expiring after known earnings dates.",
        "",
    ]
    if not ideas:
        lines.extend(
            [
                "No qualifying CSP ideas passed filters today.",
                f"Scanned {context['scanned_count']} tickers; quotes retrieved for {context['quoted_count']}.",
            ]
        )
    else:
        for idx, idea in enumerate(ideas, start=1):
            delta = f"{idea.delta:.2f}" if idea.delta is not None else "N/A"
            lines.extend(
                [
                    f"{idx}. {idea.ticker} {idea.strike:g}P {idea.expiration}",
                    f"   Credit {fmt_money(idea.bid)} | Delta {delta} | DTE {idea.dte} | Ann. yield {idea.annualized_return:.1f}%",
                    f"   Breakeven {fmt_money(idea.breakeven)} ({idea.cushion_pct:.1f}% cushion) | Score {idea.score:.1f}",
                    f"   Why: {idea.rationale}",
                    "",
                ]
            )
    lines.extend(
        [
            "Risk: verify live chain, earnings, and allocation before entry. Research only; not an order.",
            f"Report: {report_path.as_posix()}",
        ]
    )
    return "\n".join(lines)


def send_telegram(message: str, token: str, chat_id: str) -> Dict[str, Any]:
    data = urlencode(
        {
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    req = Request(url, data=data, method="POST")
    with urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-tickers", type=int, default=16, help="Maximum tickers to fetch option chains for.")
    parser.add_argument("--max-ideas", type=int, default=5, help="Maximum ideas to include.")
    parser.add_argument("--out-dir", type=Path, default=WORKSPACE / "outputs")
    parser.add_argument("--send-telegram", action="store_true", help="Send the generated summary to Telegram.")
    parser.add_argument("--dry-run", action="store_true", help="Generate output but do not send Telegram.")
    args = parser.parse_args(argv)

    try:
        ideas, context = generate_ideas(max_tickers=args.max_tickers, max_ideas=args.max_ideas)
        report_path = write_report(ideas, context, args.out_dir)
        message = build_telegram_message(ideas, context, report_path)
        print(message)
        print(f"\nWrote report: {report_path}")

        if args.send_telegram and not args.dry_run:
            token = os.environ.get("TELEGRAM_BOT_TOKEN")
            chat_id = telegram_chat_id_from_workspace()
            if not token:
                raise RuntimeError("TELEGRAM_BOT_TOKEN is not set.")
            if not chat_id:
                raise RuntimeError("TELEGRAM_CHAT_ID is not set and no workspace chatId fallback was found.")
            response = send_telegram(message, token, chat_id)
            if not response.get("ok"):
                raise RuntimeError(f"Telegram send failed: {response}")
            print(f"Telegram message sent: message_id={response.get('result', {}).get('message_id')}")
        elif args.send_telegram and args.dry_run:
            print("Dry run: Telegram send skipped.")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
