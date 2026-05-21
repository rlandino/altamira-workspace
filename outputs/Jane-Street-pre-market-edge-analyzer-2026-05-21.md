# Jane Street Pre-Market Edge - 2026-05-21

## Market assessment

SPX/ES proxy is 7,432.97 from FMP ^GSPC quote, versus prior SPX close 7,432.97. Gap: 0.0 points (+0.00%). View: **Hold/normal open** - the gap is small; first-hour direction matters more than the overnight mark.

VIX is 17.63 versus yesterday's close 17.44 (+1.09%). Options pricing is **roughly flat vs yesterday**; implication: normal 0DTE premium harvesting can work if price stays inside the expected range.

Prior session closed near the highs of the range, giving a **Bullish** opening lean because buyers controlled the close, but a gap up can be vulnerable to early profit-taking. Today's calendar is **Heavy**. Trade smaller, wait for event digestion, and place strikes outside the VIX expected move.

## Overnight futures movement

- Current SPX/ES proxy: 7,432.97 (FMP ^GSPC quote).
- Prior SPX close: 7,432.97.
- Gap: 0.0 points (+0.00%).
- Hold/fade view: **Hold/normal open** - the gap is small; first-hour direction matters more than the overnight mark.
- Note: SPX/ES from broker for exact futures and true Globex high/low.

## Pre-market IV levels

- VIX now: 17.63.
- Prior VIX close: 17.44.
- Change: 0.19 points (+1.09%).
- 5-day VIX average: 17.80; 20-day average: 17.86.
- Read: Options pricing is **roughly flat vs yesterday**. normal 0DTE premium harvesting can work if price stays inside the expected range.

## Economic calendar impact

- Calendar weight: **Heavy**.
- Recommendation: Trade smaller, wait for event digestion, and place strikes outside the VIX expected move.
- 08:30 ET - Housing Starts MoM (Apr): Moderate/High. Often widens intraday range; use wider strikes and wait for first reaction.
- 08:30 ET - Building Permits MoM (Apr): Low/Moderate. Usually secondary for index vol unless the print surprises.
- 08:30 ET - Building Permits (Apr): Low/Moderate. Usually secondary for index vol unless the print surprises.
- 08:30 ET - Philly Fed Prices Paid (May): High. Can expand SPX range to roughly 1.5-2.0x normal; avoid selling premium immediately ahead of release.
- 08:30 ET - Continuing Jobless Claims (May/09): Moderate/High. Often widens intraday range; use wider strikes and wait for first reaction.
- 08:30 ET - Philly Fed New Orders (May): High. Can expand SPX range to roughly 1.5-2.0x normal; avoid selling premium immediately ahead of release.
- 08:30 ET - Philly Fed Employment (May): High. Can expand SPX range to roughly 1.5-2.0x normal; avoid selling premium immediately ahead of release.
- 08:30 ET - Philly Fed CAPEX Index (May): High. Can expand SPX range to roughly 1.5-2.0x normal; avoid selling premium immediately ahead of release.
- 08:30 ET - Philly Fed Business Conditions (May): High. Can expand SPX range to roughly 1.5-2.0x normal; avoid selling premium immediately ahead of release.
- 08:30 ET - Philadelphia Fed Manufacturing Index (May): High. Can expand SPX range to roughly 1.5-2.0x normal; avoid selling premium immediately ahead of release.
- 08:30 ET - Housing Starts (Apr): Moderate/High. Often widens intraday range; use wider strikes and wait for first reaction.
- 08:30 ET - Jobless Claims 4-Week Average (May/16): Moderate/High. Often widens intraday range; use wider strikes and wait for first reaction.

## Earnings exposure

- Market-moving potential: Medium based on FMP earnings calendar and US index-heavy filter.
- WMT (Walmart) - BMO. Market-moving potential: Medium; large-cap consumer read-through, but not typically a full-index volatility driver by itself.

## Globex range and expected range

- Globex range: From broker/futures platform. FMP does not provide true ES overnight high/low in this command path.
- Prior day SPX range proxy: 78.2 points (high 7,435.69, low 7,357.46).
- Prior day SPY range: 7.98 points (high 741.87, low 733.89).
- VIX-based 1-day expected move: +/- 82.5 SPX points (~+/-1.11%). Formula: price x VIX / sqrt(252).

## Opening gap strategy

- Strategy: Normal theta setup after first 15-minute balance.
- Execution: Wait for the first opening range; avoid selling directly into a fast one-way tape.
- If price accepts above resistance 1, do not sell the call side aggressively; switch to put-side credit only.
- If price rejects the gap and loses support 1, avoid put-side credit until momentum stalls.

## IV crush opportunity

- Assessment: No obvious scheduled IV-crush setup from yesterday's event calendar in available data.
- Theta implication: normal 0DTE premium harvesting can work if price stays inside the expected range.

## Previous day's close analysis

- Prior session open/high/low/close: 7,369.19 / 7,435.69 / 7,357.46 / 7,432.97.
- Close location: Market closed **near the highs**.
- Lean: **Bullish** - buyers controlled the close, but a gap up can be vulnerable to early profit-taking.

## Support and resistance

### Support
- Support 1: 7,425 - Nearest downside round/strike magnet.
- Support 2: 7,357 - Prior day low.
- Support 3: 7,350 - VIX-implied expected move lower bound.

### Resistance
- Resistance 1: 7,436 - Prior day high.
- Resistance 2: 7,450 - Nearest upside round/strike magnet.
- Resistance 3: 7,516 - VIX-implied expected move upper bound.

## Pre-market trade plan

- Exact strategy: **No trade until macro event clears; then 0DTE iron condor only if price holds inside the opening range**.
- Expiration: 0DTE SPX today (2026-05-21); use SPY equivalent only if SPX liquidity/access is unavailable.
- Approximate strikes (expected-move based; confirm live deltas/credits):
  - Short put: 7,300
  - Long put: 7,290
  - Short call: 7,550
  - Long call: 7,560
- Strike logic: short strikes are placed outside ~1.35x the VIX-implied 1-day expected move, rounded to 25-point SPX strike increments. Target 0.10-0.15 delta if the live chain agrees.
- Entry time: After the listed macro catalyst and after the first 10-15 minute reaction stabilizes.
- Position size: 0.5x normal size / <=1% of account at risk due to event density.
- Risk controls: Take profits at 50% of max credit; stop if the short strike is tested or loss reaches ~2x credit; close remaining risk before the final hour if gamma expands.

## Scenario playbook

- Bull outcome: SPX accepts above Resistance 1 (7,436). Action: close or avoid call-side exposure; keep/roll put side only after a higher low forms.
- Bear outcome: SPX breaks below Support 1 (7,425). Action: close or avoid put-side exposure; harvest call side if momentum is clean and VIX is not spiking.
- Neutral outcome: SPX stays between Support 1 and Resistance 1. Action: hold the iron condor to 50% max profit or time stop; no adjustment unless price leaves the expected range.

## Data and disclaimer

- Data sources: FMP quote (^GSPC, SPY, ^VIX), FMP historical-price-full (SPY, ^GSPC, ^VIX), FMP economic_calendar, FMP earning_calendar.
- Globex/overnight note: true ES high/low should be confirmed from broker or futures platform; this report uses FMP cash/ETF proxies where futures data is unavailable.
- Options note: strikes are estimated from expected move, not live option-chain deltas. Confirm bid/ask, delta, and liquidity before any trade.
- Disclaimer: For educational and research purposes only. Not investment advice or a recommendation to buy or sell securities, options, futures, or derivatives.

## Telegram summary

```text
Jane Street Pre-Market Edge - 2026-05-21
Gap: 0.0 pts (+0.00%) | View: Hold/normal open
VIX: 17.63 (+1.09% vs yesterday)
Main risk: Heavy 08:30 ET macro calendar; WMT is the main US index-relevant earnings name flagged
Plan: No trade until macro event clears; then 0DTE iron condor only if price holds inside the opening range; SPX approx 7,300/7,290 put spread and 7,550/7,560 call spread, After the listed macro catalyst and after the first 10-15 minute reaction stabilizes
S/R: Supports 7,425, 7,357, 7,350; Resistances 7,436, 7,450, 7,516
Report: outputs/Jane-Street-pre-market-edge-analyzer-2026-05-21.md
```
