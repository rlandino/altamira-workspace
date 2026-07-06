# Jane Street Pre-Market Edge - 2026-07-06

## Market assessment

Official FMP quote data shows SPX effectively flat at 7,483.24 versus the last official close. FMP did not provide a reliable ES/SPX pre-market futures level or Globex high/low, so use SPX/ES from broker for the exact overnight gap. On available data, there is no confirmed gap edge to chase before the open.

VIX is 16.31, about 1.0% above the prior VIX close of 16.15, but still below the recent 5-day average near 17.05 and below the 50-day average near 17.63. Options pricing is a little firmer than the prior close, but not high enough to justify aggressive naked premium selling ahead of the 10:00 AM ET ISM services cluster.

The prior SPX session closed in the middle of its range, which gives a neutral overnight read. Calendar risk is moderate because ISM Services PMI, ISM Non-Manufacturing PMI, and ISM prices all hit at 10:00 AM ET, followed by Fed Waller at 11:00 AM ET. Earnings exposure is low; no mega-cap index constituent appears on today's FMP earnings calendar.

## Overnight futures movement

- **Reference price:** SPX 7,483.24 from FMP official quote data; no user-supplied ES/SPX futures price.
- **Prior official SPX close:** 7,483.24 on 2026-07-02.
- **Implied gap from available data:** ~0 points, ~0.00%.
- **View:** **Uncertain / no edge before futures confirmation.** With no reliable Globex data and a flat official quote, wait for the first post-open auction and the 10:00 AM ET ISM print before committing size.

## Pre-market IV levels

- **Current VIX:** 16.31.
- **Prior VIX close:** 16.15.
- **Change vs prior close:** +0.16 vol points, about +1.0%.
- **Recent context:** Current VIX is below the recent 5-day average near 17.05, below the 50-day average near 17.63, and below the 200-day average near 18.67.
- **Theta implication:** Premium is tradable but not rich. Favor defined-risk spreads, wider strikes, and entry after the 10:00 AM ET macro impulse.

## Economic calendar impact

Today's U.S. calendar is **moderate** because the main risk is concentrated after the open:

- **10:00 AM ET - ISM Services PMI (Jun):** Estimate 54.0 vs prior 54.5. High impact; services PMI can expand the intraday SPX range by roughly 1.25x-1.5x when the surprise is large.
- **10:00 AM ET - ISM Non-Manufacturing PMI (Jun):** Estimate 54.2 vs prior 54.5. High impact; confirms or contradicts the services signal.
- **10:00 AM ET - ISM Non-Manufacturing Prices (Jun):** Prior 71.3. High impact when inflation-sensitive; hot prices can pressure rates and equity multiples.
- **10:00 AM ET - ISM Non-Manufacturing Employment / Services Employment:** Medium-to-low impact, but relevant for growth-labor mix.
- **11:00 AM ET - Fed Waller Speech:** Medium impact; avoid assuming IV crush is complete until the first comments are digested.
- **11:30 AM ET - 3-Month and 6-Month Bill Auctions:** Low impact unless rates move sharply.
- **3:30 PM ET - CFTC S&P 500 and Nasdaq 100 speculative net positions:** Medium impact for positioning context, usually low immediate index-vol effect.

**Recommendation:** Do not sell the opening bell blindly. Let the 9:35-9:50 AM ET opening range print, then either wait until after the 10:00 AM ET ISM data or use half-size only before the release.

## Earnings exposure

FMP lists 333 earnings-calendar entries for today, but no mega-cap index-heavy company appears in the market-moving set. The largest names by available quote market cap are:

- **BMNR - Bitmine Immersion Technologies:** ~$8.2B market cap, time not specified.
- **FBGGF - Fabege AB:** ~$2.6B market cap, time not specified; non-U.S./OTC exposure.
- **BNED - Barnes & Noble Education:** ~$0.4B market cap, time not specified.
- **CRMT - America's Car-Mart:** small-cap, time not specified.

**Market-moving potential:** Low for SPX. Single-name IV can move in these tickers, but index impact should be limited unless broader risk sentiment is already unstable.

## Globex range and expected range

- **Globex range:** Not available from FMP. Use broker/futures platform for ES overnight high, low, and volume profile.
- **Proxy range:** Prior SPX session high 7,540.75, low 7,427.55, range 113.20 points.
- **VIX-based 1-day expected move:** 7,483.24 x 16.31% / sqrt(252) = approximately **+/-77 points** (~+/-1.03%).
- **Expected range from reference price:** roughly **7,406 to 7,560**.

## Opening gap strategy

- **If ES confirms a flat-to-small gap (<0.25%):** Normal theta setup, but wait for the opening range and the 10:00 AM ET ISM release before full size.
- **If ES confirms a gap >0.50%:** Fade bias only after a failed continuation through the first 15-30 minutes; do not pre-position against a strong gap before ISM.
- **Base case:** Stay cautious until 10:05-10:15 AM ET, then sell defined-risk premium outside the VIX expected range if SPX remains inside 7,406-7,560.

## IV crush opportunity

Yesterday was not identified as a major high-IV scheduled event day in the fetched calendar data, and VIX is not elevated versus recent averages. The better IV-crush setup is **post-ISM**: if the 10:00 AM ET print passes without a trend break, intraday IV should decay and support a 0DTE iron condor or single-side credit spread.

## Previous day's close analysis

- **Prior SPX open:** 7,495.14.
- **Prior SPX high:** 7,540.75.
- **Prior SPX low:** 7,427.55.
- **Prior SPX close:** 7,483.24.
- **Close location:** About 49% of the way up from the low to the high, essentially the middle of the range.
- **Read:** Neutral. The market did not close pinned to highs or lows, so directional conviction should come from the opening range and 10:00 AM ET data rather than the prior close.

## Support and resistance

### Support

1. **7,428 - Prior session low:** First real downside reference; loss of this level after ISM shifts the day from range-bound to bearish.
2. **7,406 / 7,400 - VIX expected-move lower edge and round-number shelf:** Natural lower boundary for 0DTE short-put placement.
3. **7,350 - Prior swing support / round-number zone:** Near the 2026-06-29 low area at 7,348.88; break below here signals a larger volatility expansion.

### Resistance

1. **7,500 - Round-number pivot:** First upside stall point and psychological reference.
2. **7,541 - Prior session high:** Clean resistance; break and hold above here suggests buyers can extend.
3. **7,560 - VIX expected-move upper edge:** Natural upper boundary for 0DTE short-call placement; sustained trade above it means implied move is being exceeded.

## Pre-market trade plan

**Primary plan: event-aware 0DTE SPX iron condor, entered after ISM.**

- **Strategy:** 0DTE SPX iron condor, defined risk.
- **Expiration:** Today, 2026-07-06.
- **Indicative strikes:** Sell **7,395 put**, buy **7,380 put**; sell **7,570 call**, buy **7,585 call**.
- **Delta target:** Confirm live chain before entry; short legs should be near 0.10-0.15 delta and outside the post-ISM expected range.
- **Entry window:** Prefer **10:05-10:20 AM ET** after ISM and the first reaction settle. If entering before ISM, use half-size and wider strikes.
- **Position size:** 0.5x-1.0x normal size; cap max loss at 1%-2% of account equity due to macro-event risk.
- **Profit target:** Close at 50%-60% of max profit, or close by 2:30 PM ET if premium decay stalls.
- **Stop:** Exit or adjust if either short strike is tested, or if spread value reaches roughly 2x credit received.

**Fallback if SPX trends hard after ISM:**

- If price breaks and holds above 7,541, skip the call side and consider only a lower-probability put credit spread below 7,400.
- If price breaks and holds below 7,428, skip the put side and consider only a call credit spread above 7,560 after a failed bounce.
- If bid/ask spreads are poor, use SPY equivalents around **739.5/738.0 puts** and **757.0/758.5 calls**, adjusted to live strikes and deltas.

## Scenario playbook

### Bull outcome

- **Trigger:** SPX holds above 7,500 and then breaks 7,541 after ISM.
- **Action:** Do not sell fresh call premium into momentum. Close or avoid the call side; keep only a far-out put spread if IV remains firm and breadth supports the move.
- **Risk control:** If already in the iron condor, cut the call spread if SPX holds above 7,541 for 10-15 minutes or if the short call delta expands materially.

### Bear outcome

- **Trigger:** SPX loses 7,428 and fails to reclaim it after ISM.
- **Action:** Do not sell fresh put premium into downside momentum. Close or avoid the put side; consider a defined-risk call credit spread above 7,560 only after a failed reclaim.
- **Risk control:** If already in the iron condor, cut the put spread if SPX holds below 7,428 or if the short put is tested.

### Neutral outcome

- **Trigger:** SPX remains between 7,428 and 7,541 after the 10:00 AM ET data.
- **Action:** Execute the 7,395/7,380 put spread and 7,570/7,585 call spread only if live deltas and premium justify the risk. Hold for 50%-60% of max profit; avoid over-managing unless SPX approaches support or resistance.
- **Risk control:** No adjustment if price stays inside the prior-day range and VIX fades; close into strength of P&L before late-day headline risk.

## Data and disclaimer

**Data sources:** Financial Modeling Prep quote data for `^GSPC`, `SPY`, and `^VIX`; FMP historical-price-full for SPX, SPY, and VIX prior sessions; FMP economic calendar for 2026-07-06; FMP earnings calendar for 2026-07-06. Globex/overnight high-low was not available from FMP and should be verified on a broker or futures platform.

**Disclaimer:** This briefing is for educational and research purposes only and is not investment advice, a recommendation, or a solicitation to buy or sell securities or derivatives. Options involve substantial risk and may not be suitable for all investors. Verify all prices, deltas, liquidity, event times, and risk limits before placing any trade.
