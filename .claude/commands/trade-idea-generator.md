# /trade-idea-generator - Portfolio and Watchlist Trade Ideas

Generate a concise daily trade idea scan from the repository's current portfolio, short premium positions, and watchlist, then optionally send the summary to Telegram.

## Instructions

Run the Python script:

```bash
python3 scripts/trade_idea_generator.py
```

To send the concise summary to Telegram:

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

The script reads:

- `context/portfolio-details.md` for current holdings, weights, prices, and concentration
- `context/options-positions.md` for open short premium positions
- `context/watchlist.md` for scored watchlist candidates

It writes:

- `outputs/trade-idea-generator-{DATE}.md`

## Data and Credentials

- Optional live quote enrichment uses `FMP_API_KEY` from the environment.
- Telegram delivery uses `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
- If `TELEGRAM_CHAT_ID` is missing, the script attempts to reuse the fixed chat id already configured in `outputs/csp-daily-scan-fixed.json`.

## Output Framework

The generated report covers:

1. Priority actions for existing short premium positions
2. Covered call or trim candidates for overweight holdings
3. Watchlist entry candidates for cash-secured put or defined-risk spread screening
4. Risk rules before entry, including earnings, liquidity, IV, sizing, and 50% profit / 200% credit management rules

All output is a planning scan only and must include the standard financial disclaimer.
