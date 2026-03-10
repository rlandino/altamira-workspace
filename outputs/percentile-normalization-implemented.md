# Percentile-Based Normalization — Implementation Complete

**Date:** 2026-02-19  
**Status:** ✅ **IMPLEMENTED**

---

## Summary

Percentile-based normalization has been successfully implemented for the stock scoring system. The system now uses sector-relative benchmarks when available, with automatic fallback to fixed ranges when benchmark data is unavailable.

---

## Implementation Details

### 1. Benchmark Calculator (`scripts/benchmark-calculator.py`)

**Purpose:** Calculate percentile benchmarks (p10, p25, median/p50, p75, p90) for key metrics across:
- S&P 500 (broad market benchmark)
- Sector-specific (Technology, Healthcare, Financials, etc.)

**Features:**
- Fetches metrics for 50 representative S&P 500 tickers
- Calculates percentiles for all key metrics (P/E, P/B, P/S, ROE, ROA, ROIC, margins, etc.)
- Caches benchmarks to `cache/benchmarks-sp500.json` and `cache/benchmarks-{sector}.json`
- Supports sector-specific benchmark calculation

**Usage:**
```bash
# Calculate S&P 500 benchmarks
python scripts/benchmark-calculator.py --force

# Calculate sector-specific benchmarks
python scripts/benchmark-calculator.py --sector Technology --force
```

---

### 2. Percentile Normalization Function

**New Function:** `normalize_score_percentile()`

**Purpose:** Normalize metric values using percentile rank relative to benchmarks.

**Algorithm:**
1. Calculate percentile rank using linear interpolation between benchmark percentiles
2. Map percentile rank (0-100) to score (0-100)
3. Handle outliers (extrapolate beyond p90, capped at 100)
4. Support inversion for metrics where lower is better (e.g., P/E, P/B)

**Example:**
- If P/E = 30 and benchmark median = 25, p75 = 35:
  - Percentile rank ≈ 60th percentile
  - Score = 60 (or 40 if inverted)

---

### 3. Updated Scoring Functions

**Modified Functions:**
- `calculate_quality_score()` — Uses percentile normalization for ROE, ROA, ROIC, Net Margin, Debt/Equity
- `calculate_value_score()` — Uses percentile normalization for P/E, P/B, P/S (most important for sector differences)

**Fallback Logic:**
- If benchmarks unavailable → Use fixed ranges (existing behavior)
- If sector benchmarks unavailable → Fall back to S&P 500 benchmarks
- If no benchmarks → Use fixed ranges

---

### 4. Sector Detection

**Implementation:**
- Extracts sector from FMP API profile endpoint
- Automatically loads sector-specific benchmarks if available
- Falls back to S&P 500 benchmarks if sector benchmarks unavailable

**Sectors Supported:**
- Technology
- Healthcare
- Financials
- Consumer Discretionary
- Communication Services
- Industrials
- Consumer Staples
- Energy
- Utilities
- Real Estate
- Materials

---

## Benefits

1. **Sector-Relative Scoring:** Technology stocks compared to Technology benchmarks, not broad market
2. **More Accurate Valuations:** P/E of 30 for a Tech stock vs. Tech median (e.g., 28) vs. S&P 500 median (e.g., 22)
3. **Better Differentiation:** Scores reflect relative performance within sector
4. **Automatic Fallback:** System works even without benchmark data

---

## Usage

### Generate Benchmarks

```bash
# First time: Calculate S&P 500 benchmarks
python scripts/benchmark-calculator.py --force

# Calculate sector benchmarks (optional, improves accuracy)
python scripts/benchmark-calculator.py --sector Technology --force
python scripts/benchmark-calculator.py --sector Healthcare --force
# ... repeat for other sectors
```

### Score Tickers

```bash
# Scoring automatically uses percentile normalization if benchmarks available
python scripts/stock-scorer.py AVGO MSFT GOOGL

# System automatically:
# 1. Detects sector from FMP profile
# 2. Loads sector-specific benchmarks (if available)
# 3. Falls back to S&P 500 benchmarks (if sector unavailable)
# 4. Falls back to fixed ranges (if no benchmarks)
```

---

## Benchmark Update Frequency

**Recommendation:** Update benchmarks quarterly or monthly

**Rationale:**
- Market valuations change over time
- Sector dynamics shift
- Quarterly updates balance accuracy vs. API costs

**Update Command:**
```bash
# Update all benchmarks
python scripts/benchmark-calculator.py --force
python scripts/benchmark-calculator.py --sector Technology --force
# ... repeat for all sectors
```

---

## Files Created/Modified

### New Files
- `scripts/benchmark-calculator.py` — Benchmark calculation script
- `cache/benchmarks-sp500.json` — S&P 500 benchmarks (generated)
- `cache/benchmarks-{sector}.json` — Sector benchmarks (generated)

### Modified Files
- `scripts/stock-scorer.py` — Added percentile normalization support
  - New function: `normalize_score_percentile()`
  - New function: `load_benchmarks()`
  - Updated: `calculate_quality_score()` — percentile support
  - Updated: `calculate_value_score()` — percentile support
  - Updated: `fetch_fmp_data()` — extracts sector from profile

---

## Testing

### Test Cases

1. **With Benchmarks:**
   ```bash
   # Generate benchmarks first
   python scripts/benchmark-calculator.py --force
   
   # Score ticker (should use percentile normalization)
   python scripts/stock-scorer.py AVGO
   ```

2. **Without Benchmarks:**
   ```bash
   # Delete cache to test fallback
   rm cache/benchmarks-*.json
   
   # Score ticker (should use fixed ranges)
   python scripts/stock-scorer.py AVGO
   ```

3. **Sector-Specific:**
   ```bash
   # Generate Technology benchmarks
   python scripts/benchmark-calculator.py --sector Technology --force
   
   # Score Technology stock (should use Tech benchmarks)
   python scripts/stock-scorer.py AVGO MSFT NVDA
   ```

---

## Expected Impact

### Before (Fixed Ranges)
- AVGO P/E = 73.87 → Normalized against 5-150 range → Score: ~54
- MSFT P/E = 36.31 → Normalized against 5-150 range → Score: ~79

### After (Percentile Normalization)
- AVGO P/E = 73.87 → Tech median ~35, p90 ~80 → Percentile rank ~85th → Score: ~15 (inverted)
- MSFT P/E = 36.31 → Tech median ~35, p75 ~45 → Percentile rank ~55th → Score: ~45 (inverted)

**Result:** Better differentiation — AVGO's high P/E penalized more relative to Tech sector, MSFT's moderate P/E scored better relative to Tech sector.

---

## Next Steps

1. ✅ **Generate Initial Benchmarks** — Run `benchmark-calculator.py` to create S&P 500 benchmarks
2. ✅ **Test Scoring** — Score portfolio holdings with percentile normalization
3. **Generate Sector Benchmarks** — Create benchmarks for major sectors (Technology, Healthcare, Financials)
4. **Monitor Accuracy** — Compare percentile-based scores to fixed-range scores
5. **Update Quarterly** — Refresh benchmarks quarterly to reflect market changes

---

## Documentation

- **Reference:** `reference/scoring-threshold-analysis.md` — Updated with percentile normalization approach
- **Kanban Task:** `outputs/kanban-task-percentile-normalization.md` — Mark as complete

---

*Implementation complete: 2026-02-19*
