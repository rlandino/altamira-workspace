# /daily-market-recap - Telegram Daily Market Recap

Generate a daily market recap markdown file and send both the summary and markdown document to Telegram.

## Usage

```bash
python3 scripts/daily_market_recap.py --send-telegram
```

Optional arguments:

- `--date YYYY-MM-DD` - generate for a specific date; defaults to today in America/New_York.
- `--chat-id CHAT_ID` - override the Telegram destination; defaults to `TELEGRAM_CHAT_ID`, `ALTAMIRA_TELEGRAM_CHAT_ID`, or the legacy workspace Telegram destination.
- `--out-dir outputs` - override the output directory.
- `--fmp-key KEY` - override the FMP API key; defaults to `FMP_API_KEY` or the workspace fallback key.

## What It Produces

- Markdown report: `outputs/daily-market-recap-{DATE}.md`
- Telegram summary message with:
  - S&P 500, Nasdaq, Dow, VIX, and trend
  - Best/worst sector
  - Hot stock and biggest loser
- Telegram markdown document upload of the generated file

## Data Sources

- FMP v3 quotes: `^GSPC`, `^DJI`, `^IXIC`, `^VIX`, `SPY`, `QQQ`
- FMP stable movers, sector snapshot, news, and historical S&P 500 prices
- FMP v3 earnings calendar for the next seven days

## Notes

- Requires `TELEGRAM_BOT_TOKEN` to send to Telegram.
- If one FMP endpoint fails, the script still writes the recap with `N/A` for that section.
- The report includes a market-data disclaimer and is not investment advice.
