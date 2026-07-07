# Trade Idea Generator - 2026-07-07

Generated: 2026-07-07T14:05:58.965464+00:00

## Executive Summary

- **Market regime:** VIX 16.11 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | COST | 66.0 | $964.44 | +1.5% | 44 | -1.1% | 2026-09-24 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | ADBE | 64.5 | $221.57 | +1.6% | 64 | -9.6% | 2026-09-10 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 3 | GOOGL | 58.0 | $371.32 | +1.3% | 51 | +2.2% | 2026-07-22 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 15 days (2026-07-22) |
| 4 | AAPL | 58.0 | $311.83 | -0.3% | 60 | +3.4% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 23 days (2026-07-30) |
| 5 | AMZN | 58.0 | $246.84 | +1.1% | 52 | +0.7% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 23 days (2026-07-30) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | SPY | 17.1% | $748.60 | -0.4% | 46 | 17.1% portfolio weight |
| 2 | ABBV | 3.8% | $259.14 | +1.7% | 77 | RSI elevated at 77; 20D move +16.2%; up +1.7% today |
| 3 | AVGO | 16.7% | $366.75 | -1.9% | 41 | 16.7% portfolio weight |
| 4 | CRWD | 4.3% | $194.09 | -2.7% | 72 | RSI elevated at 72; 20D move +17.8% |
| 5 | GOOGL | 13.8% | $371.32 | +1.3% | 51 | 13.8% portfolio weight |

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
Altamira Trade Ideas - 2026-07-07
Market: SPY -0.4% | QQQ -1.7% | VIX 16.11 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: COST near $964.44; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: already approved portfolio name; price above 20-day trend; RSI balanced at 44

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
