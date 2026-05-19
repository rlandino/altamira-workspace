# /daily-market-recap — Daily Market Recap with Telegram Delivery

Generate a markdown daily market recap and optionally send both a summary and the markdown file to the configured Telegram channel.

## Instructions

Run the recap script from the workspace root:

```bash
python3 scripts/daily_market_recap.py --send-telegram
```

Optional arguments:

- `--date YYYY-MM-DD` — generate the recap for a specific date.
- `--telegram-chat-id CHAT_ID` — override `TELEGRAM_CHAT_ID`.
- `--telegram-bot-token TOKEN` — override `TELEGRAM_BOT_TOKEN`.
- `--out-dir DIR` — write the markdown file somewhere other than `outputs/`.

## Data Sources

- FMP v3 quotes: S&P 500, Dow, Nasdaq, VIX, SPY, QQQ.
- FMP stable: biggest gainers/losers, sector performance, historical S&P 500 EOD, and general market headlines.
- FMP v3 sector ETF quotes as a fallback for sector leadership when the sector snapshot endpoint is unavailable.
- FMP earnings calendar: companies reporting over the next seven days.

## Output

The script writes:

```text
outputs/daily-market-recap-{DATE}.md
```

The markdown includes:

1. Executive summary
2. Market indices
3. ETFs and volatility
4. Breadth and leadership
5. Technical snapshot
6. Market drivers from headlines
7. Earnings calendar
8. Commentary
9. Telegram summary

When `--send-telegram` is provided, the script sends:

1. A concise text summary via Telegram `sendMessage`.
2. The markdown recap via Telegram `sendDocument`.

## Required Environment

- `TELEGRAM_BOT_TOKEN` — Telegram bot token.
- `TELEGRAM_CHAT_ID` — Telegram channel/chat id, unless passed with `--telegram-chat-id`.
- `FMP_API_KEY` — optional; defaults to the existing workspace FMP key if not set.

## Chat Summary

After running, report the S&P 500 move/trend, VIX level, best/worst sector, hot stock/laggard, output path, and Telegram delivery status.
