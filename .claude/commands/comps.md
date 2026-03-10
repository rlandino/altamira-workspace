# /comps — Comparable Company Analysis

Produce a peer comparison (multiples and implied price) for a ticker without a full thesis.

## Instructions

You are running comparable company analysis for Altamira Capital. Follow these steps exactly:

### Step 1: Identify ticker

The user will provide a ticker symbol as argument: $ARGUMENTS

If no ticker is provided, ask for one.

### Step 2: Fetch peer list and data

**FMP API (key: `FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz`):**

1. **Peers:** `GET /stock_peers?symbol={TICKER}` — returns list of peer tickers.
2. **Subject company:** Profile + key metrics (latest year) for the ticker: `/profile/{TICKER}`, `/key-metrics/{TICKER}?period=annual&limit=1`, `/ratios/{TICKER}?period=annual&limit=1`, `/quote/{TICKER}`.
3. **Peers (top 5):** For each of the first 5 peers, fetch `/profile/{PEER}`, `/key-metrics/{PEER}?period=annual&limit=1`, `/quote/{PEER}` (or ratios).

Extract for subject and each peer: P/E, P/B, P/S, EV/EBITDA, Revenue Growth (YoY), Operating Margin, ROE, FCF yield if available.

### Step 3: Build comparison table

| Metric | TICKER | Peer1 | Peer2 | Peer3 | Peer4 | Peer5 | Median | Subject vs Median |
|--------|--------|-------|-------|-------|-------|-------|--------|-------------------|
| P/E | ... | ... | ... | ... | ... | ... | ... | Premium/Discount % |
| EV/EBITDA | ... | ... | ... | ... | ... | ... | ... | ... |
| Revenue Growth | ... | ... | ... | ... | ... | ... | ... | ... |
| Operating Margin | ... | ... | ... | ... | ... | ... | ... | ... |
| ROE | ... | ... | ... | ... | ... | ... | ... | ... |

### Step 4: Implied price from peers

- Apply peer median P/E to subject's EPS (or NTM estimate): Implied price = EPS × median P/E.
- Optionally apply median EV/EBITDA to subject's EBITDA: Implied EV, then derive equity and per-share price.
- State: "Implied price from P/E (median): $X" and "Current price: $Y" (from quote).

### Step 5: One-paragraph summary

State whether the ticker trades at a premium or discount to peers on key multiples and what the comp-implied price suggests (overvalued / in line / undervalued).

## Context

- **Investment thesis:** `outputs/altamira-investment-thesis.md`
- **Full thesis (DCF + comps):** Use `/thesis {TICKER}` for full report.
