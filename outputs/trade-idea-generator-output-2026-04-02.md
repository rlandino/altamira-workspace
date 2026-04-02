# Trade Idea Generator Output — 2026-04-02

Source inputs: `context/portfolio-details.md` and `context/watchlist.md`.

## Portfolio snapshot
- Positions parsed: **20**
- Top holdings by table order: SPY, AVGO, GOOGL, AMAT, MSFT, AMZN, AAPL, CRWD

## Watchlist snapshot
- Watchlist entries parsed: **26**
- Top scored names: LRCX (67.4), NVDA (66.2), TSM (61.8), KLAC (61.3), ADBE (60.1)

## Today's trade ideas
### 1. LRCX — WATCHLIST_ADD_CSP
- Rationale: Top watchlist score 67.4 (**B**); not currently held.
- Action: Run /options-scan LRCX and look for 30-45 DTE CSP at 0.20-0.30 delta.

### 2. NVDA — WATCHLIST_ADD_CSP
- Rationale: Top watchlist score 66.2 (**B**); not currently held.
- Action: Run /options-scan NVDA and look for 30-45 DTE CSP at 0.20-0.30 delta.

### 3. TSM — WATCHLIST_ADD_CSP
- Rationale: Top watchlist score 61.8 (**B-**); not currently held.
- Action: Run /options-scan TSM and look for 30-45 DTE CSP at 0.20-0.30 delta.

### 4. SPY — CONCENTRATION_HEDGE
- Rationale: Largest position by market value (17.1% weight) with sizable unrealized gain.
- Action: Consider collar or staged covered calls to monetize IV while capping downside.

## Risk note
- For any options idea, confirm earnings date, liquidity, and sizing against risk limits before entry.
- This is an automation-generated idea list, not investment advice.