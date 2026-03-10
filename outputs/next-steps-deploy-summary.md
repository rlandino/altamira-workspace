# Next Steps — Deploy Summary

**Purpose:** Single place to see what to do next for the suggested tasks (kanban sync, CSP deploy, market monitoring, dashboard real-time data, trading infra).

---

## 1. Kanban Q1 sync (manual)

**Goal:** Mark completed Altamira Q1 2026 tasks as **Done** on the board.

- **Instructions:** `outputs/kanban-q1-sync-instructions.md`
- **Where:** http://localhost:3004 → project **Altamira Capital — Q1 2026**
- **Tasks to move to Done:** alt-task-02, 04, 05, 06, 07 (see the instructions doc for rationale).

---

## 2. CSP Daily Scan deploy

**Goal:** Run CSP Daily Scan at 10:30 AM ET weekdays from n8n.

**Option A — API deploy (if you have n8n API key):**

```powershell
$env:N8N_API_KEY = "your_n8n_api_key"
python scripts/deploy-csp-workflow-to-n8n.py
```

Then in n8n: open the workflow, attach credentials (FMP, Telegram, Google Sheets), set `TELEGRAM_CHAT_ID` and `GOOGLE_SHEET_ID` if required, then activate.

**Option B — Manual import:**

1. In n8n: Workflows → Import from File → select `outputs/n8n-workflow-csp-daily-scan.json`.
2. Follow **`outputs/csp-daily-scan-deploy-guide.md`** for credentials, env vars, sheet setup, and activation.

---

## 3. Market Monitoring workflows

**Goal:** Deploy the 5 market monitoring workflows (watchlist alerts, IV monitor, sector rotation, risk dashboard, vol regime).

- **Design:** `outputs/market-monitoring-workflows.md`
- **Checklist:** `outputs/market-monitoring-deploy-checklist.md`

**Ready to import (3 workflows):**  
`n8n-workflow-watchlist-alert-system.json`, `n8n-workflow-4-risk-limit-monitor.json`, `n8n-workflow-volatility-regime-hedging.json`

**To build from design (2 workflows):** Options Flow & IV Monitor, Sector Rotation Monitor — see checklist for sections and effort.

---

## 4. Real-time Market Data for dashboard (alt-dash-06)

**Goal:** Give the Altamira Dashboard (localhost:3001) live quotes, indices, and earnings data.

- **API script:** `scripts/market_data_api.py` — FastAPI bridge to FMP. Run:
  ```powershell
  python -m uvicorn scripts.market_data_api:app --host 0.0.0.0 --port 8001
  ```
  Endpoints: `GET /api/market/quote?symbol=AAPL`, `GET /api/market/indices`, `GET /api/market/earnings`, `GET /api/market/health`.  
  Set `FMP_API_KEY` (or use script default) before running.

- **Dashboard:** Point the Next.js app at `http://localhost:8001` for market data, or use the same FMP key in the app if it calls FMP directly.

---

## 5. Trading infrastructure (alt-task-01)

**Goal:** Complete core trading infrastructure by target Feb 28.

- **Checklist:** `outputs/trading-infrastructure-setup.md`
- **E-Trade API:** `outputs/etrade-api-setup-guide.md`
- **Next actions:** See the “Next actions” section at the top of `trading-infrastructure-setup.md`.

---

## Quick reference

| Task | Doc / script | Action |
|------|----------------|--------|
| Kanban Q1 sync | `outputs/kanban-q1-sync-instructions.md` | Move 5 tasks to Done in UI |
| CSP deploy | `scripts/deploy-csp-workflow-to-n8n.py` + `outputs/csp-daily-scan-deploy-guide.md` | Set N8N_API_KEY, run script, or import JSON and configure |
| Market monitoring | `outputs/market-monitoring-deploy-checklist.md` | Import 3 JSONs; build 2 from design |
| Real-time market data | `scripts/market_data_api.py` | Run uvicorn on port 8001; connect dashboard |
| Trading infra | `outputs/trading-infrastructure-setup.md` | Execute E-Trade and API phases |
