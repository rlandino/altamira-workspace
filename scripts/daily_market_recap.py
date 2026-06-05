#!/usr/bin/env python3
"""Generate a daily market recap and optionally send it to Telegram."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

import requests


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS = WORKSPACE / "outputs"
FMP_V3 = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"
INDEX_SYMBOLS = "^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ"
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


@dataclass(frozen=True)
class RecapResult:
    report_path: Path
    chart_path: Path | None
    summary: str
    telegram_responses: list[dict[str, Any]]


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"{name} is required.")
    return value


def get_json(url: str, params: dict[str, Any], timeout: int = 20) -> Any:
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def parse_percent(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace("%", "").replace("+", "").replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def format_number(value: Any, digits: int = 2) -> str:
    if value is None:
        return "-"
    try:
        return f"{float(value):,.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def format_percent(value: Any) -> str:
    pct = parse_percent(value)
    if pct is None:
        return "-"
    sign = "+" if pct > 0 else ""
    return f"{sign}{pct:.2f}%"


def quote_map(api_key: str, symbols: str) -> dict[str, dict[str, Any]]:
    rows = get_json(f"{FMP_V3}/quote/{symbols}", {"apikey": api_key})
    if not isinstance(rows, list):
        return {}
    return {str(row.get("symbol")): row for row in rows if row.get("symbol")}


def fetch_movers(api_key: str, endpoint: str) -> dict[str, Any] | None:
    try:
        rows = get_json(f"{FMP_STABLE}/{endpoint}", {"apikey": api_key})
    except requests.RequestException:
        return None
    if isinstance(rows, list) and rows:
        return rows[0]
    return None


def fetch_sector_leaders(api_key: str, recap_date: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None, str]:
    try:
        rows = get_json(
            f"{FMP_STABLE}/sector-performance-snapshot",
            {"date": recap_date, "apikey": api_key},
        )
        if isinstance(rows, list) and rows:
            normalized = []
            for row in rows:
                pct = parse_percent(row.get("changesPercentage") or row.get("changePercentage"))
                name = row.get("sector") or row.get("name")
                if pct is not None and name:
                    normalized.append({"name": name, "pct": pct, "source": "FMP sector snapshot"})
            if normalized:
                ordered = sorted(normalized, key=lambda item: item["pct"])
                return ordered[-1], ordered[0], "FMP sector snapshot"
    except requests.RequestException:
        pass

    quotes = quote_map(api_key, ",".join(SECTOR_ETFS.values()))
    normalized = []
    for name, symbol in SECTOR_ETFS.items():
        row = quotes.get(symbol)
        if not row:
            continue
        pct = parse_percent(row.get("changesPercentage"))
        if pct is not None:
            normalized.append({"name": name, "symbol": symbol, "pct": pct, "source": "sector ETF proxy"})
    if not normalized:
        return None, None, "sector data unavailable"
    ordered = sorted(normalized, key=lambda item: item["pct"])
    return ordered[-1], ordered[0], "sector ETF proxy"


def fetch_earnings(api_key: str, recap_date: str) -> list[dict[str, Any]]:
    start = datetime.strptime(recap_date, "%Y-%m-%d").date()
    end = start + timedelta(days=7)
    try:
        rows = get_json(
            f"{FMP_V3}/earning_calendar",
            {"from": start.isoformat(), "to": end.isoformat(), "apikey": api_key},
        )
    except requests.RequestException:
        return []
    if not isinstance(rows, list):
        return []
    return sorted(rows, key=lambda row: (str(row.get("date", "")), str(row.get("symbol", ""))))[:12]


def fetch_history(api_key: str, recap_date: str) -> list[dict[str, Any]]:
    to_date = datetime.strptime(recap_date, "%Y-%m-%d").date()
    from_date = to_date - timedelta(days=45)
    params = {
        "symbol": "^GSPC",
        "from": from_date.isoformat(),
        "to": to_date.isoformat(),
        "apikey": api_key,
    }
    try:
        rows = get_json(f"{FMP_STABLE}/historical-price-eod/light", params)
        if isinstance(rows, list):
            normalized = []
            for row in rows:
                close = row.get("close", row.get("price"))
                if row.get("date") and close is not None:
                    normalized.append({**row, "close": close})
            return sorted(
                normalized,
                key=lambda row: str(row["date"]),
            )
    except requests.RequestException:
        pass

    try:
        rows = get_json(
            f"{FMP_V3}/historical-price-full/%5EGSPC",
            {"from": from_date.isoformat(), "to": to_date.isoformat(), "apikey": api_key},
        )
    except requests.RequestException:
        return []
    historical = rows.get("historical") if isinstance(rows, dict) else []
    if not isinstance(historical, list):
        return []
    return sorted(
        [row for row in historical if row.get("date") and row.get("close") is not None],
        key=lambda row: str(row["date"]),
    )


def moving_average(values: list[float], window: int) -> float | None:
    if len(values) < window:
        return None
    return sum(values[-window:]) / window


def generate_chart(history: list[dict[str, Any]], recap_date: str) -> Path | None:
    if not history:
        return None
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return None

    dates = [datetime.strptime(str(row["date"]), "%Y-%m-%d") for row in history[-20:]]
    closes = [float(row["close"]) for row in history[-20:]]
    if not dates or not closes:
        return None

    OUTPUTS.mkdir(parents=True, exist_ok=True)
    chart_path = OUTPUTS / f"daily-market-recap-chart-{recap_date}.png"

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(dates, closes, color="steelblue", linewidth=2, label="S&P 500 close")
    ax.set_title("S&P 500 - Recent Performance")
    ax.set_xlabel("Date")
    ax.set_ylabel("Close")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(chart_path, dpi=150)
    plt.close(fig)
    return chart_path


def quote_change(row: dict[str, Any] | None) -> str:
    return format_percent((row or {}).get("changesPercentage"))


def report_for(
    recap_date: str,
    quotes: dict[str, dict[str, Any]],
    hot_stock: dict[str, Any] | None,
    biggest_loser: dict[str, Any] | None,
    best_sector: dict[str, Any] | None,
    worst_sector: dict[str, Any] | None,
    sector_source: str,
    earnings: list[dict[str, Any]],
    history: list[dict[str, Any]],
    chart_path: Path | None,
) -> tuple[str, str]:
    gspc = quotes.get("^GSPC", {})
    dji = quotes.get("^DJI", {})
    ixic = quotes.get("^IXIC", {})
    vix = quotes.get("^VIX", {})
    spy = quotes.get("SPY", {})
    qqq = quotes.get("QQQ", {})

    closes = [float(row["close"]) for row in history if row.get("close") is not None]
    current_spx = float(gspc.get("price") or closes[-1]) if (gspc.get("price") or closes) else None
    avg_5 = moving_average(closes, 5)
    avg_20 = moving_average(closes, 20)
    support = min(closes[-20:]) if len(closes) >= 20 else None
    resistance = max(closes[-20:]) if len(closes) >= 20 else None
    if current_spx is not None and avg_5 is not None and avg_20 is not None:
        trend = "Bullish" if current_spx > avg_5 and current_spx > avg_20 else "Bearish" if current_spx < avg_5 and current_spx < avg_20 else "Mixed"
    else:
        trend = "Unavailable"

    vix_level = parse_percent(vix.get("price"))
    if vix_level is None:
        vix_label = "Unavailable"
    elif vix_level > 20:
        vix_label = "Elevated"
    elif vix_level < 15:
        vix_label = "Low"
    else:
        vix_label = "Normal"

    hot_text = f"{hot_stock.get('symbol', '-')}: {format_percent(hot_stock.get('changesPercentage') or hot_stock.get('change'))}" if hot_stock else "Unavailable"
    loser_text = f"{biggest_loser.get('symbol', '-')}: {format_percent(biggest_loser.get('changesPercentage') or biggest_loser.get('change'))}" if biggest_loser else "Unavailable"
    best_text = (
        f"{best_sector['name']} ({best_sector.get('symbol', '')}) {format_percent(best_sector['pct'])}".replace(" ()", "")
        if best_sector
        else "Unavailable"
    )
    worst_text = (
        f"{worst_sector['name']} ({worst_sector.get('symbol', '')}) {format_percent(worst_sector['pct'])}".replace(" ()", "")
        if worst_sector
        else "Unavailable"
    )

    earnings_rows = []
    for row in earnings:
        earnings_rows.append(
            f"| {row.get('date', '-')} | {row.get('symbol', '-')} | {format_number(row.get('epsEstimated'), 2)} |"
        )
    if not earnings_rows:
        earnings_rows.append("| - | No earnings returned by FMP for the next 7 days | - |")

    chart_line = f"![S&P 500 chart]({chart_path.relative_to(WORKSPACE)})" if chart_path else "Chart not generated."

    report = f"""# Daily Market Recap - {recap_date}

**Source:** Financial Modeling Prep.  
**Generated:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}

## Market indices

| Index | Level | Day change |
|-------|-------|------------|
| S&P 500 (^GSPC) | {format_number(gspc.get('price'))} | {quote_change(gspc)} |
| Nasdaq Composite (^IXIC) | {format_number(ixic.get('price'))} | {quote_change(ixic)} |
| Dow Jones (^DJI) | {format_number(dji.get('price'))} | {quote_change(dji)} |

## ETFs and volatility

| Instrument | Level | Day change |
|------------|-------|------------|
| SPY | {format_number(spy.get('price'))} | {quote_change(spy)} |
| QQQ | {format_number(qqq.get('price'))} | {quote_change(qqq)} |
| VIX | {format_number(vix.get('price'))} | {quote_change(vix)} |

**VIX context:** {vix_label}.

## Market movers

- **Hot stock:** {hot_text}
- **Biggest loser:** {loser_text}
- **Best sector:** {best_text}
- **Worst sector:** {worst_text}
- **Sector source:** {sector_source}

## S&P 500 trend dashboard

| Metric | Value |
|--------|-------|
| Current level | {format_number(current_spx)} |
| 5-day average | {format_number(avg_5)} |
| 20-day average | {format_number(avg_20)} |
| 20-day resistance | {format_number(resistance)} |
| 20-day support | {format_number(support)} |
| Trend | {trend} |

## Earnings calendar - next 7 days

| Date | Symbol | EPS estimate |
|------|--------|--------------|
{chr(10).join(earnings_rows)}

## Commentary

The S&P 500 is {quote_change(gspc)} on the session, Nasdaq is {quote_change(ixic)}, and the Dow is {quote_change(dji)}. The short-term S&P 500 trend reads **{trend}** versus the recent 5-day and 20-day averages. Sector leadership is led by **{best_text}**, while **{worst_text}** is lagging. VIX is **{vix_label.lower()}** at {format_number(vix.get('price'))}, which frames the volatility backdrop for premium-selling and risk management.

## Index performance chart

{chart_line}

---

This market recap is for research and education only and is not investment advice.
"""

    summary = (
        f"Altamira Daily Market Recap - {recap_date}\n"
        f"S&P 500 {format_number(gspc.get('price'))} ({quote_change(gspc)}), Nasdaq {quote_change(ixic)}, Dow {quote_change(dji)}.\n"
        f"Trend: {trend}; VIX: {format_number(vix.get('price'))} ({vix_label}).\n"
        f"Best sector: {best_text}; worst sector: {worst_text}.\n"
        f"Hot stock: {hot_text}; biggest loser: {loser_text}."
    )
    return report, summary


def send_telegram(
    bot_token: str,
    chat_id: str,
    summary: str,
    report_path: Path,
) -> list[dict[str, Any]]:
    base = f"https://api.telegram.org/bot{bot_token}"
    responses: list[dict[str, Any]] = []

    message_response = requests.post(
        f"{base}/sendMessage",
        data={"chat_id": chat_id, "text": summary},
        timeout=20,
    )
    responses.append(message_response.json())
    message_response.raise_for_status()
    if not responses[-1].get("ok"):
        raise RuntimeError(f"Telegram sendMessage failed: {responses[-1]}")

    with report_path.open("rb") as report_file:
        document_response = requests.post(
            f"{base}/sendDocument",
            data={"chat_id": chat_id, "caption": f"Daily market recap markdown: {report_path.name}"},
            files={"document": (report_path.name, report_file, "text/markdown")},
            timeout=30,
        )
    responses.append(document_response.json())
    document_response.raise_for_status()
    if not responses[-1].get("ok"):
        raise RuntimeError(f"Telegram sendDocument failed: {responses[-1]}")

    return responses


def generate_recap(args: argparse.Namespace) -> RecapResult:
    api_key = require_env("FMP_API_KEY")
    recap_date = args.date or date.today().isoformat()
    OUTPUTS.mkdir(parents=True, exist_ok=True)

    quotes = quote_map(api_key, INDEX_SYMBOLS)
    hot_stock = fetch_movers(api_key, "biggest-gainers")
    biggest_loser = fetch_movers(api_key, "biggest-losers")
    best_sector, worst_sector, sector_source = fetch_sector_leaders(api_key, recap_date)
    earnings = fetch_earnings(api_key, recap_date)
    history = fetch_history(api_key, recap_date)
    chart_path = generate_chart(history, recap_date)

    report, summary = report_for(
        recap_date,
        quotes,
        hot_stock,
        biggest_loser,
        best_sector,
        worst_sector,
        sector_source,
        earnings,
        history,
        chart_path,
    )

    report_path = OUTPUTS / f"daily-market-recap-{recap_date}.md"
    report_path.write_text(report, encoding="utf-8")

    telegram_responses: list[dict[str, Any]] = []
    if args.send_telegram:
        chat_id = args.telegram_chat_id or os.environ.get("DAILY_MARKET_RECAP_CHAT_ID") or os.environ.get("TELEGRAM_CHAT_ID")
        if not chat_id:
            raise SystemExit("Telegram delivery requested, but TELEGRAM_CHAT_ID or --telegram-chat-id is missing.")
        bot_token = require_env("TELEGRAM_BOT_TOKEN")
        telegram_responses = send_telegram(bot_token, chat_id, summary, report_path)

    return RecapResult(report_path, chart_path, summary, telegram_responses)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate and optionally send a daily market recap.")
    parser.add_argument("--date", help="Recap date in YYYY-MM-DD format. Defaults to today.")
    parser.add_argument("--send-telegram", action="store_true", help="Send summary and markdown report to Telegram.")
    parser.add_argument("--telegram-chat-id", help="Telegram chat/channel ID. Defaults to DAILY_MARKET_RECAP_CHAT_ID or TELEGRAM_CHAT_ID.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable result metadata.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = generate_recap(args)
    if args.json:
        print(
            json.dumps(
                {
                    "report_path": str(result.report_path),
                    "chart_path": str(result.chart_path) if result.chart_path else None,
                    "summary": result.summary,
                    "telegram_ok": [response.get("ok") for response in result.telegram_responses],
                },
                indent=2,
            )
        )
    else:
        print(result.summary)
        print(f"Report: {result.report_path}")
        if result.chart_path:
            print(f"Chart: {result.chart_path}")
        if result.telegram_responses:
            print("Telegram: sent summary and markdown document")


if __name__ == "__main__":
    main()
