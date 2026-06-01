# /trade-idea-generator - Portfolio + Watchlist Trade Ideas

Generate a concise trade-idea report from the repository's current portfolio and watchlist context, then optionally send it to Telegram.

## Arguments

- Optional: `telegram` or `send` - send the generated report to Telegram.
- Optional: `--chat-id CHAT_ID` - override `TELEGRAM_CHAT_ID` for the Telegram destination.

## Instructions

Run from the workspace root:

```bash
python3 scripts/trade_idea_generator.py
```

To send the report to Telegram:

```bash
python3 scripts/trade_idea_generator.py --send-telegram --telegram-chat-id "$TELEGRAM_CHAT_ID"
```

If `TELEGRAM_CHAT_ID` is not configured in the environment, use the existing deployed workflow/channel configuration as the source for the chat id and pass it with `--telegram-chat-id`.

## Inputs

- `context/portfolio-details.md` - portfolio value, holdings, weights, and short-premium positions.
- `context/watchlist.md` - scored watchlist candidates and priority tiers.

## Output

- Markdown report: `outputs/trade-idea-generator-{DATE}.md`
- Optional Telegram delivery through `TELEGRAM_BOT_TOKEN`.

## Method

The script prioritizes:

1. Existing option positions that hit profit-taking or stop-loss thresholds.
2. Covered-call candidates on large or concentrated holdings with at least 100 shares.
3. Watchlist entries with B- or better scores for CSP or defined-risk spread monitoring.
4. Risk notes for concentration, underwater holdings, and options allocation.

## Risk Guardrails

- Verify live bid/ask, delta, IV rank, open interest, and earnings dates before execution.
- Keep single-trade max loss within 5% of portfolio value.
- Keep total options allocation within the 30% risk limit.
- Close winners around 50% max profit; close or roll losers at 200% of original credit.

This command produces an automated research note, not financial advice.
