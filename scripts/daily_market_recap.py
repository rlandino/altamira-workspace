#!/usr/bin/env python3
"""Generate a daily market recap and optionally send it to Telegram."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import requests

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python < 3.9 fallback
    ZoneInfo = None  # type: ignore[assignment]


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS = WORKSPACE / "outputs"
FMP_V3 = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"
MARKET_SYMBOLS = ["^GSPC", "^DJI", "^IXIC", "^VIX", "SPY", "QQQ"]


@dataclass(frozen=True)
class RecapPaths:
    markdown: Path
    chart: Path


def current_market_date() -> date:
    """Return the current US/Eastern date when zoneinfo is available."""
    if ZoneInfo is None:
        return date.today()
    return datetime.now(ZoneInfo("America/New_York")).date()


def parse_float(value: Any) -> float | None:
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


def fmt_number(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "n/a"
    return f"{value:,.{digits}f}"


def fmt_pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:+.2f}%"


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


def request_json(url: str, params: dict[str, Any], timeout: int = 20) -> Any:
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def fetch_quotes(api_key: str) -> dict[str, dict[str, Any]]:
    data = request_json(
        f"{FMP_V3}/quote/{','.join(MARKET_SYMBOLS)}",
        {"apikey": api_key},
    )
    if not isinstance(data, list):
        return {}
    return {str(item.get("symbol")): item for item in data if item.get("symbol")}


def fetch_earnings(api_key: str, report_date: date) -> list[dict[str, Any]]:
    to_date = report_date + timedelta(days=7)
    data = request_json(
        f"{FMP_V3}/earning_calendar",
        {
            "from": report_date.isoformat(),
            "to": to_date.isoformat(),
            "apikey": api_key,
        },
    )
    return data if isinstance(data, list) else []


def fetch_market_movers(api_key: str, endpoint: str) -> dict[str, Any] | None:
    data = request_json(f"{FMP_STABLE}/{endpoint}", {"apikey": api_key})
    if isinstance(data, list) and data:
        return data[0]
    return None


def fetch_sector_snapshot(api_key: str, report_date: date) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    for offset in range(0, 5):
        current_date = report_date - timedelta(days=offset)
        data = request_json(
            f"{FMP_STABLE}/sector-performance-snapshot",
            {"date": current_date.isoformat(), "apikey": api_key},
        )
        rows: list[dict[str, Any]] = []
        if isinstance(data, list):
            rows = [item for item in data if isinstance(item, dict)]
        elif isinstance(data, dict):
            nested = data.get("data") or data.get("sectors") or data.get("sectorPerformance")
            if isinstance(nested, list):
                rows = [item for item in nested if isinstance(item, dict)]
        rows = [row for row in rows if sector_change(row) is not None]
        if rows:
            rows.sort(key=lambda row: sector_change(row) or 0)
            return rows[-1], rows[0]
    return None, None


def sector_name(row: dict[str, Any] | None) -> str:
    if not row:
        return "n/a"
    return str(row.get("sector") or row.get("sectorName") or row.get("name") or "n/a")


def sector_change(row: dict[str, Any] | None) -> float | None:
    if not row:
        return None
    for key in ("changesPercentage", "changePercentage", "performance", "change", "percentChange"):
        value = parse_float(row.get(key))
        if value is not None:
            return value
    return None


def fetch_historical_closes(api_key: str, symbol: str, report_date: date) -> list[dict[str, Any]]:
    from_date = report_date - timedelta(days=45)
    data = request_json(
        f"{FMP_STABLE}/historical-price-eod/light",
        {
            "symbol": symbol,
            "from": from_date.isoformat(),
            "to": report_date.isoformat(),
            "apikey": api_key,
        },
    )
    if not isinstance(data, list):
        return []
    rows: list[dict[str, Any]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        close = parse_float(item.get("close") or item.get("adjClose") or item.get("price"))
        row_date = item.get("date")
        if close is not None and row_date:
            rows.append({"date": str(row_date), "close": close})
    return sorted(rows, key=lambda row: row["date"])


def fetch_headlines(api_key: str) -> list[dict[str, Any]]:
    data = request_json(
        f"{FMP_STABLE}/news/general-latest",
        {"page": 0, "limit": 8, "apikey": api_key},
    )
    return data if isinstance(data, list) else []


def simple_average(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def compute_trend(current_price: float | None, closes: list[float]) -> tuple[float | None, float | None, float | None, float | None, str]:
    ma5 = simple_average(closes[-5:])
    ma20 = simple_average(closes[-20:])
    support = min(closes[-20:]) if len(closes) >= 1 else None
    resistance = max(closes[-20:]) if len(closes) >= 1 else None
    if current_price is None or ma5 is None or ma20 is None:
        trend = "Unknown"
    elif current_price > ma5 and current_price > ma20:
        trend = "Bullish"
    elif current_price < ma5 and current_price < ma20:
        trend = "Bearish"
    else:
        trend = "Mixed"
    return ma5, ma20, support, resistance, trend


def quote_price(quotes: dict[str, dict[str, Any]], symbol: str) -> float | None:
    return parse_float(quotes.get(symbol, {}).get("price"))


def quote_change(quotes: dict[str, dict[str, Any]], symbol: str) -> float | None:
    item = quotes.get(symbol, {})
    return parse_float(item.get("changesPercentage") or item.get("changePercentage"))


def mover_symbol(row: dict[str, Any] | None) -> str:
    if not row:
        return "n/a"
    return str(row.get("symbol") or row.get("ticker") or "n/a")


def mover_change(row: dict[str, Any] | None) -> float | None:
    if not row:
        return None
    for key in ("changesPercentage", "changePercentage", "changes", "change"):
        value = parse_float(row.get(key))
        if value is not None:
            return value
    return None


def render_earnings_table(earnings: list[dict[str, Any]]) -> str:
    rows = []
    for item in sorted(earnings, key=lambda row: (str(row.get("date", "")), str(row.get("symbol", ""))))[:20]:
        rows.append(
            "| {date} | {symbol} | {eps} | {revenue} |".format(
                date=item.get("date", "n/a"),
                symbol=item.get("symbol", "n/a"),
                eps=fmt_number(parse_float(item.get("epsEstimated"))),
                revenue=fmt_number(parse_float(item.get("revenueEstimated")), 0),
            )
        )
    if not rows:
        return "No earnings found for the next 7 days."
    return "\n".join(["| Date | Symbol | EPS est. | Revenue est. |", "|---|---:|---:|---:|", *rows])


def render_headlines(headlines: list[dict[str, Any]]) -> str:
    lines = []
    for item in headlines[:5]:
        title = item.get("title") or item.get("headline") or item.get("text")
        site = item.get("site") or item.get("publisher") or item.get("source")
        if not title:
            continue
        suffix = f" ({site})" if site else ""
        lines.append(f"- {title}{suffix}")
    return "\n".join(lines) if lines else "No broad-market headlines returned by FMP."


def build_paths(out_dir: Path, report_date: date) -> RecapPaths:
    out_dir.mkdir(parents=True, exist_ok=True)
    date_text = report_date.isoformat()
    return RecapPaths(
        markdown=out_dir / f"daily-market-recap-{date_text}.md",
        chart=out_dir / f"daily-market-recap-chart-{date_text}.png",
    )


def generate_chart(closes: list[dict[str, Any]], chart_path: Path) -> bool:
    if not closes:
        return False
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        print(f"Chart skipped: matplotlib unavailable ({exc})")
        return False

    recent = closes[-20:]
    dates = [row["date"] for row in recent]
    values = [row["close"] for row in recent]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(dates, values, color="steelblue", linewidth=2, label="S&P 500 close")
    ax.set_title("S&P 500 - Recent Closing Prices")
    ax.set_xlabel("Date")
    ax.set_ylabel("Close")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(chart_path, dpi=150)
    plt.close(fig)
    return True


def build_markdown(
    report_date: date,
    quotes: dict[str, dict[str, Any]],
    hot_stock: dict[str, Any] | None,
    biggest_loser: dict[str, Any] | None,
    best_sector: dict[str, Any] | None,
    worst_sector: dict[str, Any] | None,
    earnings: list[dict[str, Any]],
    headlines: list[dict[str, Any]],
    historical: list[dict[str, Any]],
    paths: RecapPaths,
    chart_generated: bool,
) -> tuple[str, str]:
    spx = quote_price(quotes, "^GSPC")
    vix = quote_price(quotes, "^VIX")
    closes = [row["close"] for row in historical]
    ma5, ma20, support, resistance, trend = compute_trend(spx, closes)

    summary = (
        f"Daily Market Recap - {report_date.isoformat()}\n"
        f"S&P 500 {fmt_number(spx)} ({fmt_pct(quote_change(quotes, '^GSPC'))}); "
        f"Nasdaq {fmt_number(quote_price(quotes, '^IXIC'))} ({fmt_pct(quote_change(quotes, '^IXIC'))}); "
        f"Dow {fmt_number(quote_price(quotes, '^DJI'))} ({fmt_pct(quote_change(quotes, '^DJI'))}).\n"
        f"VIX {fmt_number(vix)} ({vix_label(vix)}). Trend: {trend}. "
        f"Best sector: {sector_name(best_sector)} {fmt_pct(sector_change(best_sector))}; "
        f"worst sector: {sector_name(worst_sector)} {fmt_pct(sector_change(worst_sector))}.\n"
        f"Hot stock: {mover_symbol(hot_stock)} {fmt_pct(mover_change(hot_stock))}; "
        f"biggest loser: {mover_symbol(biggest_loser)} {fmt_pct(mover_change(biggest_loser))}."
    )

    chart_line = f"![S&P 500 chart]({paths.chart.as_posix()})" if chart_generated else "Chart not generated."
    markdown = f"""# Daily Market Recap - {report_date.isoformat()}

Generated: {datetime.now().isoformat(timespec="seconds")}

## Executive Summary

{summary}

## Market Indices

| Index | Level | Day change |
|---|---:|---:|
| S&P 500 | {fmt_number(spx)} | {fmt_pct(quote_change(quotes, '^GSPC'))} |
| Nasdaq Composite | {fmt_number(quote_price(quotes, '^IXIC'))} | {fmt_pct(quote_change(quotes, '^IXIC'))} |
| Dow Jones Industrial Average | {fmt_number(quote_price(quotes, '^DJI'))} | {fmt_pct(quote_change(quotes, '^DJI'))} |

## ETFs and Volatility

| Instrument | Level | Day change |
|---|---:|---:|
| SPY | {fmt_number(quote_price(quotes, 'SPY'))} | {fmt_pct(quote_change(quotes, 'SPY'))} |
| QQQ | {fmt_number(quote_price(quotes, 'QQQ'))} | {fmt_pct(quote_change(quotes, 'QQQ'))} |
| VIX | {fmt_number(vix)} | {vix_label(vix)} |

## Leaders and Laggards

- Hot stock: **{mover_symbol(hot_stock)}** ({fmt_pct(mover_change(hot_stock))})
- Biggest loser: **{mover_symbol(biggest_loser)}** ({fmt_pct(mover_change(biggest_loser))})
- Best sector: **{sector_name(best_sector)}** ({fmt_pct(sector_change(best_sector))})
- Worst sector: **{sector_name(worst_sector)}** ({fmt_pct(sector_change(worst_sector))})

## Technical Read

| Metric | Value |
|---|---:|
| 5-day S&P 500 average | {fmt_number(ma5)} |
| 20-day S&P 500 average | {fmt_number(ma20)} |
| 20-day close resistance | {fmt_number(resistance)} |
| 20-day close support | {fmt_number(support)} |
| Trend | {trend} |

## Market Drivers

{render_headlines(headlines)}

## Earnings Calendar - Next 7 Days

{render_earnings_table(earnings)}

## Index Performance Chart

{chart_line}

## Disclaimer

This recap is for informational purposes only and is not investment advice. Market data comes from FMP and may be delayed or revised.
"""
    return summary, markdown


def send_telegram_message(token: str, chat_id: str, text: str) -> None:
    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={"chat_id": chat_id, "text": text, "disable_web_page_preview": True},
        timeout=20,
    )
    if not response.ok:
        raise RuntimeError(f"Telegram sendMessage failed: {response.status_code} {response.text}")


def send_telegram_document(token: str, chat_id: str, path: Path, caption: str) -> None:
    with path.open("rb") as document:
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendDocument",
            data={"chat_id": chat_id, "caption": caption},
            files={"document": (path.name, document, "text/markdown")},
            timeout=30,
        )
    if not response.ok:
        raise RuntimeError(f"Telegram sendDocument failed: {response.status_code} {response.text}")


def resolve_api_key(args: argparse.Namespace) -> str:
    api_key = args.fmp_api_key or os.environ.get("FMP_API_KEY")
    if not api_key:
        raise SystemExit("Missing FMP API key. Set FMP_API_KEY or pass --fmp-api-key.")
    return api_key


def resolve_telegram(args: argparse.Namespace) -> tuple[str, str]:
    token = args.telegram_token or os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
    chat_id = (
        args.telegram_chat_id
        or os.environ.get("TELEGRAM_CHAT_ID")
        or os.environ.get("TELEGRAM_CHANNEL_ID")
    )
    if not token:
        raise SystemExit("Missing Telegram token. Set TELEGRAM_BOT_TOKEN or pass --telegram-token.")
    if not chat_id:
        raise SystemExit("Missing Telegram chat/channel ID. Set TELEGRAM_CHAT_ID or pass --telegram-chat-id.")
    return token, chat_id


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a daily market recap and optionally send it to Telegram.")
    parser.add_argument("--date", help="Report date in YYYY-MM-DD format. Defaults to current US/Eastern date.")
    parser.add_argument("--out-dir", default=str(OUTPUTS), help="Output directory. Defaults to workspace outputs/.")
    parser.add_argument("--fmp-api-key", help="FMP API key. Defaults to FMP_API_KEY.")
    parser.add_argument("--send-telegram", action="store_true", help="Send summary and markdown report to Telegram.")
    parser.add_argument("--telegram-token", help="Telegram bot token. Defaults to TELEGRAM_BOT_TOKEN.")
    parser.add_argument("--telegram-chat-id", help="Telegram chat/channel ID. Defaults to TELEGRAM_CHAT_ID.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report_date = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else current_market_date()
    api_key = resolve_api_key(args)
    paths = build_paths(Path(args.out_dir), report_date)

    quotes = fetch_quotes(api_key)
    hot_stock = fetch_market_movers(api_key, "biggest-gainers")
    biggest_loser = fetch_market_movers(api_key, "biggest-losers")
    best_sector, worst_sector = fetch_sector_snapshot(api_key, report_date)
    earnings = fetch_earnings(api_key, report_date)
    headlines = fetch_headlines(api_key)
    historical = fetch_historical_closes(api_key, "^GSPC", report_date)
    chart_generated = generate_chart(historical, paths.chart)

    summary, markdown = build_markdown(
        report_date,
        quotes,
        hot_stock,
        biggest_loser,
        best_sector,
        worst_sector,
        earnings,
        headlines,
        historical,
        paths,
        chart_generated,
    )
    paths.markdown.write_text(markdown, encoding="utf-8")

    print(summary)
    print(f"Markdown report: {paths.markdown}")
    if chart_generated:
        print(f"Chart: {paths.chart}")

    if args.send_telegram:
        token, chat_id = resolve_telegram(args)
        send_telegram_message(token, chat_id, summary)
        send_telegram_document(
            token,
            chat_id,
            paths.markdown,
            f"Daily market recap markdown - {report_date.isoformat()}",
        )
        print("Telegram delivery: sent summary and markdown report.")


if __name__ == "__main__":
    main()
