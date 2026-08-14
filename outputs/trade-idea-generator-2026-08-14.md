# Trade Idea Generator - 2026-08-14

Generated: 2026-08-14T14:09:05.066495+00:00

## Executive Summary

- **Market regime:** VIX 14.58 (LOW); Premium is lean; sell smaller or favor covered calls.
- **Sizing:** Use 75% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | LRCX | 70.3 | $336.50 | -0.2% | 63 | +9.7% | 2026-10-21 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | V | 70.0 | $364.54 | -0.2% | 53 | +1.1% | 2026-10-27 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 3 | TSM | 69.0 | $428.30 | -0.5% | 65 | +6.5% | 2026-10-15 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 4 | LLY | 68.2 | $1,183.05 | -2.1% | 47 | +3.2% | 2026-10-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 5 | GOOGL | 66.0 | $347.76 | +0.4% | 60 | -1.2% | 2026-10-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | SPY | 17.1% | $778.58 | +0.1% | 77 | 17.1% portfolio weight; RSI elevated at 77 |
| 2 | AVGO | 16.7% | $400.57 | -4.1% | 59 | 16.7% portfolio weight |
| 3 | MSFT | 6.7% | $498.05 | +0.2% | 86 | RSI elevated at 86; 20D move +23.8% |
| 4 | NOW | 0.5% | $123.16 | -3.2% | 71 | RSI elevated at 71; 20D move +17.6% |
| 5 | NFLX | 0.0% | $78.03 | -0.3% | 74 | RSI elevated at 74; 20D move +15.4% |

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
Altamira Trade Ideas - 2026-08-14
Market: SPY +0.1% | QQQ +0.2% | VIX 14.58 (LOW)
Sizing: 75% of standard premium-selling size. Premium is lean; sell smaller or favor covered calls.

1) CSP watch: LRCX near $336.50; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 67.4 (B); price above 20-day trend; RSI balanced at 63

2) Covered-call/trim watch: SPY at 17.1% weight.
   Rationale: 17.1% portfolio weight; RSI elevated at 77

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
