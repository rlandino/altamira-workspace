# Trade Idea Generator - 2026-05-06

## Executive Summary

- Source files: `context/portfolio-details.md` and `context/watchlist.md`.
- Portfolio market value from context: **$1,207,271**.
- Weighted day change from position table: **+0.66%**.
- Data quality: **Input snapshot is 77 days old (2026-02-18). Refresh portfolio and option chains before placing any trade.**
- Verdict: **Risk-manage first, then selectively add non-overlapping watchlist exposure.**

## Top Portfolio Concentrations

| Symbol | Weight | Market Value | Total P&L | Day Change |
|--------|--------|--------------|-----------|------------|
| SPY | 17.1% | $205,887 | +43.3% | +0.5% |
| AVGO | 16.7% | $202,107 | +175.4% | +0.3% |
| GOOGL | 13.8% | $167,135 | +74.0% | +0.4% |
| AMAT | 12.6% | $152,521 | +100.5% | +2.8% |
| MSFT | 6.7% | $80,320 | +21.7% | +0.7% |

## Top Watchlist Candidates

| Ticker | Score | Grade | Company | Status |
|--------|-------|-------|---------|--------|
| LRCX | 67.4 | B | Lam Research Corporation | Top Candidate |
| NVDA | 66.2 | B | NVIDIA Corporation | Top Candidate |
| TSM | 61.8 | B- | Taiwan Semiconductor Manufacturing Company | Top Candidate |
| KLAC | 61.3 | B- | KLA Corporation | Top Candidate |
| ADBE | 60.1 | B- | Adobe Inc. | Top Candidate |

## Trade Ideas

1. Risk-first trade: reduce concentration before adding new semiconductor exposure.
   - Trigger: SPY, AVGO, GOOGL, and AMAT are each above 10% portfolio weight.
   - Action: prioritize trimming or covered-call overlays on the largest winners before opening new LRCX/NVDA/TSM/KLAC risk.
   - Rationale: this aligns the book with the documented single-position risk discipline and frees buying power for better entries.

2. Watchlist opportunity: ADBE is the cleanest non-semiconductor top-candidate add.
   - Trigger: ADBE is B- scored and diversifies away from the existing AVGO/AMAT semiconductor overweight.
   - Action: use a starter position or defined-risk put spread only after checking live trend, IV, earnings date, and liquidity.
   - Rationale: it keeps quality-growth exposure while reducing incremental chip-cycle concentration.

3. Options management: audit stale/near-dated short puts before adding premium risk.
   - Trigger: repository option context includes expired March 2026 contracts and May 15 contracts inside 14 days.
   - Action: reconcile broker reality first; close winners at 50-60% max profit and avoid rolling losers unless the updated thesis still holds.
   - Rationale: stale option state is the highest operational risk in this run.

4. Cash deployment posture: wait for fresh data before initiating new CSPs.
   - Trigger: live FMP/Massive keys were not available to validate IV, delta, spreads, or earnings windows.
   - Action: treat today's output as a pre-trade shortlist, not an executable order ticket.
   - Rationale: short-premium edge depends on live chain pricing and liquidity.

## Option Position Audit

| Ticker | Contract | Expiration | Credit | Current | Contracts | Status |
|--------|----------|------------|--------|---------|-----------|--------|
| MSFT | 430 Put | 2026-03-20 | 8.70 | 22.40 | 5 | expired |
| MSFT | 380 Put | 2026-05-15 | 10.12 | 11.80 | 5 | 9 DTE |
| AVGO | 310 Put | 2026-03-20 | 12.60 | 5.00 | 5 | expired |
| SPY | 620 Put | 2026-05-15 | 6.92 | 10.16 | 5 | 9 DTE |
| COST | 900 Put | 2026-05-15 | 11.00 | 12.40 | 5 | 9 DTE |

## Risk Notes

- Financial information is for research and planning only, not individualized investment advice.
- Confirm live prices, option chains, earnings dates, bid/ask spreads, and account buying power before trading.
- The current context has portfolio concentration above the documented 5% single-position risk limit, so new risk should be sized conservatively.
