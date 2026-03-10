# /portfolio-report — Portfolio Performance Report

Generate a portfolio performance and risk report for Altamira Capital.

## Instructions

You are generating a portfolio performance report for Altamira Capital. Follow these steps exactly:

### Step 1: Determine report type

The user may specify a report type as an argument: $ARGUMENTS

Options:
- `daily` — End-of-day snapshot (default)
- `weekly` — Weekly performance review
- `monthly` — Monthly performance + benchmark comparison
- `holdings` — Current holdings analysis without performance history

If no argument, default to `daily`.

### Step 2: Fetch portfolio data

Use the FMP API (key: `FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz`) to pull market data for the core universe.

```
Base URL: https://financialmodelingprep.com/api/v3

1. Quotes for full universe (batch):
   /quote/AAPL,AMZN,AVGO,COST,GOOGL,MA,META,MSFT,NVDA,SPY,V?apikey={KEY}

2. SPY benchmark performance:
   /stock-price-change/SPY?apikey={KEY}

3. Sector ETF performance:
   /quote/XLK,XLF,XLV,XLY,XLP,XLE,XLI,XLB,XLRE,XLU,XLC?apikey={KEY}

4. VIX level:
   /quote/%5EVIX?apikey={KEY}

5. Treasury yields (risk-free context):
   /treasury?from={30_DAYS_AGO}&to={TODAY}&apikey={KEY}

6. Market gainers/losers (context):
   /stock_market/gainers?apikey={KEY}
   /stock_market/losers?apikey={KEY}
```

### Step 3: Check for existing portfolio data

Look for any portfolio tracking files:
- `outputs/trade-journal.csv` or similar
- Google Sheets links in `context/current-data.md`
- Any position data files in `outputs/`

If no portfolio data exists yet (paper trading not started), generate a **market overview + watchlist report** instead of a performance report. Note this clearly.

### Step 4: Generate the report

Reference the `client-reporting-automation` skill from `~/.claude/skills/`.

Output to `outputs/portfolio-report-{DATE}.md` with the following sections:

**For daily/weekly reports:**

1. **Market Summary**
   - S&P 500, NASDAQ, DOW performance (1D, WTD, MTD, YTD)
   - VIX level and regime (Low/Normal/Elevated/High)
   - Top 3 gainers and losers in the market
   - Sector performance heatmap (text table)

2. **Watchlist Performance**
   - Each ticker in the universe: price, daily change, WTD change, MTD change
   - Rank by daily performance
   - Flag any ticker moving > 2% (opportunity or risk)

3. **Sector Exposure Analysis**
   - Map universe tickers to sectors
   - Show sector concentration
   - Compare to S&P 500 sector weights
   - Flag over/under-weights

4. **Options Landscape**
   - VIX level and what it means for premium selling
   - Which tickers in the universe have elevated IV (good for selling)
   - Earnings proximity for each ticker
   - Sizing adjustment based on VIX regime

5. **Risk Dashboard**
   - Current VIX regime and recommended sizing
   - Drawdown tier status (based on SPY from recent high)
   - Cash reserve recommendation
   - Correlation check: Are watchlist tickers moving together?

6. **Action Items**
   - Top 3 tickers to analyze further (based on opportunity signals)
   - Any risk flags requiring attention
   - Suggested next steps

**For monthly reports (add to above):**

7. **Benchmark Comparison**
   - SPY MTD, QTD, YTD returns
   - 10-year Treasury yield (risk-free rate)
   - Sharpe context: What return is needed to beat risk-free rate?

8. **Strategy Assessment**
   - Which strategies would have worked this month? (Premium selling vs. directional)
   - VIX trend over the month
   - Sector rotation trends

### Step 5: Summarize

After writing the report, give a concise verbal summary:
- Market regime (bull/bear/range-bound)
- Top opportunity from the watchlist
- Key risk to monitor
- One recommended action

## Context

- **Altamira Capital** — Multi-strategy investment firm (solo founder, early stage)
- **Core universe:** AAPL, AMZN, AVGO, COST, GOOGL, MA, META, MSFT, NVDA, SPY, V
- **Benchmark:** SPY total return
- **Targets:** 12-18% net Year 1, Sharpe > 1.5, max drawdown < -15%
- **Portfolio allocation:** 40-50% options, 30-40% equity long, 0-10% short, 15-25% cash
- **Risk framework:** Drawdown tiers at -5%/-10%/-15%, VIX-adjusted sizing
- **Investment thesis:** `outputs/altamira-investment-thesis.md`
- **Current status:** Paper trading phase — no live positions yet
