# Holding Snapshot Dashboard — Integration Reference

> How to add the Holding Snapshot section to the Portfolio Snapshots page at http://localhost:8501/a.

---

## Overview

The **Holding Snapshot** section displays a monthly snapshot table per portfolio holding with columns: **Month**, **Qty**, **Ticker**, **Cost Basis**, **Month Chg ($)**, **Month Chg (%)**.

Data is produced by `scripts/build-holding-monthly-snapshots.py` and stored in `context/holding-monthly-snapshots.json`. The Streamlit fragment in `scripts/streamlit_holding_snapshot.py` reads this file and renders the tables.

---

## Deploy to Dashboard (Streamlit)

### Prerequisites

1. **Monthly snapshot data** — Run the build script:
   ```bash
   # From Google Sheets Position History (set GOOGLE_SHEET_ID + GOOGLE_APPLICATION_CREDENTIALS):
   python scripts/build-holding-monthly-snapshots.py --sheets

   # From a local export:
   python scripts/build-holding-monthly-snapshots.py --file context/position-history-export.csv
   python scripts/build-holding-monthly-snapshots.py --local
   ```
   This writes `context/holding-monthly-snapshots.json`.

2. **Position History** — Ensure your Google Sheet has a "Position History" tab with columns: Date, Symbol, Quantity, MarketValue (and optionally CostBasis). See `reference/portfolio-storage-for-optimization.md`.

### Deploy Holding Snapshot to the app

**Option 1 — Deploy script (recommended)**

If you know the path to your Streamlit app root (where `app.py` or `pages/` live):

```bash
python scripts/deploy-holding-snapshot-to-app.py --app-dir "X:\path\to\your\streamlit-app"
```

This copies `streamlit_holding_snapshot.py` and `context/holding-monthly-snapshots.json` into the app, and tries to inject the section into the page that serves `/a` (e.g. `pages/a.py`). If no such page is found, the script prints the snippet to paste manually.

- **Only copy files (no injection):** `--app-dir "..." --no-inject`
- **Print snippet only (no copy):** `python scripts/deploy-holding-snapshot-to-app.py --snippet-only`

**Option 2 — Copy into existing page manually**

1. Copy `scripts/streamlit_holding_snapshot.py` into your app directory.
2. Copy `context/holding-monthly-snapshots.json` to your app’s `context/` (or set `HOLDING_SNAPSHOT_JSON` to its path).
3. In the page that serves route `/a` (Portfolio Snapshots), add:
   ```python
   from streamlit_holding_snapshot import render_holding_snapshot
   render_holding_snapshot()
   ```
   See `reference/holding-snapshot-integration-snippet.py`.

**Option 3 — Standalone preview**

Run the section alone to test:

```bash
streamlit run scripts/streamlit_holding_snapshot.py
```

Opens at http://localhost:8501 with "Portfolio Snapshots" and the Holding Snapshot section.

### Environment

- `HOLDING_SNAPSHOT_JSON` — Full path to `holding-monthly-snapshots.json` (default: `{workspace}/context/holding-monthly-snapshots.json`)

---

## Data Flow

```
Position History (Google Sheet)  or  context/position-history-export.csv
    ↓
scripts/build-holding-monthly-snapshots.py (--sheets or --file)
    ↓
context/holding-monthly-snapshots.json
    ↓
scripts/streamlit_holding_snapshot.py → render_holding_snapshot()
    ↓
Page /a (Portfolio Snapshots)
```

---

## Scheduled Refresh

To keep the monthly snapshots up to date:

1. **Cron / Task Scheduler** — Run the build script daily (e.g. after 4:15 PM ET when n8n Daily Snapshot completes):
   ```bash
   python scripts/build-holding-monthly-snapshots.py --sheets
   ```

2. **n8n** — Add a node to the Daily Portfolio Snapshot workflow (or a separate schedule) that executes the script after the Position History sheet is updated.

---

## Optional: Cost Basis

Position History does not include a Cost Basis column by default. To show Cost Basis in the table:

1. Add a **CostBasis** (or **AvgCost**) column to the Position History sheet.
2. Update the n8n Daily Portfolio Snapshot workflow to populate Cost Basis when appending rows.
3. Re-run `build-holding-monthly-snapshots.py` after the schema change.

Until then, the Cost Basis column will display "—" (blank). The script and UI handle missing Cost Basis gracefully.
