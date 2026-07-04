# Jane Street Pre-Market Edge - 2026-07-04

## Market assessment

Market status: **Closed - weekend**. With no user-supplied ES/SPX futures level, this run uses FMP ^GSPC/SPY quotes as the proxy and treats exact overnight Globex high/low as broker-platform data. Current SPX proxy is **7,483.24** versus the latest completed session close of **7,483.24** on **2026-07-02**.

Gap read: **0.00 pts (+0.00%)**. View: **No actionable gap / no trade** - US cash index options are closed today (closed - weekend); FMP quote is stale/last-session data.

VIX is stale/flat at 15.81 versus the last recorded close 16.15; no fresh pre-market IV signal. Prior close read: **Neutral** - market closed in the middle of the session range, so opening range should matter more than prior-session momentum. Today's calendar tone is **Closed** - closed-market day; do not initiate 0DTE index theta trades.

## Overnight futures movement

- SPX/ES proxy: **7,483.24** (FMP quote; exact ES from broker for live futures).
- Prior SPX close: **7,483.24** (2026-07-02).
- Gap: **0.00 points (+0.00%)**.
- Hold/fade view: **No actionable gap / no trade** - US cash index options are closed today (closed - weekend); FMP quote is stale/last-session data.

## Pre-market IV levels

- VIX: **15.81**.
- Last recorded VIX close: **16.15**.
- VIX 5-session average: **17.05**; 20-session average: **18.10**.
- Read-through: VIX is stale/flat at 15.81 versus the last recorded close 16.15; no fresh pre-market IV signal.

## Economic calendar impact

- No major US economic releases found in FMP for today.

- Calendar weight: **Closed**.
- Recommendation: **Closed-market day; do not initiate 0DTE index theta trades.**

## Earnings exposure

- No major index-heavy earnings reports found in FMP for today.

- Index impact: **Low** unless a mega-cap report appears outside the FMP filtered list or futures react to unscheduled news.

## Globex range and expected range

- Globex high/low: **From broker/futures platform**; FMP equity endpoints do not provide true ES overnight range.
- Prior-session SPX range proxy: **113.20 points** (high 7,540.75, low 7,427.55).
- VIX-implied 1-day expected move: **+/-74.53 points** (~+/-1.00%).
- Expected range from proxy price: **7,408.71 to 7,557.77**.

## Opening gap strategy

Stay flat. A weekend/holiday closure removes today's theta opportunity and makes stale quotes unusable for execution.

## IV crush opportunity

No same-day IV crush trade today. Post-holiday reopening may carry gap risk; sell premium only after spreads and realized opening range stabilize.

## Previous day's close analysis

- Prior session (2026-07-02) open/high/low/close: **7,495.14 / 7,540.75 / 7,427.55 / 7,483.24**.
- Close location: **49% of the day's range**.
- Lean: **Neutral; opening range should matter more than prior-session momentum.** - Market closed in the middle of the session range.

## Support and resistance

### Support
- Support 1: 7,483.24 - Prior close / settlement magnet.
- Support 2: 7,450.00 - Nearby round-number support.
- Support 3: 7,427.55 - Prior-session low (2026-07-02).

### Resistance
- Resistance 1: 7,483.24 - Prior close / settlement magnet.
- Resistance 2: 7,500.00 - Nearby round-number resistance.
- Resistance 3: 7,540.75 - Prior-session high (2026-07-02).

## Pre-market trade plan

- Strategy: **No trade - market closed. Prepare a next-session 0DTE iron-condor framework only after live ES/option-chain confirmation.**
- Structure: Hypothetical SPX iron condor framework if market is open/liquid: sell **7410P / buy 7385P** and sell **7560C / buy 7585C**.
- Expiration: **0DTE on the next open session**; do not enter on a closed-market day.
- Entry time: **No entry today; reassess 9:35-9:50 AM ET on the next open session.**
- Position size: **0% at risk today; next session 1/2 normal size until post-holiday liquidity normalizes.**
- Risk rule: Close at 50% max profit, stop at 2x credit received, or exit immediately on a clean short-strike breach with momentum.

## Scenario playbook

- Bull outcome: SPX reclaims **7,500.00** and holds above it. Action: avoid adding call-side risk; close/roll tested call spread and let put side decay only if breadth confirms.
- Bear outcome: SPX loses **7,450.00**. Action: close/roll tested put spread; harvest call side at 50%-75% profit if premium collapses.
- Neutral outcome: SPX stays between **7,450.00** and **7,500.00**. Action: hold defined-risk theta to 50% max profit, then flatten; no adjustment if price remains centered.

## Data and disclaimer

- Data sources: FMP quote (^GSPC, SPY, ^VIX), FMP historical-price-full (^GSPC, SPY, ^VIX), FMP economic_calendar, FMP earning_calendar.
- Globex/overnight high-low: not available from FMP equity endpoints; use broker/futures platform for exact ES range before any trade.
- Disclaimer: This is for educational and research purposes only and is not investment advice. Options involve substantial risk and may not be suitable for all investors.
