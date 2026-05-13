#!/usr/bin/env python3
"""
Generate daily trade ideas from the repository portfolio and watchlist context.

The script is intentionally self-contained:
- Reads context/portfolio-details.md and context/watchlist.md.
- Optionally enriches candidates with FMP quotes when FMP_API_KEY is set.
- Writes outputs/trade-idea-generator-{DATE}.md.
- Sends a concise summary to Telegram when --send is provided.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python <3.9 fallback
    ZoneInfo = None  # type: ignore


WORKSPACE = Path(__file__).resolve().parent.parent
CONTEXT = WORKSPACE / "context"
OUTPUTS = WORKSPACE / "outputs"
PORTFOLIO_MD = CONTEXT / "portfolio-details.md"
WATCHLIST_MD = CONTEXT / "watchlist.md"
FALLBACK_TELEGRAM_WORKFLOW = OUTPUTS / "csp-daily-scan-fixed.json"
FMP_BASE = "https://financialmodelingprep.com/api/v3"


@dataclass
class Holding:
    symbol: str
    qty: float
    avg_price: Optional[float]
    current: Optional[float]
    market_value: Optional[float]
    weight: Optional[float]


@dataclass
class WatchlistItem:
    ticker: str
    score: Optional[float]
    grade: str
    company: str
    status: str


@dataclass
class OptionPosition:
    ticker: str
    strike: float
    option_type: str
    expiration: date
    credit: Optional[float]
    current: Optional[float]
    contracts: int


def today_et() -> date:
    if ZoneInfo is None:
        return date.today()
    return datetime.now(ZoneInfo("America/New_York")).date()


def clean_cell(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("**", "").replace("⭐", "")).strip()


def parse_float(value: str) -> Optional[float]:
    raw = clean_cell(value)
    if raw in {"", "-", "—", "N/A"}:
        return None
    raw = raw.replace("$", "").replace(",", "").replace("%", "").replace("+", "")
    raw = raw.split(" ")[0]
    raw = raw.strip("()")
    try:
        return float(raw)
    except ValueError:
        return None


def parse_int(value: str) -> int:
    num = parse_float(value)
    return int(num or 0)


def split_table_row(line: str) -> List[str]:
    return [clean_cell(cell) for cell in line.strip().strip("|").split("|")]


def table_after_heading(text: str, heading: str) -> List[List[str]]:
    lines = text.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.strip().lower() == heading.lower():
            start = idx + 1
            break
    if start is None:
        return []

    rows: List[List[str]] = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("## ") and rows:
            break
        if not stripped.startswith("|"):
            continue
        if re.match(r"^\|\s*-+\s*(\|\s*-+\s*)+\|?$", stripped):
            continue
        rows.append(split_table_row(stripped))
    if len(rows) <= 1:
        return []
    return rows


def load_holdings() -> Tuple[List[Holding], Optional[float], Optional[float]]:
    text = PORTFOLIO_MD.read_text(encoding="utf-8")
    portfolio_value = None
    cash_pct = None

    value_match = re.search(r"\*\*Total MKT VALUE\*\*\s*\|\s*\$?([\d,]+)", text)
    if value_match:
        portfolio_value = parse_float(value_match.group(1))
    cash_match = re.search(r"\|\s*Cash %\s*\|\s*([\d.]+)", text)
    if cash_match:
        cash_pct = parse_float(cash_match.group(1))

    rows = table_after_heading(text, "## Current Positions (from app dashboard)")
    holdings: List[Holding] = []
    for row in rows[1:]:
        if len(row) < 9 or row[0].upper() in {"TOTALS", ""}:
            continue
        symbol = row[0].upper()
        if symbol == "SYMBOL":
            continue
        holdings.append(
            Holding(
                symbol=symbol,
                qty=parse_float(row[1]) or 0.0,
                avg_price=parse_float(row[2]),
                current=parse_float(row[3]),
                market_value=parse_float(row[4]),
                weight=parse_float(row[8]),
            )
        )
    return holdings, portfolio_value, cash_pct


def load_options() -> List[OptionPosition]:
    text = PORTFOLIO_MD.read_text(encoding="utf-8")
    rows = table_after_heading(text, "## Options / Short Premium Positions")
    positions: List[OptionPosition] = []
    for row in rows[1:]:
        if len(row) < 7 or row[0].upper() == "TICKER":
            continue
        exp = datetime.strptime(row[3], "%Y-%m-%d").date()
        strike = parse_float(row[1])
        if strike is None:
            continue
        positions.append(
            OptionPosition(
                ticker=row[0].upper(),
                strike=strike,
                option_type=row[2].title(),
                expiration=exp,
                credit=parse_float(row[4]),
                current=parse_float(row[5]),
                contracts=parse_int(row[6]),
            )
        )
    return positions


def load_watchlist() -> List[WatchlistItem]:
    text = WATCHLIST_MD.read_text(encoding="utf-8")
    rows = table_after_heading(text, "## Watchlist Tickers")
    items: List[WatchlistItem] = []
    for row in rows[1:]:
        if len(row) < 5 or row[0].upper() == "TICKER":
            continue
        items.append(
            WatchlistItem(
                ticker=row[0].upper(),
                score=parse_float(row[1]),
                grade=clean_cell(row[2]),
                company=clean_cell(row[3]),
                status=clean_cell(row[4]),
            )
        )
    return items


def http_json(url: str, timeout: int = 15) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "AltamiraTradeIdeaGenerator/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_quotes(tickers: Iterable[str], api_key: Optional[str]) -> Tuple[Dict[str, Dict[str, Any]], str]:
    if not api_key:
        return {}, "FMP_API_KEY not set; using repository snapshot prices only."
    clean = sorted({t.upper() for t in tickers if t and t.upper() not in {"FFOLX"}})
    if not clean:
        return {}, "No tickers to quote."

    quotes: Dict[str, Dict[str, Any]] = {}
    errors: List[str] = []
    for idx in range(0, len(clean), 35):
        batch = clean[idx : idx + 35]
        symbols = urllib.parse.quote(",".join(batch), safe=",")
        url = f"{FMP_BASE}/quote/{symbols}?apikey={urllib.parse.quote(api_key)}"
        try:
            data = http_json(url)
            if isinstance(data, list):
                for item in data:
                    symbol = str(item.get("symbol", "")).upper()
                    if symbol:
                        quotes[symbol] = item
        except Exception as exc:
            errors.append(f"{','.join(batch)}: {exc}")
    note = f"FMP quotes loaded for {len(quotes)} symbols."
    if errors:
        note += " Quote errors: " + "; ".join(errors[:2])
    return quotes, note


def quote_price(symbol: str, quotes: Dict[str, Dict[str, Any]], holdings_by_symbol: Dict[str, Holding]) -> Optional[float]:
    q = quotes.get(symbol.upper())
    if q and q.get("price") is not None:
        try:
            return float(q["price"])
        except (TypeError, ValueError):
            pass
    holding = holdings_by_symbol.get(symbol.upper())
    return holding.current if holding else None


def fetch_vix(api_key: Optional[str]) -> Tuple[Optional[float], str]:
    if not api_key:
        return None, "VIX live quote skipped; FMP_API_KEY not set."
    url = f"{FMP_BASE}/quote/%5EVIX?apikey={urllib.parse.quote(api_key)}"
    try:
        data = http_json(url)
        if isinstance(data, list) and data:
            return float(data[0].get("price")), "Live VIX from FMP."
    except Exception as exc:
        return None, f"VIX fetch failed: {exc}"
    return None, "VIX fetch returned no data."


def vix_regime(vix: Optional[float]) -> Tuple[str, str, float]:
    if vix is None:
        return "UNKNOWN", "Use normal sizing until live VIX is confirmed.", 1.0
    if vix < 15:
        return "LOW", "Premium is cheaper; prefer smaller entries and covered calls over aggressive CSPs.", 0.75
    if vix < 25:
        return "NORMAL", "Balanced premium-selling environment; standard sizing is acceptable.", 1.0
    if vix < 35:
        return "ELEVATED", "Prefer defined-risk spreads and reduce new short-premium size.", 0.5
    return "CRISIS", "Capital preservation first; spreads only and minimal size.", 0.25


def next_trade_expiration(as_of: date) -> date:
    start = as_of + timedelta(days=30)
    end = as_of + timedelta(days=50)
    cursor = start
    while cursor <= end:
        if cursor.weekday() == 4:
            return cursor
        cursor += timedelta(days=1)
    return as_of + timedelta(days=45)


def strike_increment(price: float) -> float:
    if price < 50:
        return 1.0
    if price < 150:
        return 2.5
    if price < 500:
        return 5.0
    return 10.0


def rounded_strike(price: Optional[float], pct: float, direction: str) -> str:
    if price is None or price <= 0:
        return "manual chain lookup"
    raw = price * pct
    inc = strike_increment(price)
    if direction == "up":
        val = math.ceil(raw / inc) * inc
    else:
        val = math.floor(raw / inc) * inc
    if inc == 1.0:
        return f"${val:.0f}"
    if val == int(val):
        return f"${val:.0f}"
    return f"${val:.1f}"


def momentum_score(q: Optional[Dict[str, Any]]) -> Tuple[int, str]:
    if not q:
        return 0, "no live momentum data"
    price = q.get("price")
    ma50 = q.get("priceAvg50")
    ma200 = q.get("priceAvg200")
    change = q.get("changesPercentage")
    score = 0
    notes: List[str] = []
    try:
        if price and ma50:
            if float(price) > float(ma50):
                score += 4
                notes.append("above 50d")
            else:
                score -= 3
                notes.append("below 50d")
        if price and ma200:
            if float(price) > float(ma200):
                score += 4
                notes.append("above 200d")
            else:
                score -= 4
                notes.append("below 200d")
        if change is not None:
            chg = float(change)
            if -2.5 <= chg <= 0.5:
                score += 2
                notes.append("orderly pullback")
            elif chg > 3:
                score -= 2
                notes.append("avoid chasing")
    except (TypeError, ValueError):
        pass
    return score, ", ".join(notes) if notes else "neutral momentum"


def build_watchlist_ideas(
    watchlist: List[WatchlistItem],
    holdings_by_symbol: Dict[str, Holding],
    quotes: Dict[str, Dict[str, Any]],
    sizing_factor: float,
    as_of: date,
) -> List[Dict[str, Any]]:
    exp = next_trade_expiration(as_of)
    ideas: List[Dict[str, Any]] = []
    for item in watchlist:
        status = item.status.lower()
        if "avoid" in status or (item.score is not None and item.score < 55):
            continue
        holding_weight = holdings_by_symbol.get(item.ticker).weight if item.ticker in holdings_by_symbol else 0
        if holding_weight and holding_weight >= 5:
            continue
        q = quotes.get(item.ticker)
        price = quote_price(item.ticker, quotes, holdings_by_symbol)
        mom, mom_note = momentum_score(q)
        base = item.score or 50
        score = base + mom + (3 if "top candidate" in status.lower() else 0)
        if holding_weight and holding_weight > 0:
            score -= 2
        strike = rounded_strike(price, 0.90, "down")
        strategy = "Cash-secured put" if sizing_factor >= 0.75 else "Bull put spread"
        ideas.append(
            {
                "ticker": item.ticker,
                "strategy": strategy,
                "score": score,
                "action": (
                    f"{strategy} around {strike}, {exp.isoformat()} expiry; "
                    "target 0.20-0.30 delta and avoid entering if earnings fall before expiration."
                ),
                "rationale": f"{item.grade} watchlist score {item.score or 'N/A'}; {mom_note}.",
                "price": price,
                "category": "watchlist",
            }
        )
    ideas.sort(key=lambda x: x["score"], reverse=True)
    return ideas[:6]


def build_covered_call_ideas(
    holdings: List[Holding],
    quotes: Dict[str, Dict[str, Any]],
    sizing_factor: float,
    as_of: date,
) -> List[Dict[str, Any]]:
    exp = next_trade_expiration(as_of)
    ideas: List[Dict[str, Any]] = []
    for holding in holdings:
        if holding.symbol in {"FFOLX"} or not holding.weight or holding.weight < 10:
            continue
        price = quote_price(holding.symbol, quotes, {holding.symbol: holding})
        call_pct = 1.08 if sizing_factor >= 0.75 else 1.05
        strike = rounded_strike(price, call_pct, "up")
        q = quotes.get(holding.symbol)
        mom, mom_note = momentum_score(q)
        score = 70 + min(holding.weight or 0, 20) - max(mom, 0) * 0.5
        ideas.append(
            {
                "ticker": holding.symbol,
                "strategy": "Covered call / trim discipline",
                "score": score,
                "action": (
                    f"Sell 0.15-0.25 delta covered calls around {strike}, {exp.isoformat()} expiry, "
                    "or trim shares if concentration needs immediate reduction."
                ),
                "rationale": f"Position weight {holding.weight:.1f}% is above concentration guardrail; {mom_note}.",
                "price": price,
                "category": "portfolio-risk",
            }
        )
    ideas.sort(key=lambda x: x["score"], reverse=True)
    return ideas[:4]


def build_option_risk_ideas(
    options: List[OptionPosition],
    quotes: Dict[str, Dict[str, Any]],
    holdings_by_symbol: Dict[str, Holding],
    as_of: date,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    ideas: List[Dict[str, Any]] = []
    stale: List[str] = []
    for pos in options:
        dte = (pos.expiration - as_of).days
        price = quote_price(pos.ticker, quotes, holdings_by_symbol)
        if dte < 0:
            stale.append(f"{pos.ticker} {pos.strike:.0f}{pos.option_type[0]} expired {pos.expiration.isoformat()}")
            continue
        if dte > 7:
            continue

        threatened = bool(price is not None and pos.option_type == "Put" and price <= pos.strike * 1.03)
        profit_close = bool(pos.credit is not None and pos.current is not None and pos.current <= pos.credit * 0.5)
        if threatened:
            action = "Close or roll before expiration; short strike is close to/above the underlying."
            score = 95
        elif profit_close:
            action = "Close to lock 50%+ of max profit and release buying power."
            score = 90
        else:
            action = "Review for close/roll; expiration is within one week and assignment risk is event-sensitive."
            score = 85
        ideas.append(
            {
                "ticker": pos.ticker,
                "strategy": f"Manage short {pos.option_type.lower()}",
                "score": score,
                "action": (
                    f"{action} Position: {pos.contracts}x {pos.ticker} {pos.strike:.0f}{pos.option_type[0]} "
                    f"exp {pos.expiration.isoformat()}."
                ),
                "rationale": f"{dte} DTE; underlying {fmt_money(price)} vs strike ${pos.strike:.0f}.",
                "price": price,
                "category": "options-risk",
            }
        )
    ideas.sort(key=lambda x: x["score"], reverse=True)
    return ideas, stale


def fmt_money(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    return f"${value:,.2f}"


def fmt_pct(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    return f"{value:.1f}%"


def resolve_telegram_chat_id(cli_chat_id: Optional[str]) -> Tuple[Optional[str], str]:
    if cli_chat_id:
        return cli_chat_id, "CLI --telegram-chat-id"
    for env_name in ("TELEGRAM_CHAT_ID", "TELEGRAM_CHANNEL_ID"):
        value = os.environ.get(env_name)
        if value:
            return value, env_name

    if FALLBACK_TELEGRAM_WORKFLOW.exists():
        try:
            data = json.loads(FALLBACK_TELEGRAM_WORKFLOW.read_text(encoding="utf-8"))
            for node in data.get("nodes", []):
                params = node.get("parameters", {})
                chat_id = params.get("chatId")
                if chat_id:
                    return str(chat_id).lstrip("="), f"{FALLBACK_TELEGRAM_WORKFLOW.name} fallback"
        except Exception:
            pass
    return None, "not configured"


def telegram_chunks(text: str, max_chars: int = 3800) -> List[str]:
    if len(text) <= max_chars:
        return [text]
    chunks: List[str] = []
    remaining = text
    while remaining:
        if len(remaining) <= max_chars:
            chunks.append(remaining)
            break
        split_at = remaining.rfind("\n", 0, max_chars)
        if split_at < max_chars * 0.5:
            split_at = max_chars
        chunks.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].strip()
    return chunks


def send_telegram(text: str, token: str, chat_id: str) -> Tuple[bool, str]:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    chunks = telegram_chunks(text)
    for idx, chunk in enumerate(chunks, start=1):
        payload = urllib.parse.urlencode(
            {
                "chat_id": chat_id,
                "text": chunk if len(chunks) == 1 else f"{chunk}\n\n({idx}/{len(chunks)})",
                "disable_web_page_preview": "true",
            }
        ).encode("utf-8")
        req = urllib.request.Request(url, data=payload, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                if not body.get("ok"):
                    return False, str(body)
        except Exception as exc:
            return False, str(exc)
        time.sleep(0.4)
    return True, f"sent {len(chunks)} Telegram message(s)"


def format_report(
    as_of: date,
    holdings: List[Holding],
    watchlist: List[WatchlistItem],
    ideas: List[Dict[str, Any]],
    stale_options: List[str],
    portfolio_value: Optional[float],
    cash_pct: Optional[float],
    vix: Optional[float],
    regime: str,
    regime_note: str,
    quote_note: str,
    vix_note: str,
) -> str:
    top_holdings = sorted([h for h in holdings if h.weight is not None], key=lambda h: h.weight or 0, reverse=True)[:6]
    top_watch = sorted([w for w in watchlist if w.score is not None], key=lambda w: w.score or 0, reverse=True)[:6]

    lines: List[str] = []
    lines.append(f"# Trade Idea Generator - {as_of.isoformat()}")
    lines.append("")
    lines.append("> Educational trade research only, not financial advice. Verify prices, chains, earnings dates, and risk limits before placing any trade.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Portfolio value: {fmt_money(portfolio_value)}")
    lines.append(f"- Cash: {fmt_pct(cash_pct)}")
    lines.append(f"- VIX regime: {regime} ({fmt_money(vix).replace('$', '') if vix is not None else 'N/A'})")
    lines.append(f"- Regime note: {regime_note}")
    lines.append(f"- Data note: {quote_note} {vix_note}")
    lines.append("")
    lines.append("## Top Trade Ideas")
    lines.append("")
    lines.append("| Rank | Ticker | Strategy | Action | Rationale |")
    lines.append("|------|--------|----------|--------|-----------|")
    for idx, idea in enumerate(ideas[:8], start=1):
        lines.append(
            f"| {idx} | {idea['ticker']} | {idea['strategy']} | {idea['action']} | {idea['rationale']} |"
        )
    if not ideas:
        lines.append("| - | - | No actionable idea | Review data inputs | No candidates passed filters. |")
    lines.append("")
    lines.append("## Portfolio Concentration Snapshot")
    lines.append("")
    lines.append("| Ticker | Weight | Current | Note |")
    lines.append("|--------|--------|---------|------|")
    for holding in top_holdings:
        note = "Above 10%; prioritize trims/covered calls over adds." if (holding.weight or 0) >= 10 else "Within top holdings."
        lines.append(f"| {holding.symbol} | {fmt_pct(holding.weight)} | {fmt_money(holding.current)} | {note} |")
    lines.append("")
    lines.append("## Watchlist Priority Snapshot")
    lines.append("")
    lines.append("| Ticker | Score | Grade | Status | Company |")
    lines.append("|--------|-------|-------|--------|---------|")
    for item in top_watch:
        lines.append(f"| {item.ticker} | {item.score:.1f} | {item.grade} | {item.status} | {item.company} |")
    lines.append("")
    lines.append("## Data Hygiene / Risk Notes")
    lines.append("")
    if stale_options:
        lines.append("- Expired option rows found in context; refresh `context/portfolio-details.md` before sizing new risk:")
        for item in stale_options:
            lines.append(f"  - {item}")
    else:
        lines.append("- No expired option rows detected in the current options table.")
    lines.append("- Do not sell new short premium through unplanned earnings.")
    lines.append("- Respect max position, options allocation, and cash-reserve limits from the risk framework.")
    lines.append("")
    return "\n".join(lines)


def format_telegram_message(
    as_of: date,
    ideas: List[Dict[str, Any]],
    stale_options: List[str],
    portfolio_value: Optional[float],
    cash_pct: Optional[float],
    vix: Optional[float],
    regime: str,
    output_path: Path,
) -> str:
    lines = [
        f"Altamira Trade Ideas - {as_of.isoformat()}",
        f"Portfolio: {fmt_money(portfolio_value)} | Cash: {fmt_pct(cash_pct)} | VIX: {fmt_money(vix).replace('$', '') if vix is not None else 'N/A'} ({regime})",
        "",
        "Top actions:",
    ]
    for idx, idea in enumerate(ideas[:5], start=1):
        lines.append(f"{idx}. {idea['ticker']} - {idea['strategy']}: {idea['action']}")
        lines.append(f"   Why: {idea['rationale']}")
    if stale_options:
        lines.append("")
        lines.append("Context refresh needed: expired option rows detected (" + "; ".join(stale_options[:3]) + ").")
    lines.append("")
    lines.append(f"Report: {output_path.relative_to(WORKSPACE)}")
    lines.append("Educational only; verify live chains, earnings, and risk limits before trading.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate portfolio/watchlist trade ideas and optionally send to Telegram.")
    parser.add_argument("--send", action="store_true", help="Send the generated summary to Telegram.")
    parser.add_argument("--telegram-chat-id", help="Telegram chat/channel ID override.")
    parser.add_argument("--date", help="Override run date (YYYY-MM-DD).")
    parser.add_argument("--out", help="Output markdown path override.")
    args = parser.parse_args()

    as_of = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else today_et()
    output_path = Path(args.out) if args.out else OUTPUTS / f"trade-idea-generator-{as_of.isoformat()}.md"
    if not output_path.is_absolute():
        output_path = WORKSPACE / output_path

    holdings, portfolio_value, cash_pct = load_holdings()
    options = load_options()
    watchlist = load_watchlist()
    holdings_by_symbol = {h.symbol: h for h in holdings}

    universe = {h.symbol for h in holdings} | {w.ticker for w in watchlist} | {p.ticker for p in options}
    api_key = os.environ.get("FMP_API_KEY")
    quotes, quote_note = fetch_quotes(universe, api_key)
    vix, vix_note = fetch_vix(api_key)
    regime, regime_note, sizing_factor = vix_regime(vix)

    option_ideas, stale_options = build_option_risk_ideas(options, quotes, holdings_by_symbol, as_of)
    watchlist_ideas = build_watchlist_ideas(watchlist, holdings_by_symbol, quotes, sizing_factor, as_of)
    covered_call_ideas = build_covered_call_ideas(holdings, quotes, sizing_factor, as_of)
    ideas = sorted(option_ideas + watchlist_ideas + covered_call_ideas, key=lambda x: x["score"], reverse=True)

    report = format_report(
        as_of=as_of,
        holdings=holdings,
        watchlist=watchlist,
        ideas=ideas,
        stale_options=stale_options,
        portfolio_value=portfolio_value,
        cash_pct=cash_pct,
        vix=vix,
        regime=regime,
        regime_note=regime_note,
        quote_note=quote_note,
        vix_note=vix_note,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")

    telegram_status = "skipped"
    if args.send:
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id, chat_source = resolve_telegram_chat_id(args.telegram_chat_id)
        if not token:
            telegram_status = "failed: TELEGRAM_BOT_TOKEN not set"
            print(telegram_status, file=sys.stderr)
            return 2
        if not chat_id:
            telegram_status = "failed: Telegram chat ID not configured"
            print(telegram_status, file=sys.stderr)
            return 2
        message = format_telegram_message(as_of, ideas, stale_options, portfolio_value, cash_pct, vix, regime, output_path)
        ok, detail = send_telegram(message, token, chat_id)
        telegram_status = f"{detail} via {chat_source}" if ok else f"failed: {detail}"
        if not ok:
            print(telegram_status, file=sys.stderr)
            return 2

    final_report = report + f"\n## Delivery\n\n- Telegram: {telegram_status}\n"
    output_path.write_text(final_report, encoding="utf-8")
    print(f"Wrote {output_path.relative_to(WORKSPACE)}")
    print(f"Telegram: {telegram_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
