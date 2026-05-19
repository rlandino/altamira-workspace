# Trade Idea Generator — 2026-05-19

**Generated:** 2026-05-19 14:11 UTC

> Informational scan only, not investment advice or trade execution. Verify live prices, liquidity, account risk, and tax implications before placing any order.

## Market Regime

- **VIX:** 17.9 (NORMAL)
- **Regime sizing:** 100% of normal options size
- **Universe:** 20 portfolio holdings, 26 watchlist names, 5 open short-premium positions

## Top Trade Ideas

### 1. OPTIONS — REFRESH EXPIRED OPTIONS CONTEXT

- **Type:** Data hygiene / risk control
- **Thesis:** The repository still lists expired short-premium contracts. Verify broker status before relying on option marks or adding replacement risk.
- **Risk:** Expired or stale option records can create false roll/close signals and distort buying-power estimates.
- **Source:** context/options-positions.md
- **Details:**
  - MSFT 430P expired 2026-03-20 (credit $8.70, stale mark $22.40, contracts 5)
  - MSFT 380P expired 2026-05-15 (credit $10.12, stale mark $11.80, contracts 5)
  - AVGO 310P expired 2026-03-20 (credit $12.60, stale mark $5.00, contracts 5)
  - SPY 620P expired 2026-05-15 (credit $6.92, stale mark $10.16, contracts 5)
  - COST 900P expired 2026-05-15 (credit $11.00, stale mark $12.40, contracts 5)

### 2. GOOGL — CONSIDER COVERED CALL

- **Type:** Portfolio income / trim discipline
- **Thesis:** GOOGL is a profitable existing holding (+74.0% P&L, +13.8% portfolio weight) and can fund income while enforcing a trim level.
- **Risk:** Covered calls cap upside; avoid selling below a price where you are comfortable trimming shares.
- **Source:** context/portfolio-details.md + Massive options snapshot
- **Details:**
  - Underlying: $393.32; RSI: 72.3; trend: Uptrend
  - Candidate: sell 2026-06-18 $420C for about $5.75 bid (30 DTE, delta 0.27, OTM +6.8%)
  - Income yield on shares: 17.8% annualized; OI 6,971

### 3. LRCX — CONSIDER CSP / BULL PUT SPREAD

- **Type:** New watchlist premium idea
- **Thesis:** LRCX is a top-ranked watchlist name (B, score 67.4) with mixed trend and no earnings conflict in the next 45 days.
- **Risk:** VIX regime is NORMAL; use 100% regime sizing and prefer defined risk if spread/liquidity worsens.
- **Source:** context/watchlist.md + Massive options snapshot
- **Details:**
  - Underlying: $266.63; RSI: 59.0; 20D return: +1.6%
  - Candidate: sell 2026-06-18 $240P for about $7.15 bid (30 DTE, delta -0.25, OTM +10.0%)
  - Breakeven: $232.85; annualized credit yield: 36.2%
  - Liquidity: OI 3,214, vol 24, spread 19.6%

### 4. TSM — CONSIDER CSP / BULL PUT SPREAD

- **Type:** New watchlist premium idea
- **Thesis:** TSM is a top-ranked watchlist name (B-, score 61.8) with mixed trend and no earnings conflict in the next 45 days.
- **Risk:** VIX regime is NORMAL; use 100% regime sizing and prefer defined risk if spread/liquidity worsens.
- **Source:** context/watchlist.md + Massive options snapshot
- **Details:**
  - Underlying: $388.26; RSI: 47.4; 20D return: +0.2%
  - Candidate: sell 2026-06-18 $360P for about $7.30 bid (30 DTE, delta -0.25, OTM +7.3%)
  - Breakeven: $352.70; annualized credit yield: 24.7%
  - Liquidity: OI 6,356, vol 985, spread 10.4%

### 5. KLAC — CONSIDER CSP / BULL PUT SPREAD

- **Type:** New watchlist premium idea
- **Thesis:** KLAC is a top-ranked watchlist name (B-, score 61.3) with mixed trend and no earnings conflict in the next 45 days.
- **Risk:** VIX regime is NORMAL; use 100% regime sizing and prefer defined risk if spread/liquidity worsens.
- **Source:** context/watchlist.md + Massive options snapshot
- **Details:**
  - Underlying: $1705.41; RSI: 42.1; 20D return: -5.8%
  - Candidate: sell 2026-06-18 $1600P for about $51.20 bid (30 DTE, delta -0.31, OTM +6.2%)
  - Breakeven: $1548.80; annualized credit yield: 38.9%
  - Liquidity: OI 280, vol 18, spread 14.8%

### 6. AMAT — CONSIDER COVERED CALL

- **Type:** Portfolio income / trim discipline
- **Thesis:** AMAT is a profitable existing holding (+100.5% P&L, +12.6% portfolio weight) and can fund income while enforcing a trim level.
- **Risk:** Covered calls cap upside; avoid selling below a price where you are comfortable trimming shares.
- **Source:** context/portfolio-details.md + Massive options snapshot
- **Details:**
  - Underlying: $400.36; RSI: 56.2; trend: Mixed trend
  - Candidate: sell 2026-06-18 $450C for about $9.40 bid (30 DTE, delta 0.27, OTM +12.4%)
  - Income yield on shares: 28.6% annualized; OI 2,354

### 7. ASML — CONSIDER CSP / BULL PUT SPREAD

- **Type:** New watchlist premium idea
- **Thesis:** ASML is a top-ranked watchlist name (C+, score 58.9) with mixed trend and no earnings conflict in the next 45 days.
- **Risk:** VIX regime is NORMAL; use 100% regime sizing and prefer defined risk if spread/liquidity worsens.
- **Source:** context/watchlist.md + Massive options snapshot
- **Details:**
  - Underlying: $1453.16; RSI: 54.6; 20D return: +0.6%
  - Candidate: sell 2026-06-18 $1360P for about $38.30 bid (30 DTE, delta -0.29, OTM +6.4%)
  - Breakeven: $1321.70; annualized credit yield: 34.3%
  - Liquidity: OI 567, vol 6, spread 7.5%

### 8. LLY — WATCH FOR PUT-SELLING ENTRY

- **Type:** New watchlist premium idea
- **Thesis:** LLY is a top-ranked watchlist name (C+, score 58.7) but no clean 30-60 DTE 0.20-0.30 delta put was available from the chain snapshot.
- **Risk:** Manual chain check required before entry; avoid forcing illiquid contracts.
- **Source:** context/watchlist.md + FMP quote
- **Details:**
  - Underlying: $1013.64; trend: Uptrend; RSI: 76.7
  - Target manual setup: 30-45 DTE, 0.20-0.30 delta, spread under 10%, OI above 100.

## Current Portfolio Snapshot

| Ticker | Weight | P&L % | Live Price | Trend | RSI | 20D Return |
|--------|--------|-------|------------|-------|-----|------------|
| SPY | +17.1% | +43.3% | $733.72 | Uptrend | 69.0 | +3.4% |
| AVGO | +16.7% | +175.4% | $408.33 | Mixed trend | 51.9 | -2.9% |
| GOOGL | +13.8% | +74.0% | $393.32 | Uptrend | 72.3 | +15.6% |
| AMAT | +12.6% | +100.5% | $400.36 | Mixed trend | 56.2 | -0.0% |
| MSFT | +6.7% | +21.7% | $427.28 | Mixed trend | 53.3 | -0.8% |
| AMZN | +4.9% | +80.7% | $259.86 | Mixed trend | 45.8 | +1.7% |
| AAPL | +4.6% | +45.6% | $298.13 | Uptrend | 83.5 | +9.4% |
| CRWD | +4.3% | +17.1% | $629.68 | Uptrend | 92.9 | +35.7% |

## Watchlist Leaders

| Ticker | Score | Grade | Status | Live Price | Trend | Earnings Next 45D |
|--------|-------|-------|--------|------------|-------|-------------------|
| LRCX | 67.4 | B | ⭐ Top Candidate | $266.63 | Mixed trend | None found |
| NVDA | 66.2 | B | ⭐ Top Candidate | $219.33 | Uptrend | 2026-05-20 |
| TSM | 61.8 | B- | ⭐ Top Candidate | $388.26 | Mixed trend | None found |
| KLAC | 61.3 | B- | ⭐ Top Candidate | $1,705.41 | Mixed trend | None found |
| ADBE | 60.1 | B- | ⭐ Top Candidate | $264.08 | Mixed trend | 2026-06-11 |
| ASML | 58.9 | C+ | Consider | $1,453.16 | Mixed trend | None found |
| LLY | 58.7 | C+ | Consider | $1,013.64 | Uptrend | None found |
| ACN | 56.3 | C+ | Consider | $182.96 | Mixed trend | 2026-06-18 |

## Existing Short Premium Checks

| Ticker | Contract | Expiration | Credit | Current | Rule Status |
|--------|----------|------------|--------|---------|-------------|
| MSFT | 430P | 2026-03-20 | $8.70 | $22.40 | Expired - verify broker/status |
| MSFT | 380P | 2026-05-15 | $10.12 | $11.80 | Expired - verify broker/status |
| AVGO | 310P | 2026-03-20 | $12.60 | $5.00 | Expired - verify broker/status |
| SPY | 620P | 2026-05-15 | $6.92 | $10.16 | Expired - verify broker/status |
| COST | 900P | 2026-05-15 | $11.00 | $12.40 | Expired - verify broker/status |

## Execution Checklist

- Confirm real-time bid/ask and open interest before any trade.
- Keep single-position risk within the portfolio risk framework.
- Do not sell new short premium through unplanned earnings.
- Use the workspace management rules: close at 50% profit; stop or roll at 200% of credit.

