# Add Holding Snapshot to Your Streamlit App

Your app shows **Portfolio Snapshots** with DAILY SNAPSHOTS and MONTHLY SNAPSHOTS but not the **Holding Snapshot** section (monthly table per ticker). Use one of these options.

---

## Option A — New sidebar page (easiest)

Add a separate **Holding Snapshot** item to the sidebar.

1. **Locate your Streamlit app folder** (the one that has `pages/` and the file that renders "Portfolio Snapshots" with DAILY SNAPSHOTS and MONTHLY SNAPSHOTS).

2. **Copy these two things into that app folder:**
   - **Page file:** Copy `outputs/pages/3_Holding_Snapshot.py` from this workspace into your app’s **`pages/`** folder (e.g. `pages/3_Holding_Snapshot.py`).
   - **Fragment:** Copy `streamlit_holding_snapshot.py` from the **root** of this workspace into the **root** of your Streamlit app (same folder as `app.py` or where `pages/` lives).

3. **Point the page at this workspace (if the app is not inside altamira-workspace):**  
   Set the env var **`ALTAMIRA_WORKSPACE`** to the full path of this workspace before starting Streamlit, e.g.:
   ```bash
   set ALTAMIRA_WORKSPACE=\\Landino-NAS\AI Automation\Claude\altamira-workspace
   streamlit run app.py
   ```
   (Or set it in your run script / environment.)  
   The page will then load `context/holding-monthly-snapshots.json` from that path. If your app already runs from inside this workspace, you don’t need to set it.

4. **Restart the Streamlit app.** You should see **Holding Snapshot** in the sidebar; open it to see the per-ticker monthly tables.

---

## Option B — Add to the existing Portfolio Snapshots page

If you want the Holding Snapshot section **on the same page** as DAILY SNAPSHOTS and MONTHLY SNAPSHOTS:

1. **Find the file that renders that page**  
   It’s the one that contains the "Portfolio Snapshots" title and the DAILY SNAPSHOTS / MONTHLY SNAPSHOTS tables (e.g. a file under `pages/` or your main app file).

2. **Copy `streamlit_holding_snapshot.py`** from the root of this workspace into the root of your Streamlit app (same folder as that file’s project).

3. **After the MONTHLY SNAPSHOTS section** (or at the end of the main content for that page), add:
   ```python
   from streamlit_holding_snapshot import render_holding_snapshot
   render_holding_snapshot()
   ```

4. **Set the data path** (if the app is not run from this workspace):  
   Before starting Streamlit, set:
   ```bash
   set HOLDING_SNAPSHOT_JSON=\\Landino-NAS\AI Automation\Claude\altamira-workspace\context\holding-monthly-snapshots.json
   ```

5. **Restart the app** and refresh the Portfolio Snapshots page.

---

## Data

- The section reads **`context/holding-monthly-snapshots.json`** from this workspace (or the path in `HOLDING_SNAPSHOT_JSON`).
- To refresh that file:  
  `python scripts/build-holding-monthly-snapshots.py --sheets`  
  (or `--file context/position-history-export.csv`).
