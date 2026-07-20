# Trade Idea Generator - 2026-07-20

Generated: 2026-07-20T10:05:35.789920+00:00

## Executive Summary

- **Market regime:** VIX 18.29 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | COST | 66.0 | $940.87 | -0.5% | 46 | -1.1% | 2026-09-24 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | MSFT | 58.0 | $393.82 | -1.8% | 64 | +3.8% | 2026-07-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 9 days (2026-07-29) |
| 3 | LLY | 56.2 | $1,179.09 | +0.8% | 44 | +7.3% | 2026-08-05 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 16 days (2026-08-05) |
| 4 | NVDA | 54.0 | $202.81 | -2.2% | 59 | -3.7% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 37 days (2026-08-26) |
| 5 | ASML | 52.2 | $1,747.58 | -2.1% | 47 | -9.4% | 2026-10-14 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | SPY | 17.1% | $743.29 | -1.0% | 61 | 17.1% portfolio weight |
| 2 | AVGO | 16.7% | $370.82 | -1.0% | 52 | 16.7% portfolio weight |
| 3 | SPGI | 0.5% | $450.84 | -1.4% | 77 | RSI elevated at 77; 20D move +16.0% |
| 4 | GOOGL | 13.8% | $346.77 | -2.2% | 55 | 13.8% portfolio weight |
| 5 | AMAT | 12.6% | $529.66 | -5.6% | 39 | 12.6% portfolio weight |

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
Altamira Trade Ideas - 2026-07-20
Market: SPY -1.0% | QQQ -1.5% | VIX 18.29 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: COST near $940.87; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: already approved portfolio name; price above 20-day trend; RSI balanced at 46

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
