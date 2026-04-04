# Jane Street Pre-Market Edge — 2026-04-04

## Market assessment

Overnight index proxy indicates SPX around **6,583** (from SPY proxy; exact ES/SPX futures should come from broker feed). Gap vs prior SPX proxy close is **+5.9 pts (+0.09%)**. Initial read: **Hold** — Smaller gap with no major catalyst usually has better continuation odds.

Implied volatility check: VIX 23.87 vs prior close 24.54 (-0.67, -2.7%). Options pricing is **lower** vs yesterday, favoring more selective premium selling (credits likely thinner).

Prior session context (most recent trading day 2026-04-02): SPY closed **near highs** of range (O/H/L/C = 646.42/658.20/645.11/655.83), giving a **bearish-to-neutral** lean into today. Calendar load is **Light** with no obvious top-tier macro catalyst in today's feed.

## Overnight futures movement

- Estimated current SPX level: **6,582.7** (SPY-derived proxy)
- Prior close proxy: **6,576.8**
- **Gap: +5.9 pts (+0.09%)**
- View: **Hold** — Smaller gap with no major catalyst usually has better continuation odds.

## Pre-market IV levels

- VIX 23.87 vs prior close 24.54 (-0.67, -2.7%).
- Theta implication: Lower IV means tighter credits; avoid over-sizing and require clean levels.

## Economic calendar impact

- No obvious top-tier US macro events identified in FMP feed for today.
- Summary: **Light** day. Recommendation: Standard opening process; confirm first 15-minute auction before entry.

## Earnings exposure

- **002285.SZ**  — None
- **300363.SZ**  — None
- **603214.SS**  — None
- **603214.SS**  — None
- **600350.SS**  — None
- Market-moving potential: **Medium**. Single-name IV likely elevated; index spillover possible.

## Globex range and expected range

- Globex range: **Use broker/futures platform for exact overnight high/low** (FMP equity feed does not provide full ES Globex range).
- Prior day SPY range proxy: **13.09** (~131.4 SPX points).
- VIX-based 1-day expected move: **±99.0 SPX points (~±1.50%)**.

## Opening gap strategy

- Small/no gap. **Normal theta playbook after opening auction stabilizes.**

## IV crush opportunity

- No clear prior high-IV catalyst in feed; IV crush setup is weaker. Focus on theta decay inside expected range.

## Previous day's close analysis

- SPY O/H/L/C: **646.42 / 658.20 / 645.11 / 655.83**
- Close location: **near highs**
- Lean: **bearish-to-neutral** — use this as bias, not a standalone signal.

## Support and resistance

### Support
- **S1: 6577** — prior close magnet / opening auction pivot
- **S2: 6478** — expected-move lower bound
- **S3: 6428** — 1.5x expected-move lower extension

### Resistance
- **R1: 6577** — prior close pivot / nearby round number
- **R2: 6676** — expected-move upper bound
- **R3: 6725** — 1.5x expected-move upper extension

## Pre-market trade plan

- **Strategy:** 0DTE SPX iron condor (defined risk)
- **Strikes (model-based, no live chain deltas):** Sell 6480P / Buy 6470P and Sell 6675C / Buy 6685C
- **Expiration:** Today (0DTE)
- **Entry time:** 9:35-9:50 AM ET after opening range forms
- **Position size:** 1x to 0.75x normal (keep max risk ~2-3% of account)
- **Risk rule:** Hard stop if spot breaches short strike or spread value reaches ~2x collected credit

## Scenario playbook

- **Bull outcome (above R1 6577):** Close call spread at 1.5x loss threshold or roll up/out if event risk has passed; keep put side to target 50% max profit.
- **Bear outcome (below S1 6577):** Defend/close put spread early; take profits on call side and reduce net gamma exposure.
- **Neutral outcome (inside S1-R1):** Hold for theta decay and take profits at ~50% of max credit before last trading hour.

## Data and disclaimer

- **Data sources:** FMP `/quote` (^GSPC, SPY, ^VIX), `/historical-price-full` (SPY, ^VIX), `/economic_calendar`, `/earning_calendar`.
- **Globex note:** Exact overnight futures high/low should come from broker/futures platform.
- **Disclaimer:** For educational and research purposes only. Not investment advice.
