# Jane Street Pre-Market Edge - 2026-04-22

## Market assessment

S&P 500 proxy pricing is **7,064.01**, with an overnight implied gap of **-45.13 points (-0.63%)** versus prior close 7,109.14. Current read is **Fade** for the opening impulse because Gap magnitude is significant (>0.5%), and these opens often mean-revert in the first 60-90 minutes unless macro catalysts immediately reinforce direction.

Implied volatility is **lower vs yesterday**: VIX **19.14** vs prior close **19.50** (-0.36, -1.85%). That supports selective premium selling, but early-session realized volatility still needs confirmation in the first 15 minutes.

Macro/event risk looks **moderate** for U.S. releases, while earnings risk is **high** due to several large-cap reports. Net: keep opening size disciplined, then scale only after direction and volatility regime are confirmed.

## Overnight futures movement

- **Gap:** -45.13 points (-0.63%).
- **View:** **Fade** - Gap magnitude is significant (>0.5%), and these opens often mean-revert in the first 60-90 minutes unless macro catalysts immediately reinforce direction.
- **Note:** ES/Globex highs and lows should be taken from broker futures feed for exact overnight structure.

## Pre-market IV levels

- **VIX now:** 19.14
- **VIX prior close:** 19.50
- **Change:** -0.36 (-1.85%)
- **Read:** Options are pricing **lower** volatility vs yesterday; theta selling is viable but do not oversize into the opening auction.

## Economic calendar impact

- **11:00 ET - MBA 30-Year Mortgage Rate (Apr/17)** (Medium): can expand intraday range ~1.2x on release.
- **11:00 ET - MBA Mortgage Refinance Index (Apr/17)** (Low): usually modest index impact.
- **11:00 ET - MBA Mortgage Market Index (Apr/17)** (Low): usually modest index impact.
- **11:00 ET - MBA Mortgage Applications (Apr/17)** (Low): usually modest index impact.
- **14:30 ET - EIA Gasoline Stocks Change (Apr/17)** (Medium): can expand intraday range ~1.2x on release.
- **14:30 ET - EIA Refinery Crude Runs Change (Apr/17)** (Low): usually modest index impact.
- **Calendar load:** Moderate. **Recommendation:** normal pre-open plan is acceptable, but keep wider strike distance and avoid entries right before medium-impact prints.

## Earnings exposure

Major names reporting today (market-cap weighted):
- **TSLA** (AMC) - Tesla, Inc., mkt cap ~$1450B
- **LRCX** (AMC) - Lam Research Corporation, mkt cap ~$323B
- **GEV** (BMO) - GE Vernova Inc., mkt cap ~$267B
- **IBM** (AMC) - International Business Machines Corporation, mkt cap ~$240B
- **PM** (BMO) - Philip Morris International Inc., mkt cap ~$239B
- **TXN** (AMC) - Texas Instruments Incorporated, mkt cap ~$212B
- **Market-moving potential:** High. Single-name IV spikes likely; index impact is limited unless multiple mega/large-cap reports surprise in same direction.

## Globex range and expected range

- **Globex range:** Pull exact ES overnight high/low from broker platform (not fully provided by FMP cash-index endpoints).
- **Prior-day proxy range (SPY):** 8.64 points (High 711.28 / Low 702.64).
- **VIX-based expected 1-day SPX move:** ±85.2 points (±1.21%).

## Opening gap strategy

- **Primary plan:** Fade the opening gap only after price fails to continue in first 10-15 minutes.
- **Execution note:** Avoid immediate open fill chasing; wait for opening range break/failure confirmation.

## IV crush opportunity

- No clear overnight event-IV hangover in index vol; treat today as standard intraday theta decay rather than a classic post-event IV crush setup.

## Previous day's close analysis

- Prior SPY session O/H/L/C: **710.28 / 711.28 / 702.64 / 704.08**
- Close location: **near lows** of range (16.7% from session low).
- Lean: **Cautious-to-bullish mean-reversion lean if sellers fail to press lower**

## Support and resistance

### Support
- **S1: 7026** - Prior day SPY low translated to SPX-equivalent zone.
- **S2: 6980** - One expected-move lower bound from current level.
- **S3: 6960** - Extension support below expected move (stress-test level).
### Resistance
- **R1: 7110** - Prior close / first mean-reversion magnet.
- **R2: 7113** - Prior day SPY high translated to SPX-equivalent zone.
- **R3: 7150** - One expected-move upper bound from current level.

## Pre-market trade plan

- **Strategy:** 0DTE iron condor (defined-risk), entered after open stabilization
- **Strikes:** Short 6995P / Long 6975P and Short 7145C / Long 7165C (20-point wings; ~0.10-0.15 delta proxy)
- **Expiration:** 0DTE (today)
- **Entry window:** 9:40-10:00 AM ET after first 10-15 minute range forms
- **Position size:** 1.0x normal size max; keep risk to 1.5-2.5% of account

## Scenario playbook

- **Bull outcome (above R1 7110):** Reduce or close call-side risk early; keep put-side premium working toward 50% max profit target.
- **Bear outcome (below S1 7026):** Cut or roll put-side risk quickly; consider taking profits on call side to reduce net risk.
- **Neutral outcome (inside S1-R1):** Hold structure for theta decay and close at ~50% of max profit or by end-of-day risk cutoff.

## Data and disclaimer

- **Data sources:** FMP `quote` (^GSPC, SPY, ^VIX), `historical-price-full` (SPY and ^VIX), `economic_calendar`, and `earning_calendar`.
- **Overnight/Globex note:** Exact ES overnight high/low should be confirmed from broker/futures platform.
- **Disclaimer:** This report is for educational and research purposes only and is not investment advice.