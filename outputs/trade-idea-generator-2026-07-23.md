# Trade Idea Generator - 2026-07-23

Generated: 2026-07-23T10:01:47.801082+00:00

## Executive Summary

- **Market regime:** VIX 17.61 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | ASML | 68.2 | $1,801.86 | +0.0% | 46 | +2.2% | 2026-10-14 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | ADBE | 59.5 | $218.36 | -3.9% | 55 | +11.1% | 2026-09-10 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 3 | NVDA | 58.0 | $212.06 | +2.3% | 63 | +6.6% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 34 days (2026-08-26) |
| 4 | MSFT | 58.0 | $390.34 | -1.9% | 54 | +6.8% | 2026-07-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 6 days (2026-07-29) |
| 5 | AVGO | 58.0 | $396.81 | +2.7% | 60 | +3.9% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 42 days (2026-09-03) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AVGO | 16.7% | $396.81 | +2.7% | 60 | 16.7% portfolio weight; up +2.7% today |
| 2 | SPY | 17.1% | $747.41 | -0.1% | 52 | 17.1% portfolio weight |
| 3 | GOOGL | 13.8% | $342.09 | -1.5% | 38 | 13.8% portfolio weight |
| 4 | AMAT | 12.6% | $553.92 | -1.9% | 34 | 12.6% portfolio weight |
| 5 | AAPL | 4.6% | $325.89 | -0.6% | 76 | RSI elevated at 76 |

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
Altamira Trade Ideas - 2026-07-23
Market: SPY -0.1% | QQQ -0.5% | VIX 17.61 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: ASML near $1,801.86; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 58.9 (C+); price above 20-day trend; RSI balanced at 46

2) Covered-call/trim watch: AVGO at 16.7% weight.
   Rationale: 16.7% portfolio weight; up +2.7% today

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
