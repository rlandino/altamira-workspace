#!/usr/bin/env python3
"""Generate Altamira trade ideas from portfolio and watchlist context.

The script reads repository context files, pulls live market/options data when
API credentials are available, writes a markdown report, and can send a concise
summary to Telegram.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:  # pragma: no cover - runtime dependency guard
    print("Install requests: pip install requests", file=sys.stderr)
    sys.exit(1)


WORKSPACE = Path(__file__).resolve().parent.parent
CONTEXT_DIR = WORKSPACE / "context"
OUTPUTS_DIR = WORKSPACE / "outputs"
COMMANDS_DIR = WORKSPACE / ".claude" / "commands"
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"
MASSIVE_BASE_URL = "https://api.massive.com/v3"
TELEGRAM_BASE_URL = "https://api.telegram.org"


@dataclass
class Position:
    symbol: str
    qty: float
    avg_price: float
    current: float
    market_value: float
    cost_basis: float
    pnl_pct: float
    day_chg_pct: float
    weight: float


@dataclass
class WatchlistItem:
    ticker: str
    score: float | None
    grade: str | None
    company: str
    status: str


@dataclass
class OptionCandidate:
    ticker: str
    strategy: str
    expiration: str
    dte: int
    strike: float
    bid: float
    ask: float
    delta: float | None
    theta: float | None
    iv: float | None
    open_interest: int
    volume: int
    spread_pct: float | None
    annualized_yield: float | None
    long_strike: float | None = None
    net_credit: float | None = None
    max_loss: float | None = None
    breakeven: float | None = None


@dataclass
class TradeIdea:
    rank: int
    ticker: str
    action: str
    rationale: str
    option: OptionCandidate | None
    confidence: int
    risk: str


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _strip_money(value: str) -> float:
    value = value.replace("$", "").replace(",", "").strip()
    if not value or value == "-":
        return 0.0
    return float(value)


def _strip_percent(value: str) -> float:
    match = re.search(r"([+-]?\d+(?:\.\d+)?)%", value.replace(",", ""))
    return float(match.group(1)) if match else 0.0


def _split_markdown_row(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def parse_positions() -> list[Position]:
    """Parse current equity positions from context/portfolio-details.md."""
    text = _read_text(CONTEXT_DIR / "portfolio-details.md")
    positions: list[Position] = []
    in_table = False
    for line in text.splitlines():
        if line.startswith("| SYMBOL |"):
            in_table = True
            continue
        if not in_table:
            continue
        if line.startswith("|--------"):
            continue
        if not line.startswith("|"):
            if positions:
                break
            continue
        cells = _split_markdown_row(line)
        if len(cells) < 9:
            continue
        try:
            positions.append(
                Position(
                    symbol=cells[0].upper(),
                    qty=float(cells[1].replace(",", "")),
                    avg_price=_strip_money(cells[2]),
                    current=_strip_money(cells[3]),
                    market_value=_strip_money(cells[4]),
                    cost_basis=_strip_money(cells[5]),
                    pnl_pct=_strip_percent(cells[6]),
                    day_chg_pct=_strip_percent(cells[7]),
                    weight=_strip_percent(cells[8]),
                )
            )
        except ValueError:
            continue
    return positions


def parse_watchlist() -> list[WatchlistItem]:
    """Parse watchlist entries from context/watchlist.md."""
    text = _read_text(CONTEXT_DIR / "watchlist.md")
    items: list[WatchlistItem] = []
    in_table = False
    for line in text.splitlines():
        if line.startswith("| Ticker |"):
            in_table = True
            continue
        if not in_table:
            continue
        if line.startswith("|--------"):
            continue
        if not line.startswith("|"):
            if items:
                break
            continue
        cells = _split_markdown_row(line)
        if len(cells) < 5:
            continue
        score = None
        if cells[1] not in {"-", "--", "—"}:
            try:
                score = float(cells[1])
            except ValueError:
                score = None
        grade = re.sub(r"[*]", "", cells[2]).strip()
        if grade in {"-", "--", "—"}:
            grade = None
        items.append(
            WatchlistItem(
                ticker=cells[0].upper(),
                score=score,
                grade=grade,
                company=cells[3],
                status=cells[4],
            )
        )
    return items


def read_snapshot_date() -> str:
    text = _read_text(CONTEXT_DIR / "portfolio-details.md")
    match = re.search(r"\| Date \| ([0-9-]+) \|", text)
    return match.group(1) if match else "unknown"


def read_existing_options(today: date) -> list[str]:
    text = _read_text(CONTEXT_DIR / "options-positions.md")
    notes: list[str] = []
    in_table = False
    for line in text.splitlines():
        if line.startswith("| Ticker |"):
            in_table = True
            continue
        if not in_table:
            continue
        if line.startswith("|--------"):
            continue
        if not line.startswith("|"):
            if notes:
                break
            continue
        cells = _split_markdown_row(line)
        if len(cells) < 7:
            continue
        ticker, strike, opt_type, exp, credit, current, contracts = cells[:7]
        try:
            exp_date = datetime.strptime(exp, "%Y-%m-%d").date()
            credit_f = float(credit)
            current_f = float(current)
        except ValueError:
            continue
        if exp_date < today:
            notes.append(f"{ticker} {strike}{opt_type[0].upper()} expired {exp}: reconcile broker/context.")
        elif current_f >= credit_f * 2:
            notes.append(f"{ticker} {strike}{opt_type[0].upper()} {exp}: at/above 2x credit stop; review roll/close.")
        else:
            notes.append(f"{ticker} {strike}{opt_type[0].upper()} {exp}: monitor; current {current_f:.2f} vs credit {credit_f:.2f}.")
    return notes


def get_fmp_key() -> str | None:
    if os.environ.get("FMP_API_KEY"):
        return os.environ["FMP_API_KEY"]
    market_api_text = _read_text(WORKSPACE / "scripts" / "market_data_api.py")
    match = re.search(r'DEFAULT_KEY\s*=\s*os\.environ\.get\("FMP_API_KEY",\s*"([^"]+)"\)', market_api_text)
    if match:
        return match.group(1)
    command_text = _read_text(COMMANDS_DIR / "options-scan.md")
    match = re.search(r"FMP API\*\* \(key: `([^`]+)`\)", command_text)
    if match:
        return match.group(1)
    try:
        sys.path.insert(0, str(WORKSPACE))
        from scripts.market_data_api import DEFAULT_KEY  # type: ignore

        return DEFAULT_KEY
    except Exception:
        return None


def get_massive_key() -> str | None:
    if os.environ.get("MASSIVE_API_KEY"):
        return os.environ["MASSIVE_API_KEY"]
    command_text = _read_text(COMMANDS_DIR / "options-scan.md")
    match = re.search(r"Massive\.com API\*\* \(key: `([^`]+)`\)", command_text)
    if match:
        return match.group(1)
    return None


def fetch_json(url: str, params: dict[str, Any] | None = None, timeout: int = 20) -> Any:
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def fetch_quotes(symbols: list[str], fmp_key: str | None) -> dict[str, dict[str, Any]]:
    if not fmp_key:
        return {}
    quotes: dict[str, dict[str, Any]] = {}
    clean = [s for s in symbols if s and s != "FFOLX"]
    for idx in range(0, len(clean), 40):
        batch = clean[idx : idx + 40]
        path_symbols = ",".join(batch)
        try:
            data = fetch_json(f"{FMP_BASE_URL}/quote/{path_symbols}", {"apikey": fmp_key})
        except Exception as exc:
            print(f"warning: quote fetch failed for {path_symbols}: {exc}", file=sys.stderr)
            continue
        if isinstance(data, list):
            for row in data:
                symbol = str(row.get("symbol", "")).upper()
                if symbol:
                    quotes[symbol] = row
    return quotes


def fetch_options(ticker: str, massive_key: str | None, today: date) -> list[dict[str, Any]]:
    if not massive_key:
        return []
    start = today + timedelta(days=20)
    end = today + timedelta(days=60)
    params = {
        "apiKey": massive_key,
        "limit": 250,
        "expiration_date.gte": start.isoformat(),
        "expiration_date.lte": end.isoformat(),
    }
    try:
        data = fetch_json(f"{MASSIVE_BASE_URL}/snapshot/options/{ticker}", params)
    except Exception as exc:
        print(f"warning: options fetch failed for {ticker}: {exc}", file=sys.stderr)
        return []
    results = data.get("results", []) if isinstance(data, dict) else []
    return results if isinstance(results, list) else []


def _as_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        value_f = float(value)
        if math.isnan(value_f) or math.isinf(value_f):
            return None
        return value_f
    except (TypeError, ValueError):
        return None


def _option_candidate(row: dict[str, Any], ticker: str, strategy: str, today: date) -> OptionCandidate | None:
    details = row.get("details") or {}
    greeks = row.get("greeks") or {}
    quote = row.get("last_quote") or {}
    day = row.get("day") or {}
    exp = details.get("expiration_date")
    strike = _as_float(details.get("strike_price"))
    if not exp or strike is None:
        return None
    try:
        dte = (datetime.strptime(exp, "%Y-%m-%d").date() - today).days
    except ValueError:
        return None
    bid = _as_float(quote.get("bid")) or _as_float(day.get("close")) or 0.0
    ask = _as_float(quote.get("ask")) or 0.0
    if bid <= 0:
        return None
    mid = (bid + ask) / 2 if ask > bid else bid
    spread_pct = ((ask - bid) / mid * 100) if ask > bid and mid else None
    oi = int(_as_float(row.get("open_interest")) or 0)
    volume = int(_as_float(day.get("volume")) or 0)
    annualized = (bid / strike) * (365 / dte) * 100 if strike > 0 and dte > 0 else None
    return OptionCandidate(
        ticker=ticker,
        strategy=strategy,
        expiration=exp,
        dte=dte,
        strike=strike,
        bid=bid,
        ask=ask,
        delta=_as_float(greeks.get("delta")),
        theta=_as_float(greeks.get("theta")),
        iv=_as_float(row.get("implied_volatility")),
        open_interest=oi,
        volume=volume,
        spread_pct=spread_pct,
        annualized_yield=annualized,
        breakeven=strike - bid if strategy == "CSP" else None,
    )


def select_csp(ticker: str, rows: list[dict[str, Any]], today: date) -> OptionCandidate | None:
    candidates: list[OptionCandidate] = []
    for row in rows:
        details = row.get("details") or {}
        if details.get("contract_type") != "put":
            continue
        candidate = _option_candidate(row, ticker, "CSP", today)
        if not candidate or not 25 <= candidate.dte <= 55:
            continue
        delta = candidate.delta
        if delta is not None and not -0.32 <= delta <= -0.15:
            continue
        if candidate.open_interest < 25:
            continue
        if candidate.spread_pct is not None and candidate.spread_pct > 30:
            continue
        candidates.append(candidate)
    return max(
        candidates,
        key=lambda c: (
            c.annualized_yield or 0,
            c.open_interest,
            -(abs((c.delta or -0.23) + 0.23)),
        ),
        default=None,
    )


def select_covered_call(ticker: str, rows: list[dict[str, Any]], today: date) -> OptionCandidate | None:
    candidates: list[OptionCandidate] = []
    for row in rows:
        details = row.get("details") or {}
        if details.get("contract_type") != "call":
            continue
        candidate = _option_candidate(row, ticker, "Covered Call", today)
        if not candidate or not 25 <= candidate.dte <= 55:
            continue
        delta = candidate.delta
        if delta is not None and not 0.15 <= delta <= 0.35:
            continue
        if candidate.open_interest < 25:
            continue
        if candidate.spread_pct is not None and candidate.spread_pct > 30:
            continue
        candidates.append(candidate)
    return max(
        candidates,
        key=lambda c: (
            c.annualized_yield or 0,
            c.open_interest,
            -(abs((c.delta or 0.25) - 0.25)),
        ),
        default=None,
    )


def vix_regime(vix: float | None) -> str:
    if vix is None:
        return "UNKNOWN"
    if vix < 15:
        return "LOW"
    if vix < 25:
        return "NORMAL"
    if vix < 35:
        return "ELEVATED"
    return "CRISIS"


def quote_price(quote: dict[str, Any] | None, fallback: float = 0.0) -> float:
    if not quote:
        return fallback
    return _as_float(quote.get("price")) or fallback


def technical_bias(quote: dict[str, Any] | None) -> str:
    if not quote:
        return "data unavailable"
    price = _as_float(quote.get("price"))
    avg50 = _as_float(quote.get("priceAvg50"))
    avg200 = _as_float(quote.get("priceAvg200"))
    if price and avg50 and avg200:
        if price > avg50 > avg200:
            return "bullish trend"
        if price < avg50 < avg200:
            return "bearish trend"
        if price > avg50:
            return "constructive"
        return "below 50-day"
    return "mixed"


def build_ideas(
    positions: list[Position],
    watchlist: list[WatchlistItem],
    quotes: dict[str, dict[str, Any]],
    option_map: dict[str, list[dict[str, Any]]],
    today: date,
) -> list[TradeIdea]:
    ideas: list[TradeIdea] = []

    overweight = [p for p in positions if p.qty >= 100 and p.weight >= 5 and p.symbol in option_map]
    for position in sorted(overweight, key=lambda p: p.weight, reverse=True):
        option = select_covered_call(position.symbol, option_map.get(position.symbol, []), today)
        if not option:
            continue
        quote = quotes.get(position.symbol)
        rationale = (
            f"{position.symbol} is {position.weight:.1f}% of portfolio, above the 5% single-position cap; "
            f"monetize upside while trimming concentration. Technical bias: {technical_bias(quote)}."
        )
        ideas.append(
            TradeIdea(
                rank=0,
                ticker=position.symbol,
                action="Sell covered call",
                rationale=rationale,
                option=option,
                confidence=82 if position.weight >= 10 else 76,
                risk="Upside capped; avoid sizing beyond shares already held.",
            )
        )

    portfolio_symbols = {p.symbol for p in positions}
    top_watchlist = [
        item
        for item in watchlist
        if item.ticker not in portfolio_symbols and item.score is not None and item.score >= 60
    ][:8]
    for item in top_watchlist:
        option = select_csp(item.ticker, option_map.get(item.ticker, []), today)
        if not option:
            continue
        quote = quotes.get(item.ticker)
        rationale = (
            f"{item.grade} watchlist candidate ({item.score:.1f}) with {item.status.lower()}; "
            f"use CSP only if assigned cost basis fits the watchlist thesis. Technical bias: {technical_bias(quote)}."
        )
        confidence = 72
        if "Top Candidate" in item.status:
            confidence += 5
        if quote and technical_bias(quote) in {"bullish trend", "constructive"}:
            confidence += 4
        ideas.append(
            TradeIdea(
                rank=0,
                ticker=item.ticker,
                action="Sell cash-secured put",
                rationale=rationale,
                option=option,
                confidence=min(confidence, 88),
                risk="Assignment risk; keep per-trade max loss within 5% and total options BP within 30%.",
            )
        )

    for position in sorted(positions, key=lambda p: p.day_chg_pct, reverse=True):
        if position.weight < 5 or position.day_chg_pct < 1.5:
            continue
        ideas.append(
            TradeIdea(
                rank=0,
                ticker=position.symbol,
                action="Trim or rebalance strength",
                rationale=(
                    f"{position.symbol} is up {position.day_chg_pct:.1f}% on the latest repository snapshot "
                    f"and remains a {position.weight:.1f}% position. Use strength to move toward the 5% cap."
                ),
                option=None,
                confidence=68,
                risk="Execution is discretionary; avoid forced selling if tax/liquidity constraints dominate.",
            )
        )

    ideas = sorted(ideas, key=lambda idea: idea.confidence, reverse=True)
    for rank, idea in enumerate(ideas[:8], start=1):
        idea.rank = rank
    return ideas[:8]


def fmt_money(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"${value:,.2f}"


def fmt_pct(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:.1f}%"


def option_line(option: OptionCandidate | None) -> str:
    if option is None:
        return "No options leg."
    delta = f"{option.delta:+.2f}" if option.delta is not None else "N/A"
    iv = fmt_pct(option.iv * 100 if option.iv is not None and option.iv < 3 else option.iv)
    spread = fmt_pct(option.spread_pct)
    annualized = fmt_pct(option.annualized_yield)
    base = (
        f"{option.strategy}: {option.expiration} {option.strike:g} "
        f"for ~{fmt_money(option.bid)} bid ({option.dte} DTE, delta {delta}, "
        f"IV {iv}, OI {option.open_interest}, spread {spread}, ann. yield {annualized})"
    )
    if option.strategy == "CSP" and option.breakeven:
        base += f"; breakeven {fmt_money(option.breakeven)}"
    return base


def build_report(
    today: date,
    positions: list[Position],
    watchlist: list[WatchlistItem],
    quotes: dict[str, dict[str, Any]],
    ideas: list[TradeIdea],
    existing_option_notes: list[str],
    snapshot_date: str,
    data_notes: list[str],
) -> str:
    portfolio_value = sum(p.market_value for p in positions)
    vix_quote = quotes.get("^VIX") or quotes.get("%5EVIX")
    spy_quote = quotes.get("SPY")
    vix = quote_price(vix_quote, 0) or None
    spy = quote_price(spy_quote, 0) or None
    spy_chg = _as_float((spy_quote or {}).get("changesPercentage"))
    regime = vix_regime(vix)

    lines = [
        "# Altamira Trade Idea Generator",
        "",
        f"**Date:** {today.isoformat()}",
        f"**Portfolio context snapshot:** {snapshot_date}",
        f"**Portfolio market value from repo:** {fmt_money(portfolio_value)}",
        f"**Universe:** {len(positions)} portfolio positions + {len(watchlist)} watchlist names",
        "",
        "> Educational / research output only. Not financial advice. Verify live prices, liquidity, earnings dates, buying power, tax impact, and risk limits before placing any order.",
        "",
        "## Market Context",
        "",
        f"- **SPY:** {fmt_money(spy)} ({spy_chg:+.2f}% latest quote)" if spy_chg is not None else f"- **SPY:** {fmt_money(spy)}",
        f"- **VIX:** {vix:.2f} ({regime})" if vix is not None else "- **VIX:** unavailable",
        f"- **Regime playbook:** {'prefer defined-risk spreads / smaller size' if regime in {'ELEVATED', 'CRISIS'} else 'standard CSP and covered-call sizing'}",
        "",
        "## Top Trade Ideas",
        "",
    ]
    if not ideas:
        lines.append("No options-qualified ideas passed the liquidity and DTE filters. Refresh data or run single-name `/options-scan` for manual review.")
    for idea in ideas:
        lines.extend(
            [
                f"### {idea.rank}. {idea.action}: {idea.ticker} (confidence {idea.confidence}/100)",
                "",
                f"- **Contract / setup:** {option_line(idea.option)}",
                f"- **Rationale:** {idea.rationale}",
                f"- **Primary risk:** {idea.risk}",
                "",
            ]
        )

    top_positions = sorted(positions, key=lambda p: p.weight, reverse=True)[:8]
    lines.extend(
        [
            "## Portfolio Concentration Check",
            "",
            "| Ticker | Weight | P&L % | Day Chg % | Note |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for pos in top_positions:
        note = "Above 5% cap" if pos.weight > 5 else "Within cap"
        lines.append(f"| {pos.symbol} | {pos.weight:.1f}% | {pos.pnl_pct:+.1f}% | {pos.day_chg_pct:+.1f}% | {note} |")

    lines.extend(["", "## Existing Options Book", ""])
    if existing_option_notes:
        for note in existing_option_notes:
            lines.append(f"- {note}")
    else:
        lines.append("- No option positions parsed from context/options-positions.md.")

    lines.extend(["", "## Data Notes", ""])
    for note in data_notes:
        lines.append(f"- {note}")
    lines.append("- Run `/options-scan TICKER` for a deeper single-name chain analysis before execution.")
    lines.append("- Refresh repository portfolio context if broker/app data has changed since the snapshot date.")
    lines.append("")
    return "\n".join(lines)


def build_telegram_message(today: date, report_path: Path, quotes: dict[str, dict[str, Any]], ideas: list[TradeIdea], snapshot_date: str) -> str:
    vix_quote = quotes.get("^VIX") or quotes.get("%5EVIX")
    spy_quote = quotes.get("SPY")
    vix = quote_price(vix_quote, 0) or None
    spy = quote_price(spy_quote, 0) or None
    spy_chg = _as_float((spy_quote or {}).get("changesPercentage"))
    regime = vix_regime(vix)
    header = [
        f"*Altamira Trade Ideas* - {today.isoformat()}",
        f"Repo snapshot: `{snapshot_date}`",
        f"SPY: {fmt_money(spy)}" + (f" ({spy_chg:+.2f}%)" if spy_chg is not None else ""),
        f"VIX: {vix:.2f} ({regime})" if vix is not None else "VIX: unavailable",
        "",
    ]
    body: list[str] = []
    for idea in ideas[:5]:
        if idea.option:
            contract = f"{idea.option.expiration} {idea.option.strike:g} @ {fmt_money(idea.option.bid)}"
        else:
            contract = "no option leg"
        body.append(f"{idea.rank}. *{idea.action} {idea.ticker}* - {contract} (conf. {idea.confidence}/100)")
    if not body:
        body.append("No liquid options-qualified ideas passed filters today.")
    footer = [
        "",
        "Risk: verify live chain, earnings, BP, and 5%/30% limits before orders.",
        f"Report: `{report_path}`",
    ]
    message = "\n".join(header + body + footer)
    return message[:3900]


def infer_telegram_chat_id() -> str | None:
    if os.environ.get("TELEGRAM_CHAT_ID"):
        return os.environ["TELEGRAM_CHAT_ID"]
    workflow = OUTPUTS_DIR / "csp-daily-scan-fixed.json"
    text = _read_text(workflow)
    match = re.search(r'"chatId"\s*:\s*"?=?(-?\d+)"?', text)
    if match:
        return match.group(1)
    return None


def send_telegram(message: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = infer_telegram_chat_id()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    if not chat_id:
        raise RuntimeError("TELEGRAM_CHAT_ID is not set and no repository fallback was found")
    response = requests.post(
        f"{TELEGRAM_BASE_URL}/bot{token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True,
        },
        timeout=20,
    )
    response.raise_for_status()


def choose_option_universe(positions: list[Position], watchlist: list[WatchlistItem]) -> list[str]:
    symbols: list[str] = []
    for pos in sorted(positions, key=lambda p: p.weight, reverse=True):
        if pos.qty >= 100 and pos.symbol not in {"FFOLX"}:
            symbols.append(pos.symbol)
    for item in watchlist:
        if item.score is not None and item.score >= 60:
            symbols.append(item.ticker)
    deduped: list[str] = []
    for symbol in symbols:
        if symbol not in deduped:
            deduped.append(symbol)
    return deduped[:16]


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate trade ideas from Altamira portfolio/watchlist context.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Report date (YYYY-MM-DD).")
    parser.add_argument("--send-telegram", action="store_true", help="Send concise report to Telegram.")
    parser.add_argument("--dry-run-telegram", action="store_true", help="Build Telegram text but do not send.")
    args = parser.parse_args()

    today = datetime.strptime(args.date, "%Y-%m-%d").date()
    OUTPUTS_DIR.mkdir(exist_ok=True)

    positions = parse_positions()
    watchlist = parse_watchlist()
    if not positions:
        raise RuntimeError("No positions parsed from context/portfolio-details.md")
    if not watchlist:
        raise RuntimeError("No watchlist parsed from context/watchlist.md")

    fmp_key = get_fmp_key()
    massive_key = get_massive_key()
    snapshot_date = read_snapshot_date()
    option_universe = choose_option_universe(positions, watchlist)
    quote_symbols = sorted({p.symbol for p in positions if p.symbol != "FFOLX"} | {w.ticker for w in watchlist} | {"SPY", "^VIX"})

    data_notes: list[str] = []
    if not fmp_key:
        data_notes.append("FMP_API_KEY unavailable; used repository prices only where possible.")
    if not massive_key:
        data_notes.append("MASSIVE_API_KEY unavailable; options contracts were not enriched.")

    quotes = fetch_quotes(quote_symbols, fmp_key)
    if "^VIX" not in quotes:
        # Some FMP endpoints normalize the symbol differently; fetch separately as a fallback.
        quotes.update(fetch_quotes(["%5EVIX"], fmp_key))
    for pos in positions:
        quotes.setdefault(
            pos.symbol,
            {
                "symbol": pos.symbol,
                "price": pos.current,
                "changesPercentage": pos.day_chg_pct,
            },
        )

    option_map: dict[str, list[dict[str, Any]]] = {}
    for ticker in option_universe:
        option_map[ticker] = fetch_options(ticker, massive_key, today)

    ideas = build_ideas(positions, watchlist, quotes, option_map, today)
    existing_option_notes = read_existing_options(today)
    report = build_report(
        today=today,
        positions=positions,
        watchlist=watchlist,
        quotes=quotes,
        ideas=ideas,
        existing_option_notes=existing_option_notes,
        snapshot_date=snapshot_date,
        data_notes=data_notes,
    )
    report_path = OUTPUTS_DIR / f"trade-idea-generator-{today.isoformat()}.md"
    report_path.write_text(report, encoding="utf-8")

    telegram_text = build_telegram_message(today, report_path.relative_to(WORKSPACE), quotes, ideas, snapshot_date)
    telegram_path = OUTPUTS_DIR / f"trade-idea-generator-telegram-{today.isoformat()}.txt"
    telegram_path.write_text(telegram_text + "\n", encoding="utf-8")

    if args.send_telegram:
        send_telegram(telegram_text)
        print(f"Sent Telegram message. Report: {report_path.relative_to(WORKSPACE)}")
    elif args.dry_run_telegram:
        print(telegram_text)
    else:
        print(f"Wrote report: {report_path.relative_to(WORKSPACE)}")
        print(f"Wrote Telegram preview: {telegram_path.relative_to(WORKSPACE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
