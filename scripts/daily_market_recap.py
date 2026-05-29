#!/usr/bin/env python3
"""Generate and optionally send the Altamira daily market recap to Telegram."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = WORKSPACE / "outputs"
FMP_V3 = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"
DEFAULT_FMP_KEY = "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz"
DEFAULT_TELEGRAM_CHAT_ID = "7830722515"
INDEX_SYMBOLS = "^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ"


@dataclass
class MarketRecap:
    report_date: date
    output_path: Path
    summary: str
    markdown: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate and send the daily market recap.")
    parser.add_argument("--date", help="Report date in YYYY-MM-DD format. Defaults to today in ET.")
    parser.add_argument("--out-dir", default=str(OUTPUTS_DIR), help="Directory for the markdown output.")
    parser.add_argument("--send-telegram", action="store_true", help="Send summary and markdown file to Telegram.")
    parser.add_argument("--chat-id", default=None, help="Telegram chat/channel ID. Defaults to env or workspace fallback.")
    parser.add_argument("--bot-token", default=None, help="Telegram bot token. Defaults to TELEGRAM_BOT_TOKEN.")
    parser.add_argument("--fmp-key", default=None, help="FMP API key. Defaults to FMP_API_KEY or workspace fallback.")
    return parser.parse_args()


def report_date_from_arg(value: str | None) -> date:
    if value:
        return datetime.strptime(value, "%Y-%m-%d").date()
    return datetime.now(ZoneInfo("America/New_York")).date()


def request_json(url: str, params: dict[str, Any] | None = None) -> Any:
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    return response.json()


def fetch_fmp_v3(path: str, fmp_key: str, params: dict[str, Any] | None = None) -> Any:
    query = dict(params or {})
    query["apikey"] = fmp_key
    return request_json(f"{FMP_V3}/{path.lstrip('/')}", query)


def fetch_fmp_stable(path: str, fmp_key: str, params: dict[str, Any] | None = None) -> Any:
    query = dict(params or {})
    query["apikey"] = fmp_key
    return request_json(f"{FMP_STABLE}/{path.lstrip('/')}", query)


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace("%", "").replace(",", "").replace("+", "").strip()
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def fmt_number(value: Any, decimals: int = 2) -> str:
    parsed = as_float(value)
    if parsed is None:
        return "N/A"
    return f"{parsed:,.{decimals}f}"


def fmt_pct(value: Any) -> str:
    parsed = as_float(value)
    if parsed is None:
        return "N/A"
    return f"{parsed:+.2f}%"


def quote_map(quotes: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(quotes, list):
        return {}
    return {str(item.get("symbol")): item for item in quotes if isinstance(item, dict) and item.get("symbol")}


def quote_line(quotes: dict[str, dict[str, Any]], symbol: str, label: str) -> str:
    quote = quotes.get(symbol, {})
    return f"| {label} | {fmt_number(quote.get('price'))} | {fmt_pct(quote.get('changesPercentage'))} |"


def pick_first(items: Any) -> dict[str, Any]:
    if isinstance(items, list) and items and isinstance(items[0], dict):
        return items[0]
    return {}


def pct_field(item: dict[str, Any]) -> Any:
    for key in ("changesPercentage", "changePercentage", "changePercent", "changes", "performance"):
        if key in item:
            return item.get(key)
    return None


def parse_sector_snapshot(data: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(data, dict):
        for key in ("sectorPerformance", "sectors", "data"):
            if isinstance(data.get(key), list):
                rows = [row for row in data[key] if isinstance(row, dict)]
                break
        if not rows:
            rows = [value for value in data.values() if isinstance(value, dict)]
    elif isinstance(data, list):
        rows = [row for row in data if isinstance(row, dict)]

    scored = [(row, as_float(pct_field(row))) for row in rows]
    scored = [(row, value) for row, value in scored if value is not None]
    if not scored:
        return {}, {}
    return max(scored, key=lambda item: item[1])[0], min(scored, key=lambda item: item[1])[0]


def sector_name(item: dict[str, Any]) -> str:
    for key in ("sector", "sectorName", "name"):
        if item.get(key):
            return str(item[key])
    return "N/A"


def fetch_historical_closes(report_date: date, fmp_key: str) -> list[dict[str, Any]]:
    from_date = (report_date - timedelta(days=45)).isoformat()
    data = fetch_fmp_stable(
        "historical-price-eod/light",
        fmp_key,
        {"symbol": "^GSPC", "from": from_date, "to": report_date.isoformat()},
    )
    rows = data if isinstance(data, list) else []
    parsed: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        close = as_float(row.get("close") or row.get("adjClose") or row.get("price"))
        row_date = row.get("date")
        if close is not None and row_date:
            parsed.append({"date": row_date, "close": close})
    return sorted(parsed, key=lambda row: row["date"])


def moving_average(values: list[float], window: int) -> float | None:
    if len(values) < window:
        return None
    return sum(values[-window:]) / window


def trend_label(current: float | None, sma5: float | None, sma20: float | None) -> str:
    if current is None or sma5 is None or sma20 is None:
        return "N/A"
    if current > sma5 and current > sma20:
        return "Bullish"
    if current < sma5 and current < sma20:
        return "Bearish"
    return "Mixed"


def vix_label(value: Any) -> str:
    parsed = as_float(value)
    if parsed is None:
        return "N/A"
    if parsed > 20:
        return "Elevated"
    if parsed < 15:
        return "Low"
    return "Normal"


def safe_fetch(default: Any, fetcher, *args, **kwargs) -> Any:
    try:
        return fetcher(*args, **kwargs)
    except Exception as exc:  # noqa: BLE001 - report should survive one failed endpoint.
        print(f"[daily_market_recap] Fetch failed: {exc}", flush=True)
        return default


def build_recap(report_date: date, out_dir: Path, fmp_key: str) -> MarketRecap:
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / f"daily-market-recap-{report_date.isoformat()}.md"

    quotes = quote_map(safe_fetch([], fetch_fmp_v3, f"quote/{INDEX_SYMBOLS}", fmp_key))
    earnings = safe_fetch(
        [],
        fetch_fmp_v3,
        "earning_calendar",
        fmp_key,
        {"from": report_date.isoformat(), "to": (report_date + timedelta(days=7)).isoformat()},
    )
    gainers = safe_fetch([], fetch_fmp_stable, "biggest-gainers", fmp_key)
    losers = safe_fetch([], fetch_fmp_stable, "biggest-losers", fmp_key)
    sector_data = safe_fetch(
        [],
        fetch_fmp_stable,
        "sector-performance-snapshot",
        fmp_key,
        {"date": report_date.isoformat()},
    )
    news = safe_fetch([], fetch_fmp_stable, "news/general-latest", fmp_key, {"page": 0, "limit": 8})
    historical = safe_fetch([], fetch_historical_closes, report_date, fmp_key)

    top_gainer = pick_first(gainers)
    top_loser = pick_first(losers)
    best_sector, worst_sector = parse_sector_snapshot(sector_data)

    spx_quote = quotes.get("^GSPC", {})
    spx_current = as_float(spx_quote.get("price"))
    closes = [row["close"] for row in historical]
    sma5 = moving_average(closes, 5)
    sma20 = moving_average(closes, 20)
    support = min(closes[-20:]) if len(closes) >= 20 else None
    resistance = max(closes[-20:]) if len(closes) >= 20 else None
    trend = trend_label(spx_current, sma5, sma20)
    vix = quotes.get("^VIX", {})
    vix_context = vix_label(vix.get("price"))

    earnings_rows = earnings if isinstance(earnings, list) else []
    earnings_rows = [row for row in earnings_rows if isinstance(row, dict)][:12]
    news_rows = news if isinstance(news, list) else []
    news_rows = [row for row in news_rows if isinstance(row, dict)][:5]

    market_direction = "mixed"
    spx_change = as_float(spx_quote.get("changesPercentage"))
    nasdaq_change = as_float(quotes.get("^IXIC", {}).get("changesPercentage"))
    if spx_change is not None and nasdaq_change is not None:
        if spx_change > 0 and nasdaq_change > 0:
            market_direction = "higher"
        elif spx_change < 0 and nasdaq_change < 0:
            market_direction = "lower"

    summary = (
        f"Altamira Daily Market Recap - {report_date.isoformat()}\n"
        f"S&P 500 {fmt_pct(spx_quote.get('changesPercentage'))} at {fmt_number(spx_quote.get('price'))}; "
        f"Nasdaq {fmt_pct(quotes.get('^IXIC', {}).get('changesPercentage'))}; "
        f"Dow {fmt_pct(quotes.get('^DJI', {}).get('changesPercentage'))}. "
        f"Trend: {trend}. VIX: {fmt_number(vix.get('price'))} ({vix_context}).\n"
        f"Best sector: {sector_name(best_sector)} ({fmt_pct(pct_field(best_sector))}); "
        f"worst sector: {sector_name(worst_sector)} ({fmt_pct(pct_field(worst_sector))}). "
        f"Hot stock: {top_gainer.get('symbol', 'N/A')} ({fmt_pct(pct_field(top_gainer))}); "
        f"biggest loser: {top_loser.get('symbol', 'N/A')} ({fmt_pct(pct_field(top_loser))})."
    )

    earnings_table = "\n".join(
        f"| {row.get('date', 'N/A')} | {row.get('symbol', 'N/A')} | {fmt_number(row.get('epsEstimated'), 2)} |"
        for row in earnings_rows
    )
    if not earnings_table:
        earnings_table = "| N/A | No earnings returned for the next 7 days | N/A |"

    news_bullets = "\n".join(
        f"- {row.get('title') or row.get('headline') or 'Untitled headline'}"
        for row in news_rows
    )
    if not news_bullets:
        news_bullets = "- No headlines returned by the news endpoint."

    markdown = f"""# Daily Market Recap - {report_date.isoformat()}

_Generated for Altamira Capital. Market data from Financial Modeling Prep. This is not investment advice._

## Executive Summary

{summary}

## Market Indices

| Index / ETF | Level | Day Change |
|---|---:|---:|
{quote_line(quotes, "^GSPC", "S&P 500")}
{quote_line(quotes, "^IXIC", "Nasdaq Composite")}
{quote_line(quotes, "^DJI", "Dow Jones Industrial Average")}
{quote_line(quotes, "SPY", "SPY")}
{quote_line(quotes, "QQQ", "QQQ")}

## Volatility

- **VIX:** {fmt_number(vix.get('price'))} ({vix_context}), {fmt_pct(vix.get('changesPercentage'))} today.

## Movers and Sectors

| Category | Name / Symbol | Day Change |
|---|---:|---:|
| Hot stock | {top_gainer.get('symbol', 'N/A')} | {fmt_pct(pct_field(top_gainer))} |
| Biggest loser | {top_loser.get('symbol', 'N/A')} | {fmt_pct(pct_field(top_loser))} |
| Best sector | {sector_name(best_sector)} | {fmt_pct(pct_field(best_sector))} |
| Worst sector | {sector_name(worst_sector)} | {fmt_pct(pct_field(worst_sector))} |

## S&P 500 Technical Snapshot

| Metric | Value |
|---|---:|
| Current Level | {fmt_number(spx_current)} |
| 5-Day Average | {fmt_number(sma5)} |
| 20-Day Average | {fmt_number(sma20)} |
| 20-Day Support | {fmt_number(support)} |
| 20-Day Resistance | {fmt_number(resistance)} |
| Trend | {trend} |

## Why the Market Is Moving

Markets are trading {market_direction} based on the broad index snapshot. Current headline feed:

{news_bullets}

## Upcoming Earnings Calendar

| Date | Symbol | EPS Estimate |
|---|---:|---:|
{earnings_table}

## Commentary

The S&P 500 is {fmt_pct(spx_quote.get('changesPercentage'))} on the session, while the Nasdaq is {fmt_pct(quotes.get('^IXIC', {}).get('changesPercentage'))} and the Dow is {fmt_pct(quotes.get('^DJI', {}).get('changesPercentage'))}. The S&P 500 trend reads **{trend}** against its 5-day and 20-day averages, with recent support near {fmt_number(support)} and resistance near {fmt_number(resistance)}. Sector leadership is led by {sector_name(best_sector)}, while {sector_name(worst_sector)} is lagging.

## Files

- Markdown report: `{output_path.relative_to(WORKSPACE)}`
"""

    output_path.write_text(markdown, encoding="utf-8")
    return MarketRecap(report_date=report_date, output_path=output_path, summary=summary, markdown=markdown)


def telegram_chat_id(value: str | None) -> str:
    return (
        value
        or os.environ.get("TELEGRAM_CHAT_ID")
        or os.environ.get("ALTAMIRA_TELEGRAM_CHAT_ID")
        or DEFAULT_TELEGRAM_CHAT_ID
    )


def send_to_telegram(recap: MarketRecap, bot_token: str | None, chat_id: str) -> None:
    token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required to send the recap.")

    base_url = f"https://api.telegram.org/bot{token}"
    message_response = requests.post(
        f"{base_url}/sendMessage",
        data={"chat_id": chat_id, "text": recap.summary},
        timeout=20,
    )
    message_response.raise_for_status()

    with recap.output_path.open("rb") as handle:
        document_response = requests.post(
            f"{base_url}/sendDocument",
            data={
                "chat_id": chat_id,
                "caption": f"Daily market recap markdown - {recap.report_date.isoformat()}",
            },
            files={"document": (recap.output_path.name, handle, "text/markdown")},
            timeout=30,
        )
    document_response.raise_for_status()


def main() -> None:
    args = parse_args()
    fmp_key = args.fmp_key or os.environ.get("FMP_API_KEY") or DEFAULT_FMP_KEY
    report_date = report_date_from_arg(args.date)
    recap = build_recap(report_date, Path(args.out_dir), fmp_key)

    print(recap.summary)
    print(f"Report path: {recap.output_path}")

    if args.send_telegram:
        chat_id = telegram_chat_id(args.chat_id)
        send_to_telegram(recap, args.bot_token, chat_id)
        print(f"Sent Telegram summary and document to chat/channel {chat_id}.")


if __name__ == "__main__":
    main()
