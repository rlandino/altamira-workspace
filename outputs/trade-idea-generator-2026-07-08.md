# Trade Idea Generator - 2026-07-08

Generated: 2026-07-08T10:02:43.738049+00:00

## Executive Summary

- **Market regime:** VIX 18.62 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | ADBE | 64.5 | $221.54 | +1.6% | 64 | -9.6% | 2026-09-10 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | GOOGL | 58.0 | $367.03 | +0.2% | 49 | +1.0% | 2026-07-22 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 14 days (2026-07-22) |
| 3 | AAPL | 58.0 | $310.66 | -0.6% | 60 | +3.0% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 22 days (2026-07-30) |
| 4 | AMZN | 58.0 | $245.98 | +0.7% | 50 | +0.3% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 22 days (2026-07-30) |
| 5 | MSFT | 54.0 | $388.84 | +0.5% | 45 | -5.6% | 2026-07-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 21 days (2026-07-29) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AMAT | 12.6% | $554.50 | -6.5% | 47 | 12.6% portfolio weight; 20D move +12.7% |
| 2 | SPY | 17.1% | $747.71 | -0.5% | 45 | 17.1% portfolio weight |
| 3 | AVGO | 16.7% | $370.78 | -0.8% | 42 | 16.7% portfolio weight |
| 4 | CRWD | 4.3% | $194.62 | -2.4% | 73 | RSI elevated at 73; 20D move +18.2% |
| 5 | ABBV | 3.8% | $254.65 | -0.0% | 76 | RSI elevated at 76; 20D move +14.2% |

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
Altamira Trade Ideas - 2026-07-08
Market: SPY -0.5% | QQQ -1.9% | VIX 18.62 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: ADBE near $221.54; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 60.1 (B-); price above 20-day trend; RSI balanced at 64

2) Covered-call/trim watch: AMAT at 12.6% weight.
   Rationale: 12.6% portfolio weight; 20D move +12.7%

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
