# Trade Idea Generator - 2026-07-14

Generated: 2026-07-14T14:01:47.609625+00:00

## Executive Summary

- **Market regime:** VIX 16.47 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | AVGO | 66.0 | $390.16 | +1.6% | 55 | -1.0% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | AAPL | 58.0 | $313.70 | -1.1% | 64 | +5.8% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 16 days (2026-07-30) |
| 3 | ADBE | 56.5 | $223.04 | -3.3% | 73 | +8.1% | 2026-09-10 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | overbought RSI 73 |
| 4 | NVDA | 54.0 | $204.66 | +0.6% | 55 | -3.7% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 43 days (2026-08-26) |
| 5 | MSFT | 54.0 | $385.02 | -1.5% | 56 | -3.7% | 2026-07-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 15 days (2026-07-29) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AVGO | 16.7% | $390.16 | +1.6% | 55 | 16.7% portfolio weight; up +1.6% today |
| 2 | SPY | 17.1% | $750.84 | +0.2% | 66 | 17.1% portfolio weight |
| 3 | CRWD | 4.3% | $203.65 | +8.4% | 72 | RSI elevated at 72; 20D move +17.6%; up +8.4% today |
| 4 | AMAT | 12.6% | $598.01 | +3.9% | 51 | 12.6% portfolio weight; up +3.9% today |
| 5 | GOOGL | 13.8% | $353.89 | +0.4% | 57 | 13.8% portfolio weight |

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
Altamira Trade Ideas - 2026-07-14
Market: SPY +0.2% | QQQ +1.0% | VIX 16.47 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: AVGO near $390.16; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: already approved portfolio name; price above 20-day trend; RSI balanced at 55

2) Covered-call/trim watch: AVGO at 16.7% weight.
   Rationale: 16.7% portfolio weight; up +1.6% today

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
