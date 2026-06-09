#!/usr/bin/env python3
"""Generate a daily market recap and optionally deliver it to Telegram."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import requests


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS = WORKSPACE / "outputs"
FMP_V3 = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"


@dataclass(frozen=True)
class MarketQuote:
    """Normalized quote data from FMP."""

    symbol: str
    name: str
    price: float | None
    change_pct: float | None
    change: float | None = None


def request_json(url: str, params: dict[str, Any] | None = None) -> Any:
    """Fetch JSON with a concise error if the upstream API fails."""
    response = requests.get(url, params=params, timeout=25)
    response.raise_for_status()
    return response.json()


def as_float(value: Any) -> float | None:
    """Convert FMP numeric fields, including percent strings, to float."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace("%", "").replace(",", "").strip()
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def format_number(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "--"
    return f"{value:,.{digits}f}"


def format_pct(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "--"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.{digits}f}%"


def quote_from_row(row: dict[str, Any], fallback_symbol: str) -> MarketQuote:
    symbol = str(row.get("symbol") or fallback_symbol)
    name = str(row.get("name") or row.get("companyName") or symbol)
    return MarketQuote(
        symbol=symbol,
        name=name,
        price=as_float(row.get("price")),
        change_pct=as_float(row.get("changesPercentage") or row.get("changePercentage")),
        change=as_float(row.get("change")),
    )


def fetch_quotes(api_key: str) -> dict[str, MarketQuote]:
    symbols = "^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ"
    data = request_json(f"{FMP_V3}/quote/{symbols}", {"apikey": api_key})
    quotes: dict[str, MarketQuote] = {}
    if isinstance(data, list):
        for row in data:
            if isinstance(row, dict):
                quote = quote_from_row(row, str(row.get("symbol") or ""))
                quotes[quote.symbol] = quote
    return quotes


def fetch_simple_list(api_key: str, path: str) -> list[dict[str, Any]]:
    data = request_json(f"{FMP_STABLE}/{path}", {"apikey": api_key})
    return data if isinstance(data, list) else []


def fetch_sector_snapshot(api_key: str, recap_date: date) -> list[dict[str, Any]]:
    """Fetch the latest available sector snapshot, trying recent dates."""
    for days_back in range(0, 8):
        snapshot_date = recap_date - timedelta(days=days_back)
        params = {"date": snapshot_date.isoformat(), "apikey": api_key}
        try:
            data = request_json(f"{FMP_STABLE}/sector-performance-snapshot", params)
        except requests.RequestException:
            continue
        if isinstance(data, list) and data:
            return data
    return []


def fetch_earnings(api_key: str, recap_date: date) -> list[dict[str, Any]]:
    end_date = recap_date + timedelta(days=7)
    params = {
        "from": recap_date.isoformat(),
        "to": end_date.isoformat(),
        "apikey": api_key,
    }
    data = request_json(f"{FMP_V3}/earning_calendar", params)
    return data if isinstance(data, list) else []


def fetch_history(api_key: str, symbol: str, recap_date: date) -> list[dict[str, Any]]:
    start_date = recap_date - timedelta(days=45)
    params = {
        "symbol": symbol,
        "from": start_date.isoformat(),
        "to": recap_date.isoformat(),
        "apikey": api_key,
    }
    data = request_json(f"{FMP_STABLE}/historical-price-eod/light", params)
    rows = data if isinstance(data, list) else []
    return sorted(
        [row for row in rows if isinstance(row, dict) and as_float(row.get("close"))],
        key=lambda row: str(row.get("date") or ""),
    )


def fetch_general_news(api_key: str) -> list[dict[str, Any]]:
    params = {"page": 0, "limit": 10, "apikey": api_key}
    data = request_json(f"{FMP_STABLE}/news/general-latest", params)
    return data if isinstance(data, list) else []


def extract_sector_rows(raw_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sectors: list[dict[str, Any]] = []
    for row in raw_rows:
        sector = row.get("sector") or row.get("sectorName") or row.get("name")
        change_pct = as_float(
            row.get("changesPercentage")
            or row.get("changePercentage")
            or row.get("performance")
            or row.get("change")
        )
        if sector and change_pct is not None:
            sectors.append({"sector": str(sector), "change_pct": change_pct})
    return sectors


def top_mover(rows: list[dict[str, Any]]) -> MarketQuote | None:
    if not rows:
        return None
    row = rows[0]
    return MarketQuote(
        symbol=str(row.get("symbol") or "--"),
        name=str(row.get("name") or row.get("companyName") or row.get("symbol") or "--"),
        price=as_float(row.get("price")),
        change_pct=as_float(row.get("changesPercentage") or row.get("changePercentage")),
    )


def moving_average(history: list[dict[str, Any]], window: int) -> float | None:
    closes = [as_float(row.get("close")) for row in history]
    values = [value for value in closes if value is not None]
    if len(values) < window:
        return None
    return sum(values[-window:]) / window


def support_resistance(history: list[dict[str, Any]]) -> tuple[float | None, float | None]:
    closes = [as_float(row.get("close")) for row in history[-20:]]
    values = [value for value in closes if value is not None]
    if not values:
        return None, None
    return min(values), max(values)


def trend_label(current: float | None, avg_5: float | None, avg_20: float | None) -> str:
    if current is None or avg_5 is None or avg_20 is None:
        return "Mixed"
    if current > avg_5 and current > avg_20:
        return "Bullish"
    if current < avg_5 and current < avg_20:
        return "Bearish"
    return "Mixed"


def vix_label(vix: float | None) -> str:
    if vix is None:
        return "unavailable"
    if vix > 20:
        return "elevated"
    if vix < 15:
        return "low"
    return "normal"


def quote_table_row(label: str, quote: MarketQuote | None) -> str:
    if quote is None:
        return f"| {label} | -- | -- |"
    return (
        f"| {label} | {format_number(quote.price)} | "
        f"{format_pct(quote.change_pct)} |"
    )


def build_earnings_rows(earnings: list[dict[str, Any]], limit: int = 12) -> list[str]:
    rows = []
    for item in earnings[:limit]:
        symbol = item.get("symbol") or "--"
        report_date = item.get("date") or "--"
        eps = item.get("epsEstimated")
        rows.append(f"| {report_date} | {symbol} | {format_number(as_float(eps))} |")
    return rows


def headline_text(row: dict[str, Any]) -> str:
    return str(row.get("title") or row.get("headline") or "").strip()


def build_commentary(
    spx: MarketQuote | None,
    nasdaq: MarketQuote | None,
    dow: MarketQuote | None,
    vix: MarketQuote | None,
    best_sector: dict[str, Any] | None,
    worst_sector: dict[str, Any] | None,
    headlines: list[dict[str, Any]],
) -> str:
    index_moves = [
        f"S&P 500 {format_pct(spx.change_pct) if spx else '--'}",
        f"Nasdaq {format_pct(nasdaq.change_pct) if nasdaq else '--'}",
        f"Dow {format_pct(dow.change_pct) if dow else '--'}",
    ]
    sector_sentence = "Sector data was unavailable."
    if best_sector and worst_sector:
        sector_sentence = (
            f"{best_sector['sector']} led sectors at {format_pct(best_sector['change_pct'])}, "
            f"while {worst_sector['sector']} lagged at {format_pct(worst_sector['change_pct'])}."
        )
    headline_bits = [headline_text(row) for row in headlines[:3]]
    headline_bits = [text for text in headline_bits if text]
    headline_sentence = (
        "Headlines tracked for context: " + "; ".join(headline_bits) + "."
        if headline_bits
        else "No broad-market headlines were returned by FMP for context."
    )
    return (
        f"Major indices finished with {', '.join(index_moves)}. "
        f"VIX was {vix_label(vix.price if vix else None)} at "
        f"{format_number(vix.price) if vix else '--'}. "
        f"{sector_sentence} {headline_sentence}"
    )


def build_report(
    recap_date: date,
    quotes: dict[str, MarketQuote],
    gainers: list[dict[str, Any]],
    losers: list[dict[str, Any]],
    sectors: list[dict[str, Any]],
    earnings: list[dict[str, Any]],
    history: list[dict[str, Any]],
    headlines: list[dict[str, Any]],
) -> tuple[str, str]:
    spx = quotes.get("^GSPC")
    dow = quotes.get("^DJI")
    nasdaq = quotes.get("^IXIC")
    vix = quotes.get("^VIX")
    spy = quotes.get("SPY")
    qqq = quotes.get("QQQ")
    hot_stock = top_mover(gainers)
    biggest_loser = top_mover(losers)
    best_sector = max(sectors, key=lambda row: row["change_pct"]) if sectors else None
    worst_sector = min(sectors, key=lambda row: row["change_pct"]) if sectors else None
    avg_5 = moving_average(history, 5)
    avg_20 = moving_average(history, 20)
    support, resistance = support_resistance(history)
    trend = trend_label(spx.price if spx else None, avg_5, avg_20)
    commentary = build_commentary(
        spx, nasdaq, dow, vix, best_sector, worst_sector, headlines
    )

    earnings_rows = build_earnings_rows(earnings)
    if not earnings_rows:
        earnings_rows = ["| -- | No earnings returned for the next 7 days | -- |"]

    headline_rows = []
    for row in headlines[:5]:
        title = headline_text(row)
        if title:
            headline_rows.append(f"- {title}")
    if not headline_rows:
        headline_rows.append("- No broad-market headlines returned by FMP.")

    summary = (
        f"Altamira Daily Market Recap - {recap_date.isoformat()}\n"
        f"S&P 500 {format_number(spx.price if spx else None)} "
        f"({format_pct(spx.change_pct if spx else None)}), "
        f"Nasdaq {format_pct(nasdaq.change_pct if nasdaq else None)}, "
        f"Dow {format_pct(dow.change_pct if dow else None)}. "
        f"Trend: {trend}; VIX {format_number(vix.price if vix else None)} "
        f"({vix_label(vix.price if vix else None)}).\n"
        f"Best sector: "
        f"{best_sector['sector'] if best_sector else '--'} "
        f"{format_pct(best_sector['change_pct']) if best_sector else '--'}; "
        f"Worst sector: "
        f"{worst_sector['sector'] if worst_sector else '--'} "
        f"{format_pct(worst_sector['change_pct']) if worst_sector else '--'}.\n"
        f"Hot stock: {hot_stock.symbol if hot_stock else '--'} "
        f"{format_pct(hot_stock.change_pct if hot_stock else None)}; "
        f"Biggest loser: {biggest_loser.symbol if biggest_loser else '--'} "
        f"{format_pct(biggest_loser.change_pct if biggest_loser else None)}."
    )

    markdown = f"""# Daily Market Recap - {recap_date.isoformat()}

**Source:** Financial Modeling Prep (quotes, movers, sectors, earnings, headlines)

> Informational market recap only. Not investment advice.

## Market indices

| Index | Level | Change |
|---|---:|---:|
{quote_table_row("S&P 500 (^GSPC)", spx)}
{quote_table_row("Nasdaq Composite (^IXIC)", nasdaq)}
{quote_table_row("Dow Jones (^DJI)", dow)}

## ETFs and volatility

| Instrument | Level | Change |
|---|---:|---:|
{quote_table_row("SPY", spy)}
{quote_table_row("QQQ", qqq)}
{quote_table_row("VIX (^VIX)", vix)}

**VIX read:** {vix_label(vix.price if vix else None).title()}

## Movers

- **Hot stock:** {hot_stock.symbol if hot_stock else "--"} - {hot_stock.name if hot_stock else "--"} ({format_pct(hot_stock.change_pct if hot_stock else None)})
- **Biggest loser:** {biggest_loser.symbol if biggest_loser else "--"} - {biggest_loser.name if biggest_loser else "--"} ({format_pct(biggest_loser.change_pct if biggest_loser else None)})

## Sector snapshot

- **Best sector:** {best_sector["sector"] if best_sector else "--"} ({format_pct(best_sector["change_pct"]) if best_sector else "--"})
- **Worst sector:** {worst_sector["sector"] if worst_sector else "--"} ({format_pct(worst_sector["change_pct"]) if worst_sector else "--"})

## Technical context - S&P 500

| Metric | Value |
|---|---:|
| Current level | {format_number(spx.price if spx else None)} |
| 5-day average | {format_number(avg_5)} |
| 20-day average | {format_number(avg_20)} |
| 20-day support | {format_number(support)} |
| 20-day resistance | {format_number(resistance)} |
| Trend | {trend} |

## Earnings calendar - next 7 days

| Date | Symbol | EPS estimate |
|---|---|---:|
{chr(10).join(earnings_rows)}

## Market drivers / headlines

{chr(10).join(headline_rows)}

## Commentary

{commentary}

## Telegram summary

```text
{summary}
```
"""
    return markdown, summary


def send_telegram_message(bot_token: str, chat_id: str, text: str) -> dict[str, Any]:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
    return request_json(url, payload)


def send_telegram_document(
    bot_token: str, chat_id: str, document_path: Path, caption: str
) -> dict[str, Any]:
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    with document_path.open("rb") as document:
        response = requests.post(
            url,
            data={"chat_id": chat_id, "caption": caption},
            files={"document": (document_path.name, document, "text/markdown")},
            timeout=30,
        )
    response.raise_for_status()
    return response.json()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate/send daily market recap")
    parser.add_argument("--date", help="Recap date in YYYY-MM-DD format")
    parser.add_argument(
        "--out-dir", default=str(OUTPUTS), help="Output directory for markdown"
    )
    parser.add_argument(
        "--chat-id",
        default=os.environ.get("TELEGRAM_CHAT_ID")
        or os.environ.get("ALTAMIRA_TELEGRAM_CHAT_ID"),
        help="Telegram chat/channel id. Defaults to TELEGRAM_CHAT_ID.",
    )
    parser.add_argument(
        "--no-telegram", action="store_true", help="Generate the file only"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    recap_date = (
        datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else date.today()
    )
    api_key = os.environ.get("FMP_API_KEY")
    if not api_key:
        raise SystemExit("FMP_API_KEY is required.")

    quotes = fetch_quotes(api_key)
    gainers = fetch_simple_list(api_key, "biggest-gainers")
    losers = fetch_simple_list(api_key, "biggest-losers")
    sector_raw = fetch_sector_snapshot(api_key, recap_date)
    sectors = extract_sector_rows(sector_raw)
    earnings = fetch_earnings(api_key, recap_date)
    history = fetch_history(api_key, "^GSPC", recap_date)
    headlines = fetch_general_news(api_key)

    markdown, summary = build_report(
        recap_date, quotes, gainers, losers, sectors, earnings, history, headlines
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"daily-market-recap-{recap_date.isoformat()}.md"
    out_path.write_text(markdown, encoding="utf-8")

    print(summary)
    print(f"Report written: {out_path}")

    if args.no_telegram:
        print("Telegram delivery skipped (--no-telegram).")
        return

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is required for Telegram delivery.")
    if not args.chat_id:
        raise SystemExit("TELEGRAM_CHAT_ID or --chat-id is required.")

    message_result = send_telegram_message(bot_token, args.chat_id, summary)
    document_result = send_telegram_document(
        bot_token,
        args.chat_id,
        out_path,
        f"Daily Market Recap - {recap_date.isoformat()}",
    )
    if not message_result.get("ok") or not document_result.get("ok"):
        raise SystemExit(
            f"Telegram delivery failed: message={message_result}, "
            f"document={document_result}"
        )
    print("Telegram message sent.")
    print("Telegram markdown document sent.")


if __name__ == "__main__":
    main()
