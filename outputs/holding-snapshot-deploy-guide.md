# Holding Snapshot — Deploy to App

**Goal:** Add the Holding Snapshot section to the Portfolio Snapshots page at http://localhost:8501/a.

---

## 1. Ensure data exists

From this workspace:

```bash
# From Google Sheets Position History (set GOOGLE_SHEET_ID + GOOGLE_APPLICATION_CREDENTIALS):
python scripts/build-holding-monthly-snapshots.py --sheets

# Or from a local export:
python scripts/build-holding-monthly-snapshots.py --local
```

This writes `context/holding-monthly-snapshots.json`.

---

## 2. Deploy to your Streamlit app

The app that serves http://localhost:8501/a is **not in this workspace**. Use one of:

### A. Deploy script (if you know the app path)

```bash
python scripts/deploy-holding-snapshot-to-app.py --app-dir "X:\path\to\your\streamlit-app"
```

- Copies `streamlit_holding_snapshot.py` and `context/holding-monthly-snapshots.json` into the app.
- Tries to inject the section into the page that serves `/a` (e.g. `pages/a.py`).
- If no such page is found, the script prints the snippet to paste manually.

**Variants:**

- Only copy files (no injection): `--app-dir "..." --no-inject`
- Print snippet only: `python scripts/deploy-holding-snapshot-to-app.py --snippet-only`

### B. Manual paste

1. Copy `scripts/streamlit_holding_snapshot.py` into your app directory.
2. Copy `context/holding-monthly-snapshots.json` into your app’s `context/` (or set env `HOLDING_SNAPSHOT_JSON` to its path).
3. In the page that serves route `/a` (Portfolio Snapshots), add:

   ```python
   from streamlit_holding_snapshot import render_holding_snapshot
   render_holding_snapshot()
   ```

   Snippet file: `reference/holding-snapshot-integration-snippet.py`.

---

## 3. Run the app

Start your Streamlit app as usual (e.g. `streamlit run app.py` or your entry point). Open the page that serves `/a` to see the Holding Snapshot section.

---

## 4. Refresh data (optional)

To keep monthly snapshots up to date, run the build script periodically (e.g. after n8n Daily Snapshot):

```bash
python scripts/build-holding-monthly-snapshots.py --sheets
```

If the app reads from this workspace’s `context/holding-monthly-snapshots.json`, refresh that file. If you deployed a copy into the app’s `context/`, re-run the deploy script or copy the JSON again after building.
