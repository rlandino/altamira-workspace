# Trade Idea Generator - 2026-08-13

Generated: 2026-08-13T14:16:37.570534+00:00

## Executive Summary

- **Market regime:** VIX 14.77 (LOW); Premium is lean; sell smaller or favor covered calls.
- **Sizing:** Use 75% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | LRCX | 70.3 | $331.12 | +1.5% | 57 | +5.7% | 2026-10-21 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | ASML | 68.2 | $1,852.60 | +2.3% | 57 | +6.0% | 2026-10-14 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 3 | LLY | 68.2 | $1,219.16 | -0.1% | 54 | +3.4% | 2026-10-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 4 | GOOGL | 66.0 | $346.53 | +0.9% | 62 | -0.1% | 2026-10-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 5 | KLAC | 64.8 | $209.72 | +0.7% | 49 | -1.4% | 2026-10-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AVGO | 16.7% | $423.33 | +1.7% | 73 | 16.7% portfolio weight; RSI elevated at 73; 20D move +14.2%; up +1.7% today |
| 2 | SPY | 17.1% | $778.29 | +0.8% | 77 | 17.1% portfolio weight; RSI elevated at 77 |
| 3 | NFLX | 0.0% | $77.28 | +4.1% | 72 | RSI elevated at 72; 20D move +12.1%; up +4.1% today |
| 4 | MSFT | 6.7% | $499.73 | +1.5% | 87 | RSI elevated at 87; 20D move +26.9% |
| 5 | NOW | 0.5% | $125.27 | +0.3% | 80 | RSI elevated at 80; 20D move +21.3% |

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
Market: SPY +0.8% | QQQ +1.2% | VIX 14.77 (LOW)
Sizing: 75% of standard premium-selling size. Premium is lean; sell smaller or favor covered calls.

1) CSP watch: LRCX near $331.12; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: watchlist score 67.4 (B); price above 20-day trend; RSI balanced at 57

2) Covered-call/trim watch: AVGO at 16.7% weight.
   Rationale: 16.7% portfolio weight; RSI elevated at 73; 20D move +14.2%

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
