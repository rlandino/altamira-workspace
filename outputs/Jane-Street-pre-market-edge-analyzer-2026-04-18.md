# Jane Street Pre-Market Edge — 2026-04-18

## Market assessment
Latest tradable prints show SPX **7126.06** (+84.78, 1.20%) and SPY **710.14** (+8.48, 1.21%). With no explicit ES input provided, this report uses SPY/SPX cash levels as the pre-open proxy and flags that exact Globex highs/lows should come from broker futures.

Volatility is softer versus yesterday’s close: VIX **17.48** vs **17.94** (-0.46, -2.56%). Lower implied vol supports theta, but credit quality is usually thinner after a vol down-shift.

Calendar risk is **Light** today, and earnings concentration is low for major US index names. Net: standard intraday theta playbook is valid, with first-15-minute discipline and no oversized opening risk.

## Overnight futures movement
- **Gap proxy (SPY):** +8.48 points (+1.21%) vs prior close 701.66.
- **Equivalent SPX gap proxy:** +84.78 points (+1.20%).
- **View:** **Fade/Mean-Revert bias in first 30 minutes** — gap magnitude is >0.5%, which statistically increases early-session two-way trade and fade risk.

## Pre-market IV levels
- **Current VIX:** 17.48
- **Yesterday close (VIX):** 17.94
- **Change:** -0.46 (-2.56%)
- **Read-through:** Options are pricing **lower** volatility than yesterday; this favors premium selling after open stabilization.

## Economic calendar impact
- **Events today (FMP):** 1 total.
- **Notable item(s):**
  - 2026-04-18 10:00:00 ET — US IMF Meeting (Impact: Low)
- **Historical range impact:** CPI/NFP/FOMC days often expand SPX realized range to ~1.5x–2.0x normal; none of those are prominent in this feed.
- **Recommendation:** Normal opening process; avoid oversized risk in first 15 minutes only.

## Earnings exposure
- **Earnings entries in feed:** 116
- **US large-cap concentration:** Not obvious in this dataset
- **Assessment:** No clear US mega-cap earnings concentration in today's feed; single-name risk appears low for index options.
- **Market-moving potential:** **Low** for broad index unless unscheduled macro/news hits tape.

## Globex range and expected range
- **Globex overnight range:** Pull exact ES high/low from broker platform (not provided by FMP cash endpoints).
- **Proxy range (prior session SPX from SPY conversion):** High **7149**, Low **7082** (Range **67** points).
- **VIX-based expected 1-day move:** ±**78** SPX points (±**1.09%**) from current level.

## Opening gap strategy
- Because the gap proxy is significant, default to **wait 10–15 minutes**, then trade only after opening auction extremes define.
- If first 15-minute range breaks with breadth confirmation, avoid immediate fade and size down.
- If price re-enters opening range quickly, favor mean-reversion premium structures.

## IV crush opportunity
- **Yesterday high-IV event:** No clear high-impact event in the feed.
- **IV crush setup today:** **Moderate** — VIX already compressed; theta edge remains, but premiums are not extreme.

## Previous day’s close analysis
- Prior session (SPY) O/H/L/C: **706.14 / 712.39 / 705.76 / 710.14**.
- Market closed in the **middle of the range** of the range (66.1% from low to high).
- **Lean for today:** **neutral**, with continuation risk if opening pullbacks hold above prior midpoint.

## Support and resistance
### Support
1. **S1: 7100** — Round-number pivot / near short-term value area.
2. **S2: 7082** — Prior session low zone (converted from SPY).
3. **S3: 7050** — Approx. downside expected-move neighborhood.

### Resistance
1. **R1: 7150** — Round-number first supply zone.
2. **R2: 7149** — Prior session high zone (converted from SPY).
3. **R3: 7200** — Upside expected-move/psychological extension.

## Pre-market trade plan
- **Strategy:** SPX **0DTE iron condor** (next tradable session).
- **Structure (expected-move / ~0.10–0.15 delta proxy):**
  - Sell **7050 put** / Buy **7020 put**
  - Sell **7200 call** / Buy **7230 call**
- **Expiration:** Next SPX same-day expiry (0DTE at session open).
- **Entry window:** **9:40–9:55 AM ET** after opening range forms.
- **Risk sizing:** **1x normal, max 2–3% account risk** until directionality is confirmed.

## Scenario playbook
- **Bull outcome (price > R1):** Trim/close call spread early if tested; hold put side for theta decay toward 50%+ total target.
- **Bear outcome (price < S1):** Reduce/close put side risk on momentum break; keep or monetize call side as offset.
- **Neutral outcome (inside S1–R1):** Hold for 50% max profit or midday time-stop; avoid over-adjusting.

## Data and disclaimer
- **Data sources:** FMP quote (^GSPC, SPY, ^VIX), historical-price-full (SPY prior session), economic_calendar, earning_calendar.
- **Overnight/Globex:** Not supplied by FMP cash endpoints; use broker futures data for exact overnight high/low.
- **Disclaimer:** For educational/research purposes only. Not investment advice. Options involve risk and can result in substantial losses.
