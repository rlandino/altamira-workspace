# /trade-idea-generator

Generate trade ideas from the current repository portfolio and watchlist, write a markdown report, and optionally send the summary to Telegram.

## Usage

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

Optional arguments:

- `--chat-id CHAT_ID` — override the Telegram chat/channel id.
- `--out outputs/custom-file.md` — override the markdown report path.

## Inputs

- `context/portfolio-details.md` — existing holdings, weights, and P&L context.
- `context/watchlist.md` — watchlist tickers, scores, grades, and statuses.
- FMP quote and earnings calendar data via `FMP_API_KEY` or the existing repository fallback key.
- Telegram delivery via `TELEGRAM_BOT_TOKEN` and either `TELEGRAM_CHAT_ID` or the deployed workflow chat id in `outputs/csp-daily-scan-fixed.json`.

## Output

- `outputs/trade-idea-generator-{DATE}.md`
- Telegram text summary with top actionable ideas, no-trade/avoid names, earnings conflicts, and an educational disclaimer.

## Notes

- This is trade planning output only, not financial advice.
- Confirm live quotes, option-chain liquidity, earnings dates, and portfolio limits before any execution.
