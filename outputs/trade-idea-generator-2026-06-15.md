# Trade Idea Generator - 2026-06-15

Generated: 2026-06-15T14:02:27.944974+00:00

## Executive Summary

- **Market regime:** VIX 16.39 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | LLY | 64.2 | $1,118.82 | -1.3% | 59 | +13.2% | 2026-08-05 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | TSM | 57.0 | $433.39 | +2.2% | 57 | +9.5% | 2026-07-16 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 31 days (2026-07-16) |
| 3 | NVDA | 54.0 | $209.16 | +1.9% | 46 | -5.9% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 4 | AVGO | 54.0 | $390.86 | +2.3% | 43 | -7.1% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 5 | COST | 48.0 | $975.45 | -0.7% | 39 | -9.4% | 2026-09-24 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AMAT | 12.6% | $588.08 | +3.7% | 77 | 12.6% portfolio weight; RSI elevated at 77; 20D move +42.2%; up +3.7% today |
| 2 | SPY | 17.1% | $753.64 | +1.6% | 52 | 17.1% portfolio weight; up +1.6% today |
| 3 | AVGO | 16.7% | $390.86 | +2.3% | 43 | 16.7% portfolio weight; up +2.3% today |
| 4 | GOOGL | 13.8% | $371.12 | +3.2% | 37 | 13.8% portfolio weight; up +3.2% today |
| 5 | MSFT | 6.7% | $398.52 | +2.0% | 43 | up +2.0% today |

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
Altamira Trade Ideas - 2026-06-15
Market: SPY +1.6% | QQQ +2.6% | VIX 16.39 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: LLY near $1,118.82; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 58.7 (C+); price above 20-day trend; RSI balanced at 59

2) Covered-call/trim watch: AMAT at 12.6% weight.
   Rationale: 12.6% portfolio weight; RSI elevated at 77; 20D move +42.2%

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
