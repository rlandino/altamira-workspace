#!/usr/bin/env python3
"""
Benchmark Calculator — Calculate percentile benchmarks for scoring normalization.

Calculates median/percentile values for key metrics across:
- S&P 500 (broad market benchmark)
- Sector-specific (Technology, Healthcare, Financials, etc.)

Uses FMP API to fetch data for benchmark tickers and calculate percentiles.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
import statistics

try:
    import requests
except ImportError:
    print("Install requests: pip install requests", file=sys.stderr)
    sys.exit(1)

WORKSPACE = Path(__file__).resolve().parent.parent
CACHE_DIR = WORKSPACE / "cache"
CACHE_DIR.mkdir(exist_ok=True)

FMP_API_KEY = "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz"
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"

# S&P 500 representative tickers (top 50 by market cap, diverse sectors)
SP500_REPRESENTATIVE = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B", "V", "UNH",
    "XOM", "JNJ", "JPM", "WMT", "MA", "PG", "AVGO", "HD", "CVX", "MRK",
    "ABBV", "COST", "ADBE", "PEP", "TMO", "CSCO", "NFLX", "ACN", "MCD", "COST",
    "LIN", "AMD", "DIS", "VZ", "NKE", "PM", "TXN", "CMCSA", "HON", "QCOM",
    "INTU", "AMGN", "AMAT", "LOW", "BKNG", "GE", "AXP", "SBUX", "ADP", "DE"
]

# Sector mapping (GICS sectors)
SECTORS = [
    "Technology", "Healthcare", "Financials", "Consumer Discretionary",
    "Communication Services", "Industrials", "Consumer Staples", "Energy",
    "Utilities", "Real Estate", "Materials"
]


def fetch_ticker_metrics(ticker: str) -> Optional[Dict]:
    """Fetch key metrics for a ticker from FMP API."""
    base = FMP_BASE_URL
    key = FMP_API_KEY
    
    try:
        # Fetch ratios (latest annual)
        ratios_url = f"{base}/ratios/{ticker}?period=annual&limit=1&apikey={key}"
        ratios_r = requests.get(ratios_url, timeout=10)
        if ratios_r.status_code != 200 or not ratios_r.json():
            return None
        
        ratios = ratios_r.json()[0] if ratios_r.json() else None
        if not ratios:
            return None
        
        # Fetch profile for sector
        profile_url = f"{base}/profile/{ticker}?apikey={key}"
        profile_r = requests.get(profile_url, timeout=10)
        profile = profile_r.json()[0] if profile_r.status_code == 200 and profile_r.json() else {}
        
        # Growth metrics (for sector-relative Growth score)
        revenue_growth = None
        net_income_growth = None
        growth_url = f"{base}/financial-growth/{ticker}?period=annual&limit=1&apikey={key}"
        growth_r = requests.get(growth_url, timeout=10)
        if growth_r.status_code == 200 and growth_r.json() and isinstance(growth_r.json(), list) and len(growth_r.json()) > 0:
            g = growth_r.json()[0]
            revenue_growth = g.get("revenueGrowth")
            net_income_growth = g.get("netIncomeGrowth")
            # FMP may return decimals (0.2387 = 23.87%)
            if revenue_growth is not None and -2 < revenue_growth < 2 and revenue_growth != 0:
                revenue_growth = revenue_growth * 100
            if net_income_growth is not None and -2 < net_income_growth < 2 and net_income_growth != 0:
                net_income_growth = net_income_growth * 100
        
        # Dividend yield (for sector-relative Shareholder score)
        div_yield = None
        km_url = f"{base}/key-metrics/{ticker}?period=annual&limit=1&apikey={key}"
        km_r = requests.get(km_url, timeout=10)
        if km_r.status_code == 200 and km_r.json() and isinstance(km_r.json(), list) and len(km_r.json()) > 0:
            km = km_r.json()[0]
            div_yield = km.get("dividendYield")
            if div_yield is not None and abs(div_yield) < 1:
                div_yield = div_yield * 100
        
        return {
            "pe": ratios.get("priceEarningsRatio"),
            "pb": ratios.get("priceToBookRatio"),
            "ps": ratios.get("priceToSalesRatio"),
            "roe": ratios.get("returnOnEquity"),
            "roa": ratios.get("returnOnAssets"),
            "roic": ratios.get("returnOnInvestedCapital"),
            "netMargin": ratios.get("netProfitMargin") or ratios.get("netIncomeMargin"),
            "debtEquity": ratios.get("debtEquityRatio"),
            "currentRatio": ratios.get("currentRatio"),
            "interestCoverage": ratios.get("interestCoverage"),
            "revenueGrowth": revenue_growth,
            "netIncomeGrowth": net_income_growth,
            "dividendYield": div_yield,
            "sector": profile.get("sector"),
            "industry": profile.get("industry"),
        }
    except Exception as e:
        print(f"Error fetching {ticker}: {e}", file=sys.stderr)
        return None


def calculate_percentiles(values: List[float], percentiles: List[int] = [10, 25, 50, 75, 90]) -> Dict[int, float]:
    """Calculate percentiles from a list of values."""
    if not values:
        return {}
    
    # Filter out None values
    valid_values = [v for v in values if v is not None and not (isinstance(v, float) and (v == float('inf') or v == float('-inf')))]
    if not valid_values:
        return {}
    
    valid_values.sort()
    n = len(valid_values)
    
    result = {}
    for p in percentiles:
        if n == 1:
            result[p] = valid_values[0]
        else:
            index = (p / 100) * (n - 1)
            lower = int(index)
            upper = min(lower + 1, n - 1)
            weight = index - lower
            result[p] = valid_values[lower] * (1 - weight) + valid_values[upper] * weight
    
    return result


def calculate_benchmarks(tickers: List[str] = None, sector: Optional[str] = None) -> Dict:
    """Calculate benchmark percentiles for key metrics."""
    if tickers is None:
        tickers = SP500_REPRESENTATIVE
    
    print(f"Calculating benchmarks for {len(tickers)} tickers...", file=sys.stderr)
    
    metrics = {
        "pe": [],
        "pb": [],
        "ps": [],
        "roe": [],
        "roa": [],
        "roic": [],
        "netMargin": [],
        "debtEquity": [],
        "currentRatio": [],
        "interestCoverage": [],
        "revenueGrowth": [],
        "netIncomeGrowth": [],
        "dividendYield": [],
    }
    
    sector_counts = {}
    
    # Fetch metrics for all tickers
    for i, ticker in enumerate(tickers):
        print(f"  Fetching {ticker} ({i+1}/{len(tickers)})...", file=sys.stderr, end="\r")
        data = fetch_ticker_metrics(ticker)
        if not data:
            continue
        
        # Filter by sector if specified
        if sector and data.get("sector") != sector:
            continue
        
        # Track sector distribution
        ticker_sector = data.get("sector", "Unknown")
        sector_counts[ticker_sector] = sector_counts.get(ticker_sector, 0) + 1
        
        # Collect metrics
        for metric in metrics.keys():
            value = data.get(metric)
            if value is not None:
                metrics[metric].append(value)
    
    print(f"\nCollected data from {sum(sector_counts.values())} tickers", file=sys.stderr)
    print(f"Sector distribution: {sector_counts}", file=sys.stderr)
    
    # Calculate percentiles for each metric
    benchmarks = {}
    for metric, values in metrics.items():
        if values:
            percentiles = calculate_percentiles(values)
            benchmarks[metric] = {
                "median": percentiles.get(50, statistics.median(values) if values else None),
                "p10": percentiles.get(10),
                "p25": percentiles.get(25),
                "p75": percentiles.get(75),
                "p90": percentiles.get(90),
                "min": min(values) if values else None,
                "max": max(values) if values else None,
                "count": len(values),
            }
        else:
            benchmarks[metric] = None
    
    return benchmarks


def save_benchmarks(benchmarks: Dict, filename: str = "benchmarks.json"):
    """Save benchmarks to cache file."""
    cache_file = CACHE_DIR / filename
    with open(cache_file, "w") as f:
        json.dump(benchmarks, f, indent=2)
    print(f"Benchmarks saved to {cache_file}", file=sys.stderr)


def load_benchmarks(filename: str = "benchmarks.json") -> Optional[Dict]:
    """Load benchmarks from cache file."""
    cache_file = CACHE_DIR / filename
    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)
    return None


def main():
    """Calculate and save S&P 500 and sector benchmarks."""
    import argparse
    
    ap = argparse.ArgumentParser(description="Calculate benchmark percentiles for scoring normalization")
    ap.add_argument("--sector", help="Calculate benchmarks for specific sector")
    ap.add_argument("--tickers", nargs="+", help="Custom ticker list")
    ap.add_argument("--force", action="store_true", help="Recalculate even if cache exists")
    args = ap.parse_args()
    
    tickers = args.tickers or SP500_REPRESENTATIVE
    sector = args.sector
    
    # Determine cache filename
    cache_filename = f"benchmarks-{sector.lower().replace(' ', '-')}.json" if sector else "benchmarks-sp500.json"
    
    # Load from cache if exists and not forcing
    if not args.force:
        cached = load_benchmarks(cache_filename)
        if cached:
            print(f"Loaded benchmarks from cache: {cache_filename}", file=sys.stderr)
            print(json.dumps(cached, indent=2))
            return
    
    # Calculate benchmarks
    benchmarks = calculate_benchmarks(tickers=tickers, sector=sector)
    
    # Save to cache
    save_benchmarks(benchmarks, cache_filename)
    
    # Print results
    print(json.dumps(benchmarks, indent=2))


if __name__ == "__main__":
    main()
