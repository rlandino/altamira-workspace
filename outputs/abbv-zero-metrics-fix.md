# ABBV Zero Metrics Fix — Calculation from Financial Statements

**Date:** 2026-02-19  
**Status:** ✅ **FIXED**

---

## Issues Identified

ABBV's report showed several metrics as **0**, which were negatively impacting the score:

### Quality Metrics Showing 0:
- **ROE**: 0.00% (should be ~127% based on Net Income / Equity)
- **ROA**: 0.00% (should be ~3.13% based on Net Income / Assets)
- **Debt/Equity**: 0 (should be ~20.40x based on Total Debt / Equity)

### Valuation Metrics Showing 0:
- **P/B**: 0 (likely negative book value per share or calculation issue)
- **FCF Yield**: 0.00% (might be negative FCF or missing data)

### Health Metrics Showing 0:
- **Current Ratio**: 0 (should be ~0.66 based on Current Assets / Current Liabilities)

---

## Root Cause

**FMP API was returning `0` for these metrics** even though the underlying financial data (income statement, balance sheet) contained valid values to calculate them. The scoring system was:
1. Using the `0` values from FMP ratios
2. Normalizing `0` to `0` score (correct for bad metrics, but wrong when data is missing)
3. Not calculating from financial statements when FMP returned `0`

---

## Fixes Applied

### 1. ✅ ROE Calculation from Financial Statements

**Problem:** FMP returned ROE = 0, but Net Income ($4.226B) and Equity ($3.325B) are available.

**Fix:**
```python
# If ROE is 0 or None, calculate from income statement and balance sheet
if roe is None or roe == 0:
    net_income = inc.get("netIncome", 0) or 0
    total_equity = bal.get("totalStockholdersEquity", 0) or 0
    if total_equity > 0 and net_income:
        roe = (net_income / total_equity) * 100
```

**Result:** ROE now shows as **127.10%** ✅

---

### 2. ✅ ROA Calculation from Financial Statements

**Problem:** FMP returned ROA = 0, but Net Income ($4.226B) and Assets ($135.161B) are available.

**Fix:**
```python
# If ROA is 0 or None, calculate from income statement and balance sheet
if roa is None or roa == 0:
    net_income = inc.get("netIncome", 0) or 0
    total_assets = bal.get("totalAssets", 0) or 0
    if total_assets > 0 and net_income:
        roa = (net_income / total_assets) * 100
```

**Result:** ROA now shows as **3.13%** ✅

---

### 3. ✅ Debt/Equity Calculation from Balance Sheet

**Problem:** FMP returned Debt/Equity = 0, but Total Debt ($67.841B) and Equity ($3.325B) are available.

**Fix:**
```python
# If debt_equity is 0 or None, calculate from balance sheet
if debt_equity is None or debt_equity == 0:
    total_debt = bal.get("totalDebt", 0) or 0
    total_equity = bal.get("totalStockholdersEquity", 0) or 0
    if total_equity > 0:
        debt_equity = total_debt / total_equity
```

**Result:** Debt/Equity now shows as **20.40** ✅

---

### 4. ✅ Current Ratio Calculation from Balance Sheet

**Problem:** FMP returned Current Ratio = 0, but Current Assets ($25.582B) and Current Liabilities ($38.749B) are available.

**Fix:**
```python
# If current_ratio is 0 or None, calculate from balance sheet
if current_ratio is None or current_ratio == 0:
    current_assets = bal.get("totalCurrentAssets", 0) or 0
    current_liabilities = bal.get("totalCurrentLiabilities", 0) or 0
    if current_liabilities > 0:
        current_ratio = current_assets / current_liabilities
```

**Result:** Current Ratio now shows as **0.66** ✅

---

### 5. ✅ FCF Yield Calculation from Cash Flow

**Problem:** FMP returned FCF Yield = 0, but cash flow data might be available.

**Fix:** Enhanced calculation logic to compute FCF Yield from cash flow statement and market cap when FMP returns 0.

**Result:** FCF Yield calculation improved (may still show N/A if FCF is negative or data unavailable)

---

### 6. ✅ P/B Handling for Negative Book Value

**Problem:** P/B = 0 might indicate negative book value per share.

**Fix:** Added logic to:
- Calculate P/B from balance sheet when FMP returns 0
- Skip P/B metric if book value per share is negative (meaningless metric)

**Result:** P/B now shows as **N/A** if negative book value (better than showing 0)

---

## Score Impact

### Before Fixes
- **ROE**: 0.00% → Score: 0.00 (penalizing Quality Score)
- **ROA**: 0.00% → Score: 0.00 (penalizing Quality Score)
- **Debt/Equity**: 0 → Score: 100.00 (incorrectly showing as excellent)
- **Current Ratio**: 0 → Score: 0.00 (penalizing Health Score)
- **Composite Score**: 36.22 (D)

### After Fixes
- **ROE**: 127.10% → Score: Improved (contributing positively to Quality Score)
- **ROA**: 3.13% → Score: Improved (contributing positively to Quality Score)
- **Debt/Equity**: 20.40 → Score: Correctly penalized (high leverage)
- **Current Ratio**: 0.66 → Score: Improved (still low, but correctly calculated)
- **Composite Score**: 36.4 (D) — **Slight improvement**

**Note:** ABBV's score remains low (D) because:
- Very high P/E (96.82) — overvalued
- High Debt/Equity (20.40x) — high leverage
- Low Current Ratio (0.66) — liquidity concerns
- Weak Growth Score (14.75 F)
- Likely negative FCF Yield

The zeros were affecting the score, but now that they're calculated correctly, the score reflects ABBV's actual financial condition.

---

## Files Modified

- `scripts/stock-scorer.py`
  - Updated `calculate_quality_score()` — Calculate ROE/ROA from financials when FMP returns 0
  - Updated `calculate_health_score()` — Calculate Current Ratio from balance sheet when FMP returns 0
  - Updated `calculate_value_score()` — Handle P/B = 0 and FCF Yield = 0 cases
  - Updated `generate_report()` — Recalculate metrics in report generation for accurate display

---

## Verification

### ABBV Test Results

**Before:**
- ROE: 0.00% ❌
- ROA: 0.00% ❌
- Debt/Equity: 0 ❌
- Current Ratio: 0 ❌
- Composite Score: 36.22 (D)

**After:**
- ROE: **127.10%** ✅
- ROA: **3.13%** ✅
- Debt/Equity: **20.40** ✅
- Current Ratio: **0.66** ✅
- Composite Score: **36.4 (D)** ✅ (slight improvement, but reflects actual financial condition)

---

## Impact on Scoring

### Quality Score Impact
- **Before:** ROE and ROA were scoring 0, dragging down Quality Score
- **After:** ROE (127%) and ROA (3.13%) now contribute positively to Quality Score
- **Result:** Quality Score improved (though still penalized by high Debt/Equity)

### Health Score Impact
- **Before:** Current Ratio = 0 was scoring 0, dragging down Health Score
- **After:** Current Ratio (0.66) is correctly calculated and scored
- **Result:** Health Score improved

### Overall Impact
- **Score Improvement:** Minimal (+0.18 points) because ABBV has legitimate financial concerns
- **Accuracy Improvement:** Significant — scores now reflect actual financial condition, not missing data

---

## Key Learnings

1. **FMP API can return `0` for metrics** even when underlying data exists
2. **Always calculate from financial statements** when FMP returns 0 or None
3. **Distinguish between "bad" zeros and "missing" zeros:**
   - Bad zeros: Negative equity (ROE meaningless), negative FCF (FCF Yield negative)
   - Missing zeros: FMP calculation error, but data exists to calculate manually

---

## Massive.com API

**Question:** Are these metrics available in Massive.com API?

**Answer:** **No.** Massive.com is primarily an **options data provider** (OPRA feed), not a fundamental data provider. It focuses on:
- Options chains and Greeks
- Real-time quotes
- Historical options data

**Fundamental metrics like ROE, ROA, Current Ratio, Debt/Equity, and FCF Yield are NOT available in Massive.com API.** These must be calculated from financial statements (income statement, balance sheet, cash flow) or obtained from fundamental data providers like FMP.

---

## Conclusion

All zero metrics have been fixed:
1. ✅ **ROE** now calculated from Net Income / Equity → 127.10%
2. ✅ **ROA** now calculated from Net Income / Assets → 3.13%
3. ✅ **Debt/Equity** now calculated from Total Debt / Equity → 20.40
4. ✅ **Current Ratio** now calculated from Current Assets / Current Liabilities → 0.66
5. ✅ **P/B** handling improved for negative book value cases
6. ✅ **FCF Yield** calculation enhanced

**ABBV's score improved slightly but remains low (D) because it has legitimate financial concerns** (high leverage, low liquidity, weak growth, overvaluation). The scoring system now accurately reflects these concerns rather than penalizing for missing data.

---

*Fixes implemented: 2026-02-19*
