#!/usr/bin/env python3
"""
Generate an Altamira daily market recap and optionally deliver it to Telegram.

The script uses FMP for market data and the Telegram Bot API for delivery.
It writes a markdown report to outputs/daily-market-recap-{DATE}.md.
"""

from __future__ import annotations

import argparse
import json
import os
import re
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
class MarketRecap:
    report_date: str
    markdown_path: Path
    summary: str
    voice_summary: str
    telegram_message: str


def fmp_key() -> str:
    """Return the FMP key, preferring environment configuration."""
    return os.environ.get("FMP_API_KEY", DEFAULT_FMP_KEY)


def request_json(url: str, params: dict[str, Any] | None = None) -> Any:
    """GET JSON with a clear error on API or transport failures."""
    response = requests.get(url, params=params or {}, timeout=20)
    response.raise_for_status()
    return response.json()


def fmp_v3(path: str, params: dict[str, Any] | None = None) -> Any:
    query = dict(params or {})
    query["apikey"] = fmp_key()
    return request_json(f"{FMP_V3}{path}", query)


def fmp_stable(path: str, params: dict[str, Any] | None = None) -> Any:
    query = dict(params or {})
    query["apikey"] = fmp_key()
    return request_json(f"{FMP_STABLE}{path}", query)


def first_list_item(data: Any) -> dict[str, Any]:
    if isinstance(data, list) and data:
        first = data[0]
        return first if isinstance(first, dict) else {}
    return data if isinstance(data, dict) else {}


def pct(value: Any) -> str:
    try:
        number = float(str(value).replace("%", ""))
    except (TypeError, ValueError):
        return "n/a"
    return f"{number:+.2f}%"


def money(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "n/a"
    return f"{number:,.2f}"


def get_change(row: dict[str, Any]) -> Any:
    for key in ("changesPercentage", "changePercentage", "change", "changes"):
        if key in row and row[key] not in (None, ""):
            return row[key]
    return None


def parse_sector_performance(data: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return best and worst sector rows from FMP sector snapshot variants."""
    rows: list[dict[str, Any]] = []
    if isinstance(data, list):
        rows = [row for row in data if isinstance(row, dict)]
    elif isinstance(data, dict):
        for value in data.values():
            if isinstance(value, list):
                rows.extend(row for row in value if isinstance(row, dict))
            elif isinstance(value, dict):
                rows.append(value)

    def row_pct(row: dict[str, Any]) -> float:
        for key in (
            "changesPercentage",
            "changePercentage",
            "performance",
            "averageChange",
            "change",
        ):
            if key in row:
                try:
                    return float(str(row[key]).replace("%", ""))
                except (TypeError, ValueError):
                    continue
        return 0.0

    if not rows:
        return {}, {}

    best = max(rows, key=row_pct)
    worst = min(rows, key=row_pct)
    return best, worst


def sector_name(row: dict[str, Any]) -> str:
    for key in ("sector", "sectorName", "name"):
        if row.get(key):
            return str(row[key])
    return "n/a"


def sector_change(row: dict[str, Any]) -> str:
    for key in (
        "changesPercentage",
        "changePercentage",
        "performance",
        "averageChange",
        "change",
    ):
        if row.get(key) is not None:
            return pct(row[key])
    return "n/a"


def fetch_history(symbol: str, report_date: str) -> list[dict[str, Any]]:
    from_date = (
        datetime.strptime(report_date, "%Y-%m-%d") - timedelta(days=45)
    ).strftime("%Y-%m-%d")
    data = fmp_stable(
        "/historical-price-eod/light",
        {"symbol": symbol, "from": from_date, "to": report_date},
    )
    if not isinstance(data, list):
        return []
    rows = []
    for row in data:
        if not isinstance(row, dict):
            continue
        close = row.get("close", row.get("price"))
        if close is None:
            continue
        normalized = dict(row)
        normalized["close"] = close
        rows.append(normalized)
    return sorted(rows, key=lambda row: row.get("date", ""))


def moving_average(rows: list[dict[str, Any]], window: int) -> float | None:
    closes = []
    for row in rows[-window:]:
        try:
            closes.append(float(row["close"]))
        except (KeyError, TypeError, ValueError):
            continue
    if len(closes) < window:
        return None
    return sum(closes) / len(closes)


def support_resistance(rows: list[dict[str, Any]], window: int = 20) -> tuple[float | None, float | None]:
    closes = []
    for row in rows[-window:]:
        try:
            closes.append(float(row["close"]))
        except (KeyError, TypeError, ValueError):
            continue
    if not closes:
        return None, None
    return min(closes), max(closes)


def vix_label(vix: float | None) -> str:
    if vix is None:
        return "unknown"
    if vix > 20:
        return "elevated"
    if vix < 15:
        return "low"
    return "normal"


def determine_trend(price: float | None, ma5: float | None, ma20: float | None) -> str:
    if price is None or ma5 is None or ma20 is None:
        return "Mixed"
    if price > ma5 and price > ma20:
        return "Bullish"
    if price < ma5 and price < ma20:
        return "Bearish"
    return "Mixed"


def safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fetch_market_data(report_date: str) -> dict[str, Any]:
    quote_rows = fmp_v3("/quote/^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ")
    quotes = {row.get("symbol"): row for row in quote_rows if isinstance(row, dict)}

    today = datetime.strptime(report_date, "%Y-%m-%d").date()
    earnings_to = (today + timedelta(days=7)).strftime("%Y-%m-%d")

    data: dict[str, Any] = {
        "quotes": quotes,
        "gainers": first_list_item(fmp_stable("/biggest-gainers")),
        "losers": first_list_item(fmp_stable("/biggest-losers")),
        "earnings": fmp_v3(
            "/earning_calendar",
            {"from": report_date, "to": earnings_to},
        ),
        "history": fetch_history("^GSPC", report_date),
    }

    try:
        sector_data = fmp_stable("/sector-performance-snapshot", {"date": report_date})
    except requests.RequestException:
        sector_data = fmp_stable("/sector-performance-snapshot")
    data["best_sector"], data["worst_sector"] = parse_sector_performance(sector_data)

    try:
        data["news"] = fmp_stable("/news/general-latest", {"page": 0, "limit": 5})
    except requests.RequestException:
        data["news"] = []

    return data


def format_earnings(rows: Any, limit: int = 10) -> str:
    if not isinstance(rows, list) or not rows:
        return "No earnings calendar items returned for the next 7 days."
    lines = ["| Date | Symbol | EPS estimate | Revenue estimate |", "|---|---:|---:|---:|"]
    for row in rows[:limit]:
        if not isinstance(row, dict):
            continue
        lines.append(
            "| {date} | {symbol} | {eps} | {revenue} |".format(
                date=row.get("date", "n/a"),
                symbol=row.get("symbol", "n/a"),
                eps=row.get("epsEstimated", "n/a"),
                revenue=row.get("revenueEstimated", "n/a"),
            )
        )
    return "\n".join(lines)


def format_news(rows: Any) -> str:
    if not isinstance(rows, list) or not rows:
        return "- No broad market headlines returned by FMP."
    lines = []
    for row in rows[:5]:
        if not isinstance(row, dict):
            continue
        title = row.get("title") or row.get("headline") or "Untitled"
        site = row.get("site") or row.get("publisher") or ""
        suffix = f" ({site})" if site else ""
        lines.append(f"- {title}{suffix}")
    return "\n".join(lines) if lines else "- No broad market headlines returned by FMP."


def quote_line(label: str, row: dict[str, Any]) -> str:
    return f"| {label} | {money(row.get('price'))} | {pct(get_change(row))} |"


def build_recap(report_date: str) -> MarketRecap:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    data = fetch_market_data(report_date)
    quotes = data["quotes"]
    spx = quotes.get("^GSPC", {})
    nasdaq = quotes.get("^IXIC", {})
    dow = quotes.get("^DJI", {})
    vix = quotes.get("^VIX", {})
    spy = quotes.get("SPY", {})
    qqq = quotes.get("QQQ", {})

    spx_price = safe_float(spx.get("price"))
    vix_price = safe_float(vix.get("price"))
    history = data["history"]
    ma5 = moving_average(history, 5)
    ma20 = moving_average(history, 20)
    support, resistance = support_resistance(history)
    trend = determine_trend(spx_price, ma5, ma20)
    vix_context = vix_label(vix_price)

    gainer = data["gainers"]
    loser = data["losers"]
    best_sector = data["best_sector"]
    worst_sector = data["worst_sector"]

    summary = (
        f"S&P 500 {pct(get_change(spx))} at {money(spx.get('price'))}; "
        f"Nasdaq {pct(get_change(nasdaq))}, Dow {pct(get_change(dow))}. "
        f"Trend is {trend}; VIX is {vix_context} at {money(vix.get('price'))}. "
        f"Best sector: {sector_name(best_sector)} ({sector_change(best_sector)}); "
        f"worst sector: {sector_name(worst_sector)} ({sector_change(worst_sector)}). "
        f"Hot stock: {gainer.get('symbol', 'n/a')} ({pct(get_change(gainer))}); "
        f"biggest loser: {loser.get('symbol', 'n/a')} ({pct(get_change(loser))})."
    )
    voice_summary = f"Daily market recap for {report_date}. {summary}"

    markdown = f"""# Daily Market Recap - {report_date}

_Generated for Altamira Capital. Market data source: Financial Modeling Prep._

## Executive Summary

{summary}

## Market Indices

| Index / ETF | Level | Day change |
|---|---:|---:|
{quote_line("S&P 500", spx)}
{quote_line("Nasdaq Composite", nasdaq)}
{quote_line("Dow Jones", dow)}
{quote_line("SPY", spy)}
{quote_line("QQQ", qqq)}
{quote_line("VIX", vix)}

## Market Internals

- **Trend:** {trend}
- **VIX context:** {vix_context.title()} at {money(vix.get('price'))}
- **Best sector:** {sector_name(best_sector)} ({sector_change(best_sector)})
- **Worst sector:** {sector_name(worst_sector)} ({sector_change(worst_sector)})
- **Hot stock:** {gainer.get('symbol', 'n/a')} ({pct(get_change(gainer))})
- **Biggest loser:** {loser.get('symbol', 'n/a')} ({pct(get_change(loser))})

## S&P 500 Technical Snapshot

| Metric | Value |
|---|---:|
| Current level | {money(spx_price)} |
| 5-day average | {money(ma5)} |
| 20-day average | {money(ma20)} |
| 20-day support | {money(support)} |
| 20-day resistance | {money(resistance)} |

## Market Headlines

{format_news(data.get("news"))}

## Earnings Calendar - Next 7 Days

{format_earnings(data.get("earnings"))}

## Commentary

Markets are {trend.lower()} on the S&P 500 trend framework, with the index trading {'above' if spx_price and ma20 and spx_price > ma20 else 'below or near'} its 20-day average. Volatility is {vix_context}, while sector leadership is coming from {sector_name(best_sector)} and weakness is concentrated in {sector_name(worst_sector)}.

## Disclaimer

This recap is for informational purposes only and is not investment advice or a recommendation to buy or sell securities.
"""

    markdown_path = OUTPUTS / f"daily-market-recap-{report_date}.md"
    markdown_path.write_text(markdown, encoding="utf-8")

    telegram_message = (
        f"Altamira Daily Market Recap - {report_date}\n\n"
        f"{summary}\n\n"
        f"Report attached: {markdown_path.name}\n\n"
        "Informational only; not investment advice."
    )

    return MarketRecap(
        report_date=report_date,
        markdown_path=markdown_path,
        summary=summary,
        voice_summary=voice_summary,
        telegram_message=telegram_message,
    )


def load_telegram_chat_id(cli_value: str | None) -> str | None:
    """Resolve chat ID from CLI/env, then workspace fallback used by prior exports."""
    if cli_value:
        return cli_value
    for key in ("TELEGRAM_CHAT_ID", "TELEGRAM_CHANNEL_ID"):
        if os.environ.get(key):
            return os.environ[key]
    return DEFAULT_TELEGRAM_CHAT_ID


def send_telegram(recap: MarketRecap, chat_id: str, bot_token: str) -> None:
    base = f"https://api.telegram.org/bot{bot_token}"
    message_response = requests.post(
        f"{base}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": recap.telegram_message,
            "disable_web_page_preview": "true",
        },
        timeout=20,
    )
    message_response.raise_for_status()

    with recap.markdown_path.open("rb") as markdown_file:
        document_response = requests.post(
            f"{base}/sendDocument",
            data={
                "chat_id": chat_id,
                "caption": f"Daily market recap markdown - {recap.report_date}",
            },
            files={
                "document": (
                    recap.markdown_path.name,
                    markdown_file,
                    "text/markdown",
                )
            },
            timeout=30,
        )
    document_response.raise_for_status()


def valid_date(value: str) -> str:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD")
    datetime.strptime(value, "%Y-%m-%d")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate and send a daily market recap")
    parser.add_argument(
        "--date",
        type=valid_date,
        default=date.today().strftime("%Y-%m-%d"),
        help="Report date in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--send-telegram",
        action="store_true",
        help="Send summary and markdown file to Telegram",
    )
    parser.add_argument(
        "--telegram-chat-id",
        default=None,
        help="Telegram chat/channel ID; defaults to TELEGRAM_CHAT_ID/TELEGRAM_CHANNEL_ID",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable result metadata",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        recap = build_recap(args.date)
        telegram_sent = False
        if args.send_telegram:
            bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
            chat_id = load_telegram_chat_id(args.telegram_chat_id)
            if not bot_token:
                raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
            if not chat_id:
                raise RuntimeError("Telegram chat ID is not configured")
            send_telegram(recap, chat_id, bot_token)
            telegram_sent = True

        result = {
            "date": recap.report_date,
            "markdown_path": str(recap.markdown_path.relative_to(WORKSPACE)),
            "summary": recap.summary,
            "telegram_sent": telegram_sent,
        }
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(recap.summary)
            print(f"Markdown: {result['markdown_path']}")
            print(f"Telegram sent: {telegram_sent}")
        return 0
    except Exception as exc:
        print(f"daily_market_recap error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
