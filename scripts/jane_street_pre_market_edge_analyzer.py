#!/usr/bin/env python3
"""
Jane Street Pre-Market Edge Analyzer.

Builds the daily pre-market theta briefing from FMP data, writes the markdown
report to outputs/, and can optionally send the report to Telegram.
"""

from __future__ import annotations

import argparse
import math
import os
import re
import textwrap
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUT_DIR = WORKSPACE / "outputs"
FMP_BASE = "https://financialmodelingprep.com/api/v3"
FMP_KEY = os.environ.get("FMP_API_KEY", "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz")
DEFAULT_TELEGRAM_CHAT_ID = "7830722515"

HIGH_IMPACT_KEYWORDS = (
    "cpi",
    "pce",
    "fomc",
    "powell",
    "federal reserve",
    "interest rate",
    "rate decision",
    "nonfarm",
    "payroll",
    "nfp",
    "pmi",
    "ism",
    "retail sales",
    "jobless",
    "claims",
    "gdp",
    "ppi",
)

INDEX_HEAVY_TICKERS = {
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "GOOGL",
    "GOOG",
    "META",
    "AVGO",
    "TSLA",
    "JPM",
    "LLY",
    "V",
    "MA",
    "COST",
    "UNH",
    "XOM",
    "NFLX",
    "HD",
    "PG",
    "JNJ",
    "BAC",
    "WMT",
}


@dataclass
class ParsedArgs:
    spx_futures: float | None
    vix: float | None
    events_text: str


def fmp_get(path: str, params: dict[str, Any] | None = None) -> Any:
    """Fetch JSON from the FMP v3 API."""
    request_params = dict(params or {})
    request_params["apikey"] = FMP_KEY
    response = requests.get(f"{FMP_BASE}{path}", params=request_params, timeout=20)
    response.raise_for_status()
    return response.json()


def parse_command_args(raw_args: str) -> ParsedArgs:
    """Extract optional SPX/ES futures price, VIX level, and free-text events."""
    if not raw_args:
        return ParsedArgs(None, None, "")

    spx_futures: float | None = None
    vix: float | None = None
    consumed_spans: list[tuple[int, int]] = []

    for match in re.finditer(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])", raw_args):
        value = float(match.group(1))
        lower_context = raw_args[max(0, match.start() - 12) : match.end() + 12].lower()
        if "vix" in lower_context and vix is None:
            vix = value
            consumed_spans.append(match.span())
        elif value >= 1000 and spx_futures is None:
            spx_futures = value
            consumed_spans.append(match.span())
        elif 8 <= value <= 80 and vix is None:
            vix = value
            consumed_spans.append(match.span())

    events_chars = list(raw_args)
    for start, end in consumed_spans:
        for idx in range(start, end):
            events_chars[idx] = " "
    events_text = re.sub(r"\s+", " ", "".join(events_chars)).strip(" ,")
    return ParsedArgs(spx_futures, vix, events_text)


def latest_quote(quotes: list[dict[str, Any]], symbol: str) -> dict[str, Any]:
    """Return a quote row by symbol, or an empty dict if missing."""
    for row in quotes:
        if row.get("symbol") == symbol:
            return row
    return {}


def historical_rows(symbol: str, start: date, end: date) -> list[dict[str, Any]]:
    """Fetch historical rows sorted newest first."""
    data = fmp_get(
        f"/historical-price-full/{symbol}",
        {"from": start.isoformat(), "to": end.isoformat()},
    )
    rows = data.get("historical", []) if isinstance(data, dict) else []
    return sorted(rows, key=lambda row: row.get("date", ""), reverse=True)


def prior_session(rows: list[dict[str, Any]], report_date: date) -> dict[str, Any]:
    """Pick the most recent completed trading session before report_date."""
    for row in rows:
        row_date = row.get("date", "")
        if row_date and row_date < report_date.isoformat():
            return row
    return rows[0] if rows else {}


def price_from_quote(row: dict[str, Any]) -> float | None:
    """Get the best available current/pre-market price field from an FMP quote."""
    for key in ("preMarket", "preMarketPrice", "price"):
        value = row.get(key)
        if isinstance(value, (int, float)) and value > 0:
            return float(value)
    return None


def fmt_price(value: float | None, decimals: int = 2) -> str:
    """Format a price or numeric value for the report."""
    if value is None:
        return "n/a"
    return f"{value:,.{decimals}f}"


def fmt_pct(value: float | None, decimals: int = 2) -> str:
    """Format a percent value."""
    if value is None:
        return "n/a"
    return f"{value:+.{decimals}f}%"


def round_to_increment(value: float, increment: int = 5) -> int:
    """Round a price to the nearest strike increment."""
    return int(round(value / increment) * increment)


def nearest_round_level(value: float, direction: str) -> int:
    """Return a nearby round SPX level."""
    if direction == "up":
        return int(math.ceil(value / 50) * 50)
    return int(math.floor(value / 50) * 50)


def is_high_impact_event(name: str) -> bool:
    """Identify macro events that should alter index option risk-taking."""
    lower = name.lower()
    regional_fed_markers = (
        "dallas fed",
        "richmond fed",
        "kansas city fed",
        "chicago fed",
        "philadelphia fed",
        "empire state",
    )
    if any(marker in lower for marker in regional_fed_markers):
        return False
    if "fed" in lower:
        return any(marker in lower for marker in ("fomc", "powell", "federal reserve", "fed chair", "fed speaker"))
    return any(keyword in lower for keyword in HIGH_IMPACT_KEYWORDS)


def high_impact_events(events: list[dict[str, Any]], user_text: str) -> list[str]:
    """Return high-impact event descriptions from FMP and user input."""
    descriptions: list[str] = []
    for event in events:
        name = str(event.get("event") or event.get("name") or "").strip()
        country = str(event.get("country") or "").upper()
        if country and country not in {"US", "USA", "UNITED STATES"}:
            continue
        if is_high_impact_event(name):
            event_time = str(event.get("date") or event.get("time") or "time n/a")
            descriptions.append(f"{event_time}: {name}")
    if user_text and is_high_impact_event(user_text):
        descriptions.insert(0, f"User-supplied: {user_text}")
    return descriptions


def calendar_lines(events: list[dict[str, Any]], user_text: str) -> list[str]:
    """Build economic calendar lines, prioritizing U.S. and high-impact events."""
    prioritized: list[tuple[int, str]] = []
    for event in events:
        name = str(event.get("event") or event.get("name") or "Economic event")
        country = str(event.get("country") or "")
        country_code = country.upper()
        is_us = country_code in {"US", "USA", "UNITED STATES"}
        is_high = is_high_impact_event(name)
        if not is_us and not is_high:
            continue

        event_time = str(event.get("date") or event.get("time") or "time n/a")
        impact = (
            event_impact_note(name)
            if is_high
            else "routine U.S. calendar item; low expected index impact unless surprise is large."
        )
        priority = 0 if is_us and is_high else (1 if is_us else 2)
        prioritized.append((priority, f"- {event_time} {country_code} - {name}: {impact}"))

    prioritized.sort(key=lambda item: item[0])
    lines = [line for _, line in prioritized[:12]]
    if user_text:
        lines.insert(0, f"- User-supplied event note: {user_text}")
    if not lines:
        lines = ["- No U.S. or high-impact FMP economic calendar items returned for today; confirm broker calendar before the open."]
    return lines


def event_impact_note(name: str) -> str:
    """Map an event name to a concise historical range-impact note."""
    lower = name.lower()
    if any(word in lower for word in ("cpi", "fomc", "powell", "pce", "federal reserve")):
        return "historically can expand SPX intraday range 1.5-2.0x; avoid selling tight premium into the release."
    if any(word in lower for word in ("nfp", "payroll", "jobless", "claims")):
        return "labor data can reset rate expectations and widen the opening range."
    if any(word in lower for word in ("pmi", "ism", "retail", "gdp", "ppi")):
        return "macro-growth data can lift realized volatility above the prior-day range."
    return "monitor for liquidity and volatility changes around the release."


def earnings_exposure(rows: list[dict[str, Any]]) -> list[str]:
    """Build a concise list of major earnings that can move index beta."""
    prioritized: list[tuple[int, str]] = []
    for row in rows:
        symbol = str(row.get("symbol") or "").upper()
        if not symbol:
            continue
        # Skip most non-U.S. exchange suffixes unless the ticker is explicitly index-heavy.
        if "." in symbol and symbol not in INDEX_HEAVY_TICKERS:
            continue
        time = str(row.get("time") or row.get("hour") or "time n/a").upper()
        company = row.get("company") or row.get("name") or symbol
        is_major = symbol in INDEX_HEAVY_TICKERS
        potential = "High" if is_major else "Low/Medium"
        priority = 0 if is_major else 1
        prioritized.append((priority, f"{symbol} ({company}, {time}) - market-moving potential: {potential}"))

    prioritized.sort(key=lambda item: item[0])
    return [line for _, line in prioritized[:10]]


def unique_levels(levels: list[tuple[float, str]], current: float, side: str) -> list[tuple[float, str]]:
    """Return three de-duplicated support or resistance levels."""
    if side == "support":
        filtered = [(value, reason) for value, reason in levels if value < current]
        filtered.sort(key=lambda item: item[0], reverse=True)
    else:
        filtered = [(value, reason) for value, reason in levels if value > current]
        filtered.sort(key=lambda item: item[0])

    output: list[tuple[float, str]] = []
    seen: set[int] = set()
    for value, reason in filtered:
        rounded = round_to_increment(value)
        if rounded in seen:
            continue
        seen.add(rounded)
        output.append((float(rounded), reason))
        if len(output) == 3:
            break
    return output


def telegram_send(chat_id: str, text: str) -> None:
    """Send a markdown report to Telegram, splitting messages at API limits."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN or TELEGRAM_TOKEN is required to send Telegram output")

    chunks = textwrap.wrap(
        text,
        width=3900,
        replace_whitespace=False,
        drop_whitespace=False,
        break_long_words=False,
    )
    if not chunks:
        chunks = [text]

    for idx, chunk in enumerate(chunks, start=1):
        prefix = f"Part {idx}/{len(chunks)}\n\n" if len(chunks) > 1 else ""
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": prefix + chunk,
                "disable_web_page_preview": True,
            },
            timeout=20,
        )
        response.raise_for_status()


def build_report(raw_args: str = "") -> tuple[Path, str, str]:
    """Build and write the Jane Street pre-market report."""
    parsed = parse_command_args(raw_args)
    et_today = datetime.now(ZoneInfo("America/New_York")).date()
    lookback_start = et_today - timedelta(days=14)
    output_path = OUTPUT_DIR / f"Jane-Street-pre-market-edge-analyzer-{et_today.isoformat()}.md"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    quotes = fmp_get("/quote/^GSPC,SPY,^VIX")
    if not isinstance(quotes, list):
        quotes = []
    spx_quote = latest_quote(quotes, "^GSPC")
    spy_quote = latest_quote(quotes, "SPY")
    vix_quote = latest_quote(quotes, "^VIX")

    spx_history = historical_rows("^GSPC", lookback_start, et_today)
    spy_history = historical_rows("SPY", lookback_start, et_today)
    vix_history = historical_rows("^VIX", lookback_start, et_today)

    prior_spx = prior_session(spx_history, et_today)
    prior_spy = prior_session(spy_history, et_today)
    prior_vix = prior_session(vix_history, et_today)

    econ_rows = fmp_get("/economic_calendar", {"from": et_today.isoformat(), "to": et_today.isoformat()})
    if not isinstance(econ_rows, list):
        econ_rows = []
    earnings_rows = fmp_get("/earning_calendar", {"from": et_today.isoformat(), "to": et_today.isoformat()})
    if not isinstance(earnings_rows, list):
        earnings_rows = []

    prior_spx_close = float(prior_spx.get("close") or 0) or None
    prior_spx_high = float(prior_spx.get("high") or 0) or None
    prior_spx_low = float(prior_spx.get("low") or 0) or None
    prior_spx_open = float(prior_spx.get("open") or 0) or None
    prior_spy_close = float(prior_spy.get("close") or 0) or None

    current_spx = parsed.spx_futures or price_from_quote(spx_quote)
    current_source = "user-supplied SPX/ES futures" if parsed.spx_futures else "FMP ^GSPC quote proxy"
    if current_spx is None and price_from_quote(spy_quote) is not None and prior_spy_close and prior_spx_close:
        current_spx = price_from_quote(spy_quote) * (prior_spx_close / prior_spy_close)
        current_source = "SPY quote scaled to SPX"
    if current_spx is None:
        current_spx = prior_spx_close or 0
        current_source = "prior SPX close fallback"

    vix_current = parsed.vix or price_from_quote(vix_quote) or float(prior_vix.get("close") or 0)
    vix_source = "user input" if parsed.vix else "FMP ^VIX quote"
    vix_prior_close = float(prior_vix.get("close") or 0) or None
    vix_change = ((vix_current - vix_prior_close) / vix_prior_close * 100) if vix_prior_close else None

    gap_points = current_spx - prior_spx_close if prior_spx_close else None
    gap_pct = gap_points / prior_spx_close * 100 if gap_points is not None and prior_spx_close else None
    abs_gap_pct = abs(gap_pct or 0)
    high_events = high_impact_events(econ_rows, parsed.events_text)

    if high_events:
        gap_view = "Uncertain"
        gap_reason = "macro event risk can override overnight positioning; wait for post-event price discovery."
    elif abs_gap_pct > 0.5:
        gap_view = "Fade early"
        gap_reason = "large overnight gaps often mean-revert during the first 30-60 minutes without fresh catalyst follow-through."
    elif abs_gap_pct > 0.15:
        gap_view = "Hold with confirmation"
        gap_reason = "moderate gap can extend if the first 15-minute range holds above/below prior close."
    else:
        gap_view = "Neutral"
        gap_reason = "small gap gives less directional edge; prioritize range definition before selling premium."

    expected_move = current_spx * (vix_current / 100) / math.sqrt(252) if current_spx and vix_current else 0
    expected_pct = expected_move / current_spx * 100 if current_spx else 0
    prior_range = (prior_spx_high - prior_spx_low) if prior_spx_high and prior_spx_low else None

    close_location = None
    close_read = "middle of the range"
    close_lean = "Neutral"
    if prior_spx_close and prior_spx_high and prior_spx_low and prior_spx_high > prior_spx_low:
        close_location = (prior_spx_close - prior_spx_low) / (prior_spx_high - prior_spx_low)
        if close_location >= 0.70:
            close_read = "near the highs"
            close_lean = "Bullish continuation lean, but watch for gap exhaustion."
        elif close_location <= 0.30:
            close_read = "near the lows"
            close_lean = "Bearish carryover risk, with bounce potential if sellers fail at support."

    event_risk = "Heavy" if high_events else ("Moderate" if len(econ_rows) >= 5 else "Light")
    earnings_list = earnings_exposure(earnings_rows)
    earnings_risk = "High" if any("High" in item for item in earnings_list) else ("Medium" if earnings_list else "Low")

    supports = unique_levels(
        [
            (prior_spx_low or 0, "Prior session low"),
            (prior_spx_close or 0, "Prior session close / gap magnet"),
            (current_spx - expected_move, "VIX-implied downside expected move"),
            (nearest_round_level(current_spx, "down"), "Nearby round-number strike"),
            (current_spx - (prior_range or expected_move), "Prior-day range projection"),
        ],
        current_spx,
        "support",
    )
    resistances = unique_levels(
        [
            (prior_spx_high or 0, "Prior session high"),
            (prior_spx_close or 0, "Prior session close / gap magnet"),
            (current_spx + expected_move, "VIX-implied upside expected move"),
            (nearest_round_level(current_spx, "up"), "Nearby round-number strike"),
            (current_spx + (prior_range or expected_move), "Prior-day range projection"),
        ],
        current_spx,
        "resistance",
    )

    short_put = round_to_increment(current_spx - expected_move)
    short_call = round_to_increment(current_spx + expected_move)
    long_put = short_put - 10
    long_call = short_call + 10

    if event_risk == "Heavy":
        strategy = "0DTE iron condor only after the event clears"
        entry = "Wait until 9:45-10:00 AM ET, or 15 minutes after the high-impact event reaction settles."
        size = "Half size to 1x normal risk; cap defined-risk exposure at 1-2% of account."
    elif vix_current >= 22:
        strategy = "0DTE wide iron condor / defined-risk strangle proxy"
        entry = "9:40-9:55 AM ET after the opening range is visible."
        size = "1x normal size; keep risk defined because elevated VIX can trend."
    else:
        strategy = "0DTE iron condor"
        entry = "9:35-9:50 AM ET after the open settles."
        size = "2-3% of account at risk across both wings."

    if vix_change is not None:
        iv_sentence = (
            f"VIX is {fmt_pct(vix_change)} versus the prior close ({fmt_price(vix_prior_close)}), "
            f"so options are pricing {'higher' if vix_change > 0 else 'lower'} volatility than yesterday."
        )
    else:
        iv_sentence = "VIX prior-close comparison was unavailable from FMP; use broker IV screens to confirm pre-market option richness."

    econ_lines = calendar_lines(econ_rows, parsed.events_text)

    support_lines = [f"- Support {idx}: {fmt_price(level, 0)} - {reason}" for idx, (level, reason) in enumerate(supports, 1)]
    resistance_lines = [f"- Resistance {idx}: {fmt_price(level, 0)} - {reason}" for idx, (level, reason) in enumerate(resistances, 1)]

    report = f"""# Jane Street Pre-Market Edge - {et_today.isoformat()}

## Market assessment

SPX/ES proxy is {fmt_price(current_spx)} from {current_source} versus prior SPX close {fmt_price(prior_spx_close)}. Gap: {fmt_price(gap_points)} points ({fmt_pct(gap_pct)}). View: **{gap_view}** - {gap_reason}

{iv_sentence} Calendar risk is **{event_risk}** and earnings beta risk is **{earnings_risk}**. The prior session closed {close_read}, giving a **{close_lean}** read into today's open.

The cleanest theta setup is **{strategy}** using expected-move strikes, with entry delayed until the first opening range confirms liquidity and direction.

## Overnight futures movement

- Current SPX/ES proxy: {fmt_price(current_spx)} ({current_source}; use broker ES/SPX for exact futures).
- Prior SPX close: {fmt_price(prior_spx_close)}.
- Overnight gap: {fmt_price(gap_points)} points ({fmt_pct(gap_pct)}).
- Hold/fade view: **{gap_view}** - {gap_reason}

## Pre-market IV levels

- Current VIX: {fmt_price(vix_current)} ({vix_source}).
- Prior VIX close: {fmt_price(vix_prior_close)}.
- VIX vs yesterday: {fmt_pct(vix_change)}.
- Implication: {'Premium selling is more attractive, but use wider strikes.' if vix_change and vix_change > 0 else 'Premium is less inflated; prioritize clean range and avoid chasing low-credit spreads.'}

## Economic calendar impact

Today's calendar: **{event_risk}**.

{chr(10).join(econ_lines)}

Recommendation: {'Use wider strikes or wait until after the event reaction.' if event_risk == 'Heavy' else 'Normal theta is acceptable after the first 15-minute range, provided spreads are liquid.'}

## Earnings exposure

{chr(10).join('- ' + item for item in earnings_list) if earnings_list else '- No major index-heavy earnings returned by FMP for today.'}

Market-moving potential: **{earnings_risk}**. Single-name IV may be elevated; index impact is material only if mega-cap or sector bellwether reports surprise guidance.

## Globex range and expected range

- Globex high/low: from broker/futures platform; FMP does not provide ES overnight high/low in this workflow.
- Prior-day SPX range proxy: {fmt_price(prior_range)} points (high {fmt_price(prior_spx_high)}, low {fmt_price(prior_spx_low)}).
- VIX-based 1-day expected move: +/- {fmt_price(expected_move)} points (~+/-{expected_pct:.2f}%).

## Opening gap strategy

- Opening plan: **{'Stay flat until the event/opening range clears' if event_risk == 'Heavy' else 'Define the first 15-minute range, then sell premium outside expected move.'}**
- If the gap is rejected back through prior close, favor gap fade and avoid adding short premium on the challenged side.
- If price holds above/below the first 15-minute range with VIX rising, stand down from neutral theta and wait for trend exhaustion.

## IV crush opportunity

- Yesterday high-IV event flag: {'Yes / possible carryover from macro calendar' if high_events else 'No major event detected from today-only FMP calendar; confirm prior-day broker event calendar.'}
- IV crush setup: {'Potentially attractive after the event if VIX starts mean reverting.' if vix_current >= 18 else 'Limited; VIX is not rich enough to force a premium-sale trade.'}

## Previous day's close analysis

- Prior open/high/low/close: {fmt_price(prior_spx_open)} / {fmt_price(prior_spx_high)} / {fmt_price(prior_spx_low)} / {fmt_price(prior_spx_close)}.
- Close location: {f'{close_location * 100:.0f}% of prior range' if close_location is not None else 'n/a'}.
- Read: Market closed {close_read}. **{close_lean}**

## Support and resistance

### Support

{chr(10).join(support_lines)}

### Resistance

{chr(10).join(resistance_lines)}

## Pre-market trade plan

- Strategy: **{strategy}**.
- Expiration: Today / 0DTE.
- Strikes: Sell {short_put} put / buy {long_put} put; sell {short_call} call / buy {long_call} call.
- Entry time: {entry}
- Position size: {size}
- Risk controls: close at 50% max profit; stop if short strike is breached or spread value reaches ~2x credit.

## Scenario playbook

- Bull outcome: SPX above Resistance 1 ({fmt_price(resistances[0][0] if resistances else None, 0)}). Close or reduce the call side if breached; let the put side decay or close at 50-75% profit.
- Bear outcome: SPX below Support 1 ({fmt_price(supports[0][0] if supports else None, 0)}). Close or roll the put side; take profits on the call side.
- Neutral outcome: SPX remains between Support 1 and Resistance 1. Hold toward 50% max profit, then close; avoid late-day gamma if credit is mostly captured.

## Data and disclaimer

Data sources: FMP quote (^GSPC, SPY, ^VIX), FMP historical-price-full (^GSPC, SPY, ^VIX), FMP economic_calendar, FMP earning_calendar, and optional user-supplied futures/VIX/news. Globex high/low should be confirmed on a broker or futures platform.

Educational/research use only. This is not investment advice or a recommendation to buy or sell securities or options. Options involve risk and can result in total loss.
"""

    output_path.write_text(report, encoding="utf-8")

    summary = (
        f"Jane Street Pre-Market Edge {et_today.isoformat()}\n"
        f"Gap: {fmt_price(gap_points)} pts ({fmt_pct(gap_pct)}), view: {gap_view}.\n"
        f"VIX: {fmt_price(vix_current)} vs prior {fmt_price(vix_prior_close)} ({fmt_pct(vix_change)}).\n"
        f"Event risk: {event_risk}; earnings risk: {earnings_risk}.\n"
        f"Strategy: {strategy}; strikes {short_put}/{long_put} put spread and {short_call}/{long_call} call spread.\n"
        f"Support: {', '.join(fmt_price(level, 0) for level, _ in supports)}. "
        f"Resistance: {', '.join(fmt_price(level, 0) for level, _ in resistances)}.\n"
        f"Report: {output_path}"
    )

    return output_path, report, summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Jane Street pre-market edge analyzer.")
    parser.add_argument("arguments", nargs="*", help="Optional command arguments: SPX futures, VIX, event text")
    parser.add_argument("--send-telegram", action="store_true", help="Send the generated report to Telegram")
    parser.add_argument("--telegram-chat-id", default=os.environ.get("TELEGRAM_CHAT_ID", DEFAULT_TELEGRAM_CHAT_ID))
    args = parser.parse_args()

    raw_args = " ".join(args.arguments)
    output_path, report, summary = build_report(raw_args)
    print(summary)

    if args.send_telegram:
        telegram_send(args.telegram_chat_id, report)
        print(f"Telegram sent to chat {args.telegram_chat_id}")

    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
