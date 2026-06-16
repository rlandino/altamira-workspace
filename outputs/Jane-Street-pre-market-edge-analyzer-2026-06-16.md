# Jane Street Pre-Market Edge - 2026-06-16

## Market assessment

SPX/ES futures were not supplied, and FMP did not return a distinct pre-market futures/extended-hours field. Using the FMP SPX/SPY proxy, the market is effectively flat versus the prior SPX cash close: SPX 7,554.29 versus 7,554.28. Exact overnight gap and Globex range should be confirmed from the broker/futures platform before sizing.

VIX is 16.13, down 0.07 points from yesterday's 16.20 close and below its 50-day average of 18.09 and 200-day average of 18.55. Options pricing is not stressed; premium selling is acceptable only with defined risk and after the open confirms range behavior.

Yesterday closed in the upper half of the session range, which leaves a constructive but not stretched read. Today's 8:30 AM ET housing starts/building permits and import/export prices create moderate morning event risk, while the earnings calendar has limited U.S. mega-cap index risk.

## Overnight futures movement

- **Proxy level:** SPX 7,554.29 from FMP quote; SPY 754.83.
- **Prior SPX close:** 7,554.28.
- **Gap:** +0.01 points (+0.00%) using FMP cash-index proxy.
- **View:** **Uncertain / flat proxy** - no reliable pre-market futures field was available. If broker ES confirms a gap under +/-0.25%, treat it as normal theta conditions; if ES is >0.50% from prior close, expect an early fade unless breadth confirms extension.

## Pre-market IV levels

- **Current VIX:** 16.13.
- **Yesterday VIX close:** 16.20.
- **Change:** -0.07 points (-0.4%).
- **Recent context:** VIX is below the recent 5-session average near 19.08 and below the 50/200-day averages.
- **Implication:** Premium is fair-to-light rather than panic-rich. Favor defined-risk spreads over naked short volatility; do not overpay for long gamma unless the opening range breaks cleanly.

## Economic calendar impact

Today's U.S. calendar is **moderate**, with the main event cluster before the cash open:

- **8:30 AM ET - Building Permits (May), High impact:** Prior 1.423M, estimate 1.420M. Housing data can move rates-sensitive equities and widen the first-hour range.
- **8:30 AM ET - Housing Starts (May), High impact:** Prior 1.465M, estimate 1.430M. A large surprise can expand SPX range by roughly 1.2-1.5x normal.
- **8:30 AM ET - Import Prices MoM (May), Medium impact:** Prior +1.9%, estimate +1.0%. Inflation-sensitive, but usually secondary to CPI/PPI.
- **8:30 AM ET - Export Prices MoM (May), Medium impact:** Prior +3.3%, estimate +1.2%.
- **1:00 PM ET - 20-Year Bond Auction, Low impact:** Watch rates reaction if morning housing data is already moving yields.
- **4:30 PM ET - API Crude Oil Stock Change, Medium impact:** Mostly energy-sector and after-hours relevance.

**Recommendation:** Let the 8:30 data settle and avoid entering a full iron condor immediately at the open if SPX is outside the first 15-minute range. Prefer entry after 9:45 AM ET when realized range and VIX direction are visible.

## Earnings exposure

FMP lists 145 companies reporting today. The large-cap/index-heavy U.S. exposure is light; the only high market-cap names returned in the major filter were Japan-listed REIT/property tickers:

- **8956.T:** Large Japan-listed issuer, no broad U.S. index impact expected.
- **8975.T:** Large Japan-listed issuer, no broad U.S. index impact expected.
- **3476.T:** Japan-listed issuer, no broad U.S. index impact expected.

**Market-moving potential:** **Low** for SPX from single-name earnings. Single-name IV remains relevant, but today is driven more by macro data and opening breadth than earnings.

## Globex range and expected range

- **Globex range:** Not available from FMP. Use broker/futures platform for ES overnight high/low.
- **Proxy range:** Prior SPX cash range was 61.17 points (7,577.92 high - 7,516.75 low).
- **VIX-based 1-day expected move:** +/-76.8 SPX points, or about +/-1.02%, using SPX 7,554.29 and VIX 16.13.
- **Expected range reference:** Approximately 7,477 to 7,631 from the current proxy level.

## Opening gap strategy

- **If ES confirms a flat/small gap (<0.25%):** Trade normal defined-risk theta after the first 15 minutes; sell premium only if SPX remains between prior low and prior high.
- **If ES confirms an upside gap >0.50%:** Do not chase the open. Fade risk is elevated unless SPX holds above 7,578 and breadth is expanding.
- **If ES confirms a downside gap >0.50%:** Wait for support response near 7,517/7,500. Sell call-side premium first; add put side only after selling pressure stabilizes.

## IV crush opportunity

Yesterday was not a single high-IV macro event day, but VIX has compressed sharply from last week's 20+ readings to 16.13. There may be modest residual premium from recent volatility, though not enough to justify aggressive naked short vol.

**Opportunity:** Defined-risk 0DTE iron condor or single-side credit spread after the morning event/opening range. Target modest premium, wider strikes, and quick profit-taking at 40-50% of max profit.

## Previous day's close analysis

- **Prior SPX open:** 7,516.75.
- **Prior SPX high:** 7,577.92.
- **Prior SPX low:** 7,516.75.
- **Prior SPX close:** 7,554.28.
- **Close location:** About 61% of the way up the prior day's range.
- **Lean:** Mild bullish/neutral. The market closed above the midpoint but below the highs, so momentum is constructive without a clear exhaustion signal.

## Support and resistance

### Support

1. **7,550 - Prior close / round-number pivot:** First balance level around the FMP proxy.
2. **7,517 - Prior day low/open:** Key downside reference; losing it weakens the neutral theta setup.
3. **7,477 - VIX expected-move lower bound:** Approximate 1-day downside range from current VIX.

### Resistance

1. **7,578 - Prior day high:** First upside stall/confirmation level.
2. **7,600-7,621 - Round number / recent year-high zone:** Psychological resistance plus recent high at 7,620.90.
3. **7,631 - VIX expected-move upper bound:** Approximate 1-day upside range from current VIX.

## Pre-market trade plan

- **Primary strategy:** 0DTE SPX iron condor, defined risk.
- **Expiration:** Today, 2026-06-16.
- **Entry window:** 9:45-10:05 AM ET, after the 8:30 data and first 15-30 minutes of cash trading settle.
- **Entry condition:** SPX remains between 7,517 and 7,578, VIX holds below 17, and the opening range is not expanding violently.
- **Estimated strikes without live chain deltas:**
  - Sell **7,475 put**, buy **7,465 put**.
  - Sell **7,630 call**, buy **7,640 call**.
- **Delta guide:** Use actual chain to target 0.10-0.15 delta shorts. If real deltas differ materially, move the shorts outside the expected-move boundary.
- **Credit target:** Prefer at least $0.70-$1.20 total credit for a 10-point-wide condor; skip if premium is too thin.
- **Position size:** 1x normal or 1-2% of account risk due to event/opening-range uncertainty.
- **Risk management:** Stop the challenged side at 2x credit received or if SPX accepts beyond the short strike; take profits at 40-50% of max profit, preferably before 2:00 PM ET.
- **Fallback:** If SPX breaks above 7,578 and holds, skip the call spread and consider put credit spread only. If SPX breaks below 7,517 and holds, skip the put spread and consider call credit spread only.

## Scenario playbook

### Bull outcome

- **Trigger:** SPX accepts above 7,578 and breadth confirms.
- **Action:** Do not initiate the call side. If already in the iron condor, close or roll the call side quickly; leave the put side only if SPX holds above prior high and VIX is stable.
- **Adjustment:** Roll call shorts higher/out only for credit and only if the move slows below the expected-move upper band near 7,631.

### Bear outcome

- **Trigger:** SPX loses 7,517 and cannot reclaim it.
- **Action:** Do not initiate the put side. If already in the iron condor, close or roll the put side; take profit on the call side.
- **Adjustment:** Consider a call credit spread above 7,578 only after the failed reclaim is confirmed.

### Neutral outcome

- **Trigger:** SPX trades between 7,517 and 7,578 through the first hour, with VIX below 17.
- **Action:** Hold the iron condor for 40-50% max-profit capture, then close. Avoid holding challenged short strikes into the final hour.
- **Adjustment:** No roll needed if price stays inside the prior-day range and theta decay is working.

## Data and disclaimer

**Data sources:** FMP quote endpoint for ^GSPC, SPY, ^VIX; FMP historical-price-full for SPX, SPY, and VIX; FMP economic_calendar; FMP earning_calendar. Globex/overnight futures high-low was not available from FMP and should be confirmed from a broker or futures platform.

**Disclaimer:** This report is for educational and research purposes only and is not investment advice, a recommendation, or a solicitation to buy or sell securities, options, or futures. Options trading involves significant risk and may not be suitable for all investors.
