# /compounder-screen — Compounder Quality Screen for Watchlist Candidates

Identify high-quality **compounder** companies suitable for the watchlist and eventual portfolio addition. Compounders exhibit sustainable high ROIC from recurring revenues, high gross margins, low capital intensity, and strong FCF that is reinvested or returned to shareholders. M&A must be ROIC-justified, not merely "strategic" or "accretive" at the expense of overall ROIC.

## Instructions

You are running a **compounder screen** for Altamira Capital. Use FMP data and, where useful, existing slash commands to score each ticker against the **Compounder Checklist** below. Output a structured scorecard and a clear recommendation for watchlist addition.

### Step 1: Resolve ticker(s)

The user provides ticker symbol(s) as argument: **$ARGUMENTS**

- **Single ticker:** e.g. `/compounder-screen COST` — run full screen and write one report.
- **Multiple tickers:** e.g. `/compounder-screen COST MSFT AVGO` — run screen for each and optionally a summary table.
- **No ticker:** Ask: "Please provide one or more tickers to screen, e.g. /compounder-screen COST MSFT."

**Output path:** `outputs/compounder-screen-{TICKER}-{DATE}.md` (use today's date YYYY-MM-DD). For multiple tickers, also write `outputs/compounder-screen-summary-{DATE}.md` with a comparison table.

---

### Step 2: Fetch data from FMP API

Use **FMP API** (key: `FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz`). Base: `https://financialmodelingprep.com/api/v3`. Make calls in parallel where possible.

For each ticker, fetch:

1. **Profile:** `GET /profile/{TICKER}?apikey={KEY}` — name, sector, industry, description (recurring revenue narrative).
2. **Quote:** `GET /quote/{TICKER}?apikey={KEY}` — price, marketCap, sharesOutstanding (for FCF yield, valuations).
3. **Income statement (annual, 5 years):** `GET /income-statement/{TICKER}?period=annual&limit=5&apikey={KEY}` — revenue, grossProfit, operatingIncome, netIncome, ebitda if present.
4. **Balance sheet (annual, 5 years):** `GET /balance-sheet-statement/{TICKER}?period=annual&limit=5&apikey={KEY}` — totalDebt, longTermDebt, netDebt, totalEquity, totalAssets.
5. **Cash flow (annual, 5 years):** `GET /cash-flow-statement/{TICKER}?period=annual&limit=5&apikey={KEY}` — operatingCashFlow, capitalExpenditure, freeCashFlow (or derive: OCF − Capex).
6. **Key metrics (annual, 5 years):** `GET /key-metrics/{TICKER}?period=annual&limit=5&apikey={KEY}` — returnOnInvestedCapital, returnOnCapitalEmployed, freeCashFlowYield, freeCashFlowPerShare, ebitda.
7. **Ratios (annual, 5 years):** `GET /ratios/{TICKER}?period=annual&limit=5&apikey={KEY}` — returnOnEquity, returnOnInvestedCapital, grossProfitMargin, operatingProfitMargin, debtRatio, interestCoverage.
8. **Revenue/product segmentation:** `GET /revenue-product-segmentation/{TICKER}?period=annual&structure=flat&apikey={KEY}` — concentration, recurring vs one-time mix.
9. **Dividends:** `GET /historical/stock_dividend/{TICKER}?apikey={KEY}` — dividend history for growth and consistency.
10. **Stock peers (optional):** `GET /stock_peers?symbol={TICKER}&apikey={KEY}` — competitive context.

**Derived when needed:**

- **FCF yield:** `freeCashFlow / marketCap` (or from key-metrics `freeCashFlowYield`). Target: 4–6%.
- **Debt / EBITDA:** `totalLongTermDebt / EBITDA` (use latest full-year EBITDA from income or key-metrics). Pass: &lt; 3x.
- **ROIC vs cost of capital:** Use ROIC from key-metrics or ratios; assume cost of capital ~8–10% for pass (ROIC consistently above).

---

### Step 3: Compounder Checklist — Score each criterion

Evaluate each ticker against the **seven criteria** below. For each criterion, assign **Pass**, **Fail**, or **Partial** (with one-line reason). Use the thresholds and definitions given.

| # | Criterion | Definition / Threshold | Data to use |
|---|-----------|------------------------|-------------|
| **1** | **Strong franchise durability** | Strong brand recognition and pricing power; durable competitive position. | Moat-style assessment: profile, margins (gross/operating), ROIC stability. Optionally run `/moat {TICKER}` and summarize rating (Wide/Narrow) and sources (Intangible Assets, Switching Costs, etc.). |
| **2** | **High return on capital** | Consistently earns ROIC (or ROCE) **much higher than cost of capital** (e.g. &gt;10–12% and stable/improving over 5y). | key-metrics `returnOnInvestedCapital` or `returnOnCapitalEmployed`; ratios. Show 5y trend; pass if consistently above ~10% and not declining. |
| **3** | **Recurring revenue** | Revenue from many repeat, predictable transactions — not one big contract, blockbuster, or one-time hard good (e.g. car). | Profile description, revenue segmentation (diversified segments, subscription/recurring mix if visible), business model. Qualitative: subscription, SaaS, consumables, repeat purchase, diversified customer base. |
| **4** | **High free cash flow** | FCF yield in **4–6%** range (or clearly above 4% with sustainable drivers). | key-metrics `freeCashFlowYield` or FCF/marketCap from cash flow + quote. Pass if in band; Partial if &gt;6% (still strong) or 3–4% with clear path to 4%+. |
| **5** | **Minimal financial leverage** | Does not rely on debt to grow. **Total long-term debt &lt; 3× last year's EBITDA.** | Balance sheet `longTermDebt` (or totalDebt) / income or key-metrics EBITDA. Pass: ratio &lt; 3; Fail: ≥ 3. |
| **6** | **Low cyclicality** | Highly profitable across the economic cycle; margins and earnings relatively stable over 5y. | 5y series: operating margin, net margin, ROIC; avoid heavy earnings swings or margin collapse in any year. Pass: stable or improving; Fail: sharp downturns in recession-like periods without recovery. |
| **7** | **Returns capital** | Pays **growing dividends** and/or **buybacks**; preferably both. | Dividend history (growth, consistency); key-metrics or computed buyback yield (shares repurchased / market cap). Pass: meaningful and growing; Partial: one of div/buyback; Fail: neither or declining. |

**Cost of capital:** Use 8–10% as reference; ROIC should be "much higher" (e.g. &gt;12% consistently) for a strong pass on criterion 2.

---

### Step 4: Build the scorecard and verdict

For each ticker:

1. **Scorecard table:** One row per criterion with **Pass / Partial / Fail** and a short reason.
2. **Overall compounder score:** Count Pass = 2, Partial = 1, Fail = 0. Optionally: **Strong compounder** (e.g. 6–7 Pass), **Compounder** (4–5 Pass, rest Partial), **Marginal** (3 Pass), **Not a compounder** (&lt;3 Pass or critical fails on leverage/recurring revenue).
3. **Verdict:** **Add to watchlist** / **Consider for watchlist** / **Do not add** — with one-line rationale tied to the checklist.

---

### Step 5: Optional deeper analysis (recommended for "Add to watchlist")

For tickers that score as Strong compounder or Compounder, you may:

- Run **`/moat {TICKER}`** and reference moat rating and direction in the report.
- Run **`/stockscore {TICKER}`** and cite composite grade and Quality/Shareholder scores.
- Run **`/company-growth {TICKER}`** and cite growth grade and ROIC/FCF margin trajectory.
- Run **`/buffett-intrinsic-value-calculator {TICKER}`** for margin of safety and owner earnings (optional).

Either run these and paste short summaries into the compounder report, or state "Run /moat, /stockscore, /company-growth for full detail" with links to command names.

---

### Step 6: Write the report

Write markdown to **`outputs/compounder-screen-{TICKER}-{DATE}.md`** (and for multiple tickers, **`outputs/compounder-screen-summary-{DATE}.md`**).

**Single-ticker report structure:**

```markdown
# Compounder Screen — [Company Name] ([TICKER])

**Report date:** YYYY-MM-DD  
**Current price:** $X.XX (FMP)  
**Sector / Industry:** …

---

## Compounder checklist scorecard

| # | Criterion | Result | Reason |
|---|-----------|--------|--------|
| 1 | Strong franchise durability | Pass / Partial / Fail | … |
| 2 | High return on capital (ROIC >> cost of capital) | … | … |
| 3 | Recurring revenue | … | … |
| 4 | High FCF (4–6% yield) | … | … |
| 5 | Minimal leverage (Debt < 3× EBITDA) | … | … |
| 6 | Low cyclicality | … | … |
| 7 | Returns capital (dividends and/or buybacks) | … | … |

**Overall:** [Strong compounder / Compounder / Marginal / Not a compounder]  
**Verdict:** [Add to watchlist / Consider for watchlist / Do not add] — [One-line rationale]

---

## Supporting data

- **ROIC / ROCE:** [5y trend and latest]
- **FCF yield:** [Latest and 3y if useful]
- **Debt / EBITDA:** [Latest]
- **Dividend / buyback:** [Brief summary]
- **Recurring revenue:** [1–2 sentences from profile/segmentation]

---

## Next steps

- If Add/Consider: run `/stockscore {TICKER}`, `/moat {TICKER}`, `/company-growth {TICKER}`; optionally `/buffett-intrinsic-value-calculator {TICKER}`. Update `context/watchlist.md` when adding.
- If Do not add: note why; re-screen after 1–2 quarters if thesis changes.
```

**Summary report (multi-ticker):** Table with columns: Ticker, Company, Pass count, Partial count, Fail count, Overall label, Verdict (Add/Consider/Do not add). Sort by Pass count descending.

---

### Step 7: Summarize in chat

After writing the file(s):

- For each ticker: overall compounder label, verdict (Add/Consider/Do not add), and 1–2 main strengths or gaps.
- File path(s).
- Reminder: "To add to watchlist, update context/watchlist.md and re-run /watchlist-refresh when ready."

---

## Context

- **Altamira Capital** targets compounders for the watchlist and portfolio: sustainable high ROIC, recurring revenues, high gross margins, low capital intensity, strong FCF, disciplined capital allocation (reinvest or return; M&A only if ROIC-justified).
- **FMP API key:** `FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz`
- **Watchlist:** `context/watchlist.md` — add candidates here; use `/watchlist-refresh` to re-score.
- **Investment thesis:** `outputs/altamira-investment-thesis.md` for strategy alignment.

## Compounder checklist (quick reference)

1. **Strong franchise durability** — Brand, pricing power.  
2. **High ROIC/ROCE** — Consistently >> cost of capital.  
3. **Recurring revenue** — Repeat, predictable; not one-off contracts or blockbusters.  
4. **High FCF** — FCF yield 4–6%.  
5. **Minimal leverage** — Total long-term debt < 3× EBITDA.  
6. **Low cyclicality** — Profitable across the cycle.  
7. **Returns capital** — Growing dividends and/or buybacks.
