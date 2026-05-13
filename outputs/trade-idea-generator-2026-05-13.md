# Trade Idea Generator - 2026-05-13

> Educational trade research only, not financial advice. Verify prices, chains, earnings dates, and risk limits before placing any trade.

## Summary

- Portfolio value: $1,207,271.00
- Cash: 22.5%
- VIX regime: UNKNOWN (N/A)
- Regime note: Use normal sizing until live VIX is confirmed.
- Data note: FMP_API_KEY not set; using repository snapshot prices only. VIX live quote skipped; FMP_API_KEY not set.

## Top Trade Ideas

| Rank | Ticker | Strategy | Action | Rationale |
|------|--------|----------|--------|-----------|
| 1 | SPY | Covered call / trim discipline | Sell 0.15-0.25 delta covered calls around $750, 2026-06-12 expiry, or trim shares if concentration needs immediate reduction. | Position weight 17.1% is above concentration guardrail; no live momentum data. |
| 2 | AVGO | Covered call / trim discipline | Sell 0.15-0.25 delta covered calls around $365, 2026-06-12 expiry, or trim shares if concentration needs immediate reduction. | Position weight 16.7% is above concentration guardrail; no live momentum data. |
| 3 | MSFT | Manage short put | Review for close/roll; expiration is within one week and assignment risk is event-sensitive. Position: 5x MSFT 380P exp 2026-05-15. | 2 DTE; underlying $399.60 vs strike $380. |
| 4 | SPY | Manage short put | Review for close/roll; expiration is within one week and assignment risk is event-sensitive. Position: 5x SPY 620P exp 2026-05-15. | 2 DTE; underlying $686.29 vs strike $620. |
| 5 | COST | Manage short put | Review for close/roll; expiration is within one week and assignment risk is event-sensitive. Position: 5x COST 900P exp 2026-05-15. | 2 DTE; underlying $996.08 vs strike $900. |
| 6 | GOOGL | Covered call / trim discipline | Sell 0.15-0.25 delta covered calls around $330, 2026-06-12 expiry, or trim shares if concentration needs immediate reduction. | Position weight 13.8% is above concentration guardrail; no live momentum data. |
| 7 | AMAT | Covered call / trim discipline | Sell 0.15-0.25 delta covered calls around $400, 2026-06-12 expiry, or trim shares if concentration needs immediate reduction. | Position weight 12.6% is above concentration guardrail; no live momentum data. |
| 8 | LRCX | Cash-secured put | Cash-secured put around manual chain lookup, 2026-06-12 expiry; target 0.20-0.30 delta and avoid entering if earnings fall before expiration. | B watchlist score 67.4; no live momentum data. |

## Portfolio Concentration Snapshot

| Ticker | Weight | Current | Note |
|--------|--------|---------|------|
| SPY | 17.1% | $686.29 | Above 10%; prioritize trims/covered calls over adds. |
| AVGO | 16.7% | $333.51 | Above 10%; prioritize trims/covered calls over adds. |
| GOOGL | 13.8% | $303.33 | Above 10%; prioritize trims/covered calls over adds. |
| AMAT | 12.6% | $369.30 | Above 10%; prioritize trims/covered calls over adds. |
| MSFT | 6.7% | $399.60 | Within top holdings. |
| AMZN | 4.9% | $204.79 | Within top holdings. |

## Watchlist Priority Snapshot

| Ticker | Score | Grade | Status | Company |
|--------|-------|-------|--------|---------|
| LRCX | 67.4 | B | Top Candidate | Lam Research Corporation |
| NVDA | 66.2 | B | Top Candidate | NVIDIA Corporation |
| TSM | 61.8 | B- | Top Candidate | Taiwan Semiconductor Manufacturing Company |
| KLAC | 61.3 | B- | Top Candidate | KLA Corporation |
| ADBE | 60.1 | B- | Top Candidate | Adobe Inc. |
| ASML | 58.9 | C+ | Consider | ASML Holding N.V. |

## Data Hygiene / Risk Notes

- Expired option rows found in context; refresh `context/portfolio-details.md` before sizing new risk:
  - MSFT 430P expired 2026-03-20
  - AVGO 310P expired 2026-03-20
- Do not sell new short premium through unplanned earnings.
- Respect max position, options allocation, and cash-reserve limits from the risk framework.

## Delivery

- Telegram: sent 1 Telegram message(s) via csp-daily-scan-fixed.json fallback
