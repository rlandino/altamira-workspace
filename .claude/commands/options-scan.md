# /options-scan — Quantitative Options Analysis

Scan options chains and generate trade recommendations for a ticker using live market data. **OCA (Options Chain Analyzer) criteria v2.1.0 — VIX + Institutional Signals (12 signals)** per `reference/institutional-signals-spec.md`.

## Instructions

You are running a quantitative options analysis for Altamira Capital. Follow these steps exactly:

### Step 1: Identify the ticker

The user will provide a ticker symbol as an argument: $ARGUMENTS

If no ticker is provided, ask for one. Default universe: AAPL, AMZN, AVGO, COST, GOOGL, MA, META, MSFT, NVDA, SPY, V

### Step 2: Fetch market and options data

Use **FMP API** for market data and **Massive.com API** for options chain data. Make these API calls in parallel:

**FMP API** (key: `FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz`):
```
Base URL: https://financialmodelingprep.com/api/v3

1. Real-time Quote:
   /quote/{TICKER}?apikey={KEY}

2. Historical Price (30 days, for technicals):
   /historical-price-full/{TICKER}?from={30_DAYS_AGO}&to={TODAY}&apikey={KEY}

3. Earnings Calendar (upcoming):
   /historical/earning_calendar/{TICKER}?apikey={KEY}

4. VIX Level:
   /quote/%5EVIX?apikey={KEY}

5. Key Metrics (for fundamentals context):
   /key-metrics/{TICKER}?period=annual&limit=1&apikey={KEY}
```

**Massive.com API** (key: `4PVSr1pGDqABoSgBkVbmgZb89LVpGGeq`) — **Primary source for options chain data**:
```
Base URL: https://api.massive.com/v3

Option Chain Snapshot (correct endpoint per Massive docs):
GET /v3/snapshot/options/{TICKER}?apiKey={KEY}&limit=250

Full URL example: https://api.massive.com/v3/snapshot/options/COST?apiKey=4PVSr1pGDqABoSgBkVbmgZb89LVpGGeq&limit=250

Authentication: Pass the API key as the query parameter apiKey= (not as Authorization: Bearer). Using Bearer header returns 401.

Headers (optional): Content-Type: application/json

Query Parameters:
  - apiKey: (required) Your Massive.com API key
  - limit: Max results (default 10, max 250)
  - expiration_date: YYYY-MM-DD
  - expiration_date.gte / .lte: Range filter
  - strike_price, strike_price.gte / .lte
  - contract_type: call | put
  - sort, order

Response includes: results[].details (strike, expiration, contract_type), greeks (delta, gamma, theta, vega), implied_volatility, last_quote (bid/ask), open_interest, underlying_asset.

Troubleshooting 401: Use apiKey in the query string. Do not use Authorization: Bearer — Massive market data API expects apiKey as query param. Old path /v1/options/chain/{TICKER} returns 404; use /v3/snapshot/options/{TICKER} only.
```

**Full chain for OCA (institutional signals):** To compute Put/Call ratios, UOA, IV skew, and GEX, fetch a **full chain** (both calls and puts) for 20–60 DTE. Either: (a) request without `contract_type` and filter client-side by expiration (e.g. `expiration_date.gte` = 20 days from today, `expiration_date.lte` = 60 days), or (b) request both `contract_type=call` and `contract_type=put` with the same expiration range; use pagination or multiple requests if needed (limit max 250 per request). If Massive returns only a subset, P/C and GEX are approximate; document "over 20–60 DTE where data available."

**Note:** If Massive.com API is unavailable, fall back to FMP `/options-chain/{TICKER}` endpoint (though it often returns empty). If both fail, note in the report that options chain data is unavailable and provide market context and strategy parameters for manual chain lookup.

### Step 3: Process the options chain

Process options chain data from **Massive.com API** (primary source). Reference the `quantitative-options-analysis` skill from `~/.claude/skills/` if available. Perform:

**Chain Filtering:**
- Filter to expirations 20-60 DTE (focus on 30-45 DTE sweet spot)
- Remove options with volume < 10, open interest < 50, or bid = 0
- Calculate bid-ask spread as % of mid price — flag if > 10% (illiquid)
- Calculate IV Rank: Current IV vs 52-week IV range (need historical IV data or estimate from chain)

**Greeks Analysis:**
- Use delta, gamma, theta, vega from Massive.com API response (should be included in chain data)
- If Greeks are missing, estimate delta from moneyness: `delta ≈ N(d1)` where d1 uses Black-Scholes approximation
- Focus on 0.15-0.35 delta range for premium selling candidates
- Calculate theta/delta ratio for each candidate (higher = better premium decay per unit of risk)
- Calculate IV for each contract (should be in Massive.com response)

**Technical Context:**
- Calculate 20-day SMA, RSI (14-period), and current price vs. SMA
- Determine technical bias: Bullish (price > SMA, RSI 40-70), Bearish (price < SMA, RSI < 40), Overbought (RSI > 70), Oversold (RSI < 30)

**Earnings Check:**
- Flag if earnings are within the expiration window
- If earnings within DTE: note IV crush opportunity or avoidance recommendation

### Step 3b: Institutional signals (OCA criteria)

**Reference:** OCA (Options Chain Analyzer) criteria and formulas are from `reference/institutional-signals-spec.md` (Options Chain Analyzer + Institutional Signals). Compute these from the full chain (calls + puts, 20–60 DTE) and VIX quote. If Greeks or IV are missing for some contracts, skip those for skew/GEX or use only contracts with data; state in report when signals are partial.

**1. Put/Call Ratio** — Over 20–60 DTE options: (a) Volume P/C = Put Volume / Call Volume; (b) OI P/C = Put OI / Call OI; (c) Dollar-weighted P/C = sum(put premium × volume) / sum(call premium × volume). Report all three.

**2. Unusual Options Activity (UOA)** — For each option, if volume > 2 × open_interest, count it. Report: count of unusual contracts, binary "has UOA" (count > 0), and optional list of strikes. Optionally flag large blocks (e.g. single-trade premium > $100k) if trade data available.

**3. IV Skew** — From chain, find put with delta ≈ -0.25 and call with delta ≈ +0.25 (same expiration window). Use their `implied_volatility`. Skew = Put IV / Call IV (or report Put IV − Call IV in vol points). Interpret: skew > 1 = typical; elevated skew = more put demand / tail hedging.

**4. Dealer Gamma Exposure (GEX)** — For each contract: GEX_i = gamma_i × OI_i × 100 × Spot² (gamma from `greeks.gamma`, OI from chain, Spot from underlying quote). Sum GEX across 20–60 DTE strikes; identify strike where |GEX| is largest (max-gamma strike). Report total GEX (scaled), max-gamma strike.

**5. Net Options Sentiment** — Composite -100 (max put/bearish) to +100 (max call/bullish). Map P/C > 1 → negative, P/C < 1 → positive; map skew > 1 → negative; combine and scale to -100..+100. Output `netSentiment` integer; optional breakdown by component.

**6. Confidence Score Adjustment** — For put-selling strategies: if net sentiment > 20 (bullish), apply +3 to +5 to composite score; if net sentiment < -20 (bearish), apply -3 to -5; else 0. Put UOA on same ticker: optional small negative adjustment. Output `confidenceAdjustment` (e.g. -5 to +5).

**7. VIX Regime Detection** — Classify VIX (from FMP quote): VIX < 15 → LOW; 15–25 → NORMAL; 25–35 → ELEVATED; > 35 → CRISIS. Report regime label in Market Context and use in sizing/confidence.

**8. VIX-Adjusted Position Sizing** — LOW: 75%; NORMAL: 100%; ELEVATED: 50%; CRISIS: 25%. Apply: maxAllocation = portfolioValue × maxPositionPct × (sizingPct / 100). Report in Risk Assessment and Action.

**9. VIX-Adjusted Confidence** — LOW/NORMAL: multiplier 1.0; ELEVATED: 0.90; CRISIS: 0.75. Compute: adjustedScore = (compositeScore + confidenceAdjustment) × vixConfidenceMultiplier. Use in ranking and final action.

**10. Regime-Specific Strategies** — LOW: naked CSP, covered calls; NORMAL: CSP, bull put spreads, covered calls; ELEVATED: prefer defined-risk spreads, reduce size; CRISIS: spreads only, minimal size. Output short text (e.g. "Prefer spreads; reduce size") for Action section.

**11. Liquidity Score (1–10)** — Per contract or per ticker (best contract in chain). Inputs: bid-ask spread as % of mid, OI tiers, volume tiers. Tiers from spec: spread < 5%, OI > 500, vol > 50 → 9–10; spread 5–10%, OI 100–500, vol 10–50 → 6–8; spread > 10% or OI < 50 or vol < 10 → 1–4. Report integer 1–10.

**12. Backtesting** — No execution in scan. In report, add one-line note: "Backtest metrics (hit rate, return by regime/sentiment) use logged scan data per institutional-signals-spec; see CSP Scans sheet / backtest script."

### Step 4: Generate strategy recommendations

Rank recommendations using a composite score that incorporates **confidence adjustment** (Step 3b.6) and **VIX-adjusted confidence** (Step 3b.9), so institutional alignment affects CONSIDER ENTRY / WATCHLIST / AVOID. For each applicable strategy, find the best candidate contract:

**1. Cash-Secured Put (CSP)**
- Target: 0.20-0.30 delta put, 30-45 DTE
- Show: Strike, premium (credit), breakeven, max loss, annualized return on capital
- Assignment scenario: "If assigned at {strike}, your cost basis is {breakeven} — is this a good entry?"

**2. Covered Call** (if already holding shares)
- Target: 0.20-0.30 delta call, 30-45 DTE
- Show: Strike, premium, upside cap, if-called return

**3. Bull Put Spread** (defined risk)
- Target: Sell 0.25-0.30 delta put, buy put 5-10 strikes lower
- Show: Net credit, max loss, max profit, breakeven, probability of profit

**4. Jade Lizard** (if IV is elevated — IV Rank > 50)
- Target: Short put + short call spread collecting more premium than call spread width
- Show: Net credit, max risk (downside only), breakeven

### Step 5: Risk assessment

For each recommendation:
- Position size at 5% max of a $100K portfolio (calculate contracts), then apply **VIX-adjusted position sizing** (Step 3b.8): LOW 75%, NORMAL 100%, ELEVATED 50%, CRISIS 25% of that max. Report VIX regime and effective sizing %.
- Check: Does this breach the 30% options allocation limit?
- VIX regime note: Current VIX level and regime label (LOW / NORMAL / ELEVATED / CRISIS); sizing adjustment per thesis.
- Liquidity score (1-10): From Step 3b.11 (bid-ask % of mid, OI, volume tiers per spec).

### Step 7: Output the scan report

Output a structured markdown report to `outputs/options-scan-{TICKER}-{DATE}.md` with:

1. **Market Context** — Price, 30-day trend, RSI, VIX level and **VIX regime** (LOW / NORMAL / ELEVATED / CRISIS), earnings proximity
2. **Options Chain Summary** — Total contracts scanned, filtered, expirations analyzed
3. **Top Recommendations** — Ranked by risk-adjusted return (incorporating confidence adjustment and VIX-adjusted confidence)
   - For each: strategy, contract details, Greeks, P&L scenarios, sizing
4. **Risk Flags** — Earnings proximity, liquidity warnings, IV extremes
5. **Action** — Clear recommendation: CONSIDER ENTRY / WATCHLIST / AVOID with rationale; include **Regime strategy** line (e.g. "Prefer spreads; reduce size" when ELEVATED/CRISIS)
6. **Institutional signals (OCA)** — Put/Call (volume, OI, dollar-weighted), UOA (count, has UOA, optional strikes), IV skew (25Δ put/call), total GEX and max-gamma strike, net sentiment (-100 to +100), confidence adjustment, VIX regime, regime strategy line, liquidity score (1–10). Optionally: "Backtest metrics use logged scan data per institutional-signals-spec; see CSP Scans sheet / backtest script."

Also give a concise verbal summary after writing the report.

## Context

- **Altamira Capital** is a multi-strategy investment firm
- **Primary strategy:** Options premium selling (CSPs, covered calls, spreads, jade lizards)
- **Parameters:** 0.20-0.30 delta, 30-45 DTE, IV Rank > 30%, max 5% position, 30% options allocation cap
- **Risk management:** Close at 50% profit, stop at 200% of credit, never hold through unplanned earnings
- **OCA criteria:** Formulas and 12 institutional signals (Put/Call, UOA, IV skew, GEX, net sentiment, confidence adjustment, VIX regime/sizing/confidence, regime strategies, liquidity score, backtesting) are from `reference/institutional-signals-spec.md` (Options Chain Analyzer + Institutional Signals).
- **Investment thesis:** `outputs/altamira-investment-thesis.md`
- **Infrastructure checklist:** `outputs/trading-infrastructure-setup.md`
