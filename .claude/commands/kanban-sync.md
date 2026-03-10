# /kanban-sync — Kanban Board Export and Sync Instructions

Export the kanban board to CSV or surface sync instructions for completed tasks.

## Instructions

You are helping sync or export the Altamira kanban board. Follow these steps exactly:

### Step 1: Determine what the user needs

- **Export board to CSV:** Refresh `context/kanban-export.csv` from the kanban API so the workspace has the latest projects and tasks.
- **Sync completed tasks:** Surface instructions for moving completed Q1 (or other) tasks to Done in the UI, since the API does not support task updates.

### Step 2: Export board (if requested or default)

Requires the kanban app running (API on port 3005):

```bash
curl -o context/kanban-export.csv "http://localhost:3005/api/board/export"
```

On Windows PowerShell:
```powershell
Invoke-WebRequest -Uri "http://localhost:3005/api/board/export" -OutFile "context/kanban-export.csv"
```

If the request fails (connection refused, timeout), state: "Kanban API not running. Start the kanban app (see reference/kanban-dashboard.md) and run the export again." Do not create an empty file.

### Step 3: Sync instructions (completed tasks)

Point the user to the instructions document:

- **Q1 2026 completed tasks:** `outputs/kanban-q1-sync-instructions.md` — lists which Altamira Capital Q1 2026 tasks to move to Done manually (alt-task-02, 04, 05, 06, 07) and how. The kanban API has no task-update endpoint; changes are done in the UI at http://localhost:3004.

Summarize briefly: "Open http://localhost:3004, project 'Altamira Capital — Q1 2026', and drag the following tasks to Done: [list from the doc]. See outputs/kanban-q1-sync-instructions.md for rationale."

### Step 4: Optional

- If the user has other projects (e.g. Altamira Dashboard, 13F) and wants similar sync instructions, create or reference the appropriate doc (e.g. kanban-13f-status-update from `scripts/kanban-update-13f-status.py`).

## Context

- **Kanban UI:** http://localhost:3004
- **Kanban API:** http://localhost:3005 — export only; no PATCH for tasks
- **Reference:** `reference/kanban-dashboard.md`
