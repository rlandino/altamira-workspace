# Trade Idea Generator - 2026-07-21

Generated: 2026-07-21T14:03:01.592685+00:00

## Executive Summary

- **Market regime:** VIX 17.73 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | ADBE | 58.5 | $229.39 | -2.3% | 68 | +16.2% | 2026-09-10 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | NVDA | 58.0 | $205.14 | +0.9% | 55 | +2.5% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 36 days (2026-08-26) |
| 3 | AVGO | 58.0 | $381.56 | +0.9% | 52 | +0.4% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 44 days (2026-09-03) |
| 4 | AMZN | 58.0 | $247.47 | -1.0% | 62 | +5.7% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 9 days (2026-07-30) |
| 5 | V | 58.0 | $357.33 | -0.9% | 60 | +8.8% | 2026-07-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 7 days (2026-07-28) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | SPY | 17.1% | $745.33 | +0.4% | 49 | 17.1% portfolio weight |
| 2 | AVGO | 16.7% | $381.56 | +0.9% | 52 | 16.7% portfolio weight |
| 3 | AMAT | 12.6% | $558.80 | +6.3% | 28 | 12.6% portfolio weight; up +6.3% today |
| 4 | SPGI | 0.5% | $436.96 | -2.5% | 69 | RSI elevated at 69; 20D move +15.4% |
| 5 | GOOGL | 13.8% | $349.52 | -0.7% | 45 | 13.8% portfolio weight |

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
Altamira Trade Ideas - 2026-07-21
Market: SPY +0.4% | QQQ +1.2% | VIX 17.73 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: ADBE near $229.39; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 60.1 (B-); price above 20-day trend; no near-term earnings conflict (2026-09-10)

2) Covered-call/trim watch: SPY at 17.1% weight.
   Rationale: 17.1% portfolio weight

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
