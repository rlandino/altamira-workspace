# Jane Street Pre-Market Edge — 2026-03-12

## Market assessment

S&P 500 proxy is opening near **6,775.80** with a **-5.68 pt (-0.08%)** gap versus prior close (6,781.48). Current read: **Uncertain / data-dependent** — Small gap into a busy 8:30 ET data window tends to whipsaw before directional conviction appears.

Implied volatility is represented by **VIX 25.36**. VIX is higher vs yesterday close (25.36 vs 24.23, +1.13, +4.66%). Premiums are richer; prefer defined-risk short premium after headline risk clears.

Prior session closed in the middle of the range, signaling balanced positioning and a neutral overnight carry into the open. This supports a **Neutral lean** heading into today's macro tape. Calendar load is **Moderate**, so entry timing matters more than directional conviction pre-open.

## Overnight futures movement

- Reference level: **SPX 6,775.80** (proxy from FMP quote; exact ES/Globex from broker).
- Gap vs prior close: **-5.68 pts (-0.08%)**.
- View: **Uncertain / data-dependent** — Small gap into a busy 8:30 ET data window tends to whipsaw before directional conviction appears.

## Pre-market IV levels

- Current VIX: **25.36**.
- Prior VIX close: **24.23** (+1.13, +4.66%).
- Read: VIX is higher vs yesterday close (25.36 vs 24.23, +1.13, +4.66%). Premiums are richer; prefer defined-risk short premium after headline risk clears.

## Economic calendar impact

- Calendar intensity: **Moderate**.
- **8:30 AM ET** | **Housing Starts (Jan)** (High) — can widen opening range, especially in rates-sensitive sectors.
- **8:30 AM ET** | **Housing Starts MoM (Jan)** (Medium) — can widen opening range, especially in rates-sensitive sectors.
- **8:30 AM ET** | **Initial Jobless Claims (Mar/07)** (Medium) — can widen opening range, especially in rates-sensitive sectors.
- **11:00 AM ET** | **Fed Bowman Speech** (Medium) — Fed speaker risk can cause intraday vol repricing.
- **1:00 PM ET** | **Atlanta Fed GDPNow (Q1)** (Medium) — Fed speaker risk can cause intraday vol repricing.
- **8:30 AM ET** | **Continuing Jobless Claims (Feb/28)** (Low) — can widen opening range, especially in rates-sensitive sectors.
- Recommendation: Wait for the first scheduled data dump to clear, then sell premium with defined risk.

## Earnings exposure

- **ADBE** (AMC) — market cap ~**$112.4B**.
- **WPM** (AMC) — market cap ~**$67.5B**.
- **DG** (BMO) — market cap ~**$31.9B**.
- **ULTA** (AMC) — market cap ~**$29.3B**.
- **LEN** (AMC) — market cap ~**$24.9B**.
- **FUTU** (BMO) — market cap ~**$21.3B**.
- **LI** (BMO) — market cap ~**$18.5B**.
- **DKS** (BMO) — market cap ~**$15.8B**.
- Market-moving potential: **Medium (single-name impact can be material in QQQ/Nasdaq futures; broad SPX impact likely contained at the open).**

## Globex range and expected range

- Globex high/low: **Use broker futures feed for exact overnight ES range** (not provided by this FMP endpoint).
- Prior cash-session proxy range: **67.6 SPX pts** (from SPY prior day range scaled to SPX).
- VIX-based 1-day expected move: **±108.2 pts (±1.60%)**.
- Implied daily envelope: **6,667.6 to 6,884.0**.

## Opening gap strategy

- **Primary plan:** stay flat through the first macro print/opening auction, then engage between **9:45–10:00 AM ET** when spreads normalize.
- **Execution rule:** if first 15-minute range > 0.60% of SPX, reduce size and widen wings.

## IV crush opportunity

- Yes — yesterday had high-impact macro releases (including inflation data), so residual event premium can still compress intraday if realized vol settles.
- Implication: prioritize premium-selling structures only after event risk is released and direction is less noisy.

## Previous day's close analysis

- SPY prior OHLC: **O 677.58 / H 680.08 / L 673.34 / C 676.33**.
- Close location: **44.4%** of session range from low to high.
- Read: market closed in the middle of the range, signaling balanced positioning and a neutral overnight carry into the open.
- Lean for today: **Neutral lean**.

## Support and resistance

### Support
- **S1: 6750** — prior-session low proxy / first downside reaction zone.
- **S2: 6720** — half expected-move down from current level.
- **S3: 6670** — full expected-move downside boundary.

### Resistance
- **R1: 6820** — prior-session high proxy / first supply zone.
- **R2: 6830** — half expected-move upside extension.
- **R3: 6885** — full expected-move upside boundary.

## Pre-market trade plan

- **Strategy:** SPX **0DTE Iron Condor** (defined-risk short premium).
- **Strikes (model-based, no live chain deltas):** Sell 6675P / Buy 6625P and Sell 6890C / Buy 6940C.
- **Target delta band:** short strikes approximating 0.10–0.15 delta equivalent using expected-move placement.
- **Expiration:** 2026-03-12 (0DTE).
- **Entry time:** **9:45–10:00 AM ET**, after opening imbalance and scheduled macro release volatility normalize.
- **Position size:** **1–2% account risk**, max 1x normal size until post-open trend quality is confirmed.
- **Risk controls:** hard stop if SPX breaches short strike with momentum; take 40–60% max profit by early afternoon.

## Scenario playbook

- **Bull outcome (SPX > 6820):** cut/close call spread at predefined loss threshold; keep or monetize put spread if premium decays >50%.
- **Bear outcome (SPX < 6750):** close or roll put spread defensively; harvest call spread gains early to reduce net risk.
- **Neutral outcome (SPX between 6750 and 6820):** hold core position, take profits at 50% of collected credit, avoid late-day gamma risk.

## Data and disclaimer

- **Data sources:** FMP `quote` (^GSPC, SPY, ^VIX), `historical-price-full` (SPY, ^VIX), `economic_calendar`, `earning_calendar`.
- **Globex note:** true overnight futures high/low should come from broker/futures platform; this report uses cash proxies where needed.
- **Disclaimer:** For educational/research purposes only. Not investment advice. Options involve substantial risk and are not suitable for all investors.
