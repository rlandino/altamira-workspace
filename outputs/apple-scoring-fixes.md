# Apple Scoring Fixes — ROIC and Interest Coverage

**Date:** 2026-02-19  
**Status:** ✅ **FIXED**

---

## Issues Identified

### 1. ROIC Showing as N/A

**Problem:** Apple's ROIC was showing as N/A in reports, even though FMP API provides `returnOnCapitalEmployed` (68.72%), which is very similar to ROIC.

**Root Cause:** The code only checked for `returnOnInvestedCapital` and didn't use `returnOnCapitalEmployed` as a fallback.

**Impact:** 
- ROIC weight (20% of Quality Score) was being redistributed to other metrics
- Quality Score was still high (86.77, A+) because weights redistribute, but ROIC wasn't contributing

**Fix Applied:**
```python
# Use returnOnCapitalEmployed as proxy if returnOnInvestedCapital unavailable
roic = latest.get("returnOnInvestedCapital")
if roic is None:
    roic = latest.get("returnOnCapitalEmployed")
```

**Result:** ROIC now shows as **68.72%** in Apple's report.

---

### 2. Interest Coverage = 0 Negatively Impacting Health Score

**Problem:** Apple's Interest Coverage was showing as 0, which was being scored as poor coverage (score: 0), dragging down the Health Score to 25.18 (F).

**Root Cause:** Apple has `interestExpense = 0` (no interest expense), which means:
- Interest Coverage = EBIT / 0 = undefined (FMP returns 0)
- This is actually **excellent** (infinite coverage), not poor
- The code was treating 0 as poor coverage

**Impact:**
- Health Score: 25.18 (F) — severely impacted by Interest Coverage = 0
- This dragged down the composite score

**Fix Applied:**
```python
# Handle case where 0 means no interest expense (excellent coverage)
if interest_coverage == 0:
    income = data.get("income")
    if income and isinstance(income, list) and len(income) > 0:
        inc = income[0]
        interest_expense = abs(inc.get("interestExpense", 0) or 0)
        if interest_expense == 0:
            # No interest expense = excellent coverage
            interest_coverage = 100.0  # Use high value for normalization
```

**Result:** 
- Interest Coverage now shows as **∞ (No Interest Expense)** in report
- Health Score improved significantly
- Composite Score improved from **41.2 (D+)** to **48.2 (C-)**

---

## Score Impact

### Before Fixes
- **Composite Score:** 41.17 (D+)
- **Quality Score:** 86.77 (A+) — ROIC not contributing
- **Health Score:** 25.18 (F) — Interest Coverage = 0 penalizing

### After Fixes
- **Composite Score:** 48.2 (C-) — **+7.03 points improvement**
- **Quality Score:** Improved (ROIC now contributing)
- **Health Score:** Improved (Interest Coverage properly recognized as excellent)

---

## Technical Details

### ROIC Calculation Priority

1. **First:** Try `returnOnInvestedCapital` from FMP ratios
2. **Second:** Try `returnOnCapitalEmployed` from FMP ratios (proxy)
3. **Third:** Calculate from income statement and balance sheet:
   - ROIC = NOPAT / Invested Capital
   - NOPAT = Operating Income × (1 - Tax Rate)
   - Invested Capital = Total Debt + Total Equity - Cash

### Interest Coverage Calculation Priority

1. **First:** Use `interestCoverage` from FMP ratios
2. **Second:** Calculate: EBIT / Interest Expense
3. **Special Case:** If Interest Expense = 0:
   - Treat as excellent coverage (infinite)
   - Use 100.0 for normalization purposes
   - Display as "∞ (No Interest Expense)" in report

---

## Files Modified

- `scripts/stock-scorer.py`
  - Updated `calculate_quality_score()` — Added `returnOnCapitalEmployed` fallback for ROIC
  - Updated `calculate_health_score()` — Handle Interest Coverage = 0 case
  - Updated `generate_report()` — Display Interest Coverage properly when 0

---

## Verification

### Apple (AAPL) Test Results

**Before:**
- ROIC: N/A
- Interest Coverage: 0
- Composite Score: 41.2 (D+)
- Health Score: 25.18 (F)

**After:**
- ROIC: **68.72%** ✅
- Interest Coverage: **∞ (No Interest Expense)** ✅
- Composite Score: **48.2 (C-)** ✅ (+7.03 points)
- Health Score: Improved ✅

---

## Impact on Other Holdings

These fixes will benefit other holdings with:
- Missing `returnOnInvestedCapital` but having `returnOnCapitalEmployed`
- Zero or negative interest expense (excellent coverage, not poor)

---

## Massive.com API

**Question:** Are ROIC and Interest Coverage available in Massive.com API?

**Answer:** Massive.com is primarily an **options data provider** (OPRA feed), not a fundamental data provider. It focuses on:
- Options chains and Greeks
- Real-time quotes
- Historical options data

**Fundamental metrics like ROIC and Interest Coverage are NOT available in Massive.com API.** These must be calculated from financial statements (income statement, balance sheet) or obtained from fundamental data providers like FMP.

---

## Conclusion

Both issues have been fixed:
1. ✅ **ROIC** now uses `returnOnCapitalEmployed` as fallback
2. ✅ **Interest Coverage** properly handles zero interest expense as excellent coverage

Apple's score improved from **D+ (41.2)** to **C- (48.2)**, reflecting more accurate evaluation of its financial health.

---

*Fixes implemented: 2026-02-19*
