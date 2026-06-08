# /daily-market-recap - Generate and Send Daily Market Recap

Generate a daily market recap markdown report, then send a concise summary and the markdown file to the configured Telegram channel.

## Usage

```bash
python3 scripts/daily_market_recap.py --send-telegram
```

Optional arguments:

- `--date YYYY-MM-DD` - generate a recap for a specific market date.
- `--out-dir outputs` - override the output directory.
- `--telegram-chat-id CHAT_ID` - override `TELEGRAM_CHAT_ID` / `TELEGRAM_CHANNEL_ID`.
- `--telegram-token TOKEN` - override `TELEGRAM_BOT_TOKEN`.
- `--fmp-api-key KEY` - override `FMP_API_KEY`.

## Required Environment

- `FMP_API_KEY` - Financial Modeling Prep API key.
- `TELEGRAM_BOT_TOKEN` - Telegram bot token.
- `TELEGRAM_CHAT_ID` or `TELEGRAM_CHANNEL_ID` - Telegram destination for the summary and markdown document.

## Output

- Markdown report: `outputs/daily-market-recap-{DATE}.md`
- Chart, when plotting succeeds: `outputs/daily-market-recap-chart-{DATE}.png`
- Telegram:
  1. Plain-text summary message.
  2. Markdown report sent as a document attachment.

## Report Contents

The report includes:

1. Executive summary.
2. S&P 500, Nasdaq, Dow, SPY, QQQ, and VIX levels.
3. Hot stock, biggest loser, best sector, and worst sector.
4. S&P 500 5-day / 20-day averages, close-based support/resistance, and trend.
5. Broad-market headlines from FMP.
6. Earnings calendar for the next 7 days.
7. Informational disclaimer.

## Notes

- If chart dependencies are unavailable, the command still writes and sends the markdown report.
- Do not hardcode API keys or bot tokens in this file or the script. Use environment variables or command-line overrides supplied by the runtime.
