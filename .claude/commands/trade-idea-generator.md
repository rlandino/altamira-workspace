# /trade-idea-generator - Portfolio and Watchlist Trade Ideas

Generate a concise trade-idea memo from the current repository portfolio and watchlist, then optionally send the concise alert to Telegram.

## Instructions

You are generating actionable, risk-aware trade ideas for Altamira Capital using the current workspace context.

### Step 1: Read repository source data

Use:

- `context/portfolio-details.md` for current holdings, weights, market values, and options rows.
- `context/watchlist.md` for watchlist scores, grades, and candidate status.

### Step 2: Run the generator

Run:

```bash
python3 scripts/trade_idea_generator.py
```

The script writes:

```text
outputs/trade-idea-generator-{DATE}.md
```

### Step 3: Send to Telegram when requested

If the user asks to send the output to Telegram, run:

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

Required environment variables:

- `TELEGRAM_BOT_TOKEN` or `TELEGRAM_TOKEN`
- `TELEGRAM_CHAT_ID`

If `TELEGRAM_CHAT_ID` is not exported but the target channel ID is known from the deployed workflow context, pass it with `--telegram-chat-id`.

### Step 4: Summarize

After execution, report:

- Output file path.
- Top add idea.
- Risk-control idea.
- Telegram send status, including the Telegram `message_id` if available.

## Guardrails

- Treat the output as informational only, not financial advice.
- Do not recommend trades from expired options context; flag stale rows and ask for a refresh before opening or rolling options.
- Respect portfolio risk rules: position concentration, sector concentration, cash reserve, near-term earnings, and options risk limits.
