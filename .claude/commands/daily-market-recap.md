# /daily-market-recap — Daily Market Recap with Telegram Delivery

Generate Altamira Capital's daily market recap, write a markdown report, and optionally send both the summary and markdown file to Telegram.

## Usage

```bash
python3 scripts/daily_market_recap.py
python3 scripts/daily_market_recap.py --send-telegram
python3 scripts/daily_market_recap.py --date YYYY-MM-DD --send-telegram --telegram-chat-id CHAT_ID
```

## Output

- Markdown report: `outputs/daily-market-recap-{DATE}.md`
- Telegram summary message when `--send-telegram` is provided
- Telegram markdown document attachment when `--send-telegram` is provided

## Data Sources

- FMP v3 quotes for major indices, VIX, SPY, QQQ, and IWM
- FMP stable sector performance snapshot, with sector ETF proxy fallback
- FMP stable biggest gainers / biggest losers
- FMP stable S&P 500 historical EOD data for 5D/20D trend, support, and resistance
- FMP earnings calendar for the next 7 days
- FMP general market news headlines

## Environment

- `FMP_API_KEY` is preferred for market data. If unset, the script reuses the workspace's existing local-development FMP fallback from `scripts/market_data_api.py`.
- `TELEGRAM_BOT_TOKEN` or `TELEGRAM_API_TOKEN` is required for Telegram delivery.
- `TELEGRAM_CHAT_ID` is required unless `--telegram-chat-id` is passed.

## Report Sections

1. Executive summary
2. Major indices
3. ETFs and volatility
4. Sector performance
5. Single-stock movers
6. S&P 500 technical snapshot
7. Earnings calendar
8. Market drivers / headlines
9. Commentary
10. Data notes, if any source falls back or fails

