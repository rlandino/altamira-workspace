#!/usr/bin/env python3
"""Generate and optionally send the Altamira daily market recap.

The script pulls live market data from FMP, writes a markdown recap to outputs/,
and can send both a short summary and the markdown file to Telegram.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import requests


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS = WORKSPACE / "outputs"
FMP_BASE = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"
DEFAULT_FMP_KEY = "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz"
DEFAULT_TELEGRAM_CHAT_ID = "7830722515"
WATCHLIST = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "JPM", "V", "UNH"]


@dataclass
class RecapPaths:
    """Output paths for a recap run."""

    report: Path
    voice: Path
    chart: Path


def request_json(url: str, params: dict[str, Any] | None = None, timeout: int = 20) -> Any:
    """Fetch JSON with a short timeout and useful error context."""
    response = requests.get(url, params=params or {}, timeout=timeout)
    response.raise_for_status()
    return response.json()


def fmp_v3(path: str, params: dict[str, Any] | None = None) -> Any:
    """Fetch from the FMP v3 API."""
    api_key = os.environ.get("FMP_API_KEY", DEFAULT_FMP_KEY)
    request_params = dict(params or {})
    request_params["apikey"] = api_key
    return request_json(f"{FMP_BASE}{path}", request_params)


def fmp_stable(path: str, params: dict[str, Any] | None = None) -> Any:
    """Fetch from the FMP stable API."""
    api_key = os.environ.get("FMP_API_KEY", DEFAULT_FMP_KEY)
    request_params = dict(params or {})
    request_params["apikey"] = api_key
    return request_json(f"{FMP_STABLE}{path}", request_params)


def as_float(value: Any) -> float | None:
    """Coerce numeric API values, including percent strings, to float."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        clean = value.strip().replace("%", "").replace(",", "")
        if not clean:
            return None
        try:
            return float(clean)
        except ValueError:
            return None
    return None


def fmt_number(value: Any, digits: int = 2) -> str:
    """Format a number or return N/A."""
    parsed = as_float(value)
    if parsed is None:
        return "N/A"
    return f"{parsed:,.{digits}f}"


def fmt_percent(value: Any, signed: bool = True) -> str:
    """Format a percentage value from numeric or percent-string API fields."""
    parsed = as_float(value)
    if parsed is None:
        return "N/A"
    sign = "+" if signed else ""
    return f"{parsed:{sign}.2f}%"


def quote_map(rows: Any) -> dict[str, dict[str, Any]]:
    """Index quote rows by symbol."""
    if not isinstance(rows, list):
        return {}
    return {str(row.get("symbol", "")).upper(): row for row in rows if isinstance(row, dict)}


def get_change(row: dict[str, Any] | None) -> float | None:
    """Extract the best available day-change percentage from a quote row."""
    if not row:
        return None
    for key in ("changesPercentage", "changePercentage", "changesPercent", "changes"):
        value = as_float(row.get(key))
        if value is not None:
            return value
    price = as_float(row.get("price"))
    previous = as_float(row.get("previousClose"))
    if price is not None and previous:
        return ((price - previous) / previous) * 100
    return None


def quote_price(row: dict[str, Any] | None) -> float | None:
    """Extract the best available price from a quote row."""
    if not row:
        return None
    for key in ("price", "close", "previousClose"):
        value = as_float(row.get(key))
        if value is not None:
            return value
    return None


def latest_mover(rows: Any) -> dict[str, Any] | None:
    """Return the first valid mover row from an FMP gainers/losers response."""
    if not isinstance(rows, list):
        return None
    for row in rows:
        if isinstance(row, dict) and row.get("symbol"):
            return row
    return None


def parse_sector_rows(data: Any) -> list[tuple[str, float]]:
    """Normalize sector performance responses into (name, percent change)."""
    rows: list[tuple[str, float]] = []
    if isinstance(data, dict):
        iterable = data.get("sectorPerformance") or data.get("sectors") or data.get("data") or []
    else:
        iterable = data
    if isinstance(iterable, dict):
        iterable = [{"sector": key, "changesPercentage": value} for key, value in iterable.items()]
    if not isinstance(iterable, list):
        return rows
    for item in iterable:
        if not isinstance(item, dict):
            continue
        name = (
            item.get("sector")
            or item.get("sectorName")
            or item.get("name")
            or item.get("label")
            or item.get("symbol")
        )
        change = None
        for key in (
            "changesPercentage",
            "changePercentage",
            "averageChange",
            "performance",
            "change",
            "percentChange",
        ):
            change = as_float(item.get(key))
            if change is not None:
                break
        if name and change is not None:
            rows.append((str(name), change))
    return rows


def fetch_sector_snapshot(run_date: date) -> tuple[tuple[str, float] | None, tuple[str, float] | None, str | None]:
    """Fetch best and worst sectors, falling back across recent dates."""
    for offset in range(0, 6):
        query_date = run_date - timedelta(days=offset)
        try:
            data = fmp_stable("/sector-performance-snapshot", {"date": query_date.isoformat()})
            rows = parse_sector_rows(data)
            if rows:
                rows.sort(key=lambda item: item[1])
                return rows[-1], rows[0], query_date.isoformat()
        except Exception:
            continue
    return None, None, None


def fetch_history(symbol: str, run_date: date) -> list[dict[str, Any]]:
    """Fetch recent historical EOD rows for support/resistance and moving averages."""
    start = (run_date - timedelta(days=45)).isoformat()
    end = run_date.isoformat()
    rows = fmp_stable("/historical-price-eod/light", {"symbol": symbol, "from": start, "to": end})
    if not isinstance(rows, list):
        return []
    normalized = []
    for row in rows:
        if not isinstance(row, dict) or not row.get("date"):
            continue
        normalized_row = dict(row)
        if normalized_row.get("close") is None and normalized_row.get("price") is not None:
            normalized_row["close"] = normalized_row["price"]
        normalized.append(normalized_row)
    normalized.sort(key=lambda row: str(row.get("date")))
    return normalized


def moving_average(values: list[float], window: int) -> float | None:
    """Return a simple moving average over the last window observations."""
    if len(values) < window:
        return None
    return sum(values[-window:]) / window


def trend_label(price: float | None, ma5: float | None, ma20: float | None) -> str:
    """Classify index trend using price vs 5D and 20D averages."""
    if price is None or ma5 is None or ma20 is None:
        return "Unknown"
    if price > ma5 and price > ma20:
        return "Bullish"
    if price < ma5 and price < ma20:
        return "Bearish"
    return "Mixed"


def vix_label(vix: float | None) -> str:
    """Map VIX level to a compact risk label."""
    if vix is None:
        return "unknown"
    if vix >= 25:
        return "high"
    if vix > 20:
        return "elevated"
    if vix < 15:
        return "low"
    return "normal"


def direction_label(changes: list[float]) -> str:
    """Return broad market direction from index changes."""
    if not changes:
        return "mixed"
    average = sum(changes) / len(changes)
    if average > 0.15:
        return "higher"
    if average < -0.15:
        return "lower"
    return "mixed"


def earnings_rows(run_date: date) -> list[dict[str, Any]]:
    """Fetch upcoming earnings calendar rows."""
    end = (run_date + timedelta(days=7)).isoformat()
    data = fmp_v3("/earning_calendar", {"from": run_date.isoformat(), "to": end})
    if not isinstance(data, list):
        return []
    seen: set[tuple[str, str]] = set()
    rows: list[dict[str, Any]] = []
    for row in data:
        if not isinstance(row, dict):
            continue
        symbol = str(row.get("symbol", "")).upper()
        if not re.fullmatch(r"[A-Z]{1,5}", symbol):
            continue
        key = (str(row.get("date", ""))[:10], symbol)
        if key in seen:
            continue
        seen.add(key)
        rows.append(row)
    rows.sort(key=lambda row: (str(row.get("date", "")), str(row.get("symbol", ""))))
    return rows[:20]


def market_news(limit: int = 8) -> list[dict[str, Any]]:
    """Fetch broad market headlines for context."""
    try:
        data = fmp_stable("/news/general-latest", {"page": 0, "limit": limit})
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict)][:limit]


def watchlist_movers(quotes: dict[str, dict[str, Any]], threshold: float = 2.0) -> list[tuple[str, float]]:
    """Return watchlist tickers moving more than the threshold."""
    movers: list[tuple[str, float]] = []
    for symbol in WATCHLIST:
        change = get_change(quotes.get(symbol))
        if change is not None and abs(change) >= threshold:
            movers.append((symbol, change))
    movers.sort(key=lambda item: abs(item[1]), reverse=True)
    return movers


def generate_chart(run_date: date) -> Path | None:
    """Run the existing chart helper if available."""
    script = WORKSPACE / "scripts" / "briefing_chart.py"
    if not script.exists():
        return None
    if importlib.util.find_spec("matplotlib") is None:
        print("[daily-market-recap] Chart generation skipped: matplotlib is not installed.", file=sys.stderr)
        return None
    try:
        subprocess.run(
            [sys.executable, str(script), "--date", run_date.isoformat()],
            cwd=WORKSPACE,
            check=True,
            timeout=60,
        )
    except Exception as exc:
        print(f"[daily-market-recap] Chart generation skipped: {exc}", file=sys.stderr)
        return None
    chart = OUTPUTS / f"briefing-chart-{run_date.isoformat()}.png"
    return chart if chart.exists() else None


def build_paths(run_date: date) -> RecapPaths:
    """Build output paths for the recap date."""
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    stamp = run_date.isoformat()
    return RecapPaths(
        report=OUTPUTS / f"daily-market-recap-{stamp}.md",
        voice=OUTPUTS / f"daily-market-recap-summary-{stamp}.txt",
        chart=OUTPUTS / f"briefing-chart-{stamp}.png",
    )


def make_table_row(label: str, row: dict[str, Any] | None) -> str:
    """Create one markdown table row for an index or ETF quote."""
    price = quote_price(row)
    change = get_change(row)
    return f"| {label} | {fmt_number(price)} | {fmt_percent(change)} |"


def build_recap(run_date: date) -> tuple[Path, Path, str]:
    """Generate the markdown recap and return paths plus Telegram summary."""
    paths = build_paths(run_date)
    generated_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")

    symbols = "^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ," + ",".join(WATCHLIST)
    quotes = quote_map(fmp_v3(f"/quote/{symbols}"))
    gainers = latest_mover(fmp_stable("/biggest-gainers"))
    losers = latest_mover(fmp_stable("/biggest-losers"))
    best_sector, worst_sector, sector_date = fetch_sector_snapshot(run_date)
    history = fetch_history("^GSPC", run_date)
    earnings = earnings_rows(run_date)
    headlines = market_news()
    chart = generate_chart(run_date)

    spx = quotes.get("^GSPC")
    nasdaq = quotes.get("^IXIC")
    dow = quotes.get("^DJI")
    vix_quote = quotes.get("^VIX")
    spy = quotes.get("SPY")
    qqq = quotes.get("QQQ")

    closes = [as_float(row.get("close")) for row in history]
    close_values = [value for value in closes if value is not None]
    spx_price = quote_price(spx)
    spx_change = get_change(spx)
    nasdaq_change = get_change(nasdaq)
    dow_change = get_change(dow)
    ma5 = moving_average(close_values, 5)
    ma20 = moving_average(close_values, 20)
    recent_20 = close_values[-20:] if len(close_values) >= 20 else close_values
    support = min(recent_20) if recent_20 else None
    resistance = max(recent_20) if recent_20 else None
    trend = trend_label(spx_price, ma5, ma20)
    vix_level = quote_price(vix_quote)
    vix_state = vix_label(vix_level)
    index_changes = [value for value in (spx_change, nasdaq_change, dow_change) if value is not None]
    direction = direction_label(index_changes)
    movers = watchlist_movers(quotes)

    hot_symbol = gainers.get("symbol") if gainers else "N/A"
    hot_change = fmt_percent(
        gainers.get("changesPercentage") if gainers else None
    )
    weak_symbol = losers.get("symbol") if losers else "N/A"
    weak_change = fmt_percent(
        losers.get("changesPercentage") if losers else None
    )
    best_sector_text = f"{best_sector[0]} ({fmt_percent(best_sector[1])})" if best_sector else "N/A"
    worst_sector_text = f"{worst_sector[0]} ({fmt_percent(worst_sector[1])})" if worst_sector else "N/A"

    headline_lines = []
    for item in headlines[:5]:
        title = item.get("title") or item.get("headline") or item.get("site") or "Untitled"
        publisher = item.get("site") or item.get("publisher") or item.get("source")
        if publisher:
            headline_lines.append(f"- {title} ({publisher})")
        else:
            headline_lines.append(f"- {title}")
    if not headline_lines:
        headline_lines.append("- No broad-market headlines returned by FMP.")

    earnings_lines = [
        "| Date | Symbol | EPS estimate | Revenue estimate |",
        "|------|--------|--------------|------------------|",
    ]
    if earnings:
        for row in earnings:
            earnings_lines.append(
                "| {date} | {symbol} | {eps} | {revenue} |".format(
                    date=str(row.get("date", "N/A"))[:10],
                    symbol=row.get("symbol", "N/A"),
                    eps=fmt_number(row.get("epsEstimated")),
                    revenue=fmt_number(row.get("revenueEstimated"), 0),
                )
            )
    else:
        earnings_lines.append("| N/A | No earnings returned for the next 7 days | N/A | N/A |")

    watchlist_lines = [
        "| Ticker | Day change |",
        "|--------|------------|",
    ]
    if movers:
        for symbol, change in movers[:8]:
            watchlist_lines.append(f"| {symbol} | {fmt_percent(change)} |")
    else:
        watchlist_lines.append("| None | No watchlist move exceeded +/-2% |")

    commentary = (
        f"Markets are trading {direction} across the major indices, with the S&P 500 at "
        f"{fmt_number(spx_price)} ({fmt_percent(spx_change)}) and trend classified as {trend}. "
        f"VIX is {vix_state} at {fmt_number(vix_level)}, which frames the current risk backdrop. "
        f"Sector leadership is led by {best_sector_text}; the weakest group is {worst_sector_text}."
    )

    report = f"""# Daily Market Recap — {run_date.isoformat()}

Generated: {generated_at}

> Educational market commentary only. Not investment advice, a recommendation, or an offer to buy or sell securities.

## Executive Summary

- **Market direction:** Major indices are **{direction}**.
- **S&P 500:** {fmt_number(spx_price)} ({fmt_percent(spx_change)}), trend **{trend}**.
- **VIX:** {fmt_number(vix_level)} ({vix_state}).
- **Best sector:** {best_sector_text}.
- **Worst sector:** {worst_sector_text}.
- **Hot stock:** {hot_symbol} ({hot_change}).
- **Biggest loser:** {weak_symbol} ({weak_change}).

## Market Indices

| Index / ETF | Level | Day change |
|-------------|-------|------------|
{make_table_row("S&P 500", spx)}
{make_table_row("Nasdaq Composite", nasdaq)}
{make_table_row("Dow Jones Industrial Average", dow)}
{make_table_row("SPY", spy)}
{make_table_row("QQQ", qqq)}
{make_table_row("VIX", vix_quote)}

## Sector Snapshot

- **Best sector:** {best_sector_text}
- **Worst sector:** {worst_sector_text}
- **Sector data date:** {sector_date or "N/A"}

## Momentum and Technical Context

- **S&P 500 vs 5D average:** {fmt_number(spx_price)} vs {fmt_number(ma5)}
- **S&P 500 vs 20D average:** {fmt_number(spx_price)} vs {fmt_number(ma20)}
- **20D resistance:** {fmt_number(resistance)}
- **20D support:** {fmt_number(support)}
- **Trend classification:** {trend}

## Watchlist Movers

{chr(10).join(watchlist_lines)}

## Earnings Calendar: Next 7 Days

{chr(10).join(earnings_lines)}

## Broad-Market Headlines

{chr(10).join(headline_lines)}

## Commentary

{commentary}

## Index Performance Chart

{"![Index performance](briefing-chart-" + run_date.isoformat() + ".png)" if chart else "Chart not generated."}

## Files

- Markdown report: `{paths.report}`
- Summary script: `{paths.voice}`
- Chart: `{paths.chart if chart else "N/A"}`
"""

    telegram_summary = (
        f"Daily Market Recap - {run_date.isoformat()}\n"
        f"S&P 500: {fmt_number(spx_price)} ({fmt_percent(spx_change)}), trend {trend}. "
        f"Nasdaq: {fmt_percent(nasdaq_change)}; Dow: {fmt_percent(dow_change)}. "
        f"VIX: {fmt_number(vix_level)} ({vix_state}).\n"
        f"Best sector: {best_sector_text}. Worst sector: {worst_sector_text}. "
        f"Hot stock: {hot_symbol} ({hot_change}); biggest loser: {weak_symbol} ({weak_change})."
    )

    voice = (
        f"Your daily market recap for {run_date.isoformat()}. "
        f"The S&P 500 is at {fmt_number(spx_price)}, {fmt_percent(spx_change)}, "
        f"with a {trend.lower()} trend signal. VIX is {vix_state} at {fmt_number(vix_level)}. "
        f"The leading sector is {best_sector_text}, while the weakest sector is {worst_sector_text}."
    )

    paths.report.write_text(report, encoding="utf-8")
    paths.voice.write_text(voice + "\n", encoding="utf-8")
    return paths.report, paths.voice, telegram_summary


def telegram_chat_id(cli_value: str | None) -> str | None:
    """Resolve Telegram chat ID from CLI or environment."""
    return (
        cli_value
        or os.environ.get("TELEGRAM_CHAT_ID")
        or os.environ.get("TELEGRAM_CHANNEL_ID")
        or os.environ.get("TELEGRAM_DEFAULT_CHAT_ID")
        or DEFAULT_TELEGRAM_CHAT_ID
    )


def send_telegram_message(token: str, chat_id: str, text: str) -> None:
    """Send a plain-text Telegram message."""
    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={"chat_id": chat_id, "text": text, "disable_web_page_preview": "true"},
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        raise RuntimeError(f"Telegram sendMessage failed: {payload}")


def send_telegram_document(token: str, chat_id: str, file_path: Path, caption: str) -> None:
    """Send the recap markdown file to Telegram."""
    with file_path.open("rb") as handle:
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendDocument",
            data={"chat_id": chat_id, "caption": caption},
            files={"document": (file_path.name, handle, "text/markdown")},
            timeout=45,
        )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        raise RuntimeError(f"Telegram sendDocument failed: {payload}")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate and send a daily market recap")
    parser.add_argument("--date", help="Recap date in YYYY-MM-DD format; default is today")
    parser.add_argument("--chat-id", help="Telegram chat/channel ID override")
    parser.add_argument("--no-telegram", action="store_true", help="Generate files without Telegram delivery")
    return parser.parse_args()


def main() -> int:
    """CLI entrypoint."""
    args = parse_args()
    run_date = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else date.today()
    report_path, voice_path, summary = build_recap(run_date)

    print(summary)
    print(f"Report: {report_path}")
    print(f"Voice script: {voice_path}")

    if args.no_telegram:
        print("Telegram delivery skipped by --no-telegram.")
        return 0

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = telegram_chat_id(args.chat_id)
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set; cannot send Telegram recap.")
    if not chat_id:
        raise RuntimeError("Telegram chat ID is not configured.")

    send_telegram_message(token, chat_id, summary)
    send_telegram_document(
        token,
        chat_id,
        report_path,
        f"Daily market recap markdown - {run_date.isoformat()}",
    )
    print("Telegram delivery complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
