"""
Streamlit fragment: Holding Snapshot section for the Portfolio Snapshots page.

Renders a monthly snapshot table per holding: Month, Qty, Ticker, Cost Basis, Month Chg ($), Month Chg (%).
Data: context/holding-monthly-snapshots.json in this folder (or HOLDING_SNAPSHOT_JSON).
"""

from pathlib import Path

import streamlit as st

_DEPLOY_DIR = Path(__file__).resolve().parent
_DEFAULT_JSON = _DEPLOY_DIR / "context" / "holding-monthly-snapshots.json"


def _snapshot_json_path() -> Path:
    import os
    env_path = os.environ.get("HOLDING_SNAPSHOT_JSON", "").strip()
    if env_path:
        return Path(env_path)
    return _DEFAULT_JSON


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
    """Render the Holding Snapshot section."""
    st.subheader("Holding Snapshot")

    data = _load_snapshot_data()
    if not data:
        st.info(
            "Run `build-holding-monthly-snapshots.py` in this folder to generate monthly snapshot data. "
            "Use `--sheets` (GOOGLE_SHEET_ID + GOOGLE_APPLICATION_CREDENTIALS) or `--file path/to/position-history.csv`."
        )
        return

    for item in data:
        ticker = item.get("ticker", "")
        rows = item.get("rows", [])
        if not rows:
            continue
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

    st.caption("Source: context/holding-monthly-snapshots.json in this deploy folder. Re-run build script to refresh.")


if __name__ == "__main__":
    st.set_page_config(page_title="Holding Snapshot", layout="wide")
    st.title("Portfolio Snapshots")
    render_holding_snapshot()
