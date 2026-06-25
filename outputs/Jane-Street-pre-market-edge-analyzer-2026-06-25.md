# Jane Street Pre-Market Edge - 2026-06-25

## Market assessment

SPX/ES is marked at **7,358.22** versus prior SPX close **7,358.21**, implying a gap of **0.0 pts (+0.00%)**. **View: Uncertain** - Core PCE, jobless claims, durable goods, and a Fed speaker are on the tape, so the opening move can reprice quickly. FMP ^GSPC quote proxy; use SPX/ES from broker for exact futures.

VIX is **18.06** (FMP ^VIX quote.) versus prior close **18.63**, so pre-market IV is **lower**. The trading implication is: **less edge in naked premium; favor defined-risk spreads**.

Yesterday's SPY close was **near the lows** of the session range, creating a **Bearish** lean: sellers controlled the close, so early rallies may be faded unless macro data reverses sentiment. Today's calendar is **Heavy**; Trade smaller or wait until the high-impact print is absorbed; use wider strikes if selling premium.

## Overnight futures movement

- Current SPX/ES proxy: **7,358.22**.
- Prior SPX close: **7,358.21**.
- Gap: **0.0 pts (+0.00%)**.
- Hold/fade call: **Uncertain** - Core PCE, jobless claims, durable goods, and a Fed speaker are on the tape, so the opening move can reprice quickly.
- Note: FMP does not reliably expose true ES Globex high/low. Use broker futures data for exact overnight range and liquidity context.

## Pre-market IV levels

- Current VIX: **18.06**.
- Prior VIX close: **18.63**.
- Change: **-0.57 pts (-3.06%)**.
- Read-through: Options pricing is **lower** versus yesterday; less edge in naked premium; favor defined-risk spreads.

## Economic calendar impact

Today's calendar classification: **Heavy**.

- **08:30 ET** - Core PCE Price Index MoM (May) (High) [est 0.3, prev 0.2] - inflation prints often expand SPX range 1.5x-2.0x normal if surprise is material.
- **08:30 ET** - Core PCE Price Index YoY (May) (High) [est 3.4, prev 3.3] - inflation prints often expand SPX range 1.5x-2.0x normal if surprise is material.
- **08:30 ET** - PCE Price Index MoM (May) (High) [est 0.5, prev 0.4] - inflation prints often expand SPX range 1.5x-2.0x normal if surprise is material.
- **08:30 ET** - PCE Price Index YoY (May) (High) [est 4.1, prev 3.8] - inflation prints often expand SPX range 1.5x-2.0x normal if surprise is material.
- **08:30 ET** - Initial Jobless Claims (Jun/20) (High) [est 225, prev 226] - labor data can expand the opening range when it alters rate expectations.
- **08:30 ET** - Continuing Jobless Claims (Jun/13) (High) [est 1800, prev 1810] - labor data can expand the opening range when it alters rate expectations.
- **08:30 ET** - Durable Goods Orders MoM (May) (High) [est -4.5, prev 7.9] - growth-sensitive data can add trend risk after the open.
- **08:30 ET** - Durable Goods Orders Ex Defense MoM (May) (High) [est -3.9, prev 8.1] - growth-sensitive data can add trend risk after the open.
- **08:30 ET** - Durable Goods Orders Ex Transp MoM (May) (High) [est 0.6, prev 1.1] - growth-sensitive data can add trend risk after the open.
- **08:30 ET** - Jobless Claims 4-Week Average (Jun/20) (Medium) [est 226, prev 223.25] - confirms labor trend but is less likely to drive the first move by itself.
- **08:30 ET** - Chicago Fed National Activity Index (May) (Low) [est 0.12, prev 0.14] - regional activity indicator; lower direct index impact than PCE or claims.
- **08:45 ET** - Fed Bowman Speech (Medium) - monitor for rate-path comments; avoid adding premium if headlines hit during the opening range.

Recommendation: **Trade smaller or wait until the high-impact print is absorbed; use wider strikes if selling premium.**

## Earnings exposure

- No obvious mega-cap reports identified by FMP; notable tickers on the calendar include: ENTEF, SVRN, WLDSW, PRZO, QTEX, PRFX, FEDU.

Market-moving potential: **Low**. Single-name IV may be elevated around individual reports; index impact is most material if mega-cap tech, major banks, or high-index-weight names surprise.

## Globex range and expected range

- Globex range: **From broker/futures platform**. FMP does not provide a reliable ES overnight high/low in this workflow.
- Prior-day SPY range proxy (2026-06-24): **9.11 SPY pts**, approximately **91.4 SPX pts**.
- VIX-based 1-day expected move: **+/-83.7 SPX pts (~+/-1.14%)** using `price x VIX / sqrt(252)`.

## Opening gap strategy

Small gap: normal theta setup after opening range forms; avoid predicting direction before breadth confirms.

Execution note: do not sell premium into the first print. Let bid/ask spreads normalize, identify the opening range, then place defined-risk structures outside the expected move.

## IV crush opportunity

Possible after the high-impact event if VIX remains elevated into the open; wait for the post-event vol flush before selling premium.

If VIX remains bid but realized volatility stalls after the open, the best structure is a defined-risk iron condor or single-side credit spread. If price immediately trends through Support 1/Resistance 1, stand down until trend exhaustion.

## Previous day's close analysis

- Prior SPY session (2026-06-24): open **735.17**, high **739.95**, low **730.84**, close **733.24**.
- Close location: **near the lows** of the range.
- Lean: **Bearish** - sellers controlled the close, so early rallies may be faded unless macro data reverses sentiment.

## Support and resistance

### Support
- **Support 1: 7,360** - Prior SPX close / pivot.
- **Support 2: 7,335** - Prior day low.
- **Support 3: 7,300** - Nearby round-number support.

### Resistance
- **Resistance 1: 7,360** - Prior SPX close / pivot.
- **Resistance 2: 7,430** - Prior day high.
- **Resistance 3: 7,440** - VIX-implied 1-day expected move up.

## Pre-market trade plan

- Strategy: **0DTE iron condor after event absorption, or no trade if opening range expands through expected move**.
- Structure: **SPX 0DTE iron condor** using expected-move strikes; validate deltas on broker chain before entry.
- Approximate strikes: short put **7,260**, long put **7,250**, short call **7,455**, long call **7,465**.
- Delta target: short strikes near **0.10-0.15 delta** or outside the VIX-implied expected range.
- Expiration: **Today (0DTE)**; if spreads are too wide or IV is compressed, use the weekly Friday expiry with smaller size.
- Entry time: **9:45-10:05 AM ET, only after the first 15-30 minutes confirm liquidity and event direction**.
- Position size: **0.5x-0.75x normal size; cap defined-risk exposure near 1%-2% of account due to event risk**.
- Risk controls: close at 50% max profit, stop if short strike is breached with momentum, or if spread value reaches roughly 2x collected credit.

## Scenario playbook

- **Bull outcome:** SPX holds above Resistance 1 (**7,360**). Action: avoid adding call-side risk; close or roll threatened call spread, keep put side only if price stays above VWAP and breadth confirms.
- **Bear outcome:** SPX loses Support 1 (**7,360**). Action: close/roll threatened put spread, harvest call-side profit, and do not re-sell puts until a lower high or stabilization forms.
- **Neutral outcome:** SPX remains between Support 1 and Resistance 1. Action: hold defined-risk premium sale to 50% max profit or time-based exit; avoid adjustments while inside the expected range.

## Data and disclaimer

Data sources: FMP quote (`^GSPC`, `SPY`, `^VIX`), FMP historical-price-full (`SPY`, `^GSPC`, `^VIX`), FMP economic calendar, and FMP earnings calendar. Globex/overnight high-low should be verified on a broker or futures platform.

Disclaimer: This report is for educational and research purposes only and is not investment advice. Options trading involves substantial risk; validate all market data, option prices, deltas, liquidity, and account-level risk before placing any trade.
