# /trade-idea-generator — Portfolio + Watchlist Trade Ideas

Generate daily trade ideas from the repository's current portfolio and watchlist,
write a report, and optionally send the summary to Telegram.

## Usage

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

Optional flags:

- `--max-tickers N` — maximum ranked tickers to fetch option chains for (default: 16)
- `--max-ideas N` — maximum trade ideas in the summary (default: 5)
- `--dry-run` — generate the report and print the Telegram message without sending

## Inputs

- `context/portfolio-details.md` — current holdings and weights
- `context/watchlist.md` — watchlist scores, grades, and candidate status
- FMP market data key from `FMP_API_KEY` or existing workspace command config
- Massive/Polygon options key from `MASSIVE_API_KEY`, `POLYGON_API_KEY`, or existing workspace command config
- Telegram bot token from `TELEGRAM_BOT_TOKEN`
- Telegram chat/channel from `TELEGRAM_CHAT_ID`, falling back to the deployed CSP scan workflow chat ID

## Process

1. Parse current portfolio holdings and watchlist tickers.
2. Merge duplicate tickers and keep source tags (`portfolio`, `watchlist`, or both).
3. Fetch live quotes, VIX, and upcoming earnings from FMP.
4. Rank the universe for option-chain fetches using quality score, portfolio status, trend, and watchlist grade.
5. Fetch 20-60 DTE put chains from Massive/Polygon, falling back to FMP options-chain data.
6. Score cash-secured put candidates by:
   - Premium yield
   - Breakeven cushion
   - Delta fit
   - Liquidity
   - Trend/quality context
   - Earnings risk
7. Write `outputs/trade-idea-generator-{DATE}.md`.
8. Send a concise Telegram summary when `--send-telegram` is provided.

## Risk Guardrails

- Ideas are research outputs, not orders.
- Confirm live bid/ask, liquidity, upcoming earnings, and portfolio exposure before entry.
- Default management reference: close short premium at 50% of max profit; define stop/adjustment trigger before entry.
