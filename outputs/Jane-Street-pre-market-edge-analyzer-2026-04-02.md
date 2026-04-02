# Jane Street Pre-Market Edge — 2026-04-02

## Market assessment
Overnight index proxy shows **SPX 6,575.32** versus prior close **6,528.52**, a **+46.80 pt (+0.72%)** gap. Baseline view is **Fade** into the open because opening gaps above 0.5% in elevated vix often mean-revert after the first liquidity sweep, especially with 8:30 et macro data risk.

Implied volatility is materially higher pre-open: **VIX 27.60** versus yesterday close **24.54** (**+3.06, +12.47%**). Richer premium supports defined-risk short-vol structures, but elevated gamma requires smaller sizing and disciplined adjustments.

Previous session closed **in the middle** of its SPY range (O/H/L/C: 653.90/658.52/653.00/655.24), giving a **Neutral lean (balanced auction into the close).** Today’s macro tape is **heavy** with clustered U.S. releases around 8:30 ET and Fed speakers later, so timing is critical.

## Overnight futures movement
- **Gap:** +46.80 pts (+0.72%) using ^GSPC quote proxy.
- **View:** **Fade** — Opening gaps above 0.5% in elevated VIX often mean-revert after the first liquidity sweep, especially with 8:30 ET macro data risk.
- **Note:** Exact ES/SPX futures print and true overnight levels should be confirmed from broker/futures platform.

## Pre-market IV levels
- **Current VIX:** 27.60
- **Yesterday VIX close:** 24.54
- **Change:** +3.06 (+12.47%)
- **Read-through:** Options are pricing materially higher volatility vs yesterday; favor **wider short strikes, defined wings, and reduced size**.

## Economic calendar impact
- **8:30 AM ET — Initial Jobless Claims (Mar/28)** (Impact: High). Labor releases can expand opening range roughly 1.2x-1.5x vs quiet days.
- **8:30 AM ET — Continuing Jobless Claims (Mar/21)** (Impact: High). Labor releases can expand opening range roughly 1.2x-1.5x vs quiet days.
- **8:30 AM ET — Goods Trade Balance Adv (Feb)** (Impact: Medium). Secondary macro release; can amplify move when aligned with risk sentiment.
- **8:30 AM ET — Goods Trade Balance (Feb)** (Impact: High). Secondary macro release; can amplify move when aligned with risk sentiment.
- **11:00 AM ET — Fed Logan Speech** (Impact: Medium). Fed communication can reprice rates quickly; avoid oversized short gamma into remarks.
- **12:45 PM ET — Fed Bowman Speech** (Impact: Medium). Fed communication can reprice rates quickly; avoid oversized short gamma into remarks.


- **Calendar load:** **Heavy**
- **Recommendation:** Reduce size and avoid entering short premium until after the 8:30 ET data clears.

## Earnings exposure
- **AYI** (BMO) — Market cap $8.8B
- **LNN** (BMO) — Market cap $1.2B
- **ANGO** (BMO) — Market cap $492.1M
- **TERN** (BMO) — Market cap $4.8B

- **Market-moving potential:** **Low** (mostly single-name risk; limited broad-index beta unless a surprise in larger reporters).

## Globex range and expected range
- **Globex range:** Not provided by FMP. Confirm overnight ES high/low from broker.
- **Proxy range (prior SPY session):** 5.52 points (658.52 - 653.00); SPX-equivalent proxy roughly ~55 points.
- **VIX-implied 1-day move:** **±114.3 SPX points** (~±1.74%).
- **Implied envelope from spot:** ~**6,461 to 6,690**.

## Opening gap strategy
- Gap is **significant** (>0.5%), so base case is **wait for 9:35-9:50 ET** and trade only after initial imbalance forms.
- If first 15 minutes fails above resistance, bias to **fade extension** with defined-risk call side.
- If breadth and price accept above resistance after data, avoid fading strength too early.

## IV crush opportunity
- **No classic event-IV crush setup** from yesterday’s close alone, but VIX is elevated and intraday decay can still be monetized if realized vol compresses after 8:30 ET.
- Theta implication: sell premium **outside expected move** with strict risk caps; avoid naked short gamma.

## Previous day's close analysis
- SPY O/H/L/C: **653.90/658.52/653.00/655.24**
- Close location: **in the middle** of range (40.6% from low to high).
- Lean: **Neutral lean (balanced auction into the close).**

## Support and resistance
### Support
- **S1: 6555** — prior session SPX low proxy from index quote.
- **S2: 6529** — prior SPX close anchor.
- **S3: 6461** — lower edge of VIX-implied 1-day range.

### Resistance
- **R1: 6610** — prior session SPX high proxy from index quote.
- **R2: 6650** — round-number supply zone.
- **R3: 6690** — upper edge of VIX-implied 1-day range.

## Pre-market trade plan
- **Strategy:** **0DTE SPX Iron Condor (defined risk)**
- **Structure (indicative, no live chain deltas):**
  - Sell **6435P** / Buy **6415P**
  - Sell **6710C** / Buy **6730C**
- **Expiration:** **Today (2026-04-02)**
- **Entry time:** **9:35-9:50 AM ET**, after open auction and 8:30 ET data reaction are visible.
- **Target sizing:** **1.0x normal size, max 1.5%-2.0% account risk** due to elevated VIX.
- **Risk management:** Take profits at ~50% max credit; cut/adjust if short strike is threatened or spread value reaches ~2x entry credit.

## Scenario playbook
- **Bull outcome (SPX > R1 6610):**
  - Reduce or close call spread side on momentum confirmation.
  - Keep put spread if safely OTM; target 50%+ total condor decay.
- **Bear outcome (SPX < S1 6555):**
  - De-risk put spread quickly; close threatened side before delta accelerates.
  - Optionally keep/harvest call side if price rejects lower levels.
- **Neutral outcome (inside 6555-6610):**
  - Hold for theta decay; take profits in 40%-60% band into midday volatility contraction.

## Data and disclaimer
- **Data sources:** FMP `/quote` (^GSPC, SPY, ^VIX), `/historical-price-full/SPY`, `/historical-price-full/^VIX`, `/economic_calendar`, `/earning_calendar`.
- **Overnight/Globex note:** Exact ES overnight high/low was not available via FMP; confirm from broker/futures terminal.
- **Disclaimer:** For educational and research purposes only. Not investment advice. Options involve significant risk.
