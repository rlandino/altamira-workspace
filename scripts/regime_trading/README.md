# Regime-Based Trading App

Professional regime-based trading dashboard using HMM regime detection, 8-condition voting, and Streamlit.

## Architecture

- **data_loader.py** — Fetches SPY hourly data (last 730 days) via yfinance.
- **hmm_engine.py** — 7-state GaussianHMM on returns, range (high-low)/close, and volume volatility; auto-identifies Bull (highest mean return) and Bear/Crash (lowest mean return).
- **indicators.py** — RSI, Momentum, Volatility, Volume vs SMA(20), ADX, EMA 50/200, MACD/Signal.
- **strategy.py** — 8 confirmations; enter only if regime is Bull and ≥7/8 conditions met; 48h cooldown after exit; exit immediately if regime flips to Bear/Crash.
- **backtester.py** — Simulation with $10k starting capital; logs every trade; computes total return, alpha vs buy & hold, win rate, max drawdown.
- **app.py** — Streamlit dashboard: current signal (cached), detected regime, Plotly candlestick with regime background (green=bull, red=bear), metrics, trade log.

## Run the dashboard

From the **scripts** directory (so `regime_trading` is a package):

```bash
cd X:\Claude\altamira-workspace\scripts
set PYTHONPATH=.
streamlit run regime_trading/app.py
```

Or from workspace root:

```bash
cd X:\Claude\altamira-workspace
set PYTHONPATH=scripts
streamlit run scripts/regime_trading/app.py
```

## Dependencies

```bash
pip install -r scripts/regime_trading/requirements.txt
```

(Includes: yfinance, hmmlearn, matplotlib, pandas, numpy, scikit-learn, streamlit, plotly.)
