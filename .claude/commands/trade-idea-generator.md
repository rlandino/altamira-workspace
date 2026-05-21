# /trade-idea-generator

Generate a portfolio-aware daily trade idea from the repository's current
portfolio and watchlist context, then optionally send it to Telegram.

## Purpose

Use the current holdings in `context/portfolio-details.md` and candidates in
`context/watchlist.md` to produce a concise, risk-aware trade idea. The command
prioritizes concentration/risk controls before new deployments, notes expired
options rows, writes an auditable report, and can send the Telegram-ready
summary to the configured channel.

## Run

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

To correct an existing Telegram post without creating a duplicate:

```bash
python3 scripts/trade_idea_generator.py --send-telegram --edit-message-id MESSAGE_ID
```

## Output

- `outputs/trade-idea-generator-{DATE}.md`
- `outputs/trade-idea-generator-telegram-{DATE}.txt`
- `outputs/trade-idea-generator-status-{DATE}.json`

## Telegram Configuration

The script uses `TELEGRAM_BOT_TOKEN` from the environment. It uses
`TELEGRAM_CHAT_ID` when set, otherwise it falls back to the existing Telegram
chat ID in `outputs/csp-daily-scan-fixed.json`.

## Notes

- Repository context prices can be stale; verify live prices, spreads,
  liquidity, tax impact, and earnings dates before acting.
- The output is an idea-generation aid, not personalized financial advice.
