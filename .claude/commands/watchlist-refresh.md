# /watchlist-refresh — Refresh and Score Watchlist

Re-score the watchlist tickers and update the watchlist context file.

## Instructions

You are refreshing the watchlist for Altamira Capital. Follow these steps exactly:

### Step 1: Identify watchlist source

- **Primary:** `context/watchlist.md` — if it exists, extract the list of tickers to score.
- **Fallback:** Use the core universe from strategy: AAPL, MSFT, GOOGL, AMZN, AVGO, COST, V, MA, META, NVDA, SPY (and any others in `context/portfolio-details.md` or `context/current-data.md` as watchlist).

### Step 2: Score all watchlist tickers

Run the stock scorer in portfolio/watchlist mode:

```bash
python scripts/stock-scorer.py --portfolio
```

If the script does not support `--portfolio` for watchlist-only, run:

```bash
python scripts/stock-scorer.py TICKER1 TICKER2 TICKER3 ...
```

for each ticker in the watchlist. Prefer a single invocation that accepts multiple tickers or reads from a file if available.

### Step 3: Consolidate output

- The script writes `outputs/portfolio-scores-{DATE}.md` when scoring multiple tickers (or multiple `outputs/stock-score-{TICKER}-{DATE}.md`).
- Summarize: table of Ticker | Composite Score | Grade | Top strength | Top weakness. Sort by composite score descending.

### Step 4: Update watchlist context (if applicable)

If `context/watchlist.md` exists and is meant to hold scored watchlist state:
- Update it with current date, list of tickers, and for each: composite score, grade, and 1-line note (e.g. "Strong Quality; Weak Growth"). Do not remove the file if it has a custom structure; merge in new scores.
- If the file does not exist, create a simple watchlist section in context or write `context/watchlist.md` with: date, tickers, scores, grades. Mention in summary that the watchlist file was created/updated.

### Step 5: Action items

- Flag tickers with composite score below 50 (review or avoid).
- Flag tickers with composite ≥ 75 that are not yet in portfolio as potential adds (subject to strategy and risk check).

## Context

- **Stock scorer:** `scripts/stock-scorer.py` — uses FMP; outputs to `outputs/`
- **Scoring methodology:** See `/stockscore` command (Quality, Growth, Value, Health, Shareholder)
- **Portfolio holdings:** `context/portfolio-details.md`
