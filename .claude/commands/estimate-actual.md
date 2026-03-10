# /estimate-actual — Quarterly Revenue & EPS Actuals, Estimates, and Growth

Retrieve quarterly **Revenue** and **EPS** actuals and estimates for a ticker, compute **% variance** (actual vs estimate) and **Growth (%)** (YoY), and output markdown tables plus two line charts (Sales Growth %, Earnings Growth %).

## Instructions

You are producing an estimate vs actual report for Altamira Capital. Follow these steps exactly.

### Step 1: Get the ticker

The user provides a ticker as the argument: **$ARGUMENTS** (e.g. COST, AVGO).

- If no ticker is provided, ask: "Please provide a ticker symbol, e.g. /estimate-actual COST."
- Normalize to a single uppercase symbol (e.g. cost → COST).

### Step 2: Fetch data

Use **FMP API** (key: `FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz`).

**FMP stable** (base: `https://financialmodelingprep.com/stable` — append `?apikey={KEY}` or `&apikey={KEY}`):

1. **Earnings (quarterly actuals + estimates):**
   ```
   GET /earnings?symbol={TICKER}&apikey={KEY}
   ```
   Response fields: `date`, `fiscalYear`, `quarter`, `revenueActual`, `revenueEstimated`, `epsActual`, `epsEstimated`. Use this as the primary source. Map each row to **QX YY** from fiscalYear + quarter, or from date (quarter = ceil(month/3), YY = year % 100).

**FMP v3** (base: `https://financialmodelingprep.com/api/v3`):

2. **Quote (optional)** — for company name in report header:
   ```
   GET /quote/{TICKER}?apikey={KEY}
   ```
   Use `name` for "Estimate vs Actual — {name} ({TICKER})".

3. **Analyst estimates (optional)** — if stable earnings has no estimate for future quarters, merge by period:
   ```
   GET /analyst-estimates/{TICKER}?limit=12&apikey={KEY}
   ```

### Step 3: Build series and compute metrics

- For each quarter in the earnings response, derive **QX YY** (e.g. Q1 24, Q2 24). Sort quarters chronologically (year, quarter ascending).
- **Revenue:** For each quarter, take `revenueActual` and `revenueEstimated` (use analyst-estimates to fill forward if needed). **Variance %** = (actual − estimate) / |estimate| × 100 when estimate ≠ 0; otherwise "—" or "N/A".
- **EPS:** Same for `epsActual` and `epsEstimated`; compute variance % when estimate ≠ 0.
- **Growth % (YoY):** For each quarter, value = actual if present else estimate. Growth % = (value − same_quarter_prior_year_value) / |same_quarter_prior_year_value| × 100. If prior year same quarter is missing, use "—" or "N/A".

### Step 4: Write tables in markdown

Create **`outputs/estimate-actual-{TICKER}-{DATE}.md`** (use today's date in YYYY-MM-DD). Ensure `outputs/` exists.

- **Header:** "Estimate vs Actual — {Company Name} ({TICKER})".
- **Revenue section:** Table with columns = Q1 24, Q2 24, … (all quarters in order). Rows: **Revenue Actual**, **Revenue Estimate**, **Variance %**, **Growth % (YoY)**. Use "—" or "N/A" when data is missing. Format revenue in B (billions) or M (millions) for readability; variance and growth as percentages (e.g. +3.2%, -1.1%).
- **EPS section:** Table with same quarter columns. Rows: **EPS Actual**, **EPS Estimate**, **Variance %**, **Growth % (YoY)**. Format EPS to 2 decimal places.
- Add a short note when a quarter has only estimates (e.g. "Quarters with actuals through Q4 25; Q1 26–Q2 26 are estimates.").

### Step 5: Generate charts

Run the chart script from the workspace root:

```bash
python scripts/estimate_actual_chart.py --ticker {TICKER} --date {DATE} --out-dir outputs
```

Use today's date for `{DATE}` if not specified. If the script fails (e.g. no data, script missing), note in the report: "Charts not generated (run `python scripts/estimate_actual_chart.py --ticker {TICKER}` manually)." Do not fail the whole command; tables are still required.

### Step 6: Embed chart images

In the same markdown file, add two sections and embed the PNGs:

```markdown
## Sales Growth

![Sales Growth](outputs/estimate-actual-{TICKER}-revenue-growth-{DATE}.png)

## Earnings Growth

![Earnings Growth](outputs/estimate-actual-{TICKER}-eps-growth-{DATE}.png)
```

If the chart script did not run successfully, write "Charts not generated." instead of the image markdown.

### Edge cases

- **No earnings data:** State "No quarterly earnings data found for {TICKER}." Do not write the report file.
- **Partial data:** Show available quarters only; use "—" or "N/A" for missing cells.
- **Script failure:** Report still includes tables; chart sections show "Charts not generated" and the manual run instruction.

End with a one-line summary (e.g. "Estimate vs actual report for {TICKER} written to outputs/estimate-actual-{TICKER}-{DATE}.md.")

## Context

- **FMP stable:** `https://financialmodelingprep.com/stable` — `earnings?symbol=` returns quarterly rows with date, fiscalYear, quarter, revenueActual, revenueEstimated, epsActual, epsEstimated.
- **Chart script:** `scripts/estimate_actual_chart.py` — fetches earnings, computes YoY growth %, plots Sales Growth and Earnings Growth (solid line = actuals, dashed = estimates), saves `outputs/estimate-actual-{TICKER}-revenue-growth-{DATE}.png` and `outputs/estimate-actual-{TICKER}-eps-growth-{DATE}.png`. Same pattern as `scripts/briefing_chart.py` (matplotlib, Agg backend).
