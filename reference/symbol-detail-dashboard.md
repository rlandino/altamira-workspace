# Symbol Detail — Dashboard Integration

> How to use the Symbol Detail section and make tickers clickable across the Altamira Dashboard.

---

## Overview

**Symbol Detail** is a dedicated page that shows, for a given ticker:

- **Header:** Company name, logo, market cap, industry, next earnings date, real-time price, market open/closed
- **Quote Panel:** Price and volume chart with 1W / 1M / 3M / 1Y selector
- **Fundamentals, Relative Strength, Forecast:** Key ratios, performance chart, analyst price target and estimates
- **Key Metrics:** Three cards (range/industry/website/sector; market cap/shares/dividend; earnings date/price target/volume/beta)
- **Growth:** Earnings growth, Sales growth, Return on Equity, Institutional ownership — each with a table and “Show Graph”

Data is loaded from the **Market Data API** (FMP proxy at `http://localhost:8001` by default).

---

## Deploy to Dashboard (Streamlit)

### Prerequisites

1. **Market Data API** running (port 8001):
   ```bash
   python -m uvicorn scripts.market_data_api:app --host 0.0.0.0 --port 8001
   ```
2. **FMP_API_KEY** set in the environment (or use the default in the API script).

### Deploy Symbol Detail into the app

From the workspace root:

```bash
python scripts/deploy-symbol-detail-to-app.py --app-dir "X:\path\to\your\streamlit-app"
```

This copies:

- `streamlit_symbol_detail.py` into the app root
- `pages/2_Symbol_Detail.py` into the app’s `pages/` folder

Symbol Detail will appear in the sidebar (e.g. “2_Symbol_Detail”). Open it with `?ticker=WM` or by clicking a ticker link from another section.

**Optional:** Set `MARKET_DATA_API_URL` in the Streamlit app environment if the API is not at `http://localhost:8001`.

---

## Making tickers clickable (Dashboard ticker linking)

Any section that shows a ticker should link to Symbol Detail so users can open the detail view in one click.

**Convention:** Use Streamlit’s `st.page_link` with query param `ticker`:

```python
st.page_link(
    "pages/2_Symbol_Detail.py",
    label="WM",  # or "View Symbol Detail → WM"
    query_params={"ticker": "WM"},
)
```

**Already wired:**

- **Holding Snapshot** (`scripts/streamlit_holding_snapshot.py`): Each expander has a “View Symbol Detail → {ticker}” link.
- **13F Copycat** (`scripts/streamlit_13f.py`): After the copycat table, tickers from the response are shown as Symbol Detail links.

**Adding links in other sections:** Wherever you render a ticker (portfolio table, screener, watchlist, etc.), add a `st.page_link` to `pages/2_Symbol_Detail.py` with `query_params={"ticker": symbol}`. Use the same pattern so all tickers behave consistently.

---

## API usage (Symbol Detail data)

The Symbol Detail fragment calls these Market Data API endpoints (all under the base URL, e.g. `http://localhost:8001`):

| Endpoint | Purpose |
|----------|--------|
| `GET /api/symbol/{symbol}/profile` | Company name, logo, sector, industry, website, marketCap |
| `GET /api/market/quote?symbol=` | Real-time price, change, marketCap |
| `GET /api/symbol/{symbol}/next-earnings` | Next earnings date |
| `GET /api/market/status` | Market open/closed |
| `GET /api/symbol/{symbol}/historical?from=&to=` | Historical prices and volume for Quote Panel |
| `GET /api/symbol/{symbol}/key-metrics` | Key metrics for Fundamentals and Key Metrics cards |
| `GET /api/symbol/{symbol}/price-target` | Analyst price target for Forecast |
| `GET /api/symbol/{symbol}/analyst-estimates` | Revenue/EPS estimates for Forecast |
| `GET /api/symbol/{symbol}/growth` | Earnings growth, sales growth, ROE, institutional for Growth section |

See `scripts/market_data_api.py` for implementation and FMP proxy details.

---

## Running Symbol Detail standalone

To preview the fragment without the full app:

```bash
streamlit run scripts/streamlit_symbol_detail.py
```

Then open `http://localhost:8501?ticker=WM` or enter a ticker in the input.

---

## Files

| File | Role |
|------|------|
| `scripts/market_data_api.py` | FMP proxy; Symbol Detail endpoints |
| `scripts/streamlit_symbol_detail.py` | Fragment: `render_symbol_detail(symbol)` |
| `pages/2_Symbol_Detail.py` | Page: reads `st.query_params.get("ticker")`, calls fragment |
| `scripts/deploy-symbol-detail-to-app.py` | Deploy fragment + page into app dir |
