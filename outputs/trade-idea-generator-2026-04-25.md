# Trade Idea Generator - 2026-04-25

**Inputs:** `context/portfolio-details.md` and `context/watchlist.md`

**Portfolio market value from repository context:** $1,207,271
**Top-4 position concentration:** 60.2%
**Watchlist names reviewed:** 26

> This is an idea-generation report, not financial advice. Verify live quotes,
> option chains, liquidity, earnings dates, tax impact, and portfolio constraints
> before placing any trade.

## Ranked Ideas

### 1. PORTFOLIO - Risk overlay

- **Action:** Harvest premium only where assignment/call-away risk is acceptable
- **Score:** 88.0
- **Rationale:** Top concentration is elevated: SPY 17.1%, AVGO 16.7%, GOOGL 13.8%, AMAT 12.6%. Avoid adding fresh long exposure to the largest holdings until weights normalize.
- **Setup:** Use 30-45 DTE 0.20-0.30 delta covered calls on 100-share lots for SPY, AVGO, GOOGL, or AMAT only if the upside cap fits the portfolio plan.
- **Risk / guardrail:** Covered calls can cap upside; keep any new short-premium risk inside the 30% options allocation limit.

### 2. MSFT - Options hygiene

- **Action:** Reconcile stale options context before opening related exposure
- **Score:** 84.0
- **Rationale:** Repository still lists a 2026-03-20 430 Put with 5 contracts.
- **Setup:** Refresh broker/export data, then decide whether to roll, close, or remove the stale record.
- **Risk / guardrail:** Do not size new premium trades from stale position data.

### 3. AVGO - Options hygiene

- **Action:** Reconcile stale options context before opening related exposure
- **Score:** 84.0
- **Rationale:** Repository still lists a 2026-03-20 310 Put with 5 contracts.
- **Setup:** Refresh broker/export data, then decide whether to roll, close, or remove the stale record.
- **Risk / guardrail:** Do not size new premium trades from stale position data.

### 4. LRCX - Watchlist candidate

- **Action:** Consider starter entry or cash-secured put
- **Score:** 70.4
- **Rationale:** Lam Research Corporation is rated B with a 67.4 stock score and status 'Top Candidate'.
- **Setup:** If options liquidity is acceptable, target a 30-45 DTE 0.20-0.30 delta cash-secured put; otherwise use a staged equity entry sized below 2% initial portfolio weight.
- **Risk / guardrail:** Semiconductor exposure is already meaningful via AVGO, AMAT, and ASML; size smaller than a normal starter.

### 5. NVDA - Watchlist candidate

- **Action:** Consider starter entry or cash-secured put
- **Score:** 69.2
- **Rationale:** NVIDIA Corporation is rated B with a 66.2 stock score and status 'Top Candidate'.
- **Setup:** If options liquidity is acceptable, target a 30-45 DTE 0.20-0.30 delta cash-secured put; otherwise use a staged equity entry sized below 2% initial portfolio weight.
- **Risk / guardrail:** Semiconductor exposure is already meaningful via AVGO, AMAT, and ASML; size smaller than a normal starter.

### 6. ADBE - Watchlist candidate

- **Action:** Consider starter entry or cash-secured put
- **Score:** 68.1
- **Rationale:** Adobe Inc. is rated B- with a 60.1 stock score and status 'Top Candidate'.
- **Setup:** If options liquidity is acceptable, target a 30-45 DTE 0.20-0.30 delta cash-secured put; otherwise use a staged equity entry sized below 2% initial portfolio weight.
- **Risk / guardrail:** Respect valuation and earnings timing; avoid holding short options through unplanned earnings.

### 7. TSM - Watchlist candidate

- **Action:** Watchlist only unless price/risk improves
- **Score:** 64.8
- **Rationale:** Taiwan Semiconductor Manufacturing Company is rated B- with a 61.8 stock score and status 'Top Candidate'.
- **Setup:** If options liquidity is acceptable, target a 30-45 DTE 0.20-0.30 delta cash-secured put; otherwise use a staged equity entry sized below 2% initial portfolio weight.
- **Risk / guardrail:** Semiconductor exposure is already meaningful via AVGO, AMAT, and ASML; size smaller than a normal starter.

### 8. KLAC - Watchlist candidate

- **Action:** Watchlist only unless price/risk improves
- **Score:** 64.3
- **Rationale:** KLA Corporation is rated B- with a 61.3 stock score and status 'Top Candidate'.
- **Setup:** If options liquidity is acceptable, target a 30-45 DTE 0.20-0.30 delta cash-secured put; otherwise use a staged equity entry sized below 2% initial portfolio weight.
- **Risk / guardrail:** Semiconductor exposure is already meaningful via AVGO, AMAT, and ASML; size smaller than a normal starter.

### 9. LLY - Watchlist candidate

- **Action:** Watchlist only unless price/risk improves
- **Score:** 62.7
- **Rationale:** Eli Lilly and Company is rated C+ with a 58.7 stock score and status 'Consider'.
- **Setup:** If options liquidity is acceptable, target a 30-45 DTE 0.20-0.30 delta cash-secured put; otherwise use a staged equity entry sized below 2% initial portfolio weight.
- **Risk / guardrail:** Respect valuation and earnings timing; avoid holding short options through unplanned earnings.

### 10. ACN - Watchlist candidate

- **Action:** Watchlist only unless price/risk improves
- **Score:** 60.3
- **Rationale:** Accenture plc is rated C+ with a 56.3 stock score and status 'Consider'.
- **Setup:** If options liquidity is acceptable, target a 30-45 DTE 0.20-0.30 delta cash-secured put; otherwise use a staged equity entry sized below 2% initial portfolio weight.
- **Risk / guardrail:** Respect valuation and earnings timing; avoid holding short options through unplanned earnings.

## Portfolio Context

| Symbol | Weight | Current | Market Value | P&L |
|--------|--------|---------|--------------|-----|
| SPY | 17.1% | $686.29 | $205,887 | +43.3% |
| AVGO | 16.7% | $333.51 | $202,107 | +175.4% |
| GOOGL | 13.8% | $303.33 | $167,135 | +74.0% |
| AMAT | 12.6% | $369.30 | $152,521 | +100.5% |
| MSFT | 6.7% | $399.60 | $80,320 | +21.7% |
| AMZN | 4.9% | $204.79 | $58,980 | +80.7% |
| AAPL | 4.6% | $264.35 | $56,042 | +45.6% |
| CRWD | 4.3% | $415.76 | $52,386 | +17.1% |
| COST | 4.1% | $996.08 | $49,804 | +34.4% |
| ABBV | 3.8% | $228.72 | $46,201 | +70.9% |
| GD | 2.2% | $349.49 | $26,561 | +97.5% |
| V | 2.2% | $320.28 | $26,263 | +36.4% |
| JPM | 2.1% | $308.78 | $25,320 | +170.4% |
| KMI | 1.8% | $32.29 | $21,344 | +92.2% |
| WM | 0.8% | $234.06 | $9,362 | +159.9% |
| FFOLX | 0.7% | $32.08 | $8,027 | +54.5% |
| QQQ | 0.7% | $605.79 | $7,875 | +42.1% |
| NOW | 0.5% | $107.81 | $5,606 | -35.7% |
| SPGI | 0.5% | $419.38 | $5,452 | -11.9% |
| NFLX | 0.0% | $77.99 | $78 | -16.5% |

## Watchlist Top Scores

| Ticker | Score | Grade | Company | Status |
|--------|-------|-------|---------|--------|
| LRCX | 67.4 | B | Lam Research Corporation | Top Candidate |
| NVDA | 66.2 | B | NVIDIA Corporation | Top Candidate |
| TSM | 61.8 | B- | Taiwan Semiconductor Manufacturing Company | Top Candidate |
| KLAC | 61.3 | B- | KLA Corporation | Top Candidate |
| ADBE | 60.1 | B- | Adobe Inc. | Top Candidate |
| ASML | 58.9 | C+ | ASML Holding N.V. | Consider |
| LLY | 58.7 | C+ | Eli Lilly and Company | Consider |
| ACN | 56.3 | C+ | Accenture plc | Consider |
| CRM | 50.7 | C | Salesforce, Inc. | Monitor |
| CDNS | 48.8 | C- | Cadence Design Systems, Inc. | Monitor |
| ANET | 48.7 | C- | Arista Networks, Inc. | Monitor |
| PANW | 47.4 | C- | Palo Alto Networks, Inc. | Monitor |
