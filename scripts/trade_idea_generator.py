#!/usr/bin/env python3
"""Generate portfolio/watchlist trade ideas and optionally send Telegram alert."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


WORKSPACE = Path(__file__).resolve().parent.parent
CONTEXT = WORKSPACE / "context"
OUTPUTS = WORKSPACE / "outputs"
FMP_BASE = "https://financialmodelingprep.com/api/v3"
FMP_KEY = os.environ.get("FMP_API_KEY", "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz")
DEFAULT_TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "7830722515")
ETF_TICKERS = {"SPY", "QQQ", "FFOLX"}


@dataclass
class Holding:
    ticker: str
    quantity: float
    current: float
    market_value: float
    pnl_pct: float
    weight: float


@dataclass
class WatchlistEntry:
    ticker: str
    score: float | None
    grade: str
    company: str
    status: str


@dataclass
class MarketSnapshot:
    spy_price: float | None
    spy_change_pct: float | None
    vix: float | None
    vix_change_pct: float | None
    regime: str


def parse_money(value: str) -> float:
    cleaned = value.replace("$", "").replace(",", "").replace("%", "").strip()
    if cleaned in {"", "-", "—"}:
        return 0.0
    return float(cleaned)


def parse_float(value: str) -> float | None:
    cleaned = value.replace("$", "").replace(",", "").replace("%", "").strip()
    if cleaned in {"", "-", "—"}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def load_holdings(path: Path) -> list[Holding]:
    holdings: list[Holding] = []
    in_positions = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("## Current Positions"):
            in_positions = True
            continue
        if in_positions and line.startswith("## "):
            break
        if not in_positions or not line.startswith("|") or "SYMBOL" in line or "---" in line:
            continue

        cells = split_markdown_row(line)
        if len(cells) < 9:
            continue

        ticker = cells[0].upper()
        if ticker == "TOTALS":
            continue

        pnl_match = re.search(r"\(([+-]?[0-9.]+)%\)", cells[6])
        pnl_pct = float(pnl_match.group(1)) if pnl_match else 0.0
        holdings.append(
            Holding(
                ticker=ticker,
                quantity=parse_money(cells[1]),
                current=parse_money(cells[3]),
                market_value=parse_money(cells[4]),
                pnl_pct=pnl_pct,
                weight=parse_money(cells[8]),
            )
        )
    return holdings


def load_watchlist(path: Path) -> list[WatchlistEntry]:
    entries: list[WatchlistEntry] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line.startswith("|") or "Ticker" in line or "---" in line:
            continue
        cells = split_markdown_row(line)
        if len(cells) < 5:
            continue
        score = parse_float(cells[1])
        grade = re.sub(r"[*`]", "", cells[2]).strip()
        entries.append(
            WatchlistEntry(
                ticker=cells[0].upper(),
                score=score,
                grade=grade,
                company=cells[3],
                status=cells[4].replace("⭐", "").strip(),
            )
        )
    return entries


def request_json(url: str, params: dict[str, Any] | None = None, timeout: int = 20) -> Any:
    query = urllib.parse.urlencode(params or {})
    full_url = f"{url}?{query}" if query else url
    request = urllib.request.Request(full_url, headers={"User-Agent": "AltamiraTradeIdeaGenerator/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fmp_get(endpoint: str, params: dict[str, Any] | None = None, timeout: int = 20) -> Any:
    payload = dict(params or {})
    payload["apikey"] = FMP_KEY
    return request_json(f"{FMP_BASE}/{endpoint.lstrip('/')}", payload, timeout=timeout)


def fetch_quotes(tickers: Iterable[str]) -> dict[str, dict[str, Any]]:
    ticker_list = sorted({ticker for ticker in tickers if ticker})
    if not ticker_list:
        return {}
    quotes: dict[str, dict[str, Any]] = {}
    chunk_size = 40
    for index in range(0, len(ticker_list), chunk_size):
        chunk = ticker_list[index : index + chunk_size]
        try:
            data = fmp_get(f"quote/{','.join(chunk)}")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            print(f"Warning: quote fetch failed for {','.join(chunk)}: {exc}", file=sys.stderr)
            continue
        if isinstance(data, list):
            for row in data:
                symbol = str(row.get("symbol", "")).upper()
                if symbol:
                    quotes[symbol] = row
    return quotes


def fetch_history(ticker: str, lookback: int = 140) -> list[dict[str, Any]]:
    try:
        data = fmp_get(f"historical-price-full/{ticker}", {"timeseries": lookback}, timeout=20)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"Warning: history fetch failed for {ticker}: {exc}", file=sys.stderr)
        return []
    rows = data.get("historical", []) if isinstance(data, dict) else []
    return rows if isinstance(rows, list) else []


def fetch_earnings(tickers: Iterable[str], horizon_days: int = 21) -> dict[str, str]:
    today = date.today()
    params = {
        "from": today.isoformat(),
        "to": (today + timedelta(days=horizon_days)).isoformat(),
    }
    try:
        data = fmp_get("earning_calendar", params, timeout=20)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"Warning: earnings fetch failed: {exc}", file=sys.stderr)
        return {}
    wanted = {ticker.upper() for ticker in tickers}
    result: dict[str, str] = {}
    if isinstance(data, list):
        for item in data:
            symbol = str(item.get("symbol", "")).upper()
            if symbol in wanted and item.get("date"):
                result[symbol] = str(item["date"])
    return result


def average(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def pct_change(new: float, old: float) -> float | None:
    if old == 0:
        return None
    return (new / old - 1.0) * 100


def technicals(ticker: str, quote: dict[str, Any]) -> dict[str, float | None]:
    history = fetch_history(ticker)
    closes = [float(row.get("close")) for row in history if row.get("close") is not None]
    price = float(quote.get("price") or (closes[0] if closes else 0.0))
    sma20 = average(closes[:20])
    sma50 = average(closes[:50])
    close_21 = closes[21] if len(closes) > 21 else None
    close_63 = closes[63] if len(closes) > 63 else None
    low_52w = min(closes[:252]) if closes else None
    high_52w = max(closes[:252]) if closes else None
    return {
        "price": price,
        "sma20": sma20,
        "sma50": sma50,
        "return_1m": pct_change(price, close_21) if close_21 else None,
        "return_3m": pct_change(price, close_63) if close_63 else None,
        "distance_sma50": pct_change(price, sma50) if sma50 else None,
        "low_52w": low_52w,
        "high_52w": high_52w,
        "pct_from_high": pct_change(price, high_52w) if high_52w else None,
    }


def market_snapshot(quotes: dict[str, dict[str, Any]]) -> MarketSnapshot:
    spy = quotes.get("SPY", {})
    vix = quotes.get("^VIX", {})
    vix_level = parse_float(str(vix.get("price", "")))
    if vix_level is None:
        regime = "UNKNOWN"
    elif vix_level < 15:
        regime = "GREEN: low vol"
    elif vix_level < 22:
        regime = "YELLOW: normal vol"
    elif vix_level < 30:
        regime = "ORANGE: elevated vol"
    else:
        regime = "RED: crisis vol"
    return MarketSnapshot(
        spy_price=parse_float(str(spy.get("price", ""))),
        spy_change_pct=parse_float(str(spy.get("changesPercentage", ""))),
        vix=vix_level,
        vix_change_pct=parse_float(str(vix.get("changesPercentage", ""))),
        regime=regime,
    )


def status_bonus(status: str) -> float:
    normalized = status.lower()
    if "top candidate" in normalized:
        return 12
    if "consider" in normalized:
        return 6
    if "monitor" in normalized:
        return 0
    if "low" in normalized:
        return -8
    if "avoid" in normalized:
        return -20
    return 0


def build_ideas(
    holdings: list[Holding],
    watchlist: list[WatchlistEntry],
    quotes: dict[str, dict[str, Any]],
    earnings: dict[str, str],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, float | None]]]:
    holding_by_ticker = {holding.ticker: holding for holding in holdings}
    watch_by_ticker = {entry.ticker: entry for entry in watchlist}
    tech_cache: dict[str, dict[str, float | None]] = {}
    ideas: list[dict[str, Any]] = []

    for entry in watchlist:
        if "avoid" in entry.status.lower():
            continue
        quote = quotes.get(entry.ticker, {})
        if not quote:
            continue
        tech_cache[entry.ticker] = technicals(entry.ticker, quote)
        tech = tech_cache[entry.ticker]
        price = tech["price"] or parse_float(str(quote.get("price", ""))) or 0.0
        if price <= 0:
            continue
        distance_sma50 = tech["distance_sma50"] or 0.0
        momentum_score = max(min(distance_sma50, 20), -20)
        not_held_bonus = 8 if entry.ticker not in holding_by_ticker else -2
        earnings_penalty = -18 if entry.ticker in earnings else 0
        score = (entry.score or 45) + status_bonus(entry.status) + momentum_score + not_held_bonus + earnings_penalty
        strike = round(price * 0.92)
        action = "WATCHLIST CSP / starter add"
        rationale = [
            f"{entry.status or 'watchlist'} with score {entry.score if entry.score is not None else 'n/a'}",
            f"price {distance_sma50:+.1f}% vs 50-day average" if tech["sma50"] else "50-day trend unavailable",
        ]
        if entry.ticker in earnings:
            rationale.append(f"earnings on {earnings[entry.ticker]}: wait until event passes")
        else:
            rationale.append("no earnings conflict inside 21-day scan")
        ideas.append(
            {
                "ticker": entry.ticker,
                "company": entry.company,
                "idea_type": action,
                "score": round(score, 1),
                "current_price": round(price, 2),
                "target_entry": round(price * 0.95, 2),
                "suggested_put_strike": strike,
                "position_context": "not held" if entry.ticker not in holding_by_ticker else f"held {holding_by_ticker[entry.ticker].weight:.1f}%",
                "earnings": earnings.get(entry.ticker, "none in next 21d"),
                "rationale": rationale,
                "risk": "Use paper-trade workflow; skip if bid/ask spread is wide or earnings date moves inside DTE.",
            }
        )

    for holding in holdings:
        if holding.ticker in ETF_TICKERS:
            continue
        quote = quotes.get(holding.ticker, {})
        if not quote:
            continue
        if holding.ticker not in tech_cache:
            tech_cache[holding.ticker] = technicals(holding.ticker, quote)
        tech = tech_cache[holding.ticker]
        distance_sma50 = tech["distance_sma50"] or 0.0
        if holding.weight >= 10 or (holding.pnl_pct >= 80 and distance_sma50 >= 8):
            score = 60 + holding.weight + min(holding.pnl_pct / 10, 15) + max(distance_sma50, 0)
            ideas.append(
                {
                    "ticker": holding.ticker,
                    "company": watch_by_ticker.get(holding.ticker, WatchlistEntry(holding.ticker, None, "", holding.ticker, "")).company,
                    "idea_type": "POSITION MANAGEMENT / covered-call or trim review",
                    "score": round(score, 1),
                    "current_price": round(tech["price"] or holding.current, 2),
                    "target_entry": None,
                    "suggested_put_strike": None,
                    "position_context": f"current weight {holding.weight:.1f}%, unrealized P/L {holding.pnl_pct:+.1f}%",
                    "earnings": earnings.get(holding.ticker, "none in next 21d"),
                    "rationale": [
                        "large concentration or extended winner",
                        f"price {distance_sma50:+.1f}% vs 50-day average" if tech["sma50"] else "50-day trend unavailable",
                        "consider 20-30 delta covered call only if comfortable selling upside",
                    ],
                    "risk": "Do not cap core compounder upside unless allocation/risk budget requires it.",
                }
            )

    return sorted(ideas, key=lambda row: row["score"], reverse=True), tech_cache


def format_money(value: float | None) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "n/a"
    return f"${value:,.2f}"


def format_pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:+.1f}%"


def render_report(
    run_date: str,
    market: MarketSnapshot,
    holdings: list[Holding],
    watchlist: list[WatchlistEntry],
    ideas: list[dict[str, Any]],
    tech_cache: dict[str, dict[str, float | None]],
) -> str:
    top = ideas[:8]
    lines = [
        f"# Trade Idea Generator - {run_date}",
        "",
        "> Generated from `context/portfolio-details.md` and `context/watchlist.md`.",
        "",
        "## Market Snapshot",
        "",
        f"- SPY: {format_money(market.spy_price)} ({format_pct(market.spy_change_pct)} today)",
        f"- VIX: {market.vix if market.vix is not None else 'n/a'} ({format_pct(market.vix_change_pct)} today)",
        f"- Regime: {market.regime}",
        "",
        "## Top Ideas",
        "",
    ]
    if not top:
        lines.append("No qualifying ideas generated.")
    for index, idea in enumerate(top, 1):
        tech = tech_cache.get(idea["ticker"], {})
        lines.extend(
            [
                f"### {index}. {idea['ticker']} - {idea['idea_type']} (score {idea['score']})",
                "",
                f"- Current price: {format_money(idea['current_price'])}",
                f"- Position context: {idea['position_context']}",
                f"- Earnings: {idea['earnings']}",
                f"- 50-day distance: {format_pct(tech.get('distance_sma50'))}",
                f"- 1m / 3m momentum: {format_pct(tech.get('return_1m'))} / {format_pct(tech.get('return_3m'))}",
            ]
        )
        if idea.get("target_entry") is not None:
            lines.append(f"- Target starter entry: {format_money(idea['target_entry'])}")
        if idea.get("suggested_put_strike") is not None:
            lines.append(f"- CSP strike to evaluate: {idea['suggested_put_strike']} put (roughly 8% OTM)")
        lines.append("- Rationale:")
        for item in idea["rationale"]:
            lines.append(f"  - {item}")
        lines.append(f"- Risk note: {idea['risk']}")
        lines.append("")

    lines.extend(
        [
            "## Universe Summary",
            "",
            f"- Holdings scanned: {len(holdings)}",
            f"- Watchlist names scanned: {len(watchlist)}",
            f"- Ideas generated: {len(ideas)}",
            "",
            "## Disclaimer",
            "",
            "This is an automation-generated research note, not financial advice or an order ticket. Verify liquidity, earnings dates, portfolio exposure, and risk limits before acting.",
            "",
        ]
    )
    return "\n".join(lines)


def render_telegram(run_date: str, market: MarketSnapshot, ideas: list[dict[str, Any]]) -> str:
    lines = [
        f"ALTAMIRA TRADE IDEAS - {run_date}",
        f"SPY {format_money(market.spy_price)} ({format_pct(market.spy_change_pct)}) | VIX {market.vix if market.vix is not None else 'n/a'}",
        f"Regime: {market.regime}",
        "",
    ]
    if not ideas:
        lines.append("No qualifying trade ideas today.")
    for index, idea in enumerate(ideas[:5], 1):
        lines.extend(
            [
                f"{index}) {idea['ticker']} - {idea['idea_type']}",
                f"Score {idea['score']} | Px {format_money(idea['current_price'])} | {idea['position_context']}",
            ]
        )
        if idea.get("suggested_put_strike") is not None:
            lines.append(f"Evaluate: starter buy near {format_money(idea['target_entry'])} or CSP around {idea['suggested_put_strike']}P")
        lines.append(f"Earnings: {idea['earnings']}")
        lines.append("")
    lines.append("Research only. Verify liquidity, earnings, and Altamira risk limits before any trade.")
    return "\n".join(lines)


def send_telegram(bot_token: str, chat_id: str, text: str) -> dict[str, Any]:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = json.dumps(
        {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": True,
        }
    ).encode("utf-8")
    request = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate trade ideas from current portfolio and watchlist.")
    parser.add_argument("--send-telegram", action="store_true", help="Send the summary to Telegram.")
    parser.add_argument("--telegram-chat-id", default=DEFAULT_TELEGRAM_CHAT_ID, help="Telegram chat/channel ID.")
    parser.add_argument("--telegram-token", default=os.environ.get("TELEGRAM_BOT_TOKEN"), help="Telegram bot token.")
    parser.add_argument("--out-dir", default=str(OUTPUTS), help="Output directory.")
    parser.add_argument("--top", type=int, default=8, help="Number of ideas to include in report.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_date = datetime.now(timezone.utc).date().isoformat()
    holdings = load_holdings(CONTEXT / "portfolio-details.md")
    watchlist = load_watchlist(CONTEXT / "watchlist.md")
    universe = {holding.ticker for holding in holdings} | {entry.ticker for entry in watchlist} | {"SPY", "^VIX"}
    quotes = fetch_quotes(universe)
    earnings = fetch_earnings(universe)
    market = market_snapshot(quotes)
    ideas, tech_cache = build_ideas(holdings, watchlist, quotes, earnings)
    ideas = ideas[: max(args.top, 1)]

    output_dir = Path(args.out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report = render_report(run_date, market, holdings, watchlist, ideas, tech_cache)
    telegram_text = render_telegram(run_date, market, ideas)
    md_path = output_dir / f"trade-idea-generator-{run_date}.md"
    json_path = output_dir / f"trade-idea-generator-{run_date}.json"
    md_path.write_text(report, encoding="utf-8")
    json_path.write_text(
        json.dumps(
            {
                "date": run_date,
                "market": market.__dict__,
                "ideas": ideas,
                "telegram_text": telegram_text,
                "source_files": ["context/portfolio-details.md", "context/watchlist.md"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"Wrote {md_path.relative_to(WORKSPACE)}")
    print(f"Wrote {json_path.relative_to(WORKSPACE)}")
    print()
    print(telegram_text)

    if args.send_telegram:
        if not args.telegram_token:
            raise SystemExit("TELEGRAM_BOT_TOKEN is required for --send-telegram")
        if not args.telegram_chat_id:
            raise SystemExit("TELEGRAM_CHAT_ID or --telegram-chat-id is required for --send-telegram")
        response = send_telegram(args.telegram_token, args.telegram_chat_id, telegram_text)
        print()
        print(f"Telegram send ok: {response.get('ok')} message_id={response.get('result', {}).get('message_id')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
