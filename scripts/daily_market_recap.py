#!/usr/bin/env python3
"""Generate and optionally send the Altamira daily market recap.

The recap uses Financial Modeling Prep for market data, writes a Markdown file
to outputs/, and can send both a short summary and the Markdown document to a
Telegram channel.
"""

from __future__ import annotations

import argparse
import ast
import os
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python 3.8 fallback
    ZoneInfo = None  # type: ignore[assignment]


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUT_DIR = WORKSPACE / "outputs"
FMP_V3 = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"

INDEX_NAMES = {
    "^GSPC": "S&P 500",
    "^DJI": "Dow Jones",
    "^IXIC": "Nasdaq Composite",
    "^VIX": "VIX",
    "SPY": "SPY",
    "QQQ": "QQQ",
}

SECTOR_ETFS = {
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


@dataclass
class RecapResult:
    output_path: Path
    summary: str
    telegram_summary_sent: bool = False
    telegram_document_sent: bool = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the daily market recap.")
    parser.add_argument(
        "--date",
        default=current_market_date(),
        help="Report date in YYYY-MM-DD format. Defaults to today's ET date.",
    )
    parser.add_argument(
        "--send-telegram",
        action="store_true",
        help="Send summary and Markdown file to Telegram after generation.",
    )
    parser.add_argument(
        "--telegram-chat-id",
        default=os.environ.get("TELEGRAM_CHAT_ID", ""),
        help="Telegram chat/channel ID. Defaults to TELEGRAM_CHAT_ID.",
    )
    parser.add_argument(
        "--telegram-token",
        default=os.environ.get("TELEGRAM_BOT_TOKEN")
        or os.environ.get("TELEGRAM_API_TOKEN", ""),
        help="Telegram bot token. Defaults to TELEGRAM_BOT_TOKEN or TELEGRAM_API_TOKEN.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(OUTPUT_DIR),
        help="Directory for the generated Markdown file.",
    )
    return parser.parse_args()


def current_market_date() -> str:
    if ZoneInfo is not None:
        return datetime.now(ZoneInfo("America/New_York")).date().isoformat()
    return date.today().isoformat()


def fmp_key() -> str:
    key = os.environ.get("FMP_API_KEY")
    if key:
        return key
    return workspace_fmp_fallback_key()


def workspace_fmp_fallback_key() -> str:
    """Reuse the workspace market-data fallback key without duplicating it here."""
    market_api_path = WORKSPACE / "scripts" / "market_data_api.py"
    try:
        tree = ast.parse(market_api_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise RuntimeError("Missing FMP_API_KEY and no workspace fallback is readable.") from exc

    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "DEFAULT_KEY" for target in node.targets):
            continue
        value = node.value
        if (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Attribute)
            and value.func.attr == "get"
            and len(value.args) >= 2
            and isinstance(value.args[1], ast.Constant)
            and isinstance(value.args[1].value, str)
        ):
            return value.args[1].value

    raise RuntimeError("Missing FMP_API_KEY and no workspace fallback key was found.")


def get_json(base_url: str, path: str, params: dict[str, Any] | None = None) -> Any:
    request_params = dict(params or {})
    request_params["apikey"] = fmp_key()
    url = f"{base_url}{path}"
    response = requests.get(url, params=request_params, timeout=20)
    response.raise_for_status()
    return response.json()


def safe_call(label: str, func: Any, fallback: Any) -> Any:
    try:
        return func()
    except Exception as exc:
        print(f"Warning: {label} unavailable: {exc}", file=sys.stderr)
        return fallback


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip().replace("%", "")
        if not value:
            return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fmt_num(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "N/A"
    return f"{value:,.{digits}f}"


def fmt_pct(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "N/A"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.{digits}f}%"


def normalize_quote(row: dict[str, Any]) -> dict[str, Any]:
    symbol = row.get("symbol") or ""
    change_pct = (
        row.get("changesPercentage")
        if row.get("changesPercentage") is not None
        else row.get("changePercentage")
    )
    return {
        "symbol": symbol,
        "name": INDEX_NAMES.get(symbol, row.get("name") or symbol),
        "price": as_float(row.get("price")),
        "change_pct": as_float(change_pct),
        "change": as_float(row.get("change")),
    }


def fetch_quotes(symbols: list[str]) -> dict[str, dict[str, Any]]:
    data = get_json(FMP_V3, f"/quote/{','.join(symbols)}")
    if not isinstance(data, list):
        return {}
    return {row.get("symbol"): normalize_quote(row) for row in data if row.get("symbol")}


def pick_first_mover(path: str) -> dict[str, Any] | None:
    data = get_json(FMP_STABLE, path)
    if not isinstance(data, list) or not data:
        return None
    row = data[0]
    symbol = row.get("symbol") or row.get("ticker") or "N/A"
    return {
        "symbol": symbol,
        "name": row.get("name") or row.get("companyName") or symbol,
        "change_pct": as_float(
            row.get("changesPercentage")
            if row.get("changesPercentage") is not None
            else row.get("changePercentage")
        ),
        "price": as_float(row.get("price")),
    }


def parse_sector_snapshot(data: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(data, dict):
        possible_rows = data.get("data") or data.get("sectors") or data.get("sectorPerformance")
        if possible_rows is None:
            possible_rows = [data]
    else:
        possible_rows = data

    if not isinstance(possible_rows, list):
        return rows

    for row in possible_rows:
        if not isinstance(row, dict):
            continue
        name = (
            row.get("sector")
            or row.get("sectorName")
            or row.get("name")
            or row.get("symbol")
        )
        change_pct = (
            row.get("changesPercentage")
            if row.get("changesPercentage") is not None
            else row.get("changePercentage")
        )
        change = as_float(change_pct)
        if name and change is not None:
            rows.append({"name": str(name), "change_pct": change})
    return rows


def fetch_sector_snapshot(report_date: str) -> tuple[list[dict[str, Any]], str]:
    """Return sector performance rows and source label."""
    for offset in range(0, 8):
        date_str = (
            datetime.fromisoformat(report_date).date() - timedelta(days=offset)
        ).isoformat()
        try:
            rows = parse_sector_snapshot(
                get_json(FMP_STABLE, "/sector-performance-snapshot", {"date": date_str})
            )
        except Exception:
            rows = []
        non_zero = [row for row in rows if row["change_pct"] != 0]
        if non_zero:
            return non_zero, f"FMP sector snapshot ({date_str})"

    quotes = fetch_quotes(list(SECTOR_ETFS))
    rows = []
    for symbol, sector_name in SECTOR_ETFS.items():
        quote = quotes.get(symbol)
        if not quote:
            continue
        change = quote.get("change_pct")
        if change is not None:
            rows.append({"name": sector_name, "symbol": symbol, "change_pct": change})
    return rows, "sector ETF proxy"


def fetch_historical_spx(report_date: str) -> list[dict[str, Any]]:
    to_date = datetime.fromisoformat(report_date).date()
    from_date = to_date - timedelta(days=45)
    data = get_json(
        FMP_V3,
        "/historical-price-full/^GSPC",
        {"from": from_date.isoformat(), "to": to_date.isoformat()},
    )
    if isinstance(data, dict) and isinstance(data.get("historical"), list):
        rows = data["historical"]
    elif isinstance(data, list):
        rows = data
    else:
        rows = []
    return sorted(
        [row for row in rows if isinstance(row, dict)],
        key=lambda row: row.get("date", ""),
    )


def moving_average(values: list[float], length: int) -> float | None:
    if len(values) < length:
        return None
    return sum(values[-length:]) / length


def fetch_earnings(report_date: str) -> list[dict[str, Any]]:
    start = datetime.fromisoformat(report_date).date()
    end = start + timedelta(days=7)
    data = get_json(
        FMP_V3,
        "/earning_calendar",
        {"from": start.isoformat(), "to": end.isoformat()},
    )
    if not isinstance(data, list):
        return []
    rows = []
    seen = set()
    for row in data:
        if not isinstance(row, dict):
            continue
        symbol = str(row.get("symbol") or "").strip().upper()
        if not is_us_style_symbol(symbol):
            continue
        key = (row.get("date") or "", symbol)
        if key in seen:
            continue
        seen.add(key)
        row["symbol"] = symbol
        rows.append(row)
    return sorted(rows, key=earnings_sort_key)


def earnings_sort_key(row: dict[str, Any]) -> tuple[str, int, float, str]:
    revenue = as_float(row.get("revenueEstimated"))
    has_revenue_rank = 0 if revenue is not None else 1
    return (
        row.get("date") or "",
        has_revenue_rank,
        -(revenue or 0),
        row.get("symbol") or "",
    )


def is_us_style_symbol(symbol: str) -> bool:
    if not symbol or "." in symbol or symbol[0].isdigit():
        return False
    normalized = symbol.replace("-", "").replace("/", "")
    if not normalized.isalnum() or not any(char.isalpha() for char in normalized):
        return False
    if len(normalized) > 5:
        return False
    # Common OTC/foreign/bankruptcy suffixes clutter broad FMP calendars.
    if len(normalized) == 5 and normalized[-1] in {"F", "Q", "R", "U", "W", "Y"}:
        return False
    return True


def fetch_news() -> list[dict[str, Any]]:
    try:
        data = get_json(FMP_STABLE, "/news/general-latest", {"page": 0, "limit": 8})
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict)]


def trend_label(price: float | None, ma_5: float | None, ma_20: float | None) -> str:
    if price is None or ma_5 is None or ma_20 is None:
        return "N/A"
    if price > ma_5 and price > ma_20:
        return "Bullish"
    if price < ma_5 and price < ma_20:
        return "Bearish"
    return "Mixed"


def vix_label(vix: float | None) -> str:
    if vix is None:
        return "N/A"
    if vix < 15:
        return "Low"
    if vix > 20:
        return "Elevated"
    return "Normal"


def describe_market_direction(spx_change: float | None, nasdaq_change: float | None) -> str:
    changes = [value for value in [spx_change, nasdaq_change] if value is not None]
    if not changes:
        return "mixed"
    if all(value > 0.15 for value in changes):
        return "higher"
    if all(value < -0.15 for value in changes):
        return "lower"
    return "mixed"


def top_news_lines(news: list[dict[str, Any]], limit: int = 5) -> list[str]:
    lines = []
    for row in news[:limit]:
        title = row.get("title") or row.get("headline") or row.get("text")
        site = row.get("site") or row.get("publisher") or ""
        if title:
            suffix = f" ({site})" if site else ""
            lines.append(f"- {title}{suffix}")
    return lines


def earnings_rows(earnings: list[dict[str, Any]], limit: int = 12) -> list[str]:
    if not earnings:
        return ["No US-style ticker earnings returned for the next 7 days."]
    rows = ["| Date | Symbol | EPS Est. | Revenue Est. |", "|---|---:|---:|---:|"]
    for row in earnings[:limit]:
        eps = as_float(row.get("epsEstimated"))
        revenue = as_float(row.get("revenueEstimated"))
        revenue_text = "N/A" if revenue is None else f"${revenue / 1_000_000:,.1f}M"
        rows.append(
            f"| {row.get('date', 'N/A')} | {row.get('symbol', 'N/A')} | "
            f"{fmt_num(eps, 2)} | {revenue_text} |"
        )
    if len(earnings) > limit:
        rows.append(f"| ... | {len(earnings) - limit} more |  |  |")
    return rows


def build_recap(report_date: str) -> tuple[str, str]:
    quotes = safe_call(
        "quotes",
        lambda: fetch_quotes(["^GSPC", "^DJI", "^IXIC", "^VIX", "SPY", "QQQ"]),
        {},
    )
    hot_stock = safe_call("biggest gainers", lambda: pick_first_mover("/biggest-gainers"), None)
    big_loser = safe_call("biggest losers", lambda: pick_first_mover("/biggest-losers"), None)
    sectors, sector_source = safe_call(
        "sector snapshot",
        lambda: fetch_sector_snapshot(report_date),
        ([], "unavailable"),
    )
    historical = safe_call("S&P 500 history", lambda: fetch_historical_spx(report_date), [])
    earnings = safe_call("earnings calendar", lambda: fetch_earnings(report_date), [])
    news = fetch_news()

    closes = [as_float(row.get("close")) for row in historical]
    closes = [value for value in closes if value is not None]
    highs = [as_float(row.get("high")) for row in historical[-20:]]
    highs = [value for value in highs if value is not None]
    lows = [as_float(row.get("low")) for row in historical[-20:]]
    lows = [value for value in lows if value is not None]

    spx = quotes.get("^GSPC", {})
    nasdaq = quotes.get("^IXIC", {})
    vix = quotes.get("^VIX", {})
    spx_price = spx.get("price")
    ma_5 = moving_average(closes, 5)
    ma_20 = moving_average(closes, 20)
    support = min(lows) if lows else None
    resistance = max(highs) if highs else None
    trend = trend_label(spx_price, ma_5, ma_20)
    vix_context = vix_label(vix.get("price"))

    best_sector = max(sectors, key=lambda row: row["change_pct"]) if sectors else None
    worst_sector = min(sectors, key=lambda row: row["change_pct"]) if sectors else None
    direction = describe_market_direction(spx.get("change_pct"), nasdaq.get("change_pct"))

    summary = (
        f"Daily Market Recap {report_date}: S&P 500 {fmt_pct(spx.get('change_pct'))} "
        f"at {fmt_num(spx_price)}, Nasdaq {fmt_pct(nasdaq.get('change_pct'))}; "
        f"trend {trend}, VIX {fmt_num(vix.get('price'))} ({vix_context})."
    )
    if best_sector:
        summary += f" Best sector: {best_sector['name']} {fmt_pct(best_sector['change_pct'])}."
    if worst_sector:
        summary += f" Worst sector: {worst_sector['name']} {fmt_pct(worst_sector['change_pct'])}."
    if hot_stock and big_loser:
        summary += (
            f" Hot stock: {hot_stock['symbol']} {fmt_pct(hot_stock['change_pct'])}; "
            f"biggest loser: {big_loser['symbol']} {fmt_pct(big_loser['change_pct'])}."
        )

    lines = [
        f"# Daily Market Recap - {report_date}",
        "",
        "> Informational market commentary only. Not investment advice.",
        "",
        "## Executive Summary",
        "",
        summary,
        "",
        "## Market Indices",
        "",
        "| Instrument | Level | Day Change |",
        "|---|---:|---:|",
    ]
    for symbol in ["^GSPC", "^DJI", "^IXIC", "SPY", "QQQ"]:
        quote = quotes.get(symbol, {})
        lines.append(
            f"| {quote.get('name', INDEX_NAMES.get(symbol, symbol))} | "
            f"{fmt_num(quote.get('price'))} | {fmt_pct(quote.get('change_pct'))} |"
        )

    lines.extend(
        [
            "",
            "## Volatility",
            "",
            f"- **VIX:** {fmt_num(vix.get('price'))} ({vix_context}), "
            f"{fmt_pct(vix.get('change_pct'))} today.",
            "",
            "## Leadership",
            "",
        ]
    )
    if hot_stock:
        lines.append(
            f"- **Hot stock:** {hot_stock['symbol']} ({hot_stock['name']}), "
            f"{fmt_pct(hot_stock['change_pct'])}."
        )
    if big_loser:
        lines.append(
            f"- **Biggest loser:** {big_loser['symbol']} ({big_loser['name']}), "
            f"{fmt_pct(big_loser['change_pct'])}."
        )
    if best_sector:
        symbol_text = f" ({best_sector['symbol']})" if best_sector.get("symbol") else ""
        lines.append(
            f"- **Best sector:** {best_sector['name']}{symbol_text}, "
            f"{fmt_pct(best_sector['change_pct'])}."
        )
    if worst_sector:
        symbol_text = f" ({worst_sector['symbol']})" if worst_sector.get("symbol") else ""
        lines.append(
            f"- **Worst sector:** {worst_sector['name']}{symbol_text}, "
            f"{fmt_pct(worst_sector['change_pct'])}."
        )
    lines.append(f"- **Sector source:** {sector_source}.")

    lines.extend(
        [
            "",
            "## S&P 500 Technical Snapshot",
            "",
            f"- **Trend:** {trend}",
            f"- **Current level:** {fmt_num(spx_price)}",
            f"- **5-day average:** {fmt_num(ma_5)}",
            f"- **20-day average:** {fmt_num(ma_20)}",
            f"- **20-day resistance:** {fmt_num(resistance)}",
            f"- **20-day support:** {fmt_num(support)}",
            "",
            "## Market Drivers",
            "",
            (
                f"Markets finished {direction} based on the S&P 500 and Nasdaq moves. "
                "Use the headlines below as context for possible drivers; avoid "
                "over-attributing price action without direct confirmation."
            ),
            "",
        ]
    )
    news_lines = top_news_lines(news)
    lines.extend(news_lines if news_lines else ["No headline feed returned from FMP."])

    lines.extend(
        [
            "",
            "## Earnings Calendar - Next 7 Days",
            "",
            *earnings_rows(earnings),
            "",
            "## Trading Takeaways",
            "",
            f"- Index trend is **{trend}** with VIX classified as **{vix_context}**.",
        ]
    )
    if best_sector and worst_sector:
        lines.append(
            f"- Sector tape favors **{best_sector['name']}** over **{worst_sector['name']}** today."
        )
    if vix.get("price") is not None and vix.get("price") > 20:
        lines.append("- Elevated volatility argues for conservative premium-selling size and wider strikes.")
    elif vix.get("price") is not None and vix.get("price") < 15:
        lines.append("- Low volatility limits premium collection; be selective on new short-volatility entries.")
    else:
        lines.append("- Normal volatility supports balanced sizing if liquidity and risk limits are met.")

    lines.extend(
        [
            "",
            "---",
            "",
            f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        ]
    )
    return "\n".join(lines) + "\n", summary


def send_telegram_message(token: str, chat_id: str, text: str) -> None:
    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={
            "chat_id": chat_id,
            "text": text[:4096],
            "disable_web_page_preview": "true",
        },
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        raise RuntimeError(f"Telegram sendMessage failed: {payload}")


def send_telegram_document(token: str, chat_id: str, path: Path, caption: str) -> None:
    with path.open("rb") as handle:
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendDocument",
            data={"chat_id": chat_id, "caption": caption[:1024]},
            files={"document": (path.name, handle, "text/markdown")},
            timeout=30,
        )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        raise RuntimeError(f"Telegram sendDocument failed: {payload}")


def run() -> RecapResult:
    args = parse_args()
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = WORKSPACE / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        datetime.fromisoformat(args.date).date()
    except ValueError as exc:
        raise SystemExit(f"Invalid --date {args.date!r}; expected YYYY-MM-DD") from exc

    markdown, summary = build_recap(args.date)
    output_path = output_dir / f"daily-market-recap-{args.date}.md"
    output_path.write_text(markdown, encoding="utf-8")

    result = RecapResult(output_path=output_path, summary=summary)
    if args.send_telegram:
        if not args.telegram_token:
            raise SystemExit("Missing Telegram token. Set TELEGRAM_BOT_TOKEN or TELEGRAM_API_TOKEN.")
        if not args.telegram_chat_id:
            raise SystemExit("Missing Telegram chat ID. Set TELEGRAM_CHAT_ID or pass --telegram-chat-id.")
        send_telegram_message(args.telegram_token, args.telegram_chat_id, summary)
        result.telegram_summary_sent = True
        send_telegram_document(
            args.telegram_token,
            args.telegram_chat_id,
            output_path,
            f"Daily market recap markdown - {args.date}",
        )
        result.telegram_document_sent = True
    return result


def main() -> int:
    try:
        result = run()
    except requests.HTTPError as exc:
        print(f"HTTP error: {exc}", file=sys.stderr)
        return 1
    except requests.RequestException as exc:
        print(f"Network error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(result.summary)
    print(f"Markdown: {result.output_path.relative_to(WORKSPACE)}")
    if result.telegram_summary_sent and result.telegram_document_sent:
        print("Telegram: summary and markdown document sent")
    elif result.telegram_summary_sent:
        print("Telegram: summary sent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
