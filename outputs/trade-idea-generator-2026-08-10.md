# Trade Idea Generator - 2026-08-10

Generated: 2026-08-10T14:01:57.351703+00:00

## Executive Summary

- **Market regime:** VIX 15.16 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | V | 70.0 | $362.41 | -0.0% | 59 | +1.8% | 2026-10-27 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | LLY | 68.2 | $1,207.97 | +1.9% | 56 | +4.8% | 2026-10-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 3 | GOOGL | 66.0 | $353.40 | -0.3% | 53 | -1.7% | 2026-10-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 4 | TSM | 65.0 | $420.37 | +0.1% | 48 | -0.0% | 2026-10-15 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 5 | ASML | 64.2 | $1,761.48 | +1.2% | 46 | -0.8% | 2026-10-14 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AVGO | 16.7% | $429.24 | +0.3% | 72 | 16.7% portfolio weight; RSI elevated at 72 |
| 2 | SPY | 17.1% | $773.70 | +0.1% | 67 | 17.1% portfolio weight |
| 3 | MSFT | 6.7% | $507.83 | +1.6% | 85 | RSI elevated at 85; 20D move +31.9%; up +1.6% today |
| 4 | NOW | 0.5% | $124.25 | -0.5% | 70 | RSI elevated at 70; 20D move +18.5% |
| 5 | GOOGL | 13.8% | $353.40 | -0.3% | 53 | 13.8% portfolio weight |

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
Altamira Trade Ideas - 2026-08-10
Market: SPY +0.1% | QQQ -0.0% | VIX 15.16 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: V near $362.41; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: already approved portfolio name; price above 20-day trend; RSI balanced at 59

2) Covered-call/trim watch: AVGO at 16.7% weight.
   Rationale: 16.7% portfolio weight; RSI elevated at 72

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
