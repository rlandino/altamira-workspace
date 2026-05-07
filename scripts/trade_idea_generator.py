#!/usr/bin/env python3
"""Generate portfolio/watchlist trade ideas and optionally send Telegram output.

The script intentionally works from repository context first. Live market data
is additive when API keys are available, but stale or missing APIs should not
block a daily operations note.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTEXT_DIR = ROOT / "context"
OUTPUT_DIR = ROOT / "outputs"

PORTFOLIO_PATH = CONTEXT_DIR / "portfolio-details.md"
WATCHLIST_PATH = CONTEXT_DIR / "watchlist.md"
OPTIONS_PATH = CONTEXT_DIR / "options-positions.md"
CSP_FIXED_WORKFLOW_PATH = OUTPUT_DIR / "csp-daily-scan-fixed.json"

FMP_BASE = "https://financialmodelingprep.com/api/v3"
TELEGRAM_BASE = "https://api.telegram.org"


@dataclass
class Position:
    ticker: str
    quantity: float
    average_price: float
    current_price: float
    market_value: float
    cost_basis: float
    weight: float


@dataclass
class WatchlistCandidate:
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
    expiration: dt.date | None
    credit: float
    current: float
    contracts: int


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def clean_number(value: str) -> float:
    cleaned = (
        value.replace("$", "")
        .replace(",", "")
        .replace("%", "")
        .replace("+", "")
        .replace("**", "")
        .strip()
    )
    if cleaned in {"", "-", "--", "\u2014"}:
        return 0.0
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    return float(match.group(0)) if match else 0.0


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_separator_row(cells: list[str]) -> bool:
    return all(set(cell.replace(" ", "")) <= {"-", ":"} for cell in cells)


def parse_first_table(path: Path, header_starts_with: str) -> list[dict[str, str]]:
    lines = read_text(path).splitlines()
    header: list[str] | None = None
    rows: list[dict[str, str]] = []

    for idx, line in enumerate(lines):
        if not line.startswith("|"):
            continue
        cells = split_table_row(line)
        if not cells:
            continue
        if header is None:
            if cells[0].lower() != header_starts_with.lower():
                continue
            header = cells
            continue
        if is_separator_row(cells):
            continue
        if len(cells) != len(header):
            break
        rows.append(dict(zip(header, cells, strict=True)))

        next_line = lines[idx + 1] if idx + 1 < len(lines) else ""
        if not next_line.startswith("|"):
            break

    return rows


def parse_positions() -> list[Position]:
    rows = parse_first_table(PORTFOLIO_PATH, "SYMBOL")
    positions: list[Position] = []
    for row in rows:
        positions.append(
            Position(
                ticker=row["SYMBOL"].strip().upper(),
                quantity=clean_number(row["QTY"]),
                average_price=clean_number(row["AVG. PRICE"]),
                current_price=clean_number(row["CURRENT"]),
                market_value=clean_number(row["MKT VALUE"]),
                cost_basis=clean_number(row["COST BASIS"]),
                weight=clean_number(row["WEIGHT"]),
            )
        )
    return positions


def parse_watchlist() -> list[WatchlistCandidate]:
    rows = parse_first_table(WATCHLIST_PATH, "Ticker")
    candidates: list[WatchlistCandidate] = []
    for row in rows:
        raw_score = row.get("Score", "").strip()
        score = None if raw_score in {"", "\u2014", "-", "--"} else clean_number(raw_score)
        candidates.append(
            WatchlistCandidate(
                ticker=row["Ticker"].strip().upper(),
                score=score,
                grade=row["Grade"].replace("**", "").strip(),
                company=row["Company"].strip(),
                status=row["Status"].replace("\u2b50", "").strip(),
            )
        )
    return candidates


def parse_date(value: str) -> dt.date | None:
    try:
        return dt.date.fromisoformat(value.strip())
    except ValueError:
        return None


def parse_options() -> list[OptionPosition]:
    source = OPTIONS_PATH if OPTIONS_PATH.exists() else PORTFOLIO_PATH
    rows = parse_first_table(source, "Ticker")
    options: list[OptionPosition] = []
    for row in rows:
        if not {"Ticker", "Strike", "Type", "Expiration", "Credit", "Current", "Contracts"} <= set(row):
            continue
        options.append(
            OptionPosition(
                ticker=row["Ticker"].strip().upper(),
                strike=clean_number(row["Strike"]),
                option_type=row["Type"].strip(),
                expiration=parse_date(row["Expiration"]),
                credit=clean_number(row["Credit"]),
                current=clean_number(row["Current"]),
                contracts=int(clean_number(row["Contracts"])),
            )
        )
    return options


def extract_snapshot_value(label: str, text: str) -> str | None:
    pattern = re.compile(rf"\|\s*{re.escape(label)}\s*\|\s*([^|]+)\|", re.IGNORECASE)
    match = pattern.search(text)
    return match.group(1).strip() if match else None


def portfolio_snapshot() -> dict[str, str]:
    text = read_text(PORTFOLIO_PATH)
    return {
        "date": extract_snapshot_value("Date", text) or "unknown",
        "cash_pct": extract_snapshot_value("Cash %", text) or "unknown",
        "vix_close": extract_snapshot_value("VIX Close", text) or "unknown",
        "spy_close": extract_snapshot_value("SPY Close", text) or "unknown",
    }


def sort_watchlist(candidates: list[WatchlistCandidate]) -> list[WatchlistCandidate]:
    return sorted(
        candidates,
        key=lambda item: (
            item.score if item.score is not None else -1.0,
            1 if "Top Candidate" in item.status else 0,
        ),
        reverse=True,
    )


def env_first(names: list[str]) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def http_json(url: str, data: dict[str, Any] | None = None, timeout: int = 12) -> Any:
    body = None
    headers = {"User-Agent": "altamira-trade-idea-generator/1.0"}
    if data is not None:
        body = urllib.parse.urlencode(data).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    request = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:  # nosec B310
        return json.loads(response.read().decode("utf-8"))


def fmp_quote(symbols: list[str], api_key: str | None) -> dict[str, dict[str, Any]]:
    if not api_key or not symbols:
        return {}
    encoded_symbols = ",".join(symbols)
    url = f"{FMP_BASE}/quote/{urllib.parse.quote(encoded_symbols)}?apikey={urllib.parse.quote(api_key)}"
    try:
        payload = http_json(url)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, list):
        return {}
    return {str(item.get("symbol", "")).upper(): item for item in payload if isinstance(item, dict)}


def fmp_historical(symbol: str, api_key: str | None, days: int = 80) -> list[dict[str, Any]]:
    if not api_key:
        return []
    end = dt.date.today()
    start = end - dt.timedelta(days=days * 2)
    params = urllib.parse.urlencode(
        {"from": start.isoformat(), "to": end.isoformat(), "apikey": api_key}
    )
    url = f"{FMP_BASE}/historical-price-full/{urllib.parse.quote(symbol)}?{params}"
    try:
        payload = http_json(url)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return []
    historical = payload.get("historical", []) if isinstance(payload, dict) else []
    return historical[:days] if isinstance(historical, list) else []


def moving_average(values: list[float]) -> float | None:
    valid = [value for value in values if value > 0]
    if not valid:
        return None
    return sum(valid) / len(valid)


def detect_market_regime(api_key: str | None, snapshot: dict[str, str]) -> dict[str, str]:
    quotes = fmp_quote(["^VIX", "SPY"], api_key)
    vix_value = clean_number(snapshot.get("vix_close", "0"))
    if "^VIX" in quotes:
        vix_value = float(quotes["^VIX"].get("price") or vix_value)

    if vix_value < 15:
        vix_regime = "LOW"
        sizing = "75% options size; premiums thin"
    elif vix_value < 25:
        vix_regime = "NORMAL"
        sizing = "100% standard options size"
    elif vix_value < 35:
        vix_regime = "ELEVATED"
        sizing = "50% options size; prefer defined-risk spreads"
    else:
        vix_regime = "CRISIS"
        sizing = "25% options size; capital preservation first"

    spy_price = clean_number(snapshot.get("spy_close", "0"))
    if "SPY" in quotes:
        spy_price = float(quotes["SPY"].get("price") or spy_price)

    history = fmp_historical("SPY", api_key, days=60)
    closes = [float(item.get("close") or 0) for item in history]
    sma_50 = moving_average(closes[:50])
    if sma_50 and spy_price:
        trend = "Bull trend" if spy_price > sma_50 else "Defensive trend"
        trend_detail = f"SPY {spy_price:.2f} vs 50D SMA {sma_50:.2f}"
    else:
        trend = "Snapshot-only trend"
        trend_detail = f"SPY snapshot {spy_price:.2f}" if spy_price else "SPY unavailable"

    return {
        "vix": f"{vix_value:.2f}" if vix_value else "unknown",
        "vix_regime": vix_regime,
        "sizing": sizing,
        "trend": trend,
        "trend_detail": trend_detail,
    }


def option_status(option: OptionPosition, today: dt.date) -> tuple[str, str]:
    dte = (option.expiration - today).days if option.expiration else None
    loss_ratio = option.current / option.credit if option.credit else 0.0

    if dte is not None and dte < 0:
        return "STALE/EXPIRED", f"expiration {option.expiration.isoformat()} is past; reconcile broker records"
    if loss_ratio >= 2.0:
        return "STOP CHECK", f"current {option.current:.2f} is {loss_ratio:.1f}x credit"
    if dte is not None and dte <= 10:
        return "ROLL/CLOSE WATCH", f"{dte} DTE; manage before expiration week risk"
    if dte is not None and dte <= 21:
        return "MONITOR", f"{dte} DTE; plan roll/close threshold"
    if loss_ratio >= 1.5:
        return "MONITOR", f"current {option.current:.2f} is {loss_ratio:.1f}x credit"
    if loss_ratio <= 0.5:
        return "TAKE PROFIT CHECK", f"current {option.current:.2f} is <=50% of credit"
    return "HOLD PLAN", "within normal management band"


def sector_bucket(ticker: str) -> str:
    semis = {"AVGO", "AMAT", "NVDA", "TSM", "KLAC", "LRCX", "ASML", "MRVL"}
    mega_tech = {"AAPL", "MSFT", "GOOGL", "AMZN", "META", "ADBE", "CRM", "NOW"}
    financials = {"V", "MA", "JPM", "SPGI", "MSCI", "FICO"}
    defensive = {"COST", "ABBV", "WM", "GD", "KMI", "LLY", "ABT", "TMO"}
    if ticker in semis:
        return "semiconductor"
    if ticker in mega_tech:
        return "mega-cap software/platform"
    if ticker in financials:
        return "financials/payments"
    if ticker in defensive:
        return "defensive/industrial/health"
    if ticker in {"SPY", "QQQ", "FFOLX"}:
        return "index/core"
    return "other"


def top_concentration(positions: list[Position], threshold: float = 5.0) -> list[Position]:
    return sorted([pos for pos in positions if pos.weight > threshold], key=lambda pos: pos.weight, reverse=True)


def covered_call_candidates(positions: list[Position]) -> list[tuple[Position, int]]:
    candidates: list[tuple[Position, int]] = []
    for pos in top_concentration(positions):
        round_lots = int(pos.quantity // 100)
        if round_lots <= 0:
            continue
        contracts = max(1, min(round_lots, max(1, round_lots // 4)))
        candidates.append((pos, contracts))
    return candidates[:5]


def watchlist_ideas(
    watchlist: list[WatchlistCandidate], positions: list[Position]
) -> list[tuple[WatchlistCandidate, str, str]]:
    owned = {position.ticker for position in positions}
    current_sector_weights: dict[str, float] = {}
    for position in positions:
        current_sector_weights[sector_bucket(position.ticker)] = (
            current_sector_weights.get(sector_bucket(position.ticker), 0.0) + position.weight
        )

    ideas: list[tuple[WatchlistCandidate, str, str]] = []
    for candidate in sort_watchlist(watchlist):
        if candidate.score is None or candidate.score < 58:
            continue
        sector = sector_bucket(candidate.ticker)
        if candidate.ticker in owned:
            action = "HOLD/DO NOT ADD"
            reason = "already owned; use position-size guardrails before adding"
        elif sector == "semiconductor" and current_sector_weights.get("semiconductor", 0.0) > 25:
            action = "DEFINED-RISK ONLY"
            reason = "score is strong, but portfolio semiconductor exposure is already above 25%"
        elif sector == "mega-cap software/platform":
            action = "WATCH FOR STARTER ENTRY"
            reason = "diversifies away from current semiconductor concentration while keeping quality bias"
        else:
            action = "WATCHLIST ENTRY"
            reason = "passes B-/C+ quality screen; verify valuation, earnings date, and options liquidity"
        ideas.append((candidate, action, reason))
    return ideas[:6]


def format_money(value: float) -> str:
    return f"${value:,.0f}"


def format_percent_text(value: str) -> str:
    stripped = value.strip()
    if not stripped or stripped == "unknown" or stripped.endswith("%"):
        return stripped
    return f"{stripped}%"


def generate_report(
    positions: list[Position],
    watchlist: list[WatchlistCandidate],
    options: list[OptionPosition],
    market: dict[str, str],
    snapshot: dict[str, str],
    today: dt.date,
) -> tuple[str, str]:
    portfolio_value = sum(position.market_value for position in positions)
    concentration = top_concentration(positions)
    covered_calls = covered_call_candidates(positions)
    watch_ideas = watchlist_ideas(watchlist, positions)
    option_actions = [(option, *option_status(option, today)) for option in options]
    urgent_options = [
        (option, status, detail)
        for option, status, detail in option_actions
        if status in {"STALE/EXPIRED", "STOP CHECK", "ROLL/CLOSE WATCH"}
    ]

    title = f"Altamira Trade Idea Generator - {today.isoformat()}"
    lines = [
        f"# {title}",
        "",
        "> Operational trade ideas only. Verify live prices, options chains, liquidity, earnings dates, and suitability before placing any order. This is not financial advice.",
        "",
        "## Inputs",
        "",
        f"- Portfolio context: `{PORTFOLIO_PATH.relative_to(ROOT)}`",
        f"- Watchlist context: `{WATCHLIST_PATH.relative_to(ROOT)}`",
        f"- Options context: `{OPTIONS_PATH.relative_to(ROOT)}`",
        f"- Portfolio snapshot date in repo: {snapshot['date']}",
        f"- Portfolio market value from positions: {format_money(portfolio_value)}",
        f"- Cash percent from snapshot: {format_percent_text(snapshot['cash_pct'])}",
        "",
        "## Market Regime",
        "",
        f"- VIX: {market['vix']} ({market['vix_regime']})",
        f"- Sizing posture: {market['sizing']}",
        f"- Trend: {market['trend']} - {market['trend_detail']}",
        "",
        "## Priority Actions",
        "",
    ]

    if urgent_options:
        lines.append("### 1. Manage open short-premium book first")
        lines.append("")
        for option, status, detail in urgent_options:
            exp = option.expiration.isoformat() if option.expiration else "unknown"
            lines.append(
                f"- **{status}: {option.ticker} {option.strike:g} {option.option_type} {exp}** "
                f"({option.contracts} contracts, credit {option.credit:.2f}, current {option.current:.2f}) - {detail}."
            )
        lines.append("")
    else:
        lines.append("### 1. Open short-premium book")
        lines.append("")
        lines.append("- No urgent option-management flags found in repository context.")
        lines.append("")

    lines.extend(
        [
            "### 2. Harvest income on concentrated equity winners",
            "",
            "Candidate covered-call overlay: sell 30-45 DTE calls around 0.20-0.25 delta on a small slice only; close at 50% profit or roll if thesis changes.",
            "",
        ]
    )
    for position, contracts in covered_calls:
        lines.append(
            f"- **{position.ticker}**: {position.weight:.1f}% weight, {position.quantity:g} shares. "
            f"Consider up to {contracts} covered-call contract(s); avoid capping the entire position."
        )
    if not covered_calls:
        lines.append("- No round-lot concentrated holdings available for covered-call overlay.")
    lines.append("")

    lines.extend(
        [
            "### 3. New capital ideas from watchlist",
            "",
            "Use defined-risk spreads when sector exposure is already high; keep starter equity positions within the 2-5% framework.",
            "",
        ]
    )
    for candidate, action, reason in watch_ideas:
        score = f"{candidate.score:.1f}" if candidate.score is not None else "n/a"
        lines.append(
            f"- **{candidate.ticker} ({candidate.grade}, score {score}) - {action}:** "
            f"{candidate.company}. {reason}."
        )
    if not watch_ideas:
        lines.append("- No watchlist candidate met the score/action threshold.")
    lines.append("")

    lines.extend(
        [
            "### 4. Risk guardrails",
            "",
            f"- Positions over 5% cap: {len(concentration)}. Do not add to these names until concentration is reduced or explicitly waived.",
            "- New short premium should respect max 5% per trade and 30% aggregate options allocation.",
            "- Avoid opening short-dated premium through earnings unless it is an explicit earnings-volatility trade.",
            "- If VIX is elevated/crisis, prefer vertical spreads over naked CSPs.",
            "",
            "## Concentration Snapshot",
            "",
        ]
    )
    for position in concentration[:8]:
        lines.append(
            f"- {position.ticker}: {position.weight:.1f}% ({format_money(position.market_value)}), "
            f"bucket: {sector_bucket(position.ticker)}"
        )
    lines.append("")

    lines.extend(["## Full Options Management Table", ""])
    for option, status, detail in option_actions:
        exp = option.expiration.isoformat() if option.expiration else "unknown"
        lines.append(
            f"- {option.ticker} {option.strike:g} {option.option_type} {exp}: "
            f"{status} - {detail}"
        )
    lines.append("")

    telegram_lines = [
        f"Altamira Trade Ideas - {today.isoformat()}",
        "",
        f"Regime: VIX {market['vix']} ({market['vix_regime']}); {market['trend']}",
        f"Portfolio: {format_money(portfolio_value)} from repo; cash {format_percent_text(snapshot['cash_pct'])}",
        f"Repo snapshot date: {snapshot['date']}",
        "",
        "Priority 1 - Manage options:",
    ]
    if urgent_options:
        for option, status, detail in urgent_options[:4]:
            exp = option.expiration.isoformat() if option.expiration else "unknown"
            telegram_lines.append(f"- {status}: {option.ticker} {option.strike:g}P {exp}; {detail}")
        if len(urgent_options) > 4:
            telegram_lines.append(f"- Plus {len(urgent_options) - 4} more option-management item(s) in the report.")
    else:
        telegram_lines.append("- No urgent flags in repo context.")

    telegram_lines.extend(["", "Priority 2 - Covered-call income:"])
    for position, contracts in covered_calls[:4]:
        telegram_lines.append(
            f"- {position.ticker}: {position.weight:.1f}% weight; consider {contracts} small covered-call overlay"
        )
    if len(covered_calls) > 4:
        telegram_lines.append(f"- Plus {len(covered_calls) - 4} more covered-call candidate(s) in the report.")

    telegram_lines.extend(["", "Priority 3 - Watchlist entries:"])
    for candidate, action, reason in watch_ideas[:4]:
        score = f"{candidate.score:.1f}" if candidate.score is not None else "n/a"
        telegram_lines.append(f"- {candidate.ticker} {candidate.grade}/{score}: {action}; {reason}")

    telegram_lines.extend(
        [
            "",
            f"Report: outputs/trade-idea-generator-{today.isoformat()}.md",
            "Guardrails: verify live chain/earnings/liquidity; 5% max trade, 30% options cap.",
            "Operational note only; not financial advice.",
        ]
    )

    return "\n".join(lines) + "\n", "\n".join(telegram_lines)


def discover_chat_id(bot_token: str | None) -> str | None:
    chat_id = env_first(["TELEGRAM_CHAT_ID", "TELEGRAM_CHANNEL_ID", "TELEGRAM_CHAT", "TELEGRAM_CHANNEL"])
    if chat_id:
        return chat_id

    if CSP_FIXED_WORKFLOW_PATH.exists():
        try:
            workflow = json.loads(read_text(CSP_FIXED_WORKFLOW_PATH))
            for node in workflow.get("nodes", []):
                chat_id_value = node.get("parameters", {}).get("chatId")
                if not chat_id_value:
                    continue
                normalized = str(chat_id_value).replace("=", "").strip()
                if normalized and "TELEGRAM_CHAT_ID" not in normalized:
                    return normalized
        except json.JSONDecodeError:
            pass

    if not bot_token:
        return None

    url = f"{TELEGRAM_BASE}/bot{bot_token}/getUpdates"
    try:
        payload = http_json(url, timeout=10)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None
    if not payload.get("ok"):
        return None
    updates = payload.get("result", [])
    for update in reversed(updates):
        for key in ("channel_post", "message", "edited_message"):
            chat = update.get(key, {}).get("chat", {})
            if chat.get("id"):
                return str(chat["id"])
    return None


def split_telegram_message(message: str, limit: int = 3800) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for line in message.splitlines():
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


def send_telegram(message: str) -> list[int]:
    bot_token = env_first(["TELEGRAM_BOT_TOKEN", "TELEGRAM_TOKEN", "TELEGRAM_API_TOKEN"])
    if not bot_token:
        raise RuntimeError("Telegram bot token is missing. Set TELEGRAM_BOT_TOKEN.")

    chat_id = discover_chat_id(bot_token)
    if not chat_id:
        raise RuntimeError(
            "Telegram chat id is missing. Set TELEGRAM_CHAT_ID or send a message to the bot so getUpdates can discover it."
        )

    message_ids: list[int] = []
    chunks = split_telegram_message(message)
    for index, chunk in enumerate(chunks, start=1):
        suffix = f"\n\nPart {index}/{len(chunks)}" if len(chunks) > 1 else ""
        data = {
            "chat_id": chat_id,
            "text": chunk + suffix,
            "disable_web_page_preview": "true",
        }
        url = f"{TELEGRAM_BASE}/bot{bot_token}/sendMessage"
        payload = http_json(url, data=data, timeout=15)
        if not payload.get("ok"):
            raise RuntimeError(f"Telegram send failed: {payload}")
        message = payload.get("result", {})
        if "message_id" in message:
            message_ids.append(int(message["message_id"]))
    return message_ids


def write_output(report: str, today: dt.date) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"trade-idea-generator-{today.isoformat()}.md"
    output_path.write_text(report, encoding="utf-8")
    return output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate Altamira portfolio/watchlist trade ideas.")
    parser.add_argument("--date", help="Override report date (YYYY-MM-DD). Defaults to today.")
    parser.add_argument("--no-telegram", action="store_true", help="Generate report without sending Telegram.")
    parser.add_argument("--print-message", action="store_true", help="Print Telegram message to stdout.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    today = parse_date(args.date) if args.date else dt.date.today()
    if today is None:
        print("Invalid --date. Use YYYY-MM-DD.", file=sys.stderr)
        return 2

    positions = parse_positions()
    watchlist = parse_watchlist()
    options = parse_options()
    if not positions:
        print(f"No positions found in {PORTFOLIO_PATH}", file=sys.stderr)
        return 1

    snapshot = portfolio_snapshot()
    fmp_api_key = env_first(["FMP_API_KEY"])
    market = detect_market_regime(fmp_api_key, snapshot)
    report, telegram_message = generate_report(positions, watchlist, options, market, snapshot, today)
    output_path = write_output(report, today)

    print(f"Wrote {output_path.relative_to(ROOT)}")
    if args.print_message:
        print("\n--- Telegram Message ---\n")
        print(telegram_message)

    if not args.no_telegram:
        message_ids = send_telegram(telegram_message)
        print(f"Sent Telegram message id(s): {', '.join(map(str, message_ids))}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
