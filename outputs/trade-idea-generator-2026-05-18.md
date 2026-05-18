# Trade Idea Generator — Portfolio + Watchlist — 2026-05-18

> Scan output only. This is not financial advice or an order ticket. Verify live quotes, liquidity, earnings dates, and account risk before trading.

## Run Context

- Portfolio source: `context/portfolio-details.md` (20 holdings; total market value $1,207,271).
- Watchlist source: `context/watchlist.md` (26 tickers).
- Options source: Massive.com snapshot API for expirations 2026-06-07 to 2026-07-17.
- Quote/earnings source: FMP API.
- VIX: 18.97 (NORMAL); sizing adjustment: 100%.
- Regime guidance: Standard CSP/covered-call sizing is acceptable.

## Context Hygiene Flag

- `context/options-positions.md` contains 5 short-premium rows whose expirations are before 2026-05-18. They were not treated as active positions.
- Refresh broker/options context before issuing management instructions for existing short premium.

## Top CSP / Put-Sale Candidates

| Rank | Ticker | Source | Exp | DTE | Strike | Bid | Delta | Ann. ROC | Breakeven | POP Proxy | Liq | Suggested Size | Collateral |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | LRCX | Watchlist | 2026-06-18 | 31 | $270.00 | $14.25 | -0.31 | 62.1% | $255.75 | 68.6% | 10/10 | 2 | $54,000 |
| 2 | LRCX | Watchlist | 2026-06-12 | 25 | $275.00 | $14.55 | -0.34 | 77.2% | $260.45 | 65.9% | 4/10 | 2 | $55,000 |
| 3 | NOW | Holding | 2026-06-18 | 31 | $92.00 | $4.80 | -0.33 | 61.4% | $87.20 | 66.6% | 9/10 | 6 | $55,200 |
| 4 | LRCX | Watchlist | 2026-06-12 | 25 | $270.00 | $12.45 | -0.31 | 67.3% | $257.55 | 69.2% | 4/10 | 2 | $54,000 |
| 5 | NOW | Holding | 2026-06-18 | 31 | $90.00 | $4.00 | -0.30 | 52.3% | $86.00 | 70.5% | 10/10 | 6 | $54,000 |

## Top Covered-Call Candidates

| Rank | Ticker | Exp | DTE | Strike | Bid | Delta | Upside to Strike | Ann. Premium Yield | Max Contracts | Premium | Liq |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | AMAT | 2026-06-18 | 31 | $480.00 | $13.10 | +0.31 | 9.9% | 35.3% | 4 | $5,240 | 6/10 |
| 2 | AMAT | 2026-06-18 | 31 | $490.00 | $10.80 | +0.27 | 12.2% | 29.1% | 4 | $4,320 | 7/10 |
| 3 | GOOGL | 2026-06-18 | 31 | $415.00 | $8.25 | +0.34 | 4.6% | 24.5% | 5 | $4,125 | 9/10 |
| 4 | GOOGL | 2026-06-18 | 31 | $420.00 | $7.10 | +0.30 | 5.9% | 21.1% | 5 | $3,550 | 10/10 |
| 5 | AMZN | 2026-06-18 | 31 | $275.00 | $5.10 | +0.33 | 4.1% | 22.7% | 2 | $1,020 | 10/10 |

## Earnings Exclusions Within Scan Window

| Ticker | Earnings Date | Note |
|---|---:|---|
| ABT | 2026-07-16 | Excluded when earnings fell before candidate expiration. |
| ACN | 2026-06-18 | Excluded when earnings fell before candidate expiration. |
| ADBE | 2026-06-11 | Excluded when earnings fell before candidate expiration. |
| ADSK | 2026-05-28 | Excluded when earnings fell before candidate expiration. |
| ASML | 2026-07-15 | Excluded when earnings fell before candidate expiration. |
| AVGO | 2026-06-03 | Excluded when earnings fell before candidate expiration. |
| COST | 2026-05-28 | Excluded when earnings fell before candidate expiration. |
| CRM | 2026-05-27 | Excluded when earnings fell before candidate expiration. |
| CRWD | 2026-06-03 | Excluded when earnings fell before candidate expiration. |
| INTU | 2026-05-20 | Excluded when earnings fell before candidate expiration. |
| JPM | 2026-07-14 | Excluded when earnings fell before candidate expiration. |
| KMI | 2026-07-15 | Excluded when earnings fell before candidate expiration. |
| MRVL | 2026-05-27 | Excluded when earnings fell before candidate expiration. |
| NFLX | 2026-07-16 | Excluded when earnings fell before candidate expiration. |
| NVDA | 2026-05-20 | Excluded when earnings fell before candidate expiration. |
| PANW | 2026-06-02 | Excluded when earnings fell before candidate expiration. |
| TSM | 2026-07-16 | Excluded when earnings fell before candidate expiration. |

## Existing Short-Premium Rows From Repo

| Ticker | Exp | Strike | Type | Credit | Current | Contracts | Status |
|---|---:|---:|---|---:|---:|---:|---|
| MSFT | 2026-03-20 | $430.00 | Put | $8.70 | $22.40 | 5 | Expired/stale in repo context |
| MSFT | 2026-05-15 | $380.00 | Put | $10.12 | $11.80 | 5 | Expired/stale in repo context |
| AVGO | 2026-03-20 | $310.00 | Put | $12.60 | $5.00 | 5 | Expired/stale in repo context |
| SPY | 2026-05-15 | $620.00 | Put | $6.92 | $10.16 | 5 | Expired/stale in repo context |
| COST | 2026-05-15 | $900.00 | Put | $11.00 | $12.40 | 5 | Expired/stale in repo context |

## Telegram Message Sent

```text
ALTAMIRA TRADE IDEAS - 2026-05-18
Universe: 20 portfolio holdings + 26 watchlist tickers (45 optionable scanned)
VIX: 19.0 (NORMAL) | Sizing: 100%

Context flag: repo options-positions are expired as of today; refresh broker context before managing legacy shorts.

Top CSP / put-sale candidates:
1) LRCX 2026-06-18 270P bid $14.25, delta -0.31, ROC ann 62.1%, BE $255.75, size 2x, liq 10/10
2) LRCX 2026-06-12 275P bid $14.55, delta -0.34, ROC ann 77.2%, BE $260.45, size 2x, liq 4/10
3) NOW 2026-06-18 92P bid $4.80, delta -0.33, ROC ann 61.4%, BE $87.20, size 6x, liq 9/10

Top covered-call candidates:
1) AMAT 2026-06-18 480C bid $13.10, delta +0.31, upside 9.9%, prem $5,240, liq 6/10
2) AMAT 2026-06-18 490C bid $10.80, delta +0.27, upside 12.2%, prem $4,320, liq 7/10
3) GOOGL 2026-06-18 415C bid $8.25, delta +0.34, upside 4.6%, prem $4,125, liq 9/10

Action: treat as scan ideas, not orders. Confirm chain quotes, earnings dates, and portfolio risk before entry.
```

## Method Notes

- CSP filters: 20–60 DTE, roughly 0.15–0.35 delta puts, bid > 0, OI >= 50, spread <= 20%, no earnings before expiration.
- Covered-call filters: held shares >= 100, 20–60 DTE, roughly 0.15–0.35 delta calls, strike above current price and cost basis buffer, bid > 0, OI >= 50, spread <= 20%, no earnings before expiration.
- Suggested CSP contracts cap gross collateral near 5% of portfolio value after VIX sizing adjustment.
