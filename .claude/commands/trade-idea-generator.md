# /trade-idea-generator

Generate one concise, portfolio-aware trade idea from the current repository context and optionally send it to Telegram.

## Purpose

Use this command for the daily trade idea workflow. It reads the current portfolio, watchlist, and short-premium positions from the repository, identifies the most actionable risk-adjusted idea, writes a dated report to `outputs/`, and can send the Telegram-ready summary to the configured channel.

## Inputs

- Portfolio: `context/portfolio-details.md`
- Watchlist: `context/watchlist.md`
- Options positions: `context/options-positions.md`
- Telegram credentials:
  - `TELEGRAM_BOT_TOKEN` environment variable
  - `TELEGRAM_CHAT_ID` environment variable, or pass `--chat-id`

## Run

```bash
python3 scripts/trade_idea_generator.py
```

To send to Telegram:

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

If the chat ID is not available in the environment, pass it explicitly:

```bash
python3 scripts/trade_idea_generator.py --send-telegram --chat-id CHAT_ID
```

## Output

- Markdown report: `outputs/trade-idea-generator-{DATE}.md`
- Telegram summary containing:
  - Primary trade idea
  - Secondary watchlist queue
  - Existing short-premium risk read-through
  - Clear action checklist
  - Trading disclaimer

## Method

1. Parse current holdings and weights from `context/portfolio-details.md`.
2. Parse scored watchlist candidates from `context/watchlist.md`.
3. Parse open short-premium positions from `context/options-positions.md`.
4. Prefer income ideas that reduce portfolio risk before adding new short-put notional.
5. Highlight existing options positions that need management before initiating new risk.
6. Send a plain-text Telegram message so no Markdown escaping is required.

## Risk Notes

- This command uses repository context. Confirm live prices, option chains, bid/ask liquidity, earnings dates, and risk limits before trading.
- Financial calculations and trade ideas are informational and are not financial advice.
