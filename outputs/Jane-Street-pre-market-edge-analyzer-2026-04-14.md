# Jane Street Pre-Market Edge — 2026-04-14

## Market assessment

S&P 500 is set for a strong upside open with spot at **6886.24** versus prior close **6816.89** (+69.35 pts, +1.02%). That is a meaningful gap-up open and increases the probability of an early opening reversion attempt before trend continuation.

Implied volatility is softer this morning: **VIX 18.28** vs yesterday close **19.12** (-0.84, -4.39%). Premium is cheaper than yesterday's close, but still elevated versus the low-volatility floor, which keeps defined-risk short premium viable if entry is patient.

Macro tape is not empty. US **PPI/Core PPI** prints land pre-open (calendar feed time converted from 12:30 UTC), followed by multiple Fed speakers later in session. Earnings are heavy in financials (JPM, C, WFC) plus JNJ before the bell, adding single-name and sector-level gap/rotation risk.

## Overnight futures movement

- **Gap:** +69.35 points (**+1.02%**) vs prior S&P 500 close.
- **View:** **Fade bias in first 30 minutes, then reassess for hold.**
- **Reason:** >0.5% upside gaps often see opening inventory unwind; however, prior session closed near highs, so failed fade can transition into trend day.

## Pre-market IV levels

- **Current VIX:** 18.28
- **Yesterday VIX close:** 19.12
- **Change:** -0.84 (-4.39%)
- **Read:** Options are pricing **lower** volatility versus yesterday close; premium selling still works, but collect after initial opening repricing rather than pre-open.

## Economic calendar impact

### Key US events today

- **08:30 ET (from feed 12:30 UTC):** Producer Price Index (MoM, Mar) and Core PPI (MoM, Mar)
- **12:15 ET (from feed 16:15 UTC):** Fed Goolsbee speech
- **12:45 ET (from feed 16:45 UTC):** Fed Barr speech
- **13:00 ET (from feed 17:00 UTC):** Fed Collins speech
- **13:00 ET (from feed 17:00 UTC):** Fed Barkin speech

### Historical impact and recommendation

- PPI inflation releases can expand opening range and increase first-hour volatility.
- Fed speaker clusters can create midday repricing bursts and headline-driven whipsaws.
- **Calendar load:** **Moderate**
- **Recommendation:** Wait for first 10-20 minutes post-open before initiating short premium; keep wings defined and avoid oversized exposure before data reaction settles.

## Earnings exposure

Major pre-market reporters flagged in today's feed:

- **JPM (BMO)**
- **C (BMO)**
- **WFC (BMO)**
- **JNJ (BMO)**

**Market-moving potential:** **Medium to High** (especially financial sector impulse via JPM/C/WFC).  
**Index implication:** Broad index move is possible through sector rotation, but risk is still more concentrated than a mega-cap tech earnings cluster.

## Globex range and expected range

- **True Globex high/low:** Not available in FMP spot feed (use broker futures ladder for exact overnight range).
- **Proxy overnight context:** Prior SPY day range was 9.72 points, which scales to roughly **97 SPX points** as a practical reference.
- **VIX-based 1-day expected move (SPX):**
  - Formula: Price x (VIX/100) / sqrt(252)
  - Result: **+/-79.3 points** (~+/-1.15%)
  - Approximate expected range from spot: **6807 to 6966**

## Opening gap strategy

- **Primary plan:** Do not chase the opening gap in first minutes.
- **Execution bias:** If SPX fails to hold above 6900 and breadth weakens, lean toward gap-fade behavior first.
- **Contingency:** If price accepts above 6900 after opening rotation and VIX stays contained (<19), switch to neutral premium-selling posture with wider call wing.

## IV crush opportunity

- No single major index-level event yesterday that implies a classic next-day IV crush setup.
- However, VIX already compressed sharply into today, so there is still intraday theta harvest potential if realized volatility cools after the data/opening impulse.
- **Verdict:** **Moderate** (not extreme) IV-crush opportunity for defined-risk premium selling.

## Previous day's close analysis

Using prior SPY session (open 677.41, high 686.30, low 676.58, close 686.10):

- Close finished at ~97.9% of session range (near highs).
- This is a **bullish momentum close**, but after a >1% gap-up setup it also raises odds of early mean reversion before directional follow-through.
- **Lean:** Bullish-over-medium horizon, tactically two-way at open.

## Support and resistance

### Support levels

1. **6845** - First pullback support inside opening gap structure.
2. **6817** - Prior cash close / key gap-fill magnet.
3. **6807** - VIX-implied lower expected-move boundary (with 6790 area just below as deeper support zone).

### Resistance levels

1. **6900** - Immediate psychological/round-number resistance.
2. **6966** - VIX-implied upper expected-move boundary.
3. **7000-7002** - Major psychological level and near prior year-high zone.

## Pre-market trade plan

- **Strategy:** **SPX 0DTE iron condor (defined risk)**
- **Structure (target ~0.10-0.15 delta shorts, refine with live chain):**
  - Sell **6795 put**
  - Buy **6775 put**
  - Sell **6995 call**
  - Buy **7015 call**
- **Expiration:** Today (0DTE)
- **Entry time:** **09:40-09:55 ET** (after opening rotation; avoid immediate open prints)
- **Position size:** **1x normal to 0.75x normal** (roughly 2-3% account risk max) given inflation print + Fed speaker stack
- **Risk controls:**
  - Hard stop if either short strike is threatened/ breached with momentum
  - Or if condor premium expands to ~2x entry credit
  - Target 40-50% max credit capture; de-risk before late-day headline windows

## Scenario playbook

### Bull outcome (SPX holds above 6900 and pushes toward 6966)

- Defend call side quickly if trend strengthens.
- Close or roll call spread up/out while harvesting put-side decay.
- If price accepts above 6966, reduce size and avoid fighting breakout.

### Bear outcome (SPX loses 6845, then 6817)

- Treat as gap-fade expansion.
- Close/roll put side before full strike pressure; keep call side as offset.
- If 6807 breaks with momentum, flatten remaining short gamma risk.

### Neutral outcome (SPX oscillates between 6845 and 6900)

- Hold structure for theta decay.
- Take profits at 40-50% of max credit, avoid greed into midday Fed headlines.
- No adjustment needed unless realized vol re-accelerates.

## Data and disclaimer

- **Data sources:** FMP `/quote` (^GSPC, SPY, ^VIX), FMP `/historical-price-full` (SPY, ^VIX), FMP `/economic_calendar`, FMP `/earning_calendar`.
- **Globex note:** True overnight futures high/low not provided by these spot endpoints; use broker/futures platform for exact Globex range.
- **Disclaimer:** This report is for educational and research purposes only, not investment advice. Options involve substantial risk; use defined risk, disciplined sizing, and independent judgment before trading.
