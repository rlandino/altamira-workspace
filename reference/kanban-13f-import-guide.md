# Update Kanban Board with Automated 13F Holdings Service

Use this to add or update the **Automated 13F Holdings Diff & Copycat Portfolio Service** project and its tasks on the kanban board at http://localhost:3004.

---

## Option 2: Import CSV (if your kanban app supports it)

1. Open the kanban board: **http://localhost:3004**
2. Look for **Import**, **Add project from CSV**, or **Upload** in the UI (e.g. project menu, settings, or board toolbar).
3. Select the file: **`outputs/kanban-13f-project-import.csv`**
4. Map columns if prompted: Project, Task ID, Title, Column, Priority, Labels, Description, Created.
5. Import. If the project already exists, the app may merge by Task ID or ask to create new tasks.

---

## Option 3: Add project and tasks manually

1. Open **http://localhost:3004**
2. Create a new project (if it doesn’t exist): **"Automated 13F Holdings Diff & Copycat Portfolio Service"**
3. Add the following tasks and set their column to **Done** (or the equivalent):

| Task ID | Title |
|--------|--------|
| 13f-service-epic | Epic: 13F Holdings Diff & Copycat Portfolio Service |
| 13f-data-pipeline-001 | 13F Data Pipeline & API |
| 13f-holdings-diff-001 | 13F Holdings Diff (period-over-period) |
| 13f-copycat-portfolio-001 | 13F Copycat Portfolio |
| 13f-fund-performance-001 | 13F Fund Performance (metrics) |
| 13f-stock-screener-001 | 13F Stock Screener |
| 13f-combined-holdings | Combined Holdings (overlap / consensus) |
| 13f-backtester-001 | 13F Backtester |
| 13f-heat-map-001 | 13F Heat Map export |
| 13f-dashboard-integration | Dashboard integration (Option B: API) |

4. Copy descriptions from **`outputs/kanban-13f-project-import.csv`** (Description column) if you want full text in each card.

---

## Option 4: Use the board’s API (if available)

The reference mentions an **export** endpoint: `http://localhost:3005/api/board/export`. If the same app exposes an **import** or **update** API (e.g. POST to create/update projects and tasks), you can:

1. Check the kanban app’s docs or source for an import/API endpoint.
2. Use **`outputs/kanban-13f-project-import.csv`** as the source of project name, task IDs, titles, columns, and descriptions.

---

## Contents of the import file

- **File:** `outputs/kanban-13f-project-import.csv`
- **Project name:** Automated 13F Holdings Diff & Copycat Portfolio Service
- **Tasks:** 10 (epic + 9 feature tasks). All marked **done** to reflect current implementation status.
- **Format:** Same columns as the board export (Project, Task ID, Title, Column, Priority, Labels, Description, Created).

After import or manual add, the 13F project on the board will match the implemented work in this workspace.

---

## Syncing task status after progress

The kanban API does **not** expose an endpoint to update a task’s column (e.g. move to Done). To reflect recent implementation progress:

1. **Run the status report** (requires the kanban app running on port 3005):
   ```bash
   python scripts/kanban-update-13f-status.py
   ```
2. Open the board UI: **http://localhost:3004**
3. Find the project **"Automated 13F Holdings Diff & Copycat Portfolio Service"** and drag each task listed in the script output (or in **`outputs/kanban-13f-status-update.md`**) into the **Done** column.
4. Optionally re-export the board to refresh `context/kanban-export.csv`:
   ```bash
   curl -o context/kanban-export.csv "http://localhost:3005/api/board/export"
   ```

**Note:** If you created the 13F project via **Option 1** (API import), the app may have placed all tasks in Backlog. Use the steps above to move the completed tasks to Done.
