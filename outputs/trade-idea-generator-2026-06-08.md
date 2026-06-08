# Trade Idea Generator - 2026-06-08

Generated: 2026-06-08T14:09:24.180092+00:00

## Executive Summary

- **Market regime:** VIX 18.75 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 5 short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | AAPL | 70.0 | $311.64 | +1.4% | 65 | +6.5% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | LRCX | 66.3 | $318.43 | +5.0% | 63 | +7.6% | 2026-07-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | chasing after +5.0% day |
| 3 | KLAC | 58.8 | $2,062.56 | +6.9% | 66 | +11.8% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | chasing after +6.9% day |
| 4 | TSM | 57.0 | $427.03 | +2.9% | 62 | +5.6% | 2026-07-16 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 38 days (2026-07-16) |
| 5 | MSFT | 54.0 | $411.58 | -1.2% | 45 | -0.3% | 2026-07-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AVGO | 16.7% | $393.23 | +1.9% | 43 | 16.7% portfolio weight; up +1.9% today |
| 2 | SPY | 17.1% | $742.07 | +0.6% | 52 | 17.1% portfolio weight |
| 3 | AMAT | 12.6% | $482.57 | +6.5% | 67 | 12.6% portfolio weight; up +6.5% today |
| 4 | GOOGL | 13.8% | $361.36 | -1.9% | 28 | 13.8% portfolio weight |
| 5 | ABBV | 3.8% | $226.17 | -0.5% | 72 | RSI elevated at 72 |

## Existing Short-Premium Review

| Ticker | Expiration | Strike | Credit | Current | Status |
|---|---|---:|---:|---:|---|
| MSFT | 2026-03-20 | 430 | 8.70 | 22.40 | Stop/roll review |
| MSFT | 2026-05-15 | 380 | 10.12 | 11.80 | Hold per plan |
| AVGO | 2026-03-20 | 310 | 12.60 | 5.00 | Profit-taking candidate |
| SPY | 2026-05-15 | 620 | 6.92 | 10.16 | Hold per plan |
| COST | 2026-05-15 | 900 | 11.00 | 12.40 | Hold per plan |

## Portfolio Risk Flags

- Technology exposure is high at 45.4% across listed holdings.
- SPY is above 15% single-name/ETF weight at 17.1%.
- AVGO is above 15% single-name/ETF weight at 16.7%.
- MSFT 2026-03-20 430P is near/above stop review (22.40 current vs 8.70 credit).

## Telegram Message

```text
Altamira Trade Ideas - 2026-06-08
Market: SPY +0.6% | QQQ +1.5% | VIX 18.75 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: AAPL near $311.64; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: already approved portfolio name; price above 20-day trend; RSI balanced at 65

2) Covered-call/trim watch: AVGO at 16.7% weight.
   Rationale: 16.7% portfolio weight; up +1.9% today

Risk flags:
- Technology exposure is high at 45.4% across listed holdings.
- SPY is above 15% single-name/ETF weight at 17.1%.
- AVGO is above 15% single-name/ETF weight at 16.7%.

Educational only - not financial advice. Verify quotes, greeks, liquidity, earnings, and order tickets before trading.
```

## Data Notes

- Portfolio/watchlist positions are sourced from repository context files.
- Live quotes and historical prices are sourced from FMP at runtime.
- Option contracts are included only when the FMP options chain endpoint returns usable data.
- Financial calculations are estimates for research and workflow triage only.

> Disclaimer: This report is for educational and operational planning purposes only. It is not financial advice. Verify live quotes, greeks, liquidity, earnings dates, portfolio exposure, and order tickets before placing any trade.
