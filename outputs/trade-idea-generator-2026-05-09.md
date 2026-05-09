# Trade Idea Generator — 2026-05-09

Source: repository snapshots in `context/portfolio-details.md`, `context/options-positions.md`, and `context/watchlist.md`.

> Execution note: this is a repo-snapshot idea memo, not a broker order ticket. Verify live quotes, option chains, earnings dates, liquidity, and account buying power before trading.

## Portfolio Snapshot

- Positions parsed: 20
- Approximate equity market value parsed: $1,207,271
- Watchlist entries parsed: 26
- Short-premium rows parsed: 5

### Top Weights

| Symbol | Weight | Current | P&L | Day Change |
| --- | ---: | ---: | ---: | ---: |
| SPY | 17.1% | $686.29 | +43.3% | +0.5% |
| AVGO | 16.7% | $333.51 | +175.4% | +0.3% |
| GOOGL | 13.8% | $303.33 | +74.0% | +0.4% |
| AMAT | 12.6% | $369.30 | +100.5% | +2.8% |
| MSFT | 6.7% | $399.60 | +21.7% | +0.7% |
| AMZN | 4.9% | $204.79 | +80.7% | +1.8% |
| AAPL | 4.6% | $264.35 | +45.6% | +0.2% |
| CRWD | 4.3% | $415.76 | +17.1% | +0.4% |

### Sector / Factor Concentration

- Mega-cap tech: 30.0% - concentration flag
- Semiconductors: 29.3% - concentration flag
- Index ETF: 17.8%
- Software: 4.8%
- Consumer staples: 4.1%
- Healthcare: 3.8%
- Industrials: 3.0%
- Other: 3.0%

## Top Trade Ideas

### 1) Risk-first portfolio overlay: write calls or trim concentrated winners

- Concentrated positions above 10% weight: SPY (17.1%), AVGO (16.7%), GOOGL (13.8%), AMAT (12.6%).
- Idea: for holdings you are willing to reduce, sell 30-45 DTE covered calls around 0.20 delta, or place staged trims back toward the target weight.
- Priority: AVGO, GOOGL, AMAT, and SPY because they dominate portfolio risk. Avoid adding new semiconductor beta until the concentration is intentionally accepted.
- Risk control: do not overwrite shares needed for long-term tax/conviction reasons; use limit orders and only sell calls at strikes where assignment is acceptable.

### 2) Manage near-term short premium before adding new risk

| Ticker | Contract | Status | Action Bias |
| --- | --- | --- | --- |
| MSFT | 2026-03-20 430P x5 | Expired 50 days ago; reconcile broker status before acting. | Reconcile/close stale row |
| AVGO | 2026-03-20 310P x5 | Expired 50 days ago; reconcile broker status before acting. | Reconcile/close stale row |
| MSFT | 2026-05-15 380P x5 | 6 DTE, OTM but within monitoring range, distance 4.9%, mark P/L about $-840. | Monitor daily; close/roll if strike test or target profit |
| SPY | 2026-05-15 620P x5 | 6 DTE, comfortably OTM, distance 9.7%, mark P/L about $-1,620. | Monitor daily; close/roll if strike test or target profit |
| COST | 2026-05-15 900P x5 | 6 DTE, comfortably OTM, distance 9.6%, mark P/L about $-700. | Monitor daily; close/roll if strike test or target profit |

### 3) New watchlist entries: use defined-risk entries first

| Rank | Ticker | Score | Grade | Status | Suggested Setup |
| ---: | --- | ---: | --- | --- | --- |
| 1 | LRCX | 67.4 | B | Top Candidate | Defined-risk bull put spread only unless semiconductor exposure is reduced |
| 2 | NVDA | 66.2 | B | Top Candidate | Defined-risk bull put spread only unless semiconductor exposure is reduced |
| 3 | TSM | 61.8 | B- | Top Candidate | Defined-risk bull put spread only unless semiconductor exposure is reduced |
| 4 | KLAC | 61.3 | B- | Top Candidate | Defined-risk bull put spread only unless semiconductor exposure is reduced |
| 5 | ADBE | 60.1 | B- | Top Candidate | 30-45 DTE bull put spread or 0.20-0.25 delta CSP after earnings check |

### 4) No-trade / avoid list

- Keep out of the trade queue until re-scored or a thesis changes: TSLA (F), CMG (F).
- Unscored names need a fresh `/stockscore` before new capital: INTU.

## Execution Checklist

- Confirm market is open and use live bid/ask quotes.
- Check earnings dates before any 30-45 DTE option sale.
- Respect the risk framework: position size, sector concentration, options allocation, and cash reserve.
- Prefer defined-risk spreads when VIX is elevated or when adding exposure to already concentrated sectors.
- This output is educational and operational planning support, not individualized financial advice.
