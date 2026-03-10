# /work-plan — Next Activities from Kanban and Recent Work

Plan the next 3–5 activities from the kanban board and recent workspace work so you have day-to-day continuity.

## Instructions

You are helping plan the next activities for Altamira. Follow these steps exactly:

### Step 1: Ensure kanban data

- **Optional refresh:** If the kanban API is running (port 3005), refresh the export first so the plan uses the latest board state. Same as `/kanban-sync` Step 2:
  - **curl:** `curl -o context/kanban-export.csv "http://localhost:3005/api/board/export"`
  - **PowerShell:** `Invoke-WebRequest -Uri "http://localhost:3005/api/board/export" -OutFile "context/kanban-export.csv"`
  - If the request fails (connection refused, timeout), skip refresh and use the existing CSV if present.
- **Read:** Parse `context/kanban-export.csv`. Columns: Project, Task ID, Title, Column (e.g. todo, backlog, done), Priority, Labels, Description, Created.
- **If missing or empty:** Tell the user to run `/kanban-sync` (or start the kanban app per `reference/kanban-dashboard.md` and run the export) so the board is up to date. Do not write a work-plan file; stop after the message.

### Step 2: Infer recent work

- **Scan `outputs/`:** Find recent files (last 7 days) by date in filename (e.g. `options-scan-COST-2026-03-02.md`, `earnings-analysis-AAPL-2026-02-28.md`) or by file modification time. Infer which projects or topics were worked on (e.g. options-scan, earnings-analysis, Altamira Q1 tasks).
- **Read `context/current-data.md`:** Use the "Deliverables" table and "Current State" section for explicit in-progress items and next steps (e.g. alt-task-01, trading infrastructure, market monitoring workflows).

### Step 3: Build the work-plan

- **Next from kanban:** From the CSV, list tasks where Column is `todo` or `in progress` first, then high-priority `backlog` (Priority order: urgent > high > medium > low). Group by Project. Limit to a small set (e.g. 5–10 tasks) so the plan stays actionable. Ignore tasks where Column is `done`.
- **Continuity:** If recent outputs or current-data point to a project (e.g. options-scan, Altamira Capital Q1 2026, Fiscal Platform), surface the next kanban task(s) for that project so the user can "continue from yesterday."
- **Suggested order:** Produce 3–5 concrete "next activities" as a numbered list (e.g. "1. Complete X (Project A — task-123); 2. Start Y (Project B — task-456)…") combining urgency, priority, and continuity.

### Step 4: Write the work-plan file

Write a single markdown file to **`outputs/work-plan-{DATE}.md`** (use today's date in YYYY-MM-DD). Ensure `outputs/` exists (create if needed). The file must include:

1. **Recent work** — Short summary of what was worked on lately (from outputs scan and current-data).
2. **Next from kanban** — Todo/in-progress tasks and selected backlog tasks, grouped by project (table or list with Project, Task ID, Title, Column, Priority).
3. **Suggested next activities** — Numbered list of 3–5 actionable items with project and task ID for continuity.

End with a one-line summary for the user (e.g. "Work-plan written to outputs/work-plan-2026-03-02.md. Start with [first activity] for continuity.")

## Context

- **Kanban export:** `context/kanban-export.csv` — from `http://localhost:3005/api/board/export` (see `/kanban-sync`).
- **Current state:** `context/current-data.md` — Deliverables and Current State.
- **Outputs:** `outputs/` — Dated reports (e.g. `*-YYYY-MM-DD.md`) and task/sync docs.
- **Reference:** `reference/kanban-dashboard.md` — Kanban UI (3004), API (3005), how to start the app.
