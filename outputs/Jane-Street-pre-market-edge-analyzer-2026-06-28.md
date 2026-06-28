# Jane Street Pre-Market Edge — 2026-06-28

## Market assessment

Today is Sunday, so there is no regular U.S. cash equity or SPX options session. FMP quote data is therefore treated as Friday's close, not a live 8 AM pre-market futures print. Exact SPX/ES overnight levels should come from the broker/futures platform before Monday's cash open.

SPX closed Friday at 7,354.02 after trading a 98.77-point range. With no live futures input, the inferred cash-market gap is 0.00 points (0.00%); the correct stance is no trade today and reassess Monday after the first 15 minutes of price discovery.

VIX closed at 18.41, down from 18.89 the prior session, so index options are pricing slightly less volatility than yesterday and near the recent short-term average. Calendar risk is light-to-moderate: no U.S. cash-session macro print is shown, but a Fed Barkin speech appears on the calendar.

## Overnight futures movement

- **Current SPX reference:** 7,354.02 from FMP quote, interpreted as Friday cash close.
- **Prior SPX close:** 7,354.02.
- **Inferred gap:** 0.00 points (0.00%).
- **View:** **Uncertain / no actionable gap** — Sunday cash-market data is stale; use broker ES/SPX futures for the real overnight gap before Monday's open.
- **Gap hold/fade read:** If Monday opens inside Friday's 7,294-7,393 range, favor normal theta after the open settles. If ES gaps more than +/-0.5%, expect a higher early fade probability unless a macro catalyst confirms continuation.

## Pre-market IV levels

- **VIX reference:** 18.41 from FMP quote.
- **Prior VIX close:** 18.89.
- **Change vs prior close:** -0.48 points (-2.54%).
- **Recent context:** The latest VIX close is near the recent 5-session average of roughly 18.54.
- **Theta implication:** Premium is tradable but not fat enough to justify forcing size on stale Sunday data. Sell defined-risk premium only after confirming Monday's opening range and event tape.

## Economic calendar impact

- **Fed Barkin Speech** — 2026-06-28 16:35, United States, medium impact.
  - Fed speakers can move rates and equity-index vol if comments shift the policy path, but this is usually less range-expanding than CPI, NFP, or FOMC.
- **No U.S. cash-session high-impact release** was returned for today by FMP.
- **Today's calendar:** **Light-to-moderate**.
- **Recommendation:** No Sunday SPX options trade. For the next cash session, use normal-to-slightly-wider strikes and avoid opening short premium immediately before any unscheduled Fed headline.

## Earnings exposure

- FMP returned **no earnings calendar entries** for 2026-06-28.
- **Market-moving potential:** Low for today. Single-name earnings risk is not the main driver; macro/futures positioning and Monday opening flows matter more.

## Globex range and expected range

- **Globex range:** From broker/futures platform. FMP does not provide ES Globex high/low in this workflow.
- **Proxy range:** Friday SPX high 7,392.95, low 7,294.18; range 98.77 points.
- **VIX-based 1-day expected move:** 7,354.02 x 18.41% / sqrt(252) = approximately **+/-85 points** (**+/-1.16%**).
- **Expected range from reference price:** approximately **7,269 to 7,439**.

## Opening gap strategy

- **Today:** No trade; U.S. cash index options are closed on Sunday.
- **Next cash session if gap is small (<0.3%):** Define the first 15-minute range, then sell defined-risk theta outside Friday's range / expected-move bands.
- **Next cash session if gap is large (>0.5%):** Stay flat until 10:00 AM ET. Fade only after failed continuation; do not sell the threatened side while price is still accepting beyond Friday's range.
- **Caution:** A confirmed break above 7,400 or below 7,294 changes the plan from range-theta to trend-risk management.

## IV crush opportunity

- Friday was **not** identified as a major scheduled high-IV event like CPI, NFP, or FOMC.
- VIX is lower than the prior close and near its 5-session average, so there is **no clear index-level IV crush edge** today.
- Best use of theta: wait for Monday's realized opening range, then sell defined-risk premium only if implied range still overstates the intraday tape.

## Previous day's close analysis

- **Friday SPX open:** 7,312.74.
- **Friday SPX high:** 7,392.95.
- **Friday SPX low:** 7,294.18.
- **Friday SPX close:** 7,354.02.
- **Close location:** Around 61% of the day's range, upper-middle rather than pinned at an extreme.
- **Lean for next session:** **Neutral to slightly mean-reverting** — not enough evidence to chase upside, but Friday's close held above the open and above the range midpoint.

## Support and resistance

### Support

1. **7,313** — Friday open / intraday pivot; first level where dip buyers should defend if the market remains balanced.
2. **7,294** — Friday low; loss of this level signals downside acceptance outside the prior range.
3. **7,269** — VIX-based expected-move lower boundary; short-put risk should be reassessed before this zone.

### Resistance

1. **7,393** — Friday high; first upside stall point.
2. **7,400** — Round-number resistance just above Friday's high; breakout confirmation level.
3. **7,439** — VIX-based expected-move upper boundary; short-call risk should be reassessed before this zone.

## Pre-market trade plan

- **Exact strategy for today:** **No trade — sit out** because today is Sunday and cash SPX options are closed.
- **Conditional next-session strategy:** 0DTE SPX iron condor only if Monday opens inside Friday's range and the first 15-minute range is balanced.
- **Indicative strikes from expected-move bands, not live option-chain deltas:**
  - Short put: **7,270**
  - Long put: **7,250**
  - Short call: **7,440**
  - Long call: **7,460**
- **Expiration:** Next listed 0DTE cash session; otherwise the nearest weekly expiration.
- **Entry time:** 9:45-10:00 AM ET after the opening range settles; do not enter on the open.
- **Position size:** 1x normal defined-risk unit, capped at **1-2% of account at risk** because Sunday data is stale and the next-session gap is unknown.
- **Risk trigger:** Close or hedge the threatened side if SPX accepts beyond 7,294 or 7,400 with expanding breadth/volume.

## Scenario playbook

- **Bull outcome:** SPX accepts above 7,393 and then 7,400.
  - **Action:** Do not add call-side premium. Close or roll the call spread if price holds above 7,400 for 15-30 minutes; keep put side only if deltas compress and premium reaches the 50% profit target.
- **Bear outcome:** SPX loses 7,313 and tests 7,294.
  - **Action:** Close or roll the put spread before a clean break of 7,294. Take profits on the call side; avoid doubling down until price reclaims Friday's range.
- **Neutral outcome:** SPX stays between 7,313 and 7,393.
  - **Action:** Hold the condor to 50% max profit or late-day decay, with no adjustment unless either short strike reaches roughly 25-30 delta.

## Data and disclaimer

- **Data sources:** FMP quote for ^GSPC, SPY, and ^VIX; FMP historical-price-full for SPY, ^GSPC, and ^VIX; FMP economic calendar; FMP earnings calendar.
- **Data limitation:** Globex/overnight futures high-low was not available from FMP. Use broker ES/SPX futures for exact overnight range and gap before trading.
- **Disclaimer:** This briefing is for educational and research purposes only and is not investment advice. Options involve substantial risk and may not be suitable for all investors.
