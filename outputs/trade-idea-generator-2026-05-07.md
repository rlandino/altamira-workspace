# Altamira Trade Idea Generator - 2026-05-07

> Operational trade ideas only. Verify live prices, options chains, liquidity, earnings dates, and suitability before placing any order. This is not financial advice.

## Inputs

- Portfolio context: `context/portfolio-details.md`
- Watchlist context: `context/watchlist.md`
- Options context: `context/options-positions.md`
- Portfolio snapshot date in repo: 2026-02-18
- Portfolio market value from positions: $1,207,271
- Cash percent from snapshot: 22.50%

## Market Regime

- VIX: 14.20 (LOW)
- Sizing posture: 75% options size; premiums thin
- Trend: Snapshot-only trend - SPY snapshot 502.75

## Priority Actions

### 1. Manage open short-premium book first

- **STALE/EXPIRED: MSFT 430 Put 2026-03-20** (5 contracts, credit 8.70, current 22.40) - expiration 2026-03-20 is past; reconcile broker records.
- **ROLL/CLOSE WATCH: MSFT 380 Put 2026-05-15** (5 contracts, credit 10.12, current 11.80) - 8 DTE; manage before expiration week risk.
- **STALE/EXPIRED: AVGO 310 Put 2026-03-20** (5 contracts, credit 12.60, current 5.00) - expiration 2026-03-20 is past; reconcile broker records.
- **ROLL/CLOSE WATCH: SPY 620 Put 2026-05-15** (5 contracts, credit 6.92, current 10.16) - 8 DTE; manage before expiration week risk.
- **ROLL/CLOSE WATCH: COST 900 Put 2026-05-15** (5 contracts, credit 11.00, current 12.40) - 8 DTE; manage before expiration week risk.

### 2. Harvest income on concentrated equity winners

Candidate covered-call overlay: sell 30-45 DTE calls around 0.20-0.25 delta on a small slice only; close at 50% profit or roll if thesis changes.

- **SPY**: 17.1% weight, 300 shares. Consider up to 1 covered-call contract(s); avoid capping the entire position.
- **AVGO**: 16.7% weight, 606 shares. Consider up to 1 covered-call contract(s); avoid capping the entire position.
- **GOOGL**: 13.8% weight, 551 shares. Consider up to 1 covered-call contract(s); avoid capping the entire position.
- **AMAT**: 12.6% weight, 413 shares. Consider up to 1 covered-call contract(s); avoid capping the entire position.
- **MSFT**: 6.7% weight, 201 shares. Consider up to 1 covered-call contract(s); avoid capping the entire position.

### 3. New capital ideas from watchlist

Use defined-risk spreads when sector exposure is already high; keep starter equity positions within the 2-5% framework.

- **LRCX (B, score 67.4) - DEFINED-RISK ONLY:** Lam Research Corporation. score is strong, but portfolio semiconductor exposure is already above 25%.
- **NVDA (B, score 66.2) - DEFINED-RISK ONLY:** NVIDIA Corporation. score is strong, but portfolio semiconductor exposure is already above 25%.
- **TSM (B-, score 61.8) - DEFINED-RISK ONLY:** Taiwan Semiconductor Manufacturing Company. score is strong, but portfolio semiconductor exposure is already above 25%.
- **KLAC (B-, score 61.3) - DEFINED-RISK ONLY:** KLA Corporation. score is strong, but portfolio semiconductor exposure is already above 25%.
- **ADBE (B-, score 60.1) - WATCH FOR STARTER ENTRY:** Adobe Inc.. diversifies away from current semiconductor concentration while keeping quality bias.
- **ASML (C+, score 58.9) - DEFINED-RISK ONLY:** ASML Holding N.V.. score is strong, but portfolio semiconductor exposure is already above 25%.

### 4. Risk guardrails

- Positions over 5% cap: 5. Do not add to these names until concentration is reduced or explicitly waived.
- New short premium should respect max 5% per trade and 30% aggregate options allocation.
- Avoid opening short-dated premium through earnings unless it is an explicit earnings-volatility trade.
- If VIX is elevated/crisis, prefer vertical spreads over naked CSPs.

## Concentration Snapshot

- SPY: 17.1% ($205,887), bucket: index/core
- AVGO: 16.7% ($202,107), bucket: semiconductor
- GOOGL: 13.8% ($167,135), bucket: mega-cap software/platform
- AMAT: 12.6% ($152,521), bucket: semiconductor
- MSFT: 6.7% ($80,320), bucket: mega-cap software/platform

## Full Options Management Table

- MSFT 430 Put 2026-03-20: STALE/EXPIRED - expiration 2026-03-20 is past; reconcile broker records
- MSFT 380 Put 2026-05-15: ROLL/CLOSE WATCH - 8 DTE; manage before expiration week risk
- AVGO 310 Put 2026-03-20: STALE/EXPIRED - expiration 2026-03-20 is past; reconcile broker records
- SPY 620 Put 2026-05-15: ROLL/CLOSE WATCH - 8 DTE; manage before expiration week risk
- COST 900 Put 2026-05-15: ROLL/CLOSE WATCH - 8 DTE; manage before expiration week risk

