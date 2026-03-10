# Kanban Task: 13F Holdings Diff (Period-over-Period Changes)

**Task ID:** 13f-holdings-diff-001  
**Created:** 2026-02-20  
**Status:** Implemented (2026-02-21)  
**Priority:** High  
**Category:** 13F / Institutional Data  
**Epic:** Automated 13F Holdings Diff & Copycat Portfolio Service

---

## Task Description

Implement **13F holdings diff**: compare a filer's 13F holdings between two periods and report **new buys**, **sells**, **increased positions**, and **decreased positions**. This is the core "diff" in the service name. Reference: [WhaleWisdom](https://whalewisdom.com/) — tracking changes in institutional holdings.

---

## Requirements

1. **Inputs**
   - Filer (CIK or name) and two period-end dates (e.g. prior quarter vs. current quarter).
   - Data from 13F Data Pipeline (task 13f-data-pipeline-001).

2. **Output**
   - New buys: positions in current period not in prior (or new CUSIP/ticker).
   - Sells: positions in prior period not in current.
   - Increased: same position, shares or value increased.
   - Decreased: same position, shares or value decreased.

3. **Format**
   - Report (markdown or JSON) with ticker, issuer name, shares/value change, % change.
   - Suitable for dashboard display and copycat decisions.

4. **Automation**
   - Script or API endpoint that can be run when new 13F data is available (e.g. quarterly).

---

## Implementation Status

- [x] Diff logic implemented (compare two holdings snapshots per filer). **`scripts/13f-holdings-diff.py`** — new buys, sells, increased, decreased by CUSIP.
- [x] Output format defined (report + optional JSON for dashboard). **`--out`** for markdown report; **`--json-out`** for dashboard/API.
- [x] Wired to 13F Data Pipeline output. Reads from same `outputs/13f/{cik}_{period}.json` as `query-13f.py`.
- [x] Documented in reference or command (e.g. `/13f-diff` or script). Docstring and this task doc.

---

## Related Files

- Epic: `outputs/kanban-task-13f-service-epic.md`
- Depends on: `outputs/kanban-task-13f-data-pipeline.md`
- Script: `scripts/13f-holdings-diff.py` — usage: `python scripts/13f-holdings-diff.py --cik CIK --prior YYYY-MM-DD --current YYYY-MM-DD [--out report.md] [--json-out diff.json]`
- Reference: [WhaleWisdom](https://whalewisdom.com/)

---

## Acceptance Criteria

- [x] For a given filer and two dates, report correctly lists new buys, sells, increases, decreases.
- [x] Output can be consumed by Copycat Portfolio task and by Altamira Dashboard (markdown via `--out`, JSON via `--json-out`).

---

**Add to kanban board:** Automated 13F Holdings Diff & Copycat Portfolio Service (http://localhost:3004).
