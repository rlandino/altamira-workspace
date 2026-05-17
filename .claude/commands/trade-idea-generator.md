# /trade-idea-generator

Generate a concise trade-idea digest from the current repository portfolio and watchlist context, write it to `outputs/`, and optionally send it to Telegram.

## Instructions

Run from the workspace root:

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

## Inputs

- `context/portfolio-details.md` — current holdings, weights, market values, and short-premium rows
- `context/watchlist.md` — scored watchlist candidates
- `context/options-positions.md` — short-premium rows used for expiration checks
- `TELEGRAM_BOT_TOKEN` — required for Telegram delivery
- `TELEGRAM_CHAT_ID` — optional; if missing, the script falls back to the existing channel ID in `outputs/csp-daily-scan-fixed.json`

## Outputs

- `outputs/trade-idea-generator-{DATE}.md` — full markdown report
- `outputs/trade-idea-generator-telegram-{DATE}.txt` — Telegram-ready digest
- `outputs/trade-idea-generator-telegram-status-{DATE}.json` — Telegram API response when `--send-telegram` is used

## Notes

- The script skips expired options and flags stale rows before recommending new short-premium activity.
- Ideas are screens and portfolio-management prompts, not financial advice or execution instructions.
