# Trade Idea Generator - 2026-08-13

Generated: 2026-08-13T10:13:29.413294+00:00

## Executive Summary

- **Market regime:** VIX 14.65 (LOW); Premium is lean; sell smaller or favor covered calls.
- **Sizing:** Use 75% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | TSM | 69.0 | $429.15 | +1.7% | 56 | +4.7% | 2026-10-15 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | ASML | 68.2 | $1,810.07 | +0.6% | 51 | +1.4% | 2026-10-14 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 3 | LLY | 68.2 | $1,220.51 | +0.5% | 56 | +4.4% | 2026-10-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 4 | LRCX | 66.3 | $326.11 | +4.7% | 52 | +1.6% | 2026-10-21 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | chasing after +4.7% day |
| 5 | AMZN | 64.0 | $267.28 | -1.8% | 68 | +7.0% | 2026-10-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | SPY | 17.1% | $772.49 | +0.3% | 75 | 17.1% portfolio weight; RSI elevated at 75 |
| 2 | AVGO | 16.7% | $416.05 | -0.0% | 63 | 16.7% portfolio weight |
| 3 | AMAT | 12.6% | $548.15 | +4.3% | 48 | 12.6% portfolio weight; up +4.3% today |
| 4 | MSFT | 6.7% | $492.43 | -2.3% | 86 | RSI elevated at 86; 20D move +22.8% |
| 5 | NOW | 0.5% | $124.94 | -2.0% | 82 | RSI elevated at 82; 20D move +20.1% |

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
Altamira Trade Ideas - 2026-08-13
Market: SPY +0.3% | QQQ +0.7% | VIX 14.65 (LOW)
Sizing: 75% of standard premium-selling size. Premium is lean; sell smaller or favor covered calls.

1) CSP watch: TSM near $429.15; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 61.8 (B-); price above 20-day trend; RSI balanced at 56

2) Covered-call/trim watch: SPY at 17.1% weight.
   Rationale: 17.1% portfolio weight; RSI elevated at 75

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
