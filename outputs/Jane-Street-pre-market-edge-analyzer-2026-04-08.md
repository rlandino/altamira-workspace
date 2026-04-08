# Jane Street Pre-Market Edge — 2026-04-08

## Market assessment

SPX proxy pricing is slightly green pre-open: **6616.85 vs 6611.83 prior close** (**+5.02 pts, +0.08%**). The opening gap is small, which usually favors early two-way trade rather than a clean trend day. With no user-supplied ES print, this uses cash index/ETF proxy (SPX/ES exact overnight tape should come from broker futures feed).

Implied volatility is materially lower this morning: **VIX 20.32 vs 25.78 prior close** (about **-21%**). That is a meaningful vol compression regime shift and supports a premium-selling bias, but intraday event timing matters.

The calendar is event-sensitive later in the US session (Fed communication cluster), so the preferred setup is **defined-risk theta entered after opening noise** and managed before the afternoon event window.

## Overnight futures movement

- **Gap (SPX proxy):** +5.02 points (**+0.08%**) vs prior close.
- **View:** **Uncertain to slight fade**.
- **Why:** Gap size is small (not a strong continuation signal), and Fed headlines later today can interrupt morning trend persistence.

## Pre-market IV levels

- **Current VIX:** 20.32  
- **Yesterday VIX close:** 25.78  
- **Change:** -5.46 points (~-21.2%)
- **Read-through:** Options are pricing **less** near-term volatility than yesterday; favors short-premium structures, but keep wings defined and reduce exposure into Fed minutes/speeches.

## Economic calendar impact

Key US events from today’s calendar (timestamps from API; ET shown approximately):

- **~10:30 ET**: EIA crude/gasoline inventories (usually sector-specific, can affect index tape if energy move is large).
- **~13:05 ET**: Fed Daly speech (headline-vol risk).
- **~14:00 ET**: **FOMC Minutes (High impact)** — often expands afternoon range and reprices rates/vol quickly.
- **~14:35 ET**: Fed Waller speech (follow-through headline risk).

**Calendar load:** **Moderate to Heavy (afternoon-heavy).**  
**Recommendation:** Run normal-to-conservative morning theta sizing, then trim or flatten risk before the 14:00 ET event window.

## Earnings exposure

Largest US names reporting today (from FMP calendar + quote market caps):

- **DAL (BMO)** — ~\$42.9B market cap
- **STZ (AMC)** — ~\$26.8B
- **RPM (BMO)** — ~\$12.4B
- **APLD (AMC)** — ~\$7.0B
- **PSMT (AMC)** — ~\$4.7B

**Market-moving potential:** **Low to Medium** for broad index (more single-name/sector impact than mega-cap index shock).

## Globex range and expected range

- **Globex overnight high/low:** Not available from FMP cash-index endpoints.  
  Use broker/futures platform for true ES overnight range.
- **Proxy reference range (prior SPY session):**
  - High: 659.61
  - Low: 651.06
  - Range: **8.55 SPY points** (~85.8 SPX-equivalent points)

**VIX-based 1-day expected move (SPX):**

- Formula: Price x (VIX/100) / 16
- 6616.85 x (20.32/100) / 16 ≈ **84.0 points**
- **Expected range today:** **~6533 to ~6701** (±1.27%)

## Opening gap strategy

- **Plan:** Wait for first 10-15 minutes, then run **defined-risk 0DTE theta** if price remains inside opening range and realized vol stays orderly.
- **Bias:** Small opening gap favors mean reversion/chop more than momentum chase.
- **Risk caveat:** Do not carry oversized short gamma into 14:00 ET FOMC minutes.

## IV crush opportunity

- Yesterday was not a classic scheduled CPI/NFP/Fed decision day, but VIX is already sharply lower this morning.
- **Opportunity:** Yes, **morning premium sale is favorable** given vol compression.
- **Execution note:** Capture theta early; reduce exposure ahead of afternoon Fed catalysts where IV can re-expand intraday.

## Previous day's close analysis

Using prior SPY OHLC (Open 656.65, High 659.61, Low 651.06, Close 659.22):

- Close location in range: (659.22 - 651.06) / (659.61 - 651.06) ≈ **95%** of day range.
- **Read:** Market closed near highs (risk of early fade/rotation), but not a standalone bearish signal unless opening breadth weakens.
- **Lean:** **Neutral to mildly mean-reversion** at the open.

## Support and resistance

### Support

1. **6612** — Prior SPX close pivot (gap-fill decision zone).
2. **6591** — Prior SPY open converted to SPX proxy zone.
3. **6533** — VIX-implied 1-day downside bound / near prior-session low cluster.

### Resistance

1. **6621** — Prior SPY high converted to SPX proxy zone.
2. **6650** — Round-number psychological barrier.
3. **6701** — VIX-implied 1-day upside bound.

## Pre-market trade plan

- **Strategy:** **SPX 0DTE iron condor (defined risk)**.
- **Structure (expected-move / ~0.10-0.15 delta proxy):**
  - Sell **6540 put**
  - Buy **6510 put**
  - Sell **6695 call**
  - Buy **6725 call**
- **Expiration:** **Today (0DTE)**.
- **Entry time:** **09:35-09:50 ET**, after opening range forms.
- **Position size:** **2% account risk max** (drop to ~1.5% if realized vol rises before noon).
- **Management rule:** Target 40-50% max profit; start reducing risk before **13:45 ET** ahead of Fed minutes window.

## Scenario playbook

- **Bull outcome (sustained > 6621):**
  - Cut/hedge call spread risk early.
  - Keep put side if trend is orderly.
  - Avoid adding new short calls into breakout strength.

- **Bear outcome (sustained < 6612):**
  - Reduce put-spread risk if downside momentum accelerates.
  - Consider closing call side to realize gains and finance adjustment.
  - If 6591 breaks with breadth weakness, de-risk aggressively.

- **Neutral outcome (price oscillates 6612-6621 and stays inside expected range):**
  - Hold for theta decay.
  - Take profits at 40-50% of credit.
  - Exit before late-day Fed headline window if gamma risk is elevated.

## Data and disclaimer

**Data sources used**

- FMP Quote: `^GSPC`, `SPY`, `^VIX`
- FMP Historical: `historical-price-full/SPY`, `historical-price-full/^VIX`
- FMP Economic Calendar: today’s events
- FMP Earnings Calendar: today’s reporters
- Globex/overnight ES range: requires broker/futures platform feed (not provided by these FMP endpoints)

**Disclaimer**

This report is for educational and research purposes only and is not investment advice, a solicitation, or a recommendation to buy/sell any security or derivative. Options involve substantial risk, including potential loss of principal.
