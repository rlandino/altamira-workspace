#!/usr/bin/env python3
"""
Generate the Altamira daily market recap and optionally send it to Telegram.

The recap uses Financial Modeling Prep for index, sector, mover, earnings,
headline, and recent historical data. It writes a markdown report to outputs/
and can send both a concise summary and the markdown file to a Telegram chat.
"""

from __future__ import annotations

import argparse
import html
import json
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
DEFAULT_FMP_KEY = "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz"
DEFAULT_CHAT_ID = "7830722515"


@dataclass
class RecapResult:
    report_path: Path
    summary: str
    telegram_chat_id: str | None
    telegram_message_sent: bool
    telegram_document_sent: bool


def pct(value: Any) -> str:
    """Format a number as a percentage, tolerating API string variants."""
    if value is None or value == "":
        return "N/A"
    if isinstance(value, str):
        cleaned = value.replace("%", "").strip()
    else:
        cleaned = value
    try:
        return f"{float(cleaned):+.2f}%"
    except (TypeError, ValueError):
        return str(value)


def money(value: Any, decimals: int = 2) -> str:
    """Format a numeric market level."""
    if value is None or value == "":
        return "N/A"
    try:
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return str(value)


def api_get(base: str, path: str, api_key: str, params: dict[str, Any] | None = None) -> Any:
    """Fetch JSON from FMP and raise a clear error on failure."""
    request_params = dict(params or {})
    request_params["apikey"] = api_key
    response = requests.get(f"{base}{path}", params=request_params, timeout=20)
    response.raise_for_status()
    return response.json()


def quote_map(api_key: str) -> dict[str, dict[str, Any]]:
    rows = api_get(FMP_V3, "/quote/^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ", api_key)
    if not isinstance(rows, list):
        return {}
    return {str(row.get("symbol")): row for row in rows if isinstance(row, dict)}


def first_row(data: Any) -> dict[str, Any]:
    if isinstance(data, list) and data and isinstance(data[0], dict):
        return data[0]
    return {}


def sector_snapshot(api_key: str, report_date: date) -> list[dict[str, Any]]:
    """Fetch sector snapshot, trying recent dates because same-day data may lag."""
    for offset in range(0, 6):
        day = report_date - timedelta(days=offset)
        if day.weekday() >= 5:
            continue
        try:
            data = api_get(
                FMP_STABLE,
                "/sector-performance-snapshot",
                api_key,
                {"date": day.isoformat()},
            )
        except requests.RequestException:
            continue
        if isinstance(data, list) and data:
            return [row for row in data if isinstance(row, dict)]
    return []


def sector_change(row: dict[str, Any]) -> float | None:
    for key in ("changesPercentage", "changePercentage", "performance", "change", "1D"):
        value = row.get(key)
        if value is None:
            continue
        try:
            return float(str(value).replace("%", "").strip())
        except ValueError:
            continue
    return None


def sector_name(row: dict[str, Any]) -> str:
    return str(row.get("sector") or row.get("name") or row.get("label") or "Unknown")


def earnings_calendar(api_key: str, report_date: date) -> list[dict[str, Any]]:
    to_date = report_date + timedelta(days=7)
    data = api_get(
        FMP_V3,
        "/earning_calendar",
        api_key,
        {"from": report_date.isoformat(), "to": to_date.isoformat()},
    )
    return data if isinstance(data, list) else []


def historical_prices(api_key: str, report_date: date) -> list[dict[str, Any]]:
    from_date = report_date - timedelta(days=45)
    data = api_get(
        FMP_STABLE,
        "/historical-price-eod/light",
        api_key,
        {"symbol": "^GSPC", "from": from_date.isoformat(), "to": report_date.isoformat()},
    )
    rows = data if isinstance(data, list) else []
    clean_rows = []
    for row in rows:
        if not isinstance(row, dict) or "date" not in row:
            continue
        close = row.get("close") or row.get("adjClose") or row.get("price")
        try:
            close_num = float(close)
        except (TypeError, ValueError):
            continue
        clean_rows.append({"date": row["date"], "close": close_num})
    return sorted(clean_rows, key=lambda item: item["date"])


def latest_news(api_key: str) -> list[dict[str, Any]]:
    try:
        data = api_get(
            FMP_STABLE,
            "/news/general-latest",
            api_key,
            {"page": 0, "limit": 5},
        )
    except requests.RequestException:
        return []
    return data if isinstance(data, list) else []


def average(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def trend_label(current: float | None, avg_5d: float | None, avg_20d: float | None) -> str:
    if current is None or avg_5d is None or avg_20d is None:
        return "Unknown"
    if current > avg_5d and current > avg_20d:
        return "Bullish"
    if current < avg_5d and current < avg_20d:
        return "Bearish"
    return "Mixed"


def vix_label(vix: float | None) -> str:
    if vix is None:
        return "unknown"
    if vix > 20:
        return "elevated"
    if vix < 15:
        return "low"
    return "normal"


def build_earnings_table(rows: list[dict[str, Any]], limit: int = 12) -> str:
    if not rows:
        return "No earnings events returned for the next 7 days."
    lines = ["| Date | Symbol | EPS estimate | Revenue estimate |", "|---|---:|---:|---:|"]
    for row in sorted(rows, key=lambda item: (item.get("date") or "", item.get("symbol") or ""))[:limit]:
        revenue = row.get("revenueEstimated")
        revenue_text = f"${float(revenue) / 1_000_000:,.1f}M" if isinstance(revenue, (int, float)) else "N/A"
        lines.append(
            f"| {row.get('date', 'N/A')} | {row.get('symbol', 'N/A')} | "
            f"{money(row.get('epsEstimated'))} | {revenue_text} |"
        )
    return "\n".join(lines)


def headline_lines(news_rows: list[dict[str, Any]]) -> list[str]:
    lines = []
    for row in news_rows[:5]:
        title = row.get("title") or row.get("headline")
        site = row.get("site") or row.get("publisher") or ""
        if title:
            suffix = f" ({site})" if site else ""
            lines.append(f"- {title}{suffix}")
    return lines


def generate_recap(api_key: str, report_date: date, out_path: Path | None = None) -> tuple[Path, str]:
    OUTPUTS.mkdir(parents=True, exist_ok=True)

    quotes = quote_map(api_key)
    gainers = first_row(api_get(FMP_STABLE, "/biggest-gainers", api_key))
    losers = first_row(api_get(FMP_STABLE, "/biggest-losers", api_key))
    sectors = sector_snapshot(api_key, report_date)
    earnings = earnings_calendar(api_key, report_date)
    history = historical_prices(api_key, report_date)
    news_rows = latest_news(api_key)

    spx = quotes.get("^GSPC", {})
    dow = quotes.get("^DJI", {})
    nasdaq = quotes.get("^IXIC", {})
    vix_row = quotes.get("^VIX", {})
    spy = quotes.get("SPY", {})
    qqq = quotes.get("QQQ", {})

    sector_rows = [(sector_change(row), row) for row in sectors]
    sector_rows = [(change, row) for change, row in sector_rows if change is not None]
    best_sector = max(sector_rows, key=lambda item: item[0], default=(None, {}))
    worst_sector = min(sector_rows, key=lambda item: item[0], default=(None, {}))

    closes = [row["close"] for row in history]
    avg_5d = average(closes[-5:])
    avg_20d = average(closes[-20:])
    support = min(closes[-20:]) if len(closes) >= 1 else None
    resistance = max(closes[-20:]) if len(closes) >= 1 else None
    spx_price = spx.get("price")
    try:
        spx_current = float(spx_price)
    except (TypeError, ValueError):
        spx_current = closes[-1] if closes else None
    try:
        vix_current = float(vix_row.get("price"))
    except (TypeError, ValueError):
        vix_current = None

    trend = trend_label(spx_current, avg_5d, avg_20d)
    vix_state = vix_label(vix_current)

    best_sector_text = (
        f"{sector_name(best_sector[1])} ({pct(best_sector[0])})" if best_sector[0] is not None else "N/A"
    )
    worst_sector_text = (
        f"{sector_name(worst_sector[1])} ({pct(worst_sector[0])})" if worst_sector[0] is not None else "N/A"
    )
    hot_stock_text = f"{gainers.get('symbol', 'N/A')} ({pct(gainers.get('changesPercentage'))})"
    loser_text = f"{losers.get('symbol', 'N/A')} ({pct(losers.get('changesPercentage'))})"

    summary = (
        f"Daily market recap {report_date.isoformat()}: S&P 500 {pct(spx.get('changesPercentage'))} "
        f"at {money(spx.get('price'))}, trend {trend}; VIX {money(vix_current)} ({vix_state}). "
        f"Best sector: {best_sector_text}; worst sector: {worst_sector_text}. "
        f"Hot stock: {hot_stock_text}; biggest loser: {loser_text}."
    )

    market_direction = "mixed"
    spx_change = spx.get("changesPercentage")
    nasdaq_change = nasdaq.get("changesPercentage")
    dow_change = dow.get("changesPercentage")
    numeric_changes = []
    for value in (spx_change, nasdaq_change, dow_change):
        try:
            numeric_changes.append(float(str(value).replace("%", "")))
        except (TypeError, ValueError):
            pass
    if numeric_changes and all(change > 0 for change in numeric_changes):
        market_direction = "higher"
    elif numeric_changes and all(change < 0 for change in numeric_changes):
        market_direction = "lower"

    headlines = headline_lines(news_rows)
    headline_section = "\n".join(headlines) if headlines else "No fresh general-market headlines returned by FMP."

    report = f"""# Daily Market Recap - {report_date.isoformat()}

_Generated: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}_

## Executive Summary

{summary}

## Market Indices

| Index | Level | Day Change |
|---|---:|---:|
| S&P 500 | {money(spx.get("price"))} | {pct(spx.get("changesPercentage"))} |
| Nasdaq Composite | {money(nasdaq.get("price"))} | {pct(nasdaq.get("changesPercentage"))} |
| Dow Jones Industrial Average | {money(dow.get("price"))} | {pct(dow.get("changesPercentage"))} |

## ETF and Volatility Snapshot

| Instrument | Level | Day Change |
|---|---:|---:|
| SPY | {money(spy.get("price"))} | {pct(spy.get("changesPercentage"))} |
| QQQ | {money(qqq.get("price"))} | {pct(qqq.get("changesPercentage"))} |
| VIX | {money(vix_current)} | {pct(vix_row.get("changesPercentage"))} |

VIX is **{vix_state}** at {money(vix_current)}.

## Market Movers

- **Hot stock:** {hot_stock_text}
- **Biggest loser:** {loser_text}
- **Best sector:** {best_sector_text}
- **Worst sector:** {worst_sector_text}

## Current Index Levels vs Averages

| Metric | Value |
|---|---:|
| S&P 500 current | {money(spx_current)} |
| 5-day average | {money(avg_5d)} |
| 20-day average | {money(avg_20d)} |
| Trend | {trend} |

## Support and Resistance

Derived from the recent 20-trading-day S&P 500 closing range.

| Level | Value |
|---|---:|
| Resistance | {money(resistance)} |
| Support | {money(support)} |

## Why the Market Moved

Markets finished **{market_direction}** based on the major-index snapshot. FMP headlines to monitor:

{headline_section}

## Economic Calendar: Earnings Next 7 Days

{build_earnings_table(earnings)}

## Commentary

The S&P 500 is {pct(spx.get("changesPercentage"))} with a **{trend}** short-term trend versus its 5-day and 20-day averages. Sector leadership is led by {best_sector_text}, while {worst_sector_text} is lagging. Volatility remains {vix_state}, which frames premium-selling risk and position sizing for tomorrow's options work.

## Disclosure

This recap is for informational purposes only and is not investment advice. Market data may be delayed or revised.
"""
    final_path = out_path or (OUTPUTS / f"daily-market-recap-{report_date.isoformat()}.md")
    final_path.write_text(report, encoding="utf-8")
    return final_path, summary


def send_telegram_message(token: str, chat_id: str, text: str) -> bool:
    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": html.escape(text),
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        },
        timeout=20,
    )
    if not response.ok:
        print(f"Telegram sendMessage failed: {response.status_code} {response.text}", file=sys.stderr)
    return response.ok


def send_telegram_document(token: str, chat_id: str, path: Path, caption: str) -> bool:
    with path.open("rb") as handle:
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendDocument",
            data={"chat_id": chat_id, "caption": caption},
            files={"document": (path.name, handle, "text/markdown")},
            timeout=30,
        )
    if not response.ok:
        print(f"Telegram sendDocument failed: {response.status_code} {response.text}", file=sys.stderr)
    return response.ok


def resolve_chat_id(explicit_chat_id: str | None) -> str | None:
    return explicit_chat_id or os.environ.get("TELEGRAM_CHAT_ID") or DEFAULT_CHAT_ID


def run(args: argparse.Namespace) -> RecapResult:
    report_date = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else date.today()
    api_key = args.fmp_key or os.environ.get("FMP_API_KEY") or DEFAULT_FMP_KEY
    report_path, summary = generate_recap(api_key=api_key, report_date=report_date)

    chat_id = resolve_chat_id(args.telegram_chat_id)
    token = args.telegram_bot_token or os.environ.get("TELEGRAM_BOT_TOKEN")
    message_sent = False
    document_sent = False

    if args.send_telegram:
        if not token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is required to send Telegram messages.")
        if not chat_id:
            raise RuntimeError("TELEGRAM_CHAT_ID or --telegram-chat-id is required to send Telegram messages.")
        message_sent = send_telegram_message(token, chat_id, summary)
        document_sent = send_telegram_document(
            token,
            chat_id,
            report_path,
            f"Daily market recap - {report_date.isoformat()}",
        )
        if not message_sent or not document_sent:
            raise RuntimeError("Telegram delivery failed; see stderr for API response.")

    return RecapResult(
        report_path=report_path,
        summary=summary,
        telegram_chat_id=chat_id if args.send_telegram else None,
        telegram_message_sent=message_sent,
        telegram_document_sent=document_sent,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate daily market recap and optionally send it to Telegram.")
    parser.add_argument("--date", help="Report date in YYYY-MM-DD format. Defaults to today.")
    parser.add_argument("--fmp-key", help="FMP API key. Defaults to FMP_API_KEY or workspace fallback.")
    parser.add_argument("--send-telegram", action="store_true", help="Send summary and markdown report to Telegram.")
    parser.add_argument("--telegram-chat-id", help="Telegram chat/channel ID. Defaults to env or workspace fallback.")
    parser.add_argument("--telegram-bot-token", help="Telegram bot token. Defaults to TELEGRAM_BOT_TOKEN.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable result JSON.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run(args)
    if args.json:
        print(
            json.dumps(
                {
                    "report_path": str(result.report_path),
                    "summary": result.summary,
                    "telegram_chat_id": result.telegram_chat_id,
                    "telegram_message_sent": result.telegram_message_sent,
                    "telegram_document_sent": result.telegram_document_sent,
                },
                indent=2,
            )
        )
    else:
        print(result.summary)
        print(f"Report: {result.report_path}")
        if result.telegram_chat_id:
            print(
                "Telegram: "
                f"message_sent={result.telegram_message_sent}, "
                f"document_sent={result.telegram_document_sent}, "
                f"chat_id={result.telegram_chat_id}"
            )


if __name__ == "__main__":
    main()
