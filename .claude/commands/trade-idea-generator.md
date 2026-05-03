# /trade-idea-generator - Portfolio and Watchlist Trade Ideas

Generate actionable trade ideas from the current repository portfolio and watchlist context, then optionally send the concise summary to Telegram.

## Instructions

Run the local generator from the workspace root:

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

The script reads:

- `context/portfolio-details.md` for current holdings and open short-premium positions
- `context/watchlist.md` for scored watchlist candidates

It writes:

- `outputs/trade-idea-generator-{DATE}.md`
- `outputs/trade-idea-generator-telegram-{DATE}.txt`

If `TELEGRAM_BOT_TOKEN` is available, `--send-telegram` posts the concise summary to Telegram. The chat id defaults to `TELEGRAM_CHAT_ID` when set, otherwise the configured Altamira Telegram chat id used by the CSP scan workflow.

## Guardrails

- Treat output as educational trade planning, not financial advice.
- Verify live options chain liquidity, bid/ask spreads, open interest, and earnings dates before order entry.
- Keep position sizing within the Altamira risk framework: max 5% per position and max 30% total options allocation.
