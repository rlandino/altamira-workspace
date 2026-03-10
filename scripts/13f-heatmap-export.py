#!/usr/bin/env python3
"""
Altamira Capital — 13F Heat Map Export
======================================
Export 13F exposure as a matrix (filers x CUSIPs or CUSIPs x filers) for visualization
(heat map in dashboard or Excel). Reads ingested 13F JSON.

Usage:
  # JSON: { filers: [], cusips: [], matrix: [[value_thousands]] }
  python scripts/13f-heatmap-export.py

  # CSV: rows = filers, columns = CUSIPs (or --transpose for CUSIPs x filers)
  python scripts/13f-heatmap-export.py --format csv --out outputs/13f-heatmap.csv

  # Limit to top N filers and top M CUSIPs by value
  python scripts/13f-heatmap-export.py --top-filers 20 --top-cusips 50
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


def build_matrix(data_dir: Path, top_filers: int | None, top_cusips: int | None) -> tuple[list[str], list[str], list[dict], dict[tuple[str, str], float]]:
    """
    Load all filings, return (filer_ciks, cusips, cusip_info, (filer_cik, cusip) -> value).
    cusip_info: list of {cusip, name} for labels.
    """
    data_dir = Path(data_dir).resolve()
    filer_values: dict[str, float] = {}
    cusip_values: dict[str, float] = {}
    cusip_names: dict[str, str] = {}
    matrix: dict[tuple[str, str], float] = {}
    filer_names: dict[str, str] = {}

    for f in sorted(data_dir.glob("*.json")):
        try:
            with open(f, encoding="utf-8") as fp:
                filing = json.load(fp)
        except (json.JSONDecodeError, OSError):
            continue
        filer = filing.get("filer") or {}
        fcik = filer.get("cik") or f.stem.split("_")[0]
        fname = filer.get("name") or fcik
        filer_names[fcik] = fname
        for h in filing.get("holdings") or []:
            cusip = _cusip(h)
            if not cusip:
                continue
            val = _value(h)
            cusip_names[cusip] = _name(h)
            filer_values[fcik] = filer_values.get(fcik, 0) + val
            cusip_values[cusip] = cusip_values.get(cusip, 0) + val
            matrix[(fcik, cusip)] = matrix.get((fcik, cusip), 0) + val

    filers = sorted(filer_values.keys(), key=lambda x: -filer_values[x])
    cusips = sorted(cusip_values.keys(), key=lambda x: -cusip_values[x])
    if top_filers:
        filers = filers[:top_filers]
    if top_cusips:
        cusips = cusips[:top_cusips]
    cusip_info = [{"cusip": c, "name": cusip_names.get(c, "")} for c in cusips]
    return filers, cusips, cusip_info, matrix


def main() -> int:
    ap = argparse.ArgumentParser(description="Export 13F heat map matrix.")
    ap.add_argument("--data-dir", type=str, default=str(DEFAULT_DATA_DIR), help="13F JSON directory")
    ap.add_argument("--top-filers", type=int, default=None, help="Limit to top N filers by value")
    ap.add_argument("--top-cusips", type=int, default=None, help="Limit to top M CUSIPs by value")
    ap.add_argument("--format", type=str, choices=("json", "csv"), default="json", help="Output format")
    ap.add_argument("--transpose", action="store_true", help="CSV: rows = CUSIPs, cols = filers")
    ap.add_argument("--out", type=str, help="Write to file")
    args = ap.parse_args()

    data_dir = Path(args.data_dir).resolve()
    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}", file=sys.stderr)
        return 1

    filers, cusips, cusip_info, matrix = build_matrix(data_dir, args.top_filers, args.top_cusips)

    if args.format == "csv":
        dest = open(args.out, "w", newline="", encoding="utf-8") if args.out else sys.stdout
        try:
            w = csv.writer(dest)
            if args.transpose:
                w.writerow(["cusip", "name"] + filers)
                name_by_cusip = {x["cusip"]: x["name"] for x in cusip_info}
                for c in cusips:
                    row = [c, name_by_cusip.get(c, "")]
                    for f in filers:
                        row.append(matrix.get((f, c), 0))
                    w.writerow(row)
            else:
                w.writerow(["filer"] + cusips)
                for f in filers:
                    row = [f]
                    for c in cusips:
                        row.append(matrix.get((f, c), 0))
                    w.writerow(row)
        finally:
            if args.out:
                dest.close()
                print(f"Wrote {args.out}", file=sys.stderr)
    else:
        # JSON: matrix as list of rows (filers x cusips)
        grid = [[matrix.get((f, c), 0) for c in cusips] for f in filers]
        out = {
            "filers": filers,
            "cusips": cusips,
            "cusipInfo": cusip_info,
            "matrix": grid,
        }
        s = json.dumps(out, indent=2)
        if args.out:
            Path(args.out).write_text(s, encoding="utf-8")
            print(f"Wrote {args.out}", file=sys.stderr)
        else:
            print(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
