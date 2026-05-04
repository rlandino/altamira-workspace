# /daily-market-recap - Daily Market Recap with Telegram Delivery

Generate the daily Altamira market recap, write a markdown report, and send both
the concise summary and markdown file to Telegram.

## Run

```bash
python3 scripts/daily_market_recap.py --send-telegram
```

Optional arguments:

```bash
python3 scripts/daily_market_recap.py --date YYYY-MM-DD --send-telegram
python3 scripts/daily_market_recap.py --send-telegram --telegram-chat-id CHAT_ID
python3 scripts/daily_market_recap.py --json
```

## Output

- Markdown report: `outputs/daily-market-recap-{DATE}.md`
- Telegram message: short market summary
- Telegram document: the generated markdown report

## Data and credentials

- Market data: FMP (`FMP_API_KEY`, with workspace fallback key)
- Telegram: `TELEGRAM_BOT_TOKEN`
- Chat/channel: `TELEGRAM_CHAT_ID` or `TELEGRAM_CHANNEL_ID`; if unset, the
  script uses the workspace Telegram chat ID from the existing workflow exports.

## Report contents

The recap includes major indices, SPY/QQQ/VIX, best and worst sector, hot stock,
biggest loser, S&P 500 moving averages, support/resistance, broad market
headlines, the next seven days of earnings, commentary, and a disclaimer.
