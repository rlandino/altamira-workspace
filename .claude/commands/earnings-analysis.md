# /earnings-analysis — Full Earnings Release Analysis

Produce a full analysis of a company's **latest earnings release**: earnings report data, press release, earnings call transcript (highlights + Q&A visibility), sentiment analysis of management's answers, and a concise verdict.

## Instructions

You are running an earnings release analysis for Altamira Capital. Follow these steps exactly.

### Step 1: Resolve ticker

The user will provide a ticker symbol as an argument: **$ARGUMENTS**

If no ticker is provided, ask for one. Default universe (for reference): AAPL, AMZN, AVGO, COST, GOOGL, MA, META, MSFT, NVDA, SPY, V.

---

### Step 2: Fetch data

Use **FMP API** (key: `FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz`). Make these calls in parallel where possible.

**FMP stable** (base: `https://financialmodelingprep.com/stable` — append `?apikey={KEY}` or `&apikey={KEY}`):

1. **Earnings report** (actual vs estimate) — **primary source for "latest" period:**
   ```
   GET /earnings?symbol={TICKER}&apikey={KEY}
   ```
   From the response, identify the **most recent earnings report that has actuals** (i.e. the first entry where `epsActual` and/or `revenueActual` are not null, and `date` is the report date). That date is the **latest earnings date** (e.g. 2026-02-25). Use it for the earnings snapshot and as the report period. Map that report date to a fiscal year and quarter (e.g. from transcript-dates or by calendar: Q1 Jan–Apr, Q2 May–Jul, Q3 Aug–Oct, Q4 Nov–Jan depending on company fiscal year).

2. **Transcript dates** (to request transcript for that period):
   ```
   GET /earning-call-transcript-dates?symbol={TICKER}&apikey={KEY}
   ```
   Find the entry whose **date** matches the latest earnings report date from step 1 (e.g. 2026-02-25). Use that entry's **fiscalYear** and **quarter** for the transcript request. If no transcript date matches the latest earnings date, the transcript for that call may not be available yet (transcripts often lag by hours or days); proceed to step 3 and still request the transcript; if the API returns empty, note in the report that the transcript is not yet available.

3. **Earnings call transcript** (full text):
   ```
   GET /earning-call-transcript?symbol={TICKER}&year={Y}&quarter={Q}&apikey={KEY}
   ```
   Use the fiscalYear and quarter from step 2 (matching latest earnings date). If the transcript is not yet available, the report should still include the earnings snapshot, press release, market context, and assessment; in the Q&A and sentiment sections state that the transcript for this period is not yet available in FMP and will be added when published.

4. **Press releases** (filter by symbol/date to match latest earnings period):
   ```
   GET /news/press-releases-latest?page=0&limit=20&apikey={KEY}
   ```
   If the endpoint supports a symbol parameter, use it; otherwise filter results by ticker or announcement date matching the earnings period. **Check each item for URL fields** (e.g. `url`, `link`, `source`) that point to the company site, press release page, or attached presentation (PDF/PPTX).

**FMP v3** (base: `https://financialmodelingprep.com/api/v3`):

5. **Quote:** `GET /quote/{TICKER}?apikey={KEY}`
6. **Profile:** `GET /profile/{TICKER}?apikey={KEY}`
7. **Earnings surprises:** `GET /earnings-surprises/{TICKER}?apikey={KEY}`
8. **Analyst estimates:** `GET /analyst-estimates/{TICKER}?limit=8&apikey={KEY}` (use for current quarter and next-quarter revenue/EPS/EBITDA estimates).
9. **Earnings calendar (historical):** `GET /historical/earning_calendar/{TICKER}?apikey={KEY}`

**For Highlights section (quarterly metrics and comparisons):**

10. **Income statement (quarterly):** `GET /income-statement/{TICKER}?period=quarter&limit=8&apikey={KEY}` — revenue, operating income (for operating margin), same quarter prior year.
11. **Cash flow statement (quarterly):** `GET /cash-flow-statement/{TICKER}?period=quarter&limit=8&apikey={KEY}` — operating cash flow, capital expenditure (for FCF and FCF margin).
12. **Key metrics (quarterly):** `GET /key-metrics/{TICKER}?period=quarter&limit=8&apikey={KEY}` — use for operating margin, FCF margin, inventory-related metrics (e.g. days inventory outstanding) when available.
13. **Balance sheet (quarterly):** `GET /balance-sheet-statement/{TICKER}?period=quarter&limit=8&apikey={KEY}` — inventory (for inventory days if not in key-metrics).
14. **Historical price or quote:** Use **quote** for current market cap; for "market cap vs end of last quarter" use prior quarter’s approximate cap if available (e.g. from key-metrics `marketCap` history or estimate from shares outstanding × prior-period price). If FMP does not provide prior-quarter market cap, state current market cap and note "prior quarter end comparison not available" or derive from shares outstanding and a stated prior price if in transcript/profile.

**Presentation materials (PDF/PPTX):** FMP does not return a dedicated "earnings presentation URL" field. Use (a) any link found in press release or earnings API responses that points to a PDF, PPTX, or "investor presentation" page; (b) from **profile**, use `website` (and `companyName`) to suggest the investor relations page — many companies use `https://investors.{domain}`, `{website}/investors`, or `{website}/ir`. In the report, include a **Presentation materials** section with direct links when available, or a clear pointer to the IR page where earnings decks are usually posted.

---

### Step 3: Resolve latest period

**Latest earnings** = the most recent earnings report that has actuals (from the stable `/earnings` response). Use that report's **date** (e.g. 2026-02-25) as the period for the entire report: earnings snapshot, market context, press release filter, and transcript (when available). Do not choose an older quarter just because it has a transcript—always lead with the latest earnings date. If the transcript for that date is not yet in FMP, still write the full report and note in the Q&A and sentiment sections that the transcript for this period is not yet available and will be added when published. State the period clearly in the report header (e.g. "Q4 FY2026 (report date 2026-02-25)").

---

### Step 3b: Compute quarter grade

From the **latest earnings report** (the one with actuals): use `revenueActual`, `revenueEstimated`, `epsActual`, `epsEstimated`. Compute surprise % for each: `surprise_rev = (actual − estimate) / estimate × 100` (similarly for EPS); if estimate is 0, skip that metric. Apply the **Quarter grade (A–F)** scale in Context (A–F rules and edge cases: one metric only, negative EPS, zero estimate). **Output:** one letter grade (A, B, C, D, or F) plus one short sentence justifying it (e.g. "Double beat; revenue +3.0%, EPS +5.2%."). Use this grade and justification in the report Header and Assessment.

---

### Step 3c: Build Highlights block

Using the **latest earnings** period and the data from Step 2 (earnings, quote, analyst-estimates, income statement, cash flow, key-metrics, balance sheet), build a **Highlights** section for the report. Match the period to the latest earnings report (fiscal year and quarter). For each item use actuals when available and compare to analyst estimates or prior periods as specified. Format numbers for readability (e.g. billions with B, margin as %). Include:

| Highlight | Source | Comparison |
|-----------|--------|------------|
| **Revenue** | Earnings: revenueActual, revenueEstimated | % beat vs estimate; **YoY growth %** (vs same quarter prior year from income statement or earnings). |
| **Adjusted EPS** | Earnings: epsActual, epsEstimated | % beat vs estimate. |
| **Adjusted EBITDA** | Key-metrics (e.g. ebitda) or income statement + D&A for the quarter; if only GAAP EBITDA, label as "EBITDA". | Actual vs analyst estimate (from analyst-estimates if available); **margin %** (EBITDA / revenue). |
| **Revenue guidance (next quarter)** | Transcript or press release (company midpoint or range). | Company guidance vs analyst-estimates for next quarter (above / in line / below). If guidance not in transcript/press release, state "Not disclosed in available data." |
| **Operating margin** | Income statement: operatingIncome / revenue for the quarter. | Current quarter %; **up or down from same quarter last year** (state prior year %). |
| **Free cash flow margin** | Cash flow: (operatingCashFlow − capitalExpenditure) / revenue (use revenue from income statement for same period). | Current quarter %; **up or down from same quarter last year** (state prior year %). |
| **Inventory days outstanding** | Key-metrics (e.g. daysInventoryOutstanding) or balance sheet inventory with COGS/revenue for quarterly run rate. | Current quarter (days); **up or down from previous quarter** (state prior quarter days). If not relevant (e.g. no meaningful inventory), omit or state "Not material." |
| **Market capitalization** | Quote: marketCap. | Current value (e.g. $X.XX trillion); **change vs end of last quarter** (prior quarter end market cap if available; otherwise "prior quarter end not in dataset" or approximate from shares × prior price). |

Place this block in the report as section **"Highlights"** (see report structure below). Use a clear, scannable format (e.g. bullets or a compact table) similar to: "**Revenue:** $X.XXB actual vs $X.XXB est. (X.X% beat); YoY +X.X%." and "**Operating margin:** X.X%, up from X.X% same quarter last year."

---

### Step 4: Parse transcript for Q&A and sentiment

From the full transcript text:

- **Identify the Q&A section** — Many transcripts have a clear "Question-and-Answer" or "Q&A" section, with speaker labels (e.g. "Analyst:", "CEO:", "CFO:"). If the format is unstructured, infer analyst questions (e.g. questions about guidance, margins, competition) and management responses that follow.
- **Extract 5–12 notable Q&A exchanges** — For each: briefly state the analyst's topic or question, and management's core answer (1–3 sentences). Do not paste the full transcript; summarize so the reader has visibility on what was asked and how management responded.
- **Sentiment analysis of management's answers** — For the Q&A segment only, assess and report:
  - **Tone:** Confident / Cautious / Defensive / Mixed. Support with a short justification (e.g. "repeated use of 'we're on track'" vs "hedged language on outlook").
  - **Sentiment:** Positive / Neutral / Negative / Mixed across answers. Note which topics drew more positive vs cautious language.
  - **Clarity:** Clear and specific vs vague or evasive. Call out any answers that dodged the question or lacked concrete numbers.
  - **Notable themes:** e.g. margin pressure, competition, supply chain, guidance raise/cut. One or two sentences on what dominated the Q&A.

Include this in the report under **"Q&A visibility"** and **"Sentiment analysis (management answers)"** (see report structure below).

---

### Step 5: Write the report

Output a structured markdown report to **`outputs/earnings-analysis-{TICKER}-{DATE}.md`** (e.g. `outputs/earnings-analysis-COST-2025-02-23.md`). Use today's date in YYYY-MM-DD format. Ensure `outputs/` exists (create if needed).

**Report structure (include all sections):**

1. **Header** — Ticker, company name, report date, "Latest earnings" period (e.g. Q4 FY2024 / Dec 2024), and **Quarter grade** | **{Letter}** — {one-sentence justification}. Example: `| **Quarter grade** | **A** — Double beat; revenue +3.0%, EPS +5.2%. |`

2. **Earnings snapshot** — Table: revenue (actual vs estimate), EPS (actual vs estimate), surprise %, timing (bmo/amc). Source: FMP earnings + earnings-surprises.

3. **Highlights** — At-a-glance metrics for the latest earnings period (same format as Step 3c). Include: **Revenue** (actual vs analyst estimates, % beat, YoY growth); **Adjusted EPS** (actual vs estimates, % beat); **Adjusted EBITDA** (actual vs estimates, % beat, margin %); **Revenue guidance for next quarter** (company midpoint vs analyst estimates, above/in line/below); **Operating margin** (current %, up/down from same quarter last year); **Free cash flow margin** (current %, up/down from same quarter last year); **Inventory days outstanding** (current, vs previous quarter — omit if not relevant); **Market capitalization** (current, change vs end of last quarter). Use bullets or a compact table; keep scannable.

4. **Market context** — Current price, 1-day change, short-term context if available (quote). Optionally VIX. Keep to a short paragraph or table.

5. **Press release summary** — One or two paragraphs: key points from FMP press releases for that ticker/period (headlines, dates, link if in API response). If no symbol-specific endpoint, filter by symbol or date.

6. **Earnings call — prepared remarks highlights** — 3–8 bullets: management's key messages from the opening remarks (guidance, metrics, segment performance, risks). No full transcript.

7. **Q&A visibility** — 5–12 summarized exchanges. For each: **Topic/Question** (analyst focus) and **Management answer** (1–3 sentences). Gives visibility on what analysts asked and how management responded.

7. **Sentiment analysis (management answers)** — Sub-sections:
   - **Tone:** Confident / Cautious / Defensive / Mixed + one-sentence justification.
   - **Sentiment:** Positive / Neutral / Negative / Mixed + which topics were more positive or cautious.
   - **Clarity:** Clear vs vague/evasive; note any dodged questions.
   - **Notable Q&A themes:** 1–2 sentences on what dominated the Q&A (e.g. margins, competition, guidance).

9. **Analyst and expectations** — What was expected (analyst-estimates / calendar), how results compared (can reference snapshot), and any forward commentary from estimates.

10. **Assessment** — Include "Quarter grade: {Letter}." then 2–4 sentence verdict: beat/miss/in line, quality of print (revenue vs EPS), guidance stance, sentiment takeaway, and one line on implications (e.g. "suitable for post-earnings CSP after IV crush" or "avoid short-dated options through next report").

11. **Presentation materials (PDFs / PPTX)** — Include links to earnings presentation materials when available:
    - **Direct links:** If any API response (press releases, earnings, or profile) contains a URL to an earnings presentation, investor deck, or PDF/PPTX file, list it here with a short label (e.g. "Q4 FY24 earnings presentation (PDF)", "Investor deck (PPTX)").
    - **Investor relations page:** From profile `website`, add the company's investor relations URL. If the profile does not include a dedicated IR URL, derive a likely URL (e.g. `https://investors.{companydomain}` or `{website}/investors` or `{website}/ir`) and present it as: "Investor relations (earnings materials): [link]. Look for 'Quarterly Results', 'Earnings Presentation', or 'Investor Presentation' (PDF/PPTX) for this period."
    - If no link can be inferred, state: "Earnings presentation (PDF/PPTX) is typically posted on the company's investor relations page; search '[Company name] investor relations earnings' or check SEC EDGAR for 8-K filings that may link to materials."

12. **Risks / caveats** — Data gaps (e.g. transcript or press release missing), FMP limits. Include: "Quarter grade is based solely on revenue and EPS vs consensus (see command doc for A–F scale). It does not include guidance or call sentiment." Note when Highlights use estimated or GAAP figures (e.g. EBITDA) or when next-quarter guidance or prior-quarter market cap is not available. Cross-reference: "For detailed trade ideas run /options-scan {TICKER}. For upcoming dates run /earnings-calendar {TICKER}."

---

### Step 6: Summarize in chat

After writing the file, give a one-paragraph verbal summary: period, quarter grade (e.g. "quarter grade A"), beat/miss, one-line sentiment takeaway, and report path. Optionally add: "To hear a short summary aloud, run /speak with the assessment sentence."

---

## Context

- **Altamira Capital** is a multi-strategy investment firm. Options thesis: avoid holding through unplanned earnings; post-earnings CSP/IV crush is a defined use case.
- **FMP:** Transcript and earnings data are from FMP stable; quote, profile, surprises, estimates, income statement, cash flow, key-metrics, and balance sheet from FMP v3. Same API key for all. Highlights section uses v3 quarterly statements and key-metrics for margins, FCF, and inventory; company guidance for next quarter comes from the transcript or press release when available.
- **Output path:** Reports go to `outputs/earnings-analysis-{TICKER}-{DATE}.md`. Paths are relative to the workspace root.

### Quarter grade (A–F) — uniform scale

Apply this scale to grade the company's quarterly financial report based **only** on revenue and EPS performance vs consensus estimates (surprise %). Use it for every report so grades are comparable across tickers and quarters.

**Rules (when both revenue and EPS are available):**

- **A — Excellent:** Both revenue and EPS beat; each surprise ≥ +2%. Strong double beat.
- **B — Good:** Both revenue and EPS beat; at least one surprise &lt; +2% but both positive. Or one metric beats by ≥ +2% and the other is in line (within ±1%).
- **C — In line:** Mixed (one beat, one miss) with no large miss; or both in line (each within ±1%). "Meet" quarter.
- **D — Below expectations:** One clear miss (surprise ≤ −2%) and the other not a strong beat; or both slightly negative (surprise &lt; 0% but &gt; −3%).
- **F — Poor:** Both miss (both surprises negative); or any surprise ≤ −3% (material miss).

**Edge cases:**

- **Only one metric available** (e.g. revenue or EPS missing): Grade from the available metric(s) using the same thresholds; if only one metric, use: A ≥ +3%, B ≥ +1%, C within ±1%, D &lt; −1%, F ≤ −3%.
- **Negative EPS:** Use surprise % as reported; "beat" = actual &gt; estimate (e.g. smaller loss than expected).
- **Zero estimate:** If estimate is 0 for a metric, exclude that metric from the grade and grade on the other; if both 0, state "Grade: N/A (no estimates)."

Surprise % formula: `(actual − estimate) / estimate × 100`. The grade is purely quantitative (actual vs estimate); guidance and call sentiment stay in the Assessment text.
