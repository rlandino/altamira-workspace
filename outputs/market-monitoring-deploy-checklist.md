# Market Monitoring Workflows — Deploy Checklist

**Reference:** `outputs/market-monitoring-workflows.md` (full design)

Deploy the 5 market monitoring workflows to n8n in this order. Existing workflow JSONs are in `outputs/`.

---

## Workflows with existing JSON (ready to import)

| # | Workflow | JSON file | Trigger | Priority |
|---|----------|------------|---------|----------|
| 1 | **Watchlist Alert System** | `n8n-workflow-watchlist-alert-system.json` | Every 15 min (market hours) | P0 |
| 4 | **Risk Limit Monitor** | `n8n-workflow-4-risk-limit-monitor.json` | Daily close + on-demand | P1 |
| 5 | **Volatility Regime & Hedging Trigger** | `n8n-workflow-volatility-regime-hedging.json` | Every 30 min (market hours) | P0 |

**Next step:** Import each JSON in n8n (Workflows → Import from File), attach FMP/Telegram/Google Sheets credentials per the design doc, set env vars if needed, then activate.

---

## Workflows to build from design (no JSON yet)

| # | Workflow | Section in design doc | Effort | Priority |
|---|----------|------------------------|--------|----------|
| 2 | **Options Flow & IV Monitor** | [Workflow 2: Options Flow & IV Monitor](market-monitoring-workflows.md#3-workflow-2-options-flow--iv-monitor) | ~3 days | P1 |
| 3 | **Sector Rotation Monitor** | [Workflow 3: Sector Rotation Monitor](market-monitoring-workflows.md#4-workflow-3-sector-rotation-monitor) | ~1.5 days | P2 |

**Next step:** Build n8n workflows from the specs in `market-monitoring-workflows.md` (triggers, FMP/Massive.com nodes, Telegram/Sheets outputs). Export to JSON and add to `outputs/` when done.

---

## Suggested deploy order

1. **Watchlist Alert System** — High impact, JSON ready. Import → credentials → activate.
2. **Volatility Regime & Hedging Trigger** — P0, JSON ready. Import → credentials → activate.
3. **Risk Limit Monitor** — Depends on E-Trade/positions; deploy once E-Trade API is live, or mock data for testing.
4. **Sector Rotation Monitor** — Build from design (FMP sector ETFs, daily 4:30 PM ET).
5. **Options Flow & IV Monitor** — Build from design (Massive.com + FMP, 10:30 AM + 3:30 PM ET).

---

## Credentials and env vars (common)

- **FMP:** API key (query param `apikey`). Use n8n HTTP Request or credential.
- **Telegram:** Bot token for alerts.
- **Google Sheets:** OAuth2 for logging (optional per workflow).
- **E-Trade:** OAuth 1.0a for Risk Limit Monitor (when available).

After deployment, update **alt-task-08** (Build automated market monitoring workflows) on the kanban to **Done** when all 5 are live.
