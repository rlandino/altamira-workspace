# Altamira Trade Idea Generator - 2026-06-10

**Portfolio holdings parsed:** 20  
**Watchlist tickers parsed:** 26  
**Sources:** `context/portfolio-details.md`, `context/watchlist.md`, FMP live market data when available.

> For research and education only. Not investment advice. Confirm prices, deltas, liquidity, earnings dates, and account risk limits before placing trades.

---

## Market Regime

- **VIX:** 20.2 (NORMAL)
- **Data mode:** live FMP market data
- **Sizing note:** CSPs and covered calls are acceptable if liquidity and risk limits pass.

## Top Trade Ideas

| Rank | Ticker | Strategy | Setup | Action | Key Risk |
|------|--------|----------|-------|--------|----------|
| 1 | MSFT | Manage existing short put | 2026-03-20 430P, 5 contracts | Review roll/close thresholds before adding any new exposure in this name. | Existing short-premium risk should take priority over new entries. |
| 2 | AMAT | Covered call | 2026-07-10 580C against shares | Sell only if the credit meets the portfolio's income hurdle and you are willing to trim above the strike. | Covered by existing shares; cap upside above strike. |
| 3 | SPY | Covered call | 2026-07-10 780C against shares | Sell only if the credit meets the portfolio's income hurdle and you are willing to trim above the strike. | Covered by existing shares; cap upside above strike. Name also has open short-put exposure. |
| 4 | AVGO | Covered call | 2026-07-10 395C against shares | Sell only if the credit meets the portfolio's income hurdle and you are willing to trim above the strike. | Covered by existing shares; cap upside above strike. Name also has open short-put exposure. |
| 5 | LRCX | Cash-secured put | 2026-07-10 320P cash-secured put | Enter only if bid/ask liquidity is clean and credit justifies risk. | NORMAL VIX regime; use <=5% max-risk sizing. Semi exposure is already high; prefer defined risk or smaller size. |

## Idea Rationale

### 1. MSFT - Manage existing short put

- **Setup:** 2026-03-20 430P, 5 contracts
- **Why:** Underlying is -6.3% vs short strike; current option value $22.40 vs entry credit $8.70.
- **Action:** Review roll/close thresholds before adding any new exposure in this name.
- **Risk:** Existing short-premium risk should take priority over new entries.

### 2. AMAT - Covered call

- **Setup:** 2026-07-10 580C against shares
- **Why:** Portfolio weight 12.6% with bullish trend; 20d change +23.1%, RSI 74.2.
- **Action:** Sell only if the credit meets the portfolio's income hurdle and you are willing to trim above the strike.
- **Risk:** Covered by existing shares; cap upside above strike.

### 3. SPY - Covered call

- **Setup:** 2026-07-10 780C against shares
- **Why:** Portfolio weight 17.1% with neutral trend; 20d change -0.1%, RSI 46.0.
- **Action:** Sell only if the credit meets the portfolio's income hurdle and you are willing to trim above the strike.
- **Risk:** Covered by existing shares; cap upside above strike. Name also has open short-put exposure.

### 4. AVGO - Covered call

- **Setup:** 2026-07-10 395C against shares
- **Why:** Portfolio weight 16.7% with neutral trend; 20d change -10.4%, RSI 39.5.
- **Action:** Sell only if the credit meets the portfolio's income hurdle and you are willing to trim above the strike.
- **Risk:** Covered by existing shares; cap upside above strike. Name also has open short-put exposure.

### 5. LRCX - Cash-secured put

- **Setup:** 2026-07-10 320P cash-secured put
- **Why:** B watchlist candidate (Top Candidate); bullish trend; 20d change +19.5%, RSI 68.3.
- **Action:** Enter only if bid/ask liquidity is clean and credit justifies risk.
- **Risk:** NORMAL VIX regime; use <=5% max-risk sizing. Semi exposure is already high; prefer defined risk or smaller size.

## Portfolio Context

| Ticker | Weight | Context price | Live price | Day change | Bias |
|--------|--------|---------------|------------|------------|------|
| SPY | 17.1% | $686.29 | $736.79 | -0.0% | neutral trend |
| AVGO | 16.7% | $333.51 | $375.35 | -4.3% | neutral trend |
| GOOGL | 13.8% | $303.33 | $366.40 | +0.6% | oversold |
| AMAT | 12.6% | $369.30 | $528.10 | +5.8% | bullish trend |
| MSFT | 6.7% | $399.60 | $402.89 | -0.1% | neutral trend |
| AMZN | 4.9% | $204.79 | $241.31 | -1.2% | oversold |
| AAPL | 4.6% | $264.35 | $290.23 | -0.1% | neutral trend |
| CRWD | 4.3% | $415.76 | $659.74 | +2.3% | neutral trend |

## Existing Short Premium

| Ticker | Position | Credit | Current | Note |
|--------|----------|--------|---------|------|
| MSFT | 2026-03-20 430P x5 | $8.70 | $22.40 | underlying -6.3% vs strike |
| MSFT | 2026-05-15 380P x5 | $10.12 | $11.80 | underlying +6.0% vs strike |
| AVGO | 2026-03-20 310P x5 | $12.60 | $5.00 | underlying +21.1% vs strike |
| SPY | 2026-05-15 620P x5 | $6.92 | $10.16 | underlying +18.8% vs strike |
| COST | 2026-05-15 900P x5 | $11.00 | $12.40 | underlying +7.9% vs strike |

## Watchlist Focus

| Ticker | Score | Grade | Status | Live price | Bias | Earnings |
|--------|-------|-------|--------|------------|------|----------|
| LRCX | 67.4 | B | Top Candidate | $345.31 | bullish trend | - |
| NVDA | 66.2 | B | Top Candidate | $205.70 | neutral trend | - |
| TSM | 61.8 | B- | Top Candidate | $420.73 | bullish trend | 2026-07-16 |
| KLAC | 61.3 | B- | Top Candidate | $2,292.11 | bullish trend | - |
| ADBE | 60.1 | B- | Top Candidate | $236.46 | neutral trend | 2026-06-11 |
| ASML | 58.9 | C+ | Consider | $1,799.67 | bullish trend | 2026-07-15 |
| LLY | 58.7 | C+ | Consider | $1,152.01 | bullish trend | - |
| ACN | 56.3 | C+ | Consider | $172.13 | bearish trend | 2026-06-18 |
| INTU | n/a | — | Consider | $285.95 | bearish trend | - |
| CRM | 50.7 | C | Monitor | $174.24 | neutral trend | - |
| CDNS | 48.8 | C- | Monitor | $396.60 | bullish trend | - |
| ANET | 48.7 | C- | Monitor | $153.80 | neutral trend | - |

## Risk Controls

- Keep single-position risk within the 5% max-risk rule and options allocation within the 30% cap.
- Do not sell new premium through known earnings unless the trade is intentionally an earnings strategy.
- For covered calls, only sell strikes where assignment would be acceptable.
- For model-based strikes, confirm actual deltas and credits in the broker before entry.
