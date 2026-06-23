# Daily Market Recap Telegram Command

## Objective

Add a `/daily-market-recap` workflow that generates an end-of-day market recap markdown file and sends both a short summary and the markdown file to Telegram.

## Scope

- Add `scripts/daily_market_recap.py`.
- Add `.claude/commands/daily-market-recap.md`.
- Update `CLAUDE.md` so future sessions know the command and script exist.
- Run the command for the current automation trigger date and verify Telegram delivery.

## Implementation Notes

- The script uses `FMP_API_KEY`, `TELEGRAM_BOT_TOKEN`, and a Telegram chat id from `TELEGRAM_CHAT_ID`, `TELEGRAM_MARKET_CHAT_ID`, `TELEGRAM_CHANNEL_ID`, or `--telegram-chat-id`.
- The generated report path is `outputs/daily-market-recap-{DATE}.md`.
- Telegram delivery uses Bot API `sendMessage` for the summary and `sendDocument` for the markdown file.

## Validation

- Compile the Python script with `python3 -m py_compile`.
- Run with `--skip-telegram` for generation validation.
- Run without `--skip-telegram` after credentials and chat id are available.
