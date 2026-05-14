# Jane Street Pre-Market Edge - 2026-05-14

## Market assessment

SPX is effectively flat versus the prior session using FMP's index quote as the pre-market proxy: 7,444.25 versus the 2026-05-13 close of 7,444.26. FMP did not return an explicit ES/Globex high-low or preMarket field, so use broker SPX/ES data for exact futures positioning before entry.

VIX is 17.82 versus yesterday's 17.87 close, down 0.05 vol points. That keeps index premium in a normal regime: enough theta to sell defined risk, but not rich enough to justify aggressive size ahead of Fed speakers.

Yesterday closed near the upper end of the range, which argues for some early mean-reversion risk if buyers cannot clear 7,460. The calendar is moderate, not heavy: no CPI/NFP-style 8:30 shock in the FMP feed, but several Fed speakers can interrupt intraday compression.

## Overnight futures movement

- **Premarket proxy:** SPX 7,444.25 from FMP quote; exact SPX/ES futures should be checked with broker data.
- **Prior SPX close:** 7,444.26.
- **Implied gap:** -0.01 points (-0.00%).
- **View:** **Uncertain / neutral open** - no actionable gap from FMP's proxy. Let the first 15 minutes define whether yesterday's high is accepted or rejected.

## Pre-market IV levels

- **Current VIX:** 17.82.
- **Yesterday's VIX close:** 17.87.
- **Change:** -0.05 vol points (-0.3%).
- **5-session VIX close average:** ~17.70.
- **Read:** Options are pricing slightly lower volatility than yesterday but still near the recent average. Defined-risk premium selling is acceptable; avoid oversized naked short-vol exposure.

## Economic calendar impact

FMP events for today, converted from UTC to ET where applicable:

- **10:00 AM ET - Business Inventories MoM (Mar), Medium impact.** Usually a secondary macro input, but it can move rates-sensitive sectors if paired with other data.
- **10:15 AM ET - Fed Schmid speech, Medium impact.** Fed commentary can expand intraday range if it changes rate-cut expectations.
- **11:30 AM ET - 4-week and 8-week bill auctions, Low impact.** Watch front-end yield reaction; usually limited SPX impact.
- **1:00 PM ET - Fed Bowman and Fed Hammack speeches, Medium impact.** Avoid initiating new short premium immediately ahead of remarks.
- **5:45 PM ET - Fed Williams speech; 7:00 PM ET - Fed Barr speech, Medium impact.** After the cash session; relevant for overnight risk rather than 0DTE management.

**Calendar grade:** Moderate. Trade after the open settles; use wider strikes and smaller size than a clean-calendar day.

## Earnings exposure

Large-cap and index-relevant reports in the FMP calendar:

- **AMAT - Applied Materials, AMC, ~$346B market cap.** High single-name and semiconductor-readthrough risk after the close; limited 0DTE cash-session impact unless semis pre-position.
- **BN - Brookfield, BMO, ~$101B market cap.** Medium financial/asset-manager readthrough, low direct SPX impulse.
- **NU - Nu Holdings, AMC, ~$62B market cap.** Growth-fintech risk after the close; limited index weight.
- **HMC, NGG, VIK - BMO reports.** Mostly single-name or international ADR risk; low broad-index impulse.

**Market-moving potential:** Medium after the close because AMAT can affect semiconductors and Nasdaq sentiment; low-to-medium during the cash session.

## Globex range and expected range

- **Globex range:** Not available from FMP. Use broker/futures platform for ES overnight high-low before placing orders.
- **Prior-day SPX range proxy:** 7,460.04 high - 7,375.13 low = **84.91 points**.
- **VIX-based 1-day expected move:** 7,444.25 x 17.82% / sqrt(252) = **+/-83.6 points** (~+/-1.12%).
- **Expected range from proxy:** Roughly **7,361 to 7,528**.

## Opening gap strategy

- **Strategy:** Normal theta setup after the first 15 minutes; do not force a gap fade because the FMP proxy shows no meaningful gap.
- **Execution rule:** If SPX rejects 7,460 early, sell call-side premium only after momentum stalls. If SPX holds above 7,460 for 10-15 minutes, avoid fading strength and move call risk farther out.
- **Caution:** Fed commentary begins at 10:15 AM ET. Prefer entries between 9:45 and 10:00 AM ET or after the first Fed headline has passed.

## IV crush opportunity

Yesterday was not flagged by FMP as a major macro-vol event like CPI, NFP, or an FOMC decision. VIX is slightly lower versus yesterday, so this is not a classic post-event IV crush setup.

**Theta implication:** Sell defined-risk premium only where technical levels and the VIX expected move agree. The edge is time decay plus range containment, not a large implied-volatility collapse.

## Previous day's close analysis

- **Prior SPX open:** 7,409.12.
- **Prior SPX high:** 7,460.04.
- **Prior SPX low:** 7,375.13.
- **Prior SPX close:** 7,444.26.
- **Close location:** About 81% of the way up the prior day's range.
- **Lean:** Bearish/mean-reversion lean at the open if price cannot clear the prior high. A sustained hold above 7,460 cancels the fade thesis.

## Support and resistance

### Support

1. **7,400** - round-number support and first downside magnet below the prior close.
2. **7,375** - prior-day low; break would signal failed momentum.
3. **7,361** - VIX expected-move downside boundary.

### Resistance

1. **7,460** - prior-day high; first test for continuation.
2. **7,500** - round-number resistance and likely gamma/momentum checkpoint.
3. **7,528** - VIX expected-move upside boundary.

## Pre-market trade plan

- **Primary strategy:** 0DTE SPX iron condor, defined risk.
- **Expiration:** Today, 2026-05-14.
- **Entry window:** 9:45-10:00 AM ET after the open settles; skip or delay if Fed headlines hit early.
- **Put side:** Sell **7,350 put**, buy **7,330 put**.
- **Call side:** Sell **7,530 call**, buy **7,550 call**.
- **Strike logic:** Shorts sit just outside the VIX expected range and beyond prior-day technical levels. Use live option chain deltas if available; target roughly 0.10-0.15 delta shorts.
- **Position size:** 1-2% of account at risk because calendar risk is moderate and VIX is not especially rich.
- **Risk management:** Close at 50% of max profit, stop at 2x credit received, or exit a side if SPX accepts beyond the short strike with momentum.

## Scenario playbook

- **Bull outcome - SPX above 7,460 and holding:** Do not add call risk. If already in the condor, take off or roll the call side higher; leave the put side to decay while SPX remains above VWAP.
- **Bear outcome - SPX below 7,400, then testing 7,375:** Close or roll the put side before the short strike comes into play. The call side can be harvested at 50-70% profit.
- **Neutral outcome - SPX between 7,400 and 7,500:** Hold the iron condor for theta decay. Take profits at 50% of max profit or flatten before late-day gamma accelerates.

## Data and disclaimer

- **Data sources:** FMP quote for `^GSPC`, `SPY`, `^VIX`; FMP historical-price-full for SPX, SPY, and VIX; FMP economic calendar; FMP earnings calendar.
- **Data gaps:** FMP did not provide exact ES Globex high-low or live option-chain deltas in this run. Confirm futures range and option deltas on the broker platform before execution.
- **Disclaimer:** This report is for educational and research purposes only. It is not investment advice or a recommendation to buy or sell securities, options, or futures.
