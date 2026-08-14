# Trade Idea Generator - 2026-08-14

Generated: 2026-08-14T10:19:20.481580+00:00

## Executive Summary

- **Market regime:** VIX 14.57 (LOW); Premium is lean; sell smaller or favor covered calls.
- **Sizing:** Use 75% of normal premium-selling size based on the VIX regime.
- **Universe:** 20 portfolio holdings, 26 watchlist names, 0 active short-premium positions.

## Top Cash-Secured Put / Put-Spread Ideas

| Rank | Ticker | Score | Price | 1D | RSI | 20D | Earnings | Suggested Action | Key Risks |
|---:|---|---:|---:|---:|---:|---:|---|---|---|
| 1 | V | 70.0 | $365.45 | +1.7% | 61 | +1.9% | 2026-10-27 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 2 | TSM | 69.0 | $430.49 | +0.3% | 64 | +8.1% | 2026-10-15 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 3 | ASML | 68.2 | $1,847.90 | +2.1% | 57 | +5.7% | 2026-10-14 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 4 | LLY | 68.2 | $1,209.85 | -0.9% | 52 | +2.6% | 2026-10-29 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | None flagged |
| 5 | LRCX | 66.3 | $337.01 | +3.3% | 59 | +7.6% | 2026-10-21 | Review 20-30 delta put or defined-risk put spread, 30-45 DTE | chasing after +3.3% day |

## Covered Call / Trim Watch

| Rank | Ticker | Weight | Price | 1D | RSI | Rationale |
|---:|---|---:|---:|---:|---:|---|
| 1 | AVGO | 16.7% | $417.82 | +0.4% | 71 | 16.7% portfolio weight; RSI elevated at 71; 20D move +12.7% |
| 2 | SPY | 17.1% | $777.88 | +0.7% | 77 | 17.1% portfolio weight; RSI elevated at 77 |
| 3 | NOW | 0.5% | $127.25 | +1.8% | 80 | RSI elevated at 80; 20D move +23.3%; up +1.8% today |
| 4 | NFLX | 0.0% | $78.24 | +5.4% | 74 | RSI elevated at 74; 20D move +13.5%; up +5.4% today |
| 5 | MSFT | 6.7% | $496.88 | +0.9% | 86 | RSI elevated at 86; 20D move +26.2% |

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
Market: SPY +0.7% | QQQ +1.2% | VIX 14.57 (LOW)
Sizing: 75% of standard premium-selling size. Premium is lean; sell smaller or favor covered calls.

1) CSP watch: V near $365.45; target 20-30 delta put, 30-45 DTE after chain check.
   Rationale: already approved portfolio name; price above 20-day trend; RSI balanced at 61

2) Covered-call/trim watch: AVGO at 16.7% weight.
   Rationale: 16.7% portfolio weight; RSI elevated at 71; 20D move +12.7%

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
