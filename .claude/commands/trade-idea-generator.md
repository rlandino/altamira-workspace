# /trade-idea-generator

**Purpose:** Generate a daily trade idea brief from the current repository portfolio and watchlist context, write an auditable report, and optionally send the concise brief to Telegram.

## Usage

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

## Inputs

- `context/portfolio-details.md` — current holdings, weights, prices, and P&L.
- `context/watchlist.md` — scored watchlist candidates.
- `context/options-positions.md` — current short-premium/options context.
- `TELEGRAM_BOT_TOKEN` — required for Telegram delivery.
- `TELEGRAM_CHAT_ID` — optional when the configured chat fallback in `outputs/csp-daily-scan-fixed.json` is valid.

## Outputs

- `outputs/trade-idea-generator-{DATE}.md` — full report.
- `outputs/trade-idea-generator-{DATE}-telegram.txt` — exact Telegram message body.
- `outputs/trade-idea-generator-{DATE}-telegram-status.json` — send status when `--send-telegram` is used.

## Notes

- The generator uses repository snapshots by default so it can run in automation without broker access.
- Verify live prices, option chains, liquidity, earnings dates, and risk limits before trading.
- Financial output must be treated as research, not financial advice.
