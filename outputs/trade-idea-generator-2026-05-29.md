# Trade Idea Generator — 2026-05-29

> Educational analysis only; not investment advice. Validate live option chains, liquidity, earnings dates, and risk limits before placing any trade.

## Run Summary

- Portfolio positions parsed: **20**
- Watchlist entries parsed: **26**
- Open short premium positions parsed: **5**
- Live quote data: **no / repository snapshot fallback**
- VIX: **N/A**

## Top Trade / Management Ideas

### 1. AVGO — Short Put management

- **Action:** Close / harvest profit
- **Setup:** 5x AVGO 2026-03-20 310P
- **Score:** 92.0
- **Source:** Existing option expiring 2026-03-20
- **Rationale:** Current mark is 40% of original credit; estimated open P&L $3,800.00.
- **Risk:** Waiting for the last premium can turn a winner into gamma/assignment risk.

### 2. MSFT — Short Put management

- **Action:** Defend or roll
- **Setup:** 5x MSFT 2026-03-20 430P
- **Score:** 88.0
- **Source:** Existing option expiring 2026-03-20
- **Rationale:** Current mark is 257% of original credit; estimated open P&L $-6,850.00.
- **Risk:** Position is beyond the 200% credit stop threshold in the risk framework.

### 3. SPY — Covered call

- **Action:** Sell 0.20-0.30 delta call
- **Setup:** 2026-07-03 ~710C, up to 3 contract(s); target 1-2% notional credit.
- **Score:** 80.0
- **Source:** Current portfolio holding
- **Rationale:** SPY is a 17.1% portfolio weight; covered calls monetize concentration while preserving defined upside. No known earnings conflict inside scan window.
- **Risk:** Caps upside above the short strike; avoid oversizing around earnings or major catalysts.

### 4. AVGO — Covered call

- **Action:** Sell 0.20-0.30 delta call
- **Setup:** 2026-07-03 ~345C, up to 6 contract(s); target 1-2% notional credit.
- **Score:** 80.0
- **Source:** Current portfolio holding
- **Rationale:** AVGO is a 16.7% portfolio weight; covered calls monetize concentration while preserving defined upside. No known earnings conflict inside scan window.
- **Risk:** Caps upside above the short strike; avoid oversizing around earnings or major catalysts.

### 5. GOOGL — Covered call

- **Action:** Sell 0.20-0.30 delta call
- **Setup:** 2026-07-03 ~315C, up to 5 contract(s); target 1-2% notional credit.
- **Score:** 76.8
- **Source:** Current portfolio holding
- **Rationale:** GOOGL is a 13.8% portfolio weight; covered calls monetize concentration while preserving defined upside. No known earnings conflict inside scan window.
- **Risk:** Caps upside above the short strike; avoid oversizing around earnings or major catalysts.

### 6. AMAT — Covered call

- **Action:** Sell 0.20-0.30 delta call
- **Setup:** 2026-07-03 ~385C, up to 4 contract(s); target 1-2% notional credit.
- **Score:** 74.7
- **Source:** Current portfolio holding
- **Rationale:** AMAT is a 12.6% portfolio weight; covered calls monetize concentration while preserving defined upside. No known earnings conflict inside scan window.
- **Risk:** Caps upside above the short strike; avoid oversizing around earnings or major catalysts.

### 7. MSFT — Covered call

- **Action:** Sell 0.20-0.30 delta call
- **Setup:** 2026-07-03 ~420C, up to 2 contract(s); target 1-2% notional credit.
- **Score:** 64.1
- **Source:** Current portfolio holding
- **Rationale:** MSFT has enough shares for up to 2 covered call contract(s); trend unavailable. No known earnings conflict inside scan window.
- **Risk:** Caps upside above the short strike; avoid oversizing around earnings or major catalysts.

### 8. AMZN — Covered call

- **Action:** Sell 0.20-0.30 delta call
- **Setup:** 2026-07-03 ~220C, up to 2 contract(s); target 1-2% notional credit.
- **Score:** 60.8
- **Source:** Current portfolio holding
- **Rationale:** AMZN has enough shares for up to 2 covered call contract(s); trend unavailable. No known earnings conflict inside scan window.
- **Risk:** Caps upside above the short strike; avoid oversizing around earnings or major catalysts.

### 9. AAPL — Covered call

- **Action:** Sell 0.20-0.30 delta call
- **Setup:** 2026-07-03 ~280C, up to 2 contract(s); target 1-2% notional credit.
- **Score:** 60.3
- **Source:** Current portfolio holding
- **Rationale:** AAPL has enough shares for up to 2 covered call contract(s); trend unavailable. No known earnings conflict inside scan window.
- **Risk:** Caps upside above the short strike; avoid oversizing around earnings or major catalysts.

### 10. CRWD — Covered call

- **Action:** Sell 0.20-0.30 delta call
- **Setup:** 2026-07-03 ~440C, up to 1 contract(s); target 1-2% notional credit.
- **Score:** 59.7
- **Source:** Current portfolio holding
- **Rationale:** CRWD has enough shares for up to 1 covered call contract(s); trend unavailable. No known earnings conflict inside scan window.
- **Risk:** Caps upside above the short strike; avoid oversizing around earnings or major catalysts.

## Portfolio Flags

- Concentration watch: SPY 17.1%, AVGO 16.7%, GOOGL 13.8%, AMAT 12.6%. Prefer income/trim ideas over adding more exposure.
- Risk framework target cash reserve is >=15%; confirm current cash before new CSPs.

## Data Warnings

- FMP_API_KEY is not set; using repository snapshot prices only.

## Execution Checklist

1. Re-check live quotes and option chain bid/ask spreads.
2. Confirm no earnings or binary catalysts inside the intended DTE window.
3. Confirm portfolio cash, concentration, and options allocation limits.
4. Enter only with predefined 50% profit-taking and 200% credit stop rules.
