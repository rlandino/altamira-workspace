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
OUTPUTS = WORKSPACE / "outputs"
FMP_V3 = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"
FMP_KEY = os.environ.get("FMP_API_KEY", "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz")


INDEX_NAMES = {
    "^GSPC": "S&P 500",
    "^DJI": "Dow Jones",
    "^IXIC": "Nasdaq Composite",
    "^VIX": "VIX",
    "SPY": "SPY",
    "QQQ": "QQQ",
}


def get_json(url: str, params: dict[str, Any] | None = None) -> Any:
    """Fetch JSON from an API endpoint and return None on failure."""
    request_params = dict(params or {})
    request_params["apikey"] = FMP_KEY
    try:
        response = requests.get(url, params=request_params, timeout=20)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        print(f"[daily_market_recap] Request failed for {url}: {exc}", flush=True)
    except ValueError as exc:
        print(f"[daily_market_recap] JSON decode failed for {url}: {exc}", flush=True)
    return None


def as_list(data: Any) -> list[dict[str, Any]]:
    """Normalize FMP list/dict responses into a list of dict rows."""
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        for key in ("historical", "data", "results"):
            value = data.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, dict)]
        return [data]
    return []


def parse_float(value: Any) -> float | None:
    """Parse numeric fields that FMP may return as floats or percent strings."""
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


def fmt_number(value: Any, decimals: int = 2) -> str:
    parsed = parse_float(value)
    if parsed is None:
        return "n/a"
    return f"{parsed:,.{decimals}f}"


def fmt_pct(value: Any) -> str:
    parsed = parse_float(value)
    if parsed is None:
        return "n/a"
    return f"{parsed:+.2f}%"


def quote_change(row: dict[str, Any]) -> float | None:
    return parse_float(row.get("changesPercentage") or row.get("changePercentage") or row.get("changesPercent"))


def fetch_quotes() -> dict[str, dict[str, Any]]:
    symbols = "^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ"
    rows = as_list(get_json(f"{FMP_V3}/quote/{symbols}"))
    return {str(row.get("symbol", "")).upper(): row for row in rows}


def fetch_earnings(run_date: date) -> list[dict[str, Any]]:
    to_date = run_date + timedelta(days=7)
    rows = as_list(
        get_json(
            f"{FMP_V3}/earning_calendar",
            {"from": run_date.isoformat(), "to": to_date.isoformat()},
        )
    )
    return sorted(rows, key=lambda row: str(row.get("date", "")))[:20]


def fetch_movers(path: str) -> dict[str, Any] | None:
    rows = as_list(get_json(f"{FMP_STABLE}/{path}"))
    return rows[0] if rows else None


def sector_name(row: dict[str, Any]) -> str:
    return str(row.get("sector") or row.get("sectorName") or row.get("name") or "Unknown")


def sector_change(row: dict[str, Any]) -> float | None:
    for key in ("changesPercentage", "changePercentage", "performance", "changesPercent", "change"):
        parsed = parse_float(row.get(key))
        if parsed is not None:
            return parsed
    return None


def fetch_sectors(run_date: date) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    rows = as_list(
        get_json(
            f"{FMP_STABLE}/sector-performance-snapshot",
            {"date": run_date.isoformat()},
        )
    )
    if not rows:
        rows = as_list(get_json(f"{FMP_STABLE}/sector-performance"))
    scored = [(sector_change(row), row) for row in rows]
    scored = [(change, row) for change, row in scored if change is not None]
    if not scored:
        return None, None
    scored.sort(key=lambda item: item[0])
    return scored[-1][1], scored[0][1]


def fetch_history(run_date: date) -> list[dict[str, Any]]:
    from_date = run_date - timedelta(days=45)
    rows = as_list(
        get_json(
            f"{FMP_STABLE}/historical-price-eod/light",
            {
                "symbol": "^GSPC",
                "from": from_date.isoformat(),
                "to": run_date.isoformat(),
            },
        )
    )
    return sorted(rows, key=lambda row: str(row.get("date", "")))


def fetch_news() -> list[dict[str, Any]]:
    rows = as_list(
        get_json(
            f"{FMP_STABLE}/news/general-latest",
            {"page": 0, "limit": 8},
        )
    )
    return rows[:8]


def moving_average(values: list[float], length: int) -> float | None:
    if len(values) < length:
        return None
    return sum(values[-length:]) / length


def derive_levels(history: list[dict[str, Any]]) -> dict[str, float | None]:
    closes = [parse_float(row.get("close") or row.get("adjClose") or row.get("price")) for row in history]
    closes = [value for value in closes if value is not None]
    last_20 = closes[-20:]
    return {
        "sma_5": moving_average(closes, 5),
        "sma_20": moving_average(closes, 20),
        "support": min(last_20) if last_20 else None,
        "resistance": max(last_20) if last_20 else None,
    }


def trend_label(current: float | None, sma_5: float | None, sma_20: float | None) -> str:
    if current is None or sma_5 is None or sma_20 is None:
        return "Unknown"
    if current > sma_5 and current > sma_20:
        return "Bullish"
    if current < sma_5 and current < sma_20:
        return "Bearish"
    return "Mixed"


def vix_label(value: float | None) -> str:
    if value is None:
        return "unknown"
    if value > 25:
        return "elevated"
    if value > 20:
        return "moderately elevated"
    if value < 15:
        return "low"
    return "normal"


def direction_label(change: float | None) -> str:
    if change is None:
        return "mixed"
    if change > 0.15:
        return "higher"
    if change < -0.15:
        return "lower"
    return "little changed"


def pct_vs_level(current: float | None, level: float | None) -> str:
    if current is None or level is None:
        return "n/a"
    diff = (current / level - 1) * 100
    relation = "above" if diff >= 0 else "below"
    return f"{abs(diff):.2f}% {relation}"


def row_symbol(row: dict[str, Any] | None) -> str:
    if not row:
        return "n/a"
    return str(row.get("symbol") or row.get("ticker") or row.get("name") or "n/a")


def row_change(row: dict[str, Any] | None) -> str:
    if not row:
        return "n/a"
    return fmt_pct(row.get("changesPercentage") or row.get("changePercentage") or row.get("changesPercent") or row.get("change"))


def build_summary(
    quotes: dict[str, dict[str, Any]],
    best_sector: dict[str, Any] | None,
    worst_sector: dict[str, Any] | None,
    gainer: dict[str, Any] | None,
    loser: dict[str, Any] | None,
    levels: dict[str, float | None],
) -> str:
    spx = quotes.get("^GSPC", {})
    vix = quotes.get("^VIX", {})
    current = parse_float(spx.get("price"))
    trend = trend_label(current, levels["sma_5"], levels["sma_20"])
    return (
        f"Daily Market Recap: S&P 500 {fmt_pct(quote_change(spx))} at {fmt_number(current)}, "
        f"trend {trend}; VIX {fmt_number(vix.get('price'))} ({vix_label(parse_float(vix.get('price')))}). "
        f"Best sector: {sector_name(best_sector or {})} ({fmt_pct(sector_change(best_sector or {}))}); "
        f"worst sector: {sector_name(worst_sector or {})} ({fmt_pct(sector_change(worst_sector or {}))}). "
        f"Hot stock: {row_symbol(gainer)} ({row_change(gainer)}); laggard: {row_symbol(loser)} ({row_change(loser)})."
    )


def build_markdown(
    run_date: date,
    quotes: dict[str, dict[str, Any]],
    earnings: list[dict[str, Any]],
    gainer: dict[str, Any] | None,
    loser: dict[str, Any] | None,
    best_sector: dict[str, Any] | None,
    worst_sector: dict[str, Any] | None,
    levels: dict[str, float | None],
    news: list[dict[str, Any]],
    summary: str,
) -> str:
    spx = quotes.get("^GSPC", {})
    spx_price = parse_float(spx.get("price"))
    spx_change = quote_change(spx)
    trend = trend_label(spx_price, levels["sma_5"], levels["sma_20"])
    direction = direction_label(spx_change)
    vix = quotes.get("^VIX", {})
    vix_value = parse_float(vix.get("price"))

    lines = [
        f"# Daily Market Recap - {run_date.isoformat()}",
        "",
        "**Generated for Altamira Capital. Informational only; not investment advice.**",
        "",
        "## Executive Summary",
        "",
        summary,
        "",
        "## Market Indices",
        "",
        "| Index | Level | Day Change |",
        "|---|---:|---:|",
    ]
    for symbol in ("^GSPC", "^DJI", "^IXIC"):
        row = quotes.get(symbol, {})
        lines.append(f"| {INDEX_NAMES[symbol]} | {fmt_number(row.get('price'))} | {fmt_pct(quote_change(row))} |")

    lines.extend(
        [
            "",
            "## ETFs and Volatility",
            "",
            "| Instrument | Level | Day Change | Note |",
            "|---|---:|---:|---|",
        ]
    )
    for symbol in ("SPY", "QQQ"):
        row = quotes.get(symbol, {})
        lines.append(f"| {symbol} | {fmt_number(row.get('price'))} | {fmt_pct(quote_change(row))} |  |")
    lines.append(f"| VIX | {fmt_number(vix_value)} | {fmt_pct(quote_change(vix))} | {vix_label(vix_value).title()} volatility |")

    lines.extend(
        [
            "",
            "## Breadth and Leadership",
            "",
            f"- **Best sector:** {sector_name(best_sector or {})} ({fmt_pct(sector_change(best_sector or {}))})",
            f"- **Worst sector:** {sector_name(worst_sector or {})} ({fmt_pct(sector_change(worst_sector or {}))})",
            f"- **Hot stock:** {row_symbol(gainer)} ({row_change(gainer)})",
            f"- **Biggest loser:** {row_symbol(loser)} ({row_change(loser)})",
            "",
            "## Technical Snapshot",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| S&P 500 price | {fmt_number(spx_price)} |",
            f"| 5-day average | {fmt_number(levels['sma_5'])} |",
            f"| 20-day average | {fmt_number(levels['sma_20'])} |",
            f"| Current vs 5-day average | {pct_vs_level(spx_price, levels['sma_5'])} |",
            f"| Current vs 20-day average | {pct_vs_level(spx_price, levels['sma_20'])} |",
            f"| 20-day resistance | {fmt_number(levels['resistance'])} |",
            f"| 20-day support | {fmt_number(levels['support'])} |",
            f"| Trend | {trend} |",
            "",
            "## Market Drivers From Headlines",
            "",
        ]
    )
    if news:
        for item in news[:5]:
            title = item.get("title") or item.get("headline") or item.get("text")
            site = item.get("site") or item.get("publisher") or item.get("source")
            if title:
                suffix = f" ({site})" if site else ""
                lines.append(f"- {title}{suffix}")
    else:
        lines.append("- No FMP general headlines were available; possible drivers could not be inferred.")

    lines.extend(
        [
            "",
            "## Earnings Calendar - Next 7 Days",
            "",
            "| Date | Symbol | EPS Estimate | Revenue Estimate |",
            "|---|---|---:|---:|",
        ]
    )
    if earnings:
        for row in earnings:
            lines.append(
                "| "
                f"{row.get('date', 'n/a')} | "
                f"{row.get('symbol', 'n/a')} | "
                f"{fmt_number(row.get('epsEstimated'))} | "
                f"{fmt_number(row.get('revenueEstimated'), 0)} |"
            )
    else:
        lines.append("| n/a | No earnings returned by FMP for the next 7 days | n/a | n/a |")

    lines.extend(
        [
            "",
            "## Commentary",
            "",
            (
                f"Markets are {direction} with the S&P 500 at {fmt_number(spx_price)} "
                f"and the VIX {vix_label(vix_value)} at {fmt_number(vix_value)}. "
                f"Sector leadership is led by {sector_name(best_sector or {})}, while "
                f"{sector_name(worst_sector or {})} is lagging. The S&P 500 trend reads {trend} "
                "based on its current level relative to the 5-day and 20-day averages."
            ),
            "",
            "## Telegram Summary",
            "",
            summary,
            "",
        ]
    )
    return "\n".join(lines)


def send_telegram(summary: str, markdown_path: Path, chat_id: str, token: str) -> None:
    """Send a summary message and markdown document to Telegram."""
    base = f"https://api.telegram.org/bot{token}"
    message_response = requests.post(
        f"{base}/sendMessage",
        data={"chat_id": chat_id, "text": summary[:3900]},
        timeout=20,
    )
    message_response.raise_for_status()
    message_payload = message_response.json()
    if not message_payload.get("ok"):
        raise RuntimeError(f"Telegram sendMessage failed: {message_payload}")

    with markdown_path.open("rb") as handle:
        document_response = requests.post(
            f"{base}/sendDocument",
            data={"chat_id": chat_id, "caption": f"Daily market recap - {markdown_path.name}"},
            files={"document": (markdown_path.name, handle, "text/markdown")},
            timeout=30,
        )
    document_response.raise_for_status()
    document_payload = document_response.json()
    if not document_payload.get("ok"):
        raise RuntimeError(f"Telegram sendDocument failed: {document_payload}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the daily market recap and optionally send it to Telegram.")
    parser.add_argument("--date", default=None, help="Recap date in YYYY-MM-DD format; defaults to today.")
    parser.add_argument("--out-dir", default=str(OUTPUTS), help="Output directory for the markdown recap.")
    parser.add_argument("--send-telegram", action="store_true", help="Send summary and markdown document to Telegram.")
    parser.add_argument("--telegram-chat-id", default=os.environ.get("TELEGRAM_CHAT_ID"), help="Telegram chat/channel id.")
    parser.add_argument("--telegram-bot-token", default=os.environ.get("TELEGRAM_BOT_TOKEN"), help="Telegram bot token.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_date = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else date.today()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    quotes = fetch_quotes()
    earnings = fetch_earnings(run_date)
    gainer = fetch_movers("biggest-gainers")
    loser = fetch_movers("biggest-losers")
    best_sector, worst_sector = fetch_sectors(run_date)
    history = fetch_history(run_date)
    levels = derive_levels(history)
    news = fetch_news()
    summary = build_summary(quotes, best_sector, worst_sector, gainer, loser, levels)
    markdown = build_markdown(
        run_date,
        quotes,
        earnings,
        gainer,
        loser,
        best_sector,
        worst_sector,
        levels,
        news,
        summary,
    )

    markdown_path = out_dir / f"daily-market-recap-{run_date.isoformat()}.md"
    markdown_path.write_text(markdown, encoding="utf-8")
    print(summary)
    print(f"Report: {markdown_path}")

    if args.send_telegram:
        if not args.telegram_chat_id:
            raise SystemExit("TELEGRAM_CHAT_ID or --telegram-chat-id is required for Telegram delivery.")
        if not args.telegram_bot_token:
            raise SystemExit("TELEGRAM_BOT_TOKEN or --telegram-bot-token is required for Telegram delivery.")
        send_telegram(summary, markdown_path, args.telegram_chat_id, args.telegram_bot_token)
        print("Telegram delivery: sent summary and markdown file.")


if __name__ == "__main__":
    main()
