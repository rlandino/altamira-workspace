# Trade Idea Generator - 2026-06-26

Generated: 2026-06-26T14:03:11.757751+00:00

## Executive Summary

- **Market regime:** VIX 19.59 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | V | 58.0 | $335.14 | +1.4% | 62 | +2.7% | 2026-07-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 32 days (2026-07-28) |
| 2 | ASML | 56.2 | $1,797.66 | -2.4% | 58 | +11.5% | 2026-07-15 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 19 days (2026-07-15) |
| 3 | COST | 54.0 | $953.23 | +1.2% | 43 | -0.3% | 2026-09-24 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 4 | AVGO | 50.0 | $368.64 | -2.7% | 45 | -17.5% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend; negative 20D trend -17.5% |
| 5 | NVDA | 48.0 | $193.69 | -1.0% | 40 | -8.3% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AMAT | 12.6% | $645.21 | -3.4% | 74 | 12.6% portfolio weight; RSI elevated at 74; 20D move +43.4% |
| 2 | SPY | 17.1% | $731.58 | -0.4% | 46 | 17.1% portfolio weight |
| 3 | ABBV | 3.8% | $248.14 | +2.1% | 69 | RSI elevated at 69; 20D move +14.0%; up +2.1% today |
| 4 | AVGO | 16.7% | $368.64 | -2.7% | 45 | 16.7% portfolio weight |
| 5 | GOOGL | 13.8% | $338.24 | -1.6% | 30 | 13.8% portfolio weight |

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
Altamira Trade Ideas - 2026-06-26
Market: SPY -0.4% | QQQ -0.9% | VIX 19.59 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: V near $335.14; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: already approved portfolio name; price above 20-day trend; RSI balanced at 62
   Risk: earnings in 32 days (2026-07-28)

2) Covered-call/trim watch: AMAT at 12.6% weight.
   Rationale: 12.6% portfolio weight; RSI elevated at 74; 20D move +43.4%

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
