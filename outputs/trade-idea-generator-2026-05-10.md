# Trade Idea Generator - 2026-05-10

Repository-based scan of the current Altamira portfolio and watchlist.

## Source Files

- Portfolio: `context/portfolio-details.md`
- Watchlist: `context/watchlist.md`
- Market data: static repository snapshot; no live quote API was required for this run.

## Portfolio Snapshot

- Total market value: **$1,207,271**
- Equity/fund positions parsed: **20**
- Short-premium positions parsed: **5**
- Single-position guardrail: **5.0%** strict / **10.0%** tactical
- Sector guardrail: **25.0%**

| Symbol | Weight | Market Value | Sector/Theme |
| --- | --- | --- | --- |
| SPY | 17.1% | $205,887 | ETF |
| AVGO | 16.7% | $202,107 | Semiconductors |
| GOOGL | 13.8% | $167,135 | Communication Services |
| AMAT | 12.6% | $152,521 | Semiconductors |
| MSFT | 6.7% | $80,320 | Software |
| AMZN | 4.9% | $58,980 | Consumer Discretionary |
| AAPL | 4.6% | $56,042 | Technology |
| CRWD | 4.3% | $52,386 | Software |
| COST | 4.1% | $49,804 | Consumer Staples |
| ABBV | 3.8% | $46,201 | Health Care |

## Sector / Theme Exposure

| Sector/Theme | Weight | Limit Check |
| --- | --- | --- |
| Semiconductors | 29.3% | BREACH |
| ETF | 17.8% | OK |
| Communication Services | 13.8% | OK |
| Software | 11.5% | OK |
| Consumer Discretionary | 4.9% | OK |
| Technology | 4.6% | OK |
| Consumer Staples | 4.1% | OK |
| Health Care | 3.8% | OK |
| Industrials | 3.0% | OK |
| Financials | 2.6% | OK |
| Financial Technology | 2.2% | OK |
| Energy | 1.8% | OK |
| Fund | 0.7% | OK |

## Ranked Trade Ideas

| Priority | Idea | Action | Candidates | Risk Control |
| --- | --- | --- | --- | --- |
| 1 | Risk-down overweight winners | Trim, collar, or sell covered calls before adding new long exposure. | SPY 17.1%, AVGO 16.7%, GOOGL 13.8%, AMAT 12.6% | Do not add correlated tech/semi exposure until position weights are back inside the chosen cap. |
| 2 | Refresh stale options context | Refresh the portfolio export, then review any still-active short puts whose marks are above entry credit. | Expired rows: MSFT 430P 2026-03-20, AVGO 310P 2026-03-20; active marks to verify: MSFT 380P 2026-05-15 mark 11.80 vs 10.12 credit, SPY 620P 2026-05-15 mark 10.16 vs 6.92 credit, COST 900P 2026-05-15 mark 12.40 vs 11.00 credit | Refresh broker or Google Sheets context, then rerun options scans before entering or rolling premium trades. |
| 3 | Watchlist semiconductor entry only after risk budget is freed | Keep LRCX/NVDA/TSM/KLAC on the buy-list, but use starter sizing or cash-secured puts only after trimming existing semi winners. | LRCX 67.4 B, NVDA 66.2 B, TSM 61.8 B-, KLAC 61.3 B- | Cap semiconductor exposure near 25.0% unless explicitly overriding the sector limit. |
| 4 | Diversifying watchlist starter | Prefer a small starter or put-sale setup in the highest-scored non-semi candidate. | ADBE 60.1 B- | Starter size 1-2% until the name earns a higher conviction score and the portfolio has available risk budget. |
| 5 | Covered-call income on large share lots | For shares you are willing to trim, price 30-45 DTE calls around 0.20 delta instead of deploying new cash. | SPY 300 sh, AVGO 606 sh, GOOGL 551 sh, AMAT 413 sh, MSFT 201 sh, AMZN 288 sh, AAPL 212 sh, CRWD 126 sh | Only sell calls at strikes where assignment is acceptable; skip around earnings if the call caps desired upside. |

## Short-Premium Review

| Ticker | Contract | Credit | Current | Status |
| --- | --- | --- | --- | --- |
| MSFT | 430P 2026-03-20 | 8.70 | 22.40 | Expired/stale in repository |
| MSFT | 380P 2026-05-15 | 10.12 | 11.80 | Underwater - monitor |
| AVGO | 310P 2026-03-20 | 12.60 | 5.00 | Expired/stale in repository |
| SPY | 620P 2026-05-15 | 6.92 | 10.16 | Underwater - monitor |
| COST | 900P 2026-05-15 | 11.00 | 12.40 | Underwater - monitor |

## Watchlist Ranking

| Ticker | Score | Grade | Status | Theme |
| --- | --- | --- | --- | --- |
| LRCX | 67.4 | B | Top Candidate | Semiconductors |
| NVDA | 66.2 | B | Top Candidate | Semiconductors |
| TSM | 61.8 | B- | Top Candidate | Semiconductors |
| KLAC | 61.3 | B- | Top Candidate | Semiconductors |
| ADBE | 60.1 | B- | Top Candidate | Software |
| ASML | 58.9 | C+ | Consider | Semiconductors |
| LLY | 58.7 | C+ | Consider | Health Care |
| ACN | 56.3 | C+ | Consider | Information Technology |
| CRM | 50.7 | C | Monitor | Software |
| CDNS | 48.8 | C- | Monitor | Software |

## Avoid / Low Priority Flags

- TSLA (F, Avoid), CMG (F, Avoid)

## Execution Notes

- Treat these as idea-generation outputs, not trade orders.
- Confirm live prices, bid/ask spreads, earnings dates, and portfolio cash before placing trades.
- For options, verify the chain and follow the standing 50% profit / 200% credit stop framework.
- Financial calculations are based on static repository data and may be stale.

## Disclaimer

This report is for research and workflow automation only. It is not financial advice or a recommendation to buy, sell, or hold any security.
