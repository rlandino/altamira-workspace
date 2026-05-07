#!/usr/bin/env python3
"""Generate a daily market recap and optionally deliver it to Telegram."""

import argparse
import json
import os
import importlib.util
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python < 3.9 fallback
    ZoneInfo = None  # type: ignore[assignment]


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS = WORKSPACE / "outputs"
FMP_V3 = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"
INDEX_SYMBOLS = ["^GSPC", "^DJI", "^IXIC", "^VIX", "SPY", "QQQ"]
INDEX_LABELS = {
    "^GSPC": "S&P 500",
    "^DJI": "Dow Jones",
    "^IXIC": "Nasdaq Composite",
    "^VIX": "VIX",
    "SPY": "SPY",
    "QQQ": "QQQ",
}


class RecapError(RuntimeError):
    """Raised when the recap cannot be generated or delivered."""


def market_date() -> str:
    """Return today's date in the New York market timezone."""
    if ZoneInfo is not None:
        return datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d")
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def fetch_json(base_url: str, path: str, params: dict[str, Any], timeout: int = 20) -> Any:
    """Fetch JSON from an HTTP API with a simple User-Agent."""
    query = urllib.parse.urlencode(params)
    url = f"{base_url}{path}?{query}"
    request = urllib.request.Request(url, headers={"User-Agent": "AltamiraDailyMarketRecap/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def parse_float(value: Any) -> float | None:
    """Parse numeric API fields that may arrive as strings or percentages."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace("%", "").replace(",", "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def first_present(row: dict[str, Any], keys: list[str]) -> Any:
    """Return the first non-empty field from a response row."""
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return None


def format_price(value: float | None) -> str:
    """Format market levels for markdown output."""
    if value is None:
        return "n/a"
    return f"{value:,.2f}"


def format_pct(value: float | None) -> str:
    """Format a percentage value with a sign."""
    if value is None:
        return "n/a"
    return f"{value:+.2f}%"


def format_number(value: Any) -> str:
    """Format large estimates while preserving missing values."""
    parsed = parse_float(value)
    if parsed is None:
        return "n/a"
    if abs(parsed) >= 1_000_000_000:
        return f"${parsed / 1_000_000_000:.1f}B"
    if abs(parsed) >= 1_000_000:
        return f"${parsed / 1_000_000:.1f}M"
    return f"{parsed:,.2f}"


def change_phrase(value: float | None) -> str:
    """Return a short direction phrase for a percent move."""
    if value is None:
        return "flat"
    if value > 0.05:
        return "up"
    if value < -0.05:
        return "down"
    return "flat"


def vix_label(value: float | None) -> str:
    """Classify VIX level for the recap."""
    if value is None:
        return "unavailable"
    if value >= 30:
        return "crisis"
    if value >= 20:
        return "elevated"
    if value < 15:
        return "low"
    return "normal"


def row_change(row: dict[str, Any]) -> float | None:
    """Extract change percentage from a quote-like response row."""
    return parse_float(first_present(row, ["changesPercentage", "changePercentage", "changePercent"]))


def normalize_quote_rows(rows: Any) -> dict[str, dict[str, Any]]:
    """Return quotes keyed by symbol."""
    if not isinstance(rows, list):
        return {}
    return {
        row.get("symbol"): row
        for row in rows
        if isinstance(row, dict) and row.get("symbol")
    }


def fetch_quotes(api_key: str) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Fetch index and ETF quotes."""
    warnings: list[str] = []
    try:
        data = fetch_json(FMP_V3, f"/quote/{','.join(INDEX_SYMBOLS)}", {"apikey": api_key})
        return normalize_quote_rows(data), warnings
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        warnings.append(f"Quote fetch failed: {exc}")
        return {}, warnings


def fetch_movers(api_key: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[str]]:
    """Fetch biggest gainer and loser."""
    warnings: list[str] = []
    gainer = None
    loser = None
    for path, label in [("/biggest-gainers", "gainer"), ("/biggest-losers", "loser")]:
        try:
            data = fetch_json(FMP_STABLE, path, {"apikey": api_key})
            if isinstance(data, list) and data:
                if label == "gainer":
                    gainer = data[0]
                else:
                    loser = data[0]
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            warnings.append(f"Biggest {label} fetch failed: {exc}")
    return gainer, loser, warnings


def sector_value(row: dict[str, Any]) -> float | None:
    """Extract sector performance from a snapshot row."""
    return parse_float(first_present(row, ["changesPercentage", "changePercentage", "averageChange", "performance", "change"]))


def sector_name(row: dict[str, Any]) -> str:
    """Extract sector name from a snapshot row."""
    value = first_present(row, ["sector", "sectorName", "name"])
    return str(value or "Unknown")


def fetch_sectors(api_key: str, date: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[str]]:
    """Fetch best and worst sectors."""
    warnings: list[str] = []
    rows: list[dict[str, Any]] = []
    for params in [{"date": date, "apikey": api_key}, {"apikey": api_key}]:
        try:
            data = fetch_json(FMP_STABLE, "/sector-performance-snapshot", params)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            warnings.append(f"Sector snapshot fetch failed: {exc}")
            continue
        if isinstance(data, list):
            rows = [row for row in data if isinstance(row, dict) and sector_value(row) is not None]
            if rows:
                break
    if not rows:
        return None, None, warnings
    rows.sort(key=lambda row: sector_value(row) or 0)
    return rows[-1], rows[0], warnings


def fetch_earnings(api_key: str, date: str) -> tuple[list[dict[str, Any]], list[str]]:
    """Fetch earnings for the next week."""
    warnings: list[str] = []
    to_date = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")
    try:
        data = fetch_json(FMP_V3, "/earning_calendar", {"from": date, "to": to_date, "apikey": api_key})
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        warnings.append(f"Earnings calendar fetch failed: {exc}")
        return [], warnings
    if not isinstance(data, list):
        return [], warnings
    rows = []
    for row in data:
        if not isinstance(row, dict) or not row.get("symbol"):
            continue
        symbol = str(row.get("symbol", ""))
        # Keep the recap focused on US-listed tickers and avoid noisy global suffixes.
        if "." in symbol or "-" in symbol or len(symbol) > 5:
            continue
        rows.append(row)
    rows.sort(key=lambda row: (str(row.get("date", "")), str(row.get("symbol", ""))))
    return rows[:20], warnings


def fetch_news(api_key: str) -> tuple[list[dict[str, Any]], list[str]]:
    """Fetch general market headlines."""
    warnings: list[str] = []
    try:
        data = fetch_json(FMP_STABLE, "/news/general-latest", {"page": 0, "limit": 8, "apikey": api_key})
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        warnings.append(f"General news fetch failed: {exc}")
        return [], warnings
    if not isinstance(data, list):
        return [], warnings
    return [row for row in data if isinstance(row, dict)][:8], warnings


def fetch_history(api_key: str, date: str) -> tuple[list[dict[str, Any]], list[str]]:
    """Fetch S&P 500 EOD history for trend and levels."""
    warnings: list[str] = []
    from_date = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=45)).strftime("%Y-%m-%d")
    try:
        data = fetch_json(
            FMP_STABLE,
            "/historical-price-eod/light",
            {"symbol": "^GSPC", "from": from_date, "to": date, "apikey": api_key},
        )
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        warnings.append(f"Historical S&P 500 fetch failed: {exc}")
        return [], warnings
    if isinstance(data, dict):
        data = data.get("historical") or data.get("data") or []
    if not isinstance(data, list):
        return [], warnings
    rows = []
    for row in data:
        if not isinstance(row, dict):
            continue
        price = parse_float(first_present(row, ["close", "price", "adjClose"]))
        if price is not None:
            row["normalizedClose"] = price
            rows.append(row)
    rows.sort(key=lambda row: str(row.get("date", "")))
    return rows, warnings


def moving_average(values: list[float], window: int) -> float | None:
    """Calculate a simple moving average."""
    if len(values) < window:
        return None
    return sum(values[-window:]) / window


def build_technicals(quotes: dict[str, dict[str, Any]], history: list[dict[str, Any]]) -> dict[str, Any]:
    """Build trend, moving average, support, and resistance details."""
    spx_price = parse_float((quotes.get("^GSPC") or {}).get("price"))
    closes = [parse_float(first_present(row, ["normalizedClose", "close", "price", "adjClose"])) for row in history]
    close_values = [value for value in closes if value is not None]
    ma_5 = moving_average(close_values, 5)
    ma_20 = moving_average(close_values, 20)
    last_20 = close_values[-20:]
    support = min(last_20) if last_20 else None
    resistance = max(last_20) if last_20 else None
    if spx_price is not None and ma_5 is not None and ma_20 is not None:
        if spx_price > ma_5 and spx_price > ma_20:
            trend = "Bullish"
        elif spx_price < ma_5 and spx_price < ma_20:
            trend = "Bearish"
        else:
            trend = "Mixed"
    else:
        trend = "Unavailable"
    return {
        "spx_price": spx_price,
        "ma_5": ma_5,
        "ma_20": ma_20,
        "support": support,
        "resistance": resistance,
        "trend": trend,
    }


def generate_chart(date: str) -> tuple[str | None, str | None]:
    """Generate the existing briefing chart when dependencies are available."""
    script = WORKSPACE / "scripts" / "briefing_chart.py"
    if not script.exists():
        return None, "Chart script not found"
    if importlib.util.find_spec("matplotlib") is None:
        return None, "Chart skipped: matplotlib is not installed"
    result = subprocess.run(
        [sys.executable, str(script), "--date", date],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    chart_path = OUTPUTS / f"briefing-chart-{date}.png"
    if result.returncode == 0 and chart_path.exists():
        return str(chart_path.relative_to(WORKSPACE)), None
    detail = (result.stderr or result.stdout or "unknown chart error").strip()
    return None, f"Chart generation failed: {detail}"


def markdown_table(rows: list[list[str]]) -> str:
    """Render a small markdown table."""
    if not rows:
        return ""
    header = rows[0]
    separator = ["---"] * len(header)
    body = rows[1:]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(separator) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in body)
    return "\n".join(lines)


def market_drivers(news: list[dict[str, Any]]) -> str:
    """Summarize headline context without inventing causality."""
    if not news:
        return "No headlines available; possible drivers could not be inferred."
    bullets = []
    for row in news[:5]:
        title = str(first_present(row, ["title", "headline", "site"]) or "Untitled headline")
        source = str(first_present(row, ["site", "publisher", "source"]) or "source unavailable")
        bullets.append(f"- {title} ({source})")
    return "\n".join(bullets)


def build_summary(
    quotes: dict[str, dict[str, Any]],
    best_sector: dict[str, Any] | None,
    worst_sector: dict[str, Any] | None,
    gainer: dict[str, Any] | None,
    loser: dict[str, Any] | None,
    technicals: dict[str, Any],
    report_path: Path,
) -> str:
    """Build a compact plain-text recap for chat and Telegram."""
    spx = quotes.get("^GSPC", {})
    ndx = quotes.get("^IXIC", {})
    dow = quotes.get("^DJI", {})
    vix = quotes.get("^VIX", {})
    spx_move = row_change(spx)
    ndx_move = row_change(ndx)
    dow_move = row_change(dow)
    vix_price = parse_float(vix.get("price"))
    best = f"{sector_name(best_sector)} {format_pct(sector_value(best_sector))}" if best_sector else "n/a"
    worst = f"{sector_name(worst_sector)} {format_pct(sector_value(worst_sector))}" if worst_sector else "n/a"
    hot = f"{gainer.get('symbol')} {format_pct(row_change(gainer))}" if gainer else "n/a"
    cold = f"{loser.get('symbol')} {format_pct(row_change(loser))}" if loser else "n/a"
    return (
        "Altamira Daily Market Recap\n"
        f"S&P 500 {format_pct(spx_move)}, Nasdaq {format_pct(ndx_move)}, Dow {format_pct(dow_move)}; "
        f"trend {technicals['trend']} with VIX {format_price(vix_price)} ({vix_label(vix_price)}).\n"
        f"Best sector: {best}. Worst sector: {worst}. Hot stock: {hot}. Biggest loser: {cold}.\n"
        f"Markdown report: {report_path.as_posix()}"
    )


def build_report(
    date: str,
    quotes: dict[str, dict[str, Any]],
    gainer: dict[str, Any] | None,
    loser: dict[str, Any] | None,
    best_sector: dict[str, Any] | None,
    worst_sector: dict[str, Any] | None,
    earnings: list[dict[str, Any]],
    news: list[dict[str, Any]],
    technicals: dict[str, Any],
    chart_path: str | None,
    warnings: list[str],
) -> str:
    """Build the markdown market recap."""
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    index_rows = [["Index", "Level", "Day Change"]]
    for symbol in ["^GSPC", "^IXIC", "^DJI", "SPY", "QQQ"]:
        row = quotes.get(symbol, {})
        index_rows.append([
            INDEX_LABELS[symbol],
            format_price(parse_float(row.get("price"))),
            format_pct(row_change(row)),
        ])

    vix_row = quotes.get("^VIX", {})
    vix_price = parse_float(vix_row.get("price"))
    earnings_rows = [["Date", "Ticker", "EPS Est.", "Revenue Est."]]
    for row in earnings[:12]:
        earnings_rows.append([
            str(row.get("date", "n/a"))[:10],
            str(row.get("symbol", "n/a")),
            format_number(row.get("epsEstimated")),
            format_number(row.get("revenueEstimated")),
        ])

    if len(earnings_rows) == 1:
        earnings_table = "No earnings calendar items returned for the next 7 days."
    else:
        earnings_table = markdown_table(earnings_rows)

    warning_block = ""
    if warnings:
        warning_lines = "\n".join(f"- {warning}" for warning in warnings)
        warning_block = f"\n## Data Warnings\n\n{warning_lines}\n"

    chart_block = "Chart not generated."
    if chart_path:
        chart_block = f"![Index performance]({chart_path})"

    return f"""# Daily Market Recap - {date}

Generated: {generated_at}

## Executive Summary

- S&P 500: {format_price(parse_float((quotes.get("^GSPC") or {}).get("price")))} ({format_pct(row_change(quotes.get("^GSPC", {})))})
- Nasdaq Composite: {format_price(parse_float((quotes.get("^IXIC") or {}).get("price")))} ({format_pct(row_change(quotes.get("^IXIC", {})))})
- Dow Jones: {format_price(parse_float((quotes.get("^DJI") or {}).get("price")))} ({format_pct(row_change(quotes.get("^DJI", {})))})
- Trend: {technicals["trend"]}
- VIX: {format_price(vix_price)} ({vix_label(vix_price)})

## Market Indices

{markdown_table(index_rows)}

## Sectors and Movers

- Best sector: {sector_name(best_sector) if best_sector else "n/a"} ({format_pct(sector_value(best_sector)) if best_sector else "n/a"})
- Worst sector: {sector_name(worst_sector) if worst_sector else "n/a"} ({format_pct(sector_value(worst_sector)) if worst_sector else "n/a"})
- Hot stock: {gainer.get("symbol") if gainer else "n/a"} ({format_pct(row_change(gainer)) if gainer else "n/a"})
- Biggest loser: {loser.get("symbol") if loser else "n/a"} ({format_pct(row_change(loser)) if loser else "n/a"})

## Technical Snapshot

- S&P 500 vs 5D average: {format_price(technicals["spx_price"])} vs {format_price(technicals["ma_5"])}
- S&P 500 vs 20D average: {format_price(technicals["spx_price"])} vs {format_price(technicals["ma_20"])}
- 20-day resistance: {format_price(technicals["resistance"])}
- 20-day support: {format_price(technicals["support"])}
- Trend classification: {technicals["trend"]}

## Market Drivers From Headlines

{market_drivers(news)}

## Earnings Calendar - Next 7 Days

{earnings_table}

## Commentary

The major indices are {change_phrase(row_change(quotes.get("^GSPC", {})))} on the S&P 500, {change_phrase(row_change(quotes.get("^IXIC", {})))} on the Nasdaq, and {change_phrase(row_change(quotes.get("^DJI", {})))} on the Dow. Volatility is {vix_label(vix_price)} based on the VIX level. Sector leadership is concentrated in {sector_name(best_sector) if best_sector else "unavailable sector data"}, while {sector_name(worst_sector) if worst_sector else "unavailable sector data"} is lagging.

## Index Performance Chart

{chart_block}
{warning_block}
## Disclaimer

This recap is for informational purposes only and is not investment advice or a recommendation to buy or sell any security.
"""


def telegram_request(bot_token: str, method: str, data: bytes, content_type: str) -> dict[str, Any]:
    """Post a request to the Telegram Bot API."""
    url = f"https://api.telegram.org/bot{bot_token}/{method}"
    request = urllib.request.Request(url, data=data, headers={"Content-Type": content_type})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = response.read().decode("utf-8")
    parsed = json.loads(payload)
    if not parsed.get("ok"):
        raise RecapError(f"Telegram {method} failed: {parsed}")
    return parsed


def send_telegram_message(bot_token: str, chat_id: str, text: str) -> None:
    """Send a plain text Telegram message."""
    body = urllib.parse.urlencode({"chat_id": chat_id, "text": text, "disable_web_page_preview": "true"}).encode()
    telegram_request(bot_token, "sendMessage", body, "application/x-www-form-urlencoded")


def send_telegram_document(bot_token: str, chat_id: str, file_path: Path, caption: str) -> None:
    """Send a markdown file to Telegram using multipart/form-data."""
    boundary = f"----AltamiraBoundary{datetime.now(timezone.utc).timestamp():.0f}"
    parts: list[bytes] = []

    def add_field(name: str, value: str) -> None:
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        parts.append(value.encode("utf-8"))
        parts.append(b"\r\n")

    add_field("chat_id", chat_id)
    add_field("caption", caption[:1024])
    parts.append(f"--{boundary}\r\n".encode())
    parts.append(
        (
            f'Content-Disposition: form-data; name="document"; filename="{file_path.name}"\r\n'
            "Content-Type: text/markdown\r\n\r\n"
        ).encode()
    )
    parts.append(file_path.read_bytes())
    parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    telegram_request(bot_token, "sendDocument", b"".join(parts), f"multipart/form-data; boundary={boundary}")


def resolve_telegram_chat(args: argparse.Namespace) -> str | None:
    """Resolve Telegram chat id from flags or environment."""
    return (
        args.telegram_chat_id
        or os.environ.get("TELEGRAM_CHAT_ID")
        or os.environ.get("TELEGRAM_CHANNEL_ID")
        or os.environ.get("TELEGRAM_CHANNEL")
    )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate and deliver the Altamira daily market recap")
    parser.add_argument("--date", default=market_date(), help="Market date in YYYY-MM-DD (default: today in New York)")
    parser.add_argument("--fmp-api-key", default=os.environ.get("FMP_API_KEY"), help="FMP API key")
    parser.add_argument("--telegram-bot-token", default=os.environ.get("TELEGRAM_BOT_TOKEN"), help="Telegram bot token")
    parser.add_argument("--telegram-chat-id", default=None, help="Telegram chat/channel id")
    parser.add_argument("--outputs-dir", default=str(OUTPUTS), help="Directory for generated recap files")
    parser.add_argument("--skip-chart", action="store_true", help="Skip chart generation")
    parser.add_argument("--no-telegram", action="store_true", help="Write files only; do not send Telegram messages")
    return parser.parse_args()


def main() -> int:
    """Run the daily recap workflow."""
    args = parse_args()
    if not args.fmp_api_key:
        raise RecapError("FMP_API_KEY or --fmp-api-key is required")

    output_dir = Path(args.outputs_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    warnings: list[str] = []

    quotes, quote_warnings = fetch_quotes(args.fmp_api_key)
    gainer, loser, mover_warnings = fetch_movers(args.fmp_api_key)
    best_sector, worst_sector, sector_warnings = fetch_sectors(args.fmp_api_key, args.date)
    earnings, earnings_warnings = fetch_earnings(args.fmp_api_key, args.date)
    news, news_warnings = fetch_news(args.fmp_api_key)
    history, history_warnings = fetch_history(args.fmp_api_key, args.date)
    warnings.extend(quote_warnings + mover_warnings + sector_warnings + earnings_warnings + news_warnings + history_warnings)
    technicals = build_technicals(quotes, history)

    chart_path = None
    if not args.skip_chart:
        chart_path, chart_warning = generate_chart(args.date)
        if chart_warning:
            warnings.append(chart_warning)

    report_text = build_report(
        args.date,
        quotes,
        gainer,
        loser,
        best_sector,
        worst_sector,
        earnings,
        news,
        technicals,
        chart_path,
        warnings,
    )
    report_path = output_dir / f"daily-market-recap-{args.date}.md"
    summary_path = output_dir / f"daily-market-recap-summary-{args.date}.txt"
    report_path.write_text(report_text, encoding="utf-8")
    summary = build_summary(quotes, best_sector, worst_sector, gainer, loser, technicals, report_path.relative_to(WORKSPACE))
    summary_path.write_text(summary + "\n", encoding="utf-8")

    delivered = False
    if not args.no_telegram:
        chat_id = resolve_telegram_chat(args)
        if not args.telegram_bot_token:
            raise RecapError("TELEGRAM_BOT_TOKEN or --telegram-bot-token is required for Telegram delivery")
        if not chat_id:
            raise RecapError("TELEGRAM_CHAT_ID, TELEGRAM_CHANNEL_ID, TELEGRAM_CHANNEL, or --telegram-chat-id is required")
        send_telegram_message(args.telegram_bot_token, chat_id, summary)
        send_telegram_document(args.telegram_bot_token, chat_id, report_path, f"Daily market recap markdown file for {args.date}")
        delivered = True

    print(summary)
    print(f"Report path: {report_path}")
    print(f"Summary path: {summary_path}")
    print(f"Telegram delivered: {'yes' if delivered else 'no'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RecapError as exc:
        print(f"daily_market_recap error: {exc}", file=sys.stderr)
        raise SystemExit(1)
