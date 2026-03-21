# Jane Street Pre-Market Edge - 2026-03-21

## Market assessment
Overnight index proxy shows **+0.0 pts (+0.00%)** versus prior SPY-implied SPX close, which frames the open as **uncertain to slight hold** bias. Small gaps are often noise; first 15 minutes of order-flow usually decide continuation vs fade.

Implied volatility is **flat iv vs yesterday** with VIX at **26.78** vs prior close **26.78** (+0.00, +0.00%). No clear IV edge shift from prior close; focus on location (S/R) and timing rather than pure vol re-rating.

Prior session closed **at lows** of range (lean: **Bullish-to-neutral**). Calendar load is **moderate** and earnings spillover risk is **low to medium**; positioning should stay defined-risk and timing-aware.

## Overnight futures movement
- **Current SPX proxy:** 6506.48
- **Prior close (SPY-implied SPX):** 6506.48
- **Gap:** +0.0 pts (+0.00%)
- **View:** **Uncertain to slight hold**
- **Reason:** Small gaps are often noise; first 15 minutes of order-flow usually decide continuation vs fade.
- **Note:** True ES Globex high/low should be taken from broker/futures platform for precise overnight range context.

## Pre-market IV levels
- **Current VIX:** 26.78
- **Yesterday VIX close:** 26.78
- **Change:** +0.00 (+0.00%)
- **Read:** Flat IV vs yesterday
- **Theta implication:** No clear IV edge shift from prior close; focus on location (S/R) and timing rather than pure vol re-rating.

## Economic calendar impact
- **Calendar load today:** **Moderate**
- One high-impact report can reprice index vol quickly around release time.
- **High-impact monitor list:**
- **Fed Chair Powell Speech** (US, 17:30 ET, impact: High): monitor for range expansion around release.
- **Recommendation:** If a high-impact release appears near/after open, trade smaller and wait until after event volatility impulse before selling premium.

## Earnings exposure
- **Market-moving potential:** **Low to Medium**
- 18 companies listed today in FMP, but no clear mega-cap index movers (mostly single-name/localized risk).
- **Read-through:** Single-name IV can spike even when index impact stays muted.

## Globex range and expected range
- **Globex overnight range:** Pull exact ES high/low from broker; not directly provided by FMP quote endpoints.
- **Prior day range proxy (SPX-implied):** 120.1 pts (high 6587.9, low 6467.9)
- **VIX-based 1-day expected move:** **+/-109.8 pts** (~+/-1.69%)

## Opening gap strategy
- **Plan:** Small/no gap: run standard opening process, define trade only after first 15-minute range forms.
- **Execution filter:** No full-size theta position before opening auction imbalance settles.

## IV crush opportunity
- **Assessment:** Yes - event-risk premium is elevated enough to favor selective post-event premium selling once direction stabilizes.
- **Implication:** Favor defined-risk structures; monetize decay after direction and realized vol normalize.

## Previous day's close analysis
- Prior SPY session closed **at lows** of its daily range.
- **Lean for today:** **Bullish-to-neutral**
- **Why:** Closing near lows often sets up either dead-cat bounce or volatility continuation; wait for opening breadth confirmation.

## Support and resistance
### Support
1. **S1: 6470** - Prior day low proxy (first downside reaction zone)
2. **S2: 6395** - Approx. 1-day implied move lower boundary
3. **S3: 6340** - Extension support / deeper downside stress level

### Resistance
1. **R1: 6590** - Prior day high proxy (first upside stall zone)
2. **R2: 6615** - Approx. 1-day implied move upper boundary
3. **R3: 6670** - Extension resistance if squeeze persists

## Pre-market trade plan
- **Strategy:** No live trade today (market closed) -> Queue Monday defined-risk short-vol setup
- **Instrument:** SPX options (defined-risk)
- **Structure:**
  - Short Put: **6390**
  - Long Put: **6340**
  - Short Call: **6620**
  - Long Call: **6670**
- **Expiration:** **2026-03-23 (next session)**
- **Entry window:** **09:40-09:55 ET after opening rotation and breadth check**
- **Position size:** 1x normal risk max (about 1-2% account at risk) because event risk can reprice vol at Monday open.
- **Risk rule:** Hard stop if spot breaches short strike with momentum and VIX expands >10% intraday from entry.

## Scenario playbook
- **Bull outcome (price holds above R1 6590):** Reduce or close call-side risk quickly; keep put side to target 50-70% max profit capture.
- **Bear outcome (price breaks below S1 6470):** Cut/roll put-side risk early; harvest call-side gains and avoid gamma trap near downside acceleration.
- **Neutral outcome (price oscillates between S1 and R1):** Hold structure for theta decay, take profit at 40-60% of max, avoid over-managing.

## Data and disclaimer
- **Data sources:** FMP `quote` (^GSPC, SPY, ^VIX), FMP `historical-price-full` (SPY and ^VIX), FMP `economic_calendar`, FMP `earning_calendar`.
- **Overnight/Globex note:** Exact ES overnight high/low should come from broker/futures platform or user-provided futures feed.
- **Disclaimer:** This report is for educational and research purposes only, not investment advice. Options involve substantial risk; use your own risk limits and confirm live market data before trading.
