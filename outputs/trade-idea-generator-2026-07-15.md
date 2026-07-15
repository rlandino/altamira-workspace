# Trade Idea Generator - 2026-07-15

Generated: 2026-07-15T14:04:08.744240+00:00

## Executive Summary

- **Market regime:** VIX 15.99 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | AVGO | 70.0 | $397.12 | +2.1% | 56 | +5.4% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | NVDA | 58.0 | $211.01 | -0.4% | 62 | +1.7% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 42 days (2026-08-26) |
| 3 | MSFT | 54.0 | $392.08 | +1.9% | 64 | -0.4% | 2026-07-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 14 days (2026-07-29) |
| 4 | GOOGL | 54.0 | $365.00 | +1.5% | 64 | -2.2% | 2026-07-21 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 6 days (2026-07-21) |
| 5 | AAPL | 52.0 | $322.63 | +2.5% | 68 | +7.8% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 15 days (2026-07-30) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | SPY | 17.1% | $754.92 | +0.4% | 68 | 17.1% portfolio weight; RSI elevated at 68 |
| 2 | AVGO | 16.7% | $397.12 | +2.1% | 56 | 16.7% portfolio weight; up +2.1% today |
| 3 | GOOGL | 13.8% | $365.00 | +1.5% | 64 | 13.8% portfolio weight; up +1.5% today |
| 4 | CRWD | 4.3% | $211.60 | +0.4% | 76 | RSI elevated at 76; 20D move +24.6% |
| 5 | AMAT | 12.6% | $588.53 | -1.2% | 50 | 12.6% portfolio weight |

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
Altamira Trade Ideas - 2026-07-15
Market: SPY +0.4% | QQQ +0.2% | VIX 15.99 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: AVGO near $397.12; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: already approved portfolio name; price above 20-day trend; RSI balanced at 56

2) Covered-call/trim watch: SPY at 17.1% weight.
   Rationale: 17.1% portfolio weight; RSI elevated at 68

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
