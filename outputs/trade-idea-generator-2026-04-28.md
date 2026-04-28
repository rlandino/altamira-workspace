# Trade Idea Generator — 2026-04-28

> Informational only; not investment advice. Validate prices, earnings dates, options chains, and liquidity before trading.

## Portfolio Context

- Portfolio value: $1,207,271
- Cash: 22.5%
- VIX / regime: UNKNOWN (no live VIX; using repo context)
- Data source: repo context only (FMP_API_KEY not set)

## Top Trade Ideas

| Rank | Ticker | Source | Action | Setup | Price | Live Day Chg | Risk Note |
|------|--------|--------|--------|-------|-------|--------------|-----------|
| 1 | LRCX | watchlist | CSP / starter-position candidate | B watchlist grade, 67.4 score, Top Candidate | N/A | N/A | Use defined risk or small CSP sizing until earnings date and option liquidity are checked. |
| 2 | NVDA | watchlist | CSP / starter-position candidate | B watchlist grade, 66.2 score, Top Candidate | N/A | N/A | Use defined risk or small CSP sizing until earnings date and option liquidity are checked. |
| 3 | TSM | watchlist | CSP / starter-position candidate | B- watchlist grade, 61.8 score, Top Candidate | N/A | N/A | Use defined risk or small CSP sizing until earnings date and option liquidity are checked. |
| 4 | KLAC | watchlist | CSP / starter-position candidate | B- watchlist grade, 61.3 score, Top Candidate | N/A | N/A | Use defined risk or small CSP sizing until earnings date and option liquidity are checked. |
| 5 | ADBE | watchlist | CSP / starter-position candidate | B- watchlist grade, 60.1 score, Top Candidate | N/A | N/A | Use defined risk or small CSP sizing until earnings date and option liquidity are checked. |
| 6 | MSFT | open-options | Manage 2026-05-15 380P | Credit $10.12, current $11.80, 5 contracts: under pressure | N/A | N/A | Close/roll per playbook if loss approaches 2x credit or short strike is threatened. |
| 7 | SPY | open-options | Manage 2026-05-15 620P | Credit $6.92, current $10.16, 5 contracts: under pressure | N/A | N/A | Close/roll per playbook if loss approaches 2x credit or short strike is threatened. |
| 8 | COST | open-options | Manage 2026-05-15 900P | Credit $11.00, current $12.40, 5 contracts: under pressure | N/A | N/A | Close/roll per playbook if loss approaches 2x credit or short strike is threatened. |
| 9 | AVGO | portfolio | concentration-management | 16.7% weight, +175.4% P&L, +0.3% day change from repo snapshot | $333.51 | N/A | Respect 5% new-risk cap and avoid adding to already concentrated names. |
| 10 | SPY | portfolio | concentration-management | 17.1% weight, +43.3% P&L, +0.5% day change from repo snapshot | $686.29 | N/A | Respect 5% new-risk cap and avoid adding to already concentrated names. |

## Concentration Dashboard

| Ticker | Weight | Snapshot Day Chg | P&L | Overlay Bias |
|--------|--------|------------------|-----|--------------|
| SPY | 17.1% | +0.5% | +43.3% | concentration-management |
| AVGO | 16.7% | +0.3% | +175.4% | concentration-management |
| GOOGL | 13.8% | +0.4% | +74.0% | concentration-management |
| AMAT | 12.6% | +2.8% | +100.5% | concentration-management |
| MSFT | 6.7% | +0.7% | +21.7% | hold / income overlay |

## Watchlist Focus

- **LRCX** (B, 67.4) — Lam Research Corporation; Top Candidate
- **NVDA** (B, 66.2) — NVIDIA Corporation; Top Candidate
- **TSM** (B-, 61.8) — Taiwan Semiconductor Manufacturing Company; Top Candidate
- **KLAC** (B-, 61.3) — KLA Corporation; Top Candidate
- **ADBE** (B-, 60.1) — Adobe Inc.; Top Candidate
- **ASML** (C+, 58.9) — ASML Holding N.V.; Consider
- **LLY** (C+, 58.7) — Eli Lilly and Company; Consider
- **ACN** (C+, 56.3) — Accenture plc; Consider

## Open Options Notes

- **MSFT 2026-05-15 380P**: credit $10.12, current $11.80, 5 contracts (under pressure).
- **SPY 2026-05-15 620P**: credit $6.92, current $10.16, 5 contracts (under pressure).
- **COST 2026-05-15 900P**: credit $11.00, current $12.40, 5 contracts (under pressure).

### Reconciliation Flags
- MSFT 2026-03-20 430P is past expiration in context; reconcile before acting.
- AVGO 2026-03-20 310P is past expiration in context; reconcile before acting.

## Execution Guardrails

- Validate live chain, bid/ask spread, open interest, and earnings timing before placing any order.
- Keep any single new risk allocation under 5% of portfolio value and total options exposure under 30%.
- Prefer defined-risk spreads if VIX is elevated or if the underlying is near earnings.
