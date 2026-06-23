# Trade Idea Generator - 2026-06-23

Generated: 2026-06-23T14:03:34.352876+00:00

## Executive Summary

- **Market regime:** VIX 19.27 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | TSM | 60.0 | $446.04 | -4.6% | 50 | +8.2% | 2026-07-16 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 23 days (2026-07-16) |
| 2 | ASML | 59.2 | $1,807.55 | -6.3% | 55 | +10.8% | 2026-07-15 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 22 days (2026-07-15) |
| 3 | V | 58.0 | $328.69 | +0.6% | 60 | +0.7% | 2026-07-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 35 days (2026-07-28) |
| 4 | LRCX | 57.3 | $375.72 | -8.3% | 58 | +16.4% | 2026-07-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 36 days (2026-07-29) |
| 5 | COST | 54.0 | $957.94 | +0.7% | 52 | -4.5% | 2026-09-24 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AMAT | 12.6% | $589.90 | -7.9% | 64 | 12.6% portfolio weight; 20D move +29.7% |
| 2 | SPY | 17.1% | $737.73 | -0.9% | 39 | 17.1% portfolio weight |
| 3 | AVGO | 16.7% | $389.77 | -0.6% | 30 | 16.7% portfolio weight |
| 4 | GOOGL | 13.8% | $348.20 | -0.4% | 42 | 13.8% portfolio weight |
| 5 | JPM | 2.1% | $330.64 | -0.3% | 74 | RSI elevated at 74 |

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
Altamira Trade Ideas - 2026-06-23
Market: SPY -0.9% | QQQ -2.2% | VIX 19.27 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: TSM near $446.04; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 61.8 (B-); price above 20-day trend; RSI balanced at 50
   Risk: earnings in 23 days (2026-07-16)

2) Covered-call/trim watch: AMAT at 12.6% weight.
   Rationale: 12.6% portfolio weight; 20D move +29.7%

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
