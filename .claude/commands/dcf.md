# /dcf — DCF Fair Value (Quick)

Produce a quick DCF fair value and sensitivity for a ticker without the full thesis document.

## Instructions

You are running a quick DCF valuation for Altamira Capital. Follow these steps exactly:

### Step 1: Identify ticker

The user will provide a ticker symbol as argument: $ARGUMENTS

If no ticker is provided, ask for one.

### Step 2: Run thesis generator and extract DCF

Run the thesis generator (it computes DCF) and extract only the valuation section:

```bash
python scripts/thesis-generator.py TICKER
```

Read `outputs/thesis-{TICKER}-{DATE}.md` and summarize: Fair value (base case), current price, upside/downside %, and the sensitivity table (WACC vs terminal growth). Omit other sections.

### Step 3: Output

- Fair value (base case): $X.XX
- Current price: $Y.YY
- Upside/Downside: Z%
- Sensitivity table: 3x3 (WACC and terminal g) with implied price per cell
- Key assumptions: Revenue growth Y1/Y2, FCF margin, WACC, terminal g (one line each)

### Step 4: One-sentence verdict

State whether at current price the ticker is overvalued, fairly valued, or undervalued on this DCF, and give the sensitivity range.

## Context

- Full thesis: Use `/thesis {TICKER}` for full document.
- FMP API key: `FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz`
