# Daily Market Recap Telegram Command Plan

## Objective

Add a reusable `/daily-market-recap` command that generates a dated market recap markdown file and sends both a concise summary and the markdown file to the configured Telegram destination.

## Success State

- Running the command produces `outputs/daily-market-recap-YYYY-MM-DD.md`.
- The recap includes index levels, VIX context, best/worst sector, market movers, upcoming earnings, trend, support/resistance, and brief commentary grounded in fetched market data.
- Telegram delivery sends:
  - A short summary message.
  - The generated markdown file as a document.
- The implementation handles missing optional data gracefully and prints actionable errors for missing Telegram configuration.

## Implementation Steps

1. Create `scripts/daily_market_recap.py`.
2. Add `.claude/commands/daily-market-recap.md`.
3. Document the new command and script in `CLAUDE.md`.
4. Commit and push implementation before running tests, per cloud branch workflow.
5. Test with a dry run, then run live Telegram delivery.

## Test Plan

- Run `python3 scripts/daily_market_recap.py --date 2026-06-04 --dry-run` to verify report generation and summary formatting without Telegram side effects.
- Run `python3 scripts/daily_market_recap.py --date 2026-06-04` to send the summary and markdown file to Telegram.
- Confirm the output file exists and inspect relevant markdown content.
