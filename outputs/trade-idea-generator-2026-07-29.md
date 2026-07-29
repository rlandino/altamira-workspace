# Trade Idea Generator - 2026-07-29

Generated: 2026-07-29T10:02:08.508859+00:00

## Executive Summary

- **Market regime:** VIX 18.17 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | COST | 70.0 | $966.58 | +1.6% | 54 | +3.3% | 2026-09-24 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | V | 64.0 | $366.59 | +1.1% | 67 | +6.8% | 2026-10-27 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 3 | MSFT | 58.0 | $393.35 | +1.1% | 56 | +5.5% | 2026-07-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 0 days (2026-07-29) |
| 4 | LLY | 56.2 | $1,222.61 | +2.1% | 51 | +1.9% | 2026-08-05 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 7 days (2026-08-05) |
| 5 | GOOGL | 48.0 | $333.71 | +2.2% | 37 | -6.6% | 2026-11-04 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | SPY | 17.1% | $740.86 | +0.2% | 46 | 17.1% portfolio weight |
| 2 | GOOGL | 13.8% | $333.71 | +2.2% | 37 | 13.8% portfolio weight; up +2.2% today |
| 3 | AVGO | 16.7% | $380.91 | -0.6% | 46 | 16.7% portfolio weight |
| 4 | AAPL | 4.6% | $340.08 | +0.9% | 72 | RSI elevated at 72; 20D move +17.5% |
| 5 | AMAT | 12.6% | $476.46 | -7.8% | 34 | 12.6% portfolio weight |

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
Altamira Trade Ideas - 2026-07-29
Market: SPY +0.2% | QQQ -1.0% | VIX 18.17 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: COST near $966.58; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: already approved portfolio name; price above 20-day trend; RSI balanced at 54

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
