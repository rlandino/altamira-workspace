# Altamira Capital — Investment Thesis

**Version:** 2.0
**Date:** 2026-02-18
**Author:** Ricardo Landino, Founder

---

## Executive Summary

Altamira Capital is a technology-driven, multi-strategy investment firm built on the conviction that systematic processes and AI-powered automation create durable, compounding edges in public markets. The firm combines disciplined options premium selling, fundamental equity analysis, and rigorous risk management — all amplified by a proprietary automation stack that enables a solo founder to operate with the analytical throughput of a multi-person team.

**Validated by backtest:** A 2-year backtest across 10 core names confirms the viability of the multi-strategy approach. CSP selling achieved an 83.3% win rate with a 1.34 Sharpe ratio and negligible drawdown (-0.26%). Equity momentum delivered 34.57% cumulative return at 60.6% average exposure. Blended portfolio estimate: ~16.1% annualized return.

The structural edge is not a single strategy but an operating model: purpose-built AI tools that analyze options chains, monitor earnings catalysts, track fiscal policy impacts, and generate market commentary in real time. This infrastructure enables faster signal processing, more consistent execution, and tighter risk controls than traditional discretionary approaches.

**Core thesis:** Markets systematically misprice volatility more reliably than direction. Implied volatility overestimates realized volatility across most regimes, creating a structural premium that can be harvested through disciplined CSP selling — validated at 83.3% win rate over 18 trades across a 2-year backtest. By pairing this with equity momentum exposure and conditional hedging, and by using AI automation to monitor and manage positions at scale, Altamira Capital targets consistent, risk-adjusted returns with capital preservation as the primary constraint.

---

## Investment Philosophy

### Guiding Principles

1. **Volatility is mispriced more reliably than direction.** Implied volatility consistently overestimates realized volatility across most market regimes. This creates a structural premium that can be harvested systematically through options selling strategies.

2. **Systematic over discretionary.** Repeatable processes with defined parameters outperform ad hoc decision-making over time. Every strategy has explicit entry criteria, position sizing rules, and exit triggers — reducing emotional interference and improving consistency.

3. **Capital preservation first.** Protecting capital is not a defensive posture — it is the prerequisite for compounding. Drawdown management is the single most important discipline. A 50% loss requires a 100% gain to recover; avoiding deep drawdowns is the highest-leverage activity in portfolio management.

4. **Automation as a force multiplier.** AI and workflow automation are not supplements to the investment process — they are integral to it. Every tool in the stack exists to increase analytical coverage, reduce latency, or enforce discipline that human psychology would otherwise erode.

5. **Simplicity over complexity.** Prefer strategies with well-understood risk profiles and transparent mechanics. Avoid exotic instruments, illiquid positions, or strategies that require heroic assumptions. Three robust strategies executed with discipline beat ten clever ones executed inconsistently.

6. **Evidence-based iteration.** No strategy is deployed without empirical validation. The firm maintains a backtesting framework that tests strategies against historical data before committing capital. The 2-year backtest across 10 core names (2024-2026) validated all three core strategies before paper trading begins. Parameters are refined based on data, not intuition.

---

## Competitive Edge: The Automation Stack

Altamira Capital's primary differentiator is a proprietary suite of AI-powered tools that provide real-time market intelligence, options analysis, and decision support. These are not research projects — they are production systems integrated into daily workflows.

### Options Chain Analyzer (OCA)

**Purpose:** Systematic options screening and trade identification.

Analyzes full options chains across the target equity universe, calculating risk/reward metrics for premium selling strategies. Screens 500+ contracts across 11 names in under 5 minutes. Filters by delta, DTE, IV rank, and expected return to surface the highest-probability setups. Outputs structured recommendations for CSP, covered call, bull put spread, and jade lizard strategies with defined entry, adjustment, and exit parameters.

**Edge created:** Replaces hours of manual options chain review with automated screening. Ensures no high-probability setup is missed and enforces delta/DTE discipline consistently across every trade.

### Market Commenter

**Purpose:** Real-time market context and narrative synthesis.

Monitors market conditions, sector rotation, and macro developments to generate concise, actionable market commentary. Provides the "why" behind price action and flags regime changes that affect strategy selection and position sizing.

**Edge created:** Maintains continuous market awareness without requiring constant screen time. Surfaces context that prevents blind-spot trades and improves timing of new positions.

### Earnings Alpha

**Purpose:** Earnings catalyst identification and position management.

Tracks upcoming earnings across the portfolio universe, analyzes historical earnings reactions, IV crush patterns, and fundamental surprise potential. Generates pre-earnings position recommendations (straddle sells, directional plays) and post-earnings adjustment signals.

**Edge created:** Systematizes one of the highest-edge recurring events in options markets. Ensures every earnings cycle is evaluated for premium selling opportunities and that existing positions are adjusted for event risk.

### Fiscal Platform

**Purpose:** Fiscal policy monitoring and macro impact analysis.

Tracks government spending, tax policy, regulatory developments, and fiscal indicators that affect sector and market-level positioning. Connects policy developments to portfolio implications.

**Edge created:** Provides a macro overlay that most retail and small-fund operators lack. Prevents concentration in sectors facing policy headwinds and surfaces opportunities from policy tailwinds.

### Backtesting Framework

**Purpose:** Strategy validation and parameter optimization before capital deployment.

Tests trading strategies against 2+ years of historical price data using Black-Scholes options pricing with IV estimation. Simulates full trade lifecycle — entry, management, exit — with configurable parameters for delta, DTE, profit targets, and stop losses. Generates comprehensive performance reports including win rate, Sharpe ratio, max drawdown, and trade-level attribution.

**Edge created:** Eliminates guesswork from strategy design. Every parameter deployed in live trading has been validated against historical data. The framework confirmed the CSP strategy at 83.3% win rate and identified that systematic hedging should be conditional (VIX-based triggers) rather than continuous — a finding that would have cost real capital to discover in live trading.

### Claude Code Commands

**Purpose:** On-demand financial analysis and portfolio intelligence.

Three deployed commands integrated into the workspace:
- **`/analyze-ticker [TICKER]`** — Pulls live FMP API data (income statement, balance sheet, cash flow, key metrics) and calculates profitability, liquidity, leverage, efficiency, and valuation ratios with 3-year trends.
- **`/options-scan [TICKER]`** — Fetches real-time options chains, filters by delta/DTE/liquidity, and recommends CSP, covered call, bull put spread, and jade lizard strategies with position sizing.
- **`/portfolio-report [type]`** — Generates daily, weekly, or monthly portfolio reports covering market summary, watchlist performance, sector exposure, options landscape, risk dashboard, and action items.

**Edge created:** Instant, structured analysis on any name in the universe without switching tools or building spreadsheets. Reduces time-to-decision from hours to minutes.

### Workflow Orchestration (n8n)

All tools are orchestrated through n8n automation workflows that handle data ingestion, analysis pipelines, alert routing (Telegram), and output formatting (Google Sheets). This creates a daily automated intelligence cycle that runs without manual intervention.

---

## Target Markets

### In Scope

| Market | Instruments | Rationale |
|--------|------------|-----------|
| US large-cap and mega-cap equities | Common stock, LEAPs | Deep liquidity, high analyst coverage, strong fundamentals data |
| US equity options | Puts, calls, spreads, multi-leg | Core premium selling universe; tight spreads, transparent pricing |
| Sector and index ETFs | SPY, QQQ, sector ETFs | Portfolio hedging, sector rotation, broad market exposure |

### Core Equity Universe

AAPL, AMZN, AVGO, COST, GOOGL, MA, META, MSFT, NVDA, SPY, V

This universe is selected for options liquidity, earnings predictability, and alignment with the automation stack's coverage. It will expand as infrastructure capacity grows.

### Out of Scope

- Cryptocurrency and digital assets
- Commodities and commodity futures
- Foreign exchange (spot or derivatives)
- Micro-cap and OTC equities
- Private placements and venture investments

These are excluded to maintain focus, avoid illiquid or poorly-understood markets, and stay within the automation stack's analytical capabilities.

---

## Core Strategies

### Strategy 1: Options Premium Selling (Primary)

**Thesis:** Implied volatility consistently overestimates realized volatility. Selling options premium at disciplined parameters generates consistent income with defined, manageable risk.

**Backtest validation:** 83.3% win rate, 1.34 Sharpe ratio, -0.26% max drawdown over 2 years (18 trades across 10 names). 15 of 18 trades hit the 50% profit target. Average P&L per trade: $25.50. Top performers: META, AVGO, NVDA.

**Structures:**
- **Cash-secured puts (CSPs):** Primary income strategy. Sell puts on conviction names at strikes where assignment represents a favorable entry point.
- **Covered calls:** Yield enhancement on existing long positions. Manage call side to avoid capping upside on high-conviction holdings.
- **Vertical spreads (bull put, bear call):** Defined-risk premium capture with lower capital requirements. Used when implied volatility is elevated.
- **Jade lizards:** Sell put + sell call spread to collect premium exceeding short call spread width. Zero upside risk with defined downside.

**Parameters:**
| Parameter | Target | Rationale |
|-----------|--------|-----------|
| Delta | 0.20 - 0.30 | ~70-80% probability of profit; far enough OTM to absorb normal volatility |
| DTE | 30 - 45 days | Optimal theta decay acceleration zone; enough time for adjustments |
| IV Rank | >30th percentile | Only sell premium when IV is elevated relative to its own history |
| Max allocation | 30% of portfolio | Prevents options tail risk from dominating total portfolio returns |
| Position size | Max 5% per underlying | Single-name concentration limit |

**Management rules:**
- Close at 50% of max profit (winners)
- Roll or close at 200% of credit received (losers)
- Never hold through earnings unless explicitly planned as an earnings trade
- Adjust or exit if delta exceeds 0.50

### Strategy 2: Equity Momentum Long

**Thesis:** Fundamental conviction, amplified by systematic momentum signals, identifies equity exposure opportunities over intermediate time horizons. A 50-day moving average filter provides trend confirmation and natural cash allocation during downtrends.

**Backtest validation:** 34.57% cumulative return (18.05% annualized), 0.68 Sharpe ratio, -20.30% max drawdown over 2 years. 72.7% monthly win rate (16/22 months). Average exposure of 60.6% — the strategy was cash ~39% of the time, providing natural downside protection. Trailed SPY by 2.14% on an absolute basis but with significantly lower average exposure.

**Long side:**
- Concentrated positions (8-15 names) in companies with durable competitive advantages, improving fundamentals, and reasonable valuation.
- 50-day SMA used as a directional filter — long when price is above MA, flat when below.
- Earnings Alpha signals used to time entries around earnings catalysts.
- Position sizing based on conviction level and correlation with existing positions.
- Rebalance every 20 trading days with equal weight among active signals.

**Short side (tactical):**
- Used sparingly and primarily through put purchases or bear spreads rather than outright shorting.
- Reserved for names showing clear fundamental deterioration with catalysts.
- Max 10% of portfolio in short exposure at any time.

### Strategy 3: Conditional Portfolio Hedging

**Thesis:** Systematic hedging reduces drawdowns and enables larger core position sizes by capping tail risk — but only when hedging is cost-effective relative to the protection provided.

**Backtest finding:** Continuous protective put buying (monthly SPY puts at 0.20 delta) cost 0.08% in total returns over 2 years with zero measurable drawdown improvement during the bull market period. This validates a conditional approach: deploy hedges when VIX is low (protection is cheap and vol expansion is more likely) rather than continuously.

**Instruments:**
- SPY/QQQ put spreads for broad market protection
- VIX call spreads for volatility spike protection
- Collar strategies on concentrated positions

**Conditional triggers:**
| VIX Level | Hedging Action |
|-----------|---------------|
| VIX < 15 | Full hedge allocation — protection is cheap, vol expansion likely |
| VIX 15-20 | Half hedge allocation — selective protection on concentrated positions |
| VIX 20-30 | Minimal hedging — protection is expensive, market already pricing risk |
| VIX > 30 | No new hedges — market is pricing crisis; premium selling is the better use of capital |

**Budget:** 0.5-1.0% of portfolio value per quarter allocated to hedging costs, deployed conditionally based on VIX regime.

---

## Risk Management Framework

*See the standalone risk management framework document for full details.*

### Position-Level Controls

| Rule | Limit | Enforcement |
|------|-------|-------------|
| Maximum single position | 5% of portfolio | Pre-trade check; OCA enforces |
| Maximum sector exposure | 25% of portfolio | Monitored weekly |
| Maximum options allocation | 30% of portfolio | Aggregate notional exposure |
| Maximum correlated positions | 3 names per sector | Prevents hidden concentration |
| Stop-loss on equity positions | -10% from entry | Hard stop; review for re-entry |

### Portfolio-Level Controls

| Drawdown Tier | Action |
|---------------|--------|
| -5% from peak | Review all positions. Reduce sizing by 25%. No new risk. |
| -10% from peak | Close lowest-conviction positions. Reduce sizing by 50%. Increase hedging. |
| -15% from peak | Move to capital preservation mode. Close all options positions. Hold only highest-conviction longs + cash. |

### Circuit Breakers

| Trigger | Action |
|---------|--------|
| Daily P&L: -2% | Halt all new trades for the remainder of the session. Review all open positions. |
| Weekly P&L: -5% | Halt all trading for the remainder of the week. Full portfolio review before resuming. |

### Greeks-Level Constraints

| Greek | Portfolio Limit | Rationale |
|-------|----------------|-----------|
| Net Delta | +0.30 to +0.70 (normalized) | Maintain long bias without excessive directional exposure |
| Gamma | Monitor; flag if > 0.05 portfolio | Avoid large P&L swings from small moves |
| Vega | Net short vega < 2% of portfolio | Limits exposure to vol expansion; consistent with premium selling thesis |
| Theta | Net positive | Confirms time decay is working in portfolio's favor |

### VIX-Adjusted Sizing

Position sizing scales dynamically with implied volatility:

| VIX Range | Sizing Adjustment | Rationale |
|-----------|-------------------|-----------|
| <15 | Standard size; increase hedging | Low vol = complacency; protect against spike |
| 15-25 | Standard size | Normal regime |
| 25-35 | Reduce size by 25%; premium selling more attractive | Elevated vol = opportunity but higher risk |
| >35 | Reduce size by 50%; only sell premium at extreme levels | Crisis regime; capital preservation priority |

### Cash Management

Minimum 15-25% cash reserve maintained at all times. Cash is not idle — it is the option to deploy capital at better prices. During drawdown tiers 2 and 3, cash allocation increases to 40-50%.

---

## Portfolio Allocation Model

*See the standalone allocation model document for full details.*

### Base Allocation

| Sleeve | Target Allocation | Range | Purpose |
|--------|-------------------|-------|---------|
| Options premium strategies | 40-50% | 30-50% | Core income generation |
| Equity long positions | 30-40% | 25-45% | Capital appreciation + conviction bets |
| Short/hedging | 0-10% | 0-15% | Tail risk management, tactical shorts |
| Cash and equivalents | 15-25% | 15-50% | Dry powder, margin buffer, drawdown cushion |

Rebalancing trigger: Any sleeve deviating by more than 10 percentage points from target, or at drawdown Tier 1.

### VIX-Based Allocation Shifts

| VIX Regime | Options Sleeve | Equity Sleeve | Cash Sleeve |
|------------|---------------|---------------|-------------|
| VIX < 15 | 40% (standard) | 40% (standard) | 20% |
| VIX 15-25 | 45% (increase — richer premiums) | 35% | 20% |
| VIX 25-35 | 35% (reduce size per position, more setups) | 30% | 35% |
| VIX > 35 | 25% (only highest-conviction) | 25% | 50% |

### Scaling Milestones

| AUM | Focus | Key Changes |
|-----|-------|-------------|
| $100K (launch) | Validate strategies, build track record | Conservative sizing, 3-5 names, paper trading first |
| $250K | Expand universe, full strategy deployment | Full 11-name universe, all three strategies live |
| $1M | Optimize and diversify | Add sector ETF strategies, consider LEAPs, formal reporting |
| $5M | Evaluate fund structure | LP/GP evaluation, potential external capital, first hire |

---

## Performance Benchmarks and Targets

### Primary Benchmark

S&P 500 Total Return (SPY) — the firm must justify active management by exceeding passive index returns on a risk-adjusted basis.

### Performance Targets

| Metric | Year 1 Target | Steady State Target | Backtest Actual | vs. Target |
|--------|--------------|---------------------|-----------------|------------|
| Net return | 12-18% | 15-25% | ~16.1% (blended) | MET |
| Sharpe ratio | >1.5 | >2.0 | 1.34 (CSP) / 0.68 (equity) | CLOSE — needs improvement |
| Maximum drawdown | <-15% | <-12% | -0.26% (CSP) / -20.3% (equity) | CSP: MET / Equity: MISSED |
| Win rate (options) | >65% | >70% | 83.3% | EXCEEDED |
| Monthly income (options premium) | Consistent positive | Growing with portfolio | $25.50 avg per trade | MET |

**Backtest observations:**
- CSP Sharpe of 1.34 is close to the 1.5 target but needs refinement — likely improved by expanding trade frequency and optimizing delta selection.
- Equity max drawdown of -20.3% exceeds the -15% target. The 50-day MA filter helps (60.6% average exposure) but does not prevent sharp drawdowns. Position sizing and the circuit breakers added in v2.0 address this gap.
- Blended return of ~16.1% falls within the Year 1 target range, validating the multi-strategy approach.

### Growth Target

**Grow portfolio to $5M AUM.** This is the primary capital growth objective and the threshold at which the firm evaluates formal fund structure, external capital, and team expansion.

### Reporting Cadence

| Report | Frequency | Content |
|--------|-----------|---------|
| Daily P&L + positions | Daily | Mark-to-market, Greeks exposure, cash balance |
| Weekly performance review | Weekly | Strategy attribution, risk metrics, trade journal summary |
| Monthly performance report | Monthly | Returns vs. benchmark, Sharpe, drawdown, strategy breakdown |
| Quarterly strategy review | Quarterly | Thesis validation, strategy adjustment, goal progress |

---

## Operational Model

### Solo Founder + AI Leverage

Altamira Capital operates as a solo-founder firm where AI automation substitutes for what would traditionally require a 3-5 person team (analyst, trader, risk manager, operations). The automation stack handles data ingestion, screening, monitoring, and reporting — freeing the founder to focus on judgment-intensive decisions: thesis development, position sizing, and risk management.

### Daily Routine

| Time | Activity |
|------|----------|
| Pre-market (8:00-9:30 AM ET) | Review Market Commenter output, OCA overnight screens, earnings calendar |
| Market open (9:30-10:30 AM ET) | Execute planned trades, manage opening positions |
| Mid-day (10:30 AM - 3:00 PM ET) | Deep work: research, thesis refinement, system development |
| Market close (3:00-4:00 PM ET) | End-of-day review, position adjustments, next-day planning |
| Post-market (4:00-5:00 PM ET) | Trade journal entry, workflow maintenance, Earnings Alpha review |

### Decision Framework

For every trade:
1. **What is the thesis?** — Why does this trade exist?
2. **What is the edge?** — Why is the market wrong?
3. **What is the risk?** — Maximum loss and probability?
4. **What is the exit?** — Profit target and stop-loss defined before entry.
5. **Does it fit the portfolio?** — Correlation, sector exposure, total risk budget.

If any question lacks a clear answer, the trade does not happen.

---

## Roadmap

### Q1 2026: Foundation (Current)

| Milestone | Status | Date |
|-----------|--------|------|
| Investment thesis v1.0 | COMPLETE | 2026-02-17 |
| Investment thesis v2.0 (backtest-validated) | COMPLETE | 2026-02-18 |
| Trading infrastructure checklist | COMPLETE | 2026-02-17 |
| Backtesting framework built and operational | COMPLETE | 2026-02-18 |
| 3 core strategies backtested (CSP, momentum, hedging) | COMPLETE | 2026-02-18 |
| Claude Code commands deployed (analyze-ticker, options-scan, portfolio-report) | COMPLETE | 2026-02-17 |
| Risk management framework document | IN PROGRESS | Target: 2026-02-21 |
| Portfolio allocation model document | IN PROGRESS | Target: 2026-02-21 |
| E-Trade account setup with options Level 3 | IN PROGRESS | Target: 2026-02-28 |
| E-Trade API integration with n8n workflows | PLANNED | Target: 2026-03-07 |
| Paper trading setup and 4-week protocol | PLANNED | Target: 2026-03-10 |
| Paper trading go-live criteria validation | PLANNED | Target: 2026-03-31 |

### Q2 2026: Live Launch

- Transition from paper to live trading with reduced position sizes (50% of target)
- Run parallel paper + live tracking for first 30 days
- Validate risk management rules in live environment
- Scale to full position sizes upon meeting performance criteria
- Begin systematic trade journaling and performance attribution

### Q3-Q4 2026: Scale and Optimize

- Full-scale live trading across all three strategies
- Optimize automation stack based on live trading feedback
- Build out performance reporting and attribution
- Evaluate portfolio growth trajectory against $5M AUM target
- Refine strategy parameters based on 6+ months of data

### 2027: Evaluation and Growth

- Assess whether to pursue formal fund structure (LP/GP)
- Evaluate external capital acceptance
- Consider first team hire (quantitative analyst or operations)
- Expand instrument universe if justified by infrastructure capacity

---

## Appendix: Key Terms

| Term | Definition |
|------|-----------|
| CSP | Cash-secured put — selling a put while holding cash to cover assignment |
| DTE | Days to expiration |
| IV Rank | Current implied volatility relative to its 52-week range |
| Jade Lizard | Short put + short call spread; premium collected exceeds call spread width |
| Theta | Rate of time decay in an option's value |
| Delta | Sensitivity of option price to $1 move in underlying; proxy for probability of expiring ITM |
| Gamma | Rate of change of delta per $1 move in underlying |
| Vega | Sensitivity of option price to 1% change in implied volatility |
| Sharpe Ratio | Risk-adjusted return: (return - risk-free rate) / standard deviation |
| VIX | CBOE Volatility Index — market's expectation of 30-day S&P 500 volatility |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-02-17 | Initial draft — investment thesis, philosophy, strategies, risk framework, roadmap |
| v2.0 | 2026-02-18 | Updated with backtest evidence (83.3% CSP win rate, 1.34 Sharpe). Enhanced automation stack section with specific metrics and backtesting framework. Added circuit breakers (daily -2%, weekly -5%). Added Greeks-level constraints. Refined hedging from continuous to conditional (VIX-based triggers). Added scaling milestones. Updated performance benchmarks with backtest actuals. Updated roadmap with completion status. Added evidence-based iteration as 6th guiding principle. |

---

*This document is a living framework. It will be updated as strategies are validated through paper and live trading, and as market conditions evolve. Version history is maintained above.*
