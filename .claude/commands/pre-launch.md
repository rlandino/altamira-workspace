# /pre-launch — Paper Trading Readiness Check

Run the pre-launch checklist to validate all paper trading prerequisites before go-live.

## Instructions

You are running the paper trading pre-launch readiness check for Altamira Capital. Follow these steps exactly:

### Step 1: Run the pre-launch script

Execute the Python script that validates prerequisites:

```bash
python scripts/pre-launch-check.py
```

The script checks:
- Strategy documents (investment thesis, risk framework, portfolio allocation, paper trading plan, E-Trade guide)
- Required commands (analyze-ticker, options-scan, portfolio-report, paper-trade, client-report, thesis, stockscore)
- FMP_API_KEY and connectivity
- n8n workflow files (Daily Portfolio Snapshot, Trade Entry Logger, etc.)
- Output files and context files

### Step 2: Summarize results

After the script completes:
- **If all checks pass:** Confirm "Ready for paper trading go-live" and list any optional follow-ups (e.g. E-Trade API production keys, n8n activation).
- **If any check fails:** List each failure with the detail from the script; recommend the fix (e.g. create missing file, set env var, deploy workflow). Do not claim readiness until all failures are resolved.

### Step 3: Reference documents

- **Paper trading plan:** `outputs/paper-trading-plan.md` — go-live criteria and action items
- **E-Trade setup:** `outputs/etrade-api-setup-guide.md` — API and OAuth steps
- **Trading infrastructure:** `outputs/trading-infrastructure-setup.md` — full checklist

## Context

- **Target go-live:** Mar 1 (per paper trading plan)
- **Portfolio size:** $100K starting capital for paper trading
- **Risk limits:** 5% max position, 25% sector, 30% options, 15% min cash
