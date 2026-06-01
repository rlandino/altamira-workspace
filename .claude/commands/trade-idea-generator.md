# /trade-idea-generator

**Purpose:** Generate actionable trade ideas from the repository's current portfolio, short-premium positions, and watchlist, then optionally send the top ideas to Telegram.

## Usage

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

Use `--require-telegram` when the run should fail if Telegram delivery cannot complete.

## Inputs

- `context/portfolio-details.md` — equity positions, weights, P&L, and short-premium table.
- `context/watchlist.md` — scored watchlist candidates.
- Environment for delivery:
  - `TELEGRAM_BOT_TOKEN`
  - `TELEGRAM_CHAT_ID` or `TELEGRAM_CHANNEL_ID`

## Output

- `outputs/trade-idea-generator-{DATE}.md` — full research report.
- `outputs/trade-idea-generator-telegram-{DATE}.txt` — Telegram-sized summary.
- Telegram message when bot token and chat/channel id are configured.

## Notes

- Financial disclaimer is included in the report.
- Ideas are research prompts, not order tickets. Verify live prices, option chain liquidity, Greeks, earnings dates, and risk limits before trading.
- The generator works from repository context first so scheduled automations still produce output if live APIs are unavailable.
