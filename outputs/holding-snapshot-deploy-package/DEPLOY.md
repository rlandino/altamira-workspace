# Holding Snapshot - Deploy from Claude Code Skills Factory

Run and deploy from this folder.

## 1. Generate data

```bash
cd "C:\Users\rland\OneDrive\Desktop\Claude Code Skills Factory\holding-snapshot-deploy"
python build-holding-monthly-snapshots.py --sheets
```
Or use `--file path\to\position-history.csv` or `--local`. Writes `context/holding-monthly-snapshots.json`.

## 2. Deploy to Streamlit app

**Option A - Sidebar page:** Copy `pages/3_Holding_Snapshot.py` into your app's `pages/` folder. Set before starting Streamlit:
- `HOLDING_SNAPSHOT_DEPLOY_DIR` = this folder path
- `HOLDING_SNAPSHOT_JSON` = this folder's `context/holding-monthly-snapshots.json`
- `PYTHONPATH` = this folder

**Option B - Add to Portfolio Snapshots page:** In that page add:
```python
import sys, os
sys.path.insert(0, r"C:\Users\rland\OneDrive\Desktop\Claude Code Skills Factory\holding-snapshot-deploy")
os.environ.setdefault("HOLDING_SNAPSHOT_JSON", r"C:\Users\rland\OneDrive\Desktop\Claude Code Skills Factory\holding-snapshot-deploy\context\holding-monthly-snapshots.json")
from streamlit_holding_snapshot import render_holding_snapshot
render_holding_snapshot()
```

## 3. Refresh data

Run `python build-holding-monthly-snapshots.py --sheets` from this folder.
