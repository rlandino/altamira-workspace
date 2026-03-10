#!/usr/bin/env python3
"""
Altamira Capital — Risk Parity Portfolio Analyzer
==================================================
AQR-style risk parity analysis: risk decomposition, equal risk contribution
weights, backtest vs current allocation, stress tests (2008, 2020, 2022).
Uses FMP historical prices. Outputs JSON for report generation.

Usage:
  # From portfolio file (JSON: list of {ticker, weightPct} or {symbol, weight})
  python scripts/risk_parity_analyzer.py --portfolio context/portfolio-export.json --from 2019-01-01 --to 2026-02-23

  # Inline weights (ticker:weight,ticker:weight)
  python scripts/risk_parity_analyzer.py --weights "SPY:30,AGG:40,GLD:30" --from 2020-01-01

  # Output to file
  python scripts/risk_parity_analyzer.py --portfolio context/portfolio-export.json --out outputs/risk-parity-result.json
"""

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from scipy.optimize import minimize

WORKSPACE = Path(__file__).resolve().parent.parent
FMP_BASE = "https://financialmodelingprep.com/api/v3"


def load_fmp_key() -> str:
    return os.environ.get("FMP_API_KEY", "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz")


def fetch_prices(ticker: str, from_date: str, to_date: str, api_key: str) -> pd.DataFrame:
    """Fetch daily historical prices from FMP. Returns DataFrame with date, close."""
    url = f"{FMP_BASE}/historical-price-full/{ticker}"
    params = {"from": from_date, "to": to_date, "apikey": api_key}
    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        hist = data.get("historical") or []
        if not hist:
            return pd.DataFrame()
        df = pd.DataFrame(hist)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        return df[["date", "close"]].rename(columns={"close": ticker})
    except Exception:
        return pd.DataFrame()


def build_returns_matrix(
    tickers: list[str],
    from_date: str,
    to_date: str,
    api_key: str,
) -> pd.DataFrame:
    """Fetch prices for all tickers, align dates, compute daily returns. Returns T x N DataFrame."""
    dfs = []
    for t in tickers:
        df = fetch_prices(t, from_date, to_date, api_key)
        if df.empty or len(df) < 22:
            continue
        df = df.set_index("date")
        dfs.append(df)
    if not dfs:
        return pd.DataFrame()
    combined = pd.concat(dfs, axis=1, join="inner")
    combined = combined.dropna(how="all").ffill().dropna()
    returns = combined.pct_change().dropna()
    return returns


def risk_decomposition(
    weights: np.ndarray,
    cov: np.ndarray,
) -> tuple[float, np.ndarray, np.ndarray]:
    """
    Portfolio vol (annualized), risk contribution per asset, risk contribution %.
    RC_i = w_i * (Sigma @ w)_i / sigma_p  =>  sum(RC) = sigma_p.
    """
    w = np.asarray(weights, dtype=float).reshape(-1, 1)
    sigma_p_sq = (w.T @ cov @ w).item()
    sigma_p = np.sqrt(max(sigma_p_sq, 1e-12))
    marginal = (cov @ w).flatten()
    rc = w.flatten() * marginal / sigma_p if sigma_p > 0 else np.zeros_like(w.flatten())
    rc_pct = rc / sigma_p if sigma_p > 0 else np.zeros_like(rc)  # each RC_i/sigma_p = contribution %
    return float(sigma_p), rc, rc_pct


def equal_risk_parity_weights(cov: np.ndarray) -> np.ndarray:
    """
    Find weights w such that each asset contributes equally to portfolio risk.
    Minimize sum_i (RC_i - target)^2 with target = sigma_p/N, sum(w)=1, w>=0.
    """
    n = cov.shape[0]

    def objective(w):
        w = np.asarray(w).reshape(-1, 1)
        sigma_p_sq = (w.T @ cov @ w).item()
        sigma_p = np.sqrt(max(sigma_p_sq, 1e-12))
        marginal = (cov @ w).flatten()
        rc = w.flatten() * marginal / sigma_p if sigma_p > 0 else np.zeros(n)
        target = sigma_p / n
        return np.sum((rc - target) ** 2)

    # Constraints: sum(w)=1, w_i >= 0
    cons = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
    bnds = [(1e-6, 1.0) for _ in range(n)]
    x0 = np.ones(n) / n
    res = minimize(objective, x0, method="SLSQP", bounds=bnds, constraints=cons)
    if not res.success:
        # Fallback: inverse volatility weights
        vols = np.sqrt(np.diag(cov))
        inv_vol = np.where(vols > 1e-12, 1.0 / vols, 0)
        w = inv_vol / np.sum(inv_vol)
        return w
    return np.clip(res.x, 0, 1)


def backtest_weights(
    returns: pd.DataFrame,
    weights: np.ndarray,
    tickers: list[str],
    rebalance_freq: str = "M",
) -> pd.Series:
    """Compute period returns with rebalancing at rebalance_freq (e.g. 'M' for month-end)."""
    cols = [c for c in tickers if c in returns.columns]
    if len(cols) != len(tickers):
        return pd.Series(dtype=float)
    R = returns[cols].values
    w = np.asarray(weights)
    if len(w) != len(cols):
        return pd.Series(dtype=float)
    dates = returns.index
    period_ends = returns.resample("ME" if rebalance_freq == "M" else rebalance_freq).last().index
    out = []
    for i, d in enumerate(returns.index):
        # Find last rebalance date
        prev = period_ends[period_ends <= d]
        if len(prev) == 0:
            out.append(0.0)
            continue
        # Period return = w' * r_t
        idx = returns.index.get_loc(d)
        if idx >= len(R):
            out.append(0.0)
            continue
        r_t = R[idx]
        out.append(np.dot(w, r_t))
    return pd.Series(out, index=returns.index)


def stress_period_returns(
    returns: pd.DataFrame,
    weights: np.ndarray,
    tickers: list[str],
    start: str,
    end: str,
) -> float:
    """Cumulative return for a given period (start/end) with given weights."""
    cols = [c for c in tickers if c in returns.columns]
    if len(cols) != len(tickers):
        return float("nan")
    R = returns.loc[start:end][cols].values
    w = np.asarray(weights)
    if len(w) != len(cols) or len(R) == 0:
        return float("nan")
    period_ret = (1 + R @ w).prod() - 1
    return float(period_ret)


def main() -> int:
    ap = argparse.ArgumentParser(description="Risk parity portfolio analyzer (AQR-style).")
    ap.add_argument("--portfolio", type=str, help="Path to JSON with tickers and weights (e.g. .tickers or .holdings)")
    ap.add_argument("--weights", type=str, help="Inline: TICKER:weightPct,TICKER:weightPct (weights in 0-100)")
    ap.add_argument("--from", dest="from_date", type=str, default="2019-01-01", help="Start date for history")
    ap.add_argument("--to", dest="to_date", type=str, help="End date (default: today)")
    ap.add_argument("--out", type=str, help="Write JSON result here")
    ap.add_argument("--rebalance", type=str, default="M", choices=["M", "Q"], help="Rebalance frequency for backtest")
    args = ap.parse_args()

    if not args.portfolio and not args.weights:
        print("Provide --portfolio <path> or --weights TICK:wt,TICK:wt", file=sys.stderr)
        return 1

    tickers = []
    weights_raw = []

    if args.portfolio:
        p = Path(args.portfolio)
        if not p.is_absolute():
            p = WORKSPACE / p
        if not p.exists():
            print(f"Portfolio file not found: {p}", file=sys.stderr)
            return 1
        data = json.loads(p.read_text(encoding="utf-8"))
        # Accept .tickers (copycat style) or .holdings or list of {symbol/ticker, weightPct/weight}
        items = data.get("tickers") or data.get("holdings") or data if isinstance(data, list) else []
        if not items and isinstance(data, dict):
            items = [{"ticker": k, "weightPct": v} for k, v in data.items() if k not in ("totalValue", "from", "to")]
        for it in items:
            if isinstance(it, dict):
                sym = it.get("ticker") or it.get("symbol") or it.get("cusip")
                wt = it.get("weightPct") or it.get("weight")
                if sym and wt is not None:
                    tickers.append(str(sym).strip())
                    weights_raw.append(float(wt))
            else:
                continue
        if not tickers:
            print("No ticker/weight pairs found in portfolio file.", file=sys.stderr)
            return 1
        # Normalize to fractions (if weights in 0-100, convert to 0-1)
        if max(weights_raw) > 2:
            weights_raw = [x / 100.0 for x in weights_raw]
        w_sum = sum(weights_raw)
        if w_sum <= 0:
            print("Weights sum to non-positive.", file=sys.stderr)
            return 1
        current_weights = np.array([x / w_sum for x in weights_raw])
    else:
        for part in args.weights.split(","):
            part = part.strip()
            if ":" in part:
                sym, wt = part.split(":", 1)
                tickers.append(sym.strip())
                weights_raw.append(float(wt.strip()))
        if not tickers:
            print("No ticker:weight pairs in --weights.", file=sys.stderr)
            return 1
        if max(weights_raw) > 2:
            weights_raw = [x / 100.0 for x in weights_raw]
        w_sum = sum(weights_raw)
        current_weights = np.array([x / w_sum for x in weights_raw])

    to_date = args.to_date or pd.Timestamp.now().strftime("%Y-%m-%d")
    api_key = load_fmp_key()
    returns = build_returns_matrix(tickers, args.from_date, to_date, api_key)
    if returns.empty or len(returns) < 60:
        print("Insufficient return data (need at least 60 days).", file=sys.stderr)
        return 1

    # Align tickers to columns present
    cols = [c for c in tickers if c in returns.columns]
    if len(cols) < 2:
        print("Need at least 2 tickers with data for risk parity.", file=sys.stderr)
        return 1
    # Reorder weights to match cols
    idx = [tickers.index(c) for c in cols]
    w_current = current_weights[idx] / current_weights[idx].sum()

    # Annualized covariance (252 trading days)
    cov = returns[cols].cov().values * 252
    vols = np.sqrt(np.diag(cov))

    # Current risk decomposition
    sigma_p, rc, rc_pct = risk_decomposition(w_current, cov)
    risk_contribution_pct = rc_pct * 100  # as percentage

    # Risk parity weights (equal risk contribution)
    w_parity = equal_risk_parity_weights(cov)
    sigma_parity, _, _ = risk_decomposition(w_parity, cov)

    # Leverage: to match current portfolio vol with risk parity allocation, scale = sigma_p / sigma_parity
    leverage_to_match_vol = sigma_p / sigma_parity if sigma_parity > 1e-12 else 1.0

    # Backtest: current vs risk parity (monthly rebalance)
    ret_series_current = backtest_weights(returns, w_current, cols, args.rebalance)
    ret_series_parity = backtest_weights(returns, w_parity, cols, args.rebalance)
    cum_current = (1 + ret_series_current).cumprod()
    cum_parity = (1 + ret_series_parity).cumprod()
    total_ret_current = cum_current.iloc[-1] - 1 if len(cum_current) else 0
    total_ret_parity = cum_parity.iloc[-1] - 1 if len(cum_parity) else 0
    n_years = len(returns) / 252
    ann_ret_current = (1 + total_ret_current) ** (1 / n_years) - 1 if n_years > 0 else 0
    ann_ret_parity = (1 + total_ret_parity) ** (1 / n_years) - 1 if n_years > 0 else 0

    # Stress periods
    stress_2008 = stress_period_returns(returns, w_current, cols, "2008-01-01", "2008-12-31"), stress_period_returns(returns, w_parity, cols, "2008-01-01", "2008-12-31")
    stress_2020 = stress_period_returns(returns, w_current, cols, "2020-01-01", "2020-12-31"), stress_period_returns(returns, w_parity, cols, "2020-01-01", "2020-12-31")
    stress_2022 = stress_period_returns(returns, w_current, cols, "2022-01-01", "2022-12-31"), stress_period_returns(returns, w_parity, cols, "2022-01-01", "2022-12-31")

    # Correlation matrix (annualized return correlation)
    corr = returns[cols].corr()

    result = {
        "tickers": cols,
        "fromDate": args.from_date,
        "toDate": to_date,
        "currentWeights": {t: round(float(w), 6) for t, w in zip(cols, w_current)},
        "volatilityAnnualized": {t: round(float(v), 6) for t, v in zip(cols, vols)},
        "portfolioVolatilityCurrent": round(float(sigma_p), 6),
        "riskContributionPct": {t: round(float(x), 4) for t, x in zip(cols, risk_contribution_pct)},
        "correlationMatrix": {t: {c: round(corr.loc[t, c], 4) for c in cols} for t in cols},
        "riskParityWeights": {t: round(float(w), 6) for t, w in zip(cols, w_parity)},
        "portfolioVolatilityParity": round(float(sigma_parity), 6),
        "leverageToMatchVol": round(float(leverage_to_match_vol), 4),
        "backtest": {
            "totalReturnCurrent": round(float(total_ret_current), 6),
            "totalReturnParity": round(float(total_ret_parity), 6),
            "annualizedReturnCurrent": round(float(ann_ret_current), 6),
            "annualizedReturnParity": round(float(ann_ret_parity), 6),
        },
        "stressTests": {
            "2008": {"current": round(float(stress_2008[0]), 6) if not np.isnan(stress_2008[0]) else None, "parity": round(float(stress_2008[1]), 6) if not np.isnan(stress_2008[1]) else None},
            "2020": {"current": round(float(stress_2020[0]), 6) if not np.isnan(stress_2020[0]) else None, "parity": round(float(stress_2020[1]), 6) if not np.isnan(stress_2020[1]) else None},
            "2022": {"current": round(float(stress_2022[0]), 6) if not np.isnan(stress_2022[0]) else None, "parity": round(float(stress_2022[1]), 6) if not np.isnan(stress_2022[1]) else None},
        },
        "rebalanceFreq": args.rebalance,
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
