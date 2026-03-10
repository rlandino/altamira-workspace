# Kanban Epic: Automated 13F Holdings Diff & Copycat Portfolio Service

**Task ID:** 13f-service-epic  
**Created:** 2026-02-20  
**Status:** Ready for Implementation  
**Priority:** High  
**Category:** 13F / Institutional Data / Copycat Portfolios

---

## Task Description

Build an **Automated 13F Holdings Diff & Copycat Portfolio Service** that captures core functionality from [WhaleWisdom](https://whalewisdom.com/) and integrates it into the **Altamira Dashboard** (http://localhost:8501). WhaleWisdom provides research and replication of top investors’ portfolios using 13F filings; this epic turns those capabilities into development tasks on the kanban board (http://localhost:3004) and delivers them into our own dashboard.

---

## WhaleWisdom Feature Mapping → Development Tasks

| WhaleWisdom Feature | Kanban Task Doc | Goal |
|--------------------|-----------------|------|
| **13F data / Developer API** | `kanban-task-13f-data-pipeline.md` | Ingest 13F filings (SEC), store holdings, expose API or feeds for the rest of the service. |
| **13F Fund Performance Evaluator** | `kanban-task-13f-fund-performance.md` | Evaluate fund/manager performance from 13F history (returns, consistency, concentration). |
| **13F Stock Screener** | `kanban-task-13f-stock-screener.md` | Screen stocks by 13F ownership (which funds hold, aggregate ownership, momentum). |
| **Combined Holdings** | `kanban-task-13f-combined-holdings.md` | Aggregate holdings across selected funds/managers (overlap, consensus picks). |
| **Backtester** | `kanban-task-13f-backtester.md` | Backtest copycat or 13F-based strategies (replicate reported holdings, measure performance). |
| **13F Heat Map** | `kanban-task-13f-heat-map.md` | Visual heat map of 13F exposure (sectors, tickers, funds over time). |
| **Holdings diff** | `kanban-task-13f-holdings-diff.md` | Compare 13F filings period-over-period (new buys, sells, changes in size). |
| **Copycat portfolio** | `kanban-task-13f-copycat-portfolio.md` | Construct and maintain a portfolio that mirrors selected managers’ 13F holdings. |
| **Search & filters** | (in data pipeline + UI tasks) | Search funds, stocks, filter by date, manager, position size (like WhaleWisdom search). |
| **Dashboard integration** | `kanban-task-13f-dashboard-integration.md` | Surface 13F features in Altamira Dashboard at http://localhost:8501 (views, links, embedded widgets). |

---

## Implementation Order (Suggested)

1. **13F Data Pipeline** — Foundation: ingest 13F data, normalize holdings, store for queries.
2. **Holdings Diff** — Core value: period-over-period changes (buys/sells/weight changes).
3. **Copycat Portfolio** — Build and track portfolios that mirror selected managers.
4. **13F Fund Performance** — Evaluate managers using 13F history.
5. **13F Stock Screener** — Screen by institutional ownership and trends.
6. **Combined Holdings** — Aggregate across managers; **13F Heat Map** — Visualization.
7. **Backtester** — Backtest 13F-based and copycat strategies.
8. **Dashboard Integration** — Integrate all above into http://localhost:8501.

---

## Related Files & References

- Kanban board: http://localhost:3004 (project: Automated 13F Holdings Diff & Copycat Portfolio Service)
- Altamira Dashboard: http://localhost:8501
- Reference: [WhaleWisdom](https://whalewisdom.com/) — Backtester, Combined Holdings, 13F Fund Performance Evaluator, 13F Stock Screener, 13F Heat Map, Developer API, search/filters
- Task docs: `outputs/kanban-task-13f-*.md`

---

## Acceptance Criteria (Epic)

- [x] All child tasks created and on kanban board.
- [x] 13F data pipeline operational (ingest and store 13F holdings). **`scripts/ingest-13f.py`, `scripts/query-13f.py`.**
- [x] Holdings diff and copycat portfolio features available (script or API). **`scripts/13f-holdings-diff.py`, `scripts/copycat-13f.py`.**
- [x] At least two WhaleWisdom-style features (e.g. Fund Performance, Stock Screener, Combined Holdings, or Heat Map) implemented. **Fund Performance (`13f-fund-performance.py`), Stock Screener (`13f-stock-screener.py`), Heat Map export (`13f-heatmap-export.py`), Backtester scaffold (`13f-backtest.py`).**
- [x] 13F features integrated into Altamira Dashboard (http://localhost:8501). **Option B: FastAPI bridge `scripts/13f_api.py` (port 8000); see `reference/13f-dashboard-integration.md`.**

---

**Add to kanban board:** Add this epic and all linked `kanban-task-13f-*.md` tasks to the **Automated 13F Holdings Diff & Copycat Portfolio Service** project at http://localhost:3004. Goal: replicate and integrate WhaleWisdom-style functionality into our dashboard.
