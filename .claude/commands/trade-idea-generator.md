# /trade-idea-generator — Portfolio and Watchlist Trade Ideas

Generate a concise trade idea report from the current repository portfolio and watchlist context, then optionally send the top ideas to Telegram.

## Instructions

Run from the workspace root:

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

The script reads:

- `context/portfolio-details.md`
- `context/watchlist.md`

It writes:

- `outputs/trade-idea-generator-{DATE}.md`

## Telegram Delivery

Telegram delivery uses:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

If `TELEGRAM_CHAT_ID` is not exported, pass it explicitly:

```bash
python3 scripts/trade_idea_generator.py --send-telegram --telegram-chat-id 7830722515
```

## Output Criteria

The report should include:

1. Portfolio concentration and risk overlay ideas.
2. Any stale or expired options-position hygiene flags.
3. Highest-scoring watchlist candidates with setups and guardrails.
4. A clear disclaimer that ideas are not financial advice and must be checked against live quotes, option chains, earnings, liquidity, tax impact, and portfolio constraints.

## Context

- Designed for the weekday automation that asks to execute `/trade-idea-generator`.
- Uses existing repository context only by default so it remains reliable when live market-data keys are unavailable.
- Does not place trades.
