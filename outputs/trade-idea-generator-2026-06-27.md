# Trade Idea Generator - 2026-06-27

Generated: 2026-06-27T14:03:49.941856+00:00

## Executive Summary

- **Market regime:** VIX 18.41 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | ASML | 59.2 | $1,794.62 | -2.5% | 58 | +11.3% | 2026-07-15 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 18 days (2026-07-15) |
| 2 | V | 58.0 | $336.23 | +1.7% | 63 | +3.0% | 2026-07-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 31 days (2026-07-28) |
| 3 | COST | 54.0 | $952.54 | +1.1% | 42 | -0.4% | 2026-09-24 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 4 | AVGO | 50.0 | $365.02 | -3.7% | 44 | -18.3% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend; negative 20D trend -18.3% |
| 5 | NVDA | 48.0 | $192.53 | -1.6% | 39 | -8.8% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AMAT | 12.6% | $626.84 | -6.2% | 72 | 12.6% portfolio weight; RSI elevated at 72; 20D move +39.3% |
| 2 | SPY | 17.1% | $728.99 | -0.7% | 45 | 17.1% portfolio weight |
| 3 | ABBV | 3.8% | $251.52 | +3.4% | 72 | RSI elevated at 72; 20D move +15.5%; up +3.4% today |
| 4 | AVGO | 16.7% | $365.02 | -3.7% | 44 | 16.7% portfolio weight |
| 5 | GOOGL | 13.8% | $337.39 | -1.8% | 29 | 13.8% portfolio weight |

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
Altamira Trade Ideas - 2026-06-27
Market: SPY -0.7% | QQQ -1.4% | VIX 18.41 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: ASML near $1,794.62; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 58.9 (C+); price above 20-day trend; RSI balanced at 58
   Risk: earnings in 18 days (2026-07-15)

2) Covered-call/trim watch: AMAT at 12.6% weight.
   Rationale: 12.6% portfolio weight; RSI elevated at 72; 20D move +39.3%

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
