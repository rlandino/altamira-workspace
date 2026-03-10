#!/usr/bin/env python3
"""
Index performance chart for the daily briefing.
Fetches recent daily EOD for an index (default ^GSPC), plots close price, saves to outputs/briefing-chart-{DATE}.png.
Uses FMP stable historical-price-eod/light with fallback to yfinance.
"""

import argparse
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import requests

WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS = WORKSPACE / "outputs"
FMP_STABLE = "https://financialmodelingprep.com/stable"
FMP_KEY = "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz"
DEFAULT_SYMBOL = "^GSPC"
TRADING_DAYS_BACK = 10


def fetch_fmp_eod(symbol: str, from_date: str, to_date: str) -> pd.DataFrame:
    """Fetch historical EOD from FMP stable (historical-price-eod/light). Returns DataFrame with date, close."""
    url = f"{FMP_STABLE}/historical-price-eod/light"
    params = {"symbol": symbol, "from": from_date, "to": to_date, "apikey": FMP_KEY}
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list) and len(data) > 0:
            df = pd.DataFrame(data)
            if "date" in df.columns and "close" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df = df.sort_values("date").reset_index(drop=True)
                return df
            # some APIs use "adjClose" or "price"
            for col in ("adjClose", "close", "price"):
                if col in df.columns:
                    df["close"] = df[col]
                    if "date" in df.columns:
                        df["date"] = pd.to_datetime(df["date"])
                        df = df.sort_values("date").reset_index(drop=True)
                        return df
    except Exception as e:
        print(f"[briefing_chart] FMP fetch failed: {e}", flush=True)
    return pd.DataFrame()


def fetch_yfinance_eod(symbol: str, from_date: str, to_date: str) -> pd.DataFrame:
    """Fallback: fetch daily EOD via yfinance."""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=from_date, end=to_date, interval="1d", auto_adjust=True)
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.reset_index()
        df = df.rename(columns={"Date": "date", "Close": "close"})
        df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
        df = df[["date", "close"]].sort_values("date").reset_index(drop=True)
        return df
    except Exception as e:
        print(f"[briefing_chart] yfinance fetch failed: {e}", flush=True)
    return pd.DataFrame()


def main() -> None:
    parser = argparse.ArgumentParser(description="Index performance chart for daily briefing")
    parser.add_argument("--date", default=None, help="Date YYYY-MM-DD (default: today)")
    parser.add_argument("--symbol", default=DEFAULT_SYMBOL, help="Index symbol (default: ^GSPC)")
    parser.add_argument("--out-dir", default=None, help="Output directory (default: workspace outputs/)")
    args = parser.parse_args()

    to_date = args.date or datetime.now().strftime("%Y-%m-%d")
    from_dt = datetime.strptime(to_date, "%Y-%m-%d") - timedelta(days=14)
    from_date = from_dt.strftime("%Y-%m-%d")

    df = fetch_fmp_eod(args.symbol, from_date, to_date)
    if df.empty:
        df = fetch_yfinance_eod(args.symbol, from_date, to_date)
    if df.empty:
        print("[briefing_chart] No data; cannot generate chart.", flush=True)
        raise SystemExit(1)

    # Limit to last N trading days for a clean "recent performance" view
    df = df.tail(TRADING_DAYS_BACK).reset_index(drop=True)

    out_dir = Path(args.out_dir) if args.out_dir else OUTPUTS
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"briefing-chart-{to_date}.png"

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["date"], df["close"], color="steelblue", linewidth=2, label="Close")
    ax.set_xlabel("Date")
    ax.set_ylabel("Close")
    title = "S&P 500 Index – Recent Performance" if args.symbol == "^GSPC" else f"{args.symbol} – Recent Performance"
    ax.set_title(title)
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"[briefing_chart] Saved {out_path}", flush=True)


if __name__ == "__main__":
    main()
