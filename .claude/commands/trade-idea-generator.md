# /trade-idea-generator

Generate trade ideas from the current repository portfolio and watchlist, write a dated report, and optionally send the summary to Telegram.

## Usage

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

## Inputs

- `context/portfolio-details.md` for current holdings, weights, prices, and P&L.
- `context/watchlist.md` for watchlist scores, grades, and candidate status.
- Yahoo Finance quote endpoint for current prices when available; repository snapshot prices remain the fallback.
- `TELEGRAM_BOT_TOKEN` for delivery.
- `TELEGRAM_CHAT_ID` when set; otherwise the script reuses the Telegram chat ID configured in `outputs/csp-daily-scan-fixed.json`.

## Output

- Writes `outputs/trade-idea-generator-{YYYY-MM-DD}.md`.
- Sends a concise Telegram message with ranked ideas when `--send-telegram` is used.

## Method

1. Parse current equity positions and watchlist candidates.
2. Generate covered-call ideas for holdings with at least 100 shares and meaningful concentration or gains.
3. Generate cash-secured put or bull-put-spread entry ideas for top watchlist candidates.
4. Rank ideas using portfolio weight, gains, watchlist score, grade, and position-cap constraints.
5. Include risk reminders to confirm live option chains, earnings dates, liquidity, and bid/ask before order entry.

## Risk Note

This command does not place trades and does not estimate option premiums without a live chain. Treat output as an idea queue only; confirm live market data and follow the risk framework before execution.
