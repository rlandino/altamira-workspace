# Trade Idea Generator - 2026-07-01

Generated: 2026-07-01T14:04:13.035852+00:00

## Executive Summary

- **Market regime:** VIX 16.51 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | TSM | 60.0 | $460.46 | -3.6% | 64 | +5.4% | 2026-07-16 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 15 days (2026-07-16) |
| 2 | ASML | 59.2 | $1,919.20 | -3.5% | 60 | +11.2% | 2026-07-15 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 14 days (2026-07-15) |
| 3 | LRCX | 57.3 | $403.99 | -6.8% | 65 | +17.5% | 2026-07-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 28 days (2026-07-29) |
| 4 | LLY | 56.2 | $1,186.02 | -1.1% | 59 | +9.9% | 2026-08-05 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 35 days (2026-08-05) |
| 5 | NVDA | 54.0 | $195.18 | -2.5% | 46 | -9.1% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AMAT | 12.6% | $680.76 | -5.8% | 70 | 12.6% portfolio weight; RSI elevated at 70; 20D move +35.9% |
| 2 | SPY | 17.1% | $745.20 | -0.2% | 61 | 17.1% portfolio weight |
| 3 | AVGO | 16.7% | $371.26 | -1.7% | 50 | 16.7% portfolio weight |
| 4 | ABBV | 3.8% | $248.30 | -1.3% | 70 | RSI elevated at 70; 20D move +14.4% |
| 5 | GOOGL | 13.8% | $358.70 | +0.4% | 51 | 13.8% portfolio weight |

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
Altamira Trade Ideas - 2026-07-01
Market: SPY -0.2% | QQQ -0.9% | VIX 16.51 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: TSM near $460.46; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 61.8 (B-); price above 20-day trend; RSI balanced at 64
   Risk: earnings in 15 days (2026-07-16)

2) Covered-call/trim watch: AMAT at 12.6% weight.
   Rationale: 12.6% portfolio weight; RSI elevated at 70; 20D move +35.9%

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
