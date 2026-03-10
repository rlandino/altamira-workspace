# /earnings-calendar — Earnings Calendar

Show an **overall view** of upcoming earnings (no argument) or earnings for a **ticker / watchlist** (with argument).

## Instructions

You are fetching earnings calendar data for Altamira Capital. Follow these steps exactly.

**Use the correct current date** for "today" (e.g. 2026-02-26). Do not use a hardcoded or stale date from workspace metadata.

---

### Step 1: Identify scope

- **No argument:** Produce an **overall view** of earnings coming up (see Step 2A and 3A).
- **Ticker provided ($ARGUMENTS):** Show upcoming earnings for that ticker only (see Step 2B and 3B).
- **Watchlist requested (e.g. "watchlist" or list of tickers):** Use the core watchlist from `context/watchlist.md` or default universe: AAPL, MSFT, GOOGL, AMZN, AVGO, COST, V, MA, META, NVDA, SPY. Show one row per ticker with next earnings date (see Step 2B and 3B).

---

### Step 2A: Fetch data — overall view (no argument)

Use FMP API (key: `FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz`). Base: `https://financialmodelingprep.com/api/v3`.

1. **Earnings calendar by date range** — from **today** through **today + 14 days** (covers "this week" and "next week"):
   ```
   GET /earning_calendar?from={TODAY}&to={TODAY+14}&apikey={KEY}
   ```
   Parse: `date`, `symbol`, `time` (bmo/amc), `fiscalDateEnding`, `epsEstimated`, `revenueEstimated`.

2. **Company names and market cap** — from the calendar response, collect **unique symbols**. Then fetch in batch (FMP allows multiple symbols in one request; if the list is long, chunk into requests of ~50 symbols):
   ```
   GET /quote/{symbol1,symbol2,...}?apikey={KEY}
   ```
   Or use `GET /profile/{symbol}` in batch if quote does not include name. From quote: `name` (company name), `marketCap`. From profile: `companyName`, `mktCap` (or use quote’s marketCap).

3. Build the overall-view table from the calendar rows, joining symbol → name and marketCap. Format **Quarter Ending** as e.g. "Jan/2026" (from `fiscalDateEnding`). Format **Market Cap** as T (trillions) or B (billions) with 2 decimals when useful (e.g. 4.51T, 580.53B).

---

### Step 3A: Present results — overall view (no argument)

Output a **table** with these columns (matching a typical earnings-calendar UI):

| Ticker | Company | Date | Time | Quarter Ending | Market Cap |
|--------|---------|------|------|-----------------|------------|
| NVDA   | NVIDIA Corporation | 02/25 | amc | Jan/2026 | 4.51T |
| HD     | The Home Depot, Inc. | 02/24 | — | Feb/2026 | 580.53B |
| …      | …      | …    | …   | …        | …   |

- **Date:** MM/DD format.
- **Time:** bmo / amc when available; otherwise "—" or leave blank.
- **Quarter Ending:** Derived from `fiscalDateEnding` (e.g. Jan/2026, Dec/2025).
- **Market Cap:** From quote (or profile); format as X.XXT or XXX.XXB.
- **Sort:** By date (ascending), then by ticker. Optionally state at the top: "Earnings from [today] through [today+14]. Today is [date]."

Add one line after the table: *"Avoid holding options through unplanned earnings (thesis). For a single ticker or watchlist view, use /earnings-calendar TICKER or /earnings-calendar watchlist. For full release analysis use /earnings-analysis TICKER."*

---

### Step 2B: Fetch data — ticker or watchlist (with argument)

Use FMP API (same key).

- **Single ticker:** `GET /historical/earning_calendar/{TICKER}` — get next 2–4 earnings dates (upcoming and recent).
- **Watchlist:** For each ticker in the watchlist, call `GET /historical/earning_calendar/{TICKER}` (or use `GET /earning_calendar?from={TODAY}&to={TODAY+90}` and filter by symbol). For each ticker, identify the **next** earnings date (earliest date ≥ today).

---

### Step 3B: Present results — ticker or watchlist

- **Single ticker:** Next 2–4 earnings dates with Date, EPS estimate, Revenue estimate, Time (bmo/amc). Note: "Avoid holding through unplanned earnings" (thesis).
- **Watchlist:** Table: **Ticker** | **Next Earnings Date** | **Days from today**. Flag any earnings within the next 14 days. Sort by next earnings date.

---

### Step 4: Optional

If portfolio positions exist in context, note which holdings have earnings in the next 30 days. Remind: for CSP/options, avoid expirations that span earnings.

---

## Context

- **Investment thesis:** Never hold options through unplanned earnings.
- **Full release analysis:** For a company's latest earnings (transcript, Q&A, sentiment), use `/earnings-analysis TICKER`.
