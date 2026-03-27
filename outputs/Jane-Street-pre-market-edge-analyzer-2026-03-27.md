# Jane Street Pre-Market Edge — 2026-03-27

## Market assessment

US index proxies indicate an overnight gap of +0.0 SPX pts (+0.00%) versus the prior close proxy. Base case is **Uncertain**: High-impact macro releases can overpower normal gap behavior after the open.

Implied volatility read: VIX 29.36 vs yesterday close 27.44 (+1.92, +7.0%). IV is higher vs yesterday; richer premiums favor defined-risk premium selling with wider wings.

Prior session closed **at lows** of its range, giving a **Bullish-to-neutral** lean into today. Calendar risk is **Heavy** and earnings index-impact risk is **High**.

## Overnight futures movement
- Gap: **+0.0 pts (+0.00%)** vs prior SPX proxy close 6477.2.
- View: **Uncertain** — High-impact macro releases can overpower normal gap behavior after the open.
- SPX/ES exact overnight level and true Globex high/low should be confirmed on broker futures feed.

## Pre-market IV levels
- VIX 29.36 vs yesterday close 27.44 (+1.92, +7.0%).
- Implication: IV is higher vs yesterday; richer premiums favor defined-risk premium selling with wider wings.

## Economic calendar impact
- High-impact: 2026-03-27 18:00:00 — Unemployment Rate (Feb)
- High-impact: 2026-03-27 17:00:00 — GDP Growth Rate YoY (Q4)
- High-impact: 2026-03-27 17:00:00 — GDP Growth Rate QoQ (Q4)
- High-impact: 2026-03-27 15:30:00 — Fed Daly Speech
- High-impact: 2026-03-27 15:00:00 — Fed Barkin Speech
- High-impact: 2026-03-27 13:00:00 — GDP Growth Rate YoY (Q4)
- High-impact: 2026-03-27 13:00:00 — GDP Growth Rate QoQ (Q4)
- High-impact: 2026-03-27 12:00:00 — Unemployment Rate (Feb)
- Other: 2026-03-27 20:00:00 — Current Account (Q4)
- Other: 2026-03-27 19:30:00 — CFTC Gold Speculative net positions
- Other: 2026-03-27 19:30:00 — CFTC GBP speculative net positions
- Other: 2026-03-27 19:30:00 — CFTC JPY speculative net positions
- Other: 2026-03-27 19:30:00 — CFTC Wheat speculative net positions
- Calendar load: **Heavy**
- Recommendation: Trade after major releases; widen short strikes and cut size to 0.5-0.75x.

## Earnings exposure
- PTPP.JK (1843B market cap), report time: N/A
- 3968.HK (1235B market cap), report time: N/A
- 600036.SS (995B market cap), report time: N/A
- 002594.SZ (948B market cap), report time: N/A
- 603993.SS (378B market cap), report time: amc
- IDCBF (289B market cap), report time: N/A
- ACGBF (234B market cap), report time: N/A
- 601600.SS (195B market cap), report time: N/A
- Market-moving potential: **High** (single-name IV can spill into index gamma positioning).

## Globex range and expected range
- Globex high/low: **from broker futures platform** (not provided by FMP spot endpoints).
- Prior SPY day range proxy: **10.03 SPY pts** (~100.7 SPX pts).
- VIX-based expected 1-day SPX move: **+/-119.8 pts** (~+/-1.85%).

## Opening gap strategy
- Small/moderate gap: run **normal theta deployment** after first 10-20 minutes.
- If opening drive breaks prior-day extremes with volume, reduce size and keep one side easier to cut.

## IV crush opportunity
- Event-driven IV pressure likely around scheduled releases; post-event decay can be harvested with defined-risk premium selling.
- Preferred expression: defined-risk iron condor, avoid naked structures into event windows.

## Previous day's close analysis
- Prior day OHLC (SPY): O 652.06 / H 654.85 / L 644.82 / C 645.09
- Market closed **at lows** of the range -> **Bullish-to-neutral** lean.
- Read: Closing near lows often sets up mean reversion if no fresh negative catalyst appears.

## Support and resistance
### Support
- S1: **6357** — VIX-implied lower expected move
- S2: **6450** — Nearby round-number support
- S3: **6474** — Prior day low (converted SPX proxy)
### Resistance
- R1: **6500** — Nearby round-number resistance
- R2: **6575** — Prior day high (converted SPX proxy)
- R3: **6597** — VIX-implied upper expected move

## Pre-market trade plan
- Strategy: **0DTE defined-risk iron condor (SPX)**
- Strikes (model-based, no live chain deltas): **6365/6345 put spread + 6585/6605 call spread**
- Target delta zone: short strikes roughly 0.10-0.15 equivalent by expected-move placement.
- Expiration: **Today (0DTE)**
- Entry time: **After the final high-impact morning release reaction is established (typically 9:40-10:05 AM ET).**
- Position size: **0.5x normal size; keep max risk at ~1.5-2.0% of account.**
- Risk control: hard stop at 2x collected credit or short strike breach with momentum confirmation.

## Scenario playbook
- **Bull outcome** (price > R1 6500): close/trim call spread early; keep or trail put spread to capture theta.
- **Bear outcome** (price < S1 6357): close/trim put spread early; keep or trail call spread; avoid averaging losers.
- **Neutral outcome** (inside S1-R1): hold for 40-60% max credit capture, then de-risk before late-day gamma expansion.

## Data and disclaimer
- Data sources: FMP `/quote` (^GSPC, SPY, ^VIX), `/historical-price-full` (SPY, ^VIX), `/economic_calendar`, `/earning_calendar`; broker feed required for exact ES Globex range.
- This briefing is for educational/research purposes only and is not investment advice.
