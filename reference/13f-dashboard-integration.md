# 13F Dashboard Integration — Reference

> How to surface 13F features in the Altamira Dashboard (http://localhost:3001 or http://localhost:8501).

---

## Deploy to Dashboard (Streamlit)

### Prerequisites

1. **13F API running** (port 8000):
   ```bash
   pip install fastapi uvicorn
   python -m uvicorn scripts.13f_api:app --host 127.0.0.1 --port 8000
   ```
2. **13F data ingested** (for real data, run **without** `--sample`):
   ```bash
   python scripts/ingest-13f.py --cik-list context/13f-filers.txt
   ```
   If SEC returns 403, set `SEC_EDGAR_USER_AGENT` (e.g. `YourName/you@example.com`).

### Add 13F section to Streamlit app

The Streamlit app is in another repo. Add the 13F section using one of these:

**Option A — Copy into existing page**

1. In the app repo, open the page where you want 13F (e.g. a new route `/13f` or under Portfolio).
2. Copy `scripts/streamlit_13f.py` into your app (e.g. as `streamlit_13f.py` in the app folder), then:
   ```python
   from streamlit_13f import render_13f
   render_13f()
   ```
   Or add the workspace `scripts/` to `sys.path` and import directly.

**Option B — Standalone preview**

Run the 13F page alone to test (requires Streamlit):

```bash
streamlit run scripts/streamlit_13f.py
```

Opens at http://localhost:8501 with Filers, Holdings, Diff, Copycat, Screener, Heat Map, Fund Metrics tabs.

**Environment**

- `13F_API_URL` — API base URL (default: http://localhost:8000)

---

## What each subsection shows

| Section | Purpose | What the user sees |
|--------|---------|--------------------|
| **Filers** | List of ingested 13F filings | **Fund name** (not just CIK), **Period** (e.g. Q3 2025), **Filed** (SEC filing date), **# Holdings**. "View Holdings →" pre-fills the Holdings tab for that filing. |
| **Holdings** | Positions for one filing | Pick by CIK + period or from a dropdown of ingested filings. Table: Issuer, CUSIP, Value ($K), **Weight %**. Total value caption. |
| **Diff** | Quarter-over-quarter changes | Pick filer (by name) and prior/current periods. **New Buys**, **Sells**, **Increased**, **Decreased** with position counts and tables. |
| **Copycat** | Combined portfolio from multiple funds | Select funds by **name** (multiselect). Weighting: value or equal. Optional consensus (min # of funds). Portfolio table with tickers and weights. |
| **Screener** | Institutional consensus | Slider: min # of funds holding. Names held by ≥N filers with total value; caption with count. |
| **Heat Map** | Exposure matrix | Top N filers × top M holdings; sliders for N and M. Table of values (fund × holding). |
| **Fund Metrics** | Concentration and overlap | Pick filer by name. Single period: holdings count, concentration (top 5/10/20%). Or compare two periods: **overlap %** (how much of prior quarter’s book is still held). |

---

## Data Source

- **13F JSON:** `outputs/13f/*.json` (from `scripts/ingest-13f.py`)
- **Query API:** Run `scripts/query-13f.py` (list filers, get holdings by cik/period) and consume JSON output
- **Copycat:** Run `scripts/copycat-13f.py --ciks X --out outputs/copycat.json` and read the JSON
- **Diff:** Run `scripts/13f-holdings-diff.py --cik X --prior P --current C --json-out outputs/13f-diff.json`
- **Heat map:** Run `scripts/13f-heatmap-export.py --format json --out outputs/13f-heatmap.json` (matrix: filers x CUSIPs)

---

## Suggested Views / Pages

| View | Data | How to Expose |
|------|------|----------------|
| **13F Filers** | `query-13f.py --list` | Table: CIK, period, path; link to Holdings by filer |
| **Holdings (filer + period)** | `query-13f.py --cik X --period Y` | Table: issuer, CUSIP, value, shares |
| **Holdings Diff** | `13f-holdings-diff.py --json-out ...` | Sections: New Buys, Sells, Increased, Decreased |
| **Copycat Portfolio** | `copycat-13f.py --out ...` | Table: name, CUSIP, weight %, value; optional chart |
| **Stock Screener** | `13f-stock-screener.py` | Table: name, CUSIP, total value, filer count; filter by min filers |
| **Heat Map** | `13f-heatmap-export.py` | Grid/heat map: filers (rows) x CUSIPs (cols), cell = value |
| **Fund Metrics** | `13f-fund-performance.py --cik X` | Cards: holdings count, concentration (top 5/10/20 %), overlap % |

---

## 13F API (Option B — implemented)

A **FastAPI bridge** runs the 13F scripts via subprocess and returns JSON. Use this so the dashboard can request data on-demand without reading files from disk.

### Run the API

From workspace root:

```bash
# Install (once)
pip install -r reference/requirements-13f-api.txt

# Start (default port 8000; use 0.0.0.0 to allow other devices on LAN)
python -m uvicorn scripts.13f_api:app --host 127.0.0.1 --port 8000
```

To allow dashboard from another machine: `--host 0.0.0.0`. Restart: stop with Ctrl+C, then run the same `uvicorn` command again.

### 13F first-run checklist

1. Run ingest (without `--sample`): `python scripts/ingest-13f.py --cik-list context/13f-filers.txt`
2. Set `SEC_EDGAR_USER_AGENT` if 403 occurs (e.g. `YourName/you@example.com`)
3. Verify Filers section shows real fund names (e.g. BERKSHIRE HATHAWAY INC)

**Base URL:** `http://localhost:8000`

**Cache:** In-memory, 5 min TTL. Override with env `13F_API_CACHE_TTL` (seconds).

**CORS:** Allowed for `http://localhost:3001`, `http://localhost:8501`, and 127.0.0.1.

### Endpoints

| Endpoint | Query params | Returns |
|----------|--------------|---------|
| `GET /api/13f/health` | — | `{ status, data_dir, data_dir_exists }` |
| `GET /api/13f/filers` | `data_dir` (opt) | `{ count, filings: [{ cik, periodEnd, path }] }` |
| `GET /api/13f/holdings` | `cik`, `period`, `cusip` (opt) | Full filing JSON with holdings |
| `GET /api/13f/diff` | `cik`, `prior`, `current` | `{ filer, priorPeriod, currentPeriod, diff: { newBuys, sells, increased, decreased } }` |
| `GET /api/13f/copycat` | `ciks`, `weight` (value\|equal), `consensus_min` (opt), `period` (opt) | `{ tickers, totalValue, filers, ... }` |
| `GET /api/13f/screener` | `min_filers`, `min_value` | `{ count, holdings: [{ cusip, ticker, name, totalValueThousands, filerCount }] }` |
| `GET /api/13f/heatmap` | `top_filers`, `top_cusips` (opt) | `{ filers, cusips, cusipInfo, matrix }` |
| `GET /api/13f/fund-metrics` | `cik`, `prior` (opt), `current` (opt) | `{ filer, metrics | prior/current/overlapPct }` |

**Example (dashboard fetch):**

```js
const res = await fetch('http://localhost:8000/api/13f/filers');
const data = await res.json();

const diff = await fetch('http://localhost:8000/api/13f/diff?cik=0001067983&prior=2025-06-30&current=2025-09-30');
const diffData = await diff.json();
```

### Dependencies

- **Python:** `fastapi`, `uvicorn`. Install with `pip install fastapi uvicorn` or use `reference/requirements-13f-api.txt` if present.

### Other options

- **Static exports:** Dashboard can still read pre-generated JSON from `outputs/` (e.g. after n8n or cron runs the scripts).
- **n8n:** Trigger ingest/diff/copycat on schedule; write to `outputs/` or Sheets; dashboard or API can read from there.

---

## Data Refresh Strategy

- **Manual (default):** Run `python scripts/ingest-13f.py --cik-list context/13f-filers.txt` from the workspace when you want fresh data. 13F filings are quarterly; refresh after quarter-end + ~45 days.
- **Scheduled (optional):** Add an n8n workflow or cron job to run ingest weekly if desired.

---

## File Locations (Dashboard Read)

| Output | Path | Refresh |
|--------|------|---------|
| Copycat portfolio | `outputs/copycat.json` | After `copycat-13f.py --out outputs/copycat.json` |
| Holdings diff | `outputs/13f-diff.json` | After `13f-holdings-diff.py --json-out outputs/13f-diff.json` |
| Heat map matrix | `outputs/13f-heatmap.json` | After `13f-heatmap-export.py --out outputs/13f-heatmap.json` |
| Screener | `outputs/13f-screener.json` | After `13f-stock-screener.py --out outputs/13f-screener.json` |
| Fund metrics | `outputs/13f-fund-metrics.json` | After `13f-fund-performance.py --out outputs/13f-fund-metrics.json` |

---

## Related

- Epic: `outputs/kanban-task-13f-service-epic.md`
- Data pipeline: `reference/13f-data-pipeline.md`
- Kanban task: `outputs/kanban-task-13f-dashboard-integration.md` (if created)
