#!/usr/bin/env python3
"""Generate a daily market recap and optionally deliver it to Telegram."""

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
DEFAULT_SYMBOLS = ["^GSPC", "^DJI", "^IXIC", "^VIX", "SPY", "QQQ"]
SECTOR_ETFS = {
    "Communication Services": "XLC",
    "Consumer Discretionary": "XLY",
    "Consumer Staples": "XLP",
    "Energy": "XLE",
    "Financials": "XLF",
    "Health Care": "XLV",
    "Industrials": "XLI",
    "Materials": "XLB",
    "Real Estate": "XLRE",
    "Technology": "XLK",
    "Utilities": "XLU",
}


class RecapError(RuntimeError):
    """Raised when recap generation cannot continue safely."""


@dataclass(frozen=True)
class Quote:
    symbol: str
    name: str
    price: float | None
    change_pct: float | None


def resolve_fmp_key() -> str:
    """Resolve the FMP key from the environment or existing command docs."""
    env_key = os.environ.get("FMP_API_KEY", "").strip()
    if env_key:
        return env_key

    command_doc = WORKSPACE / ".claude" / "commands" / "briefing.md"
    if command_doc.exists():
        match = re.search(r"Use the key:\s*`([^`]+)`", command_doc.read_text())
        if match:
            return match.group(1).strip()

    raise RecapError("FMP_API_KEY is not set and no fallback key was found in command docs.")


def resolve_telegram_chat_id(explicit_chat_id: str | None) -> str:
    """Resolve Telegram chat from args, environment, or existing workflow artifact."""
    if explicit_chat_id:
        return explicit_chat_id

    env_chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if env_chat_id:
        return env_chat_id

    workflow_path = OUTPUTS / "csp-daily-scan-fixed.json"
    if workflow_path.exists():
        try:
            workflow = json.loads(workflow_path.read_text())
            for node in workflow.get("nodes", []):
                params = node.get("parameters", {})
                chat_id = str(params.get("chatId", "")).strip()
                if chat_id and not chat_id.startswith("={{"):
                    return chat_id.removeprefix("=")
        except json.JSONDecodeError:
            pass

    raise RecapError("Telegram chat ID not found. Set TELEGRAM_CHAT_ID or pass --telegram-chat-id.")


def get_json(url: str, params: dict[str, Any], timeout: int = 20) -> Any:
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        if isinstance(value, str):
            value = value.replace("%", "").strip()
        return float(value)
    except (TypeError, ValueError):
        return None


def format_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:+.2f}%"


def format_price(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:,.2f}"


def fetch_quotes(symbols: list[str], fmp_key: str) -> dict[str, Quote]:
    data = get_json(f"{FMP_V3}/quote/{','.join(symbols)}", {"apikey": fmp_key})
    if not isinstance(data, list):
        raise RecapError("Unexpected FMP quote response.")

    quotes: dict[str, Quote] = {}
    for item in data:
        symbol = item.get("symbol")
        if not symbol:
            continue
        quotes[symbol] = Quote(
            symbol=symbol,
            name=item.get("name") or symbol,
            price=as_float(item.get("price")),
            change_pct=as_float(item.get("changesPercentage") or item.get("changePercentage")),
        )
    return quotes


def fetch_historical_closes(symbol: str, fmp_key: str, as_of: date) -> list[dict[str, Any]]:
    from_date = (as_of - timedelta(days=45)).isoformat()
    data = get_json(
        f"{FMP_STABLE}/historical-price-eod/light",
        {"symbol": symbol, "from": from_date, "to": as_of.isoformat(), "apikey": fmp_key},
    )
    if not isinstance(data, list):
        return []
    rows = [row for row in data if row.get("date") and as_float(row.get("close")) is not None]
    return sorted(rows, key=lambda row: row["date"])


def fetch_earnings(fmp_key: str, as_of: date) -> list[dict[str, Any]]:
    data = get_json(
        f"{FMP_V3}/earning_calendar",
        {"from": as_of.isoformat(), "to": (as_of + timedelta(days=7)).isoformat(), "apikey": fmp_key},
    )
    return data if isinstance(data, list) else []


def fetch_movers(fmp_key: str, endpoint: str) -> dict[str, Any] | None:
    data = get_json(f"{FMP_STABLE}/{endpoint}", {"apikey": fmp_key})
    if isinstance(data, list) and data:
        return data[0]
    return None


def select_sector_leaders(quotes: dict[str, Quote]) -> tuple[tuple[str, Quote] | None, tuple[str, Quote] | None]:
    sector_quotes = [
        (sector, quotes[etf])
        for sector, etf in SECTOR_ETFS.items()
        if etf in quotes and quotes[etf].change_pct is not None
    ]
    if not sector_quotes:
        return None, None
    return max(sector_quotes, key=lambda row: row[1].change_pct or 0), min(
        sector_quotes, key=lambda row: row[1].change_pct or 0
    )


def trend_metrics(current_price: float | None, closes: list[dict[str, Any]]) -> dict[str, Any]:
    close_values = [as_float(row.get("close")) for row in closes]
    close_values = [value for value in close_values if value is not None]
    if not current_price or len(close_values) < 5:
        return {"trend": "Unknown", "avg_5d": None, "avg_20d": None, "support": None, "resistance": None}

    avg_5d = sum(close_values[-5:]) / min(5, len(close_values))
    avg_20d = sum(close_values[-20:]) / min(20, len(close_values))
    window_20 = close_values[-20:] if len(close_values) >= 20 else close_values
    support = min(window_20)
    resistance = max(window_20)

    if current_price > avg_5d and current_price > avg_20d:
        trend = "Bullish"
    elif current_price < avg_5d and current_price < avg_20d:
        trend = "Bearish"
    else:
        trend = "Mixed"

    return {
        "trend": trend,
        "avg_5d": avg_5d,
        "avg_20d": avg_20d,
        "support": support,
        "resistance": resistance,
    }


def vix_label(vix: float | None) -> str:
    if vix is None:
        return "unknown"
    if vix >= 25:
        return "elevated"
    if vix >= 20:
        return "firm"
    if vix < 15:
        return "low"
    return "normal"


def mover_summary(item: dict[str, Any] | None) -> str:
    if not item:
        return "n/a"
    symbol = item.get("symbol") or item.get("ticker") or "n/a"
    change = as_float(item.get("changesPercentage") or item.get("changePercentage") or item.get("changes"))
    return f"{symbol} ({format_pct(change)})"


def build_recap(as_of: date, fmp_key: str) -> tuple[str, str]:
    symbols = DEFAULT_SYMBOLS + list(SECTOR_ETFS.values())
    quotes = fetch_quotes(symbols, fmp_key)
    closes = fetch_historical_closes("^GSPC", fmp_key, as_of)
    earnings = fetch_earnings(fmp_key, as_of)
    gainer = fetch_movers(fmp_key, "biggest-gainers")
    loser = fetch_movers(fmp_key, "biggest-losers")
    best_sector, worst_sector = select_sector_leaders(quotes)

    spx = quotes.get("^GSPC")
    dow = quotes.get("^DJI")
    nasdaq = quotes.get("^IXIC")
    spy = quotes.get("SPY")
    qqq = quotes.get("QQQ")
    vix = quotes.get("^VIX")
    metrics = trend_metrics(spx.price if spx else None, closes)
    as_of_label = as_of.strftime("%A, %B %-d, %Y") if sys.platform != "win32" else as_of.strftime("%A, %B %#d, %Y")

    best_sector_text = (
        f"{best_sector[0]} ({best_sector[1].symbol} {format_pct(best_sector[1].change_pct)})"
        if best_sector
        else "n/a"
    )
    worst_sector_text = (
        f"{worst_sector[0]} ({worst_sector[1].symbol} {format_pct(worst_sector[1].change_pct)})"
        if worst_sector
        else "n/a"
    )
    vix_value = vix.price if vix else None
    trend = metrics["trend"]

    summary = (
        f"Daily Market Recap ({as_of.isoformat()}): S&P 500 {format_pct(spx.change_pct if spx else None)} "
        f"at {format_price(spx.price if spx else None)}, Nasdaq {format_pct(nasdaq.change_pct if nasdaq else None)}, "
        f"Dow {format_pct(dow.change_pct if dow else None)}. VIX is {vix_label(vix_value)} at "
        f"{format_price(vix_value)}; S&P trend: {trend}. Best sector: {best_sector_text}; "
        f"worst sector: {worst_sector_text}. Hot stock: {mover_summary(gainer)}; biggest loser: {mover_summary(loser)}."
    )

    earnings_rows = []
    for item in sorted(earnings, key=lambda row: (row.get("date") or "", row.get("symbol") or ""))[:20]:
        earnings_rows.append(
            "| {date} | {symbol} | {eps} | {revenue} |".format(
                date=item.get("date", "n/a"),
                symbol=item.get("symbol", "n/a"),
                eps=item.get("epsEstimated", "n/a"),
                revenue=item.get("revenueEstimated", "n/a"),
            )
        )
    if not earnings_rows:
        earnings_rows.append("| n/a | No earnings returned for the next 7 days | n/a | n/a |")

    markdown = f"""# Daily Market Recap — {as_of.isoformat()}

Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}

## Executive Summary

{summary}

## Market Indices

| Index | Level | Day Change |
| --- | ---: | ---: |
| S&P 500 | {format_price(spx.price if spx else None)} | {format_pct(spx.change_pct if spx else None)} |
| Nasdaq Composite | {format_price(nasdaq.price if nasdaq else None)} | {format_pct(nasdaq.change_pct if nasdaq else None)} |
| Dow Jones Industrial Average | {format_price(dow.price if dow else None)} | {format_pct(dow.change_pct if dow else None)} |

## Market Dashboard

| Metric | Reading |
| --- | --- |
| SPY | {format_price(spy.price if spy else None)} ({format_pct(spy.change_pct if spy else None)}) |
| QQQ | {format_price(qqq.price if qqq else None)} ({format_pct(qqq.change_pct if qqq else None)}) |
| VIX | {format_price(vix_value)} ({vix_label(vix_value)}) |
| Hot stock | {mover_summary(gainer)} |
| Biggest loser | {mover_summary(loser)} |
| Best sector | {best_sector_text} |
| Worst sector | {worst_sector_text} |

## S&P 500 Technical Context

| Measure | Level |
| --- | ---: |
| Current | {format_price(spx.price if spx else None)} |
| 5-day average | {format_price(metrics["avg_5d"])} |
| 20-day average | {format_price(metrics["avg_20d"])} |
| 20-day resistance | {format_price(metrics["resistance"])} |
| 20-day support | {format_price(metrics["support"])} |
| Trend | {trend} |

## Earnings Calendar: Next 7 Days

| Date | Symbol | EPS Estimate | Revenue Estimate |
| --- | --- | ---: | ---: |
{chr(10).join(earnings_rows)}

## Commentary

Markets are summarized as of {as_of_label}. The S&P 500 trend is **{trend}** based on its position versus the 5-day and 20-day averages, while VIX is **{vix_label(vix_value)}** at {format_price(vix_value)}. Sector tone is led by {best_sector_text}, with {worst_sector_text} lagging.

## Disclaimer

This recap is for informational purposes only and is not investment advice. Verify market data before making trading or portfolio decisions.
"""
    return summary, markdown


def send_telegram(summary: str, markdown_path: Path, chat_id: str) -> dict[str, Any]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RecapError("TELEGRAM_BOT_TOKEN is not set.")

    base = f"https://api.telegram.org/bot{token}"
    message_response = requests.post(
        f"{base}/sendMessage",
        data={"chat_id": chat_id, "text": summary, "disable_web_page_preview": "true"},
        timeout=20,
    )
    message_response.raise_for_status()

    with markdown_path.open("rb") as handle:
        document_response = requests.post(
            f"{base}/sendDocument",
            data={"chat_id": chat_id, "caption": f"Daily market recap markdown — {markdown_path.stem[-10:]}"},
            files={"document": (markdown_path.name, handle, "text/markdown")},
            timeout=30,
        )
    document_response.raise_for_status()
    return {"message": message_response.json(), "document": document_response.json()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate and optionally send a daily market recap.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Recap date in YYYY-MM-DD format.")
    parser.add_argument("--send-telegram", action="store_true", help="Send summary and markdown file to Telegram.")
    parser.add_argument("--telegram-chat-id", default=None, help="Telegram chat/channel ID. Defaults to TELEGRAM_CHAT_ID.")
    parser.add_argument("--out-dir", default=str(OUTPUTS), help="Directory for markdown and delivery artifacts.")
    args = parser.parse_args()

    try:
        as_of = datetime.strptime(args.date, "%Y-%m-%d").date()
        fmp_key = resolve_fmp_key()
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        summary, markdown = build_recap(as_of, fmp_key)
        markdown_path = out_dir / f"daily-market-recap-{as_of.isoformat()}.md"
        markdown_path.write_text(markdown)

        delivery_path = None
        if args.send_telegram:
            chat_id = resolve_telegram_chat_id(args.telegram_chat_id)
            delivery = send_telegram(summary, markdown_path, chat_id)
            delivery_path = out_dir / f"daily-market-recap-{as_of.isoformat()}-telegram.json"
            delivery_path.write_text(json.dumps(delivery, indent=2))

        print(summary)
        print(f"Markdown: {markdown_path}")
        if delivery_path:
            print(f"Telegram delivery: {delivery_path}")
        return 0
    except Exception as exc:
        print(f"daily_market_recap failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
