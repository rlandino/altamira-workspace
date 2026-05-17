# Jane Street Pre-Market Edge -- 2026-05-17

## Market assessment

Today is Sunday; U.S. cash equity/options market is closed today (weekend). The analyzer can frame levels from the latest available FMP data, but there is no 0DTE SPX/SPY theta trade to place today.

VIX is 18.43 (flat vs latest close); 20-session reference is 18.06. Options pricing is normal, so premium selling should stay defined-risk unless opening breadth confirms a stable range.

The latest cash session closed at the lows of its range (19% location), which gives a bullish-to-neutral bounce lean if sellers cannot press below support. Calendar load: Closed; earnings market-moving potential appears low from today's feed.

## Overnight futures movement

- **SPX/ES source:** No user futures input. Using FMP ^GSPC/SPY quote as a cash-market proxy; exact ES Globex levels should come from the broker/futures platform.
- **Latest cash session:** 2026-05-15 OHLC 7,445.11 / 7,454.85 / 7,397.50 / 7,408.49.
- **Current proxy:** 7,408.50.
- **Gap:** +0.0 pts (+0.00%).
- **View:** No actionable gap today -- cash session is closed; use ES/SPX broker quotes Monday pre-market for the live gap.

## Pre-market IV levels

- **VIX:** 18.43 (flat vs latest close).
- **5-session VIX reference:** 17.99.
- **20-session VIX reference:** 18.06.
- **Implication:** IV is normal; favor defined-risk premium structures and avoid short gamma if VIX expands above the first-hour high.

## Economic calendar impact

- Weekend run: no U.S. cash equity/options session today; verify Monday calendar before trading.
- No same-day economic events returned by FMP for this date.

**Today's calendar:** Closed. **Recommendation:** Do not open same-day index premium; prepare Monday plan after live futures and calendar refresh.

## Earnings exposure

- No mega-cap/index-heavy same-day earnings returned by FMP. Market-moving potential: Low.

## Globex range and expected range

- **Globex range:** From broker/futures platform. FMP does not provide ES Globex high/low in this workflow.
- **Proxy range:** Latest cash-session SPX range was 57.4 points.
- **VIX expected 1-day move:** +/- 86.0 points (~+/-1.16%).
- **Expected range from current proxy:** 7,322.5 to 7,494.5.

## Opening gap strategy

- **Plan:** Stay flat; market is closed today.
- **Execution note:** Re-run Monday with live futures and broker option-chain deltas.

## IV crush opportunity

- **Event context:** No live same-day IV-crush opportunity because there is no Sunday cash/options session. 
- **Theta implication:** Do not sell same-day premium today.

## Previous day's close analysis

- **Close location:** Latest cash session closed at the lows (19% of range).
- **Lean:** bullish-to-neutral bounce lean if sellers cannot press below support.
- **Range guide:** Prior range of 57.4 points is the first proxy for Monday's expected auction width until live Globex data is available.

## Support and resistance

### Support

1. **7,397.5** -- prior session low; first downside reference from the latest cash session.
2. **7,375.0** -- nearby round-number support below the latest close.
3. **7,322.5** -- VIX expected-move lower band.

### Resistance

1. **7,454.9** -- prior session high; first upside reference from the latest cash session.
2. **7,494.5** -- VIX expected-move upper band.
3. **7,500.0** -- nearby round-number resistance above the expected-move band.

## Pre-market trade plan

- **Strategy:** No trade -- market closed today. Re-run Monday at 8:00 AM ET with live ES/SPX futures before placing any 0DTE order.
- **Model reference only:** If these levels were used for the next live session, model-based 0.10-0.15 delta-style boundaries would be approximately 7320/7310 put spread and 7495/7505 call spread. Confirm broker deltas and live futures first.
- **Expiration:** No same-day expiration available today.
- **Entry time:** No entry today. Next valid window: Monday 9:35-9:50 AM ET after open settles.
- **Position size:** 0% today; for next live session use 1-2% account risk until event calendar is confirmed.

## Scenario playbook

- **Bull outcome:** SPX/SPY opens next live session above Resistance 1 (7,454.9) and holds. Action: do not add call-side premium early; if already in a condor, cut or roll call risk and let put side decay only if VIX is stable.
- **Bear outcome:** SPX/SPY loses Support 1 (7,397.5) with breadth confirmation. Action: avoid selling fresh puts into momentum; close/roll threatened put side and consider harvesting call-side premium after the move exhausts.
- **Neutral outcome:** Price stays between Support 1 and Resistance 1 with VIX flat/down. Action: next live session may allow a small defined-risk iron condor, targeting 50% max profit and closing before late-day gamma.

## Data and disclaimer

- **Data sources:** FMP quote (^GSPC, SPY, ^VIX), FMP historical-price-full (SPY, ^GSPC, ^VIX), FMP economic_calendar, FMP earning_calendar. Globex/overnight high-low requires broker/futures platform data.
- **Fetch status:** spy_hist: 31; earnings: 8 rows; quotes: 3 rows; vix_hist: 31; spx_hist: 31; econ: 21 rows.
- **Disclaimer:** This briefing is for educational and research purposes only and is not investment advice. Options involve risk and can result in substantial losses.
