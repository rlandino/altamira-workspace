# Jane Street Pre-Market Edge - 2026-05-26

## Market assessment

FMP is not showing a true ES/SPX pre-market futures print, so the working reference is the latest SPX quote/proxy at **7,473.47** against the prior SPX close of **7,473.48**. That implies essentially **no actionable opening gap** from the available data; use broker ES/SPX futures for the exact pre-market level before placing risk.

VIX is **16.73**, roughly flat versus the prior VIX close near **16.70** and below its recent 5-day average. Options are not aggressively repricing volatility pre-open, so the edge is not "sell everything at the bell"; the better structure is a defined-risk theta trade after the first macro data prints confirm the range.

The calendar is **moderate**: Chicago Fed activity at 8:30 AM ET, housing data at 9:00 AM ET, Consumer Confidence at 10:00 AM ET, and Dallas Fed manufacturing at 10:30 AM ET. Earnings exposure is mostly single-name, led by AutoZone before the open and Zscaler after the close, with limited direct index-weight risk.

## Overnight futures movement

- **Current working level:** SPX 7,473.47 from FMP quote/proxy.
- **Prior SPX close:** 7,473.48 on 2026-05-22.
- **Implied gap:** ~0 points / **0.00%**.
- **View:** **Uncertain / neutral open** - FMP does not provide Globex high/low or a reliable ES pre-market print. With no visible gap and a 10:00 AM ET macro catalyst, avoid forcing a directional open read.
- **Execution note:** Confirm ES/SPX futures from broker before 9:30 AM ET. If broker futures show a >0.5% gap not reflected here, switch to the gap/fade playbook below.

## Pre-market IV levels

- **Current VIX:** 16.73.
- **Prior VIX close:** ~16.70 from FMP historical VIX.
- **Change:** +0.03 vol points, roughly flat.
- **Read:** Volatility is **normal-to-soft**, not panic-premium. Premium selling is acceptable only with defined risk and after the 10:00 AM ET Consumer Confidence event.
- **Implication:** Favor 0DTE iron condors or one-sided spreads placed outside the VIX-implied range; avoid naked short gamma at the open.

## Economic calendar impact

| Time (ET) | Event | Impact | Trading implication |
|---|---:|---:|---|
| 8:30 AM | Chicago Fed National Activity Index (Apr) | Medium | Can nudge rates/cyclicals; usually not enough alone to invalidate an index theta plan. |
| 9:00 AM | House Price Index / Case-Shiller data | Low-Medium | Housing data can affect rates-sensitive sectors; watch yields and homebuilders. |
| 10:00 AM | CB Consumer Confidence (May) | High | Main range-expansion risk; a large surprise can push SPX beyond the opening balance. |
| 10:30 AM | Dallas Fed Manufacturing Index (May) | Medium | Secondary macro impulse; wait until after this if the 10:00 move is disorderly. |
| 11:30 AM / 1:00 PM | Bill / 2-year auctions and money supply | Low | Rates color later in the session, but lower event risk for 0DTE theta. |

**Calendar verdict:** **Moderate**. Trade smaller and later than a clean-calendar morning. Preferred entry is **10:35-10:50 AM ET** once Consumer Confidence and Dallas Fed risk are absorbed.

## Earnings exposure

FMP earnings calendar does not show mega-cap index constituents with high S&P 500 weight today. Notable larger names:

- **AZO - AutoZone (BMO):** large consumer discretionary retailer; single-name read-through to retail/consumer, but limited direct index shock.
- **TCOM - Trip.com (BMO):** travel/China ADR exposure; more global risk sentiment than SPX weight.
- **ZS - Zscaler (AMC):** high-beta software name; post-close single-name IV event, possible software sentiment read-through tomorrow.
- **SMTC / MOD / SQM (AMC):** sector-specific after-close risk; not primary SPX drivers pre-open.

**Market-moving potential:** **Low to medium**. Earnings do not argue for sitting out index theta by themselves; macro timing is the larger constraint.

## Globex range and expected range

- **Globex range:** Not available from FMP. Use broker/futures platform for overnight ES high/low.
- **Prior SPX session range:** 7,506.32 high to 7,463.29 low = **43.03 points**.
- **VIX-implied 1-day move:** 7,473.47 x 16.73% / sqrt(252) = **+/- 79 points** (~**+/- 1.05%**).
- **Expected SPX range from current proxy:** approximately **7,395 to 7,552**.

## Opening gap strategy

- **Base case:** **Stay flat until after 10:00 AM ET**. No reliable gap is visible from FMP, and the highest-impact macro event arrives after the open.
- **If broker ES shows a small gap (<0.3%):** Let the first 15-30 minutes define the opening balance; sell premium only after failed range expansion.
- **If broker ES shows a large gap (>0.5%):** Expect a higher probability of early fade unless Consumer Confidence confirms the move. Do not sell the challenged side until the first reversal/acceptance signal appears.
- **If SPX breaks and holds outside 7,463-7,506 before 10:00:** Reduce size or wait for a post-data retest rather than fading blindly.

## IV crush opportunity

Yesterday was not a major scheduled high-IV macro event, and VIX is flat-to-soft rather than elevated. There is **no special overnight IV-crush setup**; the opportunity is standard intraday theta if realized range stays below the VIX-implied +/-79 point band.

Best expression: sell defined-risk premium after 10:30 AM ET if SPX remains inside the prior-day range or reclaims it quickly after a data spike.

## Previous day's close analysis

Prior SPX session:

- **Open:** 7,468.82
- **High:** 7,506.32
- **Low:** 7,463.29
- **Close:** 7,473.48

SPX closed in the **lower third** of the prior day's range, near the lows but not on the absolute low. Per the command heuristic, this gives a mild **bullish mean-reversion lean** for today, but the 10:00 AM ET macro print matters more than the close-location signal.

## Support and resistance

### Support

1. **7,463** - Prior day low; first downside acceptance/fade line.
2. **7,450** - Round-number support just below the prior range; watch for stops if broken.
3. **7,395** - VIX-implied 1-day downside expected move.

### Resistance

1. **7,506** - Prior day high; first upside rejection/acceptance line.
2. **7,520** - Round-number / recent high zone near the FMP 52-week high area.
3. **7,552** - VIX-implied 1-day upside expected move.

## Pre-market trade plan

**Primary plan: 0DTE SPX iron condor after macro data**

- **Strategy:** Defined-risk 0DTE SPX iron condor.
- **Expiration:** Today, 2026-05-26.
- **Entry window:** **10:35-10:50 AM ET**, after Consumer Confidence and Dallas Fed manufacturing.
- **Structure, using expected-move strikes if live deltas are unavailable:**
  - Sell **7,395 put**
  - Buy **7,385 put**
  - Sell **7,555 call**
  - Buy **7,565 call**
- **Delta target:** short strikes should approximate 0.10-0.15 delta on the live chain. If broker deltas differ materially, adjust to nearest 0.10-0.15 delta strikes outside the post-data range.
- **Minimum credit:** Target at least **$1.50-$2.50** total credit for a 10-point-wide SPX condor; skip if pricing is too thin after the data.
- **Position size:** **1x normal / max 2% account risk**. Cut to half-size if VIX rises above 18 or SPX is outside the prior-day range when entering.
- **Stop/adjustment:** Close or reduce the threatened side if SPX accepts beyond the short strike or if the spread value reaches ~2x credit received.
- **Profit target:** Close at **50%-60% of max profit**; do not hold full size into the final hour if SPX is trending.

**No-trade conditions**

- SPX is outside **7,395-7,552** and expanding after 10:30 AM ET.
- VIX spikes above **18** with breadth deteriorating.
- The live chain cannot pay an adequate credit for defined-risk wings.

## Scenario playbook

### Bull outcome

- **Trigger:** SPX reclaims/holds above **7,506** after 10:00 AM ET.
- **Action:** Do not sell the call side immediately into upside momentum. Wait for a failed push near 7,520 or move the call spread above the live 0.10 delta. If already in the condor, take off the put side at 50%-70% profit and manage the call side tightly.

### Bear outcome

- **Trigger:** SPX breaks and accepts below **7,463**.
- **Action:** Avoid initiating the put side until price stabilizes. If in the condor, close the put spread on acceptance below support and keep/harvest the call side. Re-enter only after a reclaim of 7,463 or a controlled test of 7,450.

### Neutral outcome

- **Trigger:** SPX remains between **7,463 and 7,506** after the macro prints.
- **Action:** Execute the planned 7,395/7,385 x 7,555/7,565 condor, take profits at 50%-60%, and avoid over-adjusting inside the prior-day range.

## Data and disclaimer

**Data sources:** FMP quote for `^GSPC`, `SPY`, and `^VIX`; FMP historical prices for SPX, SPY, and VIX; FMP economic calendar; FMP earnings calendar. Globex/overnight futures high-low were not available from FMP and should be confirmed from a broker or futures platform.

**Disclaimer:** This report is for educational and research purposes only. It is not investment advice, a recommendation, or an offer to buy or sell securities, options, futures, or derivatives. Options and 0DTE strategies involve substantial risk and may not be suitable for all investors.
