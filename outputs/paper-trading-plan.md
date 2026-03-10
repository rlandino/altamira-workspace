# Altamira Capital — Paper Trading Launch Plan

**Version:** 1.0
**Date:** 2026-02-18
**Author:** Ricardo Landino, Founder
**Status:** Ready for Execution
**Target Launch:** 2026-03-01
**Companion Documents:** Risk Management Framework v1.0, Portfolio Allocation Model v1.0, Trading Infrastructure Setup v1.0, Investment Thesis v2.0

---

## 1. Executive Summary

### Purpose

This plan defines the complete paper trading phase for Altamira Capital's multi-strategy portfolio before committing live capital. Paper trading serves three functions: (1) validate that backtest results translate to forward-looking performance, (2) stress-test the automation infrastructure end-to-end, and (3) build execution discipline and muscle memory before real money is at risk.

The firm has completed backtesting across three strategies (CSP, equity momentum, hedging) with encouraging results — particularly CSP at 83.3% win rate and 1.34 Sharpe. Paper trading is the bridge between backtested theory and live execution.

### Success Criteria

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Duration | Minimum 4 weeks (28 calendar days) | Calendar weeks of continuous paper trading |
| Win rate (CSP) | >60% | Winning trades / total trades |
| Sharpe ratio | >1.0 | Annualized from weekly returns |
| Max drawdown | <-10% of portfolio | Peak-to-trough during paper period |
| Rule compliance | 100% | Zero risk management rule violations |
| Automation uptime | >95% | n8n workflows running without failure |
| Minimum CSP trades | ≥20 | Total CSP trades executed |
| Minimum momentum rebalances | ≥4 | Weekly rebalance cycles completed |
| No single week loss >3% | 0 violations | Weekly P&L tracking |
| Daily tracking streak | Zero missed days | Consecutive trading days with journal entry |
| Emotional readiness | Self-assessed "ready" | Honest self-evaluation: no revenge trading, no FOMO, no rule-breaking urges |

### Timeline

| Phase | Dates | Duration | Focus |
|-------|-------|----------|-------|
| Setup | Feb 18 – Feb 28 | 11 days | Platform configuration, API integration, tracking sheets |
| Phase 1: CSP Only | Mar 1 – Mar 7 | 1 week | Paper trade CSPs on 5 tickers; validate fill tracking |
| Phase 2: Add Momentum | Mar 8 – Mar 14 | 1 week | Add equity momentum strategy; run both in parallel |
| Phase 3: Full Multi-Strategy | Mar 15 – Mar 28 | 2 weeks | All strategies active; refine parameters |
| Go-Live Evaluation | Mar 29 – Apr 1 | 3 days | Review all data against go-live criteria |
| Transition (if criteria met) | Apr 1 – Apr 30 | 30 days | Live at 50% size + parallel paper trading |
| Full Scale (if criteria met) | May 1+ | Ongoing | Full position sizes; paper trading discontinued |

---

## 2. Platform & Broker Setup

### E-Trade Paper Trading Capabilities

E-Trade offers paper trading through Power E-Trade (web platform). Key features and limitations:

| Feature | Power E-Trade Paper Trading | Notes |
|---------|----------------------------|-------|
| Equity trading | Yes | Market, limit, stop orders |
| Options trading | Yes | Single-leg and multi-leg |
| Supported strategies | CSPs, covered calls, verticals, iron condors | Jade lizards may require manual entry as separate legs |
| Starting capital | Configurable (default $100K) | Set to $100K to match planned real capital |
| Real-time quotes | Yes | Same data feed as live platform |
| Order fills | Simulated at mid-price | Does not reflect real spread or partial fills |
| Greeks display | Yes | Delta, gamma, theta, vega on options chains |
| API access (sandbox) | Yes | `https://apisb.etrade.com` — separate from production |
| Trade history export | Limited | Manual CSV export; API sandbox provides structured data |
| Multi-leg order support | Yes | Can enter spreads as single orders |

**Known Limitations:**
- Paper fills execute at mid-price, which overstates real fill quality
- No slippage simulation
- Sandbox API may have delayed or static data (verify during setup)
- Daily OAuth token expiration still applies in sandbox
- Paper account does not simulate margin calls or buying power accurately for portfolio margin

### Alternative Platform Comparison

| Platform | Options Paper Trading | API Access | Multi-Leg Support | Data Quality | Cost | Setup Effort |
|----------|----------------------|------------|-------------------|--------------|------|-------------|
| **E-Trade (Power E-Trade)** | Yes | OAuth 1.0a sandbox | Yes | Real-time | Free (existing account) | Low — already have account |
| **ThinkorSwim (Schwab)** | Yes (PaperMoney) | No public API | Excellent | Real-time | Free with account | Medium — new account needed |
| **IBKR (TWS)** | Yes (Paper Trader) | REST + WebSocket | Excellent | Real-time | Free with account | Medium — new account needed |
| **Tradier** | Yes (sandbox) | REST API (modern) | Yes | Real-time | Free sandbox | Medium — new account, easy API |

### Detailed Pros/Cons

**E-Trade (Recommended Primary)**
- Pros: Existing account, API access already arranged, OAuth sandbox available, will be the live trading platform, one integration to build
- Cons: OAuth 1.0a is cumbersome, daily token expiration, sandbox may have data gaps, paper fill quality unknown until tested

**ThinkorSwim (Recommended Backup)**
- Pros: Best-in-class paper trading (PaperMoney mode), excellent options analytics, most realistic fill simulation, superior charting
- Cons: No public API for automated tracking, would need to rebuild integrations for live trading, Schwab migration ongoing
- Best use: Manual paper trading fallback if E-Trade paper trading is insufficient for options strategies

**IBKR**
- Pros: Most sophisticated paper trading engine, excellent API (modern REST), realistic fills, portfolio margin simulation
- Cons: New account required, complex platform, different from E-Trade workflow, would split attention during learning phase

**Tradier**
- Pros: Modern REST API, excellent developer documentation, easy OAuth 2.0, fast sandbox setup
- Cons: New account required, less established platform, would not be the live trading platform

### Recommendation

**Primary:** E-Trade Power E-Trade paper trading + E-Trade API sandbox

Rationale: Building against the same platform you will trade live on eliminates integration rework. The API sandbox enables automated tracking from day one. Any quirks discovered during paper trading inform the live integration.

**Backup:** ThinkorSwim PaperMoney (manual tracking only)

Activate the backup only if E-Trade paper trading fails to support required options strategies (specifically multi-leg orders or CSP tracking). In that case, use ThinkorSwim for execution and Google Sheets for manual journal entry while continuing to build the E-Trade API integration for live trading.

---

## 3. Paper Trading Configuration

### Capital Allocation

| Component | Amount | Percentage | Purpose |
|-----------|--------|------------|---------|
| CSP strategy | $40,000 | 40% | Options premium selling — cash-secured puts |
| Equity momentum | $40,000 | 40% | Long equity positions via 50-day MA signal |
| Cash reserve | $20,000 | 20% | Dry powder, margin buffer, drawdown cushion |
| **Total** | **$100,000** | **100%** | Match planned real capital |

### Position Sizing Rules

All position sizing follows the Risk Management Framework v1.0:

| Rule | Limit | Enforcement |
|------|-------|-------------|
| Maximum single position | 5% of total portfolio ($5,000) | Pre-trade check; reject if breach |
| Maximum sector exposure | 25% of portfolio ($25,000) | Monitor weekly; flag at 20% |
| Maximum options allocation | 30% of notional portfolio | Aggregate notional exposure check |
| Maximum correlated positions | 3 names per sector | Prevent hidden concentration |
| Minimum cash reserve | 15% ($15,000) | Never breach; block new trades if at limit |

**CSP-specific sizing:**
- Each CSP is sized so that assignment would not exceed 5% of portfolio
- For a $200 strike, 1 contract = $20,000 notional. Max 1 contract on names with strikes above $200
- For a $100 strike, 1 contract = $10,000 notional. Max 2 contracts
- Always check that total cash-secured amount across all open CSPs does not exceed $40,000

**Momentum-specific sizing:**
- Equal-weight across active signals (tickers where price > 50-day MA)
- If 5 tickers have active signals, each gets $40,000 / 5 = $8,000
- If only 2 tickers are active, remaining allocation stays in cash (do not concentrate)
- Rebalance every 20 trading days (approximately monthly)

### VIX-Adjusted Sizing

| VIX Range | CSP Sizing | Momentum Sizing | Hedge Action |
|-----------|------------|-----------------|--------------|
| <15 | Standard | Standard | Increase hedging (cheap protection) |
| 15–25 | Standard | Standard | Standard |
| 25–35 | Reduce by 25% | Reduce by 25% | Premium selling more attractive but size smaller |
| >35 | Reduce by 50% | Reduce by 50% | Crisis regime; capital preservation priority |

### Strategy Priority (Phased Rollout)

**Rationale for CSP-first:** CSP produced the strongest backtest results (83.3% win rate, 1.34 Sharpe) with the tightest risk profile (-0.3% max drawdown). It is the simplest strategy to paper trade and validate. Starting here builds confidence and allows focused debugging of the tracking infrastructure.

**Week 1 (Mar 1–7): CSP Only**
- Trade CSPs on 5 tickers: SPY, AAPL, MSFT, NVDA, AVGO
- Target: 0.20–0.25 delta, 30–45 DTE
- Goal: Execute 3–5 CSP trades, validate tracking pipeline, confirm fill recording
- Only sell puts when price is above 50-day MA (directional filter from backtest recommendations)

**Week 2 (Mar 8–14): Add Momentum**
- Continue managing open CSP positions
- Activate equity momentum strategy across full 10-ticker universe
- First rebalance: Identify tickers above 50-day MA, allocate equal-weight
- Goal: Validate momentum signal generation and position entry/exit tracking

**Week 3–4 (Mar 15–28): Full Multi-Strategy**
- Both strategies running simultaneously
- Add conditional hedging if VIX < 18 (per backtest recommendation)
- Expand CSP universe to all 10 tickers plus SPY
- Goal: Run the full portfolio as if live, including all risk checks and weekly reviews

---

## 4. Trade Execution Protocol

### Pre-Trade Checklist (6-Point)

Before entering ANY paper trade, answer all six questions. If any answer is unclear, the trade does not happen.

| # | Check | Question | Required Answer |
|---|-------|----------|-----------------|
| 1 | **Thesis** | What is the thesis for this trade? Why does it exist? | Written in 1–2 sentences |
| 2 | **Edge** | What is the edge? Why is the market mispricing this? | Specific: IV rank, catalyst, trend alignment |
| 3 | **Risk** | What is the maximum loss? What is the probability? | Dollar amount and percentage of portfolio |
| 4 | **Exit** | What is the profit target and stop-loss? | Specific prices/levels defined before entry |
| 5 | **Portfolio Fit** | Does this trade fit the portfolio? Sector, correlation, total exposure? | Confirm no limits breached |
| 6 | **Buying Power** | Is there sufficient cash/margin? Will cash reserve stay above 15%? | Yes with specific numbers |

### Order Types

| Strategy | Order Type | Rationale |
|----------|-----------|-----------|
| CSP entry (sell to open) | **Limit order only** | Set at natural price (bid) or slightly above mid. Never market order. |
| CSP exit (buy to close) | **Limit order only** | Close at 50% of credit or GTC limit at target. |
| CSP stop-loss | **Limit order** | Set at 200% of credit. Monitor daily; adjust manually if needed. |
| Momentum entry (buy) | **Limit order** | Set at ask or slightly below. No market orders. |
| Momentum exit (sell) | **Limit order** | Set at bid or slightly above. |
| Hedging (protective puts) | **Limit order** | Set at ask for puts. Acceptable to pay up slightly for protection. |

**Rule: No market orders. Ever.** Even in paper trading, practice limit-order discipline. Market orders in live trading on options can result in significant slippage.

### Execution Windows

| Window | Time (ET) | Activity | Rationale |
|--------|-----------|----------|-----------|
| Pre-market review | 8:00–9:15 AM | Review OCA output, Market Commenter, set orders for the day | Prepare before the open; no rushed decisions |
| Opening window | 9:30–10:00 AM | Execute planned entries; do NOT chase opening moves | Spreads tighten after first 15 min; best fills 9:45–10:00 |
| Mid-day | 10:00 AM–3:00 PM | No new positions; monitor existing | Avoid thin mid-day liquidity |
| Closing window | 3:30–3:55 PM | Execute any end-of-day entries; adjust positions expiring within 5 DTE | Good liquidity; useful for momentum rebalances |
| Post-close | 4:00–5:00 PM | Journal entry, P&L review, next-day planning | Mandatory daily tracking |

### Paper vs. Reality Fill Assumptions

Paper trading fills are unrealistically optimistic. To compensate:

| Issue | Paper Trading Reality | Adjustment |
|-------|----------------------|------------|
| Fill price | Mid-price (instantaneous) | Track actual bid-ask spread at time of "fill"; record mid AND what the real fill would likely be |
| Partial fills | Always 100% filled | Note when real-world depth suggests partial fill likely |
| Speed | Instant | Record timestamp; note if market moved during hypothetical execution |
| Slippage | Zero | Add 1–2% of premium as estimated slippage cost in journal |
| Commissions | Zero | Deduct $0.65/contract from P&L in tracking sheet |

**Adjusted P&L formula for each trade:**
```
Adjusted P&L = Paper P&L - (contracts × $0.65 × 2) - (premium × slippage_factor)
```
Where `slippage_factor` = 0.02 (2% of premium) for liquid names, 0.05 (5%) for less liquid names.

Track both raw paper P&L and adjusted P&L. Use adjusted P&L for all go-live evaluation metrics.

---

## 5. Tracking & Measurement System

### Google Sheets Trade Journal

#### Sheet 1: Trade Log

| Column | Field | Data Type | Example |
|--------|-------|-----------|---------|
| A | Trade ID | Auto-increment | PT-001 |
| B | Date (Entry) | Date | 2026-03-03 |
| C | Date (Exit) | Date | 2026-03-18 |
| D | Ticker | Text | AAPL |
| E | Strategy | Dropdown: CSP/Momentum/Hedge | CSP |
| F | Direction | Dropdown: Long/Short/STO/BTC | STO |
| G | Strike | Number | 210.00 |
| H | Expiration | Date | 2026-04-04 |
| I | DTE at Entry | Number | 32 |
| J | Delta at Entry | Number | -0.22 |
| K | IV Rank at Entry | Number | 45 |
| L | Contracts/Shares | Number | 1 |
| M | Entry Price (credit/debit) | Currency | $3.20 |
| N | Exit Price | Currency | $1.60 |
| O | Raw P&L | Formula | =(M-N)*L*100 |
| P | Commission | Formula | =L*0.65*2 |
| Q | Est. Slippage | Formula | =M*0.02*L*100 |
| R | Adjusted P&L | Formula | =O-P-Q |
| S | P&L % (of allocated capital) | Formula | =R/40000 |
| T | Days Held | Formula | =C-B |
| U | Exit Reason | Dropdown: Profit Target/Stop Loss/Expiration/Assignment/Manual | Profit Target |
| V | Thesis (pre-trade) | Text | IV elevated (rank 45); price above 50-day MA; AAPL reports in 6 weeks |
| W | Edge | Text | IV overpriced vs. realized; strong support at strike level |
| X | Outcome Notes (post-trade) | Text | Closed at 50% profit in 12 days. Thesis was correct. |
| Y | Rule Compliance | Dropdown: Yes/No | Yes |
| Z | What Would I Do Differently? | Text | Entry timing was good. Could have sized up given strong setup. |

#### Sheet 2: Daily Dashboard

Populate daily after market close. Can be automated via n8n.

| Column | Field | Formula/Source |
|--------|-------|----------------|
| A | Date | Manual/auto |
| B | Portfolio Value | Sum of cash + open position mark-to-market |
| C | Daily P&L ($) | Today's value - yesterday's value |
| D | Daily P&L (%) | =C/previous day's B |
| E | Cumulative P&L ($) | =B-100000 |
| F | Cumulative P&L (%) | =E/100000 |
| G | Net Delta Exposure | Sum of position deltas |
| H | Daily Theta Income | Sum of position thetas |
| I | Open CSP Count | Count of open CSP positions |
| J | Open Equity Positions | Count of momentum positions |
| K | Cash % | Cash / Portfolio Value |
| L | VIX Close | Market data |
| M | SPY Close | Market data |
| N | Notes | Any notable events or observations |

#### Sheet 3: Weekly Performance Summary

| Metric | Formula | Target |
|--------|---------|--------|
| Weekly P&L ($) | =SUM(daily P&L for week) | Positive |
| Weekly P&L (%) | =Weekly P&L / starting portfolio value | > -3% floor |
| Trades Opened | Count from trade log | Track |
| Trades Closed | Count from trade log | Track |
| Win Rate (cumulative) | =Winning trades / total closed trades | >60% |
| Rolling 4-Week Sharpe | See formula below | >1.0 |
| Max Drawdown (cumulative) | See formula below | >-10% |
| Rule Compliance | Count of "No" in trade log | 0 |
| Automation Uptime | n8n workflow success rate | >95% |

### Key Formulas

**Rolling Sharpe Ratio (annualized from weekly returns):**
```
Weekly Return = (Portfolio Value End of Week - Portfolio Value Start of Week) / Portfolio Value Start of Week

Mean Weekly Return = AVERAGE(last N weekly returns)
StdDev Weekly Return = STDEV(last N weekly returns)

Sharpe = (Mean Weekly Return - Risk-Free Weekly Rate) / StdDev Weekly Return × SQRT(52)

Where:
  Risk-Free Weekly Rate = (1 + 0.045)^(1/52) - 1 = ~0.000847 (0.085% per week at 4.5% annual)
```

Google Sheets formula (assuming weekly returns in column B, rows 2 through N):
```
=IF(COUNT(B2:B)>=4, (AVERAGE(B2:B)-0.000847)/STDEV(B2:B)*SQRT(52), "Need 4+ weeks")
```

**Annualized Return:**
```
Days in paper trading = DAYS(end_date, start_date)
Total Return = (Final Value - Initial Value) / Initial Value
Annualized Return = (1 + Total Return)^(365 / Days) - 1
```

Google Sheets formula:
```
=(1+(B_final-100000)/100000)^(365/DAYS(date_final, date_start))-1
```

**Maximum Drawdown:**
```
Running Peak = MAX of all portfolio values up to current date
Drawdown = (Current Value - Running Peak) / Running Peak
Max Drawdown = MIN of all drawdown values
```

Google Sheets formula (with portfolio values in column B):
```
Running Peak (column C): =MAX($B$2:B2)
Drawdown (column D): =(B2-C2)/C2
Max Drawdown: =MIN(D:D)
```

### Automation: n8n Workflows

| Workflow | Trigger | Source | Destination | Priority |
|----------|---------|--------|-------------|----------|
| Daily portfolio snapshot | Cron: 4:15 PM ET, M-F | E-Trade API sandbox | Google Sheets (Daily Dashboard) | P0 |
| Trade entry logger | Webhook: triggered on order fill | E-Trade API sandbox | Google Sheets (Trade Log) | P0 |
| Buying power check | On-demand: called by OCA | E-Trade API sandbox | OCA input | P1 |
| Weekly metrics calculator | Cron: Sunday 6:00 PM ET | Google Sheets | Google Sheets (Weekly Summary) + Telegram | P1 |
| Risk limit monitor | Cron: every 30 min during market hours | E-Trade API sandbox + Google Sheets | Telegram alert if any limit breached | P1 |

**Workflow: Daily Portfolio Snapshot**
```
Trigger (Cron 4:15 PM ET)
  → E-Trade API: GET /v1/accounts/{id}/portfolio
  → E-Trade API: GET /v1/accounts/{id}/balance
  → Transform: Calculate net delta, theta, cash %
  → Google Sheets: Append row to Daily Dashboard
  → Telegram: Send daily summary message
```

**Workflow: Trade Entry Logger**
```
Trigger (Webhook from E-Trade sandbox order fill, or manual trigger)
  → Parse order details: ticker, strike, expiration, contracts, fill price
  → Google Sheets: Append row to Trade Log with auto-populated fields
  → Telegram: Send trade confirmation with pre-trade checklist reminder
```

---

## 6. Weekly Review Protocol

### Schedule

**Day:** Sunday
**Time:** 6:00 PM ET (after weekly metrics n8n workflow runs)
**Duration:** 45–60 minutes
**Location:** Dedicated focus time — no interruptions

### Review Template

```
WEEKLY REVIEW — Week of [Date]
================================

1. PERFORMANCE SNAPSHOT
   - Portfolio value: $_____ (start) → $_____ (end) = _____% change
   - Weekly P&L: $_____
   - Cumulative P&L: $_____
   - Max drawdown this week: _____%
   - Rolling Sharpe (4-week): _____

2. TRADES THIS WEEK
   - Trades opened: _____ (CSP: _____, Momentum: _____, Hedge: _____)
   - Trades closed: _____ (Winners: _____, Losers: _____)
   - Win rate (cumulative): _____%
   - Best trade: _____ (ticker, P&L, thesis)
   - Worst trade: _____ (ticker, P&L, what happened)

3. THESIS ACCURACY
   - How many trade theses played out as expected? _____/_____
   - Biggest thesis miss: _____________________________
   - Lesson learned: _________________________________

4. RULE COMPLIANCE
   - Pre-trade checklist completed for every trade? [Y/N]
   - Position limits respected? [Y/N]
   - Sector limits respected? [Y/N]
   - Cash reserve maintained above 15%? [Y/N]
   - Only limit orders used? [Y/N]
   - Daily journal completed every day? [Y/N]
   - If any "No": describe the violation and corrective action

5. STRATEGY-SPECIFIC NOTES
   CSP:
   - Average DTE at entry: _____
   - Average delta at entry: _____
   - IV rank of trades entered: _____
   - Any patterns in wins vs. losses?

   Momentum:
   - Active tickers (above 50-day MA): _____
   - Rebalance actions taken: _____
   - Any signal conflicts or confusion?

6. MARKET REGIME
   - VIX range this week: _____ to _____
   - Market direction (SPY weekly change): _____%
   - Did regime affect strategy performance? How?
   - Any regime change detected?

7. PARAMETER ADJUSTMENTS
   - Any parameters to adjust? [Y/N]
   - If yes: what, why, and new value
   - (Be conservative — only adjust after clear, repeated pattern)

8. NEXT WEEK PLAN
   - Trades to look for: _____
   - Positions to manage: _____
   - Risk concerns: _____
   - System improvements needed: _____
```

### What to Look For

**Patterns:**
- Are wins clustered in certain tickers or market conditions?
- Are losses concentrated in specific sectors or VIX regimes?
- Is the 50-day MA filter actually improving CSP win rate?
- Does time of day affect fill quality?

**Regime Changes:**
- VIX trending up or down over multiple weeks?
- Sector rotation affecting the core universe?
- Earnings season approaching (adjust CSP DTE to avoid earnings)?
- Fed announcements or macro events on the horizon?

**Strategy Drift:**
- Are you deviating from the defined parameters?
- Are you holding losers longer than the stop-loss rule allows?
- Are you taking profits too early or too late?
- Are you skipping the pre-trade checklist?

### When to Adjust Parameters vs. Trust the System

| Situation | Action |
|-----------|--------|
| 1–2 losing trades | Trust the system. Expected variance. |
| Losing week within -3% limit | Trust the system. Review thesis accuracy but don't change parameters. |
| 2+ consecutive losing weeks | Review parameters. Check if market regime has shifted. Consider tightening delta to 0.20. |
| Win rate drops below 50% over 10+ trades | Investigate. Check IV rank filter, delta selection, and ticker selection. Adjust one parameter at a time. |
| Rule violation (self-imposed) | Stop trading for the rest of the day. Journal the violation. Add a friction step to prevent recurrence. |
| Max drawdown exceeds -7% | Reduce position sizes by 25%. Continue trading but tighter. |
| Max drawdown exceeds -10% | Pause paper trading for 1 week. Full strategy review before resuming. |

**Golden rule: Change only one parameter at a time, and only after observing the pattern for at least 10 trades or 2 weeks.**

---

## 7. Go-Live Criteria

All criteria below must be met simultaneously before transitioning to live capital. No exceptions. No "close enough."

### Quantitative Criteria

| # | Criterion | Target | Minimum Sample | Measurement Method |
|---|-----------|--------|----------------|--------------------|
| 1 | Paper trading duration | ≥4 weeks | 28 calendar days | Calendar count |
| 2 | Total CSP trades closed | ≥20 | 20 trades | Trade log count |
| 3 | Momentum rebalance cycles | ≥4 | 4 rebalances | Rebalance log count |
| 4 | Win rate (all strategies combined) | >60% | 20+ closed trades | Winning / total closed trades |
| 5 | CSP win rate | >65% | 15+ CSP trades | CSP winners / CSP total |
| 6 | Sharpe ratio (annualized from weekly returns) | >1.0 | 4+ weeks | Rolling Sharpe formula |
| 7 | Maximum drawdown | >-10% (less severe than -10%) | Full period | Peak-to-trough tracking |
| 8 | No single losing week >-3% | 0 violations | All weeks | Weekly P&L tracking |
| 9 | Adjusted P&L positive | >$0 | Full period | After commissions and slippage |
| 10 | Automation uptime | >95% | Full period | n8n workflow success rate |

### Qualitative Criteria

| # | Criterion | Assessment Method |
|---|-----------|-------------------|
| 11 | 100% rule compliance | Zero "No" entries in Rule Compliance column |
| 12 | Daily tracking — zero missed days | Consecutive daily entries in dashboard (weekdays only) |
| 13 | Weekly reviews completed | 4+ completed review templates |
| 14 | Pre-trade checklist completed for every trade | Verified in trade log |
| 15 | Emotional readiness | Self-assessment: Can honestly answer "Yes" to all of the following: |
|    |  | - I did not revenge trade after a loss |
|    |  | - I did not feel FOMO and enter unplanned trades |
|    |  | - I did not override my rules because "this time is different" |
|    |  | - I can accept a losing trade without emotional distress |
|    |  | - I trust the system and am ready to use real money |

### Decision Matrix

| Scenario | Decision |
|----------|----------|
| All 15 criteria met | Proceed to live trading at 50% position sizes |
| 12–14 criteria met, none are #7 or #8 | Extend paper trading by 2 weeks, address gaps |
| Drawdown >-10% or single week >-3% | Extend paper trading; full strategy review required |
| Win rate <50% | Do not go live. Fundamental strategy review. May need to re-backtest with different parameters. |
| Fewer than 12 criteria met | Extend paper trading by 4 weeks minimum |

---

## 8. Transition to Live Protocol

### Phase 1: Half-Size Live (Apr 1 – Apr 30)

**Conditions:** All 15 go-live criteria met.

| Parameter | Paper Trading | Live Phase 1 |
|-----------|---------------|--------------|
| Capital deployed | $100K simulated | $50K real ($100K account, 50% position sizes) |
| CSP allocation | $40K | $20K |
| Momentum allocation | $40K | $20K |
| Cash reserve | $20K | $60K (including undeployed capital) |
| Max single position | 5% ($5K) | 2.5% ($2.5K) |
| Max contracts per CSP | Based on full allocation | Half of paper trading quantities |

**Parallel running:**
- Continue paper trading at full $100K alongside live trading
- Compare paper results to live results daily
- Track execution quality: paper fill vs. actual fill on identical trades
- Log any psychological differences between paper and live execution

**Daily protocol during parallel period:**
1. Run OCA scan as usual
2. Enter trade in paper account first
3. Enter identical trade in live account at 50% size
4. Record both fills; note any discrepancy
5. Manage both positions identically

### Phase 2: Full Scale (May 1+)

**Conditions for scaling to full:** All of the following during the 30-day parallel period:
- Live win rate within 5 percentage points of paper win rate
- No live drawdown exceeding -5%
- Live Sharpe >0.8
- Zero rule violations
- No significant fill quality degradation (live fills within 3% of paper fills on average)

**Scale-up protocol:**
1. Week 1 of May: Increase to 75% position sizes
2. Week 3 of May: Increase to 100% position sizes (if Week 1–2 results are on track)
3. Discontinue parallel paper trading once at full scale

### Timeline Summary

```
Feb 18 ——— Setup ——————— Feb 28
Mar 1  — Paper Phase 1 —— Mar 7   (CSP only)
Mar 8  — Paper Phase 2 —— Mar 14  (CSP + Momentum)
Mar 15 — Paper Phase 3 —— Mar 28  (Full multi-strategy)
Mar 29 — Go-Live Eval ——— Apr 1   (Review all criteria)
Apr 1  — Live at 50% + Paper — Apr 30  (Parallel running)
May 1  — Scale to 75% —— May 14
May 15 — Scale to 100% — Ongoing (if criteria met)
```

---

## 9. Risk Scenarios During Paper Trading

### Scenario 1: Strategy Significantly Underperforms

**Definition:** CSP win rate <50% after 10+ trades, or portfolio drawdown exceeds -7%.

**Response protocol:**
1. **Pause new entries** — manage existing positions only
2. **Review all losing trades** — Is the thesis wrong? Is the market regime unfavorable? Is execution flawed?
3. **Compare to backtest** — Are current conditions materially different from the backtest period?
4. **Isolate the cause:**
   - If IV rank filter is not working: tighten from >30th percentile to >40th
   - If delta selection is too aggressive: reduce from 0.25 to 0.20
   - If tickers are the problem: remove the worst-performing tickers from the universe
5. **Adjust one parameter at a time** — resume at reduced size
6. **If still underperforming after 2 weeks of adjustments:** Extend paper trading indefinitely until performance stabilizes. Do not go live.

### Scenario 2: Rule Violation

**Definition:** Any deviation from defined rules (position sizing, sector limits, order types, pre-trade checklist, etc.)

**Response protocol:**
1. **Stop trading for the rest of the day.** No exceptions.
2. **Journal the violation immediately:**
   - What rule was broken?
   - Why? (Emotional trigger? Forgot? Rationalized it?)
   - What was the outcome? (Win or loss is irrelevant — the violation is the problem)
3. **Add a friction step** to prevent recurrence:
   - Example: If skipped pre-trade checklist, add a Telegram bot that blocks order entry until checklist is confirmed
   - Example: If overrode position limit, add a hard limit in the tracking sheet that flags in red
4. **Second violation of the same rule:** Pause paper trading for 48 hours. Full process review.
5. **Third violation of the same rule:** The system has a design flaw. Redesign that specific control before resuming.

### Scenario 3: Simulated Drawdown

**Definition:** Portfolio value drops more than 5% from peak.

**Purpose:** Practice the drawdown protocol from the Risk Management Framework so it becomes automatic before real money is at risk.

**Response protocol (matching the Risk Management Framework):**

| Drawdown Tier | Trigger | Action |
|---------------|---------|--------|
| Tier 1 | -5% from peak | Review all positions. Reduce new position sizes by 25%. No new risk until review complete. |
| Tier 2 | -10% from peak | Close lowest-conviction positions. Reduce sizing by 50%. Increase hedging allocation. |
| Tier 3 | -15% from peak | Capital preservation mode. Close all options positions. Hold only highest-conviction longs + cash. |

**Even though this is paper money,** follow the drawdown protocol exactly. The purpose of paper trading is not just P&L — it is building the behavioral pattern. When a real -10% drawdown happens, the response should be automatic, not deliberated.

After a Tier 2 event:
- Pause for 24 hours
- Complete a full position and strategy review
- Write a post-mortem: What caused the drawdown? What would have prevented it?
- Resume only after adjusting parameters and confirming the adjustment addresses the cause

### Scenario 4: E-Trade Paper Trading Does Not Support Required Strategies

**Definition:** Discover during setup that E-Trade paper trading cannot handle CSPs, multi-leg spreads, or options Greeks tracking.

**Response protocol:**
1. **Activate ThinkorSwim backup** — open a Schwab account and use PaperMoney mode for options paper trading
2. **Manual tracking becomes primary** — all trades entered manually in Google Sheets
3. **Continue building E-Trade API integration** — the sandbox may still work for automated data pull even if manual execution is on ThinkorSwim
4. **Timeline impact:** Add 3–5 days to setup phase for ThinkorSwim onboarding
5. **No change to go-live criteria** — all targets still apply regardless of which platform is used for paper trading

### Scenario 5: Automation Failure During Paper Trading

**Definition:** n8n workflows fail, API connectivity drops, or tracking pipeline breaks.

**Response protocol:**
1. **Manual backup immediately** — enter all trades and daily data by hand in Google Sheets
2. **Diagnose within 24 hours** — is it an API issue, n8n issue, or credential expiration?
3. **Fix and verify** — test the pipeline with a known data set before re-enabling automation
4. **Track uptime** — each failure counts against the 95% uptime criterion
5. **If automation uptime drops below 90% for 2+ weeks:** Simplify the automation stack. Reduce scope to the critical path (daily snapshot + trade logger) and defer nice-to-haves.

---

## 10. Action Items

### Setup Phase (Feb 18 – Feb 28)

| # | Task | Deadline | Dependencies | Status |
|---|------|----------|-------------|--------|
| 1 | Confirm E-Trade Options Level 3 application status | Feb 19 | E-Trade account active | [ ] |
| 2 | Access E-Trade Developer Portal; obtain sandbox API keys | Feb 19 | Developer account at developer.etrade.com | [ ] |
| 3 | Test OAuth 1.0a flow in sandbox (Postman or curl) | Feb 20 | Task 2 complete | [ ] |
| 4 | Test E-Trade sandbox endpoints: account list, balance, portfolio, options chain | Feb 21 | Task 3 complete | [ ] |
| 5 | Enable Power E-Trade paper trading mode; configure $100K starting capital | Feb 21 | E-Trade account | [ ] |
| 6 | Set up E-Trade watchlists: AAPL, MSFT, GOOGL, AMZN, AVGO, COST, V, MA, META, NVDA, SPY | Feb 21 | Task 5 complete | [ ] |
| 7 | Create Google Sheets paper trading workbook (Trade Log, Daily Dashboard, Weekly Summary) | Feb 22 | None | [ ] |
| 8 | Build formulas: rolling Sharpe, annualized return, max drawdown, adjusted P&L | Feb 22 | Task 7 complete | [ ] |
| 9 | Create n8n workflow: Daily portfolio snapshot (E-Trade API → Google Sheets) | Feb 25 | Tasks 4, 7 complete | [ ] |
| 10 | Create n8n workflow: Trade entry logger (webhook → Google Sheets) | Feb 25 | Tasks 4, 7 complete | [ ] |
| 11 | Create n8n workflow: Weekly metrics calculator (Google Sheets → Telegram) | Feb 26 | Tasks 7, 8 complete | [ ] |
| 12 | Create n8n workflow: Risk limit monitor (30-min check → Telegram alerts) | Feb 26 | Tasks 4, 7 complete | [ ] |
| 13 | Configure Telegram notification templates for: daily summary, trade confirmation, risk alert, weekly review | Feb 27 | Tasks 9–12 complete | [ ] |
| 14 | Test full pipeline end-to-end: simulate a paper CSP trade and verify it flows through all systems | Feb 27 | Tasks 5–13 complete | [ ] |
| 15 | Open ThinkorSwim/Schwab account as backup (apply for PaperMoney access) | Feb 21 | None (parallel task) | [ ] |
| 16 | Document any sandbox limitations discovered during testing | Feb 28 | Task 14 complete | [ ] |
| 17 | Final review of this plan; confirm all systems ready for Mar 1 launch | Feb 28 | All above complete | [ ] |

### Phase 1: CSP Only (Mar 1 – Mar 7)

| # | Task | Deadline | Notes |
|---|------|----------|-------|
| 18 | Execute first paper CSP trade (SPY or AAPL) | Mar 3 | Start with most liquid name |
| 19 | Verify tracking pipeline captured the trade correctly | Mar 3 | Check Google Sheets, Telegram notification |
| 20 | Execute 2–4 additional CSP trades across 5 tickers | Mar 7 | Target 3–5 total trades in Week 1 |
| 21 | Complete first daily dashboard entries (every market day) | Mar 7 | Zero missed days |
| 22 | Complete Week 1 weekly review | Mar 9 (Sunday) | Use review template |

### Phase 2: Add Momentum (Mar 8 – Mar 14)

| # | Task | Deadline | Notes |
|---|------|----------|-------|
| 23 | Calculate 50-day MA signals for all 10 tickers | Mar 8 | Identify active tickers |
| 24 | Execute first momentum rebalance (equal-weight long active tickers) | Mar 8 | Enter positions in paper account |
| 25 | Continue managing CSP positions + enter new CSPs | Mar 14 | Target 3–5 new CSPs in Week 2 |
| 26 | Complete Week 2 weekly review | Mar 15 (Sunday) | Compare CSP-only vs. combined performance |

### Phase 3: Full Multi-Strategy (Mar 15 – Mar 28)

| # | Task | Deadline | Notes |
|---|------|----------|-------|
| 27 | Expand CSP universe to all 10 tickers + SPY | Mar 15 | Add GOOGL, AMZN, COST, V, MA, META |
| 28 | Implement conditional hedging if VIX < 18 | Mar 15 | Per backtest recommendation |
| 29 | Execute momentum rebalance #2 | Mar 15 | Second rebalance cycle |
| 30 | Execute momentum rebalance #3 | Mar 22 | Third rebalance cycle |
| 31 | Complete Week 3 weekly review | Mar 22 (Sunday) | Look for patterns across strategies |
| 32 | Execute momentum rebalance #4 | Mar 28 | Fourth rebalance (meets minimum) |
| 33 | Complete Week 4 weekly review | Mar 29 (Sunday) | Final review before go-live evaluation |

### Go-Live Evaluation (Mar 29 – Apr 1)

| # | Task | Deadline | Notes |
|---|------|----------|-------|
| 34 | Compile all metrics against go-live criteria table | Mar 30 | Score every criterion Pass/Fail |
| 35 | Complete emotional readiness self-assessment | Mar 30 | Honest answers only |
| 36 | Write go-live decision memo (1 page: results, decision, rationale) | Mar 31 | File in outputs/ |
| 37 | If criteria met: configure live E-Trade account for 50% position sizes | Apr 1 | Production API credentials required |
| 38 | If criteria NOT met: document gaps and revised timeline | Apr 1 | Extend paper trading with specific improvement targets |

---

## Appendix A: Quick Reference Card

Print or bookmark this for daily use during paper trading.

```
ALTAMIRA CAPITAL — PAPER TRADING QUICK REFERENCE
=================================================

CSP PARAMETERS
  Delta: 0.20–0.25 (conservative)
  DTE: 30–45 days
  IV Rank: >30th percentile
  Profit target: Close at 50% of credit
  Stop loss: Close at 200% of credit
  Max position: 5% of portfolio / 1 contract on $200+ strikes
  Filter: Only sell when price > 50-day MA

MOMENTUM PARAMETERS
  Signal: Long when price > 50-day MA
  Rebalance: Every 20 trading days
  Weighting: Equal weight among active signals
  Cash: Uninvested allocation earns risk-free rate

PRE-TRADE CHECKLIST
  1. Thesis?      4. Exit plan?
  2. Edge?        5. Portfolio fit?
  3. Max loss?    6. Buying power?

RISK LIMITS
  Single position: ≤5%
  Sector: ≤25%
  Options total: ≤30% notional
  Cash reserve: ≥15%
  Correlated positions: ≤3 per sector

DRAWDOWN PROTOCOL
  -5%:  Review all. Reduce size 25%. No new risk.
  -10%: Close weak. Reduce size 50%. Add hedges.
  -15%: Preservation mode. Close options. Cash up.

EXECUTION RULES
  Limit orders only. Never market orders.
  Open: 9:45–10:00 AM ET
  Close: 3:30–3:55 PM ET
  Journal: Every day. No exceptions.

GO-LIVE TARGETS
  Duration: 4+ weeks | Win rate: >60% | Sharpe: >1.0
  Max DD: >-10% | Rules: 100% | Uptime: >95%
  CSP trades: ≥20 | Rebalances: ≥4
  Weekly loss floor: -3% | Missed days: 0
```

---

## Appendix B: E-Trade API Sandbox Quick Reference

```
Base URL: https://apisb.etrade.com
Auth: OAuth 1.0a (tokens expire at midnight ET daily)

Key Endpoints:
  GET /v1/accounts/list              → List accounts
  GET /v1/accounts/{id}/balance      → Buying power, cash
  GET /v1/accounts/{id}/portfolio    → Positions + Greeks
  GET /v1/market/quote/{symbols}     → Real-time quotes
  GET /v1/market/optionchains        → Options chain data
  GET /v1/accounts/{id}/orders       → Order history
  POST /v1/accounts/{id}/orders/place → Place orders

Rate Limits:
  Market data: 2 req/sec
  Account data: 4 req/sec

Common Issues:
  401 → Token expired, re-authenticate
  429 → Rate limited, back off
  Sandbox data may be delayed or static — verify during setup
```

---

## Appendix C: Glossary

| Term | Definition |
|------|-----------|
| CSP | Cash-Secured Put — selling a put while holding cash to cover potential assignment |
| DTE | Days to Expiration |
| Delta | Option's sensitivity to $1 move in underlying; proxy for probability of expiring ITM |
| IV Rank | Current implied volatility relative to its 52-week range (0–100) |
| Sharpe Ratio | Risk-adjusted return: (return - risk-free rate) / standard deviation |
| 50-day MA | 50-day Simple Moving Average; momentum signal line |
| VIX | CBOE Volatility Index; market's expectation of 30-day S&P 500 volatility |
| STO | Sell to Open — opening a short options position |
| BTC | Buy to Close — closing a short options position |
| Paper P&L | Profit/loss before adjustments for commissions and slippage |
| Adjusted P&L | Paper P&L minus estimated commissions ($0.65/contract round-trip) minus estimated slippage |

---

*This plan is a living document. Update as systems are built and lessons are learned during paper trading. Discipline over complexity.*
