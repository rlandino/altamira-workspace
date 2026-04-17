# Jane Street Pre-Market Edge — 2026-04-17

## Market assessment

SPX proxy is 7,041.3 pre-market with an implied open gap of +0.0 points (+0.00%) versus prior close proxy. Current read is **Hold**: small gap often transitions into range extension after opening auction.

Volatility is 17.82 vs 17.94 yesterday close (-0.12, -0.7%). Versus a 20-day VIX average of 25.82 (if available), pre-market IV looks **compressed**, which slightly shifts the edge between aggressive premium selling and waiting for better post-open prices.

Prior session closed in the middle of range (neutral lean). Calendar is **Heavy** and earnings market-moving potential is **Low**, so opening execution should prioritize event timing and defined risk.

## Overnight futures movement

- **Gap:** +0.0 points (+0.00%)
- **View:** **Hold**
- **Rationale:** small gap often transitions into range extension after opening auction.

## Pre-market IV levels

- **VIX now:** 17.82
- **Vs yesterday close:** 17.94 (-0.12, -0.7%)
- **Vs 20-day average:** 25.82 -> IV regime: **compressed**
- **Theta implication:** Premium is thinner; be selective and avoid overtrading.

## Economic calendar impact

- **Today's calendar intensity:** **Heavy**
- **2026-04-17 18:00:00 ET** — Fed Waller Speech
- **2026-04-17 16:15:00 ET** — Fed Barkin Speech
- **2026-04-17 14:00:00 ET** — CPI YoY (Mar)
- **2026-04-17 12:00:00 ET** — Harmonised Inflation Rate YoY (Mar)
- **2026-04-17 10:00:00 ET** — Unemployment Rate (Mar)
- **2026-04-17 07:00:00 ET** — CPI (Apr)
- **2026-04-17 04:00:00 ET** — CPI MoM (Mar)
- **2026-04-17 04:00:00 ET** — Inflation Rate YoY (Mar)
- **2026-04-17 04:00:00 ET** — GDP Growth Rate YoY (Q1)
- **2026-04-17 04:00:00 ET** — CPI YoY (Mar)
- **Historical impact notes:**
  - Fed Waller Speech: binary event risk; avoid oversized short premium before release
  - Fed Barkin Speech: binary event risk; avoid oversized short premium before release
  - CPI YoY (Mar): often expands SPX intraday range ~1.5x
  - Harmonised Inflation Rate YoY (Mar): often expands SPX intraday range ~1.5x
  - CPI (Apr): often expands SPX intraday range ~1.5x
- **Recommendation:** Trade after key event print; widen strikes and cut size pre-event.

## Earnings exposure

- **Market-moving potential:** **Low**
- No mega-cap index-heavy earnings flagged for today from FMP calendar.
- **Index impact view:** Single-name IV likely elevated; index impact becomes material only if mega-cap guidance surprises.

## Globex range and expected range

- **Globex overnight range:** Use broker/futures platform for true ES high/low (not fully provided by FMP).
- **Prior day SPY range proxy:** 4.25 points (SPY), ~42.6 SPX-proxy points
- **Expected 1-day move (VIX model):** ±79.0 SPX points (~±1.12%)

## Opening gap strategy

- **Primary plan:** Normal theta deployment after opening auction stabilizes.
- **Execution note:** Enter only after bid/ask normalizes and breadth confirms range behavior.

## IV crush opportunity

- **IV crush setup today:** **Yes**
- Yesterday had high-IV macro catalysts; residual premium can decay after the open if no new shock prints.

## Previous day's close analysis

- **OHLC (2026-04-16, SPY):** O 701.06 | H 702.78 | L 698.53 | C 701.66
- **Range position:** Closed **in the middle** (74% up from low)
- **Lean for today:** **neutral lean**

## Support and resistance

- **Support levels (SPX proxy):**
  - **S1 7041** — Prior close / immediate pivot
  - **S2 7010** — Expected move down zone
  - **S3 6962** — Prior day low / stronger demand
- **Resistance levels (SPX proxy):**
  - **R1 7050** — Prior day high / first supply
  - **R2 7053** — Round-number pivot
  - **R3 7120** — Expected move up zone

## Pre-market trade plan

- **Strategy:** 0DTE SPX iron condor (defined risk), skewed slightly away from gap direction
- **Strikes (indicative, expected-move based):** Sell 6975P / Buy 6950P and Sell 7110C / Buy 7135C
- **Expiration:** Today (0DTE)
- **Entry time:** 9:45-10:05 AM ET (after macro print and opening range)
- **Risk size:** 1x normal if calendar light; 0.5x-0.75x if event-heavy (target 1-3% account risk max)
- **Trade management:** Take profits at 40-50% of max credit; hard stop at ~2x collected credit or short-strike breach.

## Scenario playbook

- **Bull outcome (above R1 7050):** Close or hedge call spread at 1.5-2.0x loss threshold; keep put side if safe.
- **Bear outcome (below S1 7041):** Close or roll put spread down/out; optionally harvest call side gains early.
- **Neutral outcome (between S1 7041 and R1 7050):** Hold for theta decay and close around 50% max profit before late-day gamma risk.

## Data and disclaimer

- **Data sources:** FMP `/quote` (^GSPC, SPY, ^VIX), `/historical-price-full/SPY`, `/historical-price-full/^VIX`, `/economic_calendar`, `/earning_calendar`; Globex overnight high/low should be taken from broker/futures platform.
- **Method notes:** SPX proxy levels are estimated from SPY using real-time SPX/SPY scaling where available.
- **Disclaimer:** This briefing is for educational and research purposes only and is not investment advice.
