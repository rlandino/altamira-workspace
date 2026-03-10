# Portfolio Details Storage for Optimization

**Purpose:** Persist position-level portfolio data so you can run rebalancing, risk attribution, sector limits, and return optimization.

---

## 1. Where Data Is Stored

| Store | Content | Updated By | Use Case |
|-------|---------|------------|----------|
| **Google Sheet: Daily Dashboard** | One row per day (portfolio value, P&L, net delta, theta, cash %, VIX, SPY) | n8n Daily Snapshot @ 4:15 PM ET | Time series of portfolio value and aggregates |
| **Google Sheet: Position History** | One row per position per day (symbol, type, quantity, value, weight %, sector, Greeks) | n8n Daily Snapshot @ 4:15 PM ET | Optimization inputs: weights, sectors, deltas |
| **Google Sheet: Trade Log** | Individual trades (entry/exit, P&L, strategy) | Manual / future trade workflow | Attribution, win rate, strategy breakdown |

**Position History** is the main addition for optimization: it gives you a daily snapshot of every holding with weights and (for options) Greeks.

---

## 2. Position History Schema

Use a sheet named **Position History** with these columns (append one row per position per day):

| Column | Type | Description |
|--------|------|-------------|
| **Date** | YYYY-MM-DD | Snapshot date |
| **Symbol** | Text | Underlying ticker (e.g. COST, SPY) or option symbol |
| **AssetType** | EQ \| OPT | Equity or Option |
| **Quantity** | Number | Shares or contracts (negative = short) |
| **MarketValue** | Currency | Position market value |
| **WeightPct** | % | Position value / portfolio value × 100 |
| **Sector** | Text | Sector (if available; else blank for later enrichment) |
| **Delta** | Number | Position delta (options); 1.0 per share for equity |
| **Theta** | Number | Daily theta (options); 0 for equity |
| **Strike** | Currency | Option strike (blank for equity) |
| **Expiration** | Date | Option expiration (blank for equity) |
| **CallPut** | C \| P | Call or Put (blank for equity) |

**Optional:** Adding a **CostBasis** (or **AvgCost**) column to Position History improves the **Holding Snapshot** dashboard (monthly snapshot table per ticker at http://localhost:8501/a). The build script `scripts/build-holding-monthly-snapshots.py` and the Streamlit section work without it (Cost Basis column shows blank until the column exists in the sheet and n8n workflow).

**Optimization uses:**
- **Weights** → rebalancing vs target (e.g. 40% options / 40% momentum / 20% cash)
- **Sector** → sector exposure vs 25% limit
- **Delta / Theta** → risk and income attribution
- **Time series** → returns, volatility, Sharpe by period

---

## 3. How the Daily Snapshot Workflow Feeds It

The **Altamira - Daily Portfolio Snapshot** workflow will:

1. Keep existing behavior: E-Trade portfolio + balance, FMP VIX/SPY → **Calculate Portfolio Metrics** → append one row to **Daily Dashboard** + send **Telegram**.
2. **New:** In the same Calculate step (or a parallel Code node), build one row per position with the schema above and append all rows to **Position History**.

So each run adds:
- 1 row to Daily Dashboard
- N rows to Position History (N = number of positions)

Sector can be left blank initially and filled later via FMP profile/sector lookup if you add that to the workflow.

---

## 4. Optional: Workspace Copy for Scripts

If you run optimization from this workspace (e.g. Python or Node):

- **Option A:** Export **Position History** and **Daily Dashboard** from Google Sheets to CSV/JSON (manual or scheduled) into `context/` or `outputs/portfolio/` and read that in your script.
- **Option B:** Use Google Sheets API from the script to read the same sheets directly.

Keeping Google Sheets as the source of truth works well with n8n and your existing workbook.

---

## 5. Next Steps

1. Add the **Position History** sheet to your paper trading workbook (same Google Sheet as Daily Dashboard), with the column headers above.
2. Update the n8n **Daily Portfolio Snapshot** workflow to append position rows to **Position History** (see `outputs/n8n-workflow-1-daily-portfolio-snapshot-positions-update.md` or the workflow JSON change set).
3. Run the workflow once and confirm rows appear in Position History.
4. Use the stored data in optimization: read Position History + Daily Dashboard (e.g. via Sheets API or export), compute current weights and sector exposure, then run your rebalance or risk logic.
