# /company-growth — Company Growth Evaluation

Evaluate a company's growth using **core four metrics** (Revenue, Adjusted EPS, Free Cash Flow Margin, ROIC) with 3-year CAGR and latest YoY growth, plus **optional metrics** (margins, Rule of 40, ROE, FCF $ growth, revenue trajectory). Assign a letter grade (A–F), explain the reason, and list metrics to monitor.

## Instructions

You are running a company growth evaluation for Altamira Capital. Follow these steps exactly.

### Step 1: Resolve ticker

The user provides a ticker symbol as the argument: **$ARGUMENTS** (e.g. AVGO, COST, MSFT).

- If no ticker is provided, ask: "Please provide a ticker symbol, e.g. /company-growth AVGO."
- Normalize to a single uppercase symbol (e.g. avgo → AVGO).

**Output path:** `outputs/company-growth-{TICKER}-{DATE}.md` (use today's date in YYYY-MM-DD). Ensure `outputs/` exists.

---

### Step 2: Fetch data

Use **FMP API** (key: `FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz`). Base: `https://financialmodelingprep.com/api/v3`. Make these calls in parallel where possible.

1. **Income statement (annual):** `GET /income-statement/{TICKER}?period=annual&limit=5&apikey={KEY}` — revenue, grossProfit, operatingIncome, netIncome.
2. **Cash flow (annual):** `GET /cash-flow-statement/{TICKER}?period=annual&limit=5&apikey={KEY}` — operatingCashFlow, capitalExpenditure.
3. **Key metrics (annual):** `GET /key-metrics/{TICKER}?period=annual&limit=5&apikey={KEY}` — returnOnInvestedCapital, returnOnCapitalEmployed, netIncomePerShare, ebitda, marketCap; shares if needed for EPS.
4. **Ratios (annual):** `GET /ratios/{TICKER}?period=annual&limit=5&apikey={KEY}` — returnOnEquity, returnOnInvestedCapital, assetTurnover, netProfitMargin.
5. **Financial growth (annual):** `GET /financial-growth/{TICKER}?period=annual&limit=5&apikey={KEY}` — revenueGrowth, netIncomeGrowth (for YoY/CAGR when available).
6. **Balance sheet (annual):** `GET /balance-sheet-statement/{TICKER}?period=annual&limit=5&apikey={KEY}` — totalAssets (for asset turnover), totalStockholdersEquity (for ROE if needed). Shares for EPS may be in key-metrics (weightedAverageShares) or income statement.
7. **Quote:** `GET /quote/{TICKER}?apikey={KEY}` — company name, price (for PEG if needed).
8. **Profile:** `GET /profile/{TICKER}?apikey={KEY}` — company name.
9. **Analyst estimates (optional):** `GET /analyst-estimates/{TICKER}?limit=4&apikey={KEY}` — for forward growth (PEG).

Sort all time-series responses by **date ascending** (oldest first). You need at least 4 full years for 3yr CAGR; 5 years preferred. **Optional:** For consistent numeric output run `python scripts/company_growth_metrics.py --ticker {TICKER}` (or `--out outputs/company-growth-{TICKER}-metrics.json`). The script returns JSON with `core_four` (revenue, eps, fcf_margin, roic: 3yr_cagr_pct, latest_yoy_pct, latest_value), `optional` (operating_margin_pct, net_income_yoy_pct, fcf_dollar_3yr_cagr_pct, roe_pct, etc.), `rule_of_40` (score, tier), `revenue_trajectory`, and `suggested_grade`. Use these to populate the report when available.

---

### Step 3: Build series and compute metrics

Align all series by **fiscal year / date**. Use the same period alignment across income, cash flow, key-metrics, and ratios (match on `date` or calendar year).

**Formulas:**

- **3-year CAGR:** `CAGR = (value_T / value_T−3)^(1/3) − 1`, expressed as a percentage. Use most recent year as T and the year three years earlier as T−3. If value_T−3 or value_T is zero or negative, report "N/A".
- **Latest YoY %:** `YoY = (value_T − value_T−1) / |value_T−1| × 100`. If value_T−1 is zero, report "N/A".
- **Margins (FCF, operating, gross, EBITDA):** For YoY, use **percentage-point change** (e.g. "FCF margin +2.1 pp YoY") or % change in the ratio; for CAGR apply the same CAGR formula to the ratio (e.g. margin 10% → 15% over 3 years).
- **ROIC / ROE:** YoY = % change in the ratio (e.g. "ROIC +5% YoY"); CAGR = (value_T / value_T−3)^(1/3) − 1 on the ratio.

**Core four (grade drivers):**

| Metric | Source | Compute |
|--------|--------|--------|
| Revenue | Income statement `revenue` | 3yr CAGR %, Latest YoY %, Latest value (e.g. $B) |
| Adjusted EPS | Income: `netIncome`; shares from key-metrics `weightedAverageShares` or income statement field if present; else derive from balance sheet. EPS = netIncome / shares. If FMP has only GAAP, label "EPS (GAAP)". | 3yr CAGR %, Latest YoY %, Latest value |
| FCF margin | Cash flow: (operatingCashFlow − capitalExpenditure); revenue from income same period. FCF margin = FCF / revenue × 100. | 3yr CAGR %, Latest YoY (pp or %), Latest value (%) |
| ROIC | Key-metrics `returnOnInvestedCapital` or ratios; fallback `returnOnCapitalEmployed`. If stored as decimal (e.g. 0.15), use as 15%. | 3yr CAGR %, Latest YoY %, Latest value (%) |

**Optional metrics (full report):**

- **Operating margin:** operatingIncome / revenue per year → 3yr trend + YoY; latest value (%).
- **Net income growth:** From income statement `netIncome` or financial-growth `netIncomeGrowth` → 3yr CAGR % + latest YoY %.
- **Gross margin:** grossProfit / revenue per year → 3yr trend + YoY.
- **EBITDA margin:** Key-metrics `ebitda` or income + D&A; divide by revenue → 3yr trend + YoY.
- **ROE:** Ratios `returnOnEquity` (or netIncome / totalStockholdersEquity) → 3yr trend + YoY.
- **FCF (dollars):** operatingCashFlow − capitalExpenditure per year → 3yr CAGR % + latest YoY %.
- **Rule of 40:** Revenue growth % (latest YoY) + Operating margin % (or net margin if unprofitable). Tier: **Elite** ≥40, **Solid** 20–40, **Weak** &lt;20.
- **Revenue growth trajectory:** From annual (and optionally quarterly) revenue YoY series: state whether growth is **Accelerating** or **Decelerating** over 3–5 years and recent periods.
- **PEG ratio (optional):** P/E (quote or key-metrics) ÷ expected growth rate (analyst-estimates or financial-growth). If unavailable, omit or "N/A".
- **Asset turnover (optional):** Ratios or revenue / total assets → 3yr trend.

Handle N/A for any metric when denominator is zero or data is missing; omit optional metrics that cannot be computed.

---

### Step 4: Compute grade (core four only)

The **letter grade (A–F)** is based **only** on the four core metrics: Revenue, Adjusted EPS, FCF margin, ROIC. Use the **Grade scale** in Context below. Combine the four into a composite (e.g. average letter converted to score, or worst-of, or band-based). Produce:

- One **letter grade** (A, B, C, D, or F).
- **Reason for grade:** 2–4 sentences tying the grade to the core four (which metrics are strong, which weak, direction of trend). Do not cite optional metrics in the grade reason.

---

### Step 5: Write report

Write the markdown report to **`outputs/company-growth-{TICKER}-{DATE}.md`**.

1. **Header** — Company name (from profile or quote), ticker, report date (YYYY-MM-DD), one-line summary (e.g. "Growth evaluation: core four plus margins, Rule of 40, and trajectory.").

2. **Core growth metrics table** — Table with rows: Revenue, Adjusted EPS (or EPS GAAP), Free Cash Flow Margin, ROIC. Columns: **Metric** | **3yr CAGR %** | **Latest YoY %** | **Latest value**. These four drive the grade.

3. **Grade** — Line: **Grade: {Letter}.** Then **Reason for grade:** 2–4 sentences (core four only).

4. **Full optional metrics** — Second table or bullet list:
   - Operating margin (3yr trend + YoY, latest %)
   - Net income growth (3yr CAGR % + latest YoY %)
   - Gross margin, EBITDA margin (3yr trend + YoY, latest %)
   - ROE (3yr trend + YoY, latest %)
   - FCF growth $ (3yr CAGR % + latest YoY %)
   - **Rule of 40:** score and tier (Elite / Solid / Weak)
   - **Revenue growth trajectory:** Accelerating / Decelerating (one line)
   - Optional: PEG ratio, Asset turnover (3yr trend)
   Use "N/A" or omit rows for missing data.

5. **Metrics to monitor** — Bullet list of 3–6 items: what to watch going forward (e.g. "Revenue deceleration in next quarters", "FCF margin sustainability", "ROIC vs cost of capital", "EPS consistency vs consensus", "Rule of 40 trend").

6. **Caveats** — Data source (FMP). Note when "Adjusted EPS" is GAAP (FMP has no non-GAAP). Note missing or partial data, negative/loss-year handling for CAGR/YoY. Optional: "For earnings timing run /earnings-calendar {TICKER}. For trade ideas run /options-scan {TICKER}."

End with a one-line summary in chat (e.g. "Company growth report for {TICKER} written to outputs/company-growth-{TICKER}-{DATE}.md.")

---

## Edge cases

- **No data or empty response:** State "No sufficient annual data found for {TICKER}. Check symbol or FMP coverage." Do not write the report file.
- **Fewer than 4 years:** Compute latest YoY where possible; 3yr CAGR requires T and T−3 — if not available, show "N/A" for CAGR and note in caveats.
- **Negative revenue or loss years:** CAGR may be undefined (negative/zero base); report "N/A" and explain in caveats.
- **Missing ROIC:** Use ratios `returnOnInvestedCapital` or `returnOnCapitalEmployed`; if both missing, "N/A" and exclude from grade or use fewer metrics per Context grade rules.
- **Missing optional metrics:** Omit from full section or show "N/A"; do not fail the report.

---

## Context

- **Altamira Capital** uses this command to evaluate company growth quality and trajectory. The grade is comparable across tickers.
- **FMP:** All data from FMP API v3 (and stable if earnings used for EPS). Same API key as other commands. Income statement, cash flow, key-metrics, ratios, financial-growth (annual, limit=5); quote, profile; optional analyst-estimates.
- **Output path:** `outputs/company-growth-{TICKER}-{DATE}.md`. Paths relative to workspace root.

### Formulas (reference)

- **3yr CAGR:** `(value_latest / value_3y_ago)^(1/3) − 1` (as percentage).
- **Latest YoY:** `(value_latest − value_prior_year) / |value_prior_year| × 100`.
- **Rule of 40:** Revenue growth % + Operating margin % (or net margin if negative). Elite ≥40, Solid 20–40, Weak &lt;20.

### Grade scale (A–F) — core four only

**Step 1 — Sub-grade each core metric (1–5 scale, 5 = best):** Use the bands below. Then average the sub-grades (only for metrics that are not N/A) and map the average to letter: 4.5–5 → A, 3.5–4.49 → B, 2.5–3.49 → C, 1.5–2.49 → D, 0–1.49 → F. Alternatively use **worst-of**: if any metric is D or F, cap the grade at D; if any is F, cap at F.

**Revenue 3yr CAGR %:** A ≥15%, B 10–15%, C 5–10%, D 0–5%, F &lt;0% (or N/A).  
**EPS 3yr CAGR %:** A ≥15%, B 10–15%, C 5–10%, D 0–5%, F &lt;0% or loss (or N/A).  
**FCF margin:** Consider level and trend (CAGR of margin or YoY pp change). A = expanding and &gt;15%; B = stable/expanding and &gt;10%; C = flat or 5–10%; D = declining or 0–5%; F = negative or sharply declining.  
**ROIC %:** A ≥20% and stable/up; B ≥15%; C ≥10%; D &lt;10% or declining; F &lt;5% or N/A.

**Step 2 — Combine:** Average sub-grades (1–5) for the available metrics, then map: 4.5–5 → A, 3.5–4.49 → B, 2.5–3.49 → C, 1.5–2.49 → D, 0–1.49 → F. Or use worst-of rule above for a stricter grade.

**Narrative bands (for "Reason for grade"):**

- **A — Excellent:** Strong growth across core four: revenue and EPS CAGRs solid (e.g. revenue ≥10%, EPS positive and meaningful); FCF margin stable or expanding; ROIC stable or improving and above cost of capital. No material deterioration.
- **B — Good:** Solid growth; one or two metrics slightly weak but no major red flags. Revenue/EPS CAGRs positive; FCF margin and ROIC acceptable.
- **C — In line:** Mixed: some strength, some weakness. Growth modest or decelerating; margins or ROIC flat or slightly down. Average quality.
- **D — Below expectations:** Weak growth or deteriorating: revenue or EPS CAGR low or negative; FCF margin or ROIC declining. Notable concerns.
- **F — Poor:** Materially weak: negative revenue or EPS growth, margin compression, or ROIC well below cost of capital. Loss-making or severe deterioration.

**When a metric is N/A:** Exclude it from the composite; grade from the remaining metrics. If only one or two available, state in caveats and use narrower basis for grade.

**Adjusted EPS:** FMP often provides GAAP net income and shares; "Adjusted EPS" may be labeled "EPS (GAAP)" in the report. Note in caveats when non-GAAP adjusted EPS is not available.
