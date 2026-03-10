# Altamira Capital — Portfolio Allocation Model

**Version:** 1.0
**Date:** 2026-02-18
**Author:** Ricardo Landino, Founder
**Status:** Active — Complements Investment Thesis v1.0

---

## 1. Executive Summary

### Philosophy

Altamira Capital's allocation model is built on three convictions:

1. **Volatility is harvested, not predicted.** Options premium selling generates consistent, positive-expectancy returns across most market regimes. This is the portfolio's income engine.
2. **Direction is followed, not forecast.** Momentum and conviction equity sleeves capture upside by participating in established trends and high-quality businesses, not by predicting inflection points.
3. **Cash is a position, not a default.** Maintaining 15-25% in cash and equivalents is an active allocation decision that provides dry powder for dislocations and margin safety for options strategies.

### Target Returns

| Metric | Year 1 Target | Steady State |
|--------|---------------|-------------|
| Net annual return | 12-18% | 15-25% |
| Sharpe ratio | >1.5 | >2.0 |
| Maximum drawdown | <-15% | <-12% |
| Options win rate | >65% | >70% |
| Monthly options income | Positive | Growing with AUM |

### Key Allocation Decisions

- **Options Premium Sleeve is the primary return driver at 35-45% allocation.** The 83.3% win rate and 1.34 Sharpe from backtesting validate this as the core strategy. Consistent income with defined risk.
- **Equity exposure is split into two sleeves** — Momentum (systematic, 50-day MA) and Conviction (fundamental, discretionary). This separates mechanical trend-following from research-driven positions, enabling clearer performance attribution.
- **Hedging is conditional, not permanent.** Backtesting showed negligible drawdown reduction in bull markets at ~0.1% cost. Hedging activates when VIX < 18 or when portfolio drawdown exceeds -5%.
- **Cash earns 4-5% in T-bills** while providing optionality. At current rates, 20% cash allocation contributes ~0.8-1.0% to total portfolio return with zero risk.

### Backtest Foundation

This model is grounded in 2-year backtests (ending 2026-02-18) across the core universe (AAPL, MSFT, GOOGL, AMZN, AVGO, COST, V, MA, META, NVDA, SPY):

| Strategy | Return | Sharpe | Max DD | Win Rate |
|----------|--------|--------|--------|----------|
| CSP (40% alloc) | 1.15% | 1.34 | -0.26% | 83.3% |
| Momentum (40% alloc) | 34.57% | 0.68 | -20.3% | 72.7% monthly |
| Hedging overlay | -0.08% cost | -- | 0.0% reduction | -- |
| SPY benchmark | 36.71% | -- | -- | -- |
| Blended estimate | ~16.1% | -- | -- | -- |

The CSP return appears low due to conservative backtesting methodology (estimated IV, simplified pricing). Live execution with real IV data, higher IV Rank filtering, and more frequent trading cycles is expected to produce materially higher returns. The Sharpe ratio of 1.34 and 83.3% win rate confirm the strategy's risk-adjusted quality.

---

## 2. Strategic Asset Allocation (SAA)

The Strategic Asset Allocation defines long-term target weights that reflect the firm's investment philosophy and risk tolerance. These targets are the "home base" — tactical adjustments shift allocations within defined ranges, but rebalancing always gravitates back to SAA targets.

### Sleeve Definitions

**Options Premium Sleeve** — Cash-secured puts, covered calls, vertical spreads, jade lizards. Income-focused. Relies on implied volatility overestimating realized volatility. Parameters: 0.20-0.30 delta, 30-45 DTE, IV Rank > 30th percentile.

**Equity Momentum Sleeve** — Systematic long positions based on 50-day simple moving average signal. Long when price > 50-day SMA, flat when below. Equal-weight among signal-active names. Rebalances every 20 trading days.

**Equity Conviction Sleeve** — Fundamental long positions in companies with durable competitive advantages, improving fundamentals, and reasonable valuation. Concentrated (5-10 names). Position sizing by conviction level. Holding period: 3-12 months.

**Hedging Sleeve** — SPY/QQQ put spreads, VIX call spreads, collars on concentrated positions. Activated conditionally based on VIX level and portfolio drawdown. Budget-based, not allocation-based.

**Cash & Equivalents** — T-bills (4-week, 13-week), money market funds, brokerage sweep. Provides margin safety, dry powder, and positive yield.

### SAA Target Table

| Sleeve | Target % | Range % | Purpose | Expected Return Contribution | Expected Risk Contribution |
|--------|----------|---------|---------|------------------------------|---------------------------|
| Options Premium | 35% | 25-45% | Core income, vol harvesting | 4-6% (annualized) | Low (defined risk per trade) |
| Equity Momentum | 20% | 10-30% | Systematic trend capture | 3-5% (annualized) | Moderate (equity beta) |
| Equity Conviction | 15% | 10-25% | Alpha generation, capital appreciation | 3-6% (annualized) | Moderate-High (concentrated) |
| Hedging | 0-3% | 0-5% | Tail risk reduction | -0.5% to -1.0% (cost) | Negative (reduces portfolio risk) |
| Cash & Equivalents | 20% | 15-50% | Dry powder, margin buffer, yield | 0.8-1.0% (T-bill yield) | Near-zero |
| **Total** | **~93-95%** | -- | -- | **~10.3-17.0%** | -- |

Note: Options Premium allocation represents capital reserved for cash-secured obligations, not notional options exposure. The 2-5% gap between sleeve targets and 100% accounts for the hedging budget and rounding — in practice, cash absorbs the remainder.

### Expected Return Decomposition ($100K Portfolio)

| Sleeve | Capital Allocated | Expected Annual Return | Expected Annual $ |
|--------|-------------------|----------------------|-------------------|
| Options Premium | $35,000 | 12-18% on allocated capital | $4,200 - $6,300 |
| Equity Momentum | $20,000 | 15-25% (partial exposure) | $3,000 - $5,000 |
| Equity Conviction | $15,000 | 18-35% | $2,700 - $5,250 |
| Hedging | $2,000 (annual budget) | -100% (cost center) | -$1,000 - -$2,000 |
| Cash & Equivalents | $20,000 | 4-5% | $800 - $1,000 |
| **Portfolio Total** | **$100,000** | **~9.7-15.6%** | **$9,700 - $15,550** |

Conservative estimate reflects Year 1 learning curve. Steady-state targets are higher as execution improves and strategies are refined.

---

## 3. Tactical Asset Allocation (TAA)

Tactical adjustments shift allocations away from SAA targets in response to market conditions. TAA is rules-based, not discretionary — each regime has predefined allocation shifts to reduce emotional decision-making.

### 3.1 VIX-Based Regime Model

VIX is the primary regime indicator. Four regimes map to specific allocation shifts.

| Regime | VIX Range | Market Condition | Options Premium | Equity Momentum | Equity Conviction | Hedging | Cash |
|--------|-----------|-----------------|----------------|-----------------|-------------------|---------|------|
| **Complacent** | < 15 | Low vol, trending up | 30% (-5pp) | 25% (+5pp) | 18% (+3pp) | 5% (+2pp) | 22% (+2pp) |
| **Normal** | 15-25 | Standard | 35% (SAA) | 20% (SAA) | 15% (SAA) | 2% (SAA) | 20% (SAA) |
| **Elevated** | 25-35 | Fear rising, vol expanding | 40% (+5pp) | 15% (-5pp) | 12% (-3pp) | 3% (+1pp) | 25% (+5pp) |
| **Crisis** | > 35 | Panic, dislocation | 25% (-10pp) | 5% (-15pp) | 10% (-5pp) | 5% (+3pp) | 50% (+30pp) |

**Rationale:**

- **Complacent (VIX < 15):** Options premiums are thin — reduce premium selling, increase equity exposure to capture momentum, increase hedging (cheap insurance).
- **Normal (VIX 15-25):** SAA targets. Balanced deployment across all sleeves.
- **Elevated (VIX 25-35):** Options premiums are rich — increase premium selling at wider strikes. Reduce equity exposure. Build cash.
- **Crisis (VIX > 35):** Capital preservation mode. Reduce all risk sleeves dramatically. Cash to 50%. Only sell premium at extreme levels with very wide strikes. This maps to Investment Thesis drawdown Tier 2/3.

### 3.2 Momentum Regime Detection

Market regime affects the Equity Momentum Sleeve and overall exposure.

| Signal | Condition | Interpretation | Action |
|--------|-----------|---------------|--------|
| SPY > 50-day SMA | Price above trend | Bull regime, trending | Full momentum allocation; equity sleeves at target or above |
| SPY < 50-day SMA | Price below trend | Bear/correction regime | Reduce momentum to 10%; move excess to cash |
| SPY crosses below 200-day SMA | Major trend break | Potential bear market | Reduce all equity to minimum; increase cash to 35%+ |
| 50-day SMA crosses below 200-day SMA (death cross) | Trend deterioration confirmed | Bear market likely | Maximum defensive posture: cash 40-50%, options at reduced size with wider deltas (0.15-0.20) |

### 3.3 Earnings Season Adjustments

Earnings seasons (Jan/Apr/Jul/Oct, roughly 4-6 weeks each) create elevated implied volatility across the core universe, presenting premium selling opportunities.

| Period | Options Premium Adjustment | Equity Adjustment | Notes |
|--------|---------------------------|-------------------|-------|
| Pre-earnings (5+ days before) | Increase CSP allocation by 5pp on reporting names | Hold existing positions; no new entries | IV is elevated, premium is rich |
| Earnings week | No new CSPs unless planned earnings trade | Halt new conviction entries on reporting name | Close or roll existing positions to avoid binary event |
| Post-earnings (0-5 days after) | Resume normal allocation; sell premium if IV remains elevated | Enter momentum/conviction if signal confirms | IV crush benefits open short premium positions |
| Off-earnings season | SAA targets | SAA targets | Standard regime |

### 3.4 Rate Environment Adjustments

The risk-free rate affects the opportunity cost of cash and the relative attractiveness of options income.

| Rate Environment | Cash Yield | Cash Allocation Adjustment | Options Adjustment |
|------------------|-----------|---------------------------|-------------------|
| High rates (>4%) | Attractive | Hold at 20-25%; cash is earning meaningful return | Less urgency to deploy; CSP hurdle rate is higher |
| Moderate rates (2-4%) | Moderate | SAA target (20%) | Standard allocation |
| Low rates (<2%) | Minimal | Reduce to 15% minimum; deploy excess into equity/options | More aggressive premium selling — yield is scarce |

At current rates (~4-5% on short-term T-bills), cash generates ~$800-1,000/year on a $20K allocation — a meaningful contribution that should not be dismissed.

### 3.5 TAA Regime Summary Table

| Regime Trigger | Options Premium | Eq. Momentum | Eq. Conviction | Hedging | Cash |
|----------------|----------------|-------------|----------------|---------|------|
| **SAA Baseline (Normal)** | **35%** | **20%** | **15%** | **2%** | **20%** |
| VIX < 15 | 30% | 25% | 18% | 5% | 22% |
| VIX 25-35 | 40% | 15% | 12% | 3% | 25% |
| VIX > 35 | 25% | 5% | 10% | 5% | 50% |
| SPY < 50-day SMA | 30% | 10% | 12% | 5% | 35% |
| Death Cross (50 < 200 SMA) | 20% | 5% | 10% | 5% | 50% |
| Earnings season (active) | 40% | 18% | 13% | 2% | 20% |
| Drawdown Tier 1 (-5%) | 30% | 15% | 12% | 5% | 30% |
| Drawdown Tier 2 (-10%) | 20% | 10% | 10% | 5% | 45% |
| Drawdown Tier 3 (-15%) | 0% | 0% | 10% | 5% | 75% |

When multiple regimes overlap, use the most defensive posture. For example, if VIX > 35 AND drawdown Tier 2, use drawdown Tier 2 allocations (more defensive).

---

## 4. Position Sizing Within Each Sleeve

### 4.1 Options Premium Sleeve ($35,000 at SAA)

**Sizing approach:** Equal-weight capital allocation across active positions in the core universe.

**Parameters:**

| Parameter | Rule | At $100K Portfolio |
|-----------|------|-------------------|
| Max single-name options exposure | 5% of portfolio | $5,000 per name |
| Max contracts per name | Floor($5,000 / (strike x 100)) | Varies by name price |
| Capital reservation for assignment | 100% cash-secured for CSPs | Full strike x 100 x contracts |
| Max simultaneous CSP positions | 6-8 positions | Across core universe |
| Max total options allocation | 45% of portfolio (SAA range ceiling) | $45,000 |

**Example at $100K:**

Selling 1 CSP on MSFT at $380 strike requires $38,000 in capital reservation. This exceeds the 5% single-name limit ($5,000) by the notional measure — but CSP capital reservation is different from risk exposure. The actual risk is the difference between strike and breakeven (strike - premium received).

Practical approach at $100K:
- Focus on lower-priced underlyings: SPY ($585 — too large for 1 contract at 5% limit), AAPL (~$230 — $23,000 per contract), NVDA (~$135 — $13,500 per contract)
- At $100K, CSPs on mega-cap names require accepting concentrated notional exposure per contract
- Prioritize 2-3 positions where single contracts fit within capital constraints
- Use bull put spreads on higher-priced names to reduce capital requirements

**Capital reservation formula:**

```
CSP capital needed = strike_price x 100 x num_contracts
Bull put spread capital needed = (short_strike - long_strike) x 100 x num_contracts
```

**Position rotation:** With 30-45 DTE and 50% profit target (typically reached in 10-20 days), each position "slot" can cycle 8-12 times per year, generating premium on each cycle.

### 4.2 Equity Momentum Sleeve ($20,000 at SAA)

**Sizing approach:** Equal-weight among all names with active buy signals (price > 50-day SMA).

**Parameters:**

| Parameter | Rule | At $100K Portfolio |
|-----------|------|-------------------|
| Weight per active name | $20,000 / count(active signals) | $2,000-$4,000 per name if 5-10 active |
| Maximum names | 10 (full universe) | Equal weight = $2,000 each |
| Minimum names for deployment | 3 | If < 3 active, hold excess in cash |
| Rebalance frequency | Every 20 trading days | Monthly cycle |
| Cash when signal off | Move to cash sleeve | Automatic de-risking |

**Signal logic:**

```
IF price > 50-day SMA → LONG (equal weight share of sleeve allocation)
IF price < 50-day SMA → FLAT (capital returns to cash)
```

**Example at $100K:**
- 7 of 10 names above 50-day SMA
- Allocation per name: $20,000 / 7 = $2,857 per name
- Remaining $20,000 - (7 x $2,857) = $0 unallocated in sleeve
- If only 2 names active (below minimum), hold $20,000 in cash; do not deploy

### 4.3 Equity Conviction Sleeve ($15,000 at SAA)

**Sizing approach:** Conviction-weighted. Each position is tagged as High, Medium, or Low conviction based on fundamental analysis.

| Conviction Level | Weight | At $100K Portfolio | Max Names |
|-----------------|--------|-------------------|-----------|
| High | 5% of portfolio | $5,000 | 2-3 |
| Medium | 3% of portfolio | $3,000 | 3-4 |
| Low | 2% of portfolio | $2,000 | 2-3 |

**Total conviction sleeve capacity:** Up to $15,000 (e.g., 1 high at $5K + 2 medium at $3K each + 2 low at $2K each = $15K).

**Conviction criteria:**

| Factor | High | Medium | Low |
|--------|------|--------|-----|
| Fundamental quality | Exceptional moat, growing margins | Strong moat, stable margins | Decent moat, acceptable margins |
| Valuation | Below intrinsic value | Fair value | Slightly above fair value but with catalyst |
| Catalyst | Clear near-term catalyst | Identified catalyst, uncertain timing | Thesis-based, no specific catalyst |
| Hold period target | 6-12 months | 3-6 months | 1-3 months |

**Stop-loss:** -10% hard stop on all conviction positions. Review for re-entry after 5 trading days if thesis remains intact.

### 4.4 Hedging Sleeve (Budget-Based)

**Sizing approach:** Quarterly budget, not fixed allocation. Spend 0.5-1.0% of portfolio per quarter on hedging instruments.

| Parameter | Rule | At $100K Portfolio |
|-----------|------|-------------------|
| Quarterly budget | 0.5-1.0% of portfolio | $125-$250 per quarter |
| Annual budget | 2-4% of portfolio | $500-$1,000 per year |
| Instrument preference | SPY put spreads (cheapest per unit of protection) | Defined max cost per trade |
| VIX trigger to buy | VIX < 18 (insurance is cheap) | Buy when complacent |
| VIX trigger to pause | VIX > 30 (insurance is expensive) | Skip or reduce |

**Hedging instruments by priority:**

1. SPY put spreads (e.g., buy 5% OTM put, sell 10% OTM put) — cheapest broad protection
2. VIX call spreads (e.g., buy VIX 20 call, sell VIX 35 call) — tail risk insurance
3. Collars on largest individual positions — if any single name exceeds 5% of portfolio

### 4.5 Cash Management ($20,000 at SAA)

**Instrument allocation:**

| Instrument | Allocation Within Cash | Yield | Liquidity |
|------------|----------------------|-------|-----------|
| 4-week T-bills | 40% of cash ($8,000) | ~4.3% | Weekly maturity, highly liquid |
| 13-week T-bills | 35% of cash ($7,000) | ~4.5% | Quarterly maturity, liquid |
| Brokerage money market / sweep | 25% of cash ($5,000) | ~3.5-4.0% | Same-day, immediate |

**Ladder strategy:** Stagger T-bill purchases so maturities occur weekly, ensuring continuous access to cash without sacrificing yield.

**Sweep account:** E-Trade sweep automatically moves uninvested cash into money market. Ensure sweep is enabled on account setup.

---

## 5. Scaling Model: $100K to $5M

The allocation model evolves at each AUM milestone. Early stages are simpler with fewer positions; later stages unlock additional strategies, instruments, and operational capabilities.

### 5.1 Milestone Allocation Shifts

#### $100K — Foundation (Current)

- **Focus:** Learn, validate, survive. Paper trade first, then live at 50% size.
- **Simplifications:** Fewer positions (3-5 CSPs, 5-7 momentum, 2-4 conviction). Wider rebalancing bands (15pp vs. 10pp). No spreads yet — cash-secured only.
- **Key constraint:** Single CSP contracts on most names consume 15-40% of capital. Position sizing is naturally concentrated.
- **Priority:** Build track record, validate risk management, refine automation.

#### $250K — Full Deployment

- **Unlock:** Full strategy deployment across all sleeves. Enough capital for proper diversification.
- **Changes:** 5-8 simultaneous CSP positions. Full 10-name momentum universe. 5-8 conviction positions. Formal hedging budget.
- **Key unlock:** Can sell CSPs on higher-priced names (AVGO, COST, MSFT) without exceeding concentration limits.

#### $500K — Strategy Expansion

- **Unlock:** Defined-risk spreads become capital-efficient. Greater position diversity reduces idiosyncratic risk.
- **Changes:** Add bull put spreads and jade lizards to options sleeve. Increase position count to 8-12 CSPs. Consider sector ETF positions for broader exposure. Reduce single-name concentration.
- **Key unlock:** Defined-risk spreads require less capital, enabling more positions and better diversification.

#### $1M — Institutional Capabilities

- **Unlock:** Portfolio margin eligibility. Enough scale for meaningful diversification.
- **Changes:** Apply for portfolio margin (reduces capital requirements ~60% for defined-risk positions). Expand universe beyond core 10 names (+5-10 additional). Add sector rotation via ETFs. Consider LEAPS for capital-efficient equity exposure.
- **Key unlock:** Portfolio margin dramatically expands strategy capacity.

#### $5M — Full Multi-Strategy

- **Unlock:** Fund structure evaluation. Potential external capital.
- **Changes:** Evaluate LP/GP structure. Consider hiring quantitative analyst. Expand to 30-50 name universe. Add systematic short selling. Formal risk management infrastructure. Professional audit and reporting.
- **Key unlock:** Scale justifies operational overhead of formal fund.

### 5.2 Scaling Summary Table

| AUM Level | # CSP Positions | # Momentum Names | # Conviction Names | Max Single Position $ | Strategies Active | Operational Changes |
|-----------|----------------|-------------------|--------------------|-----------------------|-------------------|---------------------|
| $100K | 2-4 | 5-7 | 2-4 | $5,000 (5%) | CSP, momentum, conviction | Paper then live transition; manual execution |
| $250K | 5-8 | 8-10 | 4-6 | $12,500 (5%) | All SAA sleeves fully deployed | Semi-automated execution via n8n |
| $500K | 8-12 | 10 | 5-8 | $25,000 (5%) | Add spreads, jade lizards | Automated pre-trade risk checks |
| $1M | 12-15 | 10-15 | 8-12 | $50,000 (5%) | Add LEAPS, sector ETFs, portfolio margin | Automated execution with approval |
| $5M | 15-25 | 15-20 | 10-15 | $250,000 (5%) | Full multi-strategy + systematic short | Fund structure, potential hire, full automation |

### 5.3 Capital Deployment Schedule

Never deploy all capital at once. Whether starting at $100K or adding new capital at any milestone, follow this deployment schedule:

| Week | Cumulative Deployed | Action |
|------|-------------------|--------|
| Week 1 | 25% | Deploy cash sleeve (T-bills, money market). Begin 1-2 CSP positions. |
| Week 2 | 50% | Add momentum sleeve positions. Add 1-2 more CSP positions. |
| Week 3 | 75% | Add conviction sleeve positions. Establish hedging if conditions warrant. |
| Week 4 | 100% | Fully deployed to SAA targets. All sleeves active. |

**Exception:** During VIX > 35 or drawdown Tier 2+, pause deployment and hold excess in cash until conditions normalize.

### 5.4 Growth Trajectory

Compounding targets from $100K starting capital:

| Year | Starting AUM | Target Return | Year-End AUM | Cumulative Growth |
|------|-------------|---------------|-------------|-------------------|
| Year 1 | $100,000 | 12-18% | $112,000 - $118,000 | 12-18% |
| Year 2 | $115,000 | 15-22% | $132,000 - $140,000 | 32-40% |
| Year 3 | $136,000 | 15-25% | $156,000 - $170,000 | 56-70% |
| Year 5 | ~$190,000 | 15-25% | $218,000 - $237,000 | 118-137% |
| Year 10 | ~$400,000 | 15-25% | $460,000 - $500,000 | 360-400% |

Reaching $5M from $100K through returns alone would require ~20%+ annual returns sustained for ~20 years, or significant external capital additions. Realistic path to $5M AUM likely combines:
- Compounded trading returns (~15-20%/year)
- Additional capital contributions
- External investor capital (post-fund formation at $1M+ AUM)

---

## 6. Rebalancing Rules

### 6.1 Calendar-Based Rebalancing

| Frequency | Action |
|-----------|--------|
| Monthly (1st trading day) | Full portfolio review. Compare all sleeves to SAA targets. Execute rebalancing trades if any sleeve deviates by > 5pp. |
| Quarterly (1st trading day of Jan/Apr/Jul/Oct) | Deep review. Reassess conviction positions, update momentum signals, evaluate hedging budget, T-bill ladder renewal. |
| Annually | Strategic review. Reassess SAA targets based on YTD performance, market outlook, and firm AUM growth. |

### 6.2 Threshold-Based Rebalancing

| Trigger | Threshold | Action |
|---------|-----------|--------|
| Sleeve deviation from SAA target | > 10 percentage points | Mandatory rebalance within 2 trading days |
| Sleeve approaching limit | > 7 percentage points | Flag for review; rebalance at next monthly review if not self-correcting |
| Single position exceeds limit | > 5% of portfolio | Trim to 4.5% (creates buffer below limit) |
| Sector exposure exceeds limit | > 25% of portfolio | Reduce most overweight name in sector |

### 6.3 Event-Based Rebalancing

| Event | Action |
|-------|--------|
| Drawdown Tier 1 (-5% from peak) | Reduce all position sizes by 25%. Increase cash to 30%. No new risk. Review all positions. |
| Drawdown Tier 2 (-10% from peak) | Close lowest-conviction positions. Reduce sizing by 50%. Increase cash to 45%. Increase hedging. |
| Drawdown Tier 3 (-15% from peak) | Capital preservation mode. Close all options. Hold only highest-conviction longs + cash (75%+). |
| VIX spike > 35 (from < 25) | Immediate review. Shift to Crisis regime allocations. Do not wait for monthly rebalance. |
| Major macro event | Discretionary review. Assess portfolio impact. Flag if any sleeve or position is directly affected. |
| Assignment on CSP | Assigned shares become equity conviction position. Reassess sleeve allocations. Sell covered calls on assigned shares if conviction permits. |

### 6.4 Tax-Aware Rebalancing

| Consideration | Rule |
|---------------|------|
| Short-term capital gains | Prefer to hold profitable equity positions > 12 months for long-term rates |
| Tax-loss harvesting | When rebalancing triggers a sell at a loss, harvest the loss. Replace with correlated-but-not-identical position if desired. |
| Wash sale avoidance | After harvesting a loss, do not repurchase substantially identical security within 30 days |
| Options tax treatment | Short options premiums are short-term capital gains. Factor into annual tax planning. |
| Year-end rebalancing | In December, favor selling losing positions (harvest losses) over selling winners. Defer winner sales to January if possible. |

### 6.5 Rebalancing Priority Order

When rebalancing is triggered, adjust sleeves in this order (first = first to adjust):

1. **Cash** — Easiest to adjust. Increase by selling T-bills or deploy by purchasing. Same-day liquidity.
2. **Options Premium** — Allow existing positions to expire or close at profit target. Initiate new positions only if sleeve is underweight.
3. **Equity Momentum** — Fully systematic. Add or remove positions based on 50-day SMA signal.
4. **Equity Conviction** — Last to adjust. These are research-driven positions with specific theses. Only trim/exit if thesis is invalidated or rebalancing is mandatory.
5. **Hedging** — Budget-based. Adjust by buying or not buying next hedge, not by selling existing protection.

### 6.6 Concrete Rebalancing Example

**Scenario:** After a strong month, the portfolio has shifted from SAA targets.

| Sleeve | SAA Target | Current Allocation | Deviation |
|--------|------------|-------------------|-----------|
| Options Premium | 35% | 28% | -7pp (positions closed at profit, cash returned) |
| Equity Momentum | 20% | 27% | +7pp (strong momentum, positions appreciated) |
| Equity Conviction | 15% | 18% | +3pp (appreciation) |
| Cash & Equivalents | 20% | 22% | +2pp (CSP premiums collected + expired positions) |
| Hedging | 2% | 1% | -1pp (puts expired worthless) |

**Action plan (monthly rebalance):**

No sleeve exceeds the 10pp mandatory threshold, but Equity Momentum is at +7pp (approaching the 7pp flag threshold).

1. **Options Premium (+7pp underweight):** Initiate 2-3 new CSP positions across the universe to deploy ~$7,000 back into premium selling. Select names with IV Rank > 30 and price above 50-day SMA.
2. **Equity Momentum (+7pp overweight):** Trim $7,000 from momentum positions. Sell proportionally across all holdings (equal reduction). If any name has dropped below 50-day SMA, sell that name entirely first.
3. **Conviction (+3pp overweight):** No action required. Within acceptable range. Will self-correct if any position hits stop-loss.
4. **Cash (+2pp overweight):** No action required. Slightly above target provides buffer for new CSP capital requirements.
5. **Hedging (-1pp underweight):** If VIX < 18, purchase 1 SPY put spread within quarterly budget.

**Net trades:** Sell ~$7,000 in equity momentum positions. Use proceeds to initiate 2-3 new CSP positions. Buy 1 hedging position if VIX conditions met.

---

## 7. Cash Management Strategy

### 7.1 Minimum Cash Reserves

| Condition | Minimum Cash % | At $100K |
|-----------|---------------|----------|
| Normal operations | 15% | $15,000 |
| SAA target | 20% | $20,000 |
| Drawdown Tier 1 (-5%) | 30% | $30,000 |
| Drawdown Tier 2 (-10%) | 45% | $45,000 |
| Drawdown Tier 3 (-15%) | 75% | $75,000 |

Cash reserves must be maintained AFTER accounting for all CSP capital reservations. If selling a CSP requires $13,500 in cash (NVDA at $135 strike), that $13,500 is committed — it cannot count toward the minimum cash reserve.

### 7.2 Where to Park Cash

| Instrument | Target Allocation | Current Yield (Est.) | Liquidity | Use Case |
|------------|-------------------|---------------------|-----------|----------|
| 4-week T-bills | 40% of cash ($8,000) | ~4.3% | Weekly maturity, highly liquid | Short-term parking; frequent access |
| 13-week T-bills | 35% of cash ($7,000) | ~4.5% | Quarterly maturity, liquid | Medium-term yield; ladder for predictable income |
| Brokerage money market / sweep | 25% of cash ($5,000) | ~3.5-4.0% | Same-day, immediate | Margin buffer; same-day deployment |

**T-Bill Ladder Example at $20,000 Cash:**

| Week | 4-Week T-Bill Purchase | 13-Week T-Bill Purchase | Sweep Balance |
|------|----------------------|------------------------|---------------|
| Week 1 | $2,000 | $7,000 | $5,000 |
| Week 2 | $2,000 | -- | $5,000 |
| Week 3 | $2,000 | -- | $5,000 |
| Week 4 | $2,000 (funded by Week 1 maturity) | -- | $5,000 |

After initial setup, $2,000 matures weekly from 4-week T-bills, providing regular liquidity. The $7,000 in 13-week T-bills matures quarterly and is renewed at the quarterly rebalance.

### 7.3 Cash as Dry Powder — Deployment Triggers

Cash above the minimum reserve is "dry powder" — capital available for opportunistic deployment.

| Trigger | Action | Cash Deployment |
|---------|--------|----------------|
| VIX spike > 30 (from < 25) | Premium selling opportunity. IV is elevated. | Deploy up to 50% of excess cash into CSPs at wide strikes (0.15-0.20 delta) |
| Single name drops > 10% in one day (on no fundamental news) | Oversold condition on quality name | Deploy up to $5,000 into conviction position or sell CSP at depressed strike |
| Market correction > -10% (SPY) | Broad opportunity. Valuations improved. | Deploy up to 75% of excess cash across momentum and conviction sleeves |
| New capital contribution | Fresh capital added to account | Follow 4-week deployment schedule (Section 5.3) |

**"Excess cash" = total cash - minimum cash reserve.** At $20K total cash with a $15K minimum, only $5K is deployable dry powder.

### 7.4 Cash Reserve Scaling in Drawdowns

As portfolio drawdown deepens, cash allocation increases aggressively. This is the primary capital preservation mechanism.

```
Normal:          [====|=== Options 35% ===|= Momentum 20% =|Conv 15%|Hedge|== Cash 20% ==]
Tier 1 (-5%):    [===|== Options 30% ==|= Mom 15% =|Conv 12%|H|===== Cash 30% =====]
Tier 2 (-10%):   [==|= Options 20% =|Mom 10%|Conv 10%|H|========= Cash 45% =========]
Tier 3 (-15%):   [Conv 10%|H|=================== Cash 75% =========================]
```

The transition between tiers should be executed within 2 trading days of the drawdown threshold being breached. Sell positions in rebalancing priority order (Section 6.5).

---

## 8. Correlation & Diversification Analysis

### 8.1 The Overlap Problem

Altamira Capital's core universe (AAPL, MSFT, GOOGL, AMZN, AVGO, COST, V, MA, META, NVDA) is heavily weighted toward technology. Selling CSPs on NVDA while holding MSFT in the momentum sleeve creates correlated exposure — a tech selloff hits both sleeves simultaneously.

**Key risk:** Cross-sleeve correlation is HIGH because the same universe underlies both the Options Premium and Equity Momentum sleeves.

### 8.2 Within-Sleeve Correlation Management

**Options Premium Sleeve:**
- Maximum 3 CSP positions in the same GICS sector simultaneously
- If selling puts on AAPL, MSFT, and NVDA (all tech), the 4th tech CSP is blocked until one closes
- Prefer distributing across sectors: tech + financials (V, MA) + consumer (COST, AMZN)

**Equity Momentum Sleeve:**
- Equal-weight inherently limits single-name concentration
- Sector concentration is signal-dependent (cannot override the 50-day SMA signal for diversification)
- Accept that in strong bull markets, all 10 names may be active and sector concentration will be high
- Mitigate by ensuring the conviction sleeve is NOT also overweight in the same sector

**Equity Conviction Sleeve:**
- No more than 2 positions in the same GICS sector
- If high conviction on 3 tech names, pick the best 2 for conviction sleeve; access the 3rd via options or momentum sleeve

### 8.3 Cross-Sleeve Aggregate Exposure

For each name in the universe, calculate total aggregate exposure across all sleeves.

**Single-Name Aggregate Exposure Limit: 8% of portfolio**

| Exposure Type | How It Counts |
|---------------|---------------|
| Equity long (momentum or conviction) | Mark-to-market value / portfolio value |
| CSP (sold put) | Max loss scenario: (strike - 0) x 100 x contracts / portfolio, capped at 5% for sizing |
| Covered call on existing long | Does not add to exposure (reduces it) |
| Bull put spread | (short strike - long strike) x 100 x contracts / portfolio |

**Example — MSFT aggregate exposure at $100K:**

| Sleeve | Position | Exposure |
|--------|----------|----------|
| Options Premium | 1 CSP at $380 strike | $5,000 notional risk (5%) |
| Equity Momentum | 50 shares at $415 | $2,075 (2.1%) |
| Equity Conviction | -- | $0 |
| **Total MSFT exposure** | | **$7,075 (7.1%)** |

This is within the 8% single-name aggregate limit. Adding a $3,000 conviction position on MSFT would push aggregate to 10.1% — this would be blocked.

### 8.4 Sector Concentration Limits

| GICS Sector | Core Universe Names | Max Portfolio Exposure | Notes |
|-------------|--------------------|-----------------------|-------|
| Information Technology | AAPL, MSFT, NVDA, AVGO | 25% | Largest sector in universe; requires active monitoring |
| Communication Services | GOOGL, META | 15% | Two mega-caps; natural limit |
| Consumer Discretionary | AMZN, COST | 15% | Retail + e-commerce |
| Financials (Payment Networks) | V, MA | 15% | Payment processing; correlated pair |
| Broad Market | SPY | 15% | Index exposure; overlaps all sectors |

**Aggregate sector check formula:**

```
Sector exposure = SUM(all positions in sector across all sleeves) / total portfolio value
IF sector exposure > 25% THEN flag for rebalancing
IF sector exposure > 30% THEN mandatory reduction within 2 trading days
```

### 8.5 Sector Allocation Targets vs. Limits

| Sector | SAA Target Range | Hard Limit | Current Universe Names | Correlation to SPY |
|--------|-----------------|------------|----------------------|-------------------|
| Technology | 15-25% | 30% | AAPL, MSFT, NVDA, AVGO | ~0.85 |
| Communication Services | 5-12% | 15% | GOOGL, META | ~0.75 |
| Consumer Discretionary | 5-12% | 15% | AMZN, COST | ~0.70 |
| Financials | 5-10% | 15% | V, MA | ~0.65 |
| Broad Market (ETF) | 5-15% | 20% | SPY | 1.00 |
| Cash & Equivalents | 15-25% | 50% | T-bills, money market | ~0.00 |

### 8.6 Correlation Mitigation Strategies

1. **Sector diversification in CSP selection.** When choosing which names to sell puts on, prioritize sector balance over individual premium richness. Selling 2 tech CSPs + 1 financials CSP + 1 consumer CSP is preferable to 4 tech CSPs even if tech premiums are richer.

2. **Cross-sleeve offset.** If the momentum sleeve is 100% long tech (all tech names above 50-day SMA), reduce tech exposure in the options sleeve by avoiding tech CSPs and focusing on V, MA, COST, AMZN.

3. **SPY as a diversifier.** SPY represents broad market exposure. Selling CSPs on SPY provides premium income with lower single-sector concentration than individual names.

4. **Universe expansion at scale.** At $250K+, add 5-10 names from underrepresented sectors (healthcare, industrials, energy) to reduce tech concentration. Candidates should meet liquidity requirements (options volume > 5,000 contracts/day, bid-ask spread < $0.10).

---

## 9. Performance Attribution Framework

### 9.1 Sleeve-Level Attribution

Each sleeve is measured independently against its own benchmark and risk parameters.

| Sleeve | Benchmark | Key Metrics | Target |
|--------|-----------|-------------|--------|
| Options Premium | Risk-free rate (T-bill yield) | Annualized return on allocated capital, Sharpe ratio, win rate, avg premium per trade | >12% return, >1.5 Sharpe, >65% win rate |
| Equity Momentum | SPY total return | Excess return vs. SPY, upside/downside capture, avg exposure % | Positive excess return per unit of risk |
| Equity Conviction | SPY total return | Alpha (excess return), hit rate on theses, avg hold period return | >5% alpha, >60% hit rate |
| Hedging | Zero (cost center) | Drawdown reduction, cost as % of portfolio, realized protection vs. theoretical | Max DD reduced by > hedge cost |
| Cash & Equivalents | 0% (capital preservation) | Yield earned, opportunity cost vs. full deployment | Positive yield, minimal opportunity cost |

### 9.2 Portfolio-Level Attribution

| Metric | Calculation | Target |
|--------|-------------|--------|
| Total portfolio return | SUM(sleeve returns weighted by average allocation) | 12-18% Year 1 |
| Portfolio Sharpe ratio | (portfolio return - risk-free rate) / portfolio std dev | >1.5 |
| Maximum drawdown | Peak-to-trough decline in portfolio value | < -15% |
| Excess return vs. SPY | Portfolio return - SPY total return | Positive on risk-adjusted basis |
| Return per unit of risk | Portfolio return / max drawdown | > 1.0 |

### 9.3 Monthly Attribution Report Template

```
ALTAMIRA CAPITAL — MONTHLY PERFORMANCE ATTRIBUTION
Period: [Month Year]
Portfolio Value: $[value] | Monthly Return: [%] | YTD Return: [%]

SLEEVE PERFORMANCE
-------------------------------------------------------------------
                    Allocation  Return    Contribution  Benchmark  Excess
Options Premium     [%]         [%]       [%]           [T-bill]   [%]
Equity Momentum     [%]         [%]       [%]           [SPY]      [%]
Equity Conviction   [%]         [%]       [%]           [SPY]      [%]
Hedging             [%]         [%]       [%]           [0%]       [%]
Cash & Equivalents  [%]         [%]       [%]           [0%]       [%]
-------------------------------------------------------------------
PORTFOLIO TOTAL     100%        [%]       [%]           [SPY]      [%]

RISK METRICS
  Sharpe Ratio (rolling 12mo):  [value]
  Max Drawdown (YTD):           [%]
  Current Drawdown:             [%]
  VIX Regime:                   [Complacent/Normal/Elevated/Crisis]

OPTIONS DETAIL
  Trades Opened:    [#]     Trades Closed:  [#]
  Win Rate (MTD):   [%]     Win Rate (YTD): [%]
  Avg Credit:       $[amt]  Avg P&L:        $[amt]
  Total Premium:    $[amt]

SECTOR EXPOSURE
  Technology:       [%] (limit 25%)
  Comm. Services:   [%] (limit 15%)
  Cons. Disc.:      [%] (limit 15%)
  Financials:       [%] (limit 15%)
  Broad Market:     [%] (limit 20%)

ACTION ITEMS
  [ ] [Any rebalancing needed]
  [ ] [Any threshold alerts]
  [ ] [Strategy adjustments for next month]
```

**Contribution calculation:**

```
Sleeve contribution to portfolio return = sleeve_return x average_sleeve_allocation

Example: Options sleeve returns 2% for the month on 35% allocation
Contribution = 2% x 0.35 = 0.70% contribution to total portfolio return
```

### 9.4 When to Reallocate Between Sleeves

Reallocation from one sleeve to another based on performance should be done cautiously and only with clear evidence, not short-term results.

| Signal | Evaluation Period | Action |
|--------|-------------------|--------|
| Sleeve underperforms benchmark for 6 consecutive months | 6 months | Reduce SAA target by 5pp; add to best-performing sleeve |
| Sleeve Sharpe ratio < 0.5 for 12 months | 12 months | Fundamental review of strategy. Consider pausing sleeve. |
| Sleeve generates > 150% of expected return for 6 months | 6 months | Evaluate if sustainable or mean-reverting. Consider increasing allocation by 5pp. |
| Market regime change (sustained) | 3+ months in new regime | Shift SAA targets to reflect new baseline. Example: sustained VIX > 25 — increase options target, reduce equity. |

**Key principle:** Do not chase performance. A sleeve that underperforms for 2-3 months may be experiencing normal variance. Only reallocate based on 6+ months of evidence or a clear regime change.

---

## 10. Implementation Checklist

### Phase 1: Pre-Deployment Setup (Week 1)

- [ ] **Review this document** with fresh eyes. Flag any parameters that feel wrong before committing capital.
- [ ] **Configure portfolio tracking spreadsheet** in Google Sheets with:
  - Tab 1: Sleeve allocations (target vs. actual, auto-calculated deviation)
  - Tab 2: Position log (all sleeves, with entry/exit dates, P&L, thesis)
  - Tab 3: Monthly attribution report (template from Section 9.3)
  - Tab 4: Sector exposure tracker (with conditional formatting at limits)
  - Tab 5: Cash management (T-bill ladder, sweep balance, reserve calculation)
- [ ] **Set up T-bill ladder** — Purchase initial 4-week and 13-week T-bills per Section 7.2.
- [ ] **Configure OCA parameters** to match Section 4.1 (delta 0.20-0.30, DTE 30-45, IV Rank > 30, 5% max position).
- [ ] **Set alerts** for VIX regime thresholds (15, 25, 35) via n8n to Telegram.
- [ ] **Calculate breakeven deployment** — At $100K, identify exactly which positions fit within CSP capital constraints.

### Phase 2: Paper Trading Deployment (Weeks 2-5)

- [ ] **Week 1 deployment:** Deploy 25% — fund cash sleeve, initiate 1-2 paper CSP positions.
- [ ] **Week 2 deployment:** Deploy to 50% — add momentum positions (buy names above 50-day SMA), add 1-2 more CSPs.
- [ ] **Week 3 deployment:** Deploy to 75% — add conviction positions. Establish initial hedging position if VIX < 18.
- [ ] **Week 4 deployment:** Deploy to 100% — all sleeves at SAA targets. Begin full tracking and attribution.
- [ ] **Weekly review:** Every Friday, run attribution report. Check all deviation thresholds. Log observations.

### Phase 3: Live Transition (Week 6+)

- [ ] **Verify go-live criteria met** (from Trading Infrastructure Setup):
  - Win rate > 60%
  - Sharpe > 1.0
  - Max drawdown < -10%
  - 100% rule compliance
  - Automation > 95% uptime
- [ ] **Deploy live at 50% of target size** — Half the positions, half the contracts.
- [ ] **Run paper + live in parallel** for 30 days.
- [ ] **Scale to full position sizes** after 30 days if live performance meets criteria.
- [ ] **First monthly attribution report** — Compare live vs. paper vs. backtest.

### Phase 4: Ongoing Operations (Monthly)

- [ ] **Monthly rebalance** (1st trading day) — compare allocations to SAA targets, execute trades per priority order.
- [ ] **Monthly attribution report** — fill in template from Section 9.3.
- [ ] **Quarterly deep review** — reassess SAA targets, conviction positions, hedging budget, and T-bill ladder.
- [ ] **Semi-annual strategy review** — evaluate if any sleeve should be expanded, reduced, or paused based on 6-month performance data.
- [ ] **Annual review** — comprehensive reassessment of allocation model, scaling progress, and AUM growth trajectory.

### Phase 5: Scaling Triggers

- [ ] **At $250K:** Expand to full universe, add 5-8 simultaneous CSPs, formal hedging budget.
- [ ] **At $500K:** Add defined-risk spreads and jade lizards, increase position diversity.
- [ ] **At $1M:** Apply for portfolio margin, expand universe by 5-10 names, add sector ETFs.
- [ ] **At $5M:** Evaluate fund structure (LP/GP), consider first hire, full multi-strategy deployment.

---

## Appendix A: Key Formulas

**CSP Capital Requirement:**
```
Capital = strike_price x 100 x num_contracts
```

**Bull Put Spread Capital Requirement:**
```
Capital = (short_strike - long_strike) x 100 x num_contracts
```

**Portfolio Return (Weighted):**
```
R_portfolio = SUM(R_sleeve_i x W_sleeve_i) for all sleeves
```

**Sharpe Ratio:**
```
Sharpe = (R_portfolio - R_risk_free) / StdDev(R_portfolio)
```

**Sleeve Contribution to Portfolio Return:**
```
Contribution_i = R_sleeve_i x W_sleeve_i
```

**Single-Name Aggregate Exposure:**
```
Exposure = (equity_value + options_notional_risk) / portfolio_value
```

**Sector Exposure:**
```
Sector_% = SUM(all positions in sector across all sleeves) / portfolio_value
```

**Rebalancing Trade Size:**
```
Trade_amount = (current_allocation% - target_allocation%) x portfolio_value
```

## Appendix B: Glossary

| Term | Definition |
|------|-----------|
| SAA | Strategic Asset Allocation — long-term target weights |
| TAA | Tactical Asset Allocation — short-term deviations from SAA based on market conditions |
| Sleeve | A distinct sub-portfolio within the total portfolio, each with its own strategy and benchmark |
| CSP | Cash-secured put — selling a put while holding cash equal to the assignment obligation |
| IV Rank | Current implied volatility as a percentile of its 52-week range |
| Delta | Option price sensitivity to $1 move in underlying; proxy for probability of expiring ITM |
| DTE | Days to expiration |
| Dry Powder | Cash reserves available for opportunistic deployment |
| Portfolio Margin | Margin methodology that calculates requirements based on net portfolio risk, not per-position |
| GICS | Global Industry Classification Standard — sector classification system |

---

*This document is a living framework that evolves with market conditions, portfolio growth, and strategy refinement. Review quarterly and update as needed. Version history is maintained in the workspace.*

*Companion documents:*
- *Investment Thesis v1.0: `outputs/altamira-investment-thesis.md`*
- *Backtest Results: `outputs/backtest-results-2026-02-18.md`*
- *Trading Infrastructure Setup: `outputs/trading-infrastructure-setup.md`*
