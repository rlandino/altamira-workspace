# Jane Street Pre-Market Edge — 2026-03-31

## Market assessment

S&P proxy pricing is effectively flat versus the prior close (SPX proxy ~6343.7), so there is no meaningful overnight gap to fade or chase at the open. The prior regular session closed in the lower quartile of its range, which keeps a slight risk-off bias unless buyers reclaim yesterday's high early.

Pre-market volatility has softened from yesterday (VIX 28.67 vs 30.61 prior close), indicating some overnight IV compression. Even so, implied volatility remains elevated versus medium-term baselines (50-day VIX ~20.84), so premium is still rich enough for defined-risk theta structures.

Today's U.S. macro tape has a 10:00 ET cluster (JOLTS and Consumer Confidence) plus Fed speakers later in the day, while earnings are lighter on mega-cap index movers. Base case: range trading early with event-driven expansion risk around the 10:00 ET data window.

## Overnight futures movement

- **Current proxy level:** SPX proxy 6343.72 (from SPY-to-SPX ratio scaling; exact ES/Globex levels should be confirmed from broker feed).
- **Gap vs prior close:** **0.0 pts (0.00%)**.
- **View:** **Uncertain-to-slight fade on early strength** — no true gap edge, and prior-day weak close argues against blindly chasing opening upticks.

## Pre-market IV levels

- **Current VIX:** 28.67  
- **Yesterday VIX close:** 30.61  
- **Change:** -1.94 points (**-6.34%**)
- **Read-through:** Options are pricing **less** volatility than yesterday's close, but IV is still elevated in absolute terms; this supports **defined-risk premium selling** rather than naked short gamma.

## Economic calendar impact

### Key U.S. events (ET)
- **8:55 ET:** Redbook YoY (low impact)
- **9:00 ET:** S&P/Case-Shiller Home Price Index (medium)
- **9:45 ET:** Chicago PMI (medium)
- **10:00 ET:** **JOLTS Job Openings (high)** and Consumer Confidence (medium)
- **12:00 ET:** Fed Goolsbee speech (medium)
- **1:10 ET:** Fed Bowman speech (medium)

### Impact assessment
- **Calendar load:** **Moderate**
- **Historical behavior:** Labor/consumer prints can push index intraday range toward ~1.3x to 1.7x typical morning expansion; Fed speakers can trigger secondary vol bursts.
- **Recommendation:** Use wider short strikes than normal and avoid max sizing before the 10:00 ET macro cluster.

## Earnings exposure

Notable U.S.-listed earnings today:

- **NKE (AMC)** — largest U.S. market cap on today's list; can influence consumer discretionary sentiment.
- **MKC (BMO)** — defensive staple read-through, limited index impact.
- **SNX (BMO)** — enterprise/IT demand signal, modest broad-market effect.
- **FDS (BMO)** — financial data/professional services bellwether, limited index beta.
- **PVH (AMC)** — apparel/consumer discretionary, single-name vol risk.

**Market-moving potential:** **Low to Medium** for index-level action (no mega-cap tech/bank concentration today).

## Globex range and expected range

- **Globex overnight high/low:** Not provided by FMP; confirm exact ES overnight range from broker/futures platform.
- **Proxy for context:** Prior SPY session range = 640.37 - 629.28 = **11.09 SPY points** (~111 SPX-proxy points).
- **VIX-based 1-day expected move:** **+/-113.7 SPX points** (~+/-1.79%) from 6343.7.
- **Implied day range:** approximately **6230 to 6457**.

## Opening gap strategy

- **Primary plan:** **Normal theta deployment after open stabilization** (9:35-9:50 ET), not at the bell.
- **Why:** Flat gap plus elevated-but-cooling IV favors collecting decay after the first volatility impulse is priced.
- **Caution:** Keep room for 10:00 ET macro expansion; do not over-concentrate near yesterday's high before data.

## IV crush opportunity

- **Assessment:** **Yes, partial IV crush underway**
- VIX has already compressed overnight, suggesting some event premium came out, but volatility remains high enough to monetize via defined-risk short premium.
- **Theta implication:** Favor iron condor / balanced credit spreads with disciplined exits over directional longs.

## Previous day's close analysis

Using prior SPY OHLC (O 640.11, H 640.37, L 629.28, C 631.97):

- Close location in range: ~24% from the low (bottom quartile).
- **Read:** Market closed near lows, implying a **mild bearish-to-neutral** lean unless price reclaims prior-day high zone.

## Support and resistance

### Support
1. **6317** - Prior day low (SPY 629.28 scaled to SPX proxy), first downside reaction zone.
2. **6260** - Round-number support below prior low; likely liquidity pocket on acceleration.
3. **6230** - VIX-implied expected-move lower bound.

### Resistance
1. **6404** - Prior day high (SPY 640.37 scaled), key reclaim level for bullish continuation.
2. **6450** - Round-number resistance near upper vol pocket.
3. **6457** - VIX-implied expected-move upper bound.

## Pre-market trade plan

- **Strategy:** **0DTE SPX iron condor (defined risk)**
- **Structure (model strikes, no live chain deltas in this run):**
  - Sell **6210 put**
  - Buy **6190 put**
  - Sell **6470 call**
  - Buy **6490 call**
- **Rationale:** Shorts are placed outside the projected 1-day implied range with 20-point wings to cap tail risk.
- **Expiration:** **Today (0DTE)**
- **Entry window:** **9:35-9:50 ET**, preferably after first directional push and before 10:00 ET macro if spreads are still fairly priced.
- **Risk size:** **1-2% account risk** (reduced from normal due to elevated volatility and scheduled data).

## Scenario playbook

- **Bull outcome (sustained move above 6404):**
  - Reduce call-side risk early (buy back short call spread if breached/near breached).
  - Keep put side to decay if downside momentum is absent.

- **Bear outcome (break below 6317 with follow-through):**
  - Defend/close put side quickly; consider keeping call spread if trend is orderly.
  - Do not average down short puts into momentum selloff.

- **Neutral outcome (price remains between 6317 and 6404):**
  - Hold position for theta decay.
  - Target 40-60% max credit capture by midday; avoid holding full size late day if gamma risk rises.

## Data and disclaimer

- **Data sources:** Financial Modeling Prep (FMP) `/quote` for ^GSPC, SPY, ^VIX; `/historical-price-full/SPY`; `/historical-price-full/^VIX`; `/economic_calendar`; `/earning_calendar`.
- **Overnight/Globex note:** Exact ES overnight high/low not provided by these endpoints; broker futures feed should be used for precise Globex range.
- **Disclaimer:** This report is for educational and research purposes only and is not investment advice. Options involve substantial risk; verify live prices, liquidity, and risk limits before placing trades.
