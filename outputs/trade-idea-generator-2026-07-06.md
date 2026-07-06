# Trade Idea Generator - 2026-07-06

Generated: 2026-07-06T14:04:00.663221+00:00

## Executive Summary

- **Market regime:** VIX 16.24 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | AAPL | 58.0 | $309.39 | +0.2% | 62 | +0.7% | 2026-07-30 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 24 days (2026-07-30) |
| 2 | ADBE | 57.5 | $215.86 | -1.8% | 61 | -14.2% | 2026-09-10 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | negative 20D trend -14.2% |
| 3 | LLY | 56.2 | $1,192.00 | -1.8% | 61 | +5.4% | 2026-08-05 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 30 days (2026-08-05) |
| 4 | V | 55.0 | $351.12 | -3.0% | 70 | +8.5% | 2026-07-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 22 days (2026-07-28) |
| 5 | NVDA | 54.0 | $196.34 | +0.8% | 42 | -4.3% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AMAT | 12.6% | $615.16 | +2.0% | 55 | 12.6% portfolio weight; 20D move +35.8%; up +2.0% today |
| 2 | AVGO | 16.7% | $380.98 | +5.7% | 49 | 16.7% portfolio weight; up +5.7% today |
| 3 | SPY | 17.1% | $748.94 | +0.6% | 54 | 17.1% portfolio weight |
| 4 | CRWD | 4.3% | $206.00 | +6.2% | 85 | RSI elevated at 85; 20D move +22.8%; up +6.2% today |
| 5 | ABBV | 3.8% | $255.66 | -2.1% | 70 | RSI elevated at 70; 20D move +12.5% |

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
Altamira Trade Ideas - 2026-07-06
Market: SPY +0.6% | QQQ +1.4% | VIX 16.24 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: AAPL near $309.39; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: already approved portfolio name; price above 20-day trend; RSI balanced at 62
   Risk: earnings in 24 days (2026-07-30)

2) Covered-call/trim watch: AMAT at 12.6% weight.
   Rationale: 12.6% portfolio weight; 20D move +35.8%; up +2.0% today

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
