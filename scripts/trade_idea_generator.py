#!/usr/bin/env python3
"""
Trade Idea Generator for the current Altamira portfolio and watchlist.

Reads repository context files, enriches the universe with live market data, ranks
actionable trade ideas, writes a markdown report, and can send the concise
summary to Telegram.

Usage:
    python scripts/trade_idea_generator.py
    python scripts/trade_idea_generator.py --send-telegram
    python scripts/trade_idea_generator.py --send-telegram --telegram-chat-id 123456
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

try:
    import requests
except ImportError:
    print("Install requests: pip install requests", file=sys.stderr)
    sys.exit(1)


WORKSPACE = Path(__file__).resolve().parent.parent
CONTEXT = WORKSPACE / "context"
OUTPUTS = WORKSPACE / "outputs"
FMP_BASE = "https://financialmodelingprep.com/api/v3"
MASSIVE_BASE = "https://api.massive.com/v3"

DEFAULT_MAX_TELEGRAM_CHARS = 3900
OPTION_MIN_DTE = 30
OPTION_MAX_DTE = 60


@dataclass
class Position:
    ticker: str
    quantity: float
    avg_price: float | None
    current: float | None
    market_value: float | None
    weight: float | None
    pnl_pct: float | None


@dataclass
class WatchlistEntry:
    ticker: str
    score: float | None
    grade: str | None
    company: str
    status: str


@dataclass
class OptionPosition:
    ticker: str
    strike: float
    option_type: str
    expiration: str
    credit: float
    current: float
    contracts: int


@dataclass
class MarketSnapshot:
    ticker: str
    price: float | None = None
    change_pct: float | None = None
    volume: float | None = None
    avg_volume: float | None = None
    market_cap: float | None = None
    year_high: float | None = None
    year_low: float | None = None
    price_avg_50: float | None = None
    price_avg_200: float | None = None
    sma_20: float | None = None
    rsi_14: float | None = None
    return_20d: float | None = None


@dataclass
class TradeIdea:
    rank_score: float
    ticker: str
    action: str
    idea_type: str
    thesis: str
    risk: str
    details: list[str]
    source: str


def _money_to_float(value: str) -> float | None:
    cleaned = value.strip().replace("$", "").replace(",", "")
    if not cleaned or cleaned in {"-", "—"}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _percent_to_float(value: str) -> float | None:
    match = re.search(r"([-+]?\d+(?:\.\d+)?)%", value)
    if not match:
        return None
    return float(match.group(1))


def _split_md_row(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def parse_portfolio(path: Path) -> list[Position]:
    text = path.read_text(encoding="utf-8")
    positions: list[Position] = []
    in_table = False

    for line in text.splitlines():
        if line.startswith("| SYMBOL |"):
            in_table = True
            continue
        if not in_table:
            continue
        if line.startswith("|--------") or not line.startswith("|"):
            continue
        if line.startswith("**Totals:**") or line.startswith("---"):
            break

        cells = _split_md_row(line)
        if len(cells) < 9:
            continue
        ticker = cells[0].upper()
        if ticker == "SYMBOL":
            continue
        try:
            quantity = float(cells[1].replace(",", ""))
        except ValueError:
            quantity = 0.0
        positions.append(
            Position(
                ticker=ticker,
                quantity=quantity,
                avg_price=_money_to_float(cells[2]),
                current=_money_to_float(cells[3]),
                market_value=_money_to_float(cells[4]),
                weight=_percent_to_float(cells[8]),
                pnl_pct=_percent_to_float(cells[6]),
            )
        )
    return positions


def parse_watchlist(path: Path) -> list[WatchlistEntry]:
    text = path.read_text(encoding="utf-8")
    entries: list[WatchlistEntry] = []
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
        cells = _split_md_row(line)
        if len(cells) < 5:
            continue
        score = None
        if cells[1] not in {"—", "-", ""}:
            try:
                score = float(cells[1])
            except ValueError:
                score = None
        grade = cells[2].replace("**", "").strip() or None
        entries.append(
            WatchlistEntry(
                ticker=cells[0].upper(),
                score=score,
                grade=grade,
                company=cells[3],
                status=cells[4],
            )
        )
    return entries


def parse_options(path: Path) -> list[OptionPosition]:
    text = path.read_text(encoding="utf-8")
    options: list[OptionPosition] = []
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
        cells = _split_md_row(line)
        if len(cells) < 7:
            continue
        try:
            options.append(
                OptionPosition(
                    ticker=cells[0].upper(),
                    strike=float(cells[1]),
                    option_type=cells[2],
                    expiration=cells[3],
                    credit=float(cells[4]),
                    current=float(cells[5]),
                    contracts=int(float(cells[6])),
                )
            )
        except ValueError:
            continue
    return options


def get_fmp_key() -> str | None:
    if os.environ.get("FMP_API_KEY"):
        return os.environ["FMP_API_KEY"]
    scripts_dir = str(WORKSPACE / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    try:
        from company_growth_metrics import FMP_API_KEY  # type: ignore

        return FMP_API_KEY
    except Exception:
        return None


def get_massive_key() -> str | None:
    if os.environ.get("MASSIVE_API_KEY"):
        return os.environ["MASSIVE_API_KEY"]
    workflow_path = OUTPUTS / "n8n-workflow-csp-daily-scan.json"
    try:
        text = workflow_path.read_text(encoding="utf-8")
    except OSError:
        return None
    match = re.search(r"const MASSIVE_API_KEY = '([^']+)'", text)
    return match.group(1) if match else None


def batched(items: list[str], size: int) -> Iterable[list[str]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def fmp_get_json(url: str, *, timeout: int = 15) -> Any:
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def fetch_quotes(tickers: list[str], fmp_key: str) -> dict[str, MarketSnapshot]:
    snapshots: dict[str, MarketSnapshot] = {}
    for chunk in batched(tickers, 60):
        joined = ",".join(chunk)
        url = f"{FMP_BASE}/quote/{joined}?apikey={fmp_key}"
        try:
            data = fmp_get_json(url)
        except Exception as exc:
            print(f"Warning: quote fetch failed for {joined}: {exc}", file=sys.stderr)
            continue
        if not isinstance(data, list):
            continue
        for q in data:
            ticker = str(q.get("symbol", "")).upper()
            if not ticker:
                continue
            snapshots[ticker] = MarketSnapshot(
                ticker=ticker,
                price=_to_float(q.get("price")),
                change_pct=_to_float(q.get("changesPercentage")),
                volume=_to_float(q.get("volume")),
                avg_volume=_to_float(q.get("avgVolume")),
                market_cap=_to_float(q.get("marketCap")),
                year_high=_to_float(q.get("yearHigh")),
                year_low=_to_float(q.get("yearLow")),
                price_avg_50=_to_float(q.get("priceAvg50")),
                price_avg_200=_to_float(q.get("priceAvg200")),
            )
    return snapshots


def fetch_historical(snapshot: MarketSnapshot, fmp_key: str) -> None:
    ticker = snapshot.ticker
    url = f"{FMP_BASE}/historical-price-full/{ticker}?timeseries=90&apikey={fmp_key}"
    try:
        data = fmp_get_json(url)
    except Exception as exc:
        print(f"Warning: historical fetch failed for {ticker}: {exc}", file=sys.stderr)
        return
    prices_raw = data.get("historical") if isinstance(data, dict) else None
    if not isinstance(prices_raw, list) or len(prices_raw) < 20:
        return

    closes = [float(row["close"]) for row in prices_raw if row.get("close") is not None]
    # FMP returns newest first.
    if len(closes) >= 20:
        snapshot.sma_20 = sum(closes[:20]) / 20
        if closes[19] != 0:
            snapshot.return_20d = (closes[0] / closes[19] - 1) * 100
    if len(closes) >= 15:
        snapshot.rsi_14 = calc_rsi(list(reversed(closes[:15])))


def calc_rsi(prices_oldest_first: list[float], period: int = 14) -> float | None:
    if len(prices_oldest_first) < period + 1:
        return None
    gains = 0.0
    losses = 0.0
    for prev, curr in zip(prices_oldest_first[-period - 1 : -1], prices_oldest_first[-period:]):
        diff = curr - prev
        if diff >= 0:
            gains += diff
        else:
            losses -= diff
    if losses == 0:
        return 100.0
    rs = gains / losses
    return 100 - (100 / (1 + rs))


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return f


def fetch_earnings(tickers: set[str], fmp_key: str) -> dict[str, str]:
    today = date.today()
    end = today + timedelta(days=45)
    url = f"{FMP_BASE}/earning_calendar?from={today.isoformat()}&to={end.isoformat()}&apikey={fmp_key}"
    earnings: dict[str, str] = {}
    try:
        data = fmp_get_json(url, timeout=20)
    except Exception as exc:
        print(f"Warning: earnings calendar fetch failed: {exc}", file=sys.stderr)
        return earnings
    if not isinstance(data, list):
        return earnings
    for row in data:
        ticker = str(row.get("symbol", "")).upper()
        if ticker in tickers and row.get("date"):
            earnings[ticker] = str(row["date"])
    return earnings


def fetch_vix(fmp_key: str) -> tuple[float | None, str, int]:
    try:
        data = fmp_get_json(f"{FMP_BASE}/quote/%5EVIX?apikey={fmp_key}")
        value = _to_float(data[0].get("price")) if isinstance(data, list) and data else None
    except Exception as exc:
        print(f"Warning: VIX fetch failed: {exc}", file=sys.stderr)
        value = None

    if value is None:
        return None, "UNKNOWN", 50
    if value < 15:
        return value, "LOW", 75
    if value <= 25:
        return value, "NORMAL", 100
    if value <= 35:
        return value, "ELEVATED", 50
    return value, "CRISIS", 25


def fetch_option_candidates(
    ticker: str,
    spot: float,
    option_type: str,
    massive_key: str | None,
) -> list[dict[str, Any]]:
    if not massive_key:
        return []
    today = date.today()
    start = today + timedelta(days=OPTION_MIN_DTE)
    end = today + timedelta(days=OPTION_MAX_DTE)
    url = (
        f"{MASSIVE_BASE}/snapshot/options/{ticker}"
        f"?contract_type={option_type}"
        f"&expiration_date.gte={start.isoformat()}"
        f"&expiration_date.lte={end.isoformat()}"
        f"&limit=250&apiKey={massive_key}"
    )
    try:
        data = fmp_get_json(url, timeout=20)
    except Exception as exc:
        print(f"Warning: option chain failed for {ticker} {option_type}: {exc}", file=sys.stderr)
        return []

    rows = data.get("results") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        return []

    candidates: list[dict[str, Any]] = []
    for raw in rows:
        details = raw.get("details") or {}
        quote = raw.get("last_quote") or {}
        greeks = raw.get("greeks") or {}
        day = raw.get("day") or {}
        strike = _to_float(details.get("strike_price"))
        expiration = details.get("expiration_date")
        bid = _to_float(quote.get("bid"))
        ask = _to_float(quote.get("ask"))
        delta = _to_float(greeks.get("delta"))
        oi = _to_float(raw.get("open_interest")) or 0
        volume = _to_float(day.get("volume")) or 0
        iv = _to_float(raw.get("implied_volatility"))
        theta = _to_float(greeks.get("theta"))
        if not strike or not expiration or not bid or bid <= 0 or ask is None:
            continue
        dte = (datetime.fromisoformat(expiration).date() - today).days
        if dte < OPTION_MIN_DTE or dte > OPTION_MAX_DTE:
            continue
        abs_delta = abs(delta or 0)
        if abs_delta < 0.18 or abs_delta > 0.32:
            continue
        mid = (bid + ask) / 2
        if mid <= 0:
            continue
        spread_pct = (ask - bid) / mid * 100
        if spread_pct > 20 or oi < 25:
            continue

        if option_type == "put":
            otm_pct = (spot - strike) / spot * 100
            annualized = (bid / strike) * (365 / max(dte, 1)) * 100
            breakeven = strike - bid
            delta_fit = 100 - abs(abs_delta - 0.25) * 250
            score = annualized * 1.6 + min(oi / 25, 30) + max(0, 20 - spread_pct) + delta_fit * 0.2
        else:
            otm_pct = (strike - spot) / spot * 100
            annualized = (bid / spot) * (365 / max(dte, 1)) * 100
            breakeven = strike + bid
            delta_fit = 100 - abs(abs_delta - 0.25) * 250
            score = annualized * 1.3 + min(oi / 25, 30) + max(0, 20 - spread_pct) + delta_fit * 0.2

        candidates.append(
            {
                "ticker": ticker,
                "type": option_type,
                "strike": strike,
                "expiration": expiration,
                "dte": dte,
                "bid": bid,
                "ask": ask,
                "mid": mid,
                "delta": delta,
                "iv": iv,
                "theta": theta,
                "open_interest": int(oi),
                "volume": int(volume),
                "spread_pct": spread_pct,
                "otm_pct": otm_pct,
                "annualized": annualized,
                "breakeven": breakeven,
                "score": score,
            }
        )
    return sorted(candidates, key=lambda c: c["score"], reverse=True)


def trend_label(snapshot: MarketSnapshot) -> str:
    if snapshot.price is None:
        return "No quote"
    bullish_checks = 0
    total = 0
    for avg in (snapshot.sma_20, snapshot.price_avg_50, snapshot.price_avg_200):
        if avg:
            total += 1
            bullish_checks += 1 if snapshot.price > avg else 0
    if total == 0:
        return "Trend unavailable"
    if bullish_checks == total:
        return "Uptrend"
    if bullish_checks == 0:
        return "Downtrend"
    return "Mixed trend"


def build_trade_ideas(
    positions: list[Position],
    watchlist: list[WatchlistEntry],
    open_options: list[OptionPosition],
    snapshots: dict[str, MarketSnapshot],
    earnings: dict[str, str],
    massive_key: str | None,
    vix_regime: str,
    sizing_pct: int,
) -> list[TradeIdea]:
    ideas: list[TradeIdea] = []
    held = {p.ticker: p for p in positions}
    expired_option_details: list[str] = []

    for opt in open_options:
        snap = snapshots.get(opt.ticker, MarketSnapshot(opt.ticker))
        stop = opt.credit * 2
        profit_target = opt.credit * 0.5
        value_per_contract = opt.current * 100
        total_current_value = value_per_contract * opt.contracts
        dte = None
        try:
            dte = (datetime.fromisoformat(opt.expiration).date() - date.today()).days
        except ValueError:
            pass

        if dte is not None and dte < 0:
            expired_option_details.append(
                f"{opt.ticker} {opt.strike:g}{opt.option_type[0].upper()} expired {opt.expiration} "
                f"(credit ${opt.credit:.2f}, stale mark ${opt.current:.2f}, contracts {opt.contracts})"
            )
            continue

        if opt.current >= stop:
            ideas.append(
                TradeIdea(
                    rank_score=96,
                    ticker=opt.ticker,
                    action="ROLL / CLOSE RISK",
                    idea_type="Existing short put management",
                    thesis=(
                        f"{opt.ticker} {opt.strike:g}P is marked at ${opt.current:.2f}, "
                        f"above the 2x credit stop (${stop:.2f})."
                    ),
                    risk="This position is beyond the stated stop discipline; reassess assignment intent before adding new risk.",
                    details=[
                        f"Expiration: {opt.expiration} ({dte} DTE)" if dte is not None else f"Expiration: {opt.expiration}",
                        f"Credit: ${opt.credit:.2f}; current mark: ${opt.current:.2f}; contracts: {opt.contracts}",
                        f"Current option liability: about ${total_current_value:,.0f}",
                        f"Underlying: ${snap.price:.2f} ({trend_label(snap)})" if snap.price else "Underlying quote unavailable",
                    ],
                    source="context/options-positions.md",
                )
            )
        elif opt.current <= profit_target:
            ideas.append(
                TradeIdea(
                    rank_score=88,
                    ticker=opt.ticker,
                    action="CLOSE TO LOCK PROFIT",
                    idea_type="Existing short put management",
                    thesis=(
                        f"{opt.ticker} {opt.strike:g}P has reached the 50% profit rule "
                        f"(${opt.current:.2f} <= ${profit_target:.2f})."
                    ),
                    risk="Keeping the position open leaves residual tail risk for limited remaining premium.",
                    details=[
                        f"Expiration: {opt.expiration} ({dte} DTE)" if dte is not None else f"Expiration: {opt.expiration}",
                        f"Credit: ${opt.credit:.2f}; close threshold: ${profit_target:.2f}; contracts: {opt.contracts}",
                        f"Potential debit to close: about ${total_current_value:,.0f}",
                    ],
                    source="context/options-positions.md",
                )
            )

    if expired_option_details:
        ideas.append(
            TradeIdea(
                rank_score=94,
                ticker="OPTIONS",
                action="REFRESH EXPIRED OPTIONS CONTEXT",
                idea_type="Data hygiene / risk control",
                thesis=(
                    "The repository still lists expired short-premium contracts. Verify broker status "
                    "before relying on option marks or adding replacement risk."
                ),
                risk="Expired or stale option records can create false roll/close signals and distort buying-power estimates.",
                details=expired_option_details[:5],
                source="context/options-positions.md",
            )
        )

    top_watchlist = [
        w
        for w in watchlist
        if (w.score or 0) >= 58 and w.ticker not in held and w.ticker in snapshots
    ][:8]

    for entry in top_watchlist:
        if entry.ticker in earnings:
            ideas.append(
                TradeIdea(
                    rank_score=55 + (entry.score or 0) / 10,
                    ticker=entry.ticker,
                    action="WATCH, AVOID NEW OPTIONS THROUGH EARNINGS",
                    idea_type="Watchlist event risk",
                    thesis=f"{entry.ticker} is a top watchlist candidate ({entry.grade}, score {entry.score}) but has earnings on {earnings[entry.ticker]}.",
                    risk="Short premium through earnings introduces binary gap risk and violates the workspace rule to avoid unplanned earnings exposure.",
                    details=[
                        f"Status: {entry.status}",
                        f"Trend: {trend_label(snapshots[entry.ticker])}",
                    ],
                    source="context/watchlist.md + FMP earnings calendar",
                )
            )
            continue

        snap = snapshots[entry.ticker]
        if snap.price is None:
            continue
        put_candidates = fetch_option_candidates(entry.ticker, snap.price, "put", massive_key)
        best_put = put_candidates[0] if put_candidates else None
        trend_bonus = 8 if trend_label(snap) == "Uptrend" else 0
        score = 70 + (entry.score or 0) / 3 + trend_bonus
        if best_put:
            ideas.append(
                TradeIdea(
                    rank_score=score,
                    ticker=entry.ticker,
                    action="CONSIDER CSP / BULL PUT SPREAD",
                    idea_type="New watchlist premium idea",
                    thesis=(
                        f"{entry.ticker} is a top-ranked watchlist name ({entry.grade}, score {entry.score}) "
                        f"with {trend_label(snap).lower()} and no earnings conflict in the next 45 days."
                    ),
                    risk=(
                        f"VIX regime is {vix_regime}; use {sizing_pct}% regime sizing and prefer defined risk if spread/liquidity worsens."
                    ),
                    details=[
                        f"Underlying: ${snap.price:.2f}; RSI: {_fmt_num(snap.rsi_14, 1)}; 20D return: {_fmt_pct(snap.return_20d)}",
                        (
                            f"Candidate: sell {best_put['expiration']} ${best_put['strike']:.0f}P "
                            f"for about ${best_put['bid']:.2f} bid ({best_put['dte']} DTE, "
                            f"delta {_fmt_num(best_put['delta'], 2)}, OTM {_fmt_pct(best_put['otm_pct'])})"
                        ),
                        f"Breakeven: ${best_put['breakeven']:.2f}; annualized credit yield: {best_put['annualized']:.1f}%",
                        f"Liquidity: OI {best_put['open_interest']:,}, vol {best_put['volume']:,}, spread {best_put['spread_pct']:.1f}%",
                    ],
                    source="context/watchlist.md + Massive options snapshot",
                )
            )
        else:
            ideas.append(
                TradeIdea(
                    rank_score=score - 10,
                    ticker=entry.ticker,
                    action="WATCH FOR PUT-SELLING ENTRY",
                    idea_type="New watchlist premium idea",
                    thesis=(
                        f"{entry.ticker} is a top-ranked watchlist name ({entry.grade}, score {entry.score}) "
                        f"but no clean 30-60 DTE 0.20-0.30 delta put was available from the chain snapshot."
                    ),
                    risk="Manual chain check required before entry; avoid forcing illiquid contracts.",
                    details=[
                        f"Underlying: ${snap.price:.2f}; trend: {trend_label(snap)}; RSI: {_fmt_num(snap.rsi_14, 1)}",
                        "Target manual setup: 30-45 DTE, 0.20-0.30 delta, spread under 10%, OI above 100.",
                    ],
                    source="context/watchlist.md + FMP quote",
                )
            )

    covered_call_candidates = [
        p
        for p in positions
        if p.quantity >= 100
        and p.ticker in snapshots
        and p.ticker not in {"SPY", "QQQ", "FFOLX"}
        and (p.pnl_pct or 0) > 20
    ]
    covered_call_candidates.sort(key=lambda p: (p.weight or 0, p.pnl_pct or 0), reverse=True)

    for pos in covered_call_candidates[:5]:
        snap = snapshots[pos.ticker]
        if snap.price is None or pos.ticker in earnings:
            continue
        is_overweight = (pos.weight or 0) >= 4
        is_extended = (snap.rsi_14 or 50) >= 60 or (
            snap.year_high and snap.price >= snap.year_high * 0.95
        )
        if not is_overweight and not is_extended:
            continue
        call_candidates = fetch_option_candidates(pos.ticker, snap.price, "call", massive_key)
        best_call = call_candidates[0] if call_candidates else None
        if not best_call:
            continue
        ideas.append(
            TradeIdea(
                rank_score=72 + min(pos.weight or 0, 15) + min((snap.rsi_14 or 50) / 10, 8),
                ticker=pos.ticker,
                action="CONSIDER COVERED CALL",
                idea_type="Portfolio income / trim discipline",
                thesis=(
                    f"{pos.ticker} is a profitable existing holding ({_fmt_pct(pos.pnl_pct)} P&L, "
                    f"{_fmt_pct(pos.weight)} portfolio weight) and can fund income while enforcing a trim level."
                ),
                risk="Covered calls cap upside; avoid selling below a price where you are comfortable trimming shares.",
                details=[
                    f"Underlying: ${snap.price:.2f}; RSI: {_fmt_num(snap.rsi_14, 1)}; trend: {trend_label(snap)}",
                    (
                        f"Candidate: sell {best_call['expiration']} ${best_call['strike']:.0f}C "
                        f"for about ${best_call['bid']:.2f} bid ({best_call['dte']} DTE, "
                        f"delta {_fmt_num(best_call['delta'], 2)}, OTM {_fmt_pct(best_call['otm_pct'])})"
                    ),
                    f"Income yield on shares: {best_call['annualized']:.1f}% annualized; OI {best_call['open_interest']:,}",
                ],
                source="context/portfolio-details.md + Massive options snapshot",
            )
        )

    ideas.sort(key=lambda idea: idea.rank_score, reverse=True)
    return ideas


def _fmt_num(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "N/A"
    return f"{value:.{digits}f}"


def _fmt_pct(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:+.1f}%"


def render_report(
    positions: list[Position],
    watchlist: list[WatchlistEntry],
    open_options: list[OptionPosition],
    snapshots: dict[str, MarketSnapshot],
    earnings: dict[str, str],
    ideas: list[TradeIdea],
    vix: float | None,
    vix_regime: str,
    sizing_pct: int,
) -> str:
    generated = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    top_positions = sorted(positions, key=lambda p: p.weight or 0, reverse=True)[:8]
    top_watchlist = watchlist[:8]

    lines = [
        f"# Trade Idea Generator — {date.today().isoformat()}",
        "",
        f"**Generated:** {generated}",
        "",
        "> Informational scan only, not investment advice or trade execution. Verify live prices, liquidity, account risk, and tax implications before placing any order.",
        "",
        "## Market Regime",
        "",
        f"- **VIX:** {_fmt_num(vix, 1)} ({vix_regime})",
        f"- **Regime sizing:** {sizing_pct}% of normal options size",
        f"- **Universe:** {len(positions)} portfolio holdings, {len(watchlist)} watchlist names, {len(open_options)} open short-premium positions",
        "",
        "## Top Trade Ideas",
        "",
    ]

    if not ideas:
        lines.extend(
            [
                "No qualifying trade ideas were generated from the current rules.",
                "",
            ]
        )
    for idx, idea in enumerate(ideas[:8], start=1):
        lines.extend(
            [
                f"### {idx}. {idea.ticker} — {idea.action}",
                "",
                f"- **Type:** {idea.idea_type}",
                f"- **Thesis:** {idea.thesis}",
                f"- **Risk:** {idea.risk}",
                f"- **Source:** {idea.source}",
                "- **Details:**",
            ]
        )
        lines.extend(f"  - {detail}" for detail in idea.details)
        lines.append("")

    lines.extend(
        [
            "## Current Portfolio Snapshot",
            "",
            "| Ticker | Weight | P&L % | Live Price | Trend | RSI | 20D Return |",
            "|--------|--------|-------|------------|-------|-----|------------|",
        ]
    )
    for pos in top_positions:
        snap = snapshots.get(pos.ticker, MarketSnapshot(pos.ticker))
        lines.append(
            f"| {pos.ticker} | {_fmt_pct(pos.weight)} | {_fmt_pct(pos.pnl_pct)} | "
            f"{('$' + format(snap.price, ',.2f')) if snap.price else 'N/A'} | "
            f"{trend_label(snap)} | {_fmt_num(snap.rsi_14, 1)} | {_fmt_pct(snap.return_20d)} |"
        )

    lines.extend(
        [
            "",
            "## Watchlist Leaders",
            "",
            "| Ticker | Score | Grade | Status | Live Price | Trend | Earnings Next 45D |",
            "|--------|-------|-------|--------|------------|-------|-------------------|",
        ]
    )
    for entry in top_watchlist:
        snap = snapshots.get(entry.ticker, MarketSnapshot(entry.ticker))
        lines.append(
            f"| {entry.ticker} | {entry.score if entry.score is not None else 'N/A'} | "
            f"{entry.grade or 'N/A'} | {entry.status} | "
            f"{('$' + format(snap.price, ',.2f')) if snap.price else 'N/A'} | "
            f"{trend_label(snap)} | {earnings.get(entry.ticker, 'None found')} |"
        )

    lines.extend(
        [
            "",
            "## Existing Short Premium Checks",
            "",
            "| Ticker | Contract | Expiration | Credit | Current | Rule Status |",
            "|--------|----------|------------|--------|---------|-------------|",
        ]
    )
    for opt in open_options:
        status = "Monitor"
        if opt.current >= opt.credit * 2:
            status = "Beyond 2x stop"
        elif opt.current <= opt.credit * 0.5:
            status = "At/through 50% profit target"
        lines.append(
            f"| {opt.ticker} | {opt.strike:g}{opt.option_type[0].upper()} | {opt.expiration} | "
            f"${opt.credit:.2f} | ${opt.current:.2f} | {status} |"
        )

    lines.extend(
        [
            "",
            "## Execution Checklist",
            "",
            "- Confirm real-time bid/ask and open interest before any trade.",
            "- Keep single-position risk within the portfolio risk framework.",
            "- Do not sell new short premium through unplanned earnings.",
            "- Use the workspace management rules: close at 50% profit; stop or roll at 200% of credit.",
            "",
        ]
    )
    return "\n".join(lines)


def render_telegram_message(
    ideas: list[TradeIdea],
    vix: float | None,
    vix_regime: str,
    sizing_pct: int,
    output_path: Path,
    max_chars: int = DEFAULT_MAX_TELEGRAM_CHARS,
) -> str:
    lines = [
        f"TRADE IDEA GENERATOR -- {date.today().isoformat()}",
        f"VIX: {_fmt_num(vix, 1)} ({vix_regime}) | Options sizing: {sizing_pct}%",
        "",
    ]
    if not ideas:
        lines.append("No qualifying ideas generated today.")
    else:
        for idx, idea in enumerate(ideas[:5], start=1):
            lines.extend(
                [
                    f"{idx}. {idea.ticker} -- {idea.action}",
                    f"   {idea.thesis}",
                    f"   Risk: {idea.risk}",
                ]
            )
            if idea.details:
                lines.append(f"   Setup: {idea.details[0]}")
                if len(idea.details) > 1:
                    lines.append(f"   {idea.details[1]}")
            lines.append("")

    lines.extend(
        [
            "Informational scan only; verify live market data before trading.",
            f"Report: {output_path.as_posix()}",
        ]
    )
    message = "\n".join(lines)
    if len(message) <= max_chars:
        return message
    return message[: max_chars - 80].rstrip() + "\n\n...truncated; see report for full details."


def discover_telegram_chat_id() -> str | None:
    for env_name in ("TELEGRAM_CHAT_ID", "TELEGRAM_CHANNEL_ID"):
        value = os.environ.get(env_name)
        if value:
            return value

    candidates = [
        OUTPUTS / "csp-daily-scan-fixed.json",
        OUTPUTS / "n8n-workflow-csp-daily-scan.json",
        OUTPUTS / "n8n-workflow-watchlist-alert-system.json",
    ]
    for path in candidates:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        matches = re.findall(r'"chatId"\s*:\s*"(?:=)?(-?\d+)"', text)
        if matches:
            return matches[0]
    return None


def send_telegram_message(token: str, chat_id: str, text: str) -> dict[str, Any]:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True,
    }
    resp = requests.post(url, json=payload, timeout=20)
    try:
        body = resp.json()
    except ValueError:
        body = {"ok": False, "description": resp.text}
    if not resp.ok or not body.get("ok"):
        raise RuntimeError(f"Telegram send failed: HTTP {resp.status_code} {body}")
    return body


def run(args: argparse.Namespace) -> int:
    OUTPUTS.mkdir(exist_ok=True)
    fmp_key = get_fmp_key()
    if not fmp_key:
        print("FMP API key is required (set FMP_API_KEY).", file=sys.stderr)
        return 2
    massive_key = get_massive_key()

    positions = parse_portfolio(CONTEXT / "portfolio-details.md")
    watchlist = parse_watchlist(CONTEXT / "watchlist.md")
    open_options = parse_options(CONTEXT / "options-positions.md")

    universe = sorted({p.ticker for p in positions} | {w.ticker for w in watchlist} | {o.ticker for o in open_options})
    snapshots = fetch_quotes(universe + ["^VIX"], fmp_key)
    for ticker in universe:
        if ticker in snapshots:
            fetch_historical(snapshots[ticker], fmp_key)
    earnings = fetch_earnings(set(universe), fmp_key)
    vix, vix_regime, sizing_pct = fetch_vix(fmp_key)

    ideas = build_trade_ideas(
        positions=positions,
        watchlist=watchlist,
        open_options=open_options,
        snapshots=snapshots,
        earnings=earnings,
        massive_key=massive_key,
        vix_regime=vix_regime,
        sizing_pct=sizing_pct,
    )

    output_path = OUTPUTS / f"trade-idea-generator-{date.today().isoformat()}.md"
    report = render_report(
        positions=positions,
        watchlist=watchlist,
        open_options=open_options,
        snapshots=snapshots,
        earnings=earnings,
        ideas=ideas,
        vix=vix,
        vix_regime=vix_regime,
        sizing_pct=sizing_pct,
    )
    output_path.write_text(report + "\n", encoding="utf-8")

    telegram_message = render_telegram_message(
        ideas=ideas,
        vix=vix,
        vix_regime=vix_regime,
        sizing_pct=sizing_pct,
        output_path=output_path,
    )

    telegram_path = OUTPUTS / f"trade-idea-generator-telegram-{date.today().isoformat()}.txt"
    telegram_path.write_text(telegram_message + "\n", encoding="utf-8")

    print(f"Wrote report: {output_path}")
    print(f"Wrote Telegram message: {telegram_path}")
    print("")
    print(telegram_message)

    if args.send_telegram:
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not token:
            print("TELEGRAM_BOT_TOKEN is required to send Telegram.", file=sys.stderr)
            return 2
        chat_id = args.telegram_chat_id or discover_telegram_chat_id()
        if not chat_id:
            print("Telegram chat ID not found. Set TELEGRAM_CHAT_ID or pass --telegram-chat-id.", file=sys.stderr)
            return 2
        result = send_telegram_message(token, chat_id, telegram_message)
        msg_id = result.get("result", {}).get("message_id")
        print(f"Telegram sent successfully (message_id={msg_id}).")

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate portfolio/watchlist trade ideas and optionally send to Telegram.")
    parser.add_argument("--send-telegram", action="store_true", help="Send the concise summary to Telegram.")
    parser.add_argument("--telegram-chat-id", help="Telegram chat/channel ID. Defaults to env or existing workflow config.")
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(run(parse_args()))
