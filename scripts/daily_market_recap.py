#!/usr/bin/env python3
"""Generate and optionally deliver the Altamira daily market recap."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS = WORKSPACE / "outputs"
FMP_V3 = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"
ET = ZoneInfo("America/New_York")


class RecapError(RuntimeError):
    """Raised when market recap generation or delivery cannot continue."""


def fetch_json(
    session: requests.Session,
    url: str,
    params: dict[str, Any],
    *,
    required: bool = True,
) -> Any:
    """Fetch JSON from an API endpoint with a concise error message."""
    try:
        response = session.get(url, params=params, timeout=25)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        if required:
            raise RecapError(f"API request failed for {url}: {exc}") from exc
        return None


def coerce_float(value: Any) -> float | None:
    """Convert strings like '+1.23%' or numeric inputs to floats."""
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


def first_value(row: dict[str, Any], keys: tuple[str, ...]) -> Any:
    """Return the first non-empty value for a list of possible API field names."""
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return None


def fmt_price(value: Any, digits: int = 2) -> str:
    number = coerce_float(value)
    return "n/a" if number is None else f"{number:,.{digits}f}"


def fmt_pct(value: Any, digits: int = 2) -> str:
    number = coerce_float(value)
    if number is None:
        return "n/a"
    sign = "+" if number > 0 else ""
    return f"{sign}{number:.{digits}f}%"


def trend_label(spx_price: float | None, sma5: float | None, sma20: float | None) -> str:
    if spx_price is None or sma5 is None or sma20 is None:
        return "Unknown"
    if spx_price > sma5 and spx_price > sma20:
        return "Bullish"
    if spx_price < sma5 and spx_price < sma20:
        return "Bearish"
    return "Mixed"


def vix_label(vix_level: float | None) -> str:
    if vix_level is None:
        return "unknown"
    if vix_level < 15:
        return "low"
    if vix_level <= 20:
        return "normal"
    if vix_level <= 30:
        return "elevated"
    return "stressed"


def market_tone(index_changes: list[float | None]) -> str:
    values = [value for value in index_changes if value is not None]
    if not values:
        return "Unknown"
    positive = sum(1 for value in values if value > 0.05)
    negative = sum(1 for value in values if value < -0.05)
    if positive >= 2:
        return "Higher"
    if negative >= 2:
        return "Lower"
    return "Mixed"


def get_quotes(session: requests.Session, api_key: str) -> dict[str, dict[str, Any]]:
    symbols = "^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ,DIA"
    data = fetch_json(session, f"{FMP_V3}/quote/{symbols}", {"apikey": api_key})
    if not isinstance(data, list):
        raise RecapError("FMP quote response was not a list.")
    return {row.get("symbol"): row for row in data if isinstance(row, dict) and row.get("symbol")}


def get_historical_spx(
    session: requests.Session,
    api_key: str,
    report_date: date,
) -> tuple[float | None, float | None, float | None, float | None]:
    from_date = (report_date - timedelta(days=45)).isoformat()
    data = fetch_json(
        session,
        f"{FMP_STABLE}/historical-price-eod/light",
        {"symbol": "^GSPC", "from": from_date, "to": report_date.isoformat(), "apikey": api_key},
        required=False,
    )
    if not isinstance(data, list):
        return None, None, None, None

    rows = sorted(
        (row for row in data if isinstance(row, dict) and coerce_float(row.get("close")) is not None),
        key=lambda row: row.get("date", ""),
    )
    closes = [coerce_float(row.get("close")) for row in rows]
    closes = [value for value in closes if value is not None]
    if not closes:
        return None, None, None, None

    sma5 = sum(closes[-5:]) / min(5, len(closes)) if closes else None
    sma20 = sum(closes[-20:]) / min(20, len(closes)) if closes else None
    support = min(closes[-20:]) if closes else None
    resistance = max(closes[-20:]) if closes else None
    return sma5, sma20, support, resistance


def get_leader_laggard(
    session: requests.Session,
    api_key: str,
    endpoint: str,
) -> dict[str, Any] | None:
    data = fetch_json(session, f"{FMP_STABLE}/{endpoint}", {"apikey": api_key}, required=False)
    if isinstance(data, list) and data:
        return data[0] if isinstance(data[0], dict) else None
    return None


def get_sector_snapshot(session: requests.Session, api_key: str, report_date: date) -> tuple[str, str]:
    for days_back in range(0, 7):
        snapshot_date = report_date - timedelta(days=days_back)
        data = fetch_json(
            session,
            f"{FMP_STABLE}/sector-performance-snapshot",
            {"date": snapshot_date.isoformat(), "apikey": api_key},
            required=False,
        )
        rows: list[dict[str, Any]] = []
        if isinstance(data, list):
            rows = [row for row in data if isinstance(row, dict)]
        elif isinstance(data, dict):
            nested = data.get("data") or data.get("sectors") or data.get("sectorPerformance")
            if isinstance(nested, list):
                rows = [row for row in nested if isinstance(row, dict)]

        parsed: list[tuple[str, float]] = []
        for row in rows:
            sector = first_value(row, ("sector", "sectorName", "name"))
            change = first_value(
                row,
                ("changesPercentage", "changePercentage", "performance", "change", "1D Change"),
            )
            pct = coerce_float(change)
            if sector and pct is not None:
                parsed.append((str(sector), pct))
        if parsed:
            parsed.sort(key=lambda item: item[1])
            worst = f"{parsed[0][0]} ({fmt_pct(parsed[0][1])})"
            best = f"{parsed[-1][0]} ({fmt_pct(parsed[-1][1])})"
            return best, worst
    return "n/a", "n/a"


def get_earnings(
    session: requests.Session,
    api_key: str,
    report_date: date,
) -> list[dict[str, Any]]:
    data = fetch_json(
        session,
        f"{FMP_V3}/earning_calendar",
        {
            "from": report_date.isoformat(),
            "to": (report_date + timedelta(days=7)).isoformat(),
            "apikey": api_key,
        },
        required=False,
    )
    if not isinstance(data, list):
        return []
    rows = [row for row in data if isinstance(row, dict)]
    return sorted(rows, key=lambda row: (row.get("date") or "", row.get("symbol") or ""))[:25]


def get_headlines(session: requests.Session, api_key: str) -> list[dict[str, Any]]:
    data = fetch_json(
        session,
        f"{FMP_STABLE}/news/general-latest",
        {"page": 0, "limit": 10, "apikey": api_key},
        required=False,
    )
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict)][:8]


def build_report(api_key: str, report_date: date) -> tuple[Path, str]:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(ET)

    with requests.Session() as session:
        quotes = get_quotes(session, api_key)
        sma5, sma20, support, resistance = get_historical_spx(session, api_key, report_date)
        gainer = get_leader_laggard(session, api_key, "biggest-gainers")
        loser = get_leader_laggard(session, api_key, "biggest-losers")
        best_sector, worst_sector = get_sector_snapshot(session, api_key, report_date)
        earnings = get_earnings(session, api_key, report_date)
        headlines = get_headlines(session, api_key)

    index_symbols = [
        ("S&P 500", "^GSPC"),
        ("Nasdaq Composite", "^IXIC"),
        ("Dow Jones", "^DJI"),
    ]
    index_changes = [
        coerce_float(first_value(quotes.get(symbol, {}), ("changesPercentage", "changePercentage")))
        for _, symbol in index_symbols
    ]
    tone = market_tone(index_changes)

    spx = quotes.get("^GSPC", {})
    vix = quotes.get("^VIX", {})
    spx_price = coerce_float(spx.get("price"))
    vix_level = coerce_float(vix.get("price"))
    trend = trend_label(spx_price, sma5, sma20)
    vix_context = vix_label(vix_level)

    hot_symbol = first_value(gainer or {}, ("symbol", "ticker")) or "n/a"
    hot_change = fmt_pct(first_value(gainer or {}, ("changesPercentage", "changePercentage", "change")))
    loser_symbol = first_value(loser or {}, ("symbol", "ticker")) or "n/a"
    loser_change = fmt_pct(first_value(loser or {}, ("changesPercentage", "changePercentage", "change")))

    summary = (
        f"Altamira Daily Market Recap - {report_date.isoformat()}\n"
        f"Market tone: {tone}; S&P 500 {fmt_price(spx.get('price'))} "
        f"({fmt_pct(spx.get('changesPercentage'))}), Nasdaq "
        f"{fmt_price(quotes.get('^IXIC', {}).get('price'))} "
        f"({fmt_pct(quotes.get('^IXIC', {}).get('changesPercentage'))}), Dow "
        f"{fmt_price(quotes.get('^DJI', {}).get('price'))} "
        f"({fmt_pct(quotes.get('^DJI', {}).get('changesPercentage'))}).\n"
        f"Trend: {trend}; VIX {fmt_price(vix.get('price'))} ({vix_context}).\n"
        f"Best sector: {best_sector}; worst sector: {worst_sector}.\n"
        f"Hot stock: {hot_symbol} {hot_change}; biggest loser: {loser_symbol} {loser_change}.\n"
        "Full markdown recap attached."
    )

    lines = [
        f"# Daily Market Recap - {report_date.isoformat()}",
        "",
        f"Generated: {generated_at.strftime('%Y-%m-%d %H:%M %Z')}",
        "",
        "## Executive Summary",
        "",
        f"- **Market tone:** {tone}",
        f"- **S&P 500 trend:** {trend}",
        f"- **VIX:** {fmt_price(vix.get('price'))} ({vix_context})",
        f"- **Leadership:** Best sector {best_sector}; worst sector {worst_sector}",
        f"- **Single-stock movers:** Hot stock {hot_symbol} {hot_change}; biggest loser {loser_symbol} {loser_change}",
        "",
        "## Market Indices",
        "",
        "| Index | Level | Day Change |",
        "| --- | ---: | ---: |",
    ]

    for name, symbol in index_symbols:
        row = quotes.get(symbol, {})
        lines.append(f"| {name} | {fmt_price(row.get('price'))} | {fmt_pct(row.get('changesPercentage'))} |")

    lines.extend(
        [
            "",
            "## ETFs and Volatility",
            "",
            "| Ticker | Level | Day Change |",
            "| --- | ---: | ---: |",
        ]
    )
    for symbol in ("SPY", "QQQ", "DIA", "^VIX"):
        row = quotes.get(symbol, {})
        label = "VIX" if symbol == "^VIX" else symbol
        lines.append(f"| {label} | {fmt_price(row.get('price'))} | {fmt_pct(row.get('changesPercentage'))} |")

    lines.extend(
        [
            "",
            "## Market Leadership",
            "",
            f"- **Best sector:** {best_sector}",
            f"- **Worst sector:** {worst_sector}",
            f"- **Hot stock:** {hot_symbol} {hot_change}",
            f"- **Biggest loser:** {loser_symbol} {loser_change}",
            "",
            "## S&P 500 Technical Context",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            f"| Current level | {fmt_price(spx_price)} |",
            f"| 5-day average | {fmt_price(sma5)} |",
            f"| 20-day average | {fmt_price(sma20)} |",
            f"| 20-day resistance | {fmt_price(resistance)} |",
            f"| 20-day support | {fmt_price(support)} |",
            f"| Trend | {trend} |",
            "",
            "Support and resistance are derived from the recent 20-trading-day S&P 500 close range.",
            "",
            "## Market Drivers from Headlines",
            "",
        ]
    )

    if headlines:
        for item in headlines[:5]:
            title = first_value(item, ("title", "headline", "text")) or "Untitled headline"
            publisher = first_value(item, ("site", "publisher", "source")) or "source n/a"
            published = first_value(item, ("publishedDate", "date")) or "date n/a"
            lines.append(f"- {title} ({publisher}, {published})")
    else:
        lines.append("- No broad-market headlines were available from the configured news source.")

    lines.extend(
        [
            "",
            "## Earnings Calendar: Next 7 Days",
            "",
        ]
    )
    if earnings:
        lines.extend(["| Date | Symbol | EPS Estimate | Revenue Estimate |", "| --- | --- | ---: | ---: |"])
        for row in earnings:
            lines.append(
                "| "
                f"{row.get('date', 'n/a')} | "
                f"{row.get('symbol', 'n/a')} | "
                f"{fmt_price(row.get('epsEstimated'))} | "
                f"{fmt_price(row.get('revenueEstimated'), 0)} |"
            )
    else:
        lines.append("No earnings-calendar entries were returned for the next 7 days.")

    lines.extend(
        [
            "",
            "## Commentary",
            "",
            (
                f"Markets are {tone.lower()} based on the major-index snapshot, with the S&P 500 "
                f"trend reading {trend.lower()} against its 5-day and 20-day averages. "
                f"Volatility is {vix_context} with VIX at {fmt_price(vix.get('price'))}. "
                f"Sector leadership is concentrated in {best_sector}, while {worst_sector} is lagging."
            ),
            "",
            "## Disclaimer",
            "",
            "This recap is for informational purposes only and is not investment advice or a recommendation to buy or sell any security.",
            "",
        ]
    )

    report_path = OUTPUTS / f"daily-market-recap-{report_date.isoformat()}.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path, summary


def send_telegram_message(token: str, chat_id: str, text: str) -> None:
    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={"chat_id": chat_id, "text": text, "disable_web_page_preview": "true"},
        timeout=25,
    )
    if not response.ok:
        raise RecapError(f"Telegram sendMessage failed: HTTP {response.status_code} {response.text[:300]}")


def send_telegram_document(token: str, chat_id: str, document_path: Path, caption: str) -> None:
    with document_path.open("rb") as document:
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendDocument",
            data={"chat_id": chat_id, "caption": caption},
            files={"document": (document_path.name, document, "text/markdown")},
            timeout=40,
        )
    if not response.ok:
        raise RecapError(f"Telegram sendDocument failed: HTTP {response.status_code} {response.text[:300]}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate and deliver the daily market recap.")
    parser.add_argument("--date", help="Report date in YYYY-MM-DD. Defaults to today's New York date.")
    parser.add_argument("--fmp-key", default=os.environ.get("FMP_API_KEY"), help="FMP API key. Defaults to FMP_API_KEY.")
    parser.add_argument(
        "--send-telegram",
        action="store_true",
        help="Send the summary and markdown recap to Telegram.",
    )
    parser.add_argument(
        "--telegram-bot-token",
        default=os.environ.get("TELEGRAM_BOT_TOKEN"),
        help="Telegram bot token. Defaults to TELEGRAM_BOT_TOKEN.",
    )
    parser.add_argument(
        "--telegram-chat-id",
        default=os.environ.get("TELEGRAM_CHAT_ID"),
        help="Telegram chat/channel ID. Defaults to TELEGRAM_CHAT_ID.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.fmp_key:
        raise RecapError("FMP API key missing. Set FMP_API_KEY or pass --fmp-key.")

    report_date = (
        datetime.strptime(args.date, "%Y-%m-%d").date()
        if args.date
        else datetime.now(ET).date()
    )
    report_path, summary = build_report(args.fmp_key, report_date)

    print(summary)
    print(f"Report path: {report_path}")

    if args.send_telegram:
        if not args.telegram_bot_token:
            raise RecapError("Telegram bot token missing. Set TELEGRAM_BOT_TOKEN or pass --telegram-bot-token.")
        if not args.telegram_chat_id:
            raise RecapError("Telegram chat ID missing. Set TELEGRAM_CHAT_ID or pass --telegram-chat-id.")
        send_telegram_message(args.telegram_bot_token, args.telegram_chat_id, summary)
        send_telegram_document(
            args.telegram_bot_token,
            args.telegram_chat_id,
            report_path,
            f"Daily market recap - {report_date.isoformat()}",
        )
        print("Telegram delivery complete.")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RecapError as exc:
        print(f"daily_market_recap: {exc}", file=sys.stderr)
        raise SystemExit(1)
