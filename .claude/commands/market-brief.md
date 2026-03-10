# /market-brief — Short Market Snapshot

Produce a short market snapshot: indices, VIX, sector move, a headline-based explanation of **why** the market is moving (up, down, or flat), and a one- to two-sentence narrative.

## Instructions

You are generating a brief market snapshot for Altamira Capital. Follow these steps exactly:

### Step 1: Fetch market data

Use one of:

**Option A — Market Data API (if running on port 8001):**
GET http://localhost:8001/api/market/indices
GET http://localhost:8001/api/market/quote?symbol=SPY,VIX
(If VIX is not in quote, use a separate source or FMP for VIX.)

**Option B — FMP API directly (key: FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz):**
GET /quote/^GSPC,^DJI,^IXIC,^VIX — for S&P 500, Dow, Nasdaq, VIX
Or quote/SPY,QQQ,DIA,VIXY if indices not available.

Extract: last price, change %, and optionally previous close for each.

### Step 2: Fetch headlines

- Call **FMP stable** (same key as above):  
  `GET https://financialmodelingprep.com/stable/news/general-latest?page=0&limit=20&apikey={KEY}`  
  Returns headlines, snippets, and publication URLs for broad market context (Fed, economy, geopolitics, etc.).
- **Optionally** call FMP stock news for market proxies (e.g. SPY, QQQ) with a small limit (5–10) to reinforce index/market-specific headlines.
- If using **Option A** (local API on port 8001), check whether it exposes a news or headlines endpoint; if yes, prefer it when available and document it here.
- Use the fetched headlines (and snippets) in Step 3 to explain **why** the market is moving.

### Step 3: Present snapshot and "Why the market is moving"

**Snapshot:**

- **Indices:** S&P 500 (^GSPC or SPY), Dow (^DJI or DIA), Nasdaq (^IXIC or QQQ) — level and day change %.
- **VIX:** Level and change; note if above 20 (elevated) or below 15 (low).
- **Sector (optional):** If data available (e.g. sector ETFs or FMP sector performance), state best- and worst-performing sector for the day.

**Why the market is moving:**

- Add a short section **after** the snapshot and **before** the narrative (Step 4). Title it **"Why the market is moving"** (or "Market drivers / Possible causes").
- **Content rules:**
  - Use the **direction** implied by the snapshot (indices and VIX): up, down, or flat.
  - **Base the explanation on the fetched headlines (and snippets)** where possible: cite or paraphrase specific headlines when linking cause to move (e.g. "Rates narrative after [headline]," "Earnings from [sector]," "Data showing [X]").
  - **Dig deeper** into **possible causes**: Fed/rates, earnings or guidance, macro data (jobs, CPI, PMI), geopolitics, sector-specific news. Only mention flows or technicals if mentioned in headlines. Do not invent news; if a cause is inferred, tie it to at least one headline or state that it is a plausible dynamic.
  - Keep to **2–5 sentences or 3–6 short bullets** so the brief stays short.
- **Fallback:** If no headlines are returned (API failure or empty response), output: "No headlines available; possible drivers could not be inferred." The snapshot and narrative (Step 4) still run.
- **Mixed indices:** If S&P and Nasdaq move in different directions, the "why" section can mention different drivers per segment if headlines support it.

### Step 4: One- to two-sentence narrative

Write a single short paragraph: "Markets [closed higher/lower/mixed]. [VIX context.] [Notable sector or catalyst if obvious from data.]" Do not invent news; stick to price/level facts. This is the summary; the "Why the market is moving" block above is the causal add-on.

### Step 5: Optional

If the user runs Market Commenter v3.1 via n8n, the full daily brief is already generated there. This command is a fallback when that workflow has not run or when a quick snapshot is needed in-session.

## Context

- **Headlines:** The "Why the market is moving" section uses FMP General News (`/stable/news/general-latest`) and optionally FMP stock news for SPY/QQQ. The explanation must be grounded in fetched headlines; do not invent causes without a headline or an explicit caveat (e.g. "plausible dynamic").
- **Market Commenter workflow:** outputs/n8n-workflow references; deployed to n8n. Full daily report may be in Telegram or outputs. This command is a lightweight alternative using live API data.
