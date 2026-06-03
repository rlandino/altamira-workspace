# /trade-idea-generator

Generate daily trade ideas from the repository's current portfolio and watchlist, then optionally send the concise alert to Telegram.

## Usage

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

Optional arguments:

- `--max-options-tickers N` — cap the number of prioritized symbols with live option-chain fetches (default: 24).
- `--chat-id CHAT_ID` — override `TELEGRAM_CHAT_ID` / repository fallback chat ID.

## Inputs

- `context/portfolio-details.md` — current holdings, quantities, average prices, portfolio value.
- `context/watchlist.md` — watchlist universe and candidate priority.
- `context/options-positions.md` — existing short-premium positions for management alerts.
- Live FMP quotes / earnings calendar and Massive.com option snapshots.

## Environment

Preferred environment variables:

- `FMP_API_KEY`
- `MASSIVE_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

If FMP/Massive keys are not set, the script reuses existing API-key references already present in workspace command/workflow docs. If `TELEGRAM_CHAT_ID` is not set, it reuses the fixed chat ID from the existing CSP scan workflow.

## Output

- Full report: `outputs/trade-idea-generator-{DATE}.md`
- Console summary.
- Telegram alert when `--send-telegram` is provided.

## Strategy Rules

- Short-premium focus: CSPs and covered calls.
- Target contracts: 30-45 DTE, 0.20-0.30 delta, positive bid, reasonable spread, minimum open interest.
- Avoid new ideas with earnings inside the target window.
- Apply VIX regime sizing: LOW 75%, NORMAL 100%, ELEVATED 50%, CRISIS 25%.
- Include management alerts for existing short-premium positions:
  - Take profit candidate at 50% of original credit.
  - Defense/stop review at 200% of original credit.
- Include a risk gate when current short-put notional exceeds the framework's options allocation cap.

## Notes

The output is informational and not financial advice. Validate liquidity, earnings dates, and limit prices before trading.
