#!/usr/bin/env python3
"""
Generate an Altamira daily market recap and optionally send it to Telegram.

The script writes a markdown report to outputs/daily-market-recap-{DATE}.md,
prints a concise summary, and can deliver both the summary and markdown file
through the Telegram Bot API.
"""

from __future__ import annotations

import argparse
import json
import os
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
INDEX_SYMBOLS = "^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ,DIA,IWM"


@dataclass
class RecapResult:
    """Generated recap artifact and Telegram status."""

    report_path: Path
    summary: str
    telegram_sent: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate and send a daily market recap")
    parser.add_argument("--date", default=date.today().isoformat(), help="Recap date YYYY-MM-DD")
    parser.add_argument("--out-dir", default=str(OUTPUTS), help="Directory for markdown output")
    parser.add_argument("--fmp-api-key", default=os.environ.get("FMP_API_KEY"), help="FMP API key")
    parser.add_argument(
        "--telegram-bot-token",
        default=os.environ.get("TELEGRAM_BOT_TOKEN"),
        help="Telegram bot token",
    )
    parser.add_argument(
        "--telegram-chat-id",
        default=(
            os.environ.get("TELEGRAM_CHAT_ID")
            or os.environ.get("TELEGRAM_MARKET_CHAT_ID")
            or os.environ.get("TELEGRAM_CHANNEL_ID")
        ),
        help="Telegram chat/channel id",
    )
    parser.add_argument("--skip-telegram", action="store_true", help="Generate only; do not send")
    parser.add_argument("--json", action="store_true", help="Print machine-readable result JSON")
    return parser.parse_args()


def fmp_get(base_url: str, path: str, api_key: str, params: dict[str, Any] | None = None) -> Any:
    """Fetch JSON from FMP and raise a clear error on failure."""
    request_params = dict(params or {})
    request_params["apikey"] = api_key
    response = requests.get(f"{base_url}{path}", params=request_params, timeout=20)
    response.raise_for_status()
    return response.json()


def parse_percent(value: Any) -> float | None:
    """Convert FMP percentage fields to floats."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace("%", "").replace("+", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def fmt_num(value: Any, digits: int = 2) -> str:
    if value is None:
        return "N/A"
    try:
        return f"{float(value):,.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def fmt_pct(value: Any) -> str:
    pct = parse_percent(value)
    if pct is None:
        return "N/A"
    return f"{pct:+.2f}%"


def quote_by_symbol(rows: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(rows, list):
        return {}
    return {
        str(row.get("symbol", "")).upper(): row
        for row in rows
        if isinstance(row, dict) and row.get("symbol")
    }


def first_row(rows: Any) -> dict[str, Any]:
    if isinstance(rows, list) and rows and isinstance(rows[0], dict):
        return rows[0]
    return {}


def extract_sector_name(row: dict[str, Any]) -> str:
    for key in ("sector", "name", "sectorName"):
        if row.get(key):
            return str(row[key])
    return "Unknown"


def extract_sector_performance(row: dict[str, Any]) -> float | None:
    for key in ("changesPercentage", "changePercentage", "performance", "changes", "change"):
        value = parse_percent(row.get(key))
        if value is not None:
            return value
    return None


def fetch_sector_snapshot(api_key: str, recap_date: str) -> tuple[dict[str, Any], dict[str, Any], str]:
    """Return best sector, worst sector, and data date with a short fallback window."""
    target = datetime.strptime(recap_date, "%Y-%m-%d").date()
    for offset in range(0, 8):
        query_date = (target - timedelta(days=offset)).isoformat()
        try:
            data = fmp_get(
                FMP_STABLE,
                "/sector-performance-snapshot",
                api_key,
                {"date": query_date},
            )
        except requests.RequestException:
            continue
        rows = data if isinstance(data, list) else []
        scored = [
            (extract_sector_performance(row), row)
            for row in rows
            if isinstance(row, dict) and extract_sector_performance(row) is not None
        ]
        if scored:
            scored.sort(key=lambda item: item[0])
            return scored[-1][1], scored[0][1], query_date
    return {}, {}, recap_date


def fetch_history(api_key: str, recap_date: str) -> list[dict[str, Any]]:
    end_date = datetime.strptime(recap_date, "%Y-%m-%d").date()
    start_date = (end_date - timedelta(days=45)).isoformat()
    data = fmp_get(
        FMP_STABLE,
        "/historical-price-eod/light",
        api_key,
        {"symbol": "^GSPC", "from": start_date, "to": recap_date},
    )
    rows = data if isinstance(data, list) else []
    return sorted(
        [row for row in rows if isinstance(row, dict) and row.get("date") and row.get("close")],
        key=lambda row: row["date"],
    )


def average(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def technicals(history: list[dict[str, Any]], current_price: float | None) -> dict[str, Any]:
    closes = [float(row["close"]) for row in history if row.get("close") is not None]
    last_20 = closes[-20:]
    sma_5 = average(closes[-5:])
    sma_20 = average(last_20)
    support = min(last_20) if last_20 else None
    resistance = max(last_20) if last_20 else None
    if current_price is None or sma_5 is None or sma_20 is None:
        trend = "Unknown"
    elif current_price > sma_5 and current_price > sma_20:
        trend = "Bullish"
    elif current_price < sma_5 and current_price < sma_20:
        trend = "Bearish"
    else:
        trend = "Mixed"
    return {
        "sma_5": sma_5,
        "sma_20": sma_20,
        "support": support,
        "resistance": resistance,
        "trend": trend,
    }


def vix_label(vix: float | None) -> str:
    if vix is None:
        return "unknown"
    if vix >= 25:
        return "elevated"
    if vix > 20:
        return "firm"
    if vix < 15:
        return "low"
    return "normal"


def market_direction(changes: list[float]) -> str:
    if not changes:
        return "mixed"
    positives = sum(1 for item in changes if item > 0.05)
    negatives = sum(1 for item in changes if item < -0.05)
    if positives > negatives:
        return "higher"
    if negatives > positives:
        return "lower"
    return "mixed"


def earnings_rows(rows: Any, limit: int = 12) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        return []
    clean_rows = [row for row in rows if isinstance(row, dict)]
    return sorted(clean_rows, key=lambda row: (row.get("date") or "", row.get("symbol") or ""))[:limit]


def news_rows(rows: Any, limit: int = 5) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)][:limit]


def row_value(row: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in row and row[key] not in (None, ""):
            return row[key]
    return None


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    header_line = "| " + " | ".join(headers) + " |"
    divider = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header_line, divider, *body])


def build_report(
    recap_date: str,
    quotes: dict[str, dict[str, Any]],
    best_sector: dict[str, Any],
    worst_sector: dict[str, Any],
    sector_date: str,
    gainer: dict[str, Any],
    loser: dict[str, Any],
    earnings: list[dict[str, Any]],
    headlines: list[dict[str, Any]],
    technical: dict[str, Any],
) -> tuple[str, str]:
    spx = quotes.get("^GSPC", {})
    dow = quotes.get("^DJI", {})
    nasdaq = quotes.get("^IXIC", {})
    vix = quotes.get("^VIX", {})
    spy = quotes.get("SPY", {})
    qqq = quotes.get("QQQ", {})
    dia = quotes.get("DIA", {})
    iwm = quotes.get("IWM", {})

    spx_change = parse_percent(row_value(spx, "changesPercentage", "changePercentage"))
    dow_change = parse_percent(row_value(dow, "changesPercentage", "changePercentage"))
    nasdaq_change = parse_percent(row_value(nasdaq, "changesPercentage", "changePercentage"))
    direction = market_direction([item for item in [spx_change, dow_change, nasdaq_change] if item is not None])

    vix_level = row_value(vix, "price")
    try:
        vix_float = float(vix_level) if vix_level is not None else None
    except (TypeError, ValueError):
        vix_float = None
    vix_state = vix_label(vix_float)

    best_sector_name = extract_sector_name(best_sector)
    best_sector_perf = extract_sector_performance(best_sector)
    worst_sector_name = extract_sector_name(worst_sector)
    worst_sector_perf = extract_sector_performance(worst_sector)

    hot_symbol = row_value(gainer, "symbol", "ticker") or "N/A"
    hot_change = row_value(gainer, "changesPercentage", "changePercentage", "changes", "change")
    loser_symbol = row_value(loser, "symbol", "ticker") or "N/A"
    loser_change = row_value(loser, "changesPercentage", "changePercentage", "changes", "change")

    summary = (
        f"Daily market recap for {recap_date}: major indices are {direction}; "
        f"S&P 500 {fmt_pct(spx_change)}, Nasdaq {fmt_pct(nasdaq_change)}, "
        f"Dow {fmt_pct(dow_change)}. VIX is {vix_state} at {fmt_num(vix_float)}. "
        f"Best sector: {best_sector_name} ({fmt_pct(best_sector_perf)}); "
        f"worst sector: {worst_sector_name} ({fmt_pct(worst_sector_perf)}). "
        f"Trend: {technical['trend']}."
    )

    index_table = markdown_table(
        ["Index", "Level", "Day change"],
        [
            ["S&P 500", fmt_num(row_value(spx, "price")), fmt_pct(spx_change)],
            ["Nasdaq Composite", fmt_num(row_value(nasdaq, "price")), fmt_pct(nasdaq_change)],
            ["Dow Jones", fmt_num(row_value(dow, "price")), fmt_pct(dow_change)],
        ],
    )
    etf_table = markdown_table(
        ["ETF", "Level", "Day change"],
        [
            ["SPY", fmt_num(row_value(spy, "price")), fmt_pct(row_value(spy, "changesPercentage", "changePercentage"))],
            ["QQQ", fmt_num(row_value(qqq, "price")), fmt_pct(row_value(qqq, "changesPercentage", "changePercentage"))],
            ["DIA", fmt_num(row_value(dia, "price")), fmt_pct(row_value(dia, "changesPercentage", "changePercentage"))],
            ["IWM", fmt_num(row_value(iwm, "price")), fmt_pct(row_value(iwm, "changesPercentage", "changePercentage"))],
        ],
    )

    if earnings:
        earnings_table = markdown_table(
            ["Date", "Symbol", "EPS estimate", "Revenue estimate"],
            [
                [
                    str(row_value(row, "date") or "N/A"),
                    str(row_value(row, "symbol") or "N/A"),
                    fmt_num(row_value(row, "epsEstimated", "epsEstimate")),
                    fmt_num(row_value(row, "revenueEstimated", "revenueEstimate"), 0),
                ]
                for row in earnings
            ],
        )
    else:
        earnings_table = "No earnings calendar rows returned for the next 7 days."

    if headlines:
        headline_lines = []
        for row in headlines:
            title = row_value(row, "title", "headline") or "Untitled"
            source = row_value(row, "site", "publisher", "source") or "FMP"
            headline_lines.append(f"- {title} ({source})")
        news_block = "\n".join(headline_lines)
    else:
        news_block = "No broad-market headlines returned by FMP."

    commentary = (
        f"Markets are {direction} on the major index tape, with the S&P 500 "
        f"{'above' if technical['sma_5'] and row_value(spx, 'price') and float(row_value(spx, 'price')) > technical['sma_5'] else 'near or below'} "
        "its 5-day average. "
        f"Sector leadership is led by {best_sector_name}, while {worst_sector_name} is lagging. "
        f"VIX is {vix_state}, which keeps the risk backdrop "
        f"{'calmer' if vix_state in ('low', 'normal') else 'more defensive'}."
    )

    report = f"""# Daily Market Recap - {recap_date}

## Executive Summary

{summary}

## Market Indices

{index_table}

## Key ETFs

{etf_table}

## Volatility

- VIX: **{fmt_num(vix_float)}** ({vix_state}); day change {fmt_pct(row_value(vix, "changesPercentage", "changePercentage"))}

## Sector Leadership

- Best sector: **{best_sector_name}** ({fmt_pct(best_sector_perf)})
- Worst sector: **{worst_sector_name}** ({fmt_pct(worst_sector_perf)})
- Sector data date: {sector_date}

## Top Movers

- Hot stock: **{hot_symbol}** ({fmt_pct(hot_change)})
- Biggest loser: **{loser_symbol}** ({fmt_pct(loser_change)})

## Technical Posture - S&P 500

- Trend: **{technical["trend"]}**
- Current level: {fmt_num(row_value(spx, "price"))}
- 5-day average: {fmt_num(technical["sma_5"])}
- 20-day average: {fmt_num(technical["sma_20"])}
- 20-day resistance: {fmt_num(technical["resistance"])}
- 20-day support: {fmt_num(technical["support"])}

## Earnings Calendar - Next 7 Days

{earnings_table}

## Market Drivers From Headlines

{news_block}

## Commentary

{commentary}

## Data Notes

- Market data source: Financial Modeling Prep.
- Technical levels are based on recent S&P 500 daily closes.
- Sector snapshot falls back to the most recent available date when same-day data is unavailable.

## Disclaimer

This recap is for informational purposes only and is not investment advice, an offer, or a solicitation to buy or sell securities or derivatives. Verify market data before making trading decisions.
"""
    return summary, report


def send_telegram_message(bot_token: str, chat_id: str, text: str) -> None:
    response = requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={"chat_id": chat_id, "text": text[:4096]},
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        raise RuntimeError(f"Telegram sendMessage failed: {payload}")


def send_telegram_document(bot_token: str, chat_id: str, path: Path, caption: str) -> None:
    with path.open("rb") as handle:
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendDocument",
            data={"chat_id": chat_id, "caption": caption[:1024]},
            files={"document": (path.name, handle, "text/markdown")},
            timeout=30,
        )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        raise RuntimeError(f"Telegram sendDocument failed: {payload}")


def generate_recap(args: argparse.Namespace) -> RecapResult:
    if not args.fmp_api_key:
        raise RuntimeError("FMP_API_KEY is required or pass --fmp-api-key")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    quote_rows = fmp_get(FMP_V3, f"/quote/{INDEX_SYMBOLS}", args.fmp_api_key)
    quotes = quote_by_symbol(quote_rows)
    earnings = earnings_rows(
        fmp_get(
            FMP_V3,
            "/earning_calendar",
            args.fmp_api_key,
            {
                "from": args.date,
                "to": (datetime.strptime(args.date, "%Y-%m-%d").date() + timedelta(days=7)).isoformat(),
            },
        )
    )
    gainer = first_row(fmp_get(FMP_STABLE, "/biggest-gainers", args.fmp_api_key))
    loser = first_row(fmp_get(FMP_STABLE, "/biggest-losers", args.fmp_api_key))
    best_sector, worst_sector, sector_date = fetch_sector_snapshot(args.fmp_api_key, args.date)
    history = fetch_history(args.fmp_api_key, args.date)
    spx_price = row_value(quotes.get("^GSPC", {}), "price")
    current_spx = float(spx_price) if spx_price is not None else None
    technical = technicals(history, current_spx)
    try:
        headlines = news_rows(
            fmp_get(
                FMP_STABLE,
                "/news/general-latest",
                args.fmp_api_key,
                {"page": 0, "limit": 5},
            )
        )
    except requests.RequestException:
        headlines = []

    summary, report = build_report(
        args.date,
        quotes,
        best_sector,
        worst_sector,
        sector_date,
        gainer,
        loser,
        earnings,
        headlines,
        technical,
    )

    report_path = out_dir / f"daily-market-recap-{args.date}.md"
    report_path.write_text(report, encoding="utf-8")

    telegram_sent = False
    if not args.skip_telegram:
        if not args.telegram_bot_token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is required unless --skip-telegram is set")
        if not args.telegram_chat_id:
            raise RuntimeError(
                "Telegram chat id is required via TELEGRAM_CHAT_ID, TELEGRAM_MARKET_CHAT_ID, "
                "TELEGRAM_CHANNEL_ID, or --telegram-chat-id"
            )
        send_telegram_message(args.telegram_bot_token, args.telegram_chat_id, summary)
        send_telegram_document(
            args.telegram_bot_token,
            args.telegram_chat_id,
            report_path,
            f"Daily market recap markdown - {args.date}",
        )
        telegram_sent = True

    return RecapResult(report_path=report_path, summary=summary, telegram_sent=telegram_sent)


def main() -> int:
    args = parse_args()
    try:
        result = generate_recap(args)
    except Exception as exc:
        print(f"daily_market_recap error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(
            json.dumps(
                {
                    "report_path": str(result.report_path),
                    "summary": result.summary,
                    "telegram_sent": result.telegram_sent,
                },
                indent=2,
            )
        )
    else:
        print(result.summary)
        print(f"Report: {result.report_path}")
        print(f"Telegram sent: {'yes' if result.telegram_sent else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
