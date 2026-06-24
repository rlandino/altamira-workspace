# Trade Idea Generator - 2026-06-24

Generated: 2026-06-24T14:02:42.976415+00:00

## Executive Summary

- **Market regime:** VIX 19.11 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | TSM | 57.0 | $437.91 | +0.3% | 51 | +3.6% | 2026-07-16 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 22 days (2026-07-16) |
| 2 | LLY | 56.2 | $1,125.77 | +1.7% | 62 | +4.0% | 2026-08-05 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 42 days (2026-08-05) |
| 3 | LRCX | 54.3 | $368.90 | -0.7% | 55 | +15.7% | 2026-07-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 35 days (2026-07-29) |
| 4 | COST | 54.0 | $963.14 | +0.6% | 50 | -4.0% | 2026-09-24 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 5 | V | 52.0 | $328.26 | -0.1% | 66 | +0.2% | 2026-07-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 34 days (2026-07-28) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AMAT | 12.6% | $585.13 | -0.1% | 63 | 12.6% portfolio weight; 20D move +30.5% |
| 2 | SPY | 17.1% | $735.46 | +0.3% | 41 | 17.1% portfolio weight |
| 3 | AVGO | 16.7% | $382.39 | +0.6% | 30 | 16.7% portfolio weight |
| 4 | GOOGL | 13.8% | $350.32 | +1.2% | 45 | 13.8% portfolio weight |
| 5 | ABBV | 3.8% | $236.37 | +0.7% | 68 | RSI elevated at 68 |

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
Altamira Trade Ideas - 2026-06-24
Market: SPY +0.3% | QQQ -0.0% | VIX 19.11 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: TSM near $437.91; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 61.8 (B-); price above 20-day trend; RSI balanced at 51
   Risk: earnings in 22 days (2026-07-16)

2) Covered-call/trim watch: AMAT at 12.6% weight.
   Rationale: 12.6% portfolio weight; 20D move +30.5%

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
