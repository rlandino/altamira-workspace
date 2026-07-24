# Trade Idea Generator - 2026-07-24

Generated: 2026-07-24T14:04:13.178478+00:00

## Executive Summary

- **Market regime:** VIX 18.85 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | AVGO | 61.0 | $381.85 | -2.7% | 53 | +4.6% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 41 days (2026-09-03) |
| 2 | NVDA | 58.0 | $207.35 | -0.7% | 59 | +7.7% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 33 days (2026-08-26) |
| 3 | V | 58.0 | $353.30 | +0.5% | 46 | +5.1% | 2026-07-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 4 days (2026-07-28) |
| 4 | COST | 54.0 | $929.88 | +0.4% | 41 | -2.4% | 2026-09-24 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 5 | AAPL | 54.0 | $327.64 | +1.9% | 64 | +15.5% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 6 days (2026-07-30) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | SPY | 17.1% | $738.20 | +0.0% | 39 | 17.1% portfolio weight |
| 2 | AVGO | 16.7% | $381.85 | -2.7% | 53 | 16.7% portfolio weight |
| 3 | GOOGL | 13.8% | $322.38 | +1.5% | 28 | 13.8% portfolio weight |
| 4 | AMAT | 12.6% | $546.73 | -2.9% | 42 | 12.6% portfolio weight |
| 5 | AAPL | 4.6% | $327.64 | +1.9% | 64 | 20D move +15.5%; up +1.9% today |

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
Altamira Trade Ideas - 2026-07-24
Market: SPY +0.0% | QQQ -0.9% | VIX 18.85 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: AVGO near $381.85; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: already approved portfolio name; price above 20-day trend; RSI balanced at 53
   Risk: earnings in 41 days (2026-09-03)

2) Covered-call/trim watch: SPY at 17.1% weight.
   Rationale: 17.1% portfolio weight

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
