# Trade Idea Generator - 2026-06-18

Generated: 2026-06-18T14:02:43.669999+00:00

## Executive Summary

- **Market regime:** VIX 17.23 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | LLY | 56.2 | $1,104.09 | -0.7% | 50 | +6.0% | 2026-08-05 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 2 | NVDA | 54.0 | $208.05 | +1.7% | 48 | -5.2% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 3 | COST | 54.0 | $949.50 | -1.7% | 48 | -9.6% | 2026-09-24 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 4 | V | 54.0 | $328.83 | -0.5% | 52 | -0.7% | 2026-07-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 40 days (2026-07-28) |
| 5 | TSM | 53.0 | $448.99 | +3.9% | 58 | +10.3% | 2026-07-16 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | chasing after +3.9% day; earnings in 28 days (2026-07-16) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AMAT | 12.6% | $636.42 | +7.3% | 79 | 12.6% portfolio weight; RSI elevated at 79; 20D move +48.9%; up +7.3% today |
| 2 | AVGO | 16.7% | $408.11 | +3.9% | 42 | 16.7% portfolio weight; up +3.9% today |
| 3 | SPY | 17.1% | $744.93 | +0.5% | 44 | 17.1% portfolio weight |
| 4 | GOOGL | 13.8% | $362.55 | -0.3% | 38 | 13.8% portfolio weight |
| 5 | JPM | 2.1% | $333.65 | +0.1% | 83 | RSI elevated at 83 |

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
Altamira Trade Ideas - 2026-06-18
Market: SPY +0.5% | QQQ +1.8% | VIX 17.23 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: LLY near $1,104.09; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 58.7 (C+); RSI balanced at 50; constructive 20D move +6.0%
   Risk: below 20-day trend

2) Covered-call/trim watch: AMAT at 12.6% weight.
   Rationale: 12.6% portfolio weight; RSI elevated at 79; 20D move +48.9%

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
