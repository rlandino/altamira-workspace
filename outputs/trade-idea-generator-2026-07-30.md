# Trade Idea Generator - 2026-07-30

Generated: 2026-07-30T14:01:40.133584+00:00

## Executive Summary

- **Market regime:** VIX 18.14 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | COST | 70.0 | $951.92 | -2.3% | 63 | +0.0% | 2026-09-24 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | V | 70.0 | $364.30 | -1.2% | 63 | +0.6% | 2026-10-27 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 3 | AAPL | 58.0 | $331.83 | -1.9% | 63 | +7.5% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 0 days (2026-07-30) |
| 4 | ADBE | 55.5 | $246.28 | -6.5% | 59 | +12.1% | 2026-09-10 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 42 days (2026-09-10) |
| 5 | AVGO | 54.0 | $386.66 | +4.4% | 44 | +7.3% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | chasing after +4.4% day; earnings in 35 days (2026-09-03) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AVGO | 16.7% | $386.66 | +4.4% | 44 | 16.7% portfolio weight; up +4.4% today |
| 2 | SPY | 17.1% | $738.69 | +1.3% | 37 | 17.1% portfolio weight |
| 3 | MSFT | 6.7% | $450.78 | +15.4% | 73 | RSI elevated at 73; 20D move +15.4%; up +15.4% today |
| 4 | AMAT | 12.6% | $501.36 | +14.9% | 36 | 12.6% portfolio weight; up +14.9% today |
| 5 | GOOGL | 13.8% | $332.63 | -1.2% | 39 | 13.8% portfolio weight |

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
Altamira Trade Ideas - 2026-07-30
Market: SPY +1.3% | QQQ +3.0% | VIX 18.14 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: COST near $951.92; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: already approved portfolio name; price above 20-day trend; RSI balanced at 63

2) Covered-call/trim watch: AVGO at 16.7% weight.
   Rationale: 16.7% portfolio weight; up +4.4% today

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
