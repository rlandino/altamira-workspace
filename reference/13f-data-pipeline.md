# 13F Data Pipeline — Reference

> Ingest and query SEC 13F-HR holdings for the Automated 13F Holdings Diff & Copycat Portfolio Service.

---

## Overview

- **Ingest:** `scripts/ingest-13f.py` — fetches 13F-HR from SEC EDGAR, parses holdings, writes JSON.
- **Query:** `scripts/query-13f.py` — list filers/periods, get holdings by filer/period, filter by CUSIP.
- **Storage:** `outputs/13f/{cik}_{period_end}.json` (one file per filing).

---

## Ingest

### Live SEC (data.sec.gov + Archives)

```bash
# One filer, latest filing
python scripts/ingest-13f.py --cik 1067983

# Last N filings per filer
python scripts/ingest-13f.py --cik 1067983 --max-filings 4

# List of CIKs (one per line; # = comment)
python scripts/ingest-13f.py --cik-list context/13f-filers.txt

# Custom output directory
python scripts/ingest-13f.py --cik 1067983 --out-dir outputs/13f
```

### SEC Access

- **No API key.** SEC EDGAR is free.
- **User-Agent required.** SEC requires a descriptive User-Agent (company + contact). Default: `Altamira Capital contact@altamira-capital.com`. Override with env:
  ```bash
  set SEC_EDGAR_USER_AGENT=YourCompany contact@email.com
  ```
- **403 from Archives:** If you get 403 when fetching the primary document, set `SEC_EDGAR_USER_AGENT` to a valid company/contact string. Some networks may be rate-limited or blocked.

### Sample Data (no SEC fetch)

```bash
python scripts/ingest-13f.py --sample --out-dir outputs/13f
```

Writes one sample filing to `outputs/13f/0001067983_20250930.json` for testing holdings-diff and copycat.

**Note:** `--sample` is for pipeline testing only. Do not use for dashboard data — run ingest **without** `--sample` to fetch real SEC filings.

---

## Query

```bash
# List available filers and periods
python scripts/query-13f.py --list

# Holdings for a filer and period (period = YYYY-MM-DD or YYYYMMDD)
python scripts/query-13f.py --cik 0001067983 --period 2025-09-30

# Filter by CUSIP
python scripts/query-13f.py --cik 0001067983 --period 20250930 --cusip 037833100

# Write output to file
python scripts/query-13f.py --list --out filers.json
python scripts/query-13f.py --cik 0001067983 --period 2025-09-30 --out holdings.json
```

---

## JSON Schema (per filing)

| Field | Description |
|-------|-------------|
| `filer` | `{ cik, name }` |
| `periodEnd` | Period end date (YYYY-MM-DD or YYYYMMDD) |
| `filingDate` | Filing date |
| `form` | `13F-HR` or `13F-HR/A` |
| `accessionNumber` | SEC accession |
| `sourceUrl` | SEC Archives URL (empty for sample) |
| `holdingsCount` | Number of holdings |
| `holdings` | Array of holding objects |

### Holding object

| Field | Description |
|-------|-------------|
| `nameOfIssuer` | Issuer name |
| `titleOfClass` | e.g. COM |
| `cusip` | CUSIP |
| `value` | Market value (thousands) |
| `valueUsd` | Market value (USD) |
| `shrsOrPrnAmt` | Shares or principal |
| `investmentDiscretion` | e.g. SOLE |

---

## CUSIP → Ticker

- **Reference file:** `reference/cusip-to-ticker.json` (CUSIP → ticker). Add entries for names you care about.
- **Loader:** `scripts/cusip_loader.py` — `get_cusip_to_ticker()`, `cusip_to_ticker(cusip)`. Used by copycat-13f, 13f-backtest, 13f-stock-screener to add `ticker` to outputs when known.

---

## Downstream

- **Holdings diff:** `scripts/13f-holdings-diff.py` — compare two filings (prior vs current) for same filer → new buys, sells, increases, decreases.
- **Copycat portfolio:** `scripts/copycat-13f.py` — combine holdings from one or more filers → target portfolio (tickers + weights).
- **Fund performance:** `scripts/13f-fund-performance.py` — concentration, holdings count, overlap %.
- **Stock screener:** `scripts/13f-stock-screener.py` — aggregate by CUSIP (value, filer count); consensus via `--min-filers`.
- **Heat map:** `scripts/13f-heatmap-export.py` — export matrix (filers x CUSIPs) for visualization.
- **Backtester:** `scripts/13f-backtest.py` — backtest copycat/13F strategy with FMP prices.
- **Dashboard:** Surface 13F views at http://localhost:8501 (or 3001). See `reference/13f-dashboard-integration.md`.

---

## Related

- Epic: `outputs/kanban-task-13f-service-epic.md`
- Data pipeline task: `outputs/kanban-task-13f-data-pipeline.md`
- SEC EDGAR: https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=13F-HR
- SEC data.sec.gov: https://data.sec.gov/submissions/CIK{cik}.json (CIK zero-padded to 10)
