# Trade Idea Generator — 2026-05-02

> Source: repository context files (`context/portfolio-details.md`, `context/watchlist.md`).
> This is not financial advice. Verify live prices, option chains, liquidity, and earnings dates before placing trades.

## Portfolio Snapshot

- Portfolio market value from context: $1,207,271
- Top 5 holdings weight: 66.9%
- Approximate tech/growth weight: 64.6%
- Positions >=10% weight: SPY (17.1%), AVGO (16.7%), GOOGL (13.8%), AMAT (12.6%)

## Top Trade Ideas

| Rank | Idea | Type | Rationale / Action |
|------|------|------|--------------------|
| 1 | Defend / roll MSFT 430P exp 2026-03-20 | Risk management | Underlying is $399.60 vs $430 strike; current option $22.40 is above $8.70 credit. Prioritize roll, close, or assignment decision before adding new risk. |
| 2 | Sell covered-call overlay on SPY | Income / trim concentration | SPY is 17.1% of the portfolio with +43.3% unrealized gain and at least 100 shares. Use 30-45 DTE, 0.20-0.30 delta, and only size against shares you would be willing to trim. |
| 3 | Take profit on AVGO 310P exp 2026-03-20 | Theta harvest | Current mark $5.00 is at or below 55% of original $12.60 credit. Consider closing near the 50% profit rule and redeploying after a fresh scan. |
| 4 | Watchlist entry scan: LRCX | Potential new premium sale | Lam Research Corporation is a top watchlist candidate (67.4, B). Prefer a defined-risk bull put spread or small CSP only if sector exposure and earnings timing pass the options scan. |

## Open Short-Premium Checks

| Ticker | Contract | Credit | Current | Status | Action Bias |
|--------|----------|--------|---------|--------|-------------|
| MSFT | 430P 2026-03-20 x5 | $8.70 | $22.40 | ITM by 7.6% | Manage first: roll/close/assignment decision |
| MSFT | 380P 2026-05-15 x5 | $10.12 | $11.80 | OTM cushion 4.9% | Monitor |
| AVGO | 310P 2026-03-20 x5 | $12.60 | $5.00 | OTM cushion 7.0% | Consider close at profit target |
| SPY | 620P 2026-05-15 x5 | $6.92 | $10.16 | OTM cushion 9.7% | Monitor |
| COST | 900P 2026-05-15 x5 | $11.00 | $12.40 | OTM cushion 9.6% | Monitor |

## Watchlist Premium-Sale Candidates

| Ticker | Grade | Score | Company | Setup Note |
|--------|-------|-------|---------|------------|
| LRCX | B | 67.4 | Lam Research Corporation | High semiconductor overlap with AVGO/AMAT; use defined-risk or wait for pullback. |
| NVDA | B | 66.2 | NVIDIA Corporation | High semiconductor overlap with AVGO/AMAT; use defined-risk or wait for pullback. |
| TSM | B | 61.8 | Taiwan Semiconductor Manufacturing Company | High semiconductor overlap with AVGO/AMAT; use defined-risk or wait for pullback. |
| KLAC | B | 61.3 | KLA Corporation | High semiconductor overlap with AVGO/AMAT; use defined-risk or wait for pullback. |
| ADBE | B | 60.1 | Adobe Inc. | Run live options scan; prefer 30-45 DTE 0.20-0.30 delta, avoid earnings. |

## Execution Checklist

1. Refresh live quotes and option chains before entry.
2. Check earnings dates; do not hold short-dated premium through unplanned earnings.
3. Keep new risk inside 5% single-position and 30% options-allocation guardrails.
4. Close short premium at ~50% profit or manage at 2x credit / short-strike breach.
