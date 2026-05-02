# /trade-idea-generator — Portfolio and Watchlist Trade Ideas

Generate a concise daily trade-idea report from the repository's current
portfolio and watchlist context, then optionally send the summary to Telegram.

## Instructions

Run from the workspace root:

```bash
python scripts/trade_idea_generator.py --send-telegram --chat-id "$TELEGRAM_CHAT_ID"
```

If `TELEGRAM_CHAT_ID` is not set in the environment, use the chat/channel ID
configured in the relevant Telegram workflow.

## Inputs

- `context/portfolio-details.md` — current holdings and short-premium positions.
- `context/watchlist.md` — scored watchlist candidates.
- `TELEGRAM_BOT_TOKEN` — Telegram bot token for delivery.
- `TELEGRAM_CHAT_ID` or `--chat-id` — Telegram channel/chat destination.

## Output

- `outputs/trade-idea-generator-{DATE}.md`
- Optional Telegram message with the top ideas and risk guardrails.

## Guardrails

- Treat outputs as idea generation, not financial advice.
- Verify live quotes, option chains, earnings dates, spreads, and liquidity before
  placing trades.
- Respect the Altamira guardrails: 5% single-position target, 30% options
  allocation cap, close short premium near 50% profit, and manage at 2x credit or
  short-strike breach.
