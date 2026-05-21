# /daily-market-recap — Daily Market Recap + Telegram Delivery

Generate a daily Altamira Capital market recap, write it to markdown, and send both a short summary and the markdown file to Telegram.

## Instructions

Run from the workspace root:

```bash
python3 scripts/daily_market_recap.py
```

Optional arguments:

```bash
python3 scripts/daily_market_recap.py --date YYYY-MM-DD
python3 scripts/daily_market_recap.py --chat-id TELEGRAM_CHAT_ID
python3 scripts/daily_market_recap.py --no-telegram
```

## Environment

- `FMP_API_KEY` is optional; the workspace fallback key is used when unset.
- `TELEGRAM_BOT_TOKEN` is required for delivery.
- `TELEGRAM_CHAT_ID`, `TELEGRAM_CHANNEL_ID`, or `TELEGRAM_DEFAULT_CHAT_ID` can override the workspace Telegram destination.

## Output

- Markdown report: `outputs/daily-market-recap-{DATE}.md`
- Voice/summary script: `outputs/daily-market-recap-summary-{DATE}.txt`
- Chart, when generated: `outputs/briefing-chart-{DATE}.png`

## Report Contents

The recap includes:

1. Executive summary
2. Major indices and ETFs
3. VIX risk context
4. Best/worst sector snapshot
5. S&P 500 trend vs 5D/20D averages
6. Support and resistance
7. Watchlist movers
8. Upcoming earnings
9. Broad-market headlines
10. Concise market commentary

Include the standard educational disclaimer in generated reports. Do not present the recap as investment advice.
