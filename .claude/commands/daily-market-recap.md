# /daily-market-recap

Generate the daily Altamira market recap, write a markdown report, and send both a short text summary and the markdown file to Telegram.

## Usage

```bash
python3 scripts/daily_market_recap.py
```

Optional arguments:

- `--date YYYY-MM-DD` - generate a recap for a specific date.
- `--chat-id CHAT_ID` - override `TELEGRAM_CHAT_ID`.
- `--no-telegram` - write the markdown file without sending Telegram messages.

## Inputs

Environment variables:

- `FMP_API_KEY` - Financial Modeling Prep API key.
- `TELEGRAM_BOT_TOKEN` - Telegram bot token used for delivery.
- `TELEGRAM_CHAT_ID` or `ALTAMIRA_TELEGRAM_CHAT_ID` - Telegram channel/chat id.

## Outputs

- Markdown report: `outputs/daily-market-recap-{DATE}.md`
- Telegram text summary with index, VIX, sector, and mover highlights.
- Telegram document upload containing the markdown report.

## Data included

The script fetches:

1. Major index and ETF quotes: S&P 500, Nasdaq, Dow, VIX, SPY, QQQ.
2. Biggest gainer and loser.
3. Sector performance snapshot.
4. S&P 500 5-day/20-day averages, support, resistance, and trend.
5. Earnings calendar for the next 7 days.
6. Latest broad-market headlines for context.

The report includes an informational-only disclaimer and should not be treated as investment advice.
