#!/usr/bin/env python3
"""
Generate Sales Growth and Earnings Growth line charts for /estimate-actual.
Fetches FMP stable earnings, computes YoY growth %, plots solid line for actuals and dashed for estimates.
Saves estimate-actual-{TICKER}-revenue-growth-{DATE}.png and estimate-actual-{TICKER}-eps-growth-{DATE}.png.
"""

import argparse
import math
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests

WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS = WORKSPACE / "outputs"
FMP_STABLE = "https://financialmodelingprep.com/stable"
FMP_KEY = "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz"
MAX_QUARTERS = 12  # last N quarters to show on chart


def _quarter_from_date(date_str: str) -> tuple[int, int]:
    """Return (year, quarter) from YYYY-MM-DD. Quarter 1-4 from month."""
    if not date_str or len(date_str) < 10:
        return (0, 0)
    try:
        y = int(date_str[:4])
        m = int(date_str[5:7])
        q = (m - 1) // 3 + 1
        return (y, q)
    except (ValueError, IndexError):
        return (0, 0)


def _label(y: int, q: int) -> str:
    return f"Q{q}.{y % 100}"


def fetch_earnings(ticker: str) -> list[dict]:
    """Fetch FMP stable earnings for symbol. Returns list of earnings rows."""
    url = f"{FMP_STABLE}/earnings"
    params = {"symbol": ticker, "apikey": FMP_KEY}
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list):
            return data
    except Exception as e:
        print(f"[estimate_actual_chart] FMP fetch failed: {e}", flush=True)
    return []


def build_series(earnings: list[dict], value_key_actual: str, value_key_est: str):
    """
    Build chronological list of (label, value, is_actual, growth_pct).
    value_key_actual e.g. 'revenueActual', value_key_est e.g. 'revenueEstimated'.
    """
    # (year, quarter) -> (value, is_actual); keep first occurrence (API often newest first)
    by_period: dict[tuple[int, int], tuple[float, bool]] = {}
    for row in earnings:
        y, q = _quarter_from_date(row.get("date") or "")
        if (y, q) == (0, 0):
            continue
        actual = row.get(value_key_actual)
        est = row.get(value_key_est)
        if actual is not None:
            try:
                v = float(actual)
                by_period[(y, q)] = (v, True)
            except (TypeError, ValueError):
                pass
        if (y, q) not in by_period and est is not None:
            try:
                v = float(est)
                by_period[(y, q)] = (v, False)
            except (TypeError, ValueError):
                pass
    if not by_period:
        return []
    periods_sorted = sorted(by_period.keys())
    # Compute growth %
    result = []
    for i, (y, q) in enumerate(periods_sorted):
        value, is_actual = by_period[(y, q)]
        prior = (y - 1, q)
        growth = None
        if prior in by_period:
            prior_val = by_period[prior][0]
            if prior_val != 0:
                growth = (value - prior_val) / abs(prior_val) * 100
        result.append((_label(y, q), value, is_actual, growth))
    return result


def plot_growth_chart(
    series: list[tuple[str, float, bool, float | None]],
    title: str,
    out_path: Path,
) -> None:
    """Plot one line chart: X = quarter labels, Y = Growth (%). Solid for actuals, dashed for estimates."""
    if not series:
        return
    # Limit to last N quarters
    series = series[-MAX_QUARTERS:]
    labels = [s[0] for s in series]
    growths = [s[3] if s[3] is not None else float("nan") for s in series]
    is_actuals = [s[2] for s in series]
    # Find split: last index where is_actual is True (then estimates follow)
    split = -1
    for i in range(len(is_actuals) - 1, -1, -1):
        if is_actuals[i]:
            split = i
            break
    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(labels))
    # Actuals: from 0 to split (inclusive)
    if split >= 0:
        x_act = x[: split + 1]
        y_act = [growths[i] for i in x_act]
        if any(math.isfinite(y) for y in y_act):
            ax.plot(x_act, y_act, color="steelblue", linewidth=2, linestyle="-", marker="o", markersize=4, label="Actual")
    # Estimates: from split+1 to end (or all if no actuals)
    if split < len(x) - 1:
        x_est = x[split + 1 :]
        y_est = [growths[i] for i in x_est]
        if any(math.isfinite(y) for y in y_est):
            ax.plot(x_est, y_est, color="steelblue", linewidth=2, linestyle="--", alpha=0.8, marker="o", markersize=4, label="Estimate")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel("Growth (%)")
    ax.set_xlabel("Quarter")
    ax.set_title(title)
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color="gray", linestyle="-", linewidth=0.5)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"[estimate_actual_chart] Saved {out_path}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sales and Earnings Growth charts for estimate-actual")
    parser.add_argument("--ticker", required=True, help="Stock symbol (e.g. AVGO)")
    parser.add_argument("--date", default=None, help="Date YYYY-MM-DD for output filename (default: today)")
    parser.add_argument("--out-dir", default=None, help="Output directory (default: workspace outputs/)")
    args = parser.parse_args()

    ticker = args.ticker.upper()
    out_date = args.date or datetime.now().strftime("%Y-%m-%d")
    out_dir = Path(args.out_dir) if args.out_dir else OUTPUTS
    out_dir.mkdir(parents=True, exist_ok=True)

    earnings = fetch_earnings(ticker)
    if not earnings:
        print("[estimate_actual_chart] No earnings data; cannot generate charts.", flush=True)
        raise SystemExit(1)

    rev_series = build_series(earnings, "revenueActual", "revenueEstimated")
    eps_series = build_series(earnings, "epsActual", "epsEstimated")

    if not rev_series and not eps_series:
        print("[estimate_actual_chart] No revenue or EPS series; cannot generate charts.", flush=True)
        raise SystemExit(1)

    if rev_series:
        rev_path = out_dir / f"estimate-actual-{ticker}-revenue-growth-{out_date}.png"
        plot_growth_chart(rev_series, "Sales Growth", rev_path)
    if eps_series:
        eps_path = out_dir / f"estimate-actual-{ticker}-eps-growth-{out_date}.png"
        plot_growth_chart(eps_series, "Earnings Growth", eps_path)


if __name__ == "__main__":
    main()
