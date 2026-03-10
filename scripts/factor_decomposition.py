#!/usr/bin/env python3
"""
Altamira Capital — Factor Decomposition (Renaissance-Style)
============================================================
Decompose a fund's return stream into factor exposures (market, size, value,
momentum, quality, volatility, sector). Supports: (1) pasted/file monthly returns,
(2) 13F filer + FMP → synthetic monthly returns. Outputs regression betas, alpha,
R², and ETF replication weights.

Usage:
  # Pasted monthly returns (consecutive months from --start-date)
  python scripts/factor_decomposition.py --returns-inline "0.02,-0.01,0.03,..." --start-date 2020-01-01 --out outputs/factor-decomp.json

  # Returns from CSV (columns: date, return)
  python scripts/factor_decomposition.py --returns-file path/to/returns.csv --out outputs/factor-decomp.json

  # 13F filer: build monthly returns from holdings + FMP, then regress
  python scripts/factor_decomposition.py --cik 1067983 --from 2020-01-01 --to 2024-12-31 --out outputs/factor-decomp.json
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

WORKSPACE = Path(__file__).resolve().parent.parent
FMP_BASE = "https://financialmodelingprep.com/api/v3"
DEFAULT_13F_DIR = WORKSPACE / "outputs" / "13f"

# Factor proxy ETFs: market, size, value, momentum, quality, low-vol, sectors (subset)
FACTOR_ETFS = {
    "MKT": "SPY",
    "SMB": "IWM",
    "HML": "VTV",
    "MOM": "MTUM",
    "QUAL": "QUAL",
    "LOWVOL": "USMV",
    "XLF": "XLF",
    "XLK": "XLK",
    "XLE": "XLE",
}

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import cusip_loader
except ImportError:
    cusip_loader = None


def load_fmp_key() -> str:
    return os.environ.get("FMP_API_KEY", "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz")


def fetch_prices(ticker: str, from_date: str, to_date: str, api_key: str) -> list[dict]:
    """FMP historical-price-full. Returns list of {date, close}."""
    url = f"{FMP_BASE}/historical-price-full/{ticker}"
    params = {"from": from_date, "to": to_date, "apikey": api_key}
    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        hist = data.get("historical") or []
        return hist
    except Exception:
        return []


def daily_to_monthly_return(ticker: str, year: int, month: int, api_key: str) -> float | None:
    """Return simple monthly return (last close / first close - 1) for the given month."""
    from datetime import date
    import calendar
    last_day = calendar.monthrange(year, month)[1]
    from_d = date(year, month, 1).strftime("%Y-%m-%d")
    to_d = date(year, month, last_day).strftime("%Y-%m-%d")
    prices = fetch_prices(ticker, from_d, to_d, api_key)
    if not prices or len(prices) < 2:
        return None
    by_date = {p["date"]: float(p.get("close") or 0) for p in prices}
    dates_sorted = sorted(by_date.keys())
    first_close = by_date[dates_sorted[0]]
    last_close = by_date[dates_sorted[-1]]
    if first_close <= 0:
        return None
    return (last_close / first_close) - 1.0


def load_13f_filing_for_month(data_dir: Path, cik: str, year: int, month: int) -> dict | None:
    """Load the 13F filing effective for this month (latest period_end <= last day of month)."""
    from datetime import date
    import calendar
    last_day = calendar.monthrange(year, month)[1]
    month_end = date(year, month, last_day).strftime("%Y-%m-%d")
    month_end_compact = month_end.replace("-", "")

    cik = str(cik).strip().zfill(10)
    pattern = f"{cik}_*.json"
    files = sorted(data_dir.glob(pattern), key=lambda f: f.stem, reverse=False)
    for f in reversed(files):
        stem = f.stem
        if "_" not in stem:
            continue
        _, period = stem.split("_", 1)
        if period <= month_end_compact:
            with open(f, encoding="utf-8") as fp:
                return json.load(fp)
    return None


def holdings_to_weights(holdings: list[dict]) -> list[tuple[str, float]]:
    """Return list of (ticker, weight_pct/100). Uses cusip_loader for CUSIP->ticker."""
    total = 0.0
    for h in holdings:
        v = h.get("value")
        if v is None:
            v = (h.get("valueUsd") or 0) / 1000.0
        total += float(v)
    if total <= 0:
        return []
    out = []
    for h in holdings:
        v = h.get("value")
        if v is None:
            v = (h.get("valueUsd") or 0) / 1000.0
        w = float(v) / total
        cusip = (h.get("cusip") or h.get("CUSIP") or "").strip()
        ticker = cusip_loader.cusip_to_ticker(cusip) if cusip_loader else ""
        if ticker:
            out.append((ticker, w))
    return out


def monthly_returns_from_13f(
    cik: str,
    from_date: str,
    to_date: str,
    api_key: str,
    data_dir: Path,
) -> tuple[list[str], list[float]]:
    """Build (month_end_strings, fund_returns) from 13F + FMP. Month format YYYY-MM-DD (last day)."""
    from datetime import date, datetime
    import calendar

    months = []
    returns = []
    from_d = datetime.strptime(from_date[:10], "%Y-%m-%d").date()
    to_d = datetime.strptime(to_date[:10], "%Y-%m-%d").date()

    y, m = from_d.year, from_d.month
    while date(y, m, 1) <= to_d:
        last_day = calendar.monthrange(y, m)[1]
        month_end = date(y, m, last_day).strftime("%Y-%m-%d")
        filing = load_13f_filing_for_month(data_dir, cik, y, m)
        if not filing:
            y += (m == 12)
            m = (m % 12) + 1
            continue
        holdings = filing.get("holdings") or []
        weighted = holdings_to_weights(holdings)
        if not weighted:
            y += (m == 12)
            m = (m % 12) + 1
            continue
        port_ret = 0.0
        for ticker, weight in weighted:
            ret = daily_to_monthly_return(ticker, y, m, api_key)
            if ret is not None:
                port_ret += weight * ret
        months.append(month_end)
        returns.append(port_ret)
        y += (m == 12)
        m = (m % 12) + 1

    return months, returns


def parse_returns_inline(s: str) -> list[float]:
    """Parse comma- or space-separated returns."""
    out = []
    for part in s.replace(",", " ").split():
        try:
            out.append(float(part.strip()))
        except ValueError:
            continue
    return out


def parse_returns_file(path: Path) -> tuple[list[str], list[float]]:
    """Parse CSV with date and return columns. Return (dates, returns)."""
    dates = []
    returns = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return [], []
        for row in reader:
            # Try common column names
            date_val = row.get("date") or row.get("Date") or row.get("month")
            ret_val = row.get("return") or row.get("Return") or row.get("ret") or row.get("r")
            if date_val is not None and ret_val is not None:
                try:
                    dates.append(str(date_val).strip())
                    returns.append(float(ret_val))
                except ValueError:
                    continue
    return dates, returns


def build_factor_monthly_returns(
    from_date: str,
    to_date: str,
    api_key: str,
) -> tuple[list[str], dict[str, list[float]]]:
    """Fetch factor ETF monthly returns. Return (month_ends, {factor_name: [returns]})."""
    from datetime import date, datetime
    import calendar

    from_d = datetime.strptime(from_date[:10], "%Y-%m-%d").date()
    to_d = datetime.strptime(to_date[:10], "%Y-%m-%d").date()

    # Get all month-end dates in range
    month_ends = []
    y, m = from_d.year, from_d.month
    while date(y, m, 1) <= to_d:
        last_day = calendar.monthrange(y, m)[1]
        month_ends.append(date(y, m, last_day).strftime("%Y-%m-%d"))
        y += (m == 12)
        m = (m % 12) + 1

    factor_returns = {name: [] for name in FACTOR_ETFS}
    for name, ticker in FACTOR_ETFS.items():
        for me in month_ends:
            dt = datetime.strptime(me, "%Y-%m-%d").date()
            r = daily_to_monthly_return(ticker, dt.year, dt.month, api_key)
            factor_returns[name].append(r if r is not None else np.nan)

    return month_ends, factor_returns


def align_fund_and_factors(
    fund_months: list[str],
    fund_returns: list[float],
    factor_months: list[str],
    factor_returns: dict[str, list[float]],
) -> tuple[np.ndarray, np.ndarray, list[str], list[str]]:
    """Align by common months. Return (fund_arr, factor_matrix, factor_names, common_months)."""
    common = set(fund_months) & set(factor_months)
    if not common:
        return np.array([]), np.array([]), [], []
    common_sorted = sorted(common)
    fund_arr = np.array([fund_returns[fund_months.index(m)] for m in common_sorted])
    factor_names = list(FACTOR_ETFS.keys())
    cols = []
    for name in factor_names:
        vals = [factor_returns[name][factor_months.index(m)] for m in common_sorted]
        cols.append(vals)
    # Drop rows with any NaN in factors
    mat = np.array(cols).T
    valid = ~np.any(np.isnan(mat), axis=1)
    if not np.any(valid):
        return np.array([]), np.array([]), [], []
    fund_arr = fund_arr[valid]
    mat = mat[valid]
    common_sorted = [m for m, v in zip(common_sorted, valid) if v]
    return fund_arr, mat, factor_names, common_sorted


def run_ols(y: np.ndarray, X: np.ndarray) -> tuple[float, np.ndarray, float, float]:
    """OLS: y = X @ beta + alpha (add constant). Return alpha, betas, r_squared, adj_r_squared."""
    n, k = X.shape
    ones = np.ones((n, 1))
    X_with_const = np.hstack([ones, X])
    try:
        # (X'X)^{-1} X'y
        coeffs, *_ = np.linalg.lstsq(X_with_const, y, rcond=None)
        alpha = float(coeffs[0])
        betas = coeffs[1:]
        y_hat = X_with_const @ coeffs
        ss_res = np.sum((y - y_hat) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_sq = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        adj_r_sq = 1 - (1 - r_sq) * (n - 1) / (n - k - 1) if (n - k - 1) > 0 else r_sq
        return alpha, betas, float(r_sq), float(adj_r_sq)
    except Exception:
        return 0.0, np.zeros(X.shape[1]), 0.0, 0.0


def replication_weights(betas: np.ndarray, factor_names: list[str]) -> dict[str, float]:
    """Proportional to absolute beta; normalize so sum = 1. Market (MKT) gets weight 1, others as tilts."""
    raw = np.abs(betas)
    if np.sum(raw) <= 0:
        return {name: 0.0 for name in factor_names}
    w = raw / np.sum(raw)
    return {name: float(w[i]) for i, name in enumerate(factor_names)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Factor decomposition: fund returns vs factor ETFs.")
    ap.add_argument("--returns-inline", type=str, help="Comma-separated monthly returns (e.g. 0.02,-0.01,...)")
    ap.add_argument("--returns-file", type=str, help="CSV with date and return columns")
    ap.add_argument("--start-date", type=str, default="2020-01-01", help="First month (YYYY-MM-01) for inline returns")
    ap.add_argument("--cik", type=str, help="13F filer CIK (build monthly returns from 13F + FMP)")
    ap.add_argument("--from", dest="from_date", type=str, help="Start date for --cik (YYYY-MM-DD)")
    ap.add_argument("--to", dest="to_date", type=str, help="End date for --cik (YYYY-MM-DD)")
    ap.add_argument("--data-dir", type=str, default=str(DEFAULT_13F_DIR), help="13F JSON directory for --cik")
    ap.add_argument("--out", type=str, help="Write JSON result here")
    ap.add_argument("--fund-name", type=str, default="Fund", help="Label for fund in output")
    args = ap.parse_args()

    api_key = load_fmp_key()
    fund_months = []
    fund_returns = []
    source = "inline"

    if args.returns_file:
        path = Path(args.returns_file)
        if not path.is_absolute():
            path = WORKSPACE / path
        if not path.exists():
            print(f"File not found: {path}", file=sys.stderr)
            return 1
        fund_months, fund_returns = parse_returns_file(path)
        if not fund_returns:
            print("No valid date/return rows in file.", file=sys.stderr)
            return 1
        source = "file"
    elif args.returns_inline:
        fund_returns = parse_returns_inline(args.returns_inline)
        if not fund_returns:
            print("No valid numbers in --returns-inline.", file=sys.stderr)
            return 1
        # Generate month ends from start_date
        from datetime import date, datetime
        import calendar
        start = datetime.strptime(args.start_date[:10], "%Y-%m-%d").date()
        for i in range(len(fund_returns)):
            y = start.year + (start.month + i - 1) // 12
            m = (start.month + i - 1) % 12 + 1
            last = calendar.monthrange(y, m)[1]
            fund_months.append(date(y, m, last).strftime("%Y-%m-%d"))
        source = "inline"
    elif args.cik:
        if not args.from_date or not args.to_date:
            print("With --cik provide --from and --to.", file=sys.stderr)
            return 1
        data_dir = Path(args.data_dir).resolve()
        if not data_dir.exists():
            print(f"13F data dir not found: {data_dir}", file=sys.stderr)
            return 1
        if not cusip_loader:
            print("cusip_loader not found; cannot resolve CUSIP to ticker.", file=sys.stderr)
            return 1
        fund_months, fund_returns = monthly_returns_from_13f(
            args.cik, args.from_date, args.to_date, api_key, data_dir
        )
        if not fund_returns:
            print("No monthly returns from 13F (check data dir and CUSIP map).", file=sys.stderr)
            return 1
        source = f"13f_cik_{args.cik}"
    else:
        print("Provide --returns-inline, --returns-file, or --cik with --from/--to.", file=sys.stderr)
        return 1

    # Factor returns over same or wider range
    if fund_months:
        from_d = min(fund_months)
        to_d = max(fund_months)
    else:
        from_d = args.start_date
        to_d = args.to_date or args.from_date or args.start_date
    factor_months, factor_returns = build_factor_monthly_returns(from_d, to_d, api_key)

    fund_arr, factor_mat, factor_names, common_months = align_fund_and_factors(
        fund_months, fund_returns, factor_months, factor_returns
    )
    if len(fund_arr) < 12:
        print("Insufficient common months (need at least 12) for regression.", file=sys.stderr)
        return 1

    alpha, betas, r_sq, adj_r_sq = run_ols(fund_arr, factor_mat)
    repl = replication_weights(betas, factor_names)

    result = {
        "fund_name": args.fund_name,
        "source": source,
        "months": common_months,
        "fund_returns": [round(float(x), 6) for x in fund_arr],
        "factor_returns": {
            name: [round(float(factor_returns[name][factor_months.index(m)]), 6) for m in common_months]
            for name in factor_names
        },
        "regression": {
            "alpha": round(float(alpha), 6),
            "betas": {name: round(float(betas[i]), 6) for i, name in enumerate(factor_names)},
            "r_squared": round(r_sq, 6),
            "adj_r_squared": round(adj_r_sq, 6),
            "replication_weights": {k: round(v, 6) for k, v in repl.items()},
        },
    }

    out_str = json.dumps(result, indent=2)
    if args.out:
        Path(args.out).write_text(out_str, encoding="utf-8")
        print(f"Wrote {args.out}", file=sys.stderr)
    else:
        print(out_str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
