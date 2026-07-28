# Trade Idea Generator - 2026-07-28

Generated: 2026-07-28T14:02:45.748780+00:00

## Executive Summary

- **Market regime:** VIX 19.04 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | COST | 66.0 | $983.60 | +3.4% | 60 | +5.1% | 2026-09-24 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | chasing after +3.4% day |
| 2 | MSFT | 58.0 | $392.36 | +0.8% | 56 | +5.2% | 2026-07-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 1 days (2026-07-29) |
| 3 | LLY | 56.2 | $1,220.92 | +2.0% | 52 | +1.8% | 2026-08-05 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 8 days (2026-08-05) |
| 4 | V | 52.0 | $365.11 | +0.7% | 67 | +6.4% | 2026-07-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 0 days (2026-07-28) |
| 5 | AAPL | 48.0 | $337.70 | +0.2% | 71 | +16.7% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 2 days (2026-07-30) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | SPY | 17.1% | $737.70 | -0.2% | 42 | 17.1% portfolio weight |
| 2 | AVGO | 16.7% | $378.55 | -1.2% | 45 | 16.7% portfolio weight |
| 3 | AAPL | 4.6% | $337.70 | +0.2% | 71 | RSI elevated at 71; 20D move +16.7% |
| 4 | GOOGL | 13.8% | $326.80 | +0.1% | 32 | 13.8% portfolio weight |
| 5 | AMAT | 12.6% | $478.18 | -7.5% | 34 | 12.6% portfolio weight |

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
Altamira Trade Ideas - 2026-07-28
Market: SPY -0.2% | QQQ -1.6% | VIX 19.04 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: COST near $983.60; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: already approved portfolio name; price above 20-day trend; RSI balanced at 60
   Risk: chasing after +3.4% day

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
