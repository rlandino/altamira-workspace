#!/usr/bin/env python3
"""Generate and optionally send a daily market recap to Telegram."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python 3.8 fallback
    ZoneInfo = None


DEFAULT_FMP_KEY = "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz"
FMP_V3 = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"
TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"

INDEX_NAMES = {
    "^GSPC": "S&P 500",
    "^DJI": "Dow Jones",
    "^IXIC": "Nasdaq Composite",
    "^VIX": "VIX",
    "SPY": "SPY",
    "QQQ": "QQQ",
}

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
    """Raised for unrecoverable recap failures."""


def today_et() -> date:
    if ZoneInfo is None:
        return date.today()
    return datetime.now(ZoneInfo("America/New_York")).date()


def request_json(url: str, timeout: int = 25) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "AltamiraDailyRecap/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            payload = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RecapError(f"HTTP {exc.code} for {sanitize_url(url)}: {body[:200]}") from exc
    except urllib.error.URLError as exc:
        raise RecapError(f"Request failed for {sanitize_url(url)}: {exc.reason}") from exc

    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RecapError(f"Invalid JSON from {sanitize_url(url)}") from exc


def sanitize_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    redacted = [(key, "[REDACTED]" if key.lower() == "apikey" else value) for key, value in query]
    return urllib.parse.urlunsplit(parsed._replace(query=urllib.parse.urlencode(redacted)))


def with_apikey(url: str, key: str) -> str:
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}{urllib.parse.urlencode({'apikey': key})}"


def parse_percent(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace("%", "").replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def fmt_num(value: Any, decimals: int = 2) -> str:
    if value is None:
        return "n/a"
    try:
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return str(value)


def fmt_pct(value: Any, show_sign: bool = True) -> str:
    pct = parse_percent(value)
    if pct is None:
        return "n/a"
    sign = "+" if show_sign and pct > 0 else ""
    return f"{sign}{pct:.2f}%"


def quote_by_symbol(quotes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(item.get("symbol", "")): item for item in quotes if item.get("symbol")}


def fetch_quotes(key: str, symbols: list[str]) -> dict[str, dict[str, Any]]:
    symbol_path = urllib.parse.quote(",".join(symbols), safe=",")
    url = with_apikey(f"{FMP_V3}/quote/{symbol_path}", key)
    data = request_json(url)
    if not isinstance(data, list):
        raise RecapError("Quote response was not a list")
    return quote_by_symbol(data)


def fetch_sector_performance(key: str, recap_date: date) -> tuple[dict[str, Any] | None, dict[str, Any] | None, str]:
    url = with_apikey(f"{FMP_STABLE}/sector-performance-snapshot?date={recap_date.isoformat()}", key)
    try:
        data = request_json(url)
        rows = data if isinstance(data, list) else data.get("sectorPerformance", []) if isinstance(data, dict) else []
        sectors: list[dict[str, Any]] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            name = row.get("sector") or row.get("sectorName") or row.get("name")
            pct = parse_percent(row.get("changesPercentage") or row.get("changePercentage") or row.get("performance"))
            if name and pct is not None:
                sectors.append({"name": name, "change": pct})
        if sectors:
            sectors.sort(key=lambda item: item["change"])
            return sectors[-1], sectors[0], "FMP sector snapshot"
    except RecapError:
        pass

    quotes = fetch_quotes(key, list(SECTOR_ETFS))
    sectors = []
    for symbol, name in SECTOR_ETFS.items():
        item = quotes.get(symbol, {})
        pct = parse_percent(item.get("changesPercentage"))
        if pct is not None:
            sectors.append({"name": name, "symbol": symbol, "change": pct})
    if not sectors:
        return None, None, "sector ETF fallback unavailable"
    sectors.sort(key=lambda item: item["change"])
    return sectors[-1], sectors[0], "sector ETF fallback"


def fetch_movers(key: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    def first(endpoint: str) -> dict[str, Any] | None:
        try:
            data = request_json(with_apikey(f"{FMP_STABLE}/{endpoint}", key))
        except RecapError:
            return None
        if isinstance(data, list) and data:
            return data[0]
        return None

    return first("biggest-gainers"), first("biggest-losers")


def fetch_headlines(key: str, limit: int = 5) -> list[dict[str, Any]]:
    try:
        url = with_apikey(f"{FMP_STABLE}/news/general-latest?page=0&limit={limit}", key)
        data = request_json(url)
    except RecapError:
        return []
    return [item for item in data if isinstance(item, dict)][:limit] if isinstance(data, list) else []


def fetch_earnings(key: str, recap_date: date, days: int = 5) -> list[dict[str, Any]]:
    end = recap_date + timedelta(days=days)
    url = with_apikey(f"{FMP_V3}/earning_calendar?from={recap_date.isoformat()}&to={end.isoformat()}", key)
    try:
        data = request_json(url)
    except RecapError:
        return []
    return [item for item in data if isinstance(item, dict)][:12] if isinstance(data, list) else []


def fetch_history(key: str, symbol: str, recap_date: date) -> list[dict[str, Any]]:
    start = recap_date - timedelta(days=45)
    symbol_path = urllib.parse.quote(symbol, safe="")
    url = with_apikey(
        f"{FMP_V3}/historical-price-full/{symbol_path}?from={start.isoformat()}&to={recap_date.isoformat()}",
        key,
    )
    try:
        data = request_json(url)
    except RecapError:
        return []
    rows = data.get("historical", []) if isinstance(data, dict) else data if isinstance(data, list) else []
    return [row for row in rows if isinstance(row, dict)]


def average(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def compute_technicals(history: list[dict[str, Any]], current: float | None) -> dict[str, Any]:
    closes = [float(row["close"]) for row in history if row.get("close") is not None]
    highs = [float(row.get("high", row["close"])) for row in history[:20] if row.get("close") is not None]
    lows = [float(row.get("low", row["close"])) for row in history[:20] if row.get("close") is not None]
    close_desc = closes[:]
    ma5 = average(close_desc[:5])
    ma20 = average(close_desc[:20])
    support = min(lows) if lows else None
    resistance = max(highs) if highs else None
    trend = "Mixed"
    if current is not None and ma5 is not None and ma20 is not None:
        if current > ma5 and current > ma20:
            trend = "Bullish"
        elif current < ma5 and current < ma20:
            trend = "Bearish"
    return {"ma5": ma5, "ma20": ma20, "support": support, "resistance": resistance, "trend": trend}


def vix_label(vix: float | None) -> str:
    if vix is None:
        return "n/a"
    if vix >= 30:
        return "crisis/elevated"
    if vix > 20:
        return "elevated"
    if vix < 15:
        return "low"
    return "normal"


def generate_recap(key: str, recap_date: date) -> tuple[str, str]:
    symbols = ["^GSPC", "^DJI", "^IXIC", "^VIX", "SPY", "QQQ"]
    quotes = fetch_quotes(key, symbols)
    best_sector, worst_sector, sector_source = fetch_sector_performance(key, recap_date)
    gainer, loser = fetch_movers(key)
    headlines = fetch_headlines(key)
    earnings = fetch_earnings(key, recap_date)

    spx_quote = quotes.get("^GSPC", {})
    spx_price = float(spx_quote["price"]) if spx_quote.get("price") is not None else None
    history = fetch_history(key, "^GSPC", recap_date)
    technicals = compute_technicals(history, spx_price)

    vix_quote = quotes.get("^VIX", {})
    vix_price = float(vix_quote["price"]) if vix_quote.get("price") is not None else None
    vix_context = vix_label(vix_price)
    spx_change = parse_percent(spx_quote.get("changesPercentage"))
    direction = "higher" if spx_change and spx_change > 0 else "lower" if spx_change and spx_change < 0 else "mixed/flat"

    best_sector_text = (
        f"{best_sector['name']} ({fmt_pct(best_sector['change'])})" if best_sector else "n/a"
    )
    worst_sector_text = (
        f"{worst_sector['name']} ({fmt_pct(worst_sector['change'])})" if worst_sector else "n/a"
    )

    lines = [
        f"# Daily Market Recap - {recap_date.isoformat()}",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z') or 'local time'}",
        "",
        "## Executive Summary",
        "",
        (
            f"- Markets are {direction}: S&P 500 {fmt_pct(spx_quote.get('changesPercentage'))}, "
            f"Nasdaq {fmt_pct(quotes.get('^IXIC', {}).get('changesPercentage'))}, "
            f"Dow {fmt_pct(quotes.get('^DJI', {}).get('changesPercentage'))}."
        ),
        f"- VIX is {vix_context} at {fmt_num(vix_price)}.",
        f"- Best sector: {best_sector_text}; worst sector: {worst_sector_text}.",
        f"- S&P 500 trend signal: {technicals['trend']} versus recent moving averages.",
        "",
        "## Market Indices",
        "",
        "| Index | Level | Day Change |",
        "|---|---:|---:|",
    ]
    for symbol in ["^GSPC", "^DJI", "^IXIC"]:
        item = quotes.get(symbol, {})
        lines.append(
            f"| {INDEX_NAMES[symbol]} | {fmt_num(item.get('price'))} | {fmt_pct(item.get('changesPercentage'))} |"
        )

    lines.extend(
        [
            "",
            "## ETFs and Volatility",
            "",
            "| Instrument | Level | Day Change |",
            "|---|---:|---:|",
        ]
    )
    for symbol in ["SPY", "QQQ", "^VIX"]:
        item = quotes.get(symbol, {})
        lines.append(
            f"| {INDEX_NAMES[symbol]} | {fmt_num(item.get('price'))} | {fmt_pct(item.get('changesPercentage'))} |"
        )

    lines.extend(
        [
            "",
            "## Leadership and Laggards",
            "",
            f"- Hot stock: {format_mover(gainer)}",
            f"- Biggest loser: {format_mover(loser)}",
            f"- Best sector: {best_sector_text}",
            f"- Worst sector: {worst_sector_text}",
            f"- Sector source: {sector_source}",
            "",
            "## S&P 500 Technical Context",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| Current | {fmt_num(spx_price)} |",
            f"| 5-day average | {fmt_num(technicals['ma5'])} |",
            f"| 20-day average | {fmt_num(technicals['ma20'])} |",
            f"| 20-day resistance | {fmt_num(technicals['resistance'])} |",
            f"| 20-day support | {fmt_num(technicals['support'])} |",
            f"| Trend | {technicals['trend']} |",
            "",
            "## Market Drivers from Headlines",
            "",
        ]
    )
    if headlines:
        for headline in headlines:
            title = headline.get("title") or headline.get("headline") or "Untitled headline"
            source = headline.get("site") or headline.get("publisher") or headline.get("source") or "source n/a"
            lines.append(f"- {title} ({source})")
    else:
        lines.append("- No headlines available from FMP; causal drivers were not inferred.")

    lines.extend(
        [
            "",
            "## Earnings Calendar",
            "",
            "| Date | Symbol | EPS Estimate | Revenue Estimate |",
            "|---|---:|---:|---:|",
        ]
    )
    if earnings:
        for item in earnings:
            lines.append(
                "| {date} | {symbol} | {eps} | {revenue} |".format(
                    date=item.get("date", "n/a"),
                    symbol=item.get("symbol", "n/a"),
                    eps=fmt_num(item.get("epsEstimated")),
                    revenue=fmt_num(item.get("revenueEstimated"), 0),
                )
            )
    else:
        lines.append("| n/a | No earnings returned for the next 5 calendar days | n/a | n/a |")

    lines.extend(
        [
            "",
            "## Commentary",
            "",
            (
                f"The S&P 500 is {fmt_pct(spx_quote.get('changesPercentage'))} with a "
                f"{technicals['trend'].lower()} short-term trend signal. Volatility is {vix_context}, "
                f"with VIX at {fmt_num(vix_price)}."
            ),
            (
                f"Sector action shows {best_sector_text} leading and {worst_sector_text} lagging. "
                "Use the headline list above as context rather than a definitive attribution of market moves."
            ),
            "",
            "## Disclaimer",
            "",
            "This recap is for informational purposes only and is not investment advice.",
        ]
    )

    summary = (
        f"Daily market recap {recap_date.isoformat()}: S&P 500 {fmt_pct(spx_quote.get('changesPercentage'))}, "
        f"Nasdaq {fmt_pct(quotes.get('^IXIC', {}).get('changesPercentage'))}, Dow "
        f"{fmt_pct(quotes.get('^DJI', {}).get('changesPercentage'))}. VIX is {vix_context} at "
        f"{fmt_num(vix_price)}. Best sector: {best_sector_text}; worst sector: {worst_sector_text}. "
        f"S&P trend: {technicals['trend']}."
    )

    return "\n".join(lines) + "\n", summary


def format_mover(item: dict[str, Any] | None) -> str:
    if not item:
        return "n/a"
    symbol = item.get("symbol") or item.get("ticker") or "n/a"
    company = item.get("name") or item.get("companyName") or ""
    pct = fmt_pct(item.get("changesPercentage") or item.get("change") or item.get("changes"))
    label = f"{symbol} ({pct})"
    return f"{label} - {company}" if company else label


def telegram_request(token: str, method: str, data: bytes, content_type: str) -> dict[str, Any]:
    url = TELEGRAM_API.format(token=token, method=method)
    req = urllib.request.Request(url, data=data, headers={"Content-Type": content_type})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            payload = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RecapError(f"Telegram {method} failed with HTTP {exc.code}: {body[:300]}") from exc
    except urllib.error.URLError as exc:
        raise RecapError(f"Telegram {method} failed: {exc.reason}") from exc
    result = json.loads(payload)
    if not result.get("ok"):
        raise RecapError(f"Telegram {method} failed: {result}")
    return result


def send_telegram_message(token: str, chat_id: str, text: str) -> None:
    payload = urllib.parse.urlencode({"chat_id": chat_id, "text": text, "disable_web_page_preview": "true"}).encode()
    telegram_request(token, "sendMessage", payload, "application/x-www-form-urlencoded")


def send_telegram_document(token: str, chat_id: str, path: Path, caption: str) -> None:
    boundary = f"----AltamiraBoundary{uuid.uuid4().hex}"
    mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    parts: list[bytes] = []

    def field(name: str, value: str) -> None:
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        parts.append(value.encode())
        parts.append(b"\r\n")

    field("chat_id", chat_id)
    field("caption", caption)
    parts.append(f"--{boundary}\r\n".encode())
    parts.append(
        (
            f'Content-Disposition: form-data; name="document"; filename="{path.name}"\r\n'
            f"Content-Type: {mime_type}\r\n\r\n"
        ).encode()
    )
    parts.append(path.read_bytes())
    parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    telegram_request(token, "sendDocument", b"".join(parts), f"multipart/form-data; boundary={boundary}")


def resolve_chat_id(args: argparse.Namespace) -> str | None:
    return (
        args.telegram_chat_id
        or os.environ.get("TELEGRAM_CHAT_ID")
        or os.environ.get("ALTAMIRA_TELEGRAM_CHAT_ID")
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a daily market recap and send it to Telegram.")
    parser.add_argument("--date", help="Recap date in YYYY-MM-DD format. Defaults to today's US/Eastern date.")
    parser.add_argument("--output-dir", default="outputs", help="Directory for markdown output.")
    parser.add_argument("--fmp-key", default=os.environ.get("FMP_API_KEY", DEFAULT_FMP_KEY), help="FMP API key.")
    parser.add_argument("--send-telegram", action="store_true", help="Send summary and markdown file to Telegram.")
    parser.add_argument("--telegram-token", default=os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN"))
    parser.add_argument("--telegram-chat-id", help="Telegram chat/channel ID. Defaults to TELEGRAM_CHAT_ID.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    recap_date = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else today_et()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    report, summary = generate_recap(args.fmp_key, recap_date)
    output_path = output_dir / f"daily-market-recap-{recap_date.isoformat()}.md"
    output_path.write_text(report, encoding="utf-8")

    print(summary)
    print(f"Report written: {output_path}")

    if args.send_telegram:
        token = args.telegram_token
        chat_id = resolve_chat_id(args)
        if not token:
            raise RecapError("TELEGRAM_BOT_TOKEN is required when --send-telegram is used")
        if not chat_id:
            raise RecapError("TELEGRAM_CHAT_ID or --telegram-chat-id is required when --send-telegram is used")
        send_telegram_message(token, chat_id, summary)
        send_telegram_document(token, chat_id, output_path, f"Daily market recap - {recap_date.isoformat()}")
        print("Telegram summary and markdown file sent.")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RecapError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
