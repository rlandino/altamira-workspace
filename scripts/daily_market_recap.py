#!/usr/bin/env python3
"""Generate a daily market recap and optionally deliver it to Telegram."""

from __future__ import annotations

import argparse
import html
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python 3.8 fallback only.
    ZoneInfo = None  # type: ignore


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS = WORKSPACE / "outputs"
FMP_V3 = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"
FMP_API_KEY = os.environ.get("FMP_API_KEY", "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz")
DEFAULT_QUOTE_SYMBOLS = "^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ"
WATCHLIST = ("AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "JPM", "V", "UNH")


@dataclass
class RecapResult:
    """Paths and summary text from a recap run."""

    date: str
    report_path: Path
    summary: str
    telegram_message_id: Optional[int] = None
    telegram_document_id: Optional[str] = None


class MarketRecapError(RuntimeError):
    """Raised when the recap cannot be generated or delivered."""


def today_et() -> str:
    """Return today's date in America/New_York."""
    if ZoneInfo is None:
        return datetime.now().strftime("%Y-%m-%d")
    return datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d")


def fmp_get(base_url: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """Fetch JSON from FMP with a shared API key."""
    query = dict(params or {})
    query["apikey"] = FMP_API_KEY
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    response = requests.get(url, params=query, timeout=25)
    response.raise_for_status()
    return response.json()


def safe_fmp_get(
    warnings: List[str],
    label: str,
    base_url: str,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
) -> Any:
    """Fetch FMP JSON and collect a warning instead of failing the run."""
    try:
        return fmp_get(base_url, endpoint, params)
    except Exception as exc:  # noqa: BLE001 - report generation should degrade gracefully.
        warnings.append(f"{label} unavailable: {exc}")
        return None


def parse_percent(value: Any) -> Optional[float]:
    """Parse an FMP percent-ish value into a numeric percentage."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = re.search(r"[-+]?\d+(?:\.\d+)?", value.replace(",", ""))
        if match:
            return float(match.group(0))
    return None


def parse_number(value: Any) -> Optional[float]:
    """Parse numeric input from FMP payloads."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace(",", "").replace("$", "").strip()
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def fmt_num(value: Optional[float], decimals: int = 2) -> str:
    """Format a number for reports."""
    if value is None:
        return "N/A"
    return f"{value:,.{decimals}f}"


def fmt_pct(value: Optional[float]) -> str:
    """Format a percentage for reports."""
    if value is None:
        return "N/A"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}%"


def normalize_quote(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a quote object across FMP response variants."""
    return {
        "symbol": raw.get("symbol"),
        "name": raw.get("name") or raw.get("companyName") or raw.get("symbol"),
        "price": parse_number(raw.get("price") or raw.get("last") or raw.get("close")),
        "change": parse_number(raw.get("change")),
        "change_pct": parse_percent(
            raw.get("changesPercentage")
            or raw.get("changePercentage")
            or raw.get("changesPercentage")
        ),
        "day_low": parse_number(raw.get("dayLow")),
        "day_high": parse_number(raw.get("dayHigh")),
        "year_low": parse_number(raw.get("yearLow")),
        "year_high": parse_number(raw.get("yearHigh")),
        "avg_50": parse_number(raw.get("priceAvg50")),
        "avg_200": parse_number(raw.get("priceAvg200")),
    }


def quote_map(raw_quotes: Any) -> Dict[str, Dict[str, Any]]:
    """Return quotes by symbol."""
    if not isinstance(raw_quotes, list):
        return {}
    return {
        str(item.get("symbol")): normalize_quote(item)
        for item in raw_quotes
        if isinstance(item, dict) and item.get("symbol")
    }


def first_market_mover(raw: Any) -> Optional[Dict[str, Any]]:
    """Normalize the first gainer/loser row."""
    if not isinstance(raw, list) or not raw:
        return None
    row = raw[0]
    if not isinstance(row, dict):
        return None
    return {
        "symbol": row.get("symbol") or row.get("ticker"),
        "name": row.get("name") or row.get("companyName") or row.get("symbol"),
        "price": parse_number(row.get("price")),
        "change_pct": parse_percent(
            row.get("changesPercentage")
            or row.get("changePercentage")
            or row.get("changes")
        ),
    }


def extract_sector_performance(raw: Any) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Extract best and worst sector rows from FMP stable sector payloads."""
    rows: List[Dict[str, Any]] = []

    if isinstance(raw, list):
        iterable: Iterable[Any] = raw
    elif isinstance(raw, dict):
        iterable = raw.get("sectorPerformance") or raw.get("data") or raw.values()
    else:
        iterable = []

    for item in iterable:
        if not isinstance(item, dict):
            continue
        name = (
            item.get("sector")
            or item.get("sectorName")
            or item.get("name")
            or item.get("label")
        )
        pct = parse_percent(
            item.get("changesPercentage")
            or item.get("changePercentage")
            or item.get("performance")
            or item.get("change")
        )
        if name and pct is not None:
            rows.append({"sector": str(name), "change_pct": pct})

    if not rows:
        return None, None
    sorted_rows = sorted(rows, key=lambda row: row["change_pct"], reverse=True)
    return sorted_rows[0], sorted_rows[-1]


def fetch_history(date_str: str, warnings: List[str]) -> List[Dict[str, Any]]:
    """Fetch recent S&P 500 historical closes for trend metrics."""
    end = datetime.strptime(date_str, "%Y-%m-%d")
    start = end - timedelta(days=45)
    raw = safe_fmp_get(
        warnings,
        "S&P 500 historical data",
        FMP_STABLE,
        "historical-price-eod/light",
        {"symbol": "^GSPC", "from": start.strftime("%Y-%m-%d"), "to": date_str},
    )
    rows = raw if isinstance(raw, list) else []
    clean_rows: List[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        close = parse_number(row.get("close") or row.get("adjClose") or row.get("price"))
        row_date = row.get("date")
        if close is not None and row_date:
            clean_rows.append({"date": str(row_date), "close": close})
    return sorted(clean_rows, key=lambda row: row["date"])


def moving_average(values: List[float], periods: int) -> Optional[float]:
    """Return a simple moving average for the last N values."""
    if len(values) < periods:
        return None
    return sum(values[-periods:]) / periods


def trend_metrics(spx: Dict[str, Any], history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute moving averages, support/resistance, and trend label."""
    current = spx.get("price")
    closes = [row["close"] for row in history if row.get("close") is not None]
    sma5 = moving_average(closes, 5)
    sma20 = moving_average(closes, 20)
    last20 = closes[-20:] if len(closes) >= 20 else closes
    support = min(last20) if last20 else spx.get("day_low") or spx.get("year_low")
    resistance = max(last20) if last20 else spx.get("day_high") or spx.get("year_high")

    if current is not None and sma5 is not None and sma20 is not None:
        if current > sma5 and current > sma20:
            trend = "Bullish"
        elif current < sma5 and current < sma20:
            trend = "Bearish"
        else:
            trend = "Mixed"
    elif current is not None and spx.get("avg_50") is not None and spx.get("avg_200") is not None:
        if current > spx["avg_50"] and current > spx["avg_200"]:
            trend = "Bullish"
        elif current < spx["avg_50"] and current < spx["avg_200"]:
            trend = "Bearish"
        else:
            trend = "Mixed"
    else:
        trend = "N/A"

    return {
        "sma5": sma5,
        "sma20": sma20,
        "support": support,
        "resistance": resistance,
        "trend": trend,
        "history_points": len(closes),
    }


def vix_label(vix_level: Optional[float]) -> str:
    """Return a plain-English VIX label."""
    if vix_level is None:
        return "N/A"
    if vix_level > 25:
        return "high"
    if vix_level > 20:
        return "elevated"
    if vix_level < 15:
        return "low"
    return "normal"


def top_earnings(raw: Any, limit: int = 12) -> List[Dict[str, Any]]:
    """Normalize earnings calendar rows."""
    if not isinstance(raw, list):
        return []
    results: List[Dict[str, Any]] = []
    for row in raw[:limit]:
        if not isinstance(row, dict):
            continue
        results.append(
            {
                "date": row.get("date") or row.get("fiscalDateEnding") or "N/A",
                "symbol": row.get("symbol") or "N/A",
                "eps": row.get("epsEstimated") or row.get("epsEstimate"),
                "revenue": row.get("revenueEstimated") or row.get("revenueEstimate"),
            }
        )
    return results


def top_headlines(raw: Any, limit: int = 5) -> List[Dict[str, str]]:
    """Normalize market headline rows."""
    if not isinstance(raw, list):
        return []
    headlines: List[Dict[str, str]] = []
    for row in raw[:limit]:
        if not isinstance(row, dict):
            continue
        title = row.get("title") or row.get("headline")
        site = row.get("site") or row.get("publisher") or row.get("source")
        url = row.get("url") or row.get("link")
        if title:
            headlines.append({"title": str(title), "source": str(site or "Source"), "url": str(url or "")})
    return headlines


def watchlist_moves(quotes: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return watchlist movers sorted by absolute daily change."""
    movers = []
    for symbol in WATCHLIST:
        quote = quotes.get(symbol)
        if not quote or quote.get("change_pct") is None:
            continue
        movers.append(quote)
    return sorted(movers, key=lambda quote: abs(quote.get("change_pct") or 0), reverse=True)


def make_markdown_table(headers: List[str], rows: List[List[str]]) -> str:
    """Build a simple markdown table."""
    if not rows:
        return "No data available.\n"
    header_line = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join(["---"] * len(headers)) + " |"
    row_lines = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header_line, separator, *row_lines]) + "\n"


def build_report(
    date_str: str,
    quotes: Dict[str, Dict[str, Any]],
    gainers: Optional[Dict[str, Any]],
    losers: Optional[Dict[str, Any]],
    best_sector: Optional[Dict[str, Any]],
    worst_sector: Optional[Dict[str, Any]],
    earnings: List[Dict[str, Any]],
    headlines: List[Dict[str, str]],
    metrics: Dict[str, Any],
    warnings: List[str],
) -> Tuple[str, str]:
    """Build markdown report and Telegram summary."""
    spx = quotes.get("^GSPC", {})
    dow = quotes.get("^DJI", {})
    nasdaq = quotes.get("^IXIC", {})
    vix = quotes.get("^VIX", {})
    spy = quotes.get("SPY", {})
    qqq = quotes.get("QQQ", {})
    movers = watchlist_moves(quotes)

    best_sector_label = (
        f"{best_sector['sector']} ({fmt_pct(best_sector['change_pct'])})"
        if best_sector
        else "N/A"
    )
    worst_sector_label = (
        f"{worst_sector['sector']} ({fmt_pct(worst_sector['change_pct'])})"
        if worst_sector
        else "N/A"
    )
    hot_stock_label = (
        f"{gainers['symbol']} ({fmt_pct(gainers['change_pct'])})"
        if gainers
        else "N/A"
    )
    loser_label = (
        f"{losers['symbol']} ({fmt_pct(losers['change_pct'])})"
        if losers
        else "N/A"
    )
    vix_context = vix_label(vix.get("price"))

    summary = (
        f"Daily Market Recap - {date_str}\n"
        f"S&P 500 {fmt_num(spx.get('price'))} ({fmt_pct(spx.get('change_pct'))}); "
        f"Nasdaq {fmt_num(nasdaq.get('price'))} ({fmt_pct(nasdaq.get('change_pct'))}); "
        f"Dow {fmt_num(dow.get('price'))} ({fmt_pct(dow.get('change_pct'))}).\n"
        f"Trend: {metrics['trend']}; VIX {fmt_num(vix.get('price'))} ({vix_context}).\n"
        f"Best/worst sector: {best_sector_label} / {worst_sector_label}. "
        f"Hot stock/loser: {hot_stock_label} / {loser_label}."
    )

    index_rows = [
        ["S&P 500", "^GSPC", fmt_num(spx.get("price")), fmt_pct(spx.get("change_pct"))],
        ["Nasdaq Composite", "^IXIC", fmt_num(nasdaq.get("price")), fmt_pct(nasdaq.get("change_pct"))],
        ["Dow Jones", "^DJI", fmt_num(dow.get("price")), fmt_pct(dow.get("change_pct"))],
    ]
    etf_rows = [
        ["SPY", fmt_num(spy.get("price")), fmt_pct(spy.get("change_pct"))],
        ["QQQ", fmt_num(qqq.get("price")), fmt_pct(qqq.get("change_pct"))],
        ["VIX", fmt_num(vix.get("price")), f"{fmt_pct(vix.get('change_pct'))} ({vix_context})"],
    ]
    earnings_rows = [
        [
            str(row["date"]),
            str(row["symbol"]),
            fmt_num(parse_number(row["eps"]), 2) if parse_number(row["eps"]) is not None else "N/A",
            fmt_num(parse_number(row["revenue"]), 0) if parse_number(row["revenue"]) is not None else "N/A",
        ]
        for row in earnings
    ]
    headline_rows = [
        [
            item["source"],
            f"[{item['title']}]({item['url']})" if item.get("url") else item["title"],
        ]
        for item in headlines
    ]
    watchlist_rows = [
        [quote["symbol"], fmt_num(quote.get("price")), fmt_pct(quote.get("change_pct"))]
        for quote in movers[:5]
    ]

    commentary = (
        f"The major index tape is {metrics['trend'].lower()} on the S&P 500 trend model, "
        f"with VIX in a {vix_context} regime at {fmt_num(vix.get('price'))}. "
        f"Leadership is concentrated in {best_sector_label}, while {worst_sector_label} is lagging. "
        "Use this as a market recap and risk-context input; it is not individualized investment advice."
    )

    markdown = f"""# Daily Market Recap - {date_str}

**Generated:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}  
**Source:** Financial Modeling Prep (quotes, sectors, gainers/losers, earnings, headlines)

> Financial market data can be delayed or revised. This recap is for informational purposes only and is not investment advice.

## Executive Summary

{summary}

## Market Indices

{make_markdown_table(["Index", "Symbol", "Level", "Change %"], index_rows)}

## ETFs and Volatility

{make_markdown_table(["Instrument", "Level", "Change / Context"], etf_rows)}

## Market Breadth and Movers

- **Best sector:** {best_sector_label}
- **Worst sector:** {worst_sector_label}
- **Hot stock:** {hot_stock_label}
- **Biggest loser:** {loser_label}

### Watchlist Movers

{make_markdown_table(["Ticker", "Level", "Change %"], watchlist_rows)}

## Technical Context

- **S&P 500 trend:** {metrics["trend"]}
- **5-day average:** {fmt_num(metrics.get("sma5"))}
- **20-day average:** {fmt_num(metrics.get("sma20"))}
- **Recent resistance:** {fmt_num(metrics.get("resistance"))}
- **Recent support:** {fmt_num(metrics.get("support"))}
- **Historical closes used:** {metrics.get("history_points", 0)}

## Market Drivers / Headlines

{make_markdown_table(["Source", "Headline"], headline_rows)}

## Earnings Calendar - Next 7 Days

{make_markdown_table(["Date", "Symbol", "EPS Est.", "Revenue Est."], earnings_rows)}

## Commentary

{commentary}
"""

    if warnings:
        markdown += "\n## Data Notes\n\n"
        markdown += "\n".join(f"- {warning}" for warning in warnings)
        markdown += "\n"

    return markdown, summary


def generate_recap(date_str: str) -> RecapResult:
    """Fetch data, write the markdown report, and return summary details."""
    warnings: List[str] = []
    OUTPUTS.mkdir(parents=True, exist_ok=True)

    quote_symbols = DEFAULT_QUOTE_SYMBOLS + "," + ",".join(WATCHLIST)
    raw_quotes = safe_fmp_get(
        warnings,
        "Quotes",
        FMP_V3,
        f"quote/{quote_symbols}",
    )
    quotes = quote_map(raw_quotes)

    gainers = first_market_mover(
        safe_fmp_get(warnings, "Biggest gainers", FMP_STABLE, "biggest-gainers")
    )
    losers = first_market_mover(
        safe_fmp_get(warnings, "Biggest losers", FMP_STABLE, "biggest-losers")
    )
    sector_raw = safe_fmp_get(
        warnings,
        "Sector performance",
        FMP_STABLE,
        "sector-performance-snapshot",
        {"date": date_str},
    )
    best_sector, worst_sector = extract_sector_performance(sector_raw)
    if best_sector is None and worst_sector is None:
        sector_raw = safe_fmp_get(
            warnings,
            "Sector performance fallback",
            FMP_STABLE,
            "sector-performance-snapshot",
        )
        best_sector, worst_sector = extract_sector_performance(sector_raw)

    end = datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=7)
    earnings_raw = safe_fmp_get(
        warnings,
        "Earnings calendar",
        FMP_V3,
        "earning_calendar",
        {"from": date_str, "to": end.strftime("%Y-%m-%d")},
    )
    headlines_raw = safe_fmp_get(
        warnings,
        "Market headlines",
        FMP_STABLE,
        "news/general-latest",
        {"page": 0, "limit": 10},
    )

    spx = quotes.get("^GSPC", {})
    if not spx.get("price"):
        raise MarketRecapError("S&P 500 quote was unavailable; cannot produce recap.")

    history = fetch_history(date_str, warnings)
    metrics = trend_metrics(spx, history)
    markdown, summary = build_report(
        date_str=date_str,
        quotes=quotes,
        gainers=gainers,
        losers=losers,
        best_sector=best_sector,
        worst_sector=worst_sector,
        earnings=top_earnings(earnings_raw),
        headlines=top_headlines(headlines_raw),
        metrics=metrics,
        warnings=warnings,
    )

    report_path = OUTPUTS / f"daily-market-recap-{date_str}.md"
    report_path.write_text(markdown, encoding="utf-8")
    return RecapResult(date=date_str, report_path=report_path, summary=summary)


def resolve_telegram_settings(chat_id_arg: Optional[str]) -> Tuple[str, str]:
    """Resolve Telegram bot token and chat id from CLI/env."""
    token = (
        os.environ.get("TELEGRAM_BOT_TOKEN")
        or os.environ.get("TELEGRAM_TOKEN")
        or os.environ.get("BOT_TOKEN")
    )
    chat_id = (
        chat_id_arg
        or os.environ.get("TELEGRAM_CHAT_ID")
        or os.environ.get("TELEGRAM_CHANNEL_ID")
    )
    if not token:
        raise MarketRecapError("TELEGRAM_BOT_TOKEN is not set.")
    if not chat_id:
        raise MarketRecapError("Telegram chat id is not set. Use --telegram-chat-id or TELEGRAM_CHAT_ID.")
    return token, chat_id


def send_telegram_message(token: str, chat_id: str, text: str) -> int:
    """Send a plain-text Telegram message and return the message id."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": "true",
        },
        timeout=25,
    )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        raise MarketRecapError(f"Telegram sendMessage failed: {payload}")
    return int(payload["result"]["message_id"])


def send_telegram_document(token: str, chat_id: str, path: Path, caption: str) -> str:
    """Send a markdown report file to Telegram and return the document file id."""
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    safe_caption = html.unescape(caption)
    if len(safe_caption) > 900:
        safe_caption = safe_caption[:897] + "..."
    with path.open("rb") as handle:
        response = requests.post(
            url,
            data={"chat_id": chat_id, "caption": safe_caption},
            files={"document": (path.name, handle, "text/markdown")},
            timeout=45,
        )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        raise MarketRecapError(f"Telegram sendDocument failed: {payload}")
    document = payload["result"].get("document") or {}
    return str(document.get("file_id") or "")


def deliver_to_telegram(result: RecapResult, chat_id_arg: Optional[str]) -> RecapResult:
    """Deliver the recap summary and markdown file to Telegram."""
    token, chat_id = resolve_telegram_settings(chat_id_arg)
    result.telegram_message_id = send_telegram_message(token, chat_id, result.summary)
    caption = f"Daily Market Recap markdown file - {result.date}"
    result.telegram_document_id = send_telegram_document(token, chat_id, result.report_path, caption)
    return result


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate and optionally send a daily market recap.")
    parser.add_argument("--date", default=today_et(), help="Recap date in YYYY-MM-DD format.")
    parser.add_argument("--send-telegram", action="store_true", help="Send summary and markdown file to Telegram.")
    parser.add_argument("--telegram-chat-id", default=None, help="Telegram chat/channel id override.")
    return parser.parse_args()


def main() -> None:
    """CLI entrypoint."""
    args = parse_args()
    result = generate_recap(args.date)
    if args.send_telegram:
        result = deliver_to_telegram(result, args.telegram_chat_id)

    print(result.summary)
    print(f"Report: {result.report_path}")
    if args.send_telegram:
        print(f"Telegram message id: {result.telegram_message_id}")
        print(f"Telegram document id: {result.telegram_document_id or 'N/A'}")


if __name__ == "__main__":
    main()
