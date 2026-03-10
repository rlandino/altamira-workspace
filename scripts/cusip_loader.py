"""
Shared 13F helpers: CUSIP→ticker mapping from reference/cusip-to-ticker.json.
Used by copycat-13f, 13f-backtest, 13f-stock-screener.
"""

import json
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
DEFAULT_MAP_PATH = WORKSPACE / "reference" / "cusip-to-ticker.json"

_BUILTIN = {
    "037833100": "AAPL",
    "594918104": "MSFT",
    "023135106": "AMZN",
    "02079K305": "GOOGL",
    "02079K107": "GOOG",
    "30303M102": "META",
    "88160R101": "TSLA",
    "67066G104": "NVDA",
}

_cached: dict[str, str] | None = None


def get_cusip_to_ticker(map_path: Path | None = None) -> dict[str, str]:
    """Load CUSIP→ticker from reference file; fallback to built-in. Cached."""
    global _cached
    if _cached is not None:
        return _cached
    path = map_path or DEFAULT_MAP_PATH
    out = dict(_BUILTIN)
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                out.update(data)
        except (json.JSONDecodeError, OSError):
            pass
    _cached = out
    return out


def cusip_to_ticker(cusip: str, map_path: Path | None = None) -> str:
    """Return ticker for CUSIP or empty string if unknown."""
    cusip = (cusip or "").strip()
    if not cusip:
        return ""
    return get_cusip_to_ticker(map_path).get(cusip, "")
