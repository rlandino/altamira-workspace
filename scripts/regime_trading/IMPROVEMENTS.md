# Dashboard Improvement Recommendations — More Visibility Under the Hood

## 1. **Condition breakdown (why LONG / FLAT)**

**Action:** Add an expander or table showing the **8 confirmations** for the **current bar** (and optionally last N bars) with:
- Condition name
- Actual value (e.g. RSI=72.3, Momentum=1.2%, Volatility=4.1%)
- Threshold (e.g. < 90, > 1%, < 6%)
- Pass/Fail

**Why:** You see exactly why the signal is LONG or FLAT (which condition failed).

---

## 2. **Regime summary table (all 7 states)**

**Action:** Show a small table: one row per HMM state (0–6) with:
- State ID
- Label (Bull Run / Bear/Crash / Neutral)
- Mean Return, Volatility (std), Count
- Sort by Mean Return descending

**Why:** You see how each regime behaves and which state IDs are bull/bear.

---

## 3. **Regime time series**

**Action:** Add a chart (line or area) of **Regime over time** (last 500 hours), with:
- Y = state (0–6) or labeled (Bull / Bear / Neutral)
- Optional: color segments by bull (green), bear (red), neutral (gray)

**Why:** You see regime switches and persistence at a glance.

---

## 4. **HMM transition matrix**

**Action:** From the fitted model, expose `model.transmat_` and show a heatmap or table:
- Rows = from state, Cols = to state
- Values = P(next state = j | current state = i)

**Why:** Shows regime persistence and likely transitions (e.g. bull → bear probability).

---

## 5. **Equity curve vs buy & hold**

**Action:** Add a Plotly line chart:
- Strategy equity (from backtester)
- Buy & hold equity (same period, same $10k)
- X = time, Y = dollar value

**Why:** Visual comparison of strategy vs B&H over time.

---

## 6. **Drawdown over time**

**Action:** Plot **drawdown** (equity vs running max, as %) over time.

**Why:** See when and how deep drawdowns occurred.

---

## 7. **Indicator subplots (optional)**

**Action:** Add expanders or tabs with:
- RSI over time (with 70/30 lines)
- MACD + Signal line
- ADX over time (with 25 line)
- Price vs EMA50 / EMA200

**Why:** Debug and validate indicator behavior.

---

## 8. **Data freshness & refresh**

**Action:** 
- Show “Data through: &lt;last timestamp&gt;” and “Cache TTL: 1h”.
- Add a “Refresh data” button that clears `get_cached_signal_and_regime` and reruns.

**Why:** You know how stale the view is and can force an update.

---

## 9. **Cooldown / position state**

**Action:** In backtester (or a small “live” state), expose:
- Whether the **simulation** is currently in a position (LONG) or flat.
- If flat: “Cooldown active until &lt;bar&gt;” or “Cooldown inactive”.

**Why:** Clear view of why the bot isn’t entering (cooldown vs conditions).

---

## 10. **Trade context (regime at entry/exit)**

**Action:** In the trade log, add columns:
- Regime at entry (state ID or label)
- Regime at exit
- Hold duration (hours or bars)

**Why:** See which regimes produced wins/losses and how long trades lasted.

---

## Priority order (quick wins first)

| Priority | Action                         | Effort | Impact   |
|----------|--------------------------------|--------|----------|
| 1        | Condition breakdown (current bar) | Low    | High     |
| 2        | Regime summary table (7 states)  | Low    | High     |
| 3        | Data freshness + Refresh button  | Low    | Medium   |
| 4        | Regime time series chart         | Medium | High     |
| 5        | Equity curve vs B&H              | Low    | High     |
| 6        | Drawdown over time               | Low    | Medium   |
| 7        | HMM transition matrix            | Low    | Medium   |
| 8        | Trade log: regime at entry/exit   | Low    | Medium   |
| 9        | Cooldown / position state        | Medium | Medium   |
| 10       | Indicator subplots               | Medium | Lower    |

Implementing **1–3 and 5** in the app gives strong “under the hood” visibility with minimal code.

### Implemented (current app)

- **Condition breakdown** — Expander with 8 conditions: name, value, threshold, pass/fail for the current bar.
- **Regime summary table** — All 7 HMM states with Label, Mean Return, Volatility, Count (sorted by Mean Return).
- **Data freshness + Refresh** — "Data through" timestamp and a "Refresh data" button that clears cache and reloads.
- **Equity curve vs Buy & Hold** — Plotly chart: strategy equity vs buy & hold over time.
- **Regime over time** — Expander with a line chart of Regime (0–6) over the last 500 hours.
- **Drawdown over time** — Plot drawdown % (equity vs running max) over time.
- **HMM transition matrix** — Heatmap of P(next state | current state) in an expander.
- **Trade log: regime at entry/exit + hold duration** — Columns Regime entry, Regime exit, Hold (h).
- **Cooldown / position state** — Simulation state (LONG/FLAT) and cooldown remaining bars.
- **Indicator subplots** — Tabs: RSI (70/30), MACD+Signal, ADX (25), Price vs EMA50/200.
