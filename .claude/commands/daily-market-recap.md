# /daily-market-recap - Daily Market Recap to Telegram

Generate an end-of-day market recap markdown file and optionally send both the
summary and the markdown file to Telegram.

## Instructions

Run from the workspace root:

```bash
python3 scripts/daily_market_recap.py --send-telegram
```

Optional arguments:

- `--date YYYY-MM-DD` - generate the recap for a specific date.
- `--telegram-chat-id CHAT_ID` - override `TELEGRAM_CHAT_ID`.
- `--out-dir outputs` - change the markdown output directory.

## Data and delivery

- Data source: Financial Modeling Prep. The runner uses `FMP_API_KEY` when set,
  otherwise it falls back to the workspace FMP key already used by market
  briefing commands.
- Telegram: the runner uses `TELEGRAM_BOT_TOKEN` or `TELEGRAM_API_TOKEN` and
  `TELEGRAM_CHAT_ID`. If `TELEGRAM_CHAT_ID` is not set, it uses the existing
  workspace Telegram chat default from the deployed CSP scan configuration.
- Output: `outputs/daily-market-recap-{DATE}.md`.

## Report contents

The recap includes:

1. Executive summary.
2. S&P 500, Nasdaq Composite, and Dow Jones levels and day changes.
3. SPY, QQQ, IWM, and VIX snapshot.
4. Best and worst sector.
5. Top gainer and biggest loser.
6. S&P 500 5-day/20-day averages, support, resistance, and trend.
7. Broad-market headlines.
8. Earnings calendar for the next 7 days.
9. Concise market commentary.

## Chat summary

After the command runs, summarize:

- Market direction, S&P 500 trend, and VIX level.
- Best/worst sector and single-stock movers.
- Markdown output path and Telegram delivery status.
