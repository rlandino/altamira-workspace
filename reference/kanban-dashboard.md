# Kanban Dashboard

The kanban board used for Financial Data Automation (and other projects) is **not in this workspace**. It runs as a separate application.

## URLs

| Purpose | URL |
|--------|-----|
| **UI** | http://localhost:3004 |
| **Export API** | http://localhost:3005/api/board/export |

## If the dashboard doesn't load (ERR_CONNECTION_REFUSED)

**Cause:** Nothing is listening on port 3004 — the kanban app process is not running.

**Fix:**

1. **Start the app**
   - **Preferred:** Double‑click the **Kanban Board** shortcut on your desktop (same place as FinceptTerminal). It should start the app that serves the UI on 3004.
   - **If no shortcut:** Open the project folder where the kanban app lives (e.g. Skills Factory repo or the repo you use for the board). From that folder:
     - **Node app:** run `npm run dev` or `npm start` (see that project’s `package.json` for the script that uses port 3004).
     - **Docker:** run `docker-compose up` or the container that maps port 3004.

2. **Confirm it’s running**  
   In a terminal: `netstat -an | findstr "3004"`. You should see a line with `LISTENING`. Then open http://localhost:3004/ in the browser.

3. **If the app is running but the page still fails**  
   Check Windows Firewall or antivirus for rules blocking **localhost** or port **3004**.

## Data in this workspace

- **Task docs**: `outputs/kanban-task-*.md` (e.g. stockscore, scoring-monitoring, percentile-normalization).
- **Export**: `context/kanban-export.csv` — exported from `localhost:3005/api/board/export` (e.g. 2026-02-17). Re-export from the running app to refresh.
- **13F project import**: `outputs/kanban-13f-project-import.csv` — CSV to add or update the "Automated 13F Holdings Diff & Copycat Portfolio Service" project and its 10 tasks. See **`reference/kanban-13f-import-guide.md`** for import steps (UI import, manual add, or API if available).

## Refreshing the export

When the kanban app is running:

```bash
# Example (adjust if your app uses a different export URL or format):
curl -o context/kanban-export.csv "http://localhost:3005/api/board/export"
```

Or use the export feature in the kanban UI if available.
