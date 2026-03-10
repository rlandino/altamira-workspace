#!/usr/bin/env python3
"""Launch the regime trading Streamlit app (run from workspace root or scripts/)."""
import sys
from pathlib import Path

scripts = Path(__file__).resolve().parent
if str(scripts) not in sys.path:
    sys.path.insert(0, str(scripts))

import streamlit.web.cli as stcli
sys.argv = ["streamlit", "run", str(scripts / "regime_trading" / "app.py"), "--server.headless", "true"]
stcli.main()
