# /trade-idea-generator

Generate daily trade ideas from the repository's current portfolio and watchlist context, write a dated report, and send a concise summary to Telegram.

## Instructions

You are generating an Altamira Capital trade-idea alert.

### Step 1: Read current context

Use these repository files:

- `context/portfolio-details.md` for holdings, weights, cash, and open short-premium positions.
- `context/watchlist.md` for candidate tickers, scores, grades, and status.

### Step 2: Run the generator

From the workspace root, run:

```bash
python scripts/trade_idea_generator.py --send
```

Optional flags:

- `--telegram-chat-id CHAT_ID` to override `TELEGRAM_CHAT_ID` / `TELEGRAM_CHANNEL_ID`.
- `--date YYYY-MM-DD` to generate for a specific date.
- `--out outputs/custom-file.md` to override the report path.

The script writes `outputs/trade-idea-generator-{DATE}.md`.

### Step 3: Delivery behavior

- Uses `TELEGRAM_BOT_TOKEN` for Telegram delivery.
- Uses `TELEGRAM_CHAT_ID` or `TELEGRAM_CHANNEL_ID` when available.
- If no chat/channel environment variable is set, falls back to the chat ID already present in `outputs/csp-daily-scan-fixed.json`.
- Splits long Telegram messages into safe chunks automatically.

### Step 4: What the report includes

1. Portfolio value, cash, VIX regime, and data-source notes.
2. Top trade ideas ranked across:
   - Near-expiration short-premium management.
   - Watchlist CSP or bull-put-spread candidates.
   - Covered-call or trim discipline for concentrated holdings.
3. Portfolio concentration snapshot.
4. Watchlist priority snapshot.
5. Data hygiene notes for stale/expired options rows.

## Context

- This command is a portfolio/watchlist alerting workflow, not order execution.
- It does not place trades.
- It can use live FMP quotes when `FMP_API_KEY` is set; otherwise it falls back to repository snapshot prices.
- Validate live prices, option chains, earnings dates, and risk limits before trading.
