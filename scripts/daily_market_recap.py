#!/usr/bin/env python3
"""Generate a daily market recap and optionally deliver it to Telegram."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib import parse, request

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python 3.8 fallback.
    ZoneInfo = None  # type: ignore[assignment]


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS = WORKSPACE / "outputs"
FMP_V3 = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"
DEFAULT_FMP_KEY = "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz"
DEFAULT_TELEGRAM_CHAT_ID = "7830722515"


@dataclass(frozen=True)
class Quote:
    """Small quote model for market recap fields."""

    symbol: str
    name: str
    price: float | None
    change_percent: float | None


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a daily market recap and send it to Telegram."
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Report date in YYYY-MM-DD format. Defaults to today's New York date.",
    )
    parser.add_argument(
        "--out-dir",
        default=str(OUTPUTS),
        help="Directory for the markdown output file.",
    )
    parser.add_argument(
        "--chat-id",
        default=None,
        help="Telegram chat/channel ID. Defaults to TELEGRAM_CHAT_ID or workspace fallback.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate the recap but do not send Telegram messages.",
    )
    return parser.parse_args()


def today_new_york() -> date:
    """Return today's date in America/New_York when zoneinfo is available."""
    if ZoneInfo is None:
        return date.today()
    return datetime.now(ZoneInfo("America/New_York")).date()


def get_json(url: str, params: dict[str, Any], timeout: int = 20) -> Any:
    """Fetch JSON from a URL with query params."""
    query = parse.urlencode(params)
    full_url = f"{url}?{query}"
    req = request.Request(full_url, headers={"User-Agent": "altamira-daily-recap/1.0"})
    with request.urlopen(req, timeout=timeout) as response:
        body = response.read().decode("utf-8")
    return json.loads(body)


def warn(message: str) -> None:
    """Print a non-fatal warning to stderr."""
    print(f"WARNING: {message}", file=sys.stderr)


def post_multipart(
    url: str,
    fields: dict[str, str],
    files: dict[str, tuple[str, bytes, str]],
    timeout: int = 30,
) -> Any:
    """Post multipart/form-data using the standard library."""
    boundary = "----AltamiraDailyRecapBoundary"
    parts: list[bytes] = []

    for name, value in fields.items():
        parts.append(f"--{boundary}\r\n".encode("utf-8"))
        parts.append(
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8")
        )
        parts.append(value.encode("utf-8"))
        parts.append(b"\r\n")

    for name, (filename, content, content_type) in files.items():
        parts.append(f"--{boundary}\r\n".encode("utf-8"))
        disposition = (
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
        )
        parts.append(disposition.encode("utf-8"))
        parts.append(f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"))
        parts.append(content)
        parts.append(b"\r\n")

    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    payload = b"".join(parts)
    req = request.Request(
        url,
        data=payload,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with request.urlopen(req, timeout=timeout) as response:
        body = response.read().decode("utf-8")
    return json.loads(body)


def as_float(value: Any) -> float | None:
    """Convert common API number formats into a float."""
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace("%", "").replace(",", "").strip()
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def format_number(value: float | None, digits: int = 2) -> str:
    """Format a float or return N/A."""
    if value is None:
        return "N/A"
    return f"{value:,.{digits}f}"


def format_percent(value: float | None) -> str:
    """Format a percent value with sign."""
    if value is None:
        return "N/A"
    return f"{value:+.2f}%"


def quote_from_item(item: dict[str, Any], names: dict[str, str]) -> Quote:
    """Build a Quote from FMP quote response data."""
    symbol = str(item.get("symbol", ""))
    price = as_float(item.get("price") or item.get("previousClose"))
    change_percent = as_float(
        item.get("changesPercentage")
        or item.get("changePercentage")
        or item.get("changePercent")
    )
    return Quote(
        symbol=symbol,
        name=names.get(symbol, symbol),
        price=price,
        change_percent=change_percent,
    )


def fetch_quotes(api_key: str) -> dict[str, Quote]:
    """Fetch index, VIX, and ETF quotes."""
    symbols = "^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ"
    try:
        data = get_json(f"{FMP_V3}/quote/{symbols}", {"apikey": api_key})
    except Exception as exc:
        warn(f"quote fetch failed: {exc}")
        return {}
    names = {
        "^GSPC": "S&P 500",
        "^DJI": "Dow Jones",
        "^IXIC": "Nasdaq Composite",
        "^VIX": "VIX",
        "SPY": "SPY",
        "QQQ": "QQQ",
    }
    if not isinstance(data, list):
        return {}
    return {str(item.get("symbol")): quote_from_item(item, names) for item in data}


def fetch_first_list_item(url: str, api_key: str) -> dict[str, Any] | None:
    """Fetch a list endpoint and return the first object when available."""
    try:
        data = get_json(url, {"apikey": api_key})
    except Exception as exc:
        warn(f"{url} fetch failed: {exc}")
        return None
    if isinstance(data, list) and data and isinstance(data[0], dict):
        return data[0]
    return None


def mover_label(item: dict[str, Any] | None) -> str:
    """Format a market mover label."""
    if not item:
        return "N/A"
    symbol = item.get("symbol") or item.get("ticker") or item.get("name") or "N/A"
    change = as_float(
        item.get("changesPercentage")
        or item.get("changePercentage")
        or item.get("change")
        or item.get("changes")
    )
    return f"{symbol} ({format_percent(change)})"


def sector_name(item: dict[str, Any]) -> str:
    """Extract a sector name from possible FMP response shapes."""
    for key in ("sector", "sectorName", "name"):
        value = item.get(key)
        if value:
            return str(value)
    return "Unknown"


def sector_change(item: dict[str, Any]) -> float | None:
    """Extract sector performance from possible FMP response shapes."""
    for key in (
        "changesPercentage",
        "changePercentage",
        "averageChange",
        "performance",
        "change",
        "changes",
    ):
        value = as_float(item.get(key))
        if value is not None:
            return value
    return None


def fetch_sector_snapshot(report_date: str, api_key: str) -> tuple[str, str]:
    """Fetch best and worst sector labels for the report date."""
    for offset in range(0, 5):
        candidate = (
            datetime.strptime(report_date, "%Y-%m-%d").date() - timedelta(days=offset)
        ).isoformat()
        try:
            data = get_json(
                f"{FMP_STABLE}/sector-performance-snapshot",
                {"date": candidate, "apikey": api_key},
            )
        except Exception as exc:
            warn(f"sector snapshot fetch failed for {candidate}: {exc}")
            continue
        if not isinstance(data, list) or not data:
            continue
        sectors = [
            (sector_name(item), sector_change(item))
            for item in data
            if isinstance(item, dict) and sector_change(item) is not None
        ]
        if not sectors:
            continue
        best = max(sectors, key=lambda row: row[1] if row[1] is not None else -999)
        worst = min(sectors, key=lambda row: row[1] if row[1] is not None else 999)
        suffix = "" if candidate == report_date else f" ({candidate})"
        return (
            f"{best[0]} ({format_percent(best[1])}){suffix}",
            f"{worst[0]} ({format_percent(worst[1])}){suffix}",
        )
    return "N/A", "N/A"


def fetch_history(symbol: str, report_date: str, api_key: str) -> list[dict[str, Any]]:
    """Fetch recent daily history for an index."""
    to_date = datetime.strptime(report_date, "%Y-%m-%d").date()
    from_date = to_date - timedelta(days=45)
    try:
        data = get_json(
            f"{FMP_STABLE}/historical-price-eod/light",
            {
                "symbol": symbol,
                "from": from_date.isoformat(),
                "to": to_date.isoformat(),
                "apikey": api_key,
            },
        )
    except Exception as exc:
        warn(f"history fetch failed for {symbol}: {exc}")
        return []
    if not isinstance(data, list):
        return []
    rows = [row for row in data if isinstance(row, dict) and row.get("date")]
    return sorted(rows, key=lambda row: str(row.get("date")))


def moving_average(values: list[float], count: int) -> float | None:
    """Return a simple moving average for the last count observations."""
    if len(values) < count:
        return None
    return sum(values[-count:]) / count


def derive_index_context(
    quote: Quote | None, history: list[dict[str, Any]]
) -> dict[str, Any]:
    """Compute moving averages, support, resistance, and trend."""
    closes = [as_float(row.get("close") or row.get("price")) for row in history]
    closes = [value for value in closes if value is not None]
    highs = [as_float(row.get("high")) for row in history[-20:]]
    lows = [as_float(row.get("low")) for row in history[-20:]]
    highs = [value for value in highs if value is not None]
    lows = [value for value in lows if value is not None]
    recent = closes[-20:]
    price = quote.price if quote else None
    avg_5 = moving_average(closes, 5)
    avg_20 = moving_average(closes, 20)
    resistance = max(highs) if highs else (max(recent) if recent else None)
    support = min(lows) if lows else (min(recent) if recent else None)

    if price is not None and avg_5 is not None and avg_20 is not None:
        if price > avg_5 and price > avg_20:
            trend = "Bullish"
        elif price < avg_5 and price < avg_20:
            trend = "Bearish"
        else:
            trend = "Mixed"
    else:
        trend = "N/A"

    return {
        "avg_5": avg_5,
        "avg_20": avg_20,
        "support": support,
        "resistance": resistance,
        "trend": trend,
    }


def vix_label(vix: Quote | None) -> str:
    """Map VIX level to a plain-language regime."""
    if vix is None or vix.price is None:
        return "N/A"
    if vix.price > 25:
        return "elevated"
    if vix.price > 20:
        return "above normal"
    if vix.price < 15:
        return "low"
    return "normal"


def fetch_earnings(report_date: str, api_key: str) -> list[dict[str, Any]]:
    """Fetch upcoming earnings for the next seven days."""
    start = datetime.strptime(report_date, "%Y-%m-%d").date()
    end = start + timedelta(days=7)
    try:
        data = get_json(
            f"{FMP_V3}/earning_calendar",
            {"from": start.isoformat(), "to": end.isoformat(), "apikey": api_key},
        )
    except Exception as exc:
        warn(f"earnings calendar fetch failed: {exc}")
        return []
    if not isinstance(data, list):
        return []
    rows = sorted(
        [row for row in data if isinstance(row, dict)],
        key=lambda row: (str(row.get("date", "")), str(row.get("symbol", ""))),
    )
    us_style_rows = [
        row
        for row in rows
        if is_relevant_earnings_row(row)
    ]
    return (us_style_rows or rows)[:15]


def is_relevant_earnings_row(row: dict[str, Any]) -> bool:
    """Return True for a cleaner US-market earnings calendar row."""
    symbol = str(row.get("symbol", ""))
    has_schedule_detail = bool(
        row.get("time") or row.get("epsEstimated") or row.get("revenueEstimated")
    )
    return has_schedule_detail and is_us_style_symbol(symbol)


def is_us_style_symbol(symbol: str) -> bool:
    """Return True for common US ticker formats and False for dotted global symbols."""
    if not symbol or "." in symbol or any(char.isdigit() for char in symbol):
        return False
    if len(symbol) == 5 and symbol[-1] in {"F", "Y"}:
        return False
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ-")
    return len(symbol) <= 7 and all(char in allowed for char in symbol)


def earnings_table(rows: list[dict[str, Any]]) -> str:
    """Render an earnings markdown table."""
    if not rows:
        return "No earnings returned for the next 7 days."
    lines = [
        "| Date | Symbol | EPS estimate | Revenue estimate |",
        "|---|---:|---:|---:|",
    ]
    for row in rows:
        eps = as_float(row.get("epsEstimated"))
        revenue = as_float(row.get("revenueEstimated"))
        lines.append(
            "| {date} | {symbol} | {eps} | {revenue} |".format(
                date=row.get("date", "N/A"),
                symbol=row.get("symbol", "N/A"),
                eps=format_number(eps) if eps is not None else "N/A",
                revenue=format_number(revenue, 0) if revenue is not None else "N/A",
            )
        )
    return "\n".join(lines)


def quote_line(quote: Quote | None) -> str:
    """Render a markdown bullet for one quote."""
    if quote is None:
        return "- N/A"
    return f"- **{quote.name}:** {format_number(quote.price)} ({format_percent(quote.change_percent)})"


def build_commentary(
    spx: Quote | None,
    nasdaq: Quote | None,
    dow: Quote | None,
    best_sector: str,
    worst_sector: str,
    trend: str,
    vix: Quote | None,
) -> str:
    """Build concise price-action commentary without inventing news."""
    index_changes = [
        quote.change_percent
        for quote in (spx, nasdaq, dow)
        if quote and quote.change_percent is not None
    ]
    if index_changes and all(change >= 0 for change in index_changes):
        direction = "higher"
    elif index_changes and all(change <= 0 for change in index_changes):
        direction = "lower"
    else:
        direction = "mixed"
    return (
        f"Major U.S. indices are trading {direction} on the latest quote snapshot. "
        f"The S&P 500 trend signal is {trend}, with VIX {vix_label(vix)} at {format_number(vix.price if vix else None)}. "
        f"Sector breadth is led by {best_sector}, while {worst_sector} is lagging."
    )


def build_report(
    report_date: str,
    fetched_at: str,
    quotes: dict[str, Quote],
    hot_stock: str,
    biggest_loser: str,
    best_sector: str,
    worst_sector: str,
    context: dict[str, Any],
    earnings: list[dict[str, Any]],
) -> tuple[str, str]:
    """Build the markdown report and Telegram summary."""
    spx = quotes.get("^GSPC")
    dow = quotes.get("^DJI")
    nasdaq = quotes.get("^IXIC")
    vix = quotes.get("^VIX")
    spy = quotes.get("SPY")
    qqq = quotes.get("QQQ")
    trend = str(context.get("trend", "N/A"))
    commentary = build_commentary(spx, nasdaq, dow, best_sector, worst_sector, trend, vix)

    md = f"""# Daily Market Recap - {report_date}

_Generated at {fetched_at}._

## Market indices

{quote_line(spx)}
{quote_line(nasdaq)}
{quote_line(dow)}

## Market movers

- **Hot stock:** {hot_stock}
- **Biggest loser:** {biggest_loser}

## Sector performance

- **Best sector:** {best_sector}
- **Worst sector:** {worst_sector}

## ETFs and volatility

{quote_line(spy)}
{quote_line(qqq)}
- **VIX:** {format_number(vix.price if vix else None)} ({format_percent(vix.change_percent if vix else None)}) - {vix_label(vix)}

## Economic calendar: upcoming earnings

{earnings_table(earnings)}

## S&P 500 levels vs averages

- **Current level:** {format_number(spx.price if spx else None)}
- **5-day average:** {format_number(context.get("avg_5"))}
- **20-day average:** {format_number(context.get("avg_20"))}

## Resistance / support

- **Resistance:** {format_number(context.get("resistance"))}
- **Support:** {format_number(context.get("support"))}
- Derived from the recent 20-trading-day price range when available.

## Trend

**{trend}**

## Commentary

{commentary}

---

_Financial market recap for informational purposes only. This is not investment advice._
"""

    summary = (
        f"Daily Market Recap - {report_date}\n"
        f"S&P 500 {format_number(spx.price if spx else None)} ({format_percent(spx.change_percent if spx else None)}), "
        f"Nasdaq {format_number(nasdaq.price if nasdaq else None)} ({format_percent(nasdaq.change_percent if nasdaq else None)}), "
        f"Dow {format_number(dow.price if dow else None)} ({format_percent(dow.change_percent if dow else None)}).\n"
        f"Trend: {trend}; VIX {format_number(vix.price if vix else None)} ({vix_label(vix)}).\n"
        f"Best sector: {best_sector}; worst sector: {worst_sector}.\n"
        f"Hot stock: {hot_stock}; biggest loser: {biggest_loser}."
    )
    return md, summary


def send_telegram_message(token: str, chat_id: str, text: str) -> Any:
    """Send a plain text Telegram message."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = parse.urlencode({"chat_id": chat_id, "text": text}).encode("utf-8")
    req = request.Request(url, data=data, method="POST")
    with request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def send_telegram_document(token: str, chat_id: str, path: Path, caption: str) -> Any:
    """Send a markdown file to Telegram as a document."""
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    return post_multipart(
        url,
        {"chat_id": chat_id, "caption": caption},
        {"document": (path.name, path.read_bytes(), "text/markdown")},
    )


def main() -> int:
    """Run the daily market recap workflow."""
    args = parse_args()
    report_date = args.date or today_new_york().isoformat()
    try:
        datetime.strptime(report_date, "%Y-%m-%d")
    except ValueError:
        print("ERROR: --date must use YYYY-MM-DD format.", file=sys.stderr)
        return 2

    api_key = os.environ.get("FMP_API_KEY", DEFAULT_FMP_KEY)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / f"daily-market-recap-{report_date}.md"

    fetched_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    quotes = fetch_quotes(api_key)
    hot_stock = mover_label(fetch_first_list_item(f"{FMP_STABLE}/biggest-gainers", api_key))
    biggest_loser = mover_label(fetch_first_list_item(f"{FMP_STABLE}/biggest-losers", api_key))
    best_sector, worst_sector = fetch_sector_snapshot(report_date, api_key)
    history = fetch_history("^GSPC", report_date, api_key)
    context = derive_index_context(quotes.get("^GSPC"), history)
    earnings = fetch_earnings(report_date, api_key)

    markdown, summary = build_report(
        report_date,
        fetched_at,
        quotes,
        hot_stock,
        biggest_loser,
        best_sector,
        worst_sector,
        context,
        earnings,
    )
    output_path.write_text(markdown, encoding="utf-8")

    print(summary)
    print(f"Report path: {output_path}")

    if args.dry_run:
        print("Dry run: Telegram delivery skipped.")
        return 0

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = args.chat_id or os.environ.get("TELEGRAM_CHAT_ID") or DEFAULT_TELEGRAM_CHAT_ID
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN is required for Telegram delivery.", file=sys.stderr)
        return 1

    send_telegram_message(token, chat_id, summary)
    send_telegram_document(
        token,
        chat_id,
        output_path,
        f"Daily market recap markdown - {report_date}",
    )
    print(f"Telegram delivery complete for chat/channel {chat_id}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
