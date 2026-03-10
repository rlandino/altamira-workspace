# Kanban Task: 13F Copycat Portfolio

**Task ID:** 13f-copycat-portfolio-001  
**Created:** 2026-02-20  
**Status:** Implemented (2026-02-21)  
**Priority:** High  
**Category:** 13F / Portfolio Construction  
**Epic:** Automated 13F Holdings Diff & Copycat Portfolio Service

---

## Task Description

Implement **copycat portfolio** construction: build and maintain a portfolio that **mirrors selected managers’ 13F holdings** (e.g. equal-weight overlap, or weight-by-reported-value). Reference: [WhaleWisdom](https://whalewisdom.com/) — “Research & Replicate Portfolios of the World's Best Investors.”

---

## Requirements

1. **Manager selection**
   - Allow user to select one or more filers (by name or CIK) from 13F data.
   - Support “consensus” copycat: only positions held by N of M selected managers.

2. **Portfolio construction**
   - From latest 13F holdings of selected filers: compute combined list of tickers and weights (e.g. equal weight, or by reported market value, or cap-weighted).
   - Output: target portfolio (ticker, weight %, optional shares/value).

3. **Maintenance**
   - When new 13F filings are ingested, refresh copycat portfolio (script or API).
   - Optional: diff vs. current Altamira portfolio to suggest trades (add/trim to align).

4. **Integration**
   - Output usable by Altamira Dashboard (e.g. target allocation view) and optionally by Backtester task.

---

## Implementation Status

- [x] Logic to combine holdings from one or more filers into a single target portfolio. **`scripts/copycat-13f.py`** — `--ciks`, `--weight value|equal`, `--consensus-min N`.
- [x] Weighting options (equal, value-weighted, consensus threshold).
- [x] Refresh path when new 13F data is available. Re-run script after ingest.
- [x] Export format for dashboard (e.g. JSON or table). **`--out outputs/copycat.json`** (tickers, weightPct, valueUsd, filerCount).

---

## Related Files

- Epic: `outputs/kanban-task-13f-service-epic.md`
- Depends on: `outputs/kanban-task-13f-data-pipeline.md`, `outputs/kanban-task-13f-holdings-diff.md`
- Reference: [WhaleWisdom](https://whalewisdom.com/)
- Portfolio context: `context/portfolio-details.md` (for comparison vs. current holdings)

---

## Acceptance Criteria

- [x] Given 1+ filers, produce a copycat target portfolio (tickers + weights). **CUSIP/name + weightPct; ticker mapping optional.**
- [x] Copycat portfolio can be refreshed from latest 13F data. **Re-run script after ingest.**
- [x] Output can be displayed or used in Altamira Dashboard (http://localhost:8501). **JSON `--out` for dashboard.**

---

**Add to kanban board:** Automated 13F Holdings Diff & Copycat Portfolio Service (http://localhost:3004).
