# Altamira Capital — Risk Management Framework

**Version:** 1.0
**Date:** 2026-02-18
**Author:** Ricardo Landino, Founder
**Status:** Active
**Companion Documents:** Investment Thesis v1.0, Backtest Results (2026-02-18), Trading Infrastructure Setup v1.0

---

## 1. Executive Summary

### Purpose

This document defines the complete risk management framework for Altamira Capital. It translates the risk parameters established in the Investment Thesis v1.0 into an operational playbook with specific formulas, enforcement mechanisms, escalation triggers, and recovery protocols. Every rule in this framework has a concrete number attached to it. There is no ambiguity about what to do in any market scenario.

### Scope

This framework governs all trading activity across three strategies:

| Strategy | Risk Profile | Primary Risk |
|----------|-------------|--------------|
| Options Premium Selling (CSPs, spreads, jade lizards) | Defined loss per trade, concentrated tail risk | Assignment risk, correlation blowup |
| Equity Momentum (50-day MA) | Market directional, drawdown risk | Trend reversal, gap risk |
| Portfolio Hedging (SPY puts, VIX calls) | Cost drag in bull markets | Overspending on protection |

### Risk Philosophy

1. **Capital preservation is the primary constraint.** A 50% drawdown requires a 100% gain to recover. Avoiding deep drawdowns is the single highest-leverage activity.
2. **Risk is sized before entry, not managed after.** Every position has a defined maximum loss before the trade is placed.
3. **Rules are not guidelines.** When a stop-loss, circuit breaker, or drawdown tier is hit, the prescribed action is mandatory. No discretion, no exceptions.
4. **Compounding requires survival.** The $100K-to-$5M growth target demands ~50x capital growth. One catastrophic loss resets the clock by years. Protecting capital is not conservative — it is the prerequisite for the growth target.
5. **Automation enforces discipline.** Human psychology degrades under stress. The n8n + OCA stack enforces rules that the founder's psychology would otherwise override.

### Backtest Validation

This framework is calibrated against 2-year backtested results:

| Metric | Backtest Result | Framework Target |
|--------|----------------|-----------------|
| CSP win rate | 83.3% (15/18 trades) | >65% |
| CSP Sharpe ratio | 1.34 | >1.5 |
| CSP max drawdown | -0.26% | <-15% |
| Equity momentum return | 34.57% (18.05% annualized) | 12-18% Year 1 |
| Equity momentum max drawdown | -20.30% | <-15% (BREACH — see Section 4) |
| Equity momentum average exposure | 60.6% | 50-80% |
| Hedging cost | ~0.1% over 2 years | <1.0% per quarter |

**Critical finding:** The equity momentum strategy's -20.3% max drawdown exceeds the -15% portfolio-level capital preservation trigger. This framework addresses this gap with trailing stops and forced exits (Section 5).

---

## 2. Position Sizing Rules

### 2.1 Options Position Sizing (CSP / Spreads)

#### Formula: Max Loss Method

```
Max Contracts = Floor(Max Position Allocation / Max Loss Per Contract)

Where:
  Max Position Allocation = Portfolio Value x 5%
  Max Loss Per Contract (CSP) = (Strike Price - 0) x 100   [theoretical, but use stop-loss adjusted]
  Max Loss Per Contract (CSP, adjusted) = Credit Received x 200% x 100   [actual stop-loss]
  Max Loss Per Contract (Spread) = (Spread Width - Net Credit) x 100
```

#### Formula: Buying Power Method

```
Max Contracts = Floor(Available Buying Power x 30% / Buying Power Per Contract)

Where:
  Buying Power Per Contract (CSP) = Strike Price x 100   [cash-secured]
  Buying Power Per Contract (Spread) = Spread Width x 100
  Available Buying Power = Cash + Margin - Existing BP Usage
```

**Use the minimum of the two methods.** Never exceed either constraint.

#### Scaling Rules by Portfolio Size

| Portfolio Size | Max Single Position (5%) | Max Options Allocation (30%) | Max Contracts per Trade (Example: $100 strike CSP) | Min Position Size |
|---------------|------------------------|------------------------------|----------------------------------------------------|--------------------|
| $100K | $5,000 | $30,000 | 3 contracts | 1 contract |
| $250K | $12,500 | $75,000 | 7 contracts | 1 contract |
| $500K | $25,000 | $150,000 | 15 contracts | 2 contracts |
| $1M | $50,000 | $300,000 | 30 contracts | 3 contracts |
| $5M | $250,000 | $1,500,000 | 150 contracts | 5 contracts |

#### Concrete Examples

**Example 1: $100K Portfolio — AAPL CSP**

- AAPL trading at $240. Sell $225 put for $3.00 credit.
- Max position allocation: $100K x 5% = $5,000
- Stop-loss adjusted max loss per contract: $3.00 x 200% x 100 = $600
- Max contracts (loss method): Floor($5,000 / $600) = 8 contracts
- Buying power required per contract: $225 x 100 = $22,500
- Max contracts (BP method at 30%): Floor($30,000 / $22,500) = 1 contract
- **Result: 1 contract.** Buying power is the binding constraint at $100K.

**Example 2: $500K Portfolio — MSFT Bull Put Spread**

- MSFT trading at $420. Sell $400/$390 bull put spread for $2.50 net credit.
- Max position allocation: $500K x 5% = $25,000
- Max loss per contract: ($10 - $2.50) x 100 = $750
- Max contracts (loss method): Floor($25,000 / $750) = 33 contracts
- Buying power per contract: $10 x 100 = $1,000
- Max contracts (BP method at 30%): Floor($150,000 / $1,000) = 150 contracts
- **Result: 33 contracts.** Loss method is the binding constraint. Also verify total options allocation does not exceed 30% with existing positions.

**Example 3: $1M Portfolio — Jade Lizard on NVDA**

- NVDA trading at $140. Sell $125 put + sell $155/$160 call spread for $4.00 total credit.
- Max position allocation: $1M x 5% = $50,000
- Max loss (downside): ($125 - $4.00) x 100 = $12,100 per contract (if assigned at zero, theoretical)
- Max loss (stop-loss adjusted): $4.00 x 200% x 100 = $800 per contract
- Upside: Zero risk if credit > call spread width (here $4.00 < $5.00 spread, so $1.00 upside risk x 100 = $100)
- Max contracts (loss method): Floor($50,000 / $800) = 62 contracts
- Buying power per contract: $125 x 100 = $12,500 (put side)
- Max contracts (BP method at 30%): Floor($300,000 / $12,500) = 24 contracts
- **Result: 24 contracts.** Buying power is the binding constraint.

### 2.2 Equity Position Sizing (Conviction-Based Kelly Adaptation)

#### Formula: Modified Kelly Criterion

```
Kelly % = (Win Rate x Avg Win / Avg Loss - (1 - Win Rate)) / (Avg Win / Avg Loss)
Position Size = Portfolio Value x Kelly % x Conviction Scalar x Kelly Fraction

Where:
  Kelly Fraction = 0.25 (quarter-Kelly for conservatism)
  Conviction Scalar:
    High conviction = 1.0
    Medium conviction = 0.7
    Low conviction = 0.4
```

**Hard cap: No single equity position exceeds 5% of portfolio regardless of Kelly output.**

#### Backtest-Calibrated Parameters

From the equity momentum backtest (72.7% monthly win rate, 60.6% average exposure):

```
Win Rate = 0.727
Avg Win / Avg Loss ratio = 1.2 (estimated from momentum returns)
Kelly % = (0.727 x 1.2 - 0.273) / 1.2 = 0.499 = 49.9%
Quarter-Kelly = 12.5%
```

This produces sizing between 5.0% (low conviction) and 12.5% (high conviction) — but the 5% hard cap applies, so maximum is always 5% per name.

#### Equity Sizing Table

| Portfolio Size | High Conviction (5%) | Medium Conviction (3.5%) | Low Conviction (2%) |
|---------------|---------------------|--------------------------|---------------------|
| $100K | $5,000 | $3,500 | $2,000 |
| $250K | $12,500 | $8,750 | $5,000 |
| $500K | $25,000 | $17,500 | $10,000 |
| $1M | $50,000 | $35,000 | $20,000 |
| $5M | $250,000 | $175,000 | $100,000 |

### 2.3 Scaling Rules as Portfolio Grows

| Portfolio Milestone | Adjustments |
|--------------------|-------------|
| **$100K (Launch)** | Max 3 simultaneous CSP positions. Max 5 equity positions. Conservative delta (0.20). Focus on most liquid names (SPY, AAPL, MSFT). |
| **$250K** | Expand to 5 simultaneous CSPs. Add spreads and jade lizards. Expand equity universe to full 11 names. |
| **$500K** | Introduce portfolio margin (if eligible). Reduce single-position cap to 4%. Add sector-rotation tactical trades. Increase hedging budget to 0.75%/quarter. |
| **$1M** | Full strategy deployment. Consider adding short exposure (tactical). Evaluate portfolio margin optimization. Increase minimum position sizes for meaningful impact. |
| **$5M** | Formal fund structure evaluation. Reduce single-position cap to 3%. Hire quantitative analyst. Institutional-grade reporting. Increase hedging budget to 1.0%/quarter. |

---

## 3. Risk Limits & Constraints

### 3.1 Single Position Limits

| Strategy Type | Max % of Portfolio | Max # of Contracts/Shares | Enforcement |
|--------------|-------------------|---------------------------|-------------|
| CSP (single name) | 5% of portfolio by buying power | See sizing table | Pre-trade OCA check |
| Bull put spread | 5% by max loss | See sizing table | Pre-trade OCA check |
| Jade lizard | 5% by buying power (put side) | See sizing table | Pre-trade OCA check |
| Equity long (high conviction) | 5% by market value | Calculated at entry | Pre-trade check |
| Equity long (medium conviction) | 3.5% by market value | Calculated at entry | Pre-trade check |
| Equity long (low conviction) | 2% by market value | Calculated at entry | Pre-trade check |
| Hedge position (SPY/VIX) | 2% by premium cost | Based on quarterly budget | Quarterly allocation |

### 3.2 Sector Concentration Limits

| Constraint | Limit | Measurement | Enforcement |
|-----------|-------|-------------|-------------|
| Max sector exposure (equities) | 25% of portfolio | Sum of all equity positions in sector by market value | Weekly review, pre-trade check |
| Max sector exposure (options) | 25% of notional | Sum of all options positions in sector by notional exposure | Weekly review, pre-trade check |
| Max correlated positions per sector | 3 names | Count of distinct underlyings with open positions in same sector | Pre-trade block |
| Max technology sector (special rule) | 35% combined equity + options | Given core universe is tech-heavy (AAPL, MSFT, GOOGL, AMZN, AVGO, META, NVDA = 7/11 names) | Weekly review with rebalance trigger |

**Sector classification for core universe:**

| Sector | Names | Max Combined Positions |
|--------|-------|----------------------|
| Technology | AAPL, MSFT, GOOGL, AMZN, META, NVDA, AVGO | 3 equity + 3 options = 6 max |
| Financial Services | V, MA | 2 equity + 2 options = 4 max |
| Consumer Defensive | COST | 1 equity + 1 options = 2 max |
| Index | SPY | Hedging only |

### 3.3 Correlation Constraints

**Definition:** Two positions are "correlated" if their 60-day rolling correlation exceeds 0.70.

**Measurement method:**
1. Pull 60-day daily returns for all open positions.
2. Calculate pairwise Pearson correlation matrix.
3. Flag any pair with |r| > 0.70.
4. Count flagged pairs per sector.

**Limits:**
- Max 3 correlated positions (|r| > 0.70) in the same sector
- Max 5 correlated positions (|r| > 0.70) across entire portfolio
- If adding a new position would breach either limit, the trade is blocked

**Known high-correlation pairs in core universe (historical):**

| Pair | Typical Correlation | Treatment |
|------|-------------------|-----------|
| AAPL / MSFT | 0.75-0.85 | Count as correlated. Max 1 CSP + 1 equity between them. |
| GOOGL / META | 0.70-0.80 | Count as correlated. Max 1 CSP + 1 equity between them. |
| NVDA / AVGO | 0.75-0.85 | Count as correlated (semiconductor). Max 1 CSP + 1 equity between them. |
| V / MA | 0.85-0.95 | Highly correlated. Treat as single position for concentration purposes. |

### 3.4 Portfolio-Level Greeks Limits

| Greek | Limit | Rationale | Monitoring |
|-------|-------|-----------|------------|
| **Net Delta** | -0.30 to +0.60 per $100K portfolio value | Limits directional exposure; net short delta from CSPs balanced by long equity | Daily dashboard |
| **Net Gamma** | > -0.05 per $100K portfolio value | Prevents convexity blowup on large moves | Daily dashboard |
| **Net Theta** | +$50 to +$200 per $100K portfolio value | Ensures positive time decay; caps overexposure to short options | Daily dashboard |
| **Net Vega** | > -$500 per $100K portfolio value | Limits exposure to volatility expansion | Daily dashboard, tighten when VIX < 15 |

**Scaling:** All Greeks limits scale linearly with portfolio size. A $500K portfolio has limits 5x the $100K values.

**Breach protocol:**
1. If any Greek breaches its limit, no new positions may be opened.
2. Within 1 trading day, adjust or close positions to bring the Greek within limits.
3. If unable to adjust within 1 day, close the most recent position that contributed to the breach.

### 3.5 Liquidity Requirements

| Parameter | Minimum Requirement | Rationale |
|-----------|-------------------|-----------|
| Open interest (options) | > 500 contracts at target strike | Ensures ability to exit without significant slippage |
| Bid-ask spread (options) | < $0.10 or < 5% of mid price | Controls entry/exit cost |
| Average daily volume (equity) | > 1M shares | Ensures equity positions can be liquidated quickly |
| Options volume (daily) | > 100 contracts at target strike | Confirms active market |

**If a position fails any liquidity requirement, do not enter the trade.** The core universe (AAPL, MSFT, GOOGL, AMZN, AVGO, COST, V, MA, META, NVDA, SPY) is selected specifically for liquidity, but individual strikes/expirations can still be illiquid — always verify.

### 3.6 Cash Reserve Requirements

| Market Regime | Minimum Cash Reserve | Maximum Deployed Capital |
|--------------|---------------------|------------------------|
| Normal (VIX 15-25) | 15% | 85% |
| Low volatility (VIX < 15) | 20% | 80% |
| Elevated volatility (VIX 25-35) | 25% | 75% |
| Crisis (VIX > 35) | 40% | 60% |
| Drawdown Tier 2 (-10%) | 40% | 60% |
| Drawdown Tier 3 (-15%) | 60% | 40% |

---

## 4. Drawdown Management Protocol

### 4.1 Three-Tier System

Drawdowns are measured from the portfolio's all-time high watermark. The watermark is updated at end-of-day only (no intraday resets).

#### Tier 1: Yellow Alert (-5% from peak)

**Trigger:** Portfolio value declines 5% from all-time high watermark.

**Mandatory actions:**
1. **Reduce all new position sizes by 25%.** Apply 0.75 multiplier to all sizing calculations.
2. **No new risk.** Do not open any new positions for 2 trading days.
3. **Review all open positions.** Score each position 1-5 on conviction. Close any position scoring below 3.
4. **Increase cash reserve to 25%** regardless of VIX regime.
5. **Add hedging.** Purchase SPY puts if not already hedged (0.20 delta, 30-45 DTE, up to 1% of portfolio in premium).
6. **Log the event.** Record date, portfolio value, positions, and the market context that caused the drawdown.

**Duration:** Tier 1 restrictions remain in place until the portfolio recovers to within 2.5% of the watermark.

#### Tier 2: Orange Alert (-10% from peak)

**Trigger:** Portfolio value declines 10% from all-time high watermark.

**Mandatory actions:**
1. **Close lowest-conviction 50% of positions.** Rank all positions by conviction score. Close the bottom half.
2. **Reduce remaining position sizes by 50%.** Apply 0.50 multiplier to all sizing calculations.
3. **Increase cash reserve to 40%.** Sell positions as needed to reach this level.
4. **Increase hedging to 2% of portfolio.** Double the hedging allocation.
5. **No new positions for 5 trading days.** Absolute freeze on new risk.
6. **Conduct root cause analysis.** Document: Was this market-wide or idiosyncratic? Did risk rules function? Were any rules violated?
7. **Review all stop-losses.** Tighten equity stops from -10% to -7%.

**Duration:** Tier 2 restrictions remain for minimum 10 trading days, even if the portfolio recovers. This prevents premature re-risking.

#### Tier 3: Red Alert — Capital Preservation Mode (-15% from peak)

**Trigger:** Portfolio value declines 15% from all-time high watermark.

**Mandatory actions:**
1. **Close ALL options positions.** No exceptions. Liquidate all CSPs, spreads, and multi-leg positions.
2. **Close all equity positions below 50-day MA.** Only hold equity positions where the underlying is above its 50-day moving average.
3. **Increase cash reserve to 60%.** Minimum.
4. **No new positions for 20 trading days.** Absolute trading halt on new risk.
5. **Maintain hedges only.** SPY puts and VIX calls are the only permissible open positions.
6. **Conduct comprehensive strategy review.** Re-evaluate all strategy parameters, position sizing, and correlation assumptions. Document findings in a formal post-mortem.
7. **Consider pausing live trading.** If the drawdown is driven by rule violations or emotional trading, return to paper trading until discipline is restored.

**Duration:** Tier 3 restrictions remain for minimum 20 trading days. Re-risking requires meeting all of the following criteria:
- Portfolio has recovered to within 10% of watermark
- 20 trading days have elapsed since Tier 3 trigger
- Root cause analysis is complete and documented
- Any identified rule failures are fixed
- At least 5 trading days of paper trading confirm system integrity

### 4.2 Recovery Protocols

| Recovery From | Re-Risking Schedule | Sizing Multiplier | Duration |
|--------------|--------------------|--------------------|----------|
| Tier 1 | Resume normal sizing when within 2.5% of watermark | 0.75 → 1.0 (immediate) | 2-5 trading days |
| Tier 2 | Week 1: 25% of normal sizing. Week 2: 50%. Week 3: 75%. Week 4: 100%. | 0.25 → 0.50 → 0.75 → 1.0 | 4 weeks minimum |
| Tier 3 | Week 1-2: Paper trading only. Week 3: 25% of normal sizing. Week 4: 50%. Week 5-6: 75%. Week 7+: 100%. | 0.0 → 0.25 → 0.50 → 0.75 → 1.0 | 7 weeks minimum |

### 4.3 Circuit Breakers

| Circuit Breaker | Trigger | Action |
|----------------|---------|--------|
| **Daily loss limit** | Portfolio declines 2% in a single trading day | Halt all new trades for remainder of day. Review all positions at market close. |
| **Weekly loss limit** | Portfolio declines 3% in a single week (Mon-Fri) | No new positions for the following week. Review all positions. Reduce sizing by 25%. |
| **Monthly loss limit** | Portfolio declines 5% in a single calendar month | Trigger Tier 1 protocol regardless of distance from watermark. Full position review. |
| **Consecutive loss limit** | 5 consecutive losing trades (any strategy) | Halt trading for 3 trading days. Review trade journal. Identify if the edge has degraded. |
| **Single-day options loss** | Any single options position loses > 3% of portfolio value in one day | Immediately close the position. No adjustment, no waiting. |

### 4.4 When to Stop Trading Entirely

Stop all live trading and return to paper trading if ANY of the following occur:

1. **Portfolio drawdown exceeds -20%.** This exceeds the maximum tolerable loss.
2. **Three consecutive months of negative returns.** The edge may have degraded or market regime has shifted.
3. **Repeated rule violations.** Two or more intentional overrides of risk management rules in a 30-day period.
4. **Technology failure causes a realized loss.** If a missed stop-loss or failed alert results in a loss exceeding 2% of portfolio.
5. **Personal judgment is compromised.** Self-assessed emotional state prevents rational decision-making (revenge trading, euphoria, panic).

**Re-entry criteria after full stop:**
- Minimum 2 weeks paper trading
- All paper trades must follow this framework
- Paper trading Sharpe > 1.0 over the period
- Root cause of the stop is documented and resolved
- Self-assessment confirms emotional readiness

---

## 5. Stop-Loss & Exit Rules

### 5.1 Cash-Secured Puts (CSPs)

| Exit Trigger | Condition | Action | Timing |
|-------------|-----------|--------|--------|
| **Profit target** | P&L reaches 50% of max credit received | Close position (buy to close) | Immediately upon trigger |
| **Stop-loss** | Loss reaches 200% of credit received | Close position (buy to close) | Immediately upon trigger; no waiting for recovery |
| **Delta breach** | Position delta exceeds 0.50 | Close or roll | Within 1 hour of breach |
| **DTE threshold** | DTE < 10 and profit < 30% of max | Close position | At next trading opportunity |
| **DTE expiration** | DTE < 5 | Close position regardless of P&L | No holding through final week unless > 80% profit captured |
| **Earnings conflict** | Earnings date falls within DTE | Close before earnings | 1 trading day before earnings (unless explicitly planned as earnings trade) |
| **IV collapse** | IV Rank drops below 15th percentile | Close position; edge has diminished | Within 1 trading day |

**Rolling rules (CSPs only):**
- Roll only if the underlying thesis remains intact and the move is due to broad market decline (not stock-specific deterioration).
- Roll down and out: Move strike down 1-2 strikes, extend DTE by 14-30 days.
- Net credit requirement: The roll must generate a net credit. If it cannot, do not roll — close the position.
- Maximum rolls: 2 per position. If a position has been rolled twice and is still losing, close it.
- Never roll past 60 DTE total from original entry.

**Assignment handling:**
- If assigned, immediately evaluate the position as a new equity holding.
- If the stock is above the 50-day MA and in the core universe: Hold and sell covered calls.
- If the stock is below the 50-day MA or deteriorating fundamentally: Sell the shares at next open.
- Set a -10% stop-loss from assignment price on all assigned positions.

### 5.2 Equity Momentum (50-Day MA Strategy)

| Exit Trigger | Condition | Action | Timing |
|-------------|-----------|--------|--------|
| **MA crossover (primary)** | Price closes below 50-day MA | Exit full position | At next rebalance date or within 2 trading days |
| **Trailing stop** | Position declines 8% from highest close since entry | Exit full position | Immediately upon trigger (intraday or close) |
| **Hard stop** | Position declines 10% from entry price | Exit full position | Immediately upon trigger |
| **Sector rotation** | Sector falls out of top 3 by momentum | Reduce position by 50% | At next rebalance date |
| **Consecutive closes below MA** | 3 consecutive closes below 50-day MA | Exit immediately, do not wait for rebalance | Next trading day open |
| **Gap down** | Stock gaps down > 5% on open | Sell 50% immediately, assess remainder | At open |

**Rebalance cadence:** Every 20 trading days, or upon any exit trigger, whichever comes first.

**Re-entry rules:**
- After a stop-loss exit, do not re-enter for 10 trading days minimum.
- After an MA crossover exit, re-enter when price closes above 50-day MA for 3 consecutive days.
- After a gap-down exit, re-enter only after a thorough fundamental review.

### 5.3 Hedging Positions

| Trigger | Action | Rationale |
|---------|--------|-----------|
| **VIX < 15** | Add SPY put hedges (0.20 delta, 30-45 DTE) | Cheap protection during complacency |
| **VIX 15-20** | Maintain existing hedges, do not add | Normal regime; hedging cost is moderate |
| **VIX 20-25** | Maintain existing hedges, begin evaluating removal | Protection becoming expensive |
| **VIX > 25** | Remove hedges purchased at lower VIX (take profit on hedge gains); shift to VIX call spreads for continued protection | Monetize existing hedges; VIX calls are more capital-efficient at elevated levels |
| **VIX > 35** | Liquidate all VIX positions (take profit); maintain only SPY put spreads | VIX mean-reversion risk; lock in hedge gains |
| **Portfolio at Tier 2+ drawdown** | Double hedging allocation to 2% of portfolio | Maximum protection during stress |
| **Quarterly hedge roll** | Roll SPY puts 7 DTE before expiration to next 30-45 DTE cycle | Maintain continuous protection |

**Hedging budget:** 0.5-1.0% of portfolio per quarter in normal conditions. This is a cost center — track it explicitly.

**Conditional hedging (from backtest recommendation):** In bull markets, hedging has minimal impact (~0.1% cost over 2 years). Focus hedging spend on periods when VIX < 18, where the cost of protection is lowest and the asymmetric payoff is highest.

### 5.4 Time-Based Forced Reviews

| DTE Remaining | Required Action |
|--------------|-----------------|
| 21 DTE | Review all options positions. Any position below 30% of max profit should be evaluated for early exit. |
| 14 DTE | Close any position that is not profitable. Theta acceleration favors closing and re-opening a new 30-45 DTE cycle. |
| 10 DTE | Close all positions unless > 80% of max profit is captured and the position is safely OTM (delta < 0.15). |
| 7 DTE | Mandatory close of all remaining positions. No exceptions. |
| Earnings within 5 days | Review all positions on the underlying. Close unless the position is an explicit earnings trade. |

---

## 6. Stress Testing & Scenario Analysis

### 6.1 Scenario Definitions

Each scenario is modeled against the current framework rules to evaluate whether the portfolio survives and how the drawdown protocols activate.

#### Scenario 1: COVID-Style Crash (-34% in 23 trading days)

**Market conditions:** S&P 500 falls 34% over 23 trading days. VIX spikes from 15 to 82. Correlation goes to 1.0 across all equities.

| Day | Market Move | Portfolio Impact | Framework Response |
|-----|-----------|------------------|-------------------|
| Day 1-3 | SPY -7% | CSPs: Delta surges past 0.50 on all positions. Equity: -4% (60% exposure). **Portfolio: ~-5%** | **Tier 1 triggered.** Close all CSPs (delta breach). Reduce equity sizing 25%. Add hedges. |
| Day 4-7 | SPY -12% cumulative | Remaining equity: -8% from peak. Hedges partially offset. **Portfolio: ~-8%** | Daily circuit breaker likely hit (2%/day). Tighten stops to -7%. |
| Day 8-12 | SPY -20% cumulative | Equity stops hit (-10% from entry). Most equity closed. **Portfolio: ~-10%** | **Tier 2 triggered.** Close 50% of remaining positions. Cash to 40%. No new risk for 5 days. |
| Day 13-23 | SPY -34% cumulative | Only hedges and highest-conviction positions remain. Hedges gain significantly. **Portfolio: ~-12 to -14%** | If -15% hit: **Tier 3 triggered.** All options closed. 60% cash. 20-day trading halt. |

**Survival assessment:** Portfolio survives with -12% to -14% drawdown (vs. -34% market). Framework prevents catastrophic loss through cascading protective actions. The 50-day MA exit removes equity exposure early in the decline.

#### Scenario 2: 2022 Rate Hike Bear Market (-25% over 10 months)

**Market conditions:** Slow grind lower. SPY falls 25% over 10 months. VIX ranges 20-35. No single-day crash, but persistent selling.

| Month | Market Move | Portfolio Impact | Framework Response |
|-------|-----------|------------------|-------------------|
| Month 1-2 | SPY -5% | CSPs: Mixed results; some stop-losses hit. Equity momentum: Partially invested. **Portfolio: ~-3%** | CSP stop-losses fire normally. Equity exposure reduces as stocks fall below 50-day MA. |
| Month 3-4 | SPY -10% | CSPs: Elevated VIX (25-35) triggers 25% sizing reduction. Equity: Most positions exited (below MA). **Portfolio: ~-5%** | **Tier 1 triggered.** Reduce sizing 25%. Increase hedging. Cash rises to 25%+. |
| Month 5-7 | SPY -18% | Minimal exposure. Portfolio mostly cash + hedges. **Portfolio: ~-7 to -9%** | If -10% hit: **Tier 2 triggered.** Mostly academic — few positions remain. Continue cash accumulation. |
| Month 8-10 | SPY -25% | Portfolio nearly fully in cash. Hedges expiring profitably, rolled monthly. **Portfolio: ~-8 to -11%** | Cash provides dry powder for recovery. Framework prevented participation in the bulk of the decline. |

**Survival assessment:** Portfolio drawdown of -8% to -11% vs. -25% market decline. The 50-day MA signal is the primary defense in slow bear markets, removing equity exposure gradually. CSP sizing reduction at VIX 25-35 limits options losses.

#### Scenario 3: Flash Crash (5%+ single-day decline)

**Market conditions:** SPY drops 5-7% in a single day. VIX spikes from 18 to 40+.

| Time | Event | Impact | Framework Response |
|------|-------|--------|-------------------|
| 9:30 AM | SPY gaps down -3% at open | CSP deltas spike. Equity positions gap down. | Monitor. Do not panic sell into the gap. |
| 10:00 AM | SPY down -5% | CSP delta breach (>0.50) on 2-3 positions. Equity trailing stops hit on volatile names. | Close CSPs with delta > 0.50. Equity stops fire automatically. |
| 11:00 AM | SPY down -6% | **Daily circuit breaker hit (2%).** | **Halt all new trades.** Review at close. |
| 4:00 PM | SPY closes -5.5% | Portfolio: ~-3% to -4% | Likely **Tier 1 triggered** depending on starting position. Execute Tier 1 protocol. |

**Survival assessment:** Single-day losses capped at -3% to -4% by combination of delta-based exits, trailing stops, and circuit breakers. Flash crashes are recoverable — the key is preventing emotional trading during the event.

#### Scenario 4: Sector Rotation (Technology -15% in 30 days)

**Market conditions:** Tech sector declines 15% over 30 days while SPY drops only 5%. Rotation into value/defensive.

| Week | Event | Impact | Framework Response |
|------|-------|--------|-------------------|
| Week 1 | Tech -5% | 3-4 tech positions hit trailing stops. CSPs on tech names see delta pressure. | Close stopped equity positions. Monitor CSP deltas. |
| Week 2 | Tech -10% | Tech sector exposure drops naturally as stops fire. Remaining tech CSPs at risk. | Close CSPs on tech names with delta > 0.40. Sector limit (35% tech) may be breached if concentrated. |
| Week 3-4 | Tech -15% | Most tech exposure eliminated by stops. Non-tech positions (V, MA, COST) stable or positive. | Rebalance toward non-tech positions. Portfolio drawdown limited to -4% to -7% depending on initial tech exposure. |

**Survival assessment:** The 3-name-per-sector correlation limit and 35% tech cap are the primary defenses. If properly enforced, tech-specific drawdown is contained to -4% to -7% even when tech falls -15%.

#### Scenario 5: VIX Spike (15 to 40 in 1 week)

**Market conditions:** VIX triples in one week, implying extreme fear. SPY may or may not have declined proportionally.

| Day | VIX Level | Framework Action |
|-----|-----------|-----------------|
| Day 1 | VIX 20 | Enter elevated volatility regime. Reduce new position sizing by 25%. |
| Day 2-3 | VIX 25-30 | CSP premium selling becomes more attractive BUT risk is higher. Continue 25% size reduction. |
| Day 4-5 | VIX 35+ | **Crisis regime.** Reduce sizing by 50%. Liquidate VIX hedges (take profit). Maintain SPY put spreads. |
| Day 5-7 | VIX 40+ | No new positions. Existing CSPs likely near stop-losses. Close any position where the premium selling edge has been overwhelmed by realized volatility. |

**Survival assessment:** VIX spikes create opportunity (elevated premiums) and risk (larger moves). The framework's VIX-adjusted sizing prevents overexposure during the spike. Cash reserves increase automatically, creating dry powder for deployment once VIX begins mean-reverting.

### 6.2 Stress Test Schedule

| Frequency | Test | Method |
|-----------|------|--------|
| Monthly | Re-run all 5 scenarios against current portfolio composition | Spreadsheet model or Python script |
| Quarterly | Backtest current parameters against most recent 6 months of data | Backtest automation scripts |
| After any Tier 2+ event | Full scenario re-run with updated parameters | Comprehensive review |
| Annually | Historical stress test against all major drawdowns since 2008 | Extended backtest |

---

## 7. Operational Risk Controls

### 7.1 Key-Person Risk Mitigation

Altamira Capital is a solo-founder firm. Ricardo Landino is the sole decision-maker, operator, and risk manager. This creates concentration risk that must be mitigated.

| Risk | Mitigation | Implementation |
|------|-----------|----------------|
| **Incapacitation (illness, injury)** | All positions have defined exits (stop-losses, profit targets). GTC (Good-Til-Cancelled) orders placed for all exits at trade entry. | Set GTC stop-loss and profit target orders immediately upon opening every position. |
| **Unavailability (travel, family emergency)** | n8n automation monitors positions and sends Telegram alerts. If unreachable for 48+ hours, all options positions should have been sized to survive to expiration without action. | Ensure no single options position can lose more than 3% of portfolio if held to expiration. |
| **Decision fatigue** | Maximum 3 new trades per day. No trading in the first 15 minutes or last 15 minutes of the session. No trading after a Tier 1+ drawdown event without a mandatory 2-day cooling period. | Self-enforced with trade journal tracking. |
| **Death/permanent incapacitation** | Maintain a "dead man's switch" document with: brokerage login, position summary, instructions to close all positions and withdraw to bank. Share with Marian. | Create and update quarterly. Store in shared secure location. |
| **Knowledge loss** | All strategies, parameters, and rules documented in this framework and the Investment Thesis. n8n workflows are self-documenting. | Maintain documentation currency. |

### 7.2 Technology Failure Protocols

| Failure Scenario | Detection | Response | Fallback |
|-----------------|-----------|----------|----------|
| **Broker outage (E-Trade down)** | Unable to access E-Trade Pro, API returns errors, website inaccessible | Do not attempt to trade. Wait for service restoration. If positions are at risk, call E-Trade broker line (1-800-387-2331). | Phone trading through E-Trade. All GTC orders remain active on exchange even during platform outage. |
| **API failure (E-Trade API)** | n8n workflows error. API returns 500/503 errors. OAuth token refresh fails. | Switch to manual monitoring via E-Trade Pro desktop. Manually check positions against dashboard. | E-Trade Pro desktop platform + Power E-Trade web. |
| **n8n downtime** | No Telegram alerts. Workflow dashboard shows failures. | Switch to manual monitoring. Check positions via E-Trade Pro every 2 hours during market hours. Set phone alarms for position check intervals. | Manual monitoring checklist (see Section 8). |
| **Data feed failure (FMP/Massive.com)** | OCA cannot run. Stale data in dashboards. API key errors. | Do not open new positions based on stale data. Monitor existing positions manually. | E-Trade Pro provides real-time quotes and options chains (less granular than Massive.com but functional). |
| **Internet outage** | Complete loss of connectivity | Use mobile data (phone hotspot) as primary backup. If total connectivity loss, call E-Trade to manage positions by phone. | Phone trading + mobile data. |
| **Power outage** | Desktop/server offline | Laptop battery provides 2-4 hours. Switch to mobile E-Trade app + phone trading. | Mobile app + phone trading. |
| **Google Sheets failure** | Trade journal inaccessible | Log trades in a local text file. Reconcile when service restores. | Local backup log. |

### 7.3 Data Integrity Checks

| Check | Frequency | Method | Action on Failure |
|-------|-----------|--------|-------------------|
| Position reconciliation | Daily at market close | Compare n8n-reported positions with E-Trade account positions | Correct discrepancies immediately. If n8n is wrong, re-sync from E-Trade. |
| P&L reconciliation | Daily at market close | Compare calculated P&L with E-Trade reported P&L | Investigate any difference > $50 or > 0.5% of position value. |
| Greeks validation | Daily when positions are open | Compare n8n/OCA Greeks with E-Trade Pro Greeks | Investigate any delta difference > 0.05 or theta difference > 10%. |
| Cash balance check | Daily pre-market | Compare expected cash (from n8n) with E-Trade cash balance | Investigate any difference > $100. |
| Historical data integrity | Weekly | Spot-check FMP data against a second source (Yahoo Finance or E-Trade) for 2-3 random tickers | If discrepancy found, flag the data source as unreliable and cross-reference before relying on it. |

### 7.4 Manual Override Procedures

Automation can fail or produce incorrect outputs. The following rules govern when and how to override automated systems.

**When to override:**
- Automated system recommends a trade that violates a risk limit (should not happen if pre-trade checks are working — investigate the failure)
- Market conditions are unprecedented and not captured by any scenario (e.g., market halt, geopolitical black swan)
- Data feed is clearly wrong (stale prices, impossible Greeks values)

**Override protocol:**
1. **Document the override before executing.** Write down: what the system recommended, why you are overriding, what you are doing instead.
2. **Execute the override manually** via E-Trade Pro (not through n8n/API to avoid propagating errors).
3. **Set a 24-hour review.** Re-evaluate the override the next day with fresh eyes.
4. **Fix the root cause.** If the override was due to a system failure, fix the automation within 48 hours.
5. **If you override more than twice in a month,** investigate whether the system needs fundamental redesign.

---

## 8. Monitoring & Reporting

### 8.1 Daily Risk Dashboard Metrics

The following metrics must be calculated and reviewed every trading day before market open (pre-market) and after market close (post-market).

**Pre-Market Dashboard (by 9:15 AM ET):**

| Metric | Source | Action Trigger |
|--------|--------|---------------|
| VIX level and overnight change | FMP API / Market Commenter | Adjust sizing regime if VIX crossed a threshold overnight |
| Portfolio value (prior close) | E-Trade API | Check drawdown distance from watermark |
| Distance from high watermark | Calculated | Determine current drawdown tier |
| Open positions summary | E-Trade API | Verify all positions match expectations |
| Positions with earnings within 5 days | Earnings Alpha | Close or evaluate pre-earnings |
| Overnight news on holdings | Market Commenter | Flag material news that may require action at open |

**Post-Market Dashboard (by 5:00 PM ET):**

| Metric | Source | Action Trigger |
|--------|--------|---------------|
| Daily P&L ($ and %) | E-Trade API | Circuit breaker check (-2% daily loss) |
| Weekly P&L ($ and %) | Calculated | Circuit breaker check (-3% weekly loss) |
| Monthly P&L ($ and %) | Calculated | Circuit breaker check (-5% monthly loss) |
| Portfolio net delta | E-Trade API / OCA | Flag if outside -0.30 to +0.60 per $100K |
| Portfolio net theta | E-Trade API / OCA | Verify positive; flag if outside +$50 to +$200 per $100K |
| Portfolio net vega | E-Trade API / OCA | Flag if below -$500 per $100K |
| Sector exposure breakdown | Calculated | Flag any sector > 25% (tech > 35%) |
| Options allocation % | Calculated | Flag if > 30% |
| Cash reserve % | E-Trade API | Flag if below regime-adjusted minimum |
| Positions at profit target (>50%) | Calculated | Queue for closing tomorrow |
| Positions at stop-loss (>200% credit) | Calculated | Should have been closed; investigate if still open |
| Positions with DTE < 14 | Calculated | Review for early close |
| Correlation matrix (top pairs) | Calculated weekly | Flag new pairs > 0.70 |

### 8.2 Weekly Risk Review Checklist

Complete every Friday after market close or Saturday morning.

```
WEEKLY RISK REVIEW — Week of [DATE]

PERFORMANCE
[ ] Weekly return: ___% ($_____)
[ ] MTD return: ___% ($_____)
[ ] YTD return: ___% ($_____)
[ ] Distance from watermark: ___%
[ ] Drawdown tier: [None / Tier 1 / Tier 2 / Tier 3]

POSITIONS
[ ] Number of open positions: ___
[ ] Positions opened this week: ___
[ ] Positions closed this week: ___ (Win: ___ / Loss: ___)
[ ] Win rate this week: ___%
[ ] Largest win: $_____ (ticker: ___)
[ ] Largest loss: $_____ (ticker: ___)

RISK LIMITS
[ ] Any position > 5% of portfolio? [Y/N] — If Y, which: ___
[ ] Any sector > 25% (tech > 35%)? [Y/N] — If Y, which: ___
[ ] Options allocation: ___% (limit: 30%)
[ ] Cash reserve: ___% (minimum: ___% based on VIX regime)
[ ] Portfolio delta: ___ (limit: -0.30 to +0.60 per $100K)
[ ] Portfolio theta: $___ /day (target: +$50 to +$200 per $100K)
[ ] Any correlation breach (>0.70)? [Y/N] — If Y, which pairs: ___

RULE COMPLIANCE
[ ] Any risk management rule violated this week? [Y/N]
[ ] If Y, document: ___
[ ] Any manual overrides this week? [Y/N]
[ ] If Y, document: ___
[ ] All GTC stop-loss orders in place? [Y/N]

NEXT WEEK
[ ] Earnings on any holdings next week? [Y/N] — If Y, action plan: ___
[ ] Economic events next week (FOMC, CPI, etc.)? [Y/N] — Impact: ___
[ ] Positions to close next week (DTE, profit target, etc.): ___
[ ] Available capital for new positions: $_____

NOTES
___________________________________________
```

### 8.3 Monthly Risk Report Template

Generate on the 1st trading day of each month for the prior month.

```
MONTHLY RISK REPORT — [MONTH YEAR]

1. PERFORMANCE SUMMARY
   - Monthly return: ___% ($_____)
   - Benchmark (SPY) return: ___%
   - Excess return: ___%
   - Sharpe ratio (rolling 3-month): ___
   - Max drawdown this month: ___%
   - Distance from all-time watermark: ___%

2. STRATEGY ATTRIBUTION
   | Strategy | Return | # Trades | Win Rate | Contribution |
   |----------|--------|----------|----------|-------------|
   | CSP      |        |          |          |             |
   | Equity   |        |          |          |             |
   | Hedging  |        |          |          |             |
   | TOTAL    |        |          |          |             |

3. RISK METRICS
   - Average portfolio delta: ___
   - Average portfolio theta: ___/day
   - Average cash reserve: ___%
   - Average options allocation: ___%
   - Max single-position concentration: ___%
   - Max sector concentration: ___%
   - Number of drawdown tier events: ___
   - Number of circuit breaker events: ___

4. RULE COMPLIANCE
   - Risk rule violations: ___
   - Manual overrides: ___
   - Stop-losses executed: ___
   - Profit targets hit: ___
   - Positions rolled: ___
   - Positions assigned: ___

5. STRESS TEST RESULTS
   - Scenarios re-run: [Y/N]
   - Any scenario breach identified: [Y/N]
   - If Y, remediation: ___

6. OPERATIONAL INCIDENTS
   - Technology failures: ___
   - Data integrity issues: ___
   - Broker/platform outages: ___

7. FORWARD-LOOKING
   - VIX regime assessment: ___
   - Key upcoming events: ___
   - Strategy adjustments planned: ___
   - Capital allocation changes: ___

8. LESSONS LEARNED
   ___________________________________________
```

### 8.4 Escalation Triggers

These conditions force immediate action — they cannot wait for the next scheduled review.

| Trigger | Severity | Required Action | Response Time |
|---------|----------|----------------|---------------|
| Portfolio drawdown hits any tier | High | Execute tier protocol (Section 4) | Immediate |
| Daily loss > 2% | High | Halt trading, review at close | Immediate |
| Single position loss > 3% of portfolio | High | Close position immediately | Within 1 hour |
| Any position delta > 0.50 | Medium | Evaluate close or roll | Within 2 hours |
| VIX crosses regime threshold | Medium | Adjust sizing regime | Before next trade |
| Sector limit breached | Medium | Identify positions to reduce | Within 1 trading day |
| Options allocation exceeds 30% | Medium | Identify positions to close | Within 1 trading day |
| Cash reserve below regime minimum | Medium | Sell positions to restore | Within 1 trading day |
| Technology failure during market hours | Medium | Switch to manual monitoring | Within 15 minutes |
| Correlation breach (new pair > 0.70) | Low | Evaluate at next weekly review | Within 1 week |
| Hedging cost exceeds quarterly budget | Low | Evaluate hedge effectiveness | Within 1 week |

---

## 9. Implementation Checklist

### Phase 1: Immediate (Before Paper Trading Begins)

- [ ] **Set up the daily dashboard.** Create Google Sheets dashboard with all metrics from Section 8.1. Connect to E-Trade API via n8n for auto-population.
- [ ] **Configure GTC orders.** For every position opened during paper trading, practice placing GTC stop-loss and profit target orders.
- [ ] **Implement pre-trade risk checks.** Build the n8n workflow that validates all risk limits (Section 3) before any trade recommendation passes through OCA.
- [ ] **Create the watermark tracker.** Automated tracking of portfolio all-time high and current drawdown tier. Telegram alert when any tier is breached.
- [ ] **Set up circuit breaker alerts.** Telegram notifications when daily loss > 1.5% (warning), > 2% (halt), weekly loss > 2.5% (warning), > 3% (halt).
- [ ] **Document current correlation matrix.** Calculate 60-day rolling correlations for all 11 names in the core universe. Store as reference for pre-trade checks.
- [ ] **Create the "dead man's switch" document.** Brokerage access, position summary, liquidation instructions. Share with Marian.

### Phase 2: During Paper Trading (4-Week Protocol)

- [ ] **Apply all risk limits as if live.** Every paper trade must pass the pre-trade risk check. No exceptions.
- [ ] **Complete the weekly risk review checklist** (Section 8.2) every Friday.
- [ ] **Run the five stress test scenarios** against the paper portfolio at Week 2 and Week 4.
- [ ] **Track all metrics** in the daily dashboard. Identify any metrics that are hard to calculate or source — fix the data pipeline.
- [ ] **Simulate a Tier 1 drawdown.** Intentionally test the Tier 1 protocol during paper trading (e.g., temporarily lower the threshold to -2% to see the protocol in action).
- [ ] **Test all technology failure protocols.** Disconnect n8n for 4 hours and practice manual monitoring. Verify GTC orders would fire without human intervention.
- [ ] **Validate position sizing formulas.** For every paper trade, calculate position size using both the Max Loss Method and Buying Power Method. Verify the lower value is used.

### Phase 3: Go-Live Transition

- [ ] **Confirm all risk limits are hard-coded** in the OCA / n8n pre-trade check. No position should be possible that violates any limit.
- [ ] **Set GTC orders for every live position** at entry. Profit target and stop-loss orders must be placed simultaneously with the opening trade.
- [ ] **Start at 50% of target position sizes** for the first 30 days of live trading.
- [ ] **Complete the monthly risk report** at the end of the first month of live trading.
- [ ] **Re-run all five stress test scenarios** against the live portfolio after 30 days.
- [ ] **Scale to 75% position sizes** after 30 days if all criteria are met (Sharpe > 1.0, max drawdown < -10%, zero rule violations).
- [ ] **Scale to 100% position sizes** after 60 days if criteria continue to be met.

### Phase 4: Ongoing Operations

- [ ] **Daily:** Pre-market and post-market dashboard review (Section 8.1).
- [ ] **Weekly:** Complete the risk review checklist (Section 8.2).
- [ ] **Monthly:** Generate the monthly risk report (Section 8.3). Run stress test scenarios.
- [ ] **Quarterly:** Full strategy parameter review. Backtest current parameters against most recent data. Update this framework if any parameter changes. Review and update the dead man's switch document.
- [ ] **Annually:** Comprehensive review of this entire framework. Update for any market regime changes, new strategies, or AUM milestones reached.

---

## Appendix A: Quick Reference Card

Print this and keep it next to your trading desk.

```
============================================
ALTAMIRA CAPITAL — RISK QUICK REFERENCE
============================================

POSITION LIMITS
  Single position: 5% max
  Sector: 25% max (tech: 35%)
  Options total: 30% max
  Correlated names/sector: 3 max
  Cash reserve: 15-25% min

CSP EXITS
  Profit target: 50% of credit
  Stop-loss: 200% of credit
  Delta breach: Close if > 0.50
  DTE < 7: Close all

EQUITY EXITS
  Hard stop: -10% from entry
  Trailing stop: -8% from high
  MA crossover: 3 closes below 50-day

DRAWDOWN TIERS
  -5%:  Reduce 25%, no new risk, add hedges
  -10%: Close 50%, reduce 50%, 40% cash
  -15%: Close all options, 60% cash, halt 20 days

CIRCUIT BREAKERS
  -2% daily: Halt trading
  -3% weekly: No new positions next week
  -5% monthly: Trigger Tier 1
  5 consecutive losses: Halt 3 days

VIX SIZING
  <15:  Standard + hedge
  15-25: Standard
  25-35: Reduce 25%
  >35:  Reduce 50%

GREEKS LIMITS (per $100K)
  Delta: -0.30 to +0.60
  Gamma: > -0.05
  Theta: +$50 to +$200
  Vega: > -$500

EMERGENCY LINE
  E-Trade: 1-800-387-2331
============================================
```

---

## Appendix B: Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-18 | Initial framework. Calibrated against 2-year backtest results. |

---

*This document is a living framework. It will be updated as strategies are validated through paper and live trading, as the portfolio grows through AUM milestones, and as market conditions evolve. All changes must be versioned and documented in Appendix B.*
