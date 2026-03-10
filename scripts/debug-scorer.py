#!/usr/bin/env python3
"""
Debug script to show detailed scoring calculations for a ticker.
"""

import sys
import json
import importlib.util
from pathlib import Path

# Import stock-scorer module directly
spec = importlib.util.spec_from_file_location("stock_scorer", Path(__file__).parent / "stock-scorer.py")
stock_scorer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stock_scorer)

fetch_fmp_data = stock_scorer.fetch_fmp_data
calculate_quality_score = stock_scorer.calculate_quality_score
calculate_growth_score = stock_scorer.calculate_growth_score
calculate_value_score = stock_scorer.calculate_value_score
calculate_health_score = stock_scorer.calculate_health_score
calculate_shareholder_score = stock_scorer.calculate_shareholder_score
normalize_score = stock_scorer.normalize_score
QUALITY_WEIGHTS = stock_scorer.QUALITY_WEIGHTS
GROWTH_WEIGHTS = stock_scorer.GROWTH_WEIGHTS
VALUE_WEIGHTS = stock_scorer.VALUE_WEIGHTS
HEALTH_WEIGHTS = stock_scorer.HEALTH_WEIGHTS
SHAREHOLDER_WEIGHTS = stock_scorer.SHAREHOLDER_WEIGHTS

def normalize_score_debug(value: float, min_val: float, max_val: float, invert: bool = False, metric_name: str = "") -> tuple:
    """Normalize with debug output."""
    if value is None or min_val is None or max_val is None:
        result = 50.0
        explanation = f"{metric_name}: Missing data (defaulting to 50.0)"
        return result, explanation
    if max_val == min_val:
        result = 50.0
        explanation = f"{metric_name}: Max == Min (defaulting to 50.0)"
        return result, explanation
    normalized = ((value - min_val) / (max_val - min_val)) * 100
    if invert:
        normalized = 100 - normalized
    result = max(0, min(100, normalized))
    explanation = f"{metric_name}: {value:.4f} -> normalized to {result:.2f} (range: {min_val:.2f}-{max_val:.2f}, invert={invert})"
    return result, explanation

def debug_quality_score(data) -> tuple:
    """Debug Quality Score calculation."""
    ratios = data.get("ratios")
    if not ratios or not isinstance(ratios, list) or len(ratios) == 0:
        return 50.0, ["No ratios data available"]
    
    latest = ratios[0]
    scores = {}
    explanations = []
    
    # ROE
    roe = latest.get("returnOnEquity")
    if roe is not None:
        roe_raw = roe
        if abs(roe) < 1:
            roe = roe * 100
        score, exp = normalize_score_debug(roe, 0, 50, False, "ROE")
        scores["roe"] = score
        explanations.append(f"ROE: Raw={roe_raw:.4f}, Converted={roe:.2f}%, {exp}")
    
    # ROA
    roa = latest.get("returnOnAssets")
    if roa is not None:
        roa_raw = roa
        if abs(roa) < 1:
            roa = roa * 100
        score, exp = normalize_score_debug(roa, 0, 25, False, "ROA")
        scores["roa"] = score
        explanations.append(f"ROA: Raw={roa_raw:.4f}, Converted={roa:.2f}%, {exp}")
    
    # Net Income Margin
    margin = latest.get("netProfitMargin")
    if margin is None:
        margin = latest.get("netIncomeMargin")
    if margin is not None:
        margin_raw = margin
        if abs(margin) < 1:
            margin = margin * 100
        score, exp = normalize_score_debug(margin, -10, 30, False, "Net Margin")
        scores["margin"] = score
        explanations.append(f"Net Margin: Raw={margin_raw:.4f}, Converted={margin:.2f}%, {exp}")
    
    # ROIC
    roic = latest.get("returnOnInvestedCapital")
    if roic is not None:
        roic_raw = roic
        if abs(roic) < 1:
            roic = roic * 100
        score, exp = normalize_score_debug(roic, 0, 40, False, "ROIC")
        scores["roic"] = score
        explanations.append(f"ROIC: Raw={roic_raw:.4f}, Converted={roic:.2f}%, {exp}")
    
    # Debt/Total Capital (inverted)
    debt_equity = latest.get("debtEquityRatio")
    if debt_equity is not None:
        score, exp = normalize_score_debug(debt_equity, 0, 1, True, "Debt/Equity (inverted)")
        scores["debtCapital"] = score
        explanations.append(f"Debt/Equity: Raw={debt_equity:.4f}, {exp}")
    
    # Weighted sum
    total = 0.0
    weight_sum = 0.0
    weighted_details = []
    for metric, weight in QUALITY_WEIGHTS.items():
        if metric in scores:
            contribution = scores[metric] * weight
            total += contribution
            weight_sum += weight
            weighted_details.append(f"  {metric}: {scores[metric]:.2f} × {weight:.2f} = {contribution:.2f}")
    
    final_score = total / weight_sum if weight_sum > 0 else 50.0
    explanations.append(f"\nWeighted Calculation:")
    explanations.extend(weighted_details)
    explanations.append(f"Total: {total:.2f} / Weight Sum: {weight_sum:.2f} = {final_score:.2f}")
    
    return final_score, explanations

def debug_value_score(data) -> tuple:
    """Debug Value Score calculation."""
    ratios = data.get("ratios")
    quote = data.get("quote")
    key_metrics = data.get("keyMetrics")
    
    if not ratios or not isinstance(ratios, list) or len(ratios) == 0:
        return 50.0, ["No ratios data available"]
    
    latest = ratios[0]
    scores = {}
    explanations = []
    
    # P/E (inverted)
    pe = latest.get("priceEarningsRatio")
    if pe is not None and pe > 0:
        score, exp = normalize_score_debug(pe, 5, 50, True, "P/E (inverted)")
        scores["pe"] = score
        explanations.append(f"P/E: Raw={pe:.2f}, {exp}")
    
    # P/B (inverted)
    pb = latest.get("priceToBookRatio")
    if pb is not None and pb > 0:
        score, exp = normalize_score_debug(pb, 0.5, 10, True, "P/B (inverted)")
        scores["pb"] = score
        explanations.append(f"P/B: Raw={pb:.2f}, {exp}")
    
    # P/S (inverted)
    ps = latest.get("priceToSalesRatio")
    if ps is not None and ps > 0:
        score, exp = normalize_score_debug(ps, 0.5, 15, True, "P/S (inverted)")
        scores["ps"] = score
        explanations.append(f"P/S: Raw={ps:.2f}, {exp}")
    
    # FCF Yield
    fcf_yield = None
    if key_metrics and isinstance(key_metrics, list) and len(key_metrics) > 0:
        fcf_yield = key_metrics[0].get("freeCashFlowYield")
    if fcf_yield is None:
        cashflow = data.get("cashflow")
        quote_data = quote[0] if quote and isinstance(quote, list) and len(quote) > 0 else {}
        if cashflow and isinstance(cashflow, list) and len(cashflow) > 0:
            fcf = cashflow[0].get("freeCashFlow") or (cashflow[0].get("operatingCashFlow", 0) - cashflow[0].get("capitalExpenditure", 0))
            market_cap = quote_data.get("marketCap") or quote_data.get("marketCapitalization", 0)
            if market_cap and market_cap > 0:
                fcf_yield = (fcf / market_cap) * 100
    if fcf_yield is not None:
        fcf_yield_raw = fcf_yield
        if abs(fcf_yield) < 1:
            fcf_yield = fcf_yield * 100
        score, exp = normalize_score_debug(fcf_yield, 0, 15, False, "FCF Yield")
        scores["fcf"] = score
        explanations.append(f"FCF Yield: Raw={fcf_yield_raw:.4f}, Converted={fcf_yield:.2f}%, {exp}")
    
    # Margin of Safety
    margin_of_safety = None
    if pe is not None:
        fair_pe = 17.5
        if pe < fair_pe:
            margin_of_safety = ((fair_pe - pe) / fair_pe) * 100
        else:
            margin_of_safety = -((pe - fair_pe) / fair_pe) * 100
    if margin_of_safety is not None:
        score, exp = normalize_score_debug(margin_of_safety, -50, 50, False, "Margin of Safety")
        scores["marginOfSafety"] = score
        explanations.append(f"Margin of Safety: Raw={margin_of_safety:.2f}%, {exp}")
    
    # Weighted sum
    total = 0.0
    weight_sum = 0.0
    weighted_details = []
    for metric, weight in VALUE_WEIGHTS.items():
        if metric in scores:
            contribution = scores[metric] * weight
            total += contribution
            weight_sum += weight
            weighted_details.append(f"  {metric}: {scores[metric]:.2f} × {weight:.2f} = {contribution:.2f}")
    
    final_score = total / weight_sum if weight_sum > 0 else 50.0
    explanations.append(f"\nWeighted Calculation:")
    explanations.extend(weighted_details)
    explanations.append(f"Total: {total:.2f} / Weight Sum: {weight_sum:.2f} = {final_score:.2f}")
    
    return final_score, explanations

def main():
    if len(sys.argv) < 2:
        print("Usage: python debug-scorer.py TICKER")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    print(f"\n{'='*80}")
    print(f"DEBUGGING SCORE CALCULATIONS FOR {ticker}")
    print(f"{'='*80}\n")
    
    print("Fetching data from FMP API...")
    data = fetch_fmp_data(ticker)
    
    # Show raw metrics
    print("\n" + "="*80)
    print("RAW METRICS FROM FMP API")
    print("="*80)
    
    ratios = data.get("ratios")
    if ratios and isinstance(ratios, list) and len(ratios) > 0:
        print("\n### Ratios (Latest Year):")
        r = ratios[0]
        print(f"  ROE: {r.get('returnOnEquity', 'N/A')}")
        print(f"  ROA: {r.get('returnOnAssets', 'N/A')}")
        print(f"  Net Profit Margin: {r.get('netProfitMargin', 'N/A')}")
        print(f"  ROIC: {r.get('returnOnInvestedCapital', 'N/A')}")
        print(f"  Debt/Equity: {r.get('debtEquityRatio', 'N/A')}")
        print(f"  P/E: {r.get('priceEarningsRatio', 'N/A')}")
        print(f"  P/B: {r.get('priceToBookRatio', 'N/A')}")
        print(f"  P/S: {r.get('priceToSalesRatio', 'N/A')}")
        print(f"  Current Ratio: {r.get('currentRatio', 'N/A')}")
        print(f"  Interest Coverage: {r.get('interestCoverage', 'N/A')}")
        print(f"  Dividend Yield: {r.get('dividendYield', 'N/A')}")
    
    key_metrics = data.get("keyMetrics")
    if key_metrics and isinstance(key_metrics, list) and len(key_metrics) > 0:
        print("\n### Key Metrics (Latest Year):")
        km = key_metrics[0]
        print(f"  FCF Yield: {km.get('freeCashFlowYield', 'N/A')}")
        print(f"  FCF Per Share: {km.get('freeCashFlowPerShare', 'N/A')}")
    
    growth = data.get("growth")
    if growth and isinstance(growth, list) and len(growth) >= 2:
        print("\n### Growth Metrics:")
        latest = growth[0]
        prev = growth[1]
        print(f"  Revenue Growth: {latest.get('revenueGrowth', 'N/A')}")
        print(f"  Net Income Growth: {latest.get('netIncomeGrowth', 'N/A')}")
        print(f"  Latest Revenue: {latest.get('revenue', 'N/A')}")
        print(f"  Previous Revenue: {prev.get('revenue', 'N/A')}")
    
    # Debug Quality Score
    print("\n" + "="*80)
    print("QUALITY SCORE CALCULATION")
    print("="*80)
    quality_score, quality_explanations = debug_quality_score(data)
    for exp in quality_explanations:
        print(exp)
    print(f"\nFINAL QUALITY SCORE: {quality_score:.2f}")
    
    # Debug Value Score
    print("\n" + "="*80)
    print("VALUE SCORE CALCULATION")
    print("="*80)
    value_score, value_explanations = debug_value_score(data)
    for exp in value_explanations:
        print(exp)
    print(f"\nFINAL VALUE SCORE: {value_score:.2f}")
    
    # Calculate other scores
    growth_score = calculate_growth_score(data)
    health_score = calculate_health_score(data)
    shareholder_score = calculate_shareholder_score(data)
    composite = (quality_score + growth_score + value_score + health_score + shareholder_score) / 5.0
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Quality Score:    {quality_score:.2f}")
    print(f"Growth Score:     {growth_score:.2f}")
    print(f"Value Score:      {value_score:.2f}")
    print(f"Health Score:     {health_score:.2f}")
    print(f"Shareholder Score: {shareholder_score:.2f}")
    print(f"Composite Score:  {composite:.2f}")
    print("="*80)

if __name__ == "__main__":
    main()
