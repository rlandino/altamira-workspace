# Trade Idea Generator - 2026-07-16

Generated: 2026-07-16T14:02:14.405059+00:00

## Executive Summary

- **Market regime:** VIX 16.13 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | NVDA | 58.0 | $207.66 | -2.3% | 61 | +1.5% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 41 days (2026-08-26) |
| 2 | AVGO | 57.0 | $381.70 | -3.2% | 51 | -2.9% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 3 | LLY | 56.2 | $1,173.15 | +1.4% | 57 | +5.5% | 2026-08-05 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 20 days (2026-08-05) |
| 4 | COST | 54.0 | $933.27 | +1.8% | 47 | -3.3% | 2026-09-24 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 5 | ASML | 52.2 | $1,816.40 | +0.1% | 48 | -2.8% | 2026-10-21 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | GOOGL | 13.8% | $370.48 | -0.1% | 69 | 13.8% portfolio weight; RSI elevated at 69 |
| 2 | SPY | 17.1% | $752.54 | -0.3% | 65 | 17.1% portfolio weight |
| 3 | AVGO | 16.7% | $381.70 | -3.2% | 51 | 16.7% portfolio weight |
| 4 | CRWD | 4.3% | $203.38 | -1.6% | 68 | RSI elevated at 68; 20D move +19.1% |
| 5 | SPGI | 0.5% | $448.82 | +1.0% | 82 | RSI elevated at 82; 20D move +13.5% |

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
Altamira Trade Ideas - 2026-07-16
Market: SPY -0.3% | QQQ -1.0% | VIX 16.13 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: NVDA near $207.66; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 66.2 (B); price above 20-day trend; RSI balanced at 61
   Risk: earnings in 41 days (2026-08-26)

2) Covered-call/trim watch: GOOGL at 13.8% weight.
   Rationale: 13.8% portfolio weight; RSI elevated at 69

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
