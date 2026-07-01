# Trade Idea Generator - 2026-07-01

Generated: 2026-07-01T10:04:14.522320+00:00

## Executive Summary

- **Market regime:** VIX 16.89 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | TSM | 53.0 | $477.57 | +4.9% | 63 | +6.9% | 2026-07-16 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | chasing after +4.9% day; earnings in 15 days (2026-07-16) |
| 2 | LLY | 52.2 | $1,199.30 | -2.5% | 61 | +12.7% | 2026-08-05 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 35 days (2026-08-05) |
| 3 | V | 52.0 | $343.09 | +0.4% | 69 | +8.1% | 2026-07-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 27 days (2026-07-28) |
| 4 | ASML | 48.2 | $1,989.44 | +5.6% | 61 | +16.7% | 2026-07-15 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | chasing after +5.6% day; earnings in 14 days (2026-07-15) |
| 5 | COST | 48.0 | $935.47 | -1.2% | 37 | -2.0% | 2026-09-24 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AMAT | 12.6% | $723.00 | +4.1% | 75 | 12.6% portfolio weight; RSI elevated at 75; 20D move +47.5%; up +4.1% today |
| 2 | SPY | 17.1% | $746.77 | +0.8% | 55 | 17.1% portfolio weight |
| 3 | AVGO | 16.7% | $377.75 | +1.4% | 46 | 16.7% portfolio weight |
| 4 | ABBV | 3.8% | $251.42 | -1.1% | 73 | RSI elevated at 73; 20D move +16.7% |
| 5 | GOOGL | 13.8% | $357.37 | +1.1% | 46 | 13.8% portfolio weight |

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
Market: SPY +0.8% | QQQ +1.7% | VIX 16.89 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: TSM near $477.57; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 61.8 (B-); price above 20-day trend; RSI balanced at 63
   Risk: chasing after +4.9% day; earnings in 15 days (2026-07-16)

2) Covered-call/trim watch: AMAT at 12.6% weight.
   Rationale: 12.6% portfolio weight; RSI elevated at 75; 20D move +47.5%

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
