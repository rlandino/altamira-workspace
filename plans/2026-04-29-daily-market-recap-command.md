# Daily Market Recap Command Plan

## Goal

Add and run a `/daily-market-recap` workflow that generates a concise markdown recap from live FMP market data and sends both a short summary and the markdown report to Telegram.

## Scope

- Add a script in `scripts/` that:
  - Fetches major index, ETF, VIX, sector, mover, earnings, headline, and recent historical data.
  - Computes simple market direction, VIX regime, trend, and support/resistance context.
  - Writes `outputs/daily-market-recap-{DATE}.md`.
  - Optionally sends a Telegram summary and attaches the markdown file using `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` or an explicit chat ID argument.
- Add `.claude/commands/daily-market-recap.md` documenting command usage.
- Update `CLAUDE.md` so future sessions know the command and script exist.
- Commit and push the implementation before validation, then run the workflow for today.

## Validation

- Run the script in dry-run mode or help mode to confirm argument parsing.
- Run the script for the current date with Telegram enabled.
- Confirm the markdown report path exists and Telegram API calls succeed.

## Notes

- Use environment variables for secrets; do not hardcode Telegram bot tokens.
- Use the existing FMP API key pattern already used by briefing scripts, with `FMP_API_KEY` override support.
- Keep output concise and include a financial-information disclaimer.
