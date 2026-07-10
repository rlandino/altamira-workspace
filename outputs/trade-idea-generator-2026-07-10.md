# Trade Idea Generator - 2026-07-10

Generated: 2026-07-10T10:05:05.969370+00:00

## Executive Summary

- **Market regime:** VIX 16.03 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | NVDA | 70.0 | $202.78 | -0.7% | 48 | +1.2% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | AVGO | 66.0 | $401.11 | +3.2% | 53 | +7.8% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | chasing after +3.2% day |
| 3 | GOOGL | 58.0 | $358.89 | -0.8% | 47 | +0.7% | 2026-07-23 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 13 days (2026-07-23) |
| 4 | AAPL | 58.0 | $316.22 | +0.9% | 64 | +8.5% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 20 days (2026-07-30) |
| 5 | AMZN | 58.0 | $247.04 | +1.4% | 59 | +3.8% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 20 days (2026-07-30) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AMAT | 12.6% | $588.66 | +3.2% | 50 | 12.6% portfolio weight; 20D move +18.4%; up +3.2% today |
| 2 | AVGO | 16.7% | $401.11 | +3.2% | 53 | 16.7% portfolio weight; up +3.2% today |
| 3 | SPY | 17.1% | $751.71 | +0.8% | 58 | 17.1% portfolio weight |
| 4 | CRWD | 4.3% | $198.40 | +3.8% | 76 | RSI elevated at 76; 20D move +22.5%; up +3.8% today |
| 5 | GOOGL | 13.8% | $358.89 | -0.8% | 47 | 13.8% portfolio weight |

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
Altamira Trade Ideas - 2026-07-10
Market: SPY +0.8% | QQQ +1.7% | VIX 16.03 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: NVDA near $202.78; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 66.2 (B); price above 20-day trend; RSI balanced at 48

2) Covered-call/trim watch: AMAT at 12.6% weight.
   Rationale: 12.6% portfolio weight; 20D move +18.4%; up +3.2% today

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
