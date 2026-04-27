# /daily-market-recap — Telegram Market Recap

Generate a daily market recap markdown report and send both a short summary and the markdown file to the configured Telegram channel.

## Instructions

Run from the workspace root:

```bash
python3 scripts/daily_market_recap.py --send-telegram
```

Optional arguments:

- `--date YYYY-MM-DD` — generate the recap for a specific date.
- `--output-dir outputs` — override the output directory.
- `--telegram-chat-id CHAT_ID` — override `TELEGRAM_CHAT_ID` or `ALTAMIRA_TELEGRAM_CHAT_ID`.

## Data sources

- FMP quote data for S&P 500, Dow, Nasdaq, VIX, SPY, and QQQ.
- FMP sector snapshot with sector ETF fallback.
- FMP biggest gainers/losers.
- FMP general headlines for market-driver context.
- FMP earnings calendar for the next five calendar days.
- FMP S&P 500 historical prices for moving averages, support/resistance, and trend.

## Output

- Markdown report: `outputs/daily-market-recap-{DATE}.md`
- Telegram message: short text summary.
- Telegram document: the markdown report.

## Required environment

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID` or `ALTAMIRA_TELEGRAM_CHAT_ID` unless `--telegram-chat-id` is provided.
- `FMP_API_KEY` is optional; the workspace fallback key is used when unset.
