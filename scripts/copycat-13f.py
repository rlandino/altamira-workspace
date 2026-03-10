#!/usr/bin/env python3
"""
Altamira Capital — 13F Copycat Portfolio
========================================
Build a target portfolio that mirrors selected managers' latest 13F holdings.
Supports equal-weight, value-weighted, or consensus (only positions held by N of M filers).
Uses data from ingest-13f.py (outputs/13f).

Usage:
  # One filer, value-weighted (default)
  python scripts/copycat-13f.py --ciks 0001067983

  # Multiple filers, equal-weight across names
  python scripts/copycat-13f.py --ciks 0001067983,1350694 --weight equal

  # Consensus: only names held by at least 2 of the selected filers
  python scripts/copycat-13f.py --ciks 0001067983,1350694 --consensus-min 2

  # Output to file for dashboard
  python scripts/copycat-13f.py --ciks 0001067983 --out outputs/copycat-berkshire.json

  # Specify period (default: latest available per filer)
  python scripts/copycat-13f.py --ciks 0001067983 --period 2025-09-30
"""

import argparse
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import cusip_loader
DEFAULT_DATA_DIR = WORKSPACE / "outputs" / "13f"


def _normalize_period(period: str) -> str:
    s = (period or "").replace("-", "").strip()
    if len(s) == 8:
        return s
    if len(s) == 6:
        return s + "01"
    return s


def list_filings_for_cik(data_dir: Path, cik: str) -> list[tuple[str, Path]]:
    """Return (period_end, path) for each filing of this CIK, newest first."""
    data_dir = Path(data_dir).resolve()
    cik = str(cik).strip().zfill(10)
    out = []
    for f in data_dir.glob(f"{cik}_*.json"):
        stem = f.stem
        if "_" in stem:
            _, period = stem.split("_", 1)
            out.append((period, f))
    out.sort(key=lambda x: x[0], reverse=True)
    return out


def load_filing(path: Path) -> dict | None:
    with open(path, encoding="utf-8") as fp:
        return json.load(fp)


def load_latest_per_filer(data_dir: Path, ciks: list[str], period_hint: str | None) -> list[dict]:
    """Load one filing per CIK (latest or matching period_hint). Returns list of filing dicts."""
    data_dir = Path(data_dir).resolve()
    out = []
    for cik in ciks:
        cik = str(cik).strip().zfill(10)
        filings = list_filings_for_cik(data_dir, cik)
        if not filings:
            continue
        if period_hint:
            period_norm = _normalize_period(period_hint)
            for p, path in filings:
                if p == period_norm or p.startswith(period_norm[:6]):
                    out.append(load_filing(path))
                    break
            else:
                if filings:
                    out.append(load_filing(filings[0][1]))
        else:
            out.append(load_filing(filings[0][1]))
    return out


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


def build_copycat(
    filings: list[dict],
    weight: str = "value",
    consensus_min: int | None = None,
) -> dict:
    """
    Combine holdings from one or more filings into a single target portfolio.
    weight: "value" (by reported value), "equal" (equal weight per name)
    consensus_min: if set, only include names held by at least this many filers
    Returns: { tickers: [{ cusip, name, weightPct, valueUsd, filerCount }], totalValue, ... }
    """
    # Aggregate by CUSIP across filers: list of (value, filer_cik) per CUSIP
    by_cusip: dict[str, list[tuple[float, str]]] = {}
    for filing in filings:
        filer_cik = (filing.get("filer") or {}).get("cik") or ""
        filer_name = (filing.get("filer") or {}).get("name") or ""
        for h in filing.get("holdings") or []:
            cusip = _cusip(h)
            if not cusip:
                continue
            val = _value(h)
            name = _name(h)
            if cusip not in by_cusip:
                by_cusip[cusip] = []
            by_cusip[cusip].append((val, filer_cik, name))

    # Apply consensus filter
    if consensus_min is not None and consensus_min > 0:
        by_cusip = {
            c: entries
            for c, entries in by_cusip.items()
            if len(set(e[1] for e in entries)) >= consensus_min
        }

    # Total value (sum of unique value per CUSIP: take max value per CUSIP for value-weight, or sum across filers then average - for copycat we usually want one value per name; take max across filers as "reported value" for that name)
    total_value = 0.0
    cusip_to_value: dict[str, float] = {}
    cusip_to_name: dict[str, str] = {}
    cusip_to_filer_count: dict[str, int] = {}
    for cusip, entries in by_cusip.items():
        # Use max value across filers as the "position size" for that name (or sum for aggregate institutional interest)
        vals = [e[0] for e in entries]
        names = [e[2] for e in entries if e[2]]
        cusip_to_value[cusip] = max(vals) if weight == "value" else sum(vals) / max(len(vals), 1)
        cusip_to_name[cusip] = names[0] if names else ""
        cusip_to_filer_count[cusip] = len(set(e[1] for e in entries))
        total_value += cusip_to_value[cusip]

    n_filers = len(filings)
    if total_value <= 0:
        return {
            "tickers": [],
            "totalValue": 0,
            "weight": weight,
            "consensusMin": consensus_min,
            "filerCount": n_filers,
            "filers": [(f.get("filer") or {}).get("name") or (f.get("filer") or {}).get("cik") for f in filings],
        }

    # Weights
    tickers = []
    for cusip in sorted(cusip_to_value.keys(), key=lambda c: -cusip_to_value[c]):
        v = cusip_to_value[cusip]
        weight_pct = (v / total_value) * 100.0
        if weight == "equal":
            weight_pct = 100.0 / len(cusip_to_value)
        ticker = cusip_loader.cusip_to_ticker(cusip)
        tickers.append({
            "cusip": cusip,
            "ticker": ticker or None,
            "name": cusip_to_name[cusip],
            "valueUsd": round(v * 1000, 0),
            "weightPct": round(weight_pct, 4),
            "filerCount": cusip_to_filer_count[cusip],
        })

    if weight == "equal":
        total_value = sum(cusip_to_value[c] for c in cusip_to_value)

    return {
        "tickers": tickers,
        "totalValue": round(total_value * 1000, 0),
        "totalValueThousands": round(total_value, 2),
        "weight": weight,
        "consensusMin": consensus_min,
        "filerCount": n_filers,
        "filers": [(f.get("filer") or {}).get("name") or (f.get("filer") or {}).get("cik") for f in filings],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Build 13F copycat portfolio from selected filers.")
    ap.add_argument("--ciks", type=str, required=True, help="Comma-separated CIKs (e.g. 0001067983,1350694)")
    ap.add_argument("--period", type=str, help="Period end (YYYY-MM-DD or YYYYMMDD); default latest per filer")
    ap.add_argument("--weight", type=str, choices=("value", "equal"), default="value", help="Weighting: value or equal")
    ap.add_argument("--consensus-min", type=int, default=None, help="Only names held by at least N filers")
    ap.add_argument("--data-dir", type=str, default=str(DEFAULT_DATA_DIR), help="13F JSON directory")
    ap.add_argument("--out", type=str, help="Write JSON to file")
    args = ap.parse_args()

    data_dir = Path(args.data_dir).resolve()
    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}", file=sys.stderr)
        return 1

    ciks = [c.strip() for c in args.ciks.split(",") if c.strip()]
    if not ciks:
        print("Provide at least one CIK in --ciks.", file=sys.stderr)
        return 1

    filings = load_latest_per_filer(data_dir, ciks, args.period)
    if not filings:
        print("No filings found for the given CIKs/period.", file=sys.stderr)
        return 1

    result = build_copycat(filings, weight=args.weight, consensus_min=args.consensus_min)
    s = json.dumps(result, indent=2)
    if args.out:
        Path(args.out).write_text(s, encoding="utf-8")
        print(f"Wrote {args.out}", file=sys.stderr)
    else:
        print(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
