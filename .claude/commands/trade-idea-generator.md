# /trade-idea-generator - Portfolio + Watchlist Trade Ideas

Generate a daily trade idea report from the current repository portfolio and watchlist, then optionally deliver the summary to Telegram.

## Usage

```bash
python3 scripts/trade_idea_generator.py --print-message
python3 scripts/trade_idea_generator.py --send-telegram
```

For manual channel routing:

```bash
python3 scripts/trade_idea_generator.py --send-telegram --telegram-chat-id CHAT_ID
```

## Inputs

- `context/portfolio-details.md` - current positions, weights, market values, and short-premium positions.
- `context/watchlist.md` - scored watchlist candidates.
- `TELEGRAM_BOT_TOKEN` - required only when `--send-telegram` is used.
- `TELEGRAM_CHAT_ID` or `--telegram-chat-id` - required only when `--send-telegram` is used.

## Output

- Writes `outputs/trade-idea-generator-{DATE}.md`.
- Telegram summary includes top exposures, ranked ideas, options needing review, top watchlist candidates, and report path.

## Method

The command is repository-based rather than live-market-data based:

1. Parse portfolio holdings and short-premium positions from `context/portfolio-details.md`.
2. Parse watchlist scores from `context/watchlist.md`.
3. Flag concentration risk versus the 5% strict and 10% tactical position guardrails.
4. Flag sector/theme exposure versus the 25% sector guardrail.
5. Rank trade ideas across:
   - risk-down / trim / collar candidates,
   - short-premium triage,
   - watchlist starters,
   - covered-call income candidates,
   - avoid or low-priority names.
6. Write a full markdown report and, if requested, send a concise Telegram message.

## Risk Note

This command produces research and workflow automation output only. It is not financial advice or a trade order. Confirm live prices, option chains, liquidity, earnings dates, and portfolio cash before execution.
