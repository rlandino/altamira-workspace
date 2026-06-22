# Trade Idea Generator

**Generated:** 2026-06-22 14:06 UTC
**Inputs:** `context/portfolio-details.md` and `context/watchlist.md`

## Executive Summary

- **VIX regime:** UNKNOWN (live VIX unavailable)
- **Sizing guidance:** Use base sizing until VIX is refreshed.
- **Ideas generated:** 8

## Top Trade Ideas

### 1. MSFT - Manage immediately

- **Strategy:** Review/roll 2026-03-20 430P
- **Rationale:** Current option value $22.40 is above the 2x credit stop ($17.40) on a $8.70 credit.
- **Risk / guardrail:** Do not add size before deciding whether to close, roll, or accept assignment risk.

### 2. AVGO - Take profits

- **Strategy:** Buy to close 2026-03-20 310P
- **Rationale:** Current option value $5.00 is at or below the 50% profit target ($6.30) on a $12.60 credit.
- **Risk / guardrail:** Close winning premium instead of letting gamma/assignment risk rebuild.

### 3. AVGO - Sell covered call overlay

- **Strategy:** 30-45 DTE covered call, target 0.20-0.30 delta
- **Rationale:** Holding is 16.7% of portfolio with +175.4% unrealized P&L and +0.3% latest day change.
- **Risk / guardrail:** Cap only shares you are willing to trim; avoid selling calls through an earnings date.

### 4. GOOGL - Sell covered call overlay

- **Strategy:** 30-45 DTE covered call, target 0.20-0.30 delta
- **Rationale:** Holding is 13.8% of portfolio with +74.0% unrealized P&L and +0.4% latest day change.
- **Risk / guardrail:** Cap only shares you are willing to trim; avoid selling calls through an earnings date.

### 5. AMAT - Sell covered call overlay

- **Strategy:** 30-45 DTE covered call, target 0.20-0.30 delta
- **Rationale:** Holding is 12.6% of portfolio with +100.5% unrealized P&L and +2.8% latest day change.
- **Risk / guardrail:** Cap only shares you are willing to trim; avoid selling calls through an earnings date.

### 6. LRCX - Put-selling entry candidate

- **Strategy:** Cash-secured put, 30-45 DTE, target 0.20-0.25 delta
- **Rationale:** Watchlist score 67.4 (B), status: Top Candidate.
- **Risk / guardrail:** Only sell puts at a strike you would accept as a long-term entry; avoid earnings windows.

### 7. NVDA - Put-selling entry candidate

- **Strategy:** Cash-secured put, 30-45 DTE, target 0.20-0.25 delta
- **Rationale:** Watchlist score 66.2 (B), status: Top Candidate.
- **Risk / guardrail:** Only sell puts at a strike you would accept as a long-term entry; avoid earnings windows.

### 8. TSM - Put-selling entry candidate

- **Strategy:** Cash-secured put, 30-45 DTE, target 0.20-0.25 delta
- **Rationale:** Watchlist score 61.8 (B-), status: Top Candidate.
- **Risk / guardrail:** Only sell puts at a strike you would accept as a long-term entry; avoid earnings windows.

## Current Portfolio Concentration

| Ticker | Weight | P&L % | Day Chg % | Quantity |
|--------|--------|-------|-----------|----------|
| SPY | 17.1% | +43.3% | +0.5% | 300 |
| AVGO | 16.7% | +175.4% | +0.3% | 606 |
| GOOGL | 13.8% | +74.0% | +0.4% | 551 |
| AMAT | 12.6% | +100.5% | +2.8% | 413 |
| MSFT | 6.7% | +21.7% | +0.7% | 201 |
| AMZN | 4.9% | +80.7% | +1.8% | 288 |
| AAPL | 4.6% | +45.6% | +0.2% | 212 |
| CRWD | 4.3% | +17.1% | +0.4% | 126 |

## Open Short-Premium Checks

| Ticker | Contract | Credit | Current | Status |
|--------|----------|--------|---------|--------|
| MSFT | 2026-03-20 430P | $8.70 | $22.40 | Stop/roll review |
| MSFT | 2026-05-15 380P | $10.12 | $11.80 | Monitor |
| AVGO | 2026-03-20 310P | $12.60 | $5.00 | 50% profit target |
| SPY | 2026-05-15 620P | $6.92 | $10.16 | Monitor |
| COST | 2026-05-15 900P | $11.00 | $12.40 | Monitor |

## Top Watchlist Candidates

| Ticker | Score | Grade | Status | Company |
|--------|-------|-------|--------|---------|
| LRCX | 67.4 | B | Top Candidate | Lam Research Corporation |
| NVDA | 66.2 | B | Top Candidate | NVIDIA Corporation |
| TSM | 61.8 | B- | Top Candidate | Taiwan Semiconductor Manufacturing Company |
| KLAC | 61.3 | B- | Top Candidate | KLA Corporation |
| ADBE | 60.1 | B- | Top Candidate | Adobe Inc. |
| ASML | 58.9 | C+ | Consider | ASML Holding N.V. |
| LLY | 58.7 | C+ | Consider | Eli Lilly and Company |
| ACN | 56.3 | C+ | Consider | Accenture plc |

## Data Notes

- FMP_API_KEY not set; using repository context without live quote refresh.

## Disclaimer

This is an internal idea-generation report, not financial advice. Validate prices, option chains, liquidity, earnings dates, tax impact, and portfolio risk before placing any trade.
