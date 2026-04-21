# Jane Street Pre-Market Edge — 2026-04-21

## Market Assessment

Overnight proxies indicate **SPX near 7,109.14**, with a modeled gap of **+0.0 pts (+0.00%)** versus prior close proxy. Initial read: **Hold/Grind** — small overnight displacement usually extends unless data surprises hit at the open.

Implied volatility is **flat** versus yesterday (**VIX 18.81 vs 18.87, -0.06 / -0.32%**). That implies vol is near yesterday, so focus edge on structure and timing rather than pure IV mean reversion.

Macro/event backdrop is **Heavy** with earnings impact assessed as **Low**. Tactical focus: avoid forcing first print, then deploy defined-risk theta if price accepts inside opening range.


## Overnight Futures Movement

- **Proxy level used:** ^GSPC cash quote (7,109.14) with SPY-to-SPX scaling factor 10.031.
- **Gap vs prior close proxy:** **+0.0 pts (+0.00%)**.
- **View:** **Hold/Grind** — small overnight displacement usually extends unless data surprises hit at the open.
- **Note:** SPX/ES exact overnight print and Globex levels should come from broker futures feed.

## Pre-Market IV Levels

- **Current VIX:** 18.81
- **Yesterday VIX close (proxy):** 18.87
- **Change:** -0.06 (-0.32%)
- **Interpretation:** Options are pricing **flat** volatility vs yesterday; vol is near yesterday, so focus edge on structure and timing rather than pure IV mean reversion.

## Economic Calendar Impact

- **High-impact US events**
- **2026-04-21 18:30:00** — Fed Waller Speech
- **2026-04-21 12:30:00** — Retail Sales MoM (Mar)
- **2026-04-21 12:30:00** — Retail Sales YoY (Mar)
- **2026-04-21 12:30:00** — Retail Sales Ex Gas/Autos MoM (Mar)
- **2026-04-21 12:30:00** — Retail Sales Ex Autos MoM (Mar)

- **Additional US events**
- **2026-04-21 20:30:00** — API Crude Oil Stock Change (Apr/17)
- **2026-04-21 18:30:00** — Fed Waller Speech
- **2026-04-21 14:00:00** — Pending Home Sales YoY (Mar)
- **2026-04-21 14:00:00** — Retail Inventories Ex Autos MoM (Feb)
- **2026-04-21 14:00:00** — Business Inventories MoM (Feb)
- **2026-04-21 14:00:00** — Pending Home Sales MoM (Mar)
- **2026-04-21 12:55:00** — Redbook YoY (Apr/18)
- **2026-04-21 12:30:00** — Retail Sales MoM (Mar)

- **Calendar load:** **Heavy**
- **Recommendation:** Trade after major prints; widen short strikes and size down.
- **Historical range note:** CPI/NFP/Fed-style prints often expand intraday range to ~1.5x-2.0x baseline.

## Earnings Exposure

- **Index-relevant reporters today**
- **UNH** () — bmo

- **Market-moving potential:** **Low**
- **Read-through:** Single-name IV can spike around prints; broad index effect is material only if mega-cap surprise is large.

## Globex Range and Expected Range

- **Globex overnight high/low:** Pull from broker/futures platform (not fully available via FMP cash endpoints).
- **Proxy (prior SPY session range):** 37.8 SPX points (709.91-706.14 SPY on 2026-04-20).
- **VIX-based expected 1-day move:** **±84.2 points (~±1.18%)**.

## Opening Gap Strategy

- Gap is **+0.00%**; base plan is **wait for first 15 minutes, then trade with accepted range**.
- If first 15-minute candle rejects the gap direction, prioritize mean-reversion entries.
- If price holds above/below opening range with breadth confirmation, avoid fighting momentum.

## IV Crush Opportunity

- Prior session was **not** flagged as a major scheduled vol event from the available feed.
- With VIX **flat** vs yesterday, IV-crush edge is **moderate**; focus on clean entry timing and defined wings.

## Previous Day's Close Analysis

- Prior session (SPY 2026-04-20) closed **at highs** of the day range.
- **Lean for today:** **Bearish-to-neutral** — late-session strength often invites profit-taking unless macro catalyst confirms continuation.

## Support and Resistance

### Support
- **S1: 7085** — Prior day low proxy.
- **S2: 7050** — Half expected-move downside / round-number magnet.
- **S3: 7025** — Full expected-move downside projection.

### Resistance
- **R1: 7120** — Prior day high proxy.
- **R2: 7175** — Half expected-move upside / round-number magnet.
- **R3: 7195** — Full expected-move upside projection.

## Pre-Market Trade Plan

- **Strategy:** 0DTE SPX iron condor (defined-risk, expected-move wings)
- **Structure (model-based, no live chain deltas):**
  - Short Put: **7035**
  - Long Put: **7010**
  - Short Call: **7185**
  - Long Call: **7210**
- **Expiration:** 0DTE (today)
- **Entry time:** Post-event entry only (after 2026-04-21 18:30:00 ET reaction stabilizes)
- **Position size:** 1x normal if calendar is light; 0.5x-0.75x if event risk is elevated (risk <= 2-3% account per trade).

## Scenario Playbook

- **Bull outcome (price > R1):** Close or trim call spread side early; keep put side if decay remains favorable; do not add risk into breakout without reset.
- **Bear outcome (price < S1):** Reduce/close put side quickly; monetize call side gains; re-center only after volatility stabilizes.
- **Neutral outcome (inside S1-R1):** Hold for 40-60% max profit target; avoid over-managing before noon unless delta imbalance spikes.

## Data and Disclaimer

- **Data sources:** FMP quote (^GSPC, SPY, ^VIX), FMP historical-price-full (SPY and ^VIX), FMP economic_calendar, FMP earning_calendar.
- **Overnight/Globex note:** Exact ES/SPX futures overnight range should be sourced from broker/futures platform.
- **Disclaimer:** This briefing is for educational and research purposes only, not investment advice. Options involve substantial risk and may not be suitable for all investors.
