# /trade-idea-generator — Portfolio + Watchlist Trade Ideas

Generate cash-secured put trade ideas from the current repository portfolio and
watchlist context, then optionally send the alert to Telegram.

## Usage

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

Optional arguments:

- `--max-ideas N` — number of ideas to include in the report and Telegram alert
  (default: 5).
- `--include-low-priority` — include watchlist-only names marked Low Priority or
  Avoid. By default, these are excluded.
- `--output outputs/trade-idea-generator-YYYY-MM-DD.md` — override report path.
- `--telegram-chat-id CHAT_ID` — override `TELEGRAM_CHAT_ID` or configured
  workflow fallback.

## Inputs

- `context/portfolio-details.md` — current holdings and portfolio value.
- `context/watchlist.md` — watchlist scores, grades, and statuses.
- `context/options-positions.md` — existing short-premium tickers for
  concentration notes.
- FMP API key from `FMP_API_KEY` or existing workflow configuration fallback.
- Massive.com API key from `MASSIVE_API_KEY` or existing workflow configuration
  fallback.
- Telegram bot token from `TELEGRAM_BOT_TOKEN` when sending.

## Process

1. Build the optionable universe from current portfolio holdings and watchlist.
2. Exclude non-optionable names, watchlist-only Low Priority/Avoid names unless
   requested, symbols below the 50-day SMA, low-volume underlyings, and stocks
   with earnings inside the target DTE window.
3. Fetch 30-45 DTE put-option snapshots from Massive.com.
4. Filter for 0.20-0.30 absolute delta, minimum open interest/volume, acceptable
   bid/ask spread, and sufficient IV proxy.
5. Score each CSP by annualized return, IV proxy, liquidity, trend, watchlist
   quality, and existing short-premium concentration.
6. Write `outputs/trade-idea-generator-{DATE}.md` plus a Telegram preview text
   file. If `--send-telegram` is passed, send the concise alert to Telegram.

## Output

- Markdown report: `outputs/trade-idea-generator-{DATE}.md`
- Telegram preview: `outputs/trade-idea-generator-{DATE}.telegram.txt`
- Telegram delivery response in stdout when `--send-telegram` is used

## Risk Note

These are scan results, not trade orders or personalized financial advice.
Verify live quotes, assignment risk, portfolio concentration, and liquidity
before entry. Use `/paper-trade` only after live quote/risk review.
