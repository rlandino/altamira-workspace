# /trade-idea-generator — Portfolio + Watchlist Trade Ideas

Generate actionable trade ideas from the current workspace portfolio, watchlist,
and open short-premium positions, then optionally send the Telegram-ready summary
to the Altamira Telegram channel.

## Usage

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

Optional arguments:

- `--max-ideas N` — number of ideas to include in the markdown report (default: 10)
- `--telegram-chat-id CHAT` — override `TELEGRAM_CHAT_ID` / channel username

## Inputs

- `context/portfolio-details.md` — current holdings, weights, P&L, and market value
- `context/watchlist.md` — scored watchlist and candidate status
- `context/options-positions.md` — open short-premium positions, if present
- `TELEGRAM_BOT_TOKEN` — required when sending to Telegram
- `TELEGRAM_CHAT_ID`, `TELEGRAM_CHANNEL_ID`, or `TELEGRAM_CHANNEL_USERNAME` — optional; if absent, the script falls back to the workspace channel convention

## Output

- `outputs/trade-idea-generator-{DATE}.md` — full report
- `outputs/trade-idea-generator-message-{DATE}.txt` — Telegram-ready summary
- Telegram message when `--send-telegram` is provided

## Process

1. Parse current portfolio holdings and identify concentration, profit-harvesting,
   and cleanup candidates.
2. Parse watchlist scores/status and identify starter-entry or CSP candidates.
3. Parse open short-premium positions and apply the workspace rules:
   close near 50% profit, manage near 200% of credit, and avoid adding correlated
   risk while challenged positions remain open.
4. Rank ideas by urgency and confidence.
5. Write the full report and concise Telegram summary.
6. Send the Telegram summary if requested.

## Guardrails

- This command produces research and trade-review candidates, not orders.
- Verify live prices, option chain liquidity, implied volatility, earnings dates,
  and tax impact before trading.
- Follow the risk-management framework: max position sizing, options allocation
  cap, 50% profit target, and 200% stop/roll review.
