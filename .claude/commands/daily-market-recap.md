# /daily-market-recap - Daily Market Recap with Telegram Delivery

Generate a daily market recap markdown file and send both a short summary and the markdown document to the Telegram channel.

## Instructions

Run from the workspace root:

```bash
python3 scripts/daily_market_recap.py --send-telegram
```

Use today's UTC date by default. To override:

```bash
python3 scripts/daily_market_recap.py --date YYYY-MM-DD --send-telegram
```

## Required configuration

- `TELEGRAM_BOT_TOKEN` - Telegram bot token.
- `TELEGRAM_CHAT_ID` - Telegram channel/chat ID. If this is not set, pass `--chat-id`.
- `FMP_API_KEY` - optional; if absent, the script uses the workspace FMP key documented in existing market commands.

## Output

The command writes:

- `outputs/daily-market-recap-{DATE}.md`
- `outputs/daily-market-recap-summary-{DATE}.txt`

The Telegram delivery sends:

1. A concise plain-text market summary.
2. The markdown recap file as a Telegram document.

## Recap contents

- Executive summary
- Index levels and day changes
- S&P 500 trend, 5-day and 20-day averages, support and resistance
- Sector rotation
- Top gainers and losers
- Market drivers from FMP headlines
- Upcoming earnings calendar
- Trading desk notes
- Informational disclaimer

## Failure handling

If Telegram delivery fails, keep the generated markdown and summary files in `outputs/`, surface the API error, and retry after confirming `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
