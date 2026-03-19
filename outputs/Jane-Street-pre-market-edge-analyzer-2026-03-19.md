# Jane Street Pre-Market Edge — 2026-03-19

## 1) Market assessment

SPX proxy conditions are risk-off into the open: SPX cash last 6624.70 and SPY 661.43 with no reliable ES pre-market tape from broker in this run. Using SPY as proxy, the gap versus the most recent close is effectively flat, so the edge is not a directional gap bet but a volatility/range execution.

Implied volatility remains elevated: VIX 26.04 vs prior close 25.09 (+0.95, +3.8%). That keeps theta attractive, but with larger intraday tails than a low-vol tape, so strikes should be wider than normal and entries delayed until opening rotation settles.

Macro/event risk is moderate-to-high for the morning because 8:30 ET labor prints (Initial/Continuing Claims) can expand first-hour range. Earnings are not broad-index dominant, but large names like ACN and FDX still add single-name volatility pockets.

## 2) Overnight futures movement

- **Input status:** No user-supplied ES/SPX futures level.
- **Proxy used:** SPY close proxy (SPY 661.43).
- **Gap (proxy):** ~0.00 points (~0.00%) vs prior close.
- **View:** **Uncertain / slight fade bias** — no meaningful gap signal, and 8:30 ET data can create a fake first move.

## 3) Pre-market IV levels

- **Current VIX:** 26.04
- **Yesterday VIX close:** 25.09
- **Delta:** +0.95 (+3.8%)
- **Read:** Options are pricing more movement than yesterday; premium selling is still valid, but use defined-risk structures and avoid early over-sizing.

## 4) Economic calendar impact

### Key U.S. events (ET)
- **8:30 ET:** Initial Jobless Claims (High impact)
- **8:30 ET:** Continuing Jobless Claims (High impact)
- **8:30 ET:** Philadelphia Fed Manufacturing Index (Medium impact)
- **10:00 ET:** New Home Sales (High impact)

### Historical range behavior (rule-of-thumb)
- Jobless claims surprises can push first-hour index range to ~1.2x-1.5x normal.
- Philly Fed surprises tend to amplify cyclical/industrial factor rotation more than index trend persistence.
- 10:00 ET housing data can trigger a second volatility pulse after open.

- **Calendar load:** **Moderate**
- **Recommendation:** Trade after first 15-30 minutes, keep wings defined, and avoid max size before 10:00 ET print clears.

## 5) Earnings exposure

### Notable larger-cap names reporting today
- **ACN (Accenture)** — BMO
- **FDX (FedEx)** — AMC
- **BABA / PDD** — BMO (large U.S.-listed, China-sensitive risk)
- **DRI (Darden)** — BMO

- **Market-moving potential for SPX index:** **Medium-Low**
- **Read:** More single-name/sector volatility than broad index shock unless guidance is extreme.

## 6) Globex range and expected range

- **Globex overnight high/low:** Not available from FMP; use broker/futures platform for true ES overnight extremes.
- **Proxy prior-day range (SPY):** 669.72 - 661.19 = **8.53 points** (~SPX proxy ~85 points).

### VIX-based expected move (1-day)
- Formula: `Price × (VIX/100) / sqrt(252)` (approx `Price × VIX / 1600`)
- Using SPX 6624.70 and VIX 26.04:
  - **Expected move:** about **+/-108 points** (~+/-1.63%)
  - **Implied day range:** roughly **6517 to 6733**

## 7) Opening gap strategy

- **Plan:** **Stay flat at open, define theta trade at 9:45-10:05 ET.**
- **Why:** No strong gap edge + 8:30/10:00 macro windows can create two-way whipsaw.
- **Execution note:** If opening drive rejects 6700 quickly, favor call-side fade; if acceptance above 6700 persists, reduce call-side aggression.

## 8) IV crush opportunity

- **Yesterday high-IV event?** No single scheduled event like FOMC/CPI, but volatility still repriced higher.
- **Opportunity:** **Yes, conditional.** Elevated VIX can still mean post-open IV softening if realized move compresses after macro prints.
- **Implication:** Use an iron condor (defined risk), not naked short premium.

## 9) Previous day close analysis

Using SPY prior session OHLC (Open 668.36, High 669.72, Low 661.19, Close 661.43):
- Close was near the **lows of day** (close-location ~3% of range from low).
- **Lean:** **Slight bullish mean-reversion / neutral** for next session open, but only after confirming buyers defend early support.

## 10) Support and resistance

### Support
1. **6620** — Prior day low proxy zone (first downside defense).
2. **6600** — Round-number gamma magnet.
3. **6517** — VIX-implied lower expected-move boundary.

### Resistance
1. **6700** — Prior day high proxy + psychological level.
2. **6733** — VIX-implied upper expected-move boundary.
3. **6750** — Round-number extension / potential exhaustion zone.

## 11) Pre-market trade plan

- **Strategy:** 0DTE **SPX Iron Condor** (defined risk, short premium)
- **Structure (model strikes):**
  - Sell **6540 Put**
  - Buy **6520 Put**
  - Sell **6715 Call**
  - Buy **6735 Call**
- **Expiration:** Today (0DTE)
- **Entry time:** **9:45-10:05 AM ET** (after open settles; reassess if strong one-way tape)
- **Sizing:** Risk **1x normal, max 2-3% account risk** due elevated VIX/event clustering
- **Invalidation:** Stand down if price accepts above 6733 or below 6600 with momentum before entry.

## 12) Scenario playbook

- **Bull outcome (price > 6700 and holding):**
  - Reduce/close call spread early if delta expands.
  - Keep put side; target 50-60% total position P&L intraday.

- **Bear outcome (price < 6620 with continuation):**
  - Reduce/close put spread risk quickly; keep/harvest call side.
  - If breakdown extends under 6600, do not roll aggressively into momentum.

- **Neutral outcome (price oscillates 6620-6700):**
  - Hold condor; take profits at 40-60% of max credit before late-day gamma window.
  - Flatten remaining risk by ~3:00 PM ET if realized vol re-expands.

## 13) Data and disclaimer

- **Data sources:** FMP `/quote` (^GSPC, SPY, ^VIX), FMP `/historical-price-full/SPY`, FMP `/historical-price-full/^VIX`, FMP `/economic_calendar`, FMP `/earning_calendar`.
- **Overnight note:** True ES/Globex high-low and exact futures positioning should be confirmed on broker/futures platform.
- **Disclaimer:** For educational and research purposes only. Not investment advice. Options involve substantial risk, including potential loss of principal. Validate prices, liquidity, and risk limits before trading.
