# Trade Idea Generator - 2026-07-09

Generated: 2026-07-09T10:03:35.354815+00:00

## Executive Summary

- **Market regime:** VIX 16.92 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | ADBE | 64.5 | $220.94 | -0.3% | 63 | -7.1% | 2026-09-10 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | NVDA | 62.0 | $204.12 | +3.7% | 47 | -2.0% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | chasing after +3.7% day |
| 3 | AVGO | 62.0 | $388.69 | +4.8% | 54 | -0.9% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | chasing after +4.8% day |
| 4 | AAPL | 58.0 | $313.39 | +0.9% | 59 | +7.9% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 21 days (2026-07-30) |
| 5 | V | 58.0 | $347.53 | -1.3% | 62 | +6.9% | 2026-07-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 19 days (2026-07-28) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AMAT | 12.6% | $570.50 | +2.9% | 50 | 12.6% portfolio weight; 20D move +14.3%; up +2.9% today |
| 2 | AVGO | 16.7% | $388.69 | +4.8% | 54 | 16.7% portfolio weight; up +4.8% today |
| 3 | SPY | 17.1% | $745.40 | -0.3% | 46 | 17.1% portfolio weight |
| 4 | CRWD | 4.3% | $191.12 | -1.8% | 73 | RSI elevated at 73; 20D move +18.5% |
| 5 | ABBV | 3.8% | $252.61 | -0.8% | 73 | RSI elevated at 73; 20D move +12.1% |

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
Market: SPY -0.3% | QQQ +0.3% | VIX 16.92 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: ADBE near $220.94; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 60.1 (B-); price above 20-day trend; RSI balanced at 63

2) Covered-call/trim watch: AMAT at 12.6% weight.
   Rationale: 12.6% portfolio weight; 20D move +14.3%; up +2.9% today

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
