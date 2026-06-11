# Altamira Trade Idea Generator - 2026-06-11

**Portfolio holdings parsed:** 20  
**Watchlist tickers parsed:** 26  
**Sources:** `context/portfolio-details.md`, `context/watchlist.md`, FMP live market data when available.

> For research and education only. Not investment advice. Confirm prices, deltas, liquidity, earnings dates, and account risk limits before placing trades.

---

## Market Regime

- **VIX:** n/a (UNKNOWN)
- **Data mode:** context-only; FMP_API_KEY missing
- **Sizing note:** CSPs and covered calls are acceptable if liquidity and risk limits pass.
- **Static options note:** Skipped 5 expired short-premium row(s) from repository context.

## Top Trade Ideas

| Rank | Ticker | Strategy | Setup | Action | Key Risk |
|------|--------|----------|-------|--------|----------|
| 1 | SPY | Covered call | 2026-07-17 730C against shares | Sell only if the credit meets the portfolio's income hurdle and you are willing to trim above the strike. | Covered by existing shares; cap upside above strike. |
| 2 | AVGO | Covered call | 2026-07-17 355C against shares | Sell only if the credit meets the portfolio's income hurdle and you are willing to trim above the strike. | Covered by existing shares; cap upside above strike. |
| 3 | GOOGL | Covered call | 2026-07-17 320C against shares | Sell only if the credit meets the portfolio's income hurdle and you are willing to trim above the strike. | Covered by existing shares; cap upside above strike. |
| 4 | AMAT | Covered call | 2026-07-17 390C against shares | Sell only if the credit meets the portfolio's income hurdle and you are willing to trim above the strike. | Covered by existing shares; cap upside above strike. |
| 5 | MSFT | Covered call | 2026-07-17 420C against shares | Sell only if the credit meets the portfolio's income hurdle and you are willing to trim above the strike. | Covered by existing shares; cap upside above strike. |

## Idea Rationale

### 1. SPY - Covered call

- **Setup:** 2026-07-17 730C against shares
- **Why:** Portfolio weight 17.1% with neutral trend; 20d change n/a, RSI n/a.
- **Action:** Sell only if the credit meets the portfolio's income hurdle and you are willing to trim above the strike.
- **Risk:** Covered by existing shares; cap upside above strike.

### 2. AVGO - Covered call

- **Setup:** 2026-07-17 355C against shares
- **Why:** Portfolio weight 16.7% with neutral trend; 20d change n/a, RSI n/a.
- **Action:** Sell only if the credit meets the portfolio's income hurdle and you are willing to trim above the strike.
- **Risk:** Covered by existing shares; cap upside above strike.

### 3. GOOGL - Covered call

- **Setup:** 2026-07-17 320C against shares
- **Why:** Portfolio weight 13.8% with neutral trend; 20d change n/a, RSI n/a.
- **Action:** Sell only if the credit meets the portfolio's income hurdle and you are willing to trim above the strike.
- **Risk:** Covered by existing shares; cap upside above strike.

### 4. AMAT - Covered call

- **Setup:** 2026-07-17 390C against shares
- **Why:** Portfolio weight 12.6% with neutral trend; 20d change n/a, RSI n/a.
- **Action:** Sell only if the credit meets the portfolio's income hurdle and you are willing to trim above the strike.
- **Risk:** Covered by existing shares; cap upside above strike.

### 5. MSFT - Covered call

- **Setup:** 2026-07-17 420C against shares
- **Why:** Portfolio weight 6.7% with neutral trend; 20d change n/a, RSI n/a.
- **Action:** Sell only if the credit meets the portfolio's income hurdle and you are willing to trim above the strike.
- **Risk:** Covered by existing shares; cap upside above strike.

## Portfolio Context

| Ticker | Weight | Context price | Live price | Day change | Bias |
|--------|--------|---------------|------------|------------|------|
| SPY | 17.1% | $686.29 | n/a | n/a | neutral trend |
| AVGO | 16.7% | $333.51 | n/a | n/a | neutral trend |
| GOOGL | 13.8% | $303.33 | n/a | n/a | neutral trend |
| AMAT | 12.6% | $369.30 | n/a | n/a | neutral trend |
| MSFT | 6.7% | $399.60 | n/a | n/a | neutral trend |
| AMZN | 4.9% | $204.79 | n/a | n/a | neutral trend |
| AAPL | 4.6% | $264.35 | n/a | n/a | neutral trend |
| CRWD | 4.3% | $415.76 | n/a | n/a | neutral trend |

## Existing Short Premium

| Ticker | Position | Credit | Current | Note |
|--------|----------|--------|---------|------|
| - | - | - | - | No active rows parsed; skipped 5 expired static row(s). |

## Watchlist Focus

| Ticker | Score | Grade | Status | Live price | Bias | Earnings |
|--------|-------|-------|--------|------------|------|----------|
| LRCX | 67.4 | B | Top Candidate | n/a | price unavailable | - |
| NVDA | 66.2 | B | Top Candidate | n/a | price unavailable | - |
| TSM | 61.8 | B- | Top Candidate | n/a | price unavailable | - |
| KLAC | 61.3 | B- | Top Candidate | n/a | price unavailable | - |
| ADBE | 60.1 | B- | Top Candidate | n/a | price unavailable | - |
| ASML | 58.9 | C+ | Consider | n/a | price unavailable | - |
| LLY | 58.7 | C+ | Consider | n/a | price unavailable | - |
| ACN | 56.3 | C+ | Consider | n/a | price unavailable | - |
| INTU | n/a | — | Consider | n/a | price unavailable | - |
| CRM | 50.7 | C | Monitor | n/a | price unavailable | - |
| CDNS | 48.8 | C- | Monitor | n/a | price unavailable | - |
| ANET | 48.7 | C- | Monitor | n/a | price unavailable | - |

## Risk Controls

- Keep single-position risk within the 5% max-risk rule and options allocation within the 30% cap.
- Do not sell new premium through known earnings unless the trade is intentionally an earnings strategy.
- For covered calls, only sell strikes where assignment would be acceptable.
- For model-based strikes, confirm actual deltas and credits in the broker before entry.
