# Jane Street Pre-Market Edge — 2026-03-13

## Market assessment

Overnight pricing data from FMP does not expose a clean ES/Globex tape in this session, so SPY/^GSPC last available prints are used as the pre-open proxy. On that basis, the gap is **+0.0 pts (+0.00%)**, which suggests **Uncertain / likely range-open** into the cash open.

Implied volatility is **lower vs yesterday**: VIX 25.88 vs prior close 27.29 (-1.41, -5.17%). Lower IV reduces absolute premium but still supports defined-risk theta structures if entries are delayed until after event volatility settles.

Macro event density is **Heavy** today with clustered US releases around 8:30 AM ET and 10:00 AM ET. Earnings are mostly single-name/small-cap exposure, so index risk is driven more by macro than by mega-cap earnings shock.

## Overnight futures movement

- **Gap (proxy):** +0.0 SPX pts (+0.00%) versus prior close proxy 6672.62.
- **View:** **Uncertain / likely range-open** — Proxy pre-market level is close to prior close; momentum edge is weak pre-open.
- **Note:** True ES Globex high/low should be confirmed on broker futures feed for execution precision.

## Pre-market IV levels

- **Current VIX:** 25.88
- **Yesterday close (VIX):** 27.29
- **Change:** -1.41 (-5.17%)
- **Read:** Options are pricing **lower** volatility than yesterday; prefer disciplined entries and quick profit harvesting (35-50%) in short premium trades.

## Economic calendar impact

- **8:30 AM ET** — Core PCE Price Index MoM (High); inflation surprise can expand intraday range by ~1.3x to 1.8x.
- **8:30 AM ET** — Personal Income / Personal Spending (High); growth mix influences rates path and index breadth.
- **8:30 AM ET** — Durable Goods Orders (High) + ex-Transportation (Medium); can push cyclicals and opening skew.
- **8:30 AM ET** — GDP growth revision (High) / GDP price index (Medium); macro growth-inflation narrative reset risk.
- **10:00 AM ET** — Michigan Consumer Sentiment (High) and JOLTS Job Openings (High); second volatility impulse likely near mid-morning.
- **Calendar load:** Heavy.
- **Recommendation:** Keep strikes wider than normal pre-10:00 ET; avoid full-size premium selling before the major data cluster is absorbed.

## Earnings exposure

- No mega-cap US index heavyweights (AAPL/MSFT/NVDA/AMZN class) are concentrated on today's tape from the FMP calendar snapshot.
- Notable US-listed names with reports around today are mostly small/mid-cap and idiosyncratic.
- **Market-moving potential:** **Low to Medium** for the index; risk is primarily single-name IV, not broad index repricing.

## Globex range and expected range

- **Globex range (true):** Pull from broker/futures platform (not fully available via FMP quote endpoint).
- **Proxy (yesterday SPY range):** 5.78 SPY points (~57.9 SPX points).
- **1-day expected move (VIX model):** ±108.8 SPX points (±1.63%).

## Opening gap strategy

- Small/no-gap setup: **Wait first 10-15 minutes**, then run a balanced theta structure if price remains inside prior-day extremes.
- If 8:30 and 10:00 ET releases produce directional break + elevated realized vol, reduce size or skip first setup.

## IV crush opportunity

- Yesterday was **not** a single marquee IV event day (e.g., FOMC/CPI), but macro releases today can create temporary morning vol inflation.
- With VIX lower vs yesterday, edge is still in **defined-risk premium selling**, but avoid overreaching for credit.

## Previous day's close analysis

- Prior session (SPY): O 671.16 / H 671.65 / L 665.87 / C 666.06.
- Market closed **near the lows** of the day range.
- **Lean:** Bullish-to-neutral mean-reversion lean — A close near lows can set up relief bounces if macro data is not worse than feared.

## Support and resistance

### Support
- **S1: 6671** — prior day low proxy.
- **S2: 6650** — round-number magnet.
- **S3: 6564** — 1-day expected-move lower bound.

### Resistance
- **R1: 6729** — prior day high proxy.
- **R2: 6750** — round-number pivot above prior-day high.
- **R3: 6781** — 1-day expected-move upper bound.

## Pre-market trade plan

- **Strategy:** SPX 0DTE **iron condor** (defined risk), event-adjusted.
- **Strikes (model-based, no live chain deltas):** Sell 6560P / Buy 6540P and Sell 6780C / Buy 6800C.
- **Expiration:** 2026-03-13 (0DTE).
- **Entry time:** 10:05-10:20 AM ET (after 10:00 ET data + opening imbalance clears).
- **Position size:** 1-2% account risk (about 0.5x normal) due clustered macro releases.
- **Risk controls:** Hard stop at 2x credit received or short-strike breach on 5-minute close; take profits at 35-50% of max credit.

## Scenario playbook

- **Bull outcome (above R1 6729):** Reduce/close call spread early; keep put spread if momentum and breadth stay positive.
- **Bear outcome (below S1 6671):** Reduce/close put spread early; do not average down into downside acceleration.
- **Neutral outcome (between S1 6671 and R1 6729):** Hold condor toward 35-50% profit target, then flatten before late-day gamma risk expands.

## Data and disclaimer

- **Data sources:** FMP `/quote/^GSPC,SPY,^VIX`, `/historical-price-full/SPY`, `/historical-price-full/^VIX`, `/economic_calendar`, `/earning_calendar`; Globex specifics from broker/futures platform.
- **Disclaimer:** This briefing is for educational and research purposes only and is not investment advice. Options involve substantial risk, including potential loss of principal.
