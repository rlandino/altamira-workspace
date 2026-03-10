#!/usr/bin/env python3
"""
Build monthly snapshot data for the Holding Snapshot dashboard.
Run from this deploy folder. Outputs context/holding-monthly-snapshots.json here.

Usage:
  python build-holding-monthly-snapshots.py --sheets
  python build-holding-monthly-snapshots.py --file path/to/position-history.csv
  python build-holding-monthly-snapshots.py --local
"""
import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    gspread = None

# When run from this deploy folder, output goes to this folder's context/
WORKSPACE = Path(__file__).resolve().parent
CONTEXT = WORKSPACE / "context"
OUTPUT_PATH = CONTEXT / "holding-monthly-snapshots.json"

DATE_KEYS = ["Date", "date"]
SYMBOL_KEYS = ["Symbol", "symbol", "Ticker", "ticker"]
QTY_KEYS = ["Quantity", "quantity", "Qty", "qty"]
MV_KEYS = ["MarketValue", "market_value", "marketValue", "MKT VALUE", "Market Value"]
CB_KEYS = ["CostBasis", "cost_basis", "costBasis", "Cost Basis", "COST BASIS", "AvgCost", "avg_cost"]
ASSET_KEYS = ["AssetType", "asset_type", "Asset Type"]


def _get(row: dict, key_lists: list):
    for keys in key_lists:
        for k in keys:
            if k in row and row[k] is not None and str(row[k]).strip() != "":
                v = row[k]
                return v.strip() if isinstance(v, str) else v
    return None


def _parse_date(s: str) -> datetime | None:
    if s is None:
        return None
    s = str(s).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s[:10], fmt)
        except ValueError:
            continue
    return None


def _to_float(v) -> float | None:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def load_from_sheets() -> list[dict] | None:
    if not gspread:
        print("Install gspread and google-auth", file=sys.stderr)
        return None
    sheet_id = os.environ.get("GOOGLE_SHEET_ID", "").strip()
    if not sheet_id:
        print("Set GOOGLE_SHEET_ID", file=sys.stderr)
        return None
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path or not Path(creds_path).exists():
        print("Set GOOGLE_APPLICATION_CREDENTIALS", file=sys.stderr)
        return None
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
        credentials = Credentials.from_service_account_file(creds_path, scopes=scopes)
        gc = gspread.authorize(credentials)
        sh = gc.open_by_key(sheet_id)
        ws = sh.worksheet("Position History")
        rows = ws.get_all_values()
        if len(rows) < 2:
            return None
        headers = [h.strip() for h in rows[0]]
        records = []
        for r in rows[1:]:
            if len(r) < len(headers):
                r = r + [""] * (len(headers) - len(r))
            row = dict(zip(headers, r[: len(headers)]))
            if not _get(row, [SYMBOL_KEYS]) or not _get(row, [DATE_KEYS]):
                continue
            for k in list(row.keys()):
                v = _to_float(row[k])
                if v is not None:
                    row[k] = v
            records.append(row)
        return records
    except Exception as e:
        print(f"Google Sheets read failed: {e}", file=sys.stderr)
        return None


def load_from_file(path: Path) -> list[dict] | None:
    if not path.exists():
        return None
    suffix = path.suffix.lower()
    try:
        if suffix == ".csv":
            return _load_csv(path)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        for key in ("rows", "positions", "positionHistory"):
            if isinstance(data, dict) and key in data and isinstance(data[key], list):
                return data[key]
        if isinstance(data, dict) and len(data) == 1:
            val = next(iter(data.values()))
            if isinstance(val, list) and val and isinstance(val[0], dict):
                return val
        return None
    except Exception as e:
        print(f"File read failed: {e}", file=sys.stderr)
        return None


def _load_csv(path: Path) -> list[dict] | None:
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    if len(rows) < 2:
        return None
    headers = [h.strip() for h in rows[0]]
    records = []
    for r in rows[1:]:
        if len(r) < len(headers):
            r = r + [""] * (len(headers) - len(r))
        row = dict(zip(headers, r[: len(headers)]))
        if not _get(row, [SYMBOL_KEYS]) or not _get(row, [DATE_KEYS]):
            continue
        for k in list(row.keys()):
            v = _to_float(row[k])
            if v is not None:
                row[k] = v
        records.append(row)
    return records


def build_monthly_snapshots(records: list[dict]) -> list[dict]:
    filtered = [r for r in records if not _get(r, [ASSET_KEYS]) or str(_get(r, [ASSET_KEYS])).upper() in ("EQ", "EQUITY", "")]
    by_ticker_month = defaultdict(dict)
    for r in filtered:
        dt = _parse_date(_get(r, [DATE_KEYS]))
        symbol = _get(r, [SYMBOL_KEYS])
        if not dt or not symbol:
            continue
        key = f"{dt.year}-{dt.month:02d}"
        existing = by_ticker_month[symbol].get(key)
        if existing is None or _parse_date(_get(existing, [DATE_KEYS])) < dt:
            by_ticker_month[symbol][key] = r
    result = []
    for ticker in sorted(by_ticker_month.keys()):
        months_data = by_ticker_month[ticker]
        sorted_keys = sorted(months_data.keys())
        rows = []
        prev_value = None
        for key in sorted_keys:
            r = months_data[key]
            dt = _parse_date(_get(r, [DATE_KEYS]))
            qty = _to_float(_get(r, [QTY_KEYS]))
            mv = _to_float(_get(r, [MV_KEYS]))
            cb = _to_float(_get(r, [CB_KEYS]))
            value = mv if mv is not None else (cb * qty if cb is not None and qty is not None else None)
            if value is None and prev_value is not None:
                value = prev_value
            month_chg_dollar = None
            month_chg_pct = None
            if prev_value is not None and value is not None and prev_value != 0:
                month_chg_dollar = value - prev_value
                month_chg_pct = (month_chg_dollar / prev_value) * 100
            rows.append({
                "month": key,
                "date": dt.strftime("%Y-%m-%d") if dt else None,
                "qty": qty,
                "ticker": ticker,
                "costBasis": cb,
                "marketValue": mv,
                "monthChgDollar": round(month_chg_dollar, 2) if month_chg_dollar is not None else None,
                "monthChgPct": round(month_chg_pct, 2) if month_chg_pct is not None else None,
            })
            if value is not None:
                prev_value = value
        result.append({"ticker": ticker, "rows": rows})
    return result


def main():
    ap = argparse.ArgumentParser(description="Build holding monthly snapshots.")
    ap.add_argument("--sheets", action="store_true")
    ap.add_argument("--file", help="Path to Position History CSV/JSON")
    ap.add_argument("--local", action="store_true", help="Try context/*.csv|.json in this folder")
    ap.add_argument("--out", default=str(OUTPUT_PATH))
    args = ap.parse_args()

    records = None
    source_hint = ""
    if args.sheets:
        records = load_from_sheets()
        source_hint = "Google Sheet Position History"
    elif args.file:
        p = Path(args.file)
        if not p.is_absolute():
            p = WORKSPACE / p
        records = load_from_file(p)
        source_hint = str(p)
    elif args.local:
        for rel in ["context/position-history-export.csv", "context/position-history-export.json", "context/portfolio-monthly-snapshots.json"]:
            p = WORKSPACE / rel
            records = load_from_file(p)
            if records:
                source_hint = rel
                print(f"Loaded from {p}", file=sys.stderr)
                break

    if not records:
        print("No Position History data. Use --sheets, --file path, or --local", file=sys.stderr)
        sys.exit(1)

    snapshots = build_monthly_snapshots(records)
    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = WORKSPACE / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(snapshots, f, indent=2)
    print(f"Wrote {len(snapshots)} tickers to {out_path}")
    if source_hint:
        print(f"Source: {source_hint}")


if __name__ == "__main__":
    main()
