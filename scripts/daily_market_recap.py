#!/usr/bin/env python3
"""
Generate a daily market recap and optionally deliver it to Telegram.

The script uses FMP for live market data and Telegram's Bot API for delivery.
Secrets are supplied through environment variables or CLI flags; no credentials
are stored in the workspace.
"""

from __future__ import annotations

import argparse
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


@dataclass(frozen=True)
class RecapResult:
    report_path: Path
    summary_path: Path
    summary: str
    sent_to_telegram: bool


class DataIssue(RuntimeError):
    """Raised when a required data source cannot be used."""


def get_json(url: str, params: dict[str, Any], label: str) -> Any:
    """Fetch JSON from an HTTP endpoint with a concise error message."""
    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise DataIssue(f"{label} request failed: {exc}") from exc
    except ValueError as exc:
        raise DataIssue(f"{label} returned invalid JSON") from exc


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace("%", "").replace(",", "")
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def fmt_num(value: Any, decimals: int = 2) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number:,.{decimals}f}"


def fmt_pct(value: Any, signed: bool = True) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    prefix = "+" if signed and number > 0 else ""
    return f"{prefix}{number:.2f}%"


def pct_value(row: dict[str, Any]) -> float | None:
    for key in ("changesPercentage", "changePercentage", "changes", "change", "percent", "1D Change"):
        value = as_float(row.get(key))
        if value is not None:
            return value
    return None


def price_value(row: dict[str, Any]) -> float | None:
    for key in ("price", "close", "adjClose", "value"):
        value = as_float(row.get(key))
        if value is not None:
            return value
    return None


def normalize_symbol(symbol: str) -> str:
    return symbol.upper().replace("^", "")


def quote_map(rows: Any) -> dict[str, dict[str, Any]]:
    quotes: dict[str, dict[str, Any]] = {}
    if not isinstance(rows, list):
        return quotes
    for row in rows:
        if not isinstance(row, dict):
            continue
        raw_symbol = str(row.get("symbol", "")).upper()
        if raw_symbol:
            quotes[raw_symbol] = row
            quotes[normalize_symbol(raw_symbol)] = row
    return quotes


def fetch_quotes(api_key: str) -> dict[str, dict[str, Any]]:
    symbols = "^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ"
    rows = get_json(f"{FMP_V3}/quote/{symbols}", {"apikey": api_key}, "FMP quote")
    quotes = quote_map(rows)
    if not quotes:
        raise DataIssue("FMP quote returned no usable rows")
    return quotes


def fetch_movers(api_key: str, endpoint: str, label: str) -> dict[str, Any] | None:
    rows = get_json(f"{FMP_STABLE}/{endpoint}", {"apikey": api_key}, label)
    if isinstance(rows, list) and rows:
        first = rows[0]
        return first if isinstance(first, dict) else None
    return None


def fetch_sectors(api_key: str, report_date: date) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    params = {"date": report_date.isoformat(), "apikey": api_key}
    rows = get_json(f"{FMP_STABLE}/sector-performance-snapshot", params, "FMP sector snapshot")
    if isinstance(rows, dict):
        rows = rows.get("sectorPerformance") or rows.get("data") or rows.get("sectors") or []
    if not isinstance(rows, list):
        return None, None

    usable = [row for row in rows if isinstance(row, dict) and pct_value(row) is not None]
    if not usable:
        return None, None
    best = max(usable, key=lambda row: pct_value(row) or 0.0)
    worst = min(usable, key=lambda row: pct_value(row) or 0.0)
    return best, worst


def fetch_history(api_key: str, report_date: date) -> list[dict[str, Any]]:
    from_date = report_date - timedelta(days=45)
    rows = get_json(
        f"{FMP_STABLE}/historical-price-eod/light",
        {
            "symbol": "^GSPC",
            "from": from_date.isoformat(),
            "to": report_date.isoformat(),
            "apikey": api_key,
        },
        "FMP historical EOD",
    )
    if not isinstance(rows, list):
        return []
    usable = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        close = price_value(row)
        raw_date = row.get("date")
        if close is None or not raw_date:
            continue
        usable.append({"date": str(raw_date), "close": close})
    return sorted(usable, key=lambda row: row["date"])


def fetch_earnings(api_key: str, report_date: date) -> list[dict[str, Any]]:
    rows = get_json(
        f"{FMP_V3}/earning_calendar",
        {
            "from": report_date.isoformat(),
            "to": (report_date + timedelta(days=7)).isoformat(),
            "apikey": api_key,
        },
        "FMP earnings calendar",
    )
    if not isinstance(rows, list):
        return []
    usable = [row for row in rows if isinstance(row, dict)]
    return sorted(usable, key=lambda row: str(row.get("date", "")))[:12]


def fetch_news(api_key: str) -> list[dict[str, Any]]:
    try:
        rows = get_json(
            f"{FMP_STABLE}/news/general-latest",
            {"page": 0, "limit": 8, "apikey": api_key},
            "FMP general news",
        )
    except DataIssue:
        return []
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)][:8]


def moving_average(values: list[float], window: int) -> float | None:
    if len(values) < window:
        return None
    return sum(values[-window:]) / window


def sector_name(row: dict[str, Any] | None) -> str:
    if not row:
        return "n/a"
    for key in ("sector", "sectorName", "name"):
        value = row.get(key)
        if value:
            return str(value)
    return "n/a"


def mover_symbol(row: dict[str, Any] | None) -> str:
    if not row:
        return "n/a"
    for key in ("symbol", "ticker"):
        value = row.get(key)
        if value:
            return str(value).upper()
    return "n/a"


def vix_label(vix_level: float | None) -> str:
    if vix_level is None:
        return "unavailable"
    if vix_level > 20:
        return "elevated"
    if vix_level < 15:
        return "low"
    return "normal"


def market_direction(spx_change: float | None, nasdaq_change: float | None, dow_change: float | None) -> str:
    changes = [change for change in (spx_change, nasdaq_change, dow_change) if change is not None]
    if not changes:
        return "mixed"
    positives = sum(1 for change in changes if change > 0.1)
    negatives = sum(1 for change in changes if change < -0.1)
    if positives >= 2 and positives > negatives:
        return "higher"
    if negatives >= 2 and negatives > positives:
        return "lower"
    return "mixed"


def trend_label(current: float | None, ma5: float | None, ma20: float | None) -> str:
    if current is None or ma5 is None or ma20 is None:
        return "Unavailable"
    if current > ma5 and current > ma20:
        return "Bullish"
    if current < ma5 and current < ma20:
        return "Bearish"
    return "Mixed"


def table_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def build_report(
    api_key: str,
    report_date: date,
    output_dir: Path,
) -> RecapResult:
    quotes = fetch_quotes(api_key)
    hot_stock = fetch_movers(api_key, "biggest-gainers", "FMP biggest gainers")
    biggest_loser = fetch_movers(api_key, "biggest-losers", "FMP biggest losers")
    best_sector, worst_sector = fetch_sectors(api_key, report_date)
    history = fetch_history(api_key, report_date)
    earnings = fetch_earnings(api_key, report_date)
    news = fetch_news(api_key)

    spx = quotes.get("^GSPC") or quotes.get("GSPC") or {}
    dow = quotes.get("^DJI") or quotes.get("DJI") or {}
    nasdaq = quotes.get("^IXIC") or quotes.get("IXIC") or {}
    vix = quotes.get("^VIX") or quotes.get("VIX") or {}
    spy = quotes.get("SPY") or {}
    qqq = quotes.get("QQQ") or {}

    spx_price = price_value(spx)
    spx_change = pct_value(spx)
    dow_change = pct_value(dow)
    nasdaq_change = pct_value(nasdaq)
    vix_level = price_value(vix)

    closes = [row["close"] for row in history]
    ma5 = moving_average(closes, 5)
    ma20 = moving_average(closes, 20)
    recent_20 = closes[-20:] if len(closes) >= 20 else closes
    support = min(recent_20) if recent_20 else None
    resistance = max(recent_20) if recent_20 else None
    trend = trend_label(spx_price, ma5, ma20)
    direction = market_direction(spx_change, nasdaq_change, dow_change)
    vix_context = vix_label(vix_level)

    best_sector_text = f"{sector_name(best_sector)} ({fmt_pct(pct_value(best_sector or {}))})"
    worst_sector_text = f"{sector_name(worst_sector)} ({fmt_pct(pct_value(worst_sector or {}))})"
    hot_stock_text = f"{mover_symbol(hot_stock)} ({fmt_pct(pct_value(hot_stock or {}))})"
    loser_text = f"{mover_symbol(biggest_loser)} ({fmt_pct(pct_value(biggest_loser or {}))})"

    summary = (
        f"Daily market recap: S&P 500 {fmt_pct(spx_change).lower()} at {fmt_num(spx_price)}, "
        f"trend {trend}; VIX is {vix_context} at {fmt_num(vix_level)}. "
        f"Best sector: {best_sector_text}; worst sector: {worst_sector_text}. "
        f"Hot stock: {hot_stock_text}; biggest loser: {loser_text}."
    )

    lines: list[str] = [
        f"# Daily Market Recap - {report_date.isoformat()}",
        "",
        "> Informational only; not investment advice. Market data is sourced from Financial Modeling Prep and may be delayed.",
        "",
        "## Executive Summary",
        "",
        summary,
        "",
        "## Market Indices",
        "",
        table_row(["Index", "Level", "Day Change"]),
        table_row(["---", "---:", "---:"]),
        table_row(["S&P 500", fmt_num(spx_price), fmt_pct(spx_change)]),
        table_row(["Nasdaq Composite", fmt_num(price_value(nasdaq)), fmt_pct(nasdaq_change)]),
        table_row(["Dow Jones", fmt_num(price_value(dow)), fmt_pct(dow_change)]),
        "",
        "## ETFs and Volatility",
        "",
        table_row(["Instrument", "Level", "Day Change", "Context"]),
        table_row(["---", "---:", "---:", "---"]),
        table_row(["SPY", fmt_num(price_value(spy)), fmt_pct(pct_value(spy)), "S&P 500 ETF"]),
        table_row(["QQQ", fmt_num(price_value(qqq)), fmt_pct(pct_value(qqq)), "Nasdaq 100 ETF"]),
        table_row(["VIX", fmt_num(vix_level), fmt_pct(pct_value(vix)), vix_context.title()]),
        "",
        "## Leadership and Laggards",
        "",
        f"- **Hot stock:** {hot_stock_text}",
        f"- **Biggest loser:** {loser_text}",
        f"- **Best sector:** {best_sector_text}",
        f"- **Worst sector:** {worst_sector_text}",
        "",
        "## S&P 500 Technical Snapshot",
        "",
        table_row(["Metric", "Value"]),
        table_row(["---", "---:"]),
        table_row(["Current level", fmt_num(spx_price)]),
        table_row(["5-day average", fmt_num(ma5)]),
        table_row(["20-day average", fmt_num(ma20)]),
        table_row(["20-day support", fmt_num(support)]),
        table_row(["20-day resistance", fmt_num(resistance)]),
        table_row(["Trend", trend]),
        "",
        "## Market Drivers From Headlines",
        "",
    ]

    if news:
        for item in news[:5]:
            title = str(item.get("title") or item.get("headline") or "").strip()
            publisher = str(item.get("site") or item.get("publisher") or "").strip()
            if title:
                suffix = f" ({publisher})" if publisher else ""
                lines.append(f"- {title}{suffix}")
    else:
        lines.append("- No headlines available; possible drivers could not be inferred.")

    lines.extend(
        [
            "",
            "## Earnings Calendar - Next 7 Days",
            "",
        ]
    )
    if earnings:
        lines.extend(
            [
                table_row(["Date", "Symbol", "EPS Estimate", "Revenue Estimate"]),
                table_row(["---", "---", "---:", "---:"]),
            ]
        )
        for row in earnings:
            lines.append(
                table_row(
                    [
                        str(row.get("date", "n/a")),
                        str(row.get("symbol", "n/a")).upper(),
                        fmt_num(row.get("epsEstimated")),
                        fmt_num(row.get("revenueEstimated"), 0),
                    ]
                )
            )
    else:
        lines.append("No earnings calendar entries returned for the next 7 days.")

    lines.extend(
        [
            "",
            "## Commentary",
            "",
            (
                f"Major indices are trading {direction}, with the S&P 500 at {fmt_num(spx_price)} "
                f"and the Nasdaq at {fmt_num(price_value(nasdaq))}. "
                f"The S&P 500 technical read is {trend.lower()} based on its 5-day and 20-day averages."
            ),
            (
                f"Volatility is {vix_context} with VIX at {fmt_num(vix_level)}. "
                f"Sector rotation is led by {sector_name(best_sector)} while {sector_name(worst_sector)} is lagging."
            ),
            "",
            "## Delivery Metadata",
            "",
            f"- Generated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            f"- Report date: {report_date.isoformat()}",
        ]
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"daily-market-recap-{report_date.isoformat()}.md"
    summary_path = output_dir / f"daily-market-recap-summary-{report_date.isoformat()}.txt"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    summary_path.write_text(summary + "\n", encoding="utf-8")

    return RecapResult(
        report_path=report_path,
        summary_path=summary_path,
        summary=summary,
        sent_to_telegram=False,
    )


def telegram_api_url(token: str, method: str) -> str:
    return f"https://api.telegram.org/bot{token}/{method}"


def sanitize_markdown(text: str) -> str:
    """Escape characters for Telegram MarkdownV2."""
    return re.sub(r"([_*\[\]()~`>#+\-=|{}.!])", r"\\\1", text)


def send_telegram(token: str, chat_id: str, summary: str, report_path: Path) -> None:
    message = f"*Altamira Daily Market Recap*\n\n{sanitize_markdown(summary)}"
    try:
        message_response = requests.post(
            telegram_api_url(token, "sendMessage"),
            data={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "MarkdownV2",
                "disable_web_page_preview": "true",
            },
            timeout=20,
        )
        message_response.raise_for_status()
        with report_path.open("rb") as handle:
            document_response = requests.post(
                telegram_api_url(token, "sendDocument"),
                data={"chat_id": chat_id, "caption": "Daily market recap markdown report"},
                files={"document": (report_path.name, handle, "text/markdown")},
                timeout=30,
            )
        document_response.raise_for_status()
    except requests.RequestException as exc:
        detail = ""
        response = getattr(exc, "response", None)
        if response is not None:
            detail = f" Response: {response.text[:500]}"
        raise DataIssue(f"Telegram delivery failed: {exc}.{detail}") from exc


def resolve_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate and send a daily market recap.")
    parser.add_argument("--date", default=None, help="Report date in YYYY-MM-DD format. Defaults to today.")
    parser.add_argument("--out-dir", default=str(OUTPUTS), help="Output directory for markdown and summary files.")
    parser.add_argument("--fmp-api-key", default=os.environ.get("FMP_API_KEY") or os.environ.get("FINANCIALMODELINGPREP_API_KEY"))
    parser.add_argument("--telegram-bot-token", default=os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN"))
    parser.add_argument("--telegram-chat-id", default=os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("TELEGRAM_CHANNEL_ID"))
    parser.add_argument("--send-telegram", action="store_true", help="Send the summary and markdown report to Telegram.")
    return parser.parse_args()


def main() -> int:
    args = resolve_args()
    if not args.fmp_api_key:
        print("FMP API key missing. Set FMP_API_KEY or pass --fmp-api-key.", file=sys.stderr)
        return 2

    try:
        report_date = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else date.today()
    except ValueError:
        print("--date must be in YYYY-MM-DD format.", file=sys.stderr)
        return 2

    try:
        result = build_report(args.fmp_api_key, report_date, Path(args.out_dir))
        sent = False
        if args.send_telegram:
            if not args.telegram_bot_token:
                raise DataIssue("Telegram bot token missing. Set TELEGRAM_BOT_TOKEN or pass --telegram-bot-token.")
            if not args.telegram_chat_id:
                raise DataIssue("Telegram chat ID missing. Set TELEGRAM_CHAT_ID/TELEGRAM_CHANNEL_ID or pass --telegram-chat-id.")
            send_telegram(args.telegram_bot_token, args.telegram_chat_id, result.summary, result.report_path)
            sent = True

        print(result.summary)
        print(f"Report path: {result.report_path}")
        print(f"Summary path: {result.summary_path}")
        print(f"Telegram sent: {'yes' if sent else 'no'}")
        return 0
    except DataIssue as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
