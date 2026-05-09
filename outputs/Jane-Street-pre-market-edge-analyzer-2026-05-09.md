# Jane Street Pre-Market Edge — 2026-05-09

## Market assessment

This automation fired on **Saturday**, so the first-order read is **market closed / no 0DTE SPX trade today**. FMP quote data is useful as a prior-session reference, but it should not be treated as a live ES Globex or SPX options chain feed.

Using the available FMP proxy, SPX is around **7,398.93** versus prior close **7,398.92**, implying a gap proxy of **0.0 points (+0.00%)**. View: **No-trade / market closed** - Saturday run: cash equities and SPX 0DTE options are closed; treat quote gaps as stale until Sunday Globex/Monday pre-market.

VIX 17.19 is flat vs prior close 17.19 (+0.00%). No same-day IV crush trade is available while the market is closed. The prior session closed **near the highs**, giving a **Bearish fade risk / momentum confirmation needed** read for the next tradable open. Calendar/earnings headline risk today is **Market closed / weekend**.

## Overnight futures movement

- **Current SPX/ES proxy:** 7,398.93 from FMP ^GSPC/SPY quote; exact SPX/ES should come from broker/futures platform.
- **Prior SPX close proxy:** 7,398.92 (historical data date: 2026-05-08).
- **Gap:** 0.0 points (+0.00%).
- **Hold/Fade view:** **No-trade / market closed** - Saturday run: cash equities and SPX 0DTE options are closed; treat quote gaps as stale until Sunday Globex/Monday pre-market.

## Pre-market IV levels

- VIX 17.19 is flat vs prior close 17.19 (+0.00%).
- **20-session VIX reference:** 18.11.
- **Theta implication:** No same-day IV crush trade is available while the market is closed.

## Economic calendar impact

- No FMP economic calendar items returned for today.

- **Calendar weight:** Market closed / weekend.
- **Trading recommendation:** Recommendation: no new SPX theta positions today; carry this as preparation for the next market session.

## Earnings exposure

- No major US index-heavy earnings returned for today. FMP returned only non-US/small-index names, which are not material for same-day SPX theta planning.

- **Index impact read:** Weekend earnings exposure is low for same-day index trading; monitor Monday pre-market updates for new single-name risk.

## Globex range and expected range

- **Globex range:** From broker/futures platform. FMP does not provide ES overnight high/low in this command.
- **Prior session range proxy:** 35.2 SPX points from SPY high/low scaled to SPX (2026-05-08).
- **VIX-based 1-day expected move:** +/- 80.1 points (~+/- 1.08%).

## Opening gap strategy

- **Strategy:** Stay flat. The correct opening strategy is to wait for the next tradable regular session and refresh futures/chain data.
- **Execution note:** If running this before the next open, refresh true ES Globex high/low, breadth, and live SPX option deltas before placing any trade.

## IV crush opportunity

- **Read:** No. Weekend run and no same-day event premium to monetize in SPX today.
- **Trade implication:** Do not assume IV crush without a live catalyst clearing and stable realized range; prefer defined-risk structures over naked short gamma.

## Previous day's close analysis

- **Prior session OHLC proxy (SPY scaled to SPX):** Open 7,371.9, High 7,403.5, Low 7,368.3, Close 7,398.9.
- **Close location:** Market closed near the highs.
- **Lean:** Bearish fade risk / momentum confirmation needed.

## Support and resistance

### Support
- **Support 1: 7,399** - Prior session close (2026-05-08); nearest pivot if reclaimed/failed.
- **Support 2: 7,368** - Prior session low (2026-05-08); first downside reference.
- **Support 3: 7,319** - VIX-based 1-day expected-move lower bound.

### Resistance
- **Resistance 1: 7,400** - Nearest upside round-number magnet in 25-point increments.
- **Resistance 2: 7,404** - Prior session high (2026-05-08); first upside rejection/acceptance level.
- **Resistance 3: 7,479** - VIX-based 1-day expected-move upper bound.

## Pre-market trade plan

- **Strategy:** No trade - market closed
- **Strikes:** No SPX 0DTE strikes today. Re-run before the next open; use expected-move wings only after live chain deltas confirm 0.10-0.15 delta.
- **Expiration:** None today; next liquid session/weekly expiration only after market reopens.
- **Entry time:** Do not enter today. Next session: reassess 9:35-9:50 AM ET after the open settles.
- **Position size:** 0% account risk today; resume at 1x normal size only if calendar remains light and VIX is stable.
- **Risk rule:** Do not sell premium into unavailable or stale data; confirm live chain deltas, bid/ask quality, and scheduled event risk before entry.

## Scenario playbook

- **Bull outcome:** SPX accepts above Resistance 1 (7,400). Action: do not chase short calls; if in an iron condor next session, reduce/close call side at risk and let put side decay only if breadth remains orderly.
- **Bear outcome:** SPX loses Support 1 (7,399). Action: close/roll threatened put side; harvest call-side profit and avoid adding downside short gamma into trend acceleration.
- **Neutral outcome:** Price remains between Support 1 and Resistance 1. Action: hold defined-risk spreads to 50% max profit or close before late-day gamma; no adjustment while price remains inside range.

## Data and disclaimer

- **Data sources:** FMP quote, historical price, economic calendar, and earnings calendar. No user-supplied futures or VIX. Globex high/low requires broker/futures platform. Saturday automation run: quotes may represent the latest regular-session close, not active pre-market trading.
- **Disclaimer:** This briefing is for educational and research purposes only and is not investment advice. Options involve risk, including the possible loss of principal. Verify all prices, Greeks, liquidity, and event timing with your broker before trading.
