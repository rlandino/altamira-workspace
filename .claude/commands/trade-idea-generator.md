# /trade-idea-generator

Generate daily trade ideas from the repository's current portfolio and watchlist,
write a markdown report, and send the concise summary to Telegram.

## Instructions

You are generating internal Altamira Capital trade ideas from existing workspace
context. Use the repository's current files as the source of truth:

- `context/portfolio-details.md` for equity holdings and open short-premium positions
- `context/watchlist.md` for scored watchlist candidates

Run:

```bash
python3 scripts/trade_idea_generator.py
```

Optional flags:

- `--limit N` to change the number of ideas included in the report
- `--no-telegram` to generate the report without Telegram delivery
- `--telegram-required` to fail the run if Telegram delivery is unavailable
- `--telegram-chat-id CHAT_ID_OR_CHANNEL` to override Telegram destination

## Environment

- `FMP_API_KEY` is optional. If set, the script refreshes quotes and VIX.
- `TELEGRAM_BOT_TOKEN` is required for Telegram delivery.
- One of `TELEGRAM_CHAT_ID`, `TELEGRAM_CHANNEL_ID`, `TELEGRAM_CHANNEL`, or
  `--telegram-chat-id` is required unless the bot has a discoverable prior chat
  from Telegram `getUpdates`.

## Output

Writes:

```text
outputs/trade-idea-generator-{DATE}.md
```

The Telegram message includes the VIX regime, sizing guidance, top ideas, and the
workspace report path.

## Guardrails

- Treat ideas as internal research, not financial advice.
- Validate live prices, option chains, liquidity, bid/ask spreads, earnings dates,
  portfolio concentration, and tax impact before trading.
- For short-premium management, respect the workspace rules: take profits near
  50% of max profit, review/roll/close at 2x credit, and avoid unplanned earnings.
