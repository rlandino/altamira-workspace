# Jane Street Pre-Market Edge — 2026-03-22

## Market assessment

S&P proxy is 6,506.48 with VIX at 26.78. Using last cash-session prices (no live ES feed supplied), implied gap vs prior session close is -0.01 pts (-0.00%). Base view: Hold / Drift.

Volatility is higher versus the prior close (+11.31% vs previous session), so premiums are richer; favor defined-risk premium selling with wider wings. Prior SPY close was in the middle-third of its daily range, which gives a neutral lean (two-way tape likely).

Macro calendar is light and earnings spillover risk is low; focus execution quality and only sell premium outside validated support/resistance.

## Overnight futures movement

- Gap: -0.01 pts (-0.00%).
- View: **Hold / Drift** — small implied gap with no U.S. high-impact macro event favors range trade rather than immediate reversal.
- Note: ES/Globex live high/low not provided by FMP quote feed; broker futures ladder is needed for exact overnight range.

## Pre-market IV levels

- Current VIX: **26.78**
- Prior close reference: **24.06**
- VIX vs prior close: **+11.31%** (higher IV)
- Implication: premiums are richer; favor defined-risk premium selling with wider wings.

## Economic calendar impact

- Today's calendar load: **Light**
- 2026-03-23 02:30:00 ET — KR 5-Year KTB Auction (impact: Low)
- Recommendation: Normal process; use first 10–15 minutes for direction confirmation before entry.

## Earnings exposure

- Market-moving potential: **Low**
- HLM.JO (time N/A) — fiscal ending 2025-12-30
- SRHYY (time N/A) — fiscal ending 2025-12-30
- Read: No obvious S&P mega-cap earnings concentration in today's feed.

## Globex range and expected range

- Globex range: **From broker / futures platform** (FMP cash endpoints do not provide full overnight ES high/low).
- Prior session SPY range proxy: **11.97** points (high 656.69, low 644.72).
- Expected 1-day SPX move (VIX model): **±108.9 pts** (~±1.67%).

## Opening gap strategy

- No major U.S. catalyst at open; trade the first 10–15 minute range and sell outside expected move.
- If opening drive breaks and holds above resistance 1 / below support 1, avoid fading immediately; wait for failed retest before contrarian entries.

## IV crush opportunity

- Opportunity: **Partial**
- No discrete scheduled IV event is evident in the U.S. calendar today; however, elevated VIX can still mean intraday IV mean-reversion after the opening impulse.

## Previous day's close analysis

- Prior OHLC (SPY): O 656.51 / H 656.69 / L 644.72 / C 648.57
- Close location: **in the middle-third** of range.
- Lean: **neutral lean (two-way tape likely)**

## Support and resistance

### Supports
- **S1 6,470** — prior session low proxy
- **S2 6,400** — VIX expected-move lower bound
- **S3 6,350** — round-number extension below expected move

### Resistances
- **R1 6,590** — prior session high proxy
- **R2 6,615** — VIX expected-move upper bound
- **R3 6,665** — round-number extension above expected move

## Pre-market trade plan

- Strategy: **No trade today (U.S. cash market closed); queue conditional 0DTE SPX iron condor for next cash session.**
- Structure (conditional): Sell **6400/6375 put spread** + sell **6625/6650 call spread** (SPX).
- Expiration: **2026-03-23 (next cash session / 0DTE)**
- Entry window: **2026-03-23 09:40–10:00 AM ET (after opening range forms)**
- Position size: Use reduced size: 1–2% account risk (about 0.5x to 0.75x normal notional).
- Risk rule: hard stop if short strike is breached with trend + rising VIX; target 40–50% max profit capture.

## Scenario playbook

- **Bull outcome (above R1 6,590)**: reduce/close call spread at 1.5x credit risk trigger; keep put spread only if momentum is orderly.
- **Bear outcome (below S1 6,470)**: cut/roll put spread quickly, monetize call spread gains; avoid adding size into downside acceleration.
- **Neutral outcome (inside 6,470–6,590)**: hold for theta decay, take profits at 40–50% max credit, avoid overtrading midday chop.

## Data and disclaimer

- Data sources: FMP `/quote` (^GSPC, SPY, ^VIX), `/historical-price-full` (SPY, ^GSPC, ^VIX), `/economic_calendar`, `/earning_calendar`.
- Globex/overnight high-low requires broker futures feed for precision; cash-index proxy used where needed.
- Disclaimer: This report is for educational/research purposes only and is not investment advice. Options involve substantial risk, including loss of principal.
