# /trade-idea-generator — Portfolio and Watchlist Trade Ideas

Generate a concise trade-idea report from the current repository portfolio and watchlist, then optionally send the Telegram summary to the configured channel.

## Instructions

Run the Python script:

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

The script:

1. Parses current holdings and options rows from `context/portfolio-details.md`.
2. Parses watchlist scores from `context/watchlist.md`.
3. Optionally enriches tickers with FMP quotes when `FMP_API_KEY` is set.
4. Writes:
   - `outputs/trade-idea-generator-{DATE}.md`
   - `outputs/trade-idea-generator-telegram-{DATE}.txt`
   - `outputs/trade-idea-generator-telegram-status-{DATE}.json`
5. Sends the Telegram summary when `--send-telegram` is passed and `TELEGRAM_BOT_TOKEN` is available.

## Telegram Configuration

- Preferred: set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in the environment.
- Fallback: if `TELEGRAM_CHAT_ID` is missing, the script reuses the existing numeric chat ID from the CSP daily scan workflow JSON in `outputs/`.

## Notes

- The output is informational only and includes a financial disclaimer.
- The script treats repository context as the source of truth; refresh `context/portfolio-details.md` and `context/watchlist.md` before running when live data matters.
- Expired option rows are excluded from active short-premium decisions and flagged in the report.
