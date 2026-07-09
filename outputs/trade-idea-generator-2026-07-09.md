# Trade Idea Generator - 2026-07-09

Generated: 2026-07-09T14:04:55.890746+00:00

## Executive Summary

- **Market regime:** VIX 16.46 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | AVGO | 70.0 | $394.60 | +1.5% | 50 | +6.0% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | NVDA | 58.0 | $201.16 | -1.5% | 47 | +0.4% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 3 | AAPL | 58.0 | $310.38 | -1.0% | 60 | +6.4% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 21 days (2026-07-30) |
| 4 | AMZN | 58.0 | $242.22 | -0.6% | 55 | +1.8% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 21 days (2026-07-30) |
| 5 | TSM | 57.0 | $444.21 | +1.7% | 53 | +8.7% | 2026-07-16 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 7 days (2026-07-16) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AMAT | 12.6% | $625.32 | +9.6% | 53 | 12.6% portfolio weight; 20D move +25.8%; up +9.6% today |
| 2 | AVGO | 16.7% | $394.60 | +1.5% | 50 | 16.7% portfolio weight; up +1.5% today |
| 3 | SPY | 17.1% | $748.84 | +0.5% | 56 | 17.1% portfolio weight |
| 4 | CRWD | 4.3% | $195.53 | +2.3% | 75 | RSI elevated at 75; 20D move +20.7%; up +2.3% today |
| 5 | ABBV | 3.8% | $253.88 | +0.5% | 75 | RSI elevated at 75; 20D move +12.9% |

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
Altamira Trade Ideas - 2026-07-09
Market: SPY +0.5% | QQQ +1.5% | VIX 16.46 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: AVGO near $394.60; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: already approved portfolio name; price above 20-day trend; RSI balanced at 50

2) Covered-call/trim watch: AMAT at 12.6% weight.
   Rationale: 12.6% portfolio weight; 20D move +25.8%; up +9.6% today

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
