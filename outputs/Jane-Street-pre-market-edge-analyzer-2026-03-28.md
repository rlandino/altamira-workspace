# Jane Street Pre-Market Edge — 2026-03-28

## Market Assessment
Overnight proxy pricing points to **SPX around 6,369** (derived from SPY, with exact ES/Globex levels to be confirmed from broker feed). Versus prior SPY-implied SPX close (6,369), the gap is **+0.0 points (+0.00%)** with a **Hold / drift** read.

Implied volatility is **higher vs yesterday**: VIX is **31.05** versus prior close **27.44** (+3.61, +13.16%). This keeps short-premium attractive, but with wider wings and reduced size while VIX is elevated.

Prior session closed **near lows** of its range (SPY O/H/L/C: 642.50/642.66/633.11/634.09). Calendar risk today looks **light**, and earnings-driven index spillover risk is **medium**.

## Overnight Futures Movement (Gap + Hold/Fade View)
- **Gap (SPX proxy):** +0.0 pts (+0.00%) vs prior close
- **View:** **Hold / drift**
- **Reason:** Small gap often resolves into trend continuation if breadth confirms.
- **Note:** Exact ES/Globex overnight range should be read from broker futures platform.

## Pre-Market IV Levels
- **Current VIX:** 31.05
- **Yesterday close (proxy):** 27.44
- **Change:** +3.61 (+13.16%)
- **Read-through:** Options are pricing higher short-term volatility vs yesterday; theta selling is still viable but should favor defined risk and conservative size.

## Economic Calendar Impact
- **Today's events:**
  - 2026-03-28 10:00:00 | EU | EcoFin Meeting | Impact: Low
  - 2026-03-28 09:00:00 | EU | ECB Cipollone Speech | Impact: Low

- **High-impact read:** 0 event(s) match high-impact macro keywords.
- **Calendar verdict:** **Light**
- **Recommendation:** Normal theta sizing; still avoid oversized risk through headline windows.

## Earnings Exposure
- **Major/US-like tickers on today's calendar (sample):** CTRYF (BMO), SZDEF (TIME N/A), AVIJF (TIME N/A), DOLHF (TIME N/A), CFEIY (TIME N/A), BEIJF (TIME N/A), GNENY (TIME N/A)
- **Market-moving potential:** **Medium**
- **Read-through:** Single-name IV can jump even when index impact stays contained; keep index premium trades outside obvious event windows.

## Globex Range and Expected Range
- **Globex range:** Not provided by FMP cash-index endpoints. Pull exact ES overnight high/low from broker.
- **Proxy range (yesterday SPY):** 9.55 points.
- **VIX-implied 1-day SPX move:** **±123.6 points (~±1.94%)**.

## Opening Gap Strategy
- **Opening posture:** Neutral-to-follow posture after opening range.
- **Execution rule:** Wait for first 5-15 minute range. If price reclaims/loses opening VWAP with breadth confirmation, align spread direction with that break.
- **Risk control:** No oversized entries in first 3 candles when VIX > 25.

## IV Crush Opportunity
- **Assessment:** **Moderate opportunity**.
- **Why:** Elevated VIX and post-gap uncertainty can keep opening premiums rich; short defined-risk structures can harvest decay once direction stabilizes.
- **Constraint:** If fresh macro headline risk appears, implied vol can re-expand intraday.

## Previous Day's Close Analysis
- **SPY O/H/L/C:** 642.50 / 642.66 / 633.11 / 634.09
- **Close location:** **near lows** (10.3% up from day low)
- **Lean:** **bullish mean-reversion, but fragile if risk-off persists** for today's open.

## Support and Resistance (SPX Proxy)
### Support
1. **S1: 6369** — Prior close / balance pivot.
2. **S2: 6245** — ~1x implied move lower.
3. **S3: 6175** — Round-number/extension support.

### Resistance
1. **R1: 6369** — Prior close reclaim pivot.
2. **R2: 6492** — ~1x implied move upper.
3. **R3: 6550** — Round-number/extension resistance.

## Pre-Market Trade Plan
- **Strategy:** **0DTE SPX iron condor (defined risk)**
- **Structure (model strikes):**
  - Short Put: **6265**
  - Long Put: **6240**
  - Short Call: **6475**
  - Long Call: **6500**
- **Expiration:** Today (0DTE)
- **Entry time:** **09:35-09:50 ET (after first 5-15 min range sets)**
- **Sizing:** **1x normal to 0.75x normal** (target risk 2-3% max account loss equivalent for total structure)
- **Management:** Take profits at ~40-50% max credit; cut/adjust if short strike touched or spread value expands to ~2x entry credit.

## Scenario Playbook
- **Bull outcome (price > R1 with breadth confirmation):**
  - De-risk call spread first if challenged; keep put side for decay.
  - Consider converting to put credit spread if trend persists.
- **Bear outcome (price < S1 with risk-off breadth):**
  - De-risk put spread first if challenged; keep call side for decay.
  - Consider converting to call credit spread on failed bounce.
- **Neutral outcome (inside S1-R1 and realized vol compresses):**
  - Hold condor for theta decay; take 40-50% profits before late-day gamma acceleration.

## Data and Disclaimer
- **Data sources:** FMP `/quote` (^GSPC, SPY, ^VIX), `/historical-price-full` (SPY, ^VIX), `/economic_calendar`, `/earning_calendar`.
- **Overnight/Globex note:** Exact ES futures overnight high/low should come from broker/futures platform; not provided in FMP cash-index endpoint response.
- **Disclaimer:** Educational and research use only. Not investment advice. Options involve substantial risk and may not be suitable for all investors.
