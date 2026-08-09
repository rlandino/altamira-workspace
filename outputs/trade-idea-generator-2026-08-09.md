# Trade Idea Generator - 2026-08-09

Generated: 2026-08-09T14:03:12.460497+00:00

## Executive Summary

- **Market regime:** VIX 14.90 (LOW); Premium is lean; sell smaller or favor covered calls.
- **Sizing:** Use 75% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | COST | 70.0 | $947.82 | -0.1% | 56 | +2.3% | 2026-09-24 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | GOOGL | 70.0 | $354.30 | -1.0% | 51 | +0.5% | 2026-10-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 3 | AMZN | 70.0 | $274.48 | +0.8% | 63 | +11.0% | 2026-10-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 4 | V | 70.0 | $362.50 | -2.2% | 52 | +1.3% | 2026-10-27 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 5 | ASML | 68.2 | $1,740.99 | +2.1% | 50 | +0.9% | 2026-10-14 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AVGO | 16.7% | $427.76 | +1.7% | 74 | 16.7% portfolio weight; RSI elevated at 74; up +1.7% today |
| 2 | SPY | 17.1% | $773.26 | +0.6% | 70 | 17.1% portfolio weight; RSI elevated at 70 |
| 3 | AMAT | 12.6% | $539.14 | +2.2% | 52 | 12.6% portfolio weight; up +2.2% today |
| 4 | MSFT | 6.7% | $499.99 | +0.0% | 81 | RSI elevated at 81; 20D move +27.9% |
| 5 | GOOGL | 13.8% | $354.30 | -1.0% | 51 | 13.8% portfolio weight |

## Existing Short-Premium Review

| Ticker | Expiration | Strike | Credit | Current | Status |
|---|---|---:|---:|---:|---|
| - | - | - | - | - | No active rows after filtering expired static context |

## Portfolio Risk Flags

- Technology exposure is high at 45.4% across listed holdings.
- SPY is above 15% single-name/ETF weight at 17.1%.
- AVGO is above 15% single-name/ETF weight at 16.7%.

## Telegram Message

```text
Altamira Trade Ideas - 2026-08-09
Market: SPY +0.6% | QQQ +1.2% | VIX 14.90 (LOW)
Sizing: 75% of standard premium-selling size. Premium is lean; sell smaller or favor covered calls.

1) CSP watch: COST near $947.82; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: already approved portfolio name; price above 20-day trend; RSI balanced at 56

2) Covered-call/trim watch: AVGO at 16.7% weight.
   Rationale: 16.7% portfolio weight; RSI elevated at 74; up +1.7% today

Risk flags:
- Technology exposure is high at 45.4% across listed holdings.
- SPY is above 15% single-name/ETF weight at 17.1%.
- AVGO is above 15% single-name/ETF weight at 16.7%.

Static options note: ignored 5 expired short-premium rows from context/options-positions.md.

Educational only - not financial advice. Verify quotes, greeks, liquidity, earnings, and order tickets before trading.
```

## Data Notes

- Portfolio/watchlist positions are sourced from repository context files.
- Live quotes and historical prices are sourced from FMP at runtime.
- Option contracts are included only when the FMP options chain endpoint returns usable data.
- Expired static short-premium rows skipped: 5.
- Financial calculations are estimates for research and workflow triage only.

> Disclaimer: This report is for educational and operational planning purposes only. It is not financial advice. Verify live quotes, greeks, liquidity, earnings dates, portfolio exposure, and order tickets before placing any trade.
