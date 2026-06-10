# /daily-market-recap - Daily Market Recap to Telegram

Generate the daily market recap markdown report, write a short summary, and deliver both to Telegram when channel credentials are configured.

## Instructions

Run from the workspace root:

```bash
python3 scripts/daily_market_recap.py
```

The script writes:

- `outputs/daily-market-recap-{DATE}.md`
- `outputs/daily-market-recap-summary-{DATE}.txt`

It then sends:

1. A concise text summary via Telegram `sendMessage`
2. The markdown recap file via Telegram `sendDocument`

## Configuration

Required for Telegram delivery:

- `TELEGRAM_BOT_TOKEN` - Telegram bot token
- `TELEGRAM_CHAT_ID` - Telegram channel/chat ID

Optional enrichment:

- `FMP_API_KEY` - enables FMP biggest-gainers, biggest-losers, and earnings-calendar enrichment

Without `FMP_API_KEY`, the command still runs using Yahoo Finance chart data plus a liquid large-cap mover fallback. Without Telegram credentials, the command still writes the recap files but exits non-zero and reports the missing variable(s).

## Options

```bash
python3 scripts/daily_market_recap.py --date 2026-06-10
python3 scripts/daily_market_recap.py --skip-telegram
python3 scripts/daily_market_recap.py --telegram-chat-id "$TELEGRAM_CHAT_ID"
```

## Output

Chat summary should include:

- S&P 500, Nasdaq, Dow day moves
- VIX level and volatility label
- S&P 500 trend classification
- Best/worst sector
- Top/weakest mover
- Report path

## Notes

- The report is informational and includes a non-investment-advice disclaimer.
- Do not hardcode Telegram credentials or API keys in this command; use environment variables.
