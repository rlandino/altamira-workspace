# /13f-diff — 13F Holdings Diff (Period-over-Period)

Compare a filer's 13F holdings between two periods and summarize new buys, sells, and size changes.

## Instructions

You are running a 13F holdings diff for Altamira Capital. Follow these steps exactly:

### Step 1: Get filer and dates

The user may provide arguments: $ARGUMENTS

- **Required:** CIK (e.g. 1067983 for Berkshire) or filer name that can be resolved to a CIK from ingested data.
- **Optional:** Prior period end date (YYYY-MM-DD) and current period end date (YYYY-MM-DD). If not provided, use the two most recent periods available in `outputs/13f/` for that filer.

To list available filers and periods:
```bash
python scripts/query-13f.py --list
```

### Step 2: Run the holdings diff script

```bash
python scripts/13f-holdings-diff.py --cik CIK --prior YYYY-MM-DD --current YYYY-MM-DD --out outputs/13f-diff-{filer}-{date}.md --json-out outputs/13f-diff-{filer}-{date}.json
```

Use actual CIK and dates. If the script fails (e.g. missing data), run `python scripts/ingest-13f.py --cik CIK` first, then retry the diff.

### Step 3: Summarize the report

- **New buys:** Positions in current period not in prior; show top 5–10 by value if many.
- **Sells:** Positions in prior not in current; list notable exits.
- **Increased:** Positions with meaningful size increase (e.g. top 5 by % or $ change).
- **Decreased:** Positions with meaningful size decrease.

If the script wrote a markdown report, read it and present a concise summary (bullet points). If only JSON, parse and summarize.

### Step 4: Optional context

- Curated filers: `context/13f-filers.txt` (use with ingest `--cik-list`).
- CUSIP to ticker: `reference/cusip-to-ticker.json` for converting CUSIPs to tickers in the summary.

## Context

- **13F data location:** `outputs/13f/` — JSON per filing (e.g. `{cik}_{period_end}.json`)
- **Reference:** `reference/13f-data-pipeline.md`
