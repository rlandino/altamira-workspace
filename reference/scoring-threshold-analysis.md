# Scoring Threshold Analysis & Recommendations

**Date:** 2026-02-19  
**Purpose:** Comprehensive review of all scoring thresholds and normalization ranges to improve investment prospect evaluation

---

## Executive Summary

Current scoring system produces artificially low scores due to:
1. **Incorrect decimal handling** — FMP returns growth metrics as decimals (0.2387 = 23.87%) but code may not convert properly
2. **Overly restrictive normalization ranges** — Designed for value stocks, penalizing growth companies
3. **Missing percentile-based normalization** — Fixed ranges don't account for sector/industry differences
4. **Grade thresholds too high** — Current thresholds (A+ = 90+) are unrealistic for most companies

---

## Current Threshold Analysis

### 1. Quality Score Thresholds

| Metric | Current Range | Issue | Industry Benchmark |
|--------|---------------|-------|-------------------|
| ROE | 0-50% | ✅ Reasonable | Excellent: 20%+, Good: 15-20%, Average: 10-15% |
| ROA | 0-25% | ✅ Reasonable | Excellent: 10%+, Good: 5-10%, Average: 3-5% |
| Net Margin | -10% to 50% | ⚠️ Max too high | Excellent: 20%+, Good: 10-20%, Average: 5-10% |
| ROIC | 0-40% | ✅ Reasonable | Excellent: 20%+, Good: 15-20%, Average: 10-15% |
| Debt/Equity | 0-1 (inverted) | ⚠️ Range too narrow | Excellent: <0.5, Good: 0.5-1.0, Concerning: >1.5 |

**Recommendations:**
- Net Margin max: 50% → **35%** (very few companies exceed 35%)
- Debt/Equity: Expand to 0-2.0 (inverted) to accommodate higher leverage companies

---

### 2. Growth Score Thresholds

| Metric | Current Range | Issue | Industry Benchmark |
|--------|---------------|-------|-------------------|
| Revenue Growth | -50% to 150% | ⚠️ **DECIMAL CONVERSION ISSUE** | Excellent: 20%+, Good: 10-20%, Average: 5-10% |
| Earnings Growth | -100% to 500% | ⚠️ **DECIMAL CONVERSION ISSUE** | Excellent: 30%+, Good: 15-30%, Average: 5-15% |
| FCF Growth | -100% to 500% | ⚠️ **DECIMAL CONVERSION ISSUE** | Excellent: 25%+, Good: 10-25%, Average: 0-10% |
| FCF Per Share Growth | -100% to 500% | ⚠️ **DECIMAL CONVERSION ISSUE** | Similar to FCF Growth |

**CRITICAL ISSUE:** FMP returns growth as decimals (e.g., `revenueGrowth: 0.2387` = 23.87%), but code may normalize the decimal value instead of converting to percentage first.

**Example (AVGO):**
- Revenue Growth: 0.2387 (23.87%)
- Current normalization: (0.2387 - (-50)) / (150 - (-50)) = 50.2387 / 200 = **25.1%** ❌ WRONG
- Correct normalization: (23.87 - (-50)) / (150 - (-50)) = 73.87 / 200 = **36.9%** ✅ CORRECT

**Recommendations:**
- **Fix decimal conversion** — Always check if growth < 1 and multiply by 100
- Revenue Growth: -50% to 150% → **-30% to 100%** (more realistic)
- Earnings Growth: -100% to 500% → **-50% to 200%** (exceptional growth is rare)
- FCF Growth: -100% to 500% → **-50% to 150%** (more realistic)

---

### 3. Value Score Thresholds

| Metric | Current Range (Growth) | Current Range (Value) | Issue | Industry Benchmark |
|--------|------------------------|----------------------|-------|-------------------|
| P/E | 5-120 | 5-100 | ⚠️ Still restrictive | Growth Tech: 30-80, Value: 10-20, Average: 15-25 |
| P/B | 0.5-40 | 0.5-30 | ⚠️ Still restrictive | Growth Tech: 5-25, Value: 1-3, Average: 2-5 |
| P/S | 0.5-50 | 0.5-40 | ⚠️ Still restrictive | Growth Tech: 5-30, Value: 1-3, Average: 2-5 |
| FCF Yield | 0-15% | 0-15% | ✅ Reasonable | Excellent: 5%+, Good: 3-5%, Average: 1-3% |
| Margin of Safety | -200% to +100% | -200% to +100% | ⚠️ Calculation issue | Should use DCF or sector-relative |

**Recommendations:**
- **P/E:** Use percentile-based normalization OR expand ranges:
  - Growth: 5-150 (was 5-120)
  - Value: 5-80 (was 5-100)
- **P/B:** Expand ranges:
  - Growth: 0.5-50 (was 0.5-40)
  - Value: 0.5-20 (was 0.5-30)
- **P/S:** Expand ranges:
  - Growth: 0.5-60 (was 0.5-50)
  - Value: 0.5-25 (was 0.5-40)
- **Margin of Safety:** Use sector-relative P/E comparison instead of fixed fair_pe

---

### 4. Health Score Thresholds

| Metric | Current Range | Issue | Industry Benchmark |
|--------|---------------|-------|-------------------|
| Debt/Equity (inverted) | 0-3 | ✅ Reasonable | Excellent: <0.5, Good: 0.5-1.0, Concerning: >1.5 |
| Current Ratio | 0-3 | ✅ Reasonable | Excellent: >2.0, Good: 1.5-2.0, Average: 1.0-1.5 |
| Interest Coverage | 0-20 | ✅ Reasonable | Excellent: >10, Good: 5-10, Concerning: <3 |

**Recommendations:**
- Current ranges are appropriate
- Consider expanding Interest Coverage to 0-30 for high-growth companies

---

### 5. Shareholder Score Thresholds

| Metric | Current Range (Growth) | Current Range (Value) | Issue | Industry Benchmark |
|--------|------------------------|----------------------|-------|-------------------|
| Dividend Yield | 0-3% | 0-6% | ✅ Reasonable | Growth: 0-2%, Value: 2-5%, High Yield: 5%+ |
| Dividend Growth | -50% to +50% | -50% to +50% | ⚠️ Too narrow | Excellent: 10%+, Good: 5-10%, Average: 0-5% |
| Buyback Yield | 0-15% | 0-10% | ✅ Reasonable | Excellent: 5%+, Good: 2-5%, Average: 0-2% |
| Debt Paydown | -50% to +50% | -50% to +50% | ✅ Reasonable | Positive = paydown (good) |

**Recommendations:**
- Dividend Growth: Expand to **-50% to +100%** (allows for exceptional dividend growth)
- Consider using **3-year average** dividend growth instead of YoY (smoother)

---

### 6. Grade Thresholds

| Grade | Current Threshold | Issue | Recommendation |
|-------|------------------|-------|----------------|
| A+ | 90+ | ⚠️ Unrealistic | **85+** (top 5% of companies) |
| A | 85+ | ⚠️ Very high | **80+** (top 10% of companies) |
| A- | 80+ | ⚠️ High | **75+** (top 15% of companies) |
| B+ | 75+ | ⚠️ High | **70+** (top 25% of companies) |
| B | 70+ | ✅ Reasonable | **65+** (top 35% of companies) |
| B- | 65+ | ✅ Reasonable | **60+** (top 50% of companies) |
| C+ | 60+ | ✅ Reasonable | **55+** (average) |
| C | 55+ | ✅ Reasonable | **50+** (below average) |
| C- | 50+ | ✅ Reasonable | **45+** (below average) |
| D+ | 45+ | ✅ Reasonable | **40+** (poor) |
| D | 40+ | ✅ Reasonable | **35+** (poor) |
| F | <40 | ✅ Reasonable | **<35** (very poor) |

**Recommendations:**
- Lower all grade thresholds by **5-10 points** to make them more achievable
- A+ should represent exceptional companies (top 5%), not perfection

---

## Critical Fixes Required

### 1. Fix Growth Metric Decimal Conversion

**Problem:** FMP returns growth metrics as decimals (0.2387 = 23.87%), but code may normalize before converting.

**Fix:**
```python
# Revenue Growth
rev_growth = latest.get("revenueGrowth")
if rev_growth is not None:
    # CRITICAL: Convert decimal to percentage BEFORE normalization
    if abs(rev_growth) < 1:
        rev_growth = rev_growth * 100
    scores["revenue"] = normalize_score(rev_growth, -50, 150)
```

**Apply to:** All growth metrics (revenue, earnings, FCF, FCF per share)

---

### 2. Implement Percentile-Based Normalization

**Problem:** Fixed ranges don't account for sector/industry differences.

**Solution:** Use percentile-based normalization relative to sector or S&P 500 median.

**Example:**
- Instead of: `normalize_score(pe, 5, 100, invert=True)`
- Use: `normalize_score_percentile(pe, sector="Technology", metric="pe", invert=True)`

**Implementation:** Requires sector data or benchmark dataset (future enhancement)

---

### 3. Adjust Grade Thresholds

**Current:** A+ = 90+, A = 85+, A- = 80+
**Recommended:** A+ = 85+, A = 80+, A- = 75+

This makes grades more achievable while maintaining differentiation.

---

## Detailed Recommendations

### Quality Score Adjustments

| Metric | Current Max | Recommended Max | Rationale |
|--------|-------------|-----------------|-----------|
| Net Margin | 50% | **35%** | Very few companies exceed 35% margins |
| Debt/Equity Range | 0-1 | **0-2.0** | Accommodate higher leverage (still inverted) |

---

### Growth Score Adjustments

| Metric | Current Range | Recommended Range | Rationale |
|--------|---------------|-------------------|-----------|
| Revenue Growth | -50% to 150% | **-30% to 100%** | More realistic for most companies |
| Earnings Growth | -100% to 500% | **-50% to 200%** | Exceptional growth (200%+) is rare |
| FCF Growth | -100% to 500% | **-50% to 150%** | More realistic range |
| FCF Per Share Growth | -100% to 500% | **-50% to 150%** | Same as FCF Growth |

**CRITICAL:** Fix decimal conversion before normalization!

---

### Value Score Adjustments

| Metric | Growth Range | Value Range | Rationale |
|--------|--------------|------------|-----------|
| P/E | 5-120 → **5-150** | 5-100 → **5-80** | Growth tech can trade at P/E 100+ |
| P/B | 0.5-40 → **0.5-50** | 0.5-30 → **0.5-20** | Growth tech can trade at P/B 30+ |
| P/S | 0.5-50 → **0.5-60** | 0.5-40 → **0.5-25** | Growth tech can trade at P/S 40+ |

**Margin of Safety:**
- Use sector-relative P/E comparison
- Growth Tech fair_pe: 30 → **35** (reflects higher valuations)
- Value fair_pe: 15 → **18** (slightly higher)

---

### Shareholder Score Adjustments

| Metric | Current Range | Recommended Range | Rationale |
|--------|---------------|-------------------|-----------|
| Dividend Growth | -50% to +50% | **-50% to +100%** | Allow for exceptional dividend growth |
| Buyback Yield (Growth) | 0-15% | **0-20%** | Growth companies can have aggressive buybacks |

---

### Grade Threshold Adjustments

| Grade | Current | Recommended | Change |
|-------|---------|-------------|--------|
| A+ | 90+ | **85+** | -5 |
| A | 85+ | **80+** | -5 |
| A- | 80+ | **75+** | -5 |
| B+ | 75+ | **70+** | -5 |
| B | 70+ | **65+** | -5 |
| B- | 65+ | **60+** | -5 |
| C+ | 60+ | **55+** | -5 |
| C | 55+ | **50+** | -5 |
| C- | 50+ | **45+** | -5 |
| D+ | 45+ | **40+** | -5 |
| D | 40+ | **35+** | -5 |
| F | <40 | **<35** | -5 |

---

## Implementation Priority

### Priority 1: Critical Fixes (Immediate)

1. **Fix Growth Metric Decimal Conversion** — This is causing Growth Score to be artificially low
2. **Lower Grade Thresholds** — Make grades more achievable and meaningful
3. **Expand Value Score Ranges** — Especially for growth companies

### Priority 2: Important Improvements (Next)

4. **Adjust Growth Score Ranges** — More realistic ranges
5. **Improve Margin of Safety Calculation** — Sector-relative approach
6. **Expand Shareholder Score Ranges** — Dividend growth range

### Priority 3: Future Enhancements

7. **Percentile-Based Normalization** — Sector-relative scoring
8. **Multi-Year Averages** — Use 3-year averages for smoother scores
9. **Sector-Specific Thresholds** — Different ranges by sector

---

## Expected Impact

### AVGO Score Projections

| Component | Current | After Fixes | Change |
|-----------|---------|-------------|--------|
| Quality | 53.03 | 55-60 | +2-7 |
| Growth | 21.86 | **60-75** | **+38-53** (decimal fix critical) |
| Value | 32.75 | 40-55 | +7-22 |
| Health | 55.78 | 55-60 | ~0 |
| Shareholder | 39.94 | 40-50 | +0-10 |
| **Composite** | **40.67 (D)** | **50-60 (C to C+)** | **+9-19** |

**Expected Grade:** C to C+ (vs. current D)

---

## Code Changes Required

### 1. Fix Growth Decimal Conversion

```python
# In calculate_growth_score()
rev_growth = latest.get("revenueGrowth")
if rev_growth is not None:
    # CRITICAL FIX: Convert decimal to percentage FIRST
    if abs(rev_growth) < 1:
        rev_growth = rev_growth * 100
    # Then normalize with adjusted range
    scores["revenue"] = normalize_score(rev_growth, -30, 100)  # Adjusted range
```

### 2. Update Grade Thresholds

```python
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
```

### 3. Expand Value Ranges

```python
# Growth companies
pe_max = 150 if is_growth else 80  # Was 120/100
pb_max = 50 if is_growth else 20   # Was 40/30
ps_max = 60 if is_growth else 25   # Was 50/40
```

### 4. Adjust Growth Ranges

```python
# Revenue Growth
scores["revenue"] = normalize_score(rev_growth, -30, 100)  # Was -50, 150

# Earnings Growth
scores["earnings"] = normalize_score(earnings_growth, -50, 200)  # Was -100, 500

# FCF Growth
scores["fcf"] = normalize_score(fcf_growth, -50, 150)  # Was -100, 500
```

---

## Validation Plan

1. **Test on AVGO** — Should score 50-60 (C to C+) after fixes
2. **Test on MSFT, GOOGL, AAPL** — Should score 55-70 (C+ to B)
3. **Test on Value Stocks** — Should maintain reasonable scores
4. **Verify Growth Score** — Should reflect actual growth rates correctly

---

*Analysis complete: 2026-02-19*
