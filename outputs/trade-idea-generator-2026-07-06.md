# Trade Idea Generator - 2026-07-06

Generated: 2026-07-06T10:02:56.985248+00:00

## Executive Summary

- **Market regime:** VIX 16.37 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | LLY | 56.2 | $1,210.50 | +1.6% | 60 | +7.6% | 2026-08-05 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 30 days (2026-08-05) |
| 2 | MSFT | 54.0 | $390.49 | +1.6% | 50 | -8.8% | 2026-07-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 23 days (2026-07-29) |
| 3 | COST | 54.0 | $951.67 | +2.9% | 42 | -2.1% | 2026-09-24 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 4 | GOOGL | 54.0 | $359.91 | -0.4% | 51 | -3.3% | 2026-07-22 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 16 days (2026-07-22) |
| 5 | AMZN | 54.0 | $242.67 | +0.4% | 51 | -4.4% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 24 days (2026-07-30) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AMAT | 12.6% | $603.04 | -7.4% | 55 | 12.6% portfolio weight; 20D move +20.2% |
| 2 | SPY | 17.1% | $744.78 | -0.1% | 55 | 17.1% portfolio weight |
| 3 | ABBV | 3.8% | $261.07 | +4.0% | 77 | RSI elevated at 77; 20D move +16.1%; up +4.0% today |
| 4 | V | 2.2% | $362.13 | +3.1% | 86 | RSI elevated at 86; 20D move +13.1%; up +3.1% today |
| 5 | AVGO | 16.7% | $360.45 | -2.4% | 41 | 16.7% portfolio weight |

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
Altamira Trade Ideas - 2026-07-06
Market: SPY -0.1% | QQQ -1.7% | VIX 16.37 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: LLY near $1,210.50; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 58.7 (C+); price above 20-day trend; RSI balanced at 60
   Risk: earnings in 30 days (2026-08-05)

2) Covered-call/trim watch: AMAT at 12.6% weight.
   Rationale: 12.6% portfolio weight; 20D move +20.2%

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
