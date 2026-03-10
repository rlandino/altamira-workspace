# Stock Score Algorithm — Next Steps Implemented

**Date:** 2026-02-19  
**Status:** ✅ Complete

---

## Summary

All three next steps from the algorithm update have been implemented:

1. **Percentile normalization extended to Health, Growth, and Shareholder**
2. **DCF-based margin of safety** when FMP DCF data is available
3. **Decimal-to-percentage conversion** standardized and audited
4. **Benchmark calculator extended** for growth and shareholder metrics

---

## 1. Percentile Normalization Extended

### Health Score
- **`calculate_health_score(data, use_percentile=True)`** now uses sector/S&P 500 benchmarks when available.
- **Debt (debtEquity):** percentile normalization, inverted (lower = better).
- **Liquidity (currentRatio):** percentile normalization.
- **Coverage (interestCoverage):** percentile normalization.
- Fallback: fixed ranges (0–3, 0–3, 0–30) when benchmarks are missing.

### Growth Score
- **`calculate_growth_score(data, use_percentile=True)`** loads benchmarks and uses them for revenue and earnings growth when available.
- **Revenue growth:** `normalize_score_percentile(..., benchmarks["revenueGrowth"])` when benchmarks exist; else fixed range -30% to 100%.
- **Earnings growth:** `normalize_score_percentile(..., benchmarks["netIncomeGrowth"])` when benchmarks exist; else -50% to 200%.
- FCF and FCF-per-share growth remain on fixed ranges (benchmarks not yet added for these).

### Shareholder Score
- **`calculate_shareholder_score(data, use_percentile=True)`** uses **dividendYield** benchmarks when available.
- **Dividend yield:** percentile normalization when benchmarks exist; else fixed range (0–3% growth, 0–6% value).
- Div growth, buyback yield, debt paydown unchanged (fixed ranges).

---

## 2. DCF-Based Margin of Safety

- **FMP endpoint added:** `discounted-cash-flow/{tICKER}` in `fetch_fmp_data()`.
- **Value score logic:**  
  - If DCF data and price exist: **margin_of_safety = (dcf_value - price) / price × 100**, capped to -200% to +100%.  
  - If no DCF or missing price: fallback to **fair P/E–based** margin (fair_pe 35 growth / 18 value).
- Aligns with `/thesis` use of FMP DCF for valuation.

---

## 3. Decimal-to-Percentage Conversion (Audit)

- **New helper:** `ensure_growth_percentage(value)` in `scripts/stock-scorer.py`.  
  - Treats values with **-2 < value < 2** (excluding 0) as decimals and multiplies by 100.  
  - Used for revenue growth, earnings growth, and in `is_growth_company()` for revenue growth check.
- **Removed:** Ad-hoc `if abs(x) < 1: x = x * 100` in favor of the helper.
- **Consistency:** All FMP growth inputs (revenue, earnings) and the growth-company detection path now use the same conversion rule.

---

## 4. Benchmark Calculator Extended

**File:** `scripts/benchmark-calculator.py`

- **New API calls per ticker:**  
  - `financial-growth/{ticker}?period=annual&limit=1` → **revenueGrowth**, **netIncomeGrowth** (converted to % if decimal).  
  - `key-metrics/{ticker}?period=annual&limit=1` → **dividendYield** (converted to % if &lt; 1).
- **New benchmark metrics:** `revenueGrowth`, `netIncomeGrowth`, `dividendYield` added to the metrics dict and percentile calculation.
- **Regenerate benchmarks** to include growth and dividend yield:
  ```bash
  python scripts/benchmark-calculator.py --force
  ```
  Existing cache (`cache/benchmarks-sp500.json`) does not include these keys until regenerated. Scorer falls back to fixed ranges when a benchmark key is missing.

---

## Files Modified

| File | Changes |
|------|--------|
| `scripts/stock-scorer.py` | `ensure_growth_percentage()`, DCF fetch and margin-of-safety logic, Health/Growth/Shareholder percentile, decimal conversion audit |
| `scripts/benchmark-calculator.py` | Fetch growth + key-metrics, add revenueGrowth, netIncomeGrowth, dividendYield to benchmarks |

---

## How to Use

1. **Regenerate benchmarks** (optional but recommended for Growth/Shareholder percentile):
   ```bash
   python scripts/benchmark-calculator.py --force
   ```
2. **Score as usual:**  
   `python scripts/stock-scorer.py MSFT` or `python scripts/stock-scorer.py --portfolio`
3. **No breaking changes:** Defaults keep percentile on; existing reports and workflows remain valid.

---

## Verification

- **MSFT** scored successfully (composite 54.7, grade C) after changes.
- No linter errors on modified files.
- DCF used for margin of safety when FMP returns DCF; otherwise fair P/E used.

---

*Last updated: 2026-02-19*
