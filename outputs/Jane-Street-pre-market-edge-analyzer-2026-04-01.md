# Jane Street Pre-Market Edge — 2026-04-01

## Market assessment
US index tape enters the session with elevated but easing implied volatility. Spot VIX is **24.31** vs **25.25** yesterday close (down **-0.94**), but still above 50-day realized complacency levels. That keeps premium-selling attractive, but only with defined risk and wider strike selection.

Overnight futures/Globex highs and lows were not provided and FMP quote fields did not return a live pre-market SPX/ES print in this run. Using cash-index proxy, the implied gap is effectively flat (**+0.0 pts, +0.00%**) versus prior close proxy; treat this as **uncertain open** until first 10-15 minutes of regular trading.

Macro event density is **heavy** for US rates/growth sensitivity today (ADP, Retail Sales complex, ISM Manufacturing PMI, energy inventory data, and Fed speakers). Expect two-way volatility and avoid oversized directional theta before the 10:00 ET macro cluster resolves.

## Overnight futures movement
- **Proxy gap (SPX):** +0.0 pts (+0.00%) vs prior close proxy.
- **View:** **Uncertain / likely early fade attempts**, not a clean hold signal.
- **Reason:** No confirmed ES pre-market trend data + dense US data calendar increases opening whipsaw probability.

## Pre-market IV levels
- **Current VIX:** 24.31
- **Yesterday VIX close:** 25.25
- **IV change:** -0.94 (-3.72%)
- **Read-through:** IV is lower than yesterday but still elevated in absolute terms; favorable for defined-risk short premium (iron condor / credit spreads) after initial event risk passes.

## Economic calendar impact
**Key US events (ET):**
- **8:15** — ADP Employment Change (**High**)  
  Typical effect: pre-open rate repricing; can expand first-hour range.
- **8:30** — Retail Sales MoM, Ex Autos, Ex Gas/Autos, YoY (**High**)  
  Typical effect: growth/inflation impulse; often increases opening drive/fade volatility.
- **9:05 / 9:13** — Fed Musalem / Fed Barr speeches (**Medium**)  
  Typical effect: rates-sensitive intraday repricing.
- **10:00** — ISM Manufacturing PMI (**High**)  
  Typical effect: can produce second volatility wave after open (often 1.3x-1.8x first-hour range).
- **10:30** — EIA Crude/Gasoline data (**Medium**)  
  Typical effect: sector-specific energy volatility; moderate index spillover.

**Calendar verdict:** **Heavy**  
**Recommendation:** Trade theta **after 10:05 ET** with wider wings and reduced size.

## Earnings exposure
Notable US-listed names reporting include **CAG, LW, CALM, UNF, ICLR, DRVN, TLRY, MSM** (mixed BMO/AMC timings in feed).

- **Market-moving potential for SPX:** **Low to Medium**
- No mega-cap index heavyweights (e.g., AAPL/MSFT/NVDA) dominate today’s list.
- Expect primarily **single-name IV** effects with limited broad-index beta shock unless guidance surprises cluster across sectors.

## Globex range and expected range
- **Globex range (true ES overnight high/low):** From broker/futures platform (not in FMP cash quote feed).
- **Proxy for context (prior SPY cash range):** 13.56 SPY points.
- **Expected 1-day SPX range (VIX model):** **±100 pts** (~±1.53%)

## Opening gap strategy
- **Playbook at open:** Stay flat through first 5-15 minutes unless tape is one-sided with breadth confirmation.
- If opening impulse extends into resistance quickly, prefer **fade-to-VWAP setups** over chasing.
- If price acceptance holds above first resistance after 10:00 ET data, shift to neutral/bullish structure by trimming call risk later.

## IV crush opportunity
- **IV crush setup:** **Moderate yes**
- Yesterday was not a singular Fed/CPI shock day, but implied vol remains high enough for theta harvesting.
- Best expression: **defined-risk 0DTE iron condor** with strikes outside expected move and active risk trimming.

## Previous day's close analysis
Using SPY prior session OHLC (**O 638.94 / H 651.54 / L 637.98 / C 650.34**):
- Close location in range: **91.2%** (near session highs)
- Read: **Mild bullish carryover bias**, but elevated odds of early mean reversion when macro data is dense.

## Support and resistance
### Support
1. **S1: 6500** — Round-number magnet / near prior close acceptance zone.
2. **S2: 6429** — VIX-implied 1-day downside move.
3. **S3: 6404** — Prior-day low proxy (SPY low translated to SPX scale).

### Resistance
1. **R1: 6541** — Prior-day high proxy.
2. **R2: 6628** — VIX-implied 1-day upside move.
3. **R3: 6700** — Round-number psychological and dealer gamma interaction zone.

## Pre-market trade plan
- **Strategy:** **SPX 0DTE iron condor (defined risk)**
- **Structure (today expiry):**
  - Sell **6400 put**
  - Buy **6380 put**
  - Sell **6650 call**
  - Buy **6670 call**
- **Entry window:** **10:05-10:25 AM ET** (after ISM release and first directional sweep)
- **Sizing:** **0.5x-0.75x normal size** (roughly 1-2% account risk)
- **Risk rules:**
  - Hard stop if spot breaches short strike with momentum confirmation.
  - Take profit at 40-55% of max credit; avoid holding full size into late-day event headlines.

## Scenario playbook
- **Bull outcome (sustained above R1):**
  - Reduce/close call spread risk early if premium decays >50%.
  - Keep put side if trend/breadth confirms upside continuation.

- **Bear outcome (sustained below S1):**
  - Reduce/close put spread risk; keep call side as residual theta.
  - Avoid rolling aggressively during high-velocity downside.

- **Neutral outcome (inside S1-R1 rotation):**
  - Hold structure for theta decay.
  - Target 40-55% max profit and flatten before late-day illiquidity.

## Data and disclaimer
- **Data sources:** FMP `quote` (^GSPC, SPY, ^VIX), `historical-price-full` (SPY, ^VIX), `economic_calendar`, `earning_calendar`.
- **Globex note:** True overnight ES high/low should be taken from broker/futures platform; cash proxies used where needed.

**Disclaimer:** For education and research only. Not investment advice. Options involve substantial risk and may not be suitable for all investors.
