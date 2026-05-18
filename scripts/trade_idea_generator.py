#!/usr/bin/env python3
"""Generate option trade ideas from the workspace portfolio/watchlist.

The script intentionally reads the static context files used by the rest of
the workspace, so cron/automation runs do not depend on a live dashboard.
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
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_PATH = ROOT / "context" / "portfolio-details.md"
WATCHLIST_PATH = ROOT / "context" / "watchlist.md"
OPTIONS_SCAN_COMMAND = ROOT / ".claude" / "commands" / "options-scan.md"
CSP_FIXED_WORKFLOW = ROOT / "outputs" / "csp-daily-scan-fixed.json"
OUTPUT_DIR = ROOT / "outputs"

FMP_BASE = "https://financialmodelingprep.com/api/v3"
MASSIVE_BASE = "https://api.massive.com/v3"
TELEGRAM_BASE = "https://api.telegram.org"

MIN_VOLUME = 10
MIN_OPEN_INTEREST = 50
MAX_SPREAD_PCT = 0.18
TARGET_MIN_DTE = 20
TARGET_MAX_DTE = 60
MAX_TELEGRAM_CHARS = 3900


@dataclass(frozen=True)
class Position:
    symbol: str
    quantity: float
    avg_price: float
    current: float
    weight: float


@dataclass(frozen=True)
class WatchlistItem:
    ticker: str
    score: float | None
    grade: str
    company: str
    status: str


@dataclass
class OptionCandidate:
    ticker: str
    strategy: str
    contract_type: str
    expiration: str
    strike: float
    bid: float
    ask: float
    mid: float
    delta: float | None
    theta: float | None
    iv: float | None
    volume: int
    open_interest: int
    dte: int
    spot: float
    source: str
    score: float
    rationale: str
    max_contracts: int
    collateral: float
    breakeven: float
    annualized_return: float
    risk_flags: list[str]


def clean_money(value: str) -> float:
    value = value.strip().replace("$", "").replace(",", "").replace("%", "")
    if value in {"", "-", "—"}:
        return 0.0
    return float(value)


def parse_portfolio(path: Path) -> dict[str, Position]:
    positions: dict[str, Position] = {}
    if not path.exists():
        return positions

    in_positions = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## Current Positions"):
            in_positions = True
            continue
        if in_positions and line.startswith("## "):
            break
        if not in_positions or not line.startswith("|"):
            continue
        if "SYMBOL" in line or "---" in line or "Totals" in line:
            continue

        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 9:
            continue
        symbol = cells[0].upper()
        try:
            positions[symbol] = Position(
                symbol=symbol,
                quantity=clean_money(cells[1]),
                avg_price=clean_money(cells[2]),
                current=clean_money(cells[3]),
                weight=clean_money(cells[8]),
            )
        except ValueError:
            continue
    return positions


def parse_portfolio_value(path: Path) -> float:
    if not path.exists():
        return 100_000.0
    text = path.read_text(encoding="utf-8")
    match = re.search(r"\*\*Total MKT VALUE\*\*\s*\|\s*\$?([\d,]+)", text)
    if match:
        return float(match.group(1).replace(",", ""))
    return 100_000.0


def parse_watchlist(path: Path) -> dict[str, WatchlistItem]:
    items: dict[str, WatchlistItem] = {}
    if not path.exists():
        return items

    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        if "Ticker" in line or "---" in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        ticker = cells[0].upper()
        if not re.fullmatch(r"[A-Z.]{1,6}", ticker):
            continue
        score = None if cells[1] in {"—", ""} else float(cells[1])
        grade = cells[2].replace("*", "").strip()
        items[ticker] = WatchlistItem(
            ticker=ticker,
            score=score,
            grade=grade,
            company=cells[3],
            status=cells[4],
        )
    return items


def resolve_key(env_name: str, regex: str) -> str:
    value = os.environ.get(env_name, "").strip()
    if value:
        return value
    if OPTIONS_SCAN_COMMAND.exists():
        text = OPTIONS_SCAN_COMMAND.read_text(encoding="utf-8")
        match = re.search(regex, text)
        if match:
            return match.group(1)
    return ""


def http_json(url: str, timeout: int = 25, retries: int = 2) -> Any:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "AltamiraTradeIdeaGenerator/1.0",
                    "Accept": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                payload = response.read().decode("utf-8")
            return json.loads(payload)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Request failed for {url}: {last_error}")


def fetch_quotes(tickers: list[str], fmp_key: str) -> dict[str, dict[str, Any]]:
    quotes: dict[str, dict[str, Any]] = {}
    for i in range(0, len(tickers), 25):
        batch = tickers[i : i + 25]
        url = f"{FMP_BASE}/quote/{','.join(batch)}?apikey={urllib.parse.quote(fmp_key)}"
        data = http_json(url)
        if isinstance(data, list):
            for item in data:
                symbol = str(item.get("symbol", "")).upper()
                if symbol:
                    quotes[symbol] = item
    return quotes


def fetch_vix(fmp_key: str) -> tuple[float | None, str, int, float]:
    url = f"{FMP_BASE}/quote/%5EVIX?apikey={urllib.parse.quote(fmp_key)}"
    data = http_json(url)
    vix = None
    if isinstance(data, list) and data:
        try:
            vix = float(data[0].get("price"))
        except (TypeError, ValueError):
            vix = None
    if vix is None:
        return None, "UNKNOWN", 50, 0.75
    if vix < 15:
        return vix, "LOW", 75, 1.0
    if vix < 25:
        return vix, "NORMAL", 100, 1.0
    if vix < 35:
        return vix, "ELEVATED", 50, 0.9
    return vix, "CRISIS", 25, 0.75


def next_monthly_expiration(today: dt.date) -> dt.date:
    """Return the next standard third-Friday expiration at least 20 DTE away."""
    for month_offset in range(0, 4):
        year = today.year + ((today.month + month_offset - 1) // 12)
        month = ((today.month + month_offset - 1) % 12) + 1
        first = dt.date(year, month, 1)
        first_friday_offset = (4 - first.weekday()) % 7
        third_friday = first + dt.timedelta(days=first_friday_offset + 14)
        if (third_friday - today).days >= TARGET_MIN_DTE:
            return third_friday
    return today + dt.timedelta(days=35)


def fetch_earnings_dates(
    tickers: list[str],
    fmp_key: str,
    today: dt.date,
    max_calls: int = 60,
) -> dict[str, dt.date]:
    earnings: dict[str, dt.date] = {}
    for ticker in tickers[:max_calls]:
        url = f"{FMP_BASE}/historical/earning_calendar/{ticker}?apikey={urllib.parse.quote(fmp_key)}"
        try:
            data = http_json(url, timeout=15, retries=1)
        except RuntimeError:
            continue
        if not isinstance(data, list):
            continue
        dates: list[dt.date] = []
        for row in data:
            date_str = row.get("date")
            if not date_str:
                continue
            try:
                date_value = dt.date.fromisoformat(str(date_str)[:10])
            except ValueError:
                continue
            if date_value >= today:
                dates.append(date_value)
        if dates:
            earnings[ticker] = min(dates)
    return earnings


def option_mid(bid: float, ask: float) -> float:
    if bid > 0 and ask > 0:
        return (bid + ask) / 2
    return max(bid, ask, 0.0)


def estimate_delta(contract_type: str, strike: float, spot: float) -> float:
    if spot <= 0:
        return -0.25 if contract_type == "put" else 0.25
    moneyness = strike / spot
    if contract_type == "put":
        if moneyness >= 0.99:
            return -0.45
        if moneyness >= 0.96:
            return -0.30
        if moneyness >= 0.93:
            return -0.20
        return -0.12
    if moneyness <= 1.01:
        return 0.45
    if moneyness <= 1.05:
        return 0.30
    if moneyness <= 1.10:
        return 0.20
    return 0.12


def liquidity_score(volume: int, open_interest: int, spread_pct: float) -> float:
    score = 0.0
    if spread_pct <= 0.05:
        score += 35
    elif spread_pct <= 0.10:
        score += 25
    elif spread_pct <= MAX_SPREAD_PCT:
        score += 12
    if open_interest >= 1000:
        score += 35
    elif open_interest >= 500:
        score += 27
    elif open_interest >= MIN_OPEN_INTEREST:
        score += 15
    if volume >= 100:
        score += 30
    elif volume >= 50:
        score += 22
    elif volume >= MIN_VOLUME:
        score += 12
    return score


def fetch_options(ticker: str, massive_key: str, today: dt.date) -> list[dict[str, Any]]:
    start = today + dt.timedelta(days=TARGET_MIN_DTE)
    end = today + dt.timedelta(days=TARGET_MAX_DTE)
    params = {
        "apiKey": massive_key,
        "limit": "250",
        "expiration_date.gte": start.isoformat(),
        "expiration_date.lte": end.isoformat(),
    }
    url = f"{MASSIVE_BASE}/snapshot/options/{ticker}?{urllib.parse.urlencode(params)}"
    data = http_json(url, timeout=25, retries=1)
    if isinstance(data, dict):
        return data.get("results") or []
    return []


def build_option_row(raw: dict[str, Any], spot: float, today: dt.date) -> dict[str, Any] | None:
    details = raw.get("details") or {}
    quote = raw.get("last_quote") or {}
    greeks = raw.get("greeks") or {}
    contract_type = details.get("contract_type")
    expiration = details.get("expiration_date")
    if contract_type not in {"put", "call"} or not expiration:
        return None
    try:
        exp_date = dt.date.fromisoformat(expiration)
        dte = (exp_date - today).days
        strike = float(details.get("strike_price"))
        bid = float(quote.get("bid") or 0)
        ask = float(quote.get("ask") or 0)
    except (TypeError, ValueError):
        return None
    if dte < TARGET_MIN_DTE or dte > TARGET_MAX_DTE or bid <= 0:
        return None

    mid = option_mid(bid, ask)
    spread_pct = ((ask - bid) / mid) if mid > 0 and ask >= bid else 1.0
    volume = int(raw.get("day", {}).get("volume") or 0)
    open_interest = int(raw.get("open_interest") or 0)
    if volume < MIN_VOLUME or open_interest < MIN_OPEN_INTEREST or spread_pct > MAX_SPREAD_PCT:
        return None

    delta = greeks.get("delta")
    if delta is None:
        delta = estimate_delta(contract_type, strike, spot)
    else:
        try:
            delta = float(delta)
        except (TypeError, ValueError):
            delta = estimate_delta(contract_type, strike, spot)

    theta = greeks.get("theta")
    iv = raw.get("implied_volatility")
    return {
        "contract_type": contract_type,
        "expiration": expiration,
        "strike": strike,
        "bid": bid,
        "ask": ask,
        "mid": mid,
        "delta": delta,
        "theta": float(theta) if theta is not None else None,
        "iv": float(iv) if iv is not None else None,
        "volume": volume,
        "open_interest": open_interest,
        "dte": dte,
        "spread_pct": spread_pct,
        "liq_score": liquidity_score(volume, open_interest, spread_pct),
    }


def target_delta_score(contract_type: str, delta: float | None) -> float:
    target = -0.25 if contract_type == "put" else 0.25
    if delta is None:
        return 10.0
    return max(0.0, 20.0 - abs(delta - target) * 100.0)


def source_bonus(
    ticker: str,
    positions: dict[str, Position],
    watchlist: dict[str, WatchlistItem],
) -> tuple[float, str]:
    parts: list[str] = []
    bonus = 0.0
    if ticker in positions:
        bonus += 10.0
        parts.append(f"existing holding ({positions[ticker].weight:.1f}% weight)")
    item = watchlist.get(ticker)
    if item:
        if item.score is not None:
            bonus += min(max((item.score - 45) / 2, 0), 12)
        if "Top Candidate" in item.status:
            bonus += 8.0
        elif "Consider" in item.status:
            bonus += 4.0
        parts.append(f"watchlist {item.grade}/{item.status.replace('⭐ ', '')}")
    return bonus, "; ".join(parts) or "screened from current universe"


def earnings_flags(ticker: str, expiration: str, earnings: dict[str, dt.date]) -> list[str]:
    next_earnings = earnings.get(ticker)
    if not next_earnings:
        return []
    exp_date = dt.date.fromisoformat(expiration)
    if next_earnings <= exp_date:
        return [f"earnings before expiration ({next_earnings.isoformat()})"]
    if (next_earnings - exp_date).days <= 7:
        return [f"earnings within a week after expiration ({next_earnings.isoformat()})"]
    return []


def build_candidates(
    tickers: list[str],
    quotes: dict[str, dict[str, Any]],
    positions: dict[str, Position],
    watchlist: dict[str, WatchlistItem],
    earnings: dict[str, dt.date],
    massive_key: str,
    portfolio_value: float,
    sizing_pct: int,
    confidence_multiplier: float,
    today: dt.date,
) -> tuple[list[OptionCandidate], list[str]]:
    candidates: list[OptionCandidate] = []
    rejected: list[str] = []
    max_allocation = portfolio_value * 0.05 * (sizing_pct / 100)

    for ticker in tickers:
        quote = quotes.get(ticker, {})
        try:
            spot = float(quote.get("price") or quote.get("previousClose") or 0)
        except (TypeError, ValueError):
            spot = 0.0
        if spot <= 0:
            rejected.append(f"{ticker}: no quote")
            continue
        try:
            raw_options = fetch_options(ticker, massive_key, today)
        except RuntimeError as exc:
            rejected.append(f"{ticker}: options fetch failed ({exc})")
            continue
        rows = [
            row
            for raw in raw_options
            if (row := build_option_row(raw, spot=spot, today=today)) is not None
        ]
        if not rows:
            rejected.append(f"{ticker}: no liquid 20-60 DTE contracts")
            continue

        bonus, source = source_bonus(ticker, positions, watchlist)

        # Cash-secured put / put-selling entry ideas.
        put_rows = [
            row
            for row in rows
            if row["contract_type"] == "put"
            and row["strike"] < spot
            and -0.35 <= (row["delta"] or estimate_delta("put", row["strike"], spot)) <= -0.15
        ]
        for row in put_rows:
            flags = earnings_flags(ticker, row["expiration"], earnings)
            annual = (row["bid"] / row["strike"]) * (365 / row["dte"]) * 100
            distance_otm = (spot - row["strike"]) / spot * 100
            score = (
                min(annual * 2.2, 35)
                + row["liq_score"] * 0.25
                + target_delta_score("put", row["delta"])
                + min(distance_otm, 12)
                + bonus
            ) * confidence_multiplier
            if any("earnings before" in flag for flag in flags):
                score -= 28
            contracts = math.floor(max_allocation / (row["strike"] * 100))
            candidates.append(
                OptionCandidate(
                    ticker=ticker,
                    strategy="Cash-secured put",
                    contract_type="put",
                    expiration=row["expiration"],
                    strike=row["strike"],
                    bid=row["bid"],
                    ask=row["ask"],
                    mid=row["mid"],
                    delta=row["delta"],
                    theta=row["theta"],
                    iv=row["iv"],
                    volume=row["volume"],
                    open_interest=row["open_interest"],
                    dte=row["dte"],
                    spot=spot,
                    source=source,
                    score=score,
                    rationale=(
                        f"{distance_otm:.1f}% OTM entry on {source}; "
                        f"{annual:.1f}% annualized premium yield before risk adjustments"
                    ),
                    max_contracts=max(contracts, 0),
                    collateral=row["strike"] * 100 * max(contracts, 0),
                    breakeven=row["strike"] - row["bid"],
                    annualized_return=annual,
                    risk_flags=flags,
                )
            )

        # Covered calls for positions with at least one round lot.
        position = positions.get(ticker)
        if position and position.quantity >= 100:
            call_rows = [
                row
                for row in rows
                if row["contract_type"] == "call"
                and row["strike"] > spot
                and row["strike"] >= position.avg_price
                and 0.15 <= (row["delta"] or estimate_delta("call", row["strike"], spot)) <= 0.35
            ]
            covered_lots = int(position.quantity // 100)
            for row in call_rows:
                flags = earnings_flags(ticker, row["expiration"], earnings)
                premium_yield = row["bid"] / spot * 100
                if_called = ((row["strike"] - spot + row["bid"]) / spot) * 100
                score = (
                    min(premium_yield * 7, 25)
                    + min(if_called * 2, 28)
                    + row["liq_score"] * 0.25
                    + target_delta_score("call", row["delta"])
                    + bonus
                ) * confidence_multiplier
                if any("earnings before" in flag for flag in flags):
                    score -= 18
                candidates.append(
                    OptionCandidate(
                        ticker=ticker,
                        strategy="Covered call",
                        contract_type="call",
                        expiration=row["expiration"],
                        strike=row["strike"],
                        bid=row["bid"],
                        ask=row["ask"],
                        mid=row["mid"],
                        delta=row["delta"],
                        theta=row["theta"],
                        iv=row["iv"],
                        volume=row["volume"],
                        open_interest=row["open_interest"],
                        dte=row["dte"],
                        spot=spot,
                        source=source,
                        score=score,
                        rationale=(
                            f"uses {covered_lots} covered lot(s); "
                            f"{premium_yield:.2f}% premium yield, {if_called:.1f}% if-called return"
                        ),
                        max_contracts=covered_lots,
                        collateral=0.0,
                        breakeven=spot - row["bid"],
                        annualized_return=premium_yield * (365 / row["dte"]),
                        risk_flags=flags,
                    )
                )

    candidates.sort(key=lambda item: item.score, reverse=True)
    return candidates, rejected


def usd(value: float, decimals: int = 2) -> str:
    return f"${value:,.{decimals}f}"


def fmt(value: float | None, decimals: int = 2) -> str:
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}"


def render_report(
    candidates: list[OptionCandidate],
    rejected: list[str],
    positions: dict[str, Position],
    watchlist: dict[str, WatchlistItem],
    quotes: dict[str, dict[str, Any]],
    vix: float | None,
    regime: str,
    sizing_pct: int,
    today: dt.date,
) -> tuple[str, str]:
    top = candidates[:8]
    top_telegram = candidates[:5]
    generated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"# Trade Idea Generator — {today.isoformat()}",
        "",
        f"Generated: {generated}",
        "",
        "## Market Regime",
        "",
        f"- **VIX:** {fmt(vix, 1)} ({regime})",
        f"- **VIX-adjusted max sizing:** {sizing_pct}% of the standard 5% position limit",
        f"- **Universe:** {len(positions)} portfolio holdings + {len(watchlist)} watchlist names",
        "",
        "## Top Trade Ideas",
        "",
    ]

    if not top:
        lines.extend(
            [
                "No qualifying liquid 20-60 DTE options ideas passed the current filters.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "| Rank | Ticker | Strategy | Contract | Credit | Delta | DTE | Score | Sizing | Rationale |",
                "|------|--------|----------|----------|--------|-------|-----|-------|--------|-----------|",
            ]
        )
        for idx, idea in enumerate(top, start=1):
            contract = f"{idea.expiration} {idea.strike:g}{idea.contract_type[0].upper()}"
            sizing = (
                f"{idea.max_contracts} contract(s), collateral {usd(idea.collateral, 0)}"
                if idea.strategy == "Cash-secured put"
                else f"{idea.max_contracts} covered contract(s)"
            )
            flags = f" Risk: {'; '.join(idea.risk_flags)}." if idea.risk_flags else ""
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(idx),
                        idea.ticker,
                        idea.strategy,
                        contract,
                        usd(idea.bid),
                        fmt(idea.delta, 3),
                        str(idea.dte),
                        f"{idea.score:.1f}",
                        sizing,
                        f"{idea.rationale}{flags}",
                    ]
                )
                + " |"
            )

    lines.extend(
        [
            "",
            "## Portfolio Context",
            "",
            "| Ticker | Weight | Quote | 1D Change |",
            "|--------|--------|-------|-----------|",
        ]
    )
    for position in sorted(positions.values(), key=lambda item: item.weight, reverse=True)[:15]:
        quote = quotes.get(position.symbol, {})
        price = quote.get("price", position.current)
        change = quote.get("changesPercentage")
        lines.append(
            f"| {position.symbol} | {position.weight:.1f}% | {usd(float(price)) if price else 'N/A'} | "
            f"{float(change):+.2f}% |"
            if change is not None
            else f"| {position.symbol} | {position.weight:.1f}% | {usd(float(price)) if price else 'N/A'} | N/A |"
        )

    lines.extend(
        [
            "",
            "## Watchlist Focus",
            "",
            "| Ticker | Score | Grade | Status |",
            "|--------|-------|-------|--------|",
        ]
    )
    for item in sorted(
        watchlist.values(),
        key=lambda row: row.score if row.score is not None else -999,
        reverse=True,
    )[:12]:
        lines.append(
            f"| {item.ticker} | {item.score if item.score is not None else 'N/A'} | {item.grade} | {item.status} |"
        )

    lines.extend(
        [
            "",
            "## Rejections / Data Gaps",
            "",
        ]
    )
    if rejected:
        for entry in rejected[:30]:
            lines.append(f"- {entry}")
        if len(rejected) > 30:
            lines.append(f"- ... {len(rejected) - 30} more omitted")
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "## Risk Notes",
            "",
            "- Informational scan only; not investment advice.",
            "- Avoid opening short premium through unplanned earnings unless explicitly intended.",
            "- Standard exits: close at 50% max profit, stop/adjust near 200% of credit or short-strike breach.",
            "- Validate bid/ask and buying power in the broker before entry.",
            "",
        ]
    )

    telegram = render_telegram(top_telegram, vix, regime, sizing_pct, today)
    return "\n".join(lines), telegram


def render_telegram(
    ideas: list[OptionCandidate],
    vix: float | None,
    regime: str,
    sizing_pct: int,
    today: dt.date,
) -> str:
    lines = [
        f"TRADE IDEA GENERATOR - {today.isoformat()}",
        f"VIX: {fmt(vix, 1)} ({regime}) | Sizing: {sizing_pct}% of standard max",
        "",
    ]
    if not ideas:
        lines.append("No qualifying liquid 20-60 DTE trade ideas passed today's filters.")
    else:
        for idx, idea in enumerate(ideas, start=1):
            contract = f"{idea.strike:g}{idea.contract_type[0].upper()} {idea.expiration}"
            lines.extend(
                [
                    f"#{idx} {idea.ticker} - {idea.strategy}",
                    f"  {contract} | credit {usd(idea.bid)} | delta {fmt(idea.delta, 3)} | DTE {idea.dte}",
                    f"  Score {idea.score:.1f} | ann. yield {idea.annualized_return:.1f}% | contracts {idea.max_contracts}",
                    f"  {idea.rationale}",
                ]
            )
            if idea.risk_flags:
                lines.append(f"  Risk: {'; '.join(idea.risk_flags)}")
            lines.append("")
    lines.extend(
        [
            "Risk: informational scan only; verify live chain/liquidity before trading.",
            "Use /paper-trade to log any selected setup.",
        ]
    )
    message = "\n".join(lines).strip()
    if len(message) <= MAX_TELEGRAM_CHARS:
        return message
    return message[: MAX_TELEGRAM_CHARS - 80].rstrip() + "\n...\nFull report saved in outputs."


def resolve_chat_id() -> str:
    env_chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if env_chat:
        return env_chat
    if CSP_FIXED_WORKFLOW.exists():
        text = CSP_FIXED_WORKFLOW.read_text(encoding="utf-8")
        match = re.search(r'"chatId"\s*:\s*"?=?(-?\d+)"?', text)
        if match:
            return match.group(1)
    return ""


def send_telegram(message: str, token: str, chat_id: str) -> dict[str, Any]:
    url = f"{TELEGRAM_BASE}/bot{token}/sendMessage"
    payload = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST")
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))


def write_output(report: str, today: dt.date) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"trade-idea-generator-{today.isoformat()}.md"
    path.write_text(report, encoding="utf-8")
    return path


def build_universe(
    positions: dict[str, Position],
    watchlist: dict[str, WatchlistItem],
    include_all_watchlist: bool,
) -> list[str]:
    excluded = {"FFOLX"}
    universe = {ticker for ticker in positions if ticker not in excluded}
    if include_all_watchlist:
        universe.update(watchlist)
    else:
        for ticker, item in watchlist.items():
            if "Avoid" in item.status or "Low Priority" in item.status:
                continue
            universe.add(ticker)
    return sorted(universe)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate portfolio/watchlist trade ideas and optionally send to Telegram."
    )
    parser.add_argument("--send-telegram", action="store_true", help="Send summary to Telegram")
    parser.add_argument("--chat-id", default="", help="Telegram chat/channel ID override")
    parser.add_argument("--include-all-watchlist", action="store_true", help="Scan every watchlist ticker")
    parser.add_argument("--dry-run", action="store_true", help="Write report but do not send Telegram")
    args = parser.parse_args()

    today = dt.datetime.now(dt.timezone.utc).date()
    fmp_key = resolve_key("FMP_API_KEY", r"FMP API\*\* \(key: `([^`]+)`\)")
    massive_key = resolve_key("MASSIVE_API_KEY", r"Massive\.com API\*\* \(key: `([^`]+)`\)")
    if not fmp_key or not massive_key:
        print("Missing FMP_API_KEY or MASSIVE_API_KEY and no repo fallback key found.", file=sys.stderr)
        return 2

    positions = parse_portfolio(PORTFOLIO_PATH)
    watchlist = parse_watchlist(WATCHLIST_PATH)
    portfolio_value = parse_portfolio_value(PORTFOLIO_PATH)
    universe = build_universe(positions, watchlist, include_all_watchlist=args.include_all_watchlist)
    if not universe:
        print("No tickers found in portfolio/watchlist context.", file=sys.stderr)
        return 2

    vix, regime, sizing_pct, confidence_multiplier = fetch_vix(fmp_key)
    quotes = fetch_quotes(universe, fmp_key)
    earnings = fetch_earnings_dates(universe, fmp_key, today)
    candidates, rejected = build_candidates(
        universe,
        quotes,
        positions,
        watchlist,
        earnings,
        massive_key,
        portfolio_value,
        sizing_pct,
        confidence_multiplier,
        today,
    )
    report, telegram = render_report(
        candidates,
        rejected,
        positions,
        watchlist,
        quotes,
        vix,
        regime,
        sizing_pct,
        today,
    )
    output_path = write_output(report, today)
    print(f"Wrote {output_path.relative_to(ROOT)}")
    print(f"Generated {len(candidates)} candidates; {len(rejected)} data gaps/rejections.")
    print("\nTelegram preview:\n")
    print(telegram)

    if args.send_telegram and not args.dry_run:
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        chat_id = args.chat_id.strip() or resolve_chat_id()
        if not token:
            print("TELEGRAM_BOT_TOKEN is not set; report was generated but not sent.", file=sys.stderr)
            return 3
        if not chat_id:
            print("TELEGRAM_CHAT_ID/chat fallback not found; report was generated but not sent.", file=sys.stderr)
            return 3
        response = send_telegram(telegram, token, chat_id)
        if not response.get("ok"):
            print(f"Telegram send failed: {response}", file=sys.stderr)
            return 4
        print(f"Sent Telegram message to chat {chat_id}.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
