# Copy this file to your Streamlit app's pages/ folder.
# It loads the Holding Snapshot fragment and data from this deploy folder.

import os
import sys
from pathlib import Path

import streamlit as st

# Deploy folder: same folder that contains streamlit_holding_snapshot.py and context/
DEPLOY_DIR = Path(__file__).resolve().parent.parent
_ws = os.environ.get("HOLDING_SNAPSHOT_DEPLOY_DIR")
if _ws:
    DEPLOY_DIR = Path(_ws)
elif not (DEPLOY_DIR / "streamlit_holding_snapshot.py").exists():
    # Page is in app's pages/; deploy folder may be elsewhere
    DEPLOY_DIR = Path(os.environ.get("ALTAMIRA_WORKSPACE", r"C:\Users\rland\OneDrive\Desktop\Claude Code Skills Factory\holding-snapshot-deploy"))

sys.path.insert(0, str(DEPLOY_DIR))
os.environ.setdefault("HOLDING_SNAPSHOT_JSON", str(DEPLOY_DIR / "context" / "holding-monthly-snapshots.json"))

from streamlit_holding_snapshot import render_holding_snapshot

st.title("Portfolio Snapshots")
render_holding_snapshot()
