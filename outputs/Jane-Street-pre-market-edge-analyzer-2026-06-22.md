# Jane Street Pre-Market Edge - 2026-06-22

## Market assessment

FMP did not provide a true ES/SPX Globex high-low or extended-hours pre-market print. Using the latest FMP SPX/SPY quote and the latest completed SPX session as the proxy, SPX is effectively flat around 7500.6 versus the most recent completed close at 7500.6. Exact SPX/ES from a broker or futures platform would refine the opening gap read.

VIX is 17.32 versus the latest completed VIX close of 16.40, up 0.92 vol points (+5.6%). Options are pricing modestly more event risk than the prior session, but VIX remains below its 50-day average of 17.79 and 200-day average of 18.56, so this is normal-to-slightly-firm volatility rather than a panic premium.

The calendar is moderate: Canada CPI before the cash open, a Fed Waller speech around 9:00 AM ET, bill auctions late morning, and CFTC positioning late day. No mega-cap or index-heavy earnings names showed in today's FMP earnings calendar. The setup favors defined-risk theta after the first 15-30 minutes, not pre-open premium selling.

## Overnight futures movement

- **Proxy level:** SPX 7500.58; SPY 746.74.
- **Prior completed SPX close:** 7500.57 on 2026-06-18.
- **Gap:** +0.01 pts (+0.00%) using FMP quote versus latest completed close.
- **View:** **Uncertain / wait for confirmation** - FMP does not expose true Globex range, and the visible proxy is flat. If broker ES shows a gap greater than 0.5%, expect the first move to be vulnerable to a fade unless SPX holds above 7511.

## Pre-market IV levels

- **Current VIX:** 17.32.
- **Latest completed VIX close:** 16.40.
- **Change:** +0.92 vol points (+5.6%).
- **Read:** Options are carrying slightly higher premium than the prior completed session. This supports selling defined-risk premium, but only after Waller/opening-flow risk clears.

## Economic calendar impact

Times below are converted to approximate ET from FMP calendar timestamps.

- **8:30 AM ET - Canada CPI (May):** Secondary for SPX, but inflation surprises can move rates and index futures at the margin.
- **9:00 AM ET - Fed Waller speech:** Medium impact. Fed speakers can widen the first-hour range; avoid initiating short premium before the market digests the remarks.
- **10:00 AM ET - EU Consumer Confidence:** Low-to-medium U.S. index impact, mostly risk-sentiment context.
- **11:30 AM ET - U.S. 3-month and 6-month bill auctions:** Low direct impact, but watch rates if auction tails.
- **3:30 PM ET - CFTC S&P 500 / Nasdaq positioning:** Usually not an intraday catalyst for 0DTE entry, but can affect late-day positioning.

**Calendar grade:** Moderate. **Recommendation:** trade after the early Fed/opening window, use defined-risk spreads, and keep strikes outside the VIX one-day expected range.

## Earnings exposure

- **FMP earnings calendar count:** 353 companies for 2026-06-22.
- **Mega-cap / index-heavy names found:** none from the monitored large-cap set.
- **Market-moving potential:** Low. Today's earnings risk appears concentrated in smaller or non-U.S. names rather than broad-index constituents.
- **Theta implication:** No major single-name IV event should dominate SPX index volatility today.

## Globex range and expected range

- **Globex range:** Not available from FMP. Use broker/futures platform for exact ES overnight high/low.
- **Proxy range:** Latest completed SPX session high 7511.07, low 7468.32, range 42.75 pts.
- **VIX-implied 1-day expected move:** +/-81.8 pts, using SPX 7500.58 x 17.32% / sqrt(252).
- **Expected range:** roughly **7419 to 7582**.

## Opening gap strategy

- **If broker ES confirms flat to small gap:** Run normal defined-risk theta after the first 15-30 minutes.
- **If gap up above 7511 holds for 15 minutes:** Do not fight the trend; widen or skip the call side until price rejects the breakout.
- **If gap up fails back below 7500:** Fade bias increases; favor call credit spreads or an iron condor centered below 7500.
- **If gap down below 7468:** Stay flat until support either reclaims or fails; avoid selling puts into a fast downside tape.

## IV crush opportunity

Yesterday was not a major scheduled U.S. macro event in the fetched calendar, but VIX is firmer than the latest completed close. There is a modest intraday IV-normalization opportunity if Waller's remarks do not add rate volatility. This is a **sell-premium-with-defined-risk** setup, not an aggressive naked premium setup.

## Previous day's close analysis

- **Prior completed SPX session:** open 7487.36, high 7511.07, low 7468.32, close 7500.57.
- **Close location:** upper quartile of the range, about 75% from low to high.
- **Lean:** Momentum closed constructive, but from a morning theta perspective an upper-range close creates fade risk if buyers cannot reclaim or hold 7511.

## Support and resistance

### Support

1. **7500** - prior completed close and large round-number pivot.
2. **7468** - prior completed session low; first real downside acceptance level.
3. **7419-7420** - VIX-implied lower bound and near the prior 7420 close area.

### Resistance

1. **7511** - prior completed session high; first breakout trigger.
2. **7550** - round-number extension level inside the expected range.
3. **7582-7600** - VIX-implied upper bound, with 7600 as the psychological cap.

## Pre-market trade plan

- **Strategy:** 0DTE SPX iron condor.
- **Expiration:** Today, 2026-06-22.
- **Entry window:** 9:45-10:05 AM ET, after the cash open and Fed Waller headline risk are absorbed.
- **Structure:**
  - Sell **7420 put** / buy **7410 put**.
  - Sell **7580 call** / buy **7590 call**.
- **Strike logic:** Short strikes sit near the VIX-implied one-day range boundaries, approximating 0.10-0.15 delta when live chain deltas are unavailable.
- **Position size:** 1-2% of account at risk due to moderate calendar risk; scale only if SPX stays inside 7468-7511 after the first 30 minutes.
- **Profit target:** Close at 50% of max profit.
- **Stop:** Close or adjust if either short strike is breached or the spread trades near 2x entry credit.

## Scenario playbook

### Bull outcome

- **Trigger:** SPX accepts above 7511 and holds above it after 10:00 AM ET.
- **Action:** Do not add call-side risk. If already in the iron condor, close or roll the 7580/7590 call spread higher; keep the put side only if VIX is falling and price is orderly.

### Bear outcome

- **Trigger:** SPX loses 7500, then breaks 7468 with breadth deterioration.
- **Action:** Close or roll the 7420/7410 put spread before momentum reaches the short strike. Consider leaving the call side on for decay only after downside velocity slows.

### Neutral outcome

- **Trigger:** SPX remains between 7468 and 7511 through the first hour.
- **Action:** Hold the iron condor for 50% max profit, then close. No adjustment needed unless VIX expands above 18.5 or price tests either short strike.

## Data and disclaimer

- **Data sources:** FMP quote for ^GSPC, SPY, ^VIX; FMP historical-price-full for ^GSPC, SPY, and ^VIX; FMP economic_calendar; FMP earning_calendar.
- **Data limitations:** No user-supplied ES/SPX futures price was provided. FMP did not expose true pre-market/Globex high-low fields, so the report uses FMP quote and latest completed-session data as proxies. Confirm exact ES level, overnight high/low, and live option deltas with a broker before trading.
- **Disclaimer:** For educational and research purposes only. This is not investment advice, a solicitation, or a recommendation to buy or sell securities or derivatives. Options involve risk and can result in losses exceeding the premium received.
