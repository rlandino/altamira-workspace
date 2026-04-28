#!/usr/bin/env python3
"""Generate and optionally deliver the Altamira daily market recap."""

from __future__ import annotations

import argparse
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import requests


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = WORKSPACE / "outputs"
FMP_BASE = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"
DEFAULT_FMP_KEY = "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz"
DEFAULT_TELEGRAM_CHAT_ID = "7830722515"


def get_fmp_key() -> str:
    return os.environ.get("FMP_API_KEY", DEFAULT_FMP_KEY)


def fmp_get(base_url: str, path: str, params: dict[str, Any] | None = None) -> Any:
    """Fetch JSON from FMP with a short timeout."""
    request_params = dict(params or {})
    request_params["apikey"] = get_fmp_key()
    response = requests.get(f"{base_url}{path}", params=request_params, timeout=20)
    response.raise_for_status()
    return response.json()


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        if isinstance(value, str):
            value = value.replace("%", "").replace(",", "").strip()
        return float(value)
    except (TypeError, ValueError):
        return default


def pct(value: Any) -> str:
    return f"{as_float(value):+.2f}%"


def money(value: Any) -> str:
    number = as_float(value)
    return f"{number:,.2f}"


def quote_map() -> dict[str, dict[str, Any]]:
    symbols = "^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ"
    data = fmp_get(FMP_BASE, f"/quote/{symbols}")
    if not isinstance(data, list):
        return {}
    return {str(row.get("symbol", "")): row for row in data if isinstance(row, dict)}


def fetch_earnings(today: date) -> list[dict[str, Any]]:
    to_date = today + timedelta(days=7)
    data = fmp_get(
        FMP_BASE,
        "/earning_calendar",
        {"from": today.isoformat(), "to": to_date.isoformat()},
    )
    return data if isinstance(data, list) else []


def fetch_sector_snapshot(today: date) -> list[dict[str, Any]]:
    for days_back in range(0, 5):
        target = today - timedelta(days=days_back)
        try:
            data = fmp_get(
                FMP_STABLE,
                "/sector-performance-snapshot",
                {"date": target.isoformat()},
            )
        except requests.RequestException:
            continue
        if isinstance(data, list) and data:
            return data
    return []


def fetch_first(path: str) -> dict[str, Any]:
    try:
        data = fmp_get(FMP_STABLE, path)
    except requests.RequestException:
        return {}
    if isinstance(data, list) and data:
        return data[0] if isinstance(data[0], dict) else {}
    return data if isinstance(data, dict) else {}


def fetch_headlines(limit: int = 8) -> list[dict[str, Any]]:
    try:
        data = fmp_get(
            FMP_STABLE,
            "/news/general-latest",
            {"page": 0, "limit": limit},
        )
    except requests.RequestException:
        return []
    return data if isinstance(data, list) else []


def fetch_history(symbol: str, today: date) -> list[dict[str, Any]]:
    from_date = today - timedelta(days=45)
    try:
        data = fmp_get(
            FMP_STABLE,
            "/historical-price-eod/light",
            {"symbol": symbol, "from": from_date.isoformat(), "to": today.isoformat()},
        )
    except requests.RequestException:
        return []
    if not isinstance(data, list):
        return []
    rows = [row for row in data if isinstance(row, dict) and row.get("date")]
    return sorted(rows, key=lambda row: str(row.get("date")))


def sector_name(row: dict[str, Any]) -> str:
    return str(
        row.get("sector")
        or row.get("sectorName")
        or row.get("name")
        or row.get("symbol")
        or "Unknown"
    )


def sector_change(row: dict[str, Any]) -> float:
    for key in (
        "changesPercentage",
        "changePercentage",
        "averageChange",
        "performance",
        "change",
        "1D",
    ):
        if key in row:
            return as_float(row.get(key))
    return 0.0


def summarize_trend(spx: dict[str, Any], history: list[dict[str, Any]]) -> dict[str, Any]:
    closes = [
        as_float(row.get("close") if row.get("close") is not None else row.get("price"))
        for row in history
        if row.get("close") is not None or row.get("price") is not None
    ]
    closes = [close for close in closes if close > 0]
    current = as_float(spx.get("price") or spx.get("previousClose"))
    if not closes or current <= 0:
        return {
            "current": current,
            "sma5": 0.0,
            "sma20": 0.0,
            "support": 0.0,
            "resistance": 0.0,
            "trend": "Unavailable",
        }

    sma5 = sum(closes[-5:]) / min(len(closes), 5)
    sma20 = sum(closes[-20:]) / min(len(closes), 20)
    last20 = closes[-20:]
    above5 = current >= sma5
    above20 = current >= sma20
    trend = "Bullish" if above5 and above20 else "Bearish" if not above5 and not above20 else "Mixed"
    return {
        "current": current,
        "sma5": sma5,
        "sma20": sma20,
        "support": min(last20),
        "resistance": max(last20),
        "trend": trend,
    }


def vix_label(vix_level: float) -> str:
    if vix_level > 20:
        return "elevated"
    if vix_level < 15:
        return "low"
    return "normal"


def earnings_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "No earnings found for the next seven days."
    lines = ["| Date | Symbol | EPS estimate | Revenue estimate |", "|---|---:|---:|---:|"]
    for row in rows[:20]:
        eps = row.get("epsEstimated")
        revenue = row.get("revenueEstimated")
        lines.append(
            "| {date} | {symbol} | {eps} | {revenue} |".format(
                date=row.get("date", ""),
                symbol=row.get("symbol", ""),
                eps="" if eps is None else f"{as_float(eps):.2f}",
                revenue="" if revenue is None else f"{as_float(revenue):,.0f}",
            )
        )
    return "\n".join(lines)


def build_markdown(
    report_date: date,
    quotes: dict[str, dict[str, Any]],
    sectors: list[dict[str, Any]],
    hot_stock: dict[str, Any],
    biggest_loser: dict[str, Any],
    headlines: list[dict[str, Any]],
    earnings: list[dict[str, Any]],
    trend: dict[str, Any],
) -> tuple[str, str]:
    spx = quotes.get("^GSPC", {})
    dow = quotes.get("^DJI", {})
    nasdaq = quotes.get("^IXIC", {})
    vix = quotes.get("^VIX", {})
    spy = quotes.get("SPY", {})
    qqq = quotes.get("QQQ", {})

    sorted_sectors = sorted(sectors, key=sector_change)
    worst_sector = sorted_sectors[0] if sorted_sectors else {}
    best_sector = sorted_sectors[-1] if sorted_sectors else {}
    vix_level = as_float(vix.get("price"))
    vix_context = vix_label(vix_level) if vix_level else "unavailable"
    market_direction = "mixed"
    spx_change = as_float(spx.get("changesPercentage"))
    nasdaq_change = as_float(nasdaq.get("changesPercentage"))
    dow_change = as_float(dow.get("changesPercentage"))
    if spx_change > 0 and nasdaq_change > 0 and dow_change > 0:
        market_direction = "higher"
    elif spx_change < 0 and nasdaq_change < 0 and dow_change < 0:
        market_direction = "lower"

    summary = (
        f"Daily Market Recap - {report_date.isoformat()}\n"
        f"S&P 500 {pct(spx.get('changesPercentage'))} at {money(spx.get('price'))}; "
        f"Nasdaq {pct(nasdaq.get('changesPercentage'))}; Dow {pct(dow.get('changesPercentage'))}. "
        f"Trend: {trend['trend']}. VIX: {money(vix_level)} ({vix_context}).\n"
        f"Best sector: {sector_name(best_sector)} {pct(sector_change(best_sector))}; "
        f"worst sector: {sector_name(worst_sector)} {pct(sector_change(worst_sector))}. "
        f"Hot stock: {hot_stock.get('symbol', 'N/A')} {pct(hot_stock.get('changesPercentage'))}; "
        f"biggest loser: {biggest_loser.get('symbol', 'N/A')} {pct(biggest_loser.get('changesPercentage'))}."
    )

    headline_lines = []
    for item in headlines[:6]:
        title = item.get("title") or item.get("text") or item.get("site") or "Untitled"
        publisher = item.get("site") or item.get("publisher") or ""
        suffix = f" ({publisher})" if publisher else ""
        headline_lines.append(f"- {title}{suffix}")
    if not headline_lines:
        headline_lines = ["- No broad-market headlines returned by the data source."]

    markdown = f"""# Daily Market Recap - {report_date.isoformat()}

> Informational only; not investment advice.

## Summary

{summary}

Markets were {market_direction} based on the major index snapshot. VIX was {vix_context} at {money(vix_level)}, while recent S&P 500 positioning reads {trend['trend'].lower()} versus the 5-day and 20-day averages.

## Market indices

| Index | Level | Day change |
|---|---:|---:|
| S&P 500 | {money(spx.get("price"))} | {pct(spx.get("changesPercentage"))} |
| Nasdaq Composite | {money(nasdaq.get("price"))} | {pct(nasdaq.get("changesPercentage"))} |
| Dow Jones | {money(dow.get("price"))} | {pct(dow.get("changesPercentage"))} |

## ETFs and volatility

| Instrument | Level | Day change |
|---|---:|---:|
| SPY | {money(spy.get("price"))} | {pct(spy.get("changesPercentage"))} |
| QQQ | {money(qqq.get("price"))} | {pct(qqq.get("changesPercentage"))} |
| VIX | {money(vix_level)} | {pct(vix.get("changesPercentage"))} |

## Movers

- Hot stock: **{hot_stock.get("symbol", "N/A")}** {pct(hot_stock.get("changesPercentage"))}
- Biggest loser: **{biggest_loser.get("symbol", "N/A")}** {pct(biggest_loser.get("changesPercentage"))}
- Best sector: **{sector_name(best_sector)}** {pct(sector_change(best_sector))}
- Worst sector: **{sector_name(worst_sector)}** {pct(sector_change(worst_sector))}

## S&P 500 technical snapshot

| Metric | Level |
|---|---:|
| Current | {money(trend["current"])} |
| 5-day average | {money(trend["sma5"])} |
| 20-day average | {money(trend["sma20"])} |
| 20-day resistance | {money(trend["resistance"])} |
| 20-day support | {money(trend["support"])} |
| Trend | {trend["trend"]} |

## Market drivers from headlines

{chr(10).join(headline_lines)}

## Earnings calendar: next seven days

{earnings_table(earnings)}

## Commentary

The tape was {market_direction} across the major averages, with S&P 500 price action {pct(spx.get("changesPercentage"))} and Nasdaq price action {pct(nasdaq.get("changesPercentage"))}. Sector leadership was led by {sector_name(best_sector)}, while {sector_name(worst_sector)} lagged. With VIX at {money(vix_level)}, volatility conditions are {vix_context}; use the S&P 500 support/resistance range above as a short-term context band.
"""
    return summary, markdown


def resolve_chat_id(cli_chat_id: str | None) -> str | None:
    if cli_chat_id:
        return cli_chat_id
    for name in (
        "TELEGRAM_CHAT_ID",
        "TELEGRAM_CHANNEL_ID",
        "MARKET_COMMENTER_TELEGRAM_CHAT_ID",
        "ALTAMIRA_TELEGRAM_CHAT_ID",
    ):
        if os.environ.get(name):
            return os.environ[name]
    return DEFAULT_TELEGRAM_CHAT_ID


def send_telegram(summary: str, report_path: Path, chat_id: str | None) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    if not chat_id:
        raise RuntimeError("Telegram chat id is not configured")

    base = f"https://api.telegram.org/bot{token}"
    message_response = requests.post(
        f"{base}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": summary,
            "disable_web_page_preview": "true",
        },
        timeout=20,
    )
    message_response.raise_for_status()

    with report_path.open("rb") as document:
        document_response = requests.post(
            f"{base}/sendDocument",
            data={"chat_id": chat_id, "caption": f"Daily market recap - {report_path.stem}"},
            files={"document": (report_path.name, document, "text/markdown")},
            timeout=30,
        )
    document_response.raise_for_status()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate and send the daily market recap")
    parser.add_argument("--date", help="Report date in YYYY-MM-DD format; defaults to today")
    parser.add_argument("--out-dir", default=str(OUTPUTS_DIR), help="Directory for the markdown report")
    parser.add_argument("--chat-id", help="Telegram chat/channel id override")
    parser.add_argument("--no-telegram", action="store_true", help="Generate the report without sending Telegram messages")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report_date = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else date.today()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    quotes = quote_map()
    sectors = fetch_sector_snapshot(report_date)
    hot_stock = fetch_first("/biggest-gainers")
    biggest_loser = fetch_first("/biggest-losers")
    headlines = fetch_headlines()
    earnings = fetch_earnings(report_date)
    trend = summarize_trend(quotes.get("^GSPC", {}), fetch_history("^GSPC", report_date))

    summary, markdown = build_markdown(
        report_date,
        quotes,
        sectors,
        hot_stock,
        biggest_loser,
        headlines,
        earnings,
        trend,
    )

    report_path = out_dir / f"daily-market-recap-{report_date.isoformat()}.md"
    report_path.write_text(markdown, encoding="utf-8")

    if not args.no_telegram:
        send_telegram(summary, report_path, resolve_chat_id(args.chat_id))

    print(summary)
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
