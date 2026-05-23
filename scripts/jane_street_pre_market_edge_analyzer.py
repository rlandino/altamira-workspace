#!/usr/bin/env python3
"""Generate the Jane Street pre-market edge briefing and optionally send it to Telegram."""

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
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FMP_BASE = "https://financialmodelingprep.com/api/v3"
DEFAULT_FMP_KEY = "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz"
DEFAULT_TELEGRAM_CHAT_ID = "7830722515"
HIGH_IMPACT_TERMS = (
    "cpi",
    "pce",
    "fomc",
    "fed",
    "powell",
    "nfp",
    "nonfarm",
    "payroll",
    "pmi",
    "ism",
    "retail sales",
    "jobless",
    "claims",
    "gdp",
    "ppi",
)
MARKET_MOVING_TICKERS = {
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
    "COST",
    "WMT",
    "HD",
    "V",
    "MA",
}


@dataclass
class ParsedArgs:
    futures_price: float | None
    vix_level: float | None
    overnight_high: float | None
    overnight_low: float | None
    events_text: str


def request_json(url: str, timeout: int = 20) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "altamira-jane-street-analyzer/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fmp_get(path: str, api_key: str, params: dict[str, str] | None = None) -> Any:
    query = dict(params or {})
    query["apikey"] = api_key
    encoded_path = urllib.parse.quote(path, safe="/,")
    url = f"{FMP_BASE}/{encoded_path}?{urllib.parse.urlencode(query)}"
    return request_json(url)


def parse_command_args(raw_args: list[str]) -> ParsedArgs:
    text = " ".join(raw_args).strip()
    if not text:
        return ParsedArgs(None, None, None, None, "")

    futures_price: float | None = None
    vix_level: float | None = None
    overnight_high: float | None = None
    overnight_low: float | None = None
    consumed_spans: list[tuple[int, int]] = []

    for pattern, target in (
        (r"\b(?:vix|vol(?:atility)?)\s*[:=]?\s*(\d+(?:\.\d+)?)", "vix"),
        (r"\b(?:spx|es|futures?)\s*[:=]?\s*(\d{4,5}(?:\.\d+)?)", "futures"),
        (r"\b(?:high|globex high)\s*[:=]?\s*(\d{4,5}(?:\.\d+)?)", "high"),
        (r"\b(?:low|globex low)\s*[:=]?\s*(\d{4,5}(?:\.\d+)?)", "low"),
    ):
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            continue
        value = float(match.group(1))
        if target == "vix":
            vix_level = value
        elif target == "futures":
            futures_price = value
        elif target == "high":
            overnight_high = value
        elif target == "low":
            overnight_low = value
        consumed_spans.append(match.span())

    if futures_price is None or vix_level is None:
        for match in re.finditer(r"\b\d+(?:\.\d+)?\b", text):
            if any(start <= match.start() and match.end() <= end for start, end in consumed_spans):
                continue
            value = float(match.group(0))
            if futures_price is None and value >= 1000:
                futures_price = value
                consumed_spans.append(match.span())
            elif vix_level is None and 5 <= value <= 100:
                vix_level = value
                consumed_spans.append(match.span())

    event_chars = list(text)
    for start, end in consumed_spans:
        for i in range(start, end):
            event_chars[i] = " "
    events_text = re.sub(r"\s+", " ", "".join(event_chars)).strip(" ,;-")
    return ParsedArgs(futures_price, vix_level, overnight_high, overnight_low, events_text)


def quote_by_symbol(quotes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(item.get("symbol", "")).upper(): item for item in quotes if isinstance(item, dict)}


def latest_historical_bar(payload: dict[str, Any]) -> dict[str, Any] | None:
    rows = payload.get("historical") if isinstance(payload, dict) else None
    if not rows:
        return None
    return rows[0]


def prior_historical_bar(payload: dict[str, Any], latest_date: str | None) -> dict[str, Any] | None:
    rows = payload.get("historical") if isinstance(payload, dict) else None
    if not rows:
        return None
    if latest_date is None:
        return rows[1] if len(rows) > 1 else None
    for row in rows:
        if row.get("date") != latest_date:
            return row
    return rows[1] if len(rows) > 1 else None


def safe_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def money(value: float | None, digits: int = 2) -> str:
    if value is None or math.isnan(value):
        return "n/a"
    return f"{value:,.{digits}f}"


def signed(value: float | None, digits: int = 2) -> str:
    if value is None or math.isnan(value):
        return "n/a"
    return f"{value:+,.{digits}f}"


def rounded_25(value: float) -> int:
    return int(round(value / 25.0) * 25)


def market_is_open_session(report_date: dt.date, latest_bar: dict[str, Any] | None) -> bool:
    if report_date.weekday() >= 5:
        return False
    return latest_bar is not None and latest_bar.get("date") == report_date.isoformat()


def classify_close_location(bar: dict[str, Any]) -> tuple[str, str, float]:
    high = safe_float(bar.get("high")) or 0.0
    low = safe_float(bar.get("low")) or 0.0
    close = safe_float(bar.get("close")) or 0.0
    if high <= low:
        return "in the middle", "Neutral", 0.5
    location = (close - low) / (high - low)
    if location >= 0.72:
        return "near the highs", "Bearish fade risk", location
    if location <= 0.28:
        return "near the lows", "Bullish rebound setup", location
    return "in the middle", "Neutral", location


def calendar_impact(events: list[dict[str, Any]], manual_events: str) -> tuple[str, list[str], str]:
    lines: list[str] = []
    high_count = 0
    if manual_events:
        high = any(term in manual_events.lower() for term in HIGH_IMPACT_TERMS)
        high_count += int(high)
        impact = "High impact" if high else "User-supplied event"
        lines.append(f"- **Manual note:** {manual_events} ({impact}).")

    for event in events[:20]:
        name = str(event.get("event") or event.get("name") or event.get("title") or "Economic event")
        country = str(event.get("country") or "")
        if country and country.upper() not in {"US", "USA", "UNITED STATES"}:
            continue
        event_time = str(event.get("date") or event.get("time") or "time n/a")
        lower = name.lower()
        high = any(term in lower for term in HIGH_IMPACT_TERMS)
        high_count += int(high)
        tag = "high impact; can expand range 1.5-2.0x" if high else "lower impact"
        lines.append(f"- **{event_time}:** {name} ({tag}).")

    if not lines:
        lines.append("- No major scheduled US economic releases found in FMP for the report date.")

    if high_count >= 2:
        return "Heavy", lines, "Use wider strikes or wait until after the event impulse settles."
    if high_count == 1:
        return "Moderate", lines, "Trade smaller and avoid selling premium directly into the event."
    return "Light", lines, "Normal theta posture is acceptable if price action confirms."


def earnings_exposure(earnings: list[dict[str, Any]]) -> tuple[str, list[str]]:
    selected: list[dict[str, Any]] = []
    for item in earnings:
        symbol = str(item.get("symbol") or "").upper()
        if symbol in MARKET_MOVING_TICKERS:
            selected.append(item)

    lines: list[str] = []
    market_movers = 0
    for item in selected[:10]:
        symbol = str(item.get("symbol") or "n/a").upper()
        company = str(item.get("name") or item.get("companyName") or "")
        when = str(item.get("time") or item.get("date") or "time n/a")
        cap = safe_float(item.get("marketCap"))
        cap_text = f", market cap ${cap / 1_000_000_000:.1f}B" if cap else ""
        potential = "High" if symbol in MARKET_MOVING_TICKERS else "Low/Medium"
        market_movers += int(potential == "High")
        display_name = f" ({company})" if company and company != symbol else ""
        lines.append(f"- **{symbol}{display_name}:** {when}{cap_text}; market-moving potential {potential}.")

    if not lines:
        total_reports = len(earnings)
        suffix = f" ({total_reports} total global reports in FMP)." if total_reports else "."
        lines.append(f"- No major index-heavy earnings found in FMP for the report date{suffix}")

    exposure = "High" if market_movers >= 2 else "Medium" if market_movers == 1 else "Low"
    return exposure, lines


def support_resistance(current: float, prior_bar: dict[str, Any], expected_move: float) -> tuple[list[tuple[float, str]], list[tuple[float, str]]]:
    high = safe_float(prior_bar.get("high")) or current
    low = safe_float(prior_bar.get("low")) or current
    close = safe_float(prior_bar.get("close")) or current
    supports = [
        (round(min(close, current) - expected_move * 0.5, 2), "Half expected-move downside from current/reference price"),
        (round(low, 2), "Prior session low"),
        (float(rounded_25(current - expected_move)), "Full expected-move downside / round strike zone"),
    ]
    resistances = [
        (round(max(close, current) + expected_move * 0.5, 2), "Half expected-move upside from current/reference price"),
        (round(high, 2), "Prior session high"),
        (float(rounded_25(current + expected_move)), "Full expected-move upside / round strike zone"),
    ]
    supports = sorted({level: reason for level, reason in supports}.items(), reverse=True)
    resistances = sorted({level: reason for level, reason in resistances}.items())
    return [(float(level), reason) for level, reason in supports[:3]], [(float(level), reason) for level, reason in resistances[:3]]


def build_trade_plan(
    current: float,
    vix: float,
    expected_move: float,
    is_open_session: bool,
    calendar_weight: str,
) -> tuple[str, dict[str, float | str]]:
    if not is_open_session:
        return (
            "No trade -- US equity/options market is closed for the report date. Re-run on the next cash session before placing 0DTE risk.",
            {},
        )

    width = 10 if current >= 1000 else 1
    short_put = rounded_25(current - expected_move * 1.15)
    long_put = short_put - width
    short_call = rounded_25(current + expected_move * 1.15)
    long_call = short_call + width
    size = "1/2 normal size" if calendar_weight in {"Moderate", "Heavy"} or vix >= 22 else "1x normal size"
    if calendar_weight == "Heavy":
        strategy = "Wait-until-after-event 0DTE iron condor"
        entry = "After the highest-impact scheduled event and first 15-minute opening balance"
    else:
        strategy = "0DTE iron condor"
        entry = "9:35-9:50 AM ET after the opening print stabilizes"
    text = (
        f"{strategy}: sell {short_put}/{long_put} put spread and {short_call}/{long_call} call spread, "
        f"same-day expiration. Entry: {entry}. Size: {size}; cap risk near 1-2% of account."
    )
    details: dict[str, float | str] = {
        "short_put": short_put,
        "long_put": long_put,
        "short_call": short_call,
        "long_call": long_call,
        "entry": entry,
        "size": size,
    }
    return text, details


def telegram_chunks(text: str, limit: int = 3900) -> list[str]:
    chunks: list[str] = []
    remaining = text
    while len(remaining) > limit:
        split_at = remaining.rfind("\n", 0, limit)
        if split_at < 1000:
            split_at = limit
        chunks.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].strip()
    if remaining:
        chunks.append(remaining)
    return chunks


def send_telegram(text: str, chat_id: str, bot_token: str) -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    for chunk in telegram_chunks(text):
        data = urllib.parse.urlencode(
            {
                "chat_id": chat_id,
                "text": chunk,
                "disable_web_page_preview": "true",
            }
        ).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if not payload.get("ok"):
            raise RuntimeError(f"Telegram send failed: {payload}")


def format_telegram_summary(report_date: dt.date, summary: dict[str, str], output_path: Path) -> str:
    return textwrap.dedent(
        f"""\
        Jane Street Pre-Market Edge -- {report_date.isoformat()}

        Gap: {summary['gap']}
        VIX: {summary['vix']}
        Event risk: {summary['event_risk']}
        Strategy: {summary['strategy']}

        Support: {summary['support']}
        Resistance: {summary['resistance']}

        Full report: {output_path}
        """
    ).strip()


def build_report(args: argparse.Namespace) -> tuple[Path, str, dict[str, str]]:
    report_date = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    parsed = parse_command_args(args.command_args)
    api_key = args.fmp_key or os.environ.get("FMP_API_KEY") or DEFAULT_FMP_KEY
    from_date = (report_date - dt.timedelta(days=14)).isoformat()
    to_date = report_date.isoformat()

    quote_map: dict[str, dict[str, Any]] = {}
    spy_history: dict[str, Any] = {}
    vix_history: dict[str, Any] = {}
    economic_events: list[dict[str, Any]] = []
    earnings: list[dict[str, Any]] = []
    errors: list[str] = []

    for label, loader in (
        ("quotes", lambda: fmp_get("quote/^GSPC,SPY,^VIX", api_key)),
        ("SPY historical", lambda: fmp_get("historical-price-full/SPY", api_key, {"from": from_date, "to": to_date})),
        ("VIX historical", lambda: fmp_get("historical-price-full/^VIX", api_key, {"from": from_date, "to": to_date})),
        ("economic calendar", lambda: fmp_get("economic_calendar", api_key, {"from": to_date, "to": to_date})),
        ("earnings calendar", lambda: fmp_get("earning_calendar", api_key, {"from": to_date, "to": to_date})),
    ):
        try:
            payload = loader()
            if label == "quotes":
                quote_map = quote_by_symbol(payload if isinstance(payload, list) else [])
            elif label == "SPY historical":
                spy_history = payload if isinstance(payload, dict) else {}
            elif label == "VIX historical":
                vix_history = payload if isinstance(payload, dict) else {}
            elif label == "economic calendar":
                economic_events = payload if isinstance(payload, list) else []
            elif label == "earnings calendar":
                earnings = payload if isinstance(payload, list) else []
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            errors.append(f"{label}: {exc}")

    spy_quote = quote_map.get("SPY", {})
    spx_quote = quote_map.get("^GSPC", {})
    vix_quote = quote_map.get("^VIX", {})
    latest_spy = latest_historical_bar(spy_history)
    previous_spy = prior_historical_bar(spy_history, latest_spy.get("date") if latest_spy else None) if latest_spy else None
    latest_vix = latest_historical_bar(vix_history)
    previous_vix = prior_historical_bar(vix_history, latest_vix.get("date") if latest_vix else None) if latest_vix else None

    prior_bar = latest_spy or {
        "date": to_date,
        "open": safe_float(spy_quote.get("open")) or safe_float(spy_quote.get("price")) or 0,
        "high": safe_float(spy_quote.get("dayHigh")) or safe_float(spy_quote.get("price")) or 0,
        "low": safe_float(spy_quote.get("dayLow")) or safe_float(spy_quote.get("price")) or 0,
        "close": safe_float(spy_quote.get("price")) or 0,
    }

    spy_close = safe_float(prior_bar.get("close")) or safe_float(spy_quote.get("price")) or 0.0
    spx_close = safe_float(spx_quote.get("previousClose")) or safe_float(spx_quote.get("price")) or spy_close * 10
    spy_spx_factor = spx_close / spy_close if spy_close else 10.0
    supplied_futures = parsed.futures_price is not None
    reference_spx = parsed.futures_price or safe_float(spx_quote.get("preMarketPrice")) or safe_float(spx_quote.get("price")) or spx_close
    reference_spy = reference_spx / spy_spx_factor if reference_spx and spy_spx_factor else spy_close

    vix = parsed.vix_level or safe_float(vix_quote.get("price")) or safe_float(latest_vix.get("close") if latest_vix else None) or 18.0
    vix_prev_close = safe_float(previous_vix.get("close") if previous_vix else None)
    if vix_prev_close is None and latest_vix and latest_vix.get("date") != to_date:
        vix_prev_close = safe_float(latest_vix.get("close"))
    vix_change = vix - vix_prev_close if vix_prev_close is not None else None
    vix_change_pct = (vix_change / vix_prev_close * 100) if vix_change is not None and vix_prev_close else None

    is_open_session = market_is_open_session(report_date, latest_spy)
    gap_points = reference_spx - spx_close if reference_spx and spx_close else 0.0
    gap_pct = gap_points / spx_close * 100 if spx_close else 0.0
    if not is_open_session:
        gap_view = "No trade"
        gap_reason = "report date is not an active US equity/options session."
    elif abs(gap_pct) > 0.5:
        gap_view = "Fade risk"
        gap_reason = "large overnight gaps often mean-revert during the first hour unless confirmed by event flow."
    elif abs(gap_pct) < 0.15:
        gap_view = "Hold/extend possible"
        gap_reason = "small gaps can extend when opening breadth confirms."
    else:
        gap_view = "Uncertain"
        gap_reason = "medium gap; wait for first 15-minute balance before selling premium."

    close_location, close_lean, close_ratio = classify_close_location(prior_bar)
    prior_range_spy = (safe_float(prior_bar.get("high")) or 0.0) - (safe_float(prior_bar.get("low")) or 0.0)
    prior_range_spx = prior_range_spy * spy_spx_factor
    expected_move = reference_spx * (vix / 100) / math.sqrt(252) if reference_spx else 0.0
    expected_pct = expected_move / reference_spx * 100 if reference_spx else 0.0
    calendar_weight, economic_lines, calendar_recommendation = calendar_impact(economic_events, parsed.events_text)
    earnings_weight, earnings_lines = earnings_exposure(earnings)
    supports, resistances = support_resistance(reference_spx, {
        "high": (safe_float(prior_bar.get("high")) or 0.0) * spy_spx_factor,
        "low": (safe_float(prior_bar.get("low")) or 0.0) * spy_spx_factor,
        "close": (safe_float(prior_bar.get("close")) or 0.0) * spy_spx_factor,
    }, expected_move)
    trade_plan, trade_details = build_trade_plan(reference_spx, vix, expected_move, is_open_session, calendar_weight)

    if not is_open_session:
        opening_strategy = "Stay flat. The report date is a weekend/non-cash session, so preserve the plan for the next regular market open."
        iv_crush = "No same-day IV crush trade today because index options are closed."
    elif calendar_weight == "Heavy":
        opening_strategy = "Stay cautious until the event clears; sell defined-risk premium only after spreads normalize."
        iv_crush = "Potential IV crush exists after the scheduled event, but avoid pre-event naked theta."
    elif abs(gap_pct) > 0.5:
        opening_strategy = "Fade the gap only after failed continuation through the first 15-minute range."
        iv_crush = "Elevated gap premium can be sold with defined risk after the opening impulse."
    else:
        opening_strategy = "Normal theta setup after the open; define risk outside the VIX one-day expected move."
        iv_crush = "No obvious prior high-IV event; theta edge depends on realized range staying below implied."

    if parsed.overnight_high and parsed.overnight_low:
        globex_line = (
            f"Overnight range: high {money(parsed.overnight_high)}, low {money(parsed.overnight_low)} "
            f"({money(parsed.overnight_high - parsed.overnight_low)} points)."
        )
    else:
        globex_line = (
            f"Globex high/low: from broker/futures platform. FMP proxy uses prior SPY range "
            f"of {money(prior_range_spy)} SPY points (~{money(prior_range_spx)} SPX points)."
        )

    support_text = "; ".join(f"{money(level, 0)} ({reason})" for level, reason in supports)
    resistance_text = "; ".join(f"{money(level, 0)} ({reason})" for level, reason in resistances)
    session_note = (
        "US equity/options market is closed for the report date; this is a planning brief, not an executable 0DTE ticket."
        if not is_open_session
        else "US cash session expected; confirm futures and broker quotes before order entry."
    )
    futures_source = "user input" if supplied_futures else "FMP quote/proxy; use SPX/ES from broker for exact futures"
    vix_source = "user input" if parsed.vix_level is not None else "FMP quote"
    vix_direction = (
        f"{signed(vix_change, 2)} pts ({signed(vix_change_pct, 1)}%) vs prior VIX close"
        if vix_change is not None and vix_change_pct is not None
        else "prior comparison unavailable"
    )

    report = textwrap.dedent(
        f"""\
        # Jane Street Pre-Market Edge -- {report_date.isoformat()}

        ## Market assessment

        SPX reference is {money(reference_spx)} ({futures_source}) versus prior SPX reference close {money(spx_close)}. Gap: {signed(gap_points)} points ({signed(gap_pct, 2)}%). View: **{gap_view}** -- {gap_reason}

        VIX is {money(vix)} ({vix_source}), {vix_direction}. Options pricing is {'higher' if (vix_change or 0) > 0 else 'lower or stable'} versus the prior reference, so premium selling should stay defined-risk and event-aware.

        Prior session SPY closed {close_location} of its range ({close_ratio:.0%} location), giving a **{close_lean}** read. Calendar weight is **{calendar_weight}** and earnings exposure is **{earnings_weight}**. {session_note}

        ## Overnight futures movement

        - **Reference:** {money(reference_spx)} SPX/ES-equivalent.
        - **Gap:** {signed(gap_points)} points ({signed(gap_pct, 2)}%).
        - **Hold/fade view:** **{gap_view}** -- {gap_reason}

        ## Pre-market IV levels

        - **Current VIX:** {money(vix)} ({vix_source}).
        - **Prior VIX close:** {money(vix_prev_close)}.
        - **Change:** {vix_direction}.
        - **Theta implication:** {'Premium is richer; favor defined-risk sales after confirmation.' if (vix_change or 0) > 0 else 'Premium is not clearly richer; avoid forcing short-vol entries.'}

        ## Economic calendar impact

        {chr(10).join(economic_lines)}

        - **Calendar weight:** {calendar_weight}.
        - **Recommendation:** {calendar_recommendation}

        ## Earnings exposure

        {chr(10).join(earnings_lines)}

        - **Index impact:** {earnings_weight}; single-name IV spikes may matter more than index gamma unless mega-cap reports dominate.

        ## Globex range and expected range

        - {globex_line}
        - **VIX-based one-day expected move:** +/-{money(expected_move)} SPX points (~+/-{expected_pct:.2f}%).
        - **Use:** Place short strikes beyond the expected move when liquidity and credit allow.

        ## Opening gap strategy

        - {opening_strategy}

        ## IV crush opportunity

        - {iv_crush}

        ## Previous day's close analysis

        - **Prior SPY date:** {prior_bar.get('date', 'n/a')}.
        - **Open / High / Low / Close:** {money(safe_float(prior_bar.get('open')))} / {money(safe_float(prior_bar.get('high')))} / {money(safe_float(prior_bar.get('low')))} / {money(safe_float(prior_bar.get('close')))}.
        - **Read:** Closed {close_location}; {close_lean}. A close near extremes raises first-hour reversal risk unless overnight flow confirms.

        ## Support and resistance

        **Support**
        1. {money(supports[0][0], 0)} -- {supports[0][1]}.
        2. {money(supports[1][0], 0)} -- {supports[1][1]}.
        3. {money(supports[2][0], 0)} -- {supports[2][1]}.

        **Resistance**
        1. {money(resistances[0][0], 0)} -- {resistances[0][1]}.
        2. {money(resistances[1][0], 0)} -- {resistances[1][1]}.
        3. {money(resistances[2][0], 0)} -- {resistances[2][1]}.

        ## Pre-market trade plan

        - **Strategy:** {trade_plan}
        - **Expiration:** {'No same-day order because the market is closed.' if not is_open_session else '0DTE / same-day SPX expiration.'}
        - **Entry time:** {'None today; re-run next regular session' if not is_open_session else trade_details.get('entry', '9:35-9:50 AM ET after open settles')}.
        - **Position size:** {'0% today' if not is_open_session else trade_details.get('size', '1x normal size; risk cap 1-2% of account')}.

        ## Scenario playbook

        - **Bull outcome:** SPX above Resistance 1 ({money(resistances[0][0], 0)}). If in a trade, reduce or close the call side on failed continuation; keep put side only if breadth confirms and premium has decayed.
        - **Bear outcome:** SPX below Support 1 ({money(supports[0][0], 0)}). If in a trade, close or roll threatened put risk; take profits on the call side.
        - **Neutral outcome:** SPX stays between Support 1 and Resistance 1. Hold defined-risk premium until 50% max profit or planned exit; avoid late-day gamma if credit is mostly harvested.

        ## Data and disclaimer

        - **Data sources:** FMP quote (^GSPC, SPY, ^VIX), FMP historical-price-full (SPY and ^VIX), FMP economic calendar, FMP earnings calendar; Globex/overnight from user input when supplied, otherwise broker/futures platform required for exact high/low.
        - **Data caveats:** FMP may not expose true pre-market SPX/ES or Globex high/low. Confirm futures, option chains, deltas, credits, and holiday schedule in a broker platform before trading.
        - **Disclaimer:** Educational/research only, not investment advice. Options involve risk and can lose more than expected if managed poorly.
        """
    )
    report = "\n".join(line[8:] if line.startswith("        ") else line for line in report.splitlines()) + "\n"
    if errors:
        report += "\n\n### Fetch warnings\n\n" + "\n".join(f"- {error}" for error in errors) + "\n"

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"Jane-Street-pre-market-edge-analyzer-{report_date.isoformat()}.md"
    output_path.write_text(report, encoding="utf-8")

    summary = {
        "gap": f"{signed(gap_points)} pts ({signed(gap_pct, 2)}%), {gap_view}",
        "vix": f"{money(vix)}; {vix_direction}",
        "event_risk": f"{calendar_weight}; earnings {earnings_weight}",
        "strategy": trade_plan,
        "support": support_text,
        "resistance": resistance_text,
    }
    return output_path, report, summary


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command_args", nargs="*", help="Optional futures price, VIX, and event text.")
    parser.add_argument("--date", help="Report date in YYYY-MM-DD. Defaults to today.")
    parser.add_argument("--output-dir", default="outputs", help="Directory for the markdown report.")
    parser.add_argument("--fmp-key", help="FMP API key. Defaults to FMP_API_KEY env or workspace default.")
    parser.add_argument("--telegram", action="store_true", help="Send a concise briefing to Telegram.")
    parser.add_argument("--telegram-full", action="store_true", help="Send the full markdown report to Telegram.")
    parser.add_argument("--telegram-chat-id", default=os.environ.get("TELEGRAM_CHAT_ID") or DEFAULT_TELEGRAM_CHAT_ID)
    parser.add_argument("--telegram-token", default=os.environ.get("TELEGRAM_BOT_TOKEN"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        output_path, report, summary = build_report(args)
    except Exception as exc:  # noqa: BLE001 - command-line runner should fail with a useful message.
        print(f"ERROR: failed to build report: {exc}", file=sys.stderr)
        return 1

    report_date = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    print(f"Wrote {output_path}")
    print()
    print(format_telegram_summary(report_date, summary, output_path))

    if args.telegram or args.telegram_full:
        if not args.telegram_token:
            print("ERROR: TELEGRAM_BOT_TOKEN is not set and --telegram-token was not provided.", file=sys.stderr)
            return 1
        message = report if args.telegram_full else format_telegram_summary(report_date, summary, output_path)
        try:
            send_telegram(message, args.telegram_chat_id, args.telegram_token)
        except Exception as exc:  # noqa: BLE001 - include Telegram API failure context.
            print(f"ERROR: failed to send Telegram message: {exc}", file=sys.stderr)
            return 1
        print(f"Sent Telegram briefing to chat {args.telegram_chat_id}.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
