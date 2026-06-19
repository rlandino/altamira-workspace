# Trade Idea Generator - 2026-06-19

Generated: 2026-06-19T14:02:30.256520+00:00

## Executive Summary

- **Market regime:** VIX 16.84 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | LLY | 56.2 | $1,098.13 | -1.2% | 49 | +5.4% | 2026-08-05 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 2 | NVDA | 54.0 | $210.69 | +3.0% | 50 | -4.0% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 3 | COST | 54.0 | $951.45 | -1.5% | 48 | -9.4% | 2026-09-24 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 4 | V | 54.0 | $327.24 | -1.0% | 51 | -1.2% | 2026-07-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 39 days (2026-07-28) |
| 5 | AVGO | 50.0 | $411.35 | +4.7% | 43 | -0.8% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend; chasing after +4.7% day |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AMAT | 12.6% | $617.11 | +4.1% | 77 | 12.6% portfolio weight; RSI elevated at 77; 20D move +44.4%; up +4.1% today |
| 2 | AVGO | 16.7% | $411.35 | +4.7% | 43 | 16.7% portfolio weight; up +4.7% today |
| 3 | SPY | 17.1% | $746.74 | +0.8% | 45 | 17.1% portfolio weight |
| 4 | GOOGL | 13.8% | $368.03 | +1.2% | 43 | 13.8% portfolio weight |
| 5 | JPM | 2.1% | $325.22 | -2.5% | 71 | RSI elevated at 71 |

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
Altamira Trade Ideas - 2026-06-19
Market: SPY +0.8% | QQQ +2.5% | VIX 16.84 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: LLY near $1,098.13; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 58.7 (C+); RSI balanced at 49; constructive 20D move +5.4%
   Risk: below 20-day trend

2) Covered-call/trim watch: AMAT at 12.6% weight.
   Rationale: 12.6% portfolio weight; RSI elevated at 77; 20D move +44.4%

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
