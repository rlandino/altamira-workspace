#!/usr/bin/env python3
"""Generate a daily market recap and optionally send it to Telegram."""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


FMP_V3_BASE = "https://financialmodelingprep.com/api/v3"
FMP_STABLE_BASE = "https://financialmodelingprep.com/stable"
TELEGRAM_API_BASE = "https://api.telegram.org"
SECTOR_ETFS = {
    "XLC": "Communication Services",
    "XLY": "Consumer Discretionary",
    "XLP": "Consumer Staples",
    "XLE": "Energy",
    "XLF": "Financials",
    "XLV": "Health Care",
    "XLI": "Industrials",
    "XLB": "Materials",
    "XLRE": "Real Estate",
    "XLK": "Technology",
    "XLU": "Utilities",
}


class RecapError(RuntimeError):
    """Raised when the recap cannot be completed."""


@dataclass(frozen=True)
class Quote:
    """Normalized market quote data."""

    symbol: str
    name: str
    price: float | None
    change_percent: float | None


def http_json(url: str, *, timeout: int = 30) -> Any:
    """Fetch a JSON endpoint with a short timeout."""

    request = urllib.request.Request(url, headers={"User-Agent": "AltamiraDailyRecap/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise RecapError(f"Failed to fetch {url}: {exc}") from exc


def http_form(url: str, fields: dict[str, str], *, timeout: int = 30) -> Any:
    """POST form-encoded data and return JSON."""

    body = urllib.parse.urlencode(fields).encode("utf-8")
    request = urllib.request.Request(url, data=body)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise RecapError(f"Telegram request failed: {exc}") from exc


def http_multipart_document(
    url: str,
    fields: dict[str, str],
    file_path: Path,
    *,
    timeout: int = 60,
) -> Any:
    """POST a multipart/form-data document to Telegram."""

    boundary = "----AltamiraDailyRecapBoundary"
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode("utf-8"),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"),
                value.encode("utf-8"),
                b"\r\n",
            ]
        )
    chunks.extend(
        [
            f"--{boundary}\r\n".encode("utf-8"),
            (
                f'Content-Disposition: form-data; name="document"; '
                f'filename="{file_path.name}"\r\n'
            ).encode("utf-8"),
            b"Content-Type: text/markdown\r\n\r\n",
            file_path.read_bytes(),
            b"\r\n",
            f"--{boundary}--\r\n".encode("utf-8"),
        ]
    )
    body = b"".join(chunks)
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise RecapError(f"Telegram document upload failed: {exc}") from exc


def fmp_url(base: str, path: str, api_key: str, params: dict[str, str] | None = None) -> str:
    """Build an FMP URL with the API key appended."""

    query = {"apikey": api_key}
    if params:
        query.update(params)
    return f"{base}{path}?{urllib.parse.urlencode(query)}"


def as_float(value: Any) -> float | None:
    """Convert FMP number-ish values to float."""

    if value is None or value == "":
        return None
    if isinstance(value, str):
        value = value.replace("%", "").strip()
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fmt_number(value: float | None, decimals: int = 2) -> str:
    """Format optional numeric values."""

    if value is None:
        return "N/A"
    return f"{value:,.{decimals}f}"


def fmt_percent(value: float | None, signed: bool = True) -> str:
    """Format optional percent values."""

    if value is None:
        return "N/A"
    prefix = "+" if signed and value > 0 else ""
    return f"{prefix}{value:.2f}%"


def normalized_quote(raw: dict[str, Any], fallback_name: str) -> Quote:
    """Normalize one FMP quote item."""

    return Quote(
        symbol=str(raw.get("symbol", "")),
        name=str(raw.get("name") or fallback_name),
        price=as_float(raw.get("price")),
        change_percent=as_float(raw.get("changesPercentage") or raw.get("changePercentage")),
    )


def fetch_quotes(api_key: str) -> dict[str, Quote]:
    """Fetch headline index and ETF quotes."""

    symbols = "^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ"
    raw_quotes = http_json(fmp_url(FMP_V3_BASE, f"/quote/{symbols}", api_key))
    names = {
        "^GSPC": "S&P 500",
        "^DJI": "Dow Jones",
        "^IXIC": "Nasdaq Composite",
        "^VIX": "VIX",
        "SPY": "SPY",
        "QQQ": "QQQ",
    }
    return {
        item.get("symbol", ""): normalized_quote(item, names.get(item.get("symbol", ""), ""))
        for item in raw_quotes
        if isinstance(item, dict)
    }


def fetch_movers(api_key: str, endpoint: str) -> dict[str, Any] | None:
    """Fetch top gainer or loser from FMP stable endpoints."""

    raw = http_json(fmp_url(FMP_STABLE_BASE, endpoint, api_key))
    if isinstance(raw, list) and raw:
        return raw[0]
    return None


def fetch_sectors(api_key: str, recap_date: date) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Fetch sector snapshot and return best/worst sectors."""

    for offset in range(0, 6):
        check_date = recap_date - timedelta(days=offset)
        raw = http_json(
            fmp_url(
                FMP_STABLE_BASE,
                "/sector-performance-snapshot",
                api_key,
                {"date": check_date.isoformat()},
            )
        )
        sectors = raw if isinstance(raw, list) else raw.get("sectorPerformance", []) if isinstance(raw, dict) else []
        parsed = [
            sector
            for sector in sectors
            if isinstance(sector, dict)
            and as_float(
                sector.get("changesPercentage")
                or sector.get("changePercentage")
                or sector.get("performance")
            )
            is not None
        ]
        if parsed:
            key = lambda item: as_float(
                item.get("changesPercentage") or item.get("changePercentage") or item.get("performance")
            ) or 0.0
            return max(parsed, key=key), min(parsed, key=key)

    # Fallback: use liquid sector SPDR ETFs when the sector snapshot endpoint is empty.
    raw_etfs = http_json(fmp_url(FMP_V3_BASE, f"/quote/{','.join(SECTOR_ETFS)}", api_key))
    parsed_etfs = []
    if isinstance(raw_etfs, list):
        for item in raw_etfs:
            if not isinstance(item, dict):
                continue
            symbol = str(item.get("symbol", ""))
            change = as_float(item.get("changesPercentage") or item.get("changePercentage"))
            if symbol in SECTOR_ETFS and change is not None:
                parsed_etfs.append(
                    {
                        "sector": f"{SECTOR_ETFS[symbol]} ({symbol})",
                        "changesPercentage": change,
                    }
                )
    if parsed_etfs:
        key = lambda item: as_float(item.get("changesPercentage")) or 0.0
        return max(parsed_etfs, key=key), min(parsed_etfs, key=key)
    return None, None


def fetch_earnings(api_key: str, recap_date: date) -> list[dict[str, Any]]:
    """Fetch earnings calendar for the next seven calendar days."""

    to_date = recap_date + timedelta(days=7)
    raw = http_json(
        fmp_url(
            FMP_V3_BASE,
            "/earning_calendar",
            api_key,
            {"from": recap_date.isoformat(), "to": to_date.isoformat()},
        )
    )
    return raw[:20] if isinstance(raw, list) else []


def fetch_sp500_history(api_key: str, recap_date: date) -> list[dict[str, Any]]:
    """Fetch recent S&P 500 closes for trend and support/resistance."""

    from_date = recap_date - timedelta(days=45)
    raw = http_json(
        fmp_url(
            FMP_STABLE_BASE,
            "/historical-price-eod/light",
            api_key,
            {
                "symbol": "^GSPC",
                "from": from_date.isoformat(),
                "to": recap_date.isoformat(),
            },
        )
    )
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict) and isinstance(raw.get("historical"), list):
        return raw["historical"]
    return []


def average(values: list[float]) -> float | None:
    """Return an average for a non-empty list."""

    if not values:
        return None
    return sum(values) / len(values)


def trend_metrics(history: list[dict[str, Any]], current: float | None) -> dict[str, float | str | None]:
    """Calculate moving averages, support/resistance, and trend label."""

    rows = sorted(
        [row for row in history if as_float(row.get("close") or row.get("price")) is not None],
        key=lambda row: str(row.get("date", "")),
    )
    closes = [as_float(row.get("close") or row.get("price")) for row in rows]
    close_values = [value for value in closes if value is not None]
    last_20 = close_values[-20:]
    five_day = average(close_values[-5:])
    twenty_day = average(last_20)
    support = min(last_20) if last_20 else None
    resistance = max(last_20) if last_20 else None
    if current is None or five_day is None or twenty_day is None:
        trend = "N/A"
    elif current > five_day and current > twenty_day:
        trend = "Bullish"
    elif current < five_day and current < twenty_day:
        trend = "Bearish"
    else:
        trend = "Mixed"
    return {
        "five_day": five_day,
        "twenty_day": twenty_day,
        "support": support,
        "resistance": resistance,
        "trend": trend,
    }


def sector_name(sector: dict[str, Any] | None) -> str:
    """Extract a sector name from FMP sector rows."""

    if not sector:
        return "N/A"
    return str(sector.get("sector") or sector.get("name") or "N/A")


def sector_change(sector: dict[str, Any] | None) -> float | None:
    """Extract a sector change percentage from FMP sector rows."""

    if not sector:
        return None
    return as_float(sector.get("changesPercentage") or sector.get("changePercentage") or sector.get("performance"))


def vix_label(vix: float | None) -> str:
    """Classify VIX level for a concise recap."""

    if vix is None:
        return "N/A"
    if vix < 15:
        return "low"
    if vix > 20:
        return "elevated"
    return "normal"


def mover_symbol(mover: dict[str, Any] | None) -> str:
    """Extract a symbol from a mover row."""

    if not mover:
        return "N/A"
    return str(mover.get("symbol") or mover.get("ticker") or "N/A")


def mover_change(mover: dict[str, Any] | None) -> float | None:
    """Extract a change percentage from a mover row."""

    if not mover:
        return None
    return as_float(mover.get("changesPercentage") or mover.get("changePercentage") or mover.get("changes"))


def build_recap(api_key: str, recap_date: date) -> tuple[str, str]:
    """Build the markdown report and Telegram summary."""

    quotes = fetch_quotes(api_key)
    hot_stock = fetch_movers(api_key, "/biggest-gainers")
    biggest_loser = fetch_movers(api_key, "/biggest-losers")
    best_sector, worst_sector = fetch_sectors(api_key, recap_date)
    earnings = fetch_earnings(api_key, recap_date)
    metrics = trend_metrics(fetch_sp500_history(api_key, recap_date), quotes.get("^GSPC", Quote("", "", None, None)).price)

    spx = quotes.get("^GSPC", Quote("^GSPC", "S&P 500", None, None))
    dow = quotes.get("^DJI", Quote("^DJI", "Dow Jones", None, None))
    nasdaq = quotes.get("^IXIC", Quote("^IXIC", "Nasdaq Composite", None, None))
    vix = quotes.get("^VIX", Quote("^VIX", "VIX", None, None))
    spy = quotes.get("SPY", Quote("SPY", "SPY", None, None))
    qqq = quotes.get("QQQ", Quote("QQQ", "QQQ", None, None))

    earnings_rows = []
    for item in earnings[:10]:
        earnings_rows.append(
            "| {date} | {symbol} | {eps} | {revenue} |".format(
                date=item.get("date", "N/A"),
                symbol=item.get("symbol", "N/A"),
                eps=fmt_number(as_float(item.get("epsEstimated"))),
                revenue=fmt_number(as_float(item.get("revenueEstimated")), 0),
            )
        )
    earnings_table = "\n".join(earnings_rows) if earnings_rows else "| N/A | No earnings found | N/A | N/A |"

    commentary = (
        f"The S&P 500 is {fmt_percent(spx.change_percent).lower()} with a {metrics['trend']} short-term trend. "
        f"VIX is {vix_label(vix.price)} at {fmt_number(vix.price)}. "
        f"Sector leadership is led by {sector_name(best_sector)} while {sector_name(worst_sector)} is lagging."
    )
    summary = (
        f"Daily market recap for {recap_date.isoformat()}: S&P 500 {fmt_percent(spx.change_percent)}, "
        f"Nasdaq {fmt_percent(nasdaq.change_percent)}, Dow {fmt_percent(dow.change_percent)}; "
        f"trend {metrics['trend']}, VIX {fmt_number(vix.price)} ({vix_label(vix.price)}). "
        f"Best sector: {sector_name(best_sector)} {fmt_percent(sector_change(best_sector))}; "
        f"worst sector: {sector_name(worst_sector)} {fmt_percent(sector_change(worst_sector))}. "
        f"Hot stock: {mover_symbol(hot_stock)} {fmt_percent(mover_change(hot_stock))}; "
        f"biggest loser: {mover_symbol(biggest_loser)} {fmt_percent(mover_change(biggest_loser))}."
    )

    markdown = f"""# Daily Market Recap - {recap_date.isoformat()}

> Informational market recap only. This is not investment advice.

## Executive Summary

{summary}

## Market Indices

| Index | Level | Day Change |
| --- | ---: | ---: |
| S&P 500 | {fmt_number(spx.price)} | {fmt_percent(spx.change_percent)} |
| Nasdaq Composite | {fmt_number(nasdaq.price)} | {fmt_percent(nasdaq.change_percent)} |
| Dow Jones | {fmt_number(dow.price)} | {fmt_percent(dow.change_percent)} |

## ETFs and Volatility

| Instrument | Level | Day Change |
| --- | ---: | ---: |
| SPY | {fmt_number(spy.price)} | {fmt_percent(spy.change_percent)} |
| QQQ | {fmt_number(qqq.price)} | {fmt_percent(qqq.change_percent)} |
| VIX | {fmt_number(vix.price)} | {fmt_percent(vix.change_percent)} |

VIX is **{vix_label(vix.price)}**.

## Movers

- **Hot stock:** {mover_symbol(hot_stock)} ({fmt_percent(mover_change(hot_stock))})
- **Biggest loser:** {mover_symbol(biggest_loser)} ({fmt_percent(mover_change(biggest_loser))})

## Sector Snapshot

- **Best sector:** {sector_name(best_sector)} ({fmt_percent(sector_change(best_sector))})
- **Worst sector:** {sector_name(worst_sector)} ({fmt_percent(sector_change(worst_sector))})

## Current Index Levels vs Averages

| Metric | Value |
| --- | ---: |
| S&P 500 current | {fmt_number(spx.price)} |
| 5-day average | {fmt_number(metrics['five_day'] if isinstance(metrics['five_day'], float) else None)} |
| 20-day average | {fmt_number(metrics['twenty_day'] if isinstance(metrics['twenty_day'], float) else None)} |
| Trend | {metrics['trend']} |

## Resistance / Support

- **Resistance:** {fmt_number(metrics['resistance'] if isinstance(metrics['resistance'], float) else None)}
- **Support:** {fmt_number(metrics['support'] if isinstance(metrics['support'], float) else None)}

These levels are derived from the recent 20-trading-day S&P 500 range.

## Earnings Calendar

Companies reporting from {recap_date.isoformat()} through {(recap_date + timedelta(days=7)).isoformat()}:

| Date | Symbol | EPS Estimate | Revenue Estimate |
| --- | --- | ---: | ---: |
{earnings_table}

## Commentary

{commentary}

## Telegram Summary

{summary}
"""
    return markdown, summary


def write_report(markdown: str, output_path: Path) -> None:
    """Write the markdown report to disk."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")


def send_telegram(summary: str, report_path: Path, bot_token: str, chat_id: str) -> None:
    """Send summary and markdown document to Telegram."""

    message_url = f"{TELEGRAM_API_BASE}/bot{bot_token}/sendMessage"
    message = f"Altamira Daily Market Recap\n\n{summary}"
    response = http_form(message_url, {"chat_id": chat_id, "text": message[:4096]})
    if not response.get("ok"):
        raise RecapError(f"Telegram summary send failed: {response}")

    document_url = f"{TELEGRAM_API_BASE}/bot{bot_token}/sendDocument"
    caption = f"Daily market recap markdown file: {report_path.name}"
    response = http_multipart_document(
        document_url,
        {"chat_id": chat_id, "caption": caption[:1024]},
        report_path,
    )
    if not response.get("ok"):
        raise RecapError(f"Telegram document upload failed: {response}")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description="Generate and send the daily market recap.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Recap date in YYYY-MM-DD format.")
    parser.add_argument("--out", default=None, help="Markdown output path.")
    parser.add_argument("--send-telegram", action="store_true", help="Send summary and report file to Telegram.")
    parser.add_argument("--chat-id", default=os.environ.get("TELEGRAM_CHAT_ID"), help="Telegram chat/channel ID.")
    parser.add_argument(
        "--fmp-api-key",
        default=os.environ.get("FMP_API_KEY"),
        help="FMP API key. Defaults to FMP_API_KEY.",
    )
    parser.add_argument(
        "--telegram-bot-token",
        default=os.environ.get("TELEGRAM_BOT_TOKEN"),
        help="Telegram bot token. Defaults to TELEGRAM_BOT_TOKEN.",
    )
    return parser.parse_args()


def main() -> int:
    """Generate the recap and optionally send it."""

    args = parse_args()
    if not args.fmp_api_key:
        raise RecapError("FMP API key is required via FMP_API_KEY or --fmp-api-key.")
    recap_date = datetime.strptime(args.date, "%Y-%m-%d").date()
    output_path = Path(args.out or f"outputs/daily-market-recap-{recap_date.isoformat()}.md")

    markdown, summary = build_recap(args.fmp_api_key, recap_date)
    write_report(markdown, output_path)

    telegram_status = "not requested"
    if args.send_telegram:
        if not args.telegram_bot_token:
            raise RecapError("TELEGRAM_BOT_TOKEN is required when --send-telegram is used.")
        if not args.chat_id:
            raise RecapError("Telegram chat ID is required via TELEGRAM_CHAT_ID or --chat-id.")
        send_telegram(summary, output_path, args.telegram_bot_token, args.chat_id)
        telegram_status = "sent"

    print(
        textwrap.dedent(
            f"""
            {summary}
            Report path: {output_path}
            Telegram: {telegram_status}
            """
        ).strip()
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RecapError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
