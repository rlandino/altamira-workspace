# Jane Street Pre-Market Edge - 2026-06-02

## Market assessment

SPX is indicated near **7,599.96** using FMP cash/ETF data as the pre-market proxy; no SPX/ES futures level was supplied, so use broker SPX/ES for the exact overnight mark. The inferred gap versus the prior SPY-implied SPX close is **+0.0 points (+0.00%)**. **Gap view: Uncertain** - scheduled macro can re-price the open, so avoid declaring a fade/hold until the event reaction is visible.

VIX is **16.14** versus prior close **16.05** (+0.56%). Options pricing is broadly in line with yesterday; normal theta structures are acceptable after the open settles. Prior session SPY closed in the middle of the range; that gives a **neutral two-sided trade; wait for the first 15 minutes to define direction** read for the open.

Today's headline risk is **4-Week Bill Auction, Economic Optimism Index (Jun), JOLTs Job Quits (Apr)** and earnings exposure is **material if any listed mega-cap guides broadly**. The base case is to wait for opening liquidity, then sell defined-risk theta only if price holds inside the expected range and market breadth is not one-way.

## Overnight futures movement

- **Current proxy level:** SPX 7,599.96 (FMP ^GSPC/SPY proxy; exact ES from broker).
- **Prior session close proxy:** SPX 7,599.96 (SPY close 758.54 x SPX/SPY factor 10.019).
- **Gap:** +0.0 points (+0.00%).
- **View:** **Uncertain** - scheduled macro can re-price the open, so avoid declaring a fade/hold until the event reaction is visible.

## Pre-market IV levels

- **Current VIX:** 16.14.
- **Yesterday VIX close:** 16.05.
- **VIX change:** +0.09 points (+0.56%) if available.
- **Recent VIX context:** 5-day average 16.08, 20-day average 17.22.
- **Implication:** options pricing is broadly in line with yesterday; normal theta structures are acceptable after the open settles.

## Economic calendar impact

- **8:30 PM ET** - API Crude Oil Stock Change (May/29) (Medium): Normal impact unless surprise deviates materially.
- **3:30 PM ET** - 4-Week Bill Auction (Low): High-impact: can expand intraday range 1.5-2.0x normal.
- **2:10 PM ET** - Economic Optimism Index (Jun) (Low): High-impact: can expand intraday range 1.5-2.0x normal.
- **2:00 PM ET** - JOLTs Job Quits (Apr) (Low): High-impact: can expand intraday range 1.5-2.0x normal.
- **2:00 PM ET** - JOLTs Job Openings (Apr) (High): High-impact: can expand intraday range 1.5-2.0x normal.
- **12:55 PM ET** - Redbook YoY (May/30) (Low): Normal impact unless surprise deviates materially.
- **12:30 PM ET** - Fed Hammack Speech (Medium): High-impact: can expand intraday range 1.5-2.0x normal.
- **10:00 AM ET** - LMI Logistics Managers Index (May) (Low): Normal impact unless surprise deviates materially.
- **5:50 AM ET** - Fed Kashkari Speech (Medium): High-impact: can expand intraday range 1.5-2.0x normal.

- **Calendar tone:** Heavy.
- **Recommendation:** trade smaller and/or wait until the event window clears; widen strikes beyond the VIX expected move.

## Earnings exposure

- **PANW** - Palo Alto Networks, Inc. (amc, $205B market cap)

- **Market-moving potential:** Medium to high if mega-cap guidance hits index futures.
- **Theta implication:** single-name IV may be elevated in reporters, but index theta should be driven more by macro, breadth, and VIX.

## Globex range and expected range

- **Globex high/low:** From broker/futures platform; FMP does not provide ES overnight high/low here.
- **Prior-day range proxy:** SPX 7,561.39 to 7,617.39 (56.01 points), derived from SPY.
- **VIX-based 1-day expected move:** +/- **77.27 points** (~+/- 1.02%).
- **Expected range around current proxy:** 7,522.69 to 7,677.23.

## Opening gap strategy

- **If price holds above the opening range high:** do not fade; wait for a pullback toward VWAP before selling put spreads.
- **If price fails VWAP/opening range after the gap:** fade bias is valid; sell call-side defined risk or wait for a balanced iron condor entry.
- **If no clean direction by 9:50 AM ET:** normal theta setup is acceptable only outside the expected range, with tight risk controls.

## IV crush opportunity

VIX is low-to-normal; theta exists but wings may be underpaid, so avoid forcing a tight condor. Yesterday was not identified as a specific high-IV macro event from the available FMP calendar, so treat IV crush as an intraday/opening-liquidity opportunity rather than a guaranteed event-vol unwind.

## Previous day's close analysis

- **Prior session (2026-06-01) SPY OHLC:** open 755.36, high 760.28, low 754.69, close 758.54.
- **Close location:** 69% of the daily range; market closed in the middle of the range.
- **Lean:** neutral two-sided trade; wait for the first 15 minutes to define direction.

## Support and resistance

### Support
- **Support 1: 7,599.96** - prior close / pivot.
- **Support 2: 7,561.39** - prior day low.
- **Support 3: 7,522.69** - VIX 1-day expected move down.

### Resistance
- **Resistance 1: 7,600.00** - nearby 25-point round-number magnet.
- **Resistance 2: 7,617.39** - prior day high.
- **Resistance 3: 7,677.23** - VIX 1-day expected move up.

## Pre-market trade plan

- **Strategy:** No opening 0DTE trade until the macro print/reaction clears; then consider a defined-risk SPX iron condor.
- **Expiration:** today (0DTE SPX) if liquidity is clean; otherwise use the nearest weekly expiry with reduced size.
- **Candidate strikes:** sell **7500P / buy 7475P** and sell **7700C / buy 7725C**. These are expected-move approximations; verify live chain deltas near 0.10-0.15 before entry.
- **Entry time:** After the event reaction and opening range settle, typically 9:50-10:15 AM ET.
- **Position size:** 0.5x-0.75x normal risk; max 1-2% of account at risk.
- **Abort conditions:** one-way trend day, VIX expanding after the open, spreads too wide, or price already pressing the expected-move boundary.

## Scenario playbook

- **Bull outcome:** SPX holds above Resistance 1 (7,600.00). Avoid adding call risk; close/roll call side if breached with momentum, and let put side decay only while breadth remains supportive.
- **Bear outcome:** SPX loses Support 1 (7,599.96). Avoid adding put risk; close/roll put side if breached, and harvest call side at 50-75% max profit.
- **Neutral outcome:** SPX stays between Support 1 and Resistance 1. Hold the condor/spreads to 50% max profit, then flatten; do not carry avoidable gamma into the final hour.

## Data and disclaimer

- **Data sources:** FMP quote (^GSPC, SPY, ^VIX), FMP historical-price-full (SPY and ^VIX), FMP economic_calendar, FMP earning_calendar. Globex/overnight futures high-low should be confirmed from a broker/futures platform.
- **Disclaimer:** For educational and research purposes only; not investment advice. Options involve risk and may not be suitable for all investors. Confirm live prices, option-chain deltas, liquidity, and account risk before trading.
