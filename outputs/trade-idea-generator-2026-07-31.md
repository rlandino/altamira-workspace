# Trade Idea Generator - 2026-07-31

Generated: 2026-07-31T14:01:35.417505+00:00

## Executive Summary

- **Market regime:** VIX 17.91 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | V | 70.0 | $364.26 | -0.5% | 56 | +2.0% | 2026-10-27 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | COST | 66.0 | $949.10 | -0.5% | 58 | -0.1% | 2026-09-24 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 3 | AMZN | 66.0 | $270.04 | +14.7% | 63 | +10.6% | 2026-10-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | chasing after +14.7% day |
| 4 | AVGO | 58.0 | $386.50 | -0.3% | 51 | +3.4% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 34 days (2026-09-03) |
| 5 | AAPL | 57.0 | $302.61 | -9.2% | 42 | -3.2% | 2026-10-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | SPY | 17.1% | $741.34 | -0.0% | 44 | 17.1% portfolio weight |
| 2 | MSFT | 6.7% | $461.12 | +2.2% | 74 | RSI elevated at 74; 20D move +19.2%; up +2.2% today |
| 3 | GOOGL | 13.8% | $345.91 | +3.7% | 46 | 13.8% portfolio weight; up +3.7% today |
| 4 | AVGO | 16.7% | $386.50 | -0.3% | 51 | 16.7% portfolio weight |
| 5 | AMAT | 12.6% | $511.12 | +1.9% | 41 | 12.6% portfolio weight; up +1.9% today |

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
Altamira Trade Ideas - 2026-07-31
Market: SPY -0.0% | QQQ +0.3% | VIX 17.91 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: V near $364.26; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: already approved portfolio name; price above 20-day trend; RSI balanced at 56

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
