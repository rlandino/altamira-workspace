# /trade-idea-generator

**Purpose:** Generate daily trade ideas from the current portfolio and watchlist, write a dated report, and optionally send a concise summary to Telegram.

## Usage

```bash
python3 scripts/trade_idea_generator.py --send
```

Optional arguments:

- `--max-tickers N` — cap the scan universe after prioritizing current holdings and highest-scored watchlist names. Default: 32.
- `--output outputs/trade-idea-generator-YYYY-MM-DD.md` — override the report path.
- `--chat-id CHAT_ID` — override `TELEGRAM_CHAT_ID` for a one-off send.

## What it does

1. Reads:
   - `context/portfolio-details.md`
   - `context/watchlist.md`
   - `context/options-positions.md`
2. Builds a prioritized universe from portfolio holdings and watchlist candidates.
3. Fetches FMP quotes, VIX, historical prices, and earnings calendar data.
4. Fetches Massive.com option snapshots for 20-60 DTE puts, plus calls for holdings with at least 100 shares.
5. Scores:
   - Cash-secured put ideas for portfolio/watchlist entries.
   - Covered call ideas for current holdings.
6. Filters out CSP ideas with known earnings before expiration.
7. Flags existing short-put exposure from `context/options-positions.md`.
8. Writes:
   - `outputs/trade-idea-generator-{DATE}.md`
   - `outputs/trade-idea-generator-{DATE}.json`
9. Sends the top ideas to Telegram when `TELEGRAM_BOT_TOKEN` and a chat destination are configured.

## Environment

- `FMP_API_KEY` optional; falls back to the workspace development key used by existing scripts.
- `MASSIVE_API_KEY` optional; falls back to the workspace development key used by existing scripts.
- `TELEGRAM_BOT_TOKEN` required for `--send`.
- `TELEGRAM_CHAT_ID` required for `--send` unless `--chat-id` is provided or a unique chat can be inferred from bot updates.

## Risk note

These are scan results, not trade orders or financial advice. Confirm all quotes, greeks, liquidity, tax impact, and portfolio risk limits in the broker before placing trades.
