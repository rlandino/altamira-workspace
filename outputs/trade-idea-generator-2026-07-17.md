# Trade Idea Generator - 2026-07-17

Generated: 2026-07-17T10:01:20.339339+00:00

## Executive Summary

- **Market regime:** VIX 18.44 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | COST | 62.0 | $945.57 | +3.2% | 51 | -2.1% | 2026-09-24 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | chasing after +3.2% day |
| 2 | NVDA | 58.0 | $207.40 | -2.4% | 60 | +1.3% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 40 days (2026-08-26) |
| 3 | AVGO | 57.0 | $374.45 | -5.0% | 48 | -4.7% | 2026-09-03 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 4 | TSM | 53.0 | $409.74 | -2.3% | 42 | -5.2% | 2026-10-15 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |
| 5 | ASML | 52.2 | $1,784.87 | -1.7% | 47 | -4.4% | 2026-10-14 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | below 20-day trend |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | SPY | 17.1% | $750.72 | -0.5% | 63 | 17.1% portfolio weight |
| 2 | AAPL | 4.6% | $333.26 | +1.8% | 90 | RSI elevated at 90; 20D move +12.6%; up +1.8% today |
| 3 | WM | 0.8% | $242.25 | +4.1% | 71 | RSI elevated at 71; 20D move +12.2%; up +4.1% today |
| 4 | SPGI | 0.5% | $457.38 | +2.9% | 84 | RSI elevated at 84; 20D move +15.7%; up +2.9% today |
| 5 | AVGO | 16.7% | $374.45 | -5.0% | 48 | 16.7% portfolio weight |

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
Altamira Trade Ideas - 2026-07-17
Market: SPY -0.5% | QQQ -1.6% | VIX 18.44 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: COST near $945.57; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: already approved portfolio name; price above 20-day trend; RSI balanced at 51
   Risk: chasing after +3.2% day

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
