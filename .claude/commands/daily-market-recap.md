# /daily-market-recap — Daily Market Recap to Telegram

Generate the Altamira daily market recap, write a Markdown report, and optionally send the summary plus Markdown file to Telegram.

## Usage

```bash
python3 scripts/daily_market_recap.py --send-telegram
```

Useful options:

- `--date YYYY-MM-DD` — report date; defaults to today's America/New_York date.
- `--dry-run` — generate the Markdown file and print the summary without Telegram delivery.
- `--telegram-chat-id CHAT_ID` — override `TELEGRAM_CHAT_ID` for this run.

## Required Environment

- `FMP_API_KEY` — Financial Modeling Prep API key.
- `TELEGRAM_BOT_TOKEN` — Telegram bot token.
- `TELEGRAM_CHAT_ID` — Telegram channel or chat id.

## Output

- Markdown report: `outputs/daily-market-recap-{DATE}.md`
- Telegram summary message with the Markdown report attached as a document.

## Report Contents

The recap includes:

1. Major index and ETF levels for S&P 500, Nasdaq, Dow, SPY, QQQ, and VIX.
2. Hot stock, biggest loser, best sector, and worst sector.
3. S&P 500 5-day and 20-day moving-average context, support/resistance, and trend.
4. Market headline drivers from FMP general news.
5. Next 7 days of major earnings.
6. Informational-only disclosure.

## Notes

- Keep API keys and Telegram credentials in environment variables; do not hardcode secrets in this command or script.
- If `TELEGRAM_CHAT_ID` is unavailable in the runtime environment, pass the channel/chat id with `--telegram-chat-id`.
