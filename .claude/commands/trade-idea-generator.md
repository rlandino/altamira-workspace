# /trade-idea-generator — Portfolio and Watchlist Trade Ideas

Generate a concise daily trade idea report from the repository's current
portfolio and watchlist context, then optionally send the Telegram summary.

## Usage

```bash
python3 scripts/trade_idea_generator.py --date YYYY-MM-DD
python3 scripts/trade_idea_generator.py --date YYYY-MM-DD --send-telegram --telegram-chat-id CHAT_ID
```

## Inputs

- `context/portfolio-details.md` — current equity and options snapshot.
- `context/watchlist.md` — scored watchlist candidates.
- `TELEGRAM_BOT_TOKEN` — required only when sending to Telegram.
- `TELEGRAM_CHAT_ID` or `--telegram-chat-id` — required only when sending to Telegram.

## Output

- `outputs/trade-idea-generator-{DATE}.md`
- Optional Telegram summary to the configured channel/chat.

## Instructions

1. Run the script from the workspace root.
2. Review the generated markdown for data-quality warnings.
3. If Telegram delivery is requested, send the concise summary only.
4. Treat results as research and pre-trade planning; verify live quotes, options
   chains, earnings dates, liquidity, and account buying power before execution.
