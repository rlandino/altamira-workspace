#!/usr/bin/env python3
"""
Generate an Altamira daily market recap and optionally deliver it to Telegram.

The report uses FMP quote, sector, mover, earnings, news, and historical-price
data. It writes outputs/daily-market-recap-{DATE}.md and can send both a short
summary and the markdown file to a Telegram chat.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests

WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS = WORKSPACE / "outputs"
FMP_V3 = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"


@dataclass(frozen=True)
class RecapResult:
    """Report paths and summary text produced by the recap."""

    report_path: Path
    summary: str
    telegram_sent: bool


def parse_args() -> argparse.Namespace:
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description="Generate and send a daily market recap")
    parser.add_argument("--date", default=None, help="Report date in YYYY-MM-DD format")
    parser.add_argument("--out-dir", default=str(OUTPUTS), help="Output directory")
    parser.add_argument(
        "--send-telegram",
        action="store_true",
        help="Send the summary and markdown report to Telegram",
    )
    parser.add_argument(
        "--telegram-chat-id",
        default=None,
        help="Telegram chat/channel ID; defaults to TELEGRAM_CHAT_ID",
    )
    parser.add_argument(
        "--no-document",
        action="store_true",
        help="Send only the Telegram summary, not the markdown document",
    )
    return parser.parse_args()


def get_fmp_key() -> str:
    """Return the FMP API key from the environment or workspace local fallback."""
    return os.environ.get("FMP_API_KEY", "").strip() or load_workspace_fmp_fallback()


def load_workspace_fmp_fallback() -> str:
    """Reuse the existing local-dev FMP fallback from market_data_api.py if present."""
    market_api = WORKSPACE / "scripts" / "market_data_api.py"
    try:
        text = market_api.read_text(encoding="utf-8")
    except OSError:
        return ""
    match = re.search(r'DEFAULT_KEY\s*=\s*os\.environ\.get\("FMP_API_KEY",\s*"([^"]+)"\)', text)
    return match.group(1) if match else ""


def fmp_get(base: str, path: str, params: dict[str, Any] | None = None) -> Any:
    """Fetch JSON from FMP and raise a helpful error on failure."""
    key = get_fmp_key()
    if not key:
        raise RuntimeError("FMP_API_KEY is not set and no workspace fallback key is available")

    url = f"{base}{path}"
    query = dict(params or {})
    query["apikey"] = key
    response = requests.get(url, params=query, timeout=20)
    response.raise_for_status()
    return response.json()


def as_float(value: Any, default: float = 0.0) -> float:
    """Convert API values like '1.2%' or numbers into floats."""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace("%", "").replace(",", "").strip()
    if not text:
        return default
    try:
        return float(text)
    except ValueError:
        return default


def fmt_number(value: Any, digits: int = 2) -> str:
    """Format a numeric value for report tables."""
    number = as_float(value, default=float("nan"))
    if number != number:
        return "n/a"
    return f"{number:,.{digits}f}"


def fmt_pct(value: Any, digits: int = 2) -> str:
    """Format a percent value, preserving sign."""
    number = as_float(value, default=float("nan"))
    if number != number:
        return "n/a"
    return f"{number:+.{digits}f}%"


def first_value(item: dict[str, Any], names: tuple[str, ...], default: Any = None) -> Any:
    """Return the first present value from a dict."""
    for name in names:
        if name in item and item[name] not in (None, ""):
            return item[name]
    return default


def quote_lookup() -> dict[str, dict[str, Any]]:
    """Fetch core index and ETF quotes."""
    symbols = "^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ,DIA,IWM"
    data = fmp_get(FMP_V3, f"/quote/{symbols}")
    if not isinstance(data, list):
        return {}
    return {str(item.get("symbol", "")).upper(): item for item in data if isinstance(item, dict)}


def fetch_sector_snapshot(report_date: date) -> tuple[list[dict[str, Any]], str | None]:
    """Fetch sector snapshot, retrying recent dates when today has no data."""
    for days_back in range(0, 8):
        snapshot_date = (report_date - timedelta(days=days_back)).isoformat()
        try:
            data = fmp_get(
                FMP_STABLE,
                "/sector-performance-snapshot",
                {"date": snapshot_date},
            )
        except Exception:
            continue
        rows = normalize_sector_rows(data)
        if rows:
            return rows, snapshot_date
    return [], None


def normalize_sector_rows(data: Any) -> list[dict[str, Any]]:
    """Normalize FMP sector data into rows with sector and changesPercentage."""
    rows: list[dict[str, Any]] = []
    if isinstance(data, dict):
        possible = data.get("data") or data.get("sectors") or data.get("sectorPerformance")
        if isinstance(possible, list):
            data = possible
        else:
            data = [data]
    if not isinstance(data, list):
        return rows
    for item in data:
        if not isinstance(item, dict):
            continue
        sector = first_value(item, ("sector", "sectorName", "name", "label"), "Unknown")
        change = first_value(
            item,
            ("changesPercentage", "changePercentage", "performance", "change", "percentage"),
            0.0,
        )
        rows.append({"sector": sector, "changesPercentage": as_float(change)})
    return sorted(rows, key=lambda row: row["changesPercentage"], reverse=True)


def fetch_movers() -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Fetch biggest gainer and loser."""
    gainer: dict[str, Any] | None = None
    loser: dict[str, Any] | None = None
    try:
        gainers = fmp_get(FMP_STABLE, "/biggest-gainers")
        if isinstance(gainers, list) and gainers:
            gainer = gainers[0]
    except Exception:
        pass
    try:
        losers = fmp_get(FMP_STABLE, "/biggest-losers")
        if isinstance(losers, list) and losers:
            loser = losers[0]
    except Exception:
        pass
    return gainer, loser


def fetch_earnings(report_date: date) -> list[dict[str, Any]]:
    """Fetch upcoming earnings for the next week."""
    end_date = report_date + timedelta(days=7)
    try:
        data = fmp_get(
            FMP_V3,
            "/earning_calendar",
            {"from": report_date.isoformat(), "to": end_date.isoformat()},
        )
    except Exception:
        return []
    return data if isinstance(data, list) else []


def fetch_headlines(limit: int = 8) -> list[dict[str, Any]]:
    """Fetch broad market headlines."""
    try:
        data = fmp_get(FMP_STABLE, "/news/general-latest", {"page": 0, "limit": limit})
    except Exception:
        return []
    return data if isinstance(data, list) else []


def fetch_history(symbol: str, report_date: date) -> list[dict[str, Any]]:
    """Fetch recent historical EOD rows for technical context."""
    start_date = report_date - timedelta(days=45)
    try:
        data = fmp_get(
            FMP_STABLE,
            "/historical-price-eod/light",
            {"symbol": symbol, "from": start_date.isoformat(), "to": report_date.isoformat()},
        )
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    rows = [
        row
        for row in data
        if isinstance(row, dict) and first_value(row, ("date",), None) and first_value(row, ("close", "adjClose", "price"), None)
    ]
    return sorted(rows, key=lambda row: str(row.get("date")))


def technicals(history: list[dict[str, Any]], current_price: float) -> dict[str, Any]:
    """Compute trend, moving averages, support, and resistance."""
    closes = [as_float(first_value(row, ("close", "adjClose", "price"), 0.0)) for row in history]
    closes = [close for close in closes if close > 0]
    if not closes:
        return {"sma5": None, "sma20": None, "support": None, "resistance": None, "trend": "Unknown"}

    recent = closes[-20:]
    sma5 = sum(closes[-5:]) / min(5, len(closes))
    sma20 = sum(recent) / len(recent)
    support = min(recent)
    resistance = max(recent)

    if current_price > sma5 and current_price > sma20:
        trend = "Bullish"
    elif current_price < sma5 and current_price < sma20:
        trend = "Bearish"
    else:
        trend = "Mixed"

    return {
        "sma5": sma5,
        "sma20": sma20,
        "support": support,
        "resistance": resistance,
        "trend": trend,
    }


def vix_label(vix_level: float) -> str:
    """Classify VIX level into trading context."""
    if vix_level >= 30:
        return "crisis/elevated"
    if vix_level >= 20:
        return "elevated"
    if vix_level < 15:
        return "low"
    return "normal"


def make_report(
    report_date: date,
    quotes: dict[str, dict[str, Any]],
    sectors: list[dict[str, Any]],
    sector_date: str | None,
    gainer: dict[str, Any] | None,
    loser: dict[str, Any] | None,
    earnings: list[dict[str, Any]],
    headlines: list[dict[str, Any]],
    tech: dict[str, Any],
) -> tuple[str, str]:
    """Build markdown report and Telegram summary."""
    spx = quotes.get("^GSPC", {})
    dow = quotes.get("^DJI", {})
    nasdaq = quotes.get("^IXIC", {})
    vix = quotes.get("^VIX", {})
    spy = quotes.get("SPY", {})
    qqq = quotes.get("QQQ", {})
    dia = quotes.get("DIA", {})
    iwm = quotes.get("IWM", {})

    spx_price = as_float(spx.get("price"))
    vix_level = as_float(vix.get("price"))
    vix_context = vix_label(vix_level)
    trend = str(tech.get("trend", "Unknown"))
    best_sector = sectors[0] if sectors else None
    worst_sector = sectors[-1] if sectors else None

    summary_lines = [
        f"Altamira Daily Market Recap - {report_date.isoformat()}",
        f"S&P 500 {fmt_number(spx.get('price'))} ({fmt_pct(spx.get('changesPercentage'))}); trend {trend}.",
        f"Nasdaq {fmt_pct(nasdaq.get('changesPercentage'))}, Dow {fmt_pct(dow.get('changesPercentage'))}, VIX {fmt_number(vix.get('price'))} ({vix_context}).",
    ]
    if best_sector and worst_sector:
        summary_lines.append(
            f"Best sector: {best_sector['sector']} {fmt_pct(best_sector['changesPercentage'])}; "
            f"worst: {worst_sector['sector']} {fmt_pct(worst_sector['changesPercentage'])}."
        )
    if gainer or loser:
        gainer_text = format_mover(gainer) if gainer else "n/a"
        loser_text = format_mover(loser) if loser else "n/a"
        summary_lines.append(f"Top mover: {gainer_text}; weakest: {loser_text}.")
    summary = "\n".join(summary_lines)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    report = [
        f"# Daily Market Recap - {report_date.isoformat()}",
        "",
        f"Generated: {generated_at}",
        "",
        "## Executive Summary",
        "",
        f"- S&P 500: **{fmt_number(spx.get('price'))}** ({fmt_pct(spx.get('changesPercentage'))}); trend: **{trend}**.",
        f"- Nasdaq: **{fmt_pct(nasdaq.get('changesPercentage'))}**; Dow: **{fmt_pct(dow.get('changesPercentage'))}**.",
        f"- VIX: **{fmt_number(vix.get('price'))}** ({vix_context}).",
    ]
    if best_sector and worst_sector:
        report.append(
            f"- Sector leadership: **{best_sector['sector']}** ({fmt_pct(best_sector['changesPercentage'])}); "
            f"laggard: **{worst_sector['sector']}** ({fmt_pct(worst_sector['changesPercentage'])})."
        )
    report.extend(
        [
            "",
            "## Market Dashboard",
            "",
            "| Instrument | Level | Day Change |",
            "|---|---:|---:|",
            f"| S&P 500 (^GSPC) | {fmt_number(spx.get('price'))} | {fmt_pct(spx.get('changesPercentage'))} |",
            f"| Nasdaq Composite (^IXIC) | {fmt_number(nasdaq.get('price'))} | {fmt_pct(nasdaq.get('changesPercentage'))} |",
            f"| Dow Jones (^DJI) | {fmt_number(dow.get('price'))} | {fmt_pct(dow.get('changesPercentage'))} |",
            f"| SPY | {fmt_number(spy.get('price'))} | {fmt_pct(spy.get('changesPercentage'))} |",
            f"| QQQ | {fmt_number(qqq.get('price'))} | {fmt_pct(qqq.get('changesPercentage'))} |",
            f"| DIA | {fmt_number(dia.get('price'))} | {fmt_pct(dia.get('changesPercentage'))} |",
            f"| IWM | {fmt_number(iwm.get('price'))} | {fmt_pct(iwm.get('changesPercentage'))} |",
            f"| VIX | {fmt_number(vix.get('price'))} | {fmt_pct(vix.get('changesPercentage'))} |",
            "",
            "## Sector Snapshot",
            "",
        ]
    )
    if sectors:
        report.append(f"Source date: {sector_date or report_date.isoformat()}")
        report.extend(["", "| Sector | Performance |", "|---|---:|"])
        for row in sectors:
            report.append(f"| {row['sector']} | {fmt_pct(row['changesPercentage'])} |")
    else:
        report.append("Sector snapshot was unavailable from FMP.")

    report.extend(["", "## Movers", ""])
    report.append(f"- Biggest gainer: {format_mover(gainer) if gainer else 'Unavailable'}")
    report.append(f"- Biggest loser: {format_mover(loser) if loser else 'Unavailable'}")

    report.extend(["", "## Market Drivers From Headlines", ""])
    if headlines:
        for item in headlines[:8]:
            title = first_value(item, ("title", "headline", "text"), "Untitled")
            source = first_value(item, ("site", "publisher", "source"), "")
            published = first_value(item, ("publishedDate", "date"), "")
            suffix = f" ({source})" if source else ""
            date_suffix = f" - {published}" if published else ""
            report.append(f"- {title}{suffix}{date_suffix}")
    else:
        report.append("- No market headlines were returned; no causal read-through inferred.")

    report.extend(
        [
            "",
            "## Technical Snapshot",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| Current S&P 500 | {fmt_number(spx_price)} |",
            f"| 5-day average | {fmt_number(tech.get('sma5'))} |",
            f"| 20-day average | {fmt_number(tech.get('sma20'))} |",
            f"| 20-day resistance | {fmt_number(tech.get('resistance'))} |",
            f"| 20-day support | {fmt_number(tech.get('support'))} |",
            f"| Trend | {trend} |",
            "",
            "## Earnings Watch",
            "",
        ]
    )
    if earnings:
        report.extend(["| Date | Symbol | EPS Estimate | Revenue Estimate |", "|---|---|---:|---:|"])
        for item in earnings[:20]:
            eps = first_value(item, ("epsEstimated", "epsestimate", "eps"), None)
            revenue = first_value(item, ("revenueEstimated", "revenueEstimate", "revenue"), None)
            report.append(
                f"| {first_value(item, ('date',), '')} | {first_value(item, ('symbol',), '')} | "
                f"{fmt_number(eps)} | {fmt_number(revenue, 0)} |"
            )
    else:
        report.append("No earnings events returned for the next 7 days.")

    report.extend(
        [
            "",
            "## Options And Risk Context",
            "",
            f"- VIX is {vix_context} at {fmt_number(vix_level)}, which informs premium-selling aggressiveness and spread width.",
            "- Keep position sizing aligned with the risk framework; avoid holding short options through unplanned earnings.",
            "- This recap is for informational purposes only and is not investment advice.",
            "",
            "## Telegram Summary",
            "",
            "```",
            summary,
            "```",
            "",
            "_Financial disclaimer: This report is informational only and is not investment advice._",
        ]
    )
    return "\n".join(report) + "\n", summary


def format_mover(item: dict[str, Any] | None) -> str:
    """Format a mover row for summary output."""
    if not item:
        return "n/a"
    symbol = first_value(item, ("symbol", "ticker"), "n/a")
    price = first_value(item, ("price",), None)
    change = first_value(item, ("changesPercentage", "changePercentage", "changes"), None)
    if price is None:
        return f"{symbol} ({fmt_pct(change)})"
    return f"{symbol} {fmt_number(price)} ({fmt_pct(change)})"


def send_telegram(summary: str, report_path: Path, chat_id: str | None, send_document: bool) -> None:
    """Send a summary and optionally the markdown file to Telegram."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_API_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN or TELEGRAM_API_TOKEN is required")
    resolved_chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")
    if not resolved_chat_id:
        raise RuntimeError("TELEGRAM_CHAT_ID is required unless --telegram-chat-id is provided")

    api_base = f"https://api.telegram.org/bot{token}"
    message = requests.post(
        f"{api_base}/sendMessage",
        data={"chat_id": resolved_chat_id, "text": summary, "disable_web_page_preview": True},
        timeout=20,
    )
    message.raise_for_status()

    if send_document:
        with report_path.open("rb") as handle:
            document = requests.post(
                f"{api_base}/sendDocument",
                data={"chat_id": resolved_chat_id, "caption": "Daily market recap markdown report"},
                files={"document": (report_path.name, handle, "text/markdown")},
                timeout=30,
            )
        document.raise_for_status()


def run(args: argparse.Namespace) -> RecapResult:
    """Generate the recap and optionally send it to Telegram."""
    report_date = date.fromisoformat(args.date) if args.date else date.today()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    quotes = quote_lookup()
    sectors, sector_date = fetch_sector_snapshot(report_date)
    gainer, loser = fetch_movers()
    earnings = fetch_earnings(report_date)
    headlines = fetch_headlines()
    spx_price = as_float(quotes.get("^GSPC", {}).get("price"))
    tech = technicals(fetch_history("^GSPC", report_date), spx_price)

    markdown, summary = make_report(
        report_date=report_date,
        quotes=quotes,
        sectors=sectors,
        sector_date=sector_date,
        gainer=gainer,
        loser=loser,
        earnings=earnings,
        headlines=headlines,
        tech=tech,
    )

    report_path = out_dir / f"daily-market-recap-{report_date.isoformat()}.md"
    report_path.write_text(markdown, encoding="utf-8")

    telegram_sent = False
    if args.send_telegram:
        send_telegram(
            summary=summary,
            report_path=report_path,
            chat_id=args.telegram_chat_id,
            send_document=not args.no_document,
        )
        telegram_sent = True

    return RecapResult(report_path=report_path, summary=summary, telegram_sent=telegram_sent)


def main() -> None:
    """CLI entrypoint."""
    try:
        result = run(parse_args())
    except Exception as exc:
        print(f"[daily_market_recap] ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print(result.summary)
    print(f"Report: {result.report_path}")
    if result.telegram_sent:
        print("Telegram: sent summary and markdown report")


if __name__ == "__main__":
    main()
