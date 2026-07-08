# Trade Idea Generator - 2026-07-08

Generated: 2026-07-08T14:05:03.375199+00:00

## Executive Summary

- **Market regime:** VIX 17.25 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | ADBE | 64.5 | $218.60 | -1.3% | 59 | -8.1% | 2026-09-10 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | AVGO | 62.0 | $385.38 | +3.9% | 53 | -1.7% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | chasing after +3.9% day |
| 3 | AAPL | 58.0 | $309.02 | -0.5% | 57 | +6.4% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 22 days (2026-07-30) |
| 4 | V | 58.0 | $346.98 | -1.5% | 61 | +6.7% | 2026-07-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 20 days (2026-07-28) |
| 5 | MSFT | 54.0 | $383.43 | -1.4% | 45 | -5.0% | 2026-07-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 21 days (2026-07-29) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AMAT | 12.6% | $566.52 | +2.2% | 50 | 12.6% portfolio weight; 20D move +13.5%; up +2.2% today |
| 2 | AVGO | 16.7% | $385.38 | +3.9% | 53 | 16.7% portfolio weight; up +3.9% today |
| 3 | SPY | 17.1% | $743.86 | -0.5% | 45 | 17.1% portfolio weight |
| 4 | CRWD | 4.3% | $189.51 | -2.6% | 73 | RSI elevated at 73; 20D move +17.5% |
| 5 | ABBV | 3.8% | $253.21 | -0.6% | 73 | RSI elevated at 73; 20D move +12.3% |

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
Altamira Trade Ideas - 2026-07-08
Market: SPY -0.5% | QQQ -0.2% | VIX 17.25 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: ADBE near $218.60; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 60.1 (B-); price above 20-day trend; RSI balanced at 59

2) Covered-call/trim watch: AMAT at 12.6% weight.
   Rationale: 12.6% portfolio weight; 20D move +13.5%; up +2.2% today

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
