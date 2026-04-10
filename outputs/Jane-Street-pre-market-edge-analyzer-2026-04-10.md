# Jane Street Pre-Market Edge — 2026-04-10

## Market assessment

Overnight index pricing implies a **+0.0-point (+0.00%) gap** versus prior SPX-proxy close, giving an initial **Hold/extend bias** read. Small gap tends to follow through if opening breadth confirms direction.
Pre-market volatility is **lower**: VIX 19.33 vs prior close 19.49 (-0.16, -0.82%). This indicates premiums are thinner; require tighter risk controls and quicker profit-taking.
Prior session closed **at highs** of the day’s range, giving a **Bearish-to-neutral** lean into today. Macro calendar is **heavy** and earnings index impact is assessed as **Low**.

## Overnight futures movement

- Gap estimate: **+0.0 pts (+0.00%)**
- View: **Hold/extend bias**
- Rationale: Small gap tends to follow through if opening breadth confirms direction.

## Pre-market IV levels

- VIX now: **19.33**
- VIX prior close: **19.49**
- IV read: **lower** (-0.16, -0.82%)
- Theta implication: premiums are thinner; require tighter risk controls and quicker profit-taking.

## Economic calendar impact

- Calendar load: **Heavy**
- 2026-04-10 12:30:00  — **Core CPI (Mar)**
- 2026-04-10 12:30:00  — **CPI (Mar)**
- 2026-04-10 12:30:00  — **CPI MoM (Mar)**
- 2026-04-10 12:30:00  — **CPI s.a (Mar)**
- 2026-04-10 12:30:00  — **CPI YoY (Mar)**
- Historical impact guide: CPI/NFP/Fed-style events can expand index intraday range to ~1.5x–2.0x normal.
- Recommendation: Use wider strikes and avoid full size before first key release.

## Earnings exposure

- No mega-cap/major-index earnings in today list from feed snapshot.
- Market-moving potential: **Low** (primarily single-name idiosyncratic).

## Globex range and expected range

- Globex high/low: **Use broker futures platform** for true overnight range (not in this FMP endpoint).
- Proxy prior-day range (SPY): **7.39** points
- VIX-based SPX expected 1-day range: **+/-83.1 pts (~+/-1.22%)**

## Opening gap strategy

- Normal theta deployment after open; follow-through probability is higher on small gaps.

## IV crush opportunity

- Event-volatility premium may stay elevated around macro prints; post-event IV compression can favor defined-risk premium selling.

## Previous day's close analysis

- Prior day OHLC (SPY): O 674.84 / H 681.16 / L 673.77 / C 679.91
- Close location: **at highs**
- Lean: **Bearish-to-neutral** — close near highs can invite profit-taking unless momentum confirms.

## Support and resistance

### Support
- Support 1: **6824.7** — Prior close proxy (SPY close × SPX/SPY ratio)
- Support 2: **6783.1** — Half expected-move downside
- Support 3: **6741.6** — Full expected-move downside

### Resistance
- Resistance 1: **6825.0** — Round-number magnet
- Resistance 2: **6866.2** — Half expected-move upside
- Resistance 3: **6907.8** — Full expected-move upside

## Pre-market trade plan

- Strategy: **0DTE SPX iron condor (defined risk)**
- Strikes (model-based, no live chain deltas): **Sell 6760P / Buy 6740P / Sell 6885C / Buy 6905C**
- Expiration: **Today (0DTE)**
- Entry time: **After first high-impact release clears and 9:35–9:50 AM ET confirmation**
- Position size: **1x normal to 0.75x if macro event within first 2 hours; keep total risk ~2–3% max**
- Risk controls: Close at 50% max profit target; hard stop if spot breaches short strike or debit doubles collected credit.

## Scenario playbook

- **Bull outcome:** Break and hold above Resistance 1 (6825.0). Action: reduce/close call spread risk early; hold put side for theta decay.
- **Bear outcome:** Break and hold below Support 1 (6824.7). Action: reduce/close put spread risk; keep/harvest call side.
- **Neutral outcome:** Price oscillates between inner S/R levels. Action: hold structure toward 50% max profit, then de-risk before late-day gamma window.

## Data and disclaimer

- Sources: FMP `/quote` (^GSPC, SPY, ^VIX), `/historical-price-full` (SPY, ^VIX), `/economic_calendar`, `/earning_calendar`.
- Globex true overnight range requires broker/futures platform data.
- Disclaimer: For educational/research purposes only. Not investment advice. Options involve substantial risk and may not be suitable for all investors.
