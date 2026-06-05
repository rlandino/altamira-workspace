# Daily Market Recap Telegram Command Plan

## Goal

Add a `/daily-market-recap` command that can be run by cron automation to:

1. Fetch live market recap data.
2. Write a dated markdown report in `outputs/`.
3. Send a concise summary and the markdown report to Telegram.

## Scope

- Add a Python script under `scripts/` for repeatable execution.
- Add a slash command file under `.claude/commands/`.
- Update `CLAUDE.md` so future sessions know the command and script exist.
- Keep credentials in environment variables; do not commit bot tokens.

## Validation

- Run the script for `2026-06-05`.
- Confirm the markdown report and chart are generated.
- Confirm Telegram API returns successful responses for both `sendMessage` and `sendDocument`.
