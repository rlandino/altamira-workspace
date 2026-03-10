# /client-report — Client Portfolio Performance Report

Generate a professional, client-facing portfolio performance report for Altamira Capital suitable for sharing with investors or stakeholders.

## Instructions

You are generating a polished client portfolio report for Altamira Capital. This differs from `/portfolio-report` (internal/operational) — this produces a narrative-driven, presentation-ready document. Follow these steps exactly:

### Step 1: Determine report type and date range

The user may specify a report type as an argument: $ARGUMENTS

Options:
- `monthly` — Monthly performance report (default)
- `quarterly` — Quarterly performance review
- `annual` — Annual performance summary

Calculate the date range:
- **Monthly**: First to last day of the previous calendar month
- **Quarterly**: First to last day of the previous quarter (Q1: Jan-Mar, Q2: Apr-Jun, Q3: Jul-Sep, Q4: Oct-Dec)
- **Annual**: Full previous calendar year

### Step 2: Fetch market data from FMP API

Use the FMP API (key: `FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz`) to pull market data. Make these API calls in parallel:

```
Base URL: https://financialmodelingprep.com/api/v3

1. Universe quotes (current):
   /quote/AAPL,AMZN,AVGO,COST,GOOGL,MA,META,MSFT,NVDA,SPY,V?apikey={KEY}

2. SPY benchmark performance:
   /stock-price-change/SPY?apikey={KEY}

3. Historical prices for period returns:
   /historical-price-full/SPY?from={PERIOD_START}&to={PERIOD_END}&apikey={KEY}

4. Sector ETF performance:
   /quote/XLK,XLF,XLV,XLY,XLP,XLE,XLI,XLB,XLRE,XLU,XLC?apikey={KEY}

5. Sector ETF price changes:
   /stock-price-change/XLK,XLF,XLV,XLY,XLP,XLE,XLI,XLB,XLRE,XLU,XLC?apikey={KEY}

6. VIX level:
   /quote/%5EVIX?apikey={KEY}

7. Treasury yields (risk-free rate):
   /treasury?from={30_DAYS_AGO}&to={TODAY}&apikey={KEY}

8. S&P 500 index:
   /quote/%5EGSPC?apikey={KEY}

9. Company profiles (for sector mapping):
   /profile/AAPL?apikey={KEY}
   /profile/AMZN?apikey={KEY}
   (repeat for each universe ticker)

10. Universe historical prices (for period returns):
    /historical-price-full/AAPL?from={PERIOD_START}&to={PERIOD_END}&apikey={KEY}
    (repeat for each universe ticker)
```

### Step 3: Check for portfolio and trade data

Look for trade data in this order:
1. `outputs/trade-journal.csv` or similar CSV files
2. Google Sheets links in `context/current-data.md`
3. Any position/portfolio data files in `outputs/`
4. `outputs/paper-trading-plan.md` for portfolio parameters

**If no trade data exists yet** (paper trading not started), generate a **template report** with:
- Market data sections fully populated from API data
- Portfolio-specific sections using placeholder values clearly marked as `[PLACEHOLDER — update with actual data]`
- A note that this is a template pending paper trading launch

### Step 4: Calculate performance metrics

**Return Metrics:**
- Period return (MTD, QTD, or YTD depending on report type)
- Year-to-date return
- Since-inception return
- Alpha vs SPY benchmark (portfolio return - SPY return)
- Excess return vs risk-free rate (10Y Treasury)

**Risk Metrics:**
- Sharpe Ratio: (Annualized Return - Risk-Free Rate) / Annualized Std Dev
- Sortino Ratio: (Annualized Return - Risk-Free Rate) / Downside Deviation
- Maximum Drawdown: Largest peak-to-trough decline
- Current Drawdown: Current NAV vs peak NAV
- Win Rate: Winning trades / Total trades
- Average Win / Average Loss ratio
- Profit Factor: Gross Profits / Gross Losses
- Beta vs SPY

**Strategy Attribution:**
Calculate returns for each of the 5 portfolio sleeves:
- CSP Sleeve (target 35%): Premium collected, assignment rate, annualized return
- Momentum Sleeve (target 20%): Long equity returns, signal accuracy
- Conviction Sleeve (target 15%): Core holdings performance
- Hedging Sleeve (target 0-3%): Cost of hedging, effectiveness
- Cash Sleeve (target ~27%): Money market / T-bill yield

### Step 5: Generate the client report

Output to `outputs/client-report-{TYPE}-{DATE}.md` with these sections:

**Section 1: Cover**

```
# Altamira Capital

## {Monthly / Quarterly / Annual} Performance Report

**Period:** {Start Date} — {End Date}
**Report Date:** {TODAY}
**Prepared by:** Altamira Capital

---
```

**Section 2: Executive Summary**

3-4 sentences covering:
- Portfolio NAV and period return
- Performance vs SPY benchmark (outperformed/underperformed by X%)
- Key highlight of the period (best trade, strategy adjustment, milestone)
- Forward outlook in one sentence

**Section 3: Performance Overview**

| Metric | Period | YTD | Since Inception |
|--------|--------|-----|-----------------|
| Portfolio Return | X.XX% | X.XX% | X.XX% |
| SPY Benchmark | X.XX% | X.XX% | X.XX% |
| Alpha | X.XX% | X.XX% | X.XX% |
| Sharpe Ratio | X.XX | X.XX | X.XX |
| Sortino Ratio | X.XX | X.XX | X.XX |
| Max Drawdown | -X.XX% | -X.XX% | -X.XX% |
| Win Rate | XX% | XX% | XX% |
| Profit Factor | X.XX | X.XX | X.XX |

Include a brief narrative interpreting the numbers (2-3 sentences).

**Section 4: Performance Attribution**

**By Strategy:**

| Strategy | Allocation | Period Return | Contribution | Notes |
|----------|-----------|--------------|-------------|-------|
| Cash-Secured Puts | XX% | X.XX% | X.XX% | Trades: X, Win Rate: XX% |
| Equity Momentum | XX% | X.XX% | X.XX% | Signals: X, Accuracy: XX% |
| Conviction Longs | XX% | X.XX% | X.XX% | Holdings: X |
| Hedging | XX% | X.XX% | X.XX% | Cost: $X |
| Cash / T-Bills | XX% | X.XX% | X.XX% | Risk-free yield |
| **Total** | **100%** | **X.XX%** | **X.XX%** | |

**By Ticker (Top 5 Contributors / Bottom 5 Detractors):**

| Rank | Ticker | Strategy | P&L | Contribution |
|------|--------|----------|-----|-------------|
| 1 | XXXX | CSP | +$X,XXX | +X.XX% |
| ... | | | | |

**Section 5: Holdings Analysis**

**Current Positions:**
- Open options positions (ticker, strike, expiry, delta, P&L)
- Equity positions (ticker, shares, cost basis, market value, unrealized P&L)
- Total invested vs cash

**Sector Allocation:**

| Sector | Allocation | Limit | Status |
|--------|-----------|-------|--------|
| Technology | XX.X% | 25% | Within / Near / Over |
| Financial Services | XX.X% | 25% | Within |
| Consumer Defensive | XX.X% | 25% | Within |
| Cash | XX.X% | 15% min | Compliant |

Map universe tickers: Tech = AAPL, MSFT, GOOGL, AMZN, AVGO, META, NVDA | Financial = V, MA | Consumer = COST | Index = SPY

**Section 6: Risk Dashboard**

| Risk Metric | Current | Limit | Status |
|-------------|---------|-------|--------|
| Max Position Size | X.X% | 5% | OK |
| Sector Concentration | XX% | 25% | OK |
| Options Allocation | XX% | 30% | OK |
| Cash Reserve | XX% | 15% min | OK |
| Current Drawdown | -X.X% | -15% max | OK |
| Correlated Positions | X | 3 per sector | OK |

**VIX Regime History:**

| Date Range | VIX Range | Regime | Sizing Adjustment |
|------------|-----------|--------|-------------------|
| {dates} | XX-XX | Normal | 100% |

- Current VIX: XX.X ({regime})
- Period average VIX: XX.X
- Drawdown tier: None / Tier 1 / Tier 2 / Tier 3

**Section 7: Options Activity**

| Metric | Period | Cumulative |
|--------|--------|-----------|
| CSPs Written | X | X |
| Total Premium Collected | $X,XXX | $X,XXX |
| Premium Retained (closed) | $X,XXX | $X,XXX |
| Assignment Rate | X% | X% |
| Average Delta at Entry | -0.XX | -0.XX |
| Average DTE at Entry | XX | XX |
| Positions Rolled | X | X |
| Positions Expired Worthless | X | X |
| Closed at 50% Profit | X | X |
| Stopped Out (200% credit) | X | X |

**Section 8: Market Commentary**

Write 2-3 paragraphs covering:
- S&P 500 and major index performance during the period
- VIX environment and what it meant for premium selling
- Sector rotation trends (which sectors led/lagged)
- Macro context (Fed policy, economic data, geopolitical events)
- How market conditions affected portfolio strategy

Use data from the FMP API calls. Be factual, not speculative.

**Section 9: Outlook & Strategy**

Write 2-3 paragraphs covering:
- Forward VIX regime expectation and impact on CSP strategy
- Strategy adjustments for the coming period (if any)
- Key catalysts to watch (earnings dates, Fed meetings, macro events)
- Portfolio rebalancing needs
- Any changes to risk parameters

**Section 10: Appendix**

**A. Trade Log Summary**

| # | Date | Ticker | Strategy | Direction | Entry | Exit | P&L | DTE | Notes |
|---|------|--------|----------|-----------|-------|------|-----|-----|-------|
| 1 | {date} | XXXX | CSP | STO | $X.XX | $X.XX | +$XXX | XX | Closed at 50% |

**B. Glossary**

| Term | Definition |
|------|-----------|
| CSP | Cash-Secured Put — selling a put option while holding cash to cover potential assignment |
| Sharpe Ratio | Risk-adjusted return metric: (Return - Risk-Free Rate) / Standard Deviation |
| Sortino Ratio | Downside risk-adjusted return: (Return - Risk-Free Rate) / Downside Deviation |
| Alpha | Excess return vs benchmark (SPY) |
| IV Rank | Current implied volatility relative to 52-week range |
| DTE | Days to expiration |
| Delta | Option sensitivity to $1 move in underlying |
| VIX | CBOE Volatility Index — market's expectation of 30-day S&P 500 volatility |
| Profit Factor | Gross profits divided by gross losses |
| Max Drawdown | Largest peak-to-trough portfolio decline |

**C. Disclosures**

```
IMPORTANT DISCLOSURES

This report is prepared for informational purposes only and does not
constitute investment advice, a solicitation, or a recommendation to
buy or sell any securities.

Past performance is not indicative of future results. All investments
involve risk, including the possible loss of principal.

Options trading involves significant risk and is not appropriate for
all investors. The strategies discussed may result in losses exceeding
the initial investment.

Paper trading results may not reflect actual trading conditions.
Simulated results have inherent limitations including the benefit of
hindsight and do not account for slippage, partial fills, or
emotional factors.

Altamira Capital | {CURRENT_YEAR}
```

### Step 6: Format and finalize

Apply professional formatting:
- All return percentages to 2 decimal places
- Dollar amounts with commas (e.g., $1,234.56)
- Dates in YYYY-MM-DD format
- Consistent table alignment
- Clear section dividers with `---` between major sections
- Tone: professional, confident, data-driven — suitable for external audience

### Step 7: Summarize

After writing the report, give a concise verbal summary:
- Portfolio return vs benchmark for the period
- Sharpe ratio and risk compliance status
- Best-performing strategy and top contributor
- Key risk flag (if any)
- One recommended action for the next period

## Context

- **Altamira Capital** — Multi-strategy investment firm (solo founder, early stage)
- **Core universe:** AAPL, AMZN, AVGO, COST, GOOGL, MA, META, MSFT, NVDA, SPY, V
- **Benchmark:** SPY total return
- **Portfolio size:** $100K paper trading, scaling to $5M AUM
- **Targets:** 12-18% net annual return, Sharpe > 1.5, max drawdown < -15%
- **Portfolio allocation:** CSP 35%, Momentum 20%, Conviction 15%, Hedging 0-3%, Cash 20-27%
- **Options parameters:** 0.20-0.30 delta, 30-45 DTE, IV Rank > 30%, close at 50% profit, stop at 200% credit
- **VIX regimes:** Low (<15): 75% size, Normal (15-25): 100%, Elevated (25-35): 50%, Crisis (>35): 25%
- **Risk limits:** 5% max position, 25% max sector, 30% options allocation, 15% min cash
- **Drawdown tiers:** -5% (reduce new positions), -10% (half sizing), -15% (no new risk)
- **This differs from /portfolio-report:** /portfolio-report is an internal operational report. /client-report is polished, narrative-driven, and suitable for investors or external stakeholders.
- **Investment thesis:** `outputs/altamira-investment-thesis.md`
- **Allocation model:** `outputs/portfolio-allocation-model.md`
- **Risk framework:** `outputs/risk-management-framework.md`
- **Paper trading plan:** `outputs/paper-trading-plan.md`
