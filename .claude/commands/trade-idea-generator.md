# /trade-idea-generator — Portfolio and Watchlist Trade Ideas

Generate options trade ideas from the current repository portfolio and watchlist context, write a markdown report, and optionally send the concise summary to Telegram.

## Instructions

Run the local generator script from the workspace root:

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

Optional arguments:

- `--dry-run` — write the report and print the Telegram preview without sending.
- `--chat-id CHAT_ID` — override `TELEGRAM_CHAT_ID` or the repository fallback chat ID.
- `--include-all-watchlist` — scan every watchlist ticker, including Low Priority/Avoid names.

## Data Sources

- Portfolio holdings: `context/portfolio-details.md`
- Watchlist: `context/watchlist.md`
- FMP quote, VIX, and earnings data
- Massive.com 20-60 DTE options chain snapshots
- Telegram delivery via `TELEGRAM_BOT_TOKEN` and either `TELEGRAM_CHAT_ID` or the existing CSP workflow fallback chat ID

## Output

- Report: `outputs/trade-idea-generator-{YYYY-MM-DD}.md`
- Telegram summary: top 5 ideas with VIX regime, sizing context, contract details, score, and risk notes

## Strategy Rules

- Screen 20-60 DTE liquid options.
- Prefer 0.15-0.35 delta short premium setups.
- Generate cash-secured put ideas for portfolio/watchlist names.
- Generate covered call ideas for existing holdings with at least 100 shares.
- Apply VIX-adjusted sizing from `reference/institutional-signals-spec.md`.
- Flag earnings risk and avoid treating the output as investment advice.
