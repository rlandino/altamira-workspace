#!/usr/bin/env python3
"""Generate daily portfolio/watchlist trade ideas and optionally send Telegram."""

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
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORTFOLIO = ROOT / "context" / "portfolio-details.md"
DEFAULT_WATCHLIST = ROOT / "context" / "watchlist.md"
DEFAULT_OPTIONS = ROOT / "context" / "options-positions.md"
DEFAULT_OUTPUT_DIR = ROOT / "outputs"
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"
TELEGRAM_API_URL = "https://api.telegram.org"


@dataclass
class Position:
    """Current equity/ETF position parsed from repository context."""

    symbol: str
    quantity: float
    average_price: Optional[float]
    current_price: Optional[float]
    market_value: Optional[float]
    weight: Optional[float]


@dataclass
class WatchlistEntry:
    """Watchlist candidate parsed from repository context."""

    ticker: str
    score: Optional[float]
    grade: str
    company: str
    status: str


@dataclass
class OptionPosition:
    """Open short premium position parsed from repository context."""

    ticker: str
    strike: float
    option_type: str
    expiration: str
    credit: float
    current: float
    contracts: int


@dataclass
class TradeIdea:
    """A generated trade or management idea."""

    rank_score: float
    ticker: str
    strategy: str
    action: str
    setup: str
    rationale: str
    risk: str
    source: str


def clean_number(value: str) -> Optional[float]:
    """Parse a number from common portfolio table formats."""

    value = value.strip()
    if not value or value in {"-", "—", "N/A"}:
        return None
    value = value.replace("$", "").replace(",", "").replace("%", "")
    value = value.replace("+", "")
    match = re.search(r"-?\d+(?:\.\d+)?", value)
    if not match:
        return None
    return float(match.group(0))


def split_table_row(line: str) -> List[str]:
    """Split a markdown table row into cells."""

    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_portfolio(path: Path) -> List[Position]:
    """Parse current positions from context/portfolio-details.md."""

    text = path.read_text(encoding="utf-8")
    positions: List[Position] = []
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
        cells = split_table_row(line)
        if len(cells) < 9 or cells[0].lower().startswith("totals"):
            continue
        symbol = cells[0].upper()
        if not re.fullmatch(r"[A-Z][A-Z0-9.\-]{0,9}", symbol):
            continue
        positions.append(
            Position(
                symbol=symbol,
                quantity=clean_number(cells[1]) or 0.0,
                average_price=clean_number(cells[2]),
                current_price=clean_number(cells[3]),
                market_value=clean_number(cells[4]),
                weight=clean_number(cells[8]),
            )
        )
    return positions


def parse_watchlist(path: Path) -> List[WatchlistEntry]:
    """Parse watchlist entries from context/watchlist.md."""

    text = path.read_text(encoding="utf-8")
    entries: List[WatchlistEntry] = []
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
            if entries:
                break
            continue
        cells = split_table_row(line)
        if len(cells) < 5:
            continue
        ticker = cells[0].upper()
        if not re.fullmatch(r"[A-Z][A-Z0-9.\-]{0,9}", ticker):
            continue
        grade = re.sub(r"[*_`]", "", cells[2]).strip()
        entries.append(
            WatchlistEntry(
                ticker=ticker,
                score=clean_number(cells[1]),
                grade=grade,
                company=cells[3],
                status=cells[4],
            )
        )
    return entries


def parse_options(path: Path) -> List[OptionPosition]:
    """Parse short premium positions from context/options-positions.md."""

    text = path.read_text(encoding="utf-8")
    options: List[OptionPosition] = []
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
            if options:
                break
            continue
        cells = split_table_row(line)
        if len(cells) < 7:
            continue
        strike = clean_number(cells[1])
        credit = clean_number(cells[4])
        current = clean_number(cells[5])
        contracts = clean_number(cells[6])
        if strike is None or credit is None or current is None or contracts is None:
            continue
        options.append(
            OptionPosition(
                ticker=cells[0].upper(),
                strike=strike,
                option_type=cells[2],
                expiration=cells[3],
                credit=credit,
                current=current,
                contracts=int(contracts),
            )
        )
    return options


def get_env_first(names: Sequence[str]) -> Optional[str]:
    """Return the first non-empty environment value from a list of names."""

    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def fetch_json(url: str, timeout: int = 15) -> Any:
    """Fetch JSON from a URL with a small timeout."""

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "AltamiraTradeIdeaGenerator/1.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def chunks(values: Sequence[str], size: int) -> Iterable[Sequence[str]]:
    """Yield fixed-size chunks."""

    for idx in range(0, len(values), size):
        yield values[idx : idx + size]


def fetch_quotes(symbols: Sequence[str], api_key: Optional[str]) -> Tuple[Dict[str, Dict[str, Any]], List[str]]:
    """Fetch batch FMP quotes. Returns quote map and warning messages."""

    warnings: List[str] = []
    if not api_key:
        return {}, ["FMP_API_KEY is not set; using repository snapshot prices only."]

    quote_map: Dict[str, Dict[str, Any]] = {}
    for chunk in chunks(sorted(set(symbols)), 35):
        encoded_symbols = urllib.parse.quote(",".join(chunk), safe=",^")
        url = f"{FMP_BASE_URL}/quote/{encoded_symbols}?apikey={urllib.parse.quote(api_key)}"
        try:
            data = fetch_json(url)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            warnings.append(f"Quote fetch failed for {','.join(chunk)}: {exc}")
            continue
        if isinstance(data, list):
            for quote in data:
                symbol = str(quote.get("symbol", "")).upper()
                if symbol:
                    quote_map[symbol] = quote
    return quote_map, warnings


def fetch_earnings_calendar(
    symbols: Sequence[str], api_key: Optional[str], as_of: dt.date, days: int = 45
) -> Tuple[Dict[str, str], List[str]]:
    """Fetch upcoming earnings dates for the target universe."""

    warnings: List[str] = []
    if not api_key:
        return {}, []
    end = as_of + dt.timedelta(days=days)
    url = (
        f"{FMP_BASE_URL}/earning_calendar?"
        f"from={as_of.isoformat()}&to={end.isoformat()}&apikey={urllib.parse.quote(api_key)}"
    )
    try:
        data = fetch_json(url)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
        return {}, [f"Earnings calendar fetch failed: {exc}"]
    wanted = set(symbols)
    earnings: Dict[str, str] = {}
    if isinstance(data, list):
        for row in data:
            symbol = str(row.get("symbol", "")).upper()
            date = row.get("date")
            if symbol in wanted and date:
                earnings.setdefault(symbol, str(date))
    return earnings, warnings


def next_friday_between(as_of: dt.date, min_days: int = 30, max_days: int = 45) -> dt.date:
    """Choose a Friday expiration between target DTE bounds."""

    candidate = as_of + dt.timedelta(days=min_days)
    while candidate.weekday() != 4:
        candidate += dt.timedelta(days=1)
    if (candidate - as_of).days > max_days:
        candidate -= dt.timedelta(days=7)
    return candidate


def round_to_increment(price: float, direction: str) -> float:
    """Round a strike to a practical increment based on underlying price."""

    if price >= 500:
        increment = 10
    elif price >= 100:
        increment = 5
    elif price >= 50:
        increment = 2.5
    else:
        increment = 1
    if direction == "down":
        return math.floor(price / increment) * increment
    return math.ceil(price / increment) * increment


def fmt_money(value: Optional[float]) -> str:
    """Format a money value."""

    if value is None:
        return "N/A"
    return f"${value:,.2f}"


def fmt_pct(value: Optional[float]) -> str:
    """Format a percentage."""

    if value is None:
        return "N/A"
    return f"{value:+.1f}%"


def latest_price(position: Optional[Position], quote: Optional[Dict[str, Any]]) -> Optional[float]:
    """Prefer live quote price and fall back to repository snapshot."""

    if quote:
        price = quote.get("price")
        if isinstance(price, (int, float)) and price > 0:
            return float(price)
    return position.current_price if position else None


def trend_description(price: Optional[float], quote: Optional[Dict[str, Any]]) -> Tuple[int, str]:
    """Score and describe current trend from FMP quote fields."""

    if not price or not quote:
        return 0, "trend unavailable"
    score = 0
    parts: List[str] = []
    avg50 = quote.get("priceAvg50")
    avg200 = quote.get("priceAvg200")
    day_change = quote.get("changesPercentage")
    if isinstance(avg50, (int, float)) and avg50 > 0:
        if price >= avg50:
            score += 8
            parts.append("above 50D")
        else:
            score -= 5
            parts.append("below 50D")
    if isinstance(avg200, (int, float)) and avg200 > 0:
        if price >= avg200:
            score += 6
            parts.append("above 200D")
        else:
            score -= 4
            parts.append("below 200D")
    if isinstance(day_change, (int, float)):
        if day_change > 3:
            score -= 2
            parts.append(f"hot today {day_change:+.1f}%")
        elif day_change < -2:
            score += 2
            parts.append(f"pullback {day_change:+.1f}%")
    return score, ", ".join(parts) if parts else "trend mixed"


def generate_option_management_ideas(options: Sequence[OptionPosition]) -> List[TradeIdea]:
    """Generate management actions for existing short premium positions."""

    ideas: List[TradeIdea] = []
    for opt in options:
        ratio = opt.current / opt.credit if opt.credit else 0
        pnl_per_contract = (opt.credit - opt.current) * 100
        total_pnl = pnl_per_contract * opt.contracts
        dte_text = opt.expiration
        if ratio <= 0.5:
            action = "Close / harvest profit"
            score = 92
            risk = "Waiting for the last premium can turn a winner into gamma/assignment risk."
            rationale = f"Current mark is {ratio:.0%} of original credit; estimated open P&L {fmt_money(total_pnl)}."
        elif ratio >= 2.0:
            action = "Defend or roll"
            score = 88
            risk = "Position is beyond the 200% credit stop threshold in the risk framework."
            rationale = f"Current mark is {ratio:.0%} of original credit; estimated open P&L {fmt_money(total_pnl)}."
        elif ratio >= 1.5:
            action = "Monitor closely"
            score = 72
            risk = "Loss is approaching the 200% credit stop threshold."
            rationale = f"Current mark is {ratio:.0%} of original credit; estimated open P&L {fmt_money(total_pnl)}."
        else:
            action = "Hold / reassess at 50% profit"
            score = 55
            risk = "Keep the predefined stop and avoid holding through unplanned earnings."
            rationale = f"Current mark is {ratio:.0%} of original credit; estimated open P&L {fmt_money(total_pnl)}."
        ideas.append(
            TradeIdea(
                rank_score=score,
                ticker=opt.ticker,
                strategy=f"Short {opt.option_type} management",
                action=action,
                setup=f"{opt.contracts}x {opt.ticker} {opt.expiration} {opt.strike:g}{opt.option_type[0].upper()}",
                rationale=rationale,
                risk=risk,
                source=f"Existing option expiring {dte_text}",
            )
        )
    return ideas


def generate_covered_call_ideas(
    positions: Sequence[Position],
    quotes: Dict[str, Dict[str, Any]],
    earnings: Dict[str, str],
    as_of: dt.date,
) -> List[TradeIdea]:
    """Generate covered call candidates for share lots already held."""

    expiry = next_friday_between(as_of)
    ideas: List[TradeIdea] = []
    for pos in positions:
        if pos.quantity < 100:
            continue
        quote = quotes.get(pos.symbol)
        price = latest_price(pos, quote)
        if not price:
            continue
        contracts = int(pos.quantity // 100)
        trend_score, trend = trend_description(price, quote)
        weight = pos.weight or 0
        if weight < 3 and pos.quantity < 200:
            continue
        upside = 1.03 if weight >= 10 else 1.05
        strike = round_to_increment(price * upside, "up")
        earnings_text = f"Earnings {earnings[pos.symbol]} inside window; use smaller size or skip." if pos.symbol in earnings else "No known earnings conflict inside scan window."
        score = 52 + min(weight * 1.8, 28) + trend_score
        if pos.symbol in earnings:
            score -= 8
        if weight >= 10:
            rationale = f"{pos.symbol} is a {weight:.1f}% portfolio weight; covered calls monetize concentration while preserving defined upside."
        else:
            rationale = f"{pos.symbol} has enough shares for up to {contracts} covered call contract(s); {trend}."
        ideas.append(
            TradeIdea(
                rank_score=score,
                ticker=pos.symbol,
                strategy="Covered call",
                action="Sell 0.20-0.30 delta call",
                setup=f"{expiry.isoformat()} ~{strike:g}C, up to {contracts} contract(s); target 1-2% notional credit.",
                rationale=f"{rationale} {earnings_text}",
                risk="Caps upside above the short strike; avoid oversizing around earnings or major catalysts.",
                source="Current portfolio holding",
            )
        )
    return ideas


def generate_watchlist_csp_ideas(
    watchlist: Sequence[WatchlistEntry],
    positions: Dict[str, Position],
    quotes: Dict[str, Dict[str, Any]],
    earnings: Dict[str, str],
    vix: Optional[float],
    as_of: dt.date,
) -> List[TradeIdea]:
    """Generate CSP/bull put spread ideas for high-quality watchlist names."""

    expiry = next_friday_between(as_of)
    ideas: List[TradeIdea] = []
    vix_regime = "NORMAL"
    if vix is not None:
        if vix < 15:
            vix_regime = "LOW"
        elif vix > 35:
            vix_regime = "CRISIS"
        elif vix > 25:
            vix_regime = "ELEVATED"
    prefer_spread = vix_regime in {"ELEVATED", "CRISIS"}
    for entry in watchlist:
        if entry.score is None or entry.score < 58:
            continue
        quote = quotes.get(entry.ticker)
        price = latest_price(positions.get(entry.ticker), quote)
        if not price:
            continue
        trend_score, trend = trend_description(price, quote)
        strike = round_to_increment(price * 0.92, "down")
        long_put = round_to_increment(strike * 0.97, "down")
        strategy = "Bull put spread" if prefer_spread else "Cash-secured put"
        setup = (
            f"{expiry.isoformat()} sell ~{strike:g}P / buy ~{long_put:g}P, 0.20-0.30 short delta."
            if prefer_spread
            else f"{expiry.isoformat()} ~{strike:g}P, 0.20-0.30 delta; target >=1% cash-secured monthly yield."
        )
        earnings_penalty = 12 if entry.ticker in earnings else 0
        status_bonus = 7 if "Top Candidate" in entry.status else 2
        score = (entry.score or 0) + trend_score + status_bonus - earnings_penalty
        earnings_text = f"Earnings {earnings[entry.ticker]} inside window; skip naked premium unless intentionally trading event risk." if entry.ticker in earnings else "No known earnings conflict inside scan window."
        ideas.append(
            TradeIdea(
                rank_score=score,
                ticker=entry.ticker,
                strategy=strategy,
                action="Open only if chain liquidity and premium targets confirm",
                setup=setup,
                rationale=f"{entry.grade} watchlist score ({entry.score:.1f}); {trend}. {earnings_text}",
                risk="Use <=5% max position risk and obey the 30% options allocation cap; validate bid/ask width before entry.",
                source=f"Watchlist: {entry.status}",
            )
        )
    return ideas


def generate_rebalance_flags(positions: Sequence[Position]) -> List[str]:
    """Return concentration and diversification flags."""

    flags: List[str] = []
    overweight = [p for p in positions if (p.weight or 0) >= 10]
    if overweight:
        names = ", ".join(f"{p.symbol} {p.weight:.1f}%" for p in sorted(overweight, key=lambda p: p.weight or 0, reverse=True))
        flags.append(f"Concentration watch: {names}. Prefer income/trim ideas over adding more exposure.")
    low_cash_note = "Risk framework target cash reserve is >=15%; confirm current cash before new CSPs."
    flags.append(low_cash_note)
    return flags


def build_report(
    ideas: Sequence[TradeIdea],
    positions: Sequence[Position],
    watchlist: Sequence[WatchlistEntry],
    options: Sequence[OptionPosition],
    warnings: Sequence[str],
    flags: Sequence[str],
    vix: Optional[float],
    as_of: dt.date,
    live_quotes: bool,
) -> str:
    """Build markdown report."""

    top_ideas = sorted(ideas, key=lambda idea: idea.rank_score, reverse=True)
    lines = [
        f"# Trade Idea Generator — {as_of.isoformat()}",
        "",
        "> Educational analysis only; not investment advice. Validate live option chains, liquidity, earnings dates, and risk limits before placing any trade.",
        "",
        "## Run Summary",
        "",
        f"- Portfolio positions parsed: **{len(positions)}**",
        f"- Watchlist entries parsed: **{len(watchlist)}**",
        f"- Open short premium positions parsed: **{len(options)}**",
        f"- Live quote data: **{'yes' if live_quotes else 'no / repository snapshot fallback'}**",
        f"- VIX: **{vix:.2f}**" if vix is not None else "- VIX: **N/A**",
        "",
        "## Top Trade / Management Ideas",
        "",
    ]
    for idx, idea in enumerate(top_ideas[:10], start=1):
        lines.extend(
            [
                f"### {idx}. {idea.ticker} — {idea.strategy}",
                "",
                f"- **Action:** {idea.action}",
                f"- **Setup:** {idea.setup}",
                f"- **Score:** {idea.rank_score:.1f}",
                f"- **Source:** {idea.source}",
                f"- **Rationale:** {idea.rationale}",
                f"- **Risk:** {idea.risk}",
                "",
            ]
        )
    if not top_ideas:
        lines.extend(["No actionable ideas were generated from the current repository context.", ""])

    lines.extend(["## Portfolio Flags", ""])
    for flag in flags:
        lines.append(f"- {flag}")
    lines.append("")
    if warnings:
        lines.extend(["## Data Warnings", ""])
        for warning in warnings:
            lines.append(f"- {warning}")
        lines.append("")
    lines.extend(
        [
            "## Execution Checklist",
            "",
            "1. Re-check live quotes and option chain bid/ask spreads.",
            "2. Confirm no earnings or binary catalysts inside the intended DTE window.",
            "3. Confirm portfolio cash, concentration, and options allocation limits.",
            "4. Enter only with predefined 50% profit-taking and 200% credit stop rules.",
            "",
        ]
    )
    return "\n".join(lines)


def build_telegram_message(
    ideas: Sequence[TradeIdea], flags: Sequence[str], vix: Optional[float], as_of: dt.date, report_path: Path
) -> str:
    """Build a concise Telegram-safe message."""

    top_ideas = sorted(ideas, key=lambda idea: idea.rank_score, reverse=True)[:5]
    lines = [
        f"Altamira Trade Ideas — {as_of.isoformat()}",
        f"VIX: {vix:.2f}" if vix is not None else "VIX: N/A",
        "",
    ]
    if not top_ideas:
        lines.append("No actionable ideas generated from current repo context.")
    for idx, idea in enumerate(top_ideas, start=1):
        lines.extend(
            [
                f"{idx}) {idea.ticker} — {idea.strategy}",
                f"Action: {idea.action}",
                f"Setup: {idea.setup}",
                f"Why: {idea.rationale}",
                "",
            ]
        )
    if flags:
        lines.append("Risk notes:")
        for flag in flags[:3]:
            lines.append(f"- {flag}")
    lines.extend(
        [
            "",
            f"Report: {report_path.name}",
            "Educational only. Validate live chain/liquidity and risk limits before trading.",
        ]
    )
    message = "\n".join(lines)
    if len(message) <= 3900:
        return message
    return message[:3800].rsplit("\n", 1)[0] + "\n\n[Truncated — see report file]"


def send_telegram(message: str, token: str, chat_id: str) -> Dict[str, Any]:
    """Send a Telegram message through Bot API."""

    url = f"{TELEGRAM_API_URL}/bot{token}/sendMessage"
    payload = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    request = urllib.request.Request(url, data=payload, method="POST")
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def run(args: argparse.Namespace) -> int:
    """Run the generator."""

    as_of = dt.date.fromisoformat(args.as_of) if args.as_of else dt.datetime.now().date()
    portfolio_path = Path(args.portfolio)
    watchlist_path = Path(args.watchlist)
    options_path = Path(args.options)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    positions = parse_portfolio(portfolio_path)
    watchlist = parse_watchlist(watchlist_path)
    options = parse_options(options_path)
    positions_by_symbol = {position.symbol: position for position in positions}

    symbols = sorted({p.symbol for p in positions} | {w.ticker for w in watchlist} | {"^VIX"})
    symbols = [symbol for symbol in symbols if symbol != "FFOLX"]
    fmp_key = None if args.no_live_data else get_env_first(["FMP_API_KEY", "FINANCIAL_MODELING_PREP_API_KEY"])
    quotes, warnings = fetch_quotes(symbols, fmp_key)
    earnings, earnings_warnings = fetch_earnings_calendar([s for s in symbols if s != "^VIX"], fmp_key, as_of)
    warnings.extend(earnings_warnings)

    vix_quote = quotes.get("^VIX") or quotes.get("VIX")
    vix = None
    if vix_quote and isinstance(vix_quote.get("price"), (int, float)):
        vix = float(vix_quote["price"])

    ideas: List[TradeIdea] = []
    ideas.extend(generate_option_management_ideas(options))
    ideas.extend(generate_covered_call_ideas(positions, quotes, earnings, as_of))
    ideas.extend(generate_watchlist_csp_ideas(watchlist, positions_by_symbol, quotes, earnings, vix, as_of))
    flags = generate_rebalance_flags(positions)

    report = build_report(
        ideas=ideas,
        positions=positions,
        watchlist=watchlist,
        options=options,
        warnings=warnings,
        flags=flags,
        vix=vix,
        as_of=as_of,
        live_quotes=bool(quotes),
    )
    report_path = output_dir / f"trade-idea-generator-{as_of.isoformat()}.md"
    report_path.write_text(report, encoding="utf-8")

    telegram_message = build_telegram_message(ideas, flags, vix, as_of, report_path)
    telegram_path = output_dir / f"trade-idea-generator-telegram-{as_of.isoformat()}.txt"
    telegram_path.write_text(telegram_message, encoding="utf-8")

    print(f"Wrote report: {report_path}")
    print(f"Wrote Telegram preview: {telegram_path}")
    print("")
    print(textwrap.indent(telegram_message, prefix="  "))

    if args.send_telegram:
        token = args.telegram_token or get_env_first(
            ["TELEGRAM_BOT_TOKEN", "TELEGRAM_TOKEN", "TELEGRAM_API_TOKEN", "TG_BOT_TOKEN"]
        )
        chat_id = args.telegram_chat_id or get_env_first(["TELEGRAM_CHAT_ID", "TELEGRAM_CHANNEL_ID", "TG_CHAT_ID"])
        if not token or not chat_id:
            print(
                "ERROR: Telegram send requested but TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID are not set.",
                file=sys.stderr,
            )
            return 2
        try:
            response = send_telegram(telegram_message, token=token, chat_id=chat_id)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as exc:
            print(f"ERROR: Telegram send failed: {exc}", file=sys.stderr)
            return 3
        if not response.get("ok"):
            print(f"ERROR: Telegram API returned non-ok response: {response}", file=sys.stderr)
            return 3
        message_id = response.get("result", {}).get("message_id")
        print(f"Telegram message sent successfully (message_id={message_id}).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser."""

    parser = argparse.ArgumentParser(
        description="Generate Altamira trade ideas from repository portfolio/watchlist context."
    )
    parser.add_argument("--portfolio", default=str(DEFAULT_PORTFOLIO), help="Portfolio markdown context path.")
    parser.add_argument("--watchlist", default=str(DEFAULT_WATCHLIST), help="Watchlist markdown context path.")
    parser.add_argument("--options", default=str(DEFAULT_OPTIONS), help="Options positions markdown context path.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for generated outputs.")
    parser.add_argument("--as-of", help="Run date as YYYY-MM-DD. Defaults to today.")
    parser.add_argument("--no-live-data", action="store_true", help="Skip FMP calls and use repository snapshot data.")
    parser.add_argument("--send-telegram", action="store_true", help="Send the concise output to Telegram.")
    parser.add_argument("--telegram-token", help="Telegram bot token. Prefer TELEGRAM_BOT_TOKEN env var.")
    parser.add_argument("--telegram-chat-id", help="Telegram chat/channel ID. Prefer TELEGRAM_CHAT_ID env var.")
    return parser


if __name__ == "__main__":
    raise SystemExit(run(build_parser().parse_args()))
