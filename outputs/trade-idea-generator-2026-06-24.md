# Trade Idea Generator - 2026-06-24

Generated: 2026-06-24T10:05:27.102616+00:00

## Executive Summary

- **Market regime:** VIX 19.31 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | TSM | 60.0 | $436.39 | -6.7% | 47 | +5.8% | 2026-07-16 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 22 days (2026-07-16) |
| 2 | ASML | 59.2 | $1,778.46 | -7.8% | 54 | +9.0% | 2026-07-15 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 21 days (2026-07-15) |
| 3 | V | 58.0 | $328.48 | +0.6% | 60 | +0.6% | 2026-07-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 34 days (2026-07-28) |
| 4 | LRCX | 57.3 | $371.33 | -9.3% | 58 | +15.1% | 2026-07-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 35 days (2026-07-29) |
| 5 | COST | 54.0 | $957.68 | +0.7% | 52 | -4.5% | 2026-09-24 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AMAT | 12.6% | $585.88 | -8.5% | 64 | 12.6% portfolio weight; 20D move +28.8% |
| 2 | SPY | 17.1% | $733.58 | -1.5% | 38 | 17.1% portfolio weight |
| 3 | AVGO | 16.7% | $380.15 | -3.1% | 29 | 16.7% portfolio weight |
| 4 | GOOGL | 13.8% | $346.13 | -1.0% | 41 | 13.8% portfolio weight |
| 5 | ABBV | 3.8% | $234.76 | +2.1% | 68 | RSI elevated at 68; up +2.1% today |

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
Altamira Trade Ideas - 2026-06-24
Market: SPY -1.5% | QQQ -3.3% | VIX 19.31 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: TSM near $436.39; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 61.8 (B-); price above 20-day trend; RSI balanced at 47
   Risk: earnings in 22 days (2026-07-16)

2) Covered-call/trim watch: AMAT at 12.6% weight.
   Rationale: 12.6% portfolio weight; 20D move +28.8%

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
