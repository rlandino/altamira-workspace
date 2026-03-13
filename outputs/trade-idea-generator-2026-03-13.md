# Trade Idea Generator - 2026-03-13

Source context:
- Portfolio: `context/portfolio-details.md`
- Watchlist: `context/watchlist.md`

## Portfolio + Watchlist Trade Ideas

### 1) AVGO covered call (income + trim concentration)
- Why: AVGO is one of the largest portfolio weights and has large unrealized gains.
- Setup: Sell 30-45 DTE covered calls around 0.20-0.25 delta on existing AVGO shares.
- Goal: Harvest premium while setting a disciplined upside exit on part of the position.
- Risk note: Cap on upside if AVGO continues to run.

### 2) MSFT short-put risk management (defensive roll plan)
- Why: Existing MSFT 430P appears under pressure versus current spot in the context file.
- Setup: Predefine roll trigger; if short strike remains threatened, roll out in time and down in strike for net credit where possible.
- Goal: Reduce assignment shock and smooth theta strategy drawdowns.
- Risk note: Extending duration can increase time-in-risk.

### 3) SPY hedge overlay (portfolio beta control)
- Why: Portfolio has meaningful index and growth exposure; hedge can reduce tail risk.
- Setup: Use a small defined-risk SPY put spread (30-60 DTE) sized to 1-2% portfolio risk.
- Goal: Limit drawdown during volatility spikes while keeping core exposure.
- Risk note: Hedge premium can be a drag if market grinds higher.

### 4) NVDA bullish premium-selling candidate (watchlist top candidate)
- Why: NVDA is a top watchlist candidate and fits high-quality growth profile.
- Setup: Consider bull put spread or cash-secured put at ~0.20 delta, 30-45 DTE, avoiding unplanned earnings risk.
- Goal: Enter or add exposure via premium capture with defined plan.
- Risk note: Elevated volatility can widen mark-to-market swings.

### 5) LRCX starter position via CSP (watchlist rank #1)
- Why: LRCX is the highest-scored watchlist name.
- Setup: Sell a 30-45 DTE cash-secured put at ~0.20-0.25 delta to target lower effective entry.
- Goal: Generate income while potentially entering at a discount.
- Risk note: Semiconductor cyclicality can accelerate downside during risk-off periods.

## Priority Queue (today)
1. AVGO covered call screening
2. MSFT short-put risk check + roll triggers
3. LRCX/NVDA premium-entry scan
4. SPY hedge sizing check

## Risk Controls
- Max 5% risk per new idea
- Keep aggregate options allocation <= 30%
- Maintain cash reserve >= 15%
- Avoid holding new short premium through unplanned earnings

## Disclaimer
For educational and planning purposes only, not investment advice. Validate live chain liquidity, bid/ask spreads, earnings dates, and portfolio limits before execution.
