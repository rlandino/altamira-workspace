#!/usr/bin/env python3
"""Generate portfolio/watchlist trade ideas and optionally send to Telegram.

The scanner is intentionally dependency-free so it can run from cron, Cursor
automation, or n8n-adjacent environments without package setup. It reads the
workspace portfolio and watchlist context, screens 30-45 DTE cash-secured put
ideas, writes a markdown report, and can deliver a concise Telegram alert.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKFLOW_CONFIGS = (
    ROOT / "outputs" / "csp-daily-scan-fixed.json",
    ROOT / "outputs" / "n8n-workflow-csp-daily-scan.json",
)
NON_OPTIONABLE = {"FFOLX"}
BLOCKED_WATCHLIST_STATUSES = {"Low Priority", "Avoid"}
INDEX_OR_ETF_TICKERS = {"SPY", "QQQ", "IWM", "DIA"}


def fetch_json(url: str, timeout: int = 15) -> Any:
    """Fetch JSON from a URL with a simple user agent."""
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "AltamiraTradeIdeaGenerator/1.0"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def post_json(url: str, payload: dict[str, Any], timeout: int = 15) -> Any:
    """POST a JSON payload and return the decoded JSON response."""
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "AltamiraTradeIdeaGenerator/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def load_text(path: Path) -> str:
    """Read a text file with a useful error if it is missing."""
    if not path.exists():
        raise FileNotFoundError(f"Required context file not found: {path}")
    return path.read_text(encoding="utf-8")


def parse_portfolio(text: str) -> tuple[float, list[str]]:
    """Parse portfolio market value and position symbols from context markdown."""
    value_match = re.search(r"Total MKT VALUE\*\* \| \$([0-9,]+)", text)
    portfolio_value = (
        float(value_match.group(1).replace(",", "")) if value_match else 100000.0
    )

    symbols: list[str] = []
    in_positions = False
    for line in text.splitlines():
        if line.startswith("## Current Positions"):
            in_positions = True
            continue
        if in_positions and line.startswith("**Totals:**"):
            break
        if not in_positions or not line.startswith("|"):
            continue
        if line.startswith("| SYMBOL") or line.startswith("|---"):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if parts and re.fullmatch(r"[A-Z][A-Z0-9.\-]{0,9}", parts[0]):
            symbols.append(parts[0])

    return portfolio_value, symbols


def parse_watchlist(text: str) -> dict[str, dict[str, Any]]:
    """Parse watchlist metadata from context markdown."""
    watchlist: dict[str, dict[str, Any]] = {}
    in_watchlist = False
    for line in text.splitlines():
        if line.startswith("## Watchlist Tickers"):
            in_watchlist = True
            continue
        if in_watchlist and line.startswith("---"):
            break
        if not in_watchlist or not line.startswith("|"):
            continue
        if line.startswith("| Ticker") or line.startswith("|---"):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) < 5 or not re.fullmatch(r"[A-Z][A-Z0-9.\-]{0,9}", parts[0]):
            continue
        score: float | None = None
        if parts[1] != "-":
            try:
                score = float(parts[1])
            except ValueError:
                score = None
        watchlist[parts[0]] = {
            "score": score,
            "grade": parts[2].replace("*", ""),
            "company": parts[3],
            "status": parts[4].replace("⭐ ", ""),
        }
    return watchlist


def parse_open_short_premium(text: str) -> set[str]:
    """Parse tickers with existing short-premium positions."""
    tickers: set[str] = set()
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        if line.startswith("| Ticker") or line.startswith("|---"):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if parts and re.fullmatch(r"[A-Z][A-Z0-9.\-]{0,9}", parts[0]):
            tickers.add(parts[0])
    return tickers


def extract_workflow_value(pattern: str, paths: tuple[Path, ...]) -> str | None:
    """Extract a configured value from existing workflow JSON files.

    Environment variables remain the preferred source. This fallback exists so
    the script can execute the repository's already-configured workflow state.
    """
    compiled = re.compile(pattern)
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        match = compiled.search(text)
        if match:
            return match.group(1)
    return None


def resolve_config(args: argparse.Namespace) -> dict[str, str | None]:
    """Resolve API and Telegram configuration from args, env, or workflow files."""
    workflow_paths = tuple(Path(p) for p in args.workflow_config) or DEFAULT_WORKFLOW_CONFIGS
    fmp_key = (
        args.fmp_api_key
        or os.environ.get("FMP_API_KEY")
        or extract_workflow_value(r'"value":\s*"=([A-Za-z0-9_\-]{20,})"', workflow_paths)
    )
    massive_key = (
        args.massive_api_key
        or os.environ.get("MASSIVE_API_KEY")
        or extract_workflow_value(r"MASSIVE_API_KEY\s*=\s*'([^']+)'", workflow_paths)
    )
    telegram_token = args.telegram_bot_token or os.environ.get("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = (
        args.telegram_chat_id
        or os.environ.get("TELEGRAM_CHAT_ID")
        or extract_workflow_value(r'"chatId":\s*"=?(-?\d+)"', workflow_paths)
    )
    return {
        "fmp_api_key": fmp_key,
        "massive_api_key": massive_key,
        "telegram_bot_token": telegram_token,
        "telegram_chat_id": telegram_chat_id,
    }


def quote_batch(symbols: list[str], api_key: str) -> dict[str, dict[str, Any]]:
    """Fetch FMP quotes for symbols in chunks."""
    quotes: dict[str, dict[str, Any]] = {}
    for index in range(0, len(symbols), 40):
        chunk = symbols[index : index + 40]
        encoded = ",".join(urllib.parse.quote(symbol, safe="") for symbol in chunk)
        url = f"https://financialmodelingprep.com/api/v3/quote/{encoded}?apikey={api_key}"
        try:
            data = fetch_json(url, timeout=20)
        except Exception as exc:  # noqa: BLE001 - report and continue per script goal
            print(f"WARN: quote fetch failed for {chunk}: {exc}", file=sys.stderr)
            continue
        if isinstance(data, list):
            for item in data:
                symbol = item.get("symbol")
                if symbol:
                    quotes[symbol] = item
    return quotes


def vix_regime(vix: float) -> tuple[str, int, str]:
    """Classify VIX into the strategy regime used by Altamira scans."""
    if vix < 15:
        return "LOW", 75, "Premium selling OK; keep selectivity because IV is low."
    if vix <= 25:
        return "NORMAL", 100, "CSPs and defined-risk put spreads acceptable."
    if vix <= 35:
        return "ELEVATED", 50, "Prefer defined-risk spreads; reduce size."
    return "CRISIS", 25, "Spreads only; minimal size; avoid naked options."


def fetch_earnings_exclusions(
    universe: list[str],
    api_key: str,
    today: dt.date,
    lookahead_days: int,
) -> dict[str, str]:
    """Fetch upcoming earnings dates and return universe tickers to exclude."""
    to_date = today + dt.timedelta(days=lookahead_days)
    params = urllib.parse.urlencode(
        {"from": today.isoformat(), "to": to_date.isoformat(), "apikey": api_key}
    )
    url = f"https://financialmodelingprep.com/api/v3/earning_calendar?{params}"
    exclusions: dict[str, str] = {}
    try:
        data = fetch_json(url, timeout=25)
    except Exception as exc:  # noqa: BLE001
        print(f"WARN: earnings fetch failed: {exc}", file=sys.stderr)
        return exclusions

    universe_set = set(universe)
    if isinstance(data, list):
        for item in data:
            symbol = item.get("symbol")
            if symbol in universe_set and symbol not in INDEX_OR_ETF_TICKERS:
                exclusions.setdefault(symbol, item.get("date", "unknown"))
    return exclusions


def massive_put_chain(
    ticker: str,
    price: float,
    api_key: str,
    from_date: dt.date,
    to_date: dt.date,
) -> list[dict[str, Any]]:
    """Fetch Massive.com put option snapshots in the target strike/DTE range."""
    params = {
        "contract_type": "put",
        "expiration_date.gte": from_date.isoformat(),
        "expiration_date.lte": to_date.isoformat(),
        "strike_price.gte": max(1, round(price * 0.78, 2)),
        "strike_price.lte": round(price * 1.02, 2),
        "limit": 250,
        "apiKey": api_key,
    }
    url: str | None = (
        f"https://api.massive.com/v3/snapshot/options/{ticker}?"
        + urllib.parse.urlencode(params)
    )
    results: list[dict[str, Any]] = []
    pages = 0
    while url and pages < 3:
        pages += 1
        try:
            data = fetch_json(url, timeout=25)
        except Exception as exc:  # noqa: BLE001
            print(f"WARN: options fetch failed for {ticker}: {exc}", file=sys.stderr)
            break
        results.extend(data.get("results") or [])
        next_url = data.get("next_url")
        if next_url:
            separator = "&" if "?" in next_url else "?"
            url = (
                next_url
                if "apiKey=" in next_url
                else next_url + separator + urllib.parse.urlencode({"apiKey": api_key})
            )
        else:
            url = None
    return results


def dte(expiration: str, today: dt.date) -> int | None:
    """Calculate days to expiration."""
    try:
        return (dt.date.fromisoformat(expiration) - today).days
    except (TypeError, ValueError):
        return None


def score_contract(
    *,
    ticker: str,
    source: str,
    quote: dict[str, Any],
    contract: dict[str, Any],
    today: dt.date,
    portfolio_value: float,
    sizing_pct: int,
    watchlist: dict[str, dict[str, Any]],
    open_short_premium: set[str],
    args: argparse.Namespace,
) -> dict[str, Any] | None:
    """Normalize, filter, size, and score an option contract."""
    details = contract.get("details") or {}
    greeks = contract.get("greeks") or {}
    last_quote = contract.get("last_quote") or {}
    day = contract.get("day") or {}
    strike = details.get("strike_price")
    expiration = details.get("expiration_date")
    days = dte(expiration, today) if expiration else None
    bid = float(last_quote.get("bid") or 0)
    ask = float(last_quote.get("ask") or 0)
    delta = greeks.get("delta")
    implied_vol = contract.get("implied_volatility")
    open_interest = int(contract.get("open_interest") or 0)
    volume = int(day.get("volume") or 0)

    if not strike or not expiration or days is None or delta is None:
        return None
    if days < args.min_dte or days > args.max_dte:
        return None
    abs_delta = abs(float(delta))
    if abs_delta < args.min_delta or abs_delta > args.max_delta:
        return None
    if bid <= 0 or open_interest < args.min_open_interest or volume < args.min_volume:
        return None
    mid = (bid + ask) / 2 if ask else bid
    spread_pct = ((ask - bid) / mid * 100) if ask and mid else 0.0
    if spread_pct > args.max_spread_pct:
        return None

    strike_float = float(strike)
    annualized_return = (bid / strike_float) * (365 / days) * 100
    if implied_vol is not None:
        iv_rank_proxy = max(0.0, min(100.0, ((float(implied_vol) - 0.15) / 0.35) * 100))
    else:
        iv_rank_proxy = min(100.0, (bid / strike_float) * 100 * 15)
    if iv_rank_proxy < args.min_iv_rank_proxy:
        return None

    collateral = strike_float * 100
    max_allocation = portfolio_value * args.max_position_pct * (sizing_pct / 100)
    max_contracts = math.floor(max_allocation / collateral)
    if max_contracts < 1:
        return None

    price = float(quote.get("price") or 0)
    year_high = float(quote.get("yearHigh") or price or 1)
    return_score = max(0.0, min(100.0, (annualized_return - 8) / 32 * 100))
    liquidity_score = min(100.0, (open_interest / 1000 * 50) + (volume / 100 * 50))
    trend_score = min(100.0, (price / year_high) * 100) if year_high else 70.0
    raw_quality_score = watchlist.get(ticker, {}).get("score")
    quality_bonus = (
        0.0
        if raw_quality_score is None
        else max(-5.0, min(5.0, (float(raw_quality_score) - 55) / 3))
    )
    existing_penalty = -6.0 if ticker in open_short_premium else 0.0
    composite = (
        return_score * 0.40
        + iv_rank_proxy * 0.30
        + liquidity_score * 0.20
        + trend_score * 0.10
        + quality_bonus
        + existing_penalty
    )
    composite = max(0.0, min(100.0, composite))

    return {
        "ticker": ticker,
        "source": source,
        "current_price": price,
        "strike": strike_float,
        "expiration": expiration,
        "dte": days,
        "bid": bid,
        "ask": ask,
        "mid": mid,
        "spread_pct": spread_pct,
        "delta": float(delta),
        "iv": float(implied_vol) if implied_vol is not None else None,
        "iv_rank_proxy": round(iv_rank_proxy),
        "open_interest": open_interest,
        "volume": volume,
        "annualized_return": annualized_return,
        "breakeven": strike_float - bid,
        "collateral": collateral,
        "max_contracts": max_contracts,
        "total_collateral": collateral * max_contracts,
        "total_premium": bid * max_contracts * 100,
        "return_score": return_score,
        "liquidity_score": liquidity_score,
        "trend_score": trend_score,
        "quality_bonus": quality_bonus,
        "existing_short_premium": ticker in open_short_premium,
        "score": composite,
    }


def build_universe(
    portfolio_symbols: list[str],
    watchlist: dict[str, dict[str, Any]],
    include_low_priority: bool,
) -> tuple[list[str], dict[str, str], dict[str, str]]:
    """Build the scan universe and record source/exclusion metadata."""
    watchlist_symbols = set(watchlist)
    portfolio_set = set(portfolio_symbols)
    excluded: dict[str, str] = {}
    universe_set = (portfolio_set | watchlist_symbols) - NON_OPTIONABLE

    if not include_low_priority:
        for symbol in list(universe_set):
            status = watchlist.get(symbol, {}).get("status")
            if symbol not in portfolio_set and status in BLOCKED_WATCHLIST_STATUSES:
                universe_set.remove(symbol)
                excluded[symbol] = f"Watchlist status {status}"

    source_by_ticker: dict[str, str] = {}
    for ticker in sorted(universe_set):
        sources = []
        if ticker in portfolio_set:
            sources.append("portfolio")
        if ticker in watchlist_symbols:
            sources.append("watchlist")
        source_by_ticker[ticker] = "+".join(sources)

    return sorted(universe_set), source_by_ticker, excluded


def run_scan(args: argparse.Namespace, config: dict[str, str | None]) -> dict[str, Any]:
    """Run the full trade idea scan and return report data."""
    fmp_api_key = config["fmp_api_key"]
    massive_api_key = config["massive_api_key"]
    if not fmp_api_key:
        raise RuntimeError("FMP API key is required. Set FMP_API_KEY or pass --fmp-api-key.")
    if not massive_api_key:
        raise RuntimeError(
            "Massive.com API key is required. Set MASSIVE_API_KEY or pass --massive-api-key."
        )

    today = dt.date.today()
    portfolio_value, portfolio_symbols = parse_portfolio(
        load_text(ROOT / "context" / "portfolio-details.md")
    )
    watchlist = parse_watchlist(load_text(ROOT / "context" / "watchlist.md"))
    open_short_premium = parse_open_short_premium(
        load_text(ROOT / "context" / "options-positions.md")
    )
    universe, source_by_ticker, static_exclusions = build_universe(
        portfolio_symbols,
        watchlist,
        args.include_low_priority,
    )

    quotes = quote_batch(universe + ["^VIX", "SPY"], fmp_api_key)
    vix = float((quotes.get("^VIX") or quotes.get("VIX") or {}).get("price") or 20.0)
    regime, sizing_pct, regime_strategy = vix_regime(vix)
    earnings_exclusions = fetch_earnings_exclusions(
        universe,
        fmp_api_key,
        today,
        args.earnings_lookahead_days,
    )

    quality_exclusions = dict(static_exclusions)
    cleared: list[str] = []
    for ticker in universe:
        quote = quotes.get(ticker)
        if not quote:
            quality_exclusions[ticker] = "No quote data"
            continue
        if ticker in earnings_exclusions:
            quality_exclusions[ticker] = (
                f"Earnings within {args.earnings_lookahead_days}d "
                f"({earnings_exclusions[ticker]})"
            )
            continue
        reasons: list[str] = []
        price = float(quote.get("price") or 0)
        sma50 = float(quote.get("priceAvg50") or 0)
        change_pct = float(quote.get("changesPercentage") or 0)
        volume = int(quote.get("volume") or 0)
        if sma50 and price < sma50:
            reasons.append(f"Below 50D SMA ({price:.2f} < {sma50:.2f})")
        if change_pct > args.max_daily_gain_pct:
            reasons.append(f"Overbought daily move (+{change_pct:.1f}%)")
        if volume < args.min_underlying_volume:
            reasons.append(f"Low/no underlying volume ({volume})")
        if reasons:
            quality_exclusions[ticker] = "; ".join(reasons)
        else:
            cleared.append(ticker)

    from_date = today + dt.timedelta(days=args.min_dte)
    to_date = today + dt.timedelta(days=args.max_dte)
    opportunities: list[dict[str, Any]] = []
    chain_counts: dict[str, int] = {}

    for ticker in cleared:
        quote = quotes[ticker]
        price = float(quote.get("price") or 0)
        if price <= 0:
            continue
        contracts = massive_put_chain(ticker, price, massive_api_key, from_date, to_date)
        chain_counts[ticker] = len(contracts)
        time.sleep(args.request_pause_seconds)
        for contract in contracts:
            scored = score_contract(
                ticker=ticker,
                source=source_by_ticker[ticker],
                quote=quote,
                contract=contract,
                today=today,
                portfolio_value=portfolio_value,
                sizing_pct=sizing_pct,
                watchlist=watchlist,
                open_short_premium=open_short_premium,
                args=args,
            )
            if scored:
                opportunities.append(scored)

    opportunities.sort(key=lambda item: item["score"], reverse=True)
    top: list[dict[str, Any]] = []
    seen: set[str] = set()
    for opportunity in opportunities:
        if opportunity["ticker"] in seen:
            continue
        top.append(opportunity)
        seen.add(opportunity["ticker"])
        if len(top) >= args.max_ideas:
            break

    return {
        "today": today,
        "run_timestamp": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat(),
        "portfolio_value": portfolio_value,
        "portfolio_symbols": portfolio_symbols,
        "watchlist": watchlist,
        "universe": universe,
        "source_by_ticker": source_by_ticker,
        "open_short_premium": open_short_premium,
        "vix": vix,
        "regime": regime,
        "sizing_pct": sizing_pct,
        "regime_strategy": regime_strategy,
        "earnings_exclusions": earnings_exclusions,
        "quality_exclusions": quality_exclusions,
        "cleared": cleared,
        "chain_counts": chain_counts,
        "opportunities": opportunities,
        "top": top,
        "args": args,
    }


def format_source(
    ticker: str,
    source: str,
    watchlist: dict[str, dict[str, Any]],
    existing_short: bool,
) -> str:
    """Format source metadata for a report line."""
    labels: list[str] = []
    if source == "portfolio":
        labels.append("portfolio holding")
    elif source == "watchlist":
        grade = watchlist.get(ticker, {}).get("grade", "").strip()
        status = watchlist.get(ticker, {}).get("status", "").strip()
        suffix = f" {grade}" if grade else ""
        labels.append(f"watchlist{suffix}".strip())
        if status:
            labels.append(status)
    else:
        labels.append("portfolio+watchlist")
    if existing_short:
        labels.append("existing CSP open")
    return "; ".join(labels)


def build_report(data: dict[str, Any]) -> str:
    """Build the markdown report."""
    args = data["args"]
    top = data["top"]
    open_short_note = ", ".join(sorted(data["open_short_premium"])) or "none"
    max_collateral = (
        data["portfolio_value"] * args.max_position_pct * (data["sizing_pct"] / 100)
    )
    lines = [
        f"# Trade Idea Generator - {data['today'].isoformat()}",
        "",
        f"Run timestamp: {data['run_timestamp']}",
        (
            f"Universe: {len(data['universe'])} unique optionable tickers "
            f"({len(data['portfolio_symbols'])} portfolio positions, "
            f"{len(data['watchlist'])} watchlist names; low-priority/avoid "
            "watchlist-only names excluded unless requested)."
        ),
        (
            f"Portfolio value used for sizing: ${data['portfolio_value']:,.0f}; "
            f"max idea collateral: {args.max_position_pct:.0%} x VIX sizing "
            f"({data['sizing_pct']}%) = ${max_collateral:,.0f}."
        ),
        f"Market regime: VIX {data['vix']:.1f} ({data['regime']}). {data['regime_strategy']}",
        f"Existing short-premium tickers noted for concentration: {open_short_note}.",
        "",
        (
            "These are scan results, not trade orders or personalized financial "
            "advice. Verify live quotes/liquidity before entry."
        ),
        "",
        "## Top CSP Trade Ideas",
        "",
    ]

    if not top:
        lines.extend(
            [
                (
                    "No qualifying 30-45 DTE, 0.20-0.30 delta CSPs passed the "
                    "trend, earnings, IV, liquidity, watchlist-status, and sizing "
                    "gates today."
                ),
                "",
            ]
        )
    for index, opportunity in enumerate(top, 1):
        lines.extend(
            [
                (
                    f"### {index}. {opportunity['ticker']} "
                    f"${opportunity['strike']:g}P {opportunity['expiration']} "
                    f"({opportunity['dte']} DTE)"
                ),
                (
                    "- Source: "
                    + format_source(
                        opportunity["ticker"],
                        opportunity["source"],
                        data["watchlist"],
                        opportunity["existing_short_premium"],
                    )
                    + (
                        f"; current price ${opportunity['current_price']:.2f}; "
                        f"breakeven ${opportunity['breakeven']:.2f}."
                    )
                ),
                (
                    f"- Credit: bid ${opportunity['bid']:.2f} / "
                    f"mid ${opportunity['mid']:.2f}; delta {opportunity['delta']:.3f}; "
                    f"IV {((opportunity['iv'] or 0) * 100):.1f}% "
                    f"(proxy rank {opportunity['iv_rank_proxy']}%)."
                ),
                (
                    f"- Return: {opportunity['annualized_return']:.1f}% annualized "
                    f"on cash collateral; score {opportunity['score']:.1f}."
                ),
                (
                    f"- Liquidity: OI {opportunity['open_interest']:,}, "
                    f"volume {opportunity['volume']:,}, "
                    f"spread {opportunity['spread_pct']:.1f}%."
                ),
                (
                    f"- Sizing: up to {opportunity['max_contracts']} contracts, "
                    f"${opportunity['total_collateral']:,.0f} collateral, "
                    f"${opportunity['total_premium']:,.0f} premium at bid."
                ),
                (
                    f"- Management: target 50% profit "
                    f"(${opportunity['bid'] * 0.50:.2f}); stop/reassess near "
                    f"200% of credit (${opportunity['bid'] * 2.0:.2f}) or "
                    "short-strike breach."
                ),
                "",
            ]
        )

    lines.extend(
        [
            "## Exclusions / Diagnostics",
            "",
            f"- Quality, status, or earnings exclusions: {len(data['quality_exclusions'])} tickers.",
        ]
    )
    if data["earnings_exclusions"]:
        earnings = ", ".join(
            f"{ticker} {date}" for ticker, date in sorted(data["earnings_exclusions"].items())
        )
        lines.append(
            f"- Earnings exclusions within {args.earnings_lookahead_days} days: {earnings}."
        )
    else:
        lines.append(
            f"- Earnings exclusions within {args.earnings_lookahead_days} days: none found."
        )
    lines.append(
        (
            f"- Options chains fetched for {len(data['cleared'])} tickers; raw "
            f"candidate contracts after filters: {len(data['opportunities'])}."
        )
    )
    return "\n".join(lines)


def build_telegram_message(data: dict[str, Any], report_path: Path) -> str:
    """Build a concise plain-text Telegram message."""
    args = data["args"]
    top = data["top"]
    open_short_note = ", ".join(sorted(data["open_short_premium"])) or "none"
    lines = [
        f"TRADE IDEA GENERATOR - {data['today'].isoformat()}",
        (
            f"VIX: {data['vix']:.1f} ({data['regime']}) | "
            f"Sizing: {data['sizing_pct']}% | "
            f"AUM: ${data['portfolio_value'] / 1_000_000:.2f}M"
        ),
        (
            f"Universe: {len(data['universe'])} optionable portfolio/watchlist "
            f"tickers | {len(data['opportunities'])} candidate contracts"
        ),
        "",
    ]
    if top:
        labels = ["1.", "2.", "3.", "4.", "5."]
        for index, opportunity in enumerate(top):
            concentration = (
                " | existing CSP open" if opportunity["existing_short_premium"] else ""
            )
            lines.extend(
                [
                    (
                        f"{labels[index]} {opportunity['ticker']} "
                        f"${opportunity['strike']:g}P {opportunity['expiration']} "
                        f"({opportunity['dte']}DTE)"
                    ),
                    (
                        f"  Credit ${opportunity['bid']:.2f} | "
                        f"Delta {opportunity['delta']:.2f} | "
                        f"AnnRet {opportunity['annualized_return']:.1f}% | "
                        f"Score {opportunity['score']:.1f}"
                    ),
                    (
                        f"  BE ${opportunity['breakeven']:.2f} | "
                        f"OI {opportunity['open_interest']:,} | "
                        f"Max {opportunity['max_contracts']}x / "
                        f"${opportunity['total_collateral']:,.0f}{concentration}"
                    ),
                    "",
                ]
            )
    else:
        lines.extend(["No qualifying CSP opportunities passed all gates today.", ""])

    if data["earnings_exclusions"]:
        symbols = sorted(data["earnings_exclusions"])
        sample = ", ".join(symbols[:12])
        more = "..." if len(symbols) > 12 else ""
        lines.append(f"Earnings exclusions: {sample}{more}")
    lines.extend(
        [
            f"Risk note: existing short-premium tickers: {open_short_note}.",
            "Use /paper-trade only after live quote/risk review.",
            "Not financial advice.",
            f"Report: {report_path.relative_to(ROOT)}",
        ]
    )
    message = "\n".join(lines)
    if len(message) > args.telegram_limit:
        return message[: args.telegram_limit - 20] + "\n...(truncated)"
    return message


def send_telegram(message: str, token: str, chat_id: str) -> dict[str, Any]:
    """Send a Telegram message via Bot API."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "disable_web_page_preview": True,
    }
    return post_json(url, payload, timeout=20)


def write_outputs(data: dict[str, Any], output_path: Path) -> tuple[Path, Path]:
    """Write the markdown report and Telegram preview text."""
    report = build_report(data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    telegram_path = output_path.with_suffix(".telegram.txt")
    telegram_path.write_text(build_telegram_message(data, output_path), encoding="utf-8")
    return output_path, telegram_path


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--send-telegram", action="store_true")
    parser.add_argument("--telegram-chat-id")
    parser.add_argument("--telegram-bot-token")
    parser.add_argument("--fmp-api-key")
    parser.add_argument("--massive-api-key")
    parser.add_argument(
        "--workflow-config",
        action="append",
        default=[str(path) for path in DEFAULT_WORKFLOW_CONFIGS],
        help="Existing workflow JSON to use as fallback config.",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-ideas", type=int, default=5)
    parser.add_argument("--min-dte", type=int, default=30)
    parser.add_argument("--max-dte", type=int, default=45)
    parser.add_argument("--min-delta", type=float, default=0.20)
    parser.add_argument("--max-delta", type=float, default=0.30)
    parser.add_argument("--min-open-interest", type=int, default=50)
    parser.add_argument("--min-volume", type=int, default=10)
    parser.add_argument("--max-spread-pct", type=float, default=25.0)
    parser.add_argument("--min-iv-rank-proxy", type=float, default=25.0)
    parser.add_argument("--min-underlying-volume", type=int, default=100000)
    parser.add_argument("--max-daily-gain-pct", type=float, default=8.0)
    parser.add_argument("--max-position-pct", type=float, default=0.05)
    parser.add_argument("--earnings-lookahead-days", type=int, default=45)
    parser.add_argument("--include-low-priority", action="store_true")
    parser.add_argument("--request-pause-seconds", type=float, default=0.05)
    parser.add_argument("--telegram-limit", type=int, default=3900)
    return parser.parse_args()


def main() -> int:
    """Run the CLI."""
    args = parse_args()
    config = resolve_config(args)
    data = run_scan(args, config)
    output_path = args.output or (
        ROOT / "outputs" / f"trade-idea-generator-{data['today'].isoformat()}.md"
    )
    report_path, telegram_path = write_outputs(data, output_path)

    telegram_response: dict[str, Any] | None = None
    if args.send_telegram:
        token = config.get("telegram_bot_token")
        chat_id = config.get("telegram_chat_id")
        if not token:
            raise RuntimeError("Telegram bot token is required. Set TELEGRAM_BOT_TOKEN.")
        if not chat_id:
            raise RuntimeError("Telegram chat ID is required. Set TELEGRAM_CHAT_ID.")
        telegram_response = send_telegram(
            telegram_path.read_text(encoding="utf-8"),
            token,
            chat_id,
        )

    summary = {
        "report": str(report_path),
        "telegram_preview": str(telegram_path),
        "sent_telegram": bool(args.send_telegram),
        "telegram_ok": telegram_response.get("ok") if telegram_response else None,
        "telegram_message_id": (
            telegram_response.get("result", {}).get("message_id")
            if telegram_response
            else None
        ),
        "top_tickers": [item["ticker"] for item in data["top"]],
        "candidate_contracts": len(data["opportunities"]),
        "cleared_tickers": len(data["cleared"]),
        "excluded_tickers": len(data["quality_exclusions"]),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
