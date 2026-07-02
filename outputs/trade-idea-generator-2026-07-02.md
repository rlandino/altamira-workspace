# Trade Idea Generator - 2026-07-02

Generated: 2026-07-02T14:03:58.315269+00:00

## Executive Summary

- **Market regime:** VIX 15.82 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | ADBE | 57.5 | $217.06 | +2.9% | 49 | -16.0% | 2026-09-10 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | negative 20D trend -16.0% |
| 2 | ASML | 56.2 | $1,854.00 | +0.6% | 47 | +5.5% | 2026-07-15 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 13 days (2026-07-15) |
| 3 | LLY | 56.2 | $1,217.13 | +2.1% | 60 | +8.2% | 2026-08-05 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 34 days (2026-08-05) |
| 4 | LRCX | 54.3 | $384.27 | -1.8% | 53 | +14.2% | 2026-07-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 27 days (2026-07-29) |
| 5 | NVDA | 54.0 | $199.83 | +1.1% | 44 | -8.6% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AMAT | 12.6% | $641.11 | -1.5% | 59 | 12.6% portfolio weight; 20D move +27.8% |
| 2 | SPY | 17.1% | $750.94 | +0.7% | 58 | 17.1% portfolio weight |
| 3 | AVGO | 16.7% | $373.44 | +1.1% | 45 | 16.7% portfolio weight |
| 4 | ABBV | 3.8% | $254.59 | +1.4% | 75 | RSI elevated at 75; 20D move +13.2% |
| 5 | GOOGL | 13.8% | $362.52 | +0.4% | 53 | 13.8% portfolio weight |

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
Altamira Trade Ideas - 2026-07-02
Market: SPY +0.7% | QQQ +0.8% | VIX 15.82 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: ADBE near $217.06; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 60.1 (B-); price above 20-day trend; RSI balanced at 49
   Risk: negative 20D trend -16.0%

2) Covered-call/trim watch: AMAT at 12.6% weight.
   Rationale: 12.6% portfolio weight; 20D move +27.8%

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
