# Daily Market Recap Telegram Runner

## Status

Planned for immediate implementation.

## Objective

Add and run a `/daily-market-recap` workflow that:

1. Fetches daily market data from FMP.
2. Writes a markdown recap to `outputs/daily-market-recap-{DATE}.md`.
3. Sends a concise summary message to Telegram.
4. Sends the markdown recap file to the same Telegram chat/channel.

## Implementation Notes

- Add `scripts/daily_market_recap.py` as the reusable runner.
- Use environment variables for credentials:
  - `FMP_API_KEY`
  - `TELEGRAM_BOT_TOKEN` or `TELEGRAM_API_TOKEN`
  - `TELEGRAM_CHAT_ID` when available.
- Keep the recap scoped to market data, sector performance, gainers/losers, upcoming earnings, and headline-aware commentary.
- Add `.claude/commands/daily-market-recap.md` and update `CLAUDE.md` so future sessions know the command exists.

## Validation

- Run the script locally for the current date.
- Confirm the markdown file is created.
- Confirm Telegram message and document endpoints return success.
