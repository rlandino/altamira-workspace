# /trade-idea-generator - Portfolio and Watchlist Trade Ideas

Generate a concise trade idea scan from the repository's current portfolio and watchlist context, write the report to `outputs/`, and optionally send the summary to Telegram.

## Usage

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

Optional flags:

- `--output outputs/trade-idea-generator-YYYY-MM-DD.md` - override report path
- `--chat-id CHAT_ID` - override `TELEGRAM_CHAT_ID`

## Inputs

- `context/portfolio-details.md`
- `context/watchlist.md`
- `TELEGRAM_BOT_TOKEN` environment variable for sending
- `TELEGRAM_CHAT_ID` environment variable, or the fixed chat id in `outputs/csp-daily-scan-fixed.json`

## Output

- Markdown report: `outputs/trade-idea-generator-{DATE}.md`
- Telegram summary when `--send-telegram` is passed

## Guardrails

- Treat ideas as research only, not order tickets.
- Verify live prices, options chain liquidity, and earnings dates before entry.
- Keep short-premium sizing within the portfolio risk limits in `outputs/risk-management-framework.md`.
