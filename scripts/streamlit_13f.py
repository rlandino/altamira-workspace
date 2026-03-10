"""
Streamlit fragment: 13F Holdings section for the Altamira Dashboard.

Renders 13F institutional holdings views: filers, holdings, diff, copycat,
screener, heat map, fund metrics. Data is fetched from the 13F API
(http://localhost:8000). Requires the 13F API to be running:
  python -m uvicorn scripts.13f_api:app --host 127.0.0.1 --port 8000

Integration: The Streamlit app that serves http://localhost:8501 is not in
this workspace. To add this section:
  1. Copy render_13f() (or import this module and call it) into a page that
     serves 13F or institutional holdings.
  2. Set 13F_API_URL to the API base URL if not http://localhost:8000.
  3. Ensure the 13F API is running (uvicorn scripts.13f_api:app --port 8000).

See reference/13f-dashboard-integration.md for deploy steps.
"""

import os
from pathlib import Path
from urllib.parse import urljoin

import streamlit as st

WORKSPACE = Path(__file__).resolve().parent.parent
DEFAULT_API_URL = os.environ.get("13F_API_URL", "http://localhost:8000")


def _api_url(path: str) -> str:
    base = os.environ.get("13F_API_URL", DEFAULT_API_URL).rstrip("/")
    return urljoin(base + "/", path.lstrip("/"))


def _fetch(path: str, params: dict | None = None) -> dict | None:
    import urllib.request
    import urllib.error
    import json
    url = _api_url(path)
    if params:
        from urllib.parse import urlencode
        url = f"{url}?{urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def _format_value(v, dollars: bool = False) -> str:
    if v is None:
        return "—"
    if dollars and isinstance(v, (int, float)):
        return f"${v:,.0f}"
    if isinstance(v, float) and abs(v) >= 0.01:
        return f"{v:,.2f}"
    return str(v)


def render_13f():
    """Render the 13F Holdings section. Call from a Streamlit page."""
    st.subheader("13F Institutional Holdings")

    # Health check
    health = _fetch("/api/13f/health")
    if health is None:
        st.warning(
            "13F API not reachable. Start it with: "
            "`python -m uvicorn scripts.13f_api:app --host 127.0.0.1 --port 8000`"
        )
        return
    if not health.get("data_dir_exists"):
        st.info("No 13F data yet. Run `python scripts/ingest-13f.py --cik-list context/13f-filers.txt`.")
        return

    # Tabs: Filers | Holdings | Diff | Copycat | Screener | Heat Map | Fund Metrics
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Filers", "Holdings", "Diff", "Copycat", "Screener", "Heat Map", "Fund Metrics"
    ])

    with tab1:
        data = _fetch("/api/13f/filers")
        if data and data.get("filings"):
            filings = data["filings"]
            sample_any = any(
                ("Sample Filer" in (f.get("name") or "")) or not (f.get("sourceUrl") or "").strip()
                for f in filings
            )
            if sample_any:
                st.warning(
                    "Sample data detected. Run `python scripts/ingest-13f.py --cik-list context/13f-filers.txt` "
                    "(without `--sample`) to fetch real SEC data."
                )
            rows = [
                {
                    "Fund": f.get("name", ""),
                    "Period": f.get("periodEnd", ""),
                    "Filed": f.get("filingDate", ""),
                    "# Holdings": f.get("holdingsCount", 0),
                }
                for f in filings[:50]
            ]
            st.dataframe(rows, use_container_width=True, hide_index=True)
            # Clickable: select a filing to pre-fill Holdings tab and optionally load
            st.markdown("**View Holdings** — select a row above, then click below to load it in the Holdings tab.")
            options = [
                f"{f.get('name', '')} — {f.get('periodEnd', '')} ({f.get('holdingsCount', 0)} holdings)"
                for f in filings[:50]
            ]
            filing_idx = st.selectbox(
                "Select a filing to view holdings",
                range(len(filings[:50])),
                format_func=lambda i: options[i] if 0 <= i < len(options) else "",
                key="filer_select",
            )
            if st.button("Load in Holdings tab", key="filer_view_btn"):
                f = filings[filing_idx]
                st.session_state["hold_cik"] = f.get("cik", "")
                pe = f.get("periodEnd", "")
                # Normalize period for display (YYYYMMDD -> YYYY-MM-DD if applicable)
                if pe and len(pe) == 8 and pe.isdigit():
                    pe = f"{pe[:4]}-{pe[4:6]}-{pe[6:8]}"
                st.session_state["hold_period"] = pe
                st.session_state["hold_auto_load"] = True
                st.success(f"Pre-filled Holdings with {f.get('name', '')} — {pe}. Switch to the **Holdings** tab to see results (or they may load automatically).")
        else:
            st.write("No filers. Ingest 13F data first.")

    with tab2:
        # Pre-fill from Filers tab selection (session state set when "Load in Holdings tab" is clicked)
        default_cik = st.session_state.get("hold_cik") or "0001067983"
        default_period = st.session_state.get("hold_period") or "2025-09-30"
        c1, c2 = st.columns(2)
        with c1:
            cik = st.text_input("CIK", value=default_cik, key="hold_cik")
        with c2:
            period = st.text_input("Period (YYYY-MM-DD or YYYYMMDD)", value=default_period, key="hold_period")
        auto_load = st.session_state.pop("hold_auto_load", False)
        if st.button("Load Holdings", key="hold_btn") or auto_load:
            data = _fetch("/api/13f/holdings", {"cik": cik.strip(), "period": period.strip()})
            if data and "holdings" in data:
                rows = [{"Issuer": h.get("nameOfIssuer") or h.get("issuer"), "CUSIP": h.get("cusip") or h.get("CUSIP"), "Value ($K)": _format_value(h.get("value") or (h.get("valueUsd") and h.get("valueUsd") / 1000), dollars=True)} for h in data["holdings"][:100]]
                st.dataframe(rows, use_container_width=True, hide_index=True)
            elif data and data.get("error"):
                st.error(data["error"])
            else:
                st.error(f"No filing found for CIK {cik}, period {period}. Pick a filing from the **Filers** tab and use \"Load in Holdings tab\" to use an exact CIK and period.")

    with tab3:
        c1, c2, c3 = st.columns(3)
        with c1:
            cik = st.text_input("CIK", value="0001067983", key="diff_cik")
        with c2:
            prior = st.text_input("Prior Period", value="2025-06-30", key="diff_prior")
        with c3:
            current = st.text_input("Current Period", value="2025-09-30", key="diff_current")
        if st.button("Load Diff", key="diff_btn"):
            data = _fetch("/api/13f/diff", {"cik": cik, "prior": prior, "current": current})
            if data and "diff" in data:
                d = data["diff"]
                for label, key in [("New Buys", "newBuys"), ("Sells", "sells"), ("Increased", "increased"), ("Decreased", "decreased")]:
                    arr = d.get(key) or []
                    with st.expander(f"{label} ({len(arr)})"):
                        if arr:
                            rows = [{"Issuer": x.get("name") or x.get("issuer") or x.get("nameOfIssuer"), "CUSIP": x.get("cusip") or x.get("CUSIP"), "Value ($K)": _format_value(x.get("value"), dollars=True)} for x in arr[:30]]
                            st.dataframe(rows, use_container_width=True, hide_index=True)
                        else:
                            st.write("—")
            elif data and data.get("error"):
                st.error(data["error"])

    with tab4:
        c1, c2, c3 = st.columns(3)
        with c1:
            ciks = st.text_input("CIKs (comma-separated)", value="0001067983,1350694", key="cc_ciks")
        with c2:
            weight = st.selectbox("Weight", ["value", "equal"], key="cc_weight")
        with c3:
            consensus_min = st.number_input("Consensus Min", min_value=0, value=0, key="cc_consensus")
        if st.button("Build Copycat", key="cc_btn"):
            params = {"ciks": ciks, "weight": weight}
            if consensus_min:
                params["consensus_min"] = consensus_min
            data = _fetch("/api/13f/copycat", params)
            if data and "tickers" in data:
                rows = data["tickers"][:50]
                st.dataframe(rows, use_container_width=True, hide_index=True)
                tickers_with_sym = [r.get("ticker") for r in rows if r.get("ticker")]
                if tickers_with_sym:
                    st.caption("Open Symbol Detail:")
                    n = min(15, len(tickers_with_sym))
                    cols = st.columns(5)
                    for i, t in enumerate(tickers_with_sym[:n]):
                        with cols[i % 5]:
                            st.page_link("pages/2_Symbol_Detail.py", label=t, query_params={"ticker": t})
            elif data and data.get("error"):
                st.error(data["error"])

    with tab5:
        c1, c2 = st.columns(2)
        with c1:
            min_filers = st.number_input("Min Filers", min_value=1, value=1, key="scr_min")
        with c2:
            min_value = st.number_input("Min Value ($K)", min_value=0, value=0, key="scr_val")
        if st.button("Run Screener", key="scr_btn"):
            params = {"min_filers": min_filers}
            if min_value:
                params["min_value"] = min_value
            data = _fetch("/api/13f/screener", params)
            if data and data.get("holdings"):
                rows = data["holdings"][:50]
                st.dataframe(rows, use_container_width=True, hide_index=True)
            elif data and data.get("error"):
                st.error(data["error"])

    with tab6:
        c1, c2 = st.columns(2)
        with c1:
            top_filers = st.number_input("Top Filers", min_value=5, value=10, key="hm_filers")
        with c2:
            top_cusips = st.number_input("Top CUSIPs", min_value=5, value=20, key="hm_cusips")
        if st.button("Load Heat Map", key="hm_btn"):
            data = _fetch("/api/13f/heatmap", {"top_filers": top_filers, "top_cusips": top_cusips})
            if data and "matrix" in data:
                import pandas as pd
                matrix = data.get("matrix") or []
                filers = data.get("filers") or []
                cusips = data.get("cusips") or []
                cusip_info = {c.get("cusip", ""): c.get("name", c.get("cusip", "")) for c in (data.get("cusipInfo") or [])}
                labels = [cusip_info.get(c, c)[:12] for c in cusips] if cusips else []
                df = pd.DataFrame(matrix, index=[f[:10] for f in filers], columns=labels or cusips)
                st.dataframe(df, use_container_width=True)
            elif data and data.get("error"):
                st.error(data["error"])

    with tab7:
        c1, c2, c3 = st.columns(3)
        with c1:
            cik = st.text_input("CIK", value="0001067983", key="fm_cik")
        with c2:
            prior = st.text_input("Prior (opt)", value="", key="fm_prior")
        with c3:
            current = st.text_input("Current (opt)", value="", key="fm_current")
        if st.button("Load Metrics", key="fm_btn"):
            params = {"cik": cik}
            if prior:
                params["prior"] = prior
            if current:
                params["current"] = current
            data = _fetch("/api/13f/fund-metrics", params)
            if data:
                if "metrics" in data:
                    m = data["metrics"]
                    st.metric("Holdings Count", m.get("holdingsCount", "—"))
                    st.metric("Top 5 %", f"{m.get('concentrationTop5Pct', 0):.1f}%")
                    st.metric("Top 10 %", f"{m.get('concentrationTop10Pct', 0):.1f}%")
                    st.metric("Top 20 %", f"{m.get('concentrationTop20Pct', 0):.1f}%")
                elif "overlapPct" in data:
                    st.metric("Overlap %", f"{data.get('overlapPct', 0):.1f}%")
                elif data.get("error"):
                    st.error(data["error"])

    st.caption("Source: 13F API at " + _api_url("/api/13f/health") + ". Run ingest-13f.py to load data.")


if __name__ == "__main__":
    st.set_page_config(page_title="13F Holdings", layout="wide")
    st.title("13F Institutional Holdings")
    render_13f()
