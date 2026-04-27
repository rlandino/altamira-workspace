#!/usr/bin/env python3
"""
Generate daily trade ideas from the current Altamira portfolio and watchlist.

The script reads repository context files, enriches them with live market data
when an FMP key is available, writes a markdown report, and can send a concise
Telegram summary when TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are configured.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    print("Install requests: pip install requests", file=sys.stderr)
    sys.exit(1)


WORKSPACE = Path(__file__).resolve().parent.parent
CONTEXT = WORKSPACE / "context"
OUTPUTS = WORKSPACE / "outputs"
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"


@dataclass
class Holding:
    ticker: str
    quantity: float
    current: float | None
    market_value: float
    weight: float
    pnl_pct: float | None
    day_change_pct: float | None


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
    expiration: str
    credit: float
    current: float
    contracts: int


def money_to_float(value: str) -> float:
    return float(value.replace("$", "").replace(",", "").strip())


def pct_to_float(value: str) -> float | None:
    match = re.search(r"([-+]?\d+(?:\.\d+)?)%", value)
    return float(match.group(1)) if match else None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_holdings() -> list[Holding]:
    text = read_text(CONTEXT / "portfolio-details.md")
    holdings: list[Holding] = []
    in_table = False
    for line in text.splitlines():
        if line.startswith("| SYMBOL |"):
            in_table = True
            continue
        if not in_table:
            continue
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 9 or cells[0] == "--------":
            continue
        try:
            ticker = cells[0].upper()
            holdings.append(
                Holding(
                    ticker=ticker,
                    quantity=float(cells[1].replace(",", "")),
                    current=money_to_float(cells[3]) if cells[3] != "N/A" else None,
                    market_value=money_to_float(cells[4]),
                    weight=pct_to_float(cells[8]) or 0.0,
                    pnl_pct=pct_to_float(cells[6]),
                    day_change_pct=pct_to_float(cells[7]),
                )
            )
        except (ValueError, IndexError):
            continue
    return holdings


def parse_options() -> list[OptionPosition]:
    text = read_text(CONTEXT / "portfolio-details.md")
    positions: list[OptionPosition] = []
    in_table = False
    for line in text.splitlines():
        if line.startswith("| Ticker | Strike | Type |"):
            in_table = True
            continue
        if not in_table:
            continue
        if not line.startswith("|") or line.startswith("|---"):
            if positions:
                break
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 7 or cells[0] == "--------":
            continue
        try:
            positions.append(
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
    return positions


def parse_watchlist() -> list[WatchlistEntry]:
    text = read_text(CONTEXT / "watchlist.md")
    entries: list[WatchlistEntry] = []
    for line in text.splitlines():
        if not line.startswith("| ") or line.startswith("| Ticker ") or line.startswith("|--------"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 5:
            continue
        score = None
        if cells[1] not in {"-", "--", "—"}:
            try:
                score = float(cells[1])
            except ValueError:
                score = None
        grade = cells[2].replace("*", "").strip()
        entries.append(
            WatchlistEntry(
                ticker=cells[0].upper(),
                score=score,
                grade=grade,
                company=cells[3],
                status=cells[4].replace("⭐", "").strip(),
            )
        )
    return entries


def load_existing_fmp_key() -> str:
    key = os.environ.get("FMP_API_KEY") or os.environ.get("FMP_KEY")
    if key:
        return key
    scorer = WORKSPACE / "scripts" / "stock-scorer.py"
    if scorer.exists():
        match = re.search(r'FMP_API_KEY\s*=\s*"([^"]+)"', read_text(scorer))
        if match:
            return match.group(1)
    return ""


class FmpClient:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.session = requests.Session()

    def get(self, endpoint: str, **params: Any) -> Any:
        if not self.api_key:
            return None
        params["apikey"] = self.api_key
        url = f"{FMP_BASE_URL}/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params, timeout=20)
        response.raise_for_status()
        return response.json()

    def quote(self, symbols: list[str]) -> dict[str, dict[str, Any]]:
        if not symbols:
            return {}
        data = self.get(f"quote/{','.join(symbols)}") or []
        return {item.get("symbol", "").upper(): item for item in data if item.get("symbol")}

    def historical(self, symbol: str, limit: int = 70) -> list[dict[str, Any]]:
        data = self.get(f"historical-price-full/{symbol}", serietype="line", timeseries=limit) or {}
        return data.get("historical") or []

    def upcoming_earnings(self, symbol: str) -> str:
        data = self.get(f"historical/earning_calendar/{symbol}") or []
        today = date.today()
        upcoming: list[date] = []
        for item in data:
            raw = item.get("date")
            if not raw:
                continue
            try:
                d = datetime.strptime(raw[:10], "%Y-%m-%d").date()
            except ValueError:
                continue
            if d >= today:
                upcoming.append(d)
        return min(upcoming).isoformat() if upcoming else "Unknown"


def sma(values: list[float], window: int) -> float | None:
    if len(values) < window:
        return None
    return sum(values[:window]) / window


def rsi(values: list[float], window: int = 14) -> float | None:
    if len(values) <= window:
        return None
    gains = []
    losses = []
    # FMP historical data is newest first. Reverse for chronological deltas.
    chronological = list(reversed(values[: window + 1]))
    for prior, current in zip(chronological, chronological[1:]):
        change = current - prior
        gains.append(max(change, 0))
        losses.append(abs(min(change, 0)))
    avg_gain = sum(gains) / window
    avg_loss = sum(losses) / window
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def technical_snapshot(client: FmpClient, symbol: str, quote_price: float | None) -> dict[str, Any]:
    try:
        history = client.historical(symbol)
    except Exception:
        history = []
    closes = [float(row["close"]) for row in history if row.get("close") is not None]
    price = quote_price or (closes[0] if closes else None)
    sma20 = sma(closes, 20)
    sma50 = sma(closes, 50)
    rsi14 = rsi(closes)
    ret20 = None
    if price is not None and len(closes) >= 21 and closes[20] != 0:
        ret20 = (price / closes[20] - 1) * 100
    return {"price": price, "sma20": sma20, "sma50": sma50, "rsi": rsi14, "ret20": ret20}


def fmt_pct(value: float | None) -> str:
    return "N/A" if value is None else f"{value:+.1f}%"


def fmt_num(value: float | None, decimals: int = 2) -> str:
    return "N/A" if value is None else f"{value:.{decimals}f}"


def grade_rank(grade: str) -> int:
    order = {"A+": 12, "A": 11, "A-": 10, "B+": 9, "B": 8, "B-": 7, "C+": 6, "C": 5, "C-": 4, "D+": 3, "D": 2, "F": 1}
    return order.get(grade, 0)


def build_report(send_requested: bool = False) -> tuple[str, str, Path]:
    holdings = parse_holdings()
    options = parse_options()
    watchlist = parse_watchlist()
    client = FmpClient(load_existing_fmp_key())

    symbols = sorted({h.ticker for h in holdings if h.ticker != "FFOLX"} | {w.ticker for w in watchlist})
    try:
        quotes = client.quote(symbols + ["^VIX"])
    except Exception:
        quotes = {}

    vix_quote = quotes.get("^VIX") or {}
    vix = vix_quote.get("price")
    if vix is None:
        try:
            vix = (client.quote(["^VIX"]).get("^VIX") or {}).get("price")
        except Exception:
            vix = None
    if vix is None:
        vix_regime = "Unknown"
        sizing = "manual"
    elif vix < 15:
        vix_regime = "LOW"
        sizing = "75%"
    elif vix < 25:
        vix_regime = "NORMAL"
        sizing = "100%"
    elif vix < 35:
        vix_regime = "ELEVATED"
        sizing = "50%"
    else:
        vix_regime = "CRISIS"
        sizing = "25%"

    technicals: dict[str, dict[str, Any]] = {}
    priority_symbols = [w.ticker for w in watchlist[:8]] + [h.ticker for h in holdings[:10] if h.ticker != "FFOLX"]
    for symbol in dict.fromkeys(priority_symbols):
        q = quotes.get(symbol) or {}
        technicals[symbol] = technical_snapshot(client, symbol, q.get("price"))

    csp_candidates: list[dict[str, Any]] = []
    for entry in watchlist:
        if entry.status.lower() == "avoid" or grade_rank(entry.grade) < grade_rank("B-"):
            continue
        tech = technicals.get(entry.ticker) or {}
        price = tech.get("price") or (quotes.get(entry.ticker) or {}).get("price")
        rsi14 = tech.get("rsi")
        ret20 = tech.get("ret20")
        score = (entry.score or 0) + grade_rank(entry.grade)
        if rsi14 and 35 <= rsi14 <= 72:
            score += 5
        if ret20 and ret20 > 0:
            score += 3
        csp_candidates.append({"entry": entry, "tech": tech, "price": price, "score": score})
    csp_candidates.sort(key=lambda item: item["score"], reverse=True)

    covered_call_candidates: list[dict[str, Any]] = []
    for holding in holdings:
        if holding.ticker in {"FFOLX"}:
            continue
        tech = technicals.get(holding.ticker) or {}
        rsi14 = tech.get("rsi")
        ret20 = tech.get("ret20")
        extension = 0.0
        if tech.get("price") and tech.get("sma20"):
            extension = (tech["price"] / tech["sma20"] - 1) * 100
        score = holding.weight
        if rsi14 and rsi14 > 65:
            score += 5
        if ret20 and ret20 > 8:
            score += 4
        if extension > 5:
            score += 3
        if holding.weight >= 5 or score >= 8:
            covered_call_candidates.append({"holding": holding, "tech": tech, "extension": extension, "score": score})
    covered_call_candidates.sort(key=lambda item: item["score"], reverse=True)

    option_actions: list[str] = []
    for pos in options:
        ratio = pos.current / pos.credit if pos.credit else 0
        if pos.current <= pos.credit * 0.5:
            action = "Close/harvest"
            reason = "at or beyond 50% profit target"
        elif pos.current >= pos.credit * 2:
            action = "Roll/stop review"
            reason = "current option value is above 2x credit"
        else:
            action = "Hold/monitor"
            reason = "inside normal management band"
        option_actions.append(
            f"- {action}: {pos.ticker} {pos.strike:g} {pos.option_type} {pos.expiration} "
            f"(credit ${pos.credit:.2f}, current ${pos.current:.2f}, {ratio:.1f}x) - {reason}."
        )

    today = date.today().isoformat()
    report_path = OUTPUTS / f"trade-idea-generator-{today}.md"
    disclosure = (
        "Educational trade-planning output only; not investment advice. Verify live option chains, "
        "earnings dates, liquidity, and account risk before placing any order."
    )

    lines: list[str] = [
        f"# Trade Idea Generator - {today}",
        "",
        f"**Universe:** current portfolio ({len(holdings)} holdings) + watchlist ({len(watchlist)} names).",
        f"**VIX regime:** {fmt_num(vix, 1)} ({vix_regime}); suggested premium-selling size factor: {sizing}.",
        "",
        f"> {disclosure}",
        "",
        "## Top Trade Ideas",
        "",
        "### 1) Cash-secured put / bull put spread candidates",
        "",
        "| Rank | Ticker | Watchlist grade | Price | RSI | 20D return | Suggested setup | Why now |",
        "|------|--------|-----------------|-------|-----|------------|-----------------|---------|",
    ]
    telegram_lines = [
        f"TRADE IDEA GENERATOR - {today}",
        f"VIX: {fmt_num(vix, 1)} ({vix_regime}) | Size factor: {sizing}",
        "",
        "Top CSP / put-spread ideas:",
    ]

    for idx, item in enumerate(csp_candidates[:5], 1):
        entry = item["entry"]
        tech = item["tech"]
        price = item["price"]
        target_delta = "0.20-0.30 delta"
        setup = "CSP" if vix_regime in {"LOW", "NORMAL", "Unknown"} else "Defined-risk bull put spread"
        why = f"{entry.status}; score {entry.score or 'N/A'}; {target_delta}; avoid if earnings <21 DTE"
        lines.append(
            f"| {idx} | {entry.ticker} | {entry.grade} ({entry.score or 'N/A'}) | "
            f"${fmt_num(price)} | {fmt_num(tech.get('rsi'), 1)} | {fmt_pct(tech.get('ret20'))} | "
            f"{setup}, 30-45 DTE | {why} |"
        )
        if idx <= 3:
            telegram_lines.append(
                f"{idx}. {entry.ticker} ({entry.grade}, score {entry.score or 'N/A'}) - {setup}, "
                f"30-45 DTE, target 0.20-0.30 delta."
            )

    lines.extend(
        [
            "",
            "### 2) Covered call / trim candidates on existing holdings",
            "",
            "| Rank | Ticker | Weight | Price vs 20D SMA | RSI | 20D return | Suggested setup | Risk note |",
            "|------|--------|--------|------------------|-----|------------|-----------------|-----------|",
        ]
    )
    for idx, item in enumerate(covered_call_candidates[:5], 1):
        holding = item["holding"]
        tech = item["tech"]
        risk_note = "Above 5% single-position guideline" if holding.weight > 5 else "Momentum extended"
        lines.append(
            f"| {idx} | {holding.ticker} | {holding.weight:.1f}% | {item['extension']:+.1f}% | "
            f"{fmt_num(tech.get('rsi'), 1)} | {fmt_pct(tech.get('ret20'))} | "
            f"Sell 0.20-0.30 delta covered call, 30-45 DTE | {risk_note} |"
        )
    telegram_lines.extend(["", "Covered call / risk-control ideas:"])
    for idx, item in enumerate(covered_call_candidates[:3], 1):
        holding = item["holding"]
        telegram_lines.append(
            f"{idx}. {holding.ticker} ({holding.weight:.1f}% weight) - consider 0.20-0.30 delta covered call or trim review."
        )

    lines.extend(
        [
            "",
            "## Existing short-premium management",
            "",
            *option_actions,
            "",
            "## Portfolio risk flags",
            "",
        ]
    )
    overweight = [h for h in holdings if h.weight > 5]
    if overweight:
        lines.append(
            "- Single-position concentration above 5% guideline: "
            + ", ".join(f"{h.ticker} {h.weight:.1f}%" for h in overweight[:8])
            + "."
        )
    tech_semis = [h for h in holdings if h.ticker in {"AVGO", "AMAT", "MSFT", "AAPL", "GOOGL", "AMZN", "CRWD", "NOW"}]
    tech_weight = sum(h.weight for h in tech_semis)
    lines.append(f"- Approximate mega-cap tech/software/semiconductor exposure from listed holdings: {tech_weight:.1f}%.")
    lines.append("- Confirm live option bid/ask, open interest, earnings timing, and assignment capacity before entry.")
    lines.extend(["", "## Telegram delivery", ""])
    lines.append("- Requested: yes." if send_requested else "- Requested: no.")
    lines.extend(["", f"**Disclosure:** {disclosure}", ""])

    report = "\n".join(lines)
    OUTPUTS.mkdir(exist_ok=True)
    report_path.write_text(report, encoding="utf-8")

    telegram_lines.extend(
        [
            "",
            "Manage open puts:",
            *option_actions[:3],
            "",
            "Verify live chains/earnings before entry. Educational only.",
        ]
    )
    telegram_message = "\n".join(telegram_lines)
    return report, telegram_message, report_path


def send_telegram(message: str, chat_id: str) -> dict[str, Any]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured.")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = requests.post(
        url,
        json={"chat_id": chat_id, "text": message, "disable_web_page_preview": True},
        timeout=20,
    )
    try:
        payload = response.json()
    except ValueError:
        payload = {"ok": False, "description": response.text}
    if not response.ok or not payload.get("ok"):
        raise RuntimeError(f"Telegram send failed: {payload}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Altamira trade ideas from repo context.")
    parser.add_argument("--send-telegram", action="store_true", help="Send concise summary to Telegram.")
    parser.add_argument("--telegram-chat-id", default=os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("TELEGRAM_CHANNEL_ID"))
    args = parser.parse_args()

    report, telegram_message, report_path = build_report(send_requested=args.send_telegram)
    print(f"Wrote {report_path}")

    if args.send_telegram:
        if not args.telegram_chat_id:
            payload_path = OUTPUTS / f"trade-idea-generator-telegram-{date.today().isoformat()}.txt"
            payload_path.write_text(telegram_message, encoding="utf-8")
            print(f"Telegram chat id missing. Saved message payload to {payload_path}", file=sys.stderr)
            return 2
        result = send_telegram(telegram_message, args.telegram_chat_id)
        message_id = (result.get("result") or {}).get("message_id")
        print(f"Sent Telegram message_id={message_id}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
