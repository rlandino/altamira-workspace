# Jane Street Pre-Market Edge — 2026-04-16

## Market assessment

US index proxies indicate a **+0.0-point (+0.00%)** overnight displacement versus the prior SPX-equivalent close. Base case is **hold** behavior into the open because small overnight displacement often extends with opening auction flow.

Implied volatility is **flat** pre-market with VIX at **18.27** versus prior close **18.36** (-0.09, -0.49%). Implied vol is near unchanged; edge comes more from level selection and timing.

Macro event load is **Heavy** with 8 flagged high-impact items; earnings spillover risk is **Medium** based on today's large-cap reporters.

## Overnight futures movement

- **Current proxy level (SPX):** 7022.95 (from ^GSPC quote; use broker ES for exact futures)
- **Prior SPX-equivalent close (from SPY):** 7022.95
- **Gap:** +0.0 points (+0.00%)
- **View:** **Hold** — Small overnight displacement often extends with opening auction flow.

## Pre-market IV levels

- **VIX now:** 18.27
- **VIX vs yesterday close:** 18.36 (-0.09, -0.49%)
- **Read:** Options are pricing **flat** volatility versus yesterday. Implied vol is near unchanged; edge comes more from level selection and timing.

## Economic calendar impact

- **2026-04-17 04:00:00** — **Inflation Rate MoM (Mar)**: Potential volatility catalyst; manage size and wait for post-release confirmation.
- **2026-04-17 04:00:00** — **CPI MoM (Mar)**: CPI releases often expand intraday index range toward ~1.5x normal.
- **2026-04-17 04:00:00** — **Inflation Rate YoY (Mar)**: Potential volatility catalyst; manage size and wait for post-release confirmation.
- **2026-04-17 04:00:00** — **CPI YoY (Mar)**: CPI releases often expand intraday index range toward ~1.5x normal.
- **2026-04-17 04:00:00** — **GDP Growth Rate YoY (Q1)**: Potential volatility catalyst; manage size and wait for post-release confirmation.
- **2026-04-16 22:45:00** — **Retail Sales MoM (Mar)**: Retail Sales can reprice growth expectations and index breadth quickly.

- **Calendar load:** **Heavy**
- **Recommendation:** Reduce size and wait until after first high-impact event window before deploying full risk.

## Earnings exposure

- **NFLX** (TBD)

- **Market-moving potential:** **Medium**
- **Read:** Single-name IV can spike even if index impact stays contained.

## Globex range and expected range

- **Globex overnight high/low:** From broker/futures platform (not fully available via equity-only FMP feed)
- **Proxy prior-session range (SPY):** 6.08 points (~61.0 SPX points)
- **Expected 1-day move (VIX model):** ±80.2 SPX points (~±1.14%)

## Opening gap strategy

- Small-to-moderate gap detected.
- **Opening plan:** Run normal theta setup after first 15-minute range defines control.
- **Risk condition:** Stand down around scheduled high-impact releases if liquidity thins.

## IV crush opportunity

- **Assessment:** Yes — elevated/flat pre-open IV supports intraday premium harvesting.
- **Implication:** Favor defined-risk structures and take profits at 40-60% of max.

## Previous day's close analysis

- **Prior day OHLC (SPY):** O 695.26 / H 700.28 / L 694.20 / C 699.94
- **Close location:** Market closed **at highs** of range (94.4% from low to high)
- **Lean:** **Bearish-to-neutral lean** — Close near session highs raises early profit-taking odds.

## Support and resistance

### Support
- **S1: 7025** — prior close/round-number magnet
- **S2: 6965** — expected move lower boundary
- **S3: 6945** — deeper downside extension

### Resistance
- **R1: 7025** — opening pivot/round number
- **R2: 7105** — expected move upper boundary
- **R3: 7130** — extension level with call-side pressure

## Pre-market trade plan

- **Strategy:** 0DTE SPX iron condor (defined risk)
- **Strikes (model-based, expected-move approximation):**
  - Short Put: **6950**
  - Long Put: **6925**
  - Short Call: **7095**
  - Long Call: **7120**
- **Expiration:** Today (0DTE)
- **Entry time:** 9:35-9:50 AM ET after opening range forms; delay if a high-impact event is imminent.
- **Position size:** 1x normal size (max 2% account risk)
- **Risk controls:** Stop at 2x credit collected or short strike breach with momentum confirmation.

## Scenario playbook

- **Bull outcome (above R1):** Reduce/close call spread on adverse delta acceleration; keep put side and target 50%+ total profit.
- **Bear outcome (below S1):** Reduce/roll put spread down and out if trend persists; keep call side as hedge.
- **Neutral outcome (inside S1-R1):** Hold for theta decay and close around 50-60% max profit before 2:00 PM ET.

## Data and disclaimer

- **Data sources:** FMP quote (^GSPC, SPY, ^VIX), FMP historical-price-full (SPY, ^VIX), FMP economic_calendar, FMP earning_calendar.
- **Overnight/Globex:** True ES Globex high/low should be pulled from broker futures platform.
- **Disclaimer:** For educational and research purposes only; not investment advice. Options involve substantial risk and may not be suitable for all investors.
