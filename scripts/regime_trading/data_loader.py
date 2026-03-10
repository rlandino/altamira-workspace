"""
Data loader for regime-based trading app.
Fetches OHLCV via yfinance with configurable ticker, period, and interval.
"""

import pandas as pd
import numpy as np
import yfinance as yf

TICKER = "SPY"
PERIOD = "730d"
INTERVAL = "1h"

PERIOD_OPTIONS = {"90d": "90 days", "180d": "180 days", "365d": "1 year", "730d": "2 years"}
TICKER_OPTIONS = ["SPY", "QQQ", "IWM", "^GSPC"]


def load_ohlcv(ticker: str = TICKER, period: str = PERIOD, interval: str = INTERVAL) -> pd.DataFrame:
    """
    Download OHLCV for the given ticker, period, and interval.
    Returns a DataFrame with columns: open, high, low, close, volume.
    """
    raw = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=False)
    if raw is None or raw.empty:
        raise ValueError(f"No data returned for {ticker} (period={period}, interval={interval})")

    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)

    raw.columns = [str(c).strip().lower() for c in raw.columns]
    required = ["open", "high", "low", "close", "volume"]
    for col in required:
        if col not in raw.columns:
            raise KeyError(f"Missing column '{col}' after download. Columns: {list(raw.columns)}")

    return raw[required].copy()


def load_spy_hourly() -> pd.DataFrame:
    """Convenience: SPY hourly for last 730 days."""
    return load_ohlcv(TICKER, PERIOD, INTERVAL)


def prepare_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """Return a clean copy with numeric index (integer position) for consistent indexing."""
    out = df.dropna(how="all").copy()
    return out
