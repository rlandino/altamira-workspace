# /daily-market-recap — Daily Market Recap to Telegram

Generate a concise daily market recap, write a markdown report, and send both the text summary and markdown file to the configured Telegram channel.

## Instructions

Run from the workspace root:

```bash
python3 scripts/daily_market_recap.py
```

Optional date override:

```bash
python3 scripts/daily_market_recap.py --date YYYY-MM-DD
```

The script writes `outputs/daily-market-recap-{DATE}.md`.

## Telegram delivery

The script sends:

1. A short Telegram message with index moves, VIX context, trend, sectors, and movers.
2. The markdown recap file via Telegram `sendDocument`.

Required environment:

- `TELEGRAM_BOT_TOKEN`

Chat/channel target resolution order:

1. `--chat-id`
2. `TELEGRAM_CHAT_ID`
3. `TELEGRAM_CHANNEL_ID`
4. `TELEGRAM_CHANNEL_USERNAME`
5. Workspace fallback chat id used by the existing CSP Telegram workflow

For a dry run without Telegram:

```bash
python3 scripts/daily_market_recap.py --no-telegram
```

## Data sources

- FMP v3 quotes for S&P 500, Dow, Nasdaq, VIX, SPY, and QQQ.
- FMP stable biggest gainers/losers, sector snapshot, historical EOD, and broad market headlines.
- FMP earnings calendar for the next 7 days.

## Output format

The markdown report includes:

- Executive summary
- Market dashboard
- Sector leadership
- Movers
- S&P 500 technical snapshot
- Earnings calendar
- Headlines watched
- Data warnings
- Informational disclaimer
