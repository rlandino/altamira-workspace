# Jane Street Pre-Market Edge — 2026-03-16

## Market assessment

SPX proxy is showing a downside gap of roughly **-40.4 points (-0.61%)** versus prior close (using FMP quote proxy; exact ES/SPX futures should come from broker feed). By rule-of-thumb, gaps larger than 0.5% are more likely to see early mean reversion than clean continuation unless driven by a major macro catalyst.

Implied volatility is still elevated but cooling: **VIX 25.25 vs 27.19 yesterday close** (about **-1.94 / -7.1%**). That supports defined-risk premium selling, but strike width should stay conservative due to elevated absolute vol.

Previous session closed near the low of the day (SPY close location ~8.5% from low within session range), which keeps a defensive tape bias into the open. Calendar risk is **moderate** this morning (8:30/9:15/10:00 ET data cluster), while earnings-driven index risk appears limited.

## Overnight futures movement

- **Gap (proxy):** -40.43 SPX points (**-0.61%**)
- **View:** **Fade-biased / uncertain hold**
- **Reason:** Down gap is large enough to attract early mean-reversion flows, and there is no single top-tier event (Fed/CPI/NFP) forcing immediate trend continuation.
- **Note:** Exact ES Globex levels should be taken from broker futures platform.

## Pre-market IV levels

- **Current VIX:** 25.25
- **Yesterday VIX close:** 27.19
- **Delta:** -1.94 points (-7.1%)
- **Read:** Options are pricing less volatility than yesterday, but absolute IV remains elevated (>20), favoring cautious theta structures with defined risk and wider-than-normal short strikes.

## Economic calendar impact

### US events today (ET)

- **8:30 AM ET:** NY Empire State Manufacturing Index (Mar) — Medium impact
- **9:15 AM ET:** Industrial Production MoM (Feb) — Medium impact
- **10:00 AM ET:** NAHB Housing Market Index (Mar) — Medium impact

### Impact read

- **Calendar load:** **Moderate**
- No CPI/FOMC/NFP-style catalyst on this schedule; expected volatility impact is usually below those events.
- Recommendation: wait through the first 10-20 minutes after open and avoid oversized exposure before 10:00 AM ET data is absorbed.

## Earnings exposure

Major names from today’s calendar with potential US attention:

- **DLTR (Dollar Tree)** — BMO, market cap ~**$21.9B**
- Additional larger-cap entries in feed are mostly non-US/OTC listings (lower direct S&P 500 index sensitivity).

**Market-moving potential for index today:** **Low to Medium**  
**Single-name IV risk:** Present in select reporters, limited broad-index spillover expected unless a major surprise.

## Globex range and expected range

- **Globex range:** Not provided by FMP quote endpoint; use broker futures data for true overnight high/low.
- **Proxy overnight context:** Prior SPY session range = **10.98 points**, which maps to roughly **~110 SPX points**.
- **VIX-based 1-day expected move (SPX):** about **+/-104.6 points** (~**+/-1.58%**).

## Opening gap strategy

- **Primary posture:** Stay patient into the open; avoid immediate first-minute fills.
- **Execution bias:** If early downside momentum stalls near Support 1, prefer fading the gap with defined-risk structures; if price accepts below Support 1, delay entry and widen strikes.
- **Timing:** Preferred entry window **9:40-9:55 AM ET** after opening imbalance settles.

## IV crush opportunity

- Yesterday was **not** a classic high-IV macro event day (no CPI/Fed/NFP in this setup).
- IV is lower than yesterday but still elevated; this is a **normal-to-good theta environment** rather than a pure post-event IV crush setup.

## Previous day's close analysis

- Prior day SPY OHLC: **Open 669.27 | High 672.34 | Low 661.36 | Close 662.29**
- Close was near session lows (roughly bottom decile of range).
- **Lean:** Mildly bearish at the open unless price quickly reclaims prior close zone.

## Support and resistance

### Support

1. **6622** — Prior day low proxy (SPY low scaled to SPX)
2. **6600** — Round-number support
3. **6528** — VIX expected-move lower bound

### Resistance

1. **6673** — Prior close zone
2. **6700** — Round-number resistance
3. **6737** — VIX expected-move upper bound / prior high zone

## Pre-market trade plan

- **Strategy:** **0DTE SPX iron condor (defined risk)**
- **Structure (model strikes):**
  - Short Put: **6520**
  - Long Put: **6510**
  - Short Call: **6745**
  - Long Call: **6755**
- **Expiration:** **Today (0DTE)**
- **Entry time:** **9:40-9:55 AM ET**, preferably after 10:00 AM ET data reaction is visible
- **Risk size:** **1-2% of account at risk** (reduced size due elevated absolute VIX)
- **Management:** Take profits at 40-50% of max credit; hard risk exit on tested short strike or premium expansion to ~2x entry credit.

## Scenario playbook

- **Bull outcome (price > 6673 and holding):**
  - Reduce/close call spread risk early if upside momentum accelerates.
  - Keep put side only if trend is orderly and delta remains controlled.

- **Bear outcome (price < 6622 and acceptance):**
  - Cut/roll put side sooner; do not wait for full strike breach in fast tape.
  - Consider taking profits on call side and reducing gross exposure.

- **Neutral outcome (range 6622-6673):**
  - Hold structure for theta decay.
  - Target 40-50% capture before midday; avoid holding full size deep into late-day gamma.

## Data and disclaimer

- **Data sources:** FMP v3 quote (^GSPC, SPY, ^VIX), historical-price-full (SPY, ^VIX), economic_calendar (today), earning_calendar (today).
- **Globex/overnight caveat:** Exact ES/SPX overnight high/low should come from broker futures platform; FMP quote used here as proxy.
- **Disclaimer:** This report is for educational and research purposes only and is not investment advice. Options involve significant risk and may not be suitable for all investors.
