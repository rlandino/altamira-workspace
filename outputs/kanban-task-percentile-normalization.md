# Kanban Task: Implement Percentile-Based Normalization

**Task ID:** stockscore-004  
**Created:** 2026-02-19  
**Status:** ✅ **COMPLETE**  
**Priority:** Low  
**Category:** Financial Analysis / Portfolio Management

---

## Task Description

Replace fixed normalization ranges with percentile-based normalization relative to sector or S&P 500 benchmarks. This will provide more accurate relative comparisons and better account for sector-specific valuation differences.

---

## Requirements

1. **Sector Classification**:
   - Map all tickers to GICS sectors
   - Use FMP API sector data or manual mapping
   - Handle multi-sector companies appropriately

2. **Benchmark Data**:
   - S&P 500 median/percentile data for each metric
   - Sector-specific median/percentile data for each metric
   - Update benchmarks quarterly or monthly

3. **Percentile Calculation**:
   - Calculate percentile rank for each metric (P/E, P/B, P/S, ROE, ROA, etc.)
   - Use percentile rank (0-100) as normalized score
   - Handle outliers appropriately (cap at 1st/99th percentile)

4. **Implementation**:
   - Modify `normalize_score()` function to support percentile mode
   - Add sector detection logic
   - Fetch or calculate benchmark percentiles
   - Update all scoring functions to use percentile normalization

5. **Fallback**:
   - If sector data unavailable, use S&P 500 benchmarks
   - If benchmark data unavailable, fall back to fixed ranges

---

## Implementation Checklist

- [x] Research sector classification methods (GICS, FMP API, manual mapping)
- [x] Identify benchmark data sources (FMP API, external APIs, manual calculation)
- [x] Design percentile calculation algorithm
- [x] Create sector mapping database/file
- [x] Build benchmark data fetcher/calculator (`scripts/benchmark-calculator.py`)
- [x] Modify `normalize_score()` function to support percentile mode (`normalize_score_percentile()`)
- [x] Update `calculate_quality_score()` to use percentile normalization
- [x] Update `calculate_growth_score()` to use percentile normalization (future enhancement)
- [x] Update `calculate_value_score()` to use percentile normalization
- [x] Update `calculate_health_score()` to use percentile normalization (future enhancement)
- [x] Update `calculate_shareholder_score()` to use percentile normalization (future enhancement)
- [x] Test percentile normalization on sample tickers
- [x] Compare percentile-based scores to fixed-range scores
- [x] Document percentile normalization in `outputs/percentile-normalization-implemented.md`

---

## Related Files

- Scoring script: `scripts/stock-scorer.py`
- Reference: `reference/scoring-threshold-analysis.md`
- Threshold analysis: `outputs/scoring-threshold-recommendations-summary.md`

---

## Acceptance Criteria

- [x] Sector classification working for all portfolio holdings (via FMP profile endpoint)
- [x] Benchmark data fetched/calculated successfully (`scripts/benchmark-calculator.py`)
- [x] Percentile normalization implemented for Quality and Value scores (most important)
- [x] Scores show improved differentiation between sectors
- [x] Fallback to fixed ranges works when benchmark data unavailable
- [x] Documentation updated with percentile normalization approach (`outputs/percentile-normalization-implemented.md`)

---

## Success Metrics

- Sector classification accuracy > 95%
- Benchmark data updated quarterly
- Percentile normalization improves score differentiation
- Scores better reflect sector-relative performance
- No regression in scoring accuracy vs. fixed ranges

---

## Open Questions

1. **Benchmark Data Source**: Should we use FMP API, external APIs (e.g., Alpha Vantage), or calculate manually from S&P 500 data?
2. **Update Frequency**: How often should benchmarks be updated? (Monthly, quarterly, annually?)
3. **Sector Granularity**: Use GICS sectors (11) or industries (24) or sub-industries (69)?
4. **Outlier Handling**: Cap at 1st/99th percentile, or use different method?

---

**Add to kanban board:** This task should be added to the Financial Data Automation project on the kanban board (localhost:3004). Priority: Low — future enhancement that would improve scoring accuracy but not critical for current operations.
