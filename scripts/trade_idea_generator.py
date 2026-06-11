#!/usr/bin/env python3
"""
Daily portfolio/watchlist trade idea generator.

Reads the repository's portfolio and watchlist context, pulls live FMP market
data when FMP_API_KEY is available, writes a dated markdown report, and can
send a concise summary to Telegram.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


WORKSPACE = Path(__file__).resolve().parent.parent
CONTEXT = WORKSPACE / "context"
OUTPUTS = WORKSPACE / "outputs"
FMP_BASE = "https://financialmodelingprep.com/api/v3"


@dataclass
class PortfolioPosition:
    symbol: str
    quantity: float
    average_price: Optional[float]
    context_price: Optional[float]
    market_value: Optional[float]
    weight: Optional[float]


@dataclass
class WatchlistEntry:
    ticker: str
    score: Optional[float]
    grade: str
    company: str
    status: str


@dataclass
class ShortPremiumPosition:
    ticker: str
    strike: float
    option_type: str
    expiration: str
    credit: Optional[float]
    current: Optional[float]
    contracts: Optional[int]


@dataclass
class Quote:
    symbol: str
    price: Optional[float]
    change_pct: Optional[float]
    name: str = ""


@dataclass
class Technicals:
    sma20: Optional[float]
    sma50: Optional[float]
    rsi14: Optional[float]
    change_20d_pct: Optional[float]


@dataclass
class TradeIdea:
    rank_score: float
    ticker: str
    strategy: str
    setup: str
    action: str
    rationale: str
    risk: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate daily trade ideas from context portfolio/watchlist."
    )
    parser.add_argument(
        "--portfolio",
        default=str(CONTEXT / "portfolio-details.md"),
        help="Path to portfolio context markdown.",
    )
    parser.add_argument(
        "--watchlist",
        default=str(CONTEXT / "watchlist.md"),
        help="Path to watchlist context markdown.",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Markdown output path. Defaults to outputs/trade-ideas-YYYY-MM-DD.md.",
    )
    parser.add_argument(
        "--max-ideas",
        type=int,
        default=5,
        help="Maximum number of ideas to include in Telegram summary.",
    )
    parser.add_argument(
        "--send-telegram",
        action="store_true",
        help="Send the concise trade idea summary to Telegram.",
    )
    parser.add_argument(
        "--telegram-chat-id",
        default=None,
        help=(
            "Telegram chat id or @channel username. Defaults to TELEGRAM_CHAT_ID, "
            "then a fixed chatId found in existing workflow exports."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate report but do not send Telegram, even with --send-telegram.",
    )
    parser.add_argument(
        "--as-of",
        default=date.today().isoformat(),
        help="Report date in YYYY-MM-DD format. Defaults to today.",
    )
    return parser.parse_args()


def parse_float(value: str) -> Optional[float]:
    cleaned = value.strip().replace("$", "").replace(",", "").replace("%", "")
    cleaned = cleaned.replace("+", "").replace("\u2212", "-")
    if not cleaned or cleaned in {"-", "\u2014", "N/A"}:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def parse_markdown_row(line: str) -> List[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def read_lines(path: Path) -> List[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()


def parse_portfolio(path: Path) -> List[PortfolioPosition]:
    lines = read_lines(path)
    positions: List[PortfolioPosition] = []
    in_table = False
    for line in lines:
        if line.startswith("| SYMBOL |"):
            in_table = True
            continue
        if not in_table:
            continue
        if not line.startswith("|"):
            if positions:
                break
            continue
        if set(line.replace("|", "").replace("-", "").replace(" ", "")) == set():
            continue
        cells = parse_markdown_row(line)
        if len(cells) < 9 or cells[0].upper() in {"SYMBOL", "--------"}:
            continue
        symbol = cells[0].upper()
        if symbol in {"TOTALS", "**TOTALS:**"}:
            break
        positions.append(
            PortfolioPosition(
                symbol=symbol,
                quantity=parse_float(cells[1]) or 0.0,
                average_price=parse_float(cells[2]),
                context_price=parse_float(cells[3]),
                market_value=parse_float(cells[4]),
                weight=parse_float(cells[8]),
            )
        )
    return positions


def parse_short_premium(path: Path) -> List[ShortPremiumPosition]:
    lines = read_lines(path)
    positions: List[ShortPremiumPosition] = []
    in_table = False
    for line in lines:
        if line.startswith("| Ticker | Strike | Type |"):
            in_table = True
            continue
        if not in_table:
            continue
        if not line.startswith("|"):
            if positions:
                break
            continue
        cells = parse_markdown_row(line)
        if len(cells) < 7 or cells[0].lower() in {"ticker", "--------"}:
            continue
        strike = parse_float(cells[1])
        if strike is None:
            continue
        positions.append(
            ShortPremiumPosition(
                ticker=cells[0].upper(),
                strike=strike,
                option_type=cells[2],
                expiration=cells[3],
                credit=parse_float(cells[4]),
                current=parse_float(cells[5]),
                contracts=int(parse_float(cells[6]) or 0),
            )
        )
    return positions


def parse_watchlist(path: Path) -> List[WatchlistEntry]:
    lines = read_lines(path)
    entries: List[WatchlistEntry] = []
    in_table = False
    for line in lines:
        if line.startswith("| Ticker | Score | Grade |"):
            in_table = True
            continue
        if not in_table:
            continue
        if not line.startswith("|"):
            if entries:
                break
            continue
        cells = parse_markdown_row(line)
        if len(cells) < 5 or cells[0].lower() in {"ticker", "--------"}:
            continue
        entries.append(
            WatchlistEntry(
                ticker=cells[0].upper(),
                score=parse_float(cells[1]),
                grade=cells[2].replace("*", ""),
                company=cells[3],
                status=re.sub(r"[^\x00-\x7F]+", "", cells[4]).strip(),
            )
        )
    return entries


def option_expiration_date(option: ShortPremiumPosition) -> Optional[date]:
    try:
        return datetime.strptime(option.expiration, "%Y-%m-%d").date()
    except ValueError:
        return None


def split_active_short_premium(
    short_premium: Sequence[ShortPremiumPosition], as_of: date
) -> Tuple[List[ShortPremiumPosition], List[ShortPremiumPosition]]:
    active: List[ShortPremiumPosition] = []
    expired: List[ShortPremiumPosition] = []
    for option in short_premium:
        expiration_date = option_expiration_date(option)
        if expiration_date is not None and expiration_date < as_of:
            expired.append(option)
        else:
            active.append(option)
    return active, expired


def chunked(values: Sequence[str], size: int) -> Iterable[Sequence[str]]:
    for index in range(0, len(values), size):
        yield values[index : index + size]


def get_json(url: str, timeout: int = 20) -> Any:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "AltamiraTradeIdeaGenerator/1.0"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fmp_url(path: str, api_key: str, params: Optional[Dict[str, Any]] = None) -> str:
    params = dict(params or {})
    params["apikey"] = api_key
    query = urllib.parse.urlencode(params)
    return f"{FMP_BASE}/{path}?{query}"


def fetch_quotes(symbols: Sequence[str], api_key: Optional[str]) -> Dict[str, Quote]:
    quotes: Dict[str, Quote] = {}
    if not api_key:
        return quotes
    for group in chunked(sorted(set(symbols)), 40):
        path = "quote/" + urllib.parse.quote(",".join(group), safe=",^")
        try:
            data = get_json(fmp_url(path, api_key))
        except Exception as exc:
            print(f"Warning: quote fetch failed for {','.join(group)}: {exc}", file=sys.stderr)
            continue
        if isinstance(data, dict):
            data = [data]
        for row in data or []:
            symbol = str(row.get("symbol") or "").upper()
            if not symbol:
                continue
            quotes[symbol] = Quote(
                symbol=symbol,
                price=as_float(row.get("price")),
                change_pct=as_float(row.get("changesPercentage")),
                name=str(row.get("name") or ""),
            )
    return quotes


def fetch_history(symbol: str, api_key: Optional[str], as_of: date) -> List[float]:
    if not api_key:
        return []
    start = (as_of - timedelta(days=180)).isoformat()
    path = f"historical-price-full/{urllib.parse.quote(symbol, safe='^')}"
    try:
        data = get_json(fmp_url(path, api_key, {"from": start, "to": as_of.isoformat()}))
    except Exception as exc:
        print(f"Warning: history fetch failed for {symbol}: {exc}", file=sys.stderr)
        return []
    rows = data.get("historical") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        return []
    closes = [as_float(row.get("close")) for row in reversed(rows)]
    return [value for value in closes if value is not None]


def fetch_earnings(api_key: Optional[str], as_of: date, days: int = 45) -> Dict[str, str]:
    if not api_key:
        return {}
    try:
        data = get_json(
            fmp_url(
                "earning_calendar",
                api_key,
                {
                    "from": as_of.isoformat(),
                    "to": (as_of + timedelta(days=days)).isoformat(),
                },
            )
        )
    except Exception as exc:
        print(f"Warning: earnings calendar fetch failed: {exc}", file=sys.stderr)
        return {}
    earnings: Dict[str, str] = {}
    if isinstance(data, list):
        for row in data:
            symbol = str(row.get("symbol") or "").upper()
            event_date = row.get("date")
            if symbol and event_date:
                earnings.setdefault(symbol, str(event_date))
    return earnings


def as_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        if isinstance(value, str):
            return parse_float(value)
        if math.isnan(float(value)):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def moving_average(values: Sequence[float], length: int) -> Optional[float]:
    if len(values) < length:
        return None
    return sum(values[-length:]) / length


def rsi(values: Sequence[float], length: int = 14) -> Optional[float]:
    if len(values) <= length:
        return None
    gains: List[float] = []
    losses: List[float] = []
    window = values[-(length + 1) :]
    for previous, current in zip(window, window[1:]):
        change = current - previous
        gains.append(max(change, 0))
        losses.append(abs(min(change, 0)))
    avg_gain = sum(gains) / length
    avg_loss = sum(losses) / length
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def compute_technicals(history: Sequence[float]) -> Technicals:
    change_20d = None
    if len(history) >= 21 and history[-21] != 0:
        change_20d = (history[-1] / history[-21] - 1) * 100
    return Technicals(
        sma20=moving_average(history, 20),
        sma50=moving_average(history, 50),
        rsi14=rsi(history),
        change_20d_pct=change_20d,
    )


def vix_regime(vix: Optional[float]) -> str:
    if vix is None:
        return "UNKNOWN"
    if vix < 15:
        return "LOW"
    if vix < 25:
        return "NORMAL"
    if vix < 35:
        return "ELEVATED"
    return "CRISIS"


def round_strike(value: float, direction: str) -> float:
    if value >= 500:
        increment = 10
    elif value >= 100:
        increment = 5
    elif value >= 30:
        increment = 2.5
    else:
        increment = 1
    if direction == "down":
        return math.floor(value / increment) * increment
    return math.ceil(value / increment) * increment


def format_strike(value: float) -> str:
    if abs(value - round(value)) < 0.001:
        return str(int(round(value)))
    return f"{value:.1f}"


def nearest_friday(as_of: date, min_days: int = 30, max_days: int = 45) -> date:
    candidates = [
        as_of + timedelta(days=offset)
        for offset in range(min_days, max_days + 1)
        if (as_of + timedelta(days=offset)).weekday() == 4
    ]
    if candidates:
        return candidates[0]
    target = as_of + timedelta(days=42)
    while target.weekday() != 4:
        target += timedelta(days=1)
    return target


def price_for(symbol: str, quotes: Dict[str, Quote], positions: Dict[str, PortfolioPosition]) -> Optional[float]:
    quote = quotes.get(symbol)
    if quote and quote.price:
        return quote.price
    position = positions.get(symbol)
    return position.context_price if position else None


def technical_bias(price: Optional[float], tech: Technicals) -> str:
    if price is None:
        return "price unavailable"
    if tech.sma20 and tech.sma50 and price > tech.sma20 > tech.sma50:
        return "bullish trend"
    if tech.sma20 and tech.sma50 and price < tech.sma20 < tech.sma50:
        return "bearish trend"
    if tech.rsi14 and tech.rsi14 > 70:
        return "overbought"
    if tech.rsi14 and tech.rsi14 < 35:
        return "oversold"
    return "neutral trend"


def build_trade_ideas(
    portfolio: Sequence[PortfolioPosition],
    watchlist: Sequence[WatchlistEntry],
    short_premium: Sequence[ShortPremiumPosition],
    quotes: Dict[str, Quote],
    technicals: Dict[str, Technicals],
    earnings: Dict[str, str],
    as_of: date,
    vix_value: Optional[float],
) -> List[TradeIdea]:
    ideas: List[TradeIdea] = []
    position_by_symbol = {position.symbol: position for position in portfolio}
    watch_by_symbol = {entry.ticker: entry for entry in watchlist}
    short_put_tickers = {
        position.ticker
        for position in short_premium
        if position.option_type.lower().startswith("put")
    }
    expiration = nearest_friday(as_of)
    regime = vix_regime(vix_value)
    csp_discount = 0.08 if regime in {"ELEVATED", "CRISIS"} else 0.06

    for position in portfolio:
        if position.quantity < 100 or position.symbol in {"FFOLX"}:
            continue
        price = price_for(position.symbol, quotes, position_by_symbol)
        if price is None:
            continue
        tech = technicals.get(position.symbol, Technicals(None, None, None, None))
        weight = position.weight or 0
        rsi_value = tech.rsi14 or 50
        if weight >= 4 or rsi_value >= 62:
            call_strike = round_strike(price * (1.05 if rsi_value < 70 else 1.08), "up")
            score = 60 + min(weight, 20) + max(rsi_value - 55, 0) / 2
            risk_note = "Covered by existing shares; cap upside above strike."
            if position.symbol in short_put_tickers:
                risk_note += " Name also has open short-put exposure."
            ideas.append(
                TradeIdea(
                    rank_score=score,
                    ticker=position.symbol,
                    strategy="Covered call",
                    setup=f"{expiration.isoformat()} {format_strike(call_strike)}C against shares",
                    action="Sell only if the credit meets the portfolio's income hurdle and you are willing to trim above the strike.",
                    rationale=(
                        f"Portfolio weight {weight:.1f}% with {technical_bias(price, tech)}; "
                        f"20d change {fmt_pct(tech.change_20d_pct)}, RSI {fmt_num(tech.rsi14)}."
                    ),
                    risk=risk_note,
                )
            )

    for entry in watchlist:
        if entry.status.lower().startswith("low") or "avoid" in entry.status.lower():
            continue
        price = price_for(entry.ticker, quotes, position_by_symbol)
        if price is None:
            continue
        tech = technicals.get(entry.ticker, Technicals(None, None, None, None))
        has_near_earnings = entry.ticker in earnings
        score = entry.score or 50
        already_owned = entry.ticker in position_by_symbol
        if entry.ticker in short_put_tickers:
            continue
        short_put = round_strike(price * (1 - csp_discount), "down")
        long_put = round_strike(short_put * 0.97, "down")
        preferred_strategy = "Bull put spread" if regime in {"ELEVATED", "CRISIS"} else "Cash-secured put"
        setup = (
            f"{expiration.isoformat()} short {format_strike(short_put)}P / long {format_strike(long_put)}P"
            if preferred_strategy == "Bull put spread"
            else f"{expiration.isoformat()} {format_strike(short_put)}P cash-secured put"
        )
        concentration_note = ""
        if entry.ticker in {"LRCX", "NVDA", "TSM", "KLAC", "ASML", "AMAT", "AVGO"}:
            concentration_note = " Semi exposure is already high; prefer defined risk or smaller size."
        if has_near_earnings:
            ideas.append(
                TradeIdea(
                    rank_score=score - 8,
                    ticker=entry.ticker,
                    strategy="Watchlist setup",
                    setup=f"Wait until after earnings on {earnings[entry.ticker]}",
                    action="Keep on watchlist; avoid new short-premium entry before the event.",
                    rationale=(
                        f"{entry.grade} watchlist candidate; {technical_bias(price, tech)}; "
                        f"RSI {fmt_num(tech.rsi14)}."
                    ),
                    risk="Earnings gap risk inside the normal options window.",
                )
            )
            continue
        ideas.append(
            TradeIdea(
                rank_score=score + (8 if not already_owned else 0),
                ticker=entry.ticker,
                strategy=preferred_strategy,
                setup=setup,
                action="Enter only if bid/ask liquidity is clean and credit justifies risk.",
                rationale=(
                    f"{entry.grade} watchlist candidate ({entry.status}); {technical_bias(price, tech)}; "
                    f"20d change {fmt_pct(tech.change_20d_pct)}, RSI {fmt_num(tech.rsi14)}."
                ),
                risk=f"{regime} VIX regime; use <=5% max-risk sizing.{concentration_note}",
            )
        )

    for option in short_premium:
        price = price_for(option.ticker, quotes, position_by_symbol)
        if price is None or option.option_type.lower() != "put":
            continue
        moneyness = (price / option.strike - 1) * 100
        if moneyness < 3:
            action = "Manage existing short put"
            setup = f"{option.expiration} {format_strike(option.strike)}P, {option.contracts or 0} contracts"
            ideas.append(
                TradeIdea(
                    rank_score=78 - moneyness,
                    ticker=option.ticker,
                    strategy=action,
                    setup=setup,
                    action="Review roll/close thresholds before adding any new exposure in this name.",
                    rationale=(
                        f"Underlying is {fmt_pct(moneyness)} vs short strike; current option value "
                        f"{fmt_money(option.current)} vs entry credit {fmt_money(option.credit)}."
                    ),
                    risk="Existing short-premium risk should take priority over new entries.",
                )
            )

    unique: Dict[Tuple[str, str], TradeIdea] = {}
    for idea in sorted(ideas, key=lambda item: item.rank_score, reverse=True):
        unique.setdefault((idea.ticker, idea.strategy), idea)
    return list(unique.values())


def fmt_num(value: Optional[float], digits: int = 1) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{digits}f}"


def fmt_pct(value: Optional[float], digits: int = 1) -> str:
    if value is None:
        return "n/a"
    return f"{value:+.{digits}f}%"


def fmt_money(value: Optional[float]) -> str:
    if value is None:
        return "n/a"
    return f"${value:,.2f}"


def report_header(as_of: date, portfolio: Sequence[PortfolioPosition], watchlist: Sequence[WatchlistEntry]) -> str:
    return (
        f"# Altamira Trade Idea Generator - {as_of.isoformat()}\n\n"
        f"**Portfolio holdings parsed:** {len(portfolio)}  \n"
        f"**Watchlist tickers parsed:** {len(watchlist)}  \n"
        "**Sources:** `context/portfolio-details.md`, `context/watchlist.md`, FMP live market data when available.\n\n"
        "> For research and education only. Not investment advice. Confirm prices, deltas, liquidity, "
        "earnings dates, and account risk limits before placing trades.\n"
    )


def build_report(
    as_of: date,
    portfolio: Sequence[PortfolioPosition],
    watchlist: Sequence[WatchlistEntry],
    short_premium: Sequence[ShortPremiumPosition],
    expired_short_premium: Sequence[ShortPremiumPosition],
    quotes: Dict[str, Quote],
    technicals: Dict[str, Technicals],
    earnings: Dict[str, str],
    ideas: Sequence[TradeIdea],
    vix_value: Optional[float],
    data_mode: str,
) -> str:
    top_positions = sorted(
        [position for position in portfolio if position.weight is not None],
        key=lambda position: position.weight or 0,
        reverse=True,
    )[:8]
    lines = [report_header(as_of, portfolio, watchlist), "\n---\n\n"]
    lines.append("## Market Regime\n\n")
    lines.append(f"- **VIX:** {fmt_num(vix_value)} ({vix_regime(vix_value)})\n")
    lines.append(f"- **Data mode:** {data_mode}\n")
    if vix_regime(vix_value) in {"ELEVATED", "CRISIS"}:
        lines.append("- **Sizing note:** Prefer defined-risk spreads and reduced size.\n")
    else:
        lines.append("- **Sizing note:** CSPs and covered calls are acceptable if liquidity and risk limits pass.\n")
    if expired_short_premium:
        lines.append(
            f"- **Static options note:** Skipped {len(expired_short_premium)} expired short-premium row(s) from repository context.\n"
        )

    lines.append("\n## Top Trade Ideas\n\n")
    lines.append("| Rank | Ticker | Strategy | Setup | Action | Key Risk |\n")
    lines.append("|------|--------|----------|-------|--------|----------|\n")
    for index, idea in enumerate(ideas, start=1):
        lines.append(
            "| {rank} | {ticker} | {strategy} | {setup} | {action} | {risk} |\n".format(
                rank=index,
                ticker=idea.ticker,
                strategy=escape_cell(idea.strategy),
                setup=escape_cell(idea.setup),
                action=escape_cell(idea.action),
                risk=escape_cell(idea.risk),
            )
        )
    if not ideas:
        lines.append("| - | - | No actionable ideas | Insufficient data | Keep watchlist only | - |\n")

    lines.append("\n## Idea Rationale\n\n")
    for index, idea in enumerate(ideas, start=1):
        lines.append(f"### {index}. {idea.ticker} - {idea.strategy}\n\n")
        lines.append(f"- **Setup:** {idea.setup}\n")
        lines.append(f"- **Why:** {idea.rationale}\n")
        lines.append(f"- **Action:** {idea.action}\n")
        lines.append(f"- **Risk:** {idea.risk}\n\n")

    lines.append("## Portfolio Context\n\n")
    lines.append("| Ticker | Weight | Context price | Live price | Day change | Bias |\n")
    lines.append("|--------|--------|---------------|------------|------------|------|\n")
    position_by_symbol = {position.symbol: position for position in portfolio}
    for position in top_positions:
        quote = quotes.get(position.symbol)
        tech = technicals.get(position.symbol, Technicals(None, None, None, None))
        live_price = quote.price if quote else None
        lines.append(
            f"| {position.symbol} | {fmt_pct(position.weight, 1).replace('+', '')} | "
            f"{fmt_money(position.context_price)} | {fmt_money(live_price)} | "
            f"{fmt_pct(quote.change_pct if quote else None)} | "
            f"{technical_bias(live_price or position.context_price, tech)} |\n"
        )

    lines.append("\n## Existing Short Premium\n\n")
    lines.append("| Ticker | Position | Credit | Current | Note |\n")
    lines.append("|--------|----------|--------|---------|------|\n")
    for option in short_premium:
        price = price_for(option.ticker, quotes, position_by_symbol)
        note = "underlying unavailable"
        if price is not None and option.strike:
            note = f"underlying {fmt_pct((price / option.strike - 1) * 100)} vs strike"
        lines.append(
            f"| {option.ticker} | {option.expiration} {format_strike(option.strike)}{option.option_type[:1].upper()} "
            f"x{option.contracts or 0} | {fmt_money(option.credit)} | {fmt_money(option.current)} | {note} |\n"
        )
    if not short_premium:
        note = (
            f"No active rows parsed; skipped {len(expired_short_premium)} expired static row(s)."
            if expired_short_premium
            else "No active rows parsed."
        )
        lines.append(f"| - | - | - | - | {note} |\n")

    lines.append("\n## Watchlist Focus\n\n")
    lines.append("| Ticker | Score | Grade | Status | Live price | Bias | Earnings |\n")
    lines.append("|--------|-------|-------|--------|------------|------|----------|\n")
    for entry in watchlist[:12]:
        quote = quotes.get(entry.ticker)
        tech = technicals.get(entry.ticker, Technicals(None, None, None, None))
        price = quote.price if quote else None
        lines.append(
            f"| {entry.ticker} | {fmt_num(entry.score)} | {entry.grade} | {entry.status} | "
            f"{fmt_money(price)} | {technical_bias(price, tech)} | {earnings.get(entry.ticker, '-')} |\n"
        )

    lines.append(
        "\n## Risk Controls\n\n"
        "- Keep single-position risk within the 5% max-risk rule and options allocation within the 30% cap.\n"
        "- Do not sell new premium through known earnings unless the trade is intentionally an earnings strategy.\n"
        "- For covered calls, only sell strikes where assignment would be acceptable.\n"
        "- For model-based strikes, confirm actual deltas and credits in the broker before entry.\n"
    )
    return "".join(lines)


def escape_cell(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def build_telegram_message(
    as_of: date,
    ideas: Sequence[TradeIdea],
    vix_value: Optional[float],
    output_path: Path,
    max_ideas: int,
    expired_short_premium_count: int = 0,
) -> str:
    lines = [
        f"Altamira Trade Ideas - {as_of.isoformat()}",
        f"VIX: {fmt_num(vix_value)} ({vix_regime(vix_value)})",
        "",
    ]
    for index, idea in enumerate(ideas[:max_ideas], start=1):
        lines.extend(
            [
                f"{index}. {idea.ticker} - {idea.strategy}",
                f"Setup: {idea.setup}",
                f"Action: {idea.action}",
                f"Why: {idea.rationale}",
                f"Risk: {idea.risk}",
                "",
            ]
        )
    if not ideas:
        lines.append("No actionable ideas generated from today's available data.")
    if expired_short_premium_count:
        lines.extend(
            [
                f"Expired static option rows skipped: {expired_short_premium_count}.",
                "",
            ]
        )
    lines.extend(
        [
            "Research only; not investment advice. Confirm live chain, deltas, earnings, and risk limits.",
            f"Report: {output_path.relative_to(WORKSPACE)}",
        ]
    )
    message = "\n".join(lines)
    if len(message) > 3900:
        message = message[:3800].rsplit("\n", 1)[0] + "\n\n[Truncated; see full report.]"
    return message


def send_telegram(message: str, chat_id: str) -> Dict[str, Any]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required for Telegram delivery")
    if not chat_id:
        raise RuntimeError("Telegram chat id is required")
    payload = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"Telegram send failed: {body}") from exc


def discover_telegram_chat_id() -> Optional[str]:
    env_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if env_chat_id:
        return env_chat_id

    for path in sorted(OUTPUTS.glob("*.json")):
        try:
            data = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for match in re.finditer(r'"chatId"\s*:\s*"([^"]+)"', data):
            candidate = match.group(1).strip()
            if candidate.startswith("=") and re.fullmatch(r"=-?\d+", candidate):
                return candidate[1:]
            if candidate and not candidate.startswith("=") and "TELEGRAM_CHAT_ID" not in candidate:
                return candidate
    return None


def data_mode(api_key: Optional[str]) -> str:
    return "live FMP market data" if api_key else "context-only; FMP_API_KEY missing"


def main() -> int:
    args = parse_args()
    as_of = datetime.strptime(args.as_of, "%Y-%m-%d").date()
    portfolio_path = Path(args.portfolio)
    watchlist_path = Path(args.watchlist)
    output_path = Path(args.out) if args.out else OUTPUTS / f"trade-ideas-{as_of.isoformat()}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    portfolio = parse_portfolio(portfolio_path)
    watchlist = parse_watchlist(watchlist_path)
    parsed_short_premium = parse_short_premium(portfolio_path)
    short_premium, expired_short_premium = split_active_short_premium(parsed_short_premium, as_of)

    api_key = os.environ.get("FMP_API_KEY")
    position_symbols = [position.symbol for position in portfolio if position.symbol != "FFOLX"]
    watch_symbols = [entry.ticker for entry in watchlist]
    quote_symbols = sorted(set(position_symbols + watch_symbols + ["^VIX", "SPY", "QQQ"]))
    quotes = fetch_quotes(quote_symbols, api_key)
    vix_value = (quotes.get("^VIX") or Quote("^VIX", None, None)).price

    earnings = fetch_earnings(api_key, as_of)
    technicals: Dict[str, Technicals] = {}
    for symbol in sorted(set(position_symbols + watch_symbols)):
        history_symbol = "SPY" if symbol == "^GSPC" else symbol
        history = fetch_history(history_symbol, api_key, as_of)
        technicals[symbol] = compute_technicals(history)

    ideas = build_trade_ideas(
        portfolio=portfolio,
        watchlist=watchlist,
        short_premium=short_premium,
        quotes=quotes,
        technicals=technicals,
        earnings=earnings,
        as_of=as_of,
        vix_value=vix_value,
    )
    ideas = ideas[: max(args.max_ideas, 1)]

    report = build_report(
        as_of=as_of,
        portfolio=portfolio,
        watchlist=watchlist,
        short_premium=short_premium,
        expired_short_premium=expired_short_premium,
        quotes=quotes,
        technicals=technicals,
        earnings=earnings,
        ideas=ideas,
        vix_value=vix_value,
        data_mode=data_mode(api_key),
    )
    output_path.write_text(report, encoding="utf-8")

    telegram_message = build_telegram_message(
        as_of,
        ideas,
        vix_value,
        output_path,
        args.max_ideas,
        expired_short_premium_count=len(expired_short_premium),
    )
    print(f"Wrote {output_path}")
    if expired_short_premium:
        print(f"Skipped {len(expired_short_premium)} expired short-premium row(s)")
    print("\nTelegram preview:\n")
    print(telegram_message)

    telegram_chat_id = args.telegram_chat_id or discover_telegram_chat_id()
    if args.send_telegram and not args.dry_run:
        result = send_telegram(telegram_message, telegram_chat_id or "")
        message_id = result.get("result", {}).get("message_id")
        print(f"Telegram sent successfully; message_id={message_id}")
    elif args.send_telegram and args.dry_run:
        print("Dry run: Telegram send skipped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
