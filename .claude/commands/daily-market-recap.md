# /daily-market-recap — Telegram Market Recap

Generate a daily market recap markdown file and deliver both the short summary and the markdown document to the configured Telegram channel.

## Usage

```bash
python scripts/daily_market_recap.py --send-telegram
```

Optional arguments:

- `--date YYYY-MM-DD` — generate a recap for a specific date.
- `--telegram-chat-id CHAT_ID` — override the default Telegram destination.
- `--out-dir outputs` — override the output directory.

## Inputs

- `FMP_API_KEY` environment variable, or the FMP key documented in `.claude/commands/briefing.md`.
- `TELEGRAM_BOT_TOKEN` environment variable for Telegram delivery.
- `TELEGRAM_CHAT_ID` environment variable, or the existing workflow chat ID fallback from `outputs/csp-daily-scan-fixed.json`.

## Outputs

- `outputs/daily-market-recap-{DATE}.md`
- `outputs/daily-market-recap-{DATE}-telegram.json` when Telegram delivery runs

## Report Contents

The recap includes:

1. Executive summary for Telegram
2. S&P 500, Nasdaq Composite, Dow Jones, SPY, QQQ, and VIX
3. Hot stock and biggest loser from FMP movers
4. Best and worst sector using sector ETF proxies
5. S&P 500 5-day/20-day average, support/resistance, and trend
6. Upcoming earnings for the next 7 days

All outputs include the standard informational-only market disclaimer.
