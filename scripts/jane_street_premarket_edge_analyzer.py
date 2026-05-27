#!/usr/bin/env python3
"""Generate the Jane Street pre-market edge report and optionally send it to Telegram."""

from __future__ import annotations

import argparse
import math
import os
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS = WORKSPACE / "outputs"
FMP_BASE = "https://financialmodelingprep.com/api/v3"
DEFAULT_FMP_KEY = "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz"
HIGH_IMPACT_KEYWORDS = (
    "cpi",
    "consumer price",
    "fomc",
    "fed",
    "powell",
    "nonfarm",
    "nfp",
    "pmi",
    "ism",
    "retail sales",
    "jobless",
    "claims",
    "ppi",
    "gdp",
    "personal consumption",
    "pce",
)
MEGA_CAP_TICKERS = {
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
    "LLY",
    "V",
    "MA",
    "XOM",
    "COST",
    "WMT",
    "HD",
    "NFLX",
    "AMD",
}


def parse_args() -> argparse.Namespace:
    """Parse CLI flags for optional user-supplied market inputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spx-futures", type=float, help="Current SPX/ES pre-market level")
    parser.add_argument("--vix", type=float, help="Current VIX level")
    parser.add_argument("--events", default="", help="User-supplied news/economic event text")
    parser.add_argument("--date", help="Report date in YYYY-MM-DD; defaults to today in New York")
    parser.add_argument("--output", help="Output markdown path")
    parser.add_argument("--send-telegram", action="store_true", help="Send summary and report file to Telegram")
    parser.add_argument("--telegram-chat-id", help="Telegram chat/channel ID; defaults to TELEGRAM_CHAT_ID")
    return parser.parse_args()


def fmp_get(path: str, params: dict[str, Any] | None = None) -> Any:
    """Fetch JSON from FMP."""
    api_key = os.environ.get("FMP_API_KEY", DEFAULT_FMP_KEY)
    merged = dict(params or {})
    merged["apikey"] = api_key
    response = requests.get(f"{FMP_BASE}{path}", params=merged, timeout=20)
    response.raise_for_status()
    return response.json()


def previous_weekday(day: date) -> date:
    """Return the previous weekday. FMP history lookup handles market holidays separately."""
    current = day - timedelta(days=1)
    while current.weekday() >= 5:
        current -= timedelta(days=1)
    return current


def parse_report_date(value: str | None) -> date:
    """Parse report date or use current New York date."""
    if value:
        return datetime.strptime(value, "%Y-%m-%d").date()
    return datetime.now(ZoneInfo("America/New_York")).date()


def quote_map(quotes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Map FMP quote rows by symbol."""
    return {row.get("symbol", ""): row for row in quotes if row.get("symbol")}


def get_number(row: dict[str, Any] | None, *keys: str) -> float | None:
    """Return the first numeric value for a set of possible keys."""
    if not row:
        return None
    for key in keys:
        value = row.get(key)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                continue
    return None


def get_history(symbol: str, report_date: date, lookback_days: int = 35) -> list[dict[str, Any]]:
    """Fetch historical prices for a symbol."""
    start = report_date - timedelta(days=lookback_days)
    data = fmp_get(
        f"/historical-price-full/{symbol}",
        {"from": start.isoformat(), "to": report_date.isoformat()},
    )
    history = data.get("historical", []) if isinstance(data, dict) else []
    return sorted(history, key=lambda row: row.get("date", ""), reverse=True)


def prior_session(history: list[dict[str, Any]], report_date: date) -> dict[str, Any] | None:
    """Return the latest completed session before the report date."""
    for row in history:
        row_date = row.get("date")
        if not row_date:
            continue
        try:
            if datetime.strptime(row_date[:10], "%Y-%m-%d").date() < report_date:
                return row
        except ValueError:
            continue
    return history[0] if history else None


def fetch_economic_calendar(report_date: date) -> list[dict[str, Any]]:
    """Fetch FMP economic calendar rows for the report date."""
    data = fmp_get(
        "/economic_calendar",
        {"from": report_date.isoformat(), "to": report_date.isoformat()},
    )
    return data if isinstance(data, list) else []


def event_name(event: dict[str, Any]) -> str:
    """Get a usable economic event name."""
    return str(event.get("event") or event.get("name") or event.get("title") or "Economic event")


def event_time(event: dict[str, Any]) -> str:
    """Get a display time from an economic event row."""
    value = str(event.get("date") or event.get("time") or "")
    if " " in value:
        return value.split(" ", 1)[1][:5] + " ET"
    return value[:5] if value else "Time N/A"


def is_high_impact_event(event: dict[str, Any]) -> bool:
    """Identify high-impact macro events by name and importance fields."""
    text = " ".join(str(event.get(key, "")) for key in ("event", "name", "title", "importance", "impact")).lower()
    return any(keyword in text for keyword in HIGH_IMPACT_KEYWORDS) or "high" in text


def fetch_major_earnings(report_date: date) -> list[dict[str, Any]]:
    """Fetch earnings calendar and retain large-cap/index-relevant reporters."""
    data = fmp_get(
        "/earning_calendar",
        {"from": report_date.isoformat(), "to": report_date.isoformat()},
    )
    rows = data if isinstance(data, list) else []
    symbols = [
        str(row.get("symbol", "")).upper()
        for row in rows
        if re.fullmatch(r"[A-Z]{1,5}", str(row.get("symbol", "")).upper())
    ]
    quotes: dict[str, dict[str, Any]] = {}
    for start in range(0, len(symbols), 50):
        chunk = symbols[start : start + 50]
        if not chunk:
            continue
        try:
            quotes.update(quote_map(fmp_get(f"/quote/{','.join(chunk)}")))
        except requests.RequestException:
            continue

    major: list[dict[str, Any]] = []
    for row in rows:
        symbol = str(row.get("symbol", "")).upper()
        quote = quotes.get(symbol, {})
        market_cap = get_number(quote, "marketCap") or 0
        if symbol in MEGA_CAP_TICKERS or market_cap >= 50_000_000_000:
            enriched = dict(row)
            enriched["marketCap"] = market_cap
            enriched["name"] = quote.get("name") or row.get("company") or symbol
            major.append(enriched)

    major.sort(key=lambda row: row.get("marketCap", 0), reverse=True)
    return major[:10]


def market_cap_label(value: float | int | None) -> str:
    """Format market cap for display."""
    if not value:
        return "N/A"
    value = float(value)
    if value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    return f"${value / 1_000_000:.0f}M"


def round_to(value: float, increment: int, direction: str = "nearest") -> float:
    """Round a price level to the requested increment."""
    if direction == "down":
        return math.floor(value / increment) * increment
    if direction == "up":
        return math.ceil(value / increment) * increment
    return round(value / increment) * increment


def unique_levels(candidates: list[tuple[float, str]], current: float, side: str) -> list[tuple[float, str]]:
    """Return the three nearest unique support or resistance levels."""
    seen: set[float] = set()
    filtered: list[tuple[float, str]] = []
    for level, reason in candidates:
        rounded = round(float(level), 2)
        bucket = round(rounded / 5) * 5
        if bucket in seen:
            continue
        if side == "support" and rounded > current:
            continue
        if side == "resistance" and rounded < current:
            continue
        seen.add(bucket)
        filtered.append((rounded, reason))

    if side == "support":
        filtered.sort(key=lambda item: current - item[0])
    else:
        filtered.sort(key=lambda item: item[0] - current)
    return filtered[:3]


def calendar_weight(events: list[dict[str, Any]], user_events: str) -> str:
    """Classify the macro calendar load."""
    high_count = sum(1 for event in events if is_high_impact_event(event))
    user_high = any(keyword in user_events.lower() for keyword in HIGH_IMPACT_KEYWORDS)
    if high_count or user_high:
        return "Heavy"
    if len(events) >= 4 or user_events:
        return "Moderate"
    return "Light"


def close_location(prior: dict[str, Any]) -> tuple[str, str]:
    """Describe where the prior close landed inside the day range."""
    high = get_number(prior, "high") or 0
    low = get_number(prior, "low") or 0
    close = get_number(prior, "close") or 0
    if high <= low:
        return "in the middle", "Neutral"
    location = (close - low) / (high - low)
    if location >= 0.75:
        return "near the highs", "Bearish mean-reversion"
    if location <= 0.25:
        return "near the lows", "Bullish bounce"
    return "in the middle", "Neutral"


def impact_note(event: dict[str, Any]) -> str:
    """Return a concise historical impact note for known event types."""
    name = event_name(event).lower()
    if "cpi" in name or "consumer price" in name:
        return "CPI can expand SPX range 1.5-2.0x normal."
    if "fomc" in name or "fed" in name or "powell" in name:
        return "Fed events often reprice IV and can create trend days."
    if "nonfarm" in name or "nfp" in name or "jobless" in name or "claims" in name:
        return "Labor data can drive early range expansion."
    if "pmi" in name or "ism" in name:
        return "Growth data can rotate sectors and widen intraday ranges."
    if "retail" in name or "pce" in name or "ppi" in name or "gdp" in name:
        return "Macro surprise risk argues for wider strikes."
    return "Low-to-moderate index range impact unless surprise is large."


def build_report(args: argparse.Namespace) -> tuple[Path, str, str]:
    """Fetch data, build the markdown report, and return path/content/summary."""
    report_date = parse_report_date(args.date)
    output_path = Path(args.output) if args.output else OUTPUTS / f"Jane-Street-pre-market-edge-analyzer-{report_date}.md"
    OUTPUTS.mkdir(parents=True, exist_ok=True)

    quotes = quote_map(fmp_get("/quote/^GSPC,SPY,^VIX"))
    spx_quote = quotes.get("^GSPC", {})
    spy_quote = quotes.get("SPY", {})
    vix_quote = quotes.get("^VIX", {})

    spx_history = get_history("^GSPC", report_date)
    spy_history = get_history("SPY", report_date)
    vix_history = get_history("^VIX", report_date)
    prior_spx = prior_session(spx_history, report_date)
    prior_spy = prior_session(spy_history, report_date)
    prior_vix = prior_session(vix_history, report_date)

    if not prior_spx and prior_spy:
        factor = (get_number(spx_quote, "price") or 10 * (get_number(spy_quote, "price") or 0)) / max(
            get_number(spy_quote, "price") or 1,
            1,
        )
        prior_spx = {
            "date": prior_spy.get("date"),
            "open": (get_number(prior_spy, "open") or 0) * factor,
            "high": (get_number(prior_spy, "high") or 0) * factor,
            "low": (get_number(prior_spy, "low") or 0) * factor,
            "close": (get_number(prior_spy, "close") or 0) * factor,
        }

    prior_spx = prior_spx or {}
    prior_date = prior_spx.get("date") or previous_weekday(report_date).isoformat()
    prior_close = get_number(prior_spx, "close") or get_number(spx_quote, "previousClose") or 0
    prior_high = get_number(prior_spx, "high") or get_number(spx_quote, "dayHigh") or prior_close
    prior_low = get_number(prior_spx, "low") or get_number(spx_quote, "dayLow") or prior_close
    prior_open = get_number(prior_spx, "open") or prior_close
    prior_range = max(prior_high - prior_low, 0)

    current_spx = args.spx_futures or get_number(spx_quote, "preMarket", "price") or prior_close
    vix = args.vix or get_number(vix_quote, "price") or 0
    prior_vix_close = get_number(prior_vix, "close") if prior_vix else get_number(vix_quote, "previousClose")
    vix_5_day = None
    vix_closes = [get_number(row, "close") for row in vix_history if get_number(row, "close")]
    if vix_closes:
        vix_5_day = sum(vix_closes[:5]) / min(len(vix_closes), 5)

    economic_events = fetch_economic_calendar(report_date)
    major_earnings = fetch_major_earnings(report_date)
    calendar_load = calendar_weight(economic_events, args.events)

    gap_points = current_spx - prior_close
    gap_pct = (gap_points / prior_close * 100) if prior_close else 0
    high_impact = calendar_load == "Heavy"
    if abs(gap_pct) >= 0.5 and high_impact:
        gap_view = "Uncertain"
        gap_reason = "large gap plus event risk can extend or reverse quickly"
    elif abs(gap_pct) >= 0.5:
        gap_view = "Fade"
        gap_reason = "large overnight gaps often mean-revert in the first hour"
    elif abs(gap_pct) <= 0.2:
        gap_view = "Hold/extend"
        gap_reason = "small gap leaves room for normal opening range discovery"
    else:
        gap_view = "Uncertain"
        gap_reason = "moderate gap needs the first 15-minute range for confirmation"

    expected_move = current_spx * (vix / 100) / math.sqrt(252) if vix else prior_range
    expected_pct = (expected_move / current_spx * 100) if current_spx else 0
    close_area, close_lean = close_location({"high": prior_high, "low": prior_low, "close": prior_close})

    strike_multiplier = 1.35 if calendar_load == "Heavy" else 1.15 if calendar_load == "Moderate" else 1.0
    short_put = round_to(current_spx - expected_move * strike_multiplier, 5, "down")
    long_put = short_put - 10
    short_call = round_to(current_spx + expected_move * strike_multiplier, 5, "up")
    long_call = short_call + 10

    support_candidates = [
        (prior_close, "Prior session close"),
        (prior_low, "Prior session low"),
        (round_to(current_spx - expected_move / 2, 25, "down"), "Half expected move down"),
        (round_to(current_spx - expected_move, 25, "down"), "Full expected move down"),
        (round_to(current_spx, 25, "down"), "Nearest round-number shelf"),
    ]
    resistance_candidates = [
        (prior_close, "Prior session close"),
        (prior_high, "Prior session high"),
        (round_to(current_spx + expected_move / 2, 25, "up"), "Half expected move up"),
        (round_to(current_spx + expected_move, 25, "up"), "Full expected move up"),
        (round_to(current_spx, 25, "up"), "Nearest round-number ceiling"),
    ]
    supports = unique_levels(support_candidates, current_spx, "support")
    resistances = unique_levels(resistance_candidates, current_spx, "resistance")

    while len(supports) < 3:
        next_level = round_to(current_spx - expected_move * (len(supports) + 1), 25, "down")
        supports.append((next_level, "Volatility-derived backup support"))
    while len(resistances) < 3:
        next_level = round_to(current_spx + expected_move * (len(resistances) + 1), 25, "up")
        resistances.append((next_level, "Volatility-derived backup resistance"))

    if prior_vix_close:
        vix_delta = vix - prior_vix_close
        vix_phrase = "higher" if vix_delta > 0.25 else "lower" if vix_delta < -0.25 else "flat"
        vix_compare = f"{vix:.2f} vs {prior_vix_close:.2f} yesterday ({vix_delta:+.2f}); IV is {vix_phrase}."
    elif vix_5_day:
        vix_delta = vix - vix_5_day
        vix_phrase = "above" if vix_delta > 0.25 else "below" if vix_delta < -0.25 else "near"
        vix_compare = f"{vix:.2f} vs {vix_5_day:.2f} 5-day average ({vix_delta:+.2f}); IV is {vix_phrase} recent average."
    else:
        vix_compare = f"{vix:.2f}; compare with broker prior close for exact IV change."

    ordered_events = sorted(
        economic_events,
        key=lambda event: (
            not is_high_impact_event(event),
            str(event.get("country") or event.get("region") or "") != "US",
            str(event.get("date") or event.get("time") or ""),
        ),
    )
    event_lines = []
    for event in ordered_events[:12]:
        country = event.get("country") or event.get("region") or "Global"
        marker = "HIGH" if is_high_impact_event(event) else "Normal"
        event_lines.append(f"- {event_time(event)} - {country} - {event_name(event)} ({marker}): {impact_note(event)}")
    if args.events:
        event_lines.insert(0, f"- User note - {args.events}")
    if not event_lines:
        event_lines.append("- No major FMP economic calendar items returned for today.")
    main_event = event_lines[0].replace("- ", "", 1)

    earnings_lines = []
    for row in major_earnings:
        symbol = row.get("symbol", "N/A")
        timing = row.get("time") or "Time N/A"
        market_cap = market_cap_label(row.get("marketCap"))
        potential = "High" if row.get("marketCap", 0) >= 500_000_000_000 or symbol in MEGA_CAP_TICKERS else "Medium"
        earnings_lines.append(f"- {symbol} ({row.get('name', symbol)}), {timing}, {market_cap}: {potential} market-moving potential.")
    if not earnings_lines:
        earnings_lines.append("- No large-cap/index-heavy reporters surfaced from the FMP calendar.")

    strategy_name = "0DTE SPX iron condor"
    if calendar_load == "Heavy":
        entry_time = "After the high-impact event and after the first 15-minute opening range confirms"
        size = "0.5x normal size; cap defined risk at 1-2% of account."
        calendar_recommendation = "Trade after the event with wider strikes; avoid selling premium before the release."
    elif calendar_load == "Moderate":
        entry_time = "9:40-10:00 AM ET after the open settles"
        size = "0.75-1.0x normal size; cap defined risk at 2% of account."
        calendar_recommendation = "Use wider-than-normal strikes and wait for the opening range."
    else:
        entry_time = "9:35-9:50 AM ET after the opening print stabilizes"
        size = "1x normal size; cap defined risk at 2-3% of account."
        calendar_recommendation = "Normal theta setup is acceptable after the first few minutes."

    gap_strategy = "Stay flat until the opening range breaks" if gap_view == "Uncertain" else "Fade the gap tactically" if gap_view == "Fade" else "Use normal theta and let the gap prove itself"
    iv_crush = (
        "Yes - elevated/event-driven IV argues for defined-risk premium selling after the event."
        if calendar_load == "Heavy" or vix >= 20
        else "Limited - IV is not high enough to rely on crush alone; edge comes from time decay and strike discipline."
    )

    title = f"Jane Street Pre-Market Edge - {report_date}"
    content = f"""# {title}

## Market assessment

SPX/ES pre-market reference is {current_spx:,.2f}. Prior SPX close was {prior_close:,.2f} on {prior_date}, so the inferred gap is {gap_points:+.1f} points ({gap_pct:+.2f}%). View: **{gap_view}** - {gap_reason}.

Pre-market IV check: VIX is {vix_compare} This sets up {'selective premium selling with wider strikes' if calendar_load != 'Light' else 'a normal defined-risk theta day'}.

Yesterday closed {close_area} of its range ({prior_low:,.2f}-{prior_high:,.2f}), giving a **{close_lean}** lean. Calendar load is **{calendar_load}**; earnings exposure is {'material' if len(major_earnings) >= 3 else 'limited'} from the large-cap names surfaced below.

## Overnight futures movement

- Current reference: {current_spx:,.2f} ({'user-supplied SPX/ES futures' if args.spx_futures else 'FMP ^GSPC quote proxy; use broker ES for exact futures'}).
- Prior close: {prior_close:,.2f}.
- Gap: {gap_points:+.1f} points ({gap_pct:+.2f}%).
- Hold/fade view: **{gap_view}** - {gap_reason}.

## Pre-market IV levels

- VIX: {vix_compare}
- Premium-selling read: {'Wider strikes and lower size are appropriate.' if calendar_load != 'Light' else 'Defined-risk 0DTE premium is reasonable if open liquidity is orderly.'}

## Economic calendar impact

Today's calendar: **{calendar_load}**.

{chr(10).join(event_lines)}

Recommendation: {calendar_recommendation}

## Earnings exposure

{chr(10).join(earnings_lines)}

Index read: single-name IV is elevated around reporters; index impact is {'material if mega-cap guidance surprises' if major_earnings else 'limited based on FMP calendar'}.

## Globex range and expected range

- Globex high/low: From broker/futures platform; FMP equity data does not provide true ES overnight range.
- Prior day proxy range: {prior_range:.1f} SPX points ({prior_low:,.2f}-{prior_high:,.2f}).
- VIX-based 1-day expected move: +/-{expected_move:.1f} points (~+/-{expected_pct:.2f}%).

## Opening gap strategy

- Strategy: **{gap_strategy}**.
- Execution note: wait for the first 5-15 minutes unless price immediately rejects/accepts the gap with volume.

## IV crush opportunity

- {iv_crush}
- Preferred expression: defined-risk spread/condor rather than naked short premium.

## Previous day's close analysis

- Prior session open/high/low/close: {prior_open:,.2f} / {prior_high:,.2f} / {prior_low:,.2f} / {prior_close:,.2f}.
- Close read: market closed {close_area}; lean is **{close_lean}** for the next session unless the open accepts above/below yesterday's range.

## Support and resistance

### Support

1. {supports[0][0]:,.2f} - {supports[0][1]}.
2. {supports[1][0]:,.2f} - {supports[1][1]}.
3. {supports[2][0]:,.2f} - {supports[2][1]}.

### Resistance

1. {resistances[0][0]:,.2f} - {resistances[0][1]}.
2. {resistances[1][0]:,.2f} - {resistances[1][1]}.
3. {resistances[2][0]:,.2f} - {resistances[2][1]}.

## Pre-market trade plan

- Strategy: **{strategy_name}**.
- Expiration: Today (0DTE SPX).
- Strikes: sell {short_put:,.0f} put / buy {long_put:,.0f} put; sell {short_call:,.0f} call / buy {long_call:,.0f} call.
- Entry time: {entry_time}.
- Position size: {size}
- Profit target: close at 50% of max profit, or earlier if one side compresses quickly after the open.
- Stop/risk: exit if short strike is tested with momentum or premium reaches roughly 2x initial credit.

## Scenario playbook

- Bull outcome: SPX accepts above {resistances[0][0]:,.2f}. Close/roll the call side if momentum is strong; keep the put side only if delta collapses and premium is mostly harvested.
- Bear outcome: SPX loses {supports[0][0]:,.2f}. Close/roll the put side; harvest the call side at 50-70% profit.
- Neutral outcome: SPX stays between {supports[0][0]:,.2f} and {resistances[0][0]:,.2f}. Hold the condor toward 50% max profit and avoid unnecessary adjustments.

## Data and disclaimer

- Data sources: FMP quote (^GSPC, SPY, ^VIX), FMP historical prices (^GSPC, SPY, ^VIX), FMP economic calendar, FMP earnings calendar.
- Globex/overnight range: use broker/futures platform for exact ES high/low; this report uses FMP equity/index proxies when futures are not supplied.
- Disclaimer: for educational and research purposes only; not investment advice.
"""

    output_path.write_text(content, encoding="utf-8")
    summary = (
        f"Jane Street Pre-Market Edge {report_date}\n"
        f"Gap: {gap_points:+.1f} pts ({gap_pct:+.2f}%) - {gap_view}\n"
        f"VIX: {vix_compare}\n"
        f"Main event risk: {calendar_load} calendar; {main_event}\n"
        f"Plan: {strategy_name} {short_put:,.0f}/{long_put:,.0f}P and {short_call:,.0f}/{long_call:,.0f}C, entry {entry_time}.\n"
        f"Support: {supports[0][0]:,.0f}, {supports[1][0]:,.0f}, {supports[2][0]:,.0f}. "
        f"Resistance: {resistances[0][0]:,.0f}, {resistances[1][0]:,.0f}, {resistances[2][0]:,.0f}."
    )
    return output_path, content, summary


def send_to_telegram(report_path: Path, summary: str, chat_id: str | None = None) -> None:
    """Send report summary and markdown file to Telegram."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
    resolved_chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN or TELEGRAM_TOKEN is required")
    if not resolved_chat_id:
        raise RuntimeError("TELEGRAM_CHAT_ID or --telegram-chat-id is required")

    base = f"https://api.telegram.org/bot{token}"
    message = requests.post(
        f"{base}/sendMessage",
        data={"chat_id": resolved_chat_id, "text": summary[:4000], "disable_web_page_preview": True},
        timeout=20,
    )
    message.raise_for_status()

    with report_path.open("rb") as handle:
        document = requests.post(
            f"{base}/sendDocument",
            data={"chat_id": resolved_chat_id, "caption": "Full pre-market edge report"},
            files={"document": (report_path.name, handle, "text/markdown")},
            timeout=30,
        )
    document.raise_for_status()


def main() -> None:
    """Generate and optionally deliver the report."""
    args = parse_args()
    report_path, _content, summary = build_report(args)
    print(f"Wrote {report_path}")
    print(summary)
    if args.send_telegram:
        send_to_telegram(report_path, summary, args.telegram_chat_id)
        print("Sent report to Telegram")


if __name__ == "__main__":
    main()
