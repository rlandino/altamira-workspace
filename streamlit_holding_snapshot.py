"""
Streamlit fragment: Holding Snapshot section for the Portfolio Snapshots page (/a).

Renders under "Portfolio Snapshots" a subheading "Holding Snapshot" and, for each
portfolio holding, a monthly snapshot table with columns: Month, Qty, Ticker,
Cost Basis, Month Chg ($), Month Chg (%).

Data: reads from context/holding-monthly-snapshots.json (produced by
scripts/build-holding-monthly-snapshots.py). If the file is missing, shows a
message asking the user to run the build script.

Integration: The Streamlit app that serves http://localhost:8501/a is not in
this workspace. To add this section:
  1. Copy the contents of render_holding_snapshot() (or import this module and
     call it) into the page that serves /a, under the "Portfolio Snapshots" heading.
  2. Ensure the app's working directory or data path includes context/ relative to
     this workspace, or set HOLDING_SNAPSHOT_JSON to the full path of
     holding-monthly-snapshots.json.
  3. Optional: run scripts/build-holding-monthly-snapshots.py (e.g. via cron or
     n8n) so the JSON is refreshed from Position History.

See reference/holding-snapshot-dashboard.md for integration notes.
"""

from pathlib import Path

import streamlit as st

# Path to monthly snapshot data: prefer env, then app_dir/context (deployed), then workspace/context (run from scripts/)
_SCRIPT_DIR = Path(__file__).resolve().parent
_DEFAULT_IN_APP = _SCRIPT_DIR / "context" / "holding-monthly-snapshots.json"
_DEFAULT_IN_WORKSPACE = _SCRIPT_DIR.parent / "context" / "holding-monthly-snapshots.json"


def _snapshot_json_path() -> Path:
    import os
    env_path = os.environ.get("HOLDING_SNAPSHOT_JSON", "").strip()
    if env_path:
        return Path(env_path)
    if _DEFAULT_IN_APP.exists():
        return _DEFAULT_IN_APP
    return _DEFAULT_IN_WORKSPACE


def _load_snapshot_data():
    path = _snapshot_json_path()
    if not path.exists():
        return None
    import json
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _format_value(v, dollars=False, pct=False):
    if v is None:
        return ""
    if pct:
        return f"{v:.2f}%"
    if dollars and isinstance(v, (int, float)):
        return f"${v:,.2f}"
    if isinstance(v, float):
        return f"{v:,.2f}" if abs(v) >= 0.01 else f"{v:.4f}"
    return str(v)


def render_holding_snapshot():
    """Render the Holding Snapshot section. Call this from the page that serves /a."""
    st.subheader("Holding Snapshot")

    data = _load_snapshot_data()
    if not data:
        st.info(
            "Run `scripts/build-holding-monthly-snapshots.py` to generate monthly snapshot data. "
            "Use `--sheets` (with GOOGLE_SHEET_ID and GOOGLE_APPLICATION_CREDENTIALS) or "
            "`--file context/position-history-export.csv`."
        )
        return

    for item in data:
        ticker = item.get("ticker", "")
        rows = item.get("rows", [])
        if not rows:
            continue
        # Build table rows for display: Month, Qty, Ticker, Cost Basis, Month Chg ($), Month Chg (%)
        table_rows = []
        for r in rows:
            table_rows.append({
                "Month": r.get("date") or r.get("month") or "—",
                "Qty": r.get("qty"),
                "Ticker": r.get("ticker", ticker),
                "Cost Basis": _format_value(r.get("costBasis"), dollars=True) or "—",
                "Month Chg ($)": _format_value(r.get("monthChgDollar"), dollars=True) or "—",
                "Month Chg (%)": _format_value(r.get("monthChgPct"), pct=True) or "—",
            })
        with st.expander(f"**{ticker}** ({len(table_rows)} months)"):
            st.dataframe(table_rows, use_container_width=True, hide_index=True)

    st.caption("Source: context/holding-monthly-snapshots.json. Refresh by running build-holding-monthly-snapshots.py.")


if __name__ == "__main__":
    # Allow running this file alone to preview the section (requires: pip install streamlit)
    st.set_page_config(page_title="Holding Snapshot", layout="wide")
    st.title("Portfolio Snapshots")
    render_holding_snapshot()
