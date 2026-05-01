# /daily-market-recap - Daily Market Recap to Telegram

Generate the daily market recap markdown file and send both a concise summary and the markdown file to the Telegram channel.

## Instructions

Run from the workspace root:

```bash
python3 scripts/daily_market_recap.py --send-telegram
```

## Optional arguments

- `--date YYYY-MM-DD` - Generate the recap for a specific date.
- `--out outputs/daily-market-recap-YYYY-MM-DD.md` - Override the markdown output path.
- `--chat-id CHAT_ID` - Override `TELEGRAM_CHAT_ID`.
- `--fmp-api-key KEY` - Override `FMP_API_KEY`.
- `--telegram-bot-token TOKEN` - Override `TELEGRAM_BOT_TOKEN`.

## Required environment

- `FMP_API_KEY` - Financial Modeling Prep API key.
- `TELEGRAM_BOT_TOKEN` - Telegram bot token.
- `TELEGRAM_CHAT_ID` - Telegram channel or chat ID.

## Output

- Writes `outputs/daily-market-recap-{DATE}.md`.
- Sends a short text summary to Telegram.
- Uploads the markdown report file to Telegram.

## Notes

- The report is informational only and includes an investment-advice disclaimer.
- If the environment does not define `TELEGRAM_CHAT_ID`, use the existing Telegram chat ID configured in deployed workflow exports only after confirming it is the intended market channel.
