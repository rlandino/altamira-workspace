# Jane Street Pre-Market Edge - 2026-06-17

## Market assessment

SPX proxy is **7,511.35** using FMP cash-index/SPY data; no SPX/ES futures input was supplied, so use your broker for exact futures and Globex high/low. The inferred gap is **-42.94 pts (-0.57%)** versus prior SPX close. **Gap view: Uncertain until event risk clears** - High-impact macro risk can overwhelm normal gap-fade statistics.

VIX is **16.47** versus prior close **16.41** (0.06 pts, +0.37%). Options are pricing volatility **flat** versus yesterday; normal theta setup; edge comes from levels and patience rather than IV crush alone.

Prior SPY session (2026-06-16) closed **at/near lows** of its range, giving a **Bullish-to-neutral** tape read. Calendar load is **Heavy**: Fed interest-rate decision and FOMC projections at 18:00 UTC / 2:00 PM ET, followed by the Fed press conference at 18:30 UTC / 2:30 PM ET.

## Overnight futures movement

- **Current SPX/ES proxy:** 7,511.35 (FMP ^GSPC/SPY proxy; SPX/ES from broker for exact futures).
- **Prior SPX close:** 7,554.29.
- **Inferred gap:** -42.94 pts (-0.57%).
- **View:** Uncertain until event risk clears - High-impact macro risk can overwhelm normal gap-fade statistics.

## Pre-market IV levels

- **Current VIX:** 16.47.
- **Yesterday VIX close:** 16.41.
- **5-day / 20-day VIX average:** 18.39 / 17.44.
- **Implication:** normal theta setup; edge comes from levels and patience rather than IV crush alone.

## Economic calendar impact

**Today's calendar: Heavy.** Recommendation: stay flat until the event clears, then use wider strikes.

- **Fed Interest Rate Decision** (US, 18:00 UTC / 2:00 PM ET): High impact. Fed events often widen index ranges; avoid initiating tight premium before the event.
- **FOMC Economic Projections** (US, 18:00 UTC / 2:00 PM ET): High impact. Dots/projections can move rates, megacap duration, and index breadth.
- **Fed Press Conference** (US, 18:30 UTC / 2:30 PM ET): High impact. Powell Q&A can create the second volatility impulse; wait for compression before selling premium.
- **17-Week Bill Auction** (US, 2026-06-17 15:30): Low impact. Usually modest index impact unless it materially changes rates or growth expectations.
- **EIA Distillate Fuel Production Change (Jun/12)** (US, 2026-06-17 14:30): Low impact. Usually modest index impact unless it materially changes rates or growth expectations.
- **EIA Weekly Refinery Utilization Rates WoW** (US, 2026-06-17 14:30): Low impact. Usually modest index impact unless it materially changes rates or growth expectations.

## Earnings exposure

**Market-moving potential:** Low from today's FMP earnings calendar; watch single-name moves but broad index impact appears limited.

- No index-heavy earnings identified in today's FMP calendar.

## Globex range and expected range

- **Globex range:** From broker/futures platform. FMP does not provide reliable ES overnight high/low in this workflow.
- **Prior day SPY range proxy:** 5.56 SPY pts, equivalent to roughly 55.98 SPX pts.
- **VIX-implied 1-day expected move:** +/-77.93 SPX pts (~+/-1.04%).

## Opening gap strategy

- **Strategy:** Stay flat into the FOMC decision/press conference; only sell premium after the post-event impulse starts compressing.
- **Gap tactic:** Uncertain until event risk clears. If price accepts beyond Resistance 1 or below Support 1, do not fade mechanically; wait for failed breakout confirmation.

## IV crush opportunity

- **Assessment:** No pre-event IV-crush sale. Wait for the data/event impulse; sell only post-event when realized volatility starts compressing.
- **Best expression:** Defined-risk iron condor or one-sided credit spread after opening-range compression; avoid naked short premium.

## Previous day's close analysis

- **SPY prior session (2026-06-16) OHLC:** O 754.55 / H 755.44 / L 749.88 / C 750.33.
- **Close location:** 8.09% of prior day range.
- **Lean:** Bullish-to-neutral. A low close can set up an early reflexive bounce if sellers fail to press.

## Support and resistance

### Support
- **Support 1: 7,500.00** - Nearest round-number support below current pre-market level.
- **Support 2: 7,475.00** - Next downside round-number shelf if the opening gap extends.
- **Support 3: 7,433.40** - VIX-implied one-day expected-move lower bound.

### Resistance
- **Resistance 1: 7,525.00** - Nearest round-number resistance above current pre-market level.
- **Resistance 2: 7,549.80** - Prior day low; reclaim level after the gap down.
- **Resistance 3: 7,554.30** - Prior close pivot if price opens below and reclaims.

## Pre-market trade plan

- **Strategy:** No 0DTE trade before the event; after the event, consider a defined-risk weekly iron condor only if VIX remains bid and the opening range stabilizes.
- **Expiration:** Weekly Friday expiration after event risk clears.
- **Strikes:** Short put **7400**, long put **7375**; short call **7625**, long call **7650**. These are expected-move/round-number strikes because no live option chain was fetched; confirm delta near 0.10-0.15 on broker.
- **Entry time:** After the FOMC decision and press-conference impulse, ideally 2:45-3:05 PM ET only if the range compresses; otherwise no trade.
- **Position size:** 0.5x normal size / <=1-2% account risk because event volatility can gap through expected move.
- **Invalidation:** No entry if SPX is trending outside the expected-move envelope or VIX is accelerating higher after entry window.

## Scenario playbook

- **Bull outcome:** SPX above Resistance 1 (7,525.00). Close or roll the call spread if price accepts above the level; keep put side only if VIX is falling and breadth remains constructive.
- **Bear outcome:** SPX below Support 1 (7,500.00). Close or roll the put spread; consider taking call-side profits but do not add new short puts into downside momentum.
- **Neutral outcome:** SPX holds between 7,500 and 7,525 after the FOMC impulse. Hold to 50% max profit or close before late-day gamma acceleration; no adjustment if price remains inside the compressed range.

## Data and disclaimer

- **Data sources:** FMP quote (^GSPC, SPY, ^VIX), FMP historical-price-full (SPY and ^VIX), FMP economic_calendar, FMP earning_calendar. Globex/overnight high-low requires broker/futures platform data; no user futures input was supplied.
- **Disclaimer:** For educational and research purposes only; not investment advice. Options involve risk and can result in substantial losses. Confirm all prices, deltas, liquidity, and event times on your trading platform before placing any order.
