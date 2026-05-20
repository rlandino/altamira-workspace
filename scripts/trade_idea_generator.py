#!/usr/bin/env python3
"""Generate daily trade ideas from repository portfolio/watchlist context.

The script intentionally uses only local context files so scheduled automation can
run even when market-data API keys are unavailable in the runtime.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


WORKSPACE = Path(__file__).resolve().parent.parent
CONTEXT_DIR = WORKSPACE / "context"
OUTPUTS_DIR = WORKSPACE / "outputs"
PORTFOLIO_PATH = CONTEXT_DIR / "portfolio-details.md"
OPTIONS_PATH = CONTEXT_DIR / "options-positions.md"
WATCHLIST_PATH = CONTEXT_DIR / "watchlist.md"

MAX_SINGLE_POSITION_WEIGHT = 5.0
HIGH_CONCENTRATION_WEIGHT = 10.0
TELEGRAM_LIMIT = 3900


@dataclass
class Holding:
    ticker: str
    quantity: float
    average_price: float
    current_price: float
    market_value: float
    pnl_percent: float
    day_change_percent: float
    weight: float


@dataclass
class OptionPosition:
    ticker: str
    strike: float
    option_type: str
    expiration: str
    credit: float
    current: float
    contracts: int

    @property
    def unrealized_pl(self) -> float:
        return (self.credit - self.current) * self.contracts * 100

    @property
    def profit_capture_percent(self) -> float:
        if self.credit == 0:
            return 0.0
        return (self.credit - self.current) / self.credit * 100

    @property
    def notional(self) -> float:
        return self.strike * self.contracts * 100


@dataclass
class WatchlistCandidate:
    ticker: str
    score: float | None
    grade: str
    company: str
    status: str


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"Required context file not found: {path}") from None


def money_to_float(value: str) -> float:
    clean = value.strip().replace("$", "").replace(",", "")
    if clean in {"", "-"}:
        return 0.0
    return float(clean)


def number_to_float(value: str) -> float:
    clean = value.strip().replace(",", "").replace("%", "")
    if clean in {"", "-", "—"}:
        return 0.0
    return float(clean)


def parse_markdown_rows(text: str, header_first_cell: str) -> list[list[str]]:
    rows: list[list[str]] = []
    in_table = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            if in_table:
                break
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells:
            continue
        if cells[0] == header_first_cell:
            in_table = True
            continue
        if in_table and set(cells[0]) <= {"-"}:
            continue
        if in_table:
            rows.append(cells)
    return rows


def parse_holdings(text: str) -> list[Holding]:
    holdings: list[Holding] = []
    for cells in parse_markdown_rows(text, "SYMBOL"):
        if len(cells) < 9 or cells[0].startswith("**Totals"):
            continue
        pnl_match = re.search(r"\(([-+0-9.,]+)%\)", cells[6])
        day_match = re.search(r"\(([-+0-9.,]+)%\)", cells[7])
        holdings.append(
            Holding(
                ticker=cells[0],
                quantity=number_to_float(cells[1]),
                average_price=money_to_float(cells[2]),
                current_price=money_to_float(cells[3]),
                market_value=money_to_float(cells[4]),
                pnl_percent=number_to_float(pnl_match.group(1) if pnl_match else "0"),
                day_change_percent=number_to_float(day_match.group(1) if day_match else "0"),
                weight=number_to_float(cells[8]),
            )
        )
    return holdings


def parse_options(text: str) -> list[OptionPosition]:
    positions: list[OptionPosition] = []
    for cells in parse_markdown_rows(text, "Ticker"):
        if len(cells) < 7:
            continue
        try:
            positions.append(
                OptionPosition(
                    ticker=cells[0],
                    strike=number_to_float(cells[1]),
                    option_type=cells[2],
                    expiration=cells[3],
                    credit=number_to_float(cells[4]),
                    current=number_to_float(cells[5]),
                    contracts=int(number_to_float(cells[6])),
                )
            )
        except ValueError:
            continue
    return positions


def parse_watchlist(text: str) -> list[WatchlistCandidate]:
    candidates: list[WatchlistCandidate] = []
    for cells in parse_markdown_rows(text, "Ticker"):
        if len(cells) < 5:
            continue
        score = None if cells[1] in {"—", "-", ""} else number_to_float(cells[1])
        candidates.append(
            WatchlistCandidate(
                ticker=cells[0],
                score=score,
                grade=cells[2].replace("**", ""),
                company=cells[3],
                status=cells[4],
            )
        )
    return candidates


def parse_total_market_value(text: str, holdings: Iterable[Holding]) -> float:
    match = re.search(r"\*\*Total MKT VALUE\*\*\s*\|\s*\$([0-9,]+)", text)
    if match:
        return money_to_float(match.group(1))
    return sum(holding.market_value for holding in holdings)


def grade_rank(grade: str) -> int:
    order = {
        "A+": 12,
        "A": 11,
        "A-": 10,
        "B+": 9,
        "B": 8,
        "B-": 7,
        "C+": 6,
        "C": 5,
        "C-": 4,
        "D+": 3,
        "D": 2,
        "F": 1,
    }
    return order.get(grade.strip(), 0)


def option_actions(options: list[OptionPosition], holding_by_ticker: dict[str, Holding]) -> list[str]:
    actions: list[str] = []
    for pos in sorted(options, key=lambda p: p.profit_capture_percent, reverse=True):
        holding = holding_by_ticker.get(pos.ticker)
        price = holding.current_price if holding else 0.0
        moneyness = ""
        if price and pos.option_type.lower() == "put":
            distance = (price - pos.strike) / price * 100
            moneyness = f" Underlying is {distance:+.1f}% vs strike."
        if pos.profit_capture_percent >= 50:
            action = "CLOSE / harvest profit"
        elif pos.profit_capture_percent <= -75:
            action = "DEFEND / roll or reduce risk"
        elif pos.profit_capture_percent < 0:
            action = "WATCH / avoid adding correlated premium"
        else:
            action = "HOLD / manage at 50% profit"
        actions.append(
            f"- {action}: {pos.ticker} {pos.strike:g}{pos.option_type[0].upper()} "
            f"{pos.expiration}, credit ${pos.credit:.2f}, current ${pos.current:.2f}, "
            f"P/L ${pos.unrealized_pl:,.0f} ({pos.profit_capture_percent:+.0f}% of credit).{moneyness}"
        )
    return actions


def sector_note(ticker: str) -> str:
    semis = {"AVGO", "AMAT", "LRCX", "NVDA", "TSM", "KLAC", "ASML", "MRVL"}
    mega_cap_tech = {"AAPL", "AMZN", "GOOGL", "META", "MSFT", "NVDA"}
    if ticker in semis:
        return "semiconductor/AI exposure; use defined risk while AVGO+AMAT are already large"
    if ticker in mega_cap_tech:
        return "mega-cap tech exposure; size against existing concentration"
    return "diversifies current portfolio factor mix better than another semi/mega-cap add"


def candidate_ideas(
    candidates: list[WatchlistCandidate], existing_tickers: set[str]
) -> list[str]:
    ranked = sorted(
        candidates,
        key=lambda c: ((c.score or 0), grade_rank(c.grade)),
        reverse=True,
    )
    ideas: list[str] = []
    for candidate in ranked:
        if len(ideas) >= 5:
            break
        if candidate.ticker in existing_tickers:
            continue
        if grade_rank(candidate.grade) < grade_rank("B-"):
            continue
        structure = "bull put spread" if candidate.ticker in {"LRCX", "NVDA", "TSM", "KLAC", "ASML"} else "cash-secured put"
        score = f"{candidate.score:.1f}" if candidate.score is not None else "N/A"
        ideas.append(
            f"- {candidate.ticker} ({candidate.grade}, score {score}) — {candidate.company}: "
            f"consider a 30-45 DTE 0.20-0.25 delta {structure}; {sector_note(candidate.ticker)}."
        )
    return ideas


def concentration_ideas(holdings: list[Holding]) -> list[str]:
    ideas: list[str] = []
    for holding in sorted(holdings, key=lambda h: h.weight, reverse=True):
        if holding.weight < HIGH_CONCENTRATION_WEIGHT:
            continue
        ideas.append(
            f"- {holding.ticker}: {holding.weight:.1f}% portfolio weight vs {MAX_SINGLE_POSITION_WEIGHT:.0f}% guideline; "
            f"use covered calls, trimming, or no-add discipline until weight normalizes."
        )
    return ideas


def build_report(
    date_str: str,
    holdings: list[Holding],
    options: list[OptionPosition],
    candidates: list[WatchlistCandidate],
    total_market_value: float,
) -> tuple[str, str]:
    holding_by_ticker = {holding.ticker: holding for holding in holdings}
    watchlist_ideas = candidate_ideas(candidates, set(holding_by_ticker))
    option_manage = option_actions(options, holding_by_ticker)
    concentration = concentration_ideas(holdings)
    option_notional = sum(option.notional for option in options)
    option_notional_pct = option_notional / total_market_value * 100 if total_market_value else 0.0
    top_holdings = sorted(holdings, key=lambda h: h.weight, reverse=True)[:5]

    primary = []
    if option_manage:
        primary.append(option_manage[0])
    if watchlist_ideas:
        primary.append(watchlist_ideas[0])
    if concentration:
        primary.append(concentration[0])

    summary_lines = [
        f"Altamira Trade Ideas - {date_str}",
        "",
        "Priority actions",
        *primary,
        "",
        "Watchlist setups",
        *(watchlist_ideas or ["- No B- or better new candidates found in watchlist."]),
        "",
        "Options book",
        *option_manage,
        "",
        "Risk flags",
        f"- Options notional: ${option_notional:,.0f} ({option_notional_pct:.1f}% of portfolio market value).",
        *(concentration or ["- No holding above 10% concentration threshold."]),
        "",
        "Not financial advice; review live chain liquidity, IV, earnings dates, and portfolio limits before trading.",
    ]

    report_lines = [
        f"# Trade Idea Generator — {date_str}",
        "",
        "> Source: repository context files (`portfolio-details.md`, `options-positions.md`, `watchlist.md`).",
        "> Live options-chain data was not required; verify current market prices before order entry.",
        "",
        "## Portfolio Snapshot",
        "",
        f"- **Portfolio market value:** ${total_market_value:,.0f}",
        f"- **Open short-premium notional:** ${option_notional:,.0f} ({option_notional_pct:.1f}% of market value)",
        "- **Top holdings by weight:** "
        + ", ".join(f"{h.ticker} {h.weight:.1f}%" for h in top_holdings),
        "",
        "## Priority Trade Ideas",
        "",
        *(primary or ["- No immediate action generated from current context."]),
        "",
        "## Watchlist Entry Setups",
        "",
        *(watchlist_ideas or ["- No B- or better new candidates found in watchlist."]),
        "",
        "## Open Options Management",
        "",
        *option_manage,
        "",
        "## Concentration / Risk Controls",
        "",
        *(concentration or ["- No holding above 10% concentration threshold."]),
        f"- Options notional check: {option_notional_pct:.1f}% vs 30% framework limit.",
        "- Avoid adding premium on names with challenged short puts until the book is back inside target risk.",
        "",
        "## Operating Checklist",
        "",
        "- Confirm no earnings are inside the target expiration window.",
        "- Use 30-45 DTE and 0.20-0.25 delta as the default short-premium lane.",
        "- Favor defined-risk spreads when adding to already concentrated semiconductor/AI exposure.",
        "- Set 50% profit-taking and 200% loss-management alerts at entry.",
        "",
        "## Disclaimer",
        "",
        "For research and paper-trading workflow support only; not financial advice or an order recommendation.",
        "",
    ]

    return "\n".join(report_lines), "\n".join(summary_lines)


def find_chat_id_from_workflows() -> str | None:
    for path in sorted(OUTPUTS_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        for node in data.get("nodes", []):
            params = node.get("parameters", {})
            chat_id = str(params.get("chatId", "")).strip()
            if chat_id.startswith("=") and re.fullmatch(r"=-?\d{6,}", chat_id):
                chat_id = chat_id[1:]
            if re.fullmatch(r"-?\d{6,}", chat_id):
                return chat_id
    return None


def telegram_chunks(message: str) -> list[str]:
    chunks: list[str] = []
    current = ""
    for line in message.splitlines():
        if len(current) + len(line) + 1 > TELEGRAM_LIMIT:
            chunks.append(current.rstrip())
            current = ""
        current += line + "\n"
    if current.strip():
        chunks.append(current.rstrip())
    return chunks


def send_telegram(message: str, chat_id: str | None) -> int:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set; cannot send Telegram message.")
    resolved_chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID") or find_chat_id_from_workflows()
    if not resolved_chat_id:
        raise SystemExit("Telegram chat ID not found. Set TELEGRAM_CHAT_ID or pass --telegram-chat-id.")

    sent = 0
    for chunk in telegram_chunks(message):
        payload = urllib.parse.urlencode(
            {
                "chat_id": resolved_chat_id,
                "text": chunk,
                "disable_web_page_preview": "true",
            }
        ).encode("utf-8")
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        request = urllib.request.Request(url, data=payload, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                response_data = json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - surface API/network errors clearly for automation logs.
            raise SystemExit(f"Telegram send failed: {exc}") from exc
        if not response_data.get("ok"):
            raise SystemExit(f"Telegram send failed: {response_data}")
        sent += 1
    return sent


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate trade ideas from portfolio/watchlist context.")
    parser.add_argument("--send-telegram", action="store_true", help="Send the summary to Telegram.")
    parser.add_argument("--telegram-chat-id", help="Override Telegram chat ID/channel ID.")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="Report date.")
    args = parser.parse_args()

    portfolio_text = read_text(PORTFOLIO_PATH)
    holdings = parse_holdings(portfolio_text)
    options = parse_options(read_text(OPTIONS_PATH))
    candidates = parse_watchlist(read_text(WATCHLIST_PATH))
    total_market_value = parse_total_market_value(portfolio_text, holdings)

    report, telegram_message = build_report(args.date, holdings, options, candidates, total_market_value)

    OUTPUTS_DIR.mkdir(exist_ok=True)
    output_path = OUTPUTS_DIR / f"trade-idea-generator-{args.date}.md"
    output_path.write_text(report, encoding="utf-8")
    print(f"Wrote {output_path.relative_to(WORKSPACE)}")

    if args.send_telegram:
        count = send_telegram(telegram_message, args.telegram_chat_id)
        print(f"Sent {count} Telegram message(s).")

    return 0


if __name__ == "__main__":
    sys.exit(main())
