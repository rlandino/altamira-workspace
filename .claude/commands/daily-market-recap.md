# /daily-market-recap — Market Recap to Telegram

Generate a concise daily market recap, write it to markdown, and send both the summary and markdown file to the configured Telegram channel.

## Instructions

Run the recap script from the workspace root:

```bash
python3 scripts/daily_market_recap.py
```

Optional arguments:

- `--date YYYY-MM-DD` — generate the report for a specific date.
- `--no-send` — generate the markdown file without Telegram delivery.
- `--chat-id CHAT_ID` — override the Telegram chat/channel ID for a single run.

## Outputs

- Markdown report: `outputs/daily-market-recap-{DATE}.md`
- Telegram summary message.
- Telegram markdown document upload.

## Configuration

Required for Telegram delivery:

- `TELEGRAM_BOT_TOKEN`
- One of `TELEGRAM_CHAT_ID`, `TELEGRAM_CHANNEL_ID`, or `TELEGRAM_CHANNEL_USERNAME`.

If no chat/channel ID is configured, the script checks existing workflow JSON exports in `outputs/` for a concrete `chatId`, then attempts to discover the most recent chat from Telegram bot updates.

Optional for richer market data:

- `FMP_API_KEY`

Without `FMP_API_KEY`, the script uses no-key Yahoo Finance endpoints for quotes, sector ETF moves, top movers, headlines, and technicals. The earnings calendar requires FMP and will be marked unavailable if no key is configured.

## Report Sections

1. Executive summary
2. Market dashboard: S&P 500, Nasdaq, Dow, SPY, QQQ, VIX
3. Sector rotation using sector ETFs
4. Hot stock and biggest loser
5. S&P 500 technical snapshot
6. Market headlines
7. Earnings calendar
8. Telegram summary
9. Disclosure

## Notes

- Market data may be delayed or incomplete; verify prices before trading.
- This output is informational only and is not investment advice.
