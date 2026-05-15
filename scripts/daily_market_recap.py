#!/usr/bin/env python3
"""Generate a daily market recap and optionally deliver it to Telegram."""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import requests


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS = WORKSPACE / "outputs"
FMP_V3 = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"
DEFAULT_FMP_KEY = "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz"
INDEX_SYMBOLS = "^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ"
INDEX_NAMES = {
    "^GSPC": "S&P 500",
    "^DJI": "Dow Jones",
    "^IXIC": "Nasdaq Composite",
    "^VIX": "VIX",
    "SPY": "SPY",
    "QQQ": "QQQ",
}


@dataclass(frozen=True)
class RecapPaths:
    markdown: Path
    summary: Path


def get_json(url: str, params: dict[str, Any] | None = None) -> Any:
    """Fetch JSON with a clear error if the upstream API fails."""
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    return response.json()


def safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def pct(value: Any) -> str:
    number = safe_float(value)
    if number is None:
        return "n/a"
    return f"{number:+.2f}%"


def money(value: Any) -> str:
    number = safe_float(value)
    if number is None:
        return "n/a"
    return f"{number:,.2f}"


def compact_number(value: Any) -> str:
    number = safe_float(value)
    if number is None:
        return "n/a"
    abs_number = abs(number)
    if abs_number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.1f}B"
    if abs_number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    return f"{number:,.0f}"


def vix_label(level: Any) -> str:
    value = safe_float(level)
    if value is None:
        return "unavailable"
    if value >= 30:
        return "crisis"
    if value >= 20:
        return "elevated"
    if value < 15:
        return "low"
    return "normal"


def fetch_quotes(api_key: str) -> dict[str, dict[str, Any]]:
    data = get_json(f"{FMP_V3}/quote/{INDEX_SYMBOLS}", {"apikey": api_key})
    if not isinstance(data, list):
        return {}
    return {item.get("symbol"): item for item in data if isinstance(item, dict) and item.get("symbol")}


def fetch_movers(api_key: str, endpoint: str, limit: int = 5) -> list[dict[str, Any]]:
    data = get_json(f"{FMP_STABLE}/{endpoint}", {"apikey": api_key})
    if not isinstance(data, list):
        return []
    return [item for item in data[:limit] if isinstance(item, dict)]


def fetch_sector_snapshot(api_key: str, date_str: str) -> list[dict[str, Any]]:
    """Fetch sector performance, falling back a few days for holidays/weekends."""
    start = datetime.strptime(date_str, "%Y-%m-%d")
    for offset in range(0, 5):
        query_date = (start - timedelta(days=offset)).strftime("%Y-%m-%d")
        data = get_json(
            f"{FMP_STABLE}/sector-performance-snapshot",
            {"date": query_date, "apikey": api_key},
        )
        if isinstance(data, list) and data:
            sectors = [item for item in data if isinstance(item, dict)]
            if sectors:
                return sectors
    return []


def fetch_historical(api_key: str, symbol: str, date_str: str) -> list[dict[str, Any]]:
    end = datetime.strptime(date_str, "%Y-%m-%d")
    start = end - timedelta(days=45)
    data = get_json(
        f"{FMP_STABLE}/historical-price-eod/light",
        {
            "symbol": symbol,
            "from": start.strftime("%Y-%m-%d"),
            "to": date_str,
            "apikey": api_key,
        },
    )
    if not isinstance(data, list):
        return []
    rows = [item for item in data if isinstance(item, dict)]
    return sorted(rows, key=lambda row: row.get("date", ""))


def historical_price(row: dict[str, Any]) -> float | None:
    return safe_float(row.get("close") or row.get("price") or row.get("adjClose"))


def moving_average(values: list[float], window: int) -> float | None:
    if len(values) < window:
        return None
    return sum(values[-window:]) / window


def fetch_earnings(api_key: str, date_str: str) -> list[dict[str, Any]]:
    start = datetime.strptime(date_str, "%Y-%m-%d")
    end = start + timedelta(days=7)
    data = get_json(
        f"{FMP_V3}/earning_calendar",
        {"from": date_str, "to": end.strftime("%Y-%m-%d"), "apikey": api_key},
    )
    if not isinstance(data, list):
        return []
    rows = [item for item in data if isinstance(item, dict)]
    return sorted(rows, key=lambda row: (row.get("date") or "", row.get("symbol") or ""))[:12]


def fetch_news(api_key: str) -> list[dict[str, Any]]:
    data = get_json(
        f"{FMP_STABLE}/news/general-latest",
        {"page": 0, "limit": 8, "apikey": api_key},
    )
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)][:6]


def change_direction(value: Any) -> str:
    number = safe_float(value)
    if number is None:
        return "flat"
    if number > 0.15:
        return "higher"
    if number < -0.15:
        return "lower"
    return "little changed"


def trend_label(current: float | None, ma_5: float | None, ma_20: float | None) -> str:
    if current is None or ma_5 is None or ma_20 is None:
        return "Unavailable"
    if current > ma_5 and current > ma_20:
        return "Bullish"
    if current < ma_5 and current < ma_20:
        return "Bearish"
    return "Mixed"


def top_sector(sectors: list[dict[str, Any]], reverse: bool) -> dict[str, Any] | None:
    valid = [sector for sector in sectors if safe_float(sector.get("averageChange")) is not None]
    if not valid:
        return None
    return sorted(valid, key=lambda sector: safe_float(sector.get("averageChange")) or 0, reverse=reverse)[0]


def format_sector(sector: dict[str, Any] | None) -> str:
    if not sector:
        return "n/a"
    return f"{sector.get('sector', 'Unknown')} ({pct(sector.get('averageChange'))})"


def quote_line(symbol: str, quote: dict[str, Any] | None) -> str:
    if not quote:
        return f"| {INDEX_NAMES.get(symbol, symbol)} | {symbol} | n/a | n/a | n/a |"
    return (
        f"| {INDEX_NAMES.get(symbol, symbol)} | {symbol} | {money(quote.get('price'))} | "
        f"{pct(quote.get('changesPercentage'))} | {money(quote.get('change'))} |"
    )


def mover_line(item: dict[str, Any]) -> str:
    return (
        f"| {item.get('symbol', 'n/a')} | {item.get('name', 'n/a')} | "
        f"{money(item.get('price'))} | {pct(item.get('changesPercentage'))} |"
    )


def news_line(item: dict[str, Any]) -> str:
    title = str(item.get("title") or "Untitled").replace("\n", " ").strip()
    publisher = item.get("publisher") or "Unknown"
    published = item.get("publishedDate") or "n/a"
    return f"- {title} ({publisher}, {published})"


def earnings_line(item: dict[str, Any]) -> str:
    return (
        f"| {item.get('date', 'n/a')} | {item.get('symbol', 'n/a')} | "
        f"{item.get('epsEstimated', 'n/a')} | {compact_number(item.get('revenueEstimated'))} |"
    )


def build_recap(api_key: str, date_str: str) -> tuple[str, str]:
    quotes = fetch_quotes(api_key)
    gainers = fetch_movers(api_key, "biggest-gainers")
    losers = fetch_movers(api_key, "biggest-losers")
    sectors = fetch_sector_snapshot(api_key, date_str)
    historical = fetch_historical(api_key, "^GSPC", date_str)
    earnings = fetch_earnings(api_key, date_str)
    news = fetch_news(api_key)

    spx_quote = quotes.get("^GSPC", {})
    spx_level = safe_float(spx_quote.get("price"))
    spx_change = safe_float(spx_quote.get("changesPercentage"))
    vix = quotes.get("^VIX", {})
    vix_level = safe_float(vix.get("price"))
    prices = [price for row in historical if (price := historical_price(row)) is not None]
    ma_5 = moving_average(prices, 5)
    ma_20 = moving_average(prices, 20)
    support = min(prices[-20:]) if len(prices) >= 20 else None
    resistance = max(prices[-20:]) if len(prices) >= 20 else None
    trend = trend_label(spx_level, ma_5, ma_20)
    best_sector = top_sector(sectors, reverse=True)
    worst_sector = top_sector(sectors, reverse=False)
    hot_stock = gainers[0] if gainers else {}
    weak_stock = losers[0] if losers else {}

    if spx_change is None:
        market_direction = "Markets were mixed or data was unavailable"
    else:
        market_direction = f"The S&P 500 traded {change_direction(spx_change)} at {pct(spx_change)}"

    summary = (
        f"Daily market recap ({date_str}): {market_direction}; trend {trend}; "
        f"VIX {money(vix_level)} ({vix_label(vix_level)}). "
        f"Best sector: {format_sector(best_sector)}. Worst sector: {format_sector(worst_sector)}. "
        f"Top gainer: {hot_stock.get('symbol', 'n/a')} {pct(hot_stock.get('changesPercentage'))}; "
        f"top loser: {weak_stock.get('symbol', 'n/a')} {pct(weak_stock.get('changesPercentage'))}."
    )

    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    markdown = f"""# Daily Market Recap - {date_str}

**Generated:** {generated_at}  
**Source:** Financial Modeling Prep (FMP)  
**Use:** Informational market recap for Altamira Capital.

## Executive summary

{summary}

## Market indices

| Index | Symbol | Level | Day change % | Point change |
| --- | --- | ---: | ---: | ---: |
{quote_line("^GSPC", quotes.get("^GSPC"))}
{quote_line("^IXIC", quotes.get("^IXIC"))}
{quote_line("^DJI", quotes.get("^DJI"))}
{quote_line("SPY", quotes.get("SPY"))}
{quote_line("QQQ", quotes.get("QQQ"))}
{quote_line("^VIX", quotes.get("^VIX"))}

## Market tone and levels

| Metric | Value |
| --- | ---: |
| S&P 500 level | {money(spx_level)} |
| S&P 500 5-day average | {money(ma_5)} |
| S&P 500 20-day average | {money(ma_20)} |
| 20-session support | {money(support)} |
| 20-session resistance | {money(resistance)} |
| Trend | {trend} |
| VIX regime | {vix_label(vix_level)} |

## Sector rotation

| Rank | Sector | Average change |
| --- | --- | ---: |
| Best | {best_sector.get("sector", "n/a") if best_sector else "n/a"} | {pct(best_sector.get("averageChange") if best_sector else None)} |
| Worst | {worst_sector.get("sector", "n/a") if worst_sector else "n/a"} | {pct(worst_sector.get("averageChange") if worst_sector else None)} |

## Biggest movers

### Top gainers

| Symbol | Name | Price | Change % |
| --- | --- | ---: | ---: |
{chr(10).join(mover_line(item) for item in gainers) if gainers else "| n/a | n/a | n/a | n/a |"}

### Top losers

| Symbol | Name | Price | Change % |
| --- | --- | ---: | ---: |
{chr(10).join(mover_line(item) for item in losers) if losers else "| n/a | n/a | n/a | n/a |"}

## Market drivers from headlines

{chr(10).join(news_line(item) for item in news) if news else "No broad market headlines were returned by FMP."}

## Earnings calendar - next 7 days

| Date | Symbol | EPS estimate | Revenue estimate |
| --- | --- | ---: | ---: |
{chr(10).join(earnings_line(item) for item in earnings) if earnings else "| n/a | No upcoming earnings returned | n/a | n/a |"}

## Trading desk notes

- Keep new option premium risk sized to the current VIX regime; {vix_label(vix_level)} volatility argues for {'wider strikes and smaller size' if (vix_level or 0) >= 20 else 'normal sizing discipline with standard stop rules'}.
- Treat {money(support)} as nearby S&P 500 support and {money(resistance)} as nearby resistance when planning index exposure.
- Avoid holding short-dated options through unplanned earnings events unless the trade thesis explicitly prices event risk.

## Disclaimer

This recap is for informational purposes only and is not investment advice, a recommendation, or an offer to buy or sell securities or derivatives. Market data may be delayed or revised; verify levels before trading.
"""
    return summary, markdown


def write_outputs(date_str: str, summary: str, markdown: str) -> RecapPaths:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    paths = RecapPaths(
        markdown=OUTPUTS / f"daily-market-recap-{date_str}.md",
        summary=OUTPUTS / f"daily-market-recap-summary-{date_str}.txt",
    )
    paths.markdown.write_text(markdown, encoding="utf-8")
    paths.summary.write_text(summary + "\n", encoding="utf-8")
    return paths


def telegram_request(method: str, token: str, **kwargs: Any) -> dict[str, Any]:
    url = f"https://api.telegram.org/bot{token}/{method}"
    response = requests.post(url, timeout=30, **kwargs)
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram {method} failed: {data}")
    return data


def send_telegram(token: str, chat_id: str, summary: str, markdown_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    text = (
        f"{summary}\n\n"
        f"Report attached: {markdown_path.name}\n"
        "Disclaimer: Informational only; verify market data before trading."
    )
    message_result = telegram_request(
        "sendMessage",
        token,
        data={"chat_id": chat_id, "text": text, "disable_web_page_preview": True},
    )
    with markdown_path.open("rb") as handle:
        document_result = telegram_request(
            "sendDocument",
            token,
            data={"chat_id": chat_id, "caption": f"Daily market recap - {markdown_path.stem[-10:]}"},
            files={"document": (markdown_path.name, handle, "text/markdown")},
        )
    return message_result, document_result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate and optionally send a daily market recap.")
    parser.add_argument("--date", default=datetime.utcnow().strftime("%Y-%m-%d"), help="Recap date YYYY-MM-DD")
    parser.add_argument("--fmp-key", default=os.environ.get("FMP_API_KEY", DEFAULT_FMP_KEY), help="FMP API key")
    parser.add_argument("--telegram-token", default=os.environ.get("TELEGRAM_BOT_TOKEN"), help="Telegram bot token")
    parser.add_argument("--chat-id", default=os.environ.get("TELEGRAM_CHAT_ID"), help="Telegram chat/channel ID")
    parser.add_argument("--send-telegram", action="store_true", help="Send summary and markdown to Telegram")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        print("--date must use YYYY-MM-DD", file=sys.stderr)
        return 2

    try:
        summary, markdown = build_recap(args.fmp_key, args.date)
        paths = write_outputs(args.date, summary, markdown)
    except Exception as exc:
        print(f"Failed to generate recap: {exc}", file=sys.stderr)
        return 1

    print(summary)
    print(f"Markdown: {paths.markdown}")
    print(f"Summary: {paths.summary}")

    if args.send_telegram:
        if not args.telegram_token:
            print("TELEGRAM_BOT_TOKEN is required when --send-telegram is set.", file=sys.stderr)
            return 2
        if not args.chat_id:
            print("TELEGRAM_CHAT_ID or --chat-id is required when --send-telegram is set.", file=sys.stderr)
            return 2
        try:
            message_result, document_result = send_telegram(
                args.telegram_token,
                str(args.chat_id),
                summary,
                paths.markdown,
            )
        except Exception as exc:
            print(f"Failed to send Telegram delivery: {exc}", file=sys.stderr)
            return 1
        print(f"Telegram message_id: {message_result['result']['message_id']}")
        print(f"Telegram document_message_id: {document_result['result']['message_id']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
