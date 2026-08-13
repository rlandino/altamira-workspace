# /daily-market-recap - Daily Market Recap with Telegram Delivery

Generate Altamira Capital's daily market recap, write a Markdown report, and
send both the short summary and Markdown file to the configured Telegram
channel.

## Usage

```bash
python3 scripts/daily_market_recap.py --send-telegram
```

Optional arguments:

- `--date YYYY-MM-DD` - report date; defaults to the current New York date.
- `--telegram-chat-id CHAT_ID` - override `TELEGRAM_CHAT_ID`.
- `--telegram-token TOKEN` - override `TELEGRAM_BOT_TOKEN` or `TELEGRAM_API_TOKEN`.
- `--output-dir outputs` - destination directory for the Markdown report.

## Data Sources

- FMP v3 quotes for major indices, VIX, SPY, QQQ, and sector ETF fallback.
- FMP stable endpoints for biggest gainers, biggest losers, sector snapshot, and
  general market headlines.
- FMP earnings calendar for the next seven days.

## Output

- Markdown report: `outputs/daily-market-recap-{DATE}.md`
- Telegram summary message
- Telegram Markdown document upload

## Environment

- `FMP_API_KEY` is preferred for market data. If unset, the workspace's existing
  FMP fallback key is used for continuity with other market commands.
- `TELEGRAM_BOT_TOKEN` or `TELEGRAM_API_TOKEN` is required for delivery.
- `TELEGRAM_CHAT_ID` is required unless `--telegram-chat-id` is passed.

## Notes

- The report is informational market commentary only and includes a disclaimer.
- If the FMP sector snapshot is unavailable or stale, the script falls back to
  sector ETF proxies (XLB, XLC, XLY, XLP, XLE, XLF, XLV, XLI, XLRE, XLK, XLU).
- Telegram messages are sent as plain text to avoid Markdown escaping failures.
