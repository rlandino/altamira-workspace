# /stockscore — Stock Scoring System

Calculate comprehensive stock scores (Quality, Growth, Value, Health, Shareholder) and composite grade for tickers using FMP API data. Score all current portfolio holdings or evaluate new entrants before adding to portfolio.

## Instructions

You are running a stock scoring analysis for Altamira Capital. **Use the Python script `scripts/stock-scorer.py` to perform the scoring.**

### Step 1: Identify ticker(s)

The user will provide ticker symbol(s) as argument: $ARGUMENTS

**If no ticker provided:**
- Score **all current portfolio holdings** by running: `python scripts/stock-scorer.py --portfolio`
- This extracts tickers from `context/portfolio-details.md`
- Current holdings: SPY, AVGO, GOOGL, AMAT, MSFT, AMZN, AAPL, CRWD, COST, ABBV, GD, V, JPM, KMI, WM, FFOLX, QQQ, NOW, SPGI, NFLX

**If ticker(s) provided:**
- Score the specified ticker(s) by running: `python scripts/stock-scorer.py TICKER1 TICKER2 ...`
- Useful for evaluating new entrants before adding to portfolio

### Step 2: Execute the scoring script

Run the Python script which automatically fetches data from FMP API (key: `FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz`) and calculates scores:

```bash
# Single ticker
python scripts/stock-scorer.py MSFT

# Multiple tickers
python scripts/stock-scorer.py MSFT AAPL GOOGL

# All portfolio holdings
python scripts/stock-scorer.py --portfolio
```

The script fetches the following data from **FMP API** (primary) with **Massive.com API** (fallback) for each ticker:

**Data Sources:**
- **Primary:** FMP API (`FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz`)
- **Fallback:** Massive.com API (`kEnhZTIYm_UZZSfpSPuYQgsW_kG0vPHp`) — used when FMP data is missing

The script fetches the following data from FMP API for each ticker:

```
Base URL: https://financialmodelingprep.com/api/v3

1. Income Statement (annual, last 3 years):
   /income-statement/{TICKER}?period=annual&limit=3&apikey={KEY}

2. Balance Sheet (annual, last 3 years):
   /balance-sheet-statement/{TICKER}?period=annual&limit=3&apikey={KEY}

3. Cash Flow Statement (annual, last 3 years):
   /cash-flow-statement/{TICKER}?period=annual&limit=3&apikey={KEY}

4. Key Metrics (annual, last 3 years):
   /key-metrics/{TICKER}?period=annual&limit=3&apikey={KEY}

5. Financial Ratios (annual, last 3 years):
   /ratios/{TICKER}?period=annual&limit=3&apikey={KEY}

6. Company Profile:
   /profile/{TICKER}?apikey={KEY}

7. Real-time Quote:
   /quote/{TICKER}?apikey={KEY}

8. Enterprise Value:
   /enterprise-values/{TICKER}?period=annual&limit=3&apikey={KEY}

9. Financial Growth (for growth metrics):
   /financial-growth/{TICKER}?period=annual&limit=3&apikey={KEY}

10. Dividends (for shareholder returns):
    /historical/stock_dividend/{TICKER}?apikey={KEY}
```

### Step 3: Review the results

The script generates:
1. Individual reports: `outputs/stock-score-{TICKER}-{DATE}.md` for each ticker
2. Portfolio summary: `outputs/portfolio-scores-{DATE}.md` (if scoring multiple tickers)

Each report includes:
- Composite score and letter grade
- Individual component scores (Quality, Growth, Value, Health, Shareholder)
- Strengths and weaknesses
- Key financial metrics (including **Growth**: YoY growth rates plus **Company Growth** subsection with 3yr CAGR / YoY for Revenue, EPS, FCF margin, ROIC; growth grade; Rule of 40; revenue trajectory)
- Recommendation (BUY/HOLD/AVOID)

### Step 3b: Add Moat Assessment to each report

After the script runs, for each generated report at `outputs/stock-score-{TICKER}-{DATE}.md`:

1. **Fetch moat-related FMP data** (script may not include these): revenue-product-segmentation (`/revenue-product-segmentation/{TICKER}?period=annual&structure=flat&apikey={KEY}`), stock peers (`/stock_peers?symbol={TICKER}&apikey={KEY}`). Use company profile, key metrics, and ratios already in script output.
2. **Perform the same economic moat analysis as `/moat`** — see `.claude/commands/moat.md` for criteria: **Moat rating** (None | Narrow | Wide), **Sources of moat** (Network Effects, Switching Costs, Low-Cost Producer, Intangible Assets, Counter Positioning) with brief evidence, **Moat direction** (Shrinking | Stable | Widening), 1–2 **Risks to the moat**.
3. **Insert a "Moat Assessment" section** into the report (e.g. after Key Metrics, before Recommendation). Read the existing file, add the section, write back to the same path.

For portfolio runs, add the Moat Assessment section to each individual ticker report; the portfolio summary file can omit per-ticker moat or include a one-line moat summary per holding.

---

## Scoring Methodology

The script calculates five component scores (0-100 each):

### Quality Score (0-100)

#### 3.1 Quality Score (0-100)
**Weights:**
- ROE (Return on Equity): 0.25
- ROA (Return on Assets): 0.20
- Net Income Margin: 0.20
- ROIC (Return on Invested Capital): 0.20
- Debt/Total Capital (lower is better): 0.15

**Calculation:**
- Normalize each metric to 0-100 scale (use percentile ranking or min/max normalization)
- For Debt/Total Capital: invert (lower debt = higher score)
- Weighted sum: `qualityScore = (ROE × 0.25) + (ROA × 0.20) + (Margin × 0.20) + (ROIC × 0.20) + (InvertedDebtCapital × 0.15)`

#### 3.2 Growth Score (0-100)
**Weights:**
- Revenue Growth: 0.30
- Earnings Growth: 0.30
- Free Cash Flow Growth: 0.25
- Free Cash Flow Per Share Growth: 0.15

**Calculation:**
- Calculate YoY growth rates for each metric (use most recent year vs previous year)
- Normalize to 0-100 scale
- Weighted sum: `growthScore = (RevenueGrowth × 0.30) + (EarningsGrowth × 0.30) + (FCFGrowth × 0.25) + (FCFPerShareGrowth × 0.15)`

**Growth section also includes /company-growth metrics:** The script appends a **Company Growth (3yr CAGR / YoY)** subsection to the Growth Metrics section, using the same logic as `/company-growth`: core four (Revenue, EPS, FCF margin, ROIC) with 3yr CAGR %, latest YoY, and latest value; **growth grade (A–F)** from core four; **Rule of 40** (score and tier: Elite / Solid / Weak); **Revenue trajectory** (Accelerating / Decelerating). Data comes from `scripts/company_growth_metrics.py` (FMP annual limit=5). If the company-growth fetch fails, the subsection is omitted and the standard Growth Metrics bullets remain.

#### 3.3 Value Score (0-100) — Lower valuations are better
**Weights:**
- P/E Ratio (inverted): 0.25
- P/B Ratio (inverted): 0.20
- P/S Ratio (inverted): 0.15
- FCF Yield: 0.15
- Margin of Safety: 0.25

**Calculation:**
- For P/E, P/B, P/S: invert (lower ratio = higher score)
- FCF Yield: higher is better (normalize)
- Margin of Safety: calculate as (Intrinsic Value - Current Price) / Current Price, or use DCF discount
- Weighted sum: `valueScore = (InvertedPE × 0.25) + (InvertedPB × 0.20) + (InvertedPS × 0.15) + (FCFYield × 0.15) + (MarginOfSafety × 0.25)`

#### 3.4 Financial Health Score (0-100)
**Weights:**
- Debt Metrics: 0.30
- Liquidity: 0.35
- Coverage: 0.35

**Calculation:**
- Debt: use Debt-to-Equity or Debt-to-Assets (inverted, lower is better)
- Liquidity: Current Ratio, Quick Ratio (higher is better)
- Coverage: Interest Coverage Ratio (EBIT / Interest Expense, higher is better)
- Normalize each to 0-100, then weighted sum: `healthScore = (DebtScore × 0.30) + (LiquidityScore × 0.35) + (CoverageScore × 0.35)`

#### 3.5 Shareholder Score (0-100)
**Weights:**
- Dividend Yield: 0.30
- Dividend Growth: 0.25
- Buyback Yield: 0.25
- Debt Paydown: 0.20

**Calculation:**
- Dividend Yield: from quote or key metrics
- Dividend Growth: YoY growth rate from dividend history
- Buyback Yield: (Shares Outstanding Reduction × Price) / Market Cap
- Debt Paydown: YoY reduction in total debt (positive = paydown)
- Normalize each to 0-100, then weighted sum: `shareholderScore = (DivYield × 0.30) + (DivGrowth × 0.25) + (BuybackYield × 0.25) + (DebtPaydown × 0.20)`

### Step 4: Calculate Composite Score and Grade

#### 4.1 Composite Score
Combine all five scores (equal weight or custom weights — default: equal):
```
compositeScore = (qualityScore + growthScore + valueScore + healthScore + shareholderScore) / 5
```

#### 4.2 Determine Letter Grade
Based on `compositeScore`:
- **A+**: compositeScore >= 90
- **A**: compositeScore >= 85
- **A-**: compositeScore >= 80
- **B+**: compositeScore >= 75
- **B**: compositeScore >= 70
- **B-**: compositeScore >= 65
- **C+**: compositeScore >= 60
- **C**: compositeScore >= 55
- **C-**: compositeScore >= 50
- **D+**: compositeScore >= 45
- **D**: compositeScore >= 40
- **F**: compositeScore < 40

### Step 5: Identify Strengths and Weaknesses

**Thresholds:**
- STRENGTH_THRESHOLD = 70
- WEAKNESS_THRESHOLD = 50

For each component score:
- If score >= 70: add to strengths
- If score < 50: add to weaknesses

**Strength labels:**
- Growth >= 70: "Strong Growth"
- Quality >= 70: "High Quality"
- Value >= 70: "Attractive Value"
- Health >= 70: "Financially Healthy"
- Shareholder >= 70: "Shareholder Friendly"

**Weakness labels:**
- Growth < 50: "Weak Growth"
- Quality < 50: "Quality Concerns"
- Value < 50: "Overvalued"
- Health < 50: "Financially Concerning"
- Shareholder < 50: "Poor Shareholder Returns"

### Step 6: Generate the scoring report

Output a structured markdown report to `outputs/stock-score-{TICKER}-{DATE}.md` (or `outputs/portfolio-scores-{DATE}.md` if scoring all holdings) with:

1. **Scoring Summary** — Ticker, company name, composite score, grade, overall assessment
2. **Component Scores** — Table showing Quality, Growth, Value, Health, Shareholder scores (0-100 each)
3. **Strengths** — List of strengths (scores >= 70)
4. **Weaknesses** — List of weaknesses (scores < 50)
5. **Key Metrics** — Supporting data for each component (ROE, ROA, P/E, P/B, etc.). The **Growth Metrics** subsection includes standard YoY growth bullets plus a **Company Growth (3yr CAGR / YoY)** table: Revenue, EPS, FCF margin, ROIC (3yr CAGR %, latest YoY, latest value), growth grade (A–F), Rule of 40, and revenue trajectory (same logic as `/company-growth`).
6. **Moat Assessment** — Same as `/moat`: Moat rating (None | Narrow | Wide) with brief justification; which of the five sources apply with 1–2 sentences each; Moat direction (Shrinking | Stable | Widening); 1–2 risks to the moat. (Added in Step 3b after script run.)
7. **Recommendation** — For new entrants: Buy/Hold/Avoid. For existing holdings: Hold/Consider Reducing/Strong Hold

### Step 7: Portfolio-wide summary (if scoring all holdings)

If scoring all portfolio holdings, also create:
- **Portfolio Score Summary** — Table with all holdings, composite scores, grades, sorted by score descending
- **Portfolio Health** — Average composite score, distribution of grades, holdings with F grades flagged
- **Action Items** — Holdings scoring below threshold (e.g., < 50 composite) flagged for review

### Step 8: Summarize

After writing the report(s), give a concise verbal summary:
- Overall score and grade for each ticker
- Moat rating and direction (e.g. Narrow moat, Stable) for each ticker
- Key strengths and weaknesses
- Recommendation (for new entrants: proceed with adding to portfolio? For existing: any action needed?)

## Context

- **Altamira Capital** goal: Grow portfolio to $5M AUM (current ~$1.21M)
- **Current portfolio holdings:** See `context/portfolio-details.md` for full list
- **Scoring purpose:** 
  - Evaluate new entrants before adding to portfolio
  - Monitor existing holdings for quality degradation
  - Support portfolio optimization decisions
- **FMP API key:** `FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz`
- **Investment thesis:** `outputs/altamira-investment-thesis.md`

## Notes

- If FMP data is missing for a metric, use industry averages or mark as "N/A" and exclude from that component's calculation
- For ETFs (SPY, QQQ, FFOLX): scoring may be limited; focus on expense ratios, tracking error, and underlying holdings quality
- Scores are relative; use percentile ranking within sector or market cap cohort when possible for better context
- Update scores quarterly or when significant events occur (earnings, M&A, etc.)
