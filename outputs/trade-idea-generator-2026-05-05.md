# Trade Idea Generator - 2026-05-05

> Generated from `context/portfolio-details.md` and `context/watchlist.md`.
> This is not financial advice. Verify live prices, option chains, liquidity, earnings dates, tax impact, and portfolio constraints before entering any trade.

## Executive Summary

- Parsed **20 equity/ETF/fund positions**, **5 short-premium positions**, and **26 watchlist candidates**.
- Portfolio value parsed from positions: **$1,207,271**.
- Main themes: harvest mature option profit, actively manage challenged short premium, reduce concentration risk, and scan top watchlist names for disciplined CSP entries.

## Trade Ideas

### 1. Harvest short-premium profit: AVGO 310P 2026-03-20

- **Action:** Buy-to-close or roll only if the next credit is attractive.
- **Current position:** 5 contracts, $12.60 credit, $5.00 current mark.
- **Open P&L:** $3,800 (60.3% of original credit captured).
- **Why now:** The position has reached the standard 50%+ profit-taking zone; closing reduces tail risk and frees buying power.
- **Risk note:** Use live bid/ask and avoid replacing it with lower-quality risk just to stay active.

### 2. Manage challenged short premium: MSFT 430P 2026-03-20

- **Action:** Review for roll-down/out or close if the thesis has weakened.
- **Current position:** 5 contracts, $8.70 credit, $22.40 current mark.
- **Open P&L:** $-6,850 (-157.5% of original credit).
- **Context:** Underlying snapshot: $399.60, portfolio weight 6.7%.
- **Trigger:** Prioritize if short strike is ITM, if delta has expanded, or if assignment would create excess concentration.
- **Risk note:** Do not roll for a debit; require enough net credit to compensate for longer duration and assignment risk.

### 3. Monetize concentration with defined upside: covered calls or trim bands

- **Action:** For outsized winners, consider 30-45 DTE covered calls 5-8% above spot, or set mechanical trim bands.
- **Highest weights:** SPY 17.1%, AVGO 16.7%, GOOGL 13.8%, AMAT 12.6%.
- **Portfolio value parsed:** $1,207,271.
- **Why now:** Multiple positions exceed the documented 5% single-position risk guideline, so premium harvesting or trims can reduce concentration without forcing an immediate thesis change.
- **Risk note:** Avoid writing calls through catalysts where assignment would conflict with long-term conviction.

### 4. Watchlist cash-secured put candidates

- **Action:** Build live-chain CSP candidates only on red days or IV spikes; target 30-45 DTE, 0.15-0.25 delta, and premium that meets portfolio risk limits.
- **Top scored names:** LRCX (B, 67.4), NVDA (B, 66.2), TSM (B-, 61.8), KLAC (B-, 61.3), ADBE (B-, 60.1).
- **Why now:** These are the highest-ranked non-portfolio candidates in the static watchlist and can diversify future option premium away from current mega-cap concentration.
- **Risk note:** Re-check earnings dates before selling premium; do not hold short-dated options through unplanned earnings.

## Top Portfolio Weights

| Symbol | Weight | Current | P&L |
|--------|--------|---------|-----|
| SPY | 17.1% | $686.29 | +43.3% |
| AVGO | 16.7% | $333.51 | +175.4% |
| GOOGL | 13.8% | $303.33 | +74.0% |
| AMAT | 12.6% | $369.30 | +100.5% |
| MSFT | 6.7% | $399.60 | +21.7% |
| AMZN | 4.9% | $204.79 | +80.7% |
| AAPL | 4.6% | $264.35 | +45.6% |
| CRWD | 4.3% | $415.76 | +17.1% |
| COST | 4.1% | $996.08 | +34.4% |
| ABBV | 3.8% | $228.72 | +70.9% |

## Short Premium Dashboard

| Ticker | Strike / Type | Expiration | Credit | Current | Open P&L | Capture |
|--------|---------------|------------|--------|---------|----------|---------|
| MSFT | 430 Put | 2026-03-20 | $8.70 | $22.40 | $-6,850 | -157.5% |
| MSFT | 380 Put | 2026-05-15 | $10.12 | $11.80 | $-840 | -16.6% |
| AVGO | 310 Put | 2026-03-20 | $12.60 | $5.00 | $3,800 | +60.3% |
| SPY | 620 Put | 2026-05-15 | $6.92 | $10.16 | $-1,620 | -46.8% |
| COST | 900 Put | 2026-05-15 | $11.00 | $12.40 | $-700 | -12.7% |

## Execution Checklist

1. Confirm live quotes and option chains before trading.
2. Check earnings dates and ex-dividend dates.
3. Keep single-name, sector, options notional, and cash-reserve limits in view.
4. Prefer closing winners over adding correlated risk when VIX is low.
5. Log any executed trade with `/paper-trade`.
