# /daily-market-recap - End-of-Day Telegram Recap

Generate an end-of-day market recap, write a markdown report, and send both a short summary and the markdown file to Telegram.

## Instructions

Run from the workspace root:

```bash
python3 scripts/daily_market_recap.py --send-telegram
```

Optional arguments:

- `--date YYYY-MM-DD` - generate the recap for a specific date.
- `--chat-id CHAT_ID` - override the Telegram target. Defaults to `TELEGRAM_CHAT_ID`, then the workspace's existing Telegram fallback chat ID.

## Outputs

- `outputs/daily-market-recap-{DATE}.md`
- `outputs/daily-market-recap-{DATE}.summary.json`
- Telegram message with the executive summary
- Telegram document upload containing the markdown recap

## Data Sources

- FMP quotes for S&P 500, Dow, Nasdaq, VIX, SPY, and QQQ
- FMP biggest gainers and losers
- FMP sector performance snapshot
- FMP S&P 500 historical EOD data for support, resistance, and moving averages
- FMP earnings calendar and broad-market headlines

## Environment

- `FMP_API_KEY` optional; falls back to the workspace FMP key used by other market commands.
- `TELEGRAM_BOT_TOKEN` required for Telegram delivery.
- `TELEGRAM_CHAT_ID` optional if using the workspace fallback target.
