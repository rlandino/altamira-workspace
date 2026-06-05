# Jane Street Pre-Market Edge - 2026-06-05

## Market assessment

SPX is indicated around **7,584.31** using FMP quote data (SPX/ES from broker for exact futures). Against the prior SPY-implied SPX close of **7,584.31**, the overnight indication is **0.00 points (+0.00%)**. Gap view: **Hold risk around catalyst** - the gap is flat, but the 8:30 AM ET U.S. payrolls cluster can extend the first move instead of fading.

VIX 15.65 is higher vs prior close 15.40 (+1.62%). Calendar risk is **heavy** today because Non Farm Payrolls, unemployment, participation, and wage data all hit before the cash open, so the theta plan should be **defined-risk**, entered only after the print/opening range settles, and adjusted quickly if price breaks the first support/resistance band.

The prior session (2026-06-04) closed **near the highs** of its range, giving a **Bearish-to-neutral fade risk** read into today. Use broker futures for the true Globex high/low; FMP equity data gives a prior-day SPY range proxy of **6.84 SPY points** (~**68.52 SPX points**).

## Overnight futures movement

- **Current indication:** SPX 7,584.31 / SPY 757.09.
- **Prior close proxy:** SPX 7,584.31 / SPY 757.09.
- **Gap:** 0.00 points (+0.00%), direction **flat**.
- **Hold/fade view:** **Hold risk around catalyst** - small gap, but high-impact calendar risk can extend the move instead of fading.

## Pre-market IV levels

- **Current VIX:** 15.65.
- **Prior VIX close:** 15.40.
- **Change vs prior:** 0.25 points (+1.62%).
- **Implication:** Premium is not especially rich; require clean range confirmation before selling theta.

## Economic calendar impact

- **8:30 AM ET - Non Farm Payrolls (May):** estimate 85K vs prior 115K. NFP often drives a first-hour range expansion; wait for post-print direction before sizing theta.
- **8:30 AM ET - Unemployment Rate (May):** estimate 4.3% vs prior 4.3%. A rate surprise changes the growth/rates read-through and can expand SPX range to ~1.5-2.0x normal.
- **8:30 AM ET - Average Hourly Earnings MoM/YoY (May):** MoM estimate 0.3% vs prior 0.2%; YoY estimate 3.4% vs prior 3.6%. Wage pressure can reprice Fed expectations and keep VIX bid.
- **8:30 AM ET - Participation Rate / U-6 Unemployment / sector payroll detail:** secondary labor details that can confirm or fade the headline payrolls reaction.
- **3:00 PM ET - Consumer Credit Change (Apr):** estimate $18B vs prior $24.86B. Usually limited index impact unless it materially shifts the consumer-credit narrative.
- **After close - CFTC positioning reports:** useful for positioning context, not a cash-open theta catalyst.

- **Calendar weight:** **Heavy**.
- **Recommendation:** Avoid selling premium into the 8:30 AM ET labor-market print; trade only after the data and cash-open range settle, with wider strikes and smaller size.

## Earnings exposure

- FMP returned 73 earnings events, but no obvious mega-cap/index-heavy reports were flagged. Market-moving potential: **Low**; single-name risk remains localized.

## Globex range and expected range

- **Globex range:** From broker/futures platform. FMP does not expose ES overnight high/low; use prior-day SPY range as proxy: **6.84 SPY points** / **68.52 SPX points**.
- **VIX-based 1-day expected move:** **+/-74.77 SPX points** (~+/-0.99%).
- **Expected range reference:** 7,509.54 to 7,659.08.

## Opening gap strategy

- **Strategy:** Stay cautious until the event/opening range resolves; do not sell premium into binary macro risk.
- **Execution rule:** If SPX rejects the opening gap and falls back through the prior close, favor the fade. If SPX holds above the opening range with VIX falling, avoid fighting continuation and move short premium farther OTM.

## IV crush opportunity

- **Read:** No obvious prior high-IV macro event identified from the fetched calendar; theta edge comes from current VIX level, not a scheduled IV-crush setup.
- **Theta implication:** Use defined-risk structures; harvest decay only after first-hour realized volatility is below the VIX-implied pace.

## Previous day's close analysis

- **Prior session (2026-06-04) SPY OHLC:** open 752.10, high 758.31, low 751.47, close 757.09.
- **Close location:** 82.16% of the day range, closed **near the highs**.
- **Lean:** **Bearish-to-neutral fade risk** - late-day strength can invite early profit-taking/fade.

## Support and resistance

### Support
- **Support 1: 7,575** - Nearest 25-point round-number support just below the flat overnight indication.
- **Support 2: 7,528** - Prior session low.
- **Support 3: 7,510** - VIX-implied 1-day downside edge.

### Resistance
- **Resistance 1: 7,597** - Prior session high.
- **Resistance 2: 7,600** - Nearby round-number breakout level.
- **Resistance 3: 7,659** - VIX-implied 1-day upside edge.

## Pre-market trade plan

- **Strategy:** Post-event 0DTE iron condor only after the macro print settles.
- **Expiration:** Today, 0DTE (2026-06-05).
- **Structure:** Sell the **7,505 / 7,495 put spread** and sell the **7,660 / 7,670 call spread** (10-point wings), using expected-move strikes as a proxy for 0.10-0.15 delta. Confirm live option deltas/liquidity before order entry.
- **Entry time:** After the high-impact event and after the 9:35-9:50 AM ET opening range stabilizes.
- **Position size:** 0.5x normal risk / max 1-2% account risk because event gamma can dominate theta.
- **Risk controls:** Target 40-50% max profit; stop/adjust if SPX trades through either short strike or if spread value reaches ~2x entry credit.

## Scenario playbook

- **Bull outcome:** SPX above **Resistance 1 (7,597)** with VIX falling. Close/roll the call side if delta expands; keep the put side only if price remains above VWAP and opening range support.
- **Bear outcome:** SPX below **Support 1 (7,575)** with VIX rising. Close or roll the put side down/out; harvest the call side at 50%+ profit rather than adding short gamma.
- **Neutral outcome:** SPX holds between **7,575** and **7,597**. Hold the iron condor to 40-50% max profit, then flatten; avoid carrying late-day gamma if realized range expands.

## Data and disclaimer

- **Data sources:** FMP quote (`^GSPC`, `SPY`, `^VIX`), FMP historical-price-full (`SPY`, `^VIX`), FMP economic calendar, FMP earnings calendar. Globex/overnight high-low should be verified on broker/futures platform.
- **Data limitations:** FMP may return regular-session prices rather than true 8 AM ES futures; live broker quotes should override the proxy levels before trading.
- **Disclaimer:** Educational/research only; not investment advice. Options involve substantial risk and 0DTE spreads can lose money quickly.
