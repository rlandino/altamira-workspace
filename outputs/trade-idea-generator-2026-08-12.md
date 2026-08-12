# Trade Idea Generator - 2026-08-12

Generated: 2026-08-12T14:07:13.233125+00:00

## Executive Summary

- **Market regime:** VIX 14.85 (LOW); Premium is lean; sell smaller or favor covered calls.
- **Sizing:** Use 75% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | TSM | 69.0 | $431.35 | +2.2% | 57 | +5.3% | 2026-10-15 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | ASML | 68.2 | $1,830.05 | +1.7% | 52 | +2.5% | 2026-10-14 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 3 | LLY | 68.2 | $1,205.11 | -0.8% | 53 | +3.1% | 2026-10-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 4 | LRCX | 66.3 | $327.08 | +5.0% | 52 | +1.9% | 2026-10-21 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | chasing after +5.0% day |
| 5 | AMZN | 64.0 | $269.83 | -0.9% | 71 | +8.0% | 2026-10-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | SPY | 17.1% | $772.29 | +0.2% | 75 | 17.1% portfolio weight; RSI elevated at 75 |
| 2 | AVGO | 16.7% | $421.73 | +1.4% | 65 | 16.7% portfolio weight; 20D move +12.6% |
| 3 | AMAT | 12.6% | $550.86 | +4.8% | 48 | 12.6% portfolio weight; up +4.8% today |
| 4 | MSFT | 6.7% | $493.66 | -2.0% | 86 | RSI elevated at 86; 20D move +23.1% |
| 5 | NOW | 0.5% | $122.54 | -3.9% | 78 | RSI elevated at 78; 20D move +17.8% |

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
Altamira Trade Ideas - 2026-08-12
Market: SPY +0.2% | QQQ +0.9% | VIX 14.85 (LOW)
Sizing: 75% of standard premium-selling size. Premium is lean; sell smaller or favor covered calls.

1) CSP watch: TSM near $431.35; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 61.8 (B-); price above 20-day trend; RSI balanced at 57

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
