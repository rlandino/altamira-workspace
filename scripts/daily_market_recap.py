#!/usr/bin/env python3
"""Generate and optionally send Altamira's daily market recap."""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS = WORKSPACE / "outputs"
FMP_V3 = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"

INDEX_SYMBOLS = {
    "^GSPC": "S&P 500",
    "^DJI": "Dow Jones",
    "^IXIC": "Nasdaq Composite",
    "^RUT": "Russell 2000",
}

ETF_SECTORS = {
    "XLB": "Materials",
    "XLC": "Communication Services",
    "XLY": "Consumer Discretionary",
    "XLP": "Consumer Staples",
    "XLE": "Energy",
    "XLF": "Financials",
    "XLV": "Health Care",
    "XLI": "Industrials",
    "XLRE": "Real Estate",
    "XLK": "Technology",
    "XLU": "Utilities",
}


@dataclass(frozen=True)
class ApiResult:
    data: Any
    error: str = ""


def _legacy_fmp_key() -> str:
    """Read the workspace's existing local-dev fallback key without duplicating it."""
    market_api = WORKSPACE / "scripts" / "market_data_api.py"
    try:
        text = market_api.read_text(encoding="utf-8")
    except OSError:
        return ""
    match = re.search(r'DEFAULT_KEY\s*=\s*os\.environ\.get\("FMP_API_KEY",\s*"([^"]+)"\)', text)
    return match.group(1) if match else ""


def fmp_key() -> str:
    key = os.environ.get("FMP_API_KEY") or _legacy_fmp_key()
    if not key:
        raise SystemExit("FMP_API_KEY is required to fetch market data.")
    return key


def fetch_json(base_url: str, path: str, params: dict[str, Any] | None = None) -> ApiResult:
    query = dict(params or {})
    query["apikey"] = fmp_key()
    url = f"{base_url}{path}"
    try:
        response = requests.get(url, params=query, timeout=20)
        response.raise_for_status()
        return ApiResult(response.json())
    except requests.RequestException as exc:
        return ApiResult(None, str(exc))
    except json.JSONDecodeError as exc:
        return ApiResult(None, f"Invalid JSON from {url}: {exc}")


def as_float(value: Any) -> float | None:
    if value is None:
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


def fmt_pct(value: Any, fallback: str = "N/A") -> str:
    parsed = as_float(value)
    if parsed is None:
        return fallback
    return f"{parsed:+.2f}%"


def fmt_price(value: Any, fallback: str = "N/A") -> str:
    parsed = as_float(value)
    if parsed is None:
        return fallback
    return f"{parsed:,.2f}"


def change_pct(row: dict[str, Any]) -> float | None:
    for key in ("changesPercentage", "changePercentage", "changes", "changePercent", "1D Change"):
        parsed = as_float(row.get(key))
        if parsed is not None:
            return parsed
    return None


def quote_map(symbols: list[str]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    result = fetch_json(FMP_V3, f"/quote/{','.join(symbols)}")
    warnings: list[str] = []
    if result.error:
        warnings.append(f"Quote fetch failed: {result.error}")
        return {}, warnings
    rows = result.data if isinstance(result.data, list) else []
    return {str(row.get("symbol")): row for row in rows if row.get("symbol")}, warnings


def sector_snapshot(report_date: str) -> tuple[list[dict[str, Any]], str, list[str]]:
    warnings: list[str] = []
    result = fetch_json(FMP_STABLE, "/sector-performance-snapshot", {"date": report_date})
    sectors: list[dict[str, Any]] = []
    if not result.error and isinstance(result.data, list):
        for row in result.data:
            name = row.get("sector") or row.get("name") or row.get("sectorName")
            pct = change_pct(row)
            if name and pct is not None:
                sectors.append({"name": str(name), "change_pct": pct, "source": "FMP sector snapshot"})

    non_zero = [row for row in sectors if abs(row["change_pct"]) > 0.0001]
    if non_zero:
        return sorted(sectors, key=lambda row: row["change_pct"], reverse=True), "FMP sector snapshot", warnings

    if result.error:
        warnings.append(f"Sector snapshot failed: {result.error}")
    elif sectors:
        warnings.append("FMP sector snapshot returned all-zero changes; using sector ETF proxy fallback.")
    else:
        warnings.append("FMP sector snapshot unavailable; using sector ETF proxy fallback.")

    quotes, quote_warnings = quote_map(list(ETF_SECTORS))
    warnings.extend(quote_warnings)
    fallback: list[dict[str, Any]] = []
    for symbol, name in ETF_SECTORS.items():
        row = quotes.get(symbol, {})
        pct = change_pct(row)
        if pct is not None:
            fallback.append({"name": name, "symbol": symbol, "change_pct": pct, "source": "sector ETF proxy"})
    return sorted(fallback, key=lambda row: row["change_pct"], reverse=True), "sector ETF proxy", warnings


def market_movers() -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[str]]:
    warnings: list[str] = []
    gainers = fetch_json(FMP_STABLE, "/biggest-gainers")
    losers = fetch_json(FMP_STABLE, "/biggest-losers")
    if gainers.error:
        warnings.append(f"Biggest gainers fetch failed: {gainers.error}")
    if losers.error:
        warnings.append(f"Biggest losers fetch failed: {losers.error}")
    top_gainer = gainers.data[0] if isinstance(gainers.data, list) and gainers.data else None
    top_loser = losers.data[0] if isinstance(losers.data, list) and losers.data else None
    return top_gainer, top_loser, warnings


def historical_spx(report_date: str) -> tuple[list[dict[str, Any]], list[str]]:
    from_date = (datetime.strptime(report_date, "%Y-%m-%d") - timedelta(days=45)).strftime("%Y-%m-%d")
    result = fetch_json(
        FMP_STABLE,
        "/historical-price-eod/light",
        {"symbol": "^GSPC", "from": from_date, "to": report_date},
    )
    if result.error:
        return [], [f"S&P 500 historical fetch failed: {result.error}"]
    rows = result.data if isinstance(result.data, list) else []
    cleaned = []
    for row in rows:
        close = as_float(row.get("close"))
        if close is None:
            close = as_float(row.get("price"))
        cleaned.append(
            {
                "date": row.get("date"),
                "close": close,
                "high": as_float(row.get("high")),
                "low": as_float(row.get("low")),
            }
        )
    cleaned = [row for row in cleaned if row["date"] and row["close"] is not None]
    cleaned.sort(key=lambda row: str(row["date"]))
    if not cleaned:
        return [], ["S&P 500 historical fetch returned no usable close/price rows."]
    return cleaned, []


def moving_average(values: list[float], count: int) -> float | None:
    if len(values) < count:
        return None
    return sum(values[-count:]) / count


def technicals(quotes: dict[str, dict[str, Any]], history: list[dict[str, Any]]) -> dict[str, Any]:
    spx_quote = quotes.get("^GSPC", {})
    current = as_float(spx_quote.get("price"))
    closes = [row["close"] for row in history if row["close"] is not None]
    avg_5 = moving_average(closes, 5)
    avg_20 = moving_average(closes, 20)
    last_20 = history[-20:]
    highs = [row["high"] if row["high"] is not None else row["close"] for row in last_20]
    lows = [row["low"] if row["low"] is not None else row["close"] for row in last_20]
    resistance = max(highs) if highs else None
    support = min(lows) if lows else None

    trend = "N/A"
    if current is not None and avg_5 is not None and avg_20 is not None:
        if current > avg_5 and current > avg_20:
            trend = "Bullish"
        elif current < avg_5 and current < avg_20:
            trend = "Bearish"
        else:
            trend = "Mixed"

    return {
        "current": current,
        "avg_5": avg_5,
        "avg_20": avg_20,
        "support": support,
        "resistance": resistance,
        "trend": trend,
    }


def earnings_calendar(report_date: str) -> tuple[list[dict[str, Any]], list[str]]:
    to_date = (datetime.strptime(report_date, "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")
    result = fetch_json(FMP_V3, "/earning_calendar", {"from": report_date, "to": to_date})
    if result.error:
        return [], [f"Earnings calendar fetch failed: {result.error}"]
    rows = result.data if isinstance(result.data, list) else []
    us_rows = [
        row for row in rows
        if re.fullmatch(r"[A-Z]{1,5}", str(row.get("symbol") or ""))
    ]
    selected = us_rows if us_rows else rows
    selected.sort(key=lambda row: (row.get("date") or "", row.get("symbol") or ""))
    return selected[:20], []


def market_news() -> tuple[list[dict[str, Any]], list[str]]:
    result = fetch_json(FMP_STABLE, "/news/general-latest", {"page": 0, "limit": 8})
    if result.error:
        return [], [f"Market news fetch failed: {result.error}"]
    rows = result.data if isinstance(result.data, list) else []
    return rows[:8], []


def vix_label(value: float | None) -> str:
    if value is None:
        return "N/A"
    if value > 25:
        return "high"
    if value > 20:
        return "elevated"
    if value < 15:
        return "low"
    return "normal"


def index_direction(quotes: dict[str, dict[str, Any]]) -> str:
    changes = [change_pct(quotes.get(symbol, {})) for symbol in INDEX_SYMBOLS]
    valid = [value for value in changes if value is not None]
    if not valid:
        return "mixed"
    positives = sum(1 for value in valid if value > 0)
    negatives = sum(1 for value in valid if value < 0)
    if positives >= 3:
        return "higher"
    if negatives >= 3:
        return "lower"
    return "mixed"


def concise_summary(
    report_date: str,
    quotes: dict[str, dict[str, Any]],
    sectors: list[dict[str, Any]],
    tech: dict[str, Any],
    gainer: dict[str, Any] | None,
    loser: dict[str, Any] | None,
) -> str:
    spx = quotes.get("^GSPC", {})
    nasdaq = quotes.get("^IXIC", {})
    dow = quotes.get("^DJI", {})
    vix = quotes.get("^VIX", {})
    best_sector = sectors[0] if sectors else {}
    worst_sector = sectors[-1] if sectors else {}
    lines = [
        f"Altamira Daily Market Recap - {report_date}",
        (
            f"S&P 500 {fmt_price(spx.get('price'))} ({fmt_pct(change_pct(spx))}); "
            f"Nasdaq {fmt_pct(change_pct(nasdaq))}; Dow {fmt_pct(change_pct(dow))}."
        ),
        f"Trend: {tech['trend']}; VIX {fmt_price(vix.get('price'))} ({vix_label(as_float(vix.get('price')))}).",
    ]
    if best_sector and worst_sector:
        lines.append(
            f"Sector leaders: {best_sector['name']} {fmt_pct(best_sector['change_pct'])}; "
            f"laggard: {worst_sector['name']} {fmt_pct(worst_sector['change_pct'])}."
        )
    if gainer or loser:
        gainer_text = f"{gainer.get('symbol')} {fmt_pct(change_pct(gainer))}" if gainer else "N/A"
        loser_text = f"{loser.get('symbol')} {fmt_pct(change_pct(loser))}" if loser else "N/A"
        lines.append(f"Top mover: {gainer_text}; biggest loser: {loser_text}.")
    lines.append("Full markdown recap is attached.")
    return "\n".join(lines)


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "N/A\n"
    header = "| " + " | ".join(headers) + " |"
    divider = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header, divider, *body]) + "\n"


def build_markdown(
    report_date: str,
    quotes: dict[str, dict[str, Any]],
    sectors: list[dict[str, Any]],
    sector_source: str,
    tech: dict[str, Any],
    gainer: dict[str, Any] | None,
    loser: dict[str, Any] | None,
    earnings: list[dict[str, Any]],
    news: list[dict[str, Any]],
    warnings: list[str],
) -> tuple[str, str]:
    summary = concise_summary(report_date, quotes, sectors, tech, gainer, loser)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    index_rows = []
    for symbol, name in INDEX_SYMBOLS.items():
        row = quotes.get(symbol, {})
        index_rows.append([name, symbol, fmt_price(row.get("price")), fmt_pct(change_pct(row))])

    etf_rows = []
    for symbol in ("SPY", "QQQ", "IWM"):
        row = quotes.get(symbol, {})
        etf_rows.append([symbol, fmt_price(row.get("price")), fmt_pct(change_pct(row))])
    vix = quotes.get("^VIX", {})

    sector_rows = [
        [row["name"], row.get("symbol", ""), fmt_pct(row["change_pct"])]
        for row in sectors[:11]
    ]
    earnings_rows = [
        [
            str(row.get("date") or ""),
            str(row.get("symbol") or ""),
            str(row.get("time") or row.get("epsTime") or ""),
            fmt_price(row.get("epsEstimated"), ""),
            fmt_price(row.get("revenueEstimated"), ""),
        ]
        for row in earnings[:12]
    ]
    news_rows = [
        [str(row.get("publishedDate") or row.get("date") or "")[:10], str(row.get("title") or row.get("headline") or "")[:140]]
        for row in news[:6]
    ]

    top_gainer = f"{gainer.get('symbol')} ({fmt_pct(change_pct(gainer))})" if gainer else "N/A"
    top_loser = f"{loser.get('symbol')} ({fmt_pct(change_pct(loser))})" if loser else "N/A"
    best_sector = f"{sectors[0]['name']} ({fmt_pct(sectors[0]['change_pct'])})" if sectors else "N/A"
    worst_sector = f"{sectors[-1]['name']} ({fmt_pct(sectors[-1]['change_pct'])})" if sectors else "N/A"
    direction = index_direction(quotes)

    commentary = (
        f"Markets are {direction} based on the major index tape. "
        f"The S&P 500 trend reads {tech['trend']} versus its 5-day and 20-day averages, "
        f"while VIX is {vix_label(as_float(vix.get('price')))} at {fmt_price(vix.get('price'))}. "
        f"Sector breadth is led by {best_sector}; {worst_sector} is lagging."
    )

    markdown = f"""# Altamira Daily Market Recap — {report_date}

Generated: {generated}

> This is a market commentary summary for monitoring purposes only, not investment advice.

## Executive Summary

{summary.replace(chr(10), chr(10) + chr(10))}

## Market Indices

{markdown_table(["Index", "Symbol", "Level", "Day Change"], index_rows)}

## ETFs and Volatility

{markdown_table(["Ticker", "Level", "Day Change"], etf_rows)}

- **VIX:** {fmt_price(vix.get("price"))} ({vix_label(as_float(vix.get("price")))}) | Day change: {fmt_pct(change_pct(vix))}

## Sector Performance

Source: {sector_source}

{markdown_table(["Sector", "Proxy", "Day Change"], sector_rows)}

- **Best sector:** {best_sector}
- **Worst sector:** {worst_sector}

## Single-Stock Movers

- **Hot stock:** {top_gainer}
- **Biggest loser:** {top_loser}

## S&P 500 Technical Snapshot

- **Current level:** {fmt_price(tech["current"])}
- **5-day average:** {fmt_price(tech["avg_5"])}
- **20-day average:** {fmt_price(tech["avg_20"])}
- **20-day resistance:** {fmt_price(tech["resistance"])}
- **20-day support:** {fmt_price(tech["support"])}
- **Trend:** {tech["trend"]}

## Earnings Calendar: Next 7 Days

{markdown_table(["Date", "Ticker", "Time", "EPS Est.", "Revenue Est."], earnings_rows)}

## Market Drivers / Headlines

{markdown_table(["Date", "Headline"], news_rows)}

## Commentary

{commentary}
"""
    if warnings:
        markdown += "\n## Data Notes\n\n" + "\n".join(f"- {warning}" for warning in warnings) + "\n"
    return markdown, summary


def telegram_credentials(chat_id: str | None = None) -> tuple[str, str]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_API_TOKEN")
    resolved_chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN or TELEGRAM_API_TOKEN is required for Telegram delivery.")
    if not resolved_chat_id:
        raise SystemExit("TELEGRAM_CHAT_ID or --telegram-chat-id is required for Telegram delivery.")
    return token, resolved_chat_id


def send_telegram(summary: str, markdown_path: Path, chat_id: str | None = None) -> None:
    token, resolved_chat_id = telegram_credentials(chat_id)
    base = f"https://api.telegram.org/bot{token}"
    message_response = requests.post(
        f"{base}/sendMessage",
        data={"chat_id": resolved_chat_id, "text": summary, "disable_web_page_preview": True},
        timeout=20,
    )
    message_response.raise_for_status()

    with markdown_path.open("rb") as handle:
        document_response = requests.post(
            f"{base}/sendDocument",
            data={"chat_id": resolved_chat_id, "caption": f"Daily market recap: {markdown_path.name}"},
            files={"document": (markdown_path.name, handle, "text/markdown")},
            timeout=30,
        )
    document_response.raise_for_status()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Altamira's daily market recap.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Report date YYYY-MM-DD (default: today)")
    parser.add_argument("--send-telegram", action="store_true", help="Send summary and markdown file to Telegram")
    parser.add_argument("--telegram-chat-id", default=None, help="Telegram chat/channel id override")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report_date = args.date
    OUTPUTS.mkdir(parents=True, exist_ok=True)

    quote_symbols = [*INDEX_SYMBOLS.keys(), "^VIX", "SPY", "QQQ", "IWM"]
    quotes, warnings = quote_map(quote_symbols)
    sectors, sector_source, sector_warnings = sector_snapshot(report_date)
    gainer, loser, mover_warnings = market_movers()
    history, history_warnings = historical_spx(report_date)
    earnings, earnings_warnings = earnings_calendar(report_date)
    news, news_warnings = market_news()
    warnings.extend(sector_warnings + mover_warnings + history_warnings + earnings_warnings + news_warnings)

    tech = technicals(quotes, history)
    markdown, summary = build_markdown(
        report_date,
        quotes,
        sectors,
        sector_source,
        tech,
        gainer,
        loser,
        earnings,
        news,
        warnings,
    )

    output_path = OUTPUTS / f"daily-market-recap-{report_date}.md"
    output_path.write_text(markdown, encoding="utf-8")

    print(summary)
    print(f"\nReport saved to {output_path}")

    if args.send_telegram:
        send_telegram(summary, output_path, args.telegram_chat_id)
        print("Telegram summary and markdown document sent successfully.")


if __name__ == "__main__":
    main()
