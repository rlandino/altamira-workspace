# Trade Idea Generator - 2026-05-13

> Generated from repository context files: `context/portfolio-details.md`, `context/watchlist.md`, and `context/options-positions.md`.

## Summary

- Portfolio market value from parsed positions: $1,207,271
- Positions parsed: 20
- Watchlist names parsed: 26
- Active short-premium notional in context: $950,000
- Data source: repository snapshot; verify live prices/chains before trading.

## Generated Ideas

### Option management
Priority: manage near-expiry short puts before adding new premium risk.
- COST 900P 2026-05-15 (2 DTE) | buffer 9.6% vs repo price $996.08 | repo mark $12.40 (-13% of credit captured)
- MSFT 380P 2026-05-15 (2 DTE) | buffer 4.9% vs repo price $399.60 | repo mark $11.80 (-17% of credit captured)
- SPY 620P 2026-05-15 (2 DTE) | buffer 9.7% vs repo price $686.29 | repo mark $10.16 (-47% of credit captured)
Skipped expired rows: MSFT 430P 2026-03-20, AVGO 310P 2026-03-20.

### Portfolio risk idea
Trim/covered-call candidates because single-name weights exceed 10%: SPY 17.1%, AVGO 16.7%, GOOGL 13.8%, AMAT 12.6%.
Top weights: SPY 17.1%, AVGO 16.7%, GOOGL 13.8%, AMAT 12.6%, MSFT 6.7%.
Largest sector/factor exposures: Technology 45.4%, ETF 17.8%, Communication Services 13.8%, Consumer Discretionary 4.9%.
Technology exposure is above the 35% enhanced-monitoring threshold; size new tech ideas conservatively.

### New trade setup
Screen these watchlist names for 30-45 DTE CSP or put-spread entries: LRCX (B, score 67.4), NVDA (B, score 66.2), TSM (B-, score 61.8), KLAC (B-, score 61.3), ADBE (B-, score 60.1).
Because most top candidates are technology/semi names, prefer defined-risk put spreads or reduced CSP size.
Entry rules: require live chain liquidity, no near earnings event, bid/ask spread under 10%, and target 0.15-0.25 delta.

### Guardrails
Review underperformers before adding capital: NOW -35.7%, SPGI -11.9%, NFLX -16.5%.
Use live broker quotes before entry; repository prices and option marks may be stale.

## Top Portfolio Weights

| Ticker | Weight | Current | P&L | Sector |
|--------|--------|---------|-----|--------|
| SPY | 17.1% | $686.29 | 43.3% | ETF |
| AVGO | 16.7% | $333.51 | 175.4% | Technology |
| GOOGL | 13.8% | $303.33 | 74.0% | Communication Services |
| AMAT | 12.6% | $369.30 | 100.5% | Technology |
| MSFT | 6.7% | $399.60 | 21.7% | Technology |
| AMZN | 4.9% | $204.79 | 80.7% | Consumer Discretionary |
| AAPL | 4.6% | $264.35 | 45.6% | Technology |
| CRWD | 4.3% | $415.76 | 17.1% | Technology |
| COST | 4.1% | $996.08 | 34.4% | Consumer Staples |
| ABBV | 3.8% | $228.72 | 70.9% | Health Care |

## Sector / Factor Exposure

| Exposure | Weight |
|----------|--------|
| Technology | 45.4% |
| ETF | 17.8% |
| Communication Services | 13.8% |
| Consumer Discretionary | 4.9% |
| Financials | 4.8% |
| Consumer Staples | 4.1% |
| Health Care | 3.8% |
| Industrials | 3.0% |
| Energy | 1.8% |
| Fund | 0.7% |

## Top Watchlist Candidates

| Ticker | Score | Grade | Company | Status |
|--------|-------|-------|---------|--------|
| LRCX | 67.4 | B | Lam Research Corporation | ⭐ Top Candidate |
| NVDA | 66.2 | B | NVIDIA Corporation | ⭐ Top Candidate |
| TSM | 61.8 | B- | Taiwan Semiconductor Manufacturing Company | ⭐ Top Candidate |
| KLAC | 61.3 | B- | KLA Corporation | ⭐ Top Candidate |
| ADBE | 60.1 | B- | Adobe Inc. | ⭐ Top Candidate |

## Disclaimer

This is an automation-generated research brief, not financial advice. Confirm suitability, live prices, liquidity, earnings dates, and risk limits before placing any order.
