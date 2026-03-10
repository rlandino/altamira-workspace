# /analyze-ticker — Financial Ratio Analysis

Perform comprehensive financial ratio analysis on a ticker using live FMP API data.

## Instructions

You are running a financial ratio analysis for Altamira Capital. Follow these steps exactly:

### Step 1: Identify the ticker

The user will provide a ticker symbol as an argument: $ARGUMENTS

If no ticker is provided, ask for one. Default universe: AAPL, AMZN, AVGO, COST, GOOGL, MA, META, MSFT, NVDA, SPY, V

### Step 2: Fetch data from FMP API

Use the FMP API (key: `FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz`) to pull financial data. Make these API calls in parallel:

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

8. Analyst Estimates:
   /analyst-estimates/{TICKER}?limit=4&apikey={KEY}

9. Revenue/Product Segmentation (for moat assessment):
   /revenue-product-segmentation/{TICKER}?period=annual&structure=flat&apikey={KEY}

10. Stock Peers (for moat competitive context):
    /stock_peers?symbol={TICKER}&apikey={KEY}
```

### Step 3: Perform economic moat analysis (Morningstar-style)

Using the FMP data (and optionally research/search), perform the same analysis as the `/moat` command. See `.claude/commands/moat.md` for full criteria.

- **Moat rating:** Choose exactly one of **None** | **Narrow** | **Wide** (Wide = strong durable advantages, multiple sources, high stable returns; Narrow = real advantages but vulnerable; None = no durable advantage).
- **Sources of moat:** For each of the five, state whether it applies and 1–2 sentences of evidence: (1) Network Effects, (2) Switching Costs, (3) Low-Cost Producer, (4) Intangible Assets, (5) Counter Positioning.
- **Moat direction:** Choose exactly one of **Shrinking** | **Stable** | **Widening** and justify with margins/ROIC trends or competitive/regulatory context.

### Step 4: Analyze using the financial ratios skill

Reference the `analyzing-financial-ratios` skill from `~/.claude/skills/`. Calculate and interpret:

**Profitability:** ROE, ROA, ROIC, Gross Margin, Operating Margin, Net Margin, EBITDA Margin
**Liquidity:** Current Ratio, Quick Ratio, Cash Ratio, Operating Cash Flow Ratio
**Leverage:** Debt-to-Equity, Debt-to-Assets, Interest Coverage, Equity Multiplier
**Efficiency:** Asset Turnover, Inventory Turnover, Receivables Turnover, Cash Conversion Cycle
**Valuation:** P/E, P/B, EV/EBITDA, FCF Yield, PEG Ratio

For each ratio: show value, 3-year trend (improving/declining/stable), and interpretation.

### Step 5: Generate the analysis report

Output a structured markdown report to `outputs/analysis-{TICKER}-{DATE}.md` with:

1. **Company Overview** — Name, sector, market cap, current price
2. **Investment Summary** — 3-sentence thesis: bull case, bear case, overall assessment
3. **Moat Assessment** — Same as `/moat`: **Moat rating** (None | Narrow | Wide) with 1–2 sentence justification; **Sources of moat** (which of the five apply: Network Effects, Switching Costs, Low-Cost Producer, Intangible Assets, Counter Positioning) with brief evidence; **Moat direction** (Shrinking | Stable | Widening) with 1–2 sentence justification; 1–2 **Risks to the moat**
4. **Profitability Analysis** — All profitability ratios with trends
5. **Balance Sheet Health** — Liquidity and leverage ratios
6. **Operational Efficiency** — Efficiency ratios and cash conversion
7. **Valuation Assessment** — Valuation ratios vs. historical and sector
8. **Key Risks** — Top 3 risks based on ratio analysis
9. **Altamira Relevance** — Does this ticker fit our investment thesis? (reference `outputs/altamira-investment-thesis.md` for strategy alignment)

### Step 6: Summarize

After writing the report, give a concise verbal summary:
- Moat rating and direction (e.g. Narrow moat, Stable)
- Overall financial health rating (Strong / Adequate / Weak)
- Whether it fits Altamira's universe and strategy
- One-line recommendation for next action

## Context

- **Altamira Capital** is a multi-strategy investment firm focused on US large/mega-cap equities and options
- **Core universe:** AAPL, AMZN, AVGO, COST, GOOGL, MA, META, MSFT, NVDA, SPY, V
- **Strategy:** Options premium selling (CSPs, covered calls, spreads) + fundamental equity long
- **Key parameters:** 0.20-0.30 delta, 30-45 DTE, 5% max position size
- **Investment thesis:** `outputs/altamira-investment-thesis.md`
