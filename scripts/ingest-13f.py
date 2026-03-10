#!/usr/bin/env python3
"""
Altamira Capital — 13F Data Pipeline (Ingest)
=============================================
Ingests SEC 13F-HR filings from EDGAR, parses holdings from the information table,
and stores normalized JSON for use by holdings-diff, copycat-portfolio, and dashboard.

Data source: SEC EDGAR (data.sec.gov submissions + Archives). No API key required.
SEC requires a descriptive User-Agent; set SEC_EDGAR_USER_AGENT or use default.

Usage:
  # Ingest latest 13F for a filer by CIK (e.g. Berkshire Hathaway = 1067983)
  python scripts/ingest-13f.py --cik 1067983

  # Ingest last N filings for a CIK
  python scripts/ingest-13f.py --cik 1067983 --max-filings 4

  # Ingest from a list of CIKs (e.g. context/13f-filers.txt)
  python scripts/ingest-13f.py --cik-list context/13f-filers.txt

  # Export path (default: outputs/13f)
  python scripts/ingest-13f.py --cik 1067983 --out-dir outputs/13f

  # Write sample JSON only (no SEC fetch; for testing pipeline if 403)
  python scripts/ingest-13f.py --sample --out-dir outputs/13f

If you get 403 from SEC Archives, set SEC_EDGAR_USER_AGENT to "YourCompany contact@email.com".

Output: One JSON file per filing under {out_dir}/{cik}_{period_end}.json
  - filer (cik, name), period_end, filing_date, holdings[], source_url
"""

import argparse
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------

WORKSPACE = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = WORKSPACE / "outputs" / "13f"

# SEC requires a descriptive User-Agent (company/contact). Use env or default.
SEC_USER_AGENT = os.environ.get(
    "SEC_EDGAR_USER_AGENT",
    "Altamira Capital contact@altamira-capital.com",
)

SEC_HEADERS = {
    "User-Agent": SEC_USER_AGENT,
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate",
    "Host": "data.sec.gov",
}

SEC_ARCHIVES_HEADERS = {
    "User-Agent": SEC_USER_AGENT,
    "Accept": "application/xml, text/html, */*",
}

DATA_SEC_BASE = "https://data.sec.gov"
ARCHIVES_BASE = "https://www.sec.gov/Archives/edgar/data"

# Rate limit: SEC recommends no more than 10 requests per second.
REQUEST_DELAY = 0.12  # ~8/sec to stay safe


def _pad_cik(cik: str) -> str:
    """Pad CIK to 10 digits with leading zeros."""
    s = str(cik).strip()
    return s.zfill(10)


def _accession_to_path(accession: str) -> str:
    """Convert accession number to path segment (remove dashes)."""
    return accession.replace("-", "")


def fetch_submissions(cik: str) -> dict:
    """Fetch company submissions JSON from data.sec.gov. Returns full JSON."""
    cik = _pad_cik(cik)
    url = f"{DATA_SEC_BASE}/submissions/CIK{cik}.json"
    try:
        r = requests.get(url, headers=SEC_HEADERS, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch submissions for CIK {cik}: {e}") from e


def get_13f_filings(submissions: dict, max_filings: int = 10) -> list[dict]:
    """From submissions JSON, return list of 13F-HR / 13F-HR/A filings (most recent first)."""
    recent = submissions.get("filings", {}).get("recent")
    if not recent:
        return []

    forms = recent.get("form") or []
    dates = recent.get("filingDate") or []
    accessions = recent.get("accessionNumber") or []
    primary_docs = recent.get("primaryDocument") or []
    # Optional: description (e.g. "13F-HR")

    out = []
    for i, form in enumerate(forms):
        if form not in ("13F-HR", "13F-HR/A"):
            continue
        if len(out) >= max_filings:
            break
        acc = accessions[i] if i < len(accessions) else ""
        primary = primary_docs[i] if i < len(primary_docs) else ""
        filing_date = dates[i] if i < len(dates) else ""
        if not acc or not primary:
            continue
        out.append({
            "form": form,
            "filingDate": filing_date,
            "accessionNumber": acc,
            "primaryDocument": primary,
        })
    return out


def filing_document_url(cik: str, accession: str, primary_document: str) -> str:
    """Build SEC Archives URL for the primary document of a filing."""
    # Archives path uses numeric CIK (no leading zeros) and accession with dashes removed
    cik_num = str(int(_pad_cik(cik)))
    path_part = _accession_to_path(accession)
    return f"{ARCHIVES_BASE}/{cik_num}/{path_part}/{primary_document}"


def filing_index_url(cik: str, accession: str, subdir: str | None = None) -> str:
    """Build SEC Archives URL for the accession index (lists files in the filing or in subdir)."""
    cik_num = str(int(_pad_cik(cik)))
    path_part = _accession_to_path(accession)
    if subdir:
        return f"{ARCHIVES_BASE}/{cik_num}/{path_part}/{subdir}/index.json"
    return f"{ARCHIVES_BASE}/{cik_num}/{path_part}/index.json"


def fetch_filing_index(cik: str, accession: str, subdir: str | None = None, retries: int = 2) -> list[dict]:
    """Fetch index.json; return list of item dicts (name, size, etc.). subdir = e.g. xslForm13F_X02."""
    url = filing_index_url(cik, accession, subdir)
    for attempt in range(max(retries, 1)):
        r = requests.get(url, headers=SEC_ARCHIVES_HEADERS, timeout=30)
        if r.status_code == 403 and attempt < retries - 1:
            time.sleep(2.0)
            continue
        r.raise_for_status()
        data = r.json()
        items = data.get("directory", {}).get("item") or []
        return items if isinstance(items, list) else [items]
    return []


def find_information_table_file(items: list[dict], primary_doc: str) -> str | None:
    """
    From index items, pick the file that contains the 13F information table.
    Prefer infotable.xml, 13FXML*.xml; else any .xml larger than primary_doc that may hold holdings.
    primary_doc may be a path (e.g. xslForm13F_X02/primary_doc.xml); comparison uses basename only.
    Returns filename (relative to the index's directory) or None to fall back to primary document.
    """
    primary_basename = (primary_doc or "").split("/")[-1].strip()
    primary_lower = primary_basename.lower()
    candidates = []
    for it in items:
        name = (it.get("name") or "").strip()
        if not name or not name.lower().endswith(".xml"):
            continue
        if name.lower() == primary_lower:
            continue
        nlower = name.lower()
        if "infotable" in nlower or "13fxml" in nlower or "informationtable" in nlower:
            return name
        try:
            size = int(it.get("size") or 0)
        except (TypeError, ValueError):
            size = 0
        # Prefer larger XML (cover is small; info table is larger)
        if size > 2000:
            candidates.append((size, name))
    if candidates:
        candidates.sort(reverse=True, key=lambda x: x[0])
        return candidates[0][1]
    return None


def fetch_filing_document(url: str, retries: int = 2) -> bytes:
    """Fetch raw document from SEC Archives. Uses SEC_ARCHIVES_HEADERS. Retries on 403 with delay."""
    for attempt in range(max(retries, 1)):
        r = requests.get(url, headers=SEC_ARCHIVES_HEADERS, timeout=60)
        if r.status_code == 403 and attempt < retries - 1:
            time.sleep(2.0)  # Back off before retry
            continue
        r.raise_for_status()
        return r.content
    raise requests.HTTPError(f"403 after {retries} attempts", response=r)


def _ns(tag: str, ns: str = "http://www.sec.gov/edgar/document/thirteenf/informationtable") -> str:
    """Optional namespace for 13F info table."""
    return f"{{{ns}}}{tag}" if ns else tag


def _local_tag(elem: ET.Element) -> str:
    """Return local tag name (no namespace)."""
    return (elem.tag or "").split("}")[-1]


def _find_text(parent: ET.Element, *names: str) -> str:
    """Find first direct or nested element with given local name and return its text."""
    for name in names:
        for e in parent.iter():
            if _local_tag(e) == name and (e.text or "").strip():
                return (e.text or "").strip()
    return ""


def parse_13f_xml(content: bytes) -> list[dict]:
    """
    Parse 13F information table from XML. Handles common namespaces and tag names.
    Returns list of holding dicts: nameOfIssuer, titleOfClass, cusip, value, shrsOrPrnAmt, etc.
    """
    root = ET.fromstring(content)

    # Find information table: common tags with or without namespace
    table = None
    for elem in root.iter():
        local = _local_tag(elem)
        if local in ("informationTable", "InformationTable"):
            table = elem
            break
    if table is None:
        for elem in root.iter():
            local = _local_tag(elem).lower()
            if "informationtable" in local or ("info" in local and "table" in local):
                table = elem
                break
    if table is None:
        return []

    # Rows: direct children are typically "infoTable" (one per holding)
    rows = []
    for child in table:
        local = _local_tag(child).lower()
        if "infotable" in local or "holding" in local or "entry" in local:
            rows.append(child)
    if not rows:
        rows = list(table)

    holdings = []
    for row in rows:
        name_of_issuer = _find_text(row, "nameOfIssuer", "nameOfIssuer")
        title_of_class = _find_text(row, "titleOfClass", "titleOfClass")
        cusip = _find_text(row, "cusip", "CUSIP")
        value_str = _find_text(row, "value", "value")
        investment_discretion = _find_text(row, "investmentDiscretion", "investmentDiscretion") or "SOLE"

        # shrsOrPrnAmt: can be element with sshPrnamt (or sshPrnamtType + sshPrnamt children)
        shrs_or_prn_amt = ""
        for e in row.iter():
            if _local_tag(e) == "shrsOrPrnAmt":
                # Nested sshPrnamt or direct text
                for c in e.iter():
                    if _local_tag(c) == "sshPrnamt" and (c.text or "").strip():
                        shrs_or_prn_amt = (c.text or "").strip()
                        break
                if not shrs_or_prn_amt and (e.text or "").strip():
                    shrs_or_prn_amt = (e.text or "").strip()
                break
        if not shrs_or_prn_amt:
            shrs_or_prn_amt = _find_text(row, "sshPrnamt", "shrsOrPrnAmt")

        if not name_of_issuer and not cusip:
            continue
        try:
            value_int = int(value_str.replace(",", "")) if value_str else 0  # thousands
        except ValueError:
            value_int = 0
        try:
            shrs_int = int(shrs_or_prn_amt.replace(",", "")) if shrs_or_prn_amt else 0
        except ValueError:
            shrs_int = 0

        holdings.append({
            "nameOfIssuer": name_of_issuer,
            "titleOfClass": title_of_class,
            "cusip": cusip,
            "value": value_int,
            "valueUsd": value_int * 1000,
            "shrsOrPrnAmt": shrs_int,
            "investmentDiscretion": investment_discretion,
        })
    return holdings


def parse_13f_document(content: bytes, url: str) -> list[dict]:
    """Parse 13F holdings from document (XML or HTML with embedded info table)."""
    content_str = content.decode("utf-8", errors="replace")
    # SEC often serves HTML wrapper with embedded informationTable (XHTML namespaces)
    try:
        return parse_13f_xml(content)
    except ET.ParseError:
        pass
    # If HTML, extract the first informationTable fragment and parse as XML
    for start_tag in ("<informationTable", "<n1:informationTable", "<n2:informationTable"):
        start = content_str.find(start_tag)
        if start != -1:
            # Find matching closing tag (same local name)
            local = "informationTable"
            end_tag = f"</{local}>"
            if start_tag.startswith("<n1:"):
                end_tag = "</n1:informationTable>"
            elif start_tag.startswith("<n2:"):
                end_tag = "</n2:informationTable>"
            end = content_str.find(end_tag, start)
            if end != -1:
                end += len(end_tag)
                fragment = content_str[start:end].encode("utf-8")
                try:
                    return parse_13f_xml(fragment)
                except ET.ParseError:
                    pass
    return []


def write_sample_filing(out_dir: Path, cik: str = "0001067983", period_end: str = "2025-09-30") -> Path:
    """Write a minimal sample 13F JSON for testing pipeline (no SEC fetch). Returns path."""
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_end = period_end.replace("-", "")
    out_path = out_dir / f"{cik}_{safe_end}.json"
    payload = {
        "filer": {"cik": cik, "name": "Sample Filer (13F test)"},
        "periodEnd": period_end,
        "filingDate": "2025-11-14",
        "form": "13F-HR",
        "accessionNumber": "0000000000-00-000000",
        "sourceUrl": "",
        "holdingsCount": 3,
        "holdings": [
            {"nameOfIssuer": "APPLE INC", "titleOfClass": "COM", "cusip": "037833100", "value": 150000, "valueUsd": 150000000, "shrsOrPrnAmt": 1000000, "investmentDiscretion": "SOLE"},
            {"nameOfIssuer": "MICROSOFT CORP", "titleOfClass": "COM", "cusip": "594918104", "value": 120000, "valueUsd": 120000000, "shrsOrPrnAmt": 400000, "investmentDiscretion": "SOLE"},
            {"nameOfIssuer": "AMAZON COM INC", "titleOfClass": "COM", "cusip": "023135106", "value": 80000, "valueUsd": 80000000, "shrsOrPrnAmt": 500000, "investmentDiscretion": "SOLE"},
        ],
    }
    with open(out_path, "w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2)
    return out_path


def ingest_filer(cik: str, out_dir: Path, max_filings: int = 4) -> list[Path]:
    """Fetch submissions, get 13F filings, download and parse each, save JSON. Returns paths saved."""
    cik = _pad_cik(cik)
    submissions = fetch_submissions(cik)
    time.sleep(REQUEST_DELAY)  # SEC rate limit before next request
    name = (submissions.get("name") or "").strip() or f"CIK{cik}"

    filings = get_13f_filings(submissions, max_filings=max_filings)
    if not filings:
        return []

    saved = []
    for f in filings:
        acc = f["accessionNumber"]
        primary = f["primaryDocument"]
        filing_date = f["filingDate"]
        # Prefer the separate information-table file (e.g. 50240.xml, infotable.xml); primary_doc is often just the cover.
        doc_url = filing_document_url(cik, acc, primary)
        doc = None
        try:
            # When primary is in a subdir (e.g. xslForm13F_X02/primary_doc.xml), try that subdir's index first.
            subdir = primary.rsplit("/", 1)[0] if "/" in primary else None
            info_file = None
            from_subdir = False
            if subdir:
                try:
                    subdir_items = fetch_filing_index(cik, acc, subdir)
                    time.sleep(REQUEST_DELAY)
                    info_file = find_information_table_file(subdir_items, primary) if subdir_items else None
                    from_subdir = bool(info_file)
                except requests.RequestException:
                    pass
            if not info_file:
                root_items = fetch_filing_index(cik, acc)
                time.sleep(REQUEST_DELAY)
                info_file = find_information_table_file(root_items, primary) if root_items else None
            if info_file:
                file_path = f"{subdir}/{info_file}" if from_subdir else info_file
                info_url = filing_document_url(cik, acc, file_path)
                doc = fetch_filing_document(info_url)
                doc_url = info_url
            if doc is None:
                doc = fetch_filing_document(doc_url)
        except requests.RequestException as e:
            try:
                doc = fetch_filing_document(doc_url)
            except requests.RequestException as e2:
                print(f"  Skip {acc}: fetch failed — {e2}", file=sys.stderr)
                continue
        time.sleep(REQUEST_DELAY)  # SEC rate limit
        holdings = parse_13f_document(doc, doc_url)
        # Period end: 13F is quarterly; we don't have it in submissions. Use filing_date as proxy or derive.
        period_end = filing_date  # Or parse from XML if present
        safe_end = period_end.replace("-", "") if period_end else acc.replace("-", "_")
        out_path = out_dir / f"{cik}_{safe_end}.json"
        payload = {
            "filer": {"cik": cik, "name": name},
            "periodEnd": period_end,
            "filingDate": filing_date,
            "form": f["form"],
            "accessionNumber": acc,
            "sourceUrl": doc_url,
            "holdingsCount": len(holdings),
            "holdings": holdings,
        }
        out_dir.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fp:
            json.dump(payload, fp, indent=2)
        saved.append(out_path)
        print(f"  Saved {out_path.name} ({len(holdings)} holdings)")
    return saved


def main() -> int:
    ap = argparse.ArgumentParser(description="Ingest SEC 13F-HR filings into JSON.")
    ap.add_argument("--cik", type=str, help="Filer CIK (e.g. 1067983 for Berkshire)")
    ap.add_argument("--cik-list", type=str, help="Path to file with one CIK per line")
    ap.add_argument("--max-filings", type=int, default=4, help="Max 13F filings per filer (default 4)")
    ap.add_argument("--out-dir", type=str, default=str(DEFAULT_OUT_DIR), help="Output directory for JSON files")
    ap.add_argument("--sample", action="store_true", help="Write sample JSON only (pipeline testing; do not use for dashboard)")
    args = ap.parse_args()

    out_dir = Path(args.out_dir).resolve()
    if args.sample:
        # Two periods so holdings-diff can be tested: prior 2 holdings, current 3 (AAPL up, MSFT down, AMZN new)
        out_dir.mkdir(parents=True, exist_ok=True)
        prior = {
            "filer": {"cik": "0001067983", "name": "Sample Filer (13F test)"},
            "periodEnd": "2025-06-30",
            "filingDate": "2025-08-14",
            "form": "13F-HR",
            "accessionNumber": "0000000000-00-000000",
            "sourceUrl": "",
            "holdingsCount": 2,
            "holdings": [
                {"nameOfIssuer": "APPLE INC", "titleOfClass": "COM", "cusip": "037833100", "value": 150000, "valueUsd": 150000000, "shrsOrPrnAmt": 1000000, "investmentDiscretion": "SOLE"},
                {"nameOfIssuer": "MICROSOFT CORP", "titleOfClass": "COM", "cusip": "594918104", "value": 120000, "valueUsd": 120000000, "shrsOrPrnAmt": 400000, "investmentDiscretion": "SOLE"},
            ],
        }
        current = {
            "filer": {"cik": "0001067983", "name": "Sample Filer (13F test)"},
            "periodEnd": "2025-09-30",
            "filingDate": "2025-11-14",
            "form": "13F-HR",
            "accessionNumber": "0000000000-00-000001",
            "sourceUrl": "",
            "holdingsCount": 3,
            "holdings": [
                {"nameOfIssuer": "APPLE INC", "titleOfClass": "COM", "cusip": "037833100", "value": 180000, "valueUsd": 180000000, "shrsOrPrnAmt": 1200000, "investmentDiscretion": "SOLE"},
                {"nameOfIssuer": "MICROSOFT CORP", "titleOfClass": "COM", "cusip": "594918104", "value": 100000, "valueUsd": 100000000, "shrsOrPrnAmt": 350000, "investmentDiscretion": "SOLE"},
                {"nameOfIssuer": "AMAZON COM INC", "titleOfClass": "COM", "cusip": "023135106", "value": 80000, "valueUsd": 80000000, "shrsOrPrnAmt": 500000, "investmentDiscretion": "SOLE"},
            ],
        }
        p1 = out_dir / "0001067983_20250630.json"
        p2 = out_dir / "0001067983_20250930.json"
        for path, data in ((p1, prior), (p2, current)):
            with open(path, "w", encoding="utf-8") as fp:
                json.dump(data, fp, indent=2)
        print(f"Wrote sample filings to {p1} and {p2}")
        return 0

    ciks = []
    if args.cik:
        ciks.append(args.cik.strip())
    if args.cik_list:
        p = Path(args.cik_list)
        if not p.is_absolute():
            p = WORKSPACE / p
        if p.exists():
            with open(p, encoding="utf-8") as f:
                for line in f:
                    cik = line.split("#")[0].strip()
                    if cik:
                        ciks.append(cik)
        else:
            print(f"File not found: {args.cik_list}", file=sys.stderr)
            return 1
    if not ciks:
        print("Provide --cik or --cik-list. Example: --cik 1067983", file=sys.stderr)
        return 1

    total = 0
    for cik in ciks:
        print(f"Filer CIK {cik}...")
        try:
            paths = ingest_filer(cik, out_dir, max_filings=args.max_filings)
            total += len(paths)
        except Exception as e:
            print(f"  Error: {e}", file=sys.stderr)
    print(f"Done. Wrote {total} filing(s) to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
