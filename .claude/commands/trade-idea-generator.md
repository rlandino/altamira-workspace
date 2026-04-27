# /trade-idea-generator — Portfolio + Watchlist Trade Ideas

Generate daily trade ideas from the current repository portfolio and watchlist, then optionally send a concise summary to Telegram.

## Instructions

Run the repository script:

```bash
python3 scripts/trade_idea_generator.py
```

To send the concise summary to Telegram:

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

The script reads:

- `context/portfolio-details.md` for current holdings and short-premium positions
- `context/watchlist.md` for ranked watchlist candidates
- FMP quote and historical data when `FMP_API_KEY` is available, with the local scorer key as a fallback
- `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` or `TELEGRAM_CHANNEL_ID` for Telegram delivery

## Output

- Markdown report: `outputs/trade-idea-generator-{DATE}.md`
- If Telegram chat id is missing, a pending Telegram payload is saved to `outputs/trade-idea-generator-telegram-{DATE}.txt`

## Guardrails

- Treat output as trade-planning research, not investment advice.
- Verify live options chains, bid/ask spreads, open interest, earnings dates, assignment capacity, and risk limits before entering orders.
- Use defined-risk spreads or reduced sizing in elevated/crisis VIX regimes.
