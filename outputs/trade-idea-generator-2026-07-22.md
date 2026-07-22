# Trade Idea Generator - 2026-07-22

Generated: 2026-07-22T10:04:17.849379+00:00

## Executive Summary

- **Market regime:** VIX 17.46 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | ADBE | 61.5 | $227.16 | -3.2% | 67 | +15.1% | 2026-09-10 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | ASML | 58.2 | $1,801.51 | +3.6% | 37 | +1.3% | 2026-10-14 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | chasing after +3.6% day |
| 3 | NVDA | 58.0 | $207.29 | +2.0% | 57 | +3.6% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 35 days (2026-08-26) |
| 4 | AVGO | 58.0 | $386.50 | +2.2% | 53 | +1.7% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 43 days (2026-09-03) |
| 5 | AMZN | 58.0 | $247.55 | -1.0% | 62 | +5.7% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 8 days (2026-07-30) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AVGO | 16.7% | $386.50 | +2.2% | 53 | 16.7% portfolio weight; up +2.2% today |
| 2 | SPY | 17.1% | $748.28 | +0.8% | 51 | 17.1% portfolio weight |
| 3 | AMAT | 12.6% | $564.55 | +7.4% | 29 | 12.6% portfolio weight; up +7.4% today |
| 4 | GOOGL | 13.8% | $347.15 | -1.4% | 44 | 13.8% portfolio weight |
| 5 | AAPL | 4.6% | $327.74 | +0.4% | 80 | RSI elevated at 80 |

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
Altamira Trade Ideas - 2026-07-22
Market: SPY +0.8% | QQQ +1.9% | VIX 17.46 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: ADBE near $227.16; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 60.1 (B-); price above 20-day trend; red-day premium setup -3.2%

2) Covered-call/trim watch: AVGO at 16.7% weight.
   Rationale: 16.7% portfolio weight; up +2.2% today

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
