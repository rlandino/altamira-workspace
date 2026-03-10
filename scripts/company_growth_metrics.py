#!/usr/bin/env python3
"""
Company Growth Metrics — Fetch FMP annual data and compute 3yr CAGR, latest YoY,
and optional metrics (margins, Rule of 40, ROE, FCF growth, trajectory) for /company-growth.
Outputs JSON with core four, optional metrics, and suggested grade (A–F).

Usage:
    python scripts/company_growth_metrics.py --ticker AVGO
    python scripts/company_growth_metrics.py --ticker MSFT --out outputs/company-growth-MSFT-metrics.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
except ImportError:
    print("Install requests: pip install requests", file=sys.stderr)
    sys.exit(1)

WORKSPACE = Path(__file__).resolve().parent.parent
FMP_API_KEY = "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz"
FMP_BASE = "https://financialmodelingprep.com/api/v3"


def _get(ticker: str, endpoint: str, limit: int = 5) -> Optional[List[Dict]]:
    url = f"{FMP_BASE}/{endpoint}?period=annual&limit={limit}&apikey={FMP_API_KEY}"
    if "period=" not in endpoint:
        url = f"{FMP_BASE}/{endpoint}?limit={limit}&apikey={FMP_API_KEY}"
    try:
        r = requests.get(url.replace("{TICKER}", ticker), timeout=15)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list) and len(data) > 0:
            return sorted(data, key=lambda x: x.get("date", "") or "")
        return data if isinstance(data, list) else None
    except Exception as e:
        print(f"Warning: {endpoint}: {e}", file=sys.stderr)
        return None


def _safe_div(num: float, denom: float) -> Optional[float]:
    if denom is None or denom == 0:
        return None
    return num / denom


def _cagr3(v_latest: Optional[float], v_3y_ago: Optional[float]) -> Optional[float]:
    if v_latest is None or v_3y_ago is None or v_3y_ago <= 0:
        return None
    if v_latest <= 0:
        return None
    return (float(v_latest) / float(v_3y_ago)) ** (1 / 3) - 1


def _yoy(v_latest: Optional[float], v_prior: Optional[float]) -> Optional[float]:
    if v_latest is None or v_prior is None:
        return None
    try:
        p = float(v_prior)
    except (TypeError, ValueError):
        return None
    if p == 0:
        return None
    return (float(v_latest) - p) / abs(p)


def _sub_grade_revenue_cagr(cagr: Optional[float]) -> int:
    if cagr is None:
        return 2
    c = cagr * 100
    if c >= 15:
        return 5
    if c >= 10:
        return 4
    if c >= 5:
        return 3
    if c >= 0:
        return 2
    return 1


def _sub_grade_eps_cagr(cagr: Optional[float]) -> int:
    if cagr is None:
        return 2
    c = cagr * 100
    if c >= 15:
        return 5
    if c >= 10:
        return 4
    if c >= 5:
        return 3
    if c >= 0:
        return 2
    return 1


def _sub_grade_fcf_margin(latest_pct: Optional[float], yoy_pp: Optional[float]) -> int:
    if latest_pct is None:
        return 2
    p = latest_pct
    if p > 15 and (yoy_pp is None or yoy_pp >= 0):
        return 5
    if p > 10:
        return 4
    if p > 5:
        return 3
    if p > 0:
        return 2
    return 1


def _sub_grade_roic(latest_pct: Optional[float], yoy: Optional[float]) -> int:
    if latest_pct is None:
        return 2
    p = latest_pct
    if p >= 20:
        return 5
    if p >= 15:
        return 4
    if p >= 10:
        return 3
    if p >= 5:
        return 2
    return 1


def _avg_grade(grades: List[int]) -> str:
    if not grades:
        return "C"
    avg = sum(grades) / len(grades)
    if avg >= 4.5:
        return "A"
    if avg >= 3.5:
        return "B"
    if avg >= 2.5:
        return "C"
    if avg >= 1.5:
        return "D"
    return "F"


def fetch_and_compute(ticker: str) -> Dict[str, Any]:
    ticker = ticker.upper()
    income = _get(ticker, "income-statement/{TICKER}")
    cashflow = _get(ticker, "cash-flow-statement/{TICKER}")
    key_metrics = _get(ticker, "key-metrics/{TICKER}")
    ratios = _get(ticker, "ratios/{TICKER}")
    growth = _get(ticker, "financial-growth/{TICKER}")
    balance = _get(ticker, "balance-sheet-statement/{TICKER}")

    out: Dict[str, Any] = {
        "ticker": ticker,
        "core_four": {},
        "optional": {},
        "suggested_grade": "C",
        "rule_of_40": None,
        "revenue_trajectory": None,
    }

    if not income or len(income) < 2:
        return out

    # Align by date: assume FMP returns newest first; we want oldest first for T-3, T-2, T-1, T
    income = sorted(income, key=lambda x: x.get("date", "") or "")
    n = len(income)
    rev_t = income[-1].get("revenue")
    rev_t1 = income[-2].get("revenue") if n >= 2 else None
    rev_t3 = income[-4].get("revenue") if n >= 4 else None

    # Revenue
    rev_cagr = _cagr3(rev_t, rev_t3)
    rev_yoy = _yoy(rev_t, rev_t1)
    out["core_four"]["revenue"] = {
        "3yr_cagr_pct": round(rev_cagr * 100, 2) if rev_cagr is not None else None,
        "latest_yoy_pct": round(rev_yoy * 100, 2) if rev_yoy is not None else None,
        "latest_value": rev_t,
    }

    # EPS: net income / shares
    ni_t = income[-1].get("netIncome")
    ni_t1 = income[-2].get("netIncome") if n >= 2 else None
    ni_t3 = income[-4].get("netIncome") if n >= 4 else None
    shares = None
    if key_metrics and len(key_metrics) > 0:
        shares = key_metrics[-1].get("weightedAverageShares") or key_metrics[-1].get("numberOfShares")
    if shares is None and income[-1].get("weightedAverageShsOut") is not None:
        shares = income[-1]["weightedAverageShsOut"]
    if ni_t is not None and shares and shares > 0:
        eps_t = ni_t / shares
        eps_t1 = (ni_t1 / shares) if ni_t1 is not None and shares else None
        eps_t3 = (ni_t3 / shares) if ni_t3 is not None and n >= 4 and shares else None
        eps_cagr = _cagr3(eps_t, eps_t3)
        eps_yoy = _yoy(eps_t, eps_t1)
        out["core_four"]["eps"] = {
            "3yr_cagr_pct": round(eps_cagr * 100, 2) if eps_cagr is not None else None,
            "latest_yoy_pct": round(eps_yoy * 100, 2) if eps_yoy is not None else None,
            "latest_value": round(eps_t, 4),
        }
    else:
        out["core_four"]["eps"] = {"3yr_cagr_pct": None, "latest_yoy_pct": None, "latest_value": None}

    # FCF margin
    if cashflow and len(cashflow) >= 2:
        cf = cashflow[-1]
        cf1 = cashflow[-2]
        ocf = cf.get("operatingCashFlow") or 0
        capex = cf.get("capitalExpenditure") or 0
        fcf = ocf - capex
        rev = income[-1].get("revenue") or 1
        fcf_margin_t = (fcf / rev) * 100 if rev else None
        ocf1 = cf1.get("operatingCashFlow") or 0
        capex1 = cf1.get("capitalExpenditure") or 0
        fcf1 = ocf1 - capex1
        rev1 = income[-2].get("revenue") or 1
        fcf_margin_t1 = (fcf1 / rev1) * 100 if rev1 else None
        fcf_margin_t3 = None
        if len(cashflow) >= 4 and len(income) >= 4:
            cf3 = cashflow[-4]
            ocf3 = cf3.get("operatingCashFlow") or 0
            capex3 = cf3.get("capitalExpenditure") or 0
            rev3 = income[-4].get("revenue") or 1
            fcf_margin_t3 = ((ocf3 - capex3) / rev3) * 100 if rev3 else None
        fcf_cagr = _cagr3(fcf_margin_t, fcf_margin_t3)
        fcf_yoy_pp = (fcf_margin_t - fcf_margin_t1) if (fcf_margin_t is not None and fcf_margin_t1 is not None) else None
        out["core_four"]["fcf_margin"] = {
            "3yr_cagr_pct": round(fcf_cagr * 100, 2) if fcf_cagr is not None else None,
            "latest_yoy_pp": round(fcf_yoy_pp, 2) if fcf_yoy_pp is not None else None,
            "latest_value_pct": round(fcf_margin_t, 2) if fcf_margin_t is not None else None,
        }
    else:
        out["core_four"]["fcf_margin"] = {"3yr_cagr_pct": None, "latest_yoy_pp": None, "latest_value_pct": None}

    # ROIC
    roic_t = None
    roic_t1 = None
    roic_t3 = None
    if key_metrics and len(key_metrics) > 0:
        for i, m in enumerate(key_metrics):
            v = m.get("returnOnInvestedCapital") or m.get("returnOnCapitalEmployed")
            if v is not None:
                v = v * 100 if abs(v) < 1.5 else v
            if i == len(key_metrics) - 1:
                roic_t = v
            elif i == len(key_metrics) - 2:
                roic_t1 = v
            elif len(key_metrics) >= 4 and i == len(key_metrics) - 4:
                roic_t3 = v
    if ratios and len(ratios) > 0 and roic_t is None:
        roic_t = ratios[-1].get("returnOnInvestedCapital") or ratios[-1].get("returnOnCapitalEmployed")
        if roic_t is not None and abs(roic_t) < 1.5:
            roic_t = roic_t * 100
        if len(ratios) >= 2:
            roic_t1 = ratios[-2].get("returnOnInvestedCapital") or ratios[-2].get("returnOnCapitalEmployed")
            if roic_t1 is not None and abs(roic_t1) < 1.5:
                roic_t1 = roic_t1 * 100
        if len(ratios) >= 4:
            roic_t3 = ratios[-4].get("returnOnInvestedCapital") or ratios[-4].get("returnOnCapitalEmployed")
            if roic_t3 is not None and abs(roic_t3) < 1.5:
                roic_t3 = roic_t3 * 100
    roic_cagr = _cagr3(roic_t, roic_t3)
    roic_yoy = _yoy(roic_t, roic_t1)
    out["core_four"]["roic"] = {
        "3yr_cagr_pct": round(roic_cagr * 100, 2) if roic_cagr is not None else None,
        "latest_yoy_pct": round(roic_yoy * 100, 2) if roic_yoy is not None else None,
        "latest_value_pct": round(roic_t, 2) if roic_t is not None else None,
    }

    # Grade from core four
    rev_cagr_for_grade = (rev_cagr * 100) if rev_cagr is not None else None
    eps_cagr_for_grade = out["core_four"]["eps"].get("3yr_cagr_pct")
    if eps_cagr_for_grade is None and out["core_four"]["eps"].get("latest_value") is not None:
        eps_cagr_for_grade = (rev_cagr * 100) if rev_cagr is not None else None  # fallback
    fcf_latest = out["core_four"]["fcf_margin"].get("latest_value_pct")
    fcf_yoy_pp = out["core_four"]["fcf_margin"].get("latest_yoy_pp")
    sub_grades = [
        _sub_grade_revenue_cagr(rev_cagr),
        _sub_grade_eps_cagr(eps_cagr_for_grade / 100.0 if eps_cagr_for_grade is not None else None),
        _sub_grade_fcf_margin(fcf_latest, fcf_yoy_pp),
        _sub_grade_roic(roic_t, roic_yoy * 100 if roic_yoy is not None else None),
    ]
    out["suggested_grade"] = _avg_grade(sub_grades)

    # Optional: operating margin, net income growth, gross margin, EBITDA margin, ROE, FCF $, Rule of 40, trajectory
    if income and len(income) >= 2:
        op_inc = income[-1].get("operatingIncome")
        rev = income[-1].get("revenue") or 1
        op_margin_t = (op_inc / rev) * 100 if op_inc is not None and rev else None
        op_inc1 = income[-2].get("operatingIncome")
        rev1 = income[-2].get("revenue") or 1
        op_margin_t1 = (op_inc1 / rev1) * 100 if op_inc1 is not None and rev1 else None
        out["optional"]["operating_margin_pct"] = round(op_margin_t, 2) if op_margin_t is not None else None
        out["optional"]["operating_margin_yoy_pp"] = round(op_margin_t - op_margin_t1, 2) if (op_margin_t is not None and op_margin_t1 is not None) else None

        gp = income[-1].get("grossProfit")
        out["optional"]["gross_margin_pct"] = round((gp / rev) * 100, 2) if (gp is not None and rev) else None

        ni_yoy = _yoy(ni_t, ni_t1)
        out["optional"]["net_income_yoy_pct"] = round(ni_yoy * 100, 2) if ni_yoy is not None else None
        ni_t3 = income[-4].get("netIncome") if len(income) >= 4 else None
        ni_cagr = _cagr3(ni_t, ni_t3)
        out["optional"]["net_income_3yr_cagr_pct"] = round(ni_cagr * 100, 2) if ni_cagr is not None else None

    if cashflow and income and len(cashflow) >= 2:
        fcf_t = (cashflow[-1].get("operatingCashFlow") or 0) - (cashflow[-1].get("capitalExpenditure") or 0)
        fcf_t1 = (cashflow[-2].get("operatingCashFlow") or 0) - (cashflow[-2].get("capitalExpenditure") or 0)
        fcf_t3 = None
        if len(cashflow) >= 4:
            fcf_t3 = (cashflow[-4].get("operatingCashFlow") or 0) - (cashflow[-4].get("capitalExpenditure") or 0)
        fcf_dollar_cagr = _cagr3(fcf_t, fcf_t3)
        fcf_dollar_yoy = _yoy(fcf_t, fcf_t1)
        out["optional"]["fcf_dollar_3yr_cagr_pct"] = round(fcf_dollar_cagr * 100, 2) if fcf_dollar_cagr is not None else None
        out["optional"]["fcf_dollar_yoy_pct"] = round(fcf_dollar_yoy * 100, 2) if fcf_dollar_yoy is not None else None

    if ratios and len(ratios) > 0:
        roe = ratios[-1].get("returnOnEquity")
        if roe is not None and abs(roe) < 1.5:
            roe = roe * 100
        out["optional"]["roe_pct"] = round(roe, 2) if roe is not None else None

    # Rule of 40
    rev_growth_pct = (rev_yoy * 100) if rev_yoy is not None else None
    op_margin_pct = out["optional"].get("operating_margin_pct")
    if rev_growth_pct is not None and op_margin_pct is not None:
        rule40 = rev_growth_pct + op_margin_pct
        out["rule_of_40"] = {
            "score": round(rule40, 1),
            "tier": "Elite" if rule40 >= 40 else "Solid" if rule40 >= 20 else "Weak",
        }

    # Revenue trajectory: compare YoY changes over last 3 years
    if income and len(income) >= 4:
        yoys = []
        for i in range(len(income) - 1, 0, -1):
            a, b = income[i].get("revenue"), income[i - 1].get("revenue")
            if a and b and b != 0:
                yoys.append((float(a) - float(b)) / float(b))
        if len(yoys) >= 2:
            out["revenue_trajectory"] = "Accelerating" if yoys[0] > yoys[-1] else "Decelerating"

    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Company growth metrics for /company-growth")
    ap.add_argument("--ticker", "-t", required=True, help="Ticker symbol")
    ap.add_argument("--out", "-o", help="Write JSON to file (default: stdout)")
    args = ap.parse_args()
    result = fetch_and_compute(args.ticker)
    s = json.dumps(result, indent=2)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(s, encoding="utf-8")
        print(f"Wrote {args.out}", file=sys.stderr)
    else:
        print(s)


if __name__ == "__main__":
    main()
