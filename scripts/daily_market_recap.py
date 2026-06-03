#!/usr/bin/env python3
"""Generate and optionally send the Altamira daily market recap."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests


WORKSPACE = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = WORKSPACE / "outputs"
FMP_V3 = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"
ET = ZoneInfo("America/New_York")
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


@dataclass
class Quote:
    symbol: str
    name: str
    price: float | None
    change_pct: float | None


def get_json(url: str, params: dict[str, Any], timeout: int = 20) -> Any:
    """Fetch JSON and raise a concise error if the API call fails."""
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


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


def fmt_number(value: float | None, decimals: int = 2) -> str:
    if value is None:
        return "N/A"
    return f"{value:,.{decimals}f}"


def fmt_pct(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:+.2f}%"


def pct_direction(value: float | None) -> str:
    if value is None:
        return "flat"
    if value > 0.15:
        return "higher"
    if value < -0.15:
        return "lower"
    return "little changed"


def vix_label(value: float | None) -> str:
    if value is None:
        return "unknown"
    if value >= 25:
        return "elevated"
    if value >= 20:
        return "firm"
    if value < 15:
        return "low"
    return "normal"


def quote_from_row(row: dict[str, Any], fallback_name: str | None = None) -> Quote:
    return Quote(
        symbol=str(row.get("symbol") or ""),
        name=str(row.get("name") or fallback_name or row.get("symbol") or ""),
        price=as_float(row.get("price") or row.get("previousClose") or row.get("open")),
        change_pct=as_float(row.get("changesPercentage") or row.get("changePercentage")),
    )


def fetch_quotes(api_key: str) -> dict[str, Quote]:
    symbols = "^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ"
    data = get_json(f"{FMP_V3}/quote/{symbols}", {"apikey": api_key})
    if not isinstance(data, list):
        data = []
    names = {
        "^GSPC": "S&P 500",
        "^DJI": "Dow Jones Industrial Average",
        "^IXIC": "Nasdaq Composite",
        "^VIX": "CBOE Volatility Index",
        "SPY": "SPDR S&P 500 ETF",
        "QQQ": "Invesco QQQ Trust",
    }
    return {row.get("symbol"): quote_from_row(row, names.get(row.get("symbol"))) for row in data}


def normalize_rows(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        for key in ("data", "sectors", "historical"):
            value = data.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, dict)]
        rows: list[dict[str, Any]] = []
        for key, value in data.items():
            if isinstance(value, dict):
                row = {"sector": key}
                row.update(value)
                rows.append(row)
            else:
                rows.append({"sector": key, "changesPercentage": value})
        return rows
    return []


def fetch_gainers_losers(api_key: str) -> tuple[Quote | None, Quote | None]:
    gainers = normalize_rows(get_json(f"{FMP_STABLE}/biggest-gainers", {"apikey": api_key}))
    losers = normalize_rows(get_json(f"{FMP_STABLE}/biggest-losers", {"apikey": api_key}))
    hot = quote_from_row(gainers[0]) if gainers else None
    loser = quote_from_row(losers[0]) if losers else None
    return hot, loser


def fetch_sector_snapshot(api_key: str, date_str: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    for offset in range(0, 5):
        query_date = (datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=offset)).strftime("%Y-%m-%d")
        rows = normalize_rows(
            get_json(
                f"{FMP_STABLE}/sector-performance-snapshot",
                {"date": query_date, "apikey": api_key},
            )
        )
        parsed: list[dict[str, Any]] = []
        for row in rows:
            sector = row.get("sector") or row.get("sectorName") or row.get("name")
            change = as_float(
                row.get("changesPercentage")
                or row.get("changePercentage")
                or row.get("performance")
                or row.get("oneDayPerformance")
            )
            if sector and change is not None:
                parsed.append({"sector": str(sector), "change_pct": change, "date": query_date})
        if parsed:
            parsed.sort(key=lambda item: item["change_pct"])
            return parsed[-1], parsed[0]
    return fetch_sector_etf_snapshot(api_key)


def fetch_sector_etf_snapshot(api_key: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    data = get_json(f"{FMP_V3}/quote/{','.join(SECTOR_ETFS)}", {"apikey": api_key})
    rows = normalize_rows(data)
    parsed: list[dict[str, Any]] = []
    for row in rows:
        symbol = row.get("symbol")
        change = as_float(row.get("changesPercentage") or row.get("changePercentage"))
        if symbol in SECTOR_ETFS and change is not None:
            parsed.append(
                {
                    "sector": SECTOR_ETFS[symbol],
                    "change_pct": change,
                    "date": "sector ETF proxy",
                    "symbol": symbol,
                }
            )
    if parsed:
        parsed.sort(key=lambda item: item["change_pct"])
        return parsed[-1], parsed[0]
    return None, None


def fetch_history(api_key: str, symbol: str, date_str: str) -> list[dict[str, Any]]:
    to_date = date_str
    from_date = (datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=45)).strftime("%Y-%m-%d")
    data = get_json(
        f"{FMP_STABLE}/historical-price-eod/light",
        {"symbol": symbol, "from": from_date, "to": to_date, "apikey": api_key},
    )
    rows = normalize_rows(data)
    rows = [row for row in rows if row.get("date") and as_float(row.get("close") or row.get("adjClose")) is not None]
    rows.sort(key=lambda row: row["date"])
    return rows


def moving_average(values: list[float], length: int) -> float | None:
    if len(values) < length:
        return None
    return sum(values[-length:]) / length


def technicals_from_history(history: list[dict[str, Any]], current_price: float | None) -> dict[str, Any]:
    closes = [as_float(row.get("close") or row.get("adjClose")) for row in history]
    closes = [close for close in closes if close is not None]
    ma_5 = moving_average(closes, 5)
    ma_20 = moving_average(closes, 20)
    last_20 = closes[-20:] if len(closes) >= 20 else closes
    support = min(last_20) if last_20 else None
    resistance = max(last_20) if last_20 else None
    if current_price is None or ma_5 is None or ma_20 is None:
        trend = "Unknown"
    elif current_price > ma_5 and current_price > ma_20:
        trend = "Bullish"
    elif current_price < ma_5 and current_price < ma_20:
        trend = "Bearish"
    else:
        trend = "Mixed"
    return {"ma_5": ma_5, "ma_20": ma_20, "support": support, "resistance": resistance, "trend": trend}


def fetch_earnings(api_key: str, date_str: str) -> list[dict[str, Any]]:
    to_date = (datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")
    rows = normalize_rows(get_json(f"{FMP_V3}/earning_calendar", {"from": date_str, "to": to_date, "apikey": api_key}))
    filtered = [
        row
        for row in rows
        if row.get("symbol")
        and "." not in str(row.get("symbol"))
        and len(str(row.get("symbol"))) <= 5
        and row.get("date")
    ]
    filtered.sort(key=lambda row: (str(row.get("date")), str(row.get("symbol"))))
    return filtered[:20]


def fetch_news(api_key: str) -> list[dict[str, Any]]:
    rows = normalize_rows(
        get_json(
            f"{FMP_STABLE}/news/general-latest",
            {"page": 0, "limit": 10, "apikey": api_key},
        )
    )
    return rows[:6]


def format_earnings_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "No major earnings found for the next 7 days.\n"
    lines = [
        "| Date | Symbol | EPS estimate | Revenue estimate |",
        "|---|---:|---:|---:|",
    ]
    for row in rows:
        eps = as_float(row.get("epsEstimated"))
        revenue = as_float(row.get("revenueEstimated"))
        revenue_text = "N/A" if revenue is None else f"${revenue / 1_000_000:,.1f}M"
        lines.append(
            f"| {str(row.get('date', ''))[:10]} | {row.get('symbol', 'N/A')} | "
            f"{fmt_number(eps, 2)} | {revenue_text} |"
        )
    return "\n".join(lines) + "\n"


def format_news(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "- No market headlines returned by FMP.\n"
    lines = []
    for row in rows[:5]:
        title = row.get("title") or row.get("headline") or "Untitled"
        site = row.get("site") or row.get("publisher") or "FMP"
        published = str(row.get("publishedDate") or row.get("date") or "")[:16]
        lines.append(f"- {title} ({site}{', ' + published if published else ''})")
    return "\n".join(lines) + "\n"


def build_commentary(
    quotes: dict[str, Quote],
    best_sector: dict[str, Any] | None,
    worst_sector: dict[str, Any] | None,
    hot_stock: Quote | None,
    loser: Quote | None,
    trend: str,
) -> str:
    spx = quotes.get("^GSPC")
    nasdaq = quotes.get("^IXIC")
    vix = quotes.get("^VIX")
    spx_direction = pct_direction(spx.change_pct if spx else None)
    nasdaq_direction = pct_direction(nasdaq.change_pct if nasdaq else None)
    parts = [
        f"The S&P 500 is {spx_direction} at {fmt_number(spx.price if spx else None)} "
        f"({fmt_pct(spx.change_pct if spx else None)}), while the Nasdaq is {nasdaq_direction} "
        f"({fmt_pct(nasdaq.change_pct if nasdaq else None)})."
    ]
    parts.append(
        f"VIX is {vix_label(vix.price if vix else None)} at {fmt_number(vix.price if vix else None)}, "
        f"and the S&P 500 technical read is {trend}."
    )
    if best_sector and worst_sector:
        parts.append(
            f"Sector leadership is {best_sector['sector']} ({fmt_pct(best_sector['change_pct'])}) "
            f"versus weakness in {worst_sector['sector']} ({fmt_pct(worst_sector['change_pct'])})."
        )
    if hot_stock or loser:
        parts.append(
            f"Top single-name mover: {hot_stock.symbol if hot_stock else 'N/A'} "
            f"({fmt_pct(hot_stock.change_pct if hot_stock else None)}); biggest loser: "
            f"{loser.symbol if loser else 'N/A'} ({fmt_pct(loser.change_pct if loser else None)})."
        )
    return " ".join(parts)


def quote_line(label: str, quote: Quote | None) -> str:
    if quote is None:
        return f"| {label} | N/A | N/A |"
    return f"| {label} | {fmt_number(quote.price)} | {fmt_pct(quote.change_pct)} |"


def build_markdown(
    *,
    date_str: str,
    generated_at: datetime,
    quotes: dict[str, Quote],
    hot_stock: Quote | None,
    loser: Quote | None,
    best_sector: dict[str, Any] | None,
    worst_sector: dict[str, Any] | None,
    technicals: dict[str, Any],
    earnings: list[dict[str, Any]],
    news: list[dict[str, Any]],
) -> tuple[str, str]:
    spx = quotes.get("^GSPC")
    vix = quotes.get("^VIX")
    technical_source = str(technicals.get("source_symbol") or "^GSPC")
    technical_label = "SPY proxy" if technical_source == "SPY" else "S&P 500"
    technical_quote = quotes.get("SPY") if technical_source == "SPY" else quotes.get("^GSPC")
    trend_text = str(technicals.get("trend", "Unknown"))
    if technical_source == "SPY":
        trend_text = f"{trend_text} (SPY proxy)"
    commentary = build_commentary(
        quotes,
        best_sector,
        worst_sector,
        hot_stock,
        loser,
        trend_text,
    )
    summary = (
        f"Altamira Daily Market Recap - {date_str}\n"
        f"S&P 500: {fmt_number(spx.price if spx else None)} ({fmt_pct(spx.change_pct if spx else None)}); "
        f"Trend: {trend_text}; "
        f"VIX: {fmt_number(vix.price if vix else None)} ({vix_label(vix.price if vix else None)}).\n"
        f"Best sector: {best_sector['sector'] if best_sector else 'N/A'} "
        f"({fmt_pct(best_sector['change_pct'] if best_sector else None)}); "
        f"worst sector: {worst_sector['sector'] if worst_sector else 'N/A'} "
        f"({fmt_pct(worst_sector['change_pct'] if worst_sector else None)}).\n"
        f"Hot stock: {hot_stock.symbol if hot_stock else 'N/A'} "
        f"({fmt_pct(hot_stock.change_pct if hot_stock else None)}); "
        f"biggest loser: {loser.symbol if loser else 'N/A'} "
        f"({fmt_pct(loser.change_pct if loser else None)}).\n"
        "Informational only; not investment advice."
    )

    generated_text = generated_at.strftime("%Y-%m-%d %H:%M %Z")
    best_sector_note = (
        f"{best_sector['sector']} ({fmt_pct(best_sector['change_pct'])}, {best_sector['date']})"
        if best_sector
        else "N/A"
    )
    worst_sector_note = (
        f"{worst_sector['sector']} ({fmt_pct(worst_sector['change_pct'])}, {worst_sector['date']})"
        if worst_sector
        else "N/A"
    )
    md = f"""# Daily Market Recap - {date_str}

Generated: {generated_text}

## Executive Summary

{commentary}

## Market Indices

| Index / ETF | Level | Day Change |
|---|---:|---:|
{quote_line("S&P 500", quotes.get("^GSPC"))}
{quote_line("Nasdaq Composite", quotes.get("^IXIC"))}
{quote_line("Dow Jones Industrial Average", quotes.get("^DJI"))}
{quote_line("SPY", quotes.get("SPY"))}
{quote_line("QQQ", quotes.get("QQQ"))}
{quote_line("VIX", quotes.get("^VIX"))}

## Movers and Sector Rotation

- **Hot stock:** {hot_stock.symbol if hot_stock else "N/A"} ({fmt_pct(hot_stock.change_pct if hot_stock else None)})
- **Biggest loser:** {loser.symbol if loser else "N/A"} ({fmt_pct(loser.change_pct if loser else None)})
- **Best sector:** {best_sector_note}
- **Worst sector:** {worst_sector_note}

## Technical Snapshot

- **Technical source:** {technical_label}
- **{technical_label} vs 5D average:** {fmt_number(technical_quote.price if technical_quote else None)} vs {fmt_number(technicals.get("ma_5"))}
- **{technical_label} vs 20D average:** {fmt_number(technical_quote.price if technical_quote else None)} vs {fmt_number(technicals.get("ma_20"))}
- **20D resistance:** {fmt_number(technicals.get("resistance"))}
- **20D support:** {fmt_number(technicals.get("support"))}
- **Trend:** {trend_text}

## Market Drivers / Headlines

{format_news(news)}
## Earnings Calendar (Next 7 Days)

{format_earnings_table(earnings)}
## Commentary

{commentary}

## Disclosure

This recap is for informational purposes only and is not investment advice or a recommendation to buy, sell, or hold any security or derivative.
"""
    return summary, md


def send_telegram_message(token: str, chat_id: str, text: str) -> dict[str, Any]:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": "true",
        },
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        raise RuntimeError(f"Telegram sendMessage failed: {payload}")
    return payload


def send_telegram_document(token: str, chat_id: str, path: Path, caption: str) -> dict[str, Any]:
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    with path.open("rb") as handle:
        response = requests.post(
            url,
            data={"chat_id": chat_id, "caption": caption},
            files={"document": (path.name, handle, "text/markdown")},
            timeout=30,
        )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        raise RuntimeError(f"Telegram sendDocument failed: {payload}")
    return payload


def require_env_or_arg(value: str | None, env_name: str, label: str) -> str:
    resolved = value or os.environ.get(env_name)
    if not resolved:
        raise SystemExit(f"Missing {label}. Set {env_name} or pass the corresponding CLI flag.")
    return resolved


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Altamira daily market recap and optionally send it to Telegram.")
    parser.add_argument("--date", help="Report date in YYYY-MM-DD format; defaults to today's ET date.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output directory for Markdown report.")
    parser.add_argument("--fmp-api-key", help="FMP API key. Defaults to FMP_API_KEY environment variable.")
    parser.add_argument("--send-telegram", action="store_true", help="Send summary and Markdown file to Telegram.")
    parser.add_argument("--telegram-bot-token", help="Telegram bot token. Defaults to TELEGRAM_BOT_TOKEN environment variable.")
    parser.add_argument("--telegram-chat-id", help="Telegram channel/chat id. Defaults to TELEGRAM_CHAT_ID environment variable.")
    parser.add_argument("--dry-run", action="store_true", help="Generate files and print summary without sending Telegram messages.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generated_at = datetime.now(ET)
    date_str = args.date or generated_at.strftime("%Y-%m-%d")
    datetime.strptime(date_str, "%Y-%m-%d")

    api_key = require_env_or_arg(args.fmp_api_key, "FMP_API_KEY", "FMP API key")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    quotes = fetch_quotes(api_key)
    hot_stock, loser = fetch_gainers_losers(api_key)
    best_sector, worst_sector = fetch_sector_snapshot(api_key, date_str)
    history = fetch_history(api_key, "^GSPC", date_str)
    technical_symbol = "^GSPC"
    technical_quote = quotes.get("^GSPC")
    if len(history) < 20 and quotes.get("SPY"):
        spy_history = fetch_history(api_key, "SPY", date_str)
        if len(spy_history) >= 20:
            history = spy_history
            technical_symbol = "SPY"
            technical_quote = quotes.get("SPY")
    technicals = technicals_from_history(history, technical_quote.price if technical_quote else None)
    technicals["source_symbol"] = technical_symbol
    earnings = fetch_earnings(api_key, date_str)
    news = fetch_news(api_key)

    summary, markdown = build_markdown(
        date_str=date_str,
        generated_at=generated_at,
        quotes=quotes,
        hot_stock=hot_stock,
        loser=loser,
        best_sector=best_sector,
        worst_sector=worst_sector,
        technicals=technicals,
        earnings=earnings,
        news=news,
    )

    report_path = out_dir / f"daily-market-recap-{date_str}.md"
    report_path.write_text(markdown, encoding="utf-8")
    print(summary)
    print(f"\nReport written: {report_path}")

    if args.send_telegram and not args.dry_run:
        token = require_env_or_arg(args.telegram_bot_token, "TELEGRAM_BOT_TOKEN", "Telegram bot token")
        chat_id = require_env_or_arg(args.telegram_chat_id, "TELEGRAM_CHAT_ID", "Telegram chat id")
        message_payload = send_telegram_message(token, chat_id, summary)
        document_payload = send_telegram_document(
            token,
            chat_id,
            report_path,
            f"Daily market recap Markdown - {date_str}",
        )
        message_id = message_payload.get("result", {}).get("message_id")
        document_id = document_payload.get("result", {}).get("message_id")
        print(f"Telegram summary sent: message_id={message_id}")
        print(f"Telegram document sent: message_id={document_id}")
    elif args.send_telegram and args.dry_run:
        print("Dry run enabled; Telegram send skipped.")


if __name__ == "__main__":
    main()
