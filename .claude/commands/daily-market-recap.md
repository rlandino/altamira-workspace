# /daily-market-recap - Daily Market Recap + Telegram Delivery

Generate Altamira Capital's daily market recap markdown file and deliver both a short summary and the markdown file to the configured Telegram channel.

## Instructions

Run from the workspace root:

```bash
python3 scripts/daily_market_recap.py --send-telegram
```

By default, the command uses today's New York date and writes:

- `outputs/daily-market-recap-{DATE}.md`

## Required Environment

- `FMP_API_KEY` - Financial Modeling Prep API key for quotes, sector data, earnings calendar, and headlines.
- `TELEGRAM_BOT_TOKEN` - Telegram bot token.
- `TELEGRAM_CHAT_ID` - Telegram chat or channel ID.

If the chat ID is not set locally, pass it explicitly:

```bash
python3 scripts/daily_market_recap.py --send-telegram --telegram-chat-id <CHAT_ID>
```

## Output

The recap includes:

1. Executive summary
2. Major index levels and day changes
3. ETF and VIX snapshot
4. Best/worst sector
5. Hot stock and biggest loser
6. S&P 500 5-day/20-day average, support, resistance, and trend
7. Broad-market headlines
8. Next 7 days of earnings-calendar entries
9. Short commentary and informational disclaimer

After generation, the script sends:

- Plain-text Telegram summary
- Markdown report as a Telegram document attachment

## Notes

- Use `--date YYYY-MM-DD` to regenerate a specific date.
- The script exits with a clear error if required credentials are missing or Telegram delivery fails.
