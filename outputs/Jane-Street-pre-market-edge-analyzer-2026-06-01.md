# Jane Street Pre-Market Edge - 2026-06-01

## Market assessment

SPX cash closed Friday at 7,580.05 after trading a 35.83 point range. FMP's pre-market equity quote is still the prior-session cash print (2026-05-29 21:03 UTC), so the exact ES/SPX overnight gap should be confirmed from broker futures data before placing opening orders.

VIX is 15.78, +0.46 points (+3.0%) versus the prior close of 15.32. That is a small vol lift from Friday, but below the recent 5-day average of 16.21, which keeps the plan in defined-risk theta rather than aggressive premium selling.

Previous close location was in the middle of the range (46% of the daily range), giving a neutral two-way trade; let the first 15-30 minutes define direction. Calendar risk is heavy from FMP, and earnings exposure is low for broad-index risk.

## Overnight futures movement

- SPX/ES pre-market level: broker futures required for exact overnight print; FMP cash proxy uses prior close 7,580.05.
- Prior SPX close: 7,580.05.
- Implied gap from available FMP proxy: +0.00 points (+0.00%).
- View: **Uncertain** - FMP equity prints are prior-session before the cash open; use live ES/SPX from broker to confirm whether an overnight gap exists.

## Pre-market IV levels

- VIX is higher than the prior close (15.78 vs 15.32, +0.46 pts / +3.0%). Options are pricing more uncertainty than Friday, but absolute VIX is still normal.
- VIX source: FMP quote for `^VIX` (timestamp 2026-06-01 11:51 UTC).
- Theta implication: use defined-risk structures; sell outside expected move only after opening range liquidity forms.

## Economic calendar impact

Today's calendar: **Heavy**.

- 10:00 AM ET - Construction Spending MoM (Apr) (est 0.2, prev 0.6): Low/medium - monitor for surprise but usually secondary to price action.
- 10:00 AM ET - ISM Manufacturing Prices (May) (est 85.5, prev 84.6): Medium/high - often widens the morning range; use wider strikes or enter after release.
- 10:00 AM ET - ISM Manufacturing PMI (May) (est 53, prev 52.7): Medium/high - often widens the morning range; use wider strikes or enter after release.
- 10:00 AM ET - ISM Manufacturing New Orders (May) (est 54.3, prev 54.1): Medium/high - often widens the morning range; use wider strikes or enter after release.
- 10:00 AM ET - ISM Manufacturing Employment (May) (est 46.6, prev 46.4): Medium/high - often widens the morning range; use wider strikes or enter after release.
- 11:30 AM ET - 3-Month Bill Auction (prev 3.595): Medium - headline risk can hit rates and index vol intraday.
- 11:30 AM ET - 6-Month Bill Auction (prev 3.65): Medium - headline risk can hit rates and index vol intraday.

Recommendation: Stay flat through the first scheduled macro print, then sell premium only after the first 15-minute post-data range is established.

## Earnings exposure

Market-moving potential: **Low**.

- No obvious mega-cap index movers found in FMP earnings list. Smaller reporters include: NNX.V, GWRRF, BBM.CN, KER.WA, YORKF, OTC.V, CHELF, SRCRF.

Single-name IV may be active in reporters, but index theta should be driven more by macro/rates and opening breadth unless a mega-cap surprise emerges.

## Globex range and expected range

- Globex high/low: from broker/futures platform; FMP does not provide reliable ES overnight range here.
- Prior cash-session range proxy: 35.83 SPX points (7,563.55 low to 7,599.38 high).
- VIX-based 1-day expected move: +/-75.3 points (~+/-0.99%) from 7,580.05.

## Opening gap strategy

Stay flat through the first scheduled macro print, then sell premium only after the first 15-minute post-data range is established.

If live ES confirms a gap larger than 0.50%, avoid immediate 9:30 ET entries and reassess once the first 15-minute candle and NYSE breadth are visible.

## IV crush opportunity

- **Assessment:** Limited. VIX is normal/low, so the edge is theta plus range discipline rather than a major IV crush.
- Best expression: defined-risk 0DTE spreads/iron condor rather than naked short premium.

## Previous day's close analysis

- Prior open: 7,579.33.
- Prior high: 7,599.38.
- Prior low: 7,563.55.
- Prior close: 7,580.05.
- Read: market closed in the middle of the range; neutral two-way trade; let the first 15-30 minutes define direction.

## Support and resistance

### Support

- Support 1: **7,565** - Prior session low / nearest downside reference.
- Support 2: **7,540** - Half expected-move support / first downside magnet.
- Support 3: **7,500** - Full VIX one-day expected move lower.

### Resistance

- Resistance 1: **7,600** - Prior session high.
- Resistance 2: **7,620** - Half expected-move resistance.
- Resistance 3: **7,660** - Full VIX one-day expected move higher.

## Pre-market trade plan

- Strategy: **0DTE iron condor after the macro window clears, using wider expected-move strikes.**
- Structure: Sell SPX 2026-06-01 0DTE iron condor.
- Put side: sell **7,485P**, buy **7,460P**.
- Call side: sell **7,675C**, buy **7,700C**.
- Expiration: today, 2026-06-01.
- Entry time: 9:40-10:05 AM ET after the opening range settles; if a 10:00 AM macro release is active, enter only after that print is absorbed.
- Position size: Half to one-times normal risk; keep max loss <= 2% of account because macro risk is elevated.
- Profit/stop: take 50% of max profit; stop or cut tested side if SPX trades through the short strike or spread value reaches roughly 2x entry credit.

## Scenario playbook

- **Bull outcome:** SPX reclaims/respects Resistance 1 (7,600) with breadth expanding. Do not add call risk; close or roll the call side if the short call is threatened, and let the put side decay if price remains above VWAP.
- **Bear outcome:** SPX loses Support 1 (7,565) and fails a retest. Close the put side before gamma accelerates, keep/profit-take the call side, and consider re-centering only after a clean lower high.
- **Neutral outcome:** SPX stays between Support 1 and Resistance 1. Hold the condor toward 50% max profit, avoid adjustments, and flatten before late-day gamma if credit target is reached.

## Data and disclaimer

Data sources: FMP quote (`^GSPC`, `SPY`, `^VIX`), FMP historical-price-full (`SPY`, `^GSPC`, `^VIX`), FMP economic calendar, and FMP earnings calendar. Globex/overnight high-low was not available from FMP and should be confirmed from broker/futures data.

This report is for educational and research purposes only and is not investment advice. Options involve risk and may not be suitable for all investors.
