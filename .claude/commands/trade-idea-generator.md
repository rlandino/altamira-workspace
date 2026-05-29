# /trade-idea-generator

Generate daily trade ideas from the repository's current portfolio, open short-premium positions, and watchlist, then optionally send the concise summary to Telegram.

## Purpose

This command is the repository-native fallback for daily trade idea generation when the n8n workflow is unavailable or when a Cloud Agent needs to run the process directly.

It reads:

- `context/portfolio-details.md`
- `context/options-positions.md`
- `context/watchlist.md`

It writes:

- `outputs/trade-idea-generator-{DATE}.md`

## Run

```bash
python3 scripts/trade_idea_generator.py
```

To send the Telegram summary:

```bash
python3 scripts/trade_idea_generator.py --send-telegram --chat-id "$TELEGRAM_CHAT_ID"
```

`TELEGRAM_BOT_TOKEN` must be set in the environment. `TELEGRAM_CHAT_ID` can be set in the environment or passed with `--chat-id`.

## Output

The generated report includes:

1. Portfolio and open-options parsing summary
2. Concentration and sector/sleeve risk read-through
3. Existing short-premium management ideas
4. Watchlist candidates with current score/grade context
5. Execution checklist and financial disclaimer
6. Telegram delivery metadata when sent

## Notes

- This command uses only repository context and Python standard library modules.
- It does not place trades. Ideas must be confirmed against live broker prices, earnings dates, liquidity, IV rank, cash, and risk limits before action.
- Use `/paper-trade` to log any selected idea after checks pass.
