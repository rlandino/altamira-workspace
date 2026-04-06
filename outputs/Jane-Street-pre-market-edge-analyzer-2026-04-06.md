# Jane Street Pre-Market Edge — 2026-04-06

## Market assessment
Overnight index pricing is modestly higher with SPX near 6,582.7 versus prior close 6,575.3, a small +0.11% gap that is more likely to **hold initially then mean-revert intraday** than to trend straight-line at the open.

Implied volatility is **elevated**: VIX 25.03 vs prior close 23.87 (+1.16, +4.86%). This keeps option premium attractive for theta sellers, but risk should stay defined because realized intraday swings can still expand.

Yesterday closed in the **upper third / near highs** of its range, which gives a mildly bearish-to-mean-reverting bias unless breadth and momentum decisively reclaim resistance early. Macro headline risk is concentrated around the 10:00 ET ISM data block; earnings exposure is low for mega-cap index movers today.

## Overnight futures movement
- **Current SPX proxy:** 6,582.69
- **Prior close:** 6,575.32
- **Gap:** +7.37 pts (+0.11%)
- **View:** **Hold-to-neutral** — Gap is small; absent a 8:30 ET macro shock, early flow tends to respect opening direction before balancing near VWAP.

## Pre-market IV levels
- **VIX now:** 25.03
- **VIX prior close:** 23.87
- **Change:** +1.16 (+4.86%)
- **Read-through:** Options are pricing more movement than yesterday; Premium is rich; prefer defined-risk structures and wider wings.

## Economic calendar impact
- **Key US events today (ET):**
  - 10:00 AM ET: ISM Services Prices (Mar) (Low impact) — Lower direct index impact unless surprise is large.
  - 10:00 AM ET: ISM Services Business Activity (Mar) (Low impact) — Lower direct index impact unless surprise is large.
  - 10:00 AM ET: ISM Services Employment (Mar) (Low impact) — Lower direct index impact unless surprise is large.
  - 10:00 AM ET: ISM Services New Orders (Mar) (Low impact) — Lower direct index impact unless surprise is large.
  - 10:00 AM ET: ISM Services PMI (Mar) (High impact) — High impact; can expand index range ~1.3x-1.7x normal intraday move.
  - 10:00 AM ET: ISM Non-Manufacturing Business Activity (Mar) (Low impact) — Lower direct index impact unless surprise is large.
- **Calendar regime:** **Moderate**
- **Recommendation:** Keep initial size smaller and avoid adding unhedged short gamma right before 10:00 ET data.

## Earnings exposure
- **Largest-cap names reporting today (FMP earnings calendar):**
  - BNCDY ($60.1B, UNSPECIFIED)
- **Market-moving potential:** **Low to Medium** (few US mega-cap index heavyweights on today's slate).

## Globex range and expected range
- **Globex overnight high/low:** Not provided by FMP; use broker futures ladder for exact ES overnight range.
- **Proxy prior session range (SPY):** 13.09 points (645.11 to 658.20)
- **VIX-based 1-day expected SPX move:** ±103.0 points (about ±1.56%)

## Opening gap strategy
- **Plan:** Normal theta deployment after first 10-15 minutes, but avoid oversized risk ahead of 10:00 ET ISM prints.
- **Execution filter:** Require 5-minute candle acceptance above/below opening range before committing full size.

## IV crush opportunity
- No major scheduled pre-open macro release in this dataset; the nearest high-impact cluster is at 10:00 ET.
- With VIX elevated, **intraday IV compression is tradable** if price remains inside expected move and breadth is not one-sided.

## Previous day's close analysis
- **SPY OHLC (prior session):** O 646.42 / H 658.20 / L 645.11 / C 655.83
- **Close location:** upper third / near highs (81.9% from low to high)
- **Lean for today:** mildly bearish-to-mean-reverting.

## Support and resistance
- **Support levels (SPX):**
  - **S1 6,575.0** — nearby round/spot support
  - **S2 6,523.8** — half expected-move downside from prior close
  - **S3 6,474.9** — prior-session low zone
- **Resistance levels (SPX):**
  - **R1 6,600.0** — nearby round level overhead
  - **R2 6,601.9** — half expected-move upside / prior high confluence
  - **R3 6,626.8** — extension toward +1 expected-move continuation

## Pre-market trade plan
- **Strategy:** 0DTE SPX iron condor (defined risk, short premium)
- **Strikes (expected-move / ~0.10-0.15 delta proxy):**
  - Short Put 6500, Long Put 6475
  - Short Call 6675, Long Call 6700
- **Expiration:** Today (0DTE)
- **Entry time:** 9:40-9:55 AM ET (after opening range forms); avoid new size inside 9:58-10:02 ET around ISM release
- **Position size:** 1/2 to 2/3 normal size (about 1.5%-2.5% account risk) due elevated VIX + macro print at 10:00 ET

## Scenario playbook
- **Bull outcome:** Sustained trade above R1 (6,600.0).
  - Action: Reduce/close call spread at 1.5x credit or if delta > 0.30; keep put side working toward 50% total P/L target.
- **Bear outcome:** Sustained trade below S1 (6,575.0).
  - Action: Reduce/close put spread at 1.5x credit or if delta > 0.30; keep call side for decay.
- **Neutral outcome:** Price remains between S1 and R1 through midday.
  - Action: Target 40-60% of max profit; flatten by ~2:30 PM ET to reduce late-day gamma risk.

## Data and disclaimer
- **Data sources:** FMP quote (^GSPC, SPY, ^VIX), historical-price-full (SPY/^GSPC/^VIX), economic_calendar, earning_calendar.
- **Globex note:** True ES overnight high/low should come from broker/futures platform; this report uses spot/proxy where futures ladder is unavailable.
- **Disclaimer:** Educational/research content only. Not investment advice. Options involve substantial risk and may not be suitable for all investors.
