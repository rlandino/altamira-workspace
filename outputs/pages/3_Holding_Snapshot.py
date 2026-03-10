# Add this file to your Streamlit app's pages/ folder (e.g. pages/3_Holding_Snapshot.py).
# It will add "Holding Snapshot" to the sidebar and show monthly snapshot tables per ticker.
# Set ALTAMIRA_WORKSPACE to the path of altamira-workspace if the default is wrong.

import os
import sys
from pathlib import Path

import streamlit as st

# Path to altamira-workspace (so we can import the fragment and find the JSON)
_app_root = Path(__file__).resolve().parent.parent
_ws = os.environ.get("ALTAMIRA_WORKSPACE")
if _ws:
    ALTAMIRA_WORKSPACE = Path(_ws)
else:
    for _candidate in [
        Path(r"\\Landino-NAS\AI Automation\Claude\altamira-workspace"),
        _app_root.parent / "altamira-workspace",
        _app_root,
    ]:
        _json = _candidate / "context" / "holding-monthly-snapshots.json"
        if _json.exists():
            ALTAMIRA_WORKSPACE = _candidate
            break
    else:
        ALTAMIRA_WORKSPACE = Path(r"\\Landino-NAS\AI Automation\Claude\altamira-workspace")

sys.path.insert(0, str(ALTAMIRA_WORKSPACE))
os.environ.setdefault("HOLDING_SNAPSHOT_JSON", str(ALTAMIRA_WORKSPACE / "context" / "holding-monthly-snapshots.json"))

from streamlit_holding_snapshot import render_holding_snapshot

st.title("Portfolio Snapshots")
render_holding_snapshot()
