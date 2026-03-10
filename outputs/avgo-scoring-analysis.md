# AVGO Scoring Analysis — Detailed Breakdown

**Date:** 2026-02-19  
**Ticker:** AVGO (Broadcom Inc.)  
**Issue:** Scores appear too low for a high-quality portfolio holding

---

## Executive Summary

The scoring system is producing artificially low scores due to **overly restrictive normalization ranges** that don't account for:
1. **High-growth tech stock valuations** (P/E, P/B, P/S ranges too low)
2. **Premium quality metrics** (margin ranges capped too low)
3. **Growth normalization** (ranges may not account for exceptional growth)

**Current Scores:**
- Quality: 60.02 (C+) — Reasonable but penalized by missing ROIC
- Growth: 38.69 (F) — **UNDERREVIEWED** — 23.87% revenue growth and 292% earnings growth should score much higher
- Value: 1.58 (F) — **CRITICAL ISSUE** — All valuation metrics normalized to 0 due to range limits
- Health: 55.78 (C) — Reasonable
- Shareholder: 27.96 (F) — Low dividend yield (0.65%)
- **Composite: 36.81 (F)** — Artificially low due to Value score

---

## Raw Metrics from FMP API

### Quality Metrics
| Metric | Raw Value | Converted | Status |
|--------|-----------|-----------|--------|
| ROE | 0.2845 | **28.45%** | ✅ Excellent (top quartile) |
| ROA | 0.1352 | **13.52%** | ✅ Excellent (top quartile) |
| Net Profit Margin | 0.3620 | **36.20%** | ✅ Exceptional (exceeds normalization max) |
| ROIC | N/A | **Missing** | ⚠️ Not available in FMP data |
| Debt/Equity | 0.8013 | 0.80 | ✅ Reasonable (moderate leverage) |

### Valuation Metrics
| Metric | Raw Value | Status |
|--------|-----------|--------|
| P/E | **73.87** | ⚠️ High but normal for growth tech |
| P/B | **21.01** | ⚠️ High but normal for tech |
| P/S | **26.74** | ⚠️ High but normal for tech |
| FCF Yield | 0.0158 | **1.58%** | ✅ Positive but low |

### Growth Metrics
| Metric | Raw Value | Converted | Status |
|--------|-----------|-----------|--------|
| Revenue Growth | 0.2387 | **23.87%** | ✅ Strong growth |
| Net Income Growth | 2.9229 | **292.29%** | ✅ Exceptional growth |

### Health Metrics
| Metric | Raw Value | Status |
|--------|-----------|--------|
| Current Ratio | 1.71 | ✅ Good liquidity |
| Interest Coverage | 7.94 | ✅ Healthy coverage |

### Shareholder Metrics
| Metric | Raw Value | Converted | Status |
|--------|-----------|-----------|--------|
| Dividend Yield | 0.0065 | **0.65%** | ⚠️ Low (tech stock norm) |

---

## Detailed Score Calculations

### 1. Quality Score: 60.02 (C+)

**Component Breakdown:**

| Component | Raw Value | Normalized Score | Weight | Contribution |
|-----------|-----------|------------------|--------|--------------|
| ROE | 28.45% | 56.90 | 0.25 | 14.22 |
| ROA | 13.52% | 54.07 | 0.20 | 10.81 |
| Net Margin | 36.20% | **100.00** (capped) | 0.20 | 20.00 |
| ROIC | **Missing** | — | 0.20 | 0.00 |
| Debt/Equity (inverted) | 0.80 | 19.87 | 0.15 | 2.98 |
| **TOTAL** | | | **0.80** | **48.02** |
| **FINAL SCORE** | | | | **60.02** |

**Issues:**
- ✅ ROE/ROA normalization reasonable (0-50% and 0-25% ranges)
- ⚠️ **Net Margin capped at 100%** — 36.20% exceeds the 30% max range, should use higher range
- ⚠️ **ROIC missing** — 20% weight lost (should try alternative calculation or use ROE as proxy)
- ⚠️ **Debt/Equity penalized** — 0.80 is reasonable leverage but gets low score (19.87)

**Recommendation:** 
- Increase margin max range to 50% or use percentile-based normalization
- Calculate ROIC from income statement if available
- Adjust debt/equity normalization (0.80 is not excessive)

---

### 2. Value Score: 1.58 (F) — **CRITICAL ISSUE**

**Component Breakdown:**

| Component | Raw Value | Normalized Score | Weight | Contribution |
|-----------|-----------|------------------|--------|--------------|
| P/E (inverted) | 73.87 | **0.00** (below range) | 0.25 | 0.00 |
| P/B (inverted) | 21.01 | **0.00** (below range) | 0.20 | 0.00 |
| P/S (inverted) | 26.74 | **0.00** (below range) | 0.15 | 0.00 |
| FCF Yield | 1.58% | 10.50 | 0.15 | 1.58 |
| Margin of Safety | -322.12% | **0.00** (below range) | 0.25 | 0.00 |
| **TOTAL** | | | **1.00** | **1.58** |
| **FINAL SCORE** | | | | **1.58** |

**Normalization Ranges (Current):**
- P/E: 5-50 (inverted) — **AVGO at 73.87 exceeds max, gets 0**
- P/B: 0.5-10 (inverted) — **AVGO at 21.01 exceeds max, gets 0**
- P/S: 0.5-15 (inverted) — **AVGO at 26.74 exceeds max, gets 0**
- FCF Yield: 0-15% — ✅ Works correctly
- Margin of Safety: -50% to 50% — **AVGO at -322% exceeds min, gets 0**

**The Problem:**
- **All valuation ratios normalized to 0** because AVGO trades at premium valuations typical of high-growth tech stocks
- These ranges are appropriate for value stocks but **too restrictive for growth stocks**
- AVGO's P/E of 73.87 is high but not unusual for a quality tech company with strong growth

**Recommendation:**
- **Expand normalization ranges** for growth stocks:
  - P/E: 5-100 (or use sector-relative normalization)
  - P/B: 0.5-30
  - P/S: 0.5-40
- **Use percentile-based normalization** relative to sector/industry
- **Adjust Margin of Safety calculation** — current formula produces extreme negative values

---

### 3. Growth Score: 38.69 (F) — **UNDERREVIEWED**

**Component Breakdown:**

| Component | Raw Value | Converted | Normalized Score | Weight | Contribution |
|-----------|-----------|-----------|------------------|--------|--------------|
| Revenue Growth | 0.2387 | 23.87% | ? | 0.30 | ? |
| Earnings Growth | 2.9229 | 292.29% | ? | 0.30 | ? |
| FCF Growth | ? | ? | ? | 0.25 | ? |
| FCF Per Share Growth | ? | ? | ? | 0.15 | ? |

**Normalization Ranges (Current):**
- Revenue Growth: -50% to 100%
- Earnings Growth: -100% to 200%

**Issues:**
- Revenue Growth of 23.87% should score well within -50% to 100% range
- Earnings Growth of 292.29% **exceeds the 200% max**, likely getting capped or penalized
- Need to verify FCF growth calculations

**Recommendation:**
- Expand earnings growth range to -100% to 500% or use percentile normalization
- Verify FCF growth calculations are working correctly

---

### 4. Health Score: 55.78 (C)

**Component Breakdown:**

| Component | Raw Value | Normalized Score | Weight | Contribution |
|-----------|-----------|------------------|--------|--------------|
| Debt/Equity (inverted) | 0.80 | ? | 0.30 | ? |
| Current Ratio | 1.71 | ? | 0.35 | ? |
| Interest Coverage | 7.94 | ? | 0.35 | ? |

**Status:** Appears reasonable, but need to verify normalization ranges.

---

### 5. Shareholder Score: 27.96 (F)

**Component Breakdown:**

| Component | Raw Value | Converted | Status |
|-----------|-----------|-----------|--------|
| Dividend Yield | 0.0065 | 0.65% | Low (normal for tech) |
| Dividend Growth | ? | ? | Need to check |
| Buyback Yield | ? | ? | Need to check |
| Debt Paydown | ? | ? | Need to check |

**Issues:**
- Low dividend yield is normal for growth tech stocks
- Should weight buybacks more heavily for tech stocks
- May need sector-adjusted expectations

---

## Root Cause Analysis

### Primary Issues:

1. **Value Score Normalization Ranges Too Restrictive**
   - Current ranges designed for value stocks (P/E 5-50)
   - Growth tech stocks typically trade at P/E 50-100+
   - **75% of Value Score weight gets normalized to 0** for AVGO

2. **Margin of Safety Calculation Produces Extreme Values**
   - Formula: `((fair_pe - current_pe) / fair_pe) * 100`
   - With fair_pe=17.5 and current_pe=73.87: `((17.5 - 73.87) / 17.5) * 100 = -322%`
   - This exceeds the -50% to 50% range, gets normalized to 0
   - **Need better Margin of Safety calculation** (e.g., DCF-based or sector-relative)

3. **Missing ROIC Data**
   - 20% weight lost in Quality Score
   - Should calculate from income statement or use ROE as proxy

4. **Growth Score May Have Range Issues**
   - 292% earnings growth exceeds 200% max range
   - Need to verify if it's being capped

---

## Recommendations

### Immediate Fixes:

1. **Expand Value Score Normalization Ranges:**
   ```python
   # Current (too restrictive):
   P/E: 5-50
   P/B: 0.5-10
   P/S: 0.5-15
   
   # Recommended (growth-friendly):
   P/E: 5-100 (or sector-relative)
   P/B: 0.5-30
   P/S: 0.5-40
   ```

2. **Fix Margin of Safety Calculation:**
   - Use DCF-based intrinsic value if available
   - Or use sector-relative P/E comparison
   - Or remove if data quality is poor

3. **Calculate ROIC from Available Data:**
   - ROIC = NOPAT / Invested Capital
   - Can calculate from income statement and balance sheet

4. **Expand Growth Score Ranges:**
   ```python
   # Current:
   Earnings Growth: -100% to 200%
   
   # Recommended:
   Earnings Growth: -100% to 500% (or percentile-based)
   ```

5. **Consider Sector-Adjusted Scoring:**
   - Tech stocks vs. value stocks have different valuation norms
   - Use sector-relative normalization where possible

---

## Expected Score After Fixes

**Estimated Adjusted Scores:**

| Component | Current | Expected After Fix | Change |
|-----------|---------|-------------------|--------|
| Quality | 60.02 | 65-70 | +5-10 |
| Growth | 38.69 | 60-75 | +20-35 |
| Value | 1.58 | 30-50 | +25-45 |
| Health | 55.78 | 55-60 | ~0 |
| Shareholder | 27.96 | 30-40 | +2-12 |
| **Composite** | **36.81** | **50-60** | **+13-23** |

**Expected Grade:** C to C+ (vs. current F)

---

## Conclusion

AVGO is a **high-quality company** with:
- ✅ Excellent profitability (28% ROE, 36% margins)
- ✅ Strong growth (24% revenue, 292% earnings)
- ✅ Healthy financials (good liquidity, coverage)
- ⚠️ Premium valuations (normal for growth tech)
- ⚠️ Low dividend yield (normal for tech)

The scoring system is **penalizing AVGO unfairly** due to normalization ranges designed for value stocks. With adjusted ranges, AVGO should score **50-60 (C to C+)**, which better reflects its quality and growth profile.

**Next Steps:**
1. Update normalization ranges in `scripts/stock-scorer.py`
2. Fix Margin of Safety calculation
3. Add ROIC calculation from available data
4. Re-score AVGO and portfolio holdings
5. Consider sector-adjusted scoring for future versions
