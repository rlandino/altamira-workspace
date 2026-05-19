# /trade-idea-generator — Portfolio + Watchlist Trade Ideas

Generate actionable trade ideas from the current repository portfolio and watchlist, write a dated report, and optionally send the concise summary to Telegram.

## Instructions

Run from the workspace root:

```bash
python scripts/trade_idea_generator.py
```

To send the generated summary to the configured Telegram channel:

```bash
python scripts/trade_idea_generator.py --send-telegram
```

Optional explicit Telegram destination:

```bash
python scripts/trade_idea_generator.py --send-telegram --telegram-chat-id CHAT_ID
```

## Inputs

- `context/portfolio-details.md` — current equity holdings and weights
- `context/watchlist.md` — scored watchlist candidates
- `context/options-positions.md` — open short-premium positions
- FMP API key from `FMP_API_KEY` or existing workspace script configuration
- Massive.com API key from `MASSIVE_API_KEY` or existing CSP workflow configuration
- Telegram bot token from `TELEGRAM_BOT_TOKEN`
- Telegram chat/channel from `TELEGRAM_CHAT_ID`, `TELEGRAM_CHANNEL_ID`, `--telegram-chat-id`, or existing workflow config

## Output

- Markdown report: `outputs/trade-idea-generator-{DATE}.md`
- Telegram-ready text: `outputs/trade-idea-generator-telegram-{DATE}.txt`
- If `--send-telegram` is provided, posts the concise summary to Telegram.

## Method

1. Parse current portfolio holdings, scored watchlist names, and open options.
2. Fetch live quotes, 20-day trend, RSI, VIX regime, and upcoming earnings.
3. Check existing short-premium positions against the 50% profit and 200% stop rules.
4. Screen top watchlist names for 30-60 DTE put-selling candidates when option-chain data is available.
5. Screen profitable overweight holdings for covered-call candidates.
6. Rank ideas by urgency, quality score, trend, event risk, and option liquidity.

## Risk Notes

- Informational scan only; not investment advice or trade execution.
- Verify live bid/ask, open interest, and earnings dates before any order.
- Do not sell new short premium through unplanned earnings.
- Follow the workspace risk framework: max position sizing, close at 50% profit, stop or roll at 200% of credit.
