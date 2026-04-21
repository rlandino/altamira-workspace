#!/usr/bin/env python3
"""Generate and send a daily market recap to Telegram.

Creates:
  - outputs/daily-market-recap-YYYY-MM-DD.md

Sends:
  1) Short text summary via Telegram sendMessage
  2) Markdown file via Telegram sendDocument

Required env:
  TELEGRAM_BOT_TOKEN

Optional env:
  TELEGRAM_CHAT_ID (defaults to 7830722515 for this workspace setup)
  FMP_API_KEY (defaults to workspace key used by other commands)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = WORKSPACE / "outputs"

FMP_V3 = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"

DEFAULT_FMP_KEY = "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz"
DEFAULT_TELEGRAM_CHAT_ID = "7830722515"


def _fmt_pct(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"


def _fmt_num(value: Optional[float], decimals: int = 2) -> str:
    if value is None:
        return "N/A"
    return f"{value:,.{decimals}f}"


def _request_json(url: str, params: Dict[str, Any], timeout: int = 20) -> Any:
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def _safe_request_json(
    label: str, url: str, params: Dict[str, Any], default: Any, timeout: int = 20
) -> Any:
    try:
        return _request_json(url=url, params=params, timeout=timeout)
    except Exception as exc:
        print(
            f"[daily-market-recap] Warning: failed to fetch {label}: {exc}",
            file=sys.stderr,
        )
        return default


def _get_symbol_map(items: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for item in items:
        symbol = item.get("symbol")
        if symbol:
            out[symbol] = item
    return out


def fetch_market_data(report_date: dt.date, fmp_key: str) -> Dict[str, Any]:
    date_to = report_date + dt.timedelta(days=7)
    date_from_lookback = report_date - dt.timedelta(days=30)

    quotes = _safe_request_json(
        "quotes",
        f"{FMP_V3}/quote/^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ",
        {"apikey": fmp_key},
        default=[],
    )

    gainers = _safe_request_json(
        "biggest-gainers",
        f"{FMP_STABLE}/biggest-gainers",
        {"apikey": fmp_key},
        default=[],
    )
    losers = _safe_request_json(
        "biggest-losers",
        f"{FMP_STABLE}/biggest-losers",
        {"apikey": fmp_key},
        default=[],
    )

    sectors = _safe_request_json(
        "sector-performance-snapshot",
        f"{FMP_STABLE}/sector-performance-snapshot",
        {"date": report_date.isoformat(), "apikey": fmp_key},
        default=[],
    )

    earnings = _safe_request_json(
        "earning_calendar",
        f"{FMP_V3}/earning_calendar",
        {"from": report_date.isoformat(), "to": date_to.isoformat(), "apikey": fmp_key},
        default=[],
    )

    eod_spx = _safe_request_json(
        "historical-price-eod/light",
        f"{FMP_STABLE}/historical-price-eod/light",
        {
            "symbol": "^GSPC",
            "from": date_from_lookback.isoformat(),
            "to": report_date.isoformat(),
            "apikey": fmp_key,
        },
        default=[],
    )
    if isinstance(eod_spx, dict) and isinstance(eod_spx.get("historical"), list):
        eod_spx = eod_spx["historical"]

    return {
        "quotes": quotes if isinstance(quotes, list) else [],
        "gainers": gainers if isinstance(gainers, list) else [],
        "losers": losers if isinstance(losers, list) else [],
        "sectors": sectors,
        "earnings": earnings if isinstance(earnings, list) else [],
        "spx_eod": eod_spx if isinstance(eod_spx, list) else [],
    }


def parse_sectors(sectors_raw: Any) -> Tuple[Optional[Tuple[str, float]], Optional[Tuple[str, float]]]:
    entries: List[Tuple[str, float]] = []

    if isinstance(sectors_raw, list):
        for item in sectors_raw:
            if not isinstance(item, dict):
                continue
            name = item.get("sector") or item.get("name") or item.get("sectorName")
            perf = (
                item.get("changesPercentage")
                or item.get("changePercentage")
                or item.get("performance")
                or item.get("change")
            )
            if name and isinstance(perf, (int, float)):
                entries.append((str(name), float(perf)))
    elif isinstance(sectors_raw, dict):
        for key, val in sectors_raw.items():
            if isinstance(val, (int, float)):
                entries.append((str(key), float(val)))
            elif isinstance(val, dict):
                name = val.get("sector") or val.get("name") or key
                perf = (
                    val.get("changesPercentage")
                    or val.get("changePercentage")
                    or val.get("performance")
                    or val.get("change")
                )
                if isinstance(perf, (int, float)):
                    entries.append((str(name), float(perf)))

    if not entries:
        return None, None

    entries_sorted = sorted(entries, key=lambda x: x[1], reverse=True)
    return entries_sorted[0], entries_sorted[-1]


def rolling_avg(values: List[float], window: int) -> Optional[float]:
    if len(values) < window:
        return None
    return sum(values[-window:]) / window


def build_report(report_date: dt.date, data: Dict[str, Any]) -> Tuple[str, str]:
    quotes_map = _get_symbol_map(data["quotes"])
    spx = quotes_map.get("^GSPC", {})
    dji = quotes_map.get("^DJI", {})
    ixic = quotes_map.get("^IXIC", {})
    vix = quotes_map.get("^VIX", {})
    spy = quotes_map.get("SPY", {})
    qqq = quotes_map.get("QQQ", {})

    top_gainer = data["gainers"][0] if data["gainers"] else {}
    top_loser = data["losers"][0] if data["losers"] else {}

    best_sector, worst_sector = parse_sectors(data["sectors"])

    closes = []
    for row in data["spx_eod"]:
        close = row.get("close")
        if isinstance(close, (int, float)):
            closes.append(float(close))
    sma5 = rolling_avg(closes, 5)
    sma20 = rolling_avg(closes, 20)

    spx_price = spx.get("price")
    spx_vs_5 = "N/A"
    spx_vs_20 = "N/A"
    if isinstance(spx_price, (int, float)) and isinstance(sma5, (int, float)):
        spx_vs_5 = "Above 5D" if spx_price > sma5 else "Below 5D"
    if isinstance(spx_price, (int, float)) and isinstance(sma20, (int, float)):
        spx_vs_20 = "Above 20D" if spx_price > sma20 else "Below 20D"

    resistance = max(closes[-20:]) if len(closes) >= 20 else (max(closes) if closes else None)
    support = min(closes[-20:]) if len(closes) >= 20 else (min(closes) if closes else None)

    trend = "Mixed"
    if spx_vs_5.startswith("Above") and spx_vs_20.startswith("Above"):
        trend = "Bullish"
    elif spx_vs_5.startswith("Below") and spx_vs_20.startswith("Below"):
        trend = "Bearish"

    vix_level = vix.get("price")
    if isinstance(vix_level, (int, float)):
        if vix_level > 20:
            vix_label = "elevated"
        elif vix_level < 15:
            vix_label = "low"
        else:
            vix_label = "normal"
    else:
        vix_label = "unknown"

    earnings_rows = []
    for e in data["earnings"][:15]:
        earnings_rows.append(
            (
                str(e.get("date", "N/A")),
                str(e.get("symbol", "N/A")),
                "—" if e.get("epsEstimated") is None else str(e.get("epsEstimated")),
            )
        )
    if not earnings_rows:
        earnings_rows.append(("N/A", "No earnings in next 7 days", "—"))

    summary = (
        f"Daily Market Recap ({report_date.isoformat()}): "
        f"S&P 500 {_fmt_pct(spx.get('changesPercentage'))} at {_fmt_num(spx_price)}, "
        f"Nasdaq {_fmt_pct(ixic.get('changesPercentage'))}, Dow {_fmt_pct(dji.get('changesPercentage'))}. "
        f"Trend: {trend}. VIX {_fmt_num(vix_level)} ({vix_label}). "
    )
    if best_sector:
        summary += f"Best sector: {best_sector[0]} ({_fmt_pct(best_sector[1])})."
    else:
        summary += "Sector snapshot unavailable."

    report_lines = [
        f"# Daily Market Recap — {report_date.isoformat()}",
        "",
        "## Market indices",
        "",
        "| Index | Level | Change % |",
        "|---|---:|---:|",
        f"| S&P 500 (^GSPC) | {_fmt_num(spx_price)} | {_fmt_pct(spx.get('changesPercentage'))} |",
        f"| Nasdaq (^IXIC) | {_fmt_num(ixic.get('price'))} | {_fmt_pct(ixic.get('changesPercentage'))} |",
        f"| Dow (^DJI) | {_fmt_num(dji.get('price'))} | {_fmt_pct(dji.get('changesPercentage'))} |",
        "",
        "## ETF and volatility check",
        "",
        f"- SPY: {_fmt_num(spy.get('price'))} ({_fmt_pct(spy.get('changesPercentage'))})",
        f"- QQQ: {_fmt_num(qqq.get('price'))} ({_fmt_pct(qqq.get('changesPercentage'))})",
        f"- VIX: {_fmt_num(vix_level)} ({_fmt_pct(vix.get('changesPercentage'))}) — {vix_label}",
        "",
        "## Leaders and laggards",
        "",
        f"- Hot stock: {top_gainer.get('symbol', 'N/A')} ({_fmt_pct(top_gainer.get('changesPercentage'))})",
        f"- Biggest loser: {top_loser.get('symbol', 'N/A')} ({_fmt_pct(top_loser.get('changesPercentage'))})",
    ]

    if best_sector and worst_sector:
        report_lines.extend(
            [
                "",
                "## Sector snapshot",
                "",
                f"- Best sector: {best_sector[0]} ({_fmt_pct(best_sector[1])})",
                f"- Worst sector: {worst_sector[0]} ({_fmt_pct(worst_sector[1])})",
            ]
        )
    else:
        report_lines.extend(
            [
                "",
                "## Sector snapshot",
                "",
                "- Sector performance snapshot unavailable for this session.",
            ]
        )

    report_lines.extend(
        [
            "",
            "## Index levels vs averages",
            "",
            f"- S&P 500: {_fmt_num(spx_price)}",
            f"- 5D SMA: {_fmt_num(sma5)} ({spx_vs_5})",
            f"- 20D SMA: {_fmt_num(sma20)} ({spx_vs_20})",
            f"- Trend: **{trend}**",
            "",
            "## Support / resistance (20-day range)",
            "",
            f"- Resistance: {_fmt_num(resistance)}",
            f"- Support: {_fmt_num(support)}",
            "",
            "## Earnings calendar (next 7 days)",
            "",
            "| Date | Symbol | EPS estimate |",
            "|---|---|---:|",
        ]
    )
    for d, s, e in earnings_rows:
        report_lines.append(f"| {d} | {s} | {e} |")

    report_lines.extend(
        [
            "",
            "## Commentary",
            "",
            (
                f"US indices closed {'higher' if (spx.get('changesPercentage') or 0) >= 0 else 'lower'} on the session, "
                f"with the S&P 500 at {_fmt_num(spx_price)} and VIX at {_fmt_num(vix_level)} ({vix_label}). "
                f"Short-term trend reads {trend} based on 5D/20D positioning."
            ),
        ]
    )
    if best_sector and worst_sector:
        report_lines.append(
            f"Sector leadership was led by {best_sector[0]} while {worst_sector[0]} lagged."
        )
    else:
        report_lines.append("Sector leadership data was unavailable in the latest snapshot.")

    return summary, "\n".join(report_lines) + "\n"


def send_telegram_message(bot_token: str, chat_id: str, text: str) -> Dict[str, Any]:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": "true",
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def send_telegram_document(
    bot_token: str, chat_id: str, file_path: Path, caption: str
) -> Dict[str, Any]:
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    with file_path.open("rb") as file_obj:
        response = requests.post(
            url,
            data={"chat_id": chat_id, "caption": caption},
            files={"document": (file_path.name, file_obj, "text/markdown")},
            timeout=60,
        )
    response.raise_for_status()
    return response.json()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate and send daily market recap")
    parser.add_argument("--date", help="Date in YYYY-MM-DD (default: today UTC)")
    parser.add_argument(
        "--chat-id",
        help="Telegram chat ID override (default: env TELEGRAM_CHAT_ID or workspace default)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Generate file and print summary without Telegram send"
    )
    args = parser.parse_args()

    if args.date:
        report_date = dt.date.fromisoformat(args.date)
    else:
        report_date = dt.datetime.utcnow().date()

    fmp_key = os.environ.get("FMP_API_KEY", DEFAULT_FMP_KEY)
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = args.chat_id or os.environ.get("TELEGRAM_CHAT_ID", DEFAULT_TELEGRAM_CHAT_ID)

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    data = fetch_market_data(report_date=report_date, fmp_key=fmp_key)
    summary, report_md = build_report(report_date, data)

    report_path = OUTPUTS_DIR / f"daily-market-recap-{report_date.isoformat()}.md"
    report_path.write_text(report_md, encoding="utf-8")

    print(summary)
    print(f"Report written: {report_path}")

    if args.dry_run:
        print("Dry run: skipping Telegram delivery.")
        return 0

    if not bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required to send recap to Telegram.")
    if not chat_id:
        raise RuntimeError("Telegram chat ID is missing.")

    message_res = send_telegram_message(bot_token=bot_token, chat_id=chat_id, text=summary)
    doc_res = send_telegram_document(
        bot_token=bot_token,
        chat_id=chat_id,
        file_path=report_path,
        caption=f"Daily Market Recap Markdown - {report_date.isoformat()}",
    )

    print(
        json.dumps(
            {
                "telegram_message_ok": bool(message_res.get("ok")),
                "telegram_document_ok": bool(doc_res.get("ok")),
                "chat_id": chat_id,
                "message_id": message_res.get("result", {}).get("message_id"),
                "document_message_id": doc_res.get("result", {}).get("message_id"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
