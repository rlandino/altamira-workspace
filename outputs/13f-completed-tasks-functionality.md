# 13F Completed Tasks — Functionality Summary

Overview of what each completed kanban task does and how to use it.

---

## 1. Epic: 13F Holdings Diff & Copycat Portfolio Service

**What it is:** The overall service that ties everything together: ingest SEC 13F-HR filings, compare holdings across periods, build copycat portfolios, screen by institutional ownership, export heat maps, backtest, and expose data via API for the dashboard.

**Delivered:** All sub-tasks below; data lives in `outputs/13f/`, scripts in `scripts/`, API at `http://localhost:8000`.

---

## 2. 13F Data Pipeline & API

**What it does:**

- **Ingest:** Fetches SEC 13F-HR filings from EDGAR (by CIK or from `context/13f-filers.txt`), parses the information table, and writes one JSON file per filing to `outputs/13f/{cik}_{period}.json`. Handles SEC rate limits and one retry on 403.
- **Query:** Lists filers/periods and returns holdings for a given filer + period (optionally filtered by CUSIP).

**Scripts:**

| Script | Purpose |
|--------|---------|
| `ingest-13f.py` | Pull filings from SEC; `--cik`, `--cik-list`, `--sample` for testing |
| `query-13f.py` | `--list` for filers/periods; `--cik` + `--period` for holdings JSON |

**Example:**

```bash
python scripts/ingest-13f.py --cik-list context/13f-filers.txt
python scripts/query-13f.py --list
python scripts/query-13f.py --cik 0001067983 --period 2025-09-30
```

---

## 3. 13F Holdings Diff (period-over-period)

**What it does:** Compares a filer’s 13F holdings between two reporting periods and reports:

- **New buys** — positions in current period not in prior
- **Sells** — positions in prior not in current
- **Increased** — same CUSIP, higher value/shares
- **Decreased** — same CUSIP, lower value/shares

**Script:** `13f-holdings-diff.py`  
**Output:** Markdown report and/or JSON for the dashboard.

**Example:**

```bash
python scripts/13f-holdings-diff.py --cik 0001067983 --prior 2025-06-30 --current 2025-09-30 --out report.md --json-out outputs/13f-diff.json
```

---

## 4. 13F Copycat Portfolio

**What it does:** Builds a target portfolio that mirrors one or more managers’ latest 13F holdings:

- **Value-weighted** — weights by reported value (default)
- **Equal-weight** — equal weight across names
- **Consensus** — only names held by at least N of the selected filers (`--consensus-min N`)

Output includes CUSIP, name, weight %, and ticker when CUSIP is in `reference/cusip-to-ticker.json`.

**Script:** `copycat-13f.py`  
**Example:**

```bash
python scripts/copycat-13f.py --ciks 0001067983,1350694 --weight equal --consensus-min 2 --out outputs/copycat.json
```

---

## 5. 13F Fund Performance (metrics)

**What it does:** Computes basic metrics from 13F filings (no market prices):

- **Holdings count** — number of positions
- **Concentration** — % of portfolio in top 5, top 10, top 20 names
- **Total reported value** — sum of position values
- **Overlap** — when comparing two periods, % of prior holdings still present (consistency)

**Script:** `13f-fund-performance.py`  
**Example:**

```bash
python scripts/13f-fund-performance.py --cik 0001067983 --prior 2025-06-30 --current 2025-09-30 --out outputs/13f-fund-metrics.json
```

---

## 6. 13F Stock Screener

**What it does:** Aggregates holdings across all ingested 13F filings:

- For each CUSIP/name: total value (across filers), number of filers holding it, optional ticker (from CUSIP map)
- Filter by **minimum filer count** (`--min-filers`) for “consensus” names
- Filter by **minimum aggregate value** (`--min-value`, in thousands)

**Script:** `13f-stock-screener.py`  
**Example:**

```bash
python scripts/13f-stock-screener.py --min-filers 2 --format csv --out outputs/13f-screener.csv
```

---

## 7. Combined Holdings (overlap / consensus)

**What it does:** “Combined holdings” and consensus are covered by:

- **Copycat** — `copycat-13f.py --consensus-min N` (only names held by N+ filers)
- **Stock screener** — `13f-stock-screener.py --min-filers N` (aggregate view of names held by N+ filers)

No separate script; functionality is in the two above.

---

## 8. 13F Backtester

**What it does:** Backtests a 13F-based portfolio over a date range:

- **Input:** A portfolio JSON (e.g. from `copycat-13f.py`) or a single filer’s filing (by CIK)
- **Prices:** FMP API historical prices; CUSIP→ticker via `reference/cusip-to-ticker.json` and `scripts/cusip_loader.py`
- **Output:** Total return %, annualized return %, and per-ticker contribution where tickers are known

**Script:** `13f-backtest.py` (requires `FMP_API_KEY`)  
**Example:**

```bash
python scripts/copycat-13f.py --ciks 0001067983 --out outputs/copycat.json
python scripts/13f-backtest.py --portfolio outputs/copycat.json --from 2025-09-30 --to 2026-02-20
```

---

## 9. 13F Heat Map export

**What it does:** Exports a matrix of 13F exposure for visualization:

- **Rows:** filers (or CUSIPs with `--transpose`)
- **Columns:** CUSIPs (or filers with `--transpose`)
- **Cells:** reported value (thousands)
- Optional limits: `--top-filers`, `--top-cusips` to keep matrix size manageable

**Script:** `13f-heatmap-export.py`  
**Output:** JSON (`filers`, `cusips`, `matrix`) or CSV.

**Example:**

```bash
python scripts/13f-heatmap-export.py --format json --out outputs/13f-heatmap.json
python scripts/13f-heatmap-export.py --top-filers 20 --top-cusips 50 --format csv
```

---

## 10. Dashboard integration (Option B: API)

**What it does:** A FastAPI app that runs the 13F scripts and returns JSON so the dashboard (or any client) can get data without reading files:

- **Base URL:** `http://localhost:8000`
- **Cache:** In-memory, 5 min TTL
- **CORS:** Allowed for local dashboard (e.g. 3001, 8501)

**Endpoints:**

| Endpoint | Purpose |
|----------|---------|
| `GET /api/13f/health` | Health check, data dir status |
| `GET /api/13f/filers` | List filers and periods |
| `GET /api/13f/holdings` | Holdings for `cik` + `period` |
| `GET /api/13f/diff` | Holdings diff (`cik`, `prior`, `current`) |
| `GET /api/13f/copycat` | Copycat portfolio (`ciks`, `weight`, `consensus_min`) |
| `GET /api/13f/screener` | Stock screener (`min_filers`, `min_value`) |
| `GET /api/13f/heatmap` | Heat map matrix (`top_filers`, `top_cusips`) |
| `GET /api/13f/fund-metrics` | Fund metrics (`cik`, optional `prior`/`current`) |

**Run:**

```bash
python -m uvicorn scripts.13f_api:app --host 127.0.0.1 --port 8000
```

**Reference:** `reference/13f-dashboard-integration.md`

---

## Quick reference

| Task | Script(s) | Key output / API |
|------|-----------|-------------------|
| Data pipeline | `ingest-13f.py`, `query-13f.py` | `outputs/13f/*.json`, `--list` / `--cik` + `--period` |
| Holdings diff | `13f-holdings-diff.py` | `--out` report, `--json-out` |
| Copycat | `copycat-13f.py` | `--out` JSON; value / equal / consensus-min |
| Fund metrics | `13f-fund-performance.py` | Concentration, overlap, holdings count |
| Stock screener | `13f-stock-screener.py` | Aggregate by CUSIP; `--min-filers` |
| Combined holdings | Copycat + screener | Consensus via `--consensus-min` / `--min-filers` |
| Backtester | `13f-backtest.py` | Return %, per-ticker (FMP + CUSIP map) |
| Heat map | `13f-heatmap-export.py` | JSON/CSV matrix filers × CUSIPs |
| Dashboard API | `13f_api.py` (uvicorn) | All of the above via HTTP at port 8000 |

**Shared:** CUSIP→ticker mapping: `scripts/cusip_loader.py` + `reference/cusip-to-ticker.json`. Curated filers: `context/13f-filers.txt`.
