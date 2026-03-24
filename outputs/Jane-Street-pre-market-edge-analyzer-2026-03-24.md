# Jane Street Pre-Market Edge — 2026-03-24

## Market assessment

Overnight price action is effectively flat on a spot proxy basis, with SPX proxy at **6581.0** versus prior proxy close **6581.0** (gap **0.0 pts / 0.00%**). With no meaningful displacement into the open, the base case is a conditional **gap hold** unless the first 15-minute range breaks cleanly.

Implied volatility remains elevated in absolute terms. **VIX is 26.19**, slightly above yesterday's close (**26.15**, +0.04 / +0.15%) and above the recent 5-session average (~**24.89**), so option premium remains rich but still event-sensitive.

Macro headline risk is the dominant driver today. The calendar is **heavy** (PMI complex, Richmond Fed data, Fed speaker later), while earnings are broad but not concentrated in mega-cap index weights. Tactically, that favors defined-risk premium selling after opening structure is visible.

## Overnight futures movement

- **Input source:** No user-supplied ES/SPX futures level; used SPY/SPX quote proxy from FMP.
- **Gap:** **0.0 pts (0.00%)** vs prior SPX proxy close.
- **View:** **Hold** (conditional) — small overnight displacement is more likely to continue with opening flow than to hard mean-revert immediately.

## Pre-market IV levels

- **Current VIX:** 26.19
- **Yesterday VIX close:** 26.15
- **Change:** +0.04 (**+0.15%**)
- **5-session average VIX:** ~24.89
- **Read-through:** Options are still pricing above-recent volatility; short premium is viable, but keep risk defined and event-aware.

## Economic calendar impact

### Key events (from FMP feed)
- **13:45 ET:** S&P Global Manufacturing PMI (Mar)
- **13:45 ET:** S&P Global Services PMI (Mar)
- **13:45 ET:** S&P Global Composite PMI (Mar)
- **14:00 ET:** Richmond Fed Manufacturing Index / related sub-indexes
- **22:30 ET:** Fed Barr speech

### Impact context
- **PMI releases:** often create fast repricing in index futures and can expand intraday range.
- **Fed communication days:** can reprice rates/volatility quickly and create two-way flows.

### Calendar verdict
- **Today’s calendar:** **Heavy**
- **Recommendation:** Use wider short strikes relative to expected move and avoid oversized exposure before scheduled macro prints.

## Earnings exposure

- Earnings calendar is populated (575 names), but there are **no clear mega-cap index-heavy reporters** in today’s filtered list.
- **Market-moving potential:** **Low to Medium** at index level.
- **Implication:** Single-name IV opportunities are present; broad index impact from earnings appears limited unless an outlier surprise occurs.

## Globex range and expected range

- **Globex overnight high/low:** Not available from FMP spot endpoints; use broker/futures platform for exact ES range.
- **Proxy range (yesterday SPY session):** 8.68 SPY points, equivalent to ~87.1 SPX points (scaling proxy).
- **VIX-implied 1-day expected move:** **±107.7 SPX points** (~**±1.64%**).

## Opening gap strategy

- **Primary approach:** Deploy normal theta only after first 10-15 minutes once opening range is established.
- **Execution note:** If the initial range breaks and immediately fails, prioritize fade setups; if break sustains with breadth, avoid fighting trend early.

## IV crush opportunity

- No single obvious "post-Fed/post-CPI crush" setup from the prior session.
- However, macro-event premium is likely to remain bid into scheduled data, creating potential **post-release volatility compression**.
- **Plan:** Prefer selling defined-risk premium *after* event prints when realized volatility starts to contract.

## Previous day's close analysis

- **Prior day OHLC (SPY):** O 658.07 / H 662.62 / L 653.94 / C 655.38
- **Close location:** Near session lows
- **Lean:** **Bullish-to-neutral** (mean-reversion bias), but catalyst-dependent.

## Support and resistance

### Support
1. **6566.5** — near half expected-move down zone from prior close proxy
2. **6527.1** — near full expected-move down zone
3. **6473.3** — prior day low proxy area / deeper support

### Resistance
1. **6634.9** — near half expected-move up zone from prior close proxy
2. **6653.7** — prior day high proxy area / first major overhead test
3. **6688.7** — near full expected-move up zone

## Pre-market trade plan

- **Strategy:** 0DTE SPX iron condor (defined-risk)
- **Structure (model-based, expected-move anchored):**
  - Short Put: **6480**
  - Long Put: **6460**
  - Short Call: **6680**
  - Long Call: **6700**
- **Expiration:** Today (0DTE)
- **Entry time:** **9:35-9:50 AM ET** (or 5-10 minutes after any high-impact print)
- **Size:** **2-3% account risk max**; cut to half-size if realized volatility expands above expected pace
- **Risk controls:** Take profit around 40-50% max credit; reduce challenged side if spot breaches S1/R1 with momentum.

## Scenario playbook

### Bull outcome (price above 6634.9 / R1 with acceptance)
- Reduce or close call-side risk early.
- Keep put side for decay if breadth confirms uptrend.
- Do not add upside premium until trend shows exhaustion.

### Bear outcome (price below 6566.5 / S1 with acceptance)
- Reduce or close put-side risk quickly.
- Consider taking call side profits and avoid averaging into downside pressure.
- Re-center only if volatility expansion stabilizes.

### Neutral outcome (price oscillates between S1 and R1)
- Hold structure for theta decay.
- Target 40-50% premium capture intraday.
- Exit remaining risk before late-day gamma acceleration if range remains intact.

## Data and disclaimer

- **Data sources:** FMP `/quote` (^GSPC, SPY, ^VIX), FMP `/historical-price-full/SPY`, FMP `/historical-price-full/^VIX`, FMP `/economic_calendar`, FMP `/earning_calendar`.
- **Overnight/Globex note:** Exact ES Globex high/low should come from broker or futures platform; this briefing used spot/proxy calculations where futures-specific data was unavailable.
- **Financial calculations disclaimer:** Expected move, proxy scaling, and level calculations are model-based estimates and may diverge from live futures/options market-implied values.
- **General disclaimer:** For research and educational use only. Not investment advice. Trading options involves substantial risk, including potential loss of capital.
