#!/usr/bin/env python3
"""Generate trade ideas from the workspace portfolio/watchlist and send Telegram.

The runner intentionally uses only the Python standard library so it can run
from cron-style automation without package setup.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python 3.8 fallback if ever needed
    ZoneInfo = None  # type: ignore


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_PATH = ROOT / "context" / "portfolio-details.md"
WATCHLIST_PATH = ROOT / "context" / "watchlist.md"
OUTPUT_DIR = ROOT / "outputs"
DEFAULT_PORTFOLIO_VALUE = 100_000.0
MAX_TELEGRAM_LEN = 3900


@dataclass
class Holding:
    ticker: str
    weight: float | None = None
    quantity: float | None = None
    pnl_pct: float | None = None


@dataclass
class WatchlistEntry:
    ticker: str
    score: float | None = None
    grade: str | None = None
    company: str | None = None
    status: str | None = None


@dataclass
class Idea:
    ticker: str
    action: str
    score: float
    setup: str
    rationale: str
    price: float | None = None
    risk: str = ""
    source: str = ""


def today_et() -> date:
    if ZoneInfo is None:
        return date.today()
    return datetime.now(ZoneInfo("America/New_York")).date()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def parse_float(value: str) -> float | None:
    cleaned = value.replace("$", "").replace(",", "").replace("%", "").strip()
    if cleaned in {"", "-", "—", "N/A"}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def ascii_status(value: str | None) -> str | None:
    """Normalize decorative watchlist status text for plain-text reports."""
    if not value:
        return None
    cleaned = value.replace("⭐", "").strip()
    return cleaned or None


def parse_portfolio(path: Path = PORTFOLIO_PATH) -> dict[str, Holding]:
    text = read_text(path)
    holdings: dict[str, Holding] = {}
    in_positions = False
    for line in text.splitlines():
        if line.startswith("## Current Positions"):
            in_positions = True
            continue
        if in_positions and line.startswith("## "):
            break
        if not in_positions or not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 9 or parts[0] in {"SYMBOL", "--------"}:
            continue
        ticker = parts[0].upper()
        if not re.fullmatch(r"[A-Z.]{1,8}", ticker):
            continue
        quantity = parse_float(parts[1])
        weight = parse_float(parts[8])
        pnl_match = re.search(r"\(([-+0-9.,]+)%\)", parts[6])
        pnl_pct = parse_float(pnl_match.group(1)) if pnl_match else None
        holdings[ticker] = Holding(ticker=ticker, weight=weight, quantity=quantity, pnl_pct=pnl_pct)
    return holdings


def parse_watchlist(path: Path = WATCHLIST_PATH) -> dict[str, WatchlistEntry]:
    text = read_text(path)
    entries: dict[str, WatchlistEntry] = {}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 5 or parts[0] in {"Ticker", "--------"}:
            continue
        ticker = parts[0].upper()
        if not re.fullmatch(r"[A-Z.]{1,8}", ticker):
            continue
        grade = parts[2].replace("*", "").strip() or None
        entries[ticker] = WatchlistEntry(
            ticker=ticker,
            score=parse_float(parts[1]),
            grade=grade if grade not in {"—", "-"} else None,
            company=parts[3] or None,
            status=ascii_status(parts[4]),
        )
    return entries


def find_regex_in_file(path: Path, patterns: list[str]) -> str | None:
    text = read_text(path)
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None


def get_fmp_key() -> str:
    key = os.environ.get("FMP_API_KEY")
    if key:
        return key
    patterns = [
        r'FMP_API_KEY\s*=\s*["\']([^"\']+)["\']',
        r'KEY\s*=\s*os\.environ\.get\("FMP_API_KEY",\s*"([^"]+)"\)',
        r"apikey=([A-Za-z0-9_-]{20,})",
    ]
    for rel in [
        "scripts/thesis-generator.py",
        "scripts/stock-scorer.py",
        ".claude/commands/options-scan.md",
        "outputs/csp-daily-scan-fixed.json",
    ]:
        found = find_regex_in_file(ROOT / rel, patterns)
        if found and "your_" not in found.lower():
            return found
    raise RuntimeError("FMP_API_KEY is not set and no existing repository FMP key was found.")


def get_telegram_chat_id() -> str | None:
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if chat_id:
        return chat_id
    workflow = ROOT / "outputs" / "csp-daily-scan-fixed.json"
    text = read_text(workflow)
    match = re.search(r'"chatId"\s*:\s*"=?(-?\d+)"', text)
    if match:
        return match.group(1)
    return None


def http_json(url: str, timeout: int = 20, retries: int = 2) -> Any:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AltamiraTradeIdeaGenerator/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = resp.read().decode("utf-8")
            return json.loads(payload)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Request failed for {url}: {last_error}")


def fmp_url(endpoint: str, key: str, params: dict[str, str] | None = None, version: str = "v3") -> str:
    query = dict(params or {})
    query["apikey"] = key
    return f"https://financialmodelingprep.com/api/{version}/{endpoint}?{urllib.parse.urlencode(query)}"


def fetch_quotes(tickers: list[str], key: str) -> dict[str, dict[str, Any]]:
    quotes: dict[str, dict[str, Any]] = {}
    for i in range(0, len(tickers), 50):
        batch = tickers[i : i + 50]
        data = http_json(fmp_url("quote/" + ",".join(batch), key))
        if isinstance(data, list):
            for row in data:
                symbol = str(row.get("symbol", "")).upper()
                if symbol:
                    quotes[symbol] = row
    return quotes


def fetch_earnings_exclusions(tickers: set[str], key: str, start: date, days: int = 45) -> dict[str, str]:
    end = start + timedelta(days=days)
    data = http_json(
        fmp_url(
            "earning_calendar",
            key,
            {"from": start.isoformat(), "to": end.isoformat()},
        ),
        timeout=30,
    )
    exclusions: dict[str, str] = {}
    if isinstance(data, list):
        for row in data:
            symbol = str(row.get("symbol", "")).upper()
            if symbol in tickers and row.get("date"):
                exclusions[symbol] = str(row["date"])
    return exclusions


def classify_vix(vix: float | None) -> tuple[str, int, str]:
    if vix is None:
        return "UNKNOWN", 75, "Use normal sizing until VIX quote refreshes."
    if vix < 15:
        return "LOW", 75, "Premium is thinner; favor quality entries and smaller credits."
    if vix <= 25:
        return "NORMAL", 100, "Standard CSP/spread sizing is acceptable."
    if vix <= 35:
        return "ELEVATED", 50, "Prefer defined-risk spreads and reduced size."
    return "CRISIS", 25, "Spreads only; preserve cash and avoid naked premium."


def pct(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def grade_bonus(entry: WatchlistEntry | None) -> float:
    if not entry:
        return 0.0
    grade = (entry.grade or "").upper()
    if grade == "B":
        return 12.0
    if grade == "B-":
        return 8.0
    if grade == "C+":
        return 4.0
    if grade.startswith("D") or grade == "F":
        return -10.0
    return 0.0


def technical_score(q: dict[str, Any]) -> float:
    price = pct(q.get("price"))
    sma50 = pct(q.get("priceAvg50"))
    sma200 = pct(q.get("priceAvg200"))
    year_high = pct(q.get("yearHigh"))
    change = pct(q.get("changesPercentage")) or 0.0
    score = 50.0
    if price and sma50:
        score += 15 if price > sma50 else -12
        score += max(-8, min(8, ((price / sma50) - 1) * 100))
    if price and sma200:
        score += 12 if price > sma200 else -10
    if price and year_high:
        pct_high = price / year_high
        if 0.70 <= pct_high <= 0.95:
            score += 8
        elif pct_high > 0.98:
            score -= 4
    if change > 5:
        score -= 6
    elif change < -3:
        score += 2
    return max(0.0, min(100.0, score))


def build_ideas(
    holdings: dict[str, Holding],
    watchlist: dict[str, WatchlistEntry],
    quotes: dict[str, dict[str, Any]],
    earnings: dict[str, str],
    regime: str,
) -> list[Idea]:
    ideas: list[Idea] = []
    tickers = sorted(set(holdings) | set(watchlist))
    for ticker in tickers:
        q = quotes.get(ticker)
        if not q:
            continue
        price = pct(q.get("price"))
        if price is None or price <= 0:
            continue
        tech = technical_score(q)
        entry = watchlist.get(ticker)
        holding = holdings.get(ticker)
        score = min(100.0, max(0.0, tech + grade_bonus(entry)))
        if ticker in earnings:
            score -= 12

        sma50 = pct(q.get("priceAvg50"))
        sma200 = pct(q.get("priceAvg200"))
        change = pct(q.get("changesPercentage")) or 0.0
        trend_bits = []
        if sma50:
            trend_bits.append(("above" if price > sma50 else "below") + f" 50D ${sma50:.2f}")
        if sma200:
            trend_bits.append(("above" if price > sma200 else "below") + f" 200D ${sma200:.2f}")
        trend = ", ".join(trend_bits) if trend_bits else "trend data partial"
        earnings_note = f" Earnings {earnings[ticker]} inside 45D window." if ticker in earnings else ""

        if entry and (entry.score or 0) >= 58 and ticker not in earnings:
            ideas.append(
                Idea(
                    ticker=ticker,
                    action="CSP / starter entry",
                    score=min(100.0, score + 5),
                    setup=f"Sell 30-45D 0.20-0.30 delta put or start 1/3 equity tranche near ${price:.2f}.",
                    rationale=f"{entry.grade or 'Watchlist'} watchlist candidate ({entry.status or 'watch'}); {trend}; day change {change:+.1f}%.",
                    price=price,
                    risk=f"Respect 5% max position; {regime} VIX regime sizing. Avoid if earnings date appears before expiration.",
                    source="watchlist",
                )
            )

        if holding:
            weight = holding.weight or 0.0
            if weight >= 10 and price > (sma50 or 0):
                ideas.append(
                    Idea(
                        ticker=ticker,
                        action="Trim / covered call",
                    score=min(100.0, score + min(weight, 20)),
                        setup=f"Consider 30-45D covered call at ~0.20 delta against part of existing {weight:.1f}% weight.",
                        rationale=f"Large portfolio weight with positive trend ({trend}); harvest premium without adding exposure.{earnings_note}",
                        price=price,
                        risk="Do not overwrite shares needed for core thesis; avoid calls through earnings unless intentional.",
                        source="portfolio",
                    )
                )
            elif weight < 5 and ticker not in earnings and tech >= 65:
                ideas.append(
                    Idea(
                        ticker=ticker,
                        action="Add-on candidate",
                    score=min(100.0, score + 3),
                        setup=f"Add on pullback toward 50D SMA or use defined-risk put spread around current ${price:.2f}.",
                        rationale=f"Existing small position, constructive technicals ({trend}), and manageable portfolio weight {weight:.1f}%.",
                        price=price,
                        risk="Keep aggregate sector concentration within portfolio limits.",
                        source="portfolio",
                    )
                )

        if entry and (entry.grade in {"D", "F"} or (entry.score is not None and entry.score < 40)):
            ideas.append(
                Idea(
                    ticker=ticker,
                    action="Avoid / no trade",
                    score=25 - (entry.score or 0) / 5,
                    setup="No new exposure.",
                    rationale=f"Low watchlist score ({entry.score}, {entry.grade}); wait for thesis or score improvement.",
                    price=price,
                    risk="Opportunity cost and weak quality screen.",
                    source="watchlist",
                )
            )

    return sorted(ideas, key=lambda item: item.score, reverse=True)


def fmt_money(value: float | None) -> str:
    return "N/A" if value is None else f"${value:,.2f}"


def build_report(
    ideas: list[Idea],
    holdings: dict[str, Holding],
    watchlist: dict[str, WatchlistEntry],
    quotes: dict[str, dict[str, Any]],
    vix: float | None,
    regime: str,
    sizing_pct: int,
    regime_note: str,
    earnings: dict[str, str],
    as_of: date,
) -> tuple[str, str]:
    top_actionable = [i for i in ideas if not i.action.startswith("Avoid")][:5]
    avoids = [i for i in ideas if i.action.startswith("Avoid")][:3]

    lines = [
        f"# Trade Idea Generator - {as_of.isoformat()}",
        "",
        "> Educational trade planning output only; not financial advice. Confirm live quotes, liquidity, earnings dates, and portfolio limits before placing trades.",
        "",
        "## Market Regime",
        "",
        f"- VIX: {vix:.2f}" if vix is not None else "- VIX: N/A",
        f"- Regime: {regime}",
        f"- Sizing guide: {sizing_pct}% of standard premium-selling size",
        f"- Note: {regime_note}",
        "",
        "## Top Actionable Ideas",
        "",
    ]
    if not top_actionable:
        lines.append("No actionable ideas passed the screen today.")
    for idx, idea in enumerate(top_actionable, start=1):
        lines.extend(
            [
                f"### {idx}. {idea.ticker} - {idea.action}",
                "",
                f"- Price: {fmt_money(idea.price)}",
                f"- Score: {idea.score:.1f}",
                f"- Setup: {idea.setup}",
                f"- Rationale: {idea.rationale}",
                f"- Risk: {idea.risk}",
                f"- Source: {idea.source}",
                "",
            ]
        )
    if avoids:
        lines.extend(["## Avoid / No-Trade List", ""])
        for idea in avoids:
            lines.append(f"- **{idea.ticker}**: {idea.rationale}")
        lines.append("")
    if earnings:
        lines.extend(["## Earnings Conflicts (next 45 days)", ""])
        for ticker, when in sorted(earnings.items()):
            lines.append(f"- {ticker}: {when}")
        lines.append("")
    missing = sorted((set(holdings) | set(watchlist)) - set(quotes))
    if missing:
        lines.extend(["## Data Gaps", "", "- Missing quotes: " + ", ".join(missing), ""])
    lines.extend(
        [
            "## Universe",
            "",
            f"- Portfolio symbols: {len(holdings)}",
            f"- Watchlist symbols: {len(watchlist)}",
            f"- Quotes retrieved: {len(quotes)}",
            "",
        ]
    )

    message_lines = [
        f"TRADE IDEA GENERATOR - {as_of.isoformat()}",
        f"VIX: {vix:.2f}" if vix is not None else "VIX: N/A",
        f"Regime: {regime} | Sizing: {sizing_pct}%",
        "",
    ]
    if top_actionable:
        message_lines.append("Top ideas:")
        for idx, idea in enumerate(top_actionable[:5], start=1):
            message_lines.append(f"{idx}. {idea.ticker} - {idea.action} @ {fmt_money(idea.price)}")
            message_lines.append(f"   {idea.setup}")
            message_lines.append(f"   Why: {idea.rationale}")
    else:
        message_lines.append("No actionable ideas passed the screen today.")
    if avoids:
        message_lines.extend(["", "Avoid/no-trade: " + ", ".join(i.ticker for i in avoids)])
    if earnings:
        message_lines.extend(["", "Earnings conflicts: " + ", ".join(f"{t} {d}" for t, d in sorted(earnings.items())[:8])])
    message_lines.extend(["", "Educational only. Confirm live chain/liquidity before trading."])
    telegram = "\n".join(message_lines)
    if len(telegram) > MAX_TELEGRAM_LEN:
        telegram = telegram[: MAX_TELEGRAM_LEN - 80] + "\n\n...truncated. See markdown report in outputs."
    return "\n".join(lines), telegram


def send_telegram(text: str, token: str, chat_id: str) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST")
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if not data.get("ok"):
        raise RuntimeError(f"Telegram send failed: {data}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--send-telegram", action="store_true", help="Send summary to Telegram.")
    parser.add_argument("--chat-id", help="Telegram chat/channel id. Defaults to TELEGRAM_CHAT_ID or deployed workflow id.")
    parser.add_argument("--out", help="Optional markdown output path.")
    args = parser.parse_args(argv)

    holdings = parse_portfolio()
    watchlist = parse_watchlist()
    tickers = sorted(t for t in set(holdings) | set(watchlist) if t not in {"FFOLX"})
    if not tickers:
        raise RuntimeError("No portfolio/watchlist tickers found.")

    key = get_fmp_key()
    as_of = today_et()
    quotes = fetch_quotes(tickers + ["^VIX"], key)
    vix_quote = quotes.get("^VIX") or quotes.get("VIX")
    vix = pct(vix_quote.get("price")) if vix_quote else None
    regime, sizing_pct, regime_note = classify_vix(vix)
    earnings = fetch_earnings_exclusions(set(tickers), key, as_of)

    ideas = build_ideas(holdings, watchlist, quotes, earnings, regime)
    report, telegram = build_report(
        ideas=ideas,
        holdings=holdings,
        watchlist=watchlist,
        quotes=quotes,
        vix=vix,
        regime=regime,
        sizing_pct=sizing_pct,
        regime_note=regime_note,
        earnings=earnings,
        as_of=as_of,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = Path(args.out) if args.out else OUTPUT_DIR / f"trade-idea-generator-{as_of.isoformat()}.md"
    out_path.write_text(report + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")

    if args.send_telegram:
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is not set.")
        chat_id = args.chat_id or get_telegram_chat_id()
        if not chat_id:
            raise RuntimeError("Telegram chat id not found. Set TELEGRAM_CHAT_ID or pass --chat-id.")
        send_telegram(telegram, token, chat_id)
        print("Sent Telegram message.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
