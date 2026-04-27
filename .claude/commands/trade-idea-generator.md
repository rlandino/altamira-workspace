# /trade-idea-generator

Generate daily trade ideas from the current repository portfolio and watchlist, write a report, and optionally send the compact summary to Telegram.

## Arguments

Optional:

- `send` or `--send-telegram` — send the compact alert to Telegram.
- `--telegram-chat-id CHAT_ID` — override `TELEGRAM_CHAT_ID`.
- `--date YYYY-MM-DD` — run for a specific as-of date.

## Data Sources

- Portfolio holdings and sizing: `context/portfolio-details.md`
- Watchlist candidates and scores: `context/watchlist.md`
- Quotes and earnings calendar: Financial Modeling Prep
- Options snapshots and greeks: Massive.com

## Functionality

Runs `scripts/trade_idea_generator.py` to:

1. Build a universe from current portfolio holdings and watchlist tickers.
2. Pull live quotes, VIX, earnings calendar, and 30-45 DTE put option snapshots.
3. Exclude tickers below the 50-day moving average, with low liquidity, or with earnings inside the trade window.
4. Rank cash-secured put ideas by annualized return, IV proxy, liquidity, trend, and portfolio/watchlist context.
5. Write a full markdown report and a compact Telegram-ready text file.
6. Send to Telegram when `--send-telegram` and a chat id are available.

## Usage

```bash
python3 scripts/trade_idea_generator.py
python3 scripts/trade_idea_generator.py --send-telegram
python3 scripts/trade_idea_generator.py --send-telegram --telegram-chat-id "$TELEGRAM_CHAT_ID"
```

## Output

- `outputs/trade-idea-generator-{DATE}.md`
- `outputs/trade-idea-generator-telegram-{DATE}.txt`

## Notes

Financial output is informational only and is not investment advice. Validate bid/ask liquidity, earnings dates, and portfolio risk limits before placing any trade.
