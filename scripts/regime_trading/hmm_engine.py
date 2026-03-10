"""
HMM-based regime detection for regime trading app.
Uses GaussianHMM (7 components) on returns, range, and volume volatility.
Automatically identifies Bull (highest mean return) and Bear/Crash (lowest mean return).
"""

import warnings
import numpy as np
import pandas as pd
from hmmlearn import hmm

N_COMPONENTS = 7
COVARIANCE_TYPE = "full"
N_ITER = 1000
RANDOM_STATE = 42

FEATURE_RETURNS = "Returns"
FEATURE_RANGE = "Range"
FEATURE_VOL_VOL = "Vol_Volatility"


def _add_hmm_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add Returns, Range, Vol_Volatility. Caller must dropna after."""
    out = df.copy()
    out[FEATURE_RETURNS] = out["close"].pct_change()
    out[FEATURE_RANGE] = (out["high"] - out["low"]) / out["close"].replace(0, np.nan)
    out[FEATURE_VOL_VOL] = out["volume"].pct_change()
    return out


def fit_hmm(df: pd.DataFrame) -> tuple[hmm.GaussianHMM, pd.DataFrame]:
    """
    Fit 7-state GaussianHMM on Returns, Range, Vol_Volatility.
    Returns (fitted model, df with 'Regime' and feature columns).
    """
    df = _add_hmm_features(df)
    df = df.dropna(subset=[FEATURE_RETURNS, FEATURE_RANGE, FEATURE_VOL_VOL])
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=[FEATURE_RETURNS, FEATURE_RANGE, FEATURE_VOL_VOL])

    X = df[[FEATURE_RETURNS, FEATURE_RANGE, FEATURE_VOL_VOL]].values
    model = hmm.GaussianHMM(
        n_components=N_COMPONENTS,
        covariance_type=COVARIANCE_TYPE,
        n_iter=N_ITER,
        random_state=RANDOM_STATE,
    )
    converged = True
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        model.fit(X)
        converged = not any("conver" in str(getattr(m, "message", m)).lower() for m in w)
    states = model.predict(X)
    df = df.copy()
    df["Regime"] = states
    return model, df, converged


def identify_bull_bear_states(df_with_regime: pd.DataFrame) -> tuple[int, int]:
    """
    Identify bull state (highest mean return) and bear/crash state (lowest mean return).
    Returns (bull_state_id, bear_state_id).
    """
    g = df_with_regime.groupby("Regime")[FEATURE_RETURNS].agg(["mean", "count"])
    g = g[g["count"] >= 1]
    if g.empty:
        return 0, 0
    bull_state = int(g["mean"].idxmax())
    bear_state = int(g["mean"].idxmin())
    return bull_state, bear_state


def get_regime_labels(bull_state: int, bear_state: int) -> dict[int, str]:
    """Return a mapping from regime index to display label (Bull Run / Bear-Crash / Neutral)."""
    labels = {}
    for i in range(N_COMPONENTS):
        if i == bull_state:
            labels[i] = "Bull Run"
        elif i == bear_state:
            labels[i] = "Bear/Crash"
        else:
            labels[i] = "Neutral"
    return labels
