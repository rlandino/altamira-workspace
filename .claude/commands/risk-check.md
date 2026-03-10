# /risk-check — Portfolio Risk Limit Validation

Validate current portfolio against Altamira risk framework limits (position size, sector, options, cash).

## Instructions

You are running a risk limit check for Altamira Capital. Follow these steps exactly:

### Step 1: Load current portfolio

- **Primary source:** `context/portfolio-details.md` — contains current positions, sector breakdown, and key metrics.
- **If missing or stale:** Use `context/current-data.md` for portfolio value and snapshot fields, or ask the user to provide current positions. Dashboard source of truth: http://localhost:8501/Portfolio (Streamlit).

Extract:
- Each position: ticker, market value (or notional for options), sector
- Total portfolio value
- Cash balance and cash %
- Options notional or allocation %

### Step 2: Load risk limits

From `outputs/risk-management-framework.md` and investment thesis:

| Limit | Rule | Check |
|-------|------|--------|
| **Position size** | No single position > 5% of portfolio | For each position: (position value / portfolio value) ≤ 0.05 |
| **Sector** | No sector > 25% of portfolio | Sum position values by sector; each sector total / portfolio value ≤ 0.25 |
| **Options** | Options allocation ≤ 30% (notional or capital at risk) | Options exposure / portfolio value ≤ 0.30 |
| **Cash** | Cash reserve ≥ 15% | Cash / portfolio value ≥ 0.15 |
| **Correlation** | Avoid >3 highly correlated positions in same sector | Count positions per sector; flag if >3 in one sector |

Sector mapping: Tech includes AAPL, MSFT, GOOGL, AMZN, AVGO, META, NVDA, etc. Use portfolio-details sector breakdown if available.

### Step 3: Run checks

For each limit:
- **PASS** — State the limit and current value (e.g. "Position size: PASS — largest position 4.2%").
- **FAIL** — State the limit, current value, and threshold (e.g. "Sector: FAIL — Technology 28% (max 25%)").

### Step 4: Output summary

- **Overall:** "Risk check: PASS" or "Risk check: FAIL" with list of failed limits.
- **Action items:** If FAIL, recommend specific actions (e.g. "Reduce Tech by 3% or add to other sectors").
- **Optional:** Table of current exposure vs limit for each rule.

## Context

- **Portfolio allocation model:** `outputs/portfolio-allocation-model.md`
- **Risk management framework:** `outputs/risk-management-framework.md`
- **Max position:** $5,000 at $100K portfolio (5%)
