# Jane Street Pre-Market Edge — 2026-06-19

## Market assessment

US equity and listed index options markets are on the Juneteenth holiday schedule today. FMP quotes show the latest SPX/SPY cash levels near the 2026-06-18 close rather than a live regular-session auction, so the correct theta posture is **no new 0DTE trade today**. Use SPX/ES from broker for exact futures and Globex high/low if trading futures products.

SPX last quote is 7500.58 versus the latest historical SPX close of 7500.57; the inferred cash gap is effectively flat. VIX is 17.09 versus 16.40 yesterday, so index options are pricing modestly firmer volatility, but holiday liquidity and closed cash options remove the usual same-day theta edge.

The prior session closed in the upper quartile of its range, which is a mild bullish continuation read for the next regular cash session. Calendar risk is light for US equities today; FMP mainly shows global macro releases and CFTC positioning later in the day.

## Overnight futures movement

- **Current proxy:** SPX 7500.58 from FMP quote. No user-supplied ES/SPX futures level.
- **Prior cash close:** SPX 7500.57 on 2026-06-18.
- **Inferred gap:** +0.01 points (+0.00%).
- **View:** **Uncertain / do not trade cash options** — the proxy shows no meaningful gap, but today is a US market holiday and true ES Globex levels should be checked on a futures platform.

## Pre-market IV levels

- **Current VIX:** 17.09.
- **Prior VIX close:** 16.40.
- **Change:** +0.69 vol points (+4.2%).
- **Read:** Options pricing is firmer versus yesterday, but the move is not large enough to override the holiday/no-liquidity constraint. Premium selling should wait for a normal opening auction and visible option markets.

## Economic calendar impact

- **US equity calendar:** Light because of the Juneteenth market holiday.
- **FMP events observed:** Global inflation, retail sales, central-bank speeches/minutes, and CFTC speculative positioning reports, including CFTC S&P 500 and Nasdaq 100 positioning at 19:30 UTC.
- **High-impact US open risk:** None comparable to CPI, NFP, FOMC, ISM, or retail sales at the US cash open.
- **Recommendation:** **Sit out today.** For the next regular session, use standard post-open confirmation and widen strikes if overnight futures expand beyond the VIX-implied range.

## Earnings exposure

- **Major US index-heavy reports:** None flagged from today's FMP earnings calendar.
- **Observed earnings feed:** Mostly smaller non-US/OTC symbols and local listings.
- **Market-moving potential:** **Low** for SPX/SPY. Single-name risk appears limited and should not drive an index theta plan today.

## Globex range and expected range

- **Globex high/low:** From broker/futures platform; FMP cash data does not provide a true ES overnight range.
- **Prior SPX day range proxy:** 7511.07 high - 7468.32 low = 42.75 points.
- **VIX-based 1-day expected move:** 7500.58 x 17.09% / sqrt(252) = approximately **+/-80.8 SPX points** (~+/-1.08%).
- **Expected range from last cash quote:** roughly **7419.8 to 7581.4**.

## Opening gap strategy

- **Today:** No cash-index opening strategy; listed US equity/options markets are closed for Juneteenth.
- **Next regular session if small gap:** Wait until 9:35-9:50 AM ET, let the opening auction settle, then consider normal defined-risk theta.
- **Next regular session if large gap (>0.5%):** Do not sell both sides immediately. Let the first 15-30 minutes reveal whether the gap holds or fades before placing the challenged side.

## IV crush opportunity

- **Yesterday's event setup:** No major US scheduled event like CPI/FOMC driving a clear overnight IV crush setup.
- **Current setup:** VIX is modestly higher than yesterday, not extreme.
- **Theta implication:** No standalone IV-crush trade today. If VIX remains above 17 on the next liquid session and price opens inside the expected range, defined-risk premium selling is acceptable at reduced size.

## Previous day's close analysis

- **Prior SPX OHLC:** Open 7487.36, high 7511.07, low 7468.32, close 7500.57.
- **Close location:** 75.4% of the day's range, in the upper quartile.
- **Lean:** Mild bullish / trend-stable for the next regular session, but not strong enough to sell downside aggressively without post-open confirmation.

## Support and resistance

### Support

1. **7500** — Prior close and round-number pivot; first reference for flat-gap trading.
2. **7468** — Prior session low; loss of this level would weaken the bullish close read.
3. **7420** — VIX expected-move downside area and near the 2026-06-17 SPX close; higher-conviction downside support.

### Resistance

1. **7511** — Prior session high; first upside stall level.
2. **7550** — Round-number / momentum checkpoint above prior range.
3. **7581** — VIX expected-move upside area; fade risk rises if reached quickly without broad participation.

## Pre-market trade plan

- **Primary strategy:** **No trade today — US equity/options market holiday.**
- **Do not enter:** 0DTE SPX/SPY iron condors, strangles, or credit spreads today unless a broker confirms a liquid listed-options session, which is not expected for the US holiday.
- **Conditional next-session plan:** If SPX opens between 7468 and 7511 with VIX 16-19 and no fresh macro shock, consider a defined-risk **0DTE SPX iron condor** after the first 5-20 minutes:
  - Short put: ~7420.
  - Long put: ~7400.
  - Short call: ~7580.
  - Long call: ~7600.
  - Expiration: next liquid 0DTE SPX session.
  - Entry time: 9:35-9:50 AM ET after the open settles.
  - Size: 1x normal or less; cap risk near 1-2% of account while VIX is only moderately elevated.
- **Execution note:** Strikes are expected-move based because no live options chain/delta surface was fetched. Replace with real 0.10-0.15 delta strikes from broker before entry.

## Scenario playbook

### Bull outcome

- **Trigger:** SPX trades above 7511 and accepts above 7550.
- **Action:** Do not add call credit risk into momentum. If in the next-session condor, close or roll the call side if price holds above 7550; let the put side decay only while breadth confirms.

### Bear outcome

- **Trigger:** SPX loses 7468 with VIX holding above 17.5.
- **Action:** Avoid selling new put spreads into the first break. If already in the next-session condor, close or roll the put side before the short strike is threatened; harvest the call side at 50-70% profit.

### Neutral outcome

- **Trigger:** SPX remains between 7468 and 7511, VIX stable to lower.
- **Action:** Best environment for the conditional next-session iron condor. Target 50% of max profit, reduce exposure before the final hour, and avoid carrying gamma through an event headline.

## Data and disclaimer

- **Data sources:** FMP quote for ^GSPC, SPY, ^VIX; FMP historical-price-full for SPY, ^GSPC, and ^VIX; FMP economic calendar; FMP earnings calendar.
- **Globex data:** Not available from FMP cash endpoints; use broker/futures platform for exact ES overnight high/low and pre-market depth.
- **Holiday note:** 2026-06-19 is Juneteenth; US equity/options market liquidity and tradability are constrained/closed.
- **Disclaimer:** This report is for educational and research purposes only and is not investment advice. Verify market hours, live prices, option chains, liquidity, and risk limits before placing any trade.
