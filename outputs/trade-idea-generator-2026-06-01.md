# Trade Idea Generator — 2026-06-01

> Financial disclaimer: This is a research workflow for Altamira Capital paper/portfolio monitoring. It is not investment advice or an order ticket. Verify live prices, liquidity, Greeks, earnings dates, and risk limits before trading.

## Inputs

- Equity positions parsed: 20
- Short-premium positions parsed: 5
- Watchlist entries parsed: 26
- Portfolio value context: $1,207,271

## Top Trade Ideas

### 1. AVGO — Reconcile expired short Put (priority 100)

**Action:** Refresh broker context for 5x 310 Put 2026-03-20; repository expiration is already past.

**Rationale:** The option table shows this position expired 73 days ago; live status must be confirmed before acting. Snapshot cushion to strike: 7.0%.

**Risk:** Using stale option rows can create false close/roll signals and inaccurate portfolio risk.

**Follow-up:** Run the portfolio refresh/export before entering any new trade and remove expired rows after reconciliation.

### 2. COST — Reconcile expired short Put (priority 100)

**Action:** Refresh broker context for 5x 900 Put 2026-05-15; repository expiration is already past.

**Rationale:** The option table shows this position expired 17 days ago; live status must be confirmed before acting. Snapshot cushion to strike: 9.6%.

**Risk:** Using stale option rows can create false close/roll signals and inaccurate portfolio risk.

**Follow-up:** Run the portfolio refresh/export before entering any new trade and remove expired rows after reconciliation.

### 3. MSFT — Reconcile expired short Put (priority 100)

**Action:** Refresh broker context for 5x 430 Put 2026-03-20; repository expiration is already past.

**Rationale:** The option table shows this position expired 73 days ago; live status must be confirmed before acting. Underlying snapshot $399.60 is below strike $430.00.

**Risk:** Using stale option rows can create false close/roll signals and inaccurate portfolio risk.

**Follow-up:** Run the portfolio refresh/export before entering any new trade and remove expired rows after reconciliation.

### 4. MSFT — Reconcile expired short Put (priority 100)

**Action:** Refresh broker context for 5x 380 Put 2026-05-15; repository expiration is already past.

**Rationale:** The option table shows this position expired 17 days ago; live status must be confirmed before acting. Snapshot cushion to strike: 4.9%.

**Risk:** Using stale option rows can create false close/roll signals and inaccurate portfolio risk.

**Follow-up:** Run the portfolio refresh/export before entering any new trade and remove expired rows after reconciliation.

### 5. SPY — Reconcile expired short Put (priority 100)

**Action:** Refresh broker context for 5x 620 Put 2026-05-15; repository expiration is already past.

**Rationale:** The option table shows this position expired 17 days ago; live status must be confirmed before acting. Snapshot cushion to strike: 9.7%.

**Risk:** Using stale option rows can create false close/roll signals and inaccurate portfolio risk.

**Follow-up:** Run the portfolio refresh/export before entering any new trade and remove expired rows after reconciliation.

### 6. AMAT — Covered call / trim overlay (priority 98)

**Action:** Evaluate selling up to 4 covered call contract(s) against shares, or trim if portfolio concentration is above target.

**Rationale:** Position weight 12.6% with P&L +100.5% creates a monetization opportunity without adding downside exposure.

**Risk:** Covered calls cap upside; trimming can create tax/friction considerations. Avoid calls through earnings unless intentional.

**Follow-up:** Target 0.20-0.30 delta, 30-45 DTE calls after confirming current chain liquidity.

### 7. AVGO — Covered call / trim overlay (priority 98)

**Action:** Evaluate selling up to 6 covered call contract(s) against shares, or trim if portfolio concentration is above target.

**Rationale:** Position weight 16.7% with P&L +175.4% creates a monetization opportunity without adding downside exposure.

**Risk:** Covered calls cap upside; trimming can create tax/friction considerations. Avoid calls through earnings unless intentional.

**Follow-up:** Target 0.20-0.30 delta, 30-45 DTE calls after confirming current chain liquidity.

### 8. GOOGL — Covered call / trim overlay (priority 98)

**Action:** Evaluate selling up to 5 covered call contract(s) against shares, or trim if portfolio concentration is above target.

**Rationale:** Position weight 13.8% with P&L +74.0% creates a monetization opportunity without adding downside exposure.

**Risk:** Covered calls cap upside; trimming can create tax/friction considerations. Avoid calls through earnings unless intentional.

**Follow-up:** Target 0.20-0.30 delta, 30-45 DTE calls after confirming current chain liquidity.

### 9. SPY — Covered call / trim overlay (priority 98)

**Action:** Evaluate selling up to 3 covered call contract(s) against shares, or trim if portfolio concentration is above target.

**Rationale:** Position weight 17.1% with P&L +43.3% creates a monetization opportunity without adding downside exposure.

**Risk:** Covered calls cap upside; trimming can create tax/friction considerations. Avoid calls through earnings unless intentional.

**Follow-up:** Target 0.20-0.30 delta, 30-45 DTE calls after confirming current chain liquidity.

### 10. AAPL — Covered call / trim overlay (priority 92)

**Action:** Evaluate selling up to 2 covered call contract(s) against shares, or trim if portfolio concentration is above target.

**Rationale:** Position weight 4.6% with P&L +45.6% creates a monetization opportunity without adding downside exposure.

**Risk:** Covered calls cap upside; trimming can create tax/friction considerations. Avoid calls through earnings unless intentional.

**Follow-up:** Target 0.20-0.30 delta, 30-45 DTE calls after confirming current chain liquidity.

## Portfolio Concentration Snapshot

| Ticker | Weight | P&L | Current |
|--------|--------|-----|---------|
| SPY | 17.1% | +43.3% | $686.29 |
| AVGO | 16.7% | +175.4% | $333.51 |
| GOOGL | 13.8% | +74.0% | $303.33 |
| AMAT | 12.6% | +100.5% | $369.30 |
| MSFT | 6.7% | +21.7% | $399.60 |
| AMZN | 4.9% | +80.7% | $204.79 |
| AAPL | 4.6% | +45.6% | $264.35 |
| CRWD | 4.3% | +17.1% | $415.76 |
| COST | 4.1% | +34.4% | $996.08 |
| ABBV | 3.8% | +70.9% | $228.72 |

## Existing Short Premium Positions

| Ticker | Strike | Type | Expiration | Credit | Current | Contracts |
|--------|--------|------|------------|--------|---------|-----------|
| MSFT | 430 | Put | 2026-03-20 | $8.70 | $22.40 | 5 |
| MSFT | 380 | Put | 2026-05-15 | $10.12 | $11.80 | 5 |
| AVGO | 310 | Put | 2026-03-20 | $12.60 | $5.00 | 5 |
| SPY | 620 | Put | 2026-05-15 | $6.92 | $10.16 | 5 |
| COST | 900 | Put | 2026-05-15 | $11.00 | $12.40 | 5 |

## Telegram Delivery

Telegram delivery is attempted by the script when `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` or `TELEGRAM_CHANNEL_ID` are configured.

