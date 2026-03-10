#!/usr/bin/env python3
"""
Altamira Capital — 13F Holdings Diff
===================================
Compare a filer's 13F holdings between two periods and report new buys, sells,
increased positions, and decreased positions. Uses data from the 13F Data Pipeline
(ingest-13f.py) and query-13f.py storage.

Usage:
  # Diff two periods for a filer (period = YYYY-MM-DD or YYYYMMDD)
  python scripts/13f-holdings-diff.py --cik 0001067983 --prior 2025-06-30 --current 2025-09-30

  # Output markdown to file
  python scripts/13f-holdings-diff.py --cik 0001067983 --prior 20250630 --current 20250930 --out outputs/13f-diff-berkshire.md

  # Also write JSON for dashboard
  python scripts/13f-holdings-diff.py --cik 0001067983 --prior 2025-06-30 --current 2025-09-30 --json-out outputs/13f-diff.json

  # Data directory (default: outputs/13f)
  python scripts/13f-holdings-diff.py --cik 0001067983 --prior 2025-06-30 --current 2025-09-30 --data-dir outputs/13f
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
        return s + "01"
    return s


def load_filing(data_dir: Path, cik: str, period: str) -> dict | None:
    """Load one filing JSON by CIK and period. Returns parsed JSON or None."""
    data_dir = Path(data_dir).resolve()
    cik = str(cik).strip().zfill(10)
    period_norm = _normalize_period(period)
    for pattern in (f"{cik}_{period_norm}.json", f"{cik}_{period_norm}*.json"):
        for f in data_dir.glob(pattern):
            with open(f, encoding="utf-8") as fp:
                return json.load(fp)
    return None


def _holdings_by_cusip(holdings: list[dict]) -> dict[str, dict]:
    """Index holdings by CUSIP. Uses first key found: cusip or CUSIP."""
    out = {}
    for h in holdings or []:
        cusip = (h.get("cusip") or h.get("CUSIP") or "").strip()
        if cusip:
            out[cusip] = h
    return out


def _value(h: dict) -> int | float:
    """Get position value (thousands) from holding. Prefer value, then valueUsd/1000."""
    v = h.get("value")
    if v is not None:
        return int(v) if isinstance(v, (int, float)) else 0
    v = h.get("valueUsd")
    if v is not None:
        return (int(v) / 1000) if isinstance(v, (int, float)) else 0
    return 0


def _shares(h: dict) -> int | float:
    """Get shares from holding. Handles shrsOrPrnAmt as int or string."""
    s = h.get("shrsOrPrnAmt") or h.get("shrsOrPrnAmt")
    if s is None:
        return 0
    if isinstance(s, (int, float)):
        return int(s) if isinstance(s, float) and s == int(s) else s
    s = str(s).replace(",", "").strip()
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return 0


def _name(h: dict) -> str:
    """Get issuer name from holding."""
    return (h.get("nameOfIssuer") or h.get("nameOfIssuer") or h.get("issuer") or "").strip() or "—"


def compute_diff(prior_holdings: list[dict], current_holdings: list[dict]) -> dict:
    """
    Compare prior vs current holdings (by CUSIP). Returns dict with:
    - newBuys: list of current holdings not in prior
    - sells: list of prior holdings not in current
    - increased: list of {cusip, name, priorValue, currentValue, priorShares, currentShares, valueChgPct, ...}
    - decreased: same structure for positions that decreased
    """
    prior_by_cusip = _holdings_by_cusip(prior_holdings)
    current_by_cusip = _holdings_by_cusip(current_holdings)

    prior_cusips = set(prior_by_cusip)
    current_cusips = set(current_by_cusip)

    new_buys = []
    for cusip in current_cusips - prior_cusips:
        h = current_by_cusip[cusip]
        new_buys.append({
            "cusip": cusip,
            "name": _name(h),
            "value": _value(h),
            "shares": _shares(h),
        })

    sells = []
    for cusip in prior_cusips - current_cusips:
        h = prior_by_cusip[cusip]
        sells.append({
            "cusip": cusip,
            "name": _name(h),
            "value": _value(h),
            "shares": _shares(h),
        })

    increased = []
    decreased = []
    for cusip in prior_cusips & current_cusips:
        p = prior_by_cusip[cusip]
        c = current_by_cusip[cusip]
        pv, cv = _value(p), _value(c)
        ps, cs = _shares(p), _shares(c)
        if pv == 0:
            value_chg_pct = 100.0 if cv else 0.0
        else:
            value_chg_pct = ((cv - pv) / pv) * 100.0
        if ps == 0:
            shares_chg_pct = 100.0 if cs else 0.0
        else:
            shares_chg_pct = ((cs - ps) / ps) * 100.0

        row = {
            "cusip": cusip,
            "name": _name(c),
            "priorValue": pv,
            "currentValue": cv,
            "priorShares": ps,
            "currentShares": cs,
            "valueChgPct": round(value_chg_pct, 2),
            "sharesChgPct": round(shares_chg_pct, 2),
        }
        if cv > pv or cs > ps:
            increased.append(row)
        elif cv < pv or cs < ps:
            decreased.append(row)

    return {
        "newBuys": new_buys,
        "sells": sells,
        "increased": increased,
        "decreased": decreased,
    }


def format_report(filer_name: str, cik: str, prior_period: str, current_period: str, diff: dict) -> str:
    """Produce a markdown report from diff result."""
    lines = [
        f"# 13F Holdings Diff - {filer_name or 'Filer'}",
        "",
        f"- **CIK:** {cik}",
        f"- **Prior period:** {prior_period}",
        f"- **Current period:** {current_period}",
        "",
        "---",
        "",
    ]

    # New buys
    lines.append("## New Buys")
    lines.append("")
    if diff["newBuys"]:
        lines.append("| Issuer | CUSIP | Value ($K) | Shares |")
        lines.append("|--------|-------|------------|--------|")
        for h in sorted(diff["newBuys"], key=lambda x: -x["value"]):
            lines.append(f"| {h['name']} | {h['cusip']} | {h['value']:,} | {h['shares']:,} |")
    else:
        lines.append("*None.*")
    lines.append("")

    # Sells
    lines.append("## Sells")
    lines.append("")
    if diff["sells"]:
        lines.append("| Issuer | CUSIP | Value ($K) | Shares |")
        lines.append("|--------|-------|------------|--------|")
        for h in sorted(diff["sells"], key=lambda x: -x["value"]):
            lines.append(f"| {h['name']} | {h['cusip']} | {h['value']:,} | {h['shares']:,} |")
    else:
        lines.append("*None.*")
    lines.append("")

    # Increased
    lines.append("## Increased Positions")
    lines.append("")
    if diff["increased"]:
        lines.append("| Issuer | CUSIP | Prior $K | Current $K | Value % Chg | Shares % Chg |")
        lines.append("|--------|-------|----------|------------|-------------|--------------|")
        for h in sorted(diff["increased"], key=lambda x: -x["currentValue"]):
            lines.append(f"| {h['name']} | {h['cusip']} | {h['priorValue']:,} | {h['currentValue']:,} | {h['valueChgPct']:+.1f}% | {h['sharesChgPct']:+.1f}% |")
    else:
        lines.append("*None.*")
    lines.append("")

    # Decreased
    lines.append("## Decreased Positions")
    lines.append("")
    if diff["decreased"]:
        lines.append("| Issuer | CUSIP | Prior $K | Current $K | Value % Chg | Shares % Chg |")
        lines.append("|--------|-------|----------|------------|-------------|--------------|")
        for h in sorted(diff["decreased"], key=lambda x: x["currentValue"]):
            lines.append(f"| {h['name']} | {h['cusip']} | {h['priorValue']:,} | {h['currentValue']:,} | {h['valueChgPct']:+.1f}% | {h['sharesChgPct']:+.1f}% |")
    else:
        lines.append("*None.*")

    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="13F holdings diff: prior vs current period.")
    ap.add_argument("--cik", type=str, required=True, help="Filer CIK")
    ap.add_argument("--prior", type=str, required=True, help="Prior period end (YYYY-MM-DD or YYYYMMDD)")
    ap.add_argument("--current", type=str, required=True, help="Current period end (YYYY-MM-DD or YYYYMMDD)")
    ap.add_argument("--data-dir", type=str, default=str(DEFAULT_DATA_DIR), help="13F JSON directory")
    ap.add_argument("--out", type=str, help="Write markdown report to file")
    ap.add_argument("--json-out", type=str, help="Write JSON diff to file (for dashboard)")
    args = ap.parse_args()

    data_dir = Path(args.data_dir).resolve()
    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}", file=sys.stderr)
        return 1

    prior_filing = load_filing(data_dir, args.cik, args.prior)
    current_filing = load_filing(data_dir, args.cik, args.current)

    if not prior_filing:
        print(f"No filing found for CIK {args.cik} period {args.prior}", file=sys.stderr)
        return 1
    if not current_filing:
        print(f"No filing found for CIK {args.cik} period {args.current}", file=sys.stderr)
        return 1

    prior_holdings = prior_filing.get("holdings") or []
    current_holdings = current_filing.get("holdings") or []
    filer_name = (prior_filing.get("filer") or {}).get("name") or (current_filing.get("filer") or {}).get("name") or ""
    cik = (prior_filing.get("filer") or {}).get("cik") or args.cik

    diff = compute_diff(prior_holdings, current_holdings)

    # Optional JSON output for dashboard / copycat
    payload = {
        "filer": {"cik": cik, "name": filer_name},
        "priorPeriod": args.prior,
        "currentPeriod": args.current,
        "diff": diff,
    }
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Wrote JSON to {args.json_out}", file=sys.stderr)

    report = format_report(filer_name, cik, args.prior, args.current, diff)
    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
        print(f"Wrote report to {args.out}", file=sys.stderr)
    else:
        print(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
