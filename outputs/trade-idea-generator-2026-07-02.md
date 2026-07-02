# Trade Idea Generator - 2026-07-02

Generated: 2026-07-02T10:03:58.394589+00:00

## Executive Summary

- **Market regime:** VIX 16.68 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | TSM | 60.0 | $444.23 | -7.0% | 58 | +1.7% | 2026-07-16 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 14 days (2026-07-16) |
| 2 | ASML | 59.2 | $1,843.04 | -7.4% | 55 | +6.8% | 2026-07-15 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 13 days (2026-07-15) |
| 3 | GOOGL | 58.0 | $361.21 | +1.1% | 53 | +0.6% | 2026-07-22 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 20 days (2026-07-22) |
| 4 | LRCX | 57.3 | $391.26 | -9.7% | 61 | +13.8% | 2026-07-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 27 days (2026-07-29) |
| 5 | LLY | 56.2 | $1,191.71 | -0.6% | 61 | +10.5% | 2026-08-05 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 34 days (2026-08-05) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AMAT | 12.6% | $650.91 | -10.0% | 65 | 12.6% portfolio weight; 20D move +30.0% |
| 2 | SPY | 17.1% | $745.76 | -0.1% | 62 | 17.1% portfolio weight |
| 3 | V | 2.2% | $351.08 | +2.3% | 77 | RSI elevated at 77; 20D move +12.4%; up +2.3% today |
| 4 | AVGO | 16.7% | $369.34 | -2.2% | 49 | 16.7% portfolio weight |
| 5 | ABBV | 3.8% | $251.07 | -0.2% | 73 | RSI elevated at 73; 20D move +15.6% |

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
Altamira Trade Ideas - 2026-07-02
Market: SPY -0.1% | QQQ -1.5% | VIX 16.68 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: TSM near $444.23; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 61.8 (B-); price above 20-day trend; RSI balanced at 58
   Risk: earnings in 14 days (2026-07-16)

2) Covered-call/trim watch: AMAT at 12.6% weight.
   Rationale: 12.6% portfolio weight; 20D move +30.0%

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
