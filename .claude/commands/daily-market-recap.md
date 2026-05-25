# /daily-market-recap — Generate and send daily market recap

Generate an end-of-day style market recap for Altamira Capital, write it to markdown, and optionally deliver both the short summary and markdown file to Telegram.

## Instructions

You are generating the daily market recap. Run from the workspace root:

```bash
python3 scripts/daily_market_recap.py --send-telegram
```

If `TELEGRAM_CHAT_ID` is not set in the environment, pass it explicitly:

```bash
python3 scripts/daily_market_recap.py --send-telegram --telegram-chat-id <CHAT_ID>
```

## Inputs

- Optional date override: `--date YYYY-MM-DD`
- Optional output directory: `--out-dir outputs`
- Telegram delivery: `--send-telegram`
- Telegram chat override: `--telegram-chat-id <CHAT_ID>`

## Data Sources

- FMP v3: index/ETF quotes and earnings calendar
- FMP stable: sector performance, biggest gainers/losers, general market headlines, historical EOD prices
- Telegram Bot API: sends the short summary and attaches the markdown report

Environment variables:

- `FMP_API_KEY` for market data when available
- `TELEGRAM_BOT_TOKEN` or `TELEGRAM_API_TOKEN` for Telegram
- `TELEGRAM_CHAT_ID` unless `--telegram-chat-id` is supplied

## Output

- Markdown report: `outputs/daily-market-recap-{DATE}.md`
- Telegram summary message
- Telegram markdown document attachment

## Recap Contents

The report includes:

1. Executive summary
2. Market dashboard for S&P 500, Nasdaq, Dow, SPY, QQQ, DIA, IWM, and VIX
3. Sector leadership and laggards
4. Biggest gainer and loser
5. Market-driver headlines
6. S&P 500 technical snapshot with 5-day and 20-day averages, support, resistance, and trend
7. Upcoming earnings watch
8. Options and risk context with a financial disclaimer

## Example

```bash
python3 scripts/daily_market_recap.py --date 2026-05-25 --send-telegram --telegram-chat-id 123456789
```
