#!/usr/bin/env python3
"""
S&P 500 Market Regime Detection using a Hidden Markov Model (HMM).
Downloads hourly data via yfinance, engineers features, fits GaussianHMM, and plots regimes.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use("Agg")  # non-interactive backend so script exits after save
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from hmmlearn import hmm

# -----------------------------------------------------------------------------
# 1. Get data: hourly S&P 500 for last 730 days
# -----------------------------------------------------------------------------
TICKER = "^GSPC"
print(f"Downloading {TICKER} hourly data (730d)...")
raw = yf.download(TICKER, period="730d", interval="1h", progress=False, auto_adjust=False)

# Flatten multi-index columns: use first level (get_level_values(0))
if isinstance(raw.columns, pd.MultiIndex):
    raw.columns = raw.columns.get_level_values(0)

# Standardize to lowercase and keep only OHLCV (avoid KeyError)
raw.columns = [c.strip().lower() for c in raw.columns]
required = ["open", "high", "low", "close", "volume"]
for col in required:
    if col not in raw.columns:
        raise KeyError(f"Missing column '{col}' after download. Columns: {list(raw.columns)}")
data = raw[required].copy()

# -----------------------------------------------------------------------------
# 2. Feature engineering
# -----------------------------------------------------------------------------
data["Returns"] = data["close"].pct_change()
data["Range"] = (data["high"] - data["low"]) / data["close"].replace(0, np.nan)
data["Vol_Change"] = data["volume"].pct_change()

# Clean: drop NaNs, replace inf/-inf with NaN, drop again
data = data.dropna(subset=["Returns", "Range", "Vol_Change"])
data = data.replace([np.inf, -np.inf], np.nan)
data = data.dropna(subset=["Returns", "Range", "Vol_Change"])

# -----------------------------------------------------------------------------
# 3. Train HMM
# -----------------------------------------------------------------------------
X = data[["Returns", "Range", "Vol_Change"]].values
model = hmm.GaussianHMM(
    n_components=7,
    covariance_type="full",
    n_iter=1000,
    random_state=42,
)
model.fit(X)
states = model.predict(X)
data["State"] = states

# -----------------------------------------------------------------------------
# 4. Summary table: one row per state (mean Return, Volatility, Count)
# -----------------------------------------------------------------------------
summary = (
    data.groupby("State")["Returns"]
    .agg([("Mean_Return", "mean"), ("Volatility", "std"), ("Count", "count")])
    .sort_values("Mean_Return", ascending=False)
)
summary = summary.reset_index()
print("\n--- Regime summary (sorted by Mean_Return descending) ---")
print(summary.to_string(index=False))

# -----------------------------------------------------------------------------
# 5. Plot: last 500 hours — close price + scatter colored by state
# -----------------------------------------------------------------------------
plot_df = data.tail(500).copy()
fig, ax = plt.subplots(figsize=(12, 6))

# Line: S&P 500 close
ax.plot(range(len(plot_df)), plot_df["close"].values, color="gray", alpha=0.7, linewidth=1, label="Close")

# Scatter: close colored by state (7 regimes)
cmap = matplotlib.colormaps.get_cmap("tab10").resampled(7)
ax.scatter(
    range(len(plot_df)),
    plot_df["close"].values,
    c=plot_df["State"].values,
    cmap=cmap,
    s=12,
    alpha=0.8,
    vmin=0,
    vmax=6,
)
ax.set_xlabel("Hours (last 500)")
ax.set_ylabel("S&P 500 Close")
ax.set_title("S&P 500 — Last 500 Hours by Detected Regime (7-state HMM)")
# Legend: one entry per regime (colormap maps 0..6 to colors)
legend_elements = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor=cmap(i / 6.0), markersize=8, label=f"Regime {i}")
    for i in range(7)
]
ax.legend(handles=legend_elements, loc="upper left", ncol=2, fontsize=8)
ax.grid(True, alpha=0.3)
plt.tight_layout()
out_path = Path(__file__).resolve().parent.parent / "outputs" / "sp500_regime_hmm.png"
out_path.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(out_path, dpi=150)
print(f"\nPlot saved to {out_path}")
