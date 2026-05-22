# /trade-idea-generator

Generate daily trade ideas from the repository's current portfolio and watchlist, write a markdown report, and optionally send a concise alert to Telegram.

## Purpose

This command turns the static portfolio/watchlist context into an actionable daily trade plan. It is designed for the scheduled automation that runs on market days and sends a short Telegram channel update.

## Inputs

- Portfolio context: `context/portfolio-details.md`
- Watchlist context: `context/watchlist.md`
- Market data: FMP (`FMP_API_KEY`)
- Options snapshots: Massive.com (`MASSIVE_API_KEY`, optional but recommended)
- Telegram delivery: `TELEGRAM_BOT_TOKEN` or `TELEGRAM_TOKEN`; destination from `TELEGRAM_CHAT_ID` or the default channel ID used by the existing CSP workflow

## Run

```bash
python3 scripts/trade_idea_generator.py --send-telegram --print-message
```

Useful variants:

```bash
python3 scripts/trade_idea_generator.py --max-ideas 3
python3 scripts/trade_idea_generator.py --telegram-chat-id "$TELEGRAM_CHAT_ID" --send-telegram
python3 scripts/trade_idea_generator.py --output outputs/trade-idea-generator-YYYY-MM-DD.md
```

## Output

- Markdown report: `outputs/trade-idea-generator-{DATE}.md`
- Telegram alert with the top ranked ideas, contract details when options data is available, rationale, risk notes, and Altamira sizing/management reminders.

## Method

1. Parse current equity positions and portfolio value from `context/portfolio-details.md`.
2. Parse watchlist score, grade, company, and status from `context/watchlist.md`.
3. Fetch quotes, recent historical prices, VIX, and earnings dates from FMP.
4. Compute basic technicals: 20-day SMA, 50-day SMA, and 14-day RSI.
5. Pull 25-55 DTE options snapshots from Massive.com when `MASSIVE_API_KEY` is configured.
6. Rank:
   - Covered calls for existing 100-share lots with profits/concentration.
   - Cash-secured puts for watchlist/current names with quality, trend, and no near-term earnings.
   - Staged equity entries for top watchlist names when options are unavailable or secondary.
7. Apply risk filters:
   - Avoid selling premium through near-term earnings unless explicitly planned.
   - Prefer 0.20-0.30 delta contracts and liquid bid/ask spreads.
   - Keep max position risk near 5% and total options exposure under 30%.
   - Close at 50% max profit; manage at 200% of credit.

## Caveats

This is an educational planning output, not financial advice. Verify live quotes, chain liquidity, earnings timing, and portfolio exposure before placing trades.
