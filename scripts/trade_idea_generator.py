#!/usr/bin/env python3
"""Generate daily trade ideas from portfolio/watchlist context and notify Telegram.

The script intentionally uses the repository's markdown context as the source of
truth, so it can run from automation without a dashboard or Google Sheets session.
Live market data is used when FMP_API_KEY is available; otherwise the latest
prices stored in the context files are used.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import textwrap
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


WORKSPACE = Path(__file__).resolve().parent.parent
CONTEXT_DIR = WORKSPACE / "context"
OUTPUTS_DIR = WORKSPACE / "outputs"
PORTFOLIO_PATH = CONTEXT_DIR / "portfolio-details.md"
WATCHLIST_PATH = CONTEXT_DIR / "watchlist.md"
CSP_FIXED_WORKFLOW_PATH = OUTPUTS_DIR / "csp-daily-scan-fixed.json"
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"


@dataclass(frozen=True)
class PortfolioPosition:
    symbol: str
    quantity: float
    average_price: float
    current_price: float
    market_value: float
    cost_basis: float
    pnl_percent: float
    day_change_percent: float
    weight_percent: float


@dataclass(frozen=True)
class OptionPosition:
    ticker: str
    strike: float
    option_type: str
    expiration: str
    credit: float
    current: float
    contracts: int


@dataclass(frozen=True)
class WatchlistCandidate:
    ticker: str
    score: float | None
    grade: str | None
    company: str
    status: str


@dataclass
class TradeIdea:
    rank_score: float
    ticker: str
    source: str
    action: str
    setup: str
    rationale: list[str]
    risk: str
    management: str
    data: dict[str, Any]


def parse_money(value: str) -> float:
    cleaned = value.replace("$", "").replace(",", "").strip()
    if cleaned in {"", "-", "—"}:
        return 0.0
    return float(cleaned)


def parse_float(value: str) -> float:
    cleaned = value.replace(",", "").strip()
    if cleaned in {"", "-", "—"}:
        return 0.0
    return float(cleaned)


def parse_percent(value: str) -> float:
    match = re.search(r"([+-]?\d+(?:\.\d+)?)%", value)
    return float(match.group(1)) if match else 0.0


def strip_markdown(value: str) -> str:
    return (
        value.replace("**", "")
        .replace("\u2b50", "")
        .replace("\u2014", "")
        .strip()
    )


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Required context file not found: {path}")
    return path.read_text(encoding="utf-8")


def parse_portfolio_positions(markdown: str) -> list[PortfolioPosition]:
    positions: list[PortfolioPosition] = []
    in_table = False

    for line in markdown.splitlines():
        if line.startswith("| SYMBOL |"):
            in_table = True
            continue
        if not in_table:
            continue
        if not line.startswith("|"):
            if positions:
                break
            continue
        if set(line.replace("|", "").strip()) <= {"-"}:
            continue
        if line.startswith("|--------"):
            continue

        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 9 or cells[0].lower().startswith("totals"):
            continue

        try:
            positions.append(
                PortfolioPosition(
                    symbol=strip_markdown(cells[0]).upper(),
                    quantity=parse_float(cells[1]),
                    average_price=parse_money(cells[2]),
                    current_price=parse_money(cells[3]),
                    market_value=parse_money(cells[4]),
                    cost_basis=parse_money(cells[5]),
                    pnl_percent=parse_percent(cells[6]),
                    day_change_percent=parse_percent(cells[7]),
                    weight_percent=parse_percent(cells[8]),
                )
            )
        except ValueError:
            continue

    return positions


def parse_option_positions(markdown: str) -> list[OptionPosition]:
    options: list[OptionPosition] = []
    in_table = False

    for line in markdown.splitlines():
        if line.startswith("| Ticker | Strike | Type | Expiration |"):
            in_table = True
            continue
        if not in_table:
            continue
        if not line.startswith("|"):
            if options:
                break
            continue
        if line.startswith("|--------"):
            continue

        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 7:
            continue
        try:
            options.append(
                OptionPosition(
                    ticker=strip_markdown(cells[0]).upper(),
                    strike=parse_float(cells[1]),
                    option_type=strip_markdown(cells[2]),
                    expiration=strip_markdown(cells[3]),
                    credit=parse_float(cells[4]),
                    current=parse_float(cells[5]),
                    contracts=int(parse_float(cells[6])),
                )
            )
        except ValueError:
            continue

    return options


def parse_portfolio_value(markdown: str, positions: list[PortfolioPosition]) -> float:
    match = re.search(r"\*\*Total MKT VALUE\*\*\s*\|\s*\$([\d,]+)", markdown)
    if match:
        return parse_money(match.group(1))
    return sum(position.market_value for position in positions)


def parse_watchlist(markdown: str) -> list[WatchlistCandidate]:
    candidates: list[WatchlistCandidate] = []
    in_table = False

    for line in markdown.splitlines():
        if line.startswith("| Ticker | Score | Grade | Company | Status |"):
            in_table = True
            continue
        if not in_table:
            continue
        if not line.startswith("|"):
            if candidates:
                break
            continue
        if line.startswith("|--------"):
            continue

        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 5:
            continue
        ticker = strip_markdown(cells[0]).upper()
        if not ticker:
            continue
        score_text = strip_markdown(cells[1])
        score = None if not score_text else parse_float(score_text)
        candidates.append(
            WatchlistCandidate(
                ticker=ticker,
                score=score,
                grade=strip_markdown(cells[2]) or None,
                company=strip_markdown(cells[3]),
                status=strip_markdown(cells[4]),
            )
        )

    return candidates


def fmp_get(path: str, api_key: str, timeout: int = 12) -> Any:
    separator = "&" if "?" in path else "?"
    url = f"{FMP_BASE_URL}{path}{separator}{urllib.parse.urlencode({'apikey': api_key})}"
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_quotes(tickers: list[str], api_key: str | None) -> dict[str, dict[str, Any]]:
    if not api_key or not tickers:
        return {}
    quotes: dict[str, dict[str, Any]] = {}
    chunk_size = 50
    for index in range(0, len(tickers), chunk_size):
        chunk = tickers[index : index + chunk_size]
        try:
            data = fmp_get(f"/quote/{','.join(chunk)}", api_key)
        except Exception as exc:  # noqa: BLE001 - report and continue with static context.
            print(f"Warning: quote fetch failed for {','.join(chunk)}: {exc}", file=sys.stderr)
            continue
        if isinstance(data, list):
            for quote in data:
                symbol = str(quote.get("symbol", "")).upper()
                if symbol:
                    quotes[symbol] = quote
    return quotes


def fetch_vix(api_key: str | None) -> float | None:
    if not api_key:
        return None
    try:
        data = fmp_get("/quote/%5EVIX", api_key)
    except Exception as exc:  # noqa: BLE001
        print(f"Warning: VIX fetch failed: {exc}", file=sys.stderr)
        return None
    if isinstance(data, list) and data:
        price = data[0].get("price")
        return float(price) if price is not None else None
    return None


def fetch_earnings(tickers: list[str], api_key: str | None) -> dict[str, str]:
    if not api_key:
        return {}
    today = date.today()
    end = today + timedelta(days=45)
    try:
        data = fmp_get(f"/earning_calendar?from={today.isoformat()}&to={end.isoformat()}", api_key)
    except Exception as exc:  # noqa: BLE001
        print(f"Warning: earnings fetch failed: {exc}", file=sys.stderr)
        return {}

    earnings: dict[str, str] = {}
    universe = set(tickers)
    if isinstance(data, list):
        for item in data:
            symbol = str(item.get("symbol", "")).upper()
            report_date = item.get("date")
            if symbol in universe and report_date and symbol not in earnings:
                earnings[symbol] = str(report_date)
    return earnings


def quote_price(symbol: str, fallback: float, quotes: dict[str, dict[str, Any]]) -> float:
    value = quotes.get(symbol, {}).get("price")
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def quote_metric(symbol: str, key: str, quotes: dict[str, dict[str, Any]]) -> float | None:
    value = quotes.get(symbol, {}).get(key)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def vix_regime(vix: float | None) -> str:
    if vix is None:
        return "UNKNOWN"
    if vix < 15:
        return "LOW"
    if vix <= 25:
        return "NORMAL"
    if vix <= 35:
        return "ELEVATED"
    return "CRISIS"


def covered_call_strike(price: float) -> float:
    if price >= 500:
        increment = 10
    elif price >= 100:
        increment = 5
    else:
        increment = 1
    raw = price * 1.05
    return round(raw / increment) * increment


def csp_strike(price: float) -> float:
    if price >= 500:
        increment = 10
    elif price >= 100:
        increment = 5
    else:
        increment = 1
    raw = price * 0.92
    return round(raw / increment) * increment


def next_standard_expiration() -> str:
    target = date.today() + timedelta(days=38)
    # Prefer Friday expirations in the 30-45 DTE window.
    days_until_friday = (4 - target.weekday()) % 7
    friday = target + timedelta(days=days_until_friday)
    if (friday - date.today()).days > 45:
        friday -= timedelta(days=7)
    return friday.isoformat()


def build_trade_ideas(
    positions: list[PortfolioPosition],
    options: list[OptionPosition],
    watchlist: list[WatchlistCandidate],
    quotes: dict[str, dict[str, Any]],
    earnings: dict[str, str],
    portfolio_value: float,
) -> list[TradeIdea]:
    ideas: list[TradeIdea] = []
    option_tickers = {option.ticker for option in options}

    for position in positions:
        symbol = position.symbol
        if symbol in {"FFOLX"}:
            continue

        price = quote_price(symbol, position.current_price, quotes)
        avg50 = quote_metric(symbol, "priceAvg50", quotes)
        year_high = quote_metric(symbol, "yearHigh", quotes)
        live_day_change = quote_metric(symbol, "changesPercentage", quotes)
        day_change = live_day_change if live_day_change is not None else position.day_change_percent

        if position.quantity >= 100 and position.weight_percent >= 4.0:
            concentration_boost = max(0.0, position.weight_percent - 5.0) * 2.0
            profit_boost = max(0.0, position.pnl_percent) / 8.0
            technical_boost = 0.0
            if year_high and price >= year_high * 0.88:
                technical_boost += 8.0
            if avg50 and price >= avg50:
                technical_boost += 4.0
            if symbol in option_tickers:
                technical_boost -= 4.0

            strike = covered_call_strike(price)
            rationale = [
                f"{position.weight_percent:.1f}% portfolio weight creates single-name concentration.",
                f"Unrealized gain is {position.pnl_percent:+.1f}%; covered calls can harvest income without adding delta.",
            ]
            if avg50:
                rationale.append(
                    f"Price is {'above' if price >= avg50 else 'below'} 50-day average (${avg50:.2f})."
                )
            if symbol in option_tickers:
                rationale.append("Existing short-premium exposure already exists; size any new call sale conservatively.")

            ideas.append(
                TradeIdea(
                    rank_score=55.0 + concentration_boost + profit_boost + technical_boost,
                    ticker=symbol,
                    source="Portfolio",
                    action="Income / risk trim",
                    setup=f"Consider covered call near ${strike:.0f} expiring {next_standard_expiration()}",
                    rationale=rationale,
                    risk="Caps upside if the position keeps trending; avoid adding if earnings are inside the option window.",
                    management="Target 50% premium capture; close or roll if delta moves above ~0.45.",
                    data={
                        "price": price,
                        "weight": position.weight_percent,
                        "day_change": day_change,
                        "pnl_percent": position.pnl_percent,
                    },
                )
            )

        if position.weight_percent >= 10.0:
            trim_percent = min(3.0, position.weight_percent - 8.0)
            rationale = [
                f"{symbol} is {position.weight_percent:.1f}% of portfolio versus a 5% single-position risk guideline.",
                f"Market value is approximately ${position.market_value:,.0f}.",
            ]
            if day_change >= 1.5:
                rationale.append(f"Today strength of {day_change:+.1f}% offers liquidity for a partial rebalance.")
            ideas.append(
                TradeIdea(
                    rank_score=60.0 + position.weight_percent + max(position.pnl_percent, 0.0) / 12.0,
                    ticker=symbol,
                    source="Portfolio",
                    action="Concentration control",
                    setup=f"Trim roughly {trim_percent:.1f}% portfolio weight or pair with covered calls",
                    rationale=rationale,
                    risk="Tax impact and opportunity cost if the leadership trend continues.",
                    management="Reallocate proceeds to cash reserve, underweight sectors, or highest-grade watchlist names.",
                    data={
                        "price": price,
                        "weight": position.weight_percent,
                        "day_change": day_change,
                        "pnl_percent": position.pnl_percent,
                    },
                )
            )

    held_symbols = {position.symbol for position in positions}
    for candidate in watchlist:
        if candidate.ticker in held_symbols:
            continue
        if candidate.score is None:
            base_score = 45.0
        else:
            base_score = candidate.score

        quote = quotes.get(candidate.ticker, {})
        price_value = quote.get("price")
        price = float(price_value) if isinstance(price_value, (int, float)) else None
        avg50 = quote_metric(candidate.ticker, "priceAvg50", quotes)
        year_high = quote_metric(candidate.ticker, "yearHigh", quotes)
        changes_pct = quote_metric(candidate.ticker, "changesPercentage", quotes)

        if "Avoid" in candidate.status or "Low Priority" in candidate.status:
            continue
        if base_score < 50 and "Top Candidate" not in candidate.status:
            continue

        trend_boost = 0.0
        rationale = [
            f"Watchlist status: {candidate.status}; score {candidate.score if candidate.score is not None else 'unscored'} ({candidate.grade or 'n/a'})."
        ]
        if price and avg50:
            if price >= avg50:
                trend_boost += 6.0
                rationale.append(f"Price ${price:.2f} is above 50-day average ${avg50:.2f}.")
            else:
                trend_boost -= 3.0
                rationale.append(f"Price ${price:.2f} is below 50-day average ${avg50:.2f}; wait for confirmation.")
        if price and year_high and price <= year_high * 0.90:
            trend_boost += 3.0
            rationale.append("Entry is not extended versus the 52-week high.")
        if candidate.ticker in earnings:
            trend_boost -= 10.0
            rationale.append(f"Earnings expected {earnings[candidate.ticker]}; avoid short options through the event.")

        if price:
            setup = f"Cash-secured put watch near ${csp_strike(price):.0f} expiring {next_standard_expiration()}"
            risk = "Assignment risk; only sell puts at a price acceptable for long-term ownership."
        else:
            setup = "Add to manual review queue for CSP or starter equity entry"
            risk = "No live quote available in this run; verify price, liquidity, and earnings before trading."

        ideas.append(
            TradeIdea(
                rank_score=base_score + trend_boost,
                ticker=candidate.ticker,
                source="Watchlist",
                action="Potential entry",
                setup=setup,
                rationale=rationale,
                risk=risk,
                management="Use 0.20-0.30 delta, 30-45 DTE, close at 50% profit, stop at 200% of credit.",
                data={
                    "price": price,
                    "score": candidate.score,
                    "grade": candidate.grade,
                    "day_change": changes_pct,
                    "portfolio_value": portfolio_value,
                },
            )
        )

    return sorted(ideas, key=lambda idea: idea.rank_score, reverse=True)


def render_report(
    ideas: list[TradeIdea],
    positions: list[PortfolioPosition],
    options: list[OptionPosition],
    watchlist: list[WatchlistCandidate],
    portfolio_value: float,
    vix: float | None,
    used_live_data: bool,
) -> str:
    today = date.today().isoformat()
    top_positions = sorted(positions, key=lambda item: item.weight_percent, reverse=True)[:5]
    top_watchlist = [item for item in watchlist if "Top Candidate" in item.status][:5]
    lines: list[str] = [
        f"# Trade Idea Generator - {today}",
        "",
        "> Automated scan of `context/portfolio-details.md` and `context/watchlist.md`.",
        "",
        "## Dashboard",
        "",
        f"- Portfolio value: ${portfolio_value:,.0f}",
        f"- Positions scanned: {len(positions)} equities/funds; {len(options)} option positions",
        f"- Watchlist candidates scanned: {len(watchlist)}",
        f"- VIX: {vix:.2f} ({vix_regime(vix)})" if vix is not None else "- VIX: unavailable",
        f"- Market data: {'live FMP quotes' if used_live_data else 'repository snapshot prices only'}",
        "",
        "## Top Trade Ideas",
        "",
    ]

    if not ideas:
        lines.extend(
            [
                "No qualifying trade ideas were generated from the current inputs.",
                "",
            ]
        )
    for index, idea in enumerate(ideas[:8], start=1):
        price = idea.data.get("price")
        price_text = f"${price:.2f}" if isinstance(price, (int, float)) else "n/a"
        lines.extend(
            [
                f"### {index}. {idea.ticker} - {idea.action}",
                "",
                f"- **Source:** {idea.source}",
                f"- **Setup:** {idea.setup}",
                f"- **Reference price:** {price_text}",
                f"- **Rank score:** {idea.rank_score:.1f}",
                "- **Rationale:**",
            ]
        )
        lines.extend([f"  - {reason}" for reason in idea.rationale])
        lines.extend(
            [
                f"- **Risk:** {idea.risk}",
                f"- **Management:** {idea.management}",
                "",
            ]
        )

    lines.extend(
        [
            "## Current Concentration Snapshot",
            "",
            "| Ticker | Weight | P&L | Day Change |",
            "|--------|--------|-----|------------|",
        ]
    )
    for position in top_positions:
        lines.append(
            f"| {position.symbol} | {position.weight_percent:.1f}% | "
            f"{position.pnl_percent:+.1f}% | {position.day_change_percent:+.1f}% |"
        )

    lines.extend(
        [
            "",
            "## Top Watchlist Candidates",
            "",
            "| Ticker | Score | Grade | Status |",
            "|--------|-------|-------|--------|",
        ]
    )
    for candidate in top_watchlist:
        score = f"{candidate.score:.1f}" if candidate.score is not None else "n/a"
        lines.append(f"| {candidate.ticker} | {score} | {candidate.grade or 'n/a'} | {candidate.status} |")

    lines.extend(
        [
            "",
            "## Disclaimers",
            "",
            "- This is not financial advice and is for research/workflow automation only.",
            "- Verify live option chains, bid/ask spreads, earnings dates, tax impact, and portfolio limits before placing trades.",
            "- Options involve substantial risk; use the Altamira risk framework for sizing and exits.",
            "",
        ]
    )
    return "\n".join(lines)


def render_telegram_message(ideas: list[TradeIdea], portfolio_value: float, vix: float | None) -> str:
    lines = [
        f"Trade Ideas - {date.today().isoformat()}",
        f"Portfolio: ${portfolio_value:,.0f} | VIX: {vix:.1f} ({vix_regime(vix)})" if vix is not None else f"Portfolio: ${portfolio_value:,.0f}",
        "",
    ]

    if not ideas:
        lines.append("No qualifying ideas from current portfolio/watchlist context.")
    for index, idea in enumerate(ideas[:5], start=1):
        price = idea.data.get("price")
        price_text = f"${price:.2f}" if isinstance(price, (int, float)) else "n/a"
        lines.extend(
            [
                f"{index}. {idea.ticker} - {idea.action}",
                f"   {idea.setup}",
                f"   Ref: {price_text} | Score: {idea.rank_score:.1f} | Source: {idea.source}",
                f"   Why: {idea.rationale[0] if idea.rationale else 'See report.'}",
                "",
            ]
        )

    lines.extend(
        [
            "Risk: verify options chain, earnings, liquidity, and sizing before entry.",
            "Generated from repository portfolio/watchlist context.",
        ]
    )
    return "\n".join(lines)[:3900]


def resolve_telegram_chat_id(explicit_chat_id: str | None) -> str | None:
    if explicit_chat_id:
        return explicit_chat_id
    env_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if env_chat_id:
        return env_chat_id
    if CSP_FIXED_WORKFLOW_PATH.exists():
        try:
            workflow = json.loads(CSP_FIXED_WORKFLOW_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
        for node in workflow.get("nodes", []):
            parameters = node.get("parameters", {})
            chat_id = parameters.get("chatId")
            if isinstance(chat_id, str):
                cleaned = chat_id.lstrip("=").strip()
                if cleaned:
                    return cleaned
    return None


def send_telegram_message(text: str, chat_id: str, bot_token: str) -> dict[str, Any]:
    payload = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    request = urllib.request.Request(url, data=payload, method="POST")
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def write_report(report: str) -> Path:
    OUTPUTS_DIR.mkdir(exist_ok=True)
    path = OUTPUTS_DIR / f"trade-idea-generator-{date.today().isoformat()}.md"
    path.write_text(report, encoding="utf-8")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate portfolio/watchlist trade ideas.")
    parser.add_argument("--send-telegram", action="store_true", help="Send summary to Telegram.")
    parser.add_argument("--telegram-chat-id", help="Telegram chat/channel id. Defaults to env/config.")
    parser.add_argument("--max-ideas", type=int, default=8, help="Maximum ideas to include in report.")
    parser.add_argument("--no-live-data", action="store_true", help="Do not call FMP even if FMP_API_KEY is set.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    portfolio_md = read_text(PORTFOLIO_PATH)
    watchlist_md = read_text(WATCHLIST_PATH)

    positions = parse_portfolio_positions(portfolio_md)
    options = parse_option_positions(portfolio_md)
    watchlist = parse_watchlist(watchlist_md)
    portfolio_value = parse_portfolio_value(portfolio_md, positions)

    if not positions:
        raise RuntimeError("No portfolio positions parsed from context/portfolio-details.md")
    if not watchlist:
        raise RuntimeError("No watchlist candidates parsed from context/watchlist.md")

    api_key = None if args.no_live_data else os.environ.get("FMP_API_KEY")
    tickers = sorted({p.symbol for p in positions if p.symbol != "FFOLX"} | {w.ticker for w in watchlist})
    quotes = fetch_quotes(tickers, api_key)
    vix = fetch_vix(api_key)
    earnings = fetch_earnings(tickers, api_key)
    ideas = build_trade_ideas(positions, options, watchlist, quotes, earnings, portfolio_value)

    if args.max_ideas > 0:
        ideas = ideas[: args.max_ideas]

    report = render_report(
        ideas=ideas,
        positions=positions,
        options=options,
        watchlist=watchlist,
        portfolio_value=portfolio_value,
        vix=vix,
        used_live_data=bool(quotes),
    )
    report_path = write_report(report)
    telegram_text = render_telegram_message(ideas, portfolio_value, vix)

    telegram_sent = False
    if args.send_telegram:
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = resolve_telegram_chat_id(args.telegram_chat_id)
        if not bot_token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN is required to send Telegram notifications.")
        if not chat_id:
            raise RuntimeError("TELEGRAM_CHAT_ID or repository Telegram chat config is required.")
        result = send_telegram_message(telegram_text, chat_id, bot_token)
        telegram_sent = bool(result.get("ok"))
        if not telegram_sent:
            raise RuntimeError(f"Telegram API returned non-ok response: {result}")

    summary = textwrap.dedent(
        f"""
        Trade idea generator complete.
        Report: {report_path.relative_to(WORKSPACE)}
        Ideas: {len(ideas)}
        Telegram sent: {'yes' if telegram_sent else 'no'}
        Generated at: {datetime.now(timezone.utc).isoformat()}
        """
    ).strip()
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
