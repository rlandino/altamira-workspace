#!/usr/bin/env python3
"""
Altamira Capital — 13F Fund Performance (Basic Metrics)
=======================================================
Evaluate a filer's 13F profile from ingested filings: concentration (top-N % of AUM),
holdings count, total reported value, and consistency (overlap between periods).
No price data required; for full returns use backtester with FMP.

Usage:
  # Metrics for a filer (latest filing)
  python scripts/13f-fund-performance.py --cik 0001067983

  # Compare two periods (concentration + overlap)
  python scripts/13f-fund-performance.py --cik 0001067983 --prior 2025-06-30 --current 2025-09-30

  # Output to file
  python scripts/13f-fund-performance.py --cik 0001067983 --out outputs/13f-fund-metrics.json
"""

import argparse
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = WORKSPACE / "outputs" / "13f"


def _normalize_period(period: str) -> str:
    s = (period or "").replace("-", "").strip()
    if len(s) == 8:
        return s
    if len(s) == 6:
        return s + "01"
    return s


def load_filing(data_dir: Path, cik: str, period: str) -> dict | None:
    data_dir = Path(data_dir).resolve()
    cik = str(cik).strip().zfill(10)
    period_norm = _normalize_period(period)
    for pattern in (f"{cik}_{period_norm}.json", f"{cik}_{period_norm}*.json"):
        for f in data_dir.glob(pattern):
            with open(f, encoding="utf-8") as fp:
                return json.load(fp)
    return None


def list_filings_for_cik(data_dir: Path, cik: str) -> list[tuple[str, Path]]:
    cik = str(cik).strip().zfill(10)
    out = []
    for f in data_dir.glob(f"{cik}_*.json"):
        if "_" in f.stem:
            _, period = f.stem.split("_", 1)
            out.append((period, f))
    out.sort(key=lambda x: x[0], reverse=True)
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


def compute_metrics(filing: dict) -> dict:
    """Concentration (top 5/10/20 % of value), holdings count, total value (thousands)."""
    holdings = filing.get("holdings") or []
    if not holdings:
        return {"holdingsCount": 0, "totalValueThousands": 0, "concentrationTop5Pct": 0, "concentrationTop10Pct": 0, "concentrationTop20Pct": 0}
    by_value = sorted(holdings, key=lambda h: -_value(h))
    total = sum(_value(h) for h in by_value)
    if total <= 0:
        return {"holdingsCount": len(holdings), "totalValueThousands": 0, "concentrationTop5Pct": 0, "concentrationTop10Pct": 0, "concentrationTop20Pct": 0}
    top5_val = sum(_value(h) for h in by_value[: min(5, len(by_value))])
    top10_val = sum(_value(h) for h in by_value[: min(10, len(by_value))])
    top20_val = sum(_value(h) for h in by_value[: min(20, len(by_value))])
    return {
        "holdingsCount": len(holdings),
        "totalValueThousands": round(total, 2),
        "totalValueUsd": round(total * 1000, 0),
        "concentrationTop5Pct": round(100.0 * top5_val / total, 2),
        "concentrationTop10Pct": round(100.0 * top10_val / total, 2),
        "concentrationTop20Pct": round(100.0 * top20_val / total, 2),
    }


def overlap_pct(holdings_a: list[dict], holdings_b: list[dict]) -> float:
    """CUSIP overlap: % of (unique CUSIPs in A) that appear in B."""
    cusips_a = {_cusip(h) for h in (holdings_a or []) if _cusip(h)}
    cusips_b = {_cusip(h) for h in (holdings_b or []) if _cusip(h)}
    if not cusips_a:
        return 0.0
    return round(100.0 * len(cusips_a & cusips_b) / len(cusips_a), 2)


def main() -> int:
    ap = argparse.ArgumentParser(description="13F fund performance metrics (concentration, overlap).")
    ap.add_argument("--cik", type=str, required=True, help="Filer CIK")
    ap.add_argument("--prior", type=str, help="Prior period (for overlap with --current)")
    ap.add_argument("--current", type=str, help="Current period (for overlap with --prior)")
    ap.add_argument("--data-dir", type=str, default=str(DEFAULT_DATA_DIR), help="13F JSON directory")
    ap.add_argument("--out", type=str, help="Write JSON to file")
    args = ap.parse_args()

    data_dir = Path(args.data_dir).resolve()
    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}", file=sys.stderr)
        return 1

    cik = str(args.cik).strip().zfill(10)
    filer_name = ""

    if args.prior and args.current:
        prior_f = load_filing(data_dir, cik, args.prior)
        current_f = load_filing(data_dir, cik, args.current)
        if not prior_f or not current_f:
            print("One or both periods not found.", file=sys.stderr)
            return 1
        filer_name = (prior_f.get("filer") or {}).get("name") or (current_f.get("filer") or {}).get("name") or ""
        metrics_prior = compute_metrics(prior_f)
        metrics_current = compute_metrics(current_f)
        overlap = overlap_pct(prior_f.get("holdings") or [], current_f.get("holdings") or [])
        result = {
            "filer": {"cik": cik, "name": filer_name},
            "priorPeriod": args.prior,
            "currentPeriod": args.current,
            "prior": metrics_prior,
            "current": metrics_current,
            "overlapPct": overlap,
        }
    else:
        filings = list_filings_for_cik(data_dir, cik)
        if not filings:
            print(f"No filings found for CIK {cik}", file=sys.stderr)
            return 1
        period, path = filings[0]
        with open(path, encoding="utf-8") as fp:
            filing = json.load(fp)
        filer_name = (filing.get("filer") or {}).get("name") or ""
        result = {
            "filer": {"cik": cik, "name": filer_name},
            "period": period,
            "metrics": compute_metrics(filing),
        }

    s = json.dumps(result, indent=2)
    if args.out:
        Path(args.out).write_text(s, encoding="utf-8")
        print(f"Wrote {args.out}", file=sys.stderr)
    else:
        print(s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
