# /copycat-13f — Copycat Portfolio from 13F Filers

Build a target portfolio that mirrors one or more 13F filers and summarize weights.

## Instructions

You are building a 13F copycat portfolio for Altamira Capital. Follow these steps exactly:

### Step 1: Get filer CIKs

The user may provide arguments: $ARGUMENTS

Required: One or more CIKs comma-separated. Optional: --weight value or equal, --consensus-min N. Resolve names to CIKs via query-13f.py --list or context/13f-filers.txt.

### Step 2: Run the copycat script

Run: python scripts/copycat-13f.py --ciks CIK1,CIK2 --out outputs/copycat-LABEL-DATE.json. Add --weight value|equal and --consensus-min N if requested.

### Step 3: Summarize output

List top 15-20 holdings by weight (ticker, weight percent). State total holdings and weighting. Parse JSON and present as table.

### Step 4: Optional

Output can feed 13f-backtest.py. Compare copycat tickers to current portfolio for overlap.

## Context

Ingest 13F first: scripts/ingest-13f.py --cik CIK or --cik-list context/13f-filers.txt.
