# /daily-market-recap - Generate and send daily market recap

Generate a daily market recap markdown report and deliver both a concise summary and the markdown file to the configured Telegram channel.

## Usage

```bash
python3 scripts/daily_market_recap.py
```

Optional arguments:

- `--date YYYY-MM-DD` - generate the recap for a specific date.
- `--chat-id CHAT_ID` - override the Telegram chat/channel id.
- `--no-telegram` - generate the markdown file without sending Telegram messages.

## Outputs

- Markdown report: `outputs/daily-market-recap-{DATE}.md`
- Telegram summary via `sendMessage`
- Markdown file upload via `sendDocument`

## Configuration

- `FMP_API_KEY` - optional; falls back to the workspace FMP key.
- `TELEGRAM_BOT_TOKEN` - required for Telegram delivery.
- `TELEGRAM_CHAT_ID`, `TELEGRAM_CHANNEL_ID`, `MARKET_COMMENTER_TELEGRAM_CHAT_ID`, or `ALTAMIRA_TELEGRAM_CHAT_ID` - optional chat/channel override. If none is set, the script uses the existing Market Commenter chat id from the workflow artifacts.

## Data included

- S&P 500, Nasdaq, Dow, SPY, QQQ, and VIX levels and day changes.
- Biggest gainer, biggest loser, best sector, and worst sector.
- S&P 500 5-day/20-day averages, support, resistance, and trend.
- Broad market headlines from FMP general news.
- Earnings calendar for the next seven days.
