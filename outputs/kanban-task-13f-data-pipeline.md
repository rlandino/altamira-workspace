# Kanban Task: 13F Data Pipeline & API

**Task ID:** 13f-data-pipeline-001  
**Created:** 2026-02-20  
**Status:** Implemented (2026-02-21)  
**Priority:** High  
**Category:** 13F / Data Engineering  
**Epic:** Automated 13F Holdings Diff & Copycat Portfolio Service

---

## Task Description

Build the **13F data pipeline** to ingest SEC 13F filings, normalize holdings data, and expose it via a local API or structured exports. This is the foundation for all other 13F features (WhaleWisdom-style). Reference: [WhaleWisdom](https://whalewisdom.com/) — "Developer API" and 13F data access.

---

## Requirements

1. **Ingest 13F filings**
   - Source: SEC EDGAR (e.g. 13F-HR, 13F-HR/A) or third-party feed.
   - Parse XML/form data to extract: filer (CIK/name), period end date, holdings (issuer, CUSIP, value, shares, investment discretion, etc.).

2. **Normalize and store**
   - Store per-filing and per-holding records (DB or structured files in workspace).
   - Support querying by: filer, date range, ticker/CUSIP.

3. **API or exports**
   - Option A: Local API (e.g. FastAPI/Flask) for other services and the dashboard to query holdings and filers.
   - Option B: Scheduled exports to `context/` or `outputs/` (JSON/CSV) for scripts and dashboard.

4. **Search and filters (WhaleWisdom-like)**
   - Search by fund/manager name or CIK.
   - Filter by filing date, position size, ticker.

---

## Implementation Status

- [x] Data source chosen (SEC EDGAR direct vs. vendor). **SEC EDGAR (data.sec.gov + Archives).**
- [x] Parser for 13F XML/form implemented. **`scripts/ingest-13f.py`** — parses XML and HTML-wrapped info table.
- [x] Storage schema and ingestion script (or workflow) implemented. **JSON per filing under `outputs/13f/{cik}_{period_end}.json`.**
- [x] Query API or export format defined and implemented. **`scripts/query-13f.py`** — list filers, get holdings by cik/period, filter by CUSIP.
- [x] Basic search/filter by filer and date. **`--list`, `--cik`, `--period`, `--cusip`.**

---

## Related Files

- Epic: `outputs/kanban-task-13f-service-epic.md`
- Reference: [WhaleWisdom](https://whalewisdom.com/) — Developer API, 13F data
- Reference: `reference/13f-data-pipeline.md` — usage and SEC access notes
- Scripts: `scripts/ingest-13f.py`, `scripts/query-13f.py`
- SEC EDGAR: https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=13F-HR

---

## Acceptance Criteria

- [x] 13F holdings for at least one filer (or sample dataset) ingested and queryable. **Use `--sample` for sample JSON; live SEC may require SEC_EDGAR_USER_AGENT if 403.**
- [x] Other 13F tasks (holdings diff, copycat, fund performance) can consume this data. **JSON schema: filer, periodEnd, filingDate, holdings[].**
- [x] Search/filter by fund/manager and date range works (API or export). **`query-13f.py --list`, `--cik`, `--period`, `--cusip`.**

---

**Add to kanban board:** Automated 13F Holdings Diff & Copycat Portfolio Service (http://localhost:3004). Dependency for: Holdings Diff, Copycat Portfolio, Fund Performance, Stock Screener.
