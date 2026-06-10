#!/usr/bin/env python3
"""Generate a daily market recap and optionally deliver it to Telegram.

The report uses Yahoo chart data for broad-market quotes so it can run without
paid data credentials. If FMP_API_KEY is present, it enriches the recap with
FMP gainers/losers and earnings-calendar data.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import requests


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS = WORKSPACE / "outputs"
YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
FMP_BASE = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"
USER_AGENT = "AltamiraDailyMarketRecap/1.0"

INDICES = {
    "^GSPC": "S&P 500",
    "^IXIC": "Nasdaq Composite",
    "^DJI": "Dow Jones Industrial Average",
    "^VIX": "CBOE Volatility Index",
    "SPY": "SPDR S&P 500 ETF",
    "QQQ": "Invesco QQQ ETF",
}

SECTOR_ETFS = {
    "XLK": "Technology",
    "XLF": "Financials",
    "XLV": "Health Care",
    "XLY": "Consumer Discretionary",
    "XLC": "Communication Services",
    "XLI": "Industrials",
    "XLP": "Consumer Staples",
    "XLE": "Energy",
    "XLU": "Utilities",
    "XLB": "Materials",
    "XLRE": "Real Estate",
}

LARGE_CAP_UNIVERSE = [
    "AAPL",
    "MSFT",
    "NVDA",
    "GOOGL",
    "GOOG",
    "AMZN",
    "META",
    "AVGO",
    "TSLA",
    "BRK-B",
    "JPM",
    "WMT",
    "LLY",
    "V",
    "MA",
    "NFLX",
    "COST",
    "ORCL",
    "HD",
    "PG",
    "JNJ",
    "BAC",
    "ABBV",
    "KO",
    "PLTR",
    "CRM",
    "AMD",
    "UNH",
    "CSCO",
    "MCD",
]


@dataclass
class Quote:
    symbol: str
    name: str
    price: float | None
    previous_close: float | None
    change_percent: float | None
    closes: list[float]


def pct(value: float | None) -> str:
    """Format a percentage with sign."""
    if value is None:
        return "N/A"
    return f"{value:+.2f}%"


def money(value: float | None) -> str:
    """Format a market level."""
    if value is None:
        return "N/A"
    return f"{value:,.2f}"


def request_json(
    session: requests.Session,
    url: str,
    params: dict[str, Any] | None = None,
) -> Any | None:
    """Fetch JSON, returning None on recoverable data errors."""
    try:
        response = session.get(url, params=params or {}, timeout=20)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        print(f"[daily_market_recap] Request failed for {url.split('?')[0]}: {exc}", file=sys.stderr)
    except ValueError as exc:
        print(f"[daily_market_recap] Invalid JSON from {url.split('?')[0]}: {exc}", file=sys.stderr)
    return None


def fetch_yahoo_quote(session: requests.Session, symbol: str, name: str | None = None) -> Quote:
    """Fetch current and recent daily data from Yahoo Finance chart API."""
    url = YAHOO_CHART_URL.format(symbol=symbol)
    params = {"range": "1mo", "interval": "1d", "includePrePost": "false"}
    data = request_json(session, url, params)
    fallback_name = name or symbol
    if not isinstance(data, dict):
        return Quote(symbol, fallback_name, None, None, None, [])

    result = (((data.get("chart") or {}).get("result")) or [None])[0]
    if not isinstance(result, dict):
        return Quote(symbol, fallback_name, None, None, None, [])

    meta = result.get("meta") or {}
    indicators = result.get("indicators") or {}
    quote_rows = indicators.get("quote") or []
    raw_closes = []
    if quote_rows and isinstance(quote_rows[0], dict):
        raw_closes = quote_rows[0].get("close") or []
    closes = [float(close) for close in raw_closes if isinstance(close, (int, float))]

    price = meta.get("regularMarketPrice")
    if not isinstance(price, (int, float)):
        price = closes[-1] if closes else None
    previous_close = meta.get("previousClose") or meta.get("chartPreviousClose")
    if not isinstance(previous_close, (int, float)) and len(closes) >= 2:
        previous_close = closes[-2]

    change_percent = None
    if isinstance(price, (int, float)) and isinstance(previous_close, (int, float)) and previous_close:
        change_percent = ((float(price) - float(previous_close)) / float(previous_close)) * 100

    resolved_name = name or meta.get("longName") or meta.get("shortName") or symbol
    return Quote(
        symbol=symbol,
        name=resolved_name,
        price=float(price) if isinstance(price, (int, float)) else None,
        previous_close=float(previous_close) if isinstance(previous_close, (int, float)) else None,
        change_percent=change_percent,
        closes=closes,
    )


def moving_average(values: list[float], window: int) -> float | None:
    """Return the simple moving average for the trailing window."""
    if len(values) < window:
        return None
    return sum(values[-window:]) / window


def trend_label(price: float | None, sma_5: float | None, sma_20: float | None) -> str:
    """Classify the index trend from current price vs moving averages."""
    if price is None or sma_5 is None or sma_20 is None:
        return "Insufficient data"
    if price > sma_5 and price > sma_20:
        return "Bullish"
    if price < sma_5 and price < sma_20:
        return "Bearish"
    return "Mixed"


def vix_label(value: float | None) -> str:
    """Classify current VIX level."""
    if value is None:
        return "unknown"
    if value >= 25:
        return "elevated/stress"
    if value >= 20:
        return "elevated"
    if value < 15:
        return "low"
    return "normal"


def fetch_fmp_list(
    session: requests.Session,
    path: str,
    api_key: str | None,
    params: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Fetch an optional FMP list endpoint."""
    if not api_key:
        return []
    url = f"{FMP_STABLE}{path}" if path.startswith("/stable/") else f"{FMP_BASE}{path}"
    clean_path = path.replace("/stable", "", 1)
    if path.startswith("/stable/"):
        url = f"{FMP_STABLE}{clean_path}"
    payload = dict(params or {})
    payload["apikey"] = api_key
    data = request_json(session, url, payload)
    return data if isinstance(data, list) else []


def extract_change_percent(row: dict[str, Any]) -> float | None:
    """Parse common FMP percentage fields."""
    raw = row.get("changesPercentage") or row.get("changePercentage") or row.get("changes")
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, str):
        cleaned = raw.replace("%", "").replace("+", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def ranked_large_cap_movers(session: requests.Session) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Find biggest up/down movers in a liquid large-cap universe."""
    rows = []
    for symbol in LARGE_CAP_UNIVERSE:
        quote = fetch_yahoo_quote(session, symbol)
        if quote.change_percent is None:
            continue
        rows.append({"symbol": symbol, "change": quote.change_percent, "price": quote.price})
    if not rows:
        return None, None
    rows.sort(key=lambda item: item["change"], reverse=True)
    return rows[0], rows[-1]


def build_report(run_date: date) -> tuple[Path, Path, str]:
    """Generate the markdown recap and plain-text summary."""
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    quotes = {
        symbol: fetch_yahoo_quote(session, symbol, label)
        for symbol, label in INDICES.items()
    }
    sectors = {
        symbol: fetch_yahoo_quote(session, symbol, label)
        for symbol, label in SECTOR_ETFS.items()
    }

    fmp_key = os.environ.get("FMP_API_KEY")
    gainers = fetch_fmp_list(session, "/stable/biggest-gainers", fmp_key)
    losers = fetch_fmp_list(session, "/stable/biggest-losers", fmp_key)
    earnings = fetch_fmp_list(
        session,
        "/earning_calendar",
        fmp_key,
        {
            "from": run_date.isoformat(),
            "to": (run_date + timedelta(days=7)).isoformat(),
        },
    )

    fallback_gainer, fallback_loser = ranked_large_cap_movers(session)
    top_gainer = gainers[0] if gainers else fallback_gainer
    top_loser = losers[0] if losers else fallback_loser
    mover_source = "FMP biggest movers" if gainers and losers else "large-cap watchlist fallback"

    sector_quotes = [quote for quote in sectors.values() if quote.change_percent is not None]
    sector_quotes.sort(key=lambda quote: quote.change_percent or 0, reverse=True)
    best_sector = sector_quotes[0] if sector_quotes else None
    worst_sector = sector_quotes[-1] if sector_quotes else None

    spx = quotes["^GSPC"]
    vix = quotes["^VIX"]
    sma_5 = moving_average(spx.closes, 5)
    sma_20 = moving_average(spx.closes, 20)
    support = min(spx.closes[-20:]) if len(spx.closes) >= 20 else None
    resistance = max(spx.closes[-20:]) if len(spx.closes) >= 20 else None
    trend = trend_label(spx.price, sma_5, sma_20)

    gainer_symbol = (top_gainer or {}).get("symbol") or "N/A"
    loser_symbol = (top_loser or {}).get("symbol") or "N/A"
    gainer_change = extract_change_percent(top_gainer or {}) if gainers else (top_gainer or {}).get("change")
    loser_change = extract_change_percent(top_loser or {}) if losers else (top_loser or {}).get("change")

    summary = (
        f"Daily market recap for {run_date.isoformat()}: "
        f"S&P 500 {pct(spx.change_percent)} at {money(spx.price)}; "
        f"Nasdaq {pct(quotes['^IXIC'].change_percent)}; Dow {pct(quotes['^DJI'].change_percent)}. "
        f"VIX is {vix_label(vix.price)} at {money(vix.price)}. "
        f"Trend: {trend}. "
        f"Best sector: {(best_sector.name if best_sector else 'N/A')} {pct(best_sector.change_percent if best_sector else None)}; "
        f"worst sector: {(worst_sector.name if worst_sector else 'N/A')} {pct(worst_sector.change_percent if worst_sector else None)}. "
        f"Top mover: {gainer_symbol} {pct(gainer_change)}; weakest mover: {loser_symbol} {pct(loser_change)}."
    )

    earnings_rows = []
    for item in earnings[:12]:
        earnings_rows.append(
            "| {date} | {symbol} | {eps} | {revenue} |".format(
                date=item.get("date", "N/A"),
                symbol=item.get("symbol", "N/A"),
                eps=item.get("epsEstimated", "N/A"),
                revenue=item.get("revenueEstimated", "N/A"),
            )
        )

    if not earnings_rows:
        earnings_rows.append("| N/A | N/A | N/A | N/A |")

    report = f"""# Daily Market Recap - {run_date.isoformat()}

**Generated:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}  
**Data sources:** Yahoo Finance chart API; FMP enrichment {'enabled' if fmp_key else 'not configured'}

> Informational market recap for Altamira Capital. Not investment advice.

## Executive summary

{summary}

## Major indices

| Index | Level | Day change |
|---|---:|---:|
| S&P 500 (^GSPC) | {money(quotes['^GSPC'].price)} | {pct(quotes['^GSPC'].change_percent)} |
| Nasdaq Composite (^IXIC) | {money(quotes['^IXIC'].price)} | {pct(quotes['^IXIC'].change_percent)} |
| Dow Jones (^DJI) | {money(quotes['^DJI'].price)} | {pct(quotes['^DJI'].change_percent)} |
| SPY | {money(quotes['SPY'].price)} | {pct(quotes['SPY'].change_percent)} |
| QQQ | {money(quotes['QQQ'].price)} | {pct(quotes['QQQ'].change_percent)} |

## Volatility

- **VIX:** {money(vix.price)} ({pct(vix.change_percent)}), classified as **{vix_label(vix.price)}**.

## S&P 500 technical snapshot

| Metric | Value |
|---|---:|
| Current level | {money(spx.price)} |
| 5-day average | {money(sma_5)} |
| 20-day average | {money(sma_20)} |
| 20-day support | {money(support)} |
| 20-day resistance | {money(resistance)} |
| Trend | {trend} |

## Sector leadership

| Rank | Sector ETF | Sector | Day change |
|---:|---|---|---:|
"""

    for index, quote in enumerate(sector_quotes, start=1):
        report += f"| {index} | {quote.symbol} | {quote.name} | {pct(quote.change_percent)} |\n"

    if not sector_quotes:
        report += "| N/A | N/A | N/A | N/A |\n"

    report += f"""
## Movers

**Source:** {mover_source}

| Category | Symbol | Day change |
|---|---|---:|
| Top mover | {gainer_symbol} | {pct(gainer_change)} |
| Weakest mover | {loser_symbol} | {pct(loser_change)} |

## Earnings calendar: next 7 days

| Date | Symbol | EPS estimate | Revenue estimate |
|---|---|---:|---:|
{chr(10).join(earnings_rows)}

## Market read-through

- Breadth proxy: sector ETFs show **{best_sector.name if best_sector else 'N/A'}** leading and **{worst_sector.name if worst_sector else 'N/A'}** lagging.
- Risk tone: VIX at **{money(vix.price)}** points to a **{vix_label(vix.price)}** volatility backdrop.
- Trend setup: S&P 500 is classified as **{trend}** versus its 5-day and 20-day averages.
"""

    report_path = OUTPUTS / f"daily-market-recap-{run_date.isoformat()}.md"
    summary_path = OUTPUTS / f"daily-market-recap-summary-{run_date.isoformat()}.txt"
    report_path.write_text(report, encoding="utf-8")
    summary_path.write_text(summary + "\n", encoding="utf-8")
    return report_path, summary_path, summary


def send_telegram_message(
    bot_token: str,
    chat_id: str,
    summary: str,
    report_path: Path,
) -> None:
    """Send the summary message and markdown report to Telegram."""
    base_url = f"https://api.telegram.org/bot{bot_token}"
    message_response = requests.post(
        f"{base_url}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": summary,
            "disable_web_page_preview": "true",
        },
        timeout=20,
    )
    if not message_response.ok:
        description = ""
        try:
            description = message_response.json().get("description", "")
        except ValueError:
            description = message_response.text
        raise RuntimeError(f"Telegram sendMessage failed: {description or message_response.status_code}")

    with report_path.open("rb") as report_file:
        document_response = requests.post(
            f"{base_url}/sendDocument",
            data={
                "chat_id": chat_id,
                "caption": f"Daily market recap markdown report: {report_path.name}",
            },
            files={"document": (report_path.name, report_file, "text/markdown")},
            timeout=30,
        )
    if not document_response.ok:
        description = ""
        try:
            description = document_response.json().get("description", "")
        except ValueError:
            description = document_response.text
        raise RuntimeError(f"Telegram sendDocument failed: {description or document_response.status_code}")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate and send the Altamira daily market recap")
    parser.add_argument("--date", default=date.today().isoformat(), help="Report date in YYYY-MM-DD format")
    parser.add_argument("--skip-telegram", action="store_true", help="Generate files without Telegram delivery")
    parser.add_argument("--telegram-chat-id", default=os.environ.get("TELEGRAM_CHAT_ID"), help="Telegram chat/channel ID")
    parser.add_argument(
        "--telegram-bot-token",
        default=os.environ.get("TELEGRAM_BOT_TOKEN"),
        help="Telegram bot token (defaults to TELEGRAM_BOT_TOKEN)",
    )
    return parser.parse_args()


def main() -> int:
    """Run the recap workflow."""
    args = parse_args()
    try:
        run_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    except ValueError:
        print("--date must use YYYY-MM-DD", file=sys.stderr)
        return 1

    report_path, summary_path, summary = build_report(run_date)
    print(summary, flush=True)
    print(f"Report: {report_path}", flush=True)
    print(f"Summary: {summary_path}", flush=True)

    if args.skip_telegram:
        print("Telegram delivery skipped by --skip-telegram.")
        return 0

    missing = []
    if not args.telegram_bot_token:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not args.telegram_chat_id:
        missing.append("TELEGRAM_CHAT_ID")
    if missing:
        print(
            f"Telegram delivery not sent: missing {', '.join(missing)}. "
            f"Generated files remain at {report_path} and {summary_path}.",
            file=sys.stderr,
        )
        return 2

    try:
        send_telegram_message(args.telegram_bot_token, args.telegram_chat_id, summary, report_path)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 3

    print("Telegram delivery complete: summary message and markdown report sent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
