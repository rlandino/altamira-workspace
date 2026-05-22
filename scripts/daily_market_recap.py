#!/usr/bin/env python3
"""Generate a daily market recap and optionally send it to Telegram."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote
from xml.etree import ElementTree

import requests


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS = WORKSPACE / "outputs"
FMP_V3 = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"
YAHOO_CHART = "https://query1.finance.yahoo.com/v8/finance/chart"
YAHOO_SCREENER = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved"
YAHOO_NEWS_RSS = "https://feeds.finance.yahoo.com/rss/2.0/headline"
TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"


INDEX_SYMBOLS = {
    "^GSPC": "S&P 500",
    "^IXIC": "Nasdaq Composite",
    "^DJI": "Dow Jones",
}
WATCH_SYMBOLS = {
    "SPY": "SPY",
    "QQQ": "QQQ",
    "^VIX": "VIX",
}
SECTOR_ETFS = {
    "XLK": "Technology",
    "XLC": "Communication Services",
    "XLY": "Consumer Discretionary",
    "XLP": "Consumer Staples",
    "XLE": "Energy",
    "XLF": "Financials",
    "XLV": "Health Care",
    "XLI": "Industrials",
    "XLB": "Materials",
    "XLRE": "Real Estate",
    "XLU": "Utilities",
}


@dataclass
class Quote:
    symbol: str
    name: str
    price: float | None
    previous_close: float | None
    change_percent: float | None
    source: str


@dataclass
class Technicals:
    close: float | None
    sma_5: float | None
    sma_20: float | None
    support: float | None
    resistance: float | None
    trend: str


def request_json(url: str, params: dict[str, Any] | None = None) -> Any:
    """Return JSON from a GET request with a browser-like user agent."""
    headers = {"User-Agent": "AltamiraMarketRecap/1.0"}
    response = requests.get(url, params=params, headers=headers, timeout=20)
    response.raise_for_status()
    return response.json()


def fmp_key() -> str | None:
    """Read an FMP key from the environment."""
    return os.environ.get("FMP_API_KEY") or os.environ.get("FMP_KEY")


def fetch_fmp_quotes(symbols: list[str], names: dict[str, str]) -> dict[str, Quote]:
    """Fetch quotes from FMP when an API key is configured."""
    key = fmp_key()
    if not key:
        return {}
    try:
        data = request_json(f"{FMP_V3}/quote/{','.join(symbols)}", {"apikey": key})
    except Exception as exc:
        print(f"[daily_market_recap] FMP quote fetch failed: {exc}", file=sys.stderr)
        return {}
    quotes: dict[str, Quote] = {}
    if not isinstance(data, list):
        return quotes
    for row in data:
        symbol = str(row.get("symbol") or "")
        if not symbol:
            continue
        price = as_float(row.get("price"))
        previous_close = as_float(row.get("previousClose"))
        change_percent = as_float(row.get("changesPercentage"))
        if change_percent is None and price is not None and previous_close:
            change_percent = ((price - previous_close) / previous_close) * 100
        quotes[symbol] = Quote(
            symbol=symbol,
            name=names.get(symbol, symbol),
            price=price,
            previous_close=previous_close,
            change_percent=change_percent,
            source="FMP",
        )
    return quotes


def fetch_yahoo_quote(symbol: str, name: str) -> Quote | None:
    """Fetch a quote from Yahoo Chart as a no-key fallback."""
    url = f"{YAHOO_CHART}/{quote(symbol, safe='')}"
    try:
        data = request_json(url, {"range": "5d", "interval": "1d"})
        result = data["chart"]["result"][0]
        meta = result.get("meta", {})
    except Exception as exc:
        print(f"[daily_market_recap] Yahoo quote fetch failed for {symbol}: {exc}", file=sys.stderr)
        return None

    price = as_float(meta.get("regularMarketPrice"))
    previous_close = as_float(meta.get("chartPreviousClose") or meta.get("previousClose"))
    change_percent = None
    if price is not None and previous_close:
        change_percent = ((price - previous_close) / previous_close) * 100
    return Quote(
        symbol=symbol,
        name=name,
        price=price,
        previous_close=previous_close,
        change_percent=change_percent,
        source="Yahoo",
    )


def fetch_quotes(symbols: dict[str, str]) -> dict[str, Quote]:
    """Fetch quotes, preferring FMP and falling back to Yahoo."""
    quotes = fetch_fmp_quotes(list(symbols.keys()), symbols)
    for symbol, name in symbols.items():
        if symbol in quotes and quotes[symbol].price is not None:
            continue
        yahoo_quote = fetch_yahoo_quote(symbol, name)
        if yahoo_quote:
            quotes[symbol] = yahoo_quote
    return quotes


def fetch_sp500_technicals() -> Technicals:
    """Compute 5D/20D averages and recent support/resistance for the S&P 500."""
    url = f"{YAHOO_CHART}/{quote('^GSPC', safe='')}"
    try:
        data = request_json(url, {"range": "2mo", "interval": "1d"})
        quote_data = data["chart"]["result"][0]["indicators"]["quote"][0]
        closes = [as_float(value) for value in quote_data.get("close", [])]
        highs = [as_float(value) for value in quote_data.get("high", [])]
        lows = [as_float(value) for value in quote_data.get("low", [])]
    except Exception as exc:
        print(f"[daily_market_recap] Technical fetch failed: {exc}", file=sys.stderr)
        return Technicals(None, None, None, None, None, "Unavailable")

    closes = [value for value in closes if value is not None]
    highs = [value for value in highs if value is not None]
    lows = [value for value in lows if value is not None]
    close = closes[-1] if closes else None
    sma_5 = average(closes[-5:])
    sma_20 = average(closes[-20:])
    support = min(lows[-20:]) if lows else None
    resistance = max(highs[-20:]) if highs else None

    if close is None or sma_5 is None or sma_20 is None:
        trend = "Unavailable"
    elif close > sma_5 and close > sma_20:
        trend = "Bullish"
    elif close < sma_5 and close < sma_20:
        trend = "Bearish"
    else:
        trend = "Mixed"
    return Technicals(close, sma_5, sma_20, support, resistance, trend)


def fetch_yahoo_screener(scr_id: str) -> dict[str, Any] | None:
    """Fetch the first result from a Yahoo predefined screener."""
    try:
        data = request_json(YAHOO_SCREENER, {"scrIds": scr_id, "count": 1})
        quotes = data["finance"]["result"][0].get("quotes", [])
        return quotes[0] if quotes else None
    except Exception as exc:
        print(f"[daily_market_recap] Yahoo screener fetch failed for {scr_id}: {exc}", file=sys.stderr)
        return None


def fetch_fmp_mover(path: str) -> dict[str, Any] | None:
    """Fetch the first gainer/loser from FMP when configured."""
    key = fmp_key()
    if not key:
        return None
    try:
        data = request_json(f"{FMP_STABLE}/{path}", {"apikey": key})
    except Exception as exc:
        print(f"[daily_market_recap] FMP {path} fetch failed: {exc}", file=sys.stderr)
        return None
    if isinstance(data, list) and data:
        return data[0]
    return None


def fetch_movers() -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Return top gainer and loser from configured data sources."""
    gainer = fetch_fmp_mover("biggest-gainers") or fetch_yahoo_screener("day_gainers")
    loser = fetch_fmp_mover("biggest-losers") or fetch_yahoo_screener("day_losers")
    return gainer, loser


def fetch_headlines(limit: int = 5) -> list[str]:
    """Fetch broad market headlines without requiring an API key."""
    key = fmp_key()
    if key:
        try:
            data = request_json(f"{FMP_STABLE}/news/general-latest", {"page": 0, "limit": limit, "apikey": key})
            if isinstance(data, list):
                return [str(row.get("title")) for row in data if row.get("title")][:limit]
        except Exception as exc:
            print(f"[daily_market_recap] FMP news fetch failed: {exc}", file=sys.stderr)

    try:
        response = requests.get(
            YAHOO_NEWS_RSS,
            params={"s": "SPY", "region": "US", "lang": "en-US"},
            headers={"User-Agent": "AltamiraMarketRecap/1.0"},
            timeout=20,
        )
        response.raise_for_status()
        root = ElementTree.fromstring(response.text)
        titles = [item.findtext("title") for item in root.findall(".//item")]
        return [title for title in titles if title][:limit]
    except Exception as exc:
        print(f"[daily_market_recap] Yahoo news fetch failed: {exc}", file=sys.stderr)
        return []


def fetch_earnings(start_date: str, days: int = 7) -> list[dict[str, Any]]:
    """Fetch the earnings calendar when FMP credentials are available."""
    key = fmp_key()
    if not key:
        return []
    end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=days)).strftime("%Y-%m-%d")
    try:
        data = request_json(
            f"{FMP_V3}/earning_calendar",
            {"from": start_date, "to": end_date, "apikey": key},
        )
    except Exception as exc:
        print(f"[daily_market_recap] FMP earnings fetch failed: {exc}", file=sys.stderr)
        return []
    return data[:20] if isinstance(data, list) else []


def average(values: list[float]) -> float | None:
    """Return the arithmetic average of a non-empty list."""
    if not values:
        return None
    return sum(values) / len(values)


def as_float(value: Any) -> float | None:
    """Convert a value to float, returning None for missing or invalid values."""
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def fmt_number(value: float | None) -> str:
    """Format a market level."""
    return "N/A" if value is None else f"{value:,.2f}"


def fmt_percent(value: float | None) -> str:
    """Format a percentage with sign."""
    return "N/A" if value is None else f"{value:+.2f}%"


def fmt_mover(row: dict[str, Any] | None) -> str:
    """Format a gainer/loser row."""
    if not row:
        return "Unavailable"
    symbol = row.get("symbol") or row.get("ticker") or row.get("shortName") or "N/A"
    name = row.get("name") or row.get("shortName") or row.get("longName") or ""
    change = (
        as_float(row.get("changesPercentage"))
        or as_float(row.get("regularMarketChangePercent"))
        or as_float(row.get("changePercent"))
    )
    name_part = f" ({name})" if name and name != symbol else ""
    return f"{symbol}{name_part}: {fmt_percent(change)}"


def vix_label(vix: Quote | None) -> str:
    """Return a concise VIX regime label."""
    if not vix or vix.price is None:
        return "Unavailable"
    if vix.price < 15:
        return "Low"
    if vix.price > 20:
        return "Elevated"
    return "Normal"


def direction_label(quotes: dict[str, Quote]) -> str:
    """Classify the broad index tape."""
    changes = [quotes[symbol].change_percent for symbol in INDEX_SYMBOLS if symbol in quotes]
    numeric = [change for change in changes if change is not None]
    if not numeric:
        return "unavailable"
    positive = sum(1 for change in numeric if change > 0.05)
    negative = sum(1 for change in numeric if change < -0.05)
    if positive == len(numeric):
        return "higher"
    if negative == len(numeric):
        return "lower"
    return "mixed"


def quote_table(quotes: dict[str, Quote], order: list[str]) -> str:
    """Build a markdown quote table."""
    lines = ["| Instrument | Level | Day Change | Source |", "|---|---:|---:|---|"]
    for symbol in order:
        quote_obj = quotes.get(symbol)
        if not quote_obj:
            lines.append(f"| {symbol} | N/A | N/A | N/A |")
            continue
        lines.append(
            f"| {quote_obj.name} ({quote_obj.symbol}) | {fmt_number(quote_obj.price)} | "
            f"{fmt_percent(quote_obj.change_percent)} | {quote_obj.source} |"
        )
    return "\n".join(lines)


def sector_table(sector_quotes: dict[str, Quote]) -> tuple[str, Quote | None, Quote | None]:
    """Build a sector markdown table and identify leaders/laggards."""
    sectors = [
        quote_obj
        for quote_obj in sector_quotes.values()
        if quote_obj.change_percent is not None
    ]
    sectors.sort(key=lambda item: item.change_percent or 0, reverse=True)
    best = sectors[0] if sectors else None
    worst = sectors[-1] if sectors else None
    lines = ["| Sector | ETF | Day Change |", "|---|---|---:|"]
    for quote_obj in sectors:
        lines.append(f"| {quote_obj.name} | {quote_obj.symbol} | {fmt_percent(quote_obj.change_percent)} |")
    if not sectors:
        lines.append("| N/A | N/A | N/A |")
    return "\n".join(lines), best, worst


def earnings_table(earnings: list[dict[str, Any]]) -> str:
    """Build a compact earnings calendar table."""
    if not earnings:
        return "Earnings calendar unavailable because `FMP_API_KEY` is not configured or the API returned no events."
    lines = ["| Date | Symbol | EPS Estimate | Revenue Estimate |", "|---|---|---:|---:|"]
    for row in earnings[:12]:
        eps = as_float(row.get("epsEstimated"))
        revenue = as_float(row.get("revenueEstimated"))
        lines.append(
            f"| {row.get('date', 'N/A')} | {row.get('symbol', 'N/A')} | "
            f"{fmt_number(eps)} | {fmt_number(revenue)} |"
        )
    return "\n".join(lines)


def build_summary(
    date_str: str,
    market_quotes: dict[str, Quote],
    sector_best: Quote | None,
    sector_worst: Quote | None,
    gainer: dict[str, Any] | None,
    loser: dict[str, Any] | None,
    technicals: Technicals,
) -> str:
    """Build the Telegram/chat summary."""
    spx = market_quotes.get("^GSPC")
    nasdaq = market_quotes.get("^IXIC")
    dow = market_quotes.get("^DJI")
    vix = market_quotes.get("^VIX")
    parts = [
        f"Daily Market Recap — {date_str}",
        (
            f"S&P 500 {fmt_percent(spx.change_percent if spx else None)}, "
            f"Nasdaq {fmt_percent(nasdaq.change_percent if nasdaq else None)}, "
            f"Dow {fmt_percent(dow.change_percent if dow else None)}; "
            f"trend is {technicals.trend}."
        ),
        (
            f"VIX {fmt_number(vix.price if vix else None)} ({vix_label(vix)}). "
            f"Best sector: {sector_best.name if sector_best else 'N/A'} "
            f"{fmt_percent(sector_best.change_percent if sector_best else None)}; "
            f"worst sector: {sector_worst.name if sector_worst else 'N/A'} "
            f"{fmt_percent(sector_worst.change_percent if sector_worst else None)}."
        ),
        f"Hot stock: {fmt_mover(gainer)}. Biggest loser: {fmt_mover(loser)}.",
    ]
    return "\n".join(parts)


def build_markdown(date_str: str) -> tuple[str, str]:
    """Fetch data and build the markdown recap plus Telegram summary."""
    all_quotes = fetch_quotes({**INDEX_SYMBOLS, **WATCH_SYMBOLS})
    sector_quotes = fetch_quotes(SECTOR_ETFS)
    technicals = fetch_sp500_technicals()
    gainer, loser = fetch_movers()
    headlines = fetch_headlines()
    earnings = fetch_earnings(date_str)
    sector_md, sector_best, sector_worst = sector_table(sector_quotes)
    summary = build_summary(date_str, all_quotes, sector_best, sector_worst, gainer, loser, technicals)

    generated_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    market_direction = direction_label(all_quotes)
    spx = all_quotes.get("^GSPC")
    vix = all_quotes.get("^VIX")

    headline_lines = "\n".join(f"- {headline}" for headline in headlines) or "- No headlines available."
    markdown = f"""# Daily Market Recap — {date_str}

Generated: {generated_utc}

## Executive Summary

- Major US indices are **{market_direction}** on the latest available quote data.
- S&P 500: **{fmt_number(spx.price if spx else None)}** ({fmt_percent(spx.change_percent if spx else None)}).
- VIX: **{fmt_number(vix.price if vix else None)}** ({vix_label(vix)}).
- S&P 500 technical trend: **{technicals.trend}**.

## Market Dashboard

{quote_table(all_quotes, list(INDEX_SYMBOLS.keys()) + list(WATCH_SYMBOLS.keys()))}

## Sector Rotation

{sector_md}

## Hot Stock / Biggest Loser

- **Hot stock:** {fmt_mover(gainer)}
- **Biggest loser:** {fmt_mover(loser)}

## S&P 500 Technical Snapshot

| Metric | Level |
|---|---:|
| Latest close/level | {fmt_number(technicals.close)} |
| 5-day average | {fmt_number(technicals.sma_5)} |
| 20-day average | {fmt_number(technicals.sma_20)} |
| 20-day support | {fmt_number(technicals.support)} |
| 20-day resistance | {fmt_number(technicals.resistance)} |
| Trend | {technicals.trend} |

## Market Drivers / Headlines

These headlines provide context for the market move; do not treat them as a complete causal attribution.

{headline_lines}

## Earnings Calendar

{earnings_table(earnings)}

## Telegram Summary

```text
{summary}
```

## Disclosures

This recap is for informational purposes only and is not investment advice, a recommendation, or an offer to buy or sell securities. Market data may be delayed or incomplete; verify prices and risks before making trading decisions.
"""
    return markdown, summary


def telegram_request(token: str, method: str, **kwargs: Any) -> dict[str, Any]:
    """Call a Telegram Bot API method."""
    url = TELEGRAM_API.format(token=token, method=method)
    response = requests.post(url, timeout=30, **kwargs)
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram {method} failed: {json.dumps(data)}")
    return data


def discover_telegram_chat_id(token: str) -> str | None:
    """Find the most recent Telegram chat ID from bot updates."""
    url = TELEGRAM_API.format(token=token, method="getUpdates")
    response = requests.get(url, params={"limit": 100, "allowed_updates": json.dumps([
        "message",
        "channel_post",
        "my_chat_member",
    ])}, timeout=30)
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        return None
    updates = data.get("result") or []
    preferred_keys = ("channel_post", "message", "my_chat_member")
    for update in reversed(updates):
        for key in preferred_keys:
            payload = update.get(key)
            if not isinstance(payload, dict):
                continue
            chat = payload.get("chat")
            if isinstance(chat, dict) and chat.get("id") is not None:
                title = chat.get("title") or chat.get("username") or chat.get("first_name") or "unknown"
                print(f"[daily_market_recap] Discovered Telegram chat: {title} ({chat['id']})")
                return str(chat["id"])
    return None


def send_to_telegram(markdown_path: Path, summary: str, chat_id: str | None = None) -> None:
    """Send the summary and markdown file to Telegram."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured.")

    resolved_chat_id = (
        chat_id
        or os.environ.get("TELEGRAM_CHAT_ID")
        or os.environ.get("TELEGRAM_CHANNEL_ID")
        or os.environ.get("TELEGRAM_CHANNEL_USERNAME")
        or discover_telegram_chat_id(token)
    )
    if not resolved_chat_id:
        raise RuntimeError(
            "Telegram chat/channel ID is not configured and could not be discovered from bot updates. "
            "Set TELEGRAM_CHAT_ID, TELEGRAM_CHANNEL_ID, or TELEGRAM_CHANNEL_USERNAME."
        )

    telegram_request(token, "sendMessage", json={"chat_id": resolved_chat_id, "text": summary})
    with markdown_path.open("rb") as file_obj:
        telegram_request(
            token,
            "sendDocument",
            data={"chat_id": resolved_chat_id, "caption": f"Daily market recap: {markdown_path.name}"},
            files={"document": (markdown_path.name, file_obj, "text/markdown")},
        )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate and send Altamira's daily market recap.")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="Report date (YYYY-MM-DD).")
    parser.add_argument("--out-dir", default=str(OUTPUTS), help="Output directory.")
    parser.add_argument("--chat-id", default=None, help="Telegram chat/channel ID override.")
    parser.add_argument("--no-send", action="store_true", help="Generate the markdown file without Telegram delivery.")
    return parser.parse_args()


def main() -> None:
    """Generate the recap and deliver it if requested."""
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    markdown, summary = build_markdown(args.date)
    output_path = out_dir / f"daily-market-recap-{args.date}.md"
    output_path.write_text(markdown, encoding="utf-8")
    print(f"[daily_market_recap] Wrote {output_path}")
    print(summary)
    if not args.no_send:
        send_to_telegram(output_path, summary, args.chat_id)
        print("[daily_market_recap] Telegram summary and markdown file sent.")


if __name__ == "__main__":
    main()
