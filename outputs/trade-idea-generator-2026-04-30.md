# Trade Idea Generator - 2026-04-30

> Source: repository context files (`context/portfolio-details.md` and `context/watchlist.md`).
> This is not financial advice. Verify live prices, option chains, earnings dates, liquidity, and account constraints before trading.

## Context Check

- Portfolio snapshot date in repo: 2026-02-18
- Equity positions parsed: 20
- Watchlist entries parsed: 26
- Option rows parsed: 5
- Target option idea expiration: 2026-06-12 (weekly/monthly availability must be verified)

## Portfolio Exposure Snapshot

- Technology: 45.4%
- Index: 17.8%
- Communication Services: 13.8%
- Consumer Discretionary: 4.9%
- Financials: 4.8%
- Consumer Staples: 4.1%

## Data Freshness Flags

- 2 option row(s) have expirations before 2026-04-30; refresh `context/options-positions.md` before acting on options-management rows.

## Top Trade Ideas

1. SPY - Covered call / trim overlay
   Action: Sell up to 3 SPY 750C exp 2026-06-12
   Rationale: 17.1% portfolio weight, +43.3% unrealized gain; monetize upside while keeping most shares invested.
   Risk: Only sell calls on shares you are willing to trim if assigned.

2. AVGO - Covered call / trim overlay
   Action: Sell up to 3 AVGO 365C exp 2026-06-12
   Rationale: 16.7% portfolio weight, +175.4% unrealized gain; monetize upside while keeping most shares invested.
   Risk: Only sell calls on shares you are willing to trim if assigned.

3. GOOGL - Covered call / trim overlay
   Action: Sell up to 3 GOOGL 330C exp 2026-06-12
   Rationale: 13.8% portfolio weight, +74.0% unrealized gain; monetize upside while keeping most shares invested.
   Risk: Only sell calls on shares you are willing to trim if assigned.

4. AMAT - Covered call / trim overlay
   Action: Sell up to 3 AMAT 400C exp 2026-06-12
   Rationale: 12.6% portfolio weight, +100.5% unrealized gain; monetize upside while keeping most shares invested.
   Risk: Only sell calls on shares you are willing to trim if assigned.

5. LRCX - Watchlist entry candidate
   Action: Run /options-scan LRCX; target 0.20-0.30 delta put, 30-45 DTE.
   Rationale: Lam Research Corporation is scored 67.4 (B) and marked Top Top Candidate.
   Risk: Do not sell premium through earnings; keep cash-secured or defined-risk sizing.

6. NVDA - Watchlist entry candidate
   Action: Run /options-scan NVDA; target 0.20-0.30 delta put, 30-45 DTE.
   Rationale: NVIDIA Corporation is scored 66.2 (B) and marked Top Top Candidate.
   Risk: Do not sell premium through earnings; keep cash-secured or defined-risk sizing.

7. TSM - Watchlist entry candidate
   Action: Run /options-scan TSM; target 0.20-0.30 delta put, 30-45 DTE.
   Rationale: Taiwan Semiconductor Manufacturing Company is scored 61.8 (B-) and marked Top Top Candidate.
   Risk: Do not sell premium through earnings; keep cash-secured or defined-risk sizing.

8. KLAC - Watchlist entry candidate
   Action: Run /options-scan KLAC; target 0.20-0.30 delta put, 30-45 DTE.
   Rationale: KLA Corporation is scored 61.3 (B-) and marked Top Top Candidate.
   Risk: Do not sell premium through earnings; keep cash-secured or defined-risk sizing.

## Execution Checklist

- Confirm latest quote and bid/ask spread before order entry.
- Confirm no earnings event falls inside the option holding window.
- Keep any new options exposure inside the 30% options allocation cap.
- Close short premium at 50% profit; stop/roll around 200% of credit or short-strike breach.
