# /daily-market-recap — Generate and Telegram Daily Market Recap

Generate a daily market recap markdown file and send both a short summary and the markdown file to Telegram.

## Usage

```bash
python3 scripts/daily_market_recap.py
```

Optional arguments:

- `--date YYYY-MM-DD` — override the report date.
- `--chat-id CHAT_ID` — override the Telegram chat/channel destination.
- `--dry-run` — generate the markdown file and print the summary without sending Telegram messages.

## Data Sources

- FMP v3 quotes for S&P 500, Dow Jones, Nasdaq Composite, VIX, SPY, and QQQ.
- FMP stable endpoints for biggest gainers, biggest losers, sector performance, and historical S&P 500 prices.
- FMP earnings calendar for upcoming earnings over the next seven days.

## Output

- Markdown report: `outputs/daily-market-recap-YYYY-MM-DD.md`
- Telegram summary message.
- Telegram markdown document attachment.

## Required Environment

- `TELEGRAM_BOT_TOKEN` for Telegram delivery.
- `TELEGRAM_CHAT_ID` is optional if the workspace fallback channel ID is valid; pass `--chat-id` to override.
- `FMP_API_KEY` is optional; if absent, the workspace FMP key from the existing briefing command is used.

## Runbook

1. Run a dry run first when changing the command:
   ```bash
   python3 scripts/daily_market_recap.py --dry-run
   ```
2. Run live delivery:
   ```bash
   python3 scripts/daily_market_recap.py
   ```
3. Confirm the terminal prints `Telegram delivery complete`.

## Notes

- The recap is informational only and includes a disclaimer in the markdown file.
- If the sector snapshot is unavailable for the report date, the script checks recent prior dates before returning `N/A`.
