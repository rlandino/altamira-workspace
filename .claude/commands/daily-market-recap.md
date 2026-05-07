# /daily-market-recap - Generate and Send Daily Market Recap

Generate a daily market recap markdown report and deliver both a short summary and the markdown file to Telegram.

## Instructions

Run the recap script from the workspace root:

```bash
python3 scripts/daily_market_recap.py
```

## Inputs

- Optional date argument from the user in `YYYY-MM-DD`; pass it as `--date YYYY-MM-DD`.
- Optional Telegram destination from the user; pass it as `--telegram-chat-id CHAT_ID_OR_CHANNEL`.

## Required Environment

- `FMP_API_KEY` - Financial Modeling Prep API key.
- `TELEGRAM_BOT_TOKEN` - Telegram bot token.
- One of:
  - `TELEGRAM_CHAT_ID`
  - `TELEGRAM_CHANNEL_ID`
  - `TELEGRAM_CHANNEL`
  - `--telegram-chat-id`

## Output

The script writes:

- `outputs/daily-market-recap-{DATE}.md`
- `outputs/daily-market-recap-summary-{DATE}.txt`

Telegram delivery sends:

1. A plain-text summary message.
2. The generated markdown file as a Telegram document.

## Data Included

- Major indices: S&P 500, Nasdaq Composite, Dow Jones, SPY, QQQ.
- VIX level and volatility regime.
- Biggest gainer and loser.
- Best and worst sector from FMP sector snapshot.
- S&P 500 5-day and 20-day moving averages, support, resistance, and trend.
- General market headlines from FMP as market-driver context.
- Earnings calendar for the next seven days.
- Informational disclaimer.

## Validation

After running, confirm the script output includes `Telegram delivered: yes` and verify the markdown path exists.
