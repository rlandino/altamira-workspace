# /daily-market-recap — Daily Market Recap to Telegram

Generate a concise end-of-day market recap, write a markdown report, and send both the summary and markdown file to Telegram.

## Instructions

Run from the workspace root:

```bash
python scripts/daily_market_recap.py --send-telegram
```

Optional arguments:

- `--date YYYY-MM-DD` — generate the recap for a specific date.
- `--telegram-chat-id CHAT_ID` — override `TELEGRAM_CHAT_ID`.
- `--telegram-bot-token TOKEN` — override `TELEGRAM_BOT_TOKEN`.
- `--json` — print a machine-readable result.

## Data sources

Uses Financial Modeling Prep for:

- Major index, SPY, QQQ, and VIX quotes.
- Biggest gainers and losers.
- Sector performance snapshot.
- S&P 500 recent historical prices for 5D/20D trend, support, and resistance.
- Earnings calendar for the next 7 days.
- General-market headlines.

The script uses `FMP_API_KEY` when set, otherwise the workspace FMP fallback key used by other market commands.

## Output

- Markdown report: `outputs/daily-market-recap-{DATE}.md`
- Telegram summary message.
- Telegram markdown document attachment.

## Required environment for Telegram

- `TELEGRAM_BOT_TOKEN` — bot token.
- `TELEGRAM_CHAT_ID` — channel/chat ID. If omitted, the script falls back to the existing workspace chat ID used by local Telegram workflow testing.

## Notes

The recap is for informational purposes only and includes a disclosure in the report.
