#!/usr/bin/env python3
"""
Generate an Altamira daily market recap and optionally send it to Telegram.

Environment:
  FMP_API_KEY                     Financial Modeling Prep API key. If omitted,
                                  this script reuses the workspace local-dev
                                  fallback from scripts.market_data_api.
  TELEGRAM_BOT_TOKEN              Telegram bot token.
  TELEGRAM_CHAT_ID                Telegram chat/channel id.
  TELEGRAM_CHANNEL_ID             Alternate chat/channel id env name.
  TELEGRAM_CHANNEL_USERNAME       Alternate @channel username env name.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests

WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS = WORKSPACE / "outputs"
FMP_V3 = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"

# Existing CSP scan workflow has this chat id checked in as its Telegram target.
DEFAULT_TELEGRAM_CHAT_ID = "7830722515"

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


@dataclass
class ApiResult:
    data: Any
    error: str = ""


@dataclass
class RecapResult:
    report_path: Path
    summary: str
    telegram_message: str
    warnings: list[str]


def resolve_fmp_key() -> str:
    """Resolve FMP key from env, then workspace local-dev fallback."""
    for key_name in ("FMP_API_KEY", "ALTAMIRA_FMP_API_KEY"):
        key = os.environ.get(key_name)
        if key:
            return key

    try:
        from scripts.market_data_api import DEFAULT_KEY  # type: ignore

        return str(DEFAULT_KEY)
    except Exception:
        return ""


def api_get(base: str, path: str, params: dict[str, Any] | None, api_key: str) -> ApiResult:
    """Fetch JSON from FMP with consistent error capture."""
    if not api_key:
        return ApiResult(None, "FMP_API_KEY is not set")

    url = f"{base}{path}"
    query = dict(params or {})
    query["apikey"] = api_key
    try:
        response = requests.get(url, params=query, timeout=20)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict):
            message = data.get("Error Message") or data.get("error")
            if message:
                return ApiResult(data, str(message))
        return ApiResult(data)
    except requests.RequestException as exc:
        return ApiResult(None, str(exc))
    except ValueError as exc:
        return ApiResult(None, f"Invalid JSON response: {exc}")


def as_list(value: Any) -> list[dict[str, Any]]:
    """Normalize FMP list/dict responses into a list of dictionaries."""
    if isinstance(value, list):
        return [row for row in value if isinstance(row, dict)]
    if isinstance(value, dict):
        if isinstance(value.get("historical"), list):
            return [row for row in value["historical"] if isinstance(row, dict)]
        return [value]
    return []


def number(value: Any) -> float | None:
    """Coerce common FMP number formats into float."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    text = text.replace("%", "").replace(",", "").replace("+", "")
    text = text.replace("(", "").replace(")", "")
    try:
        return float(text)
    except ValueError:
        return None


def fmt_level(value: Any) -> str:
    val = number(value)
    if val is None:
        return "n/a"
    if abs(val) >= 1000:
        return f"{val:,.2f}"
    return f"{val:.2f}"


def fmt_pct(value: Any) -> str:
    val = number(value)
    if val is None:
        return "n/a"
    return f"{val:+.2f}%"


def get_field(row: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in row and row[name] not in (None, ""):
            return row[name]
    return None


def quote_change(row: dict[str, Any]) -> float | None:
    return number(get_field(row, "changesPercentage", "changePercentage", "changePercent"))


def fetch_quotes(api_key: str, warnings: list[str]) -> dict[str, dict[str, Any]]:
    symbols = "^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ"
    result = api_get(FMP_V3, f"/quote/{symbols}", None, api_key)
    if result.error:
        warnings.append(f"Quote fetch failed: {result.error}")
    return {
        str(row.get("symbol")): row
        for row in as_list(result.data)
        if row.get("symbol")
    }


def fetch_movers(api_key: str, warnings: list[str]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    gainers = api_get(FMP_STABLE, "/biggest-gainers", None, api_key)
    losers = api_get(FMP_STABLE, "/biggest-losers", None, api_key)
    if gainers.error:
        warnings.append(f"Biggest gainers fetch failed: {gainers.error}")
    if losers.error:
        warnings.append(f"Biggest losers fetch failed: {losers.error}")
    return (
        as_list(gainers.data)[0] if as_list(gainers.data) else None,
        as_list(losers.data)[0] if as_list(losers.data) else None,
    )


def normalize_sector_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        name = get_field(row, "sector", "sectorName", "name")
        change = get_field(row, "changesPercentage", "changePercentage", "performance", "1D Change")
        change_num = number(change)
        if name and change_num is not None:
            normalized.append({"name": str(name), "change": change_num})
    return normalized


def fetch_sectors(api_key: str, as_of: date, warnings: list[str]) -> tuple[dict[str, Any] | None, dict[str, Any] | None, str]:
    for days_back in range(0, 8):
        snapshot_date = as_of - timedelta(days=days_back)
        result = api_get(
            FMP_STABLE,
            "/sector-performance-snapshot",
            {"date": snapshot_date.isoformat()},
            api_key,
        )
        sectors = normalize_sector_rows(as_list(result.data))
        if sectors:
            sectors.sort(key=lambda row: row["change"], reverse=True)
            return sectors[0], sectors[-1], f"FMP sector snapshot ({snapshot_date.isoformat()})"
        if result.error and days_back == 0:
            warnings.append(f"Sector snapshot fetch failed: {result.error}")

    etf_symbols = ",".join(SECTOR_ETFS)
    result = api_get(FMP_V3, f"/quote/{etf_symbols}", None, api_key)
    etf_rows = []
    for row in as_list(result.data):
        symbol = str(row.get("symbol", "")).upper()
        change = quote_change(row)
        if symbol in SECTOR_ETFS and change is not None:
            etf_rows.append({"name": SECTOR_ETFS[symbol], "symbol": symbol, "change": change})
    if etf_rows:
        etf_rows.sort(key=lambda row: row["change"], reverse=True)
        return etf_rows[0], etf_rows[-1], "sector ETF proxy"
    if result.error:
        warnings.append(f"Sector ETF proxy fetch failed: {result.error}")
    return None, None, "unavailable"


def fetch_history(api_key: str, as_of: date, warnings: list[str]) -> list[dict[str, Any]]:
    from_date = (as_of - timedelta(days=45)).isoformat()
    result = api_get(
        FMP_STABLE,
        "/historical-price-eod/light",
        {"symbol": "^GSPC", "from": from_date, "to": as_of.isoformat()},
        api_key,
    )
    rows = as_list(result.data)
    if not rows:
        fallback = api_get(
            FMP_V3,
            "/historical-price-full/^GSPC",
            {"from": from_date, "to": as_of.isoformat()},
            api_key,
        )
        rows = as_list(fallback.data)
        if fallback.error:
            warnings.append(f"Historical fallback fetch failed: {fallback.error}")
    if result.error and not rows:
        warnings.append(f"Historical fetch failed: {result.error}")

    parsed = []
    for row in rows:
        close = number(get_field(row, "close", "adjClose", "price"))
        row_date = row.get("date")
        if row_date and close is not None:
            parsed.append({"date": str(row_date), "close": close})
    return sorted(parsed, key=lambda row: row["date"])


def fetch_earnings(api_key: str, as_of: date, warnings: list[str]) -> list[dict[str, Any]]:
    result = api_get(
        FMP_V3,
        "/earning_calendar",
        {"from": as_of.isoformat(), "to": (as_of + timedelta(days=7)).isoformat()},
        api_key,
    )
    if result.error:
        warnings.append(f"Earnings calendar fetch failed: {result.error}")
    rows = as_list(result.data)
    return sorted(rows, key=lambda row: (str(row.get("date", "")), str(row.get("symbol", ""))))[:12]


def fetch_news(api_key: str, warnings: list[str]) -> list[dict[str, Any]]:
    result = api_get(FMP_STABLE, "/news/general-latest", {"page": 0, "limit": 8}, api_key)
    if result.error:
        warnings.append(f"General news fetch failed: {result.error}")
    return as_list(result.data)[:6]


def moving_average(rows: list[dict[str, Any]], window: int) -> float | None:
    closes = [row["close"] for row in rows if row.get("close") is not None]
    if len(closes) < window:
        return None
    return sum(closes[-window:]) / window


def support_resistance(rows: list[dict[str, Any]], window: int = 20) -> tuple[float | None, float | None]:
    closes = [row["close"] for row in rows if row.get("close") is not None]
    if not closes:
        return None, None
    subset = closes[-window:]
    return min(subset), max(subset)


def trend_label(current: float | None, ma5: float | None, ma20: float | None) -> str:
    if current is None or ma5 is None or ma20 is None:
        return "Unavailable"
    if current > ma5 and current > ma20:
        return "Bullish"
    if current < ma5 and current < ma20:
        return "Bearish"
    return "Mixed"


def vix_label(vix: float | None) -> str:
    if vix is None:
        return "unavailable"
    if vix >= 30:
        return "stress"
    if vix >= 20:
        return "elevated"
    if vix < 15:
        return "low"
    return "normal"


def market_direction(changes: list[float | None]) -> str:
    clean = [value for value in changes if value is not None]
    if not clean:
        return "mixed"
    average = sum(clean) / len(clean)
    positives = sum(1 for value in clean if value > 0.05)
    negatives = sum(1 for value in clean if value < -0.05)
    if positives >= 2 and average > 0.05:
        return "higher"
    if negatives >= 2 and average < -0.05:
        return "lower"
    return "mixed"


def instrument_row(name: str, row: dict[str, Any] | None) -> str:
    if not row:
        return f"| {name} | n/a | n/a |"
    return f"| {name} | {fmt_level(get_field(row, 'price', 'previousClose'))} | {fmt_pct(quote_change(row))} |"


def format_mover(row: dict[str, Any] | None) -> str:
    if not row:
        return "n/a"
    symbol = row.get("symbol") or row.get("ticker") or row.get("name") or "n/a"
    change = get_field(row, "changesPercentage", "changePercentage", "change")
    return f"{symbol} ({fmt_pct(change)})"


def build_recap(as_of: date, output_dir: Path, api_key: str) -> RecapResult:
    warnings: list[str] = []
    quotes = fetch_quotes(api_key, warnings)
    hot_stock, biggest_loser = fetch_movers(api_key, warnings)
    best_sector, worst_sector, sector_source = fetch_sectors(api_key, as_of, warnings)
    history = fetch_history(api_key, as_of, warnings)
    earnings = fetch_earnings(api_key, as_of, warnings)
    news = fetch_news(api_key, warnings)

    spx = quotes.get("^GSPC")
    dow = quotes.get("^DJI")
    nasdaq = quotes.get("^IXIC")
    vix = quotes.get("^VIX")
    spy = quotes.get("SPY")
    qqq = quotes.get("QQQ")

    spx_level = number(get_field(spx or {}, "price"))
    ma5 = moving_average(history, 5)
    ma20 = moving_average(history, 20)
    support, resistance = support_resistance(history)
    trend = trend_label(spx_level, ma5, ma20)
    vix_level = number(get_field(vix or {}, "price"))
    direction = market_direction([quote_change(spx or {}), quote_change(dow or {}), quote_change(nasdaq or {})])

    best_sector_text = (
        f"{best_sector['name']} ({fmt_pct(best_sector['change'])})" if best_sector else "n/a"
    )
    worst_sector_text = (
        f"{worst_sector['name']} ({fmt_pct(worst_sector['change'])})" if worst_sector else "n/a"
    )

    summary = (
        f"US equities are {direction}: S&P 500 {fmt_pct(quote_change(spx or {}))}, "
        f"Nasdaq {fmt_pct(quote_change(nasdaq or {}))}, Dow {fmt_pct(quote_change(dow or {}))}. "
        f"VIX is {vix_label(vix_level)} at {fmt_level(vix_level)}; S&P 500 trend is {trend}. "
        f"Best sector: {best_sector_text}; worst sector: {worst_sector_text}. "
        f"Hot stock: {format_mover(hot_stock)}; biggest loser: {format_mover(biggest_loser)}."
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"daily-market-recap-{as_of.isoformat()}.md"
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    earnings_lines = ["| Date | Symbol | EPS estimate | Revenue estimate |", "|---|---:|---:|---:|"]
    if earnings:
        for row in earnings:
            earnings_lines.append(
                "| {date} | {symbol} | {eps} | {revenue} |".format(
                    date=row.get("date", "n/a"),
                    symbol=row.get("symbol", "n/a"),
                    eps=fmt_level(get_field(row, "epsEstimated", "epsEstimate")),
                    revenue=fmt_level(get_field(row, "revenueEstimated", "revenueEstimate")),
                )
            )
    else:
        earnings_lines.append("| n/a | No earnings returned for next 7 days | n/a | n/a |")

    headline_lines = []
    for item in news[:5]:
        title = get_field(item, "title", "headline", "publishedTitle")
        source = get_field(item, "site", "publisher", "source")
        if title:
            headline_lines.append(f"- {title}" + (f" ({source})" if source else ""))
    if not headline_lines:
        headline_lines.append("- No broad market headlines returned by FMP.")

    warning_lines = [f"- {warning}" for warning in warnings] if warnings else ["- None."]

    markdown = f"""# Daily Market Recap - {as_of.isoformat()}

_Generated: {generated_at}. Data source: FMP real-time and stable endpoints._

## Executive Summary

{summary}

## Market Dashboard

| Instrument | Level | Day change |
|---|---:|---:|
{instrument_row("S&P 500", spx)}
{instrument_row("Nasdaq Composite", nasdaq)}
{instrument_row("Dow Jones", dow)}
{instrument_row("SPY", spy)}
{instrument_row("QQQ", qqq)}
{instrument_row("VIX", vix)}

## Sector Leadership

- **Best sector:** {best_sector_text}
- **Worst sector:** {worst_sector_text}
- **Sector source:** {sector_source}

## Movers

- **Hot stock:** {format_mover(hot_stock)}
- **Biggest loser:** {format_mover(biggest_loser)}

## S&P 500 Technical Snapshot

| Metric | Value |
|---|---:|
| Current level | {fmt_level(spx_level)} |
| 5D average | {fmt_level(ma5)} |
| 20D average | {fmt_level(ma20)} |
| 20D support | {fmt_level(support)} |
| 20D resistance | {fmt_level(resistance)} |
| Trend | {trend} |

## Earnings Calendar - Next 7 Days

{chr(10).join(earnings_lines)}

## Headlines Watched

{chr(10).join(headline_lines)}

## Data Warnings

{chr(10).join(warning_lines)}

## Disclaimer

This recap is for informational purposes only and is not investment advice or a recommendation to buy, sell, or hold any security. Verify real-time market data before making trading decisions.
"""

    report_path.write_text(markdown, encoding="utf-8")

    telegram_message = "\n".join(
        [
            f"Altamira Daily Market Recap - {as_of.isoformat()}",
            summary,
            f"Markdown report: {report_path.name}",
        ]
    )
    return RecapResult(report_path=report_path, summary=summary, telegram_message=telegram_message, warnings=warnings)


def resolve_telegram_chat_id(cli_chat_id: str | None) -> str:
    if cli_chat_id:
        return cli_chat_id
    for key in ("TELEGRAM_CHAT_ID", "TELEGRAM_CHANNEL_ID", "TELEGRAM_CHANNEL_USERNAME"):
        value = os.environ.get(key)
        if value:
            return value
    return DEFAULT_TELEGRAM_CHAT_ID


def send_to_telegram(token: str, chat_id: str, message: str, report_path: Path) -> None:
    api_base = f"https://api.telegram.org/bot{token}"
    text_response = requests.post(
        f"{api_base}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": message[:3900],
            "disable_web_page_preview": "true",
        },
        timeout=30,
    )
    text_response.raise_for_status()

    with report_path.open("rb") as handle:
        document_response = requests.post(
            f"{api_base}/sendDocument",
            data={
                "chat_id": chat_id,
                "caption": f"Daily Market Recap - {report_path.stem.rsplit('-', 1)[-1]}",
            },
            files={"document": (report_path.name, handle, "text/markdown")},
            timeout=60,
        )
    document_response.raise_for_status()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate and send a daily market recap.")
    parser.add_argument("--date", default=None, help="Recap date in YYYY-MM-DD format; defaults to today.")
    parser.add_argument("--output-dir", default=str(OUTPUTS), help="Output directory for markdown report.")
    parser.add_argument("--chat-id", default=None, help="Telegram chat/channel id override.")
    parser.add_argument("--no-telegram", action="store_true", help="Generate report without sending Telegram messages.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        as_of = date.fromisoformat(args.date) if args.date else date.today()
    except ValueError:
        print(f"Invalid --date value: {args.date}. Use YYYY-MM-DD.", file=sys.stderr)
        return 2

    api_key = resolve_fmp_key()
    recap = build_recap(as_of, Path(args.output_dir), api_key)

    print(recap.summary)
    print(f"Report written: {recap.report_path}")

    if args.no_telegram:
        print("Telegram send skipped (--no-telegram).")
        return 0

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("TELEGRAM_BOT_TOKEN is not set; report was generated but not sent.", file=sys.stderr)
        return 3

    chat_id = resolve_telegram_chat_id(args.chat_id)
    try:
        send_to_telegram(token, chat_id, recap.telegram_message, recap.report_path)
    except requests.RequestException as exc:
        print(f"Telegram send failed: {exc}", file=sys.stderr)
        return 4

    print("Telegram summary and markdown document sent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
