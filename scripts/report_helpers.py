"""Helpers for stock score report generation: Growth Metrics and Margin of Safety sections."""
from typing import Dict, List, Optional


def report_growth_metrics(data: Dict) -> str:
    """Return Growth Metrics section text for the report."""
    out = "\n### Growth Metrics\n"
    growth = data.get("growth")
    cashflow = data.get("cashflow")
    km_list = data.get("keyMetrics")
    rev_growth = None
    if growth and isinstance(growth, list) and len(growth) >= 2:
        latest, prev = growth[0], growth[1]
        rev_growth = latest.get("revenueGrowth")
        if rev_growth is None:
            lr, pr = latest.get("revenue"), prev.get("revenue")
            if lr is not None and pr is not None and pr != 0:
                rev_growth = ((lr - pr) / abs(pr)) * 100
        elif rev_growth != 0 and -2 < rev_growth < 2:
            rev_growth = rev_growth * 100
    out += f"- **Revenue Growth (YoY)**: {f'{rev_growth:+.1f}%' if rev_growth is not None else 'N/A'}\n"
    earnings_growth = None
    if growth and isinstance(growth, list) and len(growth) >= 2:
        latest, prev = growth[0], growth[1]
        earnings_growth = latest.get("netIncomeGrowth")
        if earnings_growth is None:
            ln, pn = latest.get("netIncome"), prev.get("netIncome")
            if ln is not None and pn is not None and pn != 0:
                earnings_growth = ((ln - pn) / abs(pn)) * 100
        elif earnings_growth != 0 and -2 < earnings_growth < 2:
            earnings_growth = earnings_growth * 100
    out += f"- **Earnings Growth (YoY)**: {f'{earnings_growth:+.1f}%' if earnings_growth is not None else 'N/A'}\n"
    fcf_growth = None
    if cashflow and isinstance(cashflow, list) and len(cashflow) >= 2:
        f0 = cashflow[0].get("freeCashFlow") or (cashflow[0].get("operatingCashFlow", 0) or 0) - abs(cashflow[0].get("capitalExpenditure", 0) or 0)
        f1 = cashflow[1].get("freeCashFlow") or (cashflow[1].get("operatingCashFlow", 0) or 0) - abs(cashflow[1].get("capitalExpenditure", 0) or 0)
        if f1 and f1 != 0:
            fcf_growth = ((f0 - f1) / abs(f1)) * 100
    out += f"- **FCF Growth (YoY)**: {f'{fcf_growth:+.1f}%' if fcf_growth is not None else 'N/A'}\n"
    fcfps_growth = None
    if km_list and isinstance(km_list, list) and len(km_list) >= 2:
        fps0 = km_list[0].get("freeCashFlowPerShare")
        fps1 = km_list[1].get("freeCashFlowPerShare")
        if fps1 and fps1 != 0 and fps0 is not None:
            fcfps_growth = ((fps0 - fps1) / abs(fps1)) * 100
    out += f"- **FCF Per Share Growth (YoY)**: {f'{fcfps_growth:+.1f}%' if fcfps_growth is not None else 'N/A'}\n"
    return out


def report_margin_of_safety(data: Dict, ratios: Optional[list], quote: Optional[list], is_growth_company_fn) -> str:
    """Return Margin of Safety line(s) for Valuation section (P/E vs Fair P/E)."""
    pe_report = None
    if ratios and len(ratios) > 0:
        pe_report = ratios[0].get("priceEarningsRatio")
        if pe_report is None and quote and len(quote) > 0:
            price = quote[0].get("price", 0)
            eps = ratios[0].get("earningsPerShare")
            if eps and eps > 0:
                pe_report = price / eps
    if pe_report is None and data.get("massive_fallback"):
        mq = data["massive_fallback"].get("quote") or data["massive_fallback"].get("snapshot")
        if mq and ratios and len(ratios) > 0:
            price = mq.get("price") or mq.get("last") or mq.get("close")
            eps = ratios[0].get("earningsPerShare")
            if price and eps and eps > 0:
                pe_report = price / eps
    if pe_report is None or pe_report <= 0:
        return "- **Margin of Safety**: N/A (from fair P/E)\n"
    is_growth = is_growth_company_fn(data)
    fair_pe_used = 35 if is_growth else 18
    if pe_report < fair_pe_used:
        margin_pct = ((fair_pe_used - pe_report) / fair_pe_used) * 100
    else:
        margin_pct = -min(((pe_report - fair_pe_used) / fair_pe_used) * 100, 200)
    out = f"- **P/E (current)**: {pe_report:.1f} | **Fair P/E** (benchmark): {fair_pe_used}\n"
    out += f"- **Margin of Safety**: {margin_pct:+.1f}% (from fair P/E)\n"
    return out
