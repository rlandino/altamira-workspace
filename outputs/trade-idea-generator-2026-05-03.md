# Trade Idea Generator - 2026-05-03

## Scope

- Portfolio context: 20 holdings, $1,207,271 market value from `context/portfolio-details.md`.
- Watchlist context: 26 tickers from `context/watchlist.md`; top candidates: LRCX (B), NVDA (B), TSM (B-), KLAC (B-), ADBE (B-).
- Target expiration window: approximately 30-45 DTE; nearest planning Friday: 2026-06-19.
- Live FMP quotes: not configured; using repository context prices.

## Top Covered Call Ideas

1. **AVGO - Covered call**
   - Action: Sell up to 6 call contract(s), around $360 strike expiring near 2026-06-19.
   - Rationale: 16.7% portfolio weight, +175.4% unrealized gain; harvest premium without adding downside exposure.
   - Risk: Cap upside above the short call strike; avoid if near a catalyst you want uncapped.
2. **AMAT - Covered call**
   - Action: Sell up to 4 call contract(s), around $405 strike expiring near 2026-06-19.
   - Rationale: 12.6% portfolio weight, +100.5% unrealized gain; harvest premium without adding downside exposure.
   - Risk: Cap upside above the short call strike; avoid if near a catalyst you want uncapped.
3. **GOOGL - Covered call**
   - Action: Sell up to 5 call contract(s), around $330 strike expiring near 2026-06-19.
   - Rationale: 13.8% portfolio weight, +74.0% unrealized gain; harvest premium without adding downside exposure.
   - Risk: Cap upside above the short call strike; avoid if near a catalyst you want uncapped.
4. **AMZN - Covered call**
   - Action: Sell up to 2 call contract(s), around $220 strike expiring near 2026-06-19.
   - Rationale: 4.9% portfolio weight, +80.7% unrealized gain; harvest premium without adding downside exposure.
   - Risk: Cap upside above the short call strike; avoid if near a catalyst you want uncapped.
5. **MSFT - Covered call**
   - Action: Sell up to 2 call contract(s), around $430 strike expiring near 2026-06-19.
   - Rationale: 6.7% portfolio weight, +21.7% unrealized gain; harvest premium without adding downside exposure.
   - Risk: Cap upside above the short call strike; avoid if near a catalyst you want uncapped.

## Top Cash-Secured Put Ideas

1. **LRCX - Cash-secured put**
   - Action: Price live chain manually; target 0.20-0.30 delta put 10-15% OTM expiring near 2026-06-19.
   - Rationale: B watchlist score (67.4); no live quote available in this run.
   - Risk: Assignment adds single-name exposure; respect 5% position and 30% options allocation limits.
2. **NVDA - Cash-secured put**
   - Action: Price live chain manually; target 0.20-0.30 delta put 10-15% OTM expiring near 2026-06-19.
   - Rationale: B watchlist score (66.2); no live quote available in this run.
   - Risk: Assignment adds single-name exposure; respect 5% position and 30% options allocation limits.
3. **TSM - Cash-secured put**
   - Action: Price live chain manually; target 0.20-0.30 delta put 10-15% OTM expiring near 2026-06-19.
   - Rationale: B- watchlist score (61.8); no live quote available in this run.
   - Risk: Assignment adds single-name exposure; respect 5% position and 30% options allocation limits.
4. **KLAC - Cash-secured put**
   - Action: Price live chain manually; target 0.20-0.30 delta put 10-15% OTM expiring near 2026-06-19.
   - Rationale: B- watchlist score (61.3); no live quote available in this run.
   - Risk: Assignment adds single-name exposure; respect 5% position and 30% options allocation limits.
5. **ADBE - Cash-secured put**
   - Action: Price live chain manually; target 0.20-0.30 delta put 10-15% OTM expiring near 2026-06-19.
   - Rationale: B- watchlist score (60.1); no live quote available in this run.
   - Risk: Assignment adds single-name exposure; respect 5% position and 30% options allocation limits.

## Risk Notes

- Concentration watch: SPY 17.1%, AVGO 16.7%, GOOGL 13.8%, AMAT 12.6%. Prefer premium that reduces or hedges exposure.
- Manage challenged short puts before adding risk: MSFT 2026-03-20 $430P.
- Do not enter short premium through unplanned earnings; verify earnings dates and live chain liquidity before order entry.

## Execution Checklist

- Confirm live bid/ask spread is under 10% of mid and open interest is adequate.
- Size each new trade at or below 5% max position risk and keep total options allocation under 30%.
- Close winners around 50% of max profit; stop or roll if loss reaches roughly 2x original credit or thesis changes.

_Educational trade planning only; not financial advice._
