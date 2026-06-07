# /trade-idea-generator - Portfolio and Watchlist Trade Ideas

Generate trade ideas from the current repository portfolio and watchlist context, save a markdown report, and optionally send the Telegram-ready summary to the configured Telegram channel.

## Usage

```bash
python3 scripts/trade_idea_generator.py
python3 scripts/trade_idea_generator.py --send-telegram
```

Required for market data:

- `FMP_API_KEY` environment variable, or pass `--fmp-api-key`.
- `MASSIVE_API_KEY` environment variable, or pass `--massive-api-key`, for primary options snapshots. If omitted or unavailable, FMP options data is attempted as a fallback.

Required for Telegram delivery:

- `TELEGRAM_BOT_TOKEN` environment variable, or pass `--telegram-token`.
- `TELEGRAM_CHAT_ID` environment variable, or pass `--telegram-chat-id`.

If no chat id is provided, the script uses the same Telegram chat id documented in the existing CSP Daily Scan workflow.

## What It Reads

- `context/portfolio-details.md` for holdings, weights, cash, and portfolio value.
- `context/watchlist.md` for scored watchlist candidates.

## What It Does

1. Pulls live FMP quotes for portfolio holdings and watchlist tickers.
2. Pulls VIX and classifies the regime:
   - LOW: VIX < 15
   - NORMAL: 15-25
   - ELEVATED: 25-35
   - CRISIS: > 35
3. Excludes tickers with earnings inside the next 45 days.
4. Ranks a candidate universe from current holdings and watchlist names.
5. Scans option chains, using Massive.com first and FMP as fallback, for:
   - Cash-secured puts, 20-60 DTE, OTM, liquid, target delta zone.
   - Covered calls on current holdings with at least 100 shares.
6. Adds watchlist entry-review ideas for high-scoring non-held names holding trend support.
7. Writes `outputs/trade-idea-generator-{DATE}.md`.
8. With `--send-telegram`, sends the concise summary to Telegram and records the delivery result in the report.

## Risk Notes

- This command produces scan output only, not trade orders.
- Confirm live option chains, bid/ask liquidity, earnings dates, portfolio exposure, and stop/management levels before entry.
- Include the standard financial disclaimer in generated reports.
