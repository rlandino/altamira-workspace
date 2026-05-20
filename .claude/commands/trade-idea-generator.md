# /trade-idea-generator — Portfolio + Watchlist Trade Ideas

Generate a concise daily trade-idea report from the repository's current portfolio,
open short-premium positions, and watchlist, then optionally send the summary to
Telegram.

## Instructions

Run the local script from the workspace root:

```bash
python3 scripts/trade_idea_generator.py
```

To send the generated summary to Telegram:

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

## Inputs

The script reads local repository context only:

- `context/portfolio-details.md` — holdings, weights, current prices, portfolio market value
- `context/options-positions.md` — open short-premium positions
- `context/watchlist.md` — ranked watchlist candidates

Telegram delivery uses:

- `TELEGRAM_BOT_TOKEN` from the environment
- `TELEGRAM_CHAT_ID` from the environment, or a numeric `chatId` discovered in
  existing n8n workflow exports under `outputs/`

Override the destination when needed:

```bash
python3 scripts/trade_idea_generator.py --send-telegram --telegram-chat-id CHAT_ID
```

## Output

Writes:

```text
outputs/trade-idea-generator-{DATE}.md
```

The Telegram message includes:

1. Priority actions from open options and concentration risk
2. Watchlist entry setups for B- or better candidates
3. Open options management notes
4. Risk flags and a disclaimer

## Trading Guardrails

- Verify live prices, options chain liquidity, IV, and earnings dates before entry.
- Use 30-45 DTE and 0.20-0.25 delta as the default short-premium lane.
- Favor defined-risk spreads when adding to already concentrated semiconductor or AI exposure.
- Set 50% profit-taking and 200% loss-management alerts at entry.
- This is research workflow support only, not financial advice or an order recommendation.
