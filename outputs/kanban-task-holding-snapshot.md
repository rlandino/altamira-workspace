# Kanban Task: Holding Snapshot under Portfolio Snapshots

**Task ID:** holding-snapshot-001  
**Created:** 2026-02-20  
**Status:** Ready for Implementation  
**Priority:** High  
**Category:** Dashboard / Portfolio Management

---

## Task Description

Add a **Holding Snapshot** section under **Portfolio Snapshots** on the local dashboard at http://localhost:8501/a. For each holding in the portfolio, display a monthly snapshot table with columns: Month (date), Qty, Ticker, Cost Basis, Month Chg ($), Month Chg (%).

---

## Requirements

1. **UI placement:** Section "Holding Snapshot" under "Portfolio Snapshots" on the page that serves http://localhost:8501/a.

2. **Table columns (per holding):**
   - Month (date)
   - Qty
   - Ticker
   - Cost Basis
   - Month Chg ($)
   - Month Chg (%)

3. **Data source:**
   - Preferred: Google Sheet "Position History" (Date, Symbol, Quantity, MarketValue; Cost Basis if column exists). Aggregate to one row per (ticker, month) — e.g. last day of month — then compute month-over-month change.
   - Fallback: Read from `context/holding-monthly-snapshots.json` produced by `scripts/build-holding-monthly-snapshots.py`.

4. **Behavior:**
   - One monthly snapshot table per holding (ticker). Use expanders or subheadings per ticker to keep the page compact.
   - If monthly snapshot data is missing, show: "Run scripts/build-holding-monthly-snapshots.py to generate monthly snapshot data."

---

## Implementation Status

- [x] Kanban task document created: `outputs/kanban-task-holding-snapshot.md`
- [x] Data script: `scripts/build-holding-monthly-snapshots.py` (read Position History or context export, aggregate by month, compute Month Chg $/%, write `context/holding-monthly-snapshots.json`)
- [x] UI component: `scripts/streamlit_holding_snapshot.py` (section to paste or import into app at /a)
- [x] Integration note: `reference/holding-snapshot-dashboard.md` (how to add section to app)
- [ ] Optional: Add Cost Basis column to Position History schema / n8n workflow for accuracy (documented in reference/portfolio-storage-for-optimization.md)

---

## Related Files

- Data script: `scripts/build-holding-monthly-snapshots.py`
- UI component: `scripts/streamlit_holding_snapshot.py`
- Data output: `context/holding-monthly-snapshots.json`
- Position History: Google Sheet "Position History" (same workbook as Daily Dashboard)
- Portfolio context: `context/portfolio-details.md`, `scripts/refresh-portfolio-context.py`
- Schema reference: `reference/portfolio-storage-for-optimization.md`

---

## Acceptance Criteria

- [x] Section "Holding Snapshot" appears under "Portfolio Snapshots" on http://localhost:8501/a (via `render_holding_snapshot()`)
- [x] For each portfolio holding, a table shows: Month, Qty, Ticker, Cost Basis, Month Chg ($), Month Chg (%)
- [x] Month Chg ($) and Month Chg (%) are computed vs prior month (requires at least two months of data per ticker)
- [x] Script `build-holding-monthly-snapshots.py` produces `context/holding-monthly-snapshots.json` from Position History or context export
- [x] If Cost Basis is not in Position History, table still works (column blank); adding Cost Basis to schema improves accuracy

---

**Add to kanban board:** This task should be added to the Financial Data Automation project on the kanban board (localhost:3004). Priority: High — supports portfolio monitoring and monthly attribution.
