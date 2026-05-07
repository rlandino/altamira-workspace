# /trade-idea-generator

**Purpose:** Generate daily actionable trade ideas from the current repository portfolio, open options positions, and watchlist, then send the summary to Telegram.

## Instructions

Run from the workspace root:

```bash
python3 scripts/trade_idea_generator.py
```

The script:

1. Reads `context/portfolio-details.md` for holdings, weights, cash %, VIX/SPY snapshot, and portfolio value.
2. Reads `context/options-positions.md` for open short-premium positions and flags expired, near-expiry, stop-check, and profit-taking situations.
3. Reads `context/watchlist.md` for scored candidates and ranks new-capital ideas.
4. Writes `outputs/trade-idea-generator-{DATE}.md`.
5. Sends a concise Telegram summary using `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.

If `TELEGRAM_CHAT_ID` is not set, the script attempts to reuse the chat id configured in `outputs/csp-daily-scan-fixed.json`, then falls back to Telegram `getUpdates`.

Optional:

```bash
python3 scripts/trade_idea_generator.py --no-telegram --print-message
python3 scripts/trade_idea_generator.py --date 2026-05-07
```

## Output

- Markdown report: `outputs/trade-idea-generator-{DATE}.md`
- Telegram alert with:
  - Market regime and portfolio snapshot
  - Priority option-management actions
  - Covered-call income candidates on concentrated holdings
  - Watchlist entry candidates
  - Risk guardrails

## Risk Notes

- Operational scan only; verify live quotes, options chains, liquidity, earnings dates, and portfolio suitability before orders.
- Respect 5% max trade risk and 30% aggregate options allocation limits.
- Prefer defined-risk spreads when VIX is elevated or sector concentration is already high.
