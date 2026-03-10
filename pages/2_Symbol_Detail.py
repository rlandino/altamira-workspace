# Add this file to your Streamlit app's pages/ folder (e.g. pages/2_Symbol_Detail.py).
# Symbol Detail is reachable with ?ticker=SYMBOL. Set ALTAMIRA_WORKSPACE if the fragment is in workspace/scripts.

import sys
from pathlib import Path

import streamlit as st

_root = Path(__file__).resolve().parent.parent
_scripts = _root / "scripts"
if (_scripts / "streamlit_symbol_detail.py").exists():
    sys.path.insert(0, str(_scripts))
else:
    sys.path.insert(0, str(_root))

from streamlit_symbol_detail import render_symbol_detail

ticker = st.query_params.get("ticker")
if ticker:
    st.title(f"Symbol Detail — {ticker}")
    render_symbol_detail(ticker)
else:
    st.title("Symbol Detail")
    st.info("Open this page with a ticker: use a link from Portfolio or enter a symbol below.")
    manual = st.text_input("Ticker", placeholder="e.g. WM", key="symbol_input")
    if manual and manual.strip():
        render_symbol_detail(manual.strip())
    else:
        st.caption("Or navigate from any section that shows a ticker (click the ticker to open Symbol Detail).")
