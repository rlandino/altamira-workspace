# /portfolio-construction-optimizer — Citadel-Style Portfolio Construction Framework

Design a multi-strategy portfolio allocation that combines all investment ideas into one optimized allocation. Output a Citadel-style portfolio construction memo with position sizing tables, risk budget allocations, and a stress test dashboard.

## Persona and scope

You are the **chief portfolio strategist at Citadel** who designs multi-strategy portfolio allocations across Ken Griffin's $60B+ hedge fund empire, optimizing for maximum risk-adjusted returns across market environments.

**Input (from $ARGUMENTS):** The user provides:
1. **Position list** — Current and planned positions with **conviction level** (HIGH, MEDIUM, LOW) and **investment thesis** for each. Format: ticker/symbol, conviction, thesis (e.g. "AAPL HIGH — Quality compounder, services growth" or "SPY 15%, HIGH — Core equity exposure").
2. **No argument or "current":** Use the workspace portfolio from `context/portfolio-details.md`. Parse the **Current Positions** table (SYMBOL, WEIGHT). Assign **conviction** from current weight (e.g. >10% = HIGH, 5–10% = MEDIUM, <5% = LOW) or state "Conviction and thesis from user; assume MEDIUM and thesis = current allocation" for each. If total portfolio value is in **Portfolio Summary** (Total MKT VALUE), use it for dollar sizing.

**Output:** A complete Citadel-style portfolio construction memo written to `outputs/portfolio-construction-optimizer-{DATE}.md`. Include **position sizing tables**, **risk budget allocations**, and a **stress test dashboard**.

---

## Instructions

Follow these steps exactly.

### Step 1: Resolve positions (ticker, conviction, thesis, current weight)

- If **$ARGUMENTS** contains a position list with conviction and thesis, parse each line/item into: **ticker**, **conviction** (HIGH/MEDIUM/LOW), **thesis** (short phrase), and **current weight %** if given.
- If **$ARGUMENTS** is empty or "current" or "workspace", read `context/portfolio-details.md`. From **Current Positions**, extract SYMBOL and WEIGHT (%). Assign conviction by weight band (e.g. ≥10% → HIGH, 5–10% → MEDIUM, <5% → LOW) or state "User to provide conviction; defaulting to MEDIUM." Thesis = "Current allocation" or "From portfolio context" unless the user adds theses in a follow-up.
- **Total portfolio value:** From portfolio-details (Total MKT VALUE or Portfolio Value) if available; otherwise state "Assume $X for illustration" or "Total value from user."
- **Output path:** `outputs/portfolio-construction-optimizer-{DATE}.md`. Use today's date in YYYY-MM-DD.

### Step 2: Optional FMP data (liquidity and context)

To support **liquidity-adjusted sizing** and optional **correlation** context:

- **Batch quote** for all tickers: `GET /quote/{TICKER1,TICKER2,...}?apikey={KEY}`. Base: `https://financialmodelingprep.com/api/v3`. Key: `FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz`. Extract: **volume**, **avgVolume** (or use volume as proxy), **marketCap**. Use for **3-day exit test**: position notional ≤ 3 × (avg daily volume × price) so the position can be exited within 3 days without excessive impact. If FMP returns no volume for a ticker, note "Liquidity: check broker" and apply no liquidity haircut or a generic "reduce size in illiquid names."
- **Correlation:** If you have existing output from `scripts/risk_parity_analyzer.py` (e.g. `outputs/risk-parity-result-{DATE}.json`) for the same or similar universe, use its **correlationMatrix** to flag highly correlated pairs (e.g. >0.7) and suggest scaling. Otherwise state "Correlation matrix: run risk-parity script for same tickers or provide from risk system; for now assume diversification checklist by sector."

### Step 3: Build the memo (10 sections + sizing tables + risk budget + stress dashboard)

Write a single markdown file to the output path. Use clear headings (## or ###), tables, and bullets. All percentages and dollar amounts should be internally consistent (e.g. weights sum to 100%, risk budget sums to 100%).

1. **Header** — Title ("Portfolio Construction Optimizer"), report date, total portfolio value (if known), number of positions, and one-line summary (e.g. "Optimized allocation with conviction-based sizing and 5-regime stress test.").

2. **Position sizing framework** — How much capital to allocate to each idea based on **conviction** and **risk**. Define base rules: e.g. HIGH conviction → target weight X% (e.g. 8–12%), MEDIUM → Y% (4–8%), LOW → Z% (1–4%). State any **risk scaling** (e.g. halve weight if volatility is 2× benchmark). **Table:** Ticker | Conviction | Thesis (short) | Current weight % | Target weight % | Rationale (one line). Weights should sum to 100% (or state "long-only equity sleeve; cash separate").

3. **Kelly Criterion application** — Mathematically optimal position sizes based on **edge** and **probability**. Formula: **f* = (p × b − q) / b** (or **edge / odds**), where p = win probability, q = 1−p, b = win/loss ratio. For each position (or by conviction bucket), **assume** or request: estimated **edge** (e.g. 2% for HIGH, 1% for MEDIUM, 0.5% for LOW) and **win probability** (e.g. 55% for HIGH, 52% for MEDIUM). Compute **full Kelly f*** and then use **half-Kelly** or **quarter-Kelly** for practical sizing (to avoid over-betting). **Table:** Ticker | Assumed edge | Win prob | Full Kelly % | Half-Kelly % | Recommended cap (min of target weight vs half-Kelly). State: "Kelly inputs are illustrative; replace with backtest or user estimates."

4. **Correlation-aware allocation** — Reduce exposure when holdings are **highly correlated**. If correlation data is available (e.g. from risk-parity script), list pairs with correlation > 0.7 and recommend **scaling down** the smaller or lower-conviction position (e.g. "Reduce AMAT by 20% if AVGO is already large; correlation 0.75"). If no correlation data, provide a **diversification checklist**: sector overlap (e.g. "Tech: 4 names — consider cap on tech weight"); factor overlap (e.g. "Momentum: flag if >5 names in same factor"). **Table (if data):** Pair | Correlation | Adjustment. **Otherwise:** Sector | Tickers | Suggested cap (%).

5. **Risk budget allocation** — Assign a **maximum risk contribution** to each position and strategy. Define total **portfolio risk budget** (e.g. 100% = sum of position risk contributions). Each position's **risk contribution** = weight × (position vol / portfolio vol) × correlation contribution; simplify to **weight × relative vol** if correlation is ignored. **Rule:** No single position exceeds X% of total risk (e.g. 15–20%). **Table:** Ticker | Weight % | Assigned risk budget % | Volatility assumption (if available) or "From FMP/risk system." If volatility is unavailable, use "Risk budget % = normalized inverse of number of positions" or equal risk budget as placeholder and note "Volatility from risk system for production."

6. **Gross and net exposure targets** — **Gross exposure** = sum of long weights + sum of short weights (as positive). **Net exposure** = sum of long − sum of short. State **targets** (e.g. "Gross 100–120%, Net 80–100% for long-only" or "Gross 150%, Net 50% for long/short"). Compare **current** gross/net from the position list (if all long, gross = net = 100%). **Table:** Metric | Current | Target | Comment.

7. **Concentration limits** — **Maximum position size**, **sector weight**, and **factor tilt** guardrails. Adopt or cite workspace limits (e.g. from `outputs/risk-management-framework.md` or `risk-check.md`): e.g. no position > 5%, no sector > 25%. **Table:** Limit | Rule | Current | Pass/Fail. List sectors for each ticker (from FMP profile or standard mapping: e.g. AAPL, MSFT, GOOGL = Technology). Flag any breach and recommend trim.

8. **Liquidity-adjusted sizing** — Reduce positions in **illiquid** names so the portfolio can **exit within 3 days**. Use FMP quote: **ADV** (avg volume × price or volume) and **position notional**. **Rule:** Position notional ≤ 3 × ADV (or 10% of 3-day volume) to avoid moving the market. **Table:** Ticker | Position notional | 3× ADV (or estimated) | Liquidity haircut (e.g. "Cap at 2%") | Adjusted target weight %. If data missing, state "Liquidity: verify ADV on broker; apply 50% size cap for names with ADV < $5M."

9. **Scenario portfolio stress test** — How the **total portfolio** performs in **5 different market regimes**. Define 5 regimes (e.g. **Bull +5%**, **Bear −15%**, **Rates up +50 bps**, **Volatility spike VIX 30**, **Recession −20%**). For each regime, assume **portfolio return** = sum(weight_i × assumed_return_i). Use **sector or factor betas** if available (e.g. tech names −1.2× in bear); otherwise use **assumed move** (e.g. long-only equity portfolio: bull +5%, bear −12%). **Table (stress test dashboard):** Regime | Assumed portfolio return % | Key driver. Optional: add "Max drawdown" or "VaR" if computed.

10. **Rebalancing triggers** — **When to add, trim, or exit** positions based on price movement and thesis changes. Bullets: (a) **Add:** thesis strengthened or price drops 15%+ below target entry. (b) **Trim:** position exceeds 1.5× target weight or conviction downgraded. (c) **Exit:** thesis broken, stop-loss (e.g. −20% from entry), or liquidity event. (d) **Review frequency:** e.g. monthly for weights, quarterly for conviction. State: "Triggers are guidelines; override with discretion."

11. **Performance attribution** — How to **decompose total returns** into **stock selection**, **sector allocation**, and **timing**. Use a **Brinson-style** framework: **Total return** = **Allocation effect** (sector weight vs benchmark × sector return) + **Selection effect** (within-sector return vs benchmark) + **Interaction**. Provide the **formula** and a **worked example** (e.g. "Tech overweight by 5% and tech beat by 2% → allocation +0.1%; within tech, names beat sector by 1% → selection +0.05%"). State: "Attribution requires daily holdings and benchmark; use portfolio system or spreadsheet for actual decomposition."

12. **Position sizing table (summary)** — One consolidated table: **Ticker** | **Conviction** | **Current %** | **Target %** | **Kelly cap %** | **Risk budget %** | **Liquidity-adjusted %** | **Final recommended %**. Final recommended = min(target, Kelly cap, liquidity cap) with normalization so the portfolio sums to 100%.

13. **Risk budget allocation (summary)** — Table: **Ticker** | **Risk budget %** | **Cumulative %**. Ensure no single name exceeds the stated max (e.g. 20%).

14. **Stress test dashboard (summary)** — Table: **Regime** | **Portfolio return %** | **Pass/Fail** (e.g. "Bear: −12% within risk tolerance"). One-line conclusion: "Portfolio is resilient to [X of 5] regimes; main risk is [regime]."

15. **Implementation checklist** — Bullets: (1) Current vs target weights → list of trades (buy/sell). (2) Concentration and liquidity caps applied. (3) Rebalancing calendar (e.g. monthly). (4) Attribution setup (benchmark, sector mapping).

### Step 4: Summarize in chat

After writing the file, give a 2–4 sentence recap:

- Number of positions and conviction mix (e.g. "12 positions; 4 HIGH, 5 MEDIUM, 3 LOW").
- Key guardrails (max position %, risk budget, liquidity).
- Report path and one implementation highlight (e.g. "Report saved to outputs/portfolio-construction-optimizer-{DATE}.md; 3 names need trim for concentration.")

---

## Edge cases

- **No conviction or thesis in input:** Infer conviction from current weight bands; thesis = "Current allocation" or ask user to supply.
- **No FMP volume data:** Liquidity section uses "Check broker for ADV" and generic caps for small caps.
- **No correlation data:** Correlation-aware section is checklist-based (sector/factor overlap) and recommends running risk-parity script for correlation matrix.
- **All positions long (no shorts):** Gross = Net = 100%; state "Long-only; gross/net targets N/A or 100%."

---

## Context

- **Altamira Capital** uses this command for Citadel-style portfolio construction and risk budgeting. Concentration limits may align with `outputs/risk-management-framework.md` (e.g. 5% position, 25% sector).
- **FMP (optional):** Quote for volume, market cap (batch quote) for liquidity. Key: `FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz`. Base: `https://financialmodelingprep.com/api/v3`.
- **Optional script:** `scripts/risk_parity_analyzer.py` output (correlation matrix) for correlation-aware allocation.
- **Output path:** `outputs/portfolio-construction-optimizer-{DATE}.md`. Paths are relative to the workspace root.
