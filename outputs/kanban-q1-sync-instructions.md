# Kanban Q1 2026 — Sync Instructions

**Purpose:** Move completed Altamira Capital Q1 2026 tasks to **Done** on the kanban board so the board reflects reality.

**Note:** The kanban API does not expose an endpoint to update a task's column. Updates must be done manually in the UI.

---

## Where to update

- **Kanban UI:** http://localhost:3004  
- **Project:** **Altamira Capital — Q1 2026**

---

## Tasks to mark as Done

Based on `context/current-data.md` and deliverables in `outputs/`:

| Task ID   | Title                              | Why mark Done |
|-----------|------------------------------------|---------------|
| **alt-task-04** | Write investment thesis document   | Investment Thesis v2.0 is **Final** — `outputs/altamira-investment-thesis.md` |
| **alt-task-07** | Deploy Claude Skills for financial analysis | Financial Analysis Commands **Operational** — `/analyze-ticker`, `/options-scan`, `/portfolio-report`, `/paper-trade`, `/client-report`, `/thesis`, `/stockscore` |
| **alt-task-02** | Backtest 3+ strategies             | Backtest framework and 2Y results complete — `outputs/backtest-results-2026-02-18.md` (CSP, momentum, hedging) |
| **alt-task-05** | Build risk management framework   | Risk Management Framework **Final v1.0** — `outputs/risk-management-framework.md` |
| **alt-task-06** | Create target portfolio allocation model | Portfolio Allocation Model **Final v1.0** — `outputs/portfolio-allocation-model.md` |

---

## How to update (manual)

1. Open http://localhost:3004 and ensure the kanban app is running.
2. Find the project **Altamira Capital — Q1 2026**.
3. For each task in the table above, **drag the card** from its current column (e.g. **todo** or **backlog**) to the **Done** column.
4. Optionally add a short note on the card (e.g. "Done: see outputs/altamira-investment-thesis.md") if the UI supports task notes.

---

## Tasks to leave as-is (not yet done)

| Task ID   | Title                              | Status / Next step |
|-----------|------------------------------------|--------------------|
| **alt-task-01** | Set up core trading infrastructure | **todo / urgent** — Target Feb 28. Use `outputs/trading-infrastructure-setup.md` and `outputs/etrade-api-setup-guide.md`. |
| **alt-task-03** | Paper trading live with risk management rules | **backlog** — Depends on alt-task-01. Target Mar 31. |
| **alt-task-08** | Build automated market monitoring workflows | **backlog** — Deploy workflows from `outputs/market-monitoring-workflows.md` and existing JSONs; then mark Done. |
| **alt-task-09** | Client reporting automation | **backlog** — `/client-report` exists; full automation (scheduled reports) can be added later. |
| **alt-task-10** | Install AI Chief of Staff system | Already **Done**. |

---

## After updating

Re-export the board to refresh `context/kanban-export.csv` (optional):

```bash
curl -o context/kanban-export.csv "http://localhost:3005/api/board/export"
```

(Requires kanban API running on port 3005.)
