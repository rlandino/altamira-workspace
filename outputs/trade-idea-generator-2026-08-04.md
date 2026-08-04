# Trade Idea Generator - 2026-08-04

Generated: 2026-08-04T10:02:39.966984+00:00

## Executive Summary

- **Market regime:** VIX 15.71 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | COST | 70.0 | $954.08 | +0.2% | 63 | +0.7% | 2026-09-24 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | V | 70.0 | $365.67 | -0.1% | 60 | +3.8% | 2026-10-27 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 3 | GOOGL | 66.0 | $373.51 | +4.9% | 55 | +1.8% | 2026-10-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | chasing after +4.9% day |
| 4 | NVDA | 58.0 | $206.64 | +2.9% | 46 | +4.9% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 22 days (2026-08-26) |
| 5 | AVGO | 58.0 | $392.23 | +0.8% | 51 | +5.8% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 30 days (2026-09-03) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | SPY | 17.1% | $757.67 | +1.4% | 54 | 17.1% portfolio weight |
| 2 | MSFT | 6.7% | $487.65 | +4.9% | 81 | RSI elevated at 81; 20D move +25.4%; up +4.9% today |
| 3 | AMZN | 4.9% | $284.02 | +4.6% | 69 | RSI elevated at 69; 20D move +15.5%; up +4.6% today |
| 4 | GOOGL | 13.8% | $373.51 | +4.9% | 55 | 13.8% portfolio weight; up +4.9% today |
| 5 | AVGO | 16.7% | $392.23 | +0.8% | 51 | 16.7% portfolio weight |

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
Altamira Trade Ideas - 2026-08-04
Market: SPY +1.4% | QQQ +1.8% | VIX 15.71 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: COST near $954.08; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: already approved portfolio name; price above 20-day trend; RSI balanced at 63

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
