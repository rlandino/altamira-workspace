# Trade Idea Generator Implementation Plan

## Request

Execute `/trade-idea-generator` for the current repository portfolio and watchlist
and send the output to the Telegram channel.

## Context

The workspace did not contain a `/trade-idea-generator` command or local script.
Relevant existing inputs:

- `context/portfolio-details.md`
- `context/watchlist.md`

Available runtime config:

- `TELEGRAM_BOT_TOKEN` is set.
- No Telegram chat/channel env var was initially visible.

## Implementation

1. Add `scripts/trade_idea_generator.py`.
   - Parse current holdings, short-premium positions, and watchlist scores.
   - Optionally refresh FMP quotes and VIX when `FMP_API_KEY` is set.
   - Generate ranked management, covered-call, hedge, and put-selling ideas.
   - Write `outputs/trade-idea-generator-{DATE}.md`.
   - Send the concise summary to Telegram when a destination is configured.
2. Add `.claude/commands/trade-idea-generator.md`.
3. Update `CLAUDE.md` command and script indexes.
4. Run the generator against current repository context.
5. Verify Telegram delivery or report the missing destination configuration.

## Validation

- Compile/check script syntax.
- Run the generator.
- Verify the output report exists and includes top ideas and disclaimers.
- Commit and push changes to the feature branch.
