#!/usr/bin/env python3
"""
Altamira Capital — 13F Backtester (Scaffold)
============================================
Backtest a copycat or 13F-based strategy: given a target portfolio (from copycat-13f.py
or a single filer's filing), compute hypothetical buy-and-hold returns using FMP historical
prices. Requires FMP_API_KEY (env or default in script). CUSIP->ticker mapping is needed
for full backtest; this scaffold uses a small built-in map for sample CUSIPs.

Usage:
  # Backtest copycat portfolio (from copycat-13f.py output)
  python scripts/copycat-13f.py --ciks 0001067983 --out outputs/copycat.json
  python scripts/13f-backtest.py --portfolio outputs/copycat.json --from 2025-09-30 --to 2026-02-20

  # Backtest single filer's latest filing
  python scripts/13f-backtest.py --cik 0001067983 --data-dir outputs/13f --from 2025-09-30 --to 2026-02-20

  # Output: total return %, annualized return, per-ticker contribution (when tickers available)
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests

# Allow import of cusip_loader from scripts
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cusip_loader

WORKSPACE = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = WORKSPACE / "outputs" / "13f"
FMP_BASE = "https://financialmodelingprep.com/api/v3"


def load_fmp_key() -> str:
    return os.environ.get("FMP_API_KEY", "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz")


def fetch_prices(ticker: str, from_date: str, to_date: str, api_key: str) -> list[dict]:
    """FMP historical-price-full. Returns list of {date, close, ...}."""
    url = f"{FMP_BASE}/historical-price-full/{ticker}"
    params = {"from": from_date, "to": to_date, "apikey": api_key}
    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        hist = data.get("historical") or []
        return hist
    except Exception:
        return []


def backtest_portfolio(
    holdings: list[dict],
    from_date: str,
    to_date: str,
    api_key: str,
    weight_key: str = "weightPct",
) -> dict:
    """
    holdings: list of {cusip, name, weightPct or valueUsd}.
    Returns { totalReturnPct, annualizedReturnPct, tickerReturns: [...], missingTickers: [...] }
    """
    ticker_returns = []
    missing = []
    total_return = 0.0
    total_weight = 0.0

    for h in holdings:
        cusip = (h.get("cusip") or "").strip()
        ticker = cusip_loader.cusip_to_ticker(cusip)
        if not ticker:
            missing.append(cusip)
            continue
        weight_pct = h.get(weight_key)
        if weight_pct is None and "valueUsd" in h:
            # Equal weight fallback
            weight_pct = 100.0 / len(holdings) if holdings else 0
        if weight_pct is None:
            weight_pct = 0
        weight_pct = float(weight_pct) / 100.0  # as fraction
        prices = fetch_prices(ticker, from_date, to_date, api_key)
        if not prices:
            missing.append(ticker)
            continue
        by_date = {p["date"]: float(p.get("close") or 0) for p in prices}
        dates_sorted = sorted(by_date.keys())
        if len(dates_sorted) < 2:
            continue
        start_price = by_date.get(from_date) or by_date.get(dates_sorted[0])
        end_price = by_date.get(to_date) or by_date.get(dates_sorted[-1])
        if not start_price or not end_price:
            continue
        ret = (end_price - start_price) / start_price
        total_return += weight_pct * ret
        total_weight += weight_pct
        ticker_returns.append({"ticker": ticker, "cusip": cusip, "weightPct": weight_pct * 100, "returnPct": round(ret * 100, 2)})

    if total_weight > 0:
        total_return = total_return / total_weight  # normalize to portfolio return
    days = max(1, (int(to_date.replace("-", "")) - int(from_date.replace("-", ""))))
    years = days / 365.25
    ann = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0

    return {
        "fromDate": from_date,
        "toDate": to_date,
        "totalReturnPct": round(total_return * 100, 2),
        "annualizedReturnPct": round(ann * 100, 2),
        "tickerReturns": ticker_returns,
        "missingTickers": missing,
        "holdingsCount": len(holdings),
        "tickersWithData": len(ticker_returns),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="13F backtest: copycat buy-and-hold returns via FMP.")
    ap.add_argument("--portfolio", type=str, help="JSON file from copycat-13f.py (must have .tickers)")
    ap.add_argument("--cik", type=str, help="Filer CIK (use latest filing as portfolio if --portfolio not set)")
    ap.add_argument("--data-dir", type=str, default=str(DEFAULT_DATA_DIR), help="13F JSON directory (for --cik)")
    ap.add_argument("--from", dest="from_date", type=str, required=True, help="Start date YYYY-MM-DD")
    ap.add_argument("--to", dest="to_date", type=str, required=True, help="End date YYYY-MM-DD")
    ap.add_argument("--out", type=str, help="Write JSON to file")
    args = ap.parse_args()

    holdings = []
    if args.portfolio:
        p = Path(args.portfolio)
        if not p.is_absolute():
            p = WORKSPACE / p
        if not p.exists():
            print(f"Portfolio file not found: {p}", file=sys.stderr)
            return 1
        data = json.loads(p.read_text(encoding="utf-8"))
        holdings = data.get("tickers") or []
    elif args.cik:
        data_dir = Path(args.data_dir).resolve()
        cik = str(args.cik).strip().zfill(10)
        pattern = f"{cik}_*.json"
        files = sorted(data_dir.glob(pattern), key=lambda f: f.stem, reverse=True)
        if not files:
            print(f"No filing found for CIK {args.cik}", file=sys.stderr)
            return 1
        filing = json.loads(files[0].read_text(encoding="utf-8"))
        raw = filing.get("holdings") or []
        total = sum((float(h.get("value") or 0) or (float(h.get("valueUsd") or 0) / 1000) for h in raw)
        for h in raw:
            v = float(h.get("value") or 0) or (float(h.get("valueUsd") or 0) / 1000)
            w = (100.0 * v / total) if total else 0
            holdings.append({
                "cusip": (h.get("cusip") or h.get("CUSIP") or "").strip(),
                "name": (h.get("nameOfIssuer") or h.get("issuer") or "").strip(),
                "weightPct": w,
                "valueUsd": (float(h.get("value") or 0) * 1000),
            })
    else:
        print("Provide --portfolio or --cik.", file=sys.stderr)
        return 1

    if not holdings:
        print("No holdings to backtest.", file=sys.stderr)
        return 1

    api_key = load_fmp_key()
    result = backtest_portfolio(holdings, args.from_date, args.to_date, api_key)
    s = json.dumps(result, indent=2)
    if args.out:
        Path(args.out).write_text(s, encoding="utf-8")
        print(f"Wrote {args.out}", file=sys.stderr)
    else:
        print(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
