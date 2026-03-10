# /eps-estimate — EPS Estimates by Quarter

Retrieve analyst EPS estimates for a ticker and show them in a table with columns **Q1 YY**, **Q2 YY**, … (quarter number 1–4 and 2-digit year).

## Instructions

You are fetching EPS estimates for Altamira Capital. Follow these steps exactly.

### Step 1: Get the ticker

The user provides a ticker as the argument: **$ARGUMENTS** (e.g. COST, AAPL).

- If no ticker is provided, ask: "Please provide a ticker symbol, e.g. /eps-estimate COST."
- Normalize to a single uppercase symbol (e.g. cost → COST).

### Step 2: Fetch data

Use **FMP API** (key: `FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz`). Base: `https://financialmodelingprep.com/api/v3`.

1. **Analyst estimates (quarterly/period):**
   ```
   GET /analyst-estimates/{TICKER}?limit=12&apikey={KEY}
   ```
   Response fields: `date` (YYYY-MM-DD period end), `estimatedEpsAvg`, `estimatedEpsLow`, `estimatedEpsHigh`, `numberAnalystsEstimatedEps`. Each row is one fiscal period (FMP may return annual or quarterly depending on ticker).

2. **Company name (optional):**
   ```
   GET /quote/{TICKER}?apikey={KEY}
   ```
   Use `name` for a one-line header: "EPS estimates — {name} ({TICKER})".

### Step 3: Build period labels and sort

For each estimate row, derive the column label **QX YY** from `date`:

- **If `date` is YYYY-MM-DD:** Quarter = ceil(month / 3) (1–4). Year = last two digits (e.g. 2026 → 26). Label = "Q{quarter} {YY}" (e.g. Q3 26).
- **If the API returns explicit `quarter` and `calendarYear` (or `fiscalYear`):** Use them directly for Q and YY.

Sort periods by (year, quarter) **ascending** so the table reads left-to-right chronologically. Deduplicate by (year, quarter) if multiple rows map to the same label; keep the one with the latest `date` or first occurrence.

### Step 4: Output the table

- **Header row:** One column per period: `| Q1 26 | Q2 26 | Q3 26 | Q4 26 | Q1 27 | … |`.
- **Data row(s):** Use **estimatedEpsAvg** (consensus) as the main EPS value for each period. Format to 2 decimal places (e.g. 4.55). Optionally add a second row for **Low** (estimatedEpsLow) and **High** (estimatedEpsHigh) if useful.
- **Optional header line:** Above the table: "EPS estimates — {Company Name} ({TICKER})".
- **Write to file:** Save the table (and optional header) to **`outputs/eps-estimate-{TICKER}-{DATE}.md`** (use today's date in YYYY-MM-DD). Ensure `outputs/` exists.

End with a one-line summary (e.g. "EPS estimates for {TICKER} written to outputs/eps-estimate-{TICKER}-{DATE}.md.").

### Edge cases

- **Empty or missing data:** If the API returns `[]` or no rows, state: "No EPS estimates found for {TICKER}. Check the symbol or FMP coverage." Do not write a file.
- **Single period:** One column is fine (e.g. `| Q2 26 |`).
- **Invalid ticker:** If the request fails or returns empty, suggest checking the symbol and try again.

## Context

- **FMP v3:** `https://financialmodelingprep.com/api/v3` — `analyst-estimates` returns period-end `date`, `estimatedEpsAvg`, `estimatedEpsLow`, `estimatedEpsHigh`. Periods may be annual (e.g. fiscal year-end) or quarterly; column label is always derived from the date as Qx YY.
- **Fallback:** If you need strictly quarterly estimates and v3 returns only annual, you can try FMP stable: `GET https://financialmodelingprep.com/stable/analyst-estimates?symbol={TICKER}&period=quarter&page=0&limit=12&apikey={KEY}` and map its period fields to Qx YY the same way.
