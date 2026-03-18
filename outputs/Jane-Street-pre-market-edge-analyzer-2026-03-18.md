# Jane Street Pre-Market Edge — 2026-03-18

## Market assessment
Overnight index pricing is modestly higher. Using ^GSPC as the SPX/ES proxy (no direct futures feed in this run), the market is at **6716.09** versus prior close **6699.38**, a **+16.71 point (+0.25%)** gap. That is a small-to-moderate gap up, not a panic extension.

Implied volatility is still elevated in absolute terms but softer this morning: **VIX 21.93 vs 22.37 yesterday close** (**-0.44, -1.97%**). Premium is still rich enough for defined-risk short theta, but event timing dominates setup quality.

Today is an event-heavy tape with a Fed decision block this afternoon (rate decision/projections/press conference). That raises intraday range expansion odds and argues for patience on entry timing.

## Overnight futures movement
- **Proxy level:** SPX (^GSPC) 6716.09 (SPX/ES exact Globex from broker/futures platform for precision)
- **Prior close:** 6699.38
- **Gap:** **+16.71 points (+0.25%)**
- **View:** **Uncertain / slight fade bias early**
  - Reason: gap size is not large enough to force continuation, and a high-impact Fed block later often suppresses clean trend persistence before 2:00 PM ET.

## Pre-market IV levels
- **Current VIX:** 21.93
- **Yesterday VIX close:** 22.37
- **Change:** -0.44 (-1.97%)
- **Read:** IV is down vs yesterday but still elevated versus calmer regimes; this supports premium selling **only with defined risk** and preferably after key macro prints/events.

## Economic calendar impact
### High-impact U.S. events today (ET)
- **8:30 AM ET** — Producer Price Index MoM (Feb) (High)
- **2:00 PM ET** — Fed Interest Rate Decision (High)
- **2:00 PM ET** — FOMC Economic Projections (High)
- **2:30 PM ET** — Fed Press Conference (High)

### Historical impact guide
- **PPI/CPI-style inflation prints:** often expand the first 30-90 minute range (~1.2-1.6x normal intraday opening volatility).
- **Fed decision + press conference:** can create two-way repricing and late-day volatility spikes; 0DTE gamma risk rises materially around 2:00-3:00 PM ET.

### Calendar verdict
- **Today’s calendar:** **Heavy**
- **Recommendation:** avoid aggressive short premium before 10:00 AM ET; if trading 0DTE, favor post-event deployment with wider short strikes and smaller size.

## Earnings exposure
Major index-relevant earnings on today’s calendar are limited, but there are notable single-name prints:
- **MU (Micron)** — AMC; semi complex read-through (can influence SOX/Nasdaq sentiment)
- **GIS (General Mills)** — BMO; defensive staples read
- **JBL (Jabil)** — BMO; electronics manufacturing read-through
- **WSM (Williams-Sonoma)** — BMO; consumer discretionary micro signal

**Market-moving potential:** **Medium-Low** at the index level (macro/Fed is the primary driver today).  
**Single-name risk:** still meaningful in reported names due earnings IV dislocations.

## Globex range and expected range
- **True Globex high/low:** from broker/futures platform (not directly available from this FMP pull)
- **Proxy (yesterday SPY range):** 674.44 - 669.70 = **4.74 SPY points** (~**47.46 SPX points** using live SPX/SPY ratio)

### VIX-based expected move (1 day)
- Formula: `SPX * (VIX/100) / 16`
- Calculation: `6716.09 * 0.2193 / 16 = 92.05`
- **Expected range:** **+/-92 points (~+/-1.37%)**
- **Implied bounds:** approximately **6624 to 6808**

## Opening gap strategy
- **Opening stance:** **Wait-and-define**
- Do not force an opening fade/chase unless breadth and tape confirm.
- Preferred playbook:
  1. Observe first 15-20 minutes for opening auction imbalance resolution.
  2. If price remains inside prior-day proxy range and IV remains bid, lean neutral theta later.
  3. Reassess around Fed window; post-event premium is typically cleaner.

## IV crush opportunity
- **Yes, but timing-sensitive.**
- The Fed block is today’s high-IV event complex. Pre-event IV can stay sticky/elevated; post-announcement, implied vol can compress quickly if direction stabilizes.
- **Theta implication:** best short-vol deployment window is often **after** 2:10-2:30 PM ET once initial event whipsaw settles.

## Previous day close analysis
Using prior session SPY OHLC (Open 672.39 / High 674.44 / Low 669.70 / Close 670.79):
- Close location in range: `(Close - Low) / (High - Low) = 0.23`
- Market closed in the **lower quarter** of the range (near lows).
- Per command heuristic: close near lows can indicate a **bullish reflex/bounce lean** for the following session, but today that signal is secondary to Fed event risk.

## Support and resistance
### Support
1. **6705** — Prior-day proxy low mapped to SPX (first technical support)
2. **6700** — Round-number psychological support
3. **6624** — VIX-implied one-day lower expected-move bound

### Resistance
1. **6750-6753** — Prior-day proxy high mapped to SPX
2. **6800** — Round-number resistance / dealer pin zone candidate
3. **6808** — VIX-implied one-day upper expected-move bound

## Pre-market trade plan
- **Strategy:** 0DTE SPX **defined-risk iron condor** (post-event deployment)
- **Structure (template):**
  - Short Put: **6600**
  - Long Put: **6570**
  - Short Call: **6840**
  - Long Call: **6870**
- **Expiration:** **Today (0DTE)**
- **Entry time:** **2:20-2:45 PM ET** (after Fed decision + first reaction wave)
- **Sizing:** **1/2 normal size**, max **1-2% account risk** due event-day gamma
- **Risk controls:** hard stop if spot breaches a short strike with momentum; target 40-50% credit capture when available.

## Scenario playbook
### Bull outcome (acceptance above 6753)
- Action:
  - Reduce/close call-side risk early if tested.
  - Keep put spread if delta decays and price remains above reclaimed resistance.
  - If upside acceleration persists, convert to put-credit-spread-only risk.

### Bear outcome (acceptance below 6705)
- Action:
  - Defend put side quickly; do not hold full width through trend day.
  - Close call side to realize residual value.
  - If trend confirms, re-establish as call-credit-spread-only structure.

### Neutral outcome (range 6705 to 6753)
- Action:
  - Hold structure for theta decay.
  - Take profits at 40-50% of max credit; avoid greed into close on event day.
  - No adjustment unless one side reaches management threshold.

## Data and disclaimer
- **Data sources:** FMP `/quote` (^GSPC, SPY, ^VIX), FMP `/historical-price-full/SPY` (prior session OHLC), FMP `/historical-price-full/^VIX` (prior VIX close), FMP `/economic_calendar`, FMP `/earning_calendar`.
- **Globex note:** true ES overnight high/low not included in this pull; use broker futures platform for exact Globex range.
- **Educational use only:** This briefing is for research/education and not investment advice. Options involve substantial risk; use defined risk and position sizing discipline.
