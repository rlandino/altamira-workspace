# /daily-market-recap — Daily Market Recap to Telegram

Generate a daily market recap, write a markdown file, and optionally send both the text summary and markdown document to Telegram.

## Instructions

Run from the workspace root:

```bash
python3 scripts/daily_market_recap.py --send-telegram
```

Optional arguments:

- `--date YYYY-MM-DD` — generate for a specific date.
- `--telegram-chat-id CHAT_ID` — override `TELEGRAM_CHAT_ID`.
- `--out-dir outputs` — override the output directory.

## Credentials

The runner uses environment variables:

- `FMP_API_KEY` — required for Financial Modeling Prep data.
- `TELEGRAM_BOT_TOKEN` or `TELEGRAM_API_TOKEN` — required when `--send-telegram` is used.
- `TELEGRAM_CHAT_ID` — required when `--send-telegram` is used unless `--telegram-chat-id` is provided.

## Output

- Markdown recap: `outputs/daily-market-recap-{DATE}.md`
- Telegram summary message
- Telegram markdown document attachment

## Recap contents

- Major indices and ETFs: S&P 500, Nasdaq, Dow, SPY, QQQ.
- VIX level and regime label.
- Best/worst sector.
- Top gainer and top loser.
- S&P 500 5-day and 20-day moving average context, support, resistance, and trend.
- Upcoming earnings.
- Market headlines and concise commentary.

The report includes the standard informational-only disclaimer.
