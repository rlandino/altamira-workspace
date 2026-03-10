# Deploy Holding Snapshot to Your Streamlit App

**Deploy from Claude Code Skills Factory:** A full deploy package is at  
`C:\Users\rland\OneDrive\Desktop\Claude Code Skills Factory\holding-snapshot-deploy`  
— run the build script and copy `pages/3_Holding_Snapshot.py` from there. See that folder's `DEPLOY.md`.

Your Portfolio Snapshots app (with DAILY SNAPSHOTS / MONTHLY SNAPSHOTS) is not in this repo. To show **Holding Snapshot** (monthly table per ticker), use one of these:

---

## Option A — Add as a sidebar page (easiest)

1. **Copy the page file** into your Streamlit app’s `pages/` folder:
   - From this repo: **`outputs/pages/3_Holding_Snapshot.py`**
   - To your app: **`<your-app>/pages/3_Holding_Snapshot.py`**

2. **Point the page at this workspace** (so it can load the fragment and data):
   - Either set env before starting Streamlit:
     ```bash
     set ALTAMIRA_WORKSPACE=X:\Claude\altamira-workspace
     streamlit run app.py
     ```
   - Or if your app is on the NAS, the default path in the page may already work.

3. **Restart the app.** You should see **Holding Snapshot** in the sidebar.

---

## Option B — Add to the existing Portfolio Snapshots page

1. In your app repo, open the file that renders the **Portfolio Snapshots** page (the one with DAILY SNAPSHOTS and MONTHLY SNAPSHOTS).
2. After the MONTHLY SNAPSHOTS section, add:
   ```python
   from streamlit_holding_snapshot import render_holding_snapshot
   render_holding_snapshot()
   ```
3. Copy **`streamlit_holding_snapshot.py`** from this repo’s root into your app folder (or put this repo on `PYTHONPATH`).
4. Set **`HOLDING_SNAPSHOT_JSON`** to the path of **`context/holding-monthly-snapshots.json`** (or copy that file into your app’s `context/`).

---

## Data refresh

From this repo:

```bash
python scripts/build-holding-monthly-snapshots.py --sheets
# or
python scripts/build-holding-monthly-snapshots.py --local
```

This updates `context/holding-monthly-snapshots.json`. If your app reads that file from this workspace (via `ALTAMIRA_WORKSPACE` or `HOLDING_SNAPSHOT_JSON`), refresh the browser to see new data.
