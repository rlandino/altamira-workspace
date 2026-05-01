# /trade-idea-generator

Generate actionable trade ideas from the repository's current portfolio and
watchlist context, write a dated report, and optionally send the concise summary
to Telegram.

## Usage

```bash
python scripts/trade_idea_generator.py --send-telegram
```

Optional flags:

- `--no-live-data` — use only repository snapshot prices.
- `--telegram-chat-id CHAT_ID` — override `TELEGRAM_CHAT_ID` / repository config.
- `--max-ideas N` — limit ideas included in the report.

## Inputs

- `context/portfolio-details.md`
- `context/watchlist.md`
- Live FMP quote/VIX/earnings data when `FMP_API_KEY` is present.
- Telegram delivery via `TELEGRAM_BOT_TOKEN` and either `TELEGRAM_CHAT_ID` or
  the configured chat id in `outputs/csp-daily-scan-fixed.json`.

## Output

- `outputs/trade-idea-generator-{DATE}.md`
- Telegram message containing the top ideas, risk note, and report context.

## Risk Note

Generated ideas are research workflow output, not financial advice. Verify live
option chains, earnings dates, liquidity, tax impact, and Altamira risk limits
before entering any trade.
