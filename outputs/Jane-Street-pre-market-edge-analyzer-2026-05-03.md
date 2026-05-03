# Jane Street Pre-Market Edge - 2026-05-03

## Market assessment

Today is Sunday, so there is no regular US cash session and no true 0DTE SPX/SPY trade to initiate. FMP quote data reflects the last available Friday close: SPX 7,230.12, SPY 720.65, and VIX 16.99. SPX/ES from broker is required for exact Sunday evening futures and Globex levels.

Friday's tape closed near the bottom of the intraday SPY range after printing fresh highs, which argues for patience rather than chasing strength. With no live Sunday pre-market liquidity, the correct desk stance is to prepare levels now and re-price the plan after ES opens and after the first 15 minutes of Monday cash trade.

Volatility is normal-to-low: VIX closed 16.99, only 0.10 points above the prior close but below its 50-day average. Premium selling can work when the market reopens, but strike selection should use Monday's live futures gap and the opening range.

## Overnight futures movement

- **Live futures input:** Not supplied.
- **FMP proxy:** Last cash close only; no Sunday pre-market print available.
- **Reference close:** SPX 7,230.12 / SPY 720.65 from Friday.
- **Inferred gap:** 0.0 points / 0.00% using stale FMP cash close data.
- **View:** **Uncertain - no trade signal until ES/Globex opens.** If Monday opens with a gap greater than 0.5%, fade risk rises; if the gap is inside 0.25%, normal opening-range theta setup is favored.

## Pre-market IV levels

- **Current VIX:** 16.99.
- **Prior VIX close:** 16.89.
- **Change:** +0.10 points / +0.59%.
- **50-day VIX average:** 22.24.
- **200-day VIX average:** 18.28.
- **Read:** Options priced only slightly richer than the prior close and still below recent averages. This is not a panic-premium environment; sell premium only after confirming Monday's gap and breadth.

## Economic calendar impact

- **Today, Sunday 2026-05-03:** No market-moving US economic releases in the FMP calendar feed.
- **Feed note:** FMP returned several non-US Monday calendar rows when queried for today; none are US index drivers.
- **Calendar weight:** **Light for today.**
- **Recommendation:** Do not initiate an index theta trade on Sunday. For Monday, re-check the US calendar before selling 0DTE premium; widen strikes or wait until after any 10:00 AM ET macro release if one appears on the live broker calendar.

## Earnings exposure

- **Today:** No major US index-heavy earnings in the FMP earnings feed.
- **Items returned:** ACV.SI and WBCPL.AX, neither relevant to SPX index risk.
- **Market-moving potential:** **Low** for today. Re-check Monday BMO/AMC reports before using a full-size SPX/SPY premium-selling plan.

## Globex range and expected range

- **Globex range:** From broker/futures platform. FMP does not provide Sunday ES overnight high/low.
- **Prior cash-session proxy:** SPY high 724.87, low 720.47, range 4.40 SPY points, roughly 44 SPX points.
- **VIX-based 1-day expected move:** SPX 7,230.12 x 16.99% / sqrt(252) = approximately **+/-77 points** (about +/-1.07%).
- **Expected SPX range from last close:** Roughly **7,153 to 7,307**.

## Opening gap strategy

- **Today:** No trade - US cash market closed.
- **For the next cash open:** Wait until 9:35-9:50 AM ET. If the opening gap is greater than 0.5% without a fresh catalyst, favor fading the gap with defined-risk spreads outside the expected move. If the gap is small and breadth is balanced, sell a wider 0DTE iron condor after the opening range forms.

## IV crush opportunity

- **Yesterday/last session:** No obvious high-IV macro event from the available data.
- **IV setup:** VIX is stable and below the 50-day average, so the opportunity is ordinary intraday theta rather than event-driven IV crush.
- **Implication:** Premium can be sold when the market reopens, but only with defined risk and strikes outside the live expected move.

## Previous day's close analysis

- **SPY Friday OHLC:** Open 721.25, high 724.87, low 720.47, close 720.65.
- **Range position:** Close was roughly 4% above the low of the day.
- **Lean:** **Bullish/rebound lean by mean-reversion logic, but tactically neutral until Monday's futures confirm.** A close near the lows after a high print often leaves room for a relief bounce if no weekend risk emerges.

## Support and resistance

### Support

1. **7,230 / 720.65 SPY - Friday close and Friday low zone.** First reference level because cash closed almost on the lows.
2. **7,209 / 718.66 SPY - Prior close / round 7,200 zone.** A break here would signal that Friday's weakness is carrying through.
3. **7,153 / 713 SPY - VIX expected-move lower band.** A breach would imply a full one-day expected move and argues against short-premium complacency.

### Resistance

1. **7,250 / 725 SPY - First round-number stall zone.** Watch for early rejection if Monday opens firm.
2. **7,273 / 724.87 SPY - Friday high.** A reclaim would confirm momentum continuation after Friday's intraday fade.
3. **7,307 / 728 SPY - VIX expected-move upper band.** Above here, call-side shorts need adjustment or removal.

## Pre-market trade plan

- **Strategy:** **No trade today - market closed.** Prepare a Monday 0DTE SPX iron condor only if the live open is orderly.
- **Conditional Monday structure:** 0DTE SPX iron condor using expected-move strikes.
- **Indicative strikes from last close:** Sell 7,150 put / buy 7,140 put and sell 7,310 call / buy 7,320 call. Re-price to live 0.10-0.15 delta strikes on Monday; do not use these as executable quotes without chain confirmation.
- **Expiration:** Next available 0DTE cash session.
- **Entry time:** 9:35-9:50 AM ET after the opening range settles; wait longer if Monday's calendar has a 10:00 AM ET release.
- **Position size:** 1x normal defined-risk size only if gap is inside 0.5% and VIX remains under 18; reduce to 0.5x or skip if gap exceeds 0.75%.

## Scenario playbook

- **Bull outcome:** SPX reclaims 7,250 and holds above it. Avoid adding call-side risk; if already in an iron condor, close or roll the call side when spot approaches 7,273.
- **Bear outcome:** SPX loses 7,230 and then 7,209. Close threatened put spreads quickly; keep or harvest call-side premium only after downside momentum slows.
- **Neutral outcome:** SPX remains between 7,209 and 7,273 through the first hour. Enter or hold defined-risk condor, target 50% of max profit, and close before late-day gamma expansion.

## Data and disclaimer

- **Data sources:** FMP quote endpoint for ^GSPC, SPY, and ^VIX; FMP historical-price-full for SPY and ^VIX; FMP economic_calendar; FMP earning_calendar.
- **Data limitations:** Sunday report uses stale Friday cash close data. Exact SPX/ES futures, Globex high/low, and live option deltas must come from the broker/futures platform before execution.
- **Disclaimer:** For educational and research purposes only. Not investment advice, not a recommendation to buy or sell securities or options, and not suitable without independent risk review.
