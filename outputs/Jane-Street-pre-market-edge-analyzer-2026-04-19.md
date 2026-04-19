# Jane Street Pre-Market Edge — 2026-04-19

## Market assessment

SPX proxy is essentially flat versus the prior session close (gap +0.0 pts, +0.00%) using SPY as the pre-market proxy because live ES/Globex levels were not provided. Initial read: opening auction likely sets direction rather than overnight momentum.

Pre-market implied volatility is softer: VIX 17.48 vs prior close 17.94 (-0.46, -2.56%). Lower IV supports theta selling, but premium is less rich than event-driven sessions.

Calendar and earnings headline risk look limited for US index traders today. That favors a rules-based, defined-risk premium sale after the first 10–20 minutes of price discovery.

## Overnight futures movement

- **Proxy method used:** SPY-to-SPX scaling (ES/Globex feed not provided).
- **Gap:** +0.0 SPX pts (+0.00%).
- **View:** **Uncertain / slight Hold bias** — small gap with no major US event usually trades the opening range before choosing direction.

## Pre-market IV levels

- **Current VIX:** 17.48
- **Prior VIX close:** 17.94
- **Change:** -0.46 (-2.56%)
- **Read:** Options are pricing **lower** volatility vs yesterday, which supports theta selling but with less absolute premium.

## Economic calendar impact

- No US economic releases were returned for today by the FMP economic calendar endpoint.

- **Historical impact note:** No classic high-impact US prints (CPI/NFP/FOMC) detected for today; event-driven range expansion risk is lower.
- **Today's calendar:** **Light**
- **Recommendation:** No major US macro prints today; normal theta deployment after open is reasonable.

## Earnings exposure

- **DHBK.QA** (TBD)
- **QEWS.QA** (TBD)

- **Market-moving potential:** **Low**
- **Read:** No mega-cap US names detected in today's feed; broad index earnings shock risk appears limited.

## Globex range and expected range

- **Globex overnight high/low:** Not available from FMP quote endpoints; pull exact ES levels from broker futures ladder.
- **Proxy range (prior SPY day):** 6.63 SPY points (~66.5 SPX points).
- **VIX-implied 1-day expected move (SPX):** ±77.9 points (±1.09%).

## Opening gap strategy

- With a near-flat gap and light US event risk: **wait for first 15 minutes**, then sell defined-risk premium outside the opening range.
- If opening drive extends through Resistance 1 or Support 1 with breadth confirmation, avoid fading immediately and reprice strikes wider.

## IV crush opportunity

- **IV crush setup today:** **Moderate / limited**
- No major macro volatility event from yesterday is evident; IV is already softer this morning, so edge comes from disciplined strike placement rather than pure volatility collapse.

## Previous day's close analysis

- Prior SPY session (used as index proxy): Open 706.14, High 712.39, Low 705.76, Close 710.14.
- Market closed **in the middle-to-upper half** of the range (66.1% up from low).
- Lean for today: **neutral-to-slightly bullish continuation lean** unless opening breadth diverges.

## Support and resistance

### Support
- **S1: 7082** — prior-session SPX-proxy low.
- **S2: 7048** — lower expected-move boundary from prior close.
- **S3: 6950** — round-number extension / secondary downside magnet.

### Resistance
- **R1: 7149** — prior-session SPX-proxy high.
- **R2: 7204** — upper expected-move boundary from prior close.
- **R3: 7250** — round-number extension above expected move.

## Pre-market trade plan

- **Strategy:** SPX **0DTE iron condor** (defined risk).
- **Indicative strikes (no live chain deltas):**
  - Sell **7050 Put**, buy **7030 Put**
  - Sell **7205 Call**, buy **7225 Call**
- **Expiration:** Today (0DTE session).
- **Entry time:** **9:40–10:00 AM ET** after opening range and breadth check.
- **Size:** **1x to 0.75x normal**, targeting **2–3% account risk max** due to weekend-to-open uncertainty.

## Scenario playbook

- **Bull outcome (price > R1 7149):** close or reduce call spread at ~1.8x credit stop; hold put side for decay if structure remains balanced.
- **Bear outcome (price < S1 7082):** close or roll put spread down/out only if implied vol expands and risk budget allows; take profits on call side early.
- **Neutral outcome (inside S1/R1):** target 40–60% max profit intraday; avoid holding full size into final hour gamma unless comfortably outside short strikes.

## Data and disclaimer

- **Data sources:** FMP `/quote/^GSPC,SPY,^VIX`, `/historical-price-full/SPY`, `/historical-price-full/^VIX`, `/economic_calendar`, `/earning_calendar`.
- **Overnight futures/Globex:** Exact ES high/low not provided by FMP quote endpoint; use broker futures platform for precise overnight range.
- **Disclaimer:** For educational and research purposes only. Not investment advice. Options involve substantial risk, including loss greater than initial premium in certain structures.
