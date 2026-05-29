#!/usr/bin/env python3
"""Generate portfolio/watchlist trade ideas and optionally send to Telegram.

The script intentionally uses only repository context and the Python standard
library so it can run from cron/cloud agents without external package setup.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import textwrap
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORTFOLIO = ROOT / "context" / "portfolio-details.md"
DEFAULT_WATCHLIST = ROOT / "context" / "watchlist.md"
DEFAULT_OPTIONS = ROOT / "context" / "options-positions.md"
DEFAULT_OUTPUT_DIR = ROOT / "outputs"


@dataclass(frozen=True)
class Position:
    symbol: str
    quantity: float
    average_price: float
    current_price: float
    market_value: float
    cost_basis: float
    pnl_dollars: float
    pnl_percent: float
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

    @property
    def capture_percent(self) -> float:
        if self.credit <= 0:
            return 0.0
        return (self.credit - self.current) / self.credit * 100

    @property
    def stop_multiple(self) -> float:
        if self.credit <= 0:
            return 0.0
        return self.current / self.credit


@dataclass(frozen=True)
class WatchlistItem:
    ticker: str
    score: float | None
    grade: str | None
    company: str
    status: str


def money_to_float(value: str) -> float:
    cleaned = value.replace("$", "").replace(",", "").replace("+", "").strip()
    if cleaned in {"", "-", "\u2014"}:
        return 0.0
    return float(cleaned)


def pct_to_float(value: str) -> float:
    cleaned = value.replace("%", "").replace("+", "").strip()
    if cleaned in {"", "-", "\u2014"}:
        return 0.0
    return float(cleaned)


def parse_float(value: str) -> float:
    cleaned = value.replace("$", "").replace(",", "").replace("+", "").strip()
    if cleaned in {"", "-", "\u2014"}:
        return 0.0
    return float(cleaned)


def strip_md(value: str) -> str:
    return re.sub(r"[*_`]", "", value).strip()


def table_rows(markdown: str) -> Iterable[list[str]]:
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line.startswith("|") or not line.endswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells or all(set(cell) <= {"-"} for cell in cells):
            continue
        if any(cell.lower() in {"symbol", "ticker"} for cell in cells):
            continue
        yield cells


def extract_inside_parentheses(value: str, marker: str) -> float:
    match = re.search(rf"\(({marker})?([+-]?[0-9.]+)%\)", value)
    if match:
        return float(match.group(2))
    match = re.search(r"([+-]?[0-9.]+)%", value)
    return float(match.group(1)) if match else 0.0


def parse_positions(path: Path) -> list[Position]:
    markdown = path.read_text(encoding="utf-8")
    positions: list[Position] = []
    for cells in table_rows(markdown):
        if len(cells) != 9:
            continue
        symbol = strip_md(cells[0])
        if symbol in {"Totals:", "Metric", "Field"}:
            continue
        try:
            positions.append(
                Position(
                    symbol=symbol,
                    quantity=parse_float(cells[1]),
                    average_price=money_to_float(cells[2]),
                    current_price=money_to_float(cells[3]),
                    market_value=money_to_float(cells[4]),
                    cost_basis=money_to_float(cells[5]),
                    pnl_dollars=money_to_float(cells[6].split()[0]),
                    pnl_percent=extract_inside_parentheses(cells[6], ""),
                    weight_percent=pct_to_float(cells[8]),
                )
            )
        except ValueError:
            continue
    return positions


def parse_options(path: Path) -> list[OptionPosition]:
    markdown = path.read_text(encoding="utf-8")
    options: list[OptionPosition] = []
    for cells in table_rows(markdown):
        if len(cells) != 7:
            continue
        try:
            options.append(
                OptionPosition(
                    ticker=strip_md(cells[0]),
                    strike=parse_float(cells[1]),
                    option_type=strip_md(cells[2]),
                    expiration=strip_md(cells[3]),
                    credit=parse_float(cells[4]),
                    current=parse_float(cells[5]),
                    contracts=int(parse_float(cells[6])),
                )
            )
        except ValueError:
            continue
    return options


def parse_watchlist(path: Path) -> list[WatchlistItem]:
    markdown = path.read_text(encoding="utf-8")
    items: list[WatchlistItem] = []
    for cells in table_rows(markdown):
        if len(cells) != 5:
            continue
        ticker = strip_md(cells[0])
        if not ticker or ticker.isdigit():
            continue
        score: float | None
        try:
            score = parse_float(cells[1])
        except ValueError:
            score = None
        grade = strip_md(cells[2]) if strip_md(cells[2]) not in {"\u2014", ""} else None
        items.append(
            WatchlistItem(
                ticker=ticker,
                score=score,
                grade=grade,
                company=strip_md(cells[3]),
                status=strip_md(cells[4]),
            )
        )
    return items


def sector_for(symbol: str) -> str:
    sectors = {
        "AAPL": "Technology",
        "MSFT": "Technology",
        "GOOGL": "Communication Services",
        "AMZN": "Consumer Discretionary",
        "AVGO": "Technology",
        "AMAT": "Technology",
        "CRWD": "Technology",
        "NOW": "Technology",
        "SPGI": "Financial Services",
        "V": "Financial Services",
        "JPM": "Financial Services",
        "COST": "Consumer Defensive",
        "ABBV": "Healthcare",
        "GD": "Industrials",
        "KMI": "Energy",
        "WM": "Industrials",
        "SPY": "Index",
        "QQQ": "Index",
        "FFOLX": "Fund",
        "NFLX": "Communication Services",
    }
    return sectors.get(symbol, "Other")


def fmt_money(value: float) -> str:
    return f"${value:,.0f}"


def portfolio_value(positions: list[Position]) -> float:
    return sum(p.market_value for p in positions)


def concentration_flags(positions: list[Position]) -> list[Position]:
    return [p for p in positions if p.weight_percent > 5.0]


def top_watchlist(items: list[WatchlistItem], limit: int = 5) -> list[WatchlistItem]:
    scored = [item for item in items if item.score is not None]
    return sorted(scored, key=lambda item: item.score or 0, reverse=True)[:limit]


def option_actions(options: list[OptionPosition]) -> tuple[list[OptionPosition], list[OptionPosition]]:
    profit_takes = [opt for opt in options if opt.capture_percent >= 50]
    stop_alerts = [opt for opt in options if opt.stop_multiple >= 2]
    return profit_takes, stop_alerts


def build_report(
    positions: list[Position],
    options: list[OptionPosition],
    watchlist: list[WatchlistItem],
    generated_at: datetime,
) -> tuple[str, str]:
    total_value = portfolio_value(positions)
    overweight = concentration_flags(positions)
    top_candidates = top_watchlist(watchlist)
    profit_takes, stop_alerts = option_actions(options)

    sector_weights: dict[str, float] = {}
    for pos in positions:
        sector_weights[sector_for(pos.symbol)] = sector_weights.get(sector_for(pos.symbol), 0) + pos.weight_percent
    sector_summary = sorted(sector_weights.items(), key=lambda item: item[1], reverse=True)

    markdown_lines = [
        f"# Trade Idea Generator - {generated_at:%Y-%m-%d}",
        "",
        "> Source: repository context (`context/portfolio-details.md`, `context/watchlist.md`, `context/options-positions.md`).",
        "> These are research ideas and risk-management prompts, not trade orders or financial advice.",
        "",
        "## Portfolio Snapshot",
        "",
        f"- Estimated market value from positions table: **{fmt_money(total_value)}**",
        f"- Positions parsed: **{len(positions)}**",
        f"- Open short-premium positions parsed: **{len(options)}**",
        f"- Watchlist names parsed: **{len(watchlist)}**",
        "",
        "## Risk Read-Through",
        "",
    ]

    if overweight:
        markdown_lines.append("Positions above the 5% framework cap for new equity exposure:")
        for pos in sorted(overweight, key=lambda p: p.weight_percent, reverse=True):
            markdown_lines.append(
                f"- **{pos.symbol}**: {pos.weight_percent:.1f}% weight, "
                f"{fmt_money(pos.market_value)} market value, P&L {pos.pnl_percent:+.1f}%"
            )
    else:
        markdown_lines.append("- No individual position is above the 5% framework cap.")

    markdown_lines.extend(["", "Sector / sleeve weights from parsed positions:"])
    for sector, weight in sector_summary:
        markdown_lines.append(f"- {sector}: {weight:.1f}%")

    markdown_lines.extend(
        [
            "",
            "## Trade Ideas",
            "",
            "### 1. Manage existing short-premium book first",
        ]
    )

    if profit_takes:
        for opt in profit_takes:
            markdown_lines.append(
                f"- **Close/roll candidate:** {opt.ticker} {opt.strike:g}{opt.option_type[0].upper()} "
                f"{opt.expiration}; credit {opt.credit:.2f}, current {opt.current:.2f}, "
                f"profit capture {opt.capture_percent:.1f}%. This exceeds the 50% profit-taking rule."
            )
    else:
        markdown_lines.append("- No option position has reached the 50% profit-capture threshold.")

    if stop_alerts:
        for opt in stop_alerts:
            markdown_lines.append(
                f"- **Risk alert:** {opt.ticker} {opt.strike:g}{opt.option_type[0].upper()} "
                f"{opt.expiration}; current premium is {opt.stop_multiple:.2f}x initial credit. "
                "Review against the 200% stop rule before adding risk."
            )
    else:
        markdown_lines.append("- No option position is above the 200% premium stop threshold.")

    markdown_lines.extend(
        [
            "",
            "### 2. Rebalance before adding correlated semiconductor exposure",
            "",
            "- Existing top weights are concentrated in SPY, AVGO, GOOGL, and AMAT; technology-linked exposure is already well above the normal framework guardrails.",
            "- If initiating a watchlist semiconductor name, pair it with a defined trim or replacement of existing semi/AI exposure rather than layering on another correlated position.",
            "",
            "### 3. Watchlist candidates for staged research entries",
            "",
        ]
    )

    for item in top_candidates:
        note = "top score, but overlaps with existing semi/AI exposure"
        if item.ticker == "ADBE":
            note = "software exposure with less direct overlap than semicap names"
        markdown_lines.append(
            f"- **{item.ticker}** ({item.grade}, score {item.score:.1f}) - {item.company}; {item.status}. {note}."
        )

    markdown_lines.extend(
        [
            "",
            "## Suggested Execution Checklist",
            "",
            "1. Do not add new short puts where an existing position is at or past a stop-review threshold.",
            "2. For any new equity entry, keep sizing within the framework cap and define the source of funds first.",
            "3. Confirm current prices, earnings dates, IV rank, bid/ask width, and available cash in the broker before acting.",
            "4. Use `/paper-trade` to log any selected idea after risk checks pass.",
            "",
            "## Telegram Summary",
            "",
        ]
    )

    telegram_lines = [
        f"ALTAMIRA TRADE IDEAS - {generated_at:%Y-%m-%d}",
        "",
        f"Portfolio parsed: {fmt_money(total_value)} across {len(positions)} positions.",
        f"Open short-premium positions: {len(options)} | Watchlist names: {len(watchlist)}",
        "",
        "TOP ACTIONS",
    ]

    if profit_takes:
        first = profit_takes[0]
        telegram_lines.append(
            f"1) Profit-take/roll review: {first.ticker} {first.strike:g}{first.option_type[0].upper()} "
            f"{first.expiration} has captured {first.capture_percent:.1f}% of credit."
        )
    else:
        telegram_lines.append("1) No short-premium leg has hit the 50% profit-taking rule.")

    if stop_alerts:
        first = stop_alerts[0]
        telegram_lines.append(
            f"2) Stop-review alert: {first.ticker} {first.strike:g}{first.option_type[0].upper()} "
            f"{first.expiration} is {first.stop_multiple:.2f}x initial credit."
        )
    else:
        telegram_lines.append("2) No short-premium leg is beyond the 200% premium stop line.")

    if overweight:
        top_overweight = ", ".join(f"{p.symbol} {p.weight_percent:.1f}%" for p in overweight[:5])
        telegram_lines.append(f"3) Concentration check: above 5% in {top_overweight}.")
    else:
        telegram_lines.append("3) Concentration check: no single name above 5%.")

    telegram_lines.extend(
        [
            "",
            "WATCHLIST READ",
            "Top scored names: "
            + ", ".join(f"{item.ticker} {item.grade}/{item.score:.1f}" for item in top_candidates),
            "Semicap names are high-ranked, but current portfolio already has large AVGO/AMAT exposure; prefer replacement/trim funding.",
            "",
            "IDEA BIAS",
            "Manage existing options risk first, preserve cash, and only add watchlist exposure after confirming live prices, earnings dates, liquidity, and risk limits.",
            "",
            "Not financial advice. Research prompt only.",
        ]
    )

    telegram_summary = "\n".join(telegram_lines)
    markdown_lines.append("```")
    markdown_lines.append(telegram_summary)
    markdown_lines.append("```")
    markdown_lines.append("")
    markdown_lines.append(f"_Generated at {generated_at.isoformat()}._")

    return "\n".join(markdown_lines), telegram_summary


def send_telegram(bot_token: str, chat_id: str, text: str) -> list[dict[str, object]]:
    chunks = split_message(text)
    responses: list[dict[str, object]] = []
    for chunk in chunks:
        payload = json.dumps(
            {
                "chat_id": chat_id,
                "text": chunk,
                "disable_web_page_preview": True,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                responses.append(json.loads(response.read().decode("utf-8")))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Telegram send failed: HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Telegram send failed: {exc.reason}") from exc
    return responses


def split_message(text: str, limit: int = 3900) -> list[str]:
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for line in text.splitlines():
        line_len = len(line) + 1
        if current and current_len + line_len > limit:
            chunks.append("\n".join(current))
            current = []
            current_len = 0
        current.append(line)
        current_len += line_len
    if current:
        chunks.append("\n".join(current))
    return chunks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate trade ideas from repository portfolio/watchlist context."
    )
    parser.add_argument("--portfolio", type=Path, default=DEFAULT_PORTFOLIO)
    parser.add_argument("--watchlist", type=Path, default=DEFAULT_WATCHLIST)
    parser.add_argument("--options", type=Path, default=DEFAULT_OPTIONS)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--send-telegram", action="store_true")
    parser.add_argument("--chat-id", default=os.environ.get("TELEGRAM_CHAT_ID"))
    parser.add_argument("--bot-token", default=os.environ.get("TELEGRAM_BOT_TOKEN"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    generated_at = datetime.now(timezone.utc)
    output = args.output or DEFAULT_OUTPUT_DIR / f"trade-idea-generator-{generated_at:%Y-%m-%d}.md"

    try:
        positions = parse_positions(args.portfolio)
        options = parse_options(args.options)
        watchlist = parse_watchlist(args.watchlist)
    except FileNotFoundError as exc:
        print(f"Missing input file: {exc.filename}", file=sys.stderr)
        return 1

    if not positions:
        print(f"No positions parsed from {args.portfolio}", file=sys.stderr)
        return 1
    if not watchlist:
        print(f"No watchlist entries parsed from {args.watchlist}", file=sys.stderr)
        return 1

    report, telegram_summary = build_report(positions, options, watchlist, generated_at)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")

    delivery_note = ""
    if args.send_telegram:
        if not args.bot_token:
            print("TELEGRAM_BOT_TOKEN is required for --send-telegram", file=sys.stderr)
            return 1
        if not args.chat_id:
            print("TELEGRAM_CHAT_ID or --chat-id is required for --send-telegram", file=sys.stderr)
            return 1
        responses = send_telegram(args.bot_token, args.chat_id, telegram_summary)
        message_ids = [
            str(resp.get("result", {}).get("message_id", "unknown")) for resp in responses
        ]
        delivery_note = textwrap.dedent(
            f"""

            ## Delivery

            - Telegram send: success
            - Message IDs: {", ".join(message_ids)}
            - Sent at: {datetime.now(timezone.utc).isoformat()}
            """
        )
        with output.open("a", encoding="utf-8") as handle:
            handle.write(delivery_note)

    print(f"Wrote {output}")
    if delivery_note:
        print("Telegram send: success")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
