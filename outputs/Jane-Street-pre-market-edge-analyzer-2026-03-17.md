# Jane Street Pre-Market Edge — 2026-03-17

## Market assessment
US index proxies indicate a pre-open level around **SPX 6699.38** (from ^GSPC quote) with **VIX 23.41**. Using SPY-based proxying for overnight context (no direct ES feed provided), the implied gap is **0.0 pts (0.00%)** versus prior SPX proxy close.

Gap view: **Hold** — Small gap with limited displacement tends to continue with opening order flow. Yesterday closed **mid-range** of its range, giving a **Neutral lean** into today unless macro prints override open-flow signals.

Event slate is **Heavy** with market-moving potential from today's macro calendar and earnings tape assessed as **Low** for index spillover risk. Execution bias: keep positions defined-risk and size-adjusted until post-open volatility stabilizes.

## Overnight futures movement
- **Gap (proxy):** 0.0 points (0.00%) vs prior SPX proxy close.
- **View:** **Hold**.
- **Reason:** Small gap with limited displacement tends to continue with opening order flow.
- **Note:** SPX/ES exact overnight tape should come from broker/futures platform for execution precision.

## Pre-market IV levels
- **Current VIX:** 23.41.
- **Prior VIX close:** 23.51.
- **Delta vs yesterday:** -0.10 (-0.43%).
- **Read-through:** Options are pricing lower implied volatility versus prior close; favor standard strike distance for premium-selling structures.

## Economic calendar impact
- **2026-03-17 23:00:00** — Unemployment Rate (Feb) (KR)
- **2026-03-17 13:20:00** — Interest Rate Decision (MA)
- **2026-03-17 13:00:00** — CPI (Jan) (KW)
- **2026-03-17 09:00:00** — CPI (Feb) (IT)
- **2026-03-17 08:00:00** — Interest Rate Decision (AM)
- **2026-03-17 07:30:00** — Interest Rate Decision (ID)
- **Calendar load:** **Heavy**.
- **Historical impact guidance:** CPI/NFP/Fed-type events often expand intraday index range by ~1.5x to 2.0x normal session range.
- **Recommendation:** Trade smaller size and wait until after the top event window clears.

## Earnings exposure
- **EYE.L** (2026-03-17)
- **SNFCA** (bmo)
- **UBXN.SW** (2026-03-17)
- **3003.SR** (2026-03-17)
- **601211.SS** (2026-03-17)
- **BOL.PA** (2026-03-17)
- **HOT-UN.TO** (2026-03-17)
- **SHCMF** (2026-03-17)
- **Market-moving potential:** **Low**.
- **Interpretation:** Single-name IV will be elevated around prints; index impact is material only if mega-cap beats/misses cluster in one direction.

## Globex range and expected range
- **Globex overnight range:** Not provided by FMP spot endpoints. Pull ES Globex high/low from broker for exact overnight range.
- **Proxy range (prior regular session SPY):** 4.95 points.
- **Expected 1-day SPX move (VIX-based):** **+/- 98.0 points** (~+/- 1.46%).

## Opening gap strategy
- **Plan:** Normal theta setup after first 15-minute range; avoid chasing first candle.
- **Execution guardrail:** No entries in the first 5 minutes; require opening range structure before selling premium.

## IV crush opportunity
- **Assessment:** Potential intraday IV mean-reversion after macro release windows; best expressed via defined-risk premium selling after event volatility spikes.
- **Implication:** Prefer defined-risk short-vol structures over naked premium into event windows.

## Previous day's close analysis
- **Prior OHLC (SPY):** O 668.38 / H 672.07 / L 667.12 / C 669.03.
- **Close location:** mid-range of daily range.
- **Lean:** Neutral lean.

## Support and resistance
### Support
- **S1:** 6680.3 — prior day low (SPY) scaled to SPX.
- **S2:** 6650.4 — prior close minus ~0.5 expected move.
- **S3:** 6601.4 — full VIX-implied downside move.

### Resistance
- **R1:** 6729.8 — prior day high (SPY) scaled to SPX.
- **R2:** 6748.4 — prior close plus ~0.5 expected move.
- **R3:** 6797.4 — full VIX-implied upside move.

## Pre-market trade plan
- **Strategy:** 0DTE iron condor.
- **Structure (indicative):**
  - Short put: **6610**
  - Long put: **6590**
  - Short call: **6790**
  - Long call: **6810**
- **Expiration:** 0DTE (today).
- **Entry time:** After the highest-impact event window and after 10:00 AM ET confirmation.
- **Position size:** 0.5x normal size (max 1-2% account risk).
- **Risk rule:** Take profits at 40-50% of max credit; hard stop if short strike is breached with trend confirmation.

## Scenario playbook
- **Bull outcome (above R1):** Close/trim call side at 1.5x premium risk or 50% loss threshold; keep/harvest put side if theta decay continues.
- **Bear outcome (below S1):** Close/trim put side quickly; consider converting to call spread-only exposure if downside momentum persists.
- **Neutral outcome (inside S1-R1):** Hold core condor for theta decay and close at 40-50% max profit or by ~2:00 PM ET.

## Data and disclaimer
- **Data sources:** FMP `/quote` (^GSPC, SPY, ^VIX), `/historical-price-full` (SPY, ^VIX), `/economic_calendar`, `/earning_calendar`.
- **Overnight/Globex source:** ES/SPX overnight high/low should be taken from broker/futures platform when executing live.
- **Disclaimer:** For educational and research purposes only. Not investment advice. Options involve significant risk.
