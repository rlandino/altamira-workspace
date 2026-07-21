# Trade Idea Generator - 2026-07-21

Generated: 2026-07-21T10:02:25.175419+00:00

## Executive Summary

- **Market regime:** VIX 17.51 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | AMZN | 58.0 | $249.99 | +1.1% | 63 | +7.4% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 9 days (2026-07-30) |
| 2 | V | 58.0 | $360.57 | +0.6% | 64 | +10.4% | 2026-07-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 7 days (2026-07-28) |
| 3 | NVDA | 54.0 | $203.28 | +0.2% | 57 | -2.6% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 36 days (2026-08-26) |
| 4 | COST | 54.0 | $935.80 | -0.5% | 47 | -1.6% | 2026-09-24 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 5 | ASML | 52.2 | $1,739.02 | -0.5% | 41 | -9.9% | 2026-10-14 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AVGO | 16.7% | $378.16 | +2.0% | 52 | 16.7% portfolio weight; up +2.0% today |
| 2 | SPY | 17.1% | $742.09 | -0.2% | 51 | 17.1% portfolio weight |
| 3 | GOOGL | 13.8% | $351.99 | +1.5% | 49 | 13.8% portfolio weight; up +1.5% today |
| 4 | SPGI | 0.5% | $448.35 | -0.6% | 76 | RSI elevated at 76; 20D move +16.4% |
| 5 | AMAT | 12.6% | $525.70 | -0.7% | 27 | 12.6% portfolio weight |

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
Altamira Trade Ideas - 2026-07-21
Market: SPY -0.2% | QQQ +0.1% | VIX 17.51 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: AMZN near $249.99; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: already approved portfolio name; price above 20-day trend; RSI balanced at 63
   Risk: earnings in 9 days (2026-07-30)

2) Covered-call/trim watch: AVGO at 16.7% weight.
   Rationale: 16.7% portfolio weight; up +2.0% today

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
