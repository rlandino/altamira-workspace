#!/usr/bin/env python3
"""
Deploy the Symbol Detail section to the Streamlit app.

Copies streamlit_symbol_detail.py and pages/2_Symbol_Detail.py into the app
directory so the Symbol Detail page is available at route 2_Symbol_Detail with
?ticker=SYMBOL. Other pages (e.g. Holding Snapshot, 13F) can link to it via
st.page_link("pages/2_Symbol_Detail.py", query_params={"ticker": symbol}).

Prerequisites:
  - Market Data API running (e.g. uvicorn scripts.market_data_api:app --port 8001)
  - FMP_API_KEY set in the environment or used by the API

Usage:
  python scripts/deploy-symbol-detail-to-app.py --app-dir "X:\\path\\to\\streamlit-app"

  # Only copy fragment (no page file):
  python scripts/deploy-symbol-detail-to-app.py --app-dir "X:\\path\\to\\app" --fragment-only

Env (in the Streamlit app):
  MARKET_DATA_API_URL — default http://localhost:8001
"""

import argparse
import shutil
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
FRAGMENT_SRC = WORKSPACE / "scripts" / "streamlit_symbol_detail.py"
PAGE_SRC = WORKSPACE / "pages" / "2_Symbol_Detail.py"


def deploy(app_dir: Path, fragment_only: bool) -> None:
    app_dir = app_dir.resolve()
    if not app_dir.is_dir():
        print(f"Not a directory: {app_dir}", file=sys.stderr)
        sys.exit(1)
    if not FRAGMENT_SRC.exists():
        print(f"Fragment not found: {FRAGMENT_SRC}", file=sys.stderr)
        sys.exit(1)

    dest_fragment = app_dir / "streamlit_symbol_detail.py"
    shutil.copy2(FRAGMENT_SRC, dest_fragment)
    print(f"Copied: {dest_fragment}")

    if not fragment_only and PAGE_SRC.exists():
        pages_dir = app_dir / "pages"
        pages_dir.mkdir(parents=True, exist_ok=True)
        dest_page = pages_dir / "2_Symbol_Detail.py"
        shutil.copy2(PAGE_SRC, dest_page)
        print(f"Copied: {dest_page}")
        print("Symbol Detail will appear in the sidebar. Open with ?ticker=SYMBOL or from ticker links.")
    elif fragment_only:
        print("Skipped page file (--fragment-only). Add a page that imports render_symbol_detail and reads st.query_params.get('ticker').")
    else:
        print(f"Page file not found: {PAGE_SRC}. Add pages/2_Symbol_Detail.py manually (see reference/symbol-detail-dashboard.md).")

    print("\nEnsure Market Data API is running (port 8001) and set MARKET_DATA_API_URL if needed.")


def main() -> None:
    ap = argparse.ArgumentParser(description="Deploy Symbol Detail section to Streamlit app.")
    ap.add_argument("--app-dir", type=Path, help="Path to Streamlit app root (where app.py or pages/ live)")
    ap.add_argument("--fragment-only", action="store_true", help="Only copy streamlit_symbol_detail.py; do not copy page")
    args = ap.parse_args()

    if not args.app_dir:
        print("Usage: python scripts/deploy-symbol-detail-to-app.py --app-dir <path-to-streamlit-app>", file=sys.stderr)
        sys.exit(1)

    deploy(args.app_dir, fragment_only=args.fragment_only)


if __name__ == "__main__":
    main()
