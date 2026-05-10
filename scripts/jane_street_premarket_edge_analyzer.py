#!/usr/bin/env python3
"""Run the Jane Street pre-market edge analyzer and optionally send Telegram output."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import re
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python 3.8 fallback
    ZoneInfo = None  # type: ignore


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = WORKSPACE / "outputs"
FMP_BASE = "https://financialmodelingprep.com/api/v3"
DEFAULT_FMP_KEY = "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz"
DEFAULT_LOOKBACK_DAYS = 30
TELEGRAM_LIMIT = 3900

HIGH_IMPACT_TERMS = (
    "cpi",
    "pce",
    "nonfarm",
    "payroll",
    "nfp",
    "fomc",
    "fed",
    "powell",
    "jobless",
    "claims",
    "retail sales",
    "pmi",
    "ism",
    "ppi",
    "gdp",
)
MARKET_MOVERS = {
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "GOOGL",
    "GOOG",
    "META",
    "TSLA",
    "AVGO",
    "JPM",
    "UNH",
    "XOM",
    "LLY",
    "COST",
    "V",
    "MA",
}
NYSE_HOLIDAYS_2026 = {
    "2026-01-01",
    "2026-01-19",
    "2026-02-16",
    "2026-04-03",
    "2026-05-25",
    "2026-06-19",
    "2026-07-03",
    "2026-09-07",
    "2026-11-26",
    "2026-12-25",
}


def et_today() -> dt.date:
    """Return today's date in New York time."""
    if ZoneInfo is None:
        return dt.date.today()
    return dt.datetime.now(ZoneInfo("America/New_York")).date()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Jane Street-style 8 AM pre-market theta briefing."
    )
    parser.add_argument(
        "arguments",
        nargs="*",
        help="Optional flexible args: SPX/ES futures, VIX, and free-text events.",
    )
    parser.add_argument("--date", help="Report date in YYYY-MM-DD. Defaults to ET today.")
    parser.add_argument(
        "--fmp-key",
        default=os.environ.get("FMP_API_KEY", DEFAULT_FMP_KEY),
        help="FMP API key. Defaults to FMP_API_KEY or workspace fallback.",
    )
    parser.add_argument(
        "--send-telegram",
        action="store_true",
        help="Send the generated output to Telegram.",
    )
    parser.add_argument(
        "--telegram-token",
        default=os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN"),
        help="Telegram bot token. Defaults to TELEGRAM_BOT_TOKEN/TELEGRAM_TOKEN.",
    )
    parser.add_argument(
        "--telegram-chat-id",
        default=os.environ.get("TELEGRAM_CHAT_ID"),
        help="Telegram chat/channel ID. Defaults to TELEGRAM_CHAT_ID.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(OUTPUTS_DIR),
        help="Directory for the markdown output.",
    )
    return parser.parse_args()


def parse_flexible_inputs(parts: list[str]) -> dict[str, Any]:
    """Extract SPX/ES futures, VIX, and remaining free-text events."""
    text = " ".join(parts).strip()
    parsed: dict[str, Any] = {"raw": text, "futures": None, "vix": None, "events": ""}
    if not text:
        return parsed

    lowered = text.lower()
    vix_match = re.search(r"\bvix\s*[:=]?\s*(\d+(?:\.\d+)?)", lowered)
    if vix_match:
        parsed["vix"] = float(vix_match.group(1))

    labeled_futures = re.search(
        r"\b(?:spx|es|futures?)\s*[:=]?\s*(\d{4,5}(?:\.\d+)?)", lowered
    )
    if labeled_futures:
        parsed["futures"] = float(labeled_futures.group(1))

    numbers = [float(n) for n in re.findall(r"\b\d+(?:\.\d+)?\b", text)]
    if parsed["futures"] is None:
        for value in numbers:
            if value >= 1000:
                parsed["futures"] = value
                break

    if parsed["vix"] is None:
        for value in numbers:
            if 8 <= value <= 80 and value != parsed["futures"]:
                parsed["vix"] = value
                break

    event_text = text
    if parsed["futures"] is not None:
        event_text = re.sub(
            rf"\b(?:spx|es|futures?)?\s*[:=]?\s*{parsed['futures']:g}\b",
            "",
            event_text,
            flags=re.IGNORECASE,
        )
    if parsed["vix"] is not None:
        event_text = re.sub(
            rf"\bvix\s*[:=]?\s*{parsed['vix']:g}\b",
            "",
            event_text,
            flags=re.IGNORECASE,
        )
    parsed["events"] = " ".join(event_text.split()).strip(" ,")
    return parsed


def fmp_get(path: str, key: str, params: dict[str, Any] | None = None) -> tuple[Any, str]:
    query = dict(params or {})
    query["apikey"] = key
    url = f"{FMP_BASE}{path}?{urllib.parse.urlencode(query)}"
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            payload = response.read().decode("utf-8")
        return json.loads(payload), ""
    except urllib.error.HTTPError as exc:
        return None, f"HTTP {exc.code} for {path}"
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return None, f"{type(exc).__name__}: {exc}"


def quote_for(symbols: list[str], key: str) -> tuple[dict[str, dict[str, Any]], str]:
    encoded = urllib.parse.quote(",".join(symbols), safe=",")
    data, err = fmp_get(f"/quote/{encoded}", key)
    if err or not isinstance(data, list):
        return {}, err or "Unexpected quote response"
    out: dict[str, dict[str, Any]] = {}
    for row in data:
        if isinstance(row, dict) and row.get("symbol"):
            out[str(row["symbol"]).upper()] = row
    return out, ""


def historical_for(symbol: str, key: str, report_date: dt.date) -> tuple[list[dict[str, Any]], str]:
    start = report_date - dt.timedelta(days=DEFAULT_LOOKBACK_DAYS)
    encoded = urllib.parse.quote(symbol, safe="")
    data, err = fmp_get(
        f"/historical-price-full/{encoded}",
        key,
        {"from": start.isoformat(), "to": report_date.isoformat()},
    )
    if err:
        return [], err
    if not isinstance(data, dict) or not isinstance(data.get("historical"), list):
        return [], "Unexpected historical response"
    rows = [r for r in data["historical"] if isinstance(r, dict) and r.get("date")]
    rows.sort(key=lambda row: row.get("date", ""), reverse=True)
    return rows, ""


def first_historical_row(rows: list[dict[str, Any]], before_or_on: dt.date) -> dict[str, Any] | None:
    for row in rows:
        try:
            row_date = dt.date.fromisoformat(str(row.get("date"))[:10])
        except ValueError:
            continue
        if row_date <= before_or_on and row.get("close") is not None:
            return row
    return None


def previous_row(rows: list[dict[str, Any]], date_str: str | None) -> dict[str, Any] | None:
    if not date_str:
        return None
    seen = False
    for row in rows:
        if seen and row.get("close") is not None:
            return row
        if row.get("date") == date_str:
            seen = True
    return None


def economic_calendar(key: str, report_date: dt.date) -> tuple[list[dict[str, Any]], str]:
    data, err = fmp_get(
        "/economic_calendar",
        key,
        {"from": report_date.isoformat(), "to": report_date.isoformat()},
    )
    if err:
        return [], err
    return data if isinstance(data, list) else [], ""


def earnings_calendar(key: str, report_date: dt.date) -> tuple[list[dict[str, Any]], str]:
    data, err = fmp_get(
        "/earning_calendar",
        key,
        {"from": report_date.isoformat(), "to": report_date.isoformat()},
    )
    if err:
        return [], err
    return data if isinstance(data, list) else [], ""


def as_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def fmt_price(value: float | None, decimals: int = 2) -> str:
    if value is None:
        return "N/A"
    return f"{value:,.{decimals}f}"


def fmt_pct(value: float | None, decimals: int = 2) -> str:
    if value is None:
        return "N/A"
    return f"{value:+.{decimals}f}%"


def fmt_points(value: float | None) -> str:
    if value is None:
        return "N/A"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:,.1f}"


def fmt_mcap(value: Any) -> str:
    number = as_float(value)
    if number is None or number <= 0:
        return "N/A"
    if number >= 1_000_000_000_000:
        return f"${number / 1_000_000_000_000:.2f}T"
    if number >= 1_000_000_000:
        return f"${number / 1_000_000_000:.1f}B"
    if number >= 1_000_000:
        return f"${number / 1_000_000:.1f}M"
    return f"${number:,.0f}"


def round_to_increment(value: float, increment: int = 5) -> int:
    return int(round(value / increment) * increment)


def floor_to_increment(value: float, increment: int = 25) -> int:
    return int(math.floor(value / increment) * increment)


def ceil_to_increment(value: float, increment: int = 25) -> int:
    return int(math.ceil(value / increment) * increment)


def close_location(row: dict[str, Any]) -> tuple[str, str]:
    high = as_float(row.get("high"))
    low = as_float(row.get("low"))
    close = as_float(row.get("close"))
    if high is None or low is None or close is None or high <= low:
        return "unknown", "Neutral"
    percentile = (close - low) / (high - low)
    if percentile >= 0.67:
        return "near the highs", "Bullish continuation, but vulnerable to early profit-taking"
    if percentile <= 0.33:
        return "near the lows", "Bearish continuation risk, but susceptible to relief bounce"
    return "in the middle", "Neutral two-way trade"


def classify_calendar(events: list[dict[str, Any]], user_events: str, market_closed: bool) -> tuple[str, list[str]]:
    lines: list[str] = []
    high_impact_count = 0

    if user_events:
        lower = user_events.lower()
        is_high = any(term in lower for term in HIGH_IMPACT_TERMS)
        high_impact_count += 1 if is_high else 0
        impact = "high impact" if is_high else "user-supplied"
        lines.append(f"- User event: {user_events} ({impact}).")

    for event in events:
        country = str(event.get("country") or event.get("currency") or "").upper()
        name = str(event.get("event") or event.get("name") or "Economic event")
        if country and country not in {"US", "USD", "UNITED STATES"}:
            continue
        event_time = str(event.get("date") or event.get("time") or "")[-8:-3]
        lower_name = name.lower()
        is_high = any(term in lower_name for term in HIGH_IMPACT_TERMS)
        if is_high:
            high_impact_count += 1
        impact_note = historical_impact_note(name)
        prefix = "High-impact" if is_high else "Calendar"
        lines.append(f"- {prefix}: {event_time or 'time N/A'} ET - {name}. {impact_note}")

    if not lines:
        if market_closed:
            lines.append("- No actionable US cash-session events today because the market is closed.")
        else:
            lines.append("- No major US events found in FMP for today.")

    if market_closed:
        level = "Closed"
    elif high_impact_count >= 2:
        level = "Heavy"
    elif high_impact_count == 1:
        level = "Moderate"
    elif len(events) > 4 or user_events:
        level = "Light-to-moderate"
    else:
        level = "Light"
    return level, lines


def historical_impact_note(name: str) -> str:
    lower = name.lower()
    if "cpi" in lower or "pce" in lower or "ppi" in lower:
        return "Inflation prints can expand SPX range to 1.5x-2.0x normal; avoid short gamma into the release."
    if "fomc" in lower or "fed" in lower or "powell" in lower:
        return "Fed risk typically keeps IV sticky; sell premium only after the first reaction stabilizes."
    if "payroll" in lower or "nfp" in lower or "nonfarm" in lower:
        return "Payrolls often widen the opening range; wait for direction confirmation."
    if "retail" in lower or "pmi" in lower or "ism" in lower or "gdp" in lower:
        return "Growth data can move rates and index leadership; use wider strikes."
    if "jobless" in lower or "claims" in lower:
        return "Claims usually matter most when growth fears are active; monitor rates reaction."
    return "Normal scheduled data risk unless it surprises consensus."


def filter_earnings(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    candidates = [
        r
        for r in rows
        if isinstance(r, dict)
        and r.get("symbol")
        and "." not in str(r.get("symbol"))
        and len(str(r.get("symbol"))) <= 5
    ]
    if not candidates:
        return []

    symbols = [str(r["symbol"]).upper() for r in candidates[:80]]
    quote_rows, _ = quote_for(symbols, key)
    enriched: list[dict[str, Any]] = []
    for row in candidates:
        symbol = str(row["symbol"]).upper()
        quote = quote_rows.get(symbol, {})
        market_cap = as_float(quote.get("marketCap"))
        if symbol in MARKET_MOVERS or (market_cap is not None and market_cap >= 100_000_000_000):
            out = dict(row)
            out["marketCap"] = market_cap
            out["companyName"] = quote.get("name") or row.get("company") or row.get("symbol")
            enriched.append(out)

    enriched.sort(key=lambda item: as_float(item.get("marketCap")) or 0, reverse=True)
    return enriched[:10]


def market_is_closed(report_date: dt.date) -> bool:
    return report_date.weekday() >= 5 or report_date.isoformat() in NYSE_HOLIDAYS_2026


def support_resistance(
    current: float,
    prior: dict[str, Any],
    expected_move: float,
) -> tuple[list[tuple[str, float, str]], list[tuple[str, float, str]]]:
    prior_high = as_float(prior.get("high"))
    prior_low = as_float(prior.get("low"))
    prior_close = as_float(prior.get("close"))

    support_candidates: list[tuple[str, float, str]] = []
    resistance_candidates: list[tuple[str, float, str]] = []
    if prior_low is not None:
        support_candidates.append(("Support 1", prior_low, "Prior session low"))
    support_candidates.append(("Support 2", floor_to_increment(current - 1, 25), "Nearest downside round-number shelf"))
    if prior_close is not None and prior_close < current:
        support_candidates.append(("Support 3", prior_close, "Prior close / gap reference"))
    support_candidates.append(("Support 3", current - expected_move, "VIX-implied one-day downside"))

    if prior_high is not None:
        resistance_candidates.append(("Resistance 1", prior_high, "Prior session high"))
    resistance_candidates.append(("Resistance 2", ceil_to_increment(current + 1, 25), "Nearest upside round-number shelf"))
    if prior_close is not None and prior_close > current:
        resistance_candidates.append(("Resistance 3", prior_close, "Prior close / gap reference"))
    resistance_candidates.append(("Resistance 3", current + expected_move, "VIX-implied one-day upside"))

    supports = unique_levels(
        sorted((item for item in support_candidates if item[1] <= current + 10), key=lambda x: x[1], reverse=True),
        3,
        below=True,
        current=current,
    )
    resistances = unique_levels(
        sorted((item for item in resistance_candidates if item[1] >= current - 10), key=lambda x: x[1]),
        3,
        below=False,
        current=current,
    )
    return renumber("Support", supports), renumber("Resistance", resistances)


def unique_levels(
    candidates: list[tuple[str, float, str]],
    count: int,
    *,
    below: bool,
    current: float,
) -> list[tuple[str, float, str]]:
    out: list[tuple[str, float, str]] = []
    seen: set[int] = set()
    for _, value, rationale in candidates:
        rounded = round_to_increment(value, 5)
        if rounded in seen:
            continue
        seen.add(rounded)
        out.append(("", float(rounded), rationale))
        if len(out) == count:
            return out

    step = 25
    next_level = floor_to_increment(current - step, step) if below else ceil_to_increment(current + step, step)
    while len(out) < count:
        if next_level not in seen:
            seen.add(next_level)
            rationale = "Fallback round-number level"
            out.append(("", float(next_level), rationale))
        next_level = next_level - step if below else next_level + step
    return out


def renumber(prefix: str, rows: list[tuple[str, float, str]]) -> list[tuple[str, float, str]]:
    return [(f"{prefix} {idx}", value, rationale) for idx, (_, value, rationale) in enumerate(rows, 1)]


def build_report(args: argparse.Namespace) -> tuple[Path, str, str]:
    report_date = dt.date.fromisoformat(args.date) if args.date else et_today()
    parsed = parse_flexible_inputs(args.arguments)
    output_path = Path(args.output_dir) / f"Jane-Street-pre-market-edge-analyzer-{report_date.isoformat()}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    quotes, quote_err = quote_for(["^GSPC", "SPY", "^VIX"], args.fmp_key)
    spx_quote = quotes.get("^GSPC") or quotes.get("GSPC") or {}
    spy_quote = quotes.get("SPY") or {}
    vix_quote = quotes.get("^VIX") or quotes.get("VIX") or {}

    spx_history, spx_hist_err = historical_for("^GSPC", args.fmp_key, report_date)
    spy_history, spy_hist_err = historical_for("SPY", args.fmp_key, report_date)
    vix_history, vix_hist_err = historical_for("^VIX", args.fmp_key, report_date)

    prior_spx = first_historical_row(spx_history, report_date)
    prior_spy = first_historical_row(spy_history, report_date)
    prior_vix = first_historical_row(vix_history, report_date - dt.timedelta(days=1)) or first_historical_row(
        vix_history, report_date
    )

    if prior_spx is None and prior_spy is not None:
        ratio = (as_float(spx_quote.get("price")) or 10 * (as_float(spy_quote.get("price")) or 0)) / (
            as_float(spy_quote.get("price")) or 1
        )
        prior_spx = {
            "date": prior_spy.get("date"),
            "open": (as_float(prior_spy.get("open")) or 0) * ratio,
            "high": (as_float(prior_spy.get("high")) or 0) * ratio,
            "low": (as_float(prior_spy.get("low")) or 0) * ratio,
            "close": (as_float(prior_spy.get("close")) or 0) * ratio,
        }

    if prior_spx is None:
        raise RuntimeError("Could not obtain prior SPX/SPY historical prices from FMP.")

    events, econ_err = economic_calendar(args.fmp_key, report_date)
    earnings, earnings_err = earnings_calendar(args.fmp_key, report_date)
    major_earnings = filter_earnings(earnings, args.fmp_key)

    closed = market_is_closed(report_date)
    current_spx, current_source = current_spx_level(parsed, spx_quote, spy_quote)
    if current_spx is None:
        current_spx = as_float(prior_spx.get("close")) or 0
        current_source = "prior SPX close fallback"

    prior_close = as_float(prior_spx.get("close")) or current_spx
    gap_points = current_spx - prior_close
    gap_pct = (gap_points / prior_close * 100) if prior_close else 0.0
    gap_view, gap_reason = gap_assessment(gap_pct, closed, parsed.get("events") or "", events)

    current_vix = parsed.get("vix") if parsed.get("vix") is not None else as_float(vix_quote.get("price"))
    vix_source = "user input" if parsed.get("vix") is not None else "FMP quote"
    previous_vix_close = as_float(prior_vix.get("close") if prior_vix else None)
    if current_vix is None:
        current_vix = previous_vix_close or 18.0
        vix_source = "prior VIX fallback"
    vix_delta = current_vix - previous_vix_close if previous_vix_close is not None else None
    vix_delta_pct = (vix_delta / previous_vix_close * 100) if previous_vix_close else None

    expected_move = current_spx * (current_vix / 100) / math.sqrt(252)
    expected_pct = expected_move / current_spx * 100 if current_spx else None
    prior_range = (as_float(prior_spx.get("high")) or 0) - (as_float(prior_spx.get("low")) or 0)
    close_desc, close_lean = close_location(prior_spx)
    calendar_level, calendar_lines = classify_calendar(events, parsed.get("events") or "", closed)
    supports, resistances = support_resistance(current_spx, prior_spx, expected_move)
    trade_plan = make_trade_plan(current_spx, expected_move, closed, calendar_level, current_vix)

    iv_tone = iv_assessment(current_vix, previous_vix_close, vix_delta_pct, closed)
    opening_strategy = opening_gap_strategy(gap_pct, gap_view, closed, calendar_level)
    iv_crush = iv_crush_opportunity(calendar_level, current_vix, closed)

    data_notes = []
    for label, err in (
        ("quote", quote_err),
        ("SPX historical", spx_hist_err),
        ("SPY historical", spy_hist_err),
        ("VIX historical", vix_hist_err),
        ("economic calendar", econ_err),
        ("earnings calendar", earnings_err),
    ):
        if err:
            data_notes.append(f"- FMP {label}: {err}")
    if not data_notes:
        data_notes.append("- FMP calls completed for quotes, historical data, economic calendar, and earnings calendar.")

    support_line = "; ".join(f"{name} {fmt_price(value, 0)}" for name, value, _ in supports)
    resistance_line = "; ".join(f"{name} {fmt_price(value, 0)}" for name, value, _ in resistances)
    summary = (
        f"Gap {fmt_points(gap_points)} pts ({fmt_pct(gap_pct)}), view: {gap_view}. "
        f"VIX {fmt_price(current_vix)} ({vix_source}) vs prior close {fmt_price(previous_vix_close)} "
        f"({fmt_pct(vix_delta_pct)}). Event risk: {calendar_level}. "
        f"Strategy: {trade_plan['strategy']}. Supports: {support_line}. Resistances: {resistance_line}."
    )

    report = render_markdown(
        report_date=report_date,
        closed=closed,
        current_spx=current_spx,
        current_source=current_source,
        prior_spx=prior_spx,
        gap_points=gap_points,
        gap_pct=gap_pct,
        gap_view=gap_view,
        gap_reason=gap_reason,
        current_vix=current_vix,
        vix_source=vix_source,
        previous_vix_close=previous_vix_close,
        vix_delta=vix_delta,
        vix_delta_pct=vix_delta_pct,
        iv_tone=iv_tone,
        calendar_level=calendar_level,
        calendar_lines=calendar_lines,
        major_earnings=major_earnings,
        prior_range=prior_range,
        expected_move=expected_move,
        expected_pct=expected_pct,
        opening_strategy=opening_strategy,
        iv_crush=iv_crush,
        close_desc=close_desc,
        close_lean=close_lean,
        supports=supports,
        resistances=resistances,
        trade_plan=trade_plan,
        data_notes=data_notes,
        user_events=parsed.get("events") or "",
        summary=summary,
    )
    output_path.write_text(report, encoding="utf-8")
    return output_path, summary, report


def current_spx_level(
    parsed: dict[str, Any],
    spx_quote: dict[str, Any],
    spy_quote: dict[str, Any],
) -> tuple[float | None, str]:
    if parsed.get("futures") is not None:
        return float(parsed["futures"]), "user-supplied SPX/ES futures"

    for field in ("preMarket", "premarket", "preMarketPrice", "extendedPrice"):
        value = as_float(spx_quote.get(field))
        if value:
            return value, f"FMP ^GSPC {field}"

    spx_price = as_float(spx_quote.get("price"))
    if spx_price:
        return spx_price, "FMP ^GSPC quote"

    spy_price = as_float(spy_quote.get("price"))
    if spy_price:
        return spy_price * 10, "FMP SPY quote scaled by 10"
    return None, "unavailable"


def gap_assessment(
    gap_pct: float,
    closed: bool,
    user_events: str,
    events: list[dict[str, Any]],
) -> tuple[str, str]:
    if closed:
        return "No cash-session trade", "Market is closed; live ES Globex levels are needed for the next open."

    text = " ".join([user_events] + [str(e.get("event") or e.get("name") or "") for e in events]).lower()
    high_event = any(term in text for term in HIGH_IMPACT_TERMS)
    abs_gap = abs(gap_pct)
    if high_event:
        return "Uncertain", "High-impact data can turn a normal fade into a trend day."
    if abs_gap >= 0.75:
        return "Fade early unless breadth confirms", "Large overnight gaps often retrace after the opening auction."
    if abs_gap >= 0.25:
        return "Hold if first 15-minute range confirms", "Moderate gap can extend if opening breadth and rates confirm."
    return "Neutral/hold", "Small gap favors normal theta structure after the opening range forms."


def iv_assessment(
    current_vix: float,
    previous_vix_close: float | None,
    vix_delta_pct: float | None,
    closed: bool,
) -> str:
    if closed:
        return "VIX is a stale weekend/reference print; do not size live premium without Monday pre-market quotes."
    if previous_vix_close is None or vix_delta_pct is None:
        return "Use broker IV screen for the exact overnight change; current VIX is the working premium gauge."
    if vix_delta_pct >= 5:
        return "Options are pricing materially higher volatility than the prior close; sell premium only with wider wings."
    if vix_delta_pct <= -5:
        return "Options are cheaper than yesterday; premium selling edge is thinner unless realized range stays muted."
    if current_vix >= 25:
        return "VIX remains elevated; premium is available but gap risk demands defined-risk structures."
    if current_vix <= 14:
        return "Low VIX limits theta edge; avoid tight short strikes."
    return "VIX is near yesterday's close; normal defined-risk theta is acceptable after the open stabilizes."


def opening_gap_strategy(gap_pct: float, gap_view: str, closed: bool, calendar_level: str) -> str:
    if closed:
        return "Stay flat today; rebuild the plan with live ES/Globex high-low before Monday's opening auction."
    if calendar_level in {"Heavy", "Moderate"}:
        return "Wait until the event reaction and first 15-minute range settle before selling premium."
    if abs(gap_pct) >= 0.75:
        return "Fade bias after failed continuation; do not sell the challenged side until breadth confirms."
    if abs(gap_pct) >= 0.25:
        return f"Conditional {gap_view.lower()} approach; define risk outside the expected move."
    return "Normal theta setup after 9:35-9:50 AM ET; avoid entering during the opening print."


def iv_crush_opportunity(calendar_level: str, current_vix: float, closed: bool) -> str:
    if closed:
        return "No same-day IV crush trade because the cash market is closed."
    if calendar_level in {"Heavy", "Moderate"}:
        return "Possible post-event IV crush, but wait until the release/speaker risk is behind the tape."
    if current_vix >= 20:
        return "Yes - elevated index IV can support a small defined-risk iron condor after the opening range."
    if current_vix >= 15:
        return "Modest - premium is normal; focus on strikes outside the VIX expected move."
    return "Limited - low VIX reduces theta compensation; prefer patience or smaller size."


def make_trade_plan(
    current_spx: float,
    expected_move: float,
    closed: bool,
    calendar_level: str,
    current_vix: float,
) -> dict[str, str]:
    if closed:
        return {
            "strategy": "No trade - market closed",
            "details": "Do not open 0DTE theta on a weekend/market holiday. Re-run pre-market with live ES, VIX, and Globex range before the next cash open.",
            "strikes": "N/A today. Monday template: sell outside +/-1.25x the live VIX expected move, 10-point wings.",
            "expiration": "N/A today",
            "entry": "No entry today. Next valid window: 9:35-9:50 AM ET after the opening range forms.",
            "size": "0% today; resume at 1x normal only when live market data confirms liquidity.",
        }

    width = 10
    buffer = 1.25 if calendar_level in {"Light", "Light-to-moderate"} else 1.5
    short_put = round_to_increment(current_spx - expected_move * buffer, 5)
    long_put = short_put - width
    short_call = round_to_increment(current_spx + expected_move * buffer, 5)
    long_call = short_call + width
    size = "1x normal size" if current_vix < 25 and calendar_level == "Light" else "0.5x-0.75x normal size"
    return {
        "strategy": "0DTE SPX iron condor",
        "details": "Defined-risk short-premium structure using expected-move strikes as a proxy for 0.10-0.15 delta.",
        "strikes": f"Sell {short_put}P / buy {long_put}P; sell {short_call}C / buy {long_call}C.",
        "expiration": "Today (0DTE)",
        "entry": "9:35-9:50 AM ET after opening range and spreads stabilize.",
        "size": f"{size}; cap max loss at 2%-3% of account risk.",
    }


def render_markdown(**context: Any) -> str:
    report_date: dt.date = context["report_date"]
    prior_spx = context["prior_spx"]
    major_earnings = context["major_earnings"]
    supports = context["supports"]
    resistances = context["resistances"]
    trade_plan = context["trade_plan"]

    earnings_lines = []
    if major_earnings:
        for row in major_earnings:
            time_value = row.get("time") or "time N/A"
            earnings_lines.append(
                f"- {row.get('symbol')}: {row.get('companyName') or row.get('symbol')} "
                f"({fmt_mcap(row.get('marketCap'))}, {time_value}). "
                "Market-moving potential: Medium-to-high if index-heavy guidance surprises."
            )
    else:
        earnings_lines.append("- No large-cap or index-heavy earnings found in FMP for today.")

    support_rows = "\n".join(
        f"- {name}: {fmt_price(value, 0)} - {rationale}" for name, value, rationale in supports
    )
    resistance_rows = "\n".join(
        f"- {name}: {fmt_price(value, 0)} - {rationale}" for name, value, rationale in resistances
    )
    calendar_rows = "\n".join(context["calendar_lines"])
    data_rows = "\n".join(context["data_notes"])
    market_closed_line = (
        "The cash market is closed today, so this is a preparation briefing rather than an executable 0DTE setup. "
        if context["closed"]
        else ""
    )

    return f"""# Jane Street Pre-Market Edge - {report_date.isoformat()}

## Market assessment

{market_closed_line}Working SPX level is {fmt_price(context['current_spx'])} from {context['current_source']}. Gap versus the prior SPX close is {fmt_points(context['gap_points'])} points ({fmt_pct(context['gap_pct'])}). View: **{context['gap_view']}** - {context['gap_reason']}

VIX is {fmt_price(context['current_vix'])} from {context['vix_source']} versus prior close {fmt_price(context['previous_vix_close'])} ({fmt_pct(context['vix_delta_pct'])}). {context['iv_tone']}

Prior session closed {context['close_desc']} of its range, giving a **{context['close_lean']}** read. Calendar risk is **{context['calendar_level']}** and earnings exposure is summarized below.

## Overnight futures movement

- Current SPX/ES reference: {fmt_price(context['current_spx'])} ({context['current_source']}).
- Prior SPX close: {fmt_price(as_float(prior_spx.get('close')))} on {prior_spx.get('date')}.
- Gap: {fmt_points(context['gap_points'])} points ({fmt_pct(context['gap_pct'])}).
- Hold/fade view: **{context['gap_view']}** - {context['gap_reason']}

## Pre-market IV levels

- VIX: {fmt_price(context['current_vix'])} ({context['vix_source']}).
- Prior VIX close: {fmt_price(context['previous_vix_close'])}.
- Change vs prior close: {fmt_points(context['vix_delta'])} points ({fmt_pct(context['vix_delta_pct'])}).
- Implication: {context['iv_tone']}

## Economic calendar impact

- Calendar weight: **{context['calendar_level']}**.
{calendar_rows}
- Recommendation: {"Do not trade today; market is closed." if context["closed"] else "Use wider strikes or wait until event risk clears if any high-impact event is present."}

## Earnings exposure

{chr(10).join(earnings_lines)}

## Globex range and expected range

- Globex range: From broker/futures platform. FMP does not provide ES overnight high/low in this command.
- Proxy range: prior SPX session high-low was {fmt_price(context['prior_range'])} points.
- VIX-implied one-day expected range: +/-{fmt_price(context['expected_move'])} points (~+/-{fmt_price(context['expected_pct'])}%).

## Opening gap strategy

{context['opening_strategy']}

## IV crush opportunity

{context['iv_crush']}

## Previous day's close analysis

- Open: {fmt_price(as_float(prior_spx.get('open')))}
- High: {fmt_price(as_float(prior_spx.get('high')))}
- Low: {fmt_price(as_float(prior_spx.get('low')))}
- Close: {fmt_price(as_float(prior_spx.get('close')))}
- Read: Market closed {context['close_desc']} of the range. {context['close_lean']}.

## Support and resistance

### Support
{support_rows}

### Resistance
{resistance_rows}

## Pre-market trade plan

- Strategy: **{trade_plan['strategy']}**
- Construction: {trade_plan['details']}
- Strikes: {trade_plan['strikes']}
- Expiration: {trade_plan['expiration']}
- Entry time: {trade_plan['entry']}
- Position size: {trade_plan['size']}

## Scenario playbook

- Bull outcome: Above {fmt_price(resistances[0][1], 0)}. If in a live 0DTE condor, take off or roll challenged call risk; keep put side only if momentum breadth remains constructive.
- Bear outcome: Below {fmt_price(supports[0][1], 0)}. If in a live 0DTE condor, close/roll the put side before short strike breach; call side can be harvested at 50%-75% profit.
- Neutral outcome: Holds between {fmt_price(supports[0][1], 0)} and {fmt_price(resistances[0][1], 0)}. Hold defined-risk premium to 50% max profit, then close; avoid pin-risk hero trades late day.

## Data and disclaimer

Data sources: FMP quote (^GSPC, SPY, ^VIX), FMP historical-price-full (^GSPC, SPY, ^VIX), FMP economic_calendar, FMP earning_calendar. Globex high/low requires a broker or futures platform unless supplied by the user.

Data notes:
{data_rows}

Disclaimer: Educational/research use only. This is not investment advice, a recommendation, or an order instruction. Options involve risk and can result in loss of capital.
"""


def split_for_telegram(text: str, limit: int = TELEGRAM_LIMIT) -> list[str]:
    chunks: list[str] = []
    remaining = text
    while len(remaining) > limit:
        cut = remaining.rfind("\n\n", 0, limit)
        if cut < limit // 2:
            cut = remaining.rfind("\n", 0, limit)
        if cut < limit // 2:
            cut = limit
        chunks.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()
    if remaining:
        chunks.append(remaining)
    return chunks


def telegram_send(token: str, chat_id: str, text: str) -> None:
    payload = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode("utf-8")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    request = urllib.request.Request(url, data=payload, method="POST")
    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.loads(response.read().decode("utf-8"))
    if not data.get("ok"):
        raise RuntimeError(f"Telegram sendMessage failed: {data}")


def send_to_telegram(token: str | None, chat_id: str | None, summary: str, report: str) -> None:
    if not token:
        raise RuntimeError("Telegram token missing. Set TELEGRAM_BOT_TOKEN or pass --telegram-token.")
    if not chat_id:
        raise RuntimeError("Telegram chat ID missing. Set TELEGRAM_CHAT_ID or pass --telegram-chat-id.")

    telegram_send(token, chat_id, f"Jane Street Pre-Market Edge\n\n{summary}")
    chunks = split_for_telegram(report)
    for index, chunk in enumerate(chunks, 1):
        header = f"Report part {index}/{len(chunks)}\n\n" if len(chunks) > 1 else ""
        telegram_send(token, chat_id, header + chunk)


def main() -> int:
    args = parse_args()
    try:
        output_path, summary, report = build_report(args)
        print(f"Wrote {output_path}")
        print(textwrap.fill(summary, width=100))
        if args.send_telegram:
            send_to_telegram(args.telegram_token, args.telegram_chat_id, summary, report)
            print("Telegram delivery complete")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
