# Jane Street Pre-Market Edge — 2026-03-30

## Market assessment

Overnight proxy pricing implies a **+0.0 point (+0.00%)** gap versus prior SPX-equivalent close. **View: Hold** - Small gaps are less stretched and can extend with opening flow.

Pre-market IV is lower vs yesterday: VIX 30.49 vs 31.05 (-0.56, -1.8%). Cheaper premiums reduce edge for short-vol; prioritize tighter risk controls.

Prior session tone: market closed **at lows** of the day range (SPY 633.11-642.66, close 634.09), giving a **Bullish-to-neutral** lean into the open. Calendar intensity is **Heavy**, so opening risk control should dominate early execution.

## Overnight futures movement
- Current proxy level: ^GSPC 6368.85 (SPX/ES exact futures from broker for precision).
- Prior SPX-equivalent close (from SPY): 6368.85.
- Gap: **+0.0 pts (+0.00%)**.
- Hold/Fade view: **Hold** - Small gaps are less stretched and can extend with opening flow.

## Pre-market IV levels
- Pre-market IV is lower vs yesterday: VIX 30.49 vs 31.05 (-0.56, -1.8%).
- Implication: Cheaper premiums reduce edge for short-vol; prioritize tighter risk controls.

## Economic calendar impact
- Today's notable events (ET):
  - **2026-03-30 20:00:00** - Fed Williams Speech (**High**) | Historically can expand index range ~1.3x-2.0x normal.
  - **2026-03-30 15:30:00** - 6-Month Bill Auction (**Medium**) | Can create intraday volatility pockets.
  - **2026-03-30 15:30:00** - 3-Month Bill Auction (**Medium**) | Can create intraday volatility pockets.
  - **2026-03-30 14:30:00** - Dallas Fed Manufacturing Index (Mar) (**High**) | Historically can expand index range ~1.3x-2.0x normal.
  - **2026-03-30 14:30:00** - Fed Chair Powell Speech (**High**) | Historically can expand index range ~1.3x-2.0x normal.
- Calendar load: **Heavy**.
- Recommendation: Use wider strikes and delay full-size entries until after key release windows.

## Earnings exposure
- Companies reporting today (FMP): 1245 total.
- No mega-cap index-heavy earnings detected from today's list.
- Market-moving potential: **Medium** (single-name IV can spike even when index impact is limited).

## Globex range and expected range
- Globex overnight high/low: **From broker/futures platform** (not available in FMP spot endpoints).
- Prior day SPY range proxy: 9.55 points.
- VIX-based 1-day expected move: **±122.3 SPX points (~±1.92%)**.

## Opening gap strategy
- Normal theta deployment after first 5-15 minutes if breadth and internals are stable.
- Trigger: if price reclaims/loses round 6375 and holds for 5-minute closes, bias shifts to trend-follow instead of fade.

## IV crush opportunity
- Potentially yes - event premium can compress post-release if outcome is in-line.
- Theta implication: Favor defined-risk structures (iron condor/credit spreads) over naked short gamma in event windows.

## Previous day's close analysis
- SPY O/H/L/C: 642.50 / 642.66 / 633.11 / 634.09
- Closed **at lows** of range -> **Bullish-to-neutral** lean. Weak close often sets up relief bounces if no fresh macro shock appears.

## Support and resistance
- **Support levels**
  - S1: **6326.0** (near lower-third expected-move band)
  - S2: **6283.2** (deeper expected-move support)
  - S3: **6246.5** (full expected-move downside)
- **Resistance levels**
  - R1: **6411.7** (upper-third expected-move band)
  - R2: **6454.5** (deeper expected-move resistance)
  - R3: **6491.2** (full expected-move upside)
- Psychological pivot: **6375** round-number magnet.

## Pre-market trade plan
- **Strategy:** 0DTE SPX iron condor (defined risk).
- **Strikes (expected-move method):** Sell 6260P / Buy 6240P and Sell 6480C / Buy 6500C.
- **Expiration:** Today (0DTE).
- **Entry window:** 9:35-9:50 AM ET after first volatility flush; delay if high-impact data is near open.
- **Size:** 1x normal risk if calendar is moderate/light; 0.5x if heavy macro event risk remains.
- **Risk controls:** hard stop at 2x collected premium or on tested short strike with momentum confirmation.

## Scenario playbook
- **Bull outcome (above R1 6411.7):** Close/trim call spread early, keep put side if delta < 0.10, or fully de-risk at 1.5x premium expansion.
- **Bear outcome (below S1 6326.0):** Close/trim put spread early, keep call side if trend is orderly; avoid averaging down short puts.
- **Neutral outcome (inside S1-R1):** Hold for 40-60% max-profit target, then close before late-day gamma acceleration.

## Data and disclaimer
- **Data sources:** FMP `/quote` (^GSPC, SPY, ^VIX), `/historical-price-full/SPY`, `/historical-price-full/^VIX`, `/economic_calendar`, `/earning_calendar`.
- **Overnight/Globex:** Exact ES overnight high/low should be taken from broker/futures platform.
- **Disclaimer:** This analysis is for education and research only, not investment advice.
