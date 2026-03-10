# /paper-trade — Log Paper Trade

Log a paper trade to the paper trading workbook via the Trade Entry Logger webhook, with pre-trade checklist validation.

## Instructions

You are helping Ricardo log a paper trade for Altamira Capital's paper trading period. Follow these steps exactly:

### Step 1: Collect trade details

The user may provide details as an argument: $ARGUMENTS

If details are incomplete, ask for the missing required fields. Collect:

**Required:**
- **Ticker** — Must be in core universe: AAPL, MSFT, GOOGL, AMZN, AVGO, COST, V, MA, META, NVDA, SPY
- **Strategy** — CSP, Momentum, or Hedge
- **Direction** — STO (sell to open), BTC (buy to close), Long, Short
- **Entry Price** — Credit received (for CSP) or price paid (for equity)
- **Thesis** — 1-2 sentences: why this trade?
- **Edge** — What is the market mispricing?

**Required for options (CSP/Hedge):**
- **Strike** — Strike price
- **Expiration** — Date (YYYY-MM-DD)
- **Delta** — Delta at entry (e.g., -0.22)
- **IV Rank** — Current IV Rank (0-100)
- **Contracts** — Number of contracts

**Required for equity (Momentum):**
- **Shares** — Number of shares
- **50-day SMA** — Current 50-day SMA level (for signal confirmation)

### Step 2: Run pre-trade checklist

Before logging, validate the 6-point pre-trade checklist from the Paper Trading Plan:

| # | Check | Validation |
|---|-------|-----------|
| 1 | **Thesis** | Is the thesis documented? (collected above) |
| 2 | **Edge** | Is the edge specific? (IV rank, catalyst, trend) |
| 3 | **Risk** | Calculate max loss in dollars and as % of $100K portfolio |
| 4 | **Exit** | Define profit target (50% of credit for CSP) and stop-loss (200% of credit for CSP) |
| 5 | **Portfolio Fit** | Check: position ≤5% of portfolio, sector exposure, correlation |
| 6 | **Buying Power** | Confirm cash reserve stays ≥15% after trade |

**For CSP max loss calculation:**
```
Max Loss (stop-loss adjusted) = Credit × 200% × 100 × Contracts
Max Loss (full assignment) = Strike × 100 × Contracts
Position Size % = Max Loss (stop-loss) / $100,000
```

**For Momentum max loss:**
```
Max Loss = Entry Price × Shares × 8% (trailing stop)
Position Size % = (Entry Price × Shares) / $100,000
```

### Step 3: Risk limit checks

Verify against risk limits from Risk Management Framework:

- [ ] Single position ≤ 5% of portfolio ($5,000 max loss)
- [ ] Sector exposure ≤ 25% (Tech includes: AAPL, MSFT, GOOGL, AMZN, AVGO, META, NVDA)
- [ ] Options total allocation ≤ 30% notional
- [ ] Cash reserve ≥ 15% after trade
- [ ] Correlated positions ≤ 3 per sector
- [ ] No earnings within DTE (for options)

If ANY check fails, show the specific failure and recommend against the trade. Do NOT log it.

### Step 4: Present trade summary for confirmation

Show the complete trade summary:

```
PAPER TRADE — [TICKER] [STRATEGY]
==================================
Direction:    [STO/Long/etc.]
Strike:       $[strike] (if options)
Expiration:   [date] ([DTE] DTE)
Contracts:    [n]
Entry Price:  $[price] (credit/debit)
Delta:        [delta]
IV Rank:      [ivRank]

PRE-TRADE CHECKLIST:
[✓] Thesis: [thesis]
[✓] Edge: [edge]
[✓] Max Loss: $[amount] ([pct]% of portfolio)
[✓] Exit Plan: TP at $[target] / SL at $[stop]
[✓] Portfolio Fit: [sector]% sector exposure
[✓] Buying Power: [cash]% cash after trade

RISK CHECKS: ALL PASS
```

Ask: **"Log this trade? (Y/N)"**

### Step 5: Log the trade

On confirmation, attempt to submit to the Trade Entry Logger webhook:

```bash
curl -X POST https://YOUR_N8N_INSTANCE/webhook/altamira-trade-entry \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "[TICKER]",
    "strategy": "[CSP/Momentum/Hedge]",
    "direction": "[STO/Long/etc.]",
    "strike": [strike],
    "expiration": "[YYYY-MM-DD]",
    "delta": [delta],
    "ivRank": [ivRank],
    "contracts": [contracts],
    "entryPrice": [price],
    "thesis": "[thesis]",
    "edge": "[edge]"
  }'
```

**If the webhook is not configured yet** (during early paper trading setup), instead:
1. Output the trade details in a format ready to paste into the Google Sheets Trade Log
2. Provide the exact row data matching the Trade Log schema (columns A-Z)
3. Remind Ricardo to enter it manually

### Step 6: Confirm and set reminders

After logging:
- Calculate and display the profit target price and stop-loss price
- Show DTE countdown
- Remind: "Set GTC limit orders — TP at $[target], SL at $[stop]"
- Note the next check time per the daily operating rhythm

## Context

- **Paper Trading Plan:** `outputs/paper-trading-plan.md`
- **Risk Management Framework:** `outputs/risk-management-framework.md`
- **Portfolio Allocation Model:** `outputs/portfolio-allocation-model.md`
- **Parameters:** 0.20-0.30 delta, 30-45 DTE, IV Rank > 30%, max 5% position, close at 50% profit, stop at 200% credit
- **Core universe:** AAPL, MSFT, GOOGL, AMZN, AVGO, COST, V, MA, META, NVDA, SPY
- **Order rule:** Limit orders only. Never market orders.
