# Trade Idea Generator — Portfolio + Watchlist

**Report date:** 2026-04-28  
**Run time context:** 10:00 UTC cron run; live FMP quotes and Massive options snapshots  
**Universe:** Current portfolio holdings plus top/consider watchlist names from `context/portfolio-details.md` and `context/watchlist.md`  
**Market regime:** VIX 18.38 — NORMAL

---

## Executive Summary

**Primary recommendation: risk-gated income management, not new naked put expansion.**

The active short-premium book that is still live after 2026-04-28 is approximately **$950,000 notional** against the portfolio snapshot value of **$1,207,271** (**78.7% notional exposure**). That is above the 30% options allocation guardrail in the workspace risk framework, so the highest-quality trade ideas today are:

1. **Harvest winners in existing short puts** where 50%+ of max profit is available.
2. **Use covered calls on overweight equity positions** to monetize upside without adding downside notional.
3. **If adding exposure, prefer defined-risk put spreads** in top watchlist names with no earnings before expiration.
4. **Avoid opening fresh premium through imminent earnings** in AAPL, MSFT, GOOGL, AMZN, ABBV, GD, and V.

---

## Top Actions

| Rank | Action | Ticker | Contract / Structure | Credit / Debit | Risk Note |
|---:|---|---|---|---:|---|
| 1 | **Close / harvest** | SPY | Buy to close 2026-05-15 620P | ~$0.33 ask | ~95% of original credit captured; reduces $310k notional. |
| 2 | **Close / harvest** | COST | Buy to close 2026-05-15 900P | ~$1.61 ask | ~85% of original credit captured; reduces $450k notional. |
| 3 | **Covered call candidate** | AVGO | Sell 2026-05-29 460C against shares | ~$8.45 bid | 0.25 delta; ~10.0% upside room; expiry before 2026-06-03 earnings. |
| 4 | **Defined-risk watchlist idea** | LRCX | Sell 2026-05-22 235P / buy 230P | ~$0.90 credit | Max loss ~$4.10; short strike ~9.4% OTM; earnings after expiry. |
| 5 | **Watchlist only** | TSM | 2026-05-22 375P CSP candidate | ~$7.80 bid | Attractive premium, but do not add naked put notional until risk is reduced. |

---

## Existing Short-Premium Book

Expired March positions from `context/options-positions.md` were excluded. Still-live positions:

| Ticker | Position | Spot | Current Ask | Original Credit | Credit Remaining | Est. P/L if Closed | Action |
|---|---:|---:|---:|---:|---:|---:|---|
| SPY | 5x 2026-05-15 620P | $715.17 | $0.33 | $6.92 | 4.8% | +$3,295 | **BTC / harvest** |
| COST | 5x 2026-05-15 900P | $998.01 | $1.61 | $11.00 | 14.6% | +$4,695 | **BTC / harvest** |
| MSFT | 5x 2026-05-15 380P | $424.82 | $3.30 | $10.12 | 32.6% | +$3,410 | Hold or set BTC near 50% max profit |

**Risk impact:** Closing SPY and COST would reduce active short-put notional by about **$760,000**, leaving the MSFT 380P position as the primary live short-put exposure.

---

## Covered Call Candidates on Current Holdings

Covered calls are preferred over new naked CSPs while options notional is above target.

| Ticker | Holding Weight | Spot | Candidate | Bid / Ask | Delta | OI / Vol | Upside to Strike | Earnings |
|---|---:|---:|---|---:|---:|---:|---:|---|
| AVGO | 16.7% | $418.20 | 2026-05-29 460C | $8.45 / $9.55 | 0.25 | 222 / 4 | 10.0% | 2026-06-03 |
| AVGO | 16.7% | $418.20 | 2026-05-29 450C | $10.60 / $12.00 | 0.29 | 286 / 37 | 7.6% | 2026-06-03 |
| AMAT | 12.6% | $404.86 | 2026-05-29 470C | $9.20 / $10.10 | 0.23 | 158 / 151 | 16.1% | 2026-05-14 |
| MSFT | 6.7% | $424.82 | 2026-05-29 460C | $7.75 / $7.90 | 0.27 | 12,256 / 731 | 8.3% | 2026-04-29 |

**Preferred covered call:** AVGO 2026-05-29 460C. It monetizes an overweight winner, gives roughly 10% upside room, and expires before the listed earnings date.  
**Avoid for now:** MSFT and AMAT calls until after their near-term earnings unless the intent is explicitly to cap upside through the event.

---

## Defined-Risk Watchlist Ideas

Only consider these after harvesting existing put exposure or if position size is intentionally tiny.

| Ticker | Structure | Spot | Credit | Max Loss | DTE | Short Delta | Short Strike OTM | Liquidity |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| LRCX | Sell 2026-05-22 235P / buy 230P | $259.47 | $0.90 | $4.10 | 24 | -0.28 | 9.4% | 6/10 |
| ADBE | Sell 2026-05-22 225P / buy 220P | $239.31 | $1.05 | $3.95 | 24 | -0.27 | 6.0% | 3/10 |
| NVDA | Sell 2026-05-29 200P / buy 195P | $216.61 | $1.05 | $3.95 | 31 | -0.28 | 7.7% | 10/10 |

**Best defined-risk candidate:** LRCX 235/230P expiring 2026-05-22. LRCX is a top watchlist candidate, the spread is below spot by ~9.4%, and earnings are listed after expiration.  
**Caution:** NVDA has strong liquidity but earnings are listed for 2026-05-20, before the 2026-05-29 expiry, so it is not a clean pre-earnings-neutral premium sale.

---

## Naked CSP Watchlist Candidates

These are attractive on premium metrics but **not recommended as immediate opens** while active short-put notional remains above target.

| Ticker | Contract | Spot | Bid / Ask | Delta | DTE | OTM | Annualized Premium | Earnings |
|---|---|---:|---:|---:|---:|---:|---:|---|
| LRCX | 2026-05-22 235P | $259.47 | $7.65 / $8.25 | -0.28 | 24 | 9.4% | 49.5% | 2026-07-29 |
| TSM | 2026-05-22 375P | $404.98 | $7.80 / $8.55 | -0.29 | 24 | 7.4% | 31.6% | 2026-07-16 |
| NVDA | 2026-05-22 200P | $216.61 | $4.15 / $4.30 | -0.27 | 24 | 7.7% | 31.6% | 2026-05-20 |

---

## Earnings Risk Filter

Avoid new short premium through the following near-term earnings windows unless the trade is explicitly structured as an earnings trade with defined risk:

- **V:** 2026-04-28
- **GD:** 2026-04-28
- **MSFT:** 2026-04-29
- **GOOGL:** 2026-04-29
- **AMZN:** 2026-04-29
- **ABBV:** 2026-04-29
- **AAPL:** 2026-04-30
- **AMAT:** 2026-05-14
- **NVDA:** 2026-05-20
- **COST:** 2026-05-28

---

## Telegram Summary Sent

Telegram summary prepared for chat ID configured in `outputs/csp-daily-scan-fixed.json` (`7830722515`).

---

## Data and Disclaimers

- **Data:** FMP quotes and earnings dates; Massive options snapshots for bid/ask, Greeks, volume, and open interest.
- **Portfolio source:** `context/portfolio-details.md`; watchlist source: `context/watchlist.md`; options positions source: `context/options-positions.md`.
- **Risk framework:** Altamira 30% options allocation target and 50% profit-taking discipline.
- **Disclaimer:** This is for research and workflow automation only. It is not investment advice or a recommendation to trade. Verify live quotes, liquidity, assignment risk, earnings dates, and portfolio constraints before order entry.
