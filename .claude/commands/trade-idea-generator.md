# /trade-idea-generator — Portfolio + Watchlist Trade Ideas

Generate a daily trade idea memo from the repository's current portfolio,
short-premium positions, and watchlist, then optionally send a concise summary
to Telegram.

## Instructions

You are generating actionable trade ideas for Altamira Capital using the
workspace context that is already checked into the repository.

### Step 1: Load repository context

Read:

- `context/portfolio-details.md` for current holdings, weights, prices, and P&L
- `context/options-positions.md` for short-premium positions
- `context/watchlist.md` for candidate additions and scores

### Step 2: Generate the memo

Run:

```bash
python3 scripts/trade_idea_generator.py
```

The script writes:

```text
outputs/trade-idea-generator-{YYYY-MM-DD}.md
```

The memo should include:

1. Current portfolio snapshot and top weights
2. Sector/factor concentration flags
3. Existing short-premium management actions
4. Watchlist entry queue, prioritizing top-scored non-held names
5. No-trade/avoid names
6. Execution checklist and financial disclaimer

### Step 3: Send to Telegram when requested

Set or provide:

- `TELEGRAM_BOT_TOKEN` in the environment
- `TELEGRAM_CHAT_ID` in the environment, or pass `--telegram-chat-id`

Run:

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

If the repository has an existing known chat ID from an n8n workflow and
`TELEGRAM_CHAT_ID` is not set, pass it explicitly:

```bash
python3 scripts/trade_idea_generator.py --send-telegram --telegram-chat-id <chat-id>
```

### Output

After running, summarize:

- Output file path
- Top 2-3 ideas
- Whether Telegram delivery succeeded

## Risk Notes

- This command uses repository snapshots. Confirm live quotes, option chains,
  earnings dates, liquidity, buying power, and risk limits before trading.
- Financial calculations and trade ideas are for planning support only, not
  individualized financial advice.
