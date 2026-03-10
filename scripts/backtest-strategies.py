#!/usr/bin/env python3
"""
Altamira Capital — Multi-Strategy Backtesting Framework
========================================================
Backtests 3 core strategies from the investment thesis:
  1. Options Premium Selling (CSP simulation via Black-Scholes)
  2. Equity Momentum Long (50-day MA crossover)
  3. Portfolio Hedging (SPY protective puts)

Uses FMP API for historical price data.
Outputs a markdown report to outputs/backtest-results-{date}.md

Usage:
  python scripts/backtest-strategies.py
  python scripts/backtest-strategies.py --years 3
  python scripts/backtest-strategies.py --tickers AAPL,MSFT,GOOGL
"""

import argparse
import json
import math
import os
import sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import requests
from scipy.stats import norm

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

FMP_API_KEY = "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz"
FMP_BASE = "https://financialmodelingprep.com/api/v3"

DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "AVGO", "COST", "V", "MA", "META", "NVDA"]
BENCHMARK = "SPY"

# Options strategy parameters (from investment thesis)
CSP_DELTA_TARGET = 0.25       # Target delta for short puts
CSP_DTE_TARGET = 30           # Days to expiration
CSP_PROFIT_TARGET = 0.50      # Close at 50% of max profit
CSP_STOP_LOSS = 2.00          # Close at 200% of credit received
CSP_IV_PREMIUM = 1.15         # IV typically ~15% above realized vol
RISK_FREE_RATE = 0.045        # ~4.5% risk-free rate

# Equity strategy parameters
MOMENTUM_MA_PERIOD = 50       # 50-day moving average
MOMENTUM_REBALANCE_DAYS = 20  # Rebalance monthly

# Hedging parameters
HEDGE_PUT_DELTA = 0.20        # OTM protective put delta
HEDGE_COST_BUDGET = 0.0025    # 0.25% of portfolio per month
HEDGE_DTE = 30

# Portfolio parameters
INITIAL_CAPITAL = 100_000
MAX_POSITION_PCT = 0.05       # 5% max per position
OPTIONS_ALLOCATION = 0.40     # 40% to options strategies
EQUITY_ALLOCATION = 0.40      # 40% to equity long
CASH_ALLOCATION = 0.20        # 20% cash reserve


# ─────────────────────────────────────────────
# Data Fetching
# ─────────────────────────────────────────────

def fetch_historical_prices(ticker, from_date, to_date):
    """Fetch daily historical prices from FMP API."""
    url = f"{FMP_BASE}/historical-price-full/{ticker}"
    params = {"from": from_date, "to": to_date, "apikey": FMP_API_KEY}
    try:
        resp = requests.get(url, params=params, timeout=15)
        data = resp.json()
        if "historical" in data and data["historical"]:
            df = pd.DataFrame(data["historical"])
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date").reset_index(drop=True)
            return df
    except Exception as e:
        print(f"  [WARN] Failed to fetch {ticker}: {e}")
    return pd.DataFrame()


def fetch_treasury_rate():
    """Fetch current treasury yield for risk-free rate."""
    try:
        url = f"{FMP_BASE}/treasury"
        params = {"apikey": FMP_API_KEY}
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data:
            return data[0].get("year10", RISK_FREE_RATE) / 100
    except:
        pass
    return RISK_FREE_RATE


# ─────────────────────────────────────────────
# Black-Scholes for Options Estimation
# ─────────────────────────────────────────────

def black_scholes_put(S, K, T, r, sigma):
    """Calculate Black-Scholes put price."""
    if T <= 0 or sigma <= 0:
        return max(K - S, 0)
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    put_price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return max(put_price, 0)


def bs_put_delta(S, K, T, r, sigma):
    """Calculate Black-Scholes put delta."""
    if T <= 0 or sigma <= 0:
        return -1.0 if S < K else 0.0
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    return norm.cdf(d1) - 1


def find_strike_for_delta(S, T, r, sigma, target_delta=-0.25):
    """Find strike price that gives the target put delta."""
    low, high = S * 0.70, S * 1.0
    for _ in range(50):
        mid = (low + high) / 2
        d = bs_put_delta(S, mid, T, r, sigma)
        if d < target_delta:
            low = mid
        else:
            high = mid
    return round(mid, 2)


def realized_volatility(prices, window=30):
    """Calculate rolling realized volatility (annualized)."""
    log_returns = np.log(prices / prices.shift(1))
    return log_returns.rolling(window).std() * np.sqrt(252)


# ─────────────────────────────────────────────
# Strategy 1: Options Premium Selling (CSP)
# ─────────────────────────────────────────────

def backtest_csp(prices_dict, benchmark_prices, capital_alloc):
    """
    Simulate Cash-Secured Put selling across the ticker universe.

    Monthly cycle: sell put at target delta, manage to 50% profit or 200% stop.
    Uses historical prices + estimated IV (realized vol * premium) to price puts.
    """
    results = {
        "trades": [],
        "monthly_returns": [],
        "equity_curve": [capital_alloc],
    }

    # Get all dates from benchmark
    dates = benchmark_prices["date"].values
    closes = benchmark_prices["close"].values

    portfolio_value = capital_alloc
    trade_count = 0
    win_count = 0
    total_pnl = 0

    for ticker, df in prices_dict.items():
        if df.empty or len(df) < 60:
            continue

        df = df.set_index("date")
        rvol = realized_volatility(df["close"], window=30)

        # Simulate monthly CSP cycles (every 30 calendar days)
        trade_dates = df.index[30::CSP_DTE_TARGET + 5]  # Start after vol warmup, ~monthly with buffer

        for entry_date in trade_dates:
            if entry_date not in df.index:
                continue

            entry_idx = df.index.get_loc(entry_date)
            if entry_idx + CSP_DTE_TARGET >= len(df):
                break

            S = df.iloc[entry_idx]["close"]
            vol = rvol.iloc[entry_idx] if not pd.isna(rvol.iloc[entry_idx]) else 0.25
            iv = vol * CSP_IV_PREMIUM  # IV premium over realized
            T = CSP_DTE_TARGET / 365

            # Find strike at target delta
            K = find_strike_for_delta(S, T, RISK_FREE_RATE, iv, target_delta=-CSP_DELTA_TARGET)
            premium = black_scholes_put(S, K, T, RISK_FREE_RATE, iv)

            if premium < 0.10:  # Skip if premium too small
                continue

            # Position size: 1 contract per $50K allocated to this ticker
            contracts = max(1, int(capital_alloc / len(prices_dict) / (K * 100)))
            credit = premium * 100 * contracts
            max_loss = (K * 100 * contracts) - credit  # If stock goes to 0

            # Simulate daily P&L through the trade
            exit_pnl = None
            exit_date = None
            exit_reason = "expiration"

            for day_offset in range(1, CSP_DTE_TARGET + 1):
                if entry_idx + day_offset >= len(df):
                    break

                current_price = df.iloc[entry_idx + day_offset]["close"]
                remaining_dte = (CSP_DTE_TARGET - day_offset) / 365

                # Estimate current put value
                current_vol = vol * CSP_IV_PREMIUM
                current_put_value = black_scholes_put(current_price, K, remaining_dte, RISK_FREE_RATE, current_vol)

                unrealized_pnl = (premium - current_put_value) * 100 * contracts

                # Check profit target (50% of credit)
                if unrealized_pnl >= credit * CSP_PROFIT_TARGET:
                    exit_pnl = unrealized_pnl
                    exit_date = df.index[entry_idx + day_offset]
                    exit_reason = "profit_target"
                    break

                # Check stop loss (200% of credit)
                if unrealized_pnl <= -credit * CSP_STOP_LOSS:
                    exit_pnl = unrealized_pnl
                    exit_date = df.index[entry_idx + day_offset]
                    exit_reason = "stop_loss"
                    break

            # If no exit triggered, settle at expiration
            if exit_pnl is None:
                exp_price = df.iloc[min(entry_idx + CSP_DTE_TARGET, len(df) - 1)]["close"]
                exit_date = df.index[min(entry_idx + CSP_DTE_TARGET, len(df) - 1)]
                if exp_price >= K:
                    exit_pnl = credit  # Full premium collected
                    exit_reason = "expired_otm"
                else:
                    # Assignment: loss = (K - exp_price) * 100 * contracts - credit
                    exit_pnl = -((K - exp_price) * 100 * contracts) + credit
                    exit_reason = "assigned"

            trade_count += 1
            if exit_pnl > 0:
                win_count += 1
            total_pnl += exit_pnl
            portfolio_value += exit_pnl

            results["trades"].append({
                "ticker": ticker,
                "entry_date": str(entry_date)[:10],
                "exit_date": str(exit_date)[:10],
                "stock_price": round(S, 2),
                "strike": K,
                "premium": round(premium, 2),
                "contracts": contracts,
                "credit": round(credit, 2),
                "pnl": round(exit_pnl, 2),
                "exit_reason": exit_reason,
            })
            results["equity_curve"].append(portfolio_value)

    # Calculate metrics
    win_rate = (win_count / trade_count * 100) if trade_count > 0 else 0
    total_return = (portfolio_value - capital_alloc) / capital_alloc * 100

    # Calculate Sharpe from trade-level returns (not equity curve)
    if results["trades"]:
        trade_returns = [t["pnl"] / max(capital_alloc / len(prices_dict), 1) for t in results["trades"]]
        avg_trade_ret = np.mean(trade_returns)
        std_trade_ret = np.std(trade_returns) if len(trade_returns) > 1 else 0.01
        # Annualize: ~12 trade cycles per year per ticker
        trades_per_year = max(len(results["trades"]) / max(1, len(prices_dict)) * 12, 1)
        annual_ret = avg_trade_ret * trades_per_year
        annual_std = std_trade_ret * np.sqrt(trades_per_year)
        sharpe = (annual_ret - RISK_FREE_RATE) / annual_std if annual_std > 0 else 0

        # Max drawdown from equity curve
        curve = np.array(results["equity_curve"])
        peak = np.maximum.accumulate(curve)
        drawdown = (curve - peak) / peak
        max_dd = np.min(drawdown) * 100
    else:
        sharpe = 0
        max_dd = 0

    results["summary"] = {
        "total_trades": trade_count,
        "win_rate": round(win_rate, 1),
        "total_pnl": round(total_pnl, 2),
        "total_return_pct": round(total_return, 2),
        "sharpe_ratio": round(sharpe, 2),
        "max_drawdown_pct": round(max_dd, 2),
        "final_value": round(portfolio_value, 2),
        "avg_pnl_per_trade": round(total_pnl / trade_count, 2) if trade_count > 0 else 0,
    }

    return results


# ─────────────────────────────────────────────
# Strategy 2: Equity Momentum Long
# ─────────────────────────────────────────────

def backtest_momentum(prices_dict, benchmark_df, capital_alloc):
    """
    Simulate equity momentum strategy:
    - Long when price > 50-day MA
    - Flat (cash) when price < 50-day MA
    - Equal-weight across universe, rebalance monthly
    """
    # Build a combined price matrix
    price_frames = {}
    for ticker, df in prices_dict.items():
        if df.empty:
            continue
        price_frames[ticker] = df.set_index("date")["close"].rename(ticker)

    if not price_frames:
        return {"summary": {"total_return_pct": 0, "sharpe_ratio": 0, "max_drawdown_pct": 0}}

    prices = pd.DataFrame(price_frames)
    prices = prices.dropna(how="all").ffill()

    # Calculate 50-day MA
    ma = prices.rolling(MOMENTUM_MA_PERIOD).mean()

    # Signal: 1 if price > MA, 0 if below
    signals = (prices > ma).astype(float)
    signals = signals.iloc[MOMENTUM_MA_PERIOD:]  # Skip warmup
    prices = prices.iloc[MOMENTUM_MA_PERIOD:]

    # Rebalance monthly — hold signal from rebalance date
    rebalance_mask = np.zeros(len(signals), dtype=bool)
    rebalance_mask[0] = True
    for i in range(MOMENTUM_REBALANCE_DAYS, len(signals), MOMENTUM_REBALANCE_DAYS):
        rebalance_mask[i] = True

    # Forward-fill signals from rebalance dates
    held_signals = signals.copy()
    last_signal = signals.iloc[0]
    for i in range(len(held_signals)):
        if rebalance_mask[i]:
            last_signal = signals.iloc[i]
        held_signals.iloc[i] = last_signal

    # Calculate daily returns
    daily_returns = prices.pct_change()

    # Portfolio returns: equal-weight among active (signal=1) tickers
    n_active = held_signals.sum(axis=1).replace(0, 1)  # Avoid division by 0
    portfolio_returns = (daily_returns * held_signals).sum(axis=1) / n_active

    # Cash portion earns risk-free rate when not invested
    cash_tickers = (held_signals == 0).sum(axis=1) / len(prices.columns)
    portfolio_returns += cash_tickers * (RISK_FREE_RATE / 252)

    # Build equity curve
    equity = capital_alloc * (1 + portfolio_returns).cumprod()

    # Benchmark
    bench_df = benchmark_df.set_index("date")["close"]
    bench_df = bench_df.reindex(equity.index).ffill()
    if len(bench_df) > 0:
        bench_return = (bench_df.iloc[-1] / bench_df.iloc[0] - 1) * 100
    else:
        bench_return = 0

    # Metrics
    total_return = (equity.iloc[-1] / capital_alloc - 1) * 100
    trading_days = len(equity)
    years = trading_days / 252
    annual_return = ((equity.iloc[-1] / capital_alloc) ** (1 / max(years, 0.01)) - 1) * 100

    daily_ret = portfolio_returns.dropna()
    sharpe = (daily_ret.mean() * 252 - RISK_FREE_RATE) / (daily_ret.std() * np.sqrt(252)) if daily_ret.std() > 0 else 0

    # Max drawdown
    peak = equity.cummax()
    drawdown = (equity - peak) / peak
    max_dd = drawdown.min() * 100

    # Win rate (monthly)
    monthly_returns = portfolio_returns.resample("ME").sum()
    win_months = (monthly_returns > 0).sum()
    total_months = len(monthly_returns)

    # Exposure (% of time invested)
    avg_exposure = held_signals.mean().mean() * 100

    return {
        "summary": {
            "total_return_pct": round(total_return, 2),
            "annualized_return_pct": round(annual_return, 2),
            "benchmark_return_pct": round(bench_return, 2),
            "excess_return_pct": round(total_return - bench_return, 2),
            "sharpe_ratio": round(sharpe, 2),
            "max_drawdown_pct": round(max_dd, 2),
            "win_months": win_months,
            "total_months": total_months,
            "win_rate_monthly": round(win_months / max(total_months, 1) * 100, 1),
            "avg_exposure_pct": round(avg_exposure, 1),
            "final_value": round(equity.iloc[-1], 2),
            "trading_days": trading_days,
        },
        "equity_curve": equity,
        "benchmark_curve": bench_df,
    }


# ─────────────────────────────────────────────
# Strategy 3: Portfolio Hedging (Protective Puts)
# ─────────────────────────────────────────────

def backtest_hedging(benchmark_df, capital_alloc):
    """
    Simulate the impact of monthly protective puts on SPY.

    Compare: unhedged buy-and-hold vs. hedged (buy-and-hold + monthly OTM puts).
    Quantifies the cost of protection vs. drawdown reduction.
    """
    df = benchmark_df.set_index("date")
    if len(df) < 60:
        return {"summary": {}}

    rvol = realized_volatility(df["close"], window=30)

    # Unhedged: simple buy-and-hold
    unhedged_returns = df["close"].pct_change()
    unhedged_equity = capital_alloc * (1 + unhedged_returns).cumprod()

    # Hedged: buy-and-hold + monthly protective put
    hedged_equity_values = [capital_alloc]
    portfolio_value = capital_alloc

    monthly_indices = list(range(30, len(df), HEDGE_DTE))

    for i in range(1, len(df)):
        daily_return = unhedged_returns.iloc[i] if not pd.isna(unhedged_returns.iloc[i]) else 0

        # Apply market return
        portfolio_value *= (1 + daily_return)

        # Monthly put purchase
        if i in monthly_indices:
            S = df["close"].iloc[i]
            vol = rvol.iloc[i] if not pd.isna(rvol.iloc[i]) else 0.20
            iv = vol * CSP_IV_PREMIUM
            T = HEDGE_DTE / 365

            # Find OTM put at target delta
            K = find_strike_for_delta(S, T, RISK_FREE_RATE, iv, target_delta=-HEDGE_PUT_DELTA)
            put_cost = black_scholes_put(S, K, T, RISK_FREE_RATE, iv)

            # Cost as % of portfolio
            hedge_cost = put_cost / S * portfolio_value
            portfolio_value -= hedge_cost

            # Check if put pays off at month end
            end_idx = min(i + HEDGE_DTE, len(df) - 1)
            end_price = df["close"].iloc[end_idx]

            if end_price < K:
                payout = (K - end_price) / S * portfolio_value
                portfolio_value += payout

        hedged_equity_values.append(portfolio_value)

    hedged_equity = pd.Series(hedged_equity_values[:len(df)], index=df.index[:len(hedged_equity_values)])

    # Metrics for both
    def calc_metrics(equity_series, label):
        total_ret = (equity_series.iloc[-1] / equity_series.iloc[0] - 1) * 100
        years = len(equity_series) / 252
        annual_ret = ((equity_series.iloc[-1] / equity_series.iloc[0]) ** (1 / max(years, 0.01)) - 1) * 100
        daily_ret = equity_series.pct_change().dropna()
        sharpe = (daily_ret.mean() * 252 - RISK_FREE_RATE) / (daily_ret.std() * np.sqrt(252)) if daily_ret.std() > 0 else 0
        peak = equity_series.cummax()
        dd = ((equity_series - peak) / peak).min() * 100
        return {
            "label": label,
            "total_return_pct": round(total_ret, 2),
            "annualized_return_pct": round(annual_ret, 2),
            "sharpe_ratio": round(sharpe, 2),
            "max_drawdown_pct": round(dd, 2),
            "final_value": round(equity_series.iloc[-1], 2),
        }

    unhedged_metrics = calc_metrics(unhedged_equity.dropna(), "Unhedged (Buy & Hold)")
    hedged_metrics = calc_metrics(hedged_equity.dropna(), "Hedged (Buy & Hold + Puts)")

    return {
        "unhedged": unhedged_metrics,
        "hedged": hedged_metrics,
        "drawdown_reduction": round(hedged_metrics["max_drawdown_pct"] - unhedged_metrics["max_drawdown_pct"], 2),
        "return_cost": round(unhedged_metrics["total_return_pct"] - hedged_metrics["total_return_pct"], 2),
    }


# ─────────────────────────────────────────────
# Report Generation
# ─────────────────────────────────────────────

def generate_report(csp_results, momentum_results, hedging_results, tickers, years, output_path):
    """Generate markdown backtest report."""
    today = datetime.now().strftime("%Y-%m-%d")

    csp = csp_results["summary"]
    mom = momentum_results["summary"]

    # Top CSP trades
    trades_sorted = sorted(csp_results.get("trades", []), key=lambda t: t["pnl"], reverse=True)
    top_wins = trades_sorted[:5]
    top_losses = trades_sorted[-5:] if len(trades_sorted) > 5 else []

    # Exit reason breakdown
    reasons = {}
    for t in csp_results.get("trades", []):
        r = t["exit_reason"]
        reasons[r] = reasons.get(r, 0) + 1

    report = f"""# Altamira Capital — Multi-Strategy Backtest Results

**Date:** {today}
**Backtest Period:** {years} years (ending {today})
**Universe:** {', '.join(tickers)}
**Benchmark:** SPY
**Initial Capital:** ${INITIAL_CAPITAL:,.0f}

---

## Executive Summary

| Strategy | Allocation | Return | Sharpe | Max Drawdown | Status |
|----------|-----------|--------|--------|-------------|--------|
| Options Premium Selling (CSP) | {OPTIONS_ALLOCATION*100:.0f}% (${INITIAL_CAPITAL*OPTIONS_ALLOCATION:,.0f}) | {csp['total_return_pct']:.1f}% | {csp['sharpe_ratio']:.2f} | {csp['max_drawdown_pct']:.1f}% | {'PASS' if csp['sharpe_ratio'] > 1.0 else 'REVIEW'} |
| Equity Momentum Long | {EQUITY_ALLOCATION*100:.0f}% (${INITIAL_CAPITAL*EQUITY_ALLOCATION:,.0f}) | {mom['total_return_pct']:.1f}% | {mom['sharpe_ratio']:.2f} | {mom['max_drawdown_pct']:.1f}% | {'PASS' if mom['sharpe_ratio'] > 0.5 else 'REVIEW'} |
| SPY Hedging Overlay | Cost center | See below | — | — | {'PASS' if hedging_results.get('drawdown_reduction', 0) < 0 else 'REVIEW'} |

**Combined portfolio estimate** (blended {OPTIONS_ALLOCATION*100:.0f}/{EQUITY_ALLOCATION*100:.0f}/{CASH_ALLOCATION*100:.0f} options/equity/cash):
- Weighted return: ~{csp['total_return_pct'] * OPTIONS_ALLOCATION + mom['total_return_pct'] * EQUITY_ALLOCATION + RISK_FREE_RATE * 100 * CASH_ALLOCATION * years:.1f}%
- Target vs actual Sharpe: {max(csp['sharpe_ratio'], mom['sharpe_ratio']):.2f} (target: >1.5)

---

## Strategy 1: Options Premium Selling (CSP)

### Parameters

| Parameter | Value |
|-----------|-------|
| Target Delta | {CSP_DELTA_TARGET} |
| Target DTE | {CSP_DTE_TARGET} days |
| Profit Target | {CSP_PROFIT_TARGET*100:.0f}% of credit |
| Stop Loss | {CSP_STOP_LOSS*100:.0f}% of credit |
| IV Estimation | Realized vol x {CSP_IV_PREMIUM} |
| Position Sizing | Equal allocation across universe |

### Results

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total Trades | {csp['total_trades']} | — | — |
| Win Rate | {csp['win_rate']:.1f}% | >65% | {'PASS' if csp['win_rate'] > 65 else 'REVIEW'} |
| Total P&L | ${csp['total_pnl']:,.2f} | Positive | {'PASS' if csp['total_pnl'] > 0 else 'FAIL'} |
| Total Return | {csp['total_return_pct']:.2f}% | 12-18% annual | — |
| Avg P&L per Trade | ${csp['avg_pnl_per_trade']:,.2f} | Positive | {'PASS' if csp['avg_pnl_per_trade'] > 0 else 'REVIEW'} |
| Sharpe Ratio | {csp['sharpe_ratio']:.2f} | >1.5 | {'PASS' if csp['sharpe_ratio'] > 1.5 else 'REVIEW'} |
| Max Drawdown | {csp['max_drawdown_pct']:.2f}% | >-15% | {'PASS' if csp['max_drawdown_pct'] > -15 else 'FAIL'} |
| Final Value | ${csp['final_value']:,.2f} | — | — |

### Exit Reason Breakdown

| Reason | Count | Pct |
|--------|-------|-----|
"""

    total_trades = max(csp["total_trades"], 1)
    for reason, count in sorted(reasons.items(), key=lambda x: -x[1]):
        report += f"| {reason} | {count} | {count/total_trades*100:.1f}% |\n"

    report += f"""
### Top 5 Winning Trades

| Ticker | Entry | Strike | Premium | P&L | Exit Reason |
|--------|-------|--------|---------|-----|-------------|
"""
    for t in top_wins[:5]:
        report += f"| {t['ticker']} | {t['entry_date']} | ${t['strike']:.2f} | ${t['premium']:.2f} | ${t['pnl']:,.2f} | {t['exit_reason']} |\n"

    if top_losses:
        report += f"""
### Top 5 Losing Trades

| Ticker | Entry | Strike | Premium | P&L | Exit Reason |
|--------|-------|--------|---------|-----|-------------|
"""
        for t in reversed(top_losses[-5:]):
            report += f"| {t['ticker']} | {t['entry_date']} | ${t['strike']:.2f} | ${t['premium']:.2f} | ${t['pnl']:,.2f} | {t['exit_reason']} |\n"

    report += f"""
---

## Strategy 2: Equity Momentum Long (50-Day MA)

### Parameters

| Parameter | Value |
|-----------|-------|
| Moving Average | {MOMENTUM_MA_PERIOD}-day SMA |
| Signal | Long when price > MA, flat when below |
| Rebalance | Every {MOMENTUM_REBALANCE_DAYS} trading days |
| Weighting | Equal weight among active signals |

### Results

| Metric | Value | Benchmark (SPY) | Excess |
|--------|-------|-----------------|--------|
| Total Return | {mom['total_return_pct']:.2f}% | {mom['benchmark_return_pct']:.2f}% | {mom['excess_return_pct']:.2f}% |
| Annualized Return | {mom['annualized_return_pct']:.2f}% | — | — |
| Sharpe Ratio | {mom['sharpe_ratio']:.2f} | — | — |
| Max Drawdown | {mom['max_drawdown_pct']:.2f}% | — | — |
| Win Rate (Monthly) | {mom['win_rate_monthly']:.1f}% ({mom['win_months']}/{mom['total_months']}) | — | — |
| Average Exposure | {mom['avg_exposure_pct']:.1f}% | 100% | — |
| Final Value | ${mom['final_value']:,.2f} | — | — |

### Interpretation

The momentum strategy {'outperformed' if mom['excess_return_pct'] > 0 else 'underperformed'} SPY by {abs(mom['excess_return_pct']):.1f}% with {'lower' if mom['max_drawdown_pct'] > -15 else 'higher'} maximum drawdown ({mom['max_drawdown_pct']:.1f}% vs benchmark). Average exposure of {mom['avg_exposure_pct']:.1f}% means the strategy was cash ~{100-mom['avg_exposure_pct']:.0f}% of the time, providing natural downside protection.

---

## Strategy 3: Portfolio Hedging (Protective Puts on SPY)

### Parameters

| Parameter | Value |
|-----------|-------|
| Hedge Instrument | SPY OTM puts |
| Put Delta | {HEDGE_PUT_DELTA} (protective) |
| Frequency | Monthly purchase |
| DTE | {HEDGE_DTE} days |

### Results

| Metric | Unhedged | Hedged | Difference |
|--------|----------|--------|------------|
| Total Return | {hedging_results.get('unhedged', {}).get('total_return_pct', 0):.2f}% | {hedging_results.get('hedged', {}).get('total_return_pct', 0):.2f}% | {hedging_results.get('return_cost', 0):.2f}% cost |
| Annualized Return | {hedging_results.get('unhedged', {}).get('annualized_return_pct', 0):.2f}% | {hedging_results.get('hedged', {}).get('annualized_return_pct', 0):.2f}% | — |
| Sharpe Ratio | {hedging_results.get('unhedged', {}).get('sharpe_ratio', 0):.2f} | {hedging_results.get('hedged', {}).get('sharpe_ratio', 0):.2f} | — |
| Max Drawdown | {hedging_results.get('unhedged', {}).get('max_drawdown_pct', 0):.2f}% | {hedging_results.get('hedged', {}).get('max_drawdown_pct', 0):.2f}% | {hedging_results.get('drawdown_reduction', 0):.2f}% improvement |

### Interpretation

Protective puts {'reduced' if hedging_results.get('drawdown_reduction', 0) < 0 else 'did not significantly reduce'} maximum drawdown by {abs(hedging_results.get('drawdown_reduction', 0)):.1f} percentage points at a cost of {abs(hedging_results.get('return_cost', 0)):.1f}% in total returns. {'This is a favorable tradeoff — the drawdown reduction justifies the cost.' if hedging_results.get('drawdown_reduction', 0) < -2 else 'Consider using hedging selectively (only when VIX < 15) to reduce cost.'}

---

## Key Takeaways

1. **Options premium selling** generated a {csp['win_rate']:.0f}% win rate with {'positive' if csp['total_pnl'] > 0 else 'negative'} total P&L. {'The strategy validates the thesis that selling puts at 0.20-0.30 delta captures the IV premium reliably.' if csp['win_rate'] > 60 else 'The win rate is below target — consider tightening delta targets or improving exit rules.'}

2. **Equity momentum** {'beat' if mom['excess_return_pct'] > 0 else 'trailed'} the benchmark while being invested only {mom['avg_exposure_pct']:.0f}% of the time. {'Risk-adjusted returns are compelling.' if mom['sharpe_ratio'] > 0.5 else 'Returns do not adequately compensate for reduced exposure.'}

3. **Hedging** costs ~{abs(hedging_results.get('return_cost', 0)):.1f}% in returns over the period. {'Worth it during high-vol regimes.' if hedging_results.get('drawdown_reduction', 0) < -2 else 'Consider conditional hedging (VIX-based) to optimize cost.'}

---

## Recommendations for Paper Trading

Based on backtest results:

1. **Start with CSP selling on 3-5 tickers** — Begin with the most liquid names (SPY, AAPL, MSFT) at conservative delta (0.20) and expand
2. **Use 50-day MA as a directional filter** — Only sell puts when price is above 50-day MA for higher win rates
3. **Hedge selectively** — Buy protective puts only when VIX < 18 (cheaper premiums, more likely to benefit from vol expansion)
4. **Track all metrics** — Log every paper trade with the parameters above to validate against backtest

---

## Methodology Notes

- **Options pricing:** Black-Scholes with estimated IV = realized volatility x {CSP_IV_PREMIUM}. This is an approximation — live IV data from Massive.com/OPRA will be more accurate.
- **Transaction costs:** Not included. Assume $0.65/contract for options, which would reduce returns by ~$1-3 per trade.
- **Slippage:** Not included. Estimated 1-2% of premium on entry/exit for liquid names.
- **Data source:** FMP API historical daily close prices. Intraday dynamics not captured.
- **Assignment handling:** Simplified — actual assignment involves share delivery and potential subsequent covered call selling.

---

*Report generated by Altamira Capital backtesting framework. Backtest results do not guarantee future performance.*
"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    return report


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Altamira Capital Multi-Strategy Backtest")
    parser.add_argument("--years", type=int, default=2, help="Number of years to backtest (default: 2)")
    parser.add_argument("--tickers", type=str, default=None, help="Comma-separated tickers (default: full universe)")
    parser.add_argument("--output", type=str, default=None, help="Output path (default: outputs/backtest-results-{date}.md)")
    args = parser.parse_args()

    tickers = args.tickers.split(",") if args.tickers else DEFAULT_TICKERS
    years = args.years
    today = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=years * 365)).strftime("%Y-%m-%d")
    output_path = args.output or f"outputs/backtest-results-{today}.md"

    print("=" * 60)
    print("Altamira Capital — Multi-Strategy Backtest")
    print("=" * 60)
    print(f"\nPeriod: {from_date} to {today} ({years} years)")
    print(f"Universe: {', '.join(tickers)}")
    print(f"Benchmark: {BENCHMARK}")
    print(f"Capital: ${INITIAL_CAPITAL:,.0f}")

    # ── Fetch Data ──
    print(f"\n[1/5] Fetching historical data...")
    prices_dict = {}
    for ticker in tickers:
        print(f"  Fetching {ticker}...", end=" ")
        df = fetch_historical_prices(ticker, from_date, today)
        if not df.empty:
            prices_dict[ticker] = df
            print(f"{len(df)} days")
        else:
            print("FAILED")

    print(f"  Fetching {BENCHMARK} (benchmark)...", end=" ")
    benchmark_df = fetch_historical_prices(BENCHMARK, from_date, today)
    print(f"{len(benchmark_df)} days" if not benchmark_df.empty else "FAILED")

    if not prices_dict or benchmark_df.empty:
        print("\n[ERROR] Insufficient data. Check API key and network.")
        sys.exit(1)

    # ── Backtest Strategies ──
    print(f"\n[2/5] Backtesting Strategy 1: Options Premium Selling (CSP)...")
    csp_capital = INITIAL_CAPITAL * OPTIONS_ALLOCATION
    csp_results = backtest_csp(prices_dict, benchmark_df, csp_capital)
    csp = csp_results["summary"]
    print(f"  Trades: {csp['total_trades']} | Win rate: {csp['win_rate']}% | P&L: ${csp['total_pnl']:,.2f} | Sharpe: {csp['sharpe_ratio']}")

    print(f"\n[3/5] Backtesting Strategy 2: Equity Momentum Long...")
    mom_capital = INITIAL_CAPITAL * EQUITY_ALLOCATION
    momentum_results = backtest_momentum(prices_dict, benchmark_df, mom_capital)
    mom = momentum_results["summary"]
    print(f"  Return: {mom['total_return_pct']}% | Sharpe: {mom['sharpe_ratio']} | Max DD: {mom['max_drawdown_pct']}%")

    print(f"\n[4/5] Backtesting Strategy 3: Portfolio Hedging...")
    hedge_capital = INITIAL_CAPITAL  # Hedging overlays the full portfolio
    hedging_results = backtest_hedging(benchmark_df, hedge_capital)
    print(f"  Unhedged: {hedging_results.get('unhedged', {}).get('total_return_pct', 0)}% | Hedged: {hedging_results.get('hedged', {}).get('total_return_pct', 0)}%")
    print(f"  Drawdown reduction: {hedging_results.get('drawdown_reduction', 0)}%")

    # ── Generate Report ──
    print(f"\n[5/5] Generating report...")
    report = generate_report(csp_results, momentum_results, hedging_results, tickers, years, output_path)
    print(f"  Report written to: {output_path}")

    print("\n" + "=" * 60)
    print("BACKTEST COMPLETE")
    print("=" * 60)
    print(f"\nStrategy 1 (CSP):      {csp['total_return_pct']:+.1f}% return | {csp['sharpe_ratio']:.2f} Sharpe | {csp['win_rate']:.0f}% win rate")
    print(f"Strategy 2 (Momentum): {mom['total_return_pct']:+.1f}% return | {mom['sharpe_ratio']:.2f} Sharpe | {mom['max_drawdown_pct']:.1f}% max DD")
    print(f"Strategy 3 (Hedging):  {hedging_results.get('return_cost', 0):.1f}% cost | {hedging_results.get('drawdown_reduction', 0):.1f}% DD improvement")


if __name__ == "__main__":
    main()
