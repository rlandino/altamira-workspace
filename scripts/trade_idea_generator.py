#!/usr/bin/env python3
"""Generate portfolio/watchlist trade ideas and optionally send them to Telegram."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib import error, parse, request


FMP_API_KEY = os.environ.get("FMP_API_KEY", "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz")
DEFAULT_TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "7830722515")
ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_PATH = ROOT / "context" / "portfolio-details.md"
WATCHLIST_PATH = ROOT / "context" / "watchlist.md"
OUTPUT_DIR = ROOT / "outputs"


@dataclass
class Position:
    ticker: str
    quantity: float
    avg_price: float
    current: float
    market_value: float
    weight: float
    pnl_pct: float | None


@dataclass
class WatchlistEntry:
    ticker: str
    score: float | None
    grade: str
    company: str
    status: str


@dataclass
class OptionPosition:
    ticker: str
    strike: float
    option_type: str
    expiration: date
    credit: float
    current: float
    contracts: int


def clean_number(value: str) -> float:
    value = value.replace("$", "").replace(",", "").replace("%", "").strip()
    if value in {"", "-", "--", "\u2014"}:
        return 0.0
    return float(value)


def parse_pct_from_cell(value: str) -> float | None:
    match = re.search(r"\(([+-]?\d+(?:\.\d+)?)%\)", value)
    if not match:
        return None
    return float(match.group(1))


def table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_portfolio(path: Path) -> tuple[list[Position], list[OptionPosition]]:
    positions: list[Position] = []
    options: list[OptionPosition] = []
    section = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("## Current Positions"):
            section = "positions"
            continue
        if line.startswith("## Options / Short Premium Positions"):
            section = "options"
            continue
        if line.startswith("---"):
            if section in {"positions", "options"}:
                section = None
            continue
        if not line.startswith("|") or "---" in line or line.startswith("| SYMBOL") or line.startswith("| Ticker"):
            continue

        cells = table_cells(line)
        if section == "positions" and len(cells) >= 9 and cells[0] != "Totals:":
            try:
                positions.append(
                    Position(
                        ticker=cells[0],
                        quantity=clean_number(cells[1]),
                        avg_price=clean_number(cells[2]),
                        current=clean_number(cells[3]),
                        market_value=clean_number(cells[4]),
                        weight=clean_number(cells[8]),
                        pnl_pct=parse_pct_from_cell(cells[6]),
                    )
                )
            except ValueError:
                continue
        elif section == "options" and len(cells) >= 7:
            try:
                options.append(
                    OptionPosition(
                        ticker=cells[0],
                        strike=clean_number(cells[1]),
                        option_type=cells[2],
                        expiration=datetime.strptime(cells[3], "%Y-%m-%d").date(),
                        credit=clean_number(cells[4]),
                        current=clean_number(cells[5]),
                        contracts=int(clean_number(cells[6])),
                    )
                )
            except ValueError:
                continue

    return positions, options


def parse_watchlist(path: Path) -> list[WatchlistEntry]:
    entries: list[WatchlistEntry] = []
    in_table = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("| Ticker |"):
            in_table = True
            continue
        if in_table and (not line.startswith("|") or line.startswith("---")):
            break
        if not in_table or "---" in line:
            continue
        cells = table_cells(line)
        if len(cells) < 5:
            continue
        score = None if cells[1] in {"—", "-", ""} else float(cells[1])
        grade = re.sub(r"[*`]", "", cells[2]).strip()
        status = cells[4].replace("\u2b50", "").strip()
        entries.append(WatchlistEntry(cells[0], score, grade, cells[3], status))
    return entries


def fetch_json(url: str, timeout: int = 12) -> Any:
    with request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fmp(path: str, params: dict[str, str] | None = None) -> Any:
    params = dict(params or {})
    params["apikey"] = FMP_API_KEY
    url = f"https://financialmodelingprep.com/api/v3/{path.lstrip('/')}?{parse.urlencode(params)}"
    return fetch_json(url)


def fetch_quote_batch(tickers: list[str]) -> dict[str, dict[str, Any]]:
    quotes: dict[str, dict[str, Any]] = {}
    for i in range(0, len(tickers), 40):
        batch = ",".join(tickers[i : i + 40])
        try:
            data = fmp(f"quote/{batch}")
        except (error.URLError, TimeoutError, json.JSONDecodeError):
            continue
        if isinstance(data, list):
            for row in data:
                symbol = str(row.get("symbol", "")).upper()
                if symbol:
                    quotes[symbol] = row
    return quotes


def fetch_history(ticker: str, lookback_days: int = 140) -> list[dict[str, Any]]:
    end = date.today()
    start = end - timedelta(days=lookback_days)
    try:
        data = fmp(
            f"historical-price-full/{ticker}",
            {"from": start.isoformat(), "to": end.isoformat()},
        )
    except (error.URLError, TimeoutError, json.JSONDecodeError):
        return []
    rows = data.get("historical", []) if isinstance(data, dict) else []
    return list(reversed(rows))


def moving_average(values: list[float], period: int) -> float | None:
    if len(values) < period:
        return None
    return sum(values[-period:]) / period


def rsi(values: list[float], period: int = 14) -> float | None:
    if len(values) <= period:
        return None
    gains = []
    losses = []
    for previous, current in zip(values[-period - 1 : -1], values[-period:]):
        change = current - previous
        gains.append(max(change, 0))
        losses.append(abs(min(change, 0)))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def pct_change(values: list[float], periods: int) -> float | None:
    if len(values) <= periods or values[-periods - 1] == 0:
        return None
    return (values[-1] / values[-periods - 1] - 1) * 100


def technicals_for(tickers: list[str]) -> dict[str, dict[str, float | None]]:
    result: dict[str, dict[str, float | None]] = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_history, ticker): ticker for ticker in tickers}
        for future in as_completed(futures):
            ticker = futures[future]
            rows = future.result()
            closes = [float(row.get("close", 0) or 0) for row in rows if row.get("close")]
            result[ticker] = {
                "sma20": moving_average(closes, 20),
                "sma50": moving_average(closes, 50),
                "rsi14": rsi(closes),
                "ret20": pct_change(closes, 20),
                "ret60": pct_change(closes, 60),
            }
    return result


def fmt_money(value: float | None) -> str:
    if value is None or math.isnan(value):
        return "n/a"
    return f"${value:,.2f}"


def fmt_pct(value: float | None) -> str:
    if value is None or math.isnan(value):
        return "n/a"
    return f"{value:+.1f}%"


def action_score_for_watchlist(entry: WatchlistEntry, tech: dict[str, float | None], quote: dict[str, Any]) -> tuple[int, str, str]:
    price = float(quote.get("price") or 0)
    sma20 = tech.get("sma20")
    sma50 = tech.get("sma50")
    current_rsi = tech.get("rsi14")
    ret20 = tech.get("ret20")
    score = entry.score or 0

    momentum_ok = price and sma20 and sma50 and price > sma20 > sma50 and (current_rsi or 0) < 72 and (ret20 or 0) > 0
    pullback_ok = price and sma50 and price > sma50 and current_rsi is not None and 40 <= current_rsi <= 55
    high_grade = entry.grade in {"A+", "A", "A-", "B+", "B", "B-"} or score >= 60

    if high_grade and momentum_ok:
        return (85 + int(score // 10), "CONSIDER STARTER / CSP", "quality watchlist name with constructive trend")
    if high_grade and pullback_ok:
        return (76 + int(score // 10), "WATCH PULLBACK ENTRY", "quality watchlist name near a healthier RSI zone")
    if high_grade:
        return (65 + int(score // 10), "WATCHLIST", "quality score is attractive; wait for better price action")
    return (45 + int(score // 10), "LOW PRIORITY", "score/status does not clear the current quality hurdle")


def generate_ideas(
    positions: list[Position],
    options: list[OptionPosition],
    watchlist: list[WatchlistEntry],
    quotes: dict[str, dict[str, Any]],
    technicals: dict[str, dict[str, float | None]],
) -> tuple[list[dict[str, Any]], list[str]]:
    holdings = {position.ticker for position in positions}
    ideas: list[dict[str, Any]] = []
    notes: list[str] = []
    today = date.today()

    for option_position in options:
        if option_position.expiration < today:
            notes.append(
                f"{option_position.ticker} {option_position.strike:g}{option_position.option_type[0]} "
                f"expired {option_position.expiration}; options context appears stale and was excluded from active ideas."
            )
            continue
        ratio = option_position.current / option_position.credit if option_position.credit else 0
        if ratio <= 0.5:
            action = "CLOSE / ROLL WINNER"
            rationale = "current option value is at or below 50% of original credit"
            score = 95
        elif ratio >= 2:
            action = "STOP / ROLL REVIEW"
            rationale = "current option value is at or above 200% of original credit"
            score = 92
        else:
            action = "MONITOR"
            rationale = "short premium position is between normal profit/stop triggers"
            score = 60
        ideas.append(
            {
                "score": score,
                "ticker": option_position.ticker,
                "action": action,
                "rationale": rationale,
                "details": (
                    f"{option_position.contracts}x {option_position.expiration} "
                    f"{option_position.strike:g}{option_position.option_type[0]}, "
                    f"credit {option_position.credit:.2f}, current {option_position.current:.2f}"
                ),
            }
        )

    for position in positions:
        quote = quotes.get(position.ticker, {})
        tech = technicals.get(position.ticker, {})
        live_price = float(quote.get("price") or position.current)
        change_pct = float(quote.get("changesPercentage") or 0)
        current_rsi = tech.get("rsi14")
        ret20 = tech.get("ret20")
        sma20 = tech.get("sma20")
        action = "HOLD"
        score = 50
        rationale = "portfolio holding remains within normal review parameters"

        if position.weight >= 12:
            score = 86
            action = "RISK TRIM / COVERED CALL WATCH"
            rationale = "single-name concentration above 12% of portfolio"
        elif position.weight >= 8:
            score = 75
            action = "POSITION SIZE REVIEW"
            rationale = "position is a large portfolio weight"

        if current_rsi is not None and current_rsi >= 70 and position.weight >= 4:
            score += 6
            action = "COVERED CALL / TRIM WATCH"
            rationale = "holding is extended by RSI; consider harvesting premium or trimming"
        elif live_price and sma20 and live_price < sma20 and position.weight >= 4:
            score += 4
            action = "RISK REVIEW"
            rationale = "large holding is below 20-day trend support"

        if position.pnl_pct is not None and position.pnl_pct < -10:
            score += 10
            action = "UNDERPERFORMER REVIEW"
            rationale = "unrealized loss warrants thesis and sizing review"

        if score >= 70:
            ideas.append(
                {
                    "score": min(score, 99),
                    "ticker": position.ticker,
                    "action": action,
                    "rationale": rationale,
                    "details": (
                        f"weight {position.weight:.1f}%, price {fmt_money(live_price)}, "
                        f"day {fmt_pct(change_pct)}, RSI {fmt_pct(current_rsi).replace('%', '')}, "
                        f"20d {fmt_pct(ret20)}"
                    ),
                }
            )

    for entry in watchlist:
        if entry.ticker in holdings:
            continue
        quote = quotes.get(entry.ticker, {})
        tech = technicals.get(entry.ticker, {})
        score, action, rationale = action_score_for_watchlist(entry, tech, quote)
        if score < 70:
            continue
        price = float(quote.get("price") or 0)
        ideas.append(
            {
                "score": score,
                "ticker": entry.ticker,
                "action": action,
                "rationale": rationale,
                "details": (
                    f"{entry.grade} score {entry.score if entry.score is not None else 'n/a'}, "
                    f"price {fmt_money(price)}, RSI {fmt_pct(tech.get('rsi14')).replace('%', '')}, "
                    f"20d {fmt_pct(tech.get('ret20'))}"
                ),
            }
        )

    ideas.sort(key=lambda row: (row["score"], row["ticker"]), reverse=True)
    return ideas, notes


def telegram_text(ideas: list[dict[str, Any]], notes: list[str]) -> str:
    today = date.today().isoformat()
    top = ideas[:6]
    lines = [
        f"Altamira Trade Ideas - {today}",
        "",
        "Generated from the repository portfolio and watchlist context.",
        "",
    ]
    if not top:
        lines.append("No high-confidence trade ideas cleared today's filters.")
    for idx, idea in enumerate(top, 1):
        lines.extend(
            [
                f"{idx}. {idea['ticker']} - {idea['action']} ({idea['score']}/100)",
                f"   {idea['rationale']}",
                f"   {idea['details']}",
            ]
        )
    if notes:
        lines.extend(["", "Data notes:"])
        for note in notes[:2]:
            lines.append(f"- {note}")
    lines.extend(["", "Not financial advice. Verify quotes, option chains, earnings, and account risk limits before trading."])
    return "\n".join(lines)


def markdown_report(ideas: list[dict[str, Any]], notes: list[str], positions: list[Position], watchlist: list[WatchlistEntry]) -> str:
    today = date.today().isoformat()
    lines = [
        f"# Trade Idea Generator - {today}",
        "",
        "> Generated from `context/portfolio-details.md` and `context/watchlist.md` with FMP market data where available.",
        "",
        "## Summary",
        "",
        f"- Portfolio holdings parsed: {len(positions)}",
        f"- Watchlist entries parsed: {len(watchlist)}",
        f"- Actionable ideas: {len(ideas)}",
        "",
        "## Top Trade Ideas",
        "",
        "| Rank | Ticker | Action | Score | Rationale | Details |",
        "|------|--------|--------|-------|-----------|---------|",
    ]
    for idx, idea in enumerate(ideas[:12], 1):
        lines.append(
            f"| {idx} | {idea['ticker']} | {idea['action']} | {idea['score']} | "
            f"{idea['rationale']} | {idea['details']} |"
        )
    if not ideas:
        lines.append("| - | - | No high-confidence ideas | - | Filters did not clear | - |")

    lines.extend(
        [
            "",
            "## Data Notes",
            "",
        ]
    )
    if notes:
        lines.extend(f"- {note}" for note in notes)
    else:
        lines.append("- No stale options or parsing issues detected.")
    lines.extend(
        [
            "",
            "## Process",
            "",
            "- Large holdings are flagged for concentration, trend, and premium-harvesting review.",
            "- Watchlist candidates are ranked by stored quality score plus current trend and RSI filters.",
            "- Short premium positions are checked against 50% profit-taking and 200% stop/roll triggers when unexpired.",
            "",
            "## Disclaimer",
            "",
            "This is not financial advice. Validate real-time prices, option chains, earnings dates, liquidity, and portfolio risk limits before placing trades.",
            "",
        ]
    )
    return "\n".join(lines)


def send_telegram(text: str, chat_id: str) -> dict[str, Any]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = parse.urlencode({"chat_id": chat_id, "text": text, "disable_web_page_preview": "true"}).encode("utf-8")
    req = request.Request(url, data=payload, method="POST")
    with request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate trade ideas from portfolio/watchlist context.")
    parser.add_argument("--send-telegram", action="store_true", help="Send the Telegram summary.")
    parser.add_argument("--chat-id", default=DEFAULT_TELEGRAM_CHAT_ID, help="Telegram chat/channel ID.")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR), help="Directory for generated output files.")
    args = parser.parse_args(argv)

    positions, option_positions = parse_portfolio(PORTFOLIO_PATH)
    watchlist = parse_watchlist(WATCHLIST_PATH)
    tickers = sorted({p.ticker for p in positions} | {w.ticker for w in watchlist if w.ticker})
    quotes = fetch_quote_batch(tickers)
    techs = technicals_for(tickers)
    ideas, notes = generate_ideas(positions, option_positions, watchlist, quotes, techs)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    report_path = output_dir / f"trade-idea-generator-{today}.md"
    telegram_path = output_dir / f"trade-idea-generator-{today}-telegram.txt"
    report_path.write_text(markdown_report(ideas, notes, positions, watchlist), encoding="utf-8")
    message = telegram_text(ideas, notes)
    telegram_path.write_text(message + "\n", encoding="utf-8")

    print(f"Wrote report: {report_path.relative_to(ROOT)}")
    print(f"Wrote Telegram summary: {telegram_path.relative_to(ROOT)}")
    print("")
    print(message)

    if args.send_telegram:
        response = send_telegram(message, args.chat_id)
        if not response.get("ok"):
            print(f"Telegram send failed: {response}", file=sys.stderr)
            return 1
        result = response.get("result", {})
        print("")
        print(f"Telegram sent: chat_id={args.chat_id}, message_id={result.get('message_id')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
