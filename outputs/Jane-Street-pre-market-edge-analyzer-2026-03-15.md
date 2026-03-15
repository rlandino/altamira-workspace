# Jane Street Pre-Market Edge — 2026-03-15

## Market assessment

Overnight index indications are effectively flat into the Monday open, with SPX proxy at **6632.19** versus prior cash close **6632.20** (gap near zero). With no meaningful gap edge pre-open, this is a structure-driven tape rather than a directional gap regime.

Implied volatility is still elevated in absolute terms (**VIX 27.19**) but slightly below the prior close (**27.29**, -0.10 / -0.37%). Premium remains rich versus the 50-day VIX average (~19.00), which favors defined-risk theta structures over outright long-vol unless price starts trending outside expected move levels.

Calendar risk is light for US macro today (Sunday), while global macro attention is on early Monday Asia data (China industrial production and retail sales). Earnings exposure is low for US index beta, so single-name idiosyncratic risk appears limited for SPX at the open.

## Overnight futures movement

- **Current level used:** SPX quote proxy (no user-supplied ES/SPX futures level)
- **Prior SPX close:** 6632.20
- **Current SPX proxy:** 6632.19
- **Gap:** **-0.01 points (-0.00%)**
- **View:** **Uncertain / slight fade bias** — gap is too small to provide directional edge; favor opening-range confirmation before sizing.

## Pre-market IV levels

- **Current VIX:** 27.19
- **Yesterday VIX close:** 27.29
- **Change:** -0.10 (-0.37%)
- **Read-through:** IV is marginally lower vs yesterday close, but still elevated in regime terms (well above medium-term average), supporting premium-selling setups with defined wings.

## Economic calendar impact

- **US high-impact events today:** None scheduled (Sunday session).
- **Global events on deck (early Monday ET):**
  - 02:00 ET (CN): Industrial Production YoY (Jan) — **High impact**
  - 02:00 ET (CN): Retail Sales YoY (Jan) — **High impact**
  - 02:00 ET (CN): Fixed Asset Investment (YTD) — Medium impact
- **Historical range behavior:** Large China growth surprises can shift global risk sentiment and widen US index opening range.
- **Calendar classification:** **Light US / Moderate global spillover**
- **Recommendation:** Trade normal size only after first 15-20 minutes unless futures react materially to Asia data.

## Earnings exposure

- **Today's earnings tape:** 7 reported names in calendar feed, predominantly non-US symbols.
- **Mega-cap US/index-heavy names reporting today:** None detected.
- **Market-moving potential for SPX:** **Low**
- **Implication:** Single-name IV spikes likely isolated; limited direct index earnings shock risk.

## Globex range and expected range

- **Globex high/low:** From broker/futures platform (not provided by FMP in this run).
- **Proxy reference range (prior SPX cash session):** 6733.30 to 6623.92 (**109.38 points**).
- **VIX-based expected 1-day move:**  
  - Formula: Price x (VIX/100) / 16  
  - 6632.19 x 0.2719 / 16 = **~112.72 points**
  - **Expected range:** **6519.47 to 6744.91** (~+/-1.70%)

## Opening gap strategy

- **Gap regime:** Flat/no meaningful dislocation.
- **Plan:** **Wait for first 15-minute range**, then deploy defined-risk theta if price remains between prior day low/high and breadth is not one-way.
- **If opening drive exceeds +/-0.5% in first 20 minutes:** delay entry and reduce size.

## IV crush opportunity

- **Yesterday high-IV event?** No major US macro/Fed event.
- **Opportunity:** **Moderate**, because IV remains elevated versus baseline even without a fresh catalyst.
- **Theta implication:** Favor iron condor or single-side credit spread; avoid naked structures.

## Previous day's close analysis

Using SPY prior session OHLC:
- **Open:** 669.27
- **High:** 672.34
- **Low:** 661.36
- **Close:** 662.29
- **Range:** 10.98

Close was in the **bottom ~8.5% of the day range** (near lows), which gives a mild **bullish mean-reversion lean** early, but only if price reclaims opening range highs.

## Support and resistance

### Support
- **S1: 6624** — Prior day SPX low (6623.92), first structural defense.
- **S2: 6600** — Round-number magnet and intraday liquidity pivot.
- **S3: 6520** — VIX-implied expected move lower bound (~6519.5).

### Resistance
- **R1: 6675** — Prior close/open zone and likely first supply area.
- **R2: 6733** — Prior day SPX high (6733.30), key breakout test.
- **R3: 6745** — VIX-implied expected move upper bound (~6744.9).

## Pre-market trade plan

- **Strategy:** 0DTE SPX iron condor (defined risk), contingent on stable opening range.
- **Expiration:** **2026-03-16** (next cash session, 0DTE at entry).
- **Target structure (expected-move / ~0.10-0.15 delta zone):**
  - Sell **6520 put**
  - Buy **6500 put**
  - Sell **6745 call**
  - Buy **6765 call**
- **Entry window:** 9:35-9:50 AM ET after opening volatility normalizes.
- **Risk sizing:** Max **1.5-2.0%** account risk; half-size if opening drive is one-directional.
- **Management:** Take 50-60% max credit; hard reduce if short strike breached or spread value reaches ~2x entry credit.

## Scenario playbook

- **Bull outcome (SPX > 6675 and holding):**
  - Call side becomes active risk; trim/close call spread early if premium doubles.
  - Keep put side to target if trend persists and realized vol compresses.

- **Bear outcome (SPX < 6624):**
  - Put side at risk; cut/roll put spread before full strike breach.
  - Optionally realize gains on call side to offset defense cost.

- **Neutral outcome (SPX oscillates between 6624 and 6675):**
  - Hold structure for theta decay.
  - Take profits at 50-60% of max credit; avoid late-day gamma exposure if range starts to expand.

## Data and disclaimer

- **Data sources:** Financial Modeling Prep (FMP) `quote` (^GSPC, SPY, ^VIX), `historical-price-full` (SPY, ^GSPC, ^VIX), `economic_calendar`, `earning_calendar`.
- **Globex note:** True overnight ES high/low should be taken from broker/futures platform; this report used cash-session proxies where needed.

**Disclaimer:** This briefing is for educational and research purposes only, not investment advice. Options involve substantial risk, including potential loss of principal. Financial calculations are model-based estimates and can differ from live market execution.
