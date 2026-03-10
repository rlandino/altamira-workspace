# /context-refresh — Refresh Context Files

Refresh key context files (holding snapshots, portfolio export, kanban export) using existing scripts.

## Instructions

You are refreshing workspace context for Altamira Capital. Follow these steps exactly:

### Step 1: Identify what to refresh

The user may specify scope in arguments: $ARGUMENTS

If no argument, refresh all of the following that are applicable:

1. **Holding monthly snapshots** — Build monthly snapshot per holding for the Holding Snapshot dashboard.
   ```bash
   python scripts/build-holding-monthly-snapshots.py --sheets
   ```
   Or if no Google Sheets: `--file context/position-history-export.csv` if that file exists. Writes `context/holding-monthly-snapshots.json`.

2. **Kanban export** — Export the kanban board to CSV (requires kanban API running on port 3005).
   ```bash
   curl -o context/kanban-export.csv "http://localhost:3005/api/board/export"
   ```
   On Windows PowerShell, use `Invoke-WebRequest` or curl if available. If the API is not reachable, skip and note "Kanban API not running; start the kanban app to refresh export."

3. **Current-data.md** — No script auto-updates this. If the user asked to refresh context, remind that `context/current-data.md` is updated manually (metrics, deliverables table, portfolio snapshot). Optionally list which metrics might need updating based on today's date.

### Step 2: Run applicable scripts

Execute each script that is relevant and for which dependencies are available (e.g. position history file or Sheets access for holding snapshots). Capture any errors.

### Step 3: Summarize

- **Refreshed:** List each context file or dataset that was updated and how (e.g. "context/holding-monthly-snapshots.json — rebuilt from build-holding-monthly-snapshots.py").
- **Skipped:** List any refresh that was skipped and why (e.g. "Kanban export — API not running").
- **Manual:** Remind about `context/current-data.md` and `context/portfolio-details.md` if they are source-of-truth files that require manual or dashboard-driven updates.

## Context

- **Holding snapshot dashboard:** `reference/holding-snapshot-dashboard.md`
- **Kanban:** `reference/kanban-dashboard.md` — UI 3004, API 3005
