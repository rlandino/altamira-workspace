# Trade Idea Generator - 2026-07-16

Generated: 2026-07-16T10:03:26.737032+00:00

## Executive Summary

- **Market regime:** VIX 15.93 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | AVGO | 70.0 | $394.28 | +1.3% | 55 | +4.7% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | NVDA | 58.0 | $212.50 | +0.3% | 62 | +2.5% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 41 days (2026-08-26) |
| 3 | ASML | 56.2 | $1,815.27 | +2.2% | 53 | +0.6% | 2026-10-21 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 4 | ADBE | 53.5 | $224.56 | +1.7% | 73 | +8.3% | 2026-09-10 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | overbought RSI 73 |
| 5 | MSFT | 52.0 | $395.63 | +2.8% | 66 | +0.5% | 2026-07-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 13 days (2026-07-29) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | SPY | 17.1% | $754.81 | +0.4% | 68 | 17.1% portfolio weight; RSI elevated at 68 |
| 2 | GOOGL | 13.8% | $370.92 | +3.2% | 68 | 13.8% portfolio weight; up +3.2% today |
| 3 | AVGO | 16.7% | $394.28 | +1.3% | 55 | 16.7% portfolio weight |
| 4 | CRWD | 4.3% | $206.77 | -1.9% | 73 | RSI elevated at 73; 20D move +21.7% |
| 5 | AMAT | 12.6% | $579.43 | -2.7% | 49 | 12.6% portfolio weight |

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
Altamira Trade Ideas - 2026-07-16
Market: SPY +0.4% | QQQ -0.3% | VIX 15.93 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: AVGO near $394.28; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: already approved portfolio name; price above 20-day trend; RSI balanced at 55

2) Covered-call/trim watch: SPY at 17.1% weight.
   Rationale: 17.1% portfolio weight; RSI elevated at 68

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
