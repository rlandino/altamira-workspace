"""
Technical indicators for regime trading strategy.
RSI, Momentum, Volatility, Volume vs SMA, ADX, EMA 50/200, MACD/Signal.
"""

import numpy as np
import pandas as pd

RSI_PERIOD = 14
MOMENTUM_PERIOD = 10
VOLATILITY_WINDOW = 20
VOLUME_SMA_PERIOD = 20
ADX_PERIOD = 14
EMA_FAST = 50
EMA_SLOW = 200
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9


def rsi(close: pd.Series, period: int = RSI_PERIOD) -> pd.Series:
    """RSI (Relative Strength Index)."""
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def momentum_pct(close: pd.Series, period: int = MOMENTUM_PERIOD) -> pd.Series:
    """Momentum as (close - close_n) / close_n (percentage)."""
    lag = close.shift(period)
    return (close - lag) / lag.replace(0, np.nan)


def volatility_pct(returns: pd.Series, window: int = VOLATILITY_WINDOW) -> pd.Series:
    """Rolling std of returns as percentage (e.g. 0.01 = 1%)."""
    return returns.rolling(window).std()


def volume_above_sma(volume: pd.Series, period: int = VOLUME_SMA_PERIOD) -> pd.Series:
    """Boolean: volume > SMA(volume, period)."""
    sma = volume.rolling(period).mean()
    return volume > sma


def _wilder_smooth(series: pd.Series, period: int) -> pd.Series:
    """Wilder's smoothing: prev_smooth * (period-1) + current, then / period."""
    return series.ewm(alpha=1 / period, adjust=False).mean()


def adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = ADX_PERIOD) -> pd.Series:
    """Average Directional Index (ADX)."""
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)
    atr = _wilder_smooth(tr, period)
    plus_di = 100 * _wilder_smooth(plus_dm, period) / atr.replace(0, np.nan)
    minus_di = 100 * _wilder_smooth(minus_dm, period) / atr.replace(0, np.nan)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return _wilder_smooth(dx, period)


def ema(close: pd.Series, span: int) -> pd.Series:
    """Exponential moving average."""
    return close.ewm(span=span, adjust=False).mean()


def macd_and_signal(close: pd.Series) -> tuple[pd.Series, pd.Series]:
    """MACD line and Signal line. Returns (macd_line, signal_line)."""
    ema_fast = close.ewm(span=MACD_FAST, adjust=False).mean()
    ema_slow = close.ewm(span=MACD_SLOW, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=MACD_SIGNAL, adjust=False).mean()
    return macd_line, signal_line


def add_all_indicators(df: pd.DataFrame, returns: pd.Series) -> pd.DataFrame:
    """
    Add RSI, Momentum, Volatility, Volume_Above_SMA, ADX, EMA50, EMA200, MACD, Signal.
    Expects df with open, high, low, close, volume; returns is close.pct_change().
    """
    out = df.copy()
    out["RSI"] = rsi(out["close"], RSI_PERIOD)
    out["Momentum"] = momentum_pct(out["close"], MOMENTUM_PERIOD)
    out["Volatility"] = volatility_pct(returns, VOLATILITY_WINDOW)
    out["Volume_Above_SMA"] = volume_above_sma(out["volume"], VOLUME_SMA_PERIOD)
    out["ADX"] = adx(out["high"], out["low"], out["close"], ADX_PERIOD)
    out["EMA50"] = ema(out["close"], EMA_FAST)
    out["EMA200"] = ema(out["close"], EMA_SLOW)
    macd_line, signal_line = macd_and_signal(out["close"])
    out["MACD"] = macd_line
    out["MACD_Signal"] = signal_line
    return out
