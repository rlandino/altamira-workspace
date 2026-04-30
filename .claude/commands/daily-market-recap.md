# /daily-market-recap — Telegram Daily Market Recap

Generate the daily market recap markdown file and send both the short summary and markdown report to the Telegram market channel.

## Instructions

Run the Python workflow from the workspace root:

```bash
python scripts/daily_market_recap.py --send-telegram
```

Optional arguments:

- `--date YYYY-MM-DD` — generate the recap for a specific date.
- `--telegram-chat-id CHAT_ID` — override the default Market Commenter Telegram chat ID. The script also respects `TELEGRAM_CHAT_ID`.
- `--out-dir outputs` — override the report output directory.

## Outputs

- Markdown report: `outputs/daily-market-recap-{DATE}.md`
- Telegram summary message
- Telegram document upload containing the markdown report

## Data sources

- FMP quotes for S&P 500, Nasdaq, Dow, VIX, SPY, and QQQ.
- FMP biggest gainers/losers.
- FMP sector performance snapshot.
- FMP S&P 500 historical EOD data for moving averages, support, and resistance.
- FMP general news headlines and earnings calendar.

## Notes

- Requires `TELEGRAM_BOT_TOKEN` or `TELEGRAM_TOKEN` to send Telegram messages.
- Uses `TELEGRAM_CHAT_ID` when set; otherwise defaults to the documented Market Commenter chat ID from the workspace workflow exports.
- The report includes a financial disclaimer and is for informational and research use only.
