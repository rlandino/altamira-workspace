# Trade Idea Generator - 2026-07-10

Generated: 2026-07-10T14:02:24.373368+00:00

## Executive Summary

- **Market regime:** VIX 15.48 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | NVDA | 70.0 | $207.69 | +2.4% | 46 | +1.4% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | AVGO | 70.0 | $399.80 | -0.3% | 45 | +3.7% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 3 | AAPL | 58.0 | $314.08 | -0.7% | 61 | +6.2% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 20 days (2026-07-30) |
| 4 | AMZN | 58.0 | $245.58 | -0.6% | 52 | +1.7% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 20 days (2026-07-30) |
| 5 | MSFT | 54.0 | $384.68 | +0.1% | 53 | -1.5% | 2026-07-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 19 days (2026-07-29) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | SPY | 17.1% | $753.19 | +0.2% | 55 | 17.1% portfolio weight |
| 2 | AVGO | 16.7% | $399.80 | -0.3% | 45 | 16.7% portfolio weight |
| 3 | CRWD | 4.3% | $196.24 | -1.1% | 72 | RSI elevated at 72; 20D move +13.5% |
| 4 | GOOGL | 13.8% | $355.98 | -0.8% | 42 | 13.8% portfolio weight |
| 5 | AMAT | 12.6% | $588.72 | +0.0% | 47 | 12.6% portfolio weight |

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
Altamira Trade Ideas - 2026-07-10
Market: SPY +0.2% | QQQ +0.0% | VIX 15.48 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: NVDA near $207.69; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 66.2 (B); price above 20-day trend; RSI balanced at 46

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
