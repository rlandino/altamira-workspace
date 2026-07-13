# Trade Idea Generator - 2026-07-13

Generated: 2026-07-13T10:03:31.238917+00:00

## Executive Summary

- **Market regime:** VIX 16.15 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | AVGO | 70.0 | $399.97 | -0.3% | 46 | +3.7% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | AAPL | 58.0 | $315.32 | -0.3% | 62 | +6.7% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 17 days (2026-07-30) |
| 3 | AMZN | 58.0 | $245.34 | -0.7% | 51 | +1.6% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 17 days (2026-07-30) |
| 4 | NVDA | 54.0 | $210.96 | +4.0% | 50 | +3.0% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | chasing after +4.0% day; earnings in 44 days (2026-08-26) |
| 5 | MSFT | 54.0 | $385.10 | +0.2% | 53 | -1.3% | 2026-07-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 16 days (2026-07-29) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | SPY | 17.1% | $754.95 | +0.4% | 57 | 17.1% portfolio weight |
| 2 | AVGO | 16.7% | $399.97 | -0.3% | 46 | 16.7% portfolio weight |
| 3 | AMAT | 12.6% | $602.50 | +2.4% | 49 | 12.6% portfolio weight; up +2.4% today |
| 4 | GOOGL | 13.8% | $357.18 | -0.5% | 43 | 13.8% portfolio weight |
| 5 | ABBV | 3.8% | $248.08 | -0.7% | 75 | RSI elevated at 75 |

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
Altamira Trade Ideas - 2026-07-13
Market: SPY +0.4% | QQQ +0.3% | VIX 16.15 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: AVGO near $399.97; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: already approved portfolio name; price above 20-day trend; RSI balanced at 46

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
