# Jane Street Pre-Market Edge — 2026-04-20

## Market Assessment

S&P 500 is opening essentially flat versus the prior close (7126.06 vs 7126.05), so there is no meaningful overnight gap edge to fade or chase. The tape is coming in balanced, which generally favors disciplined premium selling after the first 10-20 minutes confirms opening direction.

Implied volatility is firmer: VIX is 19.41 versus 17.48 on the previous close (+1.93, +11.0%). That keeps options premiums attractive for theta harvesting, but also signals a market that can still produce sharp intraday swings.

Calendar risk looks light for U.S. index traders today (no CPI/Fed/NFP-style catalyst on the FMP U.S. feed). Earnings flow is active in single names, but there are no mega-cap index heavyweights on today’s list, so broad index shock risk appears limited.

## Overnight Futures Movement

- **Current proxy level (SPX):** 7126.06
- **Prior session close (SPX):** 7126.05
- **Gap:** +0.01 points (+0.00%)
- **View:** **Uncertain/Neutral (no clear hold-or-fade edge)** — gap is too small to create a statistically strong open fade/continuation setup.

## Pre-Market IV Levels

- **Current VIX:** 19.41
- **Prior VIX close:** 17.48
- **Change:** +1.93 (+11.04%)
- **Read-through:** Options are pricing higher volatility than yesterday, improving premium levels for sellers but requiring wider strikes and stricter risk controls.

## Economic Calendar Impact

### U.S. events on today’s feed

- **3:30 PM ET:** 3-Month Bill Auction (Low impact)
- **3:30 PM ET:** 6-Month Bill Auction (Low impact)

### Impact assessment

- **Calendar regime:** **Light**
- No high-impact macro release (Fed decision, CPI, NFP, Retail Sales, PMI) appears on today’s U.S. calendar feed.
- **Recommendation:** Normal-to-slightly-conservative theta deployment is acceptable; no need to sit out for macro event risk.

## Earnings Exposure

### Notable U.S.-listed reports (single-name risk, limited index weight)

- **STLD** (AMC)
- **CLF** (BMO)
- **ALK** (AMC)
- **AGNC** (AMC)
- **ZION** (AMC)
- **WTFC** (AMC)

### Market-moving assessment

- **Single-name IV risk:** Medium
- **Index-level impact:** Low (no major mega-cap tech/bank weights reporting)

## Globex Range and Expected Range

- **Globex overnight high/low:** Not provided by FMP (use broker futures platform for exact ES range)
- **Proxy overnight context:** Prior SPX cash range was **72.97 points** (7147.52 high, 7074.55 low)
- **VIX-based expected 1-day move:** **+/-87.13 points** (~+/-1.22%)
  - Expected envelope from current SPX 7126: **7039 to 7213**

## Opening Gap Strategy

- **Gap condition:** No significant opening gap.
- **Plan:** Wait for first 15-minute opening range to print, then run balanced theta (iron condor bias) outside expected-move band.
- **Execution bias:** Avoid immediate market-open fills; prioritize 9:40-9:55 AM ET entry window.

## IV Crush Opportunity

- **Classic post-event IV crush setup:** **No** (yesterday was not a major macro event day).
- **Practical implication:** VIX is still elevated vs prior close, so premium selling remains favorable, but treat this as rich-vol carry rather than event-crush decay.

## Previous Day Close Analysis

Using prior SPX session (Open 7074.55, High 7147.52, Low 7074.55, Close 7126.05):

- Market closed in the **upper portion** of the day’s range (near highs).
- **Lean:** Mildly bearish/mean-reversion at the margin (upper-range closes often invite early two-way trade), but not a strong directional signal.

## Support and Resistance

### Support

1. **7100** — round-number magnet just below spot.
2. **7074.55** — prior day low/open reference.
3. **7040** — lower bound of VIX-implied daily move.

### Resistance

1. **7147.52** — prior day high.
2. **7175** — round-number extension zone above prior high.
3. **7213** — upper bound of VIX-implied daily move.

## Pre-Market Trade Plan

- **Strategy:** SPX 0DTE Iron Condor (defined risk, outside expected move)
- **Structure (target ~0.10-0.15 delta shorts):**
  - Sell **7030 Put**
  - Buy **7000 Put**
  - Sell **7240 Call**
  - Buy **7270 Call**
- **Expiration:** Today (0DTE)
- **Entry window:** 9:40-9:55 AM ET after opening range stabilization
- **Risk sizing:** 1x normal to 0.75x normal; cap at **~2% of account** max risk due elevated VIX
- **Management rule:** Take 50-60% of max profit; reduce challenged side if spot breaches first resistance/support pivot with momentum.

## Scenario Playbook

- **Bull outcome (sustained > 7147.52):**
  - Manage/trim call spread early if premium doubles or spot acceptance continues above R1.
  - Optionally close put spread at 70-80% capture to de-risk gamma.

- **Bear outcome (sustained < 7074.55):**
  - Defend put spread: reduce or roll down/out if support fails on momentum.
  - Harvest call-side profits early to offset defensive adjustment cost.

- **Neutral outcome (price stays between 7100 and 7147):**
  - Hold structure and target 50-60% max profit by early afternoon.
  - Avoid late-day gamma exposure if premium already sufficiently captured.

## Data and Disclaimer

- **Data sources:** Financial Modeling Prep (FMP) `quote` (^GSPC, SPY, ^VIX), `historical-price-full` (^GSPC, ^VIX), `economic_calendar`, `earning_calendar`.
- **Overnight/Globex note:** Exact ES overnight high/low should be taken from broker/futures platform; this report used cash-session proxies where needed.
- **Disclaimer:** This material is for educational and research purposes only and is not investment advice. Options involve significant risk and may not be suitable for all investors.
