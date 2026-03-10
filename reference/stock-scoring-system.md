# Stock Scoring System — Reference

**Purpose:** Comprehensive scoring framework for evaluating stocks across Quality, Growth, Value, Health, and Shareholder dimensions. Used by `/stockscore` command to score portfolio holdings and evaluate new entrants.

---

## Scoring Components

### 1. Quality Score (0-100)

**Weights:**
- ROE (Return on Equity): 0.25
- ROA (Return on Assets): 0.20
- Net Income Margin: 0.20
- ROIC (Return on Invested Capital): 0.20
- Debt/Total Capital (lower is better): 0.15

**Data Sources (FMP API):**
- ROE: `ratios/{TICKER}` → `returnOnEquity`
- ROA: `ratios/{TICKER}` → `returnOnAssets`
- Net Income Margin: `ratios/{TICKER}` → `netProfitMargin`
- ROIC: `ratios/{TICKER}` → `returnOnInvestedCapital`
- Debt/Total Capital: `ratios/{TICKER}` → `debtEquityRatio` or calculate from balance sheet

**Calculation:**
1. Normalize each metric to 0-100 scale (percentile ranking or min/max normalization)
2. For Debt/Total Capital: invert (lower debt = higher score)
3. Weighted sum: `qualityScore = (ROE × 0.25) + (ROA × 0.20) + (Margin × 0.20) + (ROIC × 0.20) + (InvertedDebtCapital × 0.15)`

---

### 2. Growth Score (0-100)

**Weights:**
- Revenue Growth: 0.30
- Earnings Growth: 0.30
- Free Cash Flow Growth: 0.25
- Free Cash Flow Per Share Growth: 0.15

**Data Sources (FMP API):**
- Revenue Growth: `financial-growth/{TICKER}` → `revenueGrowth` (YoY)
- Earnings Growth: `financial-growth/{TICKER}` → `netIncomeGrowth` (YoY)
- FCF Growth: `cash-flow-statement/{TICKER}` → calculate YoY change in `freeCashFlow`
- FCF Per Share Growth: `cash-flow-statement/{TICKER}` + `key-metrics/{TICKER}` → calculate FCF/share and YoY growth

**Calculation:**
1. Calculate YoY growth rates (most recent year vs previous year)
2. Normalize to 0-100 scale
3. Weighted sum: `growthScore = (RevenueGrowth × 0.30) + (EarningsGrowth × 0.30) + (FCFGrowth × 0.25) + (FCFPerShareGrowth × 0.15)`

---

### 3. Value Score (0-100) — Lower valuations are better

**Weights:**
- P/E Ratio (inverted): 0.25
- P/B Ratio (inverted): 0.20
- P/S Ratio (inverted): 0.15
- FCF Yield: 0.15
- Margin of Safety: 0.25

**Data Sources (FMP API):**
- P/E: `ratios/{TICKER}` → `priceEarningsRatio`
- P/B: `ratios/{TICKER}` → `priceToBookRatio`
- P/S: `ratios/{TICKER}` → `priceToSalesRatio`
- FCF Yield: `key-metrics/{TICKER}` → `freeCashFlowYield` or calculate from cash flow statement
- Margin of Safety: Calculate as `(IntrinsicValue - CurrentPrice) / CurrentPrice` (use DCF from `/thesis` or sector-relative valuation)

**Calculation:**
1. For P/E, P/B, P/S: invert (lower ratio = higher score)
2. FCF Yield: higher is better (normalize)
3. Margin of Safety: positive = discount to intrinsic value (normalize)
4. Weighted sum: `valueScore = (InvertedPE × 0.25) + (InvertedPB × 0.20) + (InvertedPS × 0.15) + (FCFYield × 0.15) + (MarginOfSafety × 0.25)`

---

### 4. Financial Health Score (0-100)

**Weights:**
- Debt Metrics: 0.30
- Liquidity: 0.35
- Coverage: 0.35

**Data Sources (FMP API):**
- Debt: `ratios/{TICKER}` → `debtEquityRatio` or `debtToAssets` (invert, lower is better)
- Liquidity: `ratios/{TICKER}` → `currentRatio`, `quickRatio` (higher is better)
- Coverage: `ratios/{TICKER}` → `interestCoverage` (EBIT / Interest Expense, higher is better)

**Calculation:**
1. Normalize each metric to 0-100 scale
2. For Debt: invert (lower debt = higher score)
3. Weighted sum: `healthScore = (DebtScore × 0.30) + (LiquidityScore × 0.35) + (CoverageScore × 0.35)`

---

### 5. Shareholder Score (0-100)

**Weights:**
- Dividend Yield: 0.30
- Dividend Growth: 0.25
- Buyback Yield: 0.25
- Debt Paydown: 0.20

**Data Sources (FMP API):**
- Dividend Yield: `key-metrics/{TICKER}` → `dividendYield` or `quote/{TICKER}` → `dividendYield`
- Dividend Growth: `historical/stock_dividend/{TICKER}` → calculate YoY growth
- Buyback Yield: `key-metrics/{TICKER}` → `sharesOutstanding` (YoY reduction) × `price` / `marketCap`
- Debt Paydown: `balance-sheet-statement/{TICKER}` → YoY reduction in `totalDebt` (positive = paydown)

**Calculation:**
1. Normalize each metric to 0-100 scale
2. Weighted sum: `shareholderScore = (DivYield × 0.30) + (DivGrowth × 0.25) + (BuybackYield × 0.25) + (DebtPaydown × 0.20)`

---

## Composite Score & Grade

### Composite Score
Average of all five component scores:
```
compositeScore = (qualityScore + growthScore + valueScore + healthScore + shareholderScore) / 5
```

### Letter Grade Assignment

| Grade | Composite Score Range |
|-------|---------------------|
| **A+** | >= 90 |
| **A** | >= 85 |
| **A-** | >= 80 |
| **B+** | >= 75 |
| **B** | >= 70 |
| **B-** | >= 65 |
| **C+** | >= 60 |
| **C** | >= 55 |
| **C-** | >= 50 |
| **D+** | >= 45 |
| **D** | >= 40 |
| **F** | < 40 |

---

## Strengths & Weaknesses

### Thresholds
- **STRENGTH_THRESHOLD**: 70
- **WEAKNESS_THRESHOLD**: 50

### Strength Labels
- Growth >= 70: "Strong Growth"
- Quality >= 70: "High Quality"
- Value >= 70: "Attractive Value"
- Health >= 70: "Financially Healthy"
- Shareholder >= 70: "Shareholder Friendly"

### Weakness Labels
- Growth < 50: "Weak Growth"
- Quality < 50: "Quality Concerns"
- Value < 50: "Overvalued"
- Health < 50: "Financially Concerning"
- Shareholder < 50: "Poor Shareholder Returns"

---

## Usage

### Score All Portfolio Holdings
```bash
/stockscore
```
Scores all holdings from `context/portfolio-details.md` and generates `outputs/portfolio-scores-{DATE}.md`.

### Score New Entrant
```bash
/stockscore MSFT
```
Scores a single ticker before adding to portfolio. Generates `outputs/stock-score-MSFT-{DATE}.md`.

---

## Data Normalization

When calculating scores, normalize metrics to 0-100 scale using one of:

1. **Percentile Ranking**: Rank within sector or market cap cohort
2. **Min/Max Normalization**: `normalized = ((value - min) / (max - min)) × 100`
3. **Z-Score**: `normalized = 50 + (z-score × 10)` (clamp to 0-100)

For missing data: exclude from that component's calculation and adjust weights proportionally, or use industry average as proxy.

---

## Report Output Format

Reports include:
1. **Scoring Summary** — Ticker, company name, composite score, grade
2. **Component Scores Table** — All five scores (0-100) with breakdown
3. **Strengths** — List of strengths (scores >= 70)
4. **Weaknesses** — List of weaknesses (scores < 50)
5. **Key Metrics** — Supporting data (ROE, ROA, P/E, P/B, FCF Yield, **DCF Fair Value**, **Current Price**, **DCF Margin of Safety** when DCF available, Health metrics)
6. **Recommendation** — Buy/Hold/Avoid (new entrants) or Hold/Consider Reducing/Strong Hold (existing)

---

## Integration with Portfolio Management

- **New Entrants**: Score before adding to portfolio. Minimum composite score threshold (e.g., >= 60) recommended.
- **Existing Holdings**: Score quarterly or on significant events. Flag holdings with F grades or declining scores for review.
- **Portfolio Optimization**: Use scores to identify underperformers and rebalancing opportunities.

---

---

## Recent Algorithm Updates (2026-02-19)

- **Health, Growth, Shareholder** use percentile-based normalization when sector/S&P 500 benchmarks are available (see `cache/benchmarks-sp500.json`; regenerate with `python scripts/benchmark-calculator.py --force` to include growth/dividendYield).
- **Margin of Safety:** Prefer FMP DCF when available (`discounted-cash-flow` endpoint); else fair P/E–based margin.
- **Growth decimals:** All FMP growth inputs (revenue, earnings) converted via `ensure_growth_percentage()` so decimal vs percentage is consistent.

*Last updated: 2026-02-19*
