# Jane Street Pre-Market Edge — 2026-04-03

## Market assessment

Pre-market proxy is essentially flat-to-slightly positive: S&P 500 spot proxy is 6,582.69 vs 6,575.32 prior close (+7.37, +0.11%). Without a live ES tape in this environment, the opening setup is best treated as a small gap, not a true trend break.

Implied volatility is still elevated in absolute terms (VIX 23.87), but it is lower than yesterday's close (24.54), indicating some overnight vol compression. That supports theta, but with event risk directly ahead, execution timing matters more than raw IV level.

The calendar is heavy for the open with U.S. labor-market prints at 8:30 AM ET (NFP, private payrolls, unemployment), which can expand the first-hour range materially. Earnings are not a dominant index driver today, so macro data is the primary risk.

## Overnight futures movement

- **Current level used (proxy):** S&P 500 6,582.69 (FMP quote proxy; exact ES/Globex from broker).
- **Prior close reference:** 6,575.32.
- **Gap:** **+7.37 points (+0.11%)**.
- **View:** **Uncertain to slight hold**, with a fade bias if first impulse overextends after 8:30 ET data. Small gap alone is not enough for a directional chase.

## Pre-market IV levels

- **Current VIX:** 23.87.
- **Yesterday VIX close:** 24.54.
- **Change:** -0.67 (-2.73%).
- **Read:** Options are pricing **slightly less** volatility than yesterday's close, but IV is still elevated vs low-vol regimes (<15). Premium selling is favorable **after** event volatility reprices.

## Economic calendar impact

**Today's key U.S. events (ET):**

- **8:30 AM (High):** Non-Farm Payrolls (Mar)
- **8:30 AM (High):** Nonfarm Payrolls Private (Mar)
- **8:30 AM (High):** Unemployment Rate (Mar)
- **8:30 AM (High):** U-6 Unemployment Rate (Mar)
- **8:30 AM (Medium):** Average Hourly Earnings (MoM/YoY), Participation Rate
- **3:30 PM (Medium):** CFTC S&P 500 speculative positioning

**Historical range implication:**

- Payroll days frequently produce **1.5x to 2.0x** of a typical first-hour move.
- Directional conviction before data is low edge; post-release mean reversion often appears after the first impulse.

**Recommendation:** **Trade after event reaction**, use wider defined-risk strikes, and size below normal if entering before 10:00 AM ET.

## Earnings exposure

- Earnings calendar shows no major U.S. mega-cap concentration for today's session.
- Largest names on today's feed are not heavy S&P index movers.
- **Market-moving potential:** **Low-to-Medium** (single-name IV risk present, broad-index earnings risk limited).

## Globex range and expected range

- **Globex overnight range:** Not available from FMP. Use broker futures platform for true ES high/low.
- **Proxy range (yesterday cash session):** ~131 points (derived from prior SPY range scaled to index level).

**VIX-based expected 1-day move:**

- Formula: Price x (VIX / 100) / 16
- 6,582.69 x (23.87 / 100) / 16 = **~98 points**
- **Expected range:** **6,485 to 6,681** (~+/-1.49%)

## Opening gap strategy

- With a small pre-market gap and high-impact 8:30 ET macro data:
  - **Primary plan:** Wait for first directional flush/chase to settle.
  - **Execution window:** 9:40-9:55 AM ET preferred (post-open price discovery).
  - **Bias:** Sell premium only if price action stabilizes inside expected-move structure.

## IV crush opportunity

- **Yes, conditional.** This is a macro-event morning (labor data), so post-release IV can compress after the initial spike.
- Best setup is short premium entered **after** early expansion, not before the data print.

## Previous day's close analysis

Using prior SPY session (O/H/L/C: 646.42 / 658.20 / 645.11 / 655.83):

- Close location in range: ~82% from low (near highs).
- Read: market finished strong; that can invite either continuation or morning mean reversion.
- **Lean:** **Slight bearish mean-reversion bias** unless payroll data confirms risk-on continuation.

## Support and resistance

### Support

1. **6,515** — round-number support near opening auction zone.
2. **6,485** — VIX-implied lower expected-move boundary.
3. **6,475** — prior-session low proxy zone.

### Resistance

1. **6,602** — prior-session high / immediate upside pivot.
2. **6,650** — round-number magnet and intraday decision area.
3. **6,681** — VIX-implied upper expected-move boundary.

## Pre-market trade plan

- **Strategy:** SPX **0DTE iron condor** (defined risk), entered only after first 10-20 minutes of cash open.
- **Structure (model-based, confirm live chain deltas):**
  - Short Put: **6460**
  - Long Put: **6435**
  - Short Call: **6710**
  - Long Call: **6735**
- **Delta target:** Approx. 0.10-0.15 on short strikes (confirm in broker chain at entry).
- **Expiration:** **Today (0DTE)**.
- **Entry time:** **9:40-9:55 AM ET** (or delay further if post-NFP volatility remains disorderly).
- **Position size:** **1x reduced size** (about 1-2% account risk) due to macro-event day.

## Scenario playbook

- **Bull outcome (break and hold above 6,602):**
  - Reduce or close call spread risk early.
  - Keep put side if premium decays and structure remains outside trend channel.

- **Bear outcome (break and hold below 6,515):**
  - Reduce/close put spread risk; consider taking call side profits.
  - Do not average down short puts into accelerating downside.

- **Neutral outcome (holds inside ~6,515 to 6,602):**
  - Hold for theta decay.
  - Target 40-50% max credit capture and de-risk before late-day gamma expansion.

## Data and disclaimer

- **Data sources:** FMP quote (^GSPC, SPY, ^VIX), FMP historical-price-full (SPY, ^VIX), FMP economic_calendar, FMP earning_calendar.
- **Overnight/Globex note:** Exact ES overnight high/low should come from broker futures platform.

**Disclaimer:** This material is for educational and research purposes only and is not investment advice. Options involve significant risk, including the risk of loss greater than initial premium for certain strategies.
