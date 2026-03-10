# Paste this into the Streamlit page that serves route /a (Portfolio Snapshots).
# Ensure streamlit_holding_snapshot.py is in the app directory (or on PYTHONPATH).

# Holding Snapshot (monthly table per holding)
from streamlit_holding_snapshot import render_holding_snapshot
render_holding_snapshot()
