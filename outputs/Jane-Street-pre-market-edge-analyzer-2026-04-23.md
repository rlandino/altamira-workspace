# Jane Street Pre-Market Edge — 2026-04-23

## Market assessment

SPX/SPY proxy positioning is **flat-to-up after yesterday's close**, but futures-specific Globex prints were not provided. Using the available FMP spot proxy, there is no measurable pre-open gap from the last cash close, so this is best treated as a **small/uncertain gap regime** unless ES data shows otherwise.

Volatility is **firmer this morning**: VIX is 19.31 versus 18.92 prior close (+2.1%). That keeps option premiums elevated versus yesterday and supports defined-risk theta structures, but it also argues for waiting until after the first macro data cluster before committing full size.

The U.S. calendar is **moderately eventful** at the open (8:30 ET claims + Chicago Fed) and again at 9:45 ET (S&P PMIs). Earnings are broad rather than mega-cap concentrated, so single-name risk is meaningful, while index-level impact is medium rather than extreme.

## Overnight futures movement

- **SPX/ES futures input:** Not provided by user.
- **Proxy used:** SPY/^GSPC quote (FMP). Exact ES/Globex should be confirmed from broker feed.
- **Proxy gap:** ~0.00% (flat vs last cash close proxy).
- **View:** **Uncertain / slight fade bias early**, because no confirmed futures impulse plus event risk in first 90 minutes can reverse initial direction quickly.

## Pre-market IV levels

- **Current VIX:** 19.31  
- **Yesterday VIX close:** 18.92  
- **Change:** +0.39 (+2.1%)
- **Read-through:** Implied volatility is higher vs yesterday, so premium selling remains attractive, but avoid pre-event entries before 8:30/9:45 ET prints.

## Economic calendar impact

### Key U.S. events today (ET)

- **8:30 ET** — Initial Jobless Claims (Medium)
- **8:30 ET** — Chicago Fed National Activity Index (Medium)
- **9:45 ET** — S&P Global Manufacturing PMI (Medium)
- **9:45 ET** — S&P Global Services PMI (Medium)
- **9:45 ET** — S&P Global Composite PMI (Medium)

### Impact and execution guidance

- Claims/PMI mornings often expand the first-hour range to roughly **1.2x–1.5x** typical early-session movement.
- Calendar load today is **Moderate**.
- **Recommendation:** Delay theta entries until post-9:45 ET data digestion (roughly 10:00 ET), then sell defined risk with slightly wider wings than normal.

## Earnings exposure

Notable reporters from today's calendar (market-cap weighted):

- **INTC (AMC)**
- **AXP (BMO)**
- **SAP (AMC)**
- **TMO (BMO)**
- **NEE (BMO)**
- **BX (BMO)**
- **UNP (BMO)**
- **HON (BMO)**
- **LMT (BMO)**
- **DOW (BMO)**

**Market-moving potential:** **Medium.** Heavy large-cap activity but not concentrated in the highest index-weight mega-cap cluster; index impact likely through sector rotation rather than one single-name shock.

## Globex range and expected range

- **Globex range (ES high/low):** Not available from FMP; pull from broker/futures platform for precise overnight extremes.
- **Cash-session proxy range (prior SPY session):** 3.23 points (~32.4 SPX-equivalent points).
- **VIX-based expected 1-day SPX move:**  
  \[
  \text{Expected Move} \approx \text{SPX} \times \frac{\text{VIX}}{100} \div \sqrt{252}
  \]
  \[
  7137.9 \times \frac{19.31}{100} \div \sqrt{252} \approx \pm 86.8 \text{ points} \; (\pm 1.22\%)
  \]

## Opening gap strategy

- **Plan:** Treat open as event-driven and **wait for confirmation**, not immediate fade/chase.
- If market opens above first resistance and holds through 9:50 ET, lean into call-side risk reduction.
- If market fails early and reclaims prior close only weakly, prefer neutral-to-bearish skewed premium selling.

## IV crush opportunity

- **Yes, conditional.**  
  Elevated VIX vs prior close and a macro-heavy open can keep premiums inflated into the first print cluster. If realized volatility decelerates after 9:45 ET, intraday IV compression favors iron condor/defined strangle structures.

## Previous day's close analysis

Using prior session OHLC proxy (SPY), close was near the top of the range (**~92.6% of session range**), which is usually a **mildly bullish-to-exhaustion** signal:

- Bullish if follow-through holds above first resistance.
- Exhaustion risk if early breakouts fail after data.

## Support and resistance

### Support

1. **7103** — Prior session SPX open/low zone (first structural support)
2. **7064** — Prior SPX close (key pivot for trend validation)
3. **7051** — VIX-implied 1-day lower expected-move boundary

### Resistance

1. **7140** — Prior session high / immediate breakout line
2. **7175** — Round-number overhead magnet
3. **7225** — VIX-implied 1-day upper expected-move boundary

## Pre-market trade plan

- **Strategy:** **0DTE SPX Iron Condor (defined risk)**
- **Structure (event-adjusted, target 0.10–0.15 delta shorts):**
  - Sell **7030 Put**
  - Buy **7000 Put**
  - Sell **7230 Call**
  - Buy **7260 Call**
- **Expiration:** Today (0DTE)
- **Entry window:** **10:05–10:25 AM ET** (after 9:45 ET PMI reaction)
- **Risk sizing:** **1/2 normal size** (about **1–2% account risk**)
- **Management:**
  - Take profits at **50% max credit**
  - Hard stop at **2x collected credit** or decisive breach of short strike
  - Flatten by end of day; avoid holding residual gamma into close unless deeply OTM

## Scenario playbook

### Bull outcome (price > 7140 and holding)

- Action: Reduce/close call spread side early if threatened.
- Keep put side to harvest decay if structure remains balanced.
- Do not roll call side up aggressively unless momentum stalls first.

### Bear outcome (price < 7103, especially sub-7064)

- Action: Close or roll put spread side before delta accelerates.
- Harvest remaining call-side premium.
- If tape becomes trend-down, convert to bearish defined-risk structure rather than forcing neutrality.

### Neutral outcome (price oscillates inside 7103–7140)

- Action: Hold condor for theta decay.
- Take 40–50% of max credit once available; avoid over-staying for final pennies.
- No adjustment unless one short strike reaches risk trigger zone.

## Data and disclaimer

- **Data sources:**  
  FMP quote (`^GSPC`, `SPY`, `^VIX`), FMP `historical-price-full/SPY`, FMP `economic_calendar`, FMP `earning_calendar`.
- **Overnight futures/Globex note:** Exact ES high/low and live futures prints should come from broker/futures platform; this report uses cash-index proxies where needed.

**Disclaimer:** For educational and research purposes only. Not investment advice. Options involve substantial risk, including total loss. Validate prices, liquidity, and risk limits before trading.
