# Trade Idea Generator - 2026-06-17

Generated: 2026-06-17T10:04:29.754340+00:00

## Executive Summary

- **Market regime:** VIX 16.36 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | LLY | 68.2 | $1,122.50 | -0.6% | 57 | +9.9% | 2026-08-05 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | TSM | 60.0 | $425.83 | -3.5% | 51 | +8.5% | 2026-07-16 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 29 days (2026-07-16) |
| 3 | V | 58.0 | $333.12 | +2.9% | 55 | +1.0% | 2026-07-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 41 days (2026-07-28) |
| 4 | AVGO | 57.0 | $376.71 | -4.4% | 40 | -8.4% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 5 | NVDA | 54.0 | $207.41 | -2.4% | 46 | -6.0% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AMAT | 12.6% | $568.23 | -3.0% | 73 | 12.6% portfolio weight; RSI elevated at 73; 20D move +39.6% |
| 2 | SPY | 17.1% | $750.33 | -0.6% | 50 | 17.1% portfolio weight |
| 3 | AVGO | 16.7% | $376.71 | -4.4% | 40 | 16.7% portfolio weight |
| 4 | GOOGL | 13.8% | $373.25 | +1.1% | 40 | 13.8% portfolio weight |
| 5 | JPM | 2.1% | $331.14 | +3.7% | 79 | RSI elevated at 79; up +3.7% today |

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
Altamira Trade Ideas - 2026-06-17
Market: SPY -0.6% | QQQ -1.9% | VIX 16.36 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: LLY near $1,122.50; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 58.7 (C+); price above 20-day trend; RSI balanced at 57

2) Covered-call/trim watch: AMAT at 12.6% weight.
   Rationale: 12.6% portfolio weight; RSI elevated at 73; 20D move +39.6%

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
