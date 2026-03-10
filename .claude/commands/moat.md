# /moat — Economic Moat Analysis (Morningstar-style)

Run a Morningstar-style economic moat analysis for a given ticker: assess moat rating (None/Narrow/Wide), source(s) of moat (five types), and moat direction (Shrinking/Stable/Widening). Output a structured markdown report to `outputs/`.

## Instructions

You are performing a high-level economic moat analysis for Altamira Capital. Follow these steps exactly:

### Step 1: Identify the ticker

The user will provide a ticker symbol as an argument: $ARGUMENTS

If no ticker is provided, ask for one. Accept any US-listed ticker — the moat analysis can be run for potential additions beyond the core universe (AAPL, AMZN, AVGO, COST, GOOGL, MA, META, MSFT, NVDA, SPY, V).

### Step 2: Fetch data from FMP API

Use the FMP API (key: `FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz`) to pull financial data. Make these API calls in parallel where possible:

```
Base URL: https://financialmodelingprep.com/api/v3

1. Company Profile:
   /profile/{TICKER}?apikey={KEY}

2. Income Statement (5 years annual):
   /income-statement/{TICKER}?period=annual&limit=5&apikey={KEY}

3. Balance Sheet (5 years):
   /balance-sheet-statement/{TICKER}?period=annual&limit=5&apikey={KEY}

4. Cash Flow (5 years):
   /cash-flow-statement/{TICKER}?period=annual&limit=5&apikey={KEY}

5. Key Metrics (5 years) — for ROIC, margins, scale:
   /key-metrics/{TICKER}?period=annual&limit=5&apikey={KEY}

6. Financial Ratios (5 years):
   /ratios/{TICKER}?period=annual&limit=5&apikey={KEY}

7. Revenue/Product Segmentation (concentration and mix):
   /revenue-product-segmentation/{TICKER}?period=annual&structure=flat&apikey={KEY}

8. Stock Peers (competitive context):
   /stock_peers?symbol={TICKER}&apikey={KEY}

9. Rating (optional):
   /rating/{TICKER}?apikey={KEY}

10. Real-time Quote:
    /quote/{TICKER}?apikey={KEY}
```

### Step 3: Optional research

Optionally use available research or search (e.g. Perplexity MCP or web search) to gather:

- Morningstar or third-party moat/competitive advantage views for the company
- Recent competitive or regulatory news that could affect moat direction

So that the assessment is grounded in both numbers and qualitative context.

### Step 4: Moat rating

Choose exactly one of **None** | **Narrow** | **Wide** and cite evidence from FMP (and research if used). Use these criteria:

- **Wide:** Strong, durable advantages; typically multiple sources; high and stable returns (e.g. ROIC well above cost of capital) and strong pricing power.
- **Narrow:** Real advantage(s) but vulnerable to competition or disruption; one or two sources; solid but not exceptional returns.
- **None:** No durable advantage; commoditized or highly contested; returns at or below cost of capital.

### Step 5: Sources of moat

For each of the five sources, decide whether it applies and, if so, add 1–2 sentences of evidence. Output as a clear list (bullets or table). Mark which apply and which do not.

1. **Network Effects** — Value increases with more users/participants (e.g. platforms, marketplaces).
2. **Switching Costs** — Customers face meaningful cost or friction to change (e.g. enterprise software, integration lock-in).
3. **Low-Cost Producer** — Structural cost advantage (scale, process, location, asset base).
4. **Intangible Assets** — Brands, patents, regulatory licenses, unique content or IP.
5. **Counter Positioning** — A way of competing that incumbents are slow or unwilling to copy.

Allow multiple sources; note primary vs secondary in the narrative if relevant.

### Step 6: Moat direction

Choose exactly one of **Shrinking** | **Stable** | **Widening** and justify with:

- Trend in margins, ROIC, or market share (from FMP)
- Competitive or regulatory changes (from research or narrative)
- 1–2 sentences of justification

### Step 7: Write report

Output to `outputs/moat-{TICKER}-{DATE}.md` (use today’s date in YYYY-MM-DD format). Include these sections:

**Section 1: Company and context**

- Company name, ticker, sector
- Brief business description (from profile)

**Section 2: Moat rating**

- One of: **None** | **Narrow** | **Wide**
- 2–4 sentence justification with evidence

**Section 3: Sources of moat**

- List which of the five sources apply (Network Effects, Switching Costs, Low-Cost Producer, Intangible Assets, Counter Positioning)
- Short evidence (1–2 sentences) for each that applies; note "Does not apply" for others if helpful

**Section 4: Moat direction**

- One of: **Shrinking** | **Stable** | **Widening**
- 2–4 sentence justification

**Section 5: Supporting data**

- Small tables or bullets: e.g. margins (gross, operating, net), ROIC, revenue concentration, key competitors (from peers). Keep it concise.

**Section 6: Risks to the moat**

- 2–4 bullets (competition, regulation, tech disruption, etc.)

### Step 8: Summarize in chat

After writing the file, give a 2–4 sentence summary in chat:

- Moat rating and main source(s)
- Moat direction
- One-line takeaway
- Report path: `outputs/moat-{TICKER}-{DATE}.md`

## Context

- **Altamira Capital** is a multi-strategy investment firm focused on US large/mega-cap equities and options
- **Core universe:** AAPL, AMZN, AVGO, COST, GOOGL, MA, META, MSFT, NVDA, SPY, V
- **Strategy:** Options premium selling (CSPs, covered calls, spreads) + fundamental equity long
- **Investment thesis:** `outputs/altamira-investment-thesis.md` (for strategy alignment if needed)
