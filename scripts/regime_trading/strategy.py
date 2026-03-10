"""
Strategy logic: 8 confirmations, 7/8 voting, cooldown 48h, exit on bear/crash.
"""

import pandas as pd
import numpy as np
from .indicators import add_all_indicators

COOLDOWN_HOURS = 48
VOTES_REQUIRED = 7
TOTAL_VOTES = 8

RSI_MAX = 90
MOMENTUM_MIN_PCT = 0.01
VOLATILITY_MAX_PCT = 0.06
ADX_MIN = 25

DEFAULT_CONFIG = {
    "rsi_max": RSI_MAX,
    "momentum_min_pct": MOMENTUM_MIN_PCT,
    "volatility_max_pct": VOLATILITY_MAX_PCT,
    "adx_min": ADX_MIN,
    "votes_required": VOTES_REQUIRED,
    "cooldown_hours": COOLDOWN_HOURS,
}


def _get_config(config: dict | None) -> dict:
    return {**DEFAULT_CONFIG, **(config or {})}


def _check_conditions(row: pd.Series, config: dict | None = None) -> list[bool]:
    """
    Return a list of 8 booleans: RSI<max, Momentum>min%, Volatility<max%, Volume>SMA20,
    ADX>min, Price>EMA50, Price>EMA200, MACD>Signal.
    """
    cfg = _get_config(config)
    c1 = row["RSI"] < cfg["rsi_max"] if pd.notna(row["RSI"]) else False
    c2 = row["Momentum"] > cfg["momentum_min_pct"] if pd.notna(row["Momentum"]) else False
    c3 = row["Volatility"] < cfg["volatility_max_pct"] if pd.notna(row["Volatility"]) else False
    c4 = row["Volume_Above_SMA"] if pd.notna(row.get("Volume_Above_SMA")) else False
    c5 = row["ADX"] > cfg["adx_min"] if pd.notna(row["ADX"]) else False
    c6 = row["close"] > row["EMA50"] if pd.notna(row["EMA50"]) else False
    c7 = row["close"] > row["EMA200"] if pd.notna(row["EMA200"]) else False
    c8 = row["MACD"] > row["MACD_Signal"] if pd.notna(row["MACD"]) and pd.notna(row["MACD_Signal"]) else False
    return [c1, c2, c3, c4, c5, c6, c7, c8]


def votes_for_entry(row: pd.Series, config: dict | None = None) -> int:
    """Number of conditions met (0..8)."""
    return sum(_check_conditions(row, config))


def get_condition_breakdown(row: pd.Series, config: dict | None = None) -> list[dict]:
    """
    Return list of dicts with keys: name, value, threshold, passed.
    Used for dashboard visibility (why LONG / FLAT).
    """
    cfg = _get_config(config)
    checks = _check_conditions(row, config)
    return [
        {"name": f"RSI < {cfg['rsi_max']}", "value": row.get("RSI"), "threshold": str(cfg["rsi_max"]), "passed": checks[0]},
        {"name": f"Momentum > {cfg['momentum_min_pct']*100:.0f}%", "value": row.get("Momentum"), "threshold": f"{cfg['momentum_min_pct']*100:.0f}%", "passed": checks[1]},
        {"name": f"Volatility < {cfg['volatility_max_pct']*100:.0f}%", "value": row.get("Volatility"), "threshold": f"{cfg['volatility_max_pct']*100:.0f}%", "passed": checks[2]},
        {"name": "Volume > SMA(20)", "value": bool(row.get("Volume_Above_SMA")), "threshold": "True", "passed": checks[3]},
        {"name": f"ADX > {cfg['adx_min']}", "value": row.get("ADX"), "threshold": str(cfg["adx_min"]), "passed": checks[4]},
        {"name": "Price > EMA50", "value": row.get("close"), "threshold": f"EMA50={row.get('EMA50')}", "passed": checks[5]},
        {"name": "Price > EMA200", "value": row.get("close"), "threshold": f"EMA200={row.get('EMA200')}", "passed": checks[6]},
        {"name": "MACD > Signal", "value": row.get("MACD"), "threshold": f"Signal={row.get('MACD_Signal')}", "passed": checks[7]},
    ]


def can_enter(row: pd.Series, bull_state: int, config: dict | None = None) -> bool:
    """True if regime is bull and at least votes_required of 8 conditions met."""
    if row["Regime"] != bull_state:
        return False
    cfg = _get_config(config)
    return votes_for_entry(row, config) >= cfg["votes_required"]


def should_exit(row: pd.Series, bear_state: int) -> bool:
    """True if regime flipped to bear/crash -> close position immediately."""
    return row["Regime"] == bear_state


def prepare_strategy_df(
    df: pd.DataFrame,
    returns_col: str = "Returns",
) -> pd.DataFrame:
    """
    Add indicators and condition columns. Drops rows where indicators are NaN.
    Expects df with OHLCV and 'Regime', and a returns column for volatility.
    """
    if returns_col not in df.columns:
        ret = df["close"].pct_change()
    else:
        ret = df[returns_col]
    out = add_all_indicators(df, ret)
    out["Votes"] = out.apply(votes_for_entry, axis=1)
    return out
