#!/usr/bin/env python3
"""Generate a daily market recap and optionally send it to Telegram."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS = WORKSPACE / "outputs"
FMP_V3 = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"
DEFAULT_FMP_KEY = "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz"
DEFAULT_TELEGRAM_CHAT_ID = "7830722515"


@dataclass(frozen=True)
class Quote:
    """Normalized market quote data."""

    symbol: str
    name: str
    price: float | None
    change_percent: float | None


def fetch_json(url: str, params: dict[str, Any] | None = None, timeout: int = 20) -> Any:
    """Fetch JSON from an HTTP endpoint with compact error reporting."""

    query = f"?{urlencode(params)}" if params else ""
    request = Request(f"{url}{query}", headers={"User-Agent": "altamira-daily-market-recap/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code} from {url}") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"Request failed for {url}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON from {url}") from exc


def as_float(value: Any) -> float | None:
    """Convert FMP numeric/string fields into floats."""

    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace("%", "").replace(",", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def fmt_number(value: float | None, decimals: int = 2) -> str:
    """Format an optional number for reports."""

    if value is None:
        return "N/A"
    return f"{value:,.{decimals}f}"


def fmt_percent(value: float | None, signed: bool = True) -> str:
    """Format an optional percentage."""

    if value is None:
        return "N/A"
    sign = "+" if signed and value > 0 else ""
    return f"{sign}{value:.2f}%"


def vix_label(value: float | None) -> str:
    """Classify the VIX level."""

    if value is None:
        return "unknown"
    if value < 15:
        return "low"
    if value <= 20:
        return "normal"
    if value <= 30:
        return "elevated"
    return "stressed"


def trend_label(price: float | None, avg_5d: float | None, avg_20d: float | None) -> str:
    """Classify trend from price versus 5-day and 20-day averages."""

    if price is None or avg_5d is None or avg_20d is None:
        return "Unknown"
    if price > avg_5d and price > avg_20d:
        return "Bullish"
    if price < avg_5d and price < avg_20d:
        return "Bearish"
    return "Mixed"


def normalize_quote(row: dict[str, Any]) -> Quote:
    """Normalize one FMP quote row."""

    change = (
        row.get("changesPercentage")
        if row.get("changesPercentage") is not None
        else row.get("changePercentage")
    )
    return Quote(
        symbol=str(row.get("symbol", "")),
        name=str(row.get("name") or row.get("symbol") or ""),
        price=as_float(row.get("price")),
        change_percent=as_float(change),
    )


def quote_map(api_key: str) -> dict[str, Quote]:
    """Fetch index and ETF quotes."""

    symbols = "^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ"
    data = fetch_json(f"{FMP_V3}/quote/{symbols}", {"apikey": api_key})
    rows = data if isinstance(data, list) else []
    return {quote.symbol: quote for quote in (normalize_quote(row) for row in rows)}


def first_market_mover(endpoint: str, api_key: str) -> Quote | None:
    """Fetch the first row from a FMP market mover endpoint."""

    data = fetch_json(f"{FMP_STABLE}/{endpoint}", {"apikey": api_key})
    if isinstance(data, list) and data:
        return normalize_quote(data[0])
    return None


def sector_snapshot(api_key: str, run_date: date) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Fetch best and worst sector from FMP sector snapshot."""

    rows: list[dict[str, Any]] = []
    for offset in range(0, 5):
        snapshot_date = (run_date - timedelta(days=offset)).isoformat()
        data = fetch_json(
            f"{FMP_STABLE}/sector-performance-snapshot",
            {"date": snapshot_date, "apikey": api_key},
        )
        if isinstance(data, list) and data:
            rows = [row for row in data if isinstance(row, dict)]
            break
    if not rows:
        return None, None

    def performance(row: dict[str, Any]) -> float:
        return as_float(
            row.get("changesPercentage")
            or row.get("changePercentage")
            or row.get("performance")
            or row.get("1D")
        ) or 0.0

    return max(rows, key=performance), min(rows, key=performance)


def sector_name(row: dict[str, Any] | None) -> str:
    """Extract a sector name from a sector row."""

    if not row:
        return "N/A"
    return str(row.get("sector") or row.get("sectorName") or row.get("name") or "N/A")


def sector_performance(row: dict[str, Any] | None) -> float | None:
    """Extract sector performance from a sector row."""

    if not row:
        return None
    return as_float(
        row.get("changesPercentage")
        or row.get("changePercentage")
        or row.get("performance")
        or row.get("1D")
    )


def historical_closes(api_key: str, symbol: str, run_date: date) -> list[dict[str, Any]]:
    """Fetch recent historical closes."""

    data = fetch_json(
        f"{FMP_STABLE}/historical-price-eod/light",
        {
            "symbol": symbol,
            "from": (run_date - timedelta(days=45)).isoformat(),
            "to": run_date.isoformat(),
            "apikey": api_key,
        },
    )
    if not isinstance(data, list):
        return []
    rows = [row for row in data if isinstance(row, dict) and as_float(row.get("close")) is not None]
    return sorted(rows, key=lambda row: str(row.get("date", "")))


def average(values: list[float]) -> float | None:
    """Return a mean for non-empty numeric lists."""

    return sum(values) / len(values) if values else None


def earnings_calendar(api_key: str, run_date: date) -> list[dict[str, Any]]:
    """Fetch earnings calendar rows for the next week."""

    data = fetch_json(
        f"{FMP_V3}/earning_calendar",
        {
            "from": run_date.isoformat(),
            "to": (run_date + timedelta(days=7)).isoformat(),
            "apikey": api_key,
        },
    )
    if not isinstance(data, list):
        return []
    rows = [row for row in data if isinstance(row, dict)]
    return sorted(rows, key=lambda row: (str(row.get("date", "")), str(row.get("symbol", ""))))[:20]


def market_news(api_key: str) -> list[dict[str, Any]]:
    """Fetch broad market headlines for context."""

    data = fetch_json(
        f"{FMP_STABLE}/news/general-latest",
        {"page": 0, "limit": 8, "apikey": api_key},
    )
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict)][:8]


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    """Build a simple markdown table."""

    output = ["| " + " | ".join(headers) + " |"]
    output.append("| " + " | ".join(["---"] * len(headers)) + " |")
    output.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(output)


def build_report(
    run_date: date,
    generated_at_et: datetime,
    quotes: dict[str, Quote],
    hot_stock: Quote | None,
    biggest_loser: Quote | None,
    best_sector: dict[str, Any] | None,
    worst_sector: dict[str, Any] | None,
    closes: list[dict[str, Any]],
    earnings: list[dict[str, Any]],
    headlines: list[dict[str, Any]],
) -> tuple[str, str]:
    """Build markdown report and Telegram-ready summary."""

    spx = quotes.get("^GSPC")
    dow = quotes.get("^DJI")
    nasdaq = quotes.get("^IXIC")
    vix = quotes.get("^VIX")
    spy = quotes.get("SPY")
    qqq = quotes.get("QQQ")

    close_values = [as_float(row.get("close")) for row in closes]
    close_values = [value for value in close_values if value is not None]
    avg_5d = average(close_values[-5:])
    avg_20d = average(close_values[-20:])
    support = min(close_values[-20:]) if len(close_values) >= 20 else (min(close_values) if close_values else None)
    resistance = max(close_values[-20:]) if len(close_values) >= 20 else (max(close_values) if close_values else None)
    trend = trend_label(spx.price if spx else None, avg_5d, avg_20d)
    vix_context = vix_label(vix.price if vix else None)

    index_rows = [
        ["S&P 500", fmt_number(spx.price if spx else None), fmt_percent(spx.change_percent if spx else None)],
        ["Nasdaq Composite", fmt_number(nasdaq.price if nasdaq else None), fmt_percent(nasdaq.change_percent if nasdaq else None)],
        ["Dow Jones", fmt_number(dow.price if dow else None), fmt_percent(dow.change_percent if dow else None)],
    ]

    earnings_rows = [
        [
            str(row.get("date", "N/A")),
            str(row.get("symbol", "N/A")),
            fmt_number(as_float(row.get("epsEstimated"))),
            fmt_number(as_float(row.get("revenueEstimated")), 0),
        ]
        for row in earnings[:10]
    ]
    if not earnings_rows:
        earnings_rows = [["N/A", "No earnings returned for the next 7 days", "N/A", "N/A"]]

    headline_rows = [
        [
            str(row.get("publishedDate") or row.get("date") or "")[:10],
            str(row.get("title") or row.get("headline") or "N/A").replace("|", "-"),
        ]
        for row in headlines[:5]
    ]
    if not headline_rows:
        headline_rows = [["N/A", "No broad market headlines returned by FMP."]]

    best_sector_name = sector_name(best_sector)
    worst_sector_name = sector_name(worst_sector)
    best_sector_pct = sector_performance(best_sector)
    worst_sector_pct = sector_performance(worst_sector)
    hot_label = f"{hot_stock.symbol} ({fmt_percent(hot_stock.change_percent)})" if hot_stock else "N/A"
    loser_label = f"{biggest_loser.symbol} ({fmt_percent(biggest_loser.change_percent)})" if biggest_loser else "N/A"

    direction = "mixed"
    if spx and nasdaq and dow:
        positives = sum((quote.change_percent or 0) > 0 for quote in (spx, nasdaq, dow))
        negatives = sum((quote.change_percent or 0) < 0 for quote in (spx, nasdaq, dow))
        if positives >= 2:
            direction = "higher"
        elif negatives >= 2:
            direction = "lower"

    summary = (
        f"Daily Market Recap - {run_date.isoformat()}\n"
        f"S&P 500 {fmt_percent(spx.change_percent if spx else None)}, "
        f"Nasdaq {fmt_percent(nasdaq.change_percent if nasdaq else None)}, "
        f"Dow {fmt_percent(dow.change_percent if dow else None)}. "
        f"Trend: {trend}; VIX {fmt_number(vix.price if vix else None)} ({vix_context}).\n"
        f"Best sector: {best_sector_name} {fmt_percent(best_sector_pct)}. "
        f"Worst sector: {worst_sector_name} {fmt_percent(worst_sector_pct)}. "
        f"Hot stock: {hot_label}; biggest loser: {loser_label}.\n"
        f"Generated {generated_at_et.strftime('%Y-%m-%d %I:%M %p ET')}."
    )

    commentary = (
        f"Markets are {direction} as of this recap, with the S&P 500 trend reading {trend}. "
        f"Volatility is {vix_context} with VIX at {fmt_number(vix.price if vix else None)}. "
        f"Sector leadership is led by {best_sector_name}, while {worst_sector_name} is lagging."
    )

    report = f"""# Daily Market Recap - {run_date.isoformat()}

Generated: {generated_at_et.strftime('%Y-%m-%d %I:%M %p ET')}

## Executive Summary

{summary}

## Market Indices

{markdown_table(["Index", "Level", "Day Change"], index_rows)}

## ETFs and Volatility

- SPY: {fmt_number(spy.price if spy else None)} ({fmt_percent(spy.change_percent if spy else None)})
- QQQ: {fmt_number(qqq.price if qqq else None)} ({fmt_percent(qqq.change_percent if qqq else None)})
- VIX: {fmt_number(vix.price if vix else None)} ({vix_context})

## Market Movers

- Hot stock: {hot_label}
- Biggest loser: {loser_label}
- Best sector: {best_sector_name} ({fmt_percent(best_sector_pct)})
- Worst sector: {worst_sector_name} ({fmt_percent(worst_sector_pct)})

## S&P 500 Technical Snapshot

- 5-day average: {fmt_number(avg_5d)}
- 20-day average: {fmt_number(avg_20d)}
- Resistance: {fmt_number(resistance)}
- Support: {fmt_number(support)}
- Trend: {trend}

## Market Drivers and Headlines

{markdown_table(["Date", "Headline"], headline_rows)}

## Earnings Calendar - Next 7 Days

{markdown_table(["Date", "Ticker", "EPS Est.", "Revenue Est."], earnings_rows)}

## Commentary

{commentary}

## Disclaimer

This recap is for informational and research purposes only and is not investment advice. Market data may be delayed or revised.
"""
    return report, summary


def send_telegram_message(token: str, chat_id: str, text: str) -> None:
    """Send a plain-text Telegram message."""

    payload = urlencode({"chat_id": chat_id, "text": text}).encode("utf-8")
    request = Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
    if not result.get("ok"):
        raise RuntimeError(f"Telegram sendMessage failed: {result}")


def send_telegram_document(token: str, chat_id: str, file_path: Path, caption: str) -> None:
    """Send a markdown file as a Telegram document."""

    boundary = "----AltamiraDailyMarketRecapBoundary"
    file_bytes = file_path.read_bytes()
    parts = [
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"chat_id\"\r\n\r\n{chat_id}\r\n".encode(),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"caption\"\r\n\r\n{caption}\r\n".encode(),
        (
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"document\"; filename=\"{file_path.name}\"\r\n"
            "Content-Type: text/markdown\r\n\r\n"
        ).encode(),
        file_bytes,
        f"\r\n--{boundary}--\r\n".encode(),
    ]
    request = Request(
        f"https://api.telegram.org/bot{token}/sendDocument",
        data=b"".join(parts),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urlopen(request, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))
    if not result.get("ok"):
        raise RuntimeError(f"Telegram sendDocument failed: {result}")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description="Generate and send Altamira daily market recap")
    parser.add_argument("--date", help="Recap date in YYYY-MM-DD format. Defaults to today in ET.")
    parser.add_argument("--send-telegram", action="store_true", help="Send summary and markdown file to Telegram.")
    parser.add_argument("--telegram-chat-id", default=os.environ.get("TELEGRAM_CHAT_ID") or DEFAULT_TELEGRAM_CHAT_ID)
    parser.add_argument("--out-dir", default=str(OUTPUTS), help="Output directory for markdown report.")
    return parser.parse_args()


def main() -> int:
    """Run the recap workflow."""

    args = parse_args()
    api_key = os.environ.get("FMP_API_KEY") or DEFAULT_FMP_KEY
    generated_at_et = datetime.now(ZoneInfo("America/New_York"))
    run_date = date.fromisoformat(args.date) if args.date else generated_at_et.date()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"daily-market-recap-{run_date.isoformat()}.md"

    try:
        quotes = quote_map(api_key)
        hot_stock = first_market_mover("biggest-gainers", api_key)
        biggest_loser = first_market_mover("biggest-losers", api_key)
        best_sector, worst_sector = sector_snapshot(api_key, run_date)
        closes = historical_closes(api_key, "^GSPC", run_date)
        earnings = earnings_calendar(api_key, run_date)
        headlines = market_news(api_key)
        report, summary = build_report(
            run_date,
            generated_at_et,
            quotes,
            hot_stock,
            biggest_loser,
            best_sector,
            worst_sector,
            closes,
            earnings,
            headlines,
        )
        report_path.write_text(report, encoding="utf-8")
        print(summary)
        print(f"Report: {report_path}")

        if args.send_telegram:
            token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
            if not token:
                raise RuntimeError("TELEGRAM_BOT_TOKEN or TELEGRAM_TOKEN must be set to send Telegram alerts.")
            if not args.telegram_chat_id:
                raise RuntimeError("Telegram chat ID is required. Set TELEGRAM_CHAT_ID or pass --telegram-chat-id.")
            send_telegram_message(token, args.telegram_chat_id, summary)
            send_telegram_document(token, args.telegram_chat_id, report_path, f"Daily market recap {run_date.isoformat()}")
            print("Telegram: summary and markdown file sent.")
    except Exception as exc:
        print(f"daily_market_recap failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
