# /trade-idea-generator

Generate ranked trade ideas from the current repository portfolio and watchlist, write the report to `outputs/`, and optionally send the concise version to the configured Telegram channel.

## Instructions

Run from the workspace root:

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

The script:

1. Reads current positions and option rows from `context/portfolio-details.md`.
2. Reads watchlist candidates from `context/watchlist.md`.
3. Fetches live FMP quotes, VIX/SPY market context, upcoming earnings, and (when available) option-chain contracts.
4. Produces:
   - `outputs/trade-idea-generator-{DATE}.md`
   - `outputs/trade-idea-generator-{DATE}-telegram.txt`
   - `outputs/trade-idea-generator-{DATE}-telegram-status.json` when sending
5. Sends the Telegram text through `TELEGRAM_BOT_TOKEN`.

## Options

- `--send-telegram` sends a new Telegram message.
- `--edit-message-id MESSAGE_ID` edits an existing Telegram post instead of sending a duplicate.
- `--skip-option-chain` skips option-chain enrichment and uses target strikes for manual chain lookup.
- `--date YYYY-MM-DD` overrides the report date.

## Context

- Uses existing workspace risk conventions: premium selling on high-quality holdings/watchlist names, earnings avoidance, position sizing discipline, and manual confirmation of liquidity before entry.
- If `TELEGRAM_CHAT_ID` is not set, the script falls back to the existing chat ID in `outputs/csp-daily-scan-fixed.json`.
- Output is for research and paper-trading support only, not financial advice.
