#!/usr/bin/env python3
"""Generate a daily market recap and optionally send it to Telegram."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import re
from typing import Any
from zoneinfo import ZoneInfo

import requests


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS = WORKSPACE / "outputs"
FMP_V3 = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"
TELEGRAM_API = "https://api.telegram.org"
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
DEFAULT_INDEX_SYMBOLS = ",".join(["^GSPC", "^DJI", "^IXIC", "^VIX", "SPY", "QQQ", *SECTOR_ETFS])


@dataclass(frozen=True)
class RecapResult:
    """Generated recap artifacts and summary text."""

    output_path: Path
    summary: str
    markdown: str


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate Altamira daily market recap")
    parser.add_argument("--date", help="Recap date in YYYY-MM-DD format; defaults to today in New York")
    parser.add_argument("--out-dir", default=str(OUTPUTS), help="Output directory for the markdown recap")
    parser.add_argument("--send-telegram", action="store_true", help="Send summary and markdown file to Telegram")
    parser.add_argument("--telegram-chat-id", help="Telegram chat/channel ID; defaults to TELEGRAM_CHAT_ID")
    parser.add_argument("--fmp-api-key", help="FMP API key; defaults to FMP_API_KEY")
    return parser.parse_args()


def get_recap_date(date_arg: str | None) -> str:
    """Return the recap date in YYYY-MM-DD format."""
    if date_arg:
        datetime.strptime(date_arg, "%Y-%m-%d")
        return date_arg
    return datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d")


def fmp_get(base_url: str, path: str, api_key: str, params: dict[str, Any] | None = None) -> Any:
    """Fetch JSON from an FMP endpoint."""
    request_params = dict(params or {})
    request_params["apikey"] = api_key
    response = requests.get(f"{base_url}{path}", params=request_params, timeout=20)
    response.raise_for_status()
    return response.json()


def safe_float(value: Any) -> float | None:
    """Convert a possibly formatted number to float."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace("%", "").replace(",", "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def format_number(value: Any, decimals: int = 2, default: str = "N/A") -> str:
    """Format a numeric value with commas."""
    number = safe_float(value)
    if number is None:
        return default
    return f"{number:,.{decimals}f}"


def format_percent(value: Any, decimals: int = 2, default: str = "N/A") -> str:
    """Format a percent-like value."""
    number = safe_float(value)
    if number is None:
        return default
    return f"{number:+.{decimals}f}%"


def row_symbol(row: dict[str, Any]) -> str:
    """Return the best available symbol/name for a quote-like row."""
    return str(row.get("symbol") or row.get("ticker") or row.get("name") or "N/A")


def quote_map(rows: Any) -> dict[str, dict[str, Any]]:
    """Map FMP quote response rows by symbol."""
    if not isinstance(rows, list):
        return {}
    return {str(row.get("symbol")): row for row in rows if isinstance(row, dict) and row.get("symbol")}


def pct_from_row(row: dict[str, Any]) -> float | None:
    """Extract a percent change/performance field from a row."""
    keys = (
        "changesPercentage",
        "changesPercent",
        "changePercentage",
        "changePercent",
        "percentage",
        "performance",
        "change",
    )
    for key in keys:
        number = safe_float(row.get(key))
        if number is not None:
            return number
    return None


def normalize_sector_rows(data: Any) -> list[dict[str, Any]]:
    """Normalize common FMP sector snapshot shapes into rows."""
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        for key in ("sectorPerformance", "sectors", "data"):
            rows = data.get(key)
            if isinstance(rows, list):
                return [row for row in rows if isinstance(row, dict)]
        rows = []
        for key, value in data.items():
            if isinstance(value, (int, float, str)):
                rows.append({"sector": key, "changesPercentage": value})
        return rows
    return []


def sector_name(row: dict[str, Any]) -> str:
    """Return the best available sector name."""
    return str(row.get("sector") or row.get("name") or row.get("sectorName") or "N/A")


def pick_best_worst(rows: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Pick best and worst rows by percent field."""
    scored = [(pct_from_row(row), row) for row in rows]
    valid = [(pct, row) for pct, row in scored if pct is not None]
    if not valid:
        return None, None
    valid.sort(key=lambda item: item[0])
    return valid[-1][1], valid[0][1]


def sector_rows_from_etfs(quotes: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Build sector rows from sector ETF quote changes as a fallback."""
    rows = []
    for symbol, name in SECTOR_ETFS.items():
        quote = quotes.get(symbol, {})
        pct = pct_from_row(quote)
        if pct is not None:
            rows.append({"sector": name, "symbol": symbol, "changesPercentage": pct})
    return rows


def historical_closes(rows: Any) -> list[float]:
    """Extract close prices from FMP historical rows ordered oldest to newest."""
    if not isinstance(rows, list):
        return []
    dated_rows = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        close = safe_float(row.get("close") or row.get("adjClose") or row.get("price"))
        date = row.get("date")
        if close is None or not date:
            continue
        dated_rows.append((str(date), close))
    dated_rows.sort(key=lambda item: item[0])
    return [close for _, close in dated_rows]


def moving_average(values: list[float], window: int) -> float | None:
    """Compute a simple moving average from the latest values."""
    if len(values) < window:
        return None
    return sum(values[-window:]) / window


def trend_label(current: float | None, ma5: float | None, ma20: float | None) -> str:
    """Classify trend based on current level versus short moving averages."""
    if current is None or ma5 is None or ma20 is None:
        return "Unknown"
    if current > ma5 and current > ma20:
        return "Bullish"
    if current < ma5 and current < ma20:
        return "Bearish"
    return "Mixed"


def vix_label(vix_level: float | None) -> str:
    """Classify VIX level."""
    if vix_level is None:
        return "Unknown"
    if vix_level < 15:
        return "Low"
    if vix_level <= 20:
        return "Normal"
    if vix_level <= 30:
        return "Elevated"
    return "High stress"


def first_row(data: Any) -> dict[str, Any] | None:
    """Return first dict row from a list-like API response."""
    if isinstance(data, list):
        for row in data:
            if isinstance(row, dict):
                return row
    return None


def fetch_market_data(api_key: str, recap_date: str) -> dict[str, Any]:
    """Fetch all market data used by the recap."""
    start_date = (datetime.strptime(recap_date, "%Y-%m-%d") - timedelta(days=45)).strftime("%Y-%m-%d")
    earnings_to = (datetime.strptime(recap_date, "%Y-%m-%d") + timedelta(days=7)).strftime("%Y-%m-%d")

    data: dict[str, Any] = {}
    data["quotes"] = fmp_get(FMP_V3, f"/quote/{DEFAULT_INDEX_SYMBOLS}", api_key)
    data["gainers"] = fmp_get(FMP_STABLE, "/biggest-gainers", api_key)
    data["losers"] = fmp_get(FMP_STABLE, "/biggest-losers", api_key)
    data["sectors"] = fmp_get(FMP_STABLE, "/sector-performance-snapshot", api_key, {"date": recap_date})
    data["earnings"] = fmp_get(FMP_V3, "/earning_calendar", api_key, {"from": recap_date, "to": earnings_to})
    data["history"] = fmp_get(
        FMP_STABLE,
        "/historical-price-eod/light",
        api_key,
        {"symbol": "^GSPC", "from": start_date, "to": recap_date},
    )
    data["news"] = fmp_get(FMP_STABLE, "/news/general-latest", api_key, {"page": 0, "limit": 8})
    return data


def is_us_equity_symbol(symbol: str) -> bool:
    """Return True for simple U.S.-style listed equity symbols."""
    return bool(re.fullmatch(r"[A-Z]{1,5}(-[A-Z])?", symbol))


def top_earnings_rows(rows: Any, limit: int = 10) -> list[dict[str, Any]]:
    """Return upcoming earnings rows sorted by date."""
    if not isinstance(rows, list):
        return []
    cleaned = [row for row in rows if isinstance(row, dict)]
    cleaned.sort(key=lambda row: (row.get("date") or "", row.get("symbol") or ""))
    us_rows = [row for row in cleaned if is_us_equity_symbol(str(row.get("symbol") or ""))]
    return (us_rows or cleaned)[:limit]


def headline_rows(rows: Any, limit: int = 5) -> list[dict[str, Any]]:
    """Return top headline rows."""
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)][:limit]


def build_commentary(
    spx_change: float | None,
    nasdaq_change: float | None,
    best_sector: dict[str, Any] | None,
    worst_sector: dict[str, Any] | None,
    vix_level: float | None,
    headlines: list[dict[str, Any]],
) -> str:
    """Build short price-grounded commentary without inventing unsupported causes."""
    if spx_change is None:
        direction = "mixed"
    elif spx_change > 0.15:
        direction = "higher"
    elif spx_change < -0.15:
        direction = "lower"
    else:
        direction = "little changed"

    parts = [f"Markets are trading {direction} based on the S&P 500 move."]
    if nasdaq_change is not None and spx_change is not None and (nasdaq_change - spx_change) > 0.35:
        parts.append("Nasdaq leadership points to a growth/technology tilt in today's tape.")
    elif nasdaq_change is not None and spx_change is not None and (spx_change - nasdaq_change) > 0.35:
        parts.append("The Nasdaq is lagging the broader index, suggesting pressure on growth-heavy exposure.")
    if best_sector and worst_sector:
        parts.append(
            f"Sector rotation is led by {sector_name(best_sector)}, while {sector_name(worst_sector)} is lagging."
        )
    if vix_level is not None:
        parts.append(f"VIX is {vix_label(vix_level).lower()} at {format_number(vix_level)}.")
    if headlines:
        titles = [str(row.get("title") or row.get("headline") or "").strip() for row in headlines[:2]]
        titles = [title for title in titles if title]
        if titles:
            parts.append("Relevant headlines include: " + "; ".join(titles) + ".")
    return " ".join(parts)


def build_recap(data: dict[str, Any], recap_date: str, out_dir: Path) -> RecapResult:
    """Build markdown recap and write it to disk."""
    quotes = quote_map(data.get("quotes"))
    spx = quotes.get("^GSPC", {})
    dow = quotes.get("^DJI", {})
    nasdaq = quotes.get("^IXIC", {})
    vix = quotes.get("^VIX", {})
    spy = quotes.get("SPY", {})
    qqq = quotes.get("QQQ", {})

    sector_rows = normalize_sector_rows(data.get("sectors"))
    if not any(pct_from_row(row) is not None for row in sector_rows):
        sector_rows = sector_rows_from_etfs(quotes)
    best_sector, worst_sector = pick_best_worst(sector_rows)
    top_gainer = first_row(data.get("gainers"))
    top_loser = first_row(data.get("losers"))
    earnings = top_earnings_rows(data.get("earnings"))
    headlines = headline_rows(data.get("news"))

    closes = historical_closes(data.get("history"))
    current_spx = safe_float(spx.get("price"))
    ma5 = moving_average(closes, 5)
    ma20 = moving_average(closes, 20)
    support = min(closes[-20:]) if len(closes) >= 20 else None
    resistance = max(closes[-20:]) if len(closes) >= 20 else None
    trend = trend_label(current_spx, ma5, ma20)
    vix_level = safe_float(vix.get("price"))

    spx_change = pct_from_row(spx)
    nasdaq_change = pct_from_row(nasdaq)
    commentary = build_commentary(spx_change, nasdaq_change, best_sector, worst_sector, vix_level, headlines)

    generated_at = datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M %Z")
    output_path = out_dir / f"daily-market-recap-{recap_date}.md"

    lines = [
        f"# Daily Market Recap - {recap_date}",
        "",
        f"_Generated at {generated_at}. Data source: Financial Modeling Prep._",
        "",
        "> Informational only; not investment advice.",
        "",
        "## Executive Summary",
        "",
        f"- **S&P 500:** {format_number(spx.get('price'))} ({format_percent(spx_change)})",
        f"- **Nasdaq Composite:** {format_number(nasdaq.get('price'))} ({format_percent(nasdaq_change)})",
        f"- **Dow Jones:** {format_number(dow.get('price'))} ({format_percent(pct_from_row(dow))})",
        f"- **VIX:** {format_number(vix_level)} ({vix_label(vix_level)})",
        f"- **Trend:** {trend}",
        "",
        "## Market Indices",
        "",
        "| Index / ETF | Level | Day Change |",
        "|---|---:|---:|",
        f"| S&P 500 (^GSPC) | {format_number(spx.get('price'))} | {format_percent(spx_change)} |",
        f"| Nasdaq Composite (^IXIC) | {format_number(nasdaq.get('price'))} | {format_percent(nasdaq_change)} |",
        f"| Dow Jones (^DJI) | {format_number(dow.get('price'))} | {format_percent(pct_from_row(dow))} |",
        f"| SPY | {format_number(spy.get('price'))} | {format_percent(pct_from_row(spy))} |",
        f"| QQQ | {format_number(qqq.get('price'))} | {format_percent(pct_from_row(qqq))} |",
        "",
        "## Sector Rotation",
        "",
    ]

    if best_sector and worst_sector:
        lines.extend(
            [
                f"- **Best sector:** {sector_name(best_sector)} ({format_percent(pct_from_row(best_sector))})",
                f"- **Worst sector:** {sector_name(worst_sector)} ({format_percent(pct_from_row(worst_sector))})",
            ]
        )
    else:
        lines.append("- Sector snapshot unavailable.")

    lines.extend(["", "## Movers", ""])
    if top_gainer:
        lines.append(f"- **Top gainer:** {row_symbol(top_gainer)} ({format_percent(pct_from_row(top_gainer))})")
    else:
        lines.append("- Top gainer unavailable.")
    if top_loser:
        lines.append(f"- **Top loser:** {row_symbol(top_loser)} ({format_percent(pct_from_row(top_loser))})")
    else:
        lines.append("- Top loser unavailable.")

    lines.extend(
        [
            "",
            "## S&P 500 Technical Context",
            "",
            f"- **5-day average:** {format_number(ma5)}",
            f"- **20-day average:** {format_number(ma20)}",
            f"- **20-day resistance:** {format_number(resistance)}",
            f"- **20-day support:** {format_number(support)}",
            f"- **Trend read:** {trend}",
            "",
            "## Upcoming Earnings",
            "",
        ]
    )

    if earnings:
        lines.extend(["| Date | Symbol | EPS Estimate | Revenue Estimate |", "|---|---:|---:|---:|"])
        for row in earnings:
            lines.append(
                "| "
                f"{row.get('date', 'N/A')} | "
                f"{row.get('symbol', 'N/A')} | "
                f"{format_number(row.get('epsEstimated'))} | "
                f"{format_number(row.get('revenueEstimated'), 0)} |"
            )
    else:
        lines.append("No upcoming earnings returned for the next seven days.")

    lines.extend(["", "## Market Drivers / Headlines", ""])
    if headlines:
        for row in headlines:
            title = str(row.get("title") or row.get("headline") or "Untitled").strip()
            site = str(row.get("site") or row.get("publisher") or "").strip()
            url = str(row.get("url") or "").strip()
            suffix = f" ({site})" if site else ""
            if url:
                lines.append(f"- [{title}]({url}){suffix}")
            else:
                lines.append(f"- {title}{suffix}")
    else:
        lines.append("No headlines available; possible drivers could not be inferred.")

    lines.extend(["", "## Commentary", "", commentary, ""])

    markdown = "\n".join(lines)
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")

    summary = "\n".join(
        [
            f"Daily Market Recap - {recap_date}",
            f"S&P 500 {format_number(spx.get('price'))} ({format_percent(spx_change)}); trend {trend}.",
            f"Nasdaq {format_percent(nasdaq_change)}, Dow {format_percent(pct_from_row(dow))}; VIX {format_number(vix_level)} ({vix_label(vix_level)}).",
            (
                f"Best sector: {sector_name(best_sector)} ({format_percent(pct_from_row(best_sector))}); "
                f"worst: {sector_name(worst_sector)} ({format_percent(pct_from_row(worst_sector))})."
                if best_sector and worst_sector
                else "Sector snapshot unavailable."
            ),
            (
                f"Top gainer: {row_symbol(top_gainer)} ({format_percent(pct_from_row(top_gainer))}); "
                f"top loser: {row_symbol(top_loser)} ({format_percent(pct_from_row(top_loser))})."
                if top_gainer and top_loser
                else "Gainer/loser snapshot unavailable."
            ),
            "Full markdown recap attached. Informational only; not investment advice.",
        ]
    )
    return RecapResult(output_path=output_path, summary=summary, markdown=markdown)


def telegram_token() -> str:
    """Return the configured Telegram bot token."""
    return os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_API_TOKEN") or ""


def telegram_post(token: str, method: str, **kwargs: Any) -> dict[str, Any]:
    """Post to a Telegram bot API method and validate the response."""
    response = requests.post(f"{TELEGRAM_API}/bot{token}/{method}", timeout=30, **kwargs)
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        raise RuntimeError(f"Telegram {method} failed: {payload}")
    return payload


def send_to_telegram(result: RecapResult, chat_id: str) -> None:
    """Send summary text and markdown document to Telegram."""
    token = telegram_token()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN or TELEGRAM_API_TOKEN is required to send Telegram messages")
    if not chat_id:
        raise RuntimeError("TELEGRAM_CHAT_ID or --telegram-chat-id is required to send Telegram messages")

    telegram_post(token, "sendMessage", data={"chat_id": chat_id, "text": result.summary})
    with result.output_path.open("rb") as handle:
        telegram_post(
            token,
            "sendDocument",
            data={"chat_id": chat_id, "caption": f"Daily market recap: {result.output_path.name}"},
            files={"document": (result.output_path.name, handle, "text/markdown")},
        )


def main() -> None:
    """Entrypoint."""
    args = parse_args()
    recap_date = get_recap_date(args.date)
    api_key = args.fmp_api_key or os.environ.get("FMP_API_KEY", "")
    if not api_key:
        raise SystemExit("FMP_API_KEY or --fmp-api-key is required")

    result = build_recap(fetch_market_data(api_key, recap_date), recap_date, Path(args.out_dir))
    print(result.summary)
    print(f"Report written: {result.output_path}")

    if args.send_telegram:
        chat_id = args.telegram_chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")
        send_to_telegram(result, chat_id)
        print("Telegram summary and markdown document sent.")


if __name__ == "__main__":
    main()
