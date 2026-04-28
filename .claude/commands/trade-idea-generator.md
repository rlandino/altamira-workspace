# /trade-idea-generator — Portfolio + Watchlist Trade Ideas

Generate daily trade ideas from the current repository portfolio and watchlist context, write a markdown report, and optionally send the concise summary to Telegram.

## Instructions

Run from the workspace root:

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

The script reads:

- `context/portfolio-details.md`
- `context/watchlist.md`
- `context/options-positions.md`

It writes:

- `outputs/trade-idea-generator-{DATE}.md`

Environment variables:

- `TELEGRAM_BOT_TOKEN` is required for Telegram delivery.
- `TELEGRAM_CHAT_ID` is optional if the existing CSP workflow JSON includes the Telegram `chatId`.
- `FMP_API_KEY` is optional; when present, live quotes and VIX are included. Without it, the report uses repository context only.

## Output

The Telegram summary includes top ranked ideas, portfolio value, VIX/regime when available, and execution guardrails. The markdown report includes portfolio context, top trade ideas, concentration dashboard, watchlist focus, open options notes, and risk guardrails.
