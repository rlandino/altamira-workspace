#!/usr/bin/env python3
"""Generate an end-of-day market recap and optionally deliver it to Telegram."""

from __future__ import annotations

import argparse
import html
import json
import os
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import requests


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS = WORKSPACE / "outputs"
FMP_V3 = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"
DEFAULT_FMP_KEY = "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz"
DEFAULT_TELEGRAM_CHAT_ID = "7830722515"


@dataclass
class DeliveryResult:
    summary_sent: bool
    document_sent: bool
    chat_id: str
    errors: list[str]


def request_json(url: str, params: dict[str, Any], timeout: int = 20) -> Any:
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def fmp_get(path: str, params: dict[str, Any] | None = None, *, stable: bool = False) -> Any:
    key = os.environ.get("FMP_API_KEY", DEFAULT_FMP_KEY)
    base = FMP_STABLE if stable else FMP_V3
    query = dict(params or {})
    query["apikey"] = key
    return request_json(f"{base}{path}", query)


def pct(value: Any) -> str:
    if value is None:
        return "n/a"
    try:
        return f"{float(value):+.2f}%"
    except (TypeError, ValueError):
        return "n/a"


def money(value: Any) -> str:
    if value is None:
        return "n/a"
    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return "n/a"


def compact_name(row: dict[str, Any]) -> str:
    return row.get("name") or row.get("companyName") or row.get("symbol") or "n/a"


def quote_map(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row.get("symbol", ""): row for row in rows if row.get("symbol")}


def get_sector_snapshot(report_date: date) -> list[dict[str, Any]]:
    for days_back in range(0, 6):
        target = report_date - timedelta(days=days_back)
        try:
            rows = fmp_get(
                "/sector-performance-snapshot",
                {"date": target.isoformat()},
                stable=True,
            )
        except requests.RequestException:
            rows = []
        if isinstance(rows, list) and rows:
            return rows
    return []


def get_historical(symbol: str, report_date: date) -> list[dict[str, Any]]:
    start = report_date - timedelta(days=45)
    rows = fmp_get(
        "/historical-price-eod/light",
        {"symbol": symbol, "from": start.isoformat(), "to": report_date.isoformat()},
        stable=True,
    )
    if not isinstance(rows, list):
        return []
    return sorted(rows, key=lambda row: row.get("date", ""))


def average(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def first_row(data: Any) -> dict[str, Any]:
    if isinstance(data, list) and data:
        return data[0]
    return {}


def vix_label(value: Any) -> str:
    try:
        level = float(value)
    except (TypeError, ValueError):
        return "unknown"
    if level < 15:
        return "low"
    if level > 20:
        return "elevated"
    return "normal"


def trend_label(current: float | None, sma5: float | None, sma20: float | None) -> str:
    if current is None or sma5 is None or sma20 is None:
        return "Unknown"
    if current > sma5 and current > sma20:
        return "Bullish"
    if current < sma5 and current < sma20:
        return "Bearish"
    return "Mixed"


def top_earnings(rows: Any, limit: int = 12) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        return []
    filtered = [row for row in rows if row.get("symbol")]
    return sorted(filtered, key=lambda row: (row.get("date") or "", row.get("symbol") or ""))[:limit]


def latest_headlines(limit: int = 5) -> list[dict[str, Any]]:
    try:
        rows = fmp_get("/news/general-latest", {"page": 0, "limit": limit}, stable=True)
    except requests.RequestException:
        return []
    return rows if isinstance(rows, list) else []


def build_recap(report_date: date) -> tuple[str, str, dict[str, Any]]:
    quotes = quote_map(
        fmp_get("/quote/^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ")
        if True
        else []
    )
    gainers = fmp_get("/biggest-gainers", stable=True)
    losers = fmp_get("/biggest-losers", stable=True)
    sectors = get_sector_snapshot(report_date)
    historical = get_historical("^GSPC", report_date)
    earnings = fmp_get(
        "/earning_calendar",
        {"from": report_date.isoformat(), "to": (report_date + timedelta(days=7)).isoformat()},
    )
    headlines = latest_headlines()

    spx = quotes.get("^GSPC", {})
    dow = quotes.get("^DJI", {})
    nasdaq = quotes.get("^IXIC", {})
    vix = quotes.get("^VIX", {})
    spy = quotes.get("SPY", {})
    qqq = quotes.get("QQQ", {})
    hot = first_row(gainers)
    cold = first_row(losers)

    sector_rows = [
        row
        for row in sectors
        if row.get("sector") is not None and row.get("averageChange") is not None
    ]
    best_sector = max(sector_rows, key=lambda row: float(row.get("averageChange", 0)), default={})
    worst_sector = min(sector_rows, key=lambda row: float(row.get("averageChange", 0)), default={})

    closes = [float(row["price"]) for row in historical if row.get("price") is not None]
    last_20 = closes[-20:]
    sma5 = average(closes[-5:])
    sma20 = average(last_20)
    support = min(last_20) if last_20 else None
    resistance = max(last_20) if last_20 else None
    current_spx = float(spx["price"]) if spx.get("price") is not None else None
    trend = trend_label(current_spx, sma5, sma20)
    vix_context = vix_label(vix.get("price"))
    earnings_rows = top_earnings(earnings)

    headline_lines = [
        f"- {item.get('title', 'Untitled')} ({item.get('publisher', 'unknown')})"
        for item in headlines
        if item.get("title")
    ]

    md = f"""# Daily Market Recap - {report_date.isoformat()}

_Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z').strip()}._

## Executive Summary

- **S&P 500:** {money(spx.get('price'))} ({pct(spx.get('changesPercentage'))}); trend **{trend}**.
- **Nasdaq:** {money(nasdaq.get('price'))} ({pct(nasdaq.get('changesPercentage'))}); **Dow:** {money(dow.get('price'))} ({pct(dow.get('changesPercentage'))}).
- **VIX:** {money(vix.get('price'))} ({vix_context}, {pct(vix.get('changesPercentage'))}).
- **Best sector:** {best_sector.get('sector', 'n/a')} ({pct(best_sector.get('averageChange'))}); **worst sector:** {worst_sector.get('sector', 'n/a')} ({pct(worst_sector.get('averageChange'))}).
- **Hot stock:** {hot.get('symbol', 'n/a')} - {compact_name(hot)} ({pct(hot.get('changesPercentage'))}); **biggest loser:** {cold.get('symbol', 'n/a')} - {compact_name(cold)} ({pct(cold.get('changesPercentage'))}).

## Market Indices

| Index / ETF | Level | Day Change |
|---|---:|---:|
| S&P 500 | {money(spx.get('price'))} | {pct(spx.get('changesPercentage'))} |
| Nasdaq Composite | {money(nasdaq.get('price'))} | {pct(nasdaq.get('changesPercentage'))} |
| Dow Jones | {money(dow.get('price'))} | {pct(dow.get('changesPercentage'))} |
| SPY | {money(spy.get('price'))} | {pct(spy.get('changesPercentage'))} |
| QQQ | {money(qqq.get('price'))} | {pct(qqq.get('changesPercentage'))} |
| VIX | {money(vix.get('price'))} | {pct(vix.get('changesPercentage'))} |

## Sector Snapshot

| Sector | Average Change |
|---|---:|
"""

    for row in sorted(sector_rows, key=lambda item: float(item.get("averageChange", 0)), reverse=True):
        md += f"| {row.get('sector', 'n/a')} | {pct(row.get('averageChange'))} |\n"

    md += f"""
## S&P 500 Technical Context

| Metric | Level |
|---|---:|
| Current | {money(current_spx)} |
| 5-day average | {money(sma5)} |
| 20-day average | {money(sma20)} |
| 20-day resistance | {money(resistance)} |
| 20-day support | {money(support)} |
| Trend | {trend} |

## Companies Reporting Earnings

| Date | Symbol | EPS Estimate | Revenue Estimate |
|---|---:|---:|---:|
"""

    if earnings_rows:
        for row in earnings_rows:
            revenue = row.get("revenueEstimated")
            revenue_text = f"{float(revenue):,.0f}" if isinstance(revenue, (int, float)) else "n/a"
            md += f"| {row.get('date', 'n/a')} | {row.get('symbol', 'n/a')} | {money(row.get('epsEstimated'))} | {revenue_text} |\n"
    else:
        md += "| n/a | No earnings found for the next 7 days | n/a | n/a |\n"

    md += "\n## Market Headlines Checked\n\n"
    md += "\n".join(headline_lines) if headline_lines else "No broad-market headlines returned by FMP."

    md += f"""

## Commentary

Markets finished with the S&P 500 at {money(spx.get('price'))}, {pct(spx.get('changesPercentage'))} on the day, leaving the short-term S&P trend classified as **{trend}**. Volatility is **{vix_context}** with VIX at {money(vix.get('price'))}, while sector breadth favored **{best_sector.get('sector', 'n/a')}** and lagged in **{worst_sector.get('sector', 'n/a')}**. The 20-day S&P 500 range points to support near {money(support)} and resistance near {money(resistance)}.

_Data source: Financial Modeling Prep. This market recap is informational only and is not investment advice._
"""

    summary = (
        f"Daily market recap {report_date.isoformat()}: S&P 500 {money(spx.get('price'))} "
        f"({pct(spx.get('changesPercentage'))}), Nasdaq {pct(nasdaq.get('changesPercentage'))}, "
        f"Dow {pct(dow.get('changesPercentage'))}; trend {trend}. VIX {money(vix.get('price'))} "
        f"({vix_context}). Best sector: {best_sector.get('sector', 'n/a')} "
        f"({pct(best_sector.get('averageChange'))}); worst: {worst_sector.get('sector', 'n/a')} "
        f"({pct(worst_sector.get('averageChange'))}). Hot stock: {hot.get('symbol', 'n/a')} "
        f"({pct(hot.get('changesPercentage'))}); biggest loser: {cold.get('symbol', 'n/a')} "
        f"({pct(cold.get('changesPercentage'))})."
    )

    metadata = {
        "date": report_date.isoformat(),
        "trend": trend,
        "spx": spx,
        "nasdaq": nasdaq,
        "dow": dow,
        "vix": vix,
        "best_sector": best_sector,
        "worst_sector": worst_sector,
        "hot_stock": hot,
        "biggest_loser": cold,
        "support": support,
        "resistance": resistance,
    }
    return md, summary, metadata


def telegram_api(method: str, payload: dict[str, Any] | None = None, files: dict[str, Any] | None = None) -> dict[str, Any]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    response = requests.post(
        f"https://api.telegram.org/bot{token}/{method}",
        data=payload or {},
        files=files,
        timeout=30,
    )
    response.raise_for_status()
    body = response.json()
    if not body.get("ok"):
        raise RuntimeError(json.dumps(body))
    return body


def send_to_telegram(summary: str, markdown_path: Path, *, chat_id: str | None = None) -> DeliveryResult:
    target_chat = chat_id or os.environ.get("TELEGRAM_CHAT_ID") or DEFAULT_TELEGRAM_CHAT_ID
    errors: list[str] = []
    summary_sent = False
    document_sent = False

    text = (
        "<b>Altamira Daily Market Recap</b>\n\n"
        f"{html.escape(summary)}\n\n"
        f"Markdown file: <code>{html.escape(markdown_path.name)}</code>"
    )
    try:
        telegram_api(
            "sendMessage",
            {
                "chat_id": target_chat,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": "true",
            },
        )
        summary_sent = True
    except Exception as exc:  # noqa: BLE001 - delivery diagnostics should not hide partial success.
        errors.append(f"summary send failed: {exc}")

    try:
        with markdown_path.open("rb") as handle:
            telegram_api(
                "sendDocument",
                {
                    "chat_id": target_chat,
                    "caption": f"Daily market recap markdown - {markdown_path.stem}",
                },
                files={"document": (markdown_path.name, handle, "text/markdown")},
            )
        document_sent = True
    except Exception as exc:  # noqa: BLE001
        errors.append(f"document send failed: {exc}")

    return DeliveryResult(summary_sent, document_sent, target_chat, errors)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate and deliver Altamira daily market recap.")
    parser.add_argument("--date", help="Recap date in YYYY-MM-DD format. Defaults to today.")
    parser.add_argument("--send-telegram", action="store_true", help="Send summary and markdown file to Telegram.")
    parser.add_argument("--chat-id", help="Telegram chat/channel ID. Defaults to TELEGRAM_CHAT_ID or workspace fallback.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report_date = date.fromisoformat(args.date) if args.date else date.today()
    OUTPUTS.mkdir(parents=True, exist_ok=True)

    markdown, summary, metadata = build_recap(report_date)
    output_path = OUTPUTS / f"daily-market-recap-{report_date.isoformat()}.md"
    output_path.write_text(markdown, encoding="utf-8")

    summary_path = OUTPUTS / f"daily-market-recap-{report_date.isoformat()}.summary.json"
    summary_path.write_text(
        json.dumps({"summary": summary, "metadata": metadata}, indent=2, default=str),
        encoding="utf-8",
    )

    print(summary)
    print(f"Report: {output_path}")

    if args.send_telegram:
        delivery = send_to_telegram(summary, output_path, chat_id=args.chat_id)
        print(
            "Telegram:",
            json.dumps(
                {
                    "chat_id": delivery.chat_id,
                    "summary_sent": delivery.summary_sent,
                    "document_sent": delivery.document_sent,
                    "errors": delivery.errors,
                },
                indent=2,
            ),
        )
        if delivery.errors:
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
