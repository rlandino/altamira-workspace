# Jane Street Pre-Market Edge — 2026-04-24

## Market Assessment

S&P proxy pricing is showing a modest downside open versus prior close. Using FMP quotes as a pre-open proxy (exact ES/SPX futures should be confirmed from broker), the implied gap is about **-29.5 points (-0.41%)** on SPX-equivalent pricing.

Volatility is softer into the open: VIX is **18.76** versus yesterday's close at **19.31** (-0.55, about -2.85%). That points to slightly cheaper intraday option premiums versus yesterday, which favors disciplined, defined-risk short premium rather than aggressive naked premium selling.

Macro headline risk is light this morning (no CPI/NFP/FOMC-tier U.S. release on the schedule). Earnings are active, but broad index shock risk appears more idiosyncratic than systemic.

## Overnight Futures Movement

- **Gap (proxy):** -29.5 SPX points (**-0.41%**) vs prior close
- **View:** **Partial fade bias** (not a full trend-gap call)
- **Reason:** Gap magnitude is moderate (below 0.5%) with no major 8:30 AM ET macro catalyst; these conditions often produce partial mean reversion in the first 30-60 minutes.

## Pre-Market IV Levels

- **Current VIX:** 18.76
- **Yesterday VIX close:** 19.31
- **Change:** -0.55 (-2.85%)
- **Read-through:** Options are pricing **lower volatility** versus yesterday, so short-premium setups are still viable but with less edge from elevated IV. Prioritize structure quality and entry timing over size.

## Economic Calendar Impact

### U.S. Events Today (FMP)
- 17:00 ET — Baker Hughes Oil Rig Count (Low)
- 19:30 ET — CFTC positioning updates (S&P 500, Nasdaq, commodities; mostly Medium/Low)

### Impact Assessment
- **Calendar load:** **Light**
- **Expected effect on intraday SPX range:** Near baseline unless an unscheduled macro headline appears.
- **Recommendation:** Normal opening process; allow first 5-15 minutes of order-flow discovery before entering short-vol structures.

## Earnings Exposure

Notable large-cap names on today's calendar include:
- **PG** (Procter & Gamble)
- **HCA** (HCA Healthcare)
- **SLB** (SLB)
- **NSC** (Norfolk Southern)

Market-moving potential for index today: **Medium-Low** (single-name volatility likely, but broad index impact likely limited unless a large miss/guide shock spills into sector ETFs).

## Globex Range and Expected Range

- **Globex range:** Not provided by FMP. Confirm exact overnight high/low from broker futures platform.
- **Proxy range anchor:** Prior SPY session range = 712.36 - 702.28 = **10.08 points** (SPY), used as a fallback context.
- **VIX-based expected 1-day SPX move:**  
  - Formula: Price × (VIX / 100) / 16  
  - 7108.4 × 0.1876 / 16 ≈ **83.3 points**
  - **Expected range:** approximately **7025 to 7191** (about **+/-1.17%**)

## Opening Gap Strategy

- **Plan:** Let the open settle, then bias to **fade weak extension** if price cannot hold below first support break.
- **Execution:** Wait for 9:35-9:50 AM ET before opening theta structures.
- **Invalidation:** If SPX drives and holds below Support 2 early with expanding breadth/volume, abandon fade thesis and reduce short-put exposure.

## IV Crush Opportunity

- **Assessment:** **No major IV crush setup** (no prior-session CPI/Fed-style volatility event).
- **Implication:** Treat this as a standard theta day, not an event-volatility collapse day. Harvest decay with defined risk; avoid oversizing.

## Previous Day's Close Analysis

Using prior SPY OHLC (Open 709.50, High 712.36, Low 702.28, Close 708.45), close was in the **upper-middle** of the session range (not at extremes).  
Lean for today: **Neutral to slightly bearish early**, with scope for two-way trade and intraday reversion.

## Support and Resistance

### Support
1. **7090** — near-term round-number pivot below current SPX proxy
2. **7046** — prior-day low proxy zone (from SPY prior low conversion)
3. **7025** — VIX-implied lower expected-move boundary

### Resistance
1. **7138** — prior close / reclaim threshold
2. **7150** — prior-day high proxy + round-number confluence
3. **7191** — VIX-implied upper expected-move boundary

## Pre-Market Trade Plan

- **Strategy:** **0DTE SPX Iron Condor (defined risk)**
- **Structure (example):**
  - Short **7020 Put**
  - Long **6995 Put**
  - Short **7195 Call**
  - Long **7220 Call**
- **Expiration:** Today (0DTE)
- **Entry window:** **9:35-9:50 AM ET** after opening volatility normalizes
- **Risk size:** **1x to 0.75x normal size** (about 2-3% account risk max) because IV is not elevated
- **Management:**
  - Profit target: 40-50% of max credit
  - Hard risk trigger: short strike tested with momentum; reduce/close threatened side

## Scenario Playbook

- **Bull outcome (above 7138, holding):**
  - Reduce or close call spread early if challenged
  - Keep put side for theta if breadth supports trend-up

- **Bear outcome (below 7090, especially through 7046):**
  - Reduce/close put spread risk immediately
  - Optionally keep call side if downside trend confirms

- **Neutral outcome (between 7090 and 7138):**
  - Hold structure for decay
  - Exit at 40-50% max profit or by early afternoon to avoid late-day gamma

## Data and Disclaimer

- **Data sources:** Financial Modeling Prep (FMP) quote (`^GSPC, SPY, ^VIX`), historical-price-full (`SPY`, `^VIX`), economic calendar, earnings calendar.
- **Overnight/Globex note:** Exact ES/SPX Globex high/low should be confirmed from broker or futures platform.

**Disclaimer:** This report is for educational and research purposes only and is not investment advice. Options involve substantial risk, including potential loss of principal.
