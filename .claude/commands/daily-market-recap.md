# /daily-market-recap — Daily Market Recap + Telegram Delivery

Generate the daily market recap markdown file and send both a concise text summary and the `.md` report to the configured Telegram channel.

## Instructions

Run from the workspace root:

```bash
python scripts/daily_market_recap.py --send-telegram
```

Optional arguments:

- `--date YYYY-MM-DD` — generate the recap for a specific date.
- `--telegram-chat-id CHAT_ID` — override `TELEGRAM_CHAT_ID` / `TELEGRAM_CHANNEL_ID`.

## Data Sources

- FMP v3 quotes for indices, ETFs, VIX, and the core watchlist.
- FMP stable endpoints for biggest gainers/losers, sector performance, general headlines, and S&P 500 historical prices.
- FMP earnings calendar for the next 7 days.

## Required Environment

- `TELEGRAM_BOT_TOKEN` — Telegram Bot API token.
- `TELEGRAM_CHAT_ID` or `TELEGRAM_CHANNEL_ID` — destination channel/chat id. If unavailable in the environment, pass `--telegram-chat-id`.
- `FMP_API_KEY` is optional; the workspace default is used if unset.

## Output

- Writes `outputs/daily-market-recap-{DATE}.md`.
- Sends a plain-text Telegram summary.
- Sends the markdown report as a Telegram document.

After running, confirm the script prints the report path plus Telegram message/document ids. If Telegram delivery fails, fix the missing environment variable or chat id and rerun the command.
