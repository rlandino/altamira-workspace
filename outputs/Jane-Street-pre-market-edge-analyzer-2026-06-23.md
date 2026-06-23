# Jane Street Pre-Market Edge - 2026-06-23

## Market assessment

Current SPX proxy is **7,472.79** versus prior close **7,472.78**, a gap of **+0.01 points (+0.00%)**. View: **Small gap; normal opening-range process** - The gap is inside noise relative to the VIX-implied daily move.

VIX 19.53 is higher vs prior close 17.28 (+13.02%). One-day VIX-implied move is about **+/-91.94 points** (~+/-1.23%). Prior session closed **near the lows**, giving a **Bullish mean-reversion lean** read for the open.

Calendar load is **Heavy** and earnings exposure is **Medium to High if reports cluster in index-heavy sectors.** The trading bias is to use defined-risk theta only after the opening range and any scheduled event risk are visible.

## Overnight futures movement

- Current level: **7,472.79** (FMP ^GSPC quote proxy; use SPX/ES from broker for exact futures.)
- Prior SPX close (2026-06-22): **7,472.78**
- Gap: **+0.01 points (+0.00%)**
- View: **Small gap; normal opening-range process** - The gap is inside noise relative to the VIX-implied daily move.

## Pre-market IV levels

- VIX 19.53 is higher vs prior close 17.28 (+13.02%).
- 5-day VIX average: **16.95**; 20-day VIX average: **17.44**.
- Volatility regime: **normal**. Implication: premium selling needs clean entries because raw IV is not especially fat.

## Economic calendar impact

Today's calendar: **Heavy**. Recommendation: **Trade after the key release or use wider-than-normal 0DTE wings; avoid tight short strikes into event risk.**

- **4:30 PM ET** - API Crude Oil Stock Change (Jun/19) (prev -8.33). After-close energy/rates context; limited direct index impact unless crude volatility spills into inflation expectations.
- **1:00 PM ET** - M2 Money Supply MoM (May) (prev 22.8). Routine: usually limited index impact unless the surprise is large.
- **1:00 PM ET** - Money Supply (May) (prev 22.8). Routine: usually limited index impact unless the surprise is large.
- **1:00 PM ET** - 2-Year Note Auction (prev 4.071). Rates-sensitive: watch yields; index vol can lift if the auction tails or front-end yields spike.
- **10:00 AM ET** - Richmond Fed Manufacturing Shipments Index (Jun) (prev 16). Regional survey: lower impact than ISM/PMI, but can add range if it confirms a growth surprise.
- **10:00 AM ET** - Richmond Fed Services Index (Jun) (prev 14). Regional survey: lower impact than ISM/PMI, but can add range if it confirms a growth surprise.
- **10:00 AM ET** - Richmond Fed Manufacturing Index (Jun) (prev 13). Regional survey: lower impact than ISM/PMI, but can add range if it confirms a growth surprise.
- **9:45 AM ET** - S&P Global Manufacturing PMI (Jun) (prev 55.1). Medium/high: can expand the first-hour range 1.2-1.5x if the print surprises.
- **9:45 AM ET** - S&P Global Composite PMI (Jun) (prev 51.5). Medium/high: can expand the first-hour range 1.2-1.5x if the print surprises.
- **9:45 AM ET** - S&P Global Services PMI (Jun) (prev 50.7). Medium/high: can expand the first-hour range 1.2-1.5x if the print surprises.
- **8:55 AM ET** - Redbook YoY (Jun/20) (prev 9.4). Routine: usually limited index impact unless the surprise is large.

## Earnings exposure

- Market-moving potential: **Medium to High if reports cluster in index-heavy sectors.**
- **FDX** ($78B market cap), reports AMC. Market-moving potential: Medium; single-name transport read-through, not normally a mega-cap index driver.

## Globex range and expected range

- Globex range: **From broker/futures platform**; FMP does not provide reliable ES overnight high/low here.
- Prior day SPX range proxy: **70.00 points** (high **7,530.01**, low **7,460.01**).
- VIX-implied 1-day range: **+/-91.94 points** (~+/-1.23%).
- Expected range around current proxy: **7,380.85 to 7,564.73**.

## Opening gap strategy

- Strategy: **Stay flat until the first post-event/opening range if high-impact data is pending or fresh.**
- Execution note: If the gap extends with breadth and VIX flat/down, avoid fading mechanically. If price fails at Resistance 1 or reclaims Support 1 after an early flush, use that failed move to enter the opposite-side credit spread first.

## IV crush opportunity

- **Not yet - IV is bid vs yesterday; sell premium only after the catalyst/range stabilizes.**
- Best expression: defined-risk SPX premium, entered after the open confirms realized volatility is not outrunning implied volatility.

## Previous day's close analysis

- Prior session OHLC: open **7,500.44**, high **7,530.01**, low **7,460.01**, close **7,472.78**.
- Close location: **near the lows** (18% of range from low to high).
- Read: **Bullish mean-reversion lean** - use as a pre-open lean only; opening breadth and VIX confirmation override it.

## Support and resistance

### Support
- **Support 1: 7,472.78** - Prior close / pivot.
- **Support 2: 7,460.01** - Prior day low.
- **Support 3: 7,450.00** - Round-number support.

### Resistance
- **Resistance 1: 7,500.00** - Round-number resistance.
- **Resistance 2: 7,530.01** - Prior day high.
- **Resistance 3: 7,564.73** - VIX-implied one-day upper bound.

## Pre-market trade plan

- Strategy: **Defined-risk 0DTE iron condor only after event risk clears; otherwise no trade.**
- Expiration: **Today / 0DTE SPX**.
- Strike framework: short strikes placed about **1.50x** the VIX-implied one-day move from the current proxy, then rounded to 5-point SPX strikes. Confirm live deltas; target **0.10-0.15 delta**.
- Short put / long put: **7,330 / 7,320**
- Short call / long call: **7,615 / 7,625**
- Entry time: **After the key event passes; otherwise use half size before the catalyst.**
- Position size: **0.5x normal size; cap risk at ~1% of account due to calendar density.**
- Risk management: stop if the short strike is breached with rising VIX, or if mark-to-market loss reaches ~2x credit. Take profits at 50% of max credit before midday if available.

## Scenario playbook

- **Bull outcome:** SPX holds above Resistance 1 (**7,500.00**) with VIX flat/down. Avoid adding call risk; close or roll the call side if delta expands, and let the put side decay toward 50% max profit.
- **Bear outcome:** SPX loses Support 1 (**7,472.78**) with VIX bid. Close/roll the put side; harvest the call side first and consider re-selling calls only after a failed bounce.
- **Neutral outcome:** SPX stays inside Support 1 / Resistance 1 and VIX trends lower. Hold the iron condor to 50% max profit or close before late-day gamma accelerates.

## Data and disclaimer

- Data sources: FMP quote (^GSPC, SPY, ^VIX), FMP historical-price-full (SPY, ^GSPC, ^VIX), FMP economic_calendar, FMP earning_calendar, and FMP quote enrichment for earnings market caps.
- Futures/Globex note: no SPX/ES futures level was supplied; exact overnight high/low and ES fair value should be checked on the broker/futures platform before execution.
- Disclaimer: For educational and research purposes only. This is not investment advice, a recommendation, or a solicitation to buy or sell securities or options. Options involve risk and can expire worthless.
