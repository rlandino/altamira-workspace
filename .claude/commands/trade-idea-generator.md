# /trade-idea-generator

## Purpose

Generate a concise daily trade-idea brief from the current repository portfolio and watchlist context, save the full report to `outputs/`, and optionally send a Telegram-ready summary to the configured Telegram channel.

## Usage

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

Optional arguments:

- `--date YYYY-MM-DD` — override the report date.
- `--telegram-chat-id CHAT_ID` — override `TELEGRAM_CHAT_ID`.
- `--telegram-token TOKEN` — override `TELEGRAM_BOT_TOKEN` / `TELEGRAM_TOKEN`.

## Inputs

- `context/portfolio-details.md`
- `context/watchlist.md`
- Environment variables for delivery:
  - `TELEGRAM_BOT_TOKEN` or `TELEGRAM_TOKEN`
  - `TELEGRAM_CHAT_ID`

## Output

- `outputs/trade-idea-generator-{DATE}.md`
- `outputs/trade-idea-generator-telegram-{DATE}.txt`
- Telegram message if both token and chat ID are available.

## Notes

The generator works from checked-in context so it can run even when live market-data credentials are unavailable. Verify live prices, option chains, liquidity, earnings dates, and risk limits before placing trades.
