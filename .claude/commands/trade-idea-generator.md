# /trade-idea-generator

Generate daily trade ideas from the existing portfolio and watchlist context, write a report, and send the concise summary to Telegram.

## Purpose

Runs `scripts/trade_idea_generator.py` against:

- `context/portfolio-details.md`
- `context/watchlist.md`

The generator combines:

- Existing short-premium management rules (50% profit take, 200% stop/roll review)
- Watchlist quality scores and live FMP quote/earnings context when available
- Portfolio concentration and covered-call/rebalance overlays
- Telegram delivery through `TELEGRAM_BOT_TOKEN` plus `TELEGRAM_CHAT_ID` or the fixed chat ID in the existing CSP workflow export

## Usage

```bash
python3 scripts/trade_idea_generator.py
```

Dry run without Telegram delivery:

```bash
python3 scripts/trade_idea_generator.py --dry-run
```

Optional date override:

```bash
python3 scripts/trade_idea_generator.py --date 2026-06-03
```

## Output

- Markdown report: `outputs/trade-ideas-{DATE}.md`
- Telegram message: top ranked actionable ideas with risk notes

## Notes

- Set `FMP_API_KEY` when possible. If it is not set, the script reuses existing repo workflow configuration for FMP access.
- Set `TELEGRAM_CHAT_ID` when possible. If it is not set, the script reuses the fixed chat ID from `outputs/csp-daily-scan-fixed.json`.
- All generated trade ideas are informational only; confirm live prices, option chains, liquidity, and risk limits before trading.
