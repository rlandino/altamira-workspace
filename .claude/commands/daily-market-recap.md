# /daily-market-recap - Generate and Send Daily Market Recap

Generate a dated market recap markdown file and send a concise summary plus the markdown report to Telegram.

## Requirements

Environment variables:

- `FMP_API_KEY` - Financial Modeling Prep API key.
- `TELEGRAM_BOT_TOKEN` - Telegram bot token.
- `TELEGRAM_CHAT_ID` or `DAILY_MARKET_RECAP_CHAT_ID` - Telegram chat/channel ID.

## Usage

Run from the workspace root:

```bash
python scripts/daily_market_recap.py --send-telegram
```

Optional date override:

```bash
python scripts/daily_market_recap.py --date YYYY-MM-DD --send-telegram
```

If the chat ID is not in the environment, pass it explicitly:

```bash
python scripts/daily_market_recap.py --date YYYY-MM-DD --send-telegram --telegram-chat-id CHAT_ID
```

## Output

- Markdown report: `outputs/daily-market-recap-{DATE}.md`
- Chart, when matplotlib and historical data are available: `outputs/daily-market-recap-chart-{DATE}.png`
- Telegram summary via `sendMessage`
- Telegram markdown document via `sendDocument`

## Notes

- The script fetches live FMP quotes for indices, SPY, QQQ, VIX, market movers, earnings, and S&P 500 history.
- Sector leaders use FMP sector snapshot when available and sector ETF proxies as a fallback.
- The report includes a research/education-only disclaimer.
