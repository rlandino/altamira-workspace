#!/usr/bin/env python3
"""Generate and optionally send an end-of-day market recap to Telegram."""

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
FMP_KEY_FALLBACK = "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz"
DEFAULT_TELEGRAM_CHAT_ID = "7830722515"


@dataclass(frozen=True)
class Quote:
    symbol: str
    name: str
    price: float | None
    change_pct: float | None
    change: float | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a daily market recap markdown file and send it to Telegram."
    )
    parser.add_argument("--date", default=date.today().isoformat(), help="Report date YYYY-MM-DD")
    parser.add_argument(
        "--out-dir",
        default=str(OUTPUTS),
        help="Directory for generated recap markdown (default: outputs/)",
    )
    parser.add_argument(
        "--send-telegram",
        action="store_true",
        help="Send the summary message and markdown file to Telegram.",
    )
    parser.add_argument(
        "--telegram-chat-id",
        default=os.environ.get("TELEGRAM_CHAT_ID", DEFAULT_TELEGRAM_CHAT_ID),
        help="Telegram chat/channel ID (default: TELEGRAM_CHAT_ID env or workspace default).",
    )
    parser.add_argument(
        "--telegram-token",
        default=os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_API_TOKEN"),
        help="Telegram bot token (default: TELEGRAM_BOT_TOKEN or TELEGRAM_API_TOKEN env).",
    )
    parser.add_argument(
        "--fmp-api-key",
        default=os.environ.get("FMP_API_KEY", FMP_KEY_FALLBACK),
        help="FMP API key (default: FMP_API_KEY env or workspace fallback).",
    )
    return parser.parse_args()


def fmp_get(base_url: str, path: str, api_key: str, params: dict[str, Any] | None = None) -> Any:
    query = dict(params or {})
    query["apikey"] = api_key
    response = requests.get(f"{base_url}{path}", params=query, timeout=20)
    response.raise_for_status()
    return response.json()


def safe_fmp_get(
    base_url: str, path: str, api_key: str, params: dict[str, Any] | None = None
) -> tuple[Any | None, str | None]:
    try:
        return fmp_get(base_url, path, api_key, params), None
    except requests.RequestException as exc:
        return None, str(exc)
    except ValueError as exc:
        return None, f"Invalid JSON from FMP: {exc}"


def to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, str):
        value = value.replace("%", "").replace(",", "").strip()
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def get_change_pct(row: dict[str, Any]) -> float | None:
    for key in ("changesPercentage", "changePercentage", "changesPercent", "changePercent"):
        value = to_float(row.get(key))
        if value is not None:
            return value
    return None


def get_price(row: dict[str, Any]) -> float | None:
    for key in ("price", "close", "adjClose"):
        value = to_float(row.get(key))
        if value is not None:
            return value
    return None


def fmt_num(value: float | None, decimals: int = 2) -> str:
    if value is None:
        return "n/a"
    return f"{value:,.{decimals}f}"


def fmt_pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}%"


def direction(change_pct: float | None) -> str:
    if change_pct is None:
        return "n/a"
    if change_pct > 0.15:
        return "higher"
    if change_pct < -0.15:
        return "lower"
    return "little changed"


def parse_quote(row: dict[str, Any], name: str | None = None) -> Quote:
    symbol = str(row.get("symbol") or "")
    return Quote(
        symbol=symbol,
        name=name or str(row.get("name") or symbol),
        price=get_price(row),
        change_pct=get_change_pct(row),
        change=to_float(row.get("change")),
    )


def fetch_quotes(api_key: str) -> tuple[dict[str, Quote], list[str]]:
    symbols = "^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ,IWM"
    data, error = safe_fmp_get(FMP_V3, f"/quote/{symbols}", api_key)
    errors = [f"Quotes: {error}"] if error else []
    quotes: dict[str, Quote] = {}
    names = {
        "^GSPC": "S&P 500",
        "^DJI": "Dow Jones Industrial Average",
        "^IXIC": "Nasdaq Composite",
        "^VIX": "VIX",
        "SPY": "SPY",
        "QQQ": "QQQ",
        "IWM": "IWM",
    }
    if isinstance(data, list):
        for row in data:
            if isinstance(row, dict):
                quote = parse_quote(row, names.get(str(row.get("symbol"))))
                quotes[quote.symbol] = quote
    return quotes, errors


def fetch_historical(api_key: str, report_date: str) -> tuple[list[dict[str, Any]], list[str]]:
    start = (datetime.strptime(report_date, "%Y-%m-%d").date() - timedelta(days=45)).isoformat()
    data, error = safe_fmp_get(
        FMP_STABLE,
        "/historical-price-eod/light",
        api_key,
        {"symbol": "^GSPC", "from": start, "to": report_date},
    )
    errors = [f"S&P 500 history: {error}"] if error else []
    rows: list[dict[str, Any]] = []
    if isinstance(data, list):
        rows = [row for row in data if isinstance(row, dict) and get_price(row) is not None]
    rows.sort(key=lambda row: str(row.get("date") or ""))
    return rows, errors


def moving_average(values: list[float], window: int) -> float | None:
    if len(values) < window:
        return None
    return sum(values[-window:]) / window


def fetch_sectors(api_key: str, report_date: str) -> tuple[list[dict[str, Any]], list[str]]:
    data, error = safe_fmp_get(
        FMP_STABLE,
        "/sector-performance-snapshot",
        api_key,
        {"date": report_date},
    )
    if error or not data:
        data, error = safe_fmp_get(FMP_STABLE, "/sector-performance-snapshot", api_key)
    errors = [f"Sectors: {error}"] if error else []
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)], errors
    if isinstance(data, dict):
        return [data], errors
    return [], errors


def sector_name(row: dict[str, Any]) -> str:
    for key in ("sector", "sectorName", "name"):
        if row.get(key):
            return str(row[key])
    return "n/a"


def sector_change(row: dict[str, Any]) -> float | None:
    for key in ("changesPercentage", "changePercentage", "averageChange", "performance", "change"):
        value = to_float(row.get(key))
        if value is not None:
            return value
    return None


def fetch_movers(api_key: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    gainers, error = safe_fmp_get(FMP_STABLE, "/biggest-gainers", api_key)
    if error:
        errors.append(f"Gainers: {error}")
    losers, error = safe_fmp_get(FMP_STABLE, "/biggest-losers", api_key)
    if error:
        errors.append(f"Losers: {error}")
    top_gainer = gainers[0] if isinstance(gainers, list) and gainers else None
    top_loser = losers[0] if isinstance(losers, list) and losers else None
    return top_gainer, top_loser, errors


def fetch_earnings(api_key: str, report_date: str) -> tuple[list[dict[str, Any]], list[str]]:
    end = (datetime.strptime(report_date, "%Y-%m-%d").date() + timedelta(days=7)).isoformat()
    data, error = safe_fmp_get(
        FMP_V3,
        "/earning_calendar",
        api_key,
        {"from": report_date, "to": end},
    )
    errors = [f"Earnings: {error}"] if error else []
    if isinstance(data, list):
        rows = [row for row in data if isinstance(row, dict)]
        rows = [row for row in rows if is_us_style_symbol(str(row.get("symbol") or ""))]
        rows.sort(key=lambda row: (str(row.get("date") or ""), str(row.get("symbol") or "")))
        return rows[:20], errors
    return [], errors


def is_us_style_symbol(symbol: str) -> bool:
    """Keep common US listed tickers and drop global/OTC suffix patterns."""
    if re.fullmatch(r"[A-Z]{1,4}(?:-[A-Z])?", symbol):
        return True
    if re.fullmatch(r"[A-Z]{5}", symbol):
        return symbol[-1] not in {"F", "Q", "W", "Y"}
    return False


def fetch_headlines(api_key: str) -> tuple[list[dict[str, Any]], list[str]]:
    data, error = safe_fmp_get(
        FMP_STABLE,
        "/news/general-latest",
        api_key,
        {"page": 0, "limit": 5},
    )
    errors = [f"Headlines: {error}"] if error else []
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)][:5], errors
    return [], errors


def vix_label(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value >= 30:
        return "crisis"
    if value > 20:
        return "elevated"
    if value < 15:
        return "low"
    return "normal"


def build_report(report_date: str, api_key: str) -> tuple[str, str, dict[str, Any]]:
    errors: list[str] = []
    quotes, quote_errors = fetch_quotes(api_key)
    history, history_errors = fetch_historical(api_key, report_date)
    sectors, sector_errors = fetch_sectors(api_key, report_date)
    top_gainer, top_loser, mover_errors = fetch_movers(api_key)
    earnings, earnings_errors = fetch_earnings(api_key, report_date)
    headlines, headline_errors = fetch_headlines(api_key)
    errors.extend(quote_errors + history_errors + sector_errors + mover_errors + earnings_errors + headline_errors)

    spx = quotes.get("^GSPC", Quote("^GSPC", "S&P 500", None, None, None))
    dow = quotes.get("^DJI", Quote("^DJI", "Dow Jones Industrial Average", None, None, None))
    nasdaq = quotes.get("^IXIC", Quote("^IXIC", "Nasdaq Composite", None, None, None))
    vix = quotes.get("^VIX", Quote("^VIX", "VIX", None, None, None))

    closes = [price for row in history if (price := get_price(row)) is not None]
    sma_5 = moving_average(closes, 5)
    sma_20 = moving_average(closes, 20)
    recent_20 = closes[-20:]
    resistance = max(recent_20) if recent_20 else None
    support = min(recent_20) if recent_20 else None
    trend = "Mixed"
    if spx.price is not None and sma_5 is not None and sma_20 is not None:
        if spx.price > sma_5 and spx.price > sma_20:
            trend = "Bullish"
        elif spx.price < sma_5 and spx.price < sma_20:
            trend = "Bearish"

    scored_sectors = [(sector_name(row), sector_change(row)) for row in sectors]
    scored_sectors = [(name, change) for name, change in scored_sectors if change is not None]
    best_sector = max(scored_sectors, key=lambda item: item[1]) if scored_sectors else ("n/a", None)
    worst_sector = min(scored_sectors, key=lambda item: item[1]) if scored_sectors else ("n/a", None)

    gainer_symbol = str((top_gainer or {}).get("symbol") or "n/a")
    gainer_change = get_change_pct(top_gainer or {})
    loser_symbol = str((top_loser or {}).get("symbol") or "n/a")
    loser_change = get_change_pct(top_loser or {})

    headline_lines = []
    for row in headlines:
        title = str(row.get("title") or row.get("headline") or "").strip()
        site = str(row.get("site") or row.get("publisher") or "").strip()
        if title:
            headline_lines.append(f"- {title}" + (f" ({site})" if site else ""))

    earnings_lines = []
    for row in earnings:
        earnings_lines.append(
            "| {date} | {symbol} | {eps} | {revenue} |".format(
                date=row.get("date") or "n/a",
                symbol=row.get("symbol") or "n/a",
                eps=fmt_num(to_float(row.get("epsEstimated"))),
                revenue=fmt_num(to_float(row.get("revenueEstimated")), 0),
            )
        )
    if not earnings_lines:
        earnings_lines = ["| n/a | No earnings found for the next 7 days | n/a | n/a |"]

    market_direction = direction(spx.change_pct)
    vix_context = vix_label(vix.price)
    commentary = (
        f"Markets finished {market_direction} with the S&P 500 at {fmt_num(spx.price)} "
        f"({fmt_pct(spx.change_pct)}), while the Nasdaq was {fmt_pct(nasdaq.change_pct)} "
        f"and the Dow was {fmt_pct(dow.change_pct)}. VIX is {vix_context} at {fmt_num(vix.price)}, "
        f"keeping the risk backdrop {vix_context if vix_context != 'n/a' else 'unclear'}. "
        f"Sector leadership was led by {best_sector[0]} ({fmt_pct(best_sector[1])}), "
        f"while {worst_sector[0]} lagged ({fmt_pct(worst_sector[1])})."
    )

    summary = (
        f"Daily Market Recap {report_date}: S&P 500 {fmt_pct(spx.change_pct)} at {fmt_num(spx.price)}, "
        f"Nasdaq {fmt_pct(nasdaq.change_pct)}, Dow {fmt_pct(dow.change_pct)}. "
        f"Trend: {trend}; VIX {fmt_num(vix.price)} ({vix_context}). "
        f"Best sector: {best_sector[0]} {fmt_pct(best_sector[1])}; "
        f"worst sector: {worst_sector[0]} {fmt_pct(worst_sector[1])}. "
        f"Top mover: {gainer_symbol} {fmt_pct(gainer_change)}; "
        f"biggest loser: {loser_symbol} {fmt_pct(loser_change)}."
    )

    lines = [
        f"# Daily Market Recap - {report_date}",
        "",
        "> Educational market commentary for Altamira Capital. Not investment advice.",
        "",
        "## Executive Summary",
        "",
        summary,
        "",
        "## Market Indices",
        "",
        "| Index | Level | Day Change |",
        "|---|---:|---:|",
        f"| S&P 500 | {fmt_num(spx.price)} | {fmt_pct(spx.change_pct)} |",
        f"| Nasdaq Composite | {fmt_num(nasdaq.price)} | {fmt_pct(nasdaq.change_pct)} |",
        f"| Dow Jones Industrial Average | {fmt_num(dow.price)} | {fmt_pct(dow.change_pct)} |",
        "",
        "## ETFs and Volatility",
        "",
        "| Instrument | Level | Day Change | Context |",
        "|---|---:|---:|---|",
        f"| SPY | {fmt_num(quotes.get('SPY', Quote('SPY', 'SPY', None, None, None)).price)} | {fmt_pct(quotes.get('SPY', Quote('SPY', 'SPY', None, None, None)).change_pct)} | S&P 500 ETF |",
        f"| QQQ | {fmt_num(quotes.get('QQQ', Quote('QQQ', 'QQQ', None, None, None)).price)} | {fmt_pct(quotes.get('QQQ', Quote('QQQ', 'QQQ', None, None, None)).change_pct)} | Nasdaq 100 ETF |",
        f"| IWM | {fmt_num(quotes.get('IWM', Quote('IWM', 'IWM', None, None, None)).price)} | {fmt_pct(quotes.get('IWM', Quote('IWM', 'IWM', None, None, None)).change_pct)} | Russell 2000 ETF |",
        f"| VIX | {fmt_num(vix.price)} | {fmt_pct(vix.change_pct)} | {vix_context.title()} volatility regime |",
        "",
        "## Sector Leadership",
        "",
        f"- **Best sector:** {best_sector[0]} ({fmt_pct(best_sector[1])})",
        f"- **Worst sector:** {worst_sector[0]} ({fmt_pct(worst_sector[1])})",
        "",
        "## Single-Stock Movers",
        "",
        f"- **Hot stock:** {gainer_symbol} ({fmt_pct(gainer_change)})",
        f"- **Biggest loser:** {loser_symbol} ({fmt_pct(loser_change)})",
        "",
        "## S&P 500 Technical Snapshot",
        "",
        "| Metric | Level |",
        "|---|---:|",
        f"| Current | {fmt_num(spx.price)} |",
        f"| 5-day average | {fmt_num(sma_5)} |",
        f"| 20-day average | {fmt_num(sma_20)} |",
        f"| 20-day resistance | {fmt_num(resistance)} |",
        f"| 20-day support | {fmt_num(support)} |",
        f"| Trend | {trend} |",
        "",
        "## Market Drivers / Headlines",
        "",
        *(headline_lines or ["- No broad-market headlines returned by the data provider."]),
        "",
        "## Earnings Calendar (Next 7 Days)",
        "",
        "| Date | Symbol | EPS Estimate | Revenue Estimate |",
        "|---|---|---:|---:|",
        *earnings_lines,
        "",
        "## Commentary",
        "",
        commentary,
        "",
        "## Data Notes",
        "",
        "- Sources: Financial Modeling Prep quotes, market movers, sector snapshot, earnings calendar, and headlines.",
        "- Technical levels use recent S&P 500 closing prices; support/resistance are the recent 20-trading-day low/high.",
    ]
    if errors:
        lines.extend(["", "## Fetch Warnings", ""])
        lines.extend(f"- {error}" for error in errors)
    lines.append("")

    metadata = {
        "summary": summary,
        "spx_change_pct": spx.change_pct,
        "trend": trend,
        "vix": vix.price,
        "best_sector": best_sector[0],
        "worst_sector": worst_sector[0],
        "warnings": errors,
    }
    return "\n".join(lines), summary, metadata


def write_report(report_date: str, out_dir: Path, content: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"daily-market-recap-{report_date}.md"
    path.write_text(content, encoding="utf-8")
    return path


def telegram_request(token: str, method: str, data: dict[str, Any] | None = None, files: Any = None) -> Any:
    response = requests.post(
        f"https://api.telegram.org/bot{token}/{method}",
        data=data,
        files=files,
        timeout=30,
    )
    response.raise_for_status()
    result = response.json()
    if not result.get("ok"):
        raise RuntimeError(f"Telegram {method} failed: {result}")
    return result


def send_to_telegram(token: str, chat_id: str, summary: str, report_path: Path) -> None:
    telegram_request(
        token,
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": summary,
            "disable_web_page_preview": "true",
        },
    )
    with report_path.open("rb") as handle:
        telegram_request(
            token,
            "sendDocument",
            {
                "chat_id": chat_id,
                "caption": f"Daily market recap markdown: {report_path.name}",
            },
            {"document": (report_path.name, handle, "text/markdown")},
        )


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)

    try:
        datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        print("--date must be YYYY-MM-DD", file=sys.stderr)
        return 2

    content, summary, metadata = build_report(args.date, args.fmp_api_key)
    report_path = write_report(args.date, out_dir, content)
    print(summary)
    print(f"Report: {report_path}")
    if metadata["warnings"]:
        print("Warnings:")
        for warning in metadata["warnings"]:
            print(f"- {warning}")

    if args.send_telegram:
        if not args.telegram_token:
            print("Telegram send skipped: TELEGRAM_BOT_TOKEN/TELEGRAM_API_TOKEN is not set.", file=sys.stderr)
            return 1
        if not args.telegram_chat_id:
            print("Telegram send skipped: TELEGRAM_CHAT_ID is not set.", file=sys.stderr)
            return 1
        send_to_telegram(args.telegram_token, str(args.telegram_chat_id), summary, report_path)
        print(f"Telegram: sent summary and {report_path.name} to chat {args.telegram_chat_id}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
