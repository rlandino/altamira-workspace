# Trade Idea Generator - 2026-05-01

## Summary

- Portfolio market value from repository context: **$1,207,271**
- Current holdings parsed: **20**
- Watchlist names parsed: **26**
- Live quote source: Yahoo Finance quote endpoint, then FMP fallback, then repository snapshot prices.
- Options premiums are not estimated without a live chain; confirm bid/ask before entry.

## Top Portfolio Exposures

| Ticker | Weight | Current | P&L % |
|--------|--------|---------|-------|
| SPY | 17.1% | $723.87 | 43.3% |
| AVGO | 16.7% | $420.63 | 175.4% |
| GOOGL | 13.8% | $384.66 | 74.0% |
| AMAT | 12.6% | $397.23 | 100.5% |
| MSFT | 6.7% | $410.72 | 21.7% |
| AMZN | 4.9% | $271.22 | 80.7% |

## Top Watchlist Candidates

| Ticker | Score | Grade | Status |
|--------|-------|-------|--------|
| LRCX | 67.4 | B | ⭐ Top Candidate |
| NVDA | 66.2 | B | ⭐ Top Candidate |
| TSM | 61.8 | B- | ⭐ Top Candidate |
| KLAC | 61.3 | B- | ⭐ Top Candidate |
| ADBE | 60.1 | B- | ⭐ Top Candidate |

## Ranked Trade Ideas

### 1. LRCX - Cash-secured put

- **Action:** Sell 1 2026-06-05 230P if credit meets target
- **Score:** 93.7
- **Rationale:** Lam Research Corporation is a ⭐ Top Candidate with score 67.4 (B); target entry is about 10% below the latest quote ($259.37).
- **Primary risk:** Assignment risk; only enter if willing to own shares at the breakeven.
### 2. NVDA - Cash-secured put

- **Action:** Sell 1 2026-06-05 175P if credit meets target
- **Score:** 93.1
- **Rationale:** NVIDIA Corporation is a ⭐ Top Candidate with score 66.2 (B); target entry is about 10% below the latest quote ($199.81).
- **Primary risk:** Assignment risk; only enter if willing to own shares at the breakeven.
### 3. TSM - Cash-secured put

- **Action:** Sell 1 2026-06-05 360P if credit meets target
- **Score:** 88.9
- **Rationale:** Taiwan Semiconductor Manufacturing Company is a ⭐ Top Candidate with score 61.8 (B-); target entry is about 10% below the latest quote ($402.58).
- **Primary risk:** Assignment risk; only enter if willing to own shares at the breakeven.
### 4. KLAC - Bull put spread

- **Action:** Sell 2026-06-05 1560P / buy 1460P
- **Score:** 88.7
- **Rationale:** KLA Corporation is a ⭐ Top Candidate with score 61.3 (B-); target entry is about 10% below the latest quote ($1733.88).
- **Primary risk:** Defined-risk spread because naked put collateral would exceed the 5% position cap.
### 5. ADBE - Cash-secured put

- **Action:** Sell 1 2026-06-05 220P if credit meets target
- **Score:** 88.0
- **Rationale:** Adobe Inc. is a ⭐ Top Candidate with score 60.1 (B-); target entry is about 10% below the latest quote ($245.20).
- **Primary risk:** Assignment risk; only enter if willing to own shares at the breakeven.
### 6. AVGO - Covered call

- **Action:** Sell 3 2026-06-05 450C against existing shares
- **Score:** 83.7
- **Rationale:** AVGO is 16.7% of portfolio and up 175.4%; harvest premium while trimming upside concentration.
- **Primary risk:** Assignment caps upside above strike; avoid if a near-term catalyst changes conviction.
### 7. AMAT - Covered call

- **Action:** Sell 3 2026-06-05 425C against existing shares
- **Score:** 77.6
- **Rationale:** AMAT is 12.6% of portfolio and up 100.5%; harvest premium while trimming upside concentration.
- **Primary risk:** Assignment caps upside above strike; avoid if a near-term catalyst changes conviction.
### 8. SPY - Covered call

- **Action:** Sell 3 2026-06-05 770C against existing shares
- **Score:** 76.4
- **Rationale:** SPY is 17.1% of portfolio and up 43.3%; harvest premium while trimming upside concentration.
- **Primary risk:** Assignment caps upside above strike; avoid if a near-term catalyst changes conviction.
### 9. GOOGL - Covered call

- **Action:** Sell 3 2026-06-05 410C against existing shares
- **Score:** 76.2
- **Rationale:** GOOGL is 13.8% of portfolio and up 74.0%; harvest premium while trimming upside concentration.
- **Primary risk:** Assignment caps upside above strike; avoid if a near-term catalyst changes conviction.

## Risk Notes

- Keep single-trade risk within the 5% position cap and aggregate options exposure within the 30% options limit.
- Do not sell premium through an unplanned earnings event.
- Close short premium at 50% of max profit or stop at 200% of credit, consistent with the workspace risk framework.

_Educational only; not financial advice._
