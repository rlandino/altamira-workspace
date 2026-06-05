# /trade-idea-generator

Generate the daily Altamira trade idea scan from the current repository portfolio
and watchlist, write the report to `outputs/`, and optionally send the summary to
Telegram.

## Usage

```bash
python scripts/trade_idea_generator.py --send-telegram
```

For a local preview without sending Telegram:

```bash
python scripts/trade_idea_generator.py --dry-run
```

## Inputs

- `context/portfolio-details.md` - current equity positions, weights, and prices.
- `context/watchlist.md` - scored watchlist candidates.
- `context/options-positions.md` - existing short-premium positions to avoid
  over-stacking risk.
- FMP market data via `FMP_API_KEY` when available. If not set, the script uses
  repository workflow defaults already checked into the workspace.
- Massive.com options-chain snapshots via `MASSIVE_API_KEY` when available. If not
  set, the script uses repository workflow defaults already checked into the
  workspace. If options-chain data is unavailable, it marks option ideas as
  heuristic estimates requiring manual chain verification.
- Telegram via `TELEGRAM_BOT_TOKEN` plus `TELEGRAM_CHAT_ID`. If `TELEGRAM_CHAT_ID`
  is not set, the script falls back to the fixed chat ID in
  `outputs/csp-daily-scan-fixed.json`.

## Output

- Markdown report: `outputs/trade-idea-generator-{YYYY-MM-DD}.md`
- Telegram summary with the top ranked ideas when `--send-telegram` is used.

## Process

1. Parse current holdings, watchlist scores, and open options exposure.
2. Fetch quotes, VIX regime, historical price context, earnings, and options-chain
   snapshots when credentials are available.
3. Rank:
   - Covered-call ideas for meaningful existing holdings.
   - Cash-secured-put ideas for top watchlist candidates.
   - A SPY hedge watch item when VIX is low and portfolio exposure is equity-heavy.
4. Apply risk flags for earnings, existing short-put exposure, large weights, and
   elevated VIX.
5. Write the markdown report and send a concise Telegram summary.

## Risk reminder

The generator produces scan results, not trade orders. Verify live option chains,
liquidity, earnings windows, and Altamira position limits before entering any
trade.
