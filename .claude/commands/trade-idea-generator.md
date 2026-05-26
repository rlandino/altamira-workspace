# /trade-idea-generator — Portfolio and Watchlist Trade Ideas

Generate ranked trade ideas from the current repository portfolio and watchlist, write a report to `outputs/`, and optionally send the summary to Telegram.

## Instructions

You are generating trade ideas for Altamira Capital from the checked-in context files. Follow these steps exactly:

### Step 1: Read repository context

- Portfolio: `context/portfolio-details.md`
- Watchlist: `context/watchlist.md`
- Options positions: the "Options / Short Premium Positions" table in `context/portfolio-details.md`

Use the repository context as the source of truth for holdings, weights, watchlist scores, and open short premium positions.

### Step 2: Run the generator

From the workspace root:

```bash
python3 scripts/trade_idea_generator.py
```

This writes:

```text
outputs/trade-idea-generator-{YYYY-MM-DD}.md
```

The script uses live Yahoo Finance chart data when available and falls back to repository context prices when live quotes are unavailable.

### Step 3: Send to Telegram when requested

If the user asks to send the trade ideas to Telegram, run:

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

Required runtime configuration:

- `TELEGRAM_BOT_TOKEN` in the environment
- `TELEGRAM_CHAT_ID` in the environment, or pass `--telegram-chat-id <CHAT_ID>`

Do not hardcode bot tokens or chat IDs in the script or command file.

### Step 4: Review output

Confirm:

- The report path was printed.
- The Telegram status is `sent (...)` when delivery was requested.
- The top ideas are grounded in portfolio concentration, open option risk, and watchlist scores.

## Output Format

The report includes:

1. Market snapshot
2. Top ranked trade ideas
3. Portfolio concentration context
4. Open options risk check
5. Watchlist leaders
6. Exact Telegram message
7. Data caveats and research-only disclaimer

## Notes

- This command is for research and education only; it is not financial advice.
- Confirm prices, earnings dates, liquidity, and portfolio risk limits before placing any trade.
- Keep generated ideas concise enough for Telegram, with the full detail in the markdown report.
