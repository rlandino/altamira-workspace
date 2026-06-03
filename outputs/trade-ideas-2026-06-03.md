# Trade Idea Generator - 2026-06-03

> Informational analysis only, not financial advice. Confirm live prices, option chains, liquidity, and account risk before trading.

## Inputs

- Portfolio positions: 20 from `context/portfolio-details.md`
- Watchlist names: 26 from `context/watchlist.md`
- Data status: live FMP quotes fetched
- Portfolio market value in context: $1,207,271

## Top Portfolio Weights

| Ticker | Weight | P&L % | Market Value |
|--------|--------|-------|--------------|
| SPY | 17.1% | 43.3% | $205,887 |
| AVGO | 16.7% | 175.4% | $202,107 |
| GOOGL | 13.8% | 74.0% | $167,135 |
| AMAT | 12.6% | 100.5% | $152,521 |
| MSFT | 6.7% | 21.7% | $80,320 |

## Highest-Ranked Ideas

| Rank | Ticker | Strategy | Action | Rationale | Risk |
|------|--------|----------|--------|-----------|------|
| 1 | MSFT | Risk-control existing short put | Review close/roll for 5x MSFT 430P 2026-03-20; current mark is 257% of original credit. | Credit $8.70, current $22.40. This breaches the 200% stop-loss rule in the workspace. | Confirm assignment willingness and avoid increasing notional in the same ticker. |
| 2 | AVGO | Manage existing short put | Consider closing 5x AVGO 310P 2026-03-20; current mark is 40% of original credit. | Credit $12.60, current $5.00. This meets the 50% profit-taking rule used in the workspace. | Re-open only if the new trade still clears earnings, liquidity, and allocation checks. |
| 3 | SPY | Covered call / rebalance overlay | Consider a covered-call overwrite or staged trim: 2026-07-17 820C as an upside-cap candidate. | SPY is 17.1% of portfolio with 43.3% unrealized gain. | Only overwrite shares you are willing to have called away; avoid caps before major catalysts. |
| 4 | GOOGL | Covered call / rebalance overlay | Consider a covered-call overwrite or staged trim: 2026-07-17 390C as an upside-cap candidate. | GOOGL is 13.8% of portfolio with 74.0% unrealized gain. | Only overwrite shares you are willing to have called away; avoid caps before major catalysts. |
| 5 | AMAT | Covered call / rebalance overlay | Consider a covered-call overwrite or staged trim: 2026-07-17 530C as an upside-cap candidate. | AMAT is 12.6% of portfolio with 100.5% unrealized gain. | Only overwrite shares you are willing to have called away; avoid caps before major catalysts. |
| 6 | NVDA | Cash-secured put / bull put spread | Watch NVDA around $222.82; target a 2026-07-17 205P or defined-risk put spread at 0.20-0.30 delta. | NVIDIA Corporation is a B watchlist candidate (score 66.2, status: ⭐ Top Candidate). Price vs 50D/200D: $201.27/$188.07; day change -0.7%. | Keep risk defined if VIX is elevated or if sector exposure is already high; do not hold short premium through earnings. |
| 7 | AVGO | Covered call / rebalance overlay | Defer new covered calls until after earnings on 2026-06-03; review a post-earnings overwrite or staged trim once IV/gap risk resets. | AVGO is 16.7% of portfolio with 175.4% unrealized gain, but the earnings event is inside the short-premium window. | Earnings gap risk can overwhelm option premium; avoid opening new short premium before the event. |
| 8 | LRCX | Cash-secured put / bull put spread | Watch LRCX around $334.41; target a 2026-07-17 310P or defined-risk put spread at 0.20-0.30 delta. | Lam Research Corporation is a B watchlist candidate (score 67.4, status: ⭐ Top Candidate). Price vs 50D/200D: $267.49/$195.06; day change 5.5%. | Keep risk defined if VIX is elevated or if sector exposure is already high; do not hold short premium through earnings. |
| 9 | AMZN | Covered call / rebalance overlay | Optional covered-call candidate if premium is attractive: 2026-07-17 280C. | AMZN has at least 100 shares and a 4.9% weight; covered calls can add income without adding downside notional. | Only overwrite shares you are willing to have called away; avoid caps before major catalysts. |
| 10 | LLY | Cash-secured put / bull put spread | Watch LLY around $1064.84; target a 2026-07-17 980P or defined-risk put spread at 0.20-0.30 delta. | Eli Lilly and Company is a C+ watchlist candidate (score 58.7, status: Consider). Price vs 50D/200D: $957.76/$939.55; day change -1.6%. | Keep risk defined if VIX is elevated or if sector exposure is already high; do not hold short premium through earnings. |

## Earnings Conflicts (Next 45 Days)

| Ticker | Date |
|--------|------|
| ABT | 2026-07-16 |
| ACN | 2026-06-18 |
| ADBE | 2026-06-11 |
| ASML | 2026-07-15 |
| AVGO | 2026-06-03 |
| CRWD | 2026-06-03 |
| JPM | 2026-07-14 |
| KMI | 2026-07-15 |
| NFLX | 2026-07-16 |
| TSM | 2026-07-16 |

## Watchlist Snapshot

| Ticker | Score | Grade | Status |
|--------|-------|-------|--------|
| LRCX | 67.4 | B | ⭐ Top Candidate |
| NVDA | 66.2 | B | ⭐ Top Candidate |
| TSM | 61.8 | B- | ⭐ Top Candidate |
| KLAC | 61.3 | B- | ⭐ Top Candidate |
| ADBE | 60.1 | B- | ⭐ Top Candidate |
| ASML | 58.9 | C+ | Consider |
| LLY | 58.7 | C+ | Consider |
| ACN | 56.3 | C+ | Consider |

## Execution Checklist

- Verify bid/ask spreads and open interest before placing any option trade.
- Respect the 5% max position and 25% sector exposure limits from the risk framework.
- Close short premium at 50% profit; stop or roll at 200% of original credit.
- Avoid initiating short premium that overlaps an unplanned earnings event.
