# Streamlit Portfolio App — Data Source

**App URL:** http://localhost:8501/Portfolio

---

## Finding the App Source

The Streamlit app that serves the Portfolio page is **not in this workspace**. To find its source:

1. **Where it might live**
   - Another repo or folder (e.g. `AI Automation`, Fincept, or a dedicated dashboard project)
   - Same machine: search for `.py` files containing `streamlit` or `st.` in your projects
   - Check how you start the app (shortcut, `streamlit run app.py`, etc.) — the working directory or script path is the app root

2. **What to look for**
   - A Python file that calls `streamlit run` or imports `streamlit`
   - Code that reads portfolio/dashboard data (e.g. `pd.read_csv`, `gspread`, Google Sheets API, or a path to a JSON/CSV)

3. **Once you find it**
   - Note the path(s) it uses for data (e.g. `./data/portfolio.json`, a Google Sheet ID, or an API)
   - To keep this workspace in sync: either copy that file into `context/` (e.g. `context/portfolio-export.json`) or set `GOOGLE_SHEET_ID` + credentials and use `scripts/refresh-portfolio-context.py --sheets`

---

## Data That Feeds the App (Canonical)

Regardless of where the app code lives, the **canonical portfolio data** in this setup is:

| Data | Stored In | Updated By |
|------|-----------|------------|
| Daily snapshot (value, P&L, delta, theta, cash %, VIX, SPY) | Google Sheet **Daily Dashboard** | n8n Daily Portfolio Snapshot @ 4:15 PM ET |
| Position-level (symbol, type, qty, value, weight %, Greeks) | Google Sheet **Position History** | n8n Daily Portfolio Snapshot @ 4:15 PM ET |

So the app almost certainly reads from:
- That same Google Sheet (via API or a sync), or
- A local export (JSON/CSV) produced from that sheet or from n8n

---

## Workspace Export

This workspace keeps an export in context for Claude and scripts:

- **context/portfolio-export.json** — Latest dashboard snapshot (JSON). Update manually or via script.
- **context/portfolio-details.md** — Human-readable snapshot + positions table. Refreshed when you run the refresh script.
- **context/current-data.md** — Includes a Portfolio (Dashboard) section; refreshed by `scripts/refresh-portfolio-context.py`.

To refresh from the same data that feeds the app:

```bash
# From Google Sheet (if credentials set)
python scripts/refresh-portfolio-context.py --sheets

# From local file (e.g. if app writes to context/)
python scripts/refresh-portfolio-context.py --local
```
