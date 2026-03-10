#!/usr/bin/env python3
"""
Altamira Capital — 13F Query / Export
=====================================
Query ingested 13F JSON (from ingest-13f.py) by filer, period, or CUSIP/ticker.
Output: JSON to stdout or export to file. For use by holdings-diff, copycat-portfolio, dashboard.

Usage:
  # List available filers and periods
  python scripts/query-13f.py --list

  # Get holdings for a filer and period (period_end = YYYY-MM-DD or YYYYMMDD)
  python scripts/query-13f.py --cik 0001067983 --period 2025-09-30

  # Filter by CUSIP
  python scripts/query-13f.py --cik 0001067983 --period 20250930 --cusip 037833100

  # Data directory (default: outputs/13f)
  python scripts/query-13f.py --list --data-dir outputs/13f
"""

import argparse
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = WORKSPACE / "outputs" / "13f"


def _normalize_period(period: str) -> str:
    """Normalize period to YYYYMMDD for filename match."""
    s = (period or "").replace("-", "").strip()
    if len(s) == 8:
        return s
    if len(s) == 6:
        return s + "01"  # YYYYMM -> YYYYMM01
    return s


def list_filers(data_dir: Path, rich: bool = True) -> list[dict]:
    """List filers and periods from JSON filenames. Returns list of {cik, periodEnd, path[, name, filingDate, holdingsCount, sourceUrl]}."""
    data_dir = Path(data_dir).resolve()
    if not data_dir.exists():
        return []
    out = []
    for f in sorted(data_dir.glob("*.json")):
        stem = f.stem
        if "_" in stem:
            cik, period = stem.split("_", 1)
            rec = {"cik": cik, "periodEnd": period, "path": str(f)}
            if rich:
                try:
                    with open(f, encoding="utf-8") as fp:
                        j = json.load(fp)
                    filer = j.get("filer") or {}
                    rec["name"] = filer.get("name", "")
                    rec["filingDate"] = filer.get("filingDate", "")
                    rec["holdingsCount"] = j.get("holdingsCount", len(j.get("holdings", [])))
                    rec["sourceUrl"] = j.get("sourceUrl", "")
                except (json.JSONDecodeError, OSError):
                    rec["name"] = rec["filingDate"] = ""
                    rec["holdingsCount"] = 0
                    rec["sourceUrl"] = ""
            out.append(rec)
    return out


def load_filing(data_dir: Path, cik: str, period: str) -> dict | None:
    """Load one filing JSON by CIK and period. Returns parsed JSON or None."""
    data_dir = Path(data_dir).resolve()
    cik = str(cik).strip().zfill(10)
    period_norm = _normalize_period(period)
    # Try exact match then prefix
    for pattern in (f"{cik}_{period_norm}.json", f"{cik}_{period_norm}*.json"):
        for f in data_dir.glob(pattern):
            with open(f, encoding="utf-8") as fp:
                return json.load(fp)
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Query 13F ingested JSON.")
    ap.add_argument("--list", action="store_true", help="List filers with fund name, filing date, holdings count")
    ap.add_argument("--no-rich", action="store_true", dest="no_rich", help="List only cik/period/path")
    ap.add_argument("--cik", type=str, help="Filer CIK")
    ap.add_argument("--period", type=str, help="Period end (YYYY-MM-DD or YYYYMMDD)")
    ap.add_argument("--cusip", type=str, help="Filter holdings by CUSIP")
    ap.add_argument("--data-dir", type=str, default=str(DEFAULT_DATA_DIR), help="13F JSON directory")
    ap.add_argument("--out", type=str, help="Write output to file instead of stdout")
    args = ap.parse_args()

    data_dir = Path(args.data_dir).resolve()

    if args.list:
        rich = not getattr(args, "no_rich", False)
        filers = list_filers(data_dir, rich=rich)
        out = {"count": len(filers), "filings": filers}
        s = json.dumps(out, indent=2)
        if args.out:
            Path(args.out).write_text(s, encoding="utf-8")
            print(f"Wrote {args.out}", file=sys.stderr)
        else:
            print(s)
        return 0

    if not args.cik or not args.period:
        print("Use --cik and --period to get holdings, or --list to list filings.", file=sys.stderr)
        return 1

    filing = load_filing(data_dir, args.cik, args.period)
    if not filing:
        print(f"No filing found for CIK {args.cik} period {args.period}", file=sys.stderr)
        return 1

    holdings = filing.get("holdings") or []
    if args.cusip:
        cusip = args.cusip.strip()
        holdings = [h for h in holdings if (h.get("cusip") or "").strip() == cusip]

    out = {**filing, "holdings": holdings, "holdingsCount": len(holdings)}
    s = json.dumps(out, indent=2)
    if args.out:
        Path(args.out).write_text(s, encoding="utf-8")
        print(f"Wrote {args.out}", file=sys.stderr)
    else:
        print(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
