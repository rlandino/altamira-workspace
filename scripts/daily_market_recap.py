#!/usr/bin/env python3
"""Generate and optionally send the Altamira daily market recap.

The script uses FMP for market data and Telegram Bot API for delivery.
Set FMP_API_KEY and TELEGRAM_BOT_TOKEN in the environment. Set
TELEGRAM_CHAT_ID or TELEGRAM_CHANNEL_ID when available; otherwise the script
will try to resolve the most recent Telegram channel/chat from bot updates.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import subprocess
import sys
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib import error, parse, request

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python 3.8 fallback
    ZoneInfo = None  # type: ignore[assignment]


WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = WORKSPACE / "outputs"
FMP_V3 = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"
TELEGRAM_API = "https://api.telegram.org"


@dataclass
class RecapResult:
    date_str: str
    markdown_path: Path
    summary: str
    telegram_message_sent: bool = False
    telegram_document_sent: bool = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a daily market recap.")
    parser.add_argument(
        "--date",
        dest="date_str",
        help="Recap date in YYYY-MM-DD format. Defaults to current America/New_York date.",
    )
    parser.add_argument(
        "--send-telegram",
        action="store_true",
        help="Send the summary and markdown file to Telegram.",
    )
    parser.add_argument(
        "--telegram-chat-id",
        help="Telegram chat/channel ID. Falls back to TELEGRAM_CHAT_ID or TELEGRAM_CHANNEL_ID.",
    )
    parser.add_argument(
        "--skip-chart",
        action="store_true",
        help="Skip generating the optional index chart.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(OUTPUTS_DIR),
        help="Directory for generated output files.",
    )
    return parser.parse_args()


def current_et_date() -> date:
    if ZoneInfo is None:
        return date.today()
    return datetime.now(ZoneInfo("America/New_York")).date()


def load_api_key() -> str:
    api_key = os.environ.get("FMP_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("FMP_API_KEY is required to generate the recap.")
    return api_key


def http_json(url: str, params: dict[str, Any] | None = None, timeout: int = 20) -> Any:
    query = parse.urlencode(params or {})
    full_url = f"{url}?{query}" if query else url
    req = request.Request(full_url, headers={"User-Agent": "altamira-daily-market-recap/1.0"})
    try:
        with request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} for {url}: {detail[:300]}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Request failed for {url}: {exc}") from exc
    return json.loads(body)


def fmp_v3(path: str, api_key: str, params: dict[str, Any] | None = None) -> Any:
    request_params = dict(params or {})
    request_params["apikey"] = api_key
    return http_json(f"{FMP_V3}{path}", request_params)


def fmp_stable(path: str, api_key: str, params: dict[str, Any] | None = None) -> Any:
    request_params = dict(params or {})
    request_params["apikey"] = api_key
    return http_json(f"{FMP_STABLE}{path}", request_params)


def safe_fetch(label: str, fetcher, fallback: Any) -> Any:
    try:
        return fetcher()
    except Exception as exc:  # noqa: BLE001 - report and keep the recap running
        print(f"[daily-market-recap] {label} unavailable: {exc}", file=sys.stderr)
        return fallback


def as_list(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        return [data]
    return []


def pct(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "n/a"
    sign = "+" if number > 0 else ""
    return f"{sign}{number:.2f}%"


def num(value: Any, digits: int = 2) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "n/a"
    return f"{number:,.{digits}f}"


def money_or_estimate(value: Any) -> str:
    if value in (None, ""):
        return "-"
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return str(value)


def quote_map(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row.get("symbol", "")).upper(): row for row in rows}


def change_percent(row: dict[str, Any]) -> Any:
    for key in ("changesPercentage", "changesPercent", "changePercentage"):
        if key in row:
            return row.get(key)
    return None


def item_symbol(row: dict[str, Any]) -> str:
    return str(row.get("symbol") or row.get("ticker") or "n/a")


def item_name(row: dict[str, Any]) -> str:
    return str(row.get("name") or row.get("companyName") or "").strip()


def sector_name(row: dict[str, Any]) -> str:
    return str(row.get("sector") or row.get("name") or row.get("sectorName") or "n/a")


def sector_change(row: dict[str, Any]) -> Any:
    for key in ("changesPercentage", "changePercentage", "performance", "changesPercent"):
        if key in row:
            raw = row.get(key)
            if isinstance(raw, str):
                raw = raw.replace("%", "")
            return raw
    return None


def latest_sector_snapshot(api_key: str, date_str: str) -> list[dict[str, Any]]:
    target = datetime.strptime(date_str, "%Y-%m-%d").date()
    for offset in range(0, 7):
        check_date = (target - timedelta(days=offset)).isoformat()
        rows = as_list(
            fmp_stable(
                "/sector-performance-snapshot",
                api_key,
                {"date": check_date},
            )
        )
        if rows:
            for row in rows:
                row["_snapshotDate"] = check_date
            return rows
    return []


def historical_closes(api_key: str, date_str: str) -> list[dict[str, Any]]:
    target = datetime.strptime(date_str, "%Y-%m-%d").date()
    from_date = (target - timedelta(days=45)).isoformat()
    rows = as_list(
        fmp_stable(
            "/historical-price-eod/light",
            api_key,
            {"symbol": "^GSPC", "from": from_date, "to": date_str},
        )
    )
    rows.sort(key=lambda row: str(row.get("date", "")))
    return rows


def moving_average(values: list[float], window: int) -> float | None:
    if len(values) < window:
        return None
    return sum(values[-window:]) / window


def trend_label(current: float | None, ma5: float | None, ma20: float | None) -> str:
    if current is None or ma5 is None or ma20 is None:
        return "Mixed"
    if current > ma5 and current > ma20:
        return "Bullish"
    if current < ma5 and current < ma20:
        return "Bearish"
    return "Mixed"


def vix_label(vix_level: float | None) -> str:
    if vix_level is None:
        return "unavailable"
    if vix_level > 20:
        return "elevated"
    if vix_level < 15:
        return "low"
    return "normal"


def first_nonempty(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    return rows[0] if rows else None


def compact_headlines(news_rows: list[dict[str, Any]], limit: int = 5) -> list[str]:
    headlines: list[str] = []
    for row in news_rows[:limit]:
        title = str(row.get("title") or row.get("headline") or "").strip()
        if title:
            headlines.append(title)
    return headlines


def generate_chart(date_str: str) -> Path | None:
    script = WORKSPACE / "scripts" / "briefing_chart.py"
    if not script.exists():
        return None
    try:
        subprocess.run(
            [sys.executable, str(script), "--date", date_str],
            cwd=str(WORKSPACE),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=90,
        )
    except Exception as exc:  # noqa: BLE001 - chart is optional
        print(f"[daily-market-recap] Chart generation skipped: {exc}", file=sys.stderr)
        return None
    chart = OUTPUTS_DIR / f"briefing-chart-{date_str}.png"
    return chart if chart.exists() else None


def build_recap(date_str: str, output_dir: Path, skip_chart: bool) -> RecapResult:
    api_key = load_api_key()
    output_dir.mkdir(parents=True, exist_ok=True)

    quotes = as_list(
        safe_fetch(
            "quotes",
            lambda: fmp_v3("/quote/^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ", api_key),
            [],
        )
    )
    qmap = quote_map(quotes)
    gainers = as_list(safe_fetch("biggest gainers", lambda: fmp_stable("/biggest-gainers", api_key), []))
    losers = as_list(safe_fetch("biggest losers", lambda: fmp_stable("/biggest-losers", api_key), []))
    sectors = as_list(safe_fetch("sector snapshot", lambda: latest_sector_snapshot(api_key, date_str), []))
    earnings = as_list(
        safe_fetch(
            "earnings calendar",
            lambda: fmp_v3(
                "/earning_calendar",
                api_key,
                {
                    "from": date_str,
                    "to": (datetime.strptime(date_str, "%Y-%m-%d").date() + timedelta(days=7)).isoformat(),
                },
            ),
            [],
        )
    )
    history = as_list(safe_fetch("historical prices", lambda: historical_closes(api_key, date_str), []))
    news = as_list(
        safe_fetch(
            "general news",
            lambda: fmp_stable("/news/general-latest", api_key, {"page": 0, "limit": 10}),
            [],
        )
    )

    spx = qmap.get("^GSPC", {})
    nasdaq = qmap.get("^IXIC", {})
    dow = qmap.get("^DJI", {})
    vix = qmap.get("^VIX", {})
    spy = qmap.get("SPY", {})
    qqq = qmap.get("QQQ", {})

    current_spx = float(spx["price"]) if spx.get("price") is not None else None
    closes = [float(row["close"]) for row in history if row.get("close") is not None]
    ma5 = moving_average(closes, 5)
    ma20 = moving_average(closes, 20)
    support = min(closes[-20:]) if len(closes) >= 20 else None
    resistance = max(closes[-20:]) if len(closes) >= 20 else None
    trend = trend_label(current_spx, ma5, ma20)

    vix_level = float(vix["price"]) if vix.get("price") is not None else None
    vix_context = vix_label(vix_level)

    hot_stock = first_nonempty(gainers)
    weak_stock = first_nonempty(losers)

    sector_ranked = [row for row in sectors if sector_change(row) is not None]
    sector_ranked.sort(key=lambda row: float(sector_change(row)))
    worst_sector = sector_ranked[0] if sector_ranked else None
    best_sector = sector_ranked[-1] if sector_ranked else None
    sector_snapshot_date = sectors[0].get("_snapshotDate") if sectors else None

    chart_path = None if skip_chart else generate_chart(date_str)
    headlines = compact_headlines(news)

    summary = build_summary(
        date_str=date_str,
        spx=spx,
        nasdaq=nasdaq,
        dow=dow,
        trend=trend,
        vix_level=vix_level,
        vix_context=vix_context,
        best_sector=best_sector,
        worst_sector=worst_sector,
        hot_stock=hot_stock,
        weak_stock=weak_stock,
    )

    markdown = render_markdown(
        date_str=date_str,
        quotes=(spx, nasdaq, dow, spy, qqq, vix),
        trend=trend,
        vix_context=vix_context,
        ma5=ma5,
        ma20=ma20,
        support=support,
        resistance=resistance,
        best_sector=best_sector,
        worst_sector=worst_sector,
        sector_snapshot_date=sector_snapshot_date,
        hot_stock=hot_stock,
        weak_stock=weak_stock,
        earnings=earnings,
        headlines=headlines,
        chart_path=chart_path,
        summary=summary,
    )

    markdown_path = output_dir / f"daily-market-recap-{date_str}.md"
    markdown_path.write_text(markdown, encoding="utf-8")
    return RecapResult(date_str=date_str, markdown_path=markdown_path, summary=summary)


def build_summary(
    *,
    date_str: str,
    spx: dict[str, Any],
    nasdaq: dict[str, Any],
    dow: dict[str, Any],
    trend: str,
    vix_level: float | None,
    vix_context: str,
    best_sector: dict[str, Any] | None,
    worst_sector: dict[str, Any] | None,
    hot_stock: dict[str, Any] | None,
    weak_stock: dict[str, Any] | None,
) -> str:
    best = (
        f"{sector_name(best_sector)} {pct(sector_change(best_sector))}"
        if best_sector
        else "sector data unavailable"
    )
    worst = (
        f"{sector_name(worst_sector)} {pct(sector_change(worst_sector))}"
        if worst_sector
        else "sector data unavailable"
    )
    hot = (
        f"{item_symbol(hot_stock)} {pct(change_percent(hot_stock))}"
        if hot_stock
        else "gainer data unavailable"
    )
    weak = (
        f"{item_symbol(weak_stock)} {pct(change_percent(weak_stock))}"
        if weak_stock
        else "loser data unavailable"
    )
    return "\n".join(
        [
            f"Altamira Daily Market Recap - {date_str}",
            f"S&P 500 {num(spx.get('price'))} ({pct(change_percent(spx))}); "
            f"Nasdaq {num(nasdaq.get('price'))} ({pct(change_percent(nasdaq))}); "
            f"Dow {num(dow.get('price'))} ({pct(change_percent(dow))}).",
            f"Trend: {trend}. VIX is {vix_context} at {num(vix_level)}.",
            f"Best sector: {best}. Worst sector: {worst}.",
            f"Hot stock: {hot}. Biggest loser: {weak}.",
        ]
    )


def render_quote_row(label: str, symbol: str, row: dict[str, Any]) -> str:
    return f"| {label} | {symbol} | {num(row.get('price'))} | {pct(change_percent(row))} |"


def render_markdown(
    *,
    date_str: str,
    quotes: tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]],
    trend: str,
    vix_context: str,
    ma5: float | None,
    ma20: float | None,
    support: float | None,
    resistance: float | None,
    best_sector: dict[str, Any] | None,
    worst_sector: dict[str, Any] | None,
    sector_snapshot_date: str | None,
    hot_stock: dict[str, Any] | None,
    weak_stock: dict[str, Any] | None,
    earnings: list[dict[str, Any]],
    headlines: list[str],
    chart_path: Path | None,
    summary: str,
) -> str:
    spx, nasdaq, dow, spy, qqq, vix = quotes

    earnings_rows = earnings[:12]
    earnings_table = ["| Date | Symbol | EPS estimate | Revenue estimate |", "|---|---:|---:|---:|"]
    if earnings_rows:
        for row in earnings_rows:
            earnings_table.append(
                "| "
                f"{row.get('date', '-')} | "
                f"{row.get('symbol', '-')} | "
                f"{money_or_estimate(row.get('epsEstimated'))} | "
                f"{money_or_estimate(row.get('revenueEstimated'))} |"
            )
    else:
        earnings_table.append("| - | No earnings data returned for the next 7 days | - | - |")

    headlines_block = "\n".join(f"- {headline}" for headline in headlines) if headlines else "- No market headlines returned."

    best_sector_text = (
        f"{sector_name(best_sector)} ({pct(sector_change(best_sector))})"
        if best_sector
        else "Unavailable"
    )
    worst_sector_text = (
        f"{sector_name(worst_sector)} ({pct(sector_change(worst_sector))})"
        if worst_sector
        else "Unavailable"
    )
    hot_name = item_name(hot_stock) if hot_stock else ""
    weak_name = item_name(weak_stock) if weak_stock else ""
    hot_text = (
        f"{item_symbol(hot_stock)} {f'({hot_name}) ' if hot_name else ''}{pct(change_percent(hot_stock))}"
        if hot_stock
        else "Unavailable"
    )
    weak_text = (
        f"{item_symbol(weak_stock)} {f'({weak_name}) ' if weak_name else ''}{pct(change_percent(weak_stock))}"
        if weak_stock
        else "Unavailable"
    )

    avg_lines = [
        f"- 5-day average: {num(ma5) if ma5 is not None else 'Unavailable'}",
        f"- 20-day average: {num(ma20) if ma20 is not None else 'Unavailable'}",
        f"- 20-day support: {num(support) if support is not None else 'Unavailable'}",
        f"- 20-day resistance: {num(resistance) if resistance is not None else 'Unavailable'}",
        f"- Trend: {trend}",
    ]

    chart_line = (
        f"![Index performance]({chart_path.relative_to(WORKSPACE)})"
        if chart_path
        else "Chart not generated."
    )

    commentary = (
        f"The S&P 500 is {pct(change_percent(spx))} on the session, with Nasdaq at "
        f"{pct(change_percent(nasdaq))} and Dow at {pct(change_percent(dow))}. "
        f"The tape screens {trend.lower()} against short-term moving averages, while VIX is "
        f"{vix_context} at {num(vix.get('price'))}. Sector leadership is led by "
        f"{best_sector_text}, with {worst_sector_text} lagging."
    )

    snapshot_note = f"Sector snapshot date: {sector_snapshot_date}." if sector_snapshot_date else "Sector snapshot unavailable."

    return "\n".join(
        [
            f"# Daily Market Recap - {date_str}",
            "",
            "## Summary",
            "",
            summary,
            "",
            "## Market Indices",
            "",
            "| Index | Symbol | Level | Day Change |",
            "|---|---:|---:|---:|",
            render_quote_row("S&P 500", "^GSPC", spx),
            render_quote_row("Nasdaq Composite", "^IXIC", nasdaq),
            render_quote_row("Dow Jones", "^DJI", dow),
            "",
            "## ETFs and Volatility",
            "",
            "| Instrument | Symbol | Level | Day Change |",
            "|---|---:|---:|---:|",
            render_quote_row("SPDR S&P 500 ETF", "SPY", spy),
            render_quote_row("Invesco QQQ Trust", "QQQ", qqq),
            render_quote_row("CBOE Volatility Index", "^VIX", vix),
            "",
            f"VIX context: {vix_context}.",
            "",
            "## Market Movers",
            "",
            f"- Hot stock: {hot_text}",
            f"- Biggest loser: {weak_text}",
            f"- Best sector: {best_sector_text}",
            f"- Worst sector: {worst_sector_text}",
            f"- {snapshot_note}",
            "",
            "## S&P 500 Technical Snapshot",
            "",
            *avg_lines,
            "",
            "## Earnings Calendar (Next 7 Days)",
            "",
            *earnings_table,
            "",
            "## Market Headlines Checked",
            "",
            headlines_block,
            "",
            "## Commentary",
            "",
            commentary,
            "",
            "## Index Performance Chart",
            "",
            chart_line,
            "",
            "## Disclaimer",
            "",
            "This recap is for informational purposes only and is not investment advice. "
            "Market data may be delayed or revised; verify quotes and risk before trading.",
            "",
        ]
    )


def telegram_request(token: str, method: str, fields: dict[str, Any]) -> dict[str, Any]:
    url = f"{TELEGRAM_API}/bot{token}/{method}"
    encoded = parse.urlencode(fields).encode("utf-8")
    req = request.Request(url, data=encoded, method="POST")
    try:
        with request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram {method} failed: HTTP {exc.code}: {detail[:300]}") from exc


def telegram_multipart_request(token: str, method: str, fields: dict[str, Any], file_field: str, path: Path) -> dict[str, Any]:
    url = f"{TELEGRAM_API}/bot{token}/{method}"
    boundary = f"----altamira-{uuid.uuid4().hex}"
    body = bytearray()

    def add_field(name: str, value: Any) -> None:
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
        body.extend(str(value).encode("utf-8"))
        body.extend(b"\r\n")

    for name, value in fields.items():
        add_field(name, value)

    mime_type = mimetypes.guess_type(path.name)[0] or "text/markdown"
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(
        (
            f'Content-Disposition: form-data; name="{file_field}"; filename="{path.name}"\r\n'
            f"Content-Type: {mime_type}\r\n\r\n"
        ).encode("utf-8")
    )
    body.extend(path.read_bytes())
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    req = request.Request(
        url,
        data=bytes(body),
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        with request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram {method} failed: HTTP {exc.code}: {detail[:300]}") from exc


def resolve_telegram_chat_id(token: str, explicit_chat_id: str | None) -> str:
    for candidate in (
        explicit_chat_id,
        os.environ.get("TELEGRAM_CHAT_ID"),
        os.environ.get("TELEGRAM_CHANNEL_ID"),
    ):
        if candidate and candidate.strip():
            return candidate.strip()

    updates = http_json(f"{TELEGRAM_API}/bot{token}/getUpdates", {"limit": 25, "allowed_updates": json.dumps(["message", "channel_post"])})
    candidates: list[tuple[int, str, str]] = []
    for update in updates.get("result", []):
        update_id = int(update.get("update_id", 0))
        for key in ("channel_post", "message"):
            payload = update.get(key)
            if not isinstance(payload, dict):
                continue
            chat = payload.get("chat")
            if not isinstance(chat, dict):
                continue
            chat_id = chat.get("id")
            chat_type = str(chat.get("type", ""))
            if chat_id is not None:
                priority = 1 if chat_type == "channel" else 0
                candidates.append((priority, update_id, str(chat_id)))
    if not candidates:
        raise RuntimeError(
            "Telegram chat ID not configured and no bot updates were available. "
            "Set TELEGRAM_CHAT_ID or TELEGRAM_CHANNEL_ID."
        )
    candidates.sort()
    return candidates[-1][2]


def send_to_telegram(result: RecapResult, explicit_chat_id: str | None) -> RecapResult:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required for Telegram delivery.")

    chat_id = resolve_telegram_chat_id(token, explicit_chat_id)
    message_response = telegram_request(
        token,
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": f"{result.summary}\n\nMarkdown report attached: {result.markdown_path.name}",
            "disable_web_page_preview": "true",
        },
    )
    if not message_response.get("ok"):
        raise RuntimeError(f"Telegram sendMessage returned an error: {message_response}")
    result.telegram_message_sent = True

    document_response = telegram_multipart_request(
        token,
        "sendDocument",
        {
            "chat_id": chat_id,
            "caption": f"Daily market recap markdown - {result.date_str}",
        },
        "document",
        result.markdown_path,
    )
    if not document_response.get("ok"):
        raise RuntimeError(f"Telegram sendDocument returned an error: {document_response}")
    result.telegram_document_sent = True
    return result


def main() -> int:
    args = parse_args()
    date_str = args.date_str or current_et_date().isoformat()
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print("--date must use YYYY-MM-DD format", file=sys.stderr)
        return 2

    try:
        result = build_recap(date_str, Path(args.output_dir), args.skip_chart)
        if args.send_telegram:
            result = send_to_telegram(result, args.telegram_chat_id)
    except Exception as exc:  # noqa: BLE001 - command line tool should show clear failure
        print(f"[daily-market-recap] ERROR: {exc}", file=sys.stderr)
        return 1

    print(result.summary)
    print(f"Markdown: {result.markdown_path.relative_to(WORKSPACE)}")
    if args.send_telegram:
        print(
            "Telegram: "
            f"message={'sent' if result.telegram_message_sent else 'not sent'}, "
            f"document={'sent' if result.telegram_document_sent else 'not sent'}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
