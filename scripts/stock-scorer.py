#!/usr/bin/env python3
"""
Stock Scoring System — Calculate Quality, Growth, Value, Health, Shareholder scores
and composite grade for tickers using FMP API data with Massive.com fallback.

Data Sources:
    Primary: FMP API (Financial Modeling Prep) — comprehensive fundamental data
    Fallback: Massive.com API — market/quote data when FMP missing

Usage:
    python scripts/stock-scorer.py MSFT                    # Score single ticker
    python scripts/stock-scorer.py --portfolio              # Score all portfolio holdings
    python scripts/stock-scorer.py MSFT AAPL GOOGL         # Score multiple tickers
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import requests
except ImportError:
    print("Install requests: pip install requests", file=sys.stderr)
    sys.exit(1)

WORKSPACE = Path(__file__).resolve().parent.parent
OUTPUTS = WORKSPACE / "outputs"
CONTEXT = WORKSPACE / "context"
CACHE_DIR = WORKSPACE / "cache"
CACHE_DIR.mkdir(exist_ok=True)

FMP_API_KEY = "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz"
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"

MASSIVE_API_KEY = "kEnhZTIYm_UZZSfpSPuYQgsW_kG0vPHp"
MASSIVE_BASE_URL = "https://api.massive.com/v1"

# Scoring weights
QUALITY_WEIGHTS = {
    "roe": 0.25,
    "roa": 0.20,
    "margin": 0.20,
    "roic": 0.20,
    "debtCapital": 0.15,
}

GROWTH_WEIGHTS = {
    "revenue": 0.30,
    "earnings": 0.30,
    "fcf": 0.25,
    "fcfPerShare": 0.15,
}

VALUE_WEIGHTS = {
    "pe": 0.25,
    "pb": 0.20,
    "ps": 0.15,
    "fcf": 0.15,
    "marginOfSafety": 0.25,
}

HEALTH_WEIGHTS = {
    "debt": 0.30,
    "liquidity": 0.35,
    "coverage": 0.35,
}

SHAREHOLDER_WEIGHTS = {
    "divYield": 0.30,
    "divGrowth": 0.25,
    "buybackYield": 0.25,
    "debtPaydown": 0.20,
}

# Grade thresholds - Lowered by 5 points to make grades more achievable
# A+ represents exceptional companies (top 5%), not perfection
GRADE_THRESHOLDS = [
    (85, "A+"),  # Was 90
    (80, "A"),   # Was 85
    (75, "A-"),  # Was 80
    (70, "B+"),  # Was 75
    (65, "B"),   # Was 70
    (60, "B-"),  # Was 65
    (55, "C+"),  # Was 60
    (50, "C"),   # Was 55
    (45, "C-"),  # Was 50
    (40, "D+"),  # Was 45
    (35, "D"),   # Was 40
]

STRENGTH_THRESHOLD = 70
WEAKNESS_THRESHOLD = 50

# Map company-growth letter grade (A/B/C/D/F) to numeric score so get_grade(score) returns same letter
COMPANY_GROWTH_GRADE_TO_SCORE = {
    "A": 82,   # get_grade(82) = "A"
    "B": 67,   # get_grade(67) = "B"
    "C": 57,   # get_grade(57) = "C"
    "D": 37,   # get_grade(37) = "D"
    "F": 30,   # get_grade(30) = "F"
}


def _growth_score_from_company_growth(ticker: str) -> Optional[float]:
    """
    Get growth score (0-100) from company-growth logic so /stockscore and /company-growth
    show the same growth grade. Returns None if company_growth_metrics unavailable or fails.
    """
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from company_growth_metrics import fetch_and_compute
    except Exception:
        return None
    try:
        cg = fetch_and_compute(ticker.upper())
    except Exception:
        return None
    grade = cg.get("suggested_grade")
    if grade not in COMPANY_GROWTH_GRADE_TO_SCORE:
        return None
    return float(COMPANY_GROWTH_GRADE_TO_SCORE[grade])


def _format_revenue_value(val) -> str:
    """Format revenue as $XB or $XM for readability."""
    if val is None:
        return "N/A"
    try:
        v = float(val)
    except (TypeError, ValueError):
        return str(val)
    if v >= 1e9:
        return f"${v / 1e9:.1f}B"
    if v >= 1e6:
        return f"${v / 1e6:.0f}M"
    return f"${v:,.0f}"


def _generate_company_growth_subsection(ticker: str) -> str:
    """Generate Company Growth (3yr CAGR / YoY) block from company_growth_metrics. Returns empty string on failure."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from company_growth_metrics import fetch_and_compute
    except Exception:
        return ""
    try:
        cg = fetch_and_compute(ticker)
    except Exception:
        return ""
    core = cg.get("core_four") or {}
    if not core:
        return ""
    rev = core.get("revenue") or {}
    eps = core.get("eps") or {}
    fcf = core.get("fcf_margin") or {}
    roic = core.get("roic") or {}
    report = "\n#### Company Growth (3yr CAGR / YoY)\n\n"
    report += "| Metric | 3yr CAGR % | Latest YoY | Latest value |\n"
    report += "|--------|------------|------------|-------------|\n"
    rev_yoy_s = (f"{rev.get('latest_yoy_pct'):+.1f}%" if rev.get('latest_yoy_pct') is not None else "N/A")
    report += f"| Revenue | {rev.get('3yr_cagr_pct') or 'N/A'} | {rev_yoy_s} | {_format_revenue_value(rev.get('latest_value'))} |\n"
    eps_yoy = eps.get("latest_yoy_pct")
    eps_yoy_s = (f"{eps_yoy:+.1f}%" if eps_yoy is not None else "N/A")
    eps_val_s = (f"{eps.get('latest_value'):.2f}" if eps.get('latest_value') is not None else "N/A")
    report += f"| EPS (GAAP) | {eps.get('3yr_cagr_pct') or 'N/A'} | {eps_yoy_s} | {eps_val_s} |\n"
    fcf_yoy = fcf.get("latest_yoy_pp")
    fcf_yoy_s = (f"{fcf_yoy:+.1f} pp" if fcf_yoy is not None else "N/A")
    fcf_val_s = (f"{fcf.get('latest_value_pct'):.1f}%" if fcf.get('latest_value_pct') is not None else "N/A")
    report += f"| FCF margin | {fcf.get('3yr_cagr_pct') or 'N/A'} | {fcf_yoy_s} | {fcf_val_s} |\n"
    roic_yoy = roic.get("latest_yoy_pct")
    roic_yoy_s = (f"{roic_yoy:+.1f}%" if roic_yoy is not None else "N/A")
    roic_val_s = (f"{roic.get('latest_value_pct'):.1f}%" if roic.get('latest_value_pct') is not None else "N/A")
    report += f"| ROIC | {roic.get('3yr_cagr_pct') or 'N/A'} | {roic_yoy_s} | {roic_val_s} |\n"
    grade = cg.get("suggested_grade")
    if grade:
        report += f"\n**Growth grade (core four):** {grade}\n"
    rule40 = cg.get("rule_of_40")
    if rule40:
        report += f"- **Rule of 40:** {rule40.get('score')} — {rule40.get('tier', '')}\n"
    traj = cg.get("revenue_trajectory")
    if traj:
        report += f"- **Revenue trajectory:** {traj}\n"
    return report


def _generate_growth_metrics_section(data: dict, ticker: str = "") -> str:
    """Generate Growth Metrics section for stock report. Includes company-growth (3yr CAGR / YoY) when ticker provided."""
    from datetime import datetime
    report = "\n### Growth Metrics\n"
    growth_data = data.get("growth") or []
    cashflow_data = data.get("cashflow") or []
    km_data = data.get("keyMetrics") or []
    
    rev_growth = None
    if len(growth_data) >= 2:
        rev_growth = growth_data[0].get("revenueGrowth")
        if rev_growth is None and growth_data[0].get("revenue") and growth_data[1].get("revenue") and growth_data[1]["revenue"] != 0:
            rev_growth = (growth_data[0]["revenue"] - growth_data[1]["revenue"]) / abs(growth_data[1]["revenue"]) * 100
        elif rev_growth is not None and abs(rev_growth) < 2:
            rev_growth = rev_growth * 100
    report += f"- **Revenue Growth (YoY)**: {f'{rev_growth:+.1f}%' if rev_growth is not None else 'N/A'}\n"
    
    earn_growth = None
    if len(growth_data) >= 2:
        earn_growth = growth_data[0].get("netIncomeGrowth")
        if earn_growth is None and growth_data[0].get("netIncome") is not None and growth_data[1].get("netIncome") and growth_data[1]["netIncome"] != 0:
            earn_growth = (growth_data[0]["netIncome"] - growth_data[1]["netIncome"]) / abs(growth_data[1]["netIncome"]) * 100
        elif earn_growth is not None and abs(earn_growth) < 2:
            earn_growth = earn_growth * 100
    report += f"- **Earnings Growth (YoY)**: {f'{earn_growth:+.1f}%' if earn_growth is not None else 'N/A'}\n"
    
    fcf_growth = None
    if len(cashflow_data) >= 2:
        fcf0 = cashflow_data[0].get("freeCashFlow") or (cashflow_data[0].get("operatingCashFlow") or 0) - abs(cashflow_data[0].get("capitalExpenditure") or 0)
        fcf1 = cashflow_data[1].get("freeCashFlow") or (cashflow_data[1].get("operatingCashFlow") or 0) - abs(cashflow_data[1].get("capitalExpenditure") or 0)
        if fcf1 and fcf1 != 0:
            fcf_growth = (fcf0 - fcf1) / abs(fcf1) * 100
    report += f"- **FCF Growth (YoY)**: {f'{fcf_growth:+.1f}%' if fcf_growth is not None else 'N/A'}\n"
    
    fcfps_growth = None
    if len(km_data) >= 2 and km_data[0].get("freeCashFlowPerShare") is not None and km_data[1].get("freeCashFlowPerShare") and km_data[1]["freeCashFlowPerShare"] != 0:
        fcfps_growth = (km_data[0]["freeCashFlowPerShare"] - km_data[1]["freeCashFlowPerShare"]) / abs(km_data[1]["freeCashFlowPerShare"]) * 100
    report += f"- **FCF Per Share Growth (YoY)**: {f'{fcfps_growth:+.1f}%' if fcfps_growth is not None else 'N/A'}\n"
    if ticker:
        report += _generate_company_growth_subsection(ticker)
    return report


def _generate_margin_of_safety_section(data: dict, ratios: list, is_growth_fn) -> str:
    """Generate Margin of Safety lines for stock report."""
    report = ""
    pe_current = ratios[0].get("priceEarningsRatio") if ratios and len(ratios) > 0 else None
    is_growth = is_growth_fn(data)
    fair_pe = 35 if is_growth else 18
    mos = ((fair_pe - pe_current) / fair_pe) * 100 if pe_current and pe_current > 0 else None
    if pe_current and pe_current > 0:
        report += f"- **P/E (current) | Fair P/E**: {pe_current:.1f} | {fair_pe}\n"
    else:
        report += f"- **Fair P/E (benchmark)**: {fair_pe}\n"
    report += f"- **Margin of Safety**: {f'{mos:+.1f}%' if mos is not None else 'N/A'}\n"
    return report


def _generate_shareholder_metrics_section(data: dict) -> str:
    """Generate Shareholder Metrics section for stock report."""
    from datetime import datetime
    report = "\n### Shareholder Metrics\n"
    quote_data = data.get("quote")
    dividends_data = data.get("dividends") or []
    balance_data = data.get("balance") or []
    cashflow_data = data.get("cashflow") or []
    km_data = data.get("keyMetrics") or []
    
    div_yield = None
    if quote_data and isinstance(quote_data, list) and len(quote_data) > 0:
        div_yield = quote_data[0].get("dividendYield")
    if div_yield is None and km_data and len(km_data) > 0:
        div_yield = km_data[0].get("dividendYield")
    if div_yield is not None and div_yield != 0 and abs(div_yield) < 1:
        div_yield = div_yield * 100
    report += f"- **Dividend Yield**: {f'{div_yield:.2f}%' if div_yield is not None and div_yield > 0 else 'N/A'}\n"
    
    div_growth = None
    if len(dividends_data) >= 2:
        cy = datetime.now().year
        d0 = sum(d.get("adjDividend", 0) or d.get("dividend", 0) for d in dividends_data if d.get("date", "")[:4] == str(cy - 1))
        d1 = sum(d.get("adjDividend", 0) or d.get("dividend", 0) for d in dividends_data if d.get("date", "")[:4] == str(cy - 2))
        if d1 and d1 != 0:
            div_growth = (d0 - d1) / abs(d1) * 100
    report += f"- **Dividend Growth (YoY)**: {f'{div_growth:+.1f}%' if div_growth is not None else 'N/A'}\n"
    
    buyback_yield = None
    if len(cashflow_data) >= 1 and quote_data and isinstance(quote_data, list) and len(quote_data) > 0:
        repurchases = abs(cashflow_data[0].get("commonStockRepurchased", 0) or 0)
        market_cap = quote_data[0].get("marketCap") or quote_data[0].get("marketCapitalization", 0)
        if market_cap and market_cap > 0:
            buyback_yield = (repurchases / market_cap) * 100
    report += f"- **Buyback Yield**: {f'{buyback_yield:.2f}%' if buyback_yield is not None and buyback_yield > 0 else 'N/A'}\n"
    
    debt_paydown = None
    if len(balance_data) >= 2:
        debt0 = balance_data[0].get("totalDebt", 0) or 0
        debt1 = balance_data[1].get("totalDebt", 0) or 0
        if debt1 and debt1 != 0:
            debt_paydown = (debt1 - debt0) / abs(debt1) * 100
    report += f"- **Debt Paydown (YoY)**: {f'{debt_paydown:+.1f}%' if debt_paydown is not None else 'N/A'}\n"
    return report


def normalize_score(value: float, min_val: float, max_val: float, invert: bool = False) -> float:
    """Normalize a value to 0-100 scale. If invert=True, lower values score higher."""
    if value is None or min_val is None or max_val is None:
        return 50.0  # Default to middle if data missing
    if max_val == min_val:
        return 50.0
    normalized = ((value - min_val) / (max_val - min_val)) * 100
    if invert:
        normalized = 100 - normalized
    return max(0, min(100, normalized))


def ensure_growth_percentage(value: Optional[float]) -> Optional[float]:
    """
    Convert FMP growth from decimal to percentage when applicable.
    FMP returns e.g. 0.2387 for 23.87%; values with |x| < 2 (excluding 0) are treated as decimals.
    """
    if value is None:
        return None
    if value == 0:
        return 0.0
    if -2 < value < 2:
        return value * 100
    return value


def normalize_score_percentile(value: float, benchmark_data: Dict, metric: str, invert: bool = False) -> float:
    """
    Normalize a value using percentile-based approach relative to benchmarks.
    
    Args:
        value: The metric value to normalize
        benchmark_data: Dictionary with percentile data (p10, p25, median/p50, p75, p90, min, max)
        metric: Metric name (for error messages)
        invert: If True, lower values score higher (e.g., P/E, P/B)
    
    Returns:
        Normalized score 0-100, or 50.0 if benchmark data unavailable
    """
    if value is None or benchmark_data is None:
        return 50.0
    
    # Extract percentiles
    p10 = benchmark_data.get("p10")
    p25 = benchmark_data.get("p25")
    median = benchmark_data.get("median") or benchmark_data.get("p50")
    p75 = benchmark_data.get("p75")
    p90 = benchmark_data.get("p90")
    min_val = benchmark_data.get("min")
    max_val = benchmark_data.get("max")
    
    if median is None:
        # Fallback to min/max if median unavailable
        if min_val is None or max_val is None:
            return 50.0
        return normalize_score(value, min_val, max_val, invert)
    
    # Calculate percentile rank
    # Use linear interpolation between percentiles
    if value <= p10 if p10 else value <= min_val:
        percentile_rank = 10.0
    elif value <= p25 if p25 else value <= median:
        # Interpolate between p10 and p25
        if p10:
            percentile_rank = 10 + ((value - p10) / (p25 - p10)) * 15 if p25 != p10 else 25
        else:
            percentile_rank = 25.0
    elif value <= median:
        # Interpolate between p25 and median
        if p25:
            percentile_rank = 25 + ((value - p25) / (median - p25)) * 25 if median != p25 else 50
        else:
            percentile_rank = 50.0
    elif value <= p75 if p75 else value <= max_val:
        # Interpolate between median and p75
        if p75:
            percentile_rank = 50 + ((value - median) / (p75 - median)) * 25 if p75 != median else 75
        else:
            percentile_rank = 75.0
    elif value <= p90 if p90 else value <= max_val:
        # Interpolate between p75 and p90
        if p75 and p90:
            percentile_rank = 75 + ((value - p75) / (p90 - p75)) * 15 if p90 != p75 else 90
        else:
            percentile_rank = 90.0
    else:
        # Above p90, use max_val for extrapolation
        if p90 and max_val:
            # Extrapolate beyond p90 (capped at 100)
            percentile_rank = min(100, 90 + ((value - p90) / (max_val - p90)) * 10 if max_val != p90 else 100)
        else:
            percentile_rank = 100.0
    
    # If invert=True, lower percentile rank means better (e.g., lower P/E is better)
    if invert:
        percentile_rank = 100 - percentile_rank
    
    return max(0, min(100, percentile_rank))


def load_benchmarks(sector: Optional[str] = None) -> Optional[Dict]:
    """Load benchmark data from cache file."""
    if sector:
        cache_file = CACHE_DIR / f"benchmarks-{sector.lower().replace(' ', '-')}.json"
    else:
        cache_file = CACHE_DIR / "benchmarks-sp500.json"
    
    if cache_file.exists():
        try:
            with open(cache_file) as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load benchmarks from {cache_file}: {e}", file=sys.stderr)
    
    # Try S&P 500 benchmarks as fallback
    if sector:
        sp500_cache = CACHE_DIR / "benchmarks-sp500.json"
        if sp500_cache.exists():
            try:
                with open(sp500_cache) as f:
                    return json.load(f)
            except Exception:
                pass
    
    return None


def fetch_massive_data(ticker: str) -> Dict:
    """
    Fetch market data from Massive.com API as fallback.
    
    Note: Massive.com is primarily an options data provider (OPRA feed), but may have
    some equity market data endpoints. This function attempts to retrieve quote/market
    data as a fallback when FMP data is unavailable.
    """
    data = {}
    base = MASSIVE_BASE_URL
    key = MASSIVE_API_KEY
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    # Massive.com endpoints (options-focused, but may have some market data)
    # Try common endpoint patterns
    endpoints = {
        "snapshot": f"{base}/snapshot/equity/{ticker}",  # Try equity snapshot
        "quote": f"{base}/market/quote/{ticker}",  # Try market quote endpoint
        "equity": f"{base}/equity/{ticker}",  # Try equity endpoint
    }
    
    for endpoint_key, url in endpoints.items():
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                result = r.json()
                if result:
                    data[endpoint_key] = result
                    break  # If we got data from one endpoint, stop trying others
        except Exception:
            # Massive.com may not have these endpoints, silently fail
            pass
    
    return data


def fetch_fmp_data(ticker: str) -> Dict:
    """Fetch all required data from FMP API for a ticker, with Massive.com fallback."""
    base = FMP_BASE_URL
    key = FMP_API_KEY
    data = {}
    
    endpoints = {
        "income": f"{base}/income-statement/{ticker}?period=annual&limit=3&apikey={key}",
        "balance": f"{base}/balance-sheet-statement/{ticker}?period=annual&limit=3&apikey={key}",
        "cashflow": f"{base}/cash-flow-statement/{ticker}?period=annual&limit=3&apikey={key}",
        "keyMetrics": f"{base}/key-metrics/{ticker}?period=annual&limit=3&apikey={key}",
        "ratios": f"{base}/ratios/{ticker}?period=annual&limit=3&apikey={key}",
        "profile": f"{base}/profile/{ticker}?apikey={key}",
        "quote": f"{base}/quote/{ticker}?apikey={key}",
        "enterprise": f"{base}/enterprise-values/{ticker}?period=annual&limit=3&apikey={key}",
        "growth": f"{base}/financial-growth/{ticker}?period=annual&limit=3&apikey={key}",
        "dividends": f"{base}/historical/stock_dividend/{ticker}?apikey={key}",
    }
    
    for endpoint_key, url in endpoints.items():
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            result = r.json()
            if isinstance(result, list) and len(result) > 0:
                data[endpoint_key] = result
            elif isinstance(result, dict):
                data[endpoint_key] = result
            else:
                data[endpoint_key] = None
        except Exception as e:
            print(f"Warning: Failed to fetch {endpoint_key} from FMP for {ticker}: {e}", file=sys.stderr)
            data[endpoint_key] = None
    
    # Extract sector from profile for percentile normalization
    if data.get("profile") and isinstance(data.get("profile"), list) and len(data.get("profile", [])) > 0:
        profile = data["profile"][0]
        data["sector"] = profile.get("sector")
        data["industry"] = profile.get("industry")
    elif data.get("profile") and isinstance(data.get("profile"), dict):
        data["sector"] = data["profile"].get("sector")
        data["industry"] = data["profile"].get("industry")
    
    # Try Massive.com as fallback for quote/market data if FMP failed
    if not data.get("quote") or (isinstance(data.get("quote"), list) and len(data.get("quote", [])) == 0):
        print(f"FMP quote missing for {ticker}, trying Massive.com fallback...", file=sys.stderr)
        massive_data = fetch_massive_data(ticker)
        if massive_data.get("quote") or massive_data.get("snapshot"):
            # Store Massive.com data separately, will be used in scoring functions
            data["massive_fallback"] = massive_data
            print(f"Massive.com fallback data retrieved for {ticker}", file=sys.stderr)
    
    return data


def calculate_quality_score(data: Dict, use_percentile: bool = True) -> float:
    """Calculate Quality Score (0-100). Redistributes weights when metrics are missing.
    
    Args:
        data: Dictionary with financial data from FMP API
        use_percentile: If True, use percentile normalization when benchmarks available
    """
    ratios = data.get("ratios")
    if not ratios or not isinstance(ratios, list) or len(ratios) == 0:
        return 50.0
    
    latest = ratios[0]
    scores = {}
    available_metrics = []
    
    # Load benchmarks if percentile normalization enabled
    benchmarks = None
    if use_percentile:
        sector = data.get("sector")
        benchmarks = load_benchmarks(sector)
    
    # ROE (FMP returns as decimal, e.g., 0.29 = 29%)
    roe = latest.get("returnOnEquity")
    # If ROE is 0 or None, calculate from income statement and balance sheet
    if roe is None or roe == 0:
        income = data.get("income")
        balance = data.get("balance")
        if income and isinstance(income, list) and len(income) > 0 and balance and isinstance(balance, list) and len(balance) > 0:
            inc = income[0]
            bal = balance[0]
            net_income = inc.get("netIncome", 0) or 0
            total_equity = bal.get("totalStockholdersEquity", 0) or 0
            # Only calculate if equity is positive (negative equity makes ROE meaningless)
            if total_equity > 0 and net_income:
                roe = (net_income / total_equity) * 100  # Already in percentage
    
    if roe is not None and roe != 0:
        # Convert to percentage if needed (if < 1, assume it's decimal)
        if abs(roe) < 1:
            roe = roe * 100
        
        # Use percentile normalization if benchmarks available, else fixed range
        if benchmarks and benchmarks.get("roe"):
            scores["roe"] = normalize_score_percentile(roe, benchmarks["roe"], "roe", invert=False)
        else:
            scores["roe"] = normalize_score(roe, 0, 50)  # 0-50% range
        available_metrics.append("roe")
    
    # ROA
    roa = latest.get("returnOnAssets")
    # If ROA is 0 or None, calculate from income statement and balance sheet
    if roa is None or roa == 0:
        income = data.get("income")
        balance = data.get("balance")
        if income and isinstance(income, list) and len(income) > 0 and balance and isinstance(balance, list) and len(balance) > 0:
            inc = income[0]
            bal = balance[0]
            net_income = inc.get("netIncome", 0) or 0
            total_assets = bal.get("totalAssets", 0) or 0
            if total_assets > 0 and net_income:
                roa = (net_income / total_assets) * 100  # Already in percentage
    
    if roa is not None and roa != 0:
        if abs(roa) < 1:
            roa = roa * 100
        
        if benchmarks and benchmarks.get("roa"):
            scores["roa"] = normalize_score_percentile(roa, benchmarks["roa"], "roa", invert=False)
        else:
            scores["roa"] = normalize_score(roa, 0, 25)  # 0-25% range
        available_metrics.append("roa")
    
    # Net Income Margin
    margin = latest.get("netProfitMargin")
    if margin is None:
        margin = latest.get("netIncomeMargin")
    if margin is not None:
        if abs(margin) < 1:
            margin = margin * 100
        
        if benchmarks and benchmarks.get("netMargin"):
            scores["margin"] = normalize_score_percentile(margin, benchmarks["netMargin"], "netMargin", invert=False)
        else:
            scores["margin"] = normalize_score(margin, -10, 35)  # Allow negative margins, max 35%
        available_metrics.append("margin")
    
    # ROIC - Calculate from available data if missing
    roic = latest.get("returnOnInvestedCapital")
    if roic is None:
        # Try returnOnCapitalEmployed as proxy (very similar metric)
        roic = latest.get("returnOnCapitalEmployed")
    
    if roic is None:
        # Calculate ROIC from available data: ROIC = NOPAT / Invested Capital
        income = data.get("income")
        balance = data.get("balance")
        if income and isinstance(income, list) and len(income) > 0 and balance and isinstance(balance, list) and len(balance) > 0:
            inc = income[0]
            bal = balance[0]
            operating_income = inc.get("operatingIncome") or inc.get("ebitda") or inc.get("ebit", 0)
            income_before_tax = inc.get("incomeBeforeTax") or inc.get("ebit", 0) or operating_income
            tax_expense = abs(inc.get("incomeTaxExpense", 0) or 0)
            if income_before_tax and income_before_tax != 0:
                tax_rate = min(tax_expense / abs(income_before_tax), 0.5)  # Cap tax rate at 50%
            else:
                tax_rate = 0.2  # Default 20% if can't calculate
            nopat = operating_income * (1 - tax_rate)
            total_debt = bal.get("totalDebt", 0) or 0
            total_equity = bal.get("totalStockholdersEquity", 0) or 0
            cash = bal.get("cashAndCashEquivalentsAtCarryingValue", 0) or bal.get("cashAndShortTermInvestments", 0) or 0
            invested_capital = total_debt + total_equity - cash
            if invested_capital > 0 and nopat:
                roic = (nopat / invested_capital) * 100
    
    if roic is not None:
        if abs(roic) < 1:
            roic = roic * 100
        
        if benchmarks and benchmarks.get("roic"):
            scores["roic"] = normalize_score_percentile(roic, benchmarks["roic"], "roic", invert=False)
        else:
            scores["roic"] = normalize_score(roic, 0, 40)
        available_metrics.append("roic")
    
    # Debt/Total Capital (inverted)
    debt_equity = latest.get("debtEquityRatio")
    # If debt_equity is 0 or None, calculate from balance sheet
    if debt_equity is None or debt_equity == 0:
        balance = data.get("balance")
        if balance and isinstance(balance, list) and len(balance) > 0:
            b = balance[0]
            total_debt = b.get("totalDebt", 0) or 0
            total_equity = b.get("totalStockholdersEquity", 0) or 0
            # Calculate debt-to-equity ratio (not debt-to-capital)
            if total_equity > 0:
                debt_equity = total_debt / total_equity
            elif total_debt > 0:
                # Negative equity but has debt - use debt-to-capital instead
                total_capital = total_debt + total_equity
                if total_capital > 0:
                    debt_equity = total_debt / total_capital
        else:
            # Fallback: calculate debt-to-capital ratio
            balance = data.get("balance")
            if balance and isinstance(balance, list) and len(balance) > 0:
                b = balance[0]
                total_debt = b.get("totalDebt", 0) or 0
                total_equity = b.get("totalStockholdersEquity", 0) or 0
                total_capital = total_debt + total_equity
                if total_capital > 0:
                    debt_equity = total_debt / total_capital
    
    if debt_equity is not None:
        if benchmarks and benchmarks.get("debtEquity"):
            scores["debtCapital"] = normalize_score_percentile(debt_equity, benchmarks["debtEquity"], "debtEquity", invert=True)
        else:
            scores["debtCapital"] = normalize_score(debt_equity, 0, 2.0, invert=True)
        available_metrics.append("debtCapital")
    
    # Redistribute weights for available metrics only
    if not available_metrics:
        return 50.0
    
    # Calculate total weight of available metrics
    available_weight = sum(QUALITY_WEIGHTS.get(m, 0) for m in available_metrics)
    
    # Weighted sum with redistributed weights
    total = 0.0
    for metric in available_metrics:
        weight = QUALITY_WEIGHTS.get(metric, 0)
        # Redistribute weight proportionally
        redistributed_weight = weight / available_weight if available_weight > 0 else 0
        total += scores[metric] * redistributed_weight
    
    return total


def calculate_growth_score(data: Dict) -> float:
    """Calculate Growth Score (0-100). Redistributes weights when metrics are missing."""
    growth = data.get("growth")
    scores = {}
    available_metrics = []
    
    # Try to get growth data from FMP growth endpoint
    if growth and isinstance(growth, list) and len(growth) >= 2:
        latest = growth[0]
        prev = growth[1]
        
        # Revenue Growth
        rev_growth = latest.get("revenueGrowth")
        if rev_growth is None:
            # Calculate from revenue values
            latest_rev = latest.get("revenue")
            prev_rev = prev.get("revenue")
            if latest_rev and prev_rev and prev_rev != 0:
                rev_growth = ((latest_rev - prev_rev) / abs(prev_rev)) * 100
        
        if rev_growth is not None:
            # CRITICAL FIX: Convert decimal to percentage BEFORE normalization
            # FMP returns growth as decimal (0.2387 = 23.87%)
            if abs(rev_growth) < 1:
                rev_growth = rev_growth * 100
            # Adjusted range: -30% to 100% (more realistic)
            scores["revenue"] = normalize_score(rev_growth, -30, 100)
            available_metrics.append("revenue")
        
        # Earnings Growth
        earnings_growth = latest.get("netIncomeGrowth")
        if earnings_growth is None:
            # Calculate from net income values
            latest_ni = latest.get("netIncome")
            prev_ni = prev.get("netIncome")
            if latest_ni and prev_ni and prev_ni != 0:
                earnings_growth = ((latest_ni - prev_ni) / abs(prev_ni)) * 100
        
        if earnings_growth is not None:
            # CRITICAL FIX: Convert decimal to percentage BEFORE normalization
            # FMP returns growth as decimal (2.9229 = 292.29%)
            if abs(earnings_growth) < 1:
                earnings_growth = earnings_growth * 100
            # Adjusted range: -50% to 200% (exceptional growth is rare)
            scores["earnings"] = normalize_score(earnings_growth, -50, 200)
            available_metrics.append("earnings")
    
    # FCF Growth - Calculate from cash flow statements
    cashflow = data.get("cashflow")
    if cashflow and isinstance(cashflow, list) and len(cashflow) >= 2:
        latest_cf = cashflow[0]
        prev_cf = cashflow[1]
        fcf_latest = latest_cf.get("freeCashFlow")
        if fcf_latest is None:
            # Calculate FCF: Operating CF - CapEx
            op_cf = latest_cf.get("operatingCashFlow", 0) or 0
            capex = abs(latest_cf.get("capitalExpenditure", 0) or 0)
            fcf_latest = op_cf - capex
        
        fcf_prev = prev_cf.get("freeCashFlow")
        if fcf_prev is None:
            op_cf_prev = prev_cf.get("operatingCashFlow", 0) or 0
            capex_prev = abs(prev_cf.get("capitalExpenditure", 0) or 0)
            fcf_prev = op_cf_prev - capex_prev
        
        if fcf_prev and fcf_prev != 0:
            fcf_growth = ((fcf_latest - fcf_prev) / abs(fcf_prev)) * 100
            # Adjusted range: -50% to 150% (more realistic)
            scores["fcf"] = normalize_score(fcf_growth, -50, 150)
            available_metrics.append("fcf")
    
    # FCF Per Share Growth
    key_metrics = data.get("keyMetrics")
    if key_metrics and isinstance(key_metrics, list) and len(key_metrics) >= 2:
        latest_km = key_metrics[0]
        prev_km = key_metrics[1]
        fcfps_latest = latest_km.get("freeCashFlowPerShare")
        fcfps_prev = prev_km.get("freeCashFlowPerShare")
        if fcfps_prev and fcfps_prev != 0:
            if fcfps_latest is None:
                # Calculate from FCF and shares outstanding
                cashflow = data.get("cashflow")
                if cashflow and isinstance(cashflow, list) and len(cashflow) > 0:
                    cf = cashflow[0]
                    fcf = cf.get("freeCashFlow") or (cf.get("operatingCashFlow", 0) - abs(cf.get("capitalExpenditure", 0) or 0))
                    shares = latest_km.get("sharesOutstanding", 0) or 0
                    if shares > 0:
                        fcfps_latest = fcf / shares
            
            if fcfps_latest is not None:
                fcfps_growth = ((fcfps_latest - fcfps_prev) / abs(fcfps_prev)) * 100
                # Adjusted range: -50% to 150% (more realistic)
                scores["fcfPerShare"] = normalize_score(fcfps_growth, -50, 150)
                available_metrics.append("fcfPerShare")
    
    # Redistribute weights for available metrics only
    if not available_metrics:
        return 50.0
    
    # Calculate total weight of available metrics
    available_weight = sum(GROWTH_WEIGHTS.get(m, 0) for m in available_metrics)
    
    # Weighted sum with redistributed weights
    total = 0.0
    for metric in available_metrics:
        weight = GROWTH_WEIGHTS.get(metric, 0)
        # Redistribute weight proportionally
        redistributed_weight = weight / available_weight if available_weight > 0 else 0
        total += scores[metric] * redistributed_weight
    
    return total


def is_growth_company(data: Dict) -> bool:
    """Detect if company is a growth stock based on ROE, revenue growth, and sector."""
    ratios = data.get("ratios")
    growth_data = data.get("growth")
    profile = data.get("profile")
    
    is_growth = False
    
    # Check ROE > 20%
    if ratios and isinstance(ratios, list) and len(ratios) > 0:
        roe = ratios[0].get("returnOnEquity", 0)
        if abs(roe) < 1:
            roe = roe * 100
        if roe > 20:
            is_growth = True
    
    # Check revenue growth > 15%
    if growth_data and isinstance(growth_data, list) and len(growth_data) > 0:
        rev_growth = growth_data[0].get("revenueGrowth", 0)
        if rev_growth is None:
            # Calculate from revenue values
            if len(growth_data) >= 2:
                latest_rev = growth_data[0].get("revenue")
                prev_rev = growth_data[1].get("revenue")
                if latest_rev and prev_rev and prev_rev != 0:
                    rev_growth = ((latest_rev - prev_rev) / abs(prev_rev)) * 100
        if rev_growth:
            if abs(rev_growth) < 1:
                rev_growth = rev_growth * 100
            if rev_growth > 15:
                is_growth = True
    
    # Check sector (tech sectors are typically growth)
    if profile:
        sector = None
        if isinstance(profile, list) and len(profile) > 0:
            sector = profile[0].get("sector", "")
        elif isinstance(profile, dict):
            sector = profile.get("sector", "")
        
        tech_sectors = ["Technology", "Information Technology", "Software", "Semiconductors", "Internet"]
        if sector and any(tech in sector for tech in tech_sectors):
            is_growth = True
    
    return is_growth


def calculate_value_score(data: Dict, use_percentile: bool = True) -> float:
    """Calculate Value Score (0-100) — lower valuations are better. Uses percentile normalization when benchmarks available."""
    ratios = data.get("ratios")
    quote = data.get("quote")
    key_metrics = data.get("keyMetrics")
    
    if not ratios or not isinstance(ratios, list) or len(ratios) == 0:
        return 50.0
    
    latest = ratios[0]
    scores = {}
    available_metrics = []
    is_growth = is_growth_company(data)
    
    # Load benchmarks if percentile normalization enabled
    benchmarks = None
    if use_percentile:
        sector = data.get("sector")
        benchmarks = load_benchmarks(sector)
    
    # P/E (inverted) - Use percentile normalization if benchmarks available
    pe = latest.get("priceEarningsRatio")
    if pe is None and quote and isinstance(quote, list) and len(quote) > 0:
        price = quote[0].get("price", 0)
        eps = latest.get("earningsPerShare")
        if eps and eps > 0:
            pe = price / eps
    
    # Fallback to Massive.com for quote if FMP quote missing
    if pe is None:
        massive_fallback = data.get("massive_fallback", {})
        massive_quote = massive_fallback.get("quote") or massive_fallback.get("snapshot")
        if massive_quote:
            price = massive_quote.get("price") or massive_quote.get("last") or massive_quote.get("close")
            eps = latest.get("earningsPerShare")
            if price and eps and eps > 0:
                pe = price / eps
    
    if pe is not None and pe > 0:
        if benchmarks and benchmarks.get("pe"):
            scores["pe"] = normalize_score_percentile(pe, benchmarks["pe"], "pe", invert=True)
        else:
            # Fallback to fixed ranges
            pe_max = 150 if is_growth else 80
            scores["pe"] = normalize_score(pe, 5, pe_max, invert=True)
        available_metrics.append("pe")
    
    # P/B (inverted) - Use percentile normalization if benchmarks available
    pb = latest.get("priceToBookRatio")
    if pb is None:
        # Calculate from price and book value
        quote_data = quote[0] if quote and isinstance(quote, list) and len(quote) > 0 else {}
        price = quote_data.get("price", 0)
        if not price:
            massive_fallback = data.get("massive_fallback", {})
            massive_quote = massive_fallback.get("quote") or massive_fallback.get("snapshot")
            if massive_quote:
                price = massive_quote.get("price") or massive_quote.get("last") or massive_quote.get("close")
        
        balance = data.get("balance")
        if price and balance and isinstance(balance, list) and len(balance) > 0:
            bal = balance[0]
            book_value = bal.get("totalStockholdersEquity", 0) or 0
            shares = latest.get("sharesOutstanding") or key_metrics[0].get("sharesOutstanding", 0) if key_metrics and isinstance(key_metrics, list) and len(key_metrics) > 0 else 0
            if book_value > 0 and shares > 0:
                book_per_share = book_value / shares
                if book_per_share > 0:
                    pb = price / book_per_share
    
    # Handle P/B = 0 (might be negative book value or calculation issue)
    if pb is not None:
        if pb == 0:
            # Try to calculate from balance sheet to see if it's really 0 or negative book value
            balance = data.get("balance")
            quote_data = quote[0] if quote and isinstance(quote, list) and len(quote) > 0 else {}
            price = quote_data.get("price", 0)
            if not price:
                massive_fallback = data.get("massive_fallback", {})
                massive_quote = massive_fallback.get("quote") or massive_fallback.get("snapshot")
                if massive_quote:
                    price = massive_quote.get("price") or massive_quote.get("last") or massive_quote.get("close")
            
            if price and balance and isinstance(balance, list) and len(balance) > 0:
                bal = balance[0]
                book_value = bal.get("totalStockholdersEquity", 0) or 0
                shares = latest.get("sharesOutstanding") or key_metrics[0].get("sharesOutstanding", 0) if key_metrics and isinstance(key_metrics, list) and len(key_metrics) > 0 else 0
                if shares > 0:
                    book_per_share = book_value / shares
                    if book_per_share > 0:
                        pb = price / book_per_share
                    elif book_per_share < 0:
                        # Negative book value - this is bad, skip P/B metric
                        pb = None
        
        if pb is not None and pb > 0:
            if benchmarks and benchmarks.get("pb"):
                scores["pb"] = normalize_score_percentile(pb, benchmarks["pb"], "pb", invert=True)
            else:
                # Fallback to fixed ranges
                pb_max = 50 if is_growth else 20
                scores["pb"] = normalize_score(pb, 0.5, pb_max, invert=True)
            available_metrics.append("pb")
    
    # P/S (inverted) - Use percentile normalization if benchmarks available
    ps = latest.get("priceToSalesRatio")
    if ps is None:
        # Calculate from price and sales
        quote_data = quote[0] if quote and isinstance(quote, list) and len(quote) > 0 else {}
        price = quote_data.get("price", 0)
        if not price:
            massive_fallback = data.get("massive_fallback", {})
            massive_quote = massive_fallback.get("quote") or massive_fallback.get("snapshot")
            if massive_quote:
                price = massive_quote.get("price") or massive_quote.get("last") or massive_quote.get("close")
        
        income = data.get("income")
        if price and income and isinstance(income, list) and len(income) > 0:
            inc = income[0]
            revenue = inc.get("revenue", 0) or 0
            shares = latest.get("sharesOutstanding") or key_metrics[0].get("sharesOutstanding", 0) if key_metrics and isinstance(key_metrics, list) and len(key_metrics) > 0 else 0
            if revenue > 0 and shares > 0:
                sales_per_share = revenue / shares
                if sales_per_share > 0:
                    ps = price / sales_per_share
    
    if ps is not None and ps > 0:
        if benchmarks and benchmarks.get("ps"):
            scores["ps"] = normalize_score_percentile(ps, benchmarks["ps"], "ps", invert=True)
        else:
            # Fallback to fixed ranges
            ps_max = 60 if is_growth else 25
            scores["ps"] = normalize_score(ps, 0.5, ps_max, invert=True)
        available_metrics.append("ps")
    
    # FCF Yield
    fcf_yield = None
    if key_metrics and isinstance(key_metrics, list) and len(key_metrics) > 0:
        fcf_yield = key_metrics[0].get("freeCashFlowYield")
    
    # If fcf_yield is 0 or None, calculate from cash flow and market cap
    if fcf_yield is None or fcf_yield == 0:
        # Calculate from cash flow and market cap
        cashflow = data.get("cashflow")
        quote_data = quote[0] if quote and isinstance(quote, list) and len(quote) > 0 else {}
        market_cap = quote_data.get("marketCap") or quote_data.get("marketCapitalization", 0)
        
        # Fallback to Massive.com for market cap if FMP missing
        if not market_cap:
            massive_fallback = data.get("massive_fallback", {})
            massive_quote = massive_fallback.get("quote") or massive_fallback.get("snapshot")
            if massive_quote:
                market_cap = massive_quote.get("marketCap") or massive_quote.get("market_cap")
        
        if cashflow and isinstance(cashflow, list) and len(cashflow) > 0:
            cf = cashflow[0]
            fcf = cf.get("freeCashFlow")
            if fcf is None:
                op_cf = cf.get("operatingCashFlow", 0) or 0
                capex = abs(cf.get("capitalExpenditure", 0) or 0)
                fcf = op_cf - capex
            
            if not market_cap and quote_data:
                # Calculate market cap from price and shares
                price = quote_data.get("price", 0)
                shares = latest.get("sharesOutstanding") or key_metrics[0].get("sharesOutstanding", 0) if key_metrics and isinstance(key_metrics, list) and len(key_metrics) > 0 else 0
                if price and shares:
                    market_cap = price * shares
            
            if fcf and market_cap and market_cap > 0:
                fcf_yield = (fcf / market_cap) * 100
    
    if fcf_yield is not None:
        # FMP may return as decimal (0.02 = 2%)
        if abs(fcf_yield) < 1:
            fcf_yield = fcf_yield * 100
        # Only include if FCF Yield is positive (negative FCF is bad, but 0 might be missing data)
        if fcf_yield > 0:
            scores["fcf"] = normalize_score(fcf_yield, 0, 15)
            available_metrics.append("fcf")
    
    # Margin of Safety - Improved calculation using sector-relative P/E
    margin_of_safety = None
    if pe is not None:
        # Dynamic fair_pe based on growth company detection
        # Growth stocks: fair_pe = 35 (reflects higher valuations), Value stocks: fair_pe = 18
        fair_pe = 35 if is_growth else 18
        
        # Calculate margin of safety as percentage discount/premium
        if pe < fair_pe:
            # Trading at discount - positive margin of safety
            margin_of_safety = ((fair_pe - pe) / fair_pe) * 100
        else:
            # Trading at premium - negative margin of safety
            # Cap the negative value to prevent extreme negatives
            margin_of_safety = -min(((pe - fair_pe) / fair_pe) * 100, 200)  # Cap at -200%
    
    if margin_of_safety is not None:
        # Expanded range: -200% to +100%
        scores["marginOfSafety"] = normalize_score(margin_of_safety, -200, 100)
        available_metrics.append("marginOfSafety")
    
    # Redistribute weights for available metrics only
    if not available_metrics:
        return 50.0
    
    # Calculate total weight of available metrics
    available_weight = sum(VALUE_WEIGHTS.get(m, 0) for m in available_metrics)
    
    # Weighted sum with redistributed weights
    total = 0.0
    for metric in available_metrics:
        weight = VALUE_WEIGHTS.get(metric, 0)
        # Redistribute weight proportionally
        redistributed_weight = weight / available_weight if available_weight > 0 else 0
        total += scores[metric] * redistributed_weight
    
    return total


def calculate_health_score(data: Dict) -> float:
    """Calculate Financial Health Score (0-100). Redistributes weights when metrics are missing."""
    ratios = data.get("ratios")
    if not ratios or not isinstance(ratios, list) or len(ratios) == 0:
        return 50.0
    
    latest = ratios[0]
    scores = {}
    available_metrics = []
    
    # Debt (inverted)
    debt_equity = latest.get("debtEquityRatio")
    if debt_equity is None:
        # Calculate from balance sheet
        balance = data.get("balance")
        if balance and isinstance(balance, list) and len(balance) > 0:
            bal = balance[0]
            total_debt = bal.get("totalDebt", 0) or 0
            total_equity = bal.get("totalStockholdersEquity", 0) or 0
            if total_equity > 0:
                debt_equity = total_debt / total_equity
    
    if debt_equity is not None:
        scores["debt"] = normalize_score(debt_equity, 0, 3, invert=True)
        available_metrics.append("debt")
    
    # Liquidity
    current_ratio = latest.get("currentRatio")
    # If current_ratio is 0 or None, calculate from balance sheet
    if current_ratio is None or current_ratio == 0:
        # Calculate from balance sheet
        balance = data.get("balance")
        if balance and isinstance(balance, list) and len(balance) > 0:
            bal = balance[0]
            current_assets = bal.get("totalCurrentAssets", 0) or 0
            current_liabilities = bal.get("totalCurrentLiabilities", 0) or 0
            if current_liabilities > 0:
                current_ratio = current_assets / current_liabilities
            elif current_assets > 0:
                # No current liabilities but has current assets = excellent liquidity
                current_ratio = 10.0  # Use high value to represent excellent liquidity
    
    if current_ratio is not None:
        scores["liquidity"] = normalize_score(current_ratio, 0, 3)
        available_metrics.append("liquidity")
    
    # Coverage
    interest_coverage = latest.get("interestCoverage")
    if interest_coverage is None:
        # Calculate: EBIT / Interest Expense
        income = data.get("income")
        if income and isinstance(income, list) and len(income) > 0:
            inc = income[0]
            ebit = inc.get("ebitda") or inc.get("operatingIncome") or inc.get("ebit", 0)
            interest = abs(inc.get("interestExpense", 0) or 0)
            if interest > 0:
                interest_coverage = ebit / interest
            elif interest == 0 and ebit:
                # No interest expense = excellent coverage (infinite), treat as very high score
                # Use a high value (e.g., 100x) to represent excellent coverage
                interest_coverage = 100.0
    
    # Handle case where FMP returns 0 for interestCoverage (means no interest expense)
    if interest_coverage == 0:
        income = data.get("income")
        if income and isinstance(income, list) and len(income) > 0:
            inc = income[0]
            interest_expense = abs(inc.get("interestExpense", 0) or 0)
            if interest_expense == 0:
                # No interest expense = excellent coverage
                interest_coverage = 100.0
    
    if interest_coverage is not None:
        # Expanded range for high-growth companies
        # Cap at 100 for normalization (100x coverage is already excellent)
        interest_coverage_normalized = min(interest_coverage, 100.0)
        scores["coverage"] = normalize_score(interest_coverage_normalized, 0, 30)
        available_metrics.append("coverage")
    
    # Redistribute weights for available metrics only
    if not available_metrics:
        return 50.0
    
    # Calculate total weight of available metrics
    available_weight = sum(HEALTH_WEIGHTS.get(m, 0) for m in available_metrics)
    
    # Weighted sum with redistributed weights
    total = 0.0
    for metric in available_metrics:
        weight = HEALTH_WEIGHTS.get(metric, 0)
        # Redistribute weight proportionally
        redistributed_weight = weight / available_weight if available_weight > 0 else 0
        total += scores[metric] * redistributed_weight
    
    return total


def calculate_shareholder_score(data: Dict) -> float:
    """Calculate Shareholder Score (0-100). Adjusted for growth companies (lower dividend expectations)."""
    quote = data.get("quote")
    key_metrics = data.get("keyMetrics")
    dividends = data.get("dividends")
    balance = data.get("balance")
    
    scores = {}
    available_metrics = []
    is_growth = is_growth_company(data)
    
    # Dividend Yield - Lower expectations for growth companies
    div_yield = None
    if quote and isinstance(quote, list) and len(quote) > 0:
        div_yield = quote[0].get("dividendYield")
    if div_yield is None and key_metrics and isinstance(key_metrics, list) and len(key_metrics) > 0:
        div_yield = key_metrics[0].get("dividendYield")
    
    # Fallback to Massive.com for dividend yield if FMP missing
    if div_yield is None:
        massive_fallback = data.get("massive_fallback", {})
        massive_quote = massive_fallback.get("quote") or massive_fallback.get("snapshot")
        if massive_quote:
            div_yield = massive_quote.get("dividendYield") or massive_quote.get("dividend_yield")
    
    if div_yield is not None:
        # FMP may return as decimal (0.02 = 2%)
        if abs(div_yield) < 1:
            div_yield = div_yield * 100
        # Growth companies: normalize to 0-3% range (lower expectations), value: 0-6%
        div_max = 3 if is_growth else 6
        scores["divYield"] = normalize_score(div_yield, 0, div_max)
        available_metrics.append("divYield")
    
    # Dividend Growth
    div_growth = None
    if dividends and isinstance(dividends, list) and len(dividends) >= 2:
        # Sum dividends by year and calculate YoY growth
        latest_year = {}
        for div in dividends[:24]:  # Last 24 entries (2+ years)
            date = div.get("date", "")
            year = date[:4] if len(date) >= 4 else None
            amount = div.get("dividend", 0) or 0
            if year:
                if year not in latest_year:
                    latest_year[year] = 0
                latest_year[year] += amount
        if len(latest_year) >= 2:
            years = sorted(latest_year.keys(), reverse=True)
            if len(years) >= 2:
                latest_total = latest_year[years[0]]
                prev_total = latest_year[years[1]]
                if prev_total > 0:
                    div_growth = ((latest_total - prev_total) / prev_total) * 100
    
    if div_growth is not None:
        # Expanded range: -50% to +100% (allow exceptional dividend growth)
        scores["divGrowth"] = normalize_score(div_growth, -50, 100)
        available_metrics.append("divGrowth")
    
    # Buyback Yield - More important for growth companies
    buyback_yield = None
    if key_metrics and isinstance(key_metrics, list) and len(key_metrics) >= 2:
        latest_km = key_metrics[0]
        prev_km = key_metrics[1]
        shares_latest = latest_km.get("sharesOutstanding", 0) or 0
        shares_prev = prev_km.get("sharesOutstanding", 0) or 0
        if shares_prev > 0 and shares_latest < shares_prev:
            quote_data = quote[0] if quote and isinstance(quote, list) and len(quote) > 0 else {}
            price = quote_data.get("price", 0) or latest_km.get("price", 0) or 0
            
            # Fallback to Massive.com for price
            if not price:
                massive_fallback = data.get("massive_fallback", {})
                massive_quote = massive_fallback.get("quote") or massive_fallback.get("snapshot")
                if massive_quote:
                    price = massive_quote.get("price") or massive_quote.get("last") or massive_quote.get("close")
            
            market_cap = quote_data.get("marketCap") or latest_km.get("marketCap", 0) or 0
            
            # Calculate market cap if missing
            if not market_cap and price and shares_latest:
                market_cap = price * shares_latest
            
            if market_cap > 0:
                shares_reduced = shares_prev - shares_latest
                buyback_value = shares_reduced * price
                buyback_yield = (buyback_value / market_cap) * 100
    
    if buyback_yield is not None:
        # Growth companies: normalize to 0-20% range (higher buyback expectations), value: 0-10%
        buyback_max = 20 if is_growth else 10
        scores["buybackYield"] = normalize_score(buyback_yield, 0, buyback_max)
        available_metrics.append("buybackYield")
    
    # Debt Paydown
    debt_paydown = None
    if balance and isinstance(balance, list) and len(balance) >= 2:
        latest_bal = balance[0]
        prev_bal = balance[1]
        debt_latest = latest_bal.get("totalDebt", 0) or 0
        debt_prev = prev_bal.get("totalDebt", 0) or 0
        if debt_prev > 0:
            debt_change_pct = ((debt_latest - debt_prev) / debt_prev) * 100
            # Negative change = paydown (good)
            debt_paydown = -debt_change_pct
    
    if debt_paydown is not None:
        scores["debtPaydown"] = normalize_score(debt_paydown, -50, 50)
        available_metrics.append("debtPaydown")
    
    # Redistribute weights for available metrics only
    if not available_metrics:
        return 50.0
    
    # For growth companies, adjust weights: reduce dividend weight, increase buyback weight
    if is_growth:
        adjusted_weights = {
            "divYield": 0.15,  # Reduced from 0.30
            "divGrowth": 0.15,  # Reduced from 0.25
            "buybackYield": 0.50,  # Increased from 0.25
            "debtPaydown": 0.20,  # Same
        }
    else:
        adjusted_weights = SHAREHOLDER_WEIGHTS
    
    # Calculate total weight of available metrics using adjusted weights
    available_weight = sum(adjusted_weights.get(m, SHAREHOLDER_WEIGHTS.get(m, 0)) for m in available_metrics)
    
    # Weighted sum with redistributed weights
    total = 0.0
    for metric in available_metrics:
        weight = adjusted_weights.get(metric, SHAREHOLDER_WEIGHTS.get(metric, 0))
        # Redistribute weight proportionally
        redistributed_weight = weight / available_weight if available_weight > 0 else 0
        total += scores[metric] * redistributed_weight
    
    return total


def calculate_composite_score(quality: float, growth: float, value: float, health: float, shareholder: float) -> float:
    """Calculate composite score as average of all component scores."""
    return (quality + growth + value + health + shareholder) / 5.0


def get_grade(composite_score: float) -> str:
    """Determine letter grade from composite score."""
    for threshold, grade in GRADE_THRESHOLDS:
        if composite_score >= threshold:
            return grade
    return "F"


def identify_strengths_weaknesses(quality: float, growth: float, value: float, health: float, shareholder: float) -> tuple:
    """Identify strengths (>=70) and weaknesses (<50)."""
    strengths = []
    weaknesses = []
    
    if growth >= STRENGTH_THRESHOLD:
        strengths.append("Strong Growth")
    elif growth < WEAKNESS_THRESHOLD:
        weaknesses.append("Weak Growth")
    
    if quality >= STRENGTH_THRESHOLD:
        strengths.append("High Quality")
    elif quality < WEAKNESS_THRESHOLD:
        weaknesses.append("Quality Concerns")
    
    if value >= STRENGTH_THRESHOLD:
        strengths.append("Attractive Value")
    elif value < WEAKNESS_THRESHOLD:
        weaknesses.append("Overvalued")
    
    if health >= STRENGTH_THRESHOLD:
        strengths.append("Financially Healthy")
    elif health < WEAKNESS_THRESHOLD:
        weaknesses.append("Financially Concerning")
    
    if shareholder >= STRENGTH_THRESHOLD:
        strengths.append("Shareholder Friendly")
    elif shareholder < WEAKNESS_THRESHOLD:
        weaknesses.append("Poor Shareholder Returns")
    
    return strengths, weaknesses


def score_ticker(ticker: str) -> Dict:
    """Score a single ticker and return results."""
    print(f"Fetching data for {ticker}...", file=sys.stderr)
    data = fetch_fmp_data(ticker)
    
    quality = calculate_quality_score(data, use_percentile=True)
    growth_from_cg = _growth_score_from_company_growth(ticker)
    growth = growth_from_cg if growth_from_cg is not None else calculate_growth_score(data)
    value = calculate_value_score(data, use_percentile=True)
    health = calculate_health_score(data)
    shareholder = calculate_shareholder_score(data)
    
    composite = calculate_composite_score(quality, growth, value, health, shareholder)
    grade = get_grade(composite)
    strengths, weaknesses = identify_strengths_weaknesses(quality, growth, value, health, shareholder)
    
    # Get company name
    profile = data.get("profile")
    company_name = ticker
    if profile and isinstance(profile, list) and len(profile) > 0:
        company_name = profile[0].get("companyName", ticker)
    elif profile and isinstance(profile, dict):
        company_name = profile.get("companyName", ticker)
    
    return {
        "ticker": ticker,
        "companyName": company_name,
        "scores": {
            "quality": round(quality, 2),
            "growth": round(growth, 2),
            "value": round(value, 2),
            "health": round(health, 2),
            "shareholder": round(shareholder, 2),
            "composite": round(composite, 2),
        },
        "grade": grade,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "data": data,  # Include raw data for report generation
    }


def generate_report(result: Dict, output_path: Path):
    """Generate markdown report for a single ticker."""
    ticker = result["ticker"]
    company_name = result["companyName"]
    scores = result["scores"]
    grade = result["grade"]
    strengths = result["strengths"]
    weaknesses = result["weaknesses"]
    
    report = f"""# Stock Score Report: {ticker} — {company_name}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Scoring Summary

| Metric | Score | Grade |
|--------|-------|-------|
| **Composite Score** | {scores['composite']:.2f} | **{grade}** |
| Quality Score | {scores['quality']:.2f} | {get_grade(scores['quality'])} |
| Growth Score | {scores['growth']:.2f} | {get_grade(scores['growth'])} |
| Value Score | {scores['value']:.2f} | {get_grade(scores['value'])} |
| Health Score | {scores['health']:.2f} | {get_grade(scores['health'])} |
| Shareholder Score | {scores['shareholder']:.2f} | {get_grade(scores['shareholder'])} |

---

## Strengths

"""
    
    if strengths:
        for s in strengths:
            report += f"- ✅ {s}\n"
    else:
        report += "*No major strengths identified (all scores < 70).*\n"
    
    report += "\n---\n\n## Weaknesses\n\n"
    
    if weaknesses:
        for w in weaknesses:
            report += f"- ⚠️ {w}\n"
    else:
        report += "*No major weaknesses identified (all scores >= 50).*\n"
    
    report += f"""

---

## Key Metrics

### Quality Metrics
"""
    
    ratios = result.get("data", {}).get("ratios")
    income = result.get("data", {}).get("income")
    balance = result.get("data", {}).get("balance")
    
    if ratios and isinstance(ratios, list) and len(ratios) > 0:
        r = ratios[0]
        roe = r.get('returnOnEquity')
        roa = r.get('returnOnAssets')
        margin = r.get('netProfitMargin') or r.get('netIncomeMargin')
        roic = r.get('returnOnInvestedCapital') or r.get('returnOnCapitalEmployed')
        debt_equity = r.get('debtEquityRatio')
        
        # Calculate ROE from financials if 0 or None
        if (roe is None or roe == 0) and income and isinstance(income, list) and len(income) > 0 and balance and isinstance(balance, list) and len(balance) > 0:
            inc = income[0]
            bal = balance[0]
            net_income = inc.get("netIncome", 0) or 0
            total_equity = bal.get("totalStockholdersEquity", 0) or 0
            if total_equity > 0 and net_income:
                roe = (net_income / total_equity) * 100
        
        # Calculate ROA from financials if 0 or None
        if (roa is None or roa == 0) and income and isinstance(income, list) and len(income) > 0 and balance and isinstance(balance, list) and len(balance) > 0:
            inc = income[0]
            bal = balance[0]
            net_income = inc.get("netIncome", 0) or 0
            total_assets = bal.get("totalAssets", 0) or 0
            if total_assets > 0 and net_income:
                roa = (net_income / total_assets) * 100
        
        # Calculate ROIC from financials if None
        if roic is None and income and isinstance(income, list) and len(income) > 0 and balance and isinstance(balance, list) and len(balance) > 0:
            inc = income[0]
            bal = balance[0]
            operating_income = inc.get("operatingIncome") or inc.get("ebitda") or inc.get("ebit", 0)
            income_before_tax = inc.get("incomeBeforeTax") or inc.get("ebit", 0) or operating_income
            tax_expense = abs(inc.get("incomeTaxExpense", 0) or 0)
            if income_before_tax and income_before_tax != 0:
                tax_rate = min(tax_expense / abs(income_before_tax), 0.5)
            else:
                tax_rate = 0.2
            nopat = operating_income * (1 - tax_rate)
            total_debt = bal.get("totalDebt", 0) or 0
            total_equity = bal.get("totalStockholdersEquity", 0) or 0
            cash = bal.get("cashAndCashEquivalentsAtCarryingValue", 0) or bal.get("cashAndShortTermInvestments", 0) or 0
            invested_capital = total_debt + total_equity - cash
            if invested_capital > 0 and nopat:
                roic = (nopat / invested_capital) * 100
        
        # Calculate Debt/Equity from balance sheet if 0 or None
        if (debt_equity is None or debt_equity == 0) and balance and isinstance(balance, list) and len(balance) > 0:
            bal = balance[0]
            total_debt = bal.get("totalDebt", 0) or 0
            total_equity = bal.get("totalStockholdersEquity", 0) or 0
            if total_equity > 0:
                debt_equity = total_debt / total_equity
        
        # Convert decimals to percentages for display
        roe_display = f"{roe * 100:.2f}%" if roe is not None and roe != 0 and abs(roe) < 1 else f"{roe:.2f}%" if roe is not None and roe != 0 else "N/A"
        roa_display = f"{roa * 100:.2f}%" if roa is not None and roa != 0 and abs(roa) < 1 else f"{roa:.2f}%" if roa is not None and roa != 0 else "N/A"
        margin_display = f"{margin * 100:.2f}%" if margin is not None and abs(margin) < 1 else f"{margin:.2f}%" if margin is not None else "N/A"
        roic_display = f"{roic * 100:.2f}%" if roic is not None and abs(roic) < 1 else f"{roic:.2f}%" if roic is not None else "N/A"
        debt_equity_display = f"{debt_equity:.2f}" if debt_equity is not None and debt_equity != 0 else "N/A"
        
        report += f"- **ROE**: {roe_display}\n"
        report += f"- **ROA**: {roa_display}\n"
        report += f"- **Net Margin**: {margin_display}\n"
        report += f"- **ROIC**: {roic_display}\n"
        report += f"- **Debt/Equity**: {debt_equity_display}\n"
    
    data = result.get("data", {})
    report += _generate_growth_metrics_section(data, ticker)
    
    report += "\n### Valuation Metrics\n"
    quote = data.get("quote")
    key_metrics = data.get("keyMetrics")
    
    if ratios and isinstance(ratios, list) and len(ratios) > 0:
        r = ratios[0]
        pe = r.get('priceEarningsRatio')
        pb = r.get('priceToBookRatio')
        ps = r.get('priceToSalesRatio')
        
        # Calculate P/B from financials if 0
        if (pb is None or pb == 0) and quote and isinstance(quote, list) and len(quote) > 0 and balance and isinstance(balance, list) and len(balance) > 0:
            quote_data = quote[0]
            price = quote_data.get("price", 0)
            bal = balance[0]
            book_value = bal.get("totalStockholdersEquity", 0) or 0
            shares = r.get("sharesOutstanding") or (key_metrics[0].get("sharesOutstanding", 0) if key_metrics and isinstance(key_metrics, list) and len(key_metrics) > 0 else 0)
            if shares > 0:
                book_per_share = book_value / shares
                if book_per_share > 0:
                    pb = price / book_per_share
        
        pe_display = f"{pe:.2f}" if pe is not None and pe > 0 else "N/A"
        pb_display = f"{pb:.2f}" if pb is not None and pb > 0 else "N/A"
        ps_display = f"{ps:.2f}" if ps is not None and ps > 0 else "N/A"
        
        report += f"- **P/E**: {pe_display}\n"
        report += f"- **P/B**: {pb_display}\n"
        report += f"- **P/S**: {ps_display}\n"
    
    if key_metrics and isinstance(key_metrics, list) and len(key_metrics) > 0:
        km = key_metrics[0]
        fcf_yield = km.get('freeCashFlowYield')
        
        # Calculate FCF Yield from cash flow if 0 or None
        if (fcf_yield is None or fcf_yield == 0):
            cashflow = result.get("data", {}).get("cashflow")
            quote_data = quote[0] if quote and isinstance(quote, list) and len(quote) > 0 else {}
            market_cap = quote_data.get("marketCap") or quote_data.get("marketCapitalization", 0)
            if cashflow and isinstance(cashflow, list) and len(cashflow) > 0:
                cf = cashflow[0]
                fcf = cf.get("freeCashFlow")
                if fcf is None:
                    op_cf = cf.get("operatingCashFlow", 0) or 0
                    capex = abs(cf.get("capitalExpenditure", 0) or 0)
                    fcf = op_cf - capex
                if not market_cap and quote_data:
                    price = quote_data.get("price", 0)
                    shares = km.get("sharesOutstanding", 0) or 0
                    if price and shares:
                        market_cap = price * shares
                if fcf and market_cap and market_cap > 0:
                    fcf_yield = (fcf / market_cap) * 100
        
        fcf_yield_display = f"{fcf_yield * 100:.2f}%" if fcf_yield is not None and fcf_yield != 0 and abs(fcf_yield) < 1 else f"{fcf_yield:.2f}%" if fcf_yield is not None and fcf_yield != 0 else "N/A"
        report += f"- **FCF Yield**: {fcf_yield_display}\n"
        report += _generate_margin_of_safety_section(data, ratios, is_growth_company)
    
    report += "\n### Health Metrics\n"
    if ratios and isinstance(ratios, list) and len(ratios) > 0:
        r = ratios[0]
        current_ratio = r.get('currentRatio')
        
        # Calculate Current Ratio from balance sheet if 0 or None
        if (current_ratio is None or current_ratio == 0) and balance and isinstance(balance, list) and len(balance) > 0:
            bal = balance[0]
            current_assets = bal.get("totalCurrentAssets", 0) or 0
            current_liabilities = bal.get("totalCurrentLiabilities", 0) or 0
            if current_liabilities > 0:
                current_ratio = current_assets / current_liabilities
            elif current_assets > 0:
                current_ratio = 10.0  # Excellent liquidity (no current liabilities)
        
        current_ratio_display = f"{current_ratio:.2f}" if current_ratio is not None and current_ratio != 0 else "N/A"
        report += f"- **Current Ratio**: {current_ratio_display}\n"
        interest_cov = r.get('interestCoverage')
        # Handle case where 0 means no interest expense (excellent coverage)
        if interest_cov == 0:
            income = result.get("data", {}).get("income")
            if income and isinstance(income, list) and len(income) > 0:
                inc = income[0]
                interest_expense = abs(inc.get("interestExpense", 0) or 0)
                if interest_expense == 0:
                    interest_cov_display = "∞ (No Interest Expense)"
                else:
                    interest_cov_display = "0"
            else:
                interest_cov_display = "0"
        else:
            interest_cov_display = f"{interest_cov:.2f}" if interest_cov is not None else "N/A"
        report += f"- **Interest Coverage**: {interest_cov_display}\n"
    
    report += _generate_shareholder_metrics_section(data)
    
    report += f"""

---

## Recommendation

"""
    
    if scores['composite'] >= 70:
        recommendation = "**BUY / STRONG HOLD** — High composite score indicates strong fundamentals across multiple dimensions."
    elif scores['composite'] >= 60:
        recommendation = "**HOLD** — Solid score with some areas for improvement."
    elif scores['composite'] >= 50:
        recommendation = "**HOLD / CONSIDER REDUCING** — Below-average score; monitor closely."
    else:
        recommendation = "**AVOID / CONSIDER SELLING** — Low composite score indicates significant concerns."
    
    report += recommendation
    
    report += f"""

---

*Scoring system: Quality (ROE, ROA, Margin, ROIC, Debt), Growth (Revenue, Earnings, FCF), Value (PE, PB, PS, FCF Yield, Margin of Safety), Health (Debt, Liquidity, Coverage), Shareholder (Div Yield, Div Growth, Buybacks, Debt Paydown). Composite = average of 5 components. Grade thresholds: A+ (90+), A (85+), A- (80+), B+ (75+), B (70+), B- (65+), C+ (60+), C (55+), C- (50+), D+ (45+), D (40+), F (<40).*
"""
    
    output_path.write_text(report, encoding="utf-8")
    print(f"Report written to {output_path}", file=sys.stderr)


def generate_portfolio_report(results: List[Dict], output_path: Path):
    """Generate portfolio-wide summary report."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    report = f"""# Portfolio Stock Scores — {date_str}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Holdings Scored:** {len(results)}

---

## Portfolio Score Summary

| Ticker | Company | Composite | Grade | Quality | Growth | Value | Health | Shareholder |
|--------|---------|-----------|-------|---------|--------|-------|--------|-------------|
"""
    
    # Sort by composite score descending
    sorted_results = sorted(results, key=lambda x: x["scores"]["composite"], reverse=True)
    
    for r in sorted_results:
        scores = r["scores"]
        report += f"| {r['ticker']} | {r['companyName'][:30]} | {scores['composite']:.1f} | {r['grade']} | {scores['quality']:.1f} | {scores['growth']:.1f} | {scores['value']:.1f} | {scores['health']:.1f} | {scores['shareholder']:.1f} |\n"
    
    # Calculate averages
    avg_composite = sum(r["scores"]["composite"] for r in results) / len(results)
    avg_quality = sum(r["scores"]["quality"] for r in results) / len(results)
    avg_growth = sum(r["scores"]["growth"] for r in results) / len(results)
    avg_value = sum(r["scores"]["value"] for r in results) / len(results)
    avg_health = sum(r["scores"]["health"] for r in results) / len(results)
    avg_shareholder = sum(r["scores"]["shareholder"] for r in results) / len(results)
    
    report += f"""
| **AVERAGE** | — | **{avg_composite:.1f}** | **{get_grade(avg_composite)}** | {avg_quality:.1f} | {avg_growth:.1f} | {avg_value:.1f} | {avg_health:.1f} | {avg_shareholder:.1f} |

---

## Portfolio Health

- **Average Composite Score**: {avg_composite:.2f} ({get_grade(avg_composite)})
- **Holdings with A/A- Grade**: {sum(1 for r in results if r['grade'] in ['A+', 'A', 'A-'])}
- **Holdings with B/B- Grade**: {sum(1 for r in results if r['grade'] in ['B+', 'B', 'B-'])}
- **Holdings with C/C- Grade**: {sum(1 for r in results if r['grade'] in ['C+', 'C', 'C-'])}
- **Holdings with D/F Grade**: {sum(1 for r in results if r['grade'] in ['D+', 'D', 'F'])}

---

## Action Items

### Holdings Requiring Review (Composite Score < 50)

"""
    
    low_scores = [r for r in results if r["scores"]["composite"] < 50]
    if low_scores:
        for r in low_scores:
            report += f"- **{r['ticker']}** ({r['companyName']}): Composite {r['scores']['composite']:.1f} ({r['grade']}) — {', '.join(r['weaknesses']) if r['weaknesses'] else 'Multiple concerns'}\n"
    else:
        report += "*No holdings below threshold.*\n"
    
    report += "\n### Top Performers (Composite Score >= 75)\n\n"
    
    top_scores = [r for r in results if r["scores"]["composite"] >= 75]
    if top_scores:
        for r in top_scores:
            report += f"- **{r['ticker']}** ({r['companyName']}): Composite {r['scores']['composite']:.1f} ({r['grade']}) — {', '.join(r['strengths']) if r['strengths'] else 'Strong overall'}\n"
    else:
        report += "*No holdings above threshold.*\n"
    
    report += f"""

---

*Individual reports available in `outputs/stock-score-{{TICKER}}-{date_str}.md`*
"""
    
    output_path.write_text(report, encoding="utf-8")
    print(f"Portfolio report written to {output_path}", file=sys.stderr)


def get_portfolio_holdings() -> List[str]:
    """Extract ticker symbols from portfolio-details.md."""
    portfolio_file = CONTEXT / "portfolio-details.md"
    if not portfolio_file.exists():
        return []
    
    text = portfolio_file.read_text(encoding="utf-8")
    # Extract symbols from the positions table
    import re
    # Look for table rows with SYMBOL column
    pattern = r'\|\s*([A-Z]{1,5})\s*\|'  # Match ticker symbols in table
    matches = re.findall(pattern, text)
    # Filter out headers and common words
    symbols = [m for m in matches if m not in ['SYMBOL', 'TOTAL', 'AVERAGE', 'DATE']]
    # Remove duplicates while preserving order
    seen = set()
    unique_symbols = []
    for s in symbols:
        if s not in seen:
            seen.add(s)
            unique_symbols.append(s)
    return unique_symbols


def main():
    ap = argparse.ArgumentParser(description="Score stocks using Quality, Growth, Value, Health, Shareholder metrics.")
    ap.add_argument("tickers", nargs="*", help="Ticker symbol(s) to score")
    ap.add_argument("--portfolio", action="store_true", help="Score all portfolio holdings from context/portfolio-details.md")
    args = ap.parse_args()
    
    tickers = []
    if args.portfolio:
        tickers = get_portfolio_holdings()
        if not tickers:
            print("No portfolio holdings found in context/portfolio-details.md", file=sys.stderr)
            sys.exit(1)
        print(f"Scoring {len(tickers)} portfolio holdings: {', '.join(tickers)}", file=sys.stderr)
    elif args.tickers:
        tickers = args.tickers
    else:
        ap.print_help()
        sys.exit(1)
    
    OUTPUTS.mkdir(exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    results = []
    
    for ticker in tickers:
        try:
            result = score_ticker(ticker.upper())
            results.append(result)
            
            # Generate individual report
            report_path = OUTPUTS / f"stock-score-{ticker.upper()}-{date_str}.md"
            generate_report(result, report_path)
            
        except Exception as e:
            print(f"Error scoring {ticker}: {e}", file=sys.stderr)
            continue
    
    # Generate portfolio summary if scoring multiple
    if len(results) > 1:
        portfolio_report_path = OUTPUTS / f"portfolio-scores-{date_str}.md"
        generate_portfolio_report(results, portfolio_report_path)
    
    # Print summary
    print("\n" + "=" * 60, file=sys.stderr)
    print("SCORING SUMMARY", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    for r in sorted(results, key=lambda x: x["scores"]["composite"], reverse=True):
        print(f"{r['ticker']:6s} | {r['grade']:3s} | {r['scores']['composite']:5.1f} | {r['companyName'][:40]}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)


if __name__ == "__main__":
    main()
