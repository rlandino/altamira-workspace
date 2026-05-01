# Trade Idea Generator - 2026-05-01

> Automated scan of `context/portfolio-details.md` and `context/watchlist.md`.

## Dashboard

- Portfolio value: $1,207,271
- Positions scanned: 20 equities/funds; 5 option positions
- Watchlist candidates scanned: 26
- VIX: unavailable
- Market data: repository snapshot prices only

## Top Trade Ideas

### 1. AVGO - Income / risk trim

- **Source:** Portfolio
- **Setup:** Consider covered call near $350 expiring 2026-06-12
- **Reference price:** $333.51
- **Rank score:** 96.3
- **Rationale:**
  - 16.7% portfolio weight creates single-name concentration.
  - Unrealized gain is +175.4%; covered calls can harvest income without adding delta.
  - Existing short-premium exposure already exists; size any new call sale conservatively.
- **Risk:** Caps upside if the position keeps trending; avoid adding if earnings are inside the option window.
- **Management:** Target 50% premium capture; close or roll if delta moves above ~0.45.

### 2. AVGO - Concentration control

- **Source:** Portfolio
- **Setup:** Trim roughly 3.0% portfolio weight or pair with covered calls
- **Reference price:** $333.51
- **Rank score:** 91.3
- **Rationale:**
  - AVGO is 16.7% of portfolio versus a 5% single-position risk guideline.
  - Market value is approximately $202,107.
- **Risk:** Tax impact and opportunity cost if the leadership trend continues.
- **Management:** Reallocate proceeds to cash reserve, underweight sectors, or highest-grade watchlist names.

### 3. AMAT - Income / risk trim

- **Source:** Portfolio
- **Setup:** Consider covered call near $390 expiring 2026-06-12
- **Reference price:** $369.30
- **Rank score:** 82.8
- **Rationale:**
  - 12.6% portfolio weight creates single-name concentration.
  - Unrealized gain is +100.5%; covered calls can harvest income without adding delta.
- **Risk:** Caps upside if the position keeps trending; avoid adding if earnings are inside the option window.
- **Management:** Target 50% premium capture; close or roll if delta moves above ~0.45.

### 4. GOOGL - Income / risk trim

- **Source:** Portfolio
- **Setup:** Consider covered call near $320 expiring 2026-06-12
- **Reference price:** $303.33
- **Rank score:** 81.8
- **Rationale:**
  - 13.8% portfolio weight creates single-name concentration.
  - Unrealized gain is +74.0%; covered calls can harvest income without adding delta.
- **Risk:** Caps upside if the position keeps trending; avoid adding if earnings are inside the option window.
- **Management:** Target 50% premium capture; close or roll if delta moves above ~0.45.

### 5. AMAT - Concentration control

- **Source:** Portfolio
- **Setup:** Trim roughly 3.0% portfolio weight or pair with covered calls
- **Reference price:** $369.30
- **Rank score:** 81.0
- **Rationale:**
  - AMAT is 12.6% of portfolio versus a 5% single-position risk guideline.
  - Market value is approximately $152,521.
  - Today strength of +2.8% offers liquidity for a partial rebalance.
- **Risk:** Tax impact and opportunity cost if the leadership trend continues.
- **Management:** Reallocate proceeds to cash reserve, underweight sectors, or highest-grade watchlist names.

### 6. SPY - Concentration control

- **Source:** Portfolio
- **Setup:** Trim roughly 3.0% portfolio weight or pair with covered calls
- **Reference price:** $686.29
- **Rank score:** 80.7
- **Rationale:**
  - SPY is 17.1% of portfolio versus a 5% single-position risk guideline.
  - Market value is approximately $205,887.
- **Risk:** Tax impact and opportunity cost if the leadership trend continues.
- **Management:** Reallocate proceeds to cash reserve, underweight sectors, or highest-grade watchlist names.

### 7. SPY - Income / risk trim

- **Source:** Portfolio
- **Setup:** Consider covered call near $720 expiring 2026-06-12
- **Reference price:** $686.29
- **Rank score:** 80.6
- **Rationale:**
  - 17.1% portfolio weight creates single-name concentration.
  - Unrealized gain is +43.3%; covered calls can harvest income without adding delta.
  - Existing short-premium exposure already exists; size any new call sale conservatively.
- **Risk:** Caps upside if the position keeps trending; avoid adding if earnings are inside the option window.
- **Management:** Target 50% premium capture; close or roll if delta moves above ~0.45.

### 8. GOOGL - Concentration control

- **Source:** Portfolio
- **Setup:** Trim roughly 3.0% portfolio weight or pair with covered calls
- **Reference price:** $303.33
- **Rank score:** 80.0
- **Rationale:**
  - GOOGL is 13.8% of portfolio versus a 5% single-position risk guideline.
  - Market value is approximately $167,135.
- **Risk:** Tax impact and opportunity cost if the leadership trend continues.
- **Management:** Reallocate proceeds to cash reserve, underweight sectors, or highest-grade watchlist names.

## Current Concentration Snapshot

| Ticker | Weight | P&L | Day Change |
|--------|--------|-----|------------|
| SPY | 17.1% | +43.3% | +0.5% |
| AVGO | 16.7% | +175.4% | +0.3% |
| GOOGL | 13.8% | +74.0% | +0.4% |
| AMAT | 12.6% | +100.5% | +2.8% |
| MSFT | 6.7% | +21.7% | +0.7% |

## Top Watchlist Candidates

| Ticker | Score | Grade | Status |
|--------|-------|-------|--------|
| LRCX | 67.4 | B | Top Candidate |
| NVDA | 66.2 | B | Top Candidate |
| TSM | 61.8 | B- | Top Candidate |
| KLAC | 61.3 | B- | Top Candidate |
| ADBE | 60.1 | B- | Top Candidate |

## Disclaimers

- This is not financial advice and is for research/workflow automation only.
- Verify live option chains, bid/ask spreads, earnings dates, tax impact, and portfolio limits before placing trades.
- Options involve substantial risk; use the Altamira risk framework for sizing and exits.
