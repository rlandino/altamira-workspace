# Jane Street Pre-Market Edge — 2026-07-08

## Market assessment

FMP did not return a true ES/SPX pre-market futures level or Globex high/low. Using the latest SPX cash quote as a proxy, the market is effectively flat versus the prior cash close at 7,503.85; use SPX/ES from broker for the exact futures gap before placing orders.

Volatility is the main edge this morning. VIX is 17.74 versus yesterday's 16.13 close, up 1.61 points (+10.0%), which means index options are pricing richer intraday movement than yesterday. That supports premium selling, but not blindly: the 2:00 PM ET FOMC Minutes are a high-impact event that can widen range and reverse the morning trend.

Yesterday closed in the middle/lower half of the range, which gives a neutral-to-slightly bearish read into the open. With no confirmed overnight gap and FOMC risk later, the best structure is a reduced-size 0DTE iron condor outside the 1-day expected move, entered only after the opening range settles and closed before the minutes unless already at target.

## Overnight futures movement

- **SPX cash proxy:** 7,503.85
- **Prior SPX close:** 7,503.85
- **Inferred gap:** 0.0 points (0.00%) using FMP cash proxy
- **True ES/SPX futures gap:** from broker/futures platform; FMP did not expose preMarket or Globex fields.
- **View:** **Uncertain / define after open** — without a confirmed ES level, do not assume a hold or fade. If broker ES shows a gap larger than +/-0.5%, expect the first 30 minutes to test whether that gap holds; otherwise treat it as a normal theta morning.

## Pre-market IV levels

- **Current VIX:** 17.74
- **Yesterday VIX close:** 16.13
- **Change:** +1.61 points (+10.0%)
- **Recent context:** VIX is above the 5-session average near 16.2 and close to the 18-session average near 17.7.
- **Implication:** Premium is richer than yesterday, but the richness is partly justified by FOMC Minutes. Sell premium only with wider strikes, reduced size, and a defined event-risk exit.

## Economic calendar impact

| Time (ET) | Event | Impact | Trading read |
|---:|---|---|---|
| 7:00 AM | MBA mortgage data / 30-year mortgage rate | Low to Medium | Already out before the open; rates read-through only. |
| 1:00 PM | 10-Year Note Auction | Low | Can matter if tail/stop is weak; watch yields before adding risk. |
| 2:00 PM | FOMC Minutes | High | Often expands or reverses intraday range; avoid holding full-size short gamma into the release. |
| 2:30 PM | EIA crude / gasoline inventories | Low to Medium | Sector-specific energy impulse; usually not an SPX-wide catalyst unless oil moves sharply. |
| 3:00 PM | Consumer Credit Change | Low | Late-day macro, limited index impact unless surprise is extreme. |

**Today's calendar:** Moderate-to-heavy because one high-impact Fed event sits inside the cash session.  
**Recommendation:** Wider strikes, half-size risk, and close or materially de-risk by 1:30 PM ET. A second post-FOMC trade is acceptable only if IV remains elevated and price is contained inside the morning range.

## Earnings exposure

No mega-cap S&P constituents appear on today's FMP earnings calendar. The notable liquid names are:

| Ticker | Company | Time | Market cap | Market-moving potential |
|---|---|---:|---:|---|
| LEVI | Levi Strauss & Co. | AMC | ~$9.7B | Low for SPX; consumer discretionary read-through. |
| PSMT | PriceSmart, Inc. | AMC | ~$5.9B | Low for SPX; retail/consumer read-through. |
| AZZ | AZZ Inc. | AMC | ~$4.3B | Low for SPX; industrial read-through. |
| HELE | Helen of Troy Limited | BMO | ~$0.7B | Low for SPX; single-name consumer risk. |
| 9983.T | Fast Retailing Co., Ltd. | AMC / Japan | large non-US listing | Limited direct SPX impact; global retail sentiment only. |

**Earnings risk:** Low index impact. Today is macro-driven rather than single-name driven.

## Globex range and expected range

- **Globex range:** FMP did not provide ES overnight high/low. Use broker/futures platform for exact Globex high, low, and volume nodes.
- **Prior SPX day range proxy:** 7,536.06 high to 7,478.63 low = **57.43 points**.
- **VIX-based 1-day expected move:** 7,503.85 x 17.74% / sqrt(252) = **~84 points** (~1.12%).
- **Expected range from cash proxy:** approximately **7,420 to 7,588**.

## Opening gap strategy

- **Base case:** No confirmed FMP pre-market gap. Wait for the first 15-20 minutes and define the opening range.
- **If broker ES shows a >0.5% gap up:** Fade only if price rejects prior-day high / first 15-minute high; otherwise do not sell calls into trend strength.
- **If broker ES shows a >0.5% gap down:** Fade only if price reclaims prior close / VWAP; otherwise keep put spreads wider or skip the put side.
- **If flat to small gap:** Normal theta structure is acceptable, but only reduced size because of the 2:00 PM FOMC Minutes.

## IV crush opportunity

Yesterday was not a major scheduled high-IV event, so this is not a clean morning-after IV crush setup. Today's elevated VIX is more about forward event risk into FOMC Minutes.

**Opportunity:** Sell premium only if the opening range is contained and liquidity is clean. The better IV crush window may come **after** the 2:00 PM release if VIX remains elevated and SPX does not break the expected range.

## Previous day's close analysis

- **Prior SPX open:** 7,516.63
- **Prior SPX high:** 7,536.06
- **Prior SPX low:** 7,478.63
- **Prior SPX close:** 7,503.85
- **Close location:** 43.9% up from the low within the prior day's range.

The market closed in the middle/lower half of the session range, not at the highs. That is neutral-to-slightly bearish for the open: buyers did not fully regain control, but sellers also failed to close the market on the lows.

## Support and resistance

### Support

1. **7,500 / 7,503** — prior close and round-number pivot.
2. **7,479** — prior day low; first important downside test.
3. **7,420** — VIX-based expected-move lower bound; short put spreads should be below or near this zone.

### Resistance

1. **7,536** — prior day high; first upside stall zone.
2. **7,550** — round-number breakout checkpoint above prior high.
3. **7,588 / 7,600** — VIX-based expected-move upper bound and major round-number magnet.

## Pre-market trade plan

- **Preferred strategy:** Reduced-size 0DTE SPX iron condor.
- **Expiration:** Today, 2026-07-08.
- **Entry time:** 9:45-10:00 AM ET, after the opening range and spreads settle. Do not enter before confirming there is no one-way trend through support/resistance.
- **Structure:** Expected-move-based strikes because no live options chain/deltas were available.
  - Sell **7,420 put**, buy **7,410 put**
  - Sell **7,590 call**, buy **7,600 call**
- **Delta guide:** Use broker chain to confirm shorts are near 0.10-0.15 delta. If either side is richer than 0.20 delta because of skew or gap, move that side farther out or skip it.
- **Position size:** Half normal size; target **1-2% of account at risk** because of FOMC Minutes.
- **Profit target:** Close at 40-50% of max profit.
- **Stop / risk rule:** Close a tested side if SPX trades through the short strike or if the spread value reaches 2x initial credit.
- **Event rule:** Close or reduce materially by **1:30 PM ET** ahead of the 2:00 PM FOMC Minutes. Do not carry full-size short gamma into the release.

## Scenario playbook

### Bull outcome

**Trigger:** SPX breaks and holds above 7,536, then accepts above 7,550.

- Do not add call-side risk into momentum.
- If already in the condor, close or roll the call spread higher before 7,590 becomes a magnet.
- Keep the put side only if VIX is stable/falling and price holds above VWAP.
- If SPX reaches 7,588/7,600 before FOMC, close the full structure.

### Bear outcome

**Trigger:** SPX loses 7,500 and then breaks 7,479 with breadth weakening.

- Close or roll the put spread lower before 7,420 becomes exposed.
- Take profits quickly on the call side; do not overstay if VIX is expanding.
- If decline is orderly and holds above 7,420, consider converting to a call credit spread only.
- If SPX breaks 7,420, stop out; do not average down short puts.

### Neutral outcome

**Trigger:** SPX remains between 7,479 and 7,536 through late morning.

- Hold the iron condor for 40-50% max profit.
- Avoid adding size after 12:30 PM ET because FOMC risk starts to dominate decay.
- Close or reduce by 1:30 PM ET unless premium has already collapsed and remaining risk is minimal.
- After 2:00 PM ET, only re-enter if price stays inside the morning range and VIX turns lower.

## Data and disclaimer

**Data sources:** Financial Modeling Prep quote endpoint for ^GSPC, SPY, and ^VIX; FMP historical-price-full for prior SPX/SPY OHLC and VIX history; FMP economic_calendar for today's macro events; FMP earning_calendar and quote endpoint for earnings exposure and market caps. FMP did not provide true ES/SPX futures pre-market level or Globex high/low; use broker/futures platform for exact overnight data.

**Disclaimer:** This report is for educational and research purposes only and is not investment advice, a recommendation, or an offer to buy or sell securities, options, or futures. Options involve substantial risk and may not be suitable for all investors. Verify all prices, strikes, greeks, liquidity, and event times in your broker platform before trading.
