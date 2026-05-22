# Trade Idea Generator - 2026-05-22

> For research and paper-trading workflow support only. This is not financial advice.

## Market Regime

- **VIX:** 17.03 (NORMAL)
- **SPY day change:** +0.20%
- **Sizing posture:** standard premium selling size

## Portfolio Inputs

- **Parsed portfolio value:** $1,207,271
- **Equity/fund positions parsed:** 20
- **Active option rows:** 0
- **Expired option rows skipped:** 5

| Top holding | Weight | Market value | Current |
|-------------|--------|--------------|---------|
| SPY | 17.1% | $205,887 | $686.29 |
| AVGO | 16.7% | $202,107 | $333.51 |
| GOOGL | 13.8% | $167,135 | $303.33 |
| AMAT | 12.6% | $152,521 | $369.30 |
| MSFT | 6.7% | $80,320 | $399.60 |

## Top Trade Ideas

| Rank | Type | Ticker | Score | Setup | Risk control |
|------|------|--------|-------|-------|--------------|
| 1 | Covered call | SPY | 100.0 | Manual chain lookup: 2026-06-26 ~$780 covered call | Upside is capped above the short call; avoid if a near-term breakout is desired. |
| 2 | Covered call | GOOGL | 100.0 | Manual chain lookup: 2026-06-26 ~$405 covered call | Upside is capped above the short call; avoid if a near-term breakout is desired. |
| 3 | Covered call | AMAT | 100.0 | Manual chain lookup: 2026-06-26 ~$450 covered call | Upside is capped above the short call; avoid if a near-term breakout is desired. |
| 4 | Covered call | AMZN | 100.0 | Manual chain lookup: 2026-06-26 ~$285 covered call | Upside is capped above the short call; avoid if a near-term breakout is desired. |
| 5 | Covered call | AAPL | 100.0 | Manual chain lookup: 2026-06-26 ~$325 covered call | Upside is capped above the short call; avoid if a near-term breakout is desired. |
| 6 | Cash-secured put | NVDA | 92.0 | Manual chain lookup: 2026-06-26 ~$200 cash-secured put | Skip if bid/ask is wide, earnings date moves inside the option window, or sizing exceeds cash limits. |
| 7 | Cash-secured put | KLAC | 90.5 | Manual chain lookup: 2026-06-26 ~$1660 cash-secured put | Skip if bid/ask is wide, earnings date moves inside the option window, or sizing exceeds cash limits. |

## Idea Detail

### 1. SPY - Covered call

- **Action:** Harvest premium on existing shares
- **Setup:** Manual chain lookup: 2026-06-26 ~$780 covered call
- **Rationale:** Holding has 300 shares, 17.1% portfolio weight, and trades near $742.72.
- **Risk:** Upside is capped above the short call; avoid if a near-term breakout is desired.

### 2. GOOGL - Covered call

- **Action:** Harvest premium on existing shares
- **Setup:** Manual chain lookup: 2026-06-26 ~$405 covered call
- **Rationale:** Holding has 551 shares, 13.8% portfolio weight, and trades near $387.66.
- **Risk:** Upside is capped above the short call; avoid if a near-term breakout is desired.

### 3. AMAT - Covered call

- **Action:** Harvest premium on existing shares
- **Setup:** Manual chain lookup: 2026-06-26 ~$450 covered call
- **Rationale:** Holding has 413 shares, 12.6% portfolio weight, and trades near $427.36.
- **Risk:** Upside is capped above the short call; avoid if a near-term breakout is desired.

### 4. AMZN - Covered call

- **Action:** Harvest premium on existing shares
- **Setup:** Manual chain lookup: 2026-06-26 ~$285 covered call
- **Rationale:** Holding has 288 shares, 4.9% portfolio weight, and trades near $268.46.
- **Risk:** Upside is capped above the short call; avoid if a near-term breakout is desired.

### 5. AAPL - Covered call

- **Action:** Harvest premium on existing shares
- **Setup:** Manual chain lookup: 2026-06-26 ~$325 covered call
- **Rationale:** Holding has 212 shares, 4.6% portfolio weight, and trades near $304.99.
- **Risk:** Upside is capped above the short call; avoid if a near-term breakout is desired.

### 6. NVDA - Cash-secured put

- **Action:** Enter only at a price you want to own
- **Setup:** Manual chain lookup: 2026-06-26 ~$200 cash-secured put
- **Rationale:** Watchlist grade B, score 66.2, status Top Candidate; live trend score 92.0.
- **Risk:** Skip if bid/ask is wide, earnings date moves inside the option window, or sizing exceeds cash limits.

### 7. KLAC - Cash-secured put

- **Action:** Enter only at a price you want to own
- **Setup:** Manual chain lookup: 2026-06-26 ~$1660 cash-secured put
- **Rationale:** Watchlist grade B-, score 61.3, status Top Candidate; live trend score 90.5.
- **Risk:** Skip if bid/ask is wide, earnings date moves inside the option window, or sizing exceeds cash limits.

## Watchlist Snapshot

| Ticker | Score | Grade | Status |
|--------|-------|-------|--------|
| LRCX | 67.4 | B | Top Candidate |
| NVDA | 66.2 | B | Top Candidate |
| TSM | 61.8 | B- | Top Candidate |
| KLAC | 61.3 | B- | Top Candidate |
| ADBE | 60.1 | B- | Top Candidate |
| ASML | 58.9 | C+ | Consider |
| LLY | 58.7 | C+ | Consider |
| ACN | 56.3 | C+ | Consider |

## Expired Option Rows Skipped

- MSFT 2026-03-20 $430 Put
- MSFT 2026-05-15 $380 Put
- AVGO 2026-03-20 $310 Put
- SPY 2026-05-15 $620 Put
- COST 2026-05-15 $900 Put

## Risk Notes

- Keep single new position risk near the portfolio risk limits documented in the workspace.
- Confirm option liquidity, bid/ask spread, and earnings date before placing any trade.
- Short premium ideas assume willingness to own the underlying at the breakeven price.
