# Trade Idea Generator - Portfolio + Watchlist

**Generated:** 2026-07-07  
**Universe:** Current repository portfolio (`context/portfolio-details.md`) + watchlist (`context/watchlist.md`)  
**Live data:** FMP quotes/history and Massive options snapshots fetched 2026-07-07  

> **Execution warning:** Repository portfolio context is stale. The equity snapshot is dated 2026-02-18 and the short-premium table has expired March/May 2026 contracts. Refresh broker/portfolio data before placing any order. This is research and trade-planning support, not financial advice.

## Market Regime

| Metric | Reading | Interpretation |
|--------|---------|----------------|
| SPY | $751.28, +0.9% on day | Above 20D/50D; trend supportive |
| VIX | 15.86 | Normal volatility regime |
| Premium-selling posture | Selective | CSPs/covered calls acceptable, but avoid selling through earnings |

## Highest-Priority Ideas

### 1. NVDA - Watchlist CSP / Bull Put Spread Candidate

- **Why:** Top watchlist candidate, **B score / 66.2**, no repository equity position, liquid options, earnings not until **2026-08-26**.
- **Price/technical:** $195.55; RSI 40.9; below 20D/50D after a -10.6% 20-day pullback.
- **Preferred structure:** Cash-secured put only if willing to own; otherwise define risk with a bull put spread.
- **Candidate contract:** Sell **2026-08-14 $180 put**, bid/ask $3.85/$3.95, delta -0.25, OI 307, spread ~2.6%.
- **Sizing:** Portfolio 5% cap implies about $60k max notional; 1-3 contracts depending buying power and concentration. Defined-risk spread preferred if tech exposure is already too high.
- **Action:** **Consider entry** with limit pricing; close at 50% max profit or manage before earnings.

### 2. SPY - Covered Call Overlay on Existing Core Position

- **Why:** Repository portfolio shows **300 SPY shares / 17.1% weight**, above the 5% single-position guardrail. A covered-call overlay can harvest premium without adding downside notional.
- **Price/technical:** $751.28; above 20D/50D; RSI 56.0.
- **Candidate contract:** Sell up to **3x 2026-08-07 $771 calls**, bid/ask $4.11/$4.15, delta +0.25, spread ~1.0%.
- **Upside cap:** Roughly +2.6% from spot before premium.
- **Action:** **Consider covered calls** only if willing to trim/cap SPY near $771.

### 3. ADBE - Watchlist CSP Candidate, Smaller Size

- **Why:** Watchlist top candidate, **B- score / 60.1**, earnings not until **2026-09-10**.
- **Price/technical:** $218.07; above 20D but below 50D after a -15.6% 20-day move; RSI 63.2 shows a bounce from weakness.
- **Candidate contract:** Sell **2026-08-21 $200 put**, bid/ask $5.40/$5.70, delta -0.24, OI 1,667, spread ~5.4%.
- **Sizing:** 1-2 contracts max under 5% portfolio notional cap; reduce if software/tech exposure is already elevated.
- **Action:** **Conditional entry** only on continued price stabilization above the 20D average; otherwise keep on watchlist.

### 4. AVGO - Covered Call / Trim Candidate, Not a New Put-Sale

- **Why:** Existing holding is **16.7% portfolio weight**, well above the 5% guardrail. The current quote is $373.90, below 20D/50D despite today's strength.
- **Candidate contract:** 2026-08-07 $415 call has bid/ask $7.05/$9.80 and delta +0.25, but spread is wide (~32.6%).
- **Action:** **Prefer trim/rebalance over new downside exposure.** If using covered calls, use small size and patient limit orders near mid; avoid adding AVGO puts while position is concentrated.

### 5. Semiconductor Watchlist - Wait for Earnings

| Ticker | Watchlist grade | Earnings | Technical note | Action |
|--------|-----------------|----------|----------------|--------|
| LRCX | B | 2026-07-29 | Above 50D, below 20D; RSI 47 | Watch post-earnings |
| TSM | B- | 2026-07-16 | Above 20D/50D; RSI 56 | Avoid new premium before earnings |
| KLAC | B- | 2026-07-30 | Above 50D, below 20D; RSI 45 | Watch post-earnings |
| ASML | C+ | 2026-07-15 | Near 20D, above 50D; RSI 48 | Avoid new premium before earnings |

## Portfolio Risk Flags

- **Concentration:** Repository weights show SPY 17.1%, AVGO 16.7%, GOOGL 13.8%, and AMAT 12.6%, all above the 5% single-position limit in the risk framework.
- **Earnings proximity:** GOOGL 2026-07-22, MSFT 2026-07-29, AMZN/AAPL 2026-07-30, AMAT 2026-08-13. Avoid opening new short premium that intentionally holds through these prints unless using defined-risk earnings strategies.
- **Expired option context:** Current `context/options-positions.md` entries are expired as of this run date. Do not use them for live risk decisions.

## Telegram Summary

Altamira Trade Ideas - 2026-07-07

Regime: SPY $751.28 (+0.9%), VIX 15.86 = normal vol. Premium selling is selective; avoid holding new short premium through earnings.

1) NVDA CSP/BPS candidate: watchlist B score, price $195.55, RSI 40.9, earnings 8/26. Candidate: sell 8/14 $180P around $3.85-$3.95, delta -0.25, tight spread. Use 1-3 contracts max or define risk.

2) SPY covered call overlay: repo shows 300 shares / 17.1% weight. Candidate: sell up to 3x 8/7 $771C around $4.11-$4.15, delta +0.25, if willing to cap upside near $771.

3) ADBE conditional CSP: watchlist B-, price $218.07, earnings 9/10. Candidate: sell 8/21 $200P around $5.40-$5.70, delta -0.24. Entry only if price stabilizes above 20D.

4) AVGO: no new put exposure; repo weight 16.7%. Prefer trim/rebalance or small covered-call overlay only with patient limit pricing.

Waitlist: LRCX, TSM, KLAC, ASML all have near-term earnings; reassess after prints.

Warning: repo portfolio/options context is stale; refresh broker data before trades. Research only, not financial advice.
