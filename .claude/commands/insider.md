# /insider — Insider Transaction Summary

Summarize recent insider buying and selling for a ticker.

## Instructions

You are fetching insider transaction data for Altamira Capital. Follow these steps exactly:

### Step 1: Identify ticker

The user will provide a ticker symbol as argument: $ARGUMENTS

If no ticker is provided, ask for one.

### Step 2: Fetch insider data

Use FMP API (key: FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz):

GET /insider-trading?symbol={TICKER}&limit=20

Parse: transaction date, insider name, title, transaction type (P=purchase, S=sale, etc.), shares, value (if available), and reporting date.

### Step 3: Summarize

- **Net direction:** Count purchases vs sales (by transaction type or description). State "Net buying" or "Net selling" or "Mixed" over the last 6 months (or period covered by the data).
- **Notable C-suite:** List any CEO, CFO, or director transactions with date and size (shares or dollar value).
- **Dollar totals:** If the API provides value, sum purchase value and sale value; state total bought vs total sold in dollars.
- **Table (optional):** Up to 10 most recent transactions: Date | Insider | Title | Type | Shares | Value.

### Step 4: Sentiment read

One sentence: "Insider sentiment reads [Bullish / Neutral / Bearish] — [brief reason]."

## Context

Same data is used in /thesis for Section 10. Use this command for a quick standalone insider check without generating a full thesis.
