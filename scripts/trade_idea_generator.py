#!/usr/bin/env python3
"""Generate a portfolio-aware trade idea and optionally send it to Telegram."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_PATH = ROOT / "context" / "portfolio-details.md"
WATCHLIST_PATH = ROOT / "context" / "watchlist.md"
OPTIONS_PATH = ROOT / "context" / "options-positions.md"
OUTPUT_DIR = ROOT / "outputs"


@dataclass(frozen=True)
class Holding:
    symbol: str
    quantity: float
    average_price: float
    current_price: float
    market_value: float
    cost_basis: float
    pnl_dollars: float
    pnl_percent: float
    day_change_percent: float
    weight: float


@dataclass(frozen=True)
class WatchlistItem:
    ticker: str
    score: float | None
    grade: str | None
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

    @property
    def collateral(self) -> float:
        if self.option_type.lower() == "put":
            return self.strike * self.contracts * 100
        return 0.0

    @property
    def open_pnl(self) -> float:
        return (self.credit - self.current) * self.contracts * 100


def clean_money(value: str) -> float:
    value = value.strip().replace("$", "").replace(",", "")
    if not value or value in {"-", "—"}:
        return 0.0
    return float(value)


def clean_percent(value: str) -> float:
    value = value.strip().replace("%", "")
    if not value or value in {"-", "—"}:
        return 0.0
    return float(value)


def split_row(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def parse_first_number(text: str) -> float:
    match = re.search(r"[-+]?\$?([\d,]+(?:\.\d+)?)", text)
    if not match:
        return 0.0
    return clean_money(match.group(1))


def parse_holdings(path: Path) -> list[Holding]:
    holdings: list[Holding] = []
    in_table = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("| SYMBOL |"):
            in_table = True
            continue
        if in_table and line.startswith("|--------"):
            continue
        if in_table and (not line.startswith("|") or line.startswith("| Ticker |")):
            break
        if not in_table or not line.startswith("|"):
            continue

        cells = split_row(line)
        if len(cells) < 9:
            continue

        pnl_match = re.search(r"([-+]?\$?[\d,]+)\s+\(([-+]?\d+(?:\.\d+)?)%\)", cells[6])
        day_match = re.search(r"([-+]?\$?[\d,]+)\s+\(([-+]?\d+(?:\.\d+)?)%\)", cells[7])
        holdings.append(
            Holding(
                symbol=cells[0],
                quantity=clean_money(cells[1]),
                average_price=clean_money(cells[2]),
                current_price=clean_money(cells[3]),
                market_value=clean_money(cells[4]),
                cost_basis=clean_money(cells[5]),
                pnl_dollars=clean_money(pnl_match.group(1)) if pnl_match else 0.0,
                pnl_percent=float(pnl_match.group(2)) if pnl_match else 0.0,
                day_change_percent=float(day_match.group(2)) if day_match else 0.0,
                weight=clean_percent(cells[8]),
            )
        )
    return holdings


def parse_portfolio_value(path: Path, holdings: Iterable[Holding]) -> float:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"\*\*Total MKT VALUE\*\*\s*\|\s*\$?([\d,]+)", text)
    if match:
        return clean_money(match.group(1))
    return sum(holding.market_value for holding in holdings)


def parse_watchlist(path: Path) -> list[WatchlistItem]:
    items: list[WatchlistItem] = []
    in_table = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("| Ticker |"):
            in_table = True
            continue
        if in_table and line.startswith("|--------"):
            continue
        if in_table and (not line.startswith("|") or line.startswith("|---")):
            break
        if not in_table or not line.startswith("|"):
            continue

        cells = split_row(line)
        if len(cells) < 5:
            continue
        score = None if cells[1] in {"—", "-"} else float(cells[1])
        grade = cells[2].replace("*", "") if cells[2] not in {"—", "-"} else None
        status = cells[4].replace("⭐", "").strip()
        items.append(
            WatchlistItem(
                ticker=cells[0],
                score=score,
                grade=grade,
                company=cells[3],
                status=status,
            )
        )
    return items


def parse_options(path: Path) -> list[OptionPosition]:
    positions: list[OptionPosition] = []
    in_table = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("| Ticker |"):
            in_table = True
            continue
        if in_table and line.startswith("|--------"):
            continue
        if in_table and not line.startswith("|"):
            break
        if not in_table or not line.startswith("|"):
            continue

        cells = split_row(line)
        if len(cells) < 7:
            continue
        positions.append(
            OptionPosition(
                ticker=cells[0],
                strike=clean_money(cells[1]),
                option_type=cells[2],
                expiration=cells[3],
                credit=clean_money(cells[4]),
                current=clean_money(cells[5]),
                contracts=int(clean_money(cells[6])),
            )
        )
    return positions


def covered_call_candidate(holdings: list[Holding]) -> Holding:
    candidates = [
        holding
        for holding in holdings
        if holding.quantity >= 100 and holding.symbol not in {"SPY", "QQQ", "FFOLX"}
    ]
    if not candidates:
        return max(holdings, key=lambda item: item.weight)
    return max(candidates, key=lambda item: (item.weight, item.pnl_percent))


def top_watchlist_candidates(items: list[WatchlistItem], held_symbols: set[str]) -> list[WatchlistItem]:
    filtered = [
        item
        for item in items
        if item.ticker not in held_symbols
        and item.score is not None
        and item.status.lower() in {"top candidate", "consider"}
    ]
    return sorted(filtered, key=lambda item: item.score or 0.0, reverse=True)[:5]


def format_currency(value: float) -> str:
    return f"${value:,.0f}"


def format_report(
    holdings: list[Holding],
    watchlist: list[WatchlistItem],
    options: list[OptionPosition],
    portfolio_value: float,
) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    held_symbols = {holding.symbol for holding in holdings}
    primary = covered_call_candidate(holdings)
    watch_candidates = top_watchlist_candidates(watchlist, held_symbols)
    overweight = [holding for holding in holdings if holding.weight >= 10.0]
    option_collateral = sum(position.collateral for position in options)
    option_pnl = sum(position.open_pnl for position in options)
    stressed_options = [position for position in options if position.current > position.credit * 1.5]
    suggested_call_strike = round(primary.current_price * 1.12 / 5) * 5
    lots_to_cover = max(1, min(int(primary.quantity // 100), 2))

    lines = [
        "# Trade Idea Generator",
        "",
        f"Generated: {generated_at}",
        f"Portfolio value: {format_currency(portfolio_value)}",
        f"Source files: `{PORTFOLIO_PATH.relative_to(ROOT)}`, `{WATCHLIST_PATH.relative_to(ROOT)}`, `{OPTIONS_PATH.relative_to(ROOT)}`",
        "",
        "## Telegram Summary",
        "",
        "ALTAMIRA TRADE IDEA",
        f"Generated: {generated_at}",
        "",
        "Primary idea: Covered-call overlay on an overweight winner.",
        f"- Candidate: {primary.symbol} ({primary.quantity:.0f} shares, {primary.weight:.1f}% weight, "
        f"{primary.pnl_percent:+.1f}% unrealized P/L).",
        f"- Action: consider selling {lots_to_cover} covered call contract(s), 30-45 DTE, "
        f"0.20-0.25 delta, around ${suggested_call_strike:.0f}+ if the chain pays enough premium.",
        "- Rationale: harvest income and trim concentration risk without adding new cash-secured put exposure.",
        "- Entry filter: only sell if bid/ask is tight, earnings are outside the expiration window, "
        "and premium is worth capping part of the position.",
        "",
        "Secondary watchlist queue:",
    ]

    if watch_candidates:
        for item in watch_candidates:
            lines.append(
                f"- {item.ticker} ({item.grade}, score {item.score:.1f}) - {item.company}; "
                "wait for a pullback or use defined-risk put spreads."
            )
    else:
        lines.append("- No unowned top-candidate watchlist names with scores were found.")

    lines.extend(
        [
            "",
            "Risk read-through:",
            f"- Gross short-put collateral/notional: {format_currency(option_collateral)} "
            f"({option_collateral / portfolio_value * 100:.1f}% of portfolio).",
            f"- Open short-premium mark-to-market P/L: {format_currency(option_pnl)}.",
        ]
    )

    if overweight:
        lines.append(
            "- Overweight positions above 10%: "
            + ", ".join(f"{holding.symbol} {holding.weight:.1f}%" for holding in overweight)
            + "."
        )
    if stressed_options:
        lines.append(
            "- Manage before adding risk: "
            + ", ".join(
                f"{position.ticker} {position.strike:.0f}P {position.expiration} "
                f"(credit ${position.credit:.2f}, current ${position.current:.2f})"
                for position in stressed_options
            )
            + "."
        )

    lines.extend(
        [
            "",
            "Action today:",
            "1. Do not add naked put notional until existing short-put exposure is reduced or rolled.",
            f"2. Check {primary.symbol} option chain for the covered-call overlay above.",
            "3. If initiating a watchlist name, prefer a small defined-risk spread and keep sector exposure in check.",
            "",
            "Disclosure: This is a rules-based idea from repository context, not financial advice. "
            "Confirm live prices, option liquidity, earnings dates, and portfolio limits before trading.",
            "",
            "## Details",
            "",
            "### Current overweight positions",
            "",
            "| Symbol | Weight | Shares | Current | Unrealized P/L |",
            "|---|---:|---:|---:|---:|",
        ]
    )

    for holding in sorted(overweight, key=lambda item: item.weight, reverse=True):
        lines.append(
            f"| {holding.symbol} | {holding.weight:.1f}% | {holding.quantity:.0f} | "
            f"${holding.current_price:.2f} | {holding.pnl_percent:+.1f}% |"
        )

    lines.extend(
        [
            "",
            "### Short-premium positions",
            "",
            "| Ticker | Position | Expiration | Credit | Current | Collateral | Open P/L |",
            "|---|---:|---|---:|---:|---:|---:|",
        ]
    )
    for position in options:
        lines.append(
            f"| {position.ticker} | {position.strike:.0f}{position.option_type[0].upper()} x{position.contracts} | "
            f"{position.expiration} | ${position.credit:.2f} | ${position.current:.2f} | "
            f"{format_currency(position.collateral)} | {format_currency(position.open_pnl)} |"
        )

    return "\n".join(lines) + "\n"


def extract_telegram_summary(report: str) -> str:
    marker = "## Telegram Summary"
    details = "## Details"
    if marker not in report:
        return report
    body = report.split(marker, 1)[1]
    if details in body:
        body = body.split(details, 1)[0]
    return body.strip()


def send_telegram_message(token: str, chat_id: str, text: str) -> dict:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    request = urllib.request.Request(url, data=payload, method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--portfolio", type=Path, default=PORTFOLIO_PATH)
    parser.add_argument("--watchlist", type=Path, default=WATCHLIST_PATH)
    parser.add_argument("--options", type=Path, default=OPTIONS_PATH)
    parser.add_argument("--out", type=Path, default=None, help="Output markdown path.")
    parser.add_argument("--send-telegram", action="store_true", help="Send the summary to Telegram.")
    parser.add_argument("--chat-id", default=os.environ.get("TELEGRAM_CHAT_ID"))
    parser.add_argument("--token-env", default="TELEGRAM_BOT_TOKEN")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    holdings = parse_holdings(args.portfolio)
    if not holdings:
        raise SystemExit(f"No holdings parsed from {args.portfolio}")

    watchlist = parse_watchlist(args.watchlist)
    options = parse_options(args.options)
    portfolio_value = parse_portfolio_value(args.portfolio, holdings)
    report = format_report(holdings, watchlist, options, portfolio_value)

    output_path = args.out
    if output_path is None:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        output_path = OUTPUT_DIR / f"trade-idea-generator-{date_str}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"Wrote {output_path}")

    if args.send_telegram:
        token = os.environ.get(args.token_env)
        if not token:
            raise SystemExit(f"{args.token_env} is not set")
        if not args.chat_id:
            raise SystemExit("Telegram chat ID is not set. Use --chat-id or TELEGRAM_CHAT_ID.")
        result = send_telegram_message(token, args.chat_id, extract_telegram_summary(report))
        message_id = result.get("result", {}).get("message_id")
        print(f"Telegram send ok: message_id={message_id}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
