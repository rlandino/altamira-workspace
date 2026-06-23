# /daily-market-recap - Daily Market Recap to Telegram

Generate an end-of-day market recap, write a markdown report, and send both a concise summary and the markdown file to a Telegram channel.

## Usage

```bash
python3 scripts/daily_market_recap.py
```

Optional arguments:

```bash
python3 scripts/daily_market_recap.py --date YYYY-MM-DD
python3 scripts/daily_market_recap.py --skip-telegram
python3 scripts/daily_market_recap.py --telegram-chat-id <CHAT_ID>
```

## Required Environment

- `FMP_API_KEY` - Financial Modeling Prep API key.
- `TELEGRAM_BOT_TOKEN` - Telegram bot token.
- `TELEGRAM_CHAT_ID` - Telegram destination chat or channel id.
  - The script also accepts `TELEGRAM_MARKET_CHAT_ID` or `TELEGRAM_CHANNEL_ID`.

## Output

- Markdown report: `outputs/daily-market-recap-{DATE}.md`
- Telegram message: concise 1-paragraph market summary
- Telegram document: generated markdown report

## Workflow

1. Resolve the date from `--date` or today's date.
2. Fetch FMP data:
   - Major index quotes: S&P 500, Dow, Nasdaq, VIX
   - Key ETF quotes: SPY, QQQ, DIA, IWM
   - Biggest gainers and losers
   - Sector performance snapshot
   - S&P 500 historical closes for 5-day/20-day averages, support, and resistance
   - Earnings calendar for the next 7 days
   - Broad market headlines
3. Build a markdown recap with:
   - Executive summary
   - Index and ETF tables
   - Volatility context
   - Sector leadership
   - Top movers
   - Technical posture
   - Earnings calendar
   - Headline-derived market drivers
   - Commentary and disclaimer
4. Send the summary with Telegram `sendMessage`.
5. Send the markdown report with Telegram `sendDocument`.

## Notes

- If same-day sector data is unavailable, the script falls back to the most recent available sector snapshot within the prior 7 days.
- Use `--skip-telegram` for local report generation or dry runs.
- Financial recaps are informational only and are not investment advice.
