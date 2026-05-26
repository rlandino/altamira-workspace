# /daily-market-recap - Generate and Send Daily Market Recap

Generate a daily market recap, write a markdown report, and send both a short summary and the markdown file to the configured Telegram channel.

## Instructions

Run the recap script from the workspace root:

```bash
python3 scripts/daily_market_recap.py --send-telegram
```

Optional arguments:

- `--date YYYY-MM-DD` - generate the recap for a specific date.
- `--out-dir outputs` - override the output directory.
- `--fmp-api-key KEY` - use when `FMP_API_KEY` or `FINANCIALMODELINGPREP_API_KEY` is not set.
- `--telegram-bot-token TOKEN` - use when `TELEGRAM_BOT_TOKEN` or `TELEGRAM_TOKEN` is not set.
- `--telegram-chat-id CHAT_ID` - use when `TELEGRAM_CHAT_ID` or `TELEGRAM_CHANNEL_ID` is not set.

## Required Environment

- `FMP_API_KEY` or `FINANCIALMODELINGPREP_API_KEY`
- `TELEGRAM_BOT_TOKEN` or `TELEGRAM_TOKEN`
- `TELEGRAM_CHAT_ID` or `TELEGRAM_CHANNEL_ID`

## Output

- `outputs/daily-market-recap-{DATE}.md`
- `outputs/daily-market-recap-summary-{DATE}.txt`
- Telegram message with the summary
- Telegram document upload with the markdown report

## Report Contents

The markdown report includes:

1. Executive summary
2. Major indices
3. SPY, QQQ, and VIX
4. Hot stock, biggest loser, best sector, and worst sector
5. S&P 500 5-day/20-day average, support, resistance, and trend
6. Current market headlines
7. Next 7 days of earnings
8. Short market commentary

After running, summarize:

- Main S&P 500 move, trend, and VIX context
- Best/worst sector and hot stock/biggest loser
- Report path and Telegram delivery status
