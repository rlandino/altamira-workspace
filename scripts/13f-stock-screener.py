#!/usr/bin/env python3
"""
Altamira Capital — 13F Stock Screener & Combined Holdings
=========================================================
Screen by 13F institutional ownership: which filers hold each name, aggregate value,
and consensus (names held by N+ filers). Reads all ingested 13F JSON in data-dir.

Usage:
  # All names with aggregate value and filer count (sorted by value)
  python scripts/13f-stock-screener.py

  # Only names held by at least 2 filers (consensus)
  python scripts/13f-stock-screener.py --min-filers 2

  # Filter by minimum aggregate value (thousands)
  python scripts/13f-stock-screener.py --min-value 50000

  # Output CSV for heat map or dashboard
  python scripts/13f-stock-screener.py --format csv --out outputs/13f-screener.csv
"""

import argparse
import csv
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = WORKSPACE / "outputs" / "13f"


def _value(h: dict) -> float:
    v = h.get("value")
    if v is not None:
        return float(v)
    v = h.get("valueUsd")
    if v is not None:
        return float(v) / 1000
    return 0.0


def _cusip(h: dict) -> str:
    return (h.get("cusip") or h.get("CUSIP") or "").strip()


def _name(h: dict) -> str:
    return (h.get("nameOfIssuer") or h.get("issuer") or "").strip()


def aggregate_all(data_dir: Path) -> dict[str, dict]:
    """
    Aggregate holdings across all JSON filings. Returns dict cusip -> {
      name, totalValueThousands, filerCount, filerCiks, filerNames
    }
    """
    data_dir = Path(data_dir).resolve()
    by_cusip: dict[str, dict] = {}
    for f in data_dir.glob("*.json"):
        try:
            with open(f, encoding="utf-8") as fp:
                filing = json.load(fp)
        except (json.JSONDecodeError, OSError):
            continue
        filer = filing.get("filer") or {}
        filer_cik = filer.get("cik") or ""
        filer_name = filer.get("name") or filer_cik
        for h in filing.get("holdings") or []:
            cusip = _cusip(h)
            if not cusip:
                continue
            val = _value(h)
            name = _name(h)
            if cusip not in by_cusip:
                by_cusip[cusip] = {
                    "cusip": cusip,
                    "ticker": cusip_loader.cusip_to_ticker(cusip) or None,
                    "name": name,
                    "totalValueThousands": 0.0,
                    "filerCount": 0,
                    "filerCiks": [],
                    "filerNames": [],
                }
            by_cusip[cusip]["totalValueThousands"] += val
            if filer_cik not in by_cusip[cusip]["filerCiks"]:
                by_cusip[cusip]["filerCount"] += 1
                by_cusip[cusip]["filerCiks"].append(filer_cik)
                by_cusip[cusip]["filerNames"].append(filer_name)
    return by_cusip


def main() -> int:
    ap = argparse.ArgumentParser(description="13F stock screener: aggregate ownership by CUSIP.")
    ap.add_argument("--min-filers", type=int, default=1, help="Minimum number of filers holding (default 1)")
    ap.add_argument("--min-value", type=float, default=0, help="Minimum aggregate value (thousands)")
    ap.add_argument("--data-dir", type=str, default=str(DEFAULT_DATA_DIR), help="13F JSON directory")
    ap.add_argument("--format", type=str, choices=("json", "csv"), default="json", help="Output format")
    ap.add_argument("--out", type=str, help="Write to file")
    args = ap.parse_args()

    data_dir = Path(args.data_dir).resolve()
    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}", file=sys.stderr)
        return 1

    by_cusip = aggregate_all(data_dir)
    rows = [
        v for v in by_cusip.values()
        if v["filerCount"] >= args.min_filers and v["totalValueThousands"] >= args.min_value
    ]
    rows.sort(key=lambda x: -x["totalValueThousands"])

    if args.format == "csv":
        dest = open(args.out, "w", newline="", encoding="utf-8") if args.out else sys.stdout
        try:
            w = csv.writer(dest)
            w.writerow(["cusip", "name", "totalValueThousands", "filerCount", "filerNames"])
            for r in rows:
                w.writerow([r["cusip"], r["name"], r["totalValueThousands"], r["filerCount"], "|".join(r["filerNames"])])
        finally:
            if args.out:
                dest.close()
                print(f"Wrote {args.out}", file=sys.stderr)
    else:
        out = {"count": len(rows), "holdings": rows}
        s = json.dumps(out, indent=2)
        if args.out:
            Path(args.out).write_text(s, encoding="utf-8")
            print(f"Wrote {args.out}", file=sys.stderr)
        else:
            print(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
