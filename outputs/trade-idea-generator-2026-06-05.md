# Trade Idea Generator - 2026-06-05

> Educational scan only. These are not trade orders or investment advice. Verify live chains, liquidity, earnings, and portfolio limits before entry.

## Dashboard

- Portfolio market value from context: **$1,207,271.00**
- VIX: **15.68 (NORMAL)**
- Current equity positions scanned: **20**
- Watchlist names scanned: **26**
- Open short-premium positions: **5**
- Market data source: **repo default: scripts/thesis-generator.py**
- Options data source: **repo default: outputs/n8n-workflow-csp-daily-scan.json**

## Top Current Portfolio Weights

| Ticker | Weight | Position Value | Current Price |
|--------|--------|----------------|---------------|
| SPY | 17.1% | $205,887.00 | $757.09 |
| AVGO | 16.7% | $202,107.00 | $418.91 |
| GOOGL | 13.8% | $167,135.00 | $372.19 |
| AMAT | 12.6% | $152,521.00 | $501.70 |
| MSFT | 6.7% | $80,320.00 | $428.05 |

## Top Watchlist Candidates

| Ticker | Score | Grade | Status | Quote |
|--------|-------|-------|--------|-------|
| LRCX | 67.4 | B | ⭐ Top Candidate | $336.41 |
| NVDA | 66.2 | B | ⭐ Top Candidate | $218.66 |
| TSM | 61.8 | B- | ⭐ Top Candidate | $444.92 |
| KLAC | 61.3 | B- | ⭐ Top Candidate | $2,131.10 |
| ADBE | 60.1 | B- | ⭐ Top Candidate | $258.42 |
| ASML | 58.9 | C+ | Consider | $1,757.47 |
| LLY | 58.7 | C+ | Consider | $1,125.38 |
| ACN | 56.3 | C+ | Consider | $178.86 |

## Ranked Trade Ideas

| Rank | Ticker | Strategy | Contract / Level | Premium | Ann. ROC | Action | Flags | Source |
|------|--------|----------|------------------|---------|----------|--------|-------|--------|
| 1 | AMAT | Covered call | 2026-07-02 $550C | $14.65 | 39.5% | Sell up to 4 covered call(s) | large existing weight; RSI extended | Massive snapshot |
| 2 | NVDA | Cash-secured put | 2026-07-02 $205P | $3.65 | 24.1% | Sell 2 put(s); use a bull put spread if risk budget is tight | None | Massive snapshot |
| 3 | AVGO | Covered call | 2026-07-10 $470C | $9.45 | 23.5% | Sell up to 6 covered call(s) | large existing weight | Massive snapshot |
| 4 | LRCX | Cash-secured put | 2026-07-17 $290P | $9.05 | 27.1% | Sell 2 put(s); use a bull put spread if risk budget is tight | earnings 2026-07-29 | Massive snapshot |
| 5 | GOOGL | Covered call | 2026-07-10 $400C | $5.30 | 14.9% | Sell up to 5 covered call(s) | earnings 2026-07-22; large existing weight | Massive snapshot |
| 6 | TSM | Cash-secured put | 2026-07-02 $410P | $6.80 | 22.4% | Sell 1 put(s); use a bull put spread if risk budget is tight | earnings 2026-07-16 | Massive snapshot |
| 7 | SPY | Covered call | 2026-07-17 $810C | $6.42 | 7.4% | Sell up to 3 covered call(s) | large existing weight | heuristic estimate |
| 8 | KLAC | Cash-secured put | 2026-07-17 $1740P | $35.70 | 17.8% | Sell 1 put(s); use a bull put spread if risk budget is tight | earnings 2026-07-30 | Massive snapshot |

## Idea Detail

### 1. AMAT - Covered call

- **Action:** Sell up to 4 covered call(s)
- **Contract / level:** 2026-07-02 $550.00
- **Premium:** $14.65 | **Delta:** 0.30
- **DTE:** 27 | **Annualized ROC:** 39.5%
- **Breakeven / collateral:** N/A / N/A
- **Rationale:** Harvest premium against an existing 12.6% weight; selected strike is 9.6% above spot.
- **Risk flags:** large existing weight, RSI extended

### 2. NVDA - Cash-secured put

- **Action:** Sell 2 put(s); use a bull put spread if risk budget is tight
- **Contract / level:** 2026-07-02 $205.00
- **Premium:** $3.65 | **Delta:** -0.27
- **DTE:** 27 | **Annualized ROC:** 24.1%
- **Breakeven / collateral:** $201.35 / $41,000.00
- **Rationale:** Top watchlist candidate (B, score 66.2) with an entry basis near $201.35 if assigned.
- **Risk flags:** None

### 3. AVGO - Covered call

- **Action:** Sell up to 6 covered call(s)
- **Contract / level:** 2026-07-10 $470.00
- **Premium:** $9.45 | **Delta:** 0.25
- **DTE:** 35 | **Annualized ROC:** 23.5%
- **Breakeven / collateral:** N/A / N/A
- **Rationale:** Harvest premium against an existing 16.7% weight; selected strike is 12.2% above spot.
- **Risk flags:** large existing weight

### 4. LRCX - Cash-secured put

- **Action:** Sell 2 put(s); use a bull put spread if risk budget is tight
- **Contract / level:** 2026-07-17 $290.00
- **Premium:** $9.05 | **Delta:** -0.24
- **DTE:** 42 | **Annualized ROC:** 27.1%
- **Breakeven / collateral:** $280.95 / $58,000.00
- **Rationale:** Top watchlist candidate (B, score 67.4) with an entry basis near $280.95 if assigned.
- **Risk flags:** earnings 2026-07-29

### 5. GOOGL - Covered call

- **Action:** Sell up to 5 covered call(s)
- **Contract / level:** 2026-07-10 $400.00
- **Premium:** $5.30 | **Delta:** 0.26
- **DTE:** 35 | **Annualized ROC:** 14.9%
- **Breakeven / collateral:** N/A / N/A
- **Rationale:** Harvest premium against an existing 13.8% weight; selected strike is 7.5% above spot.
- **Risk flags:** earnings 2026-07-22, large existing weight

## Earnings in Lookahead Window

- AAPL: 2026-07-30
- ABBV: 2026-07-30
- ABT: 2026-07-16
- ACN: 2026-06-18
- ADBE: 2026-06-11
- AMZN: 2026-07-30
- ANET: 2026-08-04
- ASML: 2026-07-15
- CDNS: 2026-07-27
- CMG: 2026-07-29
- FICO: 2026-07-29
- GD: 2026-07-22
- GOOGL: 2026-07-22
- ISRG: 2026-07-28
- JPM: 2026-07-14
- KLAC: 2026-07-30
- KMI: 2026-07-15
- LRCX: 2026-07-29
- MA: 2026-07-30
- META: 2026-07-29
- MSCI: 2026-07-21
- MSFT: 2026-07-29
- NFLX: 2026-07-16
- NOW: 2026-07-22
- PLTR: 2026-08-03
- SPGI: 2026-07-30
- TMO: 2026-07-22
- TSLA: 2026-07-22
- TSM: 2026-07-16
- V: 2026-07-28
- WM: 2026-07-27

## Risk Checklist

- Confirm no unplanned earnings exposure inside the intended holding period.
- Keep any single idea within the 5% max-position rule and total options allocation within 30%.
- Use 50% profit-taking and 200% credit stop discipline for short premium.
- Recheck bid/ask spreads and open interest before entry; heuristic ideas require manual chain verification.

*Generated by scripts/trade_idea_generator.py on 2026-06-05 10:08:57 local time.*
