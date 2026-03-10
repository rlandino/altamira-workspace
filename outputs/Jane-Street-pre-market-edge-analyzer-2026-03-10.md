# Jane Street Pre-Market Edge — 2026-03-10

## Market assessment
Overnight proxy pricing points to **SPX 6,835.8** versus a prior-session SPX-proxy close near **6,794.6**, implying a **gap of +41.2 points (+0.61%)**. **View: Uncertain** - Gap is statistically fade-prone, but high-impact macro events can force continuation after data.

Implied volatility is represented by **VIX 22.41 vs yesterday close 25.50 (-3.09, -12.1%).** This suggests leaner option premium versus yesterday, with less edge in aggressive short-vol.

The prior session closed **at highs** of the day range (SPY proxy), giving a **Bearish-to-neutral mean-reversion lean**. Macro calendar load is **Moderate**, and earnings-related index spillover risk is assessed as **High**.

## Overnight futures movement
- **Current proxy level:** SPX 6,835.8 (using ^GSPC quote; exact ES/Globex from broker).
- **Prior close proxy:** SPX 6,794.6.
- **Gap:** +41.2 points (+0.61%).
- **Gap view:** **Uncertain** - Gap is statistically fade-prone, but high-impact macro events can force continuation after data.

## Pre-market IV levels
- **Current VIX:** 22.41.
- **Vs yesterday:** VIX 22.41 vs yesterday close 25.50 (-3.09, -12.1%).
- **Implication:** Premiums are lighter; avoid forcing tight short strikes.

## Economic calendar impact
- **Calendar load:** **Moderate**.
- **2026-03-10 10:00:00** - **NFIB Business Optimism Index (Feb)**. Can increase intraday volatility around release time.
- **Recommendation:** Trade smaller and wait until event clears; use wider strikes.

## Earnings exposure
- **Market-moving potential:** **High**.
- **ORCL**  - amc.
- **Read-through risk:** Single-name IV spikes can spill into index vol if mega-cap beats/misses materially.

## Globex range and expected range
- **Globex range:** Exact overnight high/low should be read from broker futures feed.
- **Proxy (prior session range):** 175.6 SPX points (from prior SPY high-low converted to SPX scale).
- **VIX-implied 1-day expected move:** **+/-96.5 points (~+/-1.41%)**.

## Opening gap strategy
- **Plan:** Stay cautious into open; wait for first 15 minutes and then fade extension back toward VWAP.
- If gap extends beyond first 15 minutes with volume confirmation, avoid early fade and re-anchor strikes to new range.

## IV crush opportunity
- **IV crush setup:** Yes - event premium can compress after scheduled releases; prioritize defined-risk short premium after data clears.

## Previous day's close analysis
- Prior day SPY OHLC: **O 666.39 / H 679.92 / L 662.39 / C 678.27**.
- Session closed **at highs** of range -> **Bearish-to-neutral mean-reversion lean** for today's open.

## Support and resistance
**Support levels (SPX):**
- **S1: 6800** - nearest support / overnight balance zone proxy.
- **S2: 6745** - prior-session structure / expected-move overlap.
- **S3: 6740** - deeper expected-move support.

**Resistance levels (SPX):**
- **R1: 6845** - nearest resistance / opening extension checkpoint.
- **R2: 6850** - prior-session structure or round-number magnet.
- **R3: 6930** - expected-move upper boundary.

## Pre-market trade plan
- **Strategy:** 0DTE iron condor with wider wings
- **Structure (SPX 0DTE):**
  - Sell **6750 Put**
  - Buy **6720 Put**
  - Sell **6925 Call**
  - Buy **6955 Call**
- **Expiration:** Today (0DTE).
- **Entry time:** 9:40-10:00 AM ET after opening range forms
- **Position size:** Normal to 0.75x size; risk 2% account max.
- **Risk protocol:** Hard stop if spot touches short strike with momentum; target 40-50% max credit capture.

## Scenario playbook
- **Bull outcome (price > R1 6845):** Close/trim call spread early, keep put spread if trend remains orderly; do not add call risk into breakout.
- **Bear outcome (price < S1 6800):** Close/roll put spread defensively, consider taking call side profits; avoid averaging losers.
- **Neutral outcome (price between S1 and R1):** Hold position for theta decay, take 40-50% profits or close by ~2:00 PM ET.

## Data and disclaimer
- **Data sources:** FMP `quote` (^GSPC, SPY, ^VIX), `historical-price-full` (SPY, ^VIX), `economic_calendar`, `earning_calendar` for 2026-03-10.
- **Overnight/Globex note:** Exact ES overnight high/low not provided by FMP in this run; broker futures feed should be used for precise Globex range.
- **Disclaimer:** For educational and research purposes only; not investment advice.
