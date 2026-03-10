#!/usr/bin/env python3
"""
Refresh context/current-data.md Portfolio section from the same data that feeds
the Portfolio app (http://localhost:8501/Portfolio).

Data sources (same as app):
  - Google Sheet "Daily Dashboard" (n8n writes here; app may read from here)
  - Local JSON/CSV in context/ or outputs/portfolio/ (if app exports there)

Usage:
  # Pull from Google Sheets (same sheet as n8n / app):
  python scripts/refresh-portfolio-context.py --sheets

  # Try local paths the app might use (context/*.json, outputs/portfolio/*.json):
  python scripts/refresh-portfolio-context.py --local

  # Read from a specific file:
  python scripts/refresh-portfolio-context.py --file context/portfolio-export.json

  # Fetch from an API (if app exposes one):
  python scripts/refresh-portfolio-context.py --url http://localhost:8501/api/portfolio

For --sheets: set GOOGLE_SHEET_ID and use a service account JSON
(GOOGLE_APPLICATION_CREDENTIALS) or OAuth. Same workbook as Daily Dashboard.
"""

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    gspread = None

WORKSPACE = Path(__file__).resolve().parent.parent
CONTEXT = WORKSPACE / "context"
CURRENT_DATA = CONTEXT / "current-data.md"
PORTFOLIO_DETAILS = CONTEXT / "portfolio-details.md"

# Map our table fields to typical JSON keys (snake_case or camelCase)
SNAPSHOT_KEYS = {
    "Date": ["date"],
    "Portfolio Value": ["portfolioValue", "portfolio_value"],
    "Daily P&L ($)": ["dailyPnL", "daily_pnl"],
    "Daily P&L (%)": ["dailyPnLPercent", "daily_pnl_percent"],
    "Cumulative P&L ($)": ["cumulativePnL", "cumulative_pnl"],
    "Cumulative P&L (%)": ["cumulativePnLPercent", "cumulative_pnl_percent"],
    "Net Delta Exposure": ["netDelta", "net_delta"],
    "Daily Theta Income": ["dailyTheta", "daily_theta"],
    "Open CSP Count": ["openCSPCount", "open_csp_count"],
    "Open Equity Positions": ["openEquityCount", "open_equity_count"],
    "Cash %": ["cashPercent", "cash_percent"],
    "VIX Close": ["vixClose", "vix_close"],
    "SPY Close": ["spyClose", "spy_close"],
}

# Google Sheet "Daily Dashboard" column names (n8n vs workbook may differ)
SHEET_COLUMN_ALIASES = {
    "Date": ["Date"],
    "Portfolio Value": ["Portfolio Value"],
    "Daily P&L ($)": ["Daily P&L ($)"],
    "Daily P&L (%)": ["Daily P&L (%)"],
    "Cumulative P&L ($)": ["Cumulative P&L ($)"],
    "Cumulative P&L (%)": ["Cumulative P&L (%)"],
    "Net Delta Exposure": ["Net Delta Exposure", "Net Delta"],
    "Daily Theta Income": ["Daily Theta Income", "Daily Theta"],
    "Open CSP Count": ["Open CSP Count"],
    "Open Equity Positions": ["Open Equity Positions"],
    "Cash %": ["Cash %"],
    "VIX Close": ["VIX Close"],
    "SPY Close": ["SPY Close"],
}


def get_value(data: dict, keys: list):
    """Get first key that exists; format number for display."""
    for k in keys:
        if k in data and data[k] is not None:
            v = data[k]
            if isinstance(v, float):
                if abs(v) >= 1:
                    return f"{v:,.2f}"
                return f"{v:.2%}" if "Percent" in str(keys) or "%" in str(keys) else f"{v:.2f}"
            return str(v)
    return "—"


def load_from_url(url: str) -> dict | None:
    if not requests:
        print("Install requests: pip install requests", file=sys.stderr)
        return None
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"URL fetch failed: {e}", file=sys.stderr)
        return None


def load_from_file(path: Path) -> dict | None:
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return None
    path = Path(path)
    suffix = path.suffix.lower()
    try:
        if suffix == ".csv":
            return _load_from_csv(path)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        # If wrapped in {"snapshot": {...}} or similar, unwrap
        if isinstance(data, dict) and "snapshot" in data:
            return data["snapshot"]
        if isinstance(data, dict) and len(data) == 1 and isinstance(next(iter(data.values())), dict):
            return next(iter(data.values()))
        return data if isinstance(data, dict) else None
    except Exception as e:
        print(f"File read failed: {e}", file=sys.stderr)
        return None


def _load_from_csv(path: Path) -> dict | None:
    """Read last data row of a CSV; first row = headers."""
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    if len(rows) < 2:
        return None
    headers = [h.strip() for h in rows[0]]
    # Last row that has at least one non-empty cell
    data_row = None
    for r in reversed(rows[1:]):
        if any(c and c.strip() for c in r):
            data_row = r
            break
    if not data_row:
        return None
    # Normalize length
    while len(data_row) < len(headers):
        data_row.append("")
    row = data_row[: len(headers)]
    # Build dict; try to coerce numbers
    out = {}
    for h, v in zip(headers, row):
        v = v.strip() if v else ""
        if not h:
            continue
        try:
            if "." in v and v.replace(".", "").replace("-", "").isdigit():
                out[h] = float(v)
            elif v.isdigit() or (v.startswith("-") and v[1:].isdigit()):
                out[h] = int(v)
            else:
                out[h] = v
        except Exception:
            out[h] = v
    return _sheet_row_to_snapshot(out)


def _sheet_row_to_snapshot(row: dict) -> dict:
    """Map Google Sheet row (any header alias) to our canonical snapshot keys."""
    snapshot = {}
    for field, keys in SNAPSHOT_KEYS.items():
        value = None
        for k in keys:
            if k in row and row[k] is not None and str(row[k]).strip() != "":
                value = row[k]
                break
        if value is None and field in SHEET_COLUMN_ALIASES:
            for col in SHEET_COLUMN_ALIASES[field]:
                if col in row and row[col] is not None and str(row[col]).strip() != "":
                    value = row[col]
                    break
        if value is not None:
            snapshot[keys[0]] = value
    return snapshot


def load_from_sheets() -> dict | None:
    """Read last row of 'Daily Dashboard' from the paper trading Google Sheet."""
    if not gspread:
        print("Install gspread and google-auth: pip install gspread google-auth", file=sys.stderr)
        return None
    sheet_id = os.environ.get("GOOGLE_SHEET_ID", "").strip()
    if not sheet_id:
        print("Set GOOGLE_SHEET_ID to your paper trading workbook ID", file=sys.stderr)
        return None
    try:
        creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if creds_path and Path(creds_path).exists():
            scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
            credentials = Credentials.from_service_account_file(creds_path, scopes=scopes)
        else:
            print("Set GOOGLE_APPLICATION_CREDENTIALS to a service account JSON path", file=sys.stderr)
            return None
        gc = gspread.authorize(credentials)
        sh = gc.open_by_key(sheet_id)
        ws = sh.worksheet("Daily Dashboard")
        rows = ws.get_all_values()
        if len(rows) < 2:
            return None
        headers = [h.strip() for h in rows[0]]
        # Last row with data
        data_row = None
        for r in reversed(rows[1:]):
            if any(c and str(c).strip() for c in r):
                data_row = r
                break
        if not data_row:
            return None
        while len(data_row) < len(headers):
            data_row.append("")
        row = dict(zip(headers, data_row[: len(headers)]))
        # Coerce numbers
        for k, v in list(row.items()):
            if v is None or (isinstance(v, str) and not v.strip()):
                continue
            try:
                s = str(v).strip().replace(",", "")
                if s.replace(".", "").replace("-", "").isdigit():
                    row[k] = float(s) if "." in s else int(s)
            except Exception:
                pass
        return _sheet_row_to_snapshot(row)
    except Exception as e:
        print(f"Google Sheets read failed: {e}", file=sys.stderr)
        return None


# Paths to try when --local is used (same data the app might read)
LOCAL_CANDIDATE_PATHS = [
    "context/portfolio-export.json",
    "context/daily-dashboard.json",
    "context/portfolio-snapshot.json",
    "context/daily-dashboard.csv",
    "outputs/portfolio/latest.json",
    "outputs/portfolio/daily-dashboard.csv",
]


def build_table(data: dict) -> str:
    lines = [
        "| Field | Value | Notes |",
        "| ----- | ----- | ----- |",
    ]
    notes = {
        "Date": "YYYY-MM-DD of snapshot",
        "Portfolio Value": "Total account value",
        "Daily P&L ($)": "vs previous close",
        "Daily P&L (%)": "",
        "Cumulative P&L ($)": "vs $100K starting capital",
        "Cumulative P&L (%)": "",
        "Net Delta Exposure": "Target range -30 to +50 per $100K",
        "Daily Theta Income": "Target positive (income)",
        "Open CSP Count": "Short put contracts",
        "Open Equity Positions": "Long stock count",
        "Cash %": "Target ≥ 15%",
        "VIX Close": "",
        "SPY Close": "",
    }
    for field, keys in SNAPSHOT_KEYS.items():
        value = get_value(data, keys)
        note = notes.get(field, "")
        lines.append(f"| {field} | {value} | {note} |")
    return "\n".join(lines)


def update_current_data(new_table: str) -> bool:
    if not CURRENT_DATA.exists():
        print(f"Not found: {CURRENT_DATA}", file=sys.stderr)
        return False
    text = CURRENT_DATA.read_text(encoding="utf-8")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    start_marker = "**Latest dashboard snapshot** (from the Portfolio app):"
    start = text.find(start_marker)
    if start == -1:
        print("Could not find Portfolio section in current-data.md", file=sys.stderr)
        return False
    # Find start of "**Current positions**" paragraph (any newlines before it)
    positions_marker = "**Current positions**"
    end_idx = text.find(positions_marker, start)
    if end_idx == -1:
        print("Could not find **Current positions** in current-data.md", file=sys.stderr)
        return False
    # Suffix starts at the blank line(s) before **Current positions**
    suffix_start = text.rfind("\n\n", start, end_idx)
    if suffix_start == -1:
        suffix_start = text.rfind("\n", start, end_idx)
    if suffix_start == -1:
        suffix_start = end_idx
    replacement = f"{start_marker}\n\n{new_table}"
    new_text = text[:start] + replacement + text[suffix_start:]
    CURRENT_DATA.write_text(new_text, encoding="utf-8")
    return True


def build_portfolio_details_table(data: dict) -> str:
    """Build a two-column table for portfolio-details.md (no Notes column)."""
    lines = ["| Field | Value |", "| ----- | ----- |"]
    for field, keys in SNAPSHOT_KEYS.items():
        value = get_value(data, keys)
        lines.append(f"| {field} | {value} |")
    return "\n".join(lines)


def update_portfolio_details(data: dict, source_hint: str = "") -> bool:
    """Write or update context/portfolio-details.md with snapshot table."""
    table = build_portfolio_details_table(data)
    date_val = data.get("date") or data.get("Date") or ""
    try:
        if PORTFOLIO_DETAILS.exists():
            text = PORTFOLIO_DETAILS.read_text(encoding="utf-8")
            text = text.replace("\r\n", "\n").replace("\r", "\n")
            # Replace the "Latest Dashboard Snapshot" table
            pattern = re.compile(
                r"(## Latest Dashboard Snapshot\n\n)(\| Field \| Value \|\n\| ----- \| ----- \|\n(?:\|[^\n]+\n)+)",
                re.MULTILINE,
            )
            if pattern.search(text):
                text = pattern.sub(r"\g<1>" + table + "\n", text)
            else:
                # Fallback: look for ## Latest Dashboard Snapshot and replace until ## Current
                start = text.find("## Latest Dashboard Snapshot")
                end = text.find("## Current Positions")
                if start != -1 and end != -1:
                    text = text[:start] + "## Latest Dashboard Snapshot\n\n" + table + "\n\n" + text[end:]
            # Update "Last export" line
            last_export = f"*Last export: {date_val or 'snapshot'}. "
            if source_hint:
                last_export += f"Source: {source_hint}. "
            last_export += "Run `python scripts/refresh-portfolio-context.py --sheets` or `--local` to refresh.*"
            old_last = re.compile(r"\*Last export:.*?\*", re.DOTALL)
            if old_last.search(text):
                text = old_last.sub(last_export, text)
        else:
            header = """# Portfolio Details (Workspace Context Export)

> Exported for Claude and scripts. **Source:** Same data that feeds the Streamlit app at http://localhost:8501/Portfolio — Google Sheet "Daily Dashboard" + "Position History", or local export at `context/portfolio-export.json`.

---

## Latest Dashboard Snapshot

"""
            footer = """

---

## Current Positions

*(Position-level: from Position History sheet or app export.)*

| Date | Symbol | AssetType | Quantity | Market Value | Weight % | Sector | Delta | Theta | Strike | Expiration | CallPut |
|------|--------|-----------|----------|-------------|----------|--------|-------|-------|--------|------------|--------|
| — | — | — | — | — | — | — | — | — | — | — | — |

---
"""
            text = header + table + footer + "\n" + (f"*Last export: {date_val}. Run script to refresh.*" if date_val else "*Run script to refresh.*")
        PORTFOLIO_DETAILS.write_text(text, encoding="utf-8")
        return True
    except Exception as e:
        print(f"Could not update portfolio-details.md: {e}", file=sys.stderr)
        return False


def main():
    ap = argparse.ArgumentParser(description="Refresh Portfolio section in context/current-data.md from app or file.")
    ap.add_argument("--url", help="API URL returning JSON snapshot (e.g. http://localhost:8501/api/portfolio)")
    ap.add_argument("--file", help="Path to JSON/CSV file with snapshot (e.g. context/portfolio-export.json)")
    ap.add_argument("--sheets", action="store_true", help="Pull last row from Google Sheet 'Daily Dashboard' (same data as n8n/app)")
    ap.add_argument("--local", action="store_true", help="Try local paths the app might use (context/*.json, outputs/portfolio/*)")
    args = ap.parse_args()

    data = None
    source_hint = ""
    if args.sheets:
        data = load_from_sheets()
        source_hint = "Google Sheet Daily Dashboard"
    elif args.url:
        data = load_from_url(args.url)
        source_hint = args.url
    elif args.file:
        path = Path(args.file)
        if not path.is_absolute():
            path = WORKSPACE / path
        data = load_from_file(path)
        source_hint = str(path)
    elif args.local:
        for rel in LOCAL_CANDIDATE_PATHS:
            path = WORKSPACE / rel
            data = load_from_file(path)
            if data:
                source_hint = rel
                print(f"Loaded from {path}", file=sys.stderr)
                break

    if data:
        table = build_table(data)
        if update_current_data(table):
            print("Updated context/current-data.md with latest portfolio snapshot.")
        else:
            sys.exit(1)
        if update_portfolio_details(data, source_hint):
            print("Updated context/portfolio-details.md.")
    else:
        print("Portfolio source of truth: http://localhost:8501/Portfolio")
        print("Pull from the same data that feeds the app:")
        print("  --sheets   Read last row from Google Sheet 'Daily Dashboard' (set GOOGLE_SHEET_ID + GOOGLE_APPLICATION_CREDENTIALS)")
        print("  --local    Try context/portfolio-export.json, context/daily-dashboard.json, outputs/portfolio/latest.json, etc.")
        print("  --file     Path to JSON or CSV snapshot")
        print("  --url      API URL returning JSON")


if __name__ == "__main__":
    main()
