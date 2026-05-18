#!/usr/bin/env python3
"""Run the Jane Street pre-market edge analyzer and optionally send Telegram.

The slash command is documented in .claude/commands; this script is the
automation-friendly runner used by cron/cloud jobs.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = WORKSPACE / "outputs"
FMP_BASE = "https://financialmodelingprep.com/api/v3"
FMP_API_KEY = os.environ.get("FMP_API_KEY", "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz")
DEFAULT_CHAT_SOURCE = WORKSPACE / "outputs" / "csp-daily-scan-fixed.json"


HIGH_IMPACT_KEYWORDS = (
    "cpi",
    "inflation",
    "fomc",
    "fed",
    "powell",
    "nfp",
    "nonfarm",
    "payroll",
    "pmi",
    "ism",
    "retail sales",
    "ppi",
    "pce",
    "jobless",
    "unemployment",
    "gdp",
)

MEGA_CAP_TICKERS = {
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "META",
    "GOOGL",
    "GOOG",
    "TSLA",
    "AVGO",
    "JPM",
    "UNH",
    "V",
    "MA",
    "LLY",
    "COST",
    "NFLX",
    "AMD",
    "CRM",
    "WMT",
    "HD",
}


@dataclass
class ParsedArgs:
    futures_price: float | None
    vix: float | None
    events_text: str


def parse_command_args(raw_args: str) -> ParsedArgs:
    """Extract optional futures price, VIX, and free-text event notes."""
    text = raw_args.strip()
    if not text:
        return ParsedArgs(None, None, "")

    futures_price: float | None = None
    vix: float | None = None

    vix_match = re.search(r"\bvix\b\s*[:=]?\s*(\d+(?:\.\d+)?)", text, re.I)
    if vix_match:
        vix = float(vix_match.group(1))

    spx_match = re.search(
        r"\b(?:spx|es|futures?)\b\s*[:=]?\s*(\d{3,5}(?:\.\d+)?)", text, re.I
    )
    if spx_match:
        futures_price = float(spx_match.group(1))

    numbers = [float(x) for x in re.findall(r"(?<![A-Za-z])(\d+(?:\.\d+)?)(?![A-Za-z])", text)]
    if futures_price is None:
        for number in numbers:
            if number >= 1000:
                futures_price = number
                break
    if vix is None:
        for number in numbers:
            if 5 <= number <= 80 and number != futures_price:
                vix = number
                break

    return ParsedArgs(futures_price, vix, text)


def fmp_get(path: str, params: dict[str, Any] | None = None) -> Any:
    """GET an FMP endpoint and return decoded JSON."""
    query = dict(params or {})
    query["apikey"] = FMP_API_KEY
    response = requests.get(f"{FMP_BASE}{path}", params=query, timeout=25)
    response.raise_for_status()
    return response.json()


def quote_map() -> dict[str, dict[str, Any]]:
    data = fmp_get("/quote/^GSPC,SPY,^VIX")
    if not isinstance(data, list):
        return {}
    return {str(row.get("symbol")): row for row in data if isinstance(row, dict)}


def historical(symbol: str, start: str, end: str) -> list[dict[str, Any]]:
    data = fmp_get(f"/historical-price-full/{symbol}", {"from": start, "to": end})
    rows = data.get("historical", []) if isinstance(data, dict) else []
    return rows if isinstance(rows, list) else []


def prior_session(rows: list[dict[str, Any]], report_date: str) -> dict[str, Any] | None:
    dated_rows = [row for row in rows if row.get("date")]
    dated_rows.sort(key=lambda row: row["date"], reverse=True)
    for row in dated_rows:
        if row["date"] < report_date:
            return row
    return dated_rows[0] if dated_rows else None


def pct(value: float) -> str:
    return f"{value:+.2f}%"


def points(value: float) -> str:
    return f"{value:+.1f}"


def money(value: float) -> str:
    return f"{value:,.2f}"


def round_down(value: float, step: int = 5) -> int:
    return int(math.floor(value / step) * step)


def round_up(value: float, step: int = 5) -> int:
    return int(math.ceil(value / step) * step)


def unique_levels(levels: list[tuple[float, str]], limit: int = 3) -> list[tuple[float, str]]:
    seen: set[int] = set()
    output: list[tuple[float, str]] = []
    for level, reason in levels:
        rounded = round(int(round(level / 5) * 5), -0)
        key = int(rounded)
        if key in seen:
            continue
        seen.add(key)
        output.append((float(key), reason))
        if len(output) >= limit:
            break
    return output


def classify_event(event: dict[str, Any]) -> bool:
    searchable = " ".join(str(event.get(k, "")) for k in ("event", "title", "name", "country", "currency"))
    return any(keyword in searchable.lower() for keyword in HIGH_IMPACT_KEYWORDS)


def format_event(event: dict[str, Any]) -> str:
    name = event.get("event") or event.get("title") or event.get("name") or "Economic event"
    time_value = event.get("date") or event.get("time") or "time n/a"
    country = event.get("country") or event.get("currency") or ""
    impact = "High-impact" if classify_event(event) else "Scheduled"
    return f"- **{time_value}** - {name}{f' ({country})' if country else ''}: {impact}."


def economic_calendar(report_date: str) -> list[dict[str, Any]]:
    data = fmp_get("/economic_calendar", {"from": report_date, "to": report_date})
    return data if isinstance(data, list) else []


def earnings_calendar(report_date: str) -> list[dict[str, Any]]:
    data = fmp_get("/earning_calendar", {"from": report_date, "to": report_date})
    return data if isinstance(data, list) else []


def pick_major_earnings(rows: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    def market_cap(row: dict[str, Any]) -> float:
        for key in ("marketCap", "mktCap", "marketcap"):
            value = row.get(key)
            if isinstance(value, (int, float)):
                return float(value)
        return 0.0

    major = [
        row
        for row in rows
        if str(row.get("symbol", "")).upper() in MEGA_CAP_TICKERS or market_cap(row) >= 50_000_000_000
    ]
    if not major:
        major = rows[:limit]
    major.sort(key=market_cap, reverse=True)
    return major[:limit]


def close_location(prior_spy: dict[str, Any]) -> tuple[str, str, float]:
    high = float(prior_spy.get("high") or 0)
    low = float(prior_spy.get("low") or 0)
    close = float(prior_spy.get("close") or 0)
    if high <= low:
        return "in the middle", "Neutral", 0.5
    location = (close - low) / (high - low)
    if location >= 0.75:
        return "near the highs", "Bearish mean-reversion lean", location
    if location <= 0.25:
        return "near the lows", "Bullish mean-reversion lean", location
    return "in the middle", "Neutral", location


def gap_view(gap_pct: float, high_impact_events: int, close_lean: str) -> tuple[str, str]:
    abs_gap = abs(gap_pct)
    if high_impact_events:
        return "Uncertain", "high-impact calendar risk can override the overnight signal"
    if abs_gap >= 0.50:
        return "Fade", "large overnight gaps often mean-revert during the first hour"
    if abs_gap >= 0.20:
        if "Bearish" in close_lean and gap_pct < 0:
            return "Hold", "prior close at highs plus a downside gap favors continuation pressure"
        if "Bullish" in close_lean and gap_pct > 0:
            return "Hold", "prior close at lows plus an upside gap favors continuation squeeze"
        return "Fade cautiously", "moderate gap with no event catalyst favors partial mean reversion"
    return "Hold/neutral", "small gap leaves the opening range more important than the overnight move"


def calendar_historical_note(event: dict[str, Any]) -> str:
    text = " ".join(str(event.get(k, "")) for k in ("event", "title", "name")).lower()
    if "cpi" in text or "pce" in text or "inflation" in text:
        return "Inflation prints often expand SPX range 1.5-2.0x normal."
    if "fomc" in text or "fed" in text or "powell" in text:
        return "Fed events can reprice vol intraday; avoid selling premium directly into the release."
    if "payroll" in text or "nfp" in text or "unemployment" in text:
        return "Labor data frequently sets the morning trend and can double the opening range."
    if "pmi" in text or "ism" in text:
        return "Growth surveys can move rates and cyclicals; expect a moderate range impulse."
    if "retail sales" in text:
        return "Retail sales can shift growth expectations; watch consumer discretionary breadth."
    return "Routine event; usually secondary unless surprise is large."


def resolve_telegram_chat_id() -> str | None:
    for key in ("TELEGRAM_CHAT_ID", "ALTAMIRA_TELEGRAM_CHAT_ID"):
        value = os.environ.get(key)
        if value:
            return value

    if DEFAULT_CHAT_SOURCE.exists():
        text = DEFAULT_CHAT_SOURCE.read_text(encoding="utf-8")
        match = re.search(r'"chatId"\s*:\s*"?=?(-?\d+)"?', text)
        if match:
            return match.group(1)
    return None


def send_telegram(report_path: Path, summary: str) -> dict[str, Any]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = resolve_telegram_chat_id()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    if not chat_id:
        raise RuntimeError("Telegram chat ID is not set and no workspace fallback was found")

    base = f"https://api.telegram.org/bot{token}"
    message = requests.post(
        f"{base}/sendMessage",
        data={"chat_id": chat_id, "text": summary[:3900]},
        timeout=25,
    )
    message.raise_for_status()

    with report_path.open("rb") as handle:
        document = requests.post(
            f"{base}/sendDocument",
            data={
                "chat_id": chat_id,
                "caption": f"Full Jane Street Pre-Market Edge report: {report_path.name}",
            },
            files={"document": (report_path.name, handle, "text/markdown")},
            timeout=45,
        )
    document.raise_for_status()
    return {"message": message.json(), "document": document.json(), "chat_id": chat_id}


def build_report(raw_args: str = "") -> tuple[Path, str]:
    parsed = parse_command_args(raw_args)
    et_now = datetime.now(ZoneInfo("America/New_York"))
    report_date = et_now.strftime("%Y-%m-%d")
    start_date = (et_now.date() - timedelta(days=14)).strftime("%Y-%m-%d")
    OUTPUTS_DIR.mkdir(exist_ok=True)

    quotes = quote_map()
    spx_quote = quotes.get("^GSPC", {})
    spy_quote = quotes.get("SPY", {})
    vix_quote = quotes.get("^VIX", {})

    spy_rows = historical("SPY", start_date, report_date)
    spx_rows = historical("^GSPC", start_date, report_date)
    vix_rows = historical("^VIX", start_date, report_date)
    prior_spy = prior_session(spy_rows, report_date) or {}
    prior_spx = prior_session(spx_rows, report_date) or {}
    prior_vix = prior_session(vix_rows, report_date) or {}
    econ_rows = economic_calendar(report_date)
    earnings_rows = earnings_calendar(report_date)

    prior_spx_close = float(
        prior_spx.get("close")
        or spx_quote.get("previousClose")
        or (float(prior_spy.get("close", 0)) * 10)
        or 0
    )
    current_spx = float(parsed.futures_price or spx_quote.get("preMarket") or spx_quote.get("price") or prior_spx_close)
    current_spy = float(spy_quote.get("preMarket") or spy_quote.get("price") or prior_spy.get("close") or 0)
    current_vix = float(parsed.vix or vix_quote.get("price") or 0)
    prior_vix_close = float(prior_vix.get("close") or vix_quote.get("previousClose") or current_vix)

    gap = current_spx - prior_spx_close
    gap_pct = (gap / prior_spx_close * 100) if prior_spx_close else 0
    expected_move = current_spx * (current_vix / 100) / math.sqrt(252) if current_vix else 0
    expected_pct = (expected_move / current_spx * 100) if current_spx else 0

    close_desc, close_lean, close_pct = close_location(prior_spy)
    high_impact_events = [event for event in econ_rows if classify_event(event)]
    view, view_reason = gap_view(gap_pct, len(high_impact_events), close_lean)

    vix_change = current_vix - prior_vix_close
    vix_change_pct = (vix_change / prior_vix_close * 100) if prior_vix_close else 0
    iv_direction = "higher" if vix_change > 0.10 else "lower" if vix_change < -0.10 else "flat"

    calendar_intensity = "Heavy" if len(high_impact_events) >= 2 else "Moderate" if high_impact_events else "Light"
    calendar_recommendation = (
        "wait until after the event window and use wider strikes"
        if high_impact_events
        else "normal theta entry after the first 15-20 minutes"
    )

    prior_spy_high = float(prior_spy.get("high") or current_spy)
    prior_spy_low = float(prior_spy.get("low") or current_spy)
    prior_spy_close = float(prior_spy.get("close") or current_spy)
    spx_factor = (prior_spx_close / prior_spy_close) if prior_spy_close and prior_spx_close else 10.0
    prior_range_spx = (prior_spy_high - prior_spy_low) * spx_factor

    support_candidates = [
        (current_spx - expected_move, "VIX expected-move lower bound"),
        (float(prior_spx.get("low") or prior_spy_low * spx_factor), "Prior session low"),
        (prior_spx_close, "Prior session close"),
        (round_down(current_spx, 50), "Round-number support"),
    ]
    support_candidates = [(lvl, reason) for lvl, reason in support_candidates if lvl < current_spx + 5]
    support_candidates.sort(key=lambda item: item[0], reverse=True)
    supports = unique_levels(support_candidates)

    resistance_candidates = [
        (current_spx + expected_move, "VIX expected-move upper bound"),
        (float(prior_spx.get("high") or prior_spy_high * spx_factor), "Prior session high"),
        (prior_spx_close, "Prior session close"),
        (round_up(current_spx, 50), "Round-number resistance"),
    ]
    resistance_candidates = [(lvl, reason) for lvl, reason in resistance_candidates if lvl > current_spx - 5]
    resistance_candidates.sort(key=lambda item: item[0])
    resistances = unique_levels(resistance_candidates)

    short_put = round_down(current_spx - max(expected_move, prior_range_spx * 0.45), 5)
    long_put = short_put - 25
    short_call = round_up(current_spx + max(expected_move, prior_range_spx * 0.45), 5)
    long_call = short_call + 25
    size = "1/2 normal size; max 1-2% of account at risk" if high_impact_events else "1x normal size; max 2-3% of account at risk"
    entry = "9:45-10:00 AM ET after the first opening range settles"
    if high_impact_events:
        entry = "after the high-impact event reaction settles; otherwise 9:45-10:15 AM ET"

    opening_strategy = (
        "Stay flat until the event and opening auction clear, then sell premium only outside the realized range."
        if high_impact_events
        else "Define the first 15-minute range, then sell premium outside the VIX expected move."
    )
    if abs(gap_pct) >= 0.50 and not high_impact_events:
        opening_strategy = "Fade the opening gap with defined-risk premium; avoid chasing the first candle."

    iv_crush = (
        "Yes - VIX is above yesterday and event risk can leave inflated premium after the first reaction."
        if iv_direction == "higher" or high_impact_events
        else "No major event-vol overhang; theta edge comes from disciplined range placement, not a large IV crush."
    )

    major_earnings = pick_major_earnings(earnings_rows)
    if major_earnings:
        earnings_lines = []
        for row in major_earnings:
            symbol = str(row.get("symbol", "")).upper() or "N/A"
            time_value = row.get("time") or row.get("date") or "time n/a"
            cap = row.get("marketCap") or row.get("mktCap")
            cap_text = f", market cap ${cap/1_000_000_000:.0f}B" if isinstance(cap, (int, float)) and cap else ""
            potential = "High" if symbol in MEGA_CAP_TICKERS else "Medium"
            earnings_lines.append(
                f"- **{symbol}** ({time_value}{cap_text}): market-moving potential {potential}."
            )
    else:
        earnings_lines = ["- No major index-heavy earnings found in today's FMP earnings calendar."]

    econ_lines = [format_event(event) + f" {calendar_historical_note(event)}" for event in econ_rows[:12]]
    if not econ_lines:
        econ_lines = ["- No major events returned by FMP for today."]

    data_note = "SPX/ES from user input" if parsed.futures_price else "FMP ^GSPC quote used as SPX/ES proxy; use broker futures for exact Globex."
    vix_source = "VIX from user input" if parsed.vix else "VIX from FMP ^VIX quote"
    events_source = "User event notes included" if parsed.events_text else "FMP economic and earnings calendars"

    support_text = "\n".join(f"- **Support {idx}: {level:,.0f}** - {reason}." for idx, (level, reason) in enumerate(supports, 1))
    resistance_text = "\n".join(
        f"- **Resistance {idx}: {level:,.0f}** - {reason}." for idx, (level, reason) in enumerate(resistances, 1)
    )

    report = f"""# Jane Street Pre-Market Edge - {report_date}

## Market assessment

SPX/ES proxy is **{money(current_spx)}** versus prior SPX close **{money(prior_spx_close)}**, implying a gap of **{points(gap)} points ({pct(gap_pct)})**. View: **{view}** - {view_reason}.

Pre-market IV is **{iv_direction}** versus yesterday: VIX **{current_vix:.2f}** vs prior close **{prior_vix_close:.2f}** ({points(vix_change)} pts, {pct(vix_change_pct)}). That keeps premium sale attractive only if strikes are placed outside the expected move and event risk is respected.

Prior session SPY closed **{close_desc}** ({close_pct:.0%} of the range), creating a **{close_lean}** for today's opening read. Calendar intensity is **{calendar_intensity}**; recommendation is to **{calendar_recommendation}**.

## Overnight futures movement

- **Current SPX/ES proxy:** {money(current_spx)} ({data_note})
- **Prior SPX close:** {money(prior_spx_close)}
- **Gap:** {points(gap)} points ({pct(gap_pct)})
- **Hold/Fade view:** **{view}** - {view_reason}.

## Pre-market IV levels

- **Current VIX:** {current_vix:.2f} ({vix_source})
- **Prior VIX close:** {prior_vix_close:.2f}
- **Change:** {points(vix_change)} points ({pct(vix_change_pct)})
- **Implication:** Options are pricing **{iv_direction}** volatility than yesterday; sell premium with defined risk and avoid being short gamma inside the expected range.

## Economic calendar impact

{chr(10).join(econ_lines)}

- **Calendar read:** {calendar_intensity}
- **Trading recommendation:** {calendar_recommendation}.
{f"- **User notes:** {parsed.events_text}" if parsed.events_text else ""}

## Earnings exposure

{chr(10).join(earnings_lines)}

- **Index risk:** Single-name IV spikes are the main risk unless a mega-cap or major bank reports during the session.

## Globex range and expected range

- **Globex range:** From broker/futures platform for exact high/low. FMP does not provide ES Globex high/low in this runner.
- **Prior day SPX-equivalent range proxy:** {prior_range_spx:.1f} points.
- **VIX-based 1-day expected move:** +/-{expected_move:.1f} points (~+/-{expected_pct:.2f}%).

## Opening gap strategy

- **Strategy:** {opening_strategy}
- **Gap handling:** {view} bias; reassess if SPX accepts above Resistance 1 or below Support 1 after 10:00 AM ET.

## IV crush opportunity

- **Opportunity:** {iv_crush}
- **Theta implication:** Favor defined-risk structures over naked short premium because intraday headline risk can expand gamma quickly.

## Previous day's close analysis

- **SPY prior session:** open {prior_spy.get('open', 'n/a')}, high {prior_spy_high:.2f}, low {prior_spy_low:.2f}, close {prior_spy_close:.2f}.
- **Close location:** {close_desc} ({close_pct:.0%} of prior range).
- **Lean:** {close_lean}; use the first opening range to confirm before entering.

## Support and resistance

### Support
{support_text}

### Resistance
{resistance_text}

## Pre-market trade plan

- **Exact strategy:** 0DTE SPX iron condor, defined-risk.
- **Strikes:** Sell {short_put}P / buy {long_put}P; sell {short_call}C / buy {long_call}C.
- **Expiration:** Today (0DTE).
- **Entry time:** {entry}.
- **Position size:** {size}.
- **Risk management:** Take profits at 40-50% of max credit; stop if either short strike is tested or spread marks at 2x entry credit.

## Scenario playbook

- **Bull outcome:** SPX accepts above Resistance 1 ({resistances[0][0]:,.0f}). Close or roll the call side; keep the put side only if delta has collapsed and price remains above VWAP.
- **Bear outcome:** SPX accepts below Support 1 ({supports[0][0]:,.0f}). Close or roll the put side; take profits on the call side and avoid adding short puts into downside momentum.
- **Neutral outcome:** SPX stays between Support 1 and Resistance 1. Hold the iron condor toward 40-50% max profit, then close; do not wait for expiration if gamma expands.

## Data and disclaimer

- **Data sources:** FMP quote (^GSPC, SPY, ^VIX), FMP historical-price-full (SPY, ^GSPC, ^VIX), FMP economic_calendar, FMP earning_calendar.
- **Overnight data:** {data_note}; Globex high/low should be confirmed from a broker or futures platform.
- **Events source:** {events_source}.
- **Disclaimer:** Educational/research only. This is not investment advice, a recommendation, or an instruction to trade. Validate quotes, options chains, margin, and risk limits before placing any order.
"""

    report_path = OUTPUTS_DIR / f"Jane-Street-pre-market-edge-analyzer-{report_date}.md"
    report_path.write_text(report, encoding="utf-8")

    support_summary = ", ".join(f"{level:,.0f}" for level, _ in supports)
    resistance_summary = ", ".join(f"{level:,.0f}" for level, _ in resistances)
    summary = (
        f"Jane Street Pre-Market Edge - {report_date}\n\n"
        f"Gap: {points(gap)} pts ({pct(gap_pct)}). View: {view} - {view_reason}.\n"
        f"VIX: {current_vix:.2f} vs {prior_vix_close:.2f} yesterday ({iv_direction}).\n"
        f"Event risk: {calendar_intensity}; {calendar_recommendation}.\n"
        f"Strategy: 0DTE SPX IC {short_put}/{long_put}P x {short_call}/{long_call}C, entry {entry}, size {size}.\n"
        f"Support: {support_summary}. Resistance: {resistance_summary}.\n"
        f"Report: {report_path}"
    )
    return report_path, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("args", nargs="*", help="Optional slash-command arguments")
    parser.add_argument("--telegram", action="store_true", help="Send summary and report to Telegram")
    parser.add_argument("--no-telegram", action="store_true", help="Do not send Telegram")
    ns = parser.parse_args(argv)

    raw_args = " ".join(ns.args)
    report_path, summary = build_report(raw_args)
    print(summary)
    print(f"Wrote {report_path}")

    if ns.telegram and not ns.no_telegram:
        result = send_telegram(report_path, summary)
        message_id = result["message"].get("result", {}).get("message_id")
        document_id = result["document"].get("result", {}).get("message_id")
        print(f"Telegram sent to chat {result['chat_id']} (message {message_id}, document {document_id})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
