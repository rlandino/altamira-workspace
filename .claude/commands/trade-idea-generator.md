# /trade-idea-generator — Portfolio and Watchlist Trade Ideas

Generate daily trade ideas from the existing repository portfolio and watchlist context, write a report, and optionally send a concise Telegram summary.

## Usage

```bash
python3 scripts/trade_idea_generator.py
python3 scripts/trade_idea_generator.py --send-telegram
python3 scripts/trade_idea_generator.py --dry-run-telegram
```

## Inputs

- `context/portfolio-details.md` — current equity positions, weights, and portfolio value.
- `context/watchlist.md` — scored watchlist candidates.
- `context/options-positions.md` — existing short-premium book for risk notes.
- FMP quote API via `FMP_API_KEY` if set, otherwise the workspace default.
- Massive.com options snapshot via `MASSIVE_API_KEY` if set, otherwise the documented `/options-scan` key.
- Telegram delivery via `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`; if `TELEGRAM_CHAT_ID` is not set, the script attempts to infer the existing chat id from the CSP workflow export.

## Output

- Full report: `outputs/trade-idea-generator-{DATE}.md`
- Telegram preview text: `outputs/trade-idea-generator-telegram-{DATE}.txt`
- Optional Telegram message when run with `--send-telegram`

## Method

1. Parse current portfolio positions and watchlist scores from repository context.
2. Pull live SPY/VIX and symbol quotes from FMP when available.
3. Pull 20-60 DTE option snapshots for concentrated holdings and top watchlist names.
4. Rank covered-call ideas for concentrated holdings and CSP ideas for top watchlist candidates.
5. Include existing-options alerts for expired positions or 2x-credit stop review.

## Risk Rules

- Treat output as research only, not a trade ticket.
- Verify live chain data, earnings dates, buying power, and tax impact before orders.
- Respect Altamira risk limits: 5% max single position and 30% max options allocation.
- Run `/options-scan TICKER` for a deeper single-name options analysis before execution.
