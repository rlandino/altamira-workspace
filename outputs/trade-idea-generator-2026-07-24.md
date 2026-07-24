# Trade Idea Generator - 2026-07-24

Generated: 2026-07-24T10:03:44.313143+00:00

## Executive Summary

- **Market regime:** VIX 18.62 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | ASML | 64.2 | $1,803.00 | +0.1% | 53 | -2.1% | 2026-10-14 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | ADBE | 59.5 | $212.17 | -2.8% | 44 | +9.7% | 2026-09-10 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 3 | NVDA | 58.0 | $208.76 | -1.6% | 62 | +6.7% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 33 days (2026-08-26) |
| 4 | AVGO | 58.0 | $392.47 | -1.1% | 63 | +3.6% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 41 days (2026-09-03) |
| 5 | AAPL | 54.0 | $321.66 | -1.3% | 63 | +16.9% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 6 days (2026-07-30) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | SPY | 17.1% | $738.18 | -1.2% | 45 | 17.1% portfolio weight |
| 2 | AVGO | 16.7% | $392.47 | -1.1% | 63 | 16.7% portfolio weight |
| 3 | AMAT | 12.6% | $562.80 | +1.6% | 43 | 12.6% portfolio weight; up +1.6% today |
| 4 | GOOGL | 13.8% | $317.69 | -7.1% | 30 | 13.8% portfolio weight |
| 5 | AAPL | 4.6% | $321.66 | -1.3% | 63 | 20D move +16.9% |

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
Market: SPY -1.2% | QQQ -1.9% | VIX 18.62 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: ASML near $1,803.00; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 58.9 (C+); price above 20-day trend; RSI balanced at 53

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
