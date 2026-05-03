#!/usr/bin/env python3
"""Generate portfolio/watchlist trade ideas and optionally send Telegram output."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable


WORKSPACE = Path(__file__).resolve().parents[1]
CONTEXT = WORKSPACE / "context"
OUTPUTS = WORKSPACE / "outputs"

DEFAULT_CHAT_ID = "7830722515"
TELEGRAM_LIMIT = 3900


@dataclass(frozen=True)
class Holding:
    symbol: str
    qty: float
    avg_price: float
    current: float
    market_value: float
    pnl_pct: float
    day_chg_pct: float
    weight: float


@dataclass(frozen=True)
class WatchlistItem:
    ticker: str
    score: float | None
    grade: str
    company: str
    status: str


@dataclass(frozen=True)
class OptionPosition:
    ticker: str
    strike: float
    option_type: str
    expiration: str
    credit: float
    current: float
    contracts: int


def money_to_float(value: str) -> float:
    cleaned = value.replace("$", "").replace(",", "").replace("%", "").strip()
    if cleaned in {"", "-", "—"}:
        return 0.0
    return float(cleaned)


def parse_pct_pair(value: str) -> float:
    match = re.search(r"\(([+-]?[0-9.]+)%\)", value)
    if match:
        return float(match.group(1))
    match = re.search(r"([+-]?[0-9.]+)%", value)
    return float(match.group(1)) if match else 0.0


def markdown_rows(path: Path, header_prefix: str) -> list[list[str]]:
    rows: list[list[str]] = []
    in_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith(header_prefix):
            in_table = True
            continue
        if not in_table:
            continue
        if not stripped.startswith("|"):
            if rows:
                break
            continue
        if set(stripped.replace("|", "").replace("-", "").replace(" ", "")) == set():
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        rows.append(cells)
    return rows


def load_holdings() -> list[Holding]:
    rows = markdown_rows(CONTEXT / "portfolio-details.md", "| SYMBOL |")
    holdings: list[Holding] = []
    for cells in rows:
        if len(cells) < 9 or cells[0] == "SYMBOL" or cells[0].startswith("--"):
            continue
        holdings.append(
            Holding(
                symbol=cells[0],
                qty=money_to_float(cells[1]),
                avg_price=money_to_float(cells[2]),
                current=money_to_float(cells[3]),
                market_value=money_to_float(cells[4]),
                pnl_pct=parse_pct_pair(cells[6]),
                day_chg_pct=parse_pct_pair(cells[7]),
                weight=money_to_float(cells[8]),
            )
        )
    return holdings


def load_watchlist() -> list[WatchlistItem]:
    rows = markdown_rows(CONTEXT / "watchlist.md", "| Ticker |")
    items: list[WatchlistItem] = []
    for cells in rows:
        if len(cells) < 5 or cells[0] == "Ticker" or cells[0].startswith("--"):
            continue
        score = None if cells[1] in {"—", "-", ""} else float(cells[1])
        grade = cells[2].replace("*", "")
        items.append(WatchlistItem(cells[0], score, grade, cells[3], cells[4]))
    return items


def load_options() -> list[OptionPosition]:
    rows = markdown_rows(CONTEXT / "portfolio-details.md", "| Ticker | Strike |")
    positions: list[OptionPosition] = []
    for cells in rows:
        if len(cells) < 7 or cells[0] == "Ticker" or cells[0].startswith("--"):
            continue
        positions.append(
            OptionPosition(
                ticker=cells[0],
                strike=money_to_float(cells[1]),
                option_type=cells[2],
                expiration=cells[3],
                credit=money_to_float(cells[4]),
                current=money_to_float(cells[5]),
                contracts=int(money_to_float(cells[6])),
            )
        )
    return positions


def http_json(url: str, timeout: int = 15) -> object:
    request = urllib.request.Request(url, headers={"User-Agent": "altamira-trade-idea-generator/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_fmp_quotes(symbols: Iterable[str], api_key: str | None) -> dict[str, dict[str, float]]:
    if not api_key:
        return {}
    symbol_csv = ",".join(sorted(set(symbols)))
    url = (
        "https://financialmodelingprep.com/api/v3/quote/"
        + urllib.parse.quote(symbol_csv)
        + "?apikey="
        + urllib.parse.quote(api_key)
    )
    try:
        payload = http_json(url)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"Warning: FMP quote fetch failed: {exc}", file=sys.stderr)
        return {}
    if not isinstance(payload, list):
        return {}
    quotes: dict[str, dict[str, float]] = {}
    for item in payload:
        if not isinstance(item, dict) or not item.get("symbol"):
            continue
        quotes[str(item["symbol"])] = {
            "price": float(item.get("price") or 0),
            "changesPercentage": float(item.get("changesPercentage") or 0),
        }
    return quotes


def next_monthly_expiration(today: date) -> date:
    """Return a conservative 30-45 DTE Friday expiration."""
    target = today + timedelta(days=42)
    while target.weekday() != 4:
        target += timedelta(days=1)
    return target


def nearest_strike(price: float, step: float = 5.0) -> float:
    return round(price / step) * step


def build_covered_call_ideas(holdings: list[Holding]) -> list[dict[str, object]]:
    ideas: list[dict[str, object]] = []
    for h in holdings:
        if h.qty < 100 or h.symbol in {"SPY", "QQQ", "FFOLX"}:
            continue
        if h.weight < 3.5:
            continue
        contracts = int(h.qty // 100)
        otm_pct = 0.08 if h.day_chg_pct < 2 else 0.10
        strike = nearest_strike(h.current * (1 + otm_pct))
        annualized_yield_est = 0.10 if h.pnl_pct > 50 else 0.07
        ideas.append(
            {
                "ticker": h.symbol,
                "strategy": "Covered call",
                "action": f"Sell up to {contracts} call contract(s), around ${strike:,.0f} strike",
                "rationale": (
                    f"{h.weight:.1f}% portfolio weight, +{h.pnl_pct:.1f}% unrealized gain; "
                    "harvest premium without adding downside exposure."
                ),
                "risk": "Cap upside above the short call strike; avoid if near a catalyst you want uncapped.",
                "score": h.weight + min(max(h.pnl_pct, 0), 150) / 20 + annualized_yield_est * 10,
            }
        )
    return sorted(ideas, key=lambda x: float(x["score"]), reverse=True)


def build_csp_ideas(
    holdings: list[Holding],
    watchlist: list[WatchlistItem],
    open_options: list[OptionPosition],
    quotes: dict[str, dict[str, float]],
) -> list[dict[str, object]]:
    prices = {holding.symbol: holding.current for holding in holdings}
    for ticker, quote in quotes.items():
        if quote.get("price"):
            prices[ticker] = quote["price"]
    open_puts = {pos.ticker for pos in open_options if pos.option_type.lower() == "put"}
    ideas: list[dict[str, object]] = []
    for item in watchlist:
        if item.score is None or item.score < 58:
            continue
        price = prices.get(item.ticker)
        if item.ticker in open_puts:
            continue
        if price:
            strike = nearest_strike(price * 0.90)
            action = f"Sell 0.20-0.30 delta put near ${strike:,.0f}"
            rationale = f"{item.grade} watchlist score ({item.score:.1f}) and 10% entry discount to ${price:,.2f} reference price."
        else:
            action = "Price live chain manually; target 0.20-0.30 delta put 10-15% OTM"
            rationale = f"{item.grade} watchlist score ({item.score:.1f}); no live quote available in this run."
        ideas.append(
            {
                "ticker": item.ticker,
                "strategy": "Cash-secured put",
                "action": action,
                "rationale": rationale,
                "risk": "Assignment adds single-name exposure; respect 5% position and 30% options allocation limits.",
                "score": item.score,
            }
        )
    return sorted(ideas, key=lambda x: float(x["score"]), reverse=True)


def build_risk_notes(holdings: list[Holding], open_options: list[OptionPosition]) -> list[str]:
    notes: list[str] = []
    concentration = [h for h in holdings if h.weight >= 10]
    if concentration:
        names = ", ".join(f"{h.symbol} {h.weight:.1f}%" for h in concentration)
        notes.append(f"Concentration watch: {names}. Prefer premium that reduces or hedges exposure.")
    challenged = [
        pos
        for pos in open_options
        if pos.option_type.lower() == "put" and pos.current > pos.credit * 1.5
    ]
    if challenged:
        names = ", ".join(f"{p.ticker} {p.expiration} ${p.strike:g}P" for p in challenged)
        notes.append(f"Manage challenged short puts before adding risk: {names}.")
    notes.append("Do not enter short premium through unplanned earnings; verify earnings dates and live chain liquidity before order entry.")
    return notes


def format_report(
    holdings: list[Holding],
    watchlist: list[WatchlistItem],
    open_options: list[OptionPosition],
    quotes: dict[str, dict[str, float]],
) -> tuple[str, str]:
    today = datetime.now(timezone.utc).date()
    expiry = next_monthly_expiration(today)
    cc_ideas = build_covered_call_ideas(holdings)[:5]
    csp_ideas = build_csp_ideas(holdings, watchlist, open_options, quotes)[:5]
    risk_notes = build_risk_notes(holdings, open_options)

    portfolio_value = sum(h.market_value for h in holdings)
    top_candidates = [item for item in watchlist if item.score is not None and item.score >= 58][:5]

    lines = [
        f"# Trade Idea Generator - {today.isoformat()}",
        "",
        "## Scope",
        "",
        f"- Portfolio context: {len(holdings)} holdings, ${portfolio_value:,.0f} market value from `context/portfolio-details.md`.",
        f"- Watchlist context: {len(watchlist)} tickers from `context/watchlist.md`; top candidates: "
        + ", ".join(f"{item.ticker} ({item.grade})" for item in top_candidates)
        + ".",
        f"- Target expiration window: approximately 30-45 DTE; nearest planning Friday: {expiry.isoformat()}.",
        "- Live FMP quotes: " + ("available for configured symbols." if quotes else "not configured; using repository context prices."),
        "",
        "## Top Covered Call Ideas",
        "",
    ]
    if cc_ideas:
        for idx, idea in enumerate(cc_ideas, 1):
            lines.extend(
                [
                    f"{idx}. **{idea['ticker']} - {idea['strategy']}**",
                    f"   - Action: {idea['action']} expiring near {expiry.isoformat()}.",
                    f"   - Rationale: {idea['rationale']}",
                    f"   - Risk: {idea['risk']}",
                ]
            )
    else:
        lines.append("- No covered call candidates met the portfolio/lot-size filters.")

    lines.extend(["", "## Top Cash-Secured Put Ideas", ""])
    if csp_ideas:
        for idx, idea in enumerate(csp_ideas, 1):
            lines.extend(
                [
                    f"{idx}. **{idea['ticker']} - {idea['strategy']}**",
                    f"   - Action: {idea['action']} expiring near {expiry.isoformat()}.",
                    f"   - Rationale: {idea['rationale']}",
                    f"   - Risk: {idea['risk']}",
                ]
            )
    else:
        lines.append("- No CSP candidates passed the score, price, and existing-risk filters from repository context.")

    lines.extend(["", "## Risk Notes", ""])
    lines.extend(f"- {note}" for note in risk_notes)
    lines.extend(
        [
            "",
            "## Execution Checklist",
            "",
            "- Confirm live bid/ask spread is under 10% of mid and open interest is adequate.",
            "- Size each new trade at or below 5% max position risk and keep total options allocation under 30%.",
            "- Close winners around 50% of max profit; stop or roll if loss reaches roughly 2x original credit or thesis changes.",
            "",
            "_Educational trade planning only; not financial advice._",
        ]
    )
    report = "\n".join(lines) + "\n"

    telegram_lines = [
        f"Altamira Trade Ideas - {today.isoformat()}",
        "",
        "Covered calls:",
    ]
    telegram_lines.extend(
        f"{idx}. {idea['ticker']}: {idea['action']} ({expiry.isoformat()})"
        for idx, idea in enumerate(cc_ideas[:3], 1)
    )
    if not cc_ideas:
        telegram_lines.append("None passed filters.")
    telegram_lines.extend(["", "CSP watchlist:"])
    telegram_lines.extend(
        f"{idx}. {idea['ticker']}: {idea['action']} ({expiry.isoformat()})"
        for idx, idea in enumerate(csp_ideas[:3], 1)
    )
    if not csp_ideas:
        telegram_lines.append("None passed filters.")
    telegram_lines.extend(["", "Risk: " + risk_notes[0], "", "Verify live chain liquidity/earnings before entry. Educational only."])
    telegram = "\n".join(telegram_lines)
    if len(telegram) > TELEGRAM_LIMIT:
        telegram = telegram[: TELEGRAM_LIMIT - 20] + "\n...[truncated]"
    return report, telegram


def send_telegram(message: str, chat_id: str, token: str) -> dict[str, object]:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Altamira trade ideas from repository context.")
    parser.add_argument("--send-telegram", action="store_true", help="Send concise output to Telegram.")
    parser.add_argument("--telegram-chat-id", default=os.environ.get("TELEGRAM_CHAT_ID", DEFAULT_CHAT_ID))
    parser.add_argument("--out", help="Optional output markdown path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    holdings = load_holdings()
    watchlist = load_watchlist()
    open_options = load_options()
    if not holdings or not watchlist:
        print("Portfolio or watchlist context is missing.", file=sys.stderr)
        return 1

    fmp_key = os.environ.get("FMP_API_KEY")
    quote_symbols = [h.symbol for h in holdings] + [item.ticker for item in watchlist]
    quotes = fetch_fmp_quotes(quote_symbols, fmp_key)
    report, telegram = format_report(holdings, watchlist, open_options, quotes)

    OUTPUTS.mkdir(exist_ok=True)
    out_path = Path(args.out) if args.out else OUTPUTS / f"trade-idea-generator-{date.today().isoformat()}.md"
    if not out_path.is_absolute():
        out_path = WORKSPACE / out_path
    out_path.write_text(report, encoding="utf-8")
    print(f"Wrote {out_path.relative_to(WORKSPACE)}")

    telegram_path = OUTPUTS / f"trade-idea-generator-telegram-{date.today().isoformat()}.txt"
    telegram_path.write_text(textwrap.dedent(telegram).strip() + "\n", encoding="utf-8")
    print(f"Wrote {telegram_path.relative_to(WORKSPACE)}")

    if args.send_telegram:
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not token:
            print("TELEGRAM_BOT_TOKEN is not set; cannot send Telegram message.", file=sys.stderr)
            return 2
        try:
            result = send_telegram(telegram, args.telegram_chat_id, token)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            print(f"Telegram send failed: {exc}", file=sys.stderr)
            return 3
        if not result.get("ok"):
            print(f"Telegram send failed: {result}", file=sys.stderr)
            return 3
        print("Telegram message sent.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
