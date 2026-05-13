# /daily-market-recap — Telegram Daily Market Recap

Generate an Altamira daily market recap, write a markdown report, and send both a concise summary and the markdown file to the configured Telegram channel.

## Instructions

Run from the workspace root:

```bash
python3 scripts/daily_market_recap.py --send-telegram
```

Optional arguments:

- `--date YYYY-MM-DD` — generate for a specific date; defaults to the current America/New_York date.
- `--telegram-chat-id CHAT_ID` — override Telegram destination. If omitted, the script uses `TELEGRAM_CHAT_ID`, then `TELEGRAM_CHANNEL_ID`, then attempts to resolve the latest bot channel/chat from `getUpdates`.
- `--skip-chart` — skip the optional S&P 500 chart.

## Required environment

- `FMP_API_KEY` — Financial Modeling Prep API key.
- `TELEGRAM_BOT_TOKEN` — Telegram bot token.
- `TELEGRAM_CHAT_ID` or `TELEGRAM_CHANNEL_ID` — recommended for deterministic delivery.

## Output

- Markdown report: `outputs/daily-market-recap-{DATE}.md`
- Optional chart: `outputs/briefing-chart-{DATE}.png`
- Telegram message: concise market summary.
- Telegram document: generated markdown report.

## Data included

- S&P 500, Nasdaq Composite, Dow Jones, SPY, QQQ, and VIX quotes.
- Top gainer and biggest loser.
- Best/worst sector from the latest available FMP sector snapshot.
- S&P 500 5-day/20-day moving averages, support, resistance, and trend.
- Upcoming earnings for the next 7 days.
- Latest general market headlines checked for context.

## Notes

- The recap is informational only and not investment advice.
- If Telegram chat/channel ID is not configured and bot updates are empty, delivery will fail with a clear setup message while still leaving the markdown file on disk.
