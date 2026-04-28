# Jane Street Pre-Market Edge - 2026-04-28

## Market assessment

SPX is marked at **7,173.91** using FMP ^GSPC quote proxy; use broker ES/SPX futures for exact pre-market level. Prior SPX close was **7,173.92** on 2026-04-27, implying a gap of **-0.01 points (-0.00%)**. View: **Neutral / no meaningful gap** - opening conditions look close to prior settlement; use normal range-definition process.

VIX is **19.16**, +1.14 points (+6.33%) versus the prior close of 18.02. Vol regime is **normal-to-elevated**; defined-risk premium selling is acceptable after the open settles.

The prior session closed near the highs, creating a **mild bearish/mean-reversion lean if the open cannot reclaim the prior high**. Calendar weight is **Light** and earnings exposure is **material** for the index tape.

## Overnight futures movement

- Current SPX/ES proxy: **7,173.91** (FMP ^GSPC quote proxy; use broker ES/SPX futures for exact pre-market level.)
- Prior SPX close: **7,173.92**
- Gap: **-0.01 points (-0.00%)**
- Hold/fade view: **Neutral / no meaningful gap** - opening conditions look close to prior settlement; use normal range-definition process.
- Note: true ES Globex high/low should be checked on the broker/futures platform before placing live orders.

## Pre-market IV levels

- VIX: **19.16** vs prior close **18.02** (+1.14, +6.33%).
- 5-session VIX average: **18.89**.
- Read-through: options are pricing **higher** volatility vs yesterday; defined-risk premium selling is acceptable after the open settles.

## Economic calendar impact

- No U.S. economic calendar events returned by FMP for today.
- Calendar summary: **Light**. Recommendation: **Normal theta is acceptable after the first 15 minutes; keep strikes outside the VIX expected move.**

## Earnings exposure

- **KO**  - bmo, EPS est. 0.81. Market-moving potential: **High**.
- **V**  - amc, EPS est. 3.09. Market-moving potential: **High**.
- Single-name IV remains event-specific; index impact is material only if mega-cap or sector-heavy names surprise.

## Globex range and expected range

- Globex range: **from broker/futures platform**. FMP does not provide ES overnight high/low in this workflow.
- Prior day SPX range proxy: **7,146.72 - 7,178.74** (32.02 points).
- VIX-based 1-day expected move: **+/-86.59 points** (~+/-1.21%), giving a working range of **7,087.32 - 7,260.50**.

## Opening gap strategy

- Strategy: **Normal theta setup after 9:45 ET; define strikes outside prior day extremes and the VIX expected range.**
- If the first 15-minute range breaks and holds, avoid fighting trend day mechanics; sell only the untested side or stand down.

## IV crush opportunity

- No scheduled macro IV-crush catalyst identified from today's calendar; theta edge is mainly intraday decay, not event-vol collapse.
- Best expression is defined-risk SPX premium after the first volatility impulse, not naked short gamma into unknown range expansion.

## Previous day's close analysis

- Prior SPX OHLC (2026-04-27): open **7,152.72**, high **7,178.74**, low **7,146.72**, close **7,173.92**.
- Market closed near the highs; mild bearish/mean-reversion lean if the open cannot reclaim the prior high.

## Support and resistance

**Support**
- Support 1: **7,146.72** - Prior session low.
- Support 2: **7,125.00** - Nearby round-number demand zone.
- Support 3: **7,085.00** - VIX 1-day expected move lower bound.

**Resistance**
- Resistance 1: **7,178.74** - Prior session high.
- Resistance 2: **7,200.00** - Nearby round-number supply zone.
- Resistance 3: **7,265.00** - VIX 1-day expected move upper bound.

## Pre-market trade plan

- Strategy: **0DTE SPX iron condor, defined-risk, small size**
- Structure: sell **7085P / buy 7075P**, sell **7265C / buy 7275C**.
- Expiration: **today (0DTE)** if liquidity and spreads are normal; otherwise use the nearest weekly and cut size.
- Entry time: **9:45-10:00 AM ET after the opening range settles**.
- Position size: **Risk 2-3% of account, defined-risk only; reduce size if bid/ask spreads are wide.**
- Profit/risk management: target 40-50% of max profit; stop or reduce if SPX trades through a short strike, if spread value reaches ~2x credit, or if realized range expands beyond the VIX envelope.

## Scenario playbook

- **Bull outcome:** SPX holds above Resistance 1 (**7,178.74**). Do not add call risk; close or roll the call spread if momentum holds above the level, and leave the put side only if credit has decayed meaningfully.
- **Bear outcome:** SPX breaks below Support 1 (**7,146.72**). Do not add put risk; close or roll the put spread, and consider harvesting the call side at 50-70% of max profit.
- **Neutral outcome:** SPX remains between Support 1 and Resistance 1. Hold toward 40-50% max profit, then close; avoid holding into late-day gamma unless spreads are nearly worthless.

## Data and disclaimer

- Data sources: FMP quote for ^GSPC, SPY, ^VIX; FMP historical-price-full for SPX/SPY/VIX prior-session data; FMP economic_calendar; FMP earning_calendar.
- Globex/overnight range: not supplied by FMP; use broker/futures platform for exact ES high/low and live futures level.
- Disclaimer: for educational and research purposes only; not investment advice or a recommendation to buy or sell securities/options. Options involve substantial risk.
