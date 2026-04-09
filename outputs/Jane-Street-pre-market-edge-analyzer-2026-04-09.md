# Jane Street Pre-Market Edge — 2026-04-09

## Market assessment

S&P futures (ES proxy) are indicating a strong gap up into the U.S. open. ES is trading around **6805.75** pre-market versus prior S&P 500 cash close **6616.85**, a gap of **+188.90 points (+2.85%)**. This is a large overnight displacement and typically raises the probability of an early fade unless fresh macro data validates continuation.

Volatility is still elevated. **VIX is 21.36**, up from yesterday's close at **21.04** (**+0.32, +1.52%**), which implies option premiums remain rich enough for defined-risk premium selling, but with event-aware timing.

Macro timing is the key risk today: multiple U.S. releases hit at **8:30 ET** (Initial/Continuing Jobless Claims, Core PCE, Personal Spending). With a large pre-open gap and elevated VIX, the best setup is to wait for the first reaction window and deploy a controlled theta structure after price discovery.

## Overnight futures movement

- **Pre-market level (ES proxy):** 6805.75
- **Prior SPX close:** 6616.85
- **Gap:** **+188.90 points (+2.85%)**
- **View:** **Fade/Uncertain early, then reassess**
  - Reason: a >0.5% gap is statistically prone to partial mean reversion in the first 30-90 minutes, especially with 8:30 ET macro releases.

## Pre-market IV levels

- **Current VIX:** 21.36
- **Yesterday VIX close:** 21.04
- **Change:** +0.32 (+1.52%)
- **Read:** Pre-market IV is **higher** versus yesterday, so premium is still attractive, but wider strikes and disciplined sizing are required.

## Economic calendar impact

### High-impact U.S. events (ET)

- **8:30 ET**
  - Initial Jobless Claims
  - Continuing Jobless Claims
  - Core PCE Price Index MoM / YoY
  - Personal Spending MoM
- **10:00 ET**
  - Wholesale Sales / Wholesale Inventories
- **11:30 ET**
  - Atlanta Fed GDPNow

### Impact read

- **Calendar load:** **Moderate to Heavy** (front-loaded at 8:30 ET).
- Claims/PCE prints can expand intraday index range to roughly **1.3-1.8x** normal on surprise days.
- **Recommendation:** do not force pre-open premium selling; wait for post-release and opening-range stabilization before entering 0DTE risk.

## Earnings exposure

- Earnings feed is active globally today, but there are **no obvious mega-cap U.S. index-heavy names** (e.g., AAPL/MSFT/NVDA/AMZN/META) dominating today's schedule.
- **Market-moving potential from earnings:** **Low to Medium**
  - Single-name volatility may be elevated in select small/mid caps.
  - Broad index impact appears more macro-driven than earnings-driven this morning.

## Globex range and expected range

### Globex / overnight range (ES proxy)

- **Overnight high:** 6823.00
- **Overnight low:** 6792.50
- **Overnight range:** **30.50 points**

### Expected range (VIX-based)

- Formula: `Price × (VIX/100) / sqrt(252)`
- Using ES 6805.75 and VIX 21.36:
  - **Expected 1-day move:** approximately **+/-91.6 points** (~**+/-1.35%**)
  - Implied day range envelope: roughly **6714 to 6897**

## Opening gap strategy

- **Primary plan:** wait and define after first 15-30 minutes (and after 8:30 ET data shock passes).
- **Execution bias:** if first push after open is rejected near overnight highs, favor fade structure; if acceptance above overnight highs with breadth confirmation, keep call side farther out and reduce size.
- **Risk posture:** half-size until post-data direction is confirmed.

## IV crush opportunity

- Yesterday was not a classic single binary (e.g., FOMC/CPI day), but IV remains elevated above low-volatility baseline.
- **Opportunity:** moderate intraday IV compression can still favor defined-risk premium selling (iron condor / one-sided credit spread), provided entry is post-volatility spike and not pre-event.

## Previous day's close analysis

Using SPY prior-session bar:

- **Open:** 676.39
- **High:** 677.08
- **Low:** 671.46
- **Close:** 676.01

Close location in range = `(Close - Low) / (High - Low)` = `(676.01 - 671.46) / (677.08 - 671.46)` = **~81%** (near highs).

- **Lean:** mildly bullish carryover, but today's very large gap increases early two-way risk and fade probability.

## Support and resistance

### Support levels

1. **6790** — Overnight low zone (first pullback defense).
2. **6760** — Round-number magnet and likely liquidity pocket if gap retraces.
3. **6715** — VIX-implied expected-move downside boundary.

### Resistance levels

1. **6825** — Overnight high / breakout decision point.
2. **6850** — Psychological round-number resistance.
3. **6897** — VIX-implied expected-move upside boundary.

## Pre-market trade plan

- **Strategy:** **0DTE SPX iron condor (defined risk)**
- **Structure (guide, no live chain deltas):**
  - Short Put: **6705**
  - Long Put: **6680**
  - Short Call: **6910**
  - Long Call: **6935**
- **Expiration:** **2026-04-09 (0DTE)**
- **Entry window:** **9:50-10:15 ET** (after 8:30 ET macro reaction and opening-range stabilization)
- **Sizing:** **1/2 normal size** (about **1-2% account risk**)
- **Management rules:**
  - Take profits at 40-60% of max credit.
  - Hard stop if short strike is breached with momentum or spread marks at ~1.8-2.0x entry credit.

## Scenario playbook

### Bull outcome

- **Trigger:** price accepts above **6825**.
- **Action:** reduce call-side risk early (close/trim call spread if delta accelerates), keep put side for theta harvest.

### Bear outcome

- **Trigger:** price loses **6790** and fails to reclaim.
- **Action:** reduce put-side risk first; if downside momentum persists, close challenged side and keep opposite side only if risk is capped.

### Neutral outcome

- **Trigger:** price rotates inside **6760-6850** after opening volatility.
- **Action:** hold condor and harvest decay; target 40-60% max profit by early afternoon rather than forcing late-day gamma risk.

## Data and disclaimer

- **Data sources used:**
  - FMP Quote: `^GSPC, SPY, ^VIX`, and ES proxy (`ES=F`)
  - FMP Historical: `SPY`, `^VIX` (prior session OHLC)
  - FMP Economic Calendar: U.S. releases for 2026-04-09
  - FMP Earnings Calendar: 2026-04-09 schedule
- **Notes:**
  - True broker Globex tape and live options-chain deltas should be used for final strike precision.
  - This report uses pre-market snapshots and expected-move approximations.

**Disclaimer:** For education and research only. This is not investment advice, a solicitation, or a guarantee of performance. Options involve substantial risk, including total loss.
