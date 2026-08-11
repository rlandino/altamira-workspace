# Trade Idea Generator - 2026-08-11

Generated: 2026-08-11T10:02:20.244722+00:00

## Executive Summary

- **Market regime:** VIX 15.52 (NORMAL); Standard CSP/spread sizing is acceptable.
- **Sizing:** Use 100% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | GOOGL | 66.0 | $357.52 | +0.9% | 54 | -0.6% | 2026-10-28 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | TSM | 65.0 | $418.47 | -0.4% | 47 | -0.5% | 2026-10-15 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 3 | ASML | 64.2 | $1,733.48 | -0.4% | 44 | -2.4% | 2026-10-14 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 4 | LLY | 64.2 | $1,231.58 | +3.9% | 59 | +6.9% | 2026-10-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | chasing after +3.9% day |
| 5 | NVDA | 61.0 | $217.55 | -2.9% | 57 | +2.7% | 2026-08-26 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | earnings in 15 days (2026-08-26) |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | SPY | 17.1% | $773.03 | -0.0% | 67 | 17.1% portfolio weight |
| 2 | NOW | 0.5% | $127.44 | +2.0% | 72 | RSI elevated at 72; 20D move +21.5%; up +2.0% today |
| 3 | AVGO | 16.7% | $422.40 | -1.3% | 68 | 16.7% portfolio weight |
| 4 | MSFT | 6.7% | $506.06 | +1.2% | 85 | RSI elevated at 85; 20D move +31.5% |
| 5 | GOOGL | 13.8% | $357.52 | +0.9% | 54 | 13.8% portfolio weight |

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
Altamira Trade Ideas - 2026-08-11
Market: SPY -0.0% | QQQ -0.3% | VIX 15.52 (NORMAL)
Sizing: 100% of standard premium-selling size. Standard CSP/spread sizing is acceptable.

1) CSP watch: GOOGL near $357.52; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: already approved portfolio name; price above 20-day trend; RSI balanced at 54

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
