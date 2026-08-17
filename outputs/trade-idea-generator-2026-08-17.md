# Trade Idea Generator - 2026-08-17

Generated: 2026-08-17T10:01:55.774076+00:00

## Executive Summary

- **Market regime:** VIX 14.96 (LOW); Premium is lean; sell smaller or favor covered calls.
- **Sizing:** Use 75% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | LRCX | 70.3 | $332.36 | -1.4% | 62 | +8.3% | 2026-10-21 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | V | 70.0 | $364.15 | -0.4% | 52 | +1.0% | 2026-10-27 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 3 | TSM | 69.0 | $426.35 | -1.0% | 65 | +6.0% | 2026-10-15 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 4 | KLAC | 67.8 | $203.72 | -2.7% | 50 | -1.9% | 2026-10-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 5 | AMZN | 64.0 | $262.65 | -0.9% | 66 | +5.1% | 2026-10-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | SPY | 17.1% | $776.34 | -0.2% | 75 | 17.1% portfolio weight; RSI elevated at 75 |
| 2 | AVGO | 16.7% | $392.99 | -5.9% | 54 | 16.7% portfolio weight |
| 3 | MSFT | 6.7% | $495.40 | -0.3% | 85 | RSI elevated at 85; 20D move +23.1% |
| 4 | NOW | 0.5% | $124.00 | -2.6% | 71 | RSI elevated at 71; 20D move +18.4% |
| 5 | NFLX | 0.0% | $78.16 | -0.1% | 73 | RSI elevated at 73; 20D move +15.6% |

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
Altamira Trade Ideas - 2026-08-17
Market: SPY -0.2% | QQQ -0.1% | VIX 14.96 (LOW)
Sizing: 75% of standard premium-selling size. Premium is lean; sell smaller or favor covered calls.

1) CSP watch: LRCX near $332.36; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 67.4 (B); price above 20-day trend; RSI balanced at 62

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
