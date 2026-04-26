# Altamira Trade Idea Generator

**Date:** 2026-04-26
**Portfolio context snapshot:** 2026-02-18
**Portfolio market value from repo:** $1,207,271.00
**Universe:** 20 portfolio positions + 26 watchlist names

> Educational / research output only. Not financial advice. Verify live prices, liquidity, earnings dates, buying power, tax impact, and risk limits before placing any order.

## Market Context

- **SPY:** $713.94 (+0.77% latest quote)
- **VIX:** 18.71 (NORMAL)
- **Regime playbook:** standard CSP and covered-call sizing

## Top Trade Ideas

### 1. Sell covered call: SPY (confidence 82/100)

- **Contract / setup:** Covered Call: 2026-05-22 727 for ~$6.57 bid (26 DTE, delta +0.35, IV 14.9%, OI 441, spread 0.6%, ann. yield 12.7%)
- **Rationale:** SPY is 17.1% of portfolio, above the 5% single-position cap; monetize upside while trimming concentration. Technical bias: bullish trend.
- **Primary risk:** Upside capped; avoid sizing beyond shares already held.

### 2. Sell covered call: AVGO (confidence 82/100)

- **Contract / setup:** Covered Call: 2026-05-22 450 for ~$10.30 bid (26 DTE, delta +0.33, IV 49.6%, OI 1571, spread 22.8%, ann. yield 32.1%)
- **Rationale:** AVGO is 16.7% of portfolio, above the 5% single-position cap; monetize upside while trimming concentration. Technical bias: bullish trend.
- **Primary risk:** Upside capped; avoid sizing beyond shares already held.

### 3. Sell covered call: GOOGL (confidence 82/100)

- **Contract / setup:** Covered Call: 2026-05-22 365 for ~$6.40 bid (26 DTE, delta +0.31, IV 38.9%, OI 416, spread 11.8%, ann. yield 24.6%)
- **Rationale:** GOOGL is 13.8% of portfolio, above the 5% single-position cap; monetize upside while trimming concentration. Technical bias: bullish trend.
- **Primary risk:** Upside capped; avoid sizing beyond shares already held.

### 4. Sell covered call: AMAT (confidence 82/100)

- **Contract / setup:** Covered Call: 2026-05-22 455 for ~$13.30 bid (26 DTE, delta +0.34, IV 62.4%, OI 74, spread 20.0%, ann. yield 41.0%)
- **Rationale:** AMAT is 12.6% of portfolio, above the 5% single-position cap; monetize upside while trimming concentration. Technical bias: bullish trend.
- **Primary risk:** Upside capped; avoid sizing beyond shares already held.

### 5. Sell cash-secured put: LRCX (confidence 81/100)

- **Contract / setup:** CSP: 2026-05-22 250 for ~$10.75 bid (26 DTE, delta -0.31, IV 69.9%, OI 129, spread 7.2%, ann. yield 60.4%); breakeven $239.25
- **Rationale:** B watchlist candidate (67.4) with ⭐ top candidate; use CSP only if assigned cost basis fits the watchlist thesis. Technical bias: bullish trend.
- **Primary risk:** Assignment risk; keep per-trade max loss within 5% and total options BP within 30%.

### 6. Sell cash-secured put: NVDA (confidence 81/100)

- **Contract / setup:** CSP: 2026-05-22 195 for ~$4.60 bid (26 DTE, delta -0.27, IV 46.2%, OI 8062, spread 3.2%, ann. yield 33.1%); breakeven $190.40
- **Rationale:** B watchlist candidate (66.2) with ⭐ top candidate; use CSP only if assigned cost basis fits the watchlist thesis. Technical bias: bullish trend.
- **Primary risk:** Assignment risk; keep per-trade max loss within 5% and total options BP within 30%.

### 7. Sell cash-secured put: TSM (confidence 81/100)

- **Contract / setup:** CSP: 2026-05-22 380 for ~$10.35 bid (26 DTE, delta -0.30, IV 49.4%, OI 228, spread 10.5%, ann. yield 38.2%); breakeven $369.65
- **Rationale:** B- watchlist candidate (61.8) with ⭐ top candidate; use CSP only if assigned cost basis fits the watchlist thesis. Technical bias: bullish trend.
- **Primary risk:** Assignment risk; keep per-trade max loss within 5% and total options BP within 30%.

### 8. Sell cash-secured put: ADBE (confidence 77/100)

- **Contract / setup:** CSP: 2026-05-22 230 for ~$5.10 bid (26 DTE, delta -0.27, IV 45.2%, OI 191, spread 10.2%, ann. yield 31.1%); breakeven $224.90
- **Rationale:** B- watchlist candidate (60.1) with ⭐ top candidate; use CSP only if assigned cost basis fits the watchlist thesis. Technical bias: bearish trend.
- **Primary risk:** Assignment risk; keep per-trade max loss within 5% and total options BP within 30%.

## Portfolio Concentration Check

| Ticker | Weight | P&L % | Day Chg % | Note |
|---|---:|---:|---:|---|
| SPY | 17.1% | +43.3% | +0.5% | Above 5% cap |
| AVGO | 16.7% | +175.4% | +0.3% | Above 5% cap |
| GOOGL | 13.8% | +74.0% | +0.4% | Above 5% cap |
| AMAT | 12.6% | +100.5% | +2.8% | Above 5% cap |
| MSFT | 6.7% | +21.7% | +0.7% | Above 5% cap |
| AMZN | 4.9% | +80.7% | +1.8% | Within cap |
| AAPL | 4.6% | +45.6% | +0.2% | Within cap |
| CRWD | 4.3% | +17.1% | +0.4% | Within cap |

## Existing Options Book

- MSFT 430P expired 2026-03-20: reconcile broker/context.
- MSFT 380P 2026-05-15: monitor; current 11.80 vs credit 10.12.
- AVGO 310P expired 2026-03-20: reconcile broker/context.
- SPY 620P 2026-05-15: monitor; current 10.16 vs credit 6.92.
- COST 900P 2026-05-15: monitor; current 12.40 vs credit 11.00.

## Data Notes

- Run `/options-scan TICKER` for a deeper single-name chain analysis before execution.
- Refresh repository portfolio context if broker/app data has changed since the snapshot date.
