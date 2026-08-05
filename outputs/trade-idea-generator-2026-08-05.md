# Trade Idea Generator - 2026-08-05

Generated: 2026-08-05T14:03:10.414381+00:00

## Executive Summary

- **Market regime:** VIX 17.08 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | COST | 70.0 | $943.50 | -0.5% | 48 | +3.3% | 2026-09-24 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | GOOGL | 70.0 | $378.32 | +0.2% | 61 | +5.4% | 2026-10-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 3 | AMZN | 70.0 | $276.14 | -0.5% | 64 | +11.8% | 2026-10-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 4 | V | 70.0 | $370.23 | +0.2% | 55 | +6.3% | 2026-10-27 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 5 | LRCX | 66.3 | $318.81 | +0.3% | 50 | -9.7% | 2026-10-21 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AVGO | 16.7% | $420.82 | +0.6% | 72 | 16.7% portfolio weight; RSI elevated at 72 |
| 2 | SPY | 17.1% | $775.23 | +0.5% | 65 | 17.1% portfolio weight |
| 3 | MSFT | 6.7% | $488.18 | -0.9% | 78 | RSI elevated at 78; 20D move +27.0% |
| 4 | GOOGL | 13.8% | $378.32 | +0.2% | 61 | 13.8% portfolio weight |
| 5 | AMAT | 12.6% | $546.20 | -0.1% | 49 | 12.6% portfolio weight |

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
Altamira Trade Ideas - 2026-08-05
Market: SPY +0.5% | QQQ +0.2% | VIX 17.08 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: COST near $943.50; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: already approved portfolio name; price above 20-day trend; RSI balanced at 48

2) Covered-call/trim watch: AVGO at 16.7% weight.
   Rationale: 16.7% portfolio weight; RSI elevated at 72

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
