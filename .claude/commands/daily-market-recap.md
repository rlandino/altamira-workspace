# /daily-market-recap — Daily Market Recap to Telegram

Generate a daily US market recap markdown file and deliver both a short summary and the markdown file to Telegram.

## Instructions

Run from workspace root:

```bash
python3 scripts/daily_market_recap.py
```

### Inputs

- **Date (optional):** `--date YYYY-MM-DD` to backfill or re-run a specific day.
- **Telegram chat override (optional):** `--chat-id <CHAT_ID>` if you need to target a different Telegram destination.
- **Dry run (optional):** `--dry-run` to generate the markdown and print summary without Telegram delivery.

### Environment

- Required:
  - `TELEGRAM_BOT_TOKEN`
- Optional:
  - `TELEGRAM_CHAT_ID` (falls back to workspace default if missing)
  - `FMP_API_KEY` (falls back to workspace default key if missing)

### What this command does

1. Pulls market data from FMP:
   - Indices and ETFs: `^GSPC,^DJI,^IXIC,^VIX,SPY,QQQ`
   - Biggest gainers / losers
   - Sector performance snapshot
   - Earnings calendar (next 7 days)
   - S&P 500 EOD history for 5D/20D and support/resistance
2. Computes:
   - Trend (Bullish/Bearish/Mixed)
   - VIX context (low/normal/elevated)
   - 5D and 20D average positioning
3. Writes:
   - `outputs/daily-market-recap-{DATE}.md`
4. Sends to Telegram:
   - A concise text summary
   - The markdown file as a document

### Expected output

Console output includes:

- Summary line
- Report path
- Telegram delivery status with message/document IDs

### Examples

```bash
# Standard daily run
python3 scripts/daily_market_recap.py

# Re-run for a specific day
python3 scripts/daily_market_recap.py --date 2026-04-21

# Generate without sending to Telegram
python3 scripts/daily_market_recap.py --dry-run
```
