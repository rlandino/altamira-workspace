# Trade Idea Generator - 2026-05-29

> Source: repository context (`context/portfolio-details.md`, `context/watchlist.md`, `context/options-positions.md`).
> These are research ideas and risk-management prompts, not trade orders or financial advice.

## Portfolio Snapshot

- Estimated market value from positions table: **$1,207,271**
- Positions parsed: **20**
- Open short-premium positions parsed: **5**
- Watchlist names parsed: **26**

## Risk Read-Through

Positions above the 5% framework cap for new equity exposure:
- **SPY**: 17.1% weight, $205,887 market value, P&L +43.3%
- **AVGO**: 16.7% weight, $202,107 market value, P&L +175.4%
- **GOOGL**: 13.8% weight, $167,135 market value, P&L +74.0%
- **AMAT**: 12.6% weight, $152,521 market value, P&L +100.5%
- **MSFT**: 6.7% weight, $80,320 market value, P&L +21.7%

Sector / sleeve weights from parsed positions:
- Technology: 45.4%
- Index: 17.8%
- Communication Services: 13.8%
- Consumer Discretionary: 4.9%
- Financial Services: 4.8%
- Consumer Defensive: 4.1%
- Healthcare: 3.8%
- Industrials: 3.0%
- Energy: 1.8%
- Fund: 0.7%

## Trade Ideas

### 1. Manage existing short-premium book first
- **Close/roll candidate:** AVGO 310P 2026-03-20; credit 12.60, current 5.00, profit capture 60.3%. This exceeds the 50% profit-taking rule.
- **Risk alert:** MSFT 430P 2026-03-20; current premium is 2.57x initial credit. Review against the 200% stop rule before adding risk.

### 2. Rebalance before adding correlated semiconductor exposure

- Existing top weights are concentrated in SPY, AVGO, GOOGL, and AMAT; technology-linked exposure is already well above the normal framework guardrails.
- If initiating a watchlist semiconductor name, pair it with a defined trim or replacement of existing semi/AI exposure rather than layering on another correlated position.

### 3. Watchlist candidates for staged research entries

- **LRCX** (B, score 67.4) - Lam Research Corporation; ⭐ Top Candidate. top score, but overlaps with existing semi/AI exposure.
- **NVDA** (B, score 66.2) - NVIDIA Corporation; ⭐ Top Candidate. top score, but overlaps with existing semi/AI exposure.
- **TSM** (B-, score 61.8) - Taiwan Semiconductor Manufacturing Company; ⭐ Top Candidate. top score, but overlaps with existing semi/AI exposure.
- **KLAC** (B-, score 61.3) - KLA Corporation; ⭐ Top Candidate. top score, but overlaps with existing semi/AI exposure.
- **ADBE** (B-, score 60.1) - Adobe Inc.; ⭐ Top Candidate. software exposure with less direct overlap than semicap names.

## Suggested Execution Checklist

1. Do not add new short puts where an existing position is at or past a stop-review threshold.
2. For any new equity entry, keep sizing within the framework cap and define the source of funds first.
3. Confirm current prices, earnings dates, IV rank, bid/ask width, and available cash in the broker before acting.
4. Use `/paper-trade` to log any selected idea after risk checks pass.

## Telegram Summary

```
ALTAMIRA TRADE IDEAS - 2026-05-29

Portfolio parsed: $1,207,271 across 20 positions.
Open short-premium positions: 5 | Watchlist names: 26

TOP ACTIONS
1) Profit-take/roll review: AVGO 310P 2026-03-20 has captured 60.3% of credit.
2) Stop-review alert: MSFT 430P 2026-03-20 is 2.57x initial credit.
3) Concentration check: above 5% in SPY 17.1%, AVGO 16.7%, GOOGL 13.8%, AMAT 12.6%, MSFT 6.7%.

WATCHLIST READ
Top scored names: LRCX B/67.4, NVDA B/66.2, TSM B-/61.8, KLAC B-/61.3, ADBE B-/60.1
Semicap names are high-ranked, but current portfolio already has large AVGO/AMAT exposure; prefer replacement/trim funding.

IDEA BIAS
Manage existing options risk first, preserve cash, and only add watchlist exposure after confirming live prices, earnings dates, liquidity, and risk limits.

Not financial advice. Research prompt only.
```

_Generated at 2026-05-29T10:07:10.719037+00:00._

## Delivery

- Telegram send: success
- Message IDs: 1133
- Sent at: 2026-05-29T10:07:11.180890+00:00
