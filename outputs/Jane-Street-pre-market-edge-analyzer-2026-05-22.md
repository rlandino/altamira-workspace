# Jane Street Pre-Market Edge - 2026-05-22

## Market assessment

SPX/ES futures were not supplied and FMP did not return a true pre-market/Globex high-low field, so this briefing uses the FMP cash-index/SPY quote as the proxy and notes that exact ES levels should be confirmed on the broker/futures platform. SPX is effectively flat versus the prior cash close: 7,445.72 versus 7,445.73, while FMP's quote change field shows +12.75 points (+0.17%) versus its vendor previous-close field.

VIX is 16.99, up 0.23 points from yesterday's 16.76 close but still below the 5-day average of 17.70 and 20-day average of 17.73. Options are not cheap enough to chase long premium, but the modest uptick argues for defined-risk premium selling only after the open confirms range behavior.

The calendar is moderate: the main US macro items are Leading Index at 10:00 AM ET and Fed Waller at 11:00 AM ET, with positioning data after the close. No mega-cap US earnings catalyst showed up in the FMP earnings scan, so index risk is more macro/rate-speech driven than single-name driven.

## Overnight futures movement

- **Proxy level:** SPX 7,445.72 / SPY 742.72 from FMP cash/ETF quote.
- **Prior SPX close:** 7,445.73 on 2026-05-21.
- **Gap:** ~0.0 points (~0.00%) versus the prior cash close using the FMP proxy.
- **View:** **Uncertain / neutral open.** The cash proxy says no meaningful gap; use live ES for the true overnight read. If ES opens inside yesterday's range, default to range-first theta. If ES is materially above 7,466 or below 7,389 at 9:30, wait for the first 15-30 minutes before selling premium.

## Pre-market IV levels

- **Current VIX:** 16.99.
- **Yesterday's VIX close:** 16.76.
- **Change:** +0.23 points (+1.37%).
- **Recent context:** VIX is below both the 5-day average (17.70) and 20-day average (17.73).
- **Implication:** Premium is adequate but not rich. Favor defined-risk structures and avoid oversizing short gamma before the 10:00-11:00 AM ET macro window.

## Economic calendar impact

| Time (ET) | Event | Impact | Trading implication |
|---:|---|---|---|
| 10:00 AM | US Leading Index MoM | Medium | Can widen the morning range if the release conflicts with the opening trend. Avoid entering too close to the print. |
| 11:00 AM | Fed Waller Speech | Medium | Rate-language risk; short-premium entries should have enough distance from current price and a hard stop. |
| 3:30 PM | CFTC S&P 500 / Nasdaq 100 positioning | Medium | Mostly after-hours positioning read; limited 0DTE impact before the close. |

**Calendar read:** Moderate. Trade after the open settles and avoid initiating fresh short premium directly ahead of the 10:00 AM ET data.

## Earnings exposure

- FMP returned 633 earnings-calendar entries for today, but no US mega-cap index-heavy report appeared in the large-cap screen.
- Larger non-US/OTC names flagged by the market-cap screen:
  - **CHYFF** - market cap ~$31.2B.
  - **KAP.L** - market cap ~$17.7B.
- **Market-moving potential:** Low for SPX. Single-name IV may be elevated in reporting names, but index impact should be limited unless a broader sector theme develops.

## Globex range and expected range

- **Globex range:** Not available from FMP. Confirm ES overnight high/low from the broker/futures platform.
- **Proxy range:** Prior SPX day high 7,465.96, low 7,389.48; range = 76.48 points.
- **VIX-based 1-day expected move:** 7,445.72 x 16.99% / sqrt(252) = **~+/-79.7 points** (~+/-1.07%).
- **Expected SPX range:** Roughly **7,366 to 7,525** if the day prices close to VIX-implied one-day movement.

## Opening gap strategy

- **Base case:** Small/no gap by the available proxy. Define the first 15-minute opening range, then sell defined-risk premium outside the expected-move bands.
- **If SPX opens above 7,466:** Do not immediately fade; wait for acceptance or rejection of prior high. A failed hold above 7,466 favors selling call spreads or an iron condor with the call side above 7,525.
- **If SPX opens below 7,389:** Treat as downside range expansion. Avoid selling puts until a reclaim of prior low or a volatility flush is visible.

## IV crush opportunity

Yesterday was not a major scheduled high-IV event in the fetched data, and VIX is only slightly above yesterday's close. There is no obvious event-vol crush setup at the open. The opportunity is standard intraday theta decay if SPX remains inside yesterday's range after the macro window.

## Previous day's close analysis

- **Prior session open/high/low/close:** 7,410.78 / 7,465.96 / 7,389.48 / 7,445.73.
- **Close location:** 73.5% of the prior day's range, closer to the highs.
- **Lean:** Mildly bullish momentum, but not a clean breakout because price did not close above the high. The best theta setup is a range hold between 7,389 and 7,466.

## Support and resistance

### Support

1. **7,445** - Prior close/current proxy pivot; losing this early weakens the flat-open thesis.
2. **7,389** - Prior day low; first real downside invalidation level for neutral theta.
3. **7,366** - VIX-implied lower expected-move boundary; put spreads should sit below or near this zone if selling 0DTE risk.

### Resistance

1. **7,466** - Prior day high; first upside breakout/rejection level.
2. **7,500** - Round-number magnet and likely dealer/psychological level.
3. **7,525** - VIX-implied upper expected-move boundary; call spreads should sit above or near this zone if selling 0DTE risk.

## Pre-market trade plan

- **Strategy:** 0DTE SPX iron condor, only after the first 15-minute range forms and price remains inside the prior day's range.
- **Expiration:** Today, 2026-05-22.
- **Structure:** Defined-risk, expected-move based strikes because live option-chain deltas were not available in the command data.
  - Sell **7,365 put**, buy **7,355 put**.
  - Sell **7,525 call**, buy **7,535 call**.
- **Entry window:** 9:40-10:00 AM ET if the open is stable; otherwise wait until after the 10:00 AM ET Leading Index release.
- **Position size:** 1x normal or less; cap max loss at ~1-2% of account due Fed-speaker risk at 11:00 AM ET.
- **Risk rules:** Take profits at 50% of max credit. Stop if premium expands to 2x entry credit, if SPX breaches a short strike, or if price accepts outside prior high/low for more than 15 minutes.
- **No-trade filter:** Skip the condor if ES/SPX opens with a true gap greater than 0.5% or if VIX spikes above 18.00 before entry.

## Scenario playbook

### Bull outcome

- **Trigger:** SPX accepts above **7,466** and holds above prior high.
- **Action:** Do not add short calls. If already in the condor, close or reduce the call side quickly and keep/harvest the put side. A replacement trade would be a put credit spread below 7,390 only after a pullback holds above 7,466.

### Bear outcome

- **Trigger:** SPX loses **7,445** and then trades below **7,389**.
- **Action:** Close or reduce the put side; do not roll into falling realized volatility. Keep the call side only if price stays below 7,445 and VIX is not accelerating. Consider a call credit spread above 7,500 after a failed reclaim of 7,389.

### Neutral outcome

- **Trigger:** SPX remains between **7,389 and 7,466** through late morning.
- **Action:** Hold the condor to 50% max profit, then close. Do not hold full size into the final hour unless both short strikes remain outside expected-move boundaries and premium has already decayed materially.

## Data and disclaimer

- **Data sources:** FMP quote for `^GSPC`, `SPY`, `^VIX`; FMP historical-price-full for SPY, `^GSPC`, and `^VIX`; FMP economic calendar; FMP earnings calendar.
- **Limitations:** FMP did not provide a true ES/SPX Globex high-low or explicit SPY pre-market field in the fetched quote. Confirm SPX/ES futures level, overnight high/low, and live option-chain deltas from the broker platform before execution.
- **Disclaimer:** This is for educational and research purposes only and is not investment advice. Options trading involves substantial risk, including the risk of loss greater than premium received.
