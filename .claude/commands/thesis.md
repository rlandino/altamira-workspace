# /thesis — Automated Investment Thesis Generator

Generate a comprehensive, data-driven investment thesis for any US-listed ticker with DCF valuation, comps analysis, and a clear buy/hold/avoid recommendation.

## Instructions

You are generating a full investment thesis for Altamira Capital. Follow these steps exactly:

### Step 1: Identify the ticker

The user will provide a ticker symbol as an argument: $ARGUMENTS

If no ticker is provided, ask for one. Accept any US-listed ticker — the thesis can be generated for potential additions beyond the core universe (AAPL, AMZN, AVGO, COST, GOOGL, MA, META, MSFT, NVDA, SPY, V).

### Step 2: Fetch comprehensive data from FMP API

Use the FMP API (key: `FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz`) to pull financial data. Make these API calls in parallel where possible:

```
Base URL: https://financialmodelingprep.com/api/v3

1. Company Profile:
   /profile/{TICKER}?apikey={KEY}

2. Income Statement (5 years annual + 4 quarters):
   /income-statement/{TICKER}?period=annual&limit=5&apikey={KEY}
   /income-statement/{TICKER}?period=quarter&limit=4&apikey={KEY}

3. Balance Sheet (5 years):
   /balance-sheet-statement/{TICKER}?period=annual&limit=5&apikey={KEY}

4. Cash Flow (5 years):
   /cash-flow-statement/{TICKER}?period=annual&limit=5&apikey={KEY}

5. Key Metrics (5 years):
   /key-metrics/{TICKER}?period=annual&limit=5&apikey={KEY}

6. Financial Ratios (5 years):
   /ratios/{TICKER}?period=annual&limit=5&apikey={KEY}

7. Analyst Estimates (next 4 quarters + 2 years):
   /analyst-estimates/{TICKER}?limit=8&apikey={KEY}

8. Insider Transactions (last 6 months):
   /insider-trading?symbol={TICKER}&limit=20&apikey={KEY}

9. Institutional Holders (top holders):
   /institutional-holder/{TICKER}?apikey={KEY}

10. Peers/Competitors:
    /stock_peers?symbol={TICKER}&apikey={KEY}

11. Real-time Quote:
    /quote/{TICKER}?apikey={KEY}

12. DCF (FMP's own calculation):
    /discounted-cash-flow/{TICKER}?apikey={KEY}

13. Historical DCF:
    /historical-discounted-cash-flow-statement/{TICKER}?period=annual&limit=5&apikey={KEY}

14. Rating:
    /rating/{TICKER}?apikey={KEY}

15. Price Target Consensus:
    /price-target-consensus/{TICKER}?apikey={KEY}

16. Earnings Surprises:
    /earnings-surprises/{TICKER}?apikey={KEY}

17. Revenue Segmentation:
    /revenue-product-segmentation/{TICKER}?period=annual&structure=flat&apikey={KEY}

18. Sector Performance:
    /sector-performance?apikey={KEY}
```

### Step 3: Build DCF Valuation Model

Using the financial data, construct a 5-year DCF model:

1. **Revenue projection**: Use analyst estimates for Y1-Y2, then fade growth rate to terminal (3-4% nominal GDP)
2. **Margin assumptions**: Use trailing 3Y average operating margin, with trend adjustment
3. **FCF calculation**: Operating income x (1 - tax rate) + D&A - CapEx - change in working capital
4. **WACC estimation**:
   - Risk-free rate: Use 10Y Treasury (~4.5%)
   - Equity risk premium: 5.5%
   - Beta: From company profile
   - Cost of equity: Rf + Beta x ERP
   - If debt exists: WACC = E/(E+D) x Ke + D/(E+D) x Kd x (1-t)
5. **Terminal value**: FCF_Y5 x (1 + g) / (WACC - g) where g = 3%
6. **Enterprise value**: Sum of discounted FCFs + discounted terminal value
7. **Equity value**: EV - net debt + cash
8. **Per share**: Equity value / shares outstanding
9. **Sensitivity table**: Show implied price at WACC +/-1% and terminal growth +/-0.5%

### Step 4: Comparable Company Analysis

Using the peers list from the stock_peers endpoint:

1. Pull profile + key metrics for top 5 peers (use `/profile/{PEER}` and `/key-metrics/{PEER}?period=annual&limit=1` for each)
2. Compare: EV/EBITDA, P/E, P/FCF, Revenue Growth, Operating Margin, ROE
3. Calculate where the subject ticker trades relative to peer median
4. Calculate implied price from peer median multiples

### Step 5: Insider & Institutional Analysis

1. Summarize insider transactions: net buys vs. sells over 6 months, notable C-suite transactions
2. Top 10 institutional holders and % ownership
3. Any notable changes in institutional ownership

### Step 6: Generate Thesis Document

Output to `outputs/thesis-{TICKER}-{DATE}.md` with these sections:

**Section 1: Title Page**

```
# Investment Thesis: {COMPANY NAME} ({TICKER})

**Date:** {DATE}
**Prepared by:** Altamira Capital Research
**Current Price:** ${PRICE}
**Fair Value (Base Case):** ${FAIR_VALUE}
**Verdict:** {BUY / HOLD / AVOID}
```

**Section 2: Executive Summary**

One paragraph. State the verdict, fair value estimate, current price, upside/downside percentage, and conviction level (High / Medium / Low). This should be self-contained — a reader should understand the recommendation from this paragraph alone.

**Section 3: Company Overview**

- Business description (2-3 sentences)
- Revenue segments (table from revenue segmentation data)
- Market position and competitive advantages
- Moat assessment: None / Narrow / Wide — with justification

**Section 4: Financial Analysis**

Present in tables with 5Y data:

- **Growth trajectory**: Revenue, EPS, FCF growth rates (5Y table)
- **Profitability trends**: Gross Margin, Operating Margin, Net Margin, EBITDA Margin, ROE, ROIC (5Y table)
- **Balance sheet strength**: Total Debt/EBITDA, Interest Coverage, Current Ratio, Cash/Total Assets
- **Cash flow quality**: FCF Conversion (FCF/Net Income), CapEx as % of revenue, FCF Margin
- **Quality score (1-10)**: Based on:
  - Revenue growth consistency (low variance = higher score)
  - Margin stability or expansion
  - ROE consistently > 15%
  - FCF positive every year
  - Debt/EBITDA < 3x

**Section 5: Valuation**

- **DCF model**: Show all assumptions in a table, then the result
- **Sensitivity table**: WACC (rows) vs terminal growth (columns) — show implied share price in each cell
- **Comparable company analysis**: Peer comparison table, implied price from median multiples
- **Historical valuation range**: 5Y P/E and EV/EBITDA min/median/max vs current
- **Fair value range**:
  - Bear case: $X (methodology)
  - Base case: $X (methodology)
  - Bull case: $X (methodology)

**Section 6: Bull Case**

3-5 bullets. What goes right? Growth catalysts, market expansion, margin improvement, product launches, secular tailwinds.

**Section 7: Bear Case**

3-5 bullets. What goes wrong? Competitive threats, regulatory risk, macro sensitivity, execution risk, valuation compression.

**Section 8: Base Case**

Most likely scenario. Expected total return over 12 months (price appreciation + dividend yield). State key assumptions.

**Section 9: Catalyst Timeline**

Table of upcoming events that could move the stock:

| Date (Est.) | Event | Potential Impact |
|-------------|-------|-----------------|
| {DATE} | Earnings (Q{X} FY{YYYY}) | {Impact assessment} |
| {DATE} | {Product launch / regulatory / macro event} | {Impact assessment} |

Use earnings surprises data and analyst estimates to inform this.

**Section 10: Insider & Institutional Sentiment**

- Net insider buying/selling over 6 months (total shares and dollar value)
- Notable C-suite transactions (CEO, CFO, directors)
- Top 10 institutional holders with ownership %
- Sentiment read: Bullish / Neutral / Bearish signal

**Section 11: Altamira Fit Assessment**

- **Universe fit**: Does it meet core criteria? (Mega-cap, liquid options, quality fundamentals)
- **Strategy applicability**:
  - CSP candidate? If yes: ideal delta (0.20-0.30), DTE (30-45), current IV assessment
  - Momentum candidate? If yes: 50-day SMA status, trend strength
  - Conviction long? If yes: what makes it a core holding
- **Position sizing**: At $100K portfolio with 5% max position = $5,000 max allocation
- **Sector concentration check**: Which sector does this add to? Does it breach 25% sector limit?

**Section 12: Verdict**

```
## Verdict: {BUY / HOLD / AVOID}

| Metric | Value |
|--------|-------|
| Fair Value (Base Case) | ${X} |
| Fair Value Range | ${BEAR} — ${BULL} |
| Current Price | ${X} |
| Upside/Downside | {X}% |
| Conviction | {High / Medium / Low} |
| Quality Score | {X}/10 |
| Recommended Strategy | {CSP / Momentum Long / Conviction Long / Avoid} |
```

Decision framework:
- **BUY**: Upside > 15%, Quality Score >= 7, conviction High or Medium
- **HOLD**: Upside 5-15%, or Quality Score 5-6, or fair-valued within the range
- **AVOID**: Downside risk, Quality Score < 5, or doesn't fit Altamira's risk framework

**Section 13: Appendix**

- 5Y Income Statement summary table (Revenue, COGS, Gross Profit, OpEx, Operating Income, Net Income, EPS)
- 5Y Balance Sheet summary table (Total Assets, Total Liabilities, Total Equity, Cash, Total Debt)
- 5Y Cash Flow summary table (Operating CF, CapEx, FCF, Dividends, Buybacks)

### Step 7: Summarize

After writing the thesis, provide a concise verbal summary:
- Fair value vs current price (upside/downside %)
- Conviction level and quality score
- Recommended Altamira strategy (CSP, Momentum, Conviction Long, or Avoid)
- Key risk to monitor
- One sentence on timing (is now a good entry point?)

## Context

- **Altamira Capital** — Multi-strategy investment firm (solo founder, early stage)
- **Core universe:** AAPL, AMZN, AVGO, COST, GOOGL, MA, META, MSFT, NVDA, SPY, V
- **Strategies:** CSP (0.20-0.30 delta, 30-45 DTE), Equity Momentum (50-day MA), Conviction Longs, Conditional Hedging
- **Targets:** 12-18% net Year 1, Sharpe > 1.5, max drawdown < -15%
- **Portfolio allocation:** Options 35%, Momentum 20%, Conviction 15%, Hedging 0-3%, Cash ~27%
- **Risk framework:** 5% max position, 25% max sector, 30% options allocation, 15% min cash
- **Investment thesis:** `outputs/altamira-investment-thesis.md`
- **Risk management:** `outputs/risk-management-framework.md`
- **This command differs from /analyze-ticker**: /analyze-ticker focuses on financial ratio analysis (3Y data, ratio interpretation). /thesis goes deeper — 5Y data, DCF valuation, comps analysis, insider/institutional data, and a full publishable thesis with buy/hold/avoid verdict.
