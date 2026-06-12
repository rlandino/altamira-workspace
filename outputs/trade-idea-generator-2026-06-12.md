# Trade Idea Generator - 2026-06-12

Generated: 2026-06-12T14:04:59.071039+00:00

## Executive Summary

- **Market regime:** VIX 18.90 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | LLY | 58.2 | $1,160.50 | -0.0% | 68 | +15.5% | 2026-08-05 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | TSM | 57.0 | $422.75 | +0.4% | 55 | +4.6% | 2026-07-16 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 34 days (2026-07-16) |
| 3 | LRCX | 54.4 | $362.00 | -0.1% | 67 | +27.1% | 2026-07-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | extended 20D move +27.1% |
| 4 | NVDA | 54.0 | $205.08 | +0.1% | 41 | -9.0% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 5 | V | 54.0 | $323.79 | +1.5% | 45 | -0.6% | 2026-07-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AMAT | 12.6% | $551.47 | -0.2% | 75 | 12.6% portfolio weight; RSI elevated at 75; 20D move +26.3% |
| 2 | SPY | 17.1% | $738.83 | +0.1% | 44 | 17.1% portfolio weight |
| 3 | AVGO | 16.7% | $380.34 | -1.4% | 42 | 16.7% portfolio weight |
| 4 | GOOGL | 13.8% | $359.35 | +0.4% | 33 | 13.8% portfolio weight |
| 5 | CRWD | 4.3% | $697.74 | +0.9% | 54 | 20D move +17.4% |

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
Altamira Trade Ideas - 2026-06-12
Market: SPY +0.1% | QQQ +0.0% | VIX 18.90 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: LLY near $1,160.50; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 58.7 (C+); price above 20-day trend; no near-term earnings conflict (2026-08-05)

2) Covered-call/trim watch: AMAT at 12.6% weight.
   Rationale: 12.6% portfolio weight; RSI elevated at 75; 20D move +26.3%

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
