# /trade-idea-generator — Portfolio + Watchlist Trade Ideas

Generate current trade ideas from the existing repository portfolio and watchlist context, write a report to `outputs/`, and optionally send the concise summary to Telegram.

## Usage

```bash
python scripts/trade_idea_generator.py --send-telegram
```

Optional arguments:

- `--date YYYY-MM-DD` — override report date.
- `--top N` — number of trade ideas to include; default `5`.
- `--skip-options` — use quote/earnings context only if option-chain data is unavailable.
- `--telegram-chat-id CHAT_ID` — override `TELEGRAM_CHAT_ID`; defaults to the configured Altamira chat ID when no environment variable is set.

## Inputs

- `context/portfolio-details.md` — current holdings and short-premium positions.
- `context/watchlist.md` — scored watchlist candidates.
- Environment:
  - `FMP_API_KEY` for quotes and earnings.
  - `MASSIVE_API_KEY` optional, preferred for options chains.
  - `TELEGRAM_BOT_TOKEN` or `TELEGRAM_TOKEN` plus `TELEGRAM_CHAT_ID` for delivery.

## Output

- `outputs/trade-idea-generator-{DATE}.md`
- `outputs/trade-idea-generator-{DATE}.json`
- Telegram summary when `--send-telegram` is provided and Telegram credentials are available.

## Method

1. Parse current holdings, existing short-premium positions, and watchlist scores.
2. Fetch quotes, VIX, 45-day earnings calendar, and options chains.
3. Screen new cash-secured put and covered-call ideas for:
   - 25-60 DTE
   - 0.15-0.35 delta target when available
   - acceptable open interest and bid/ask spread
   - no earnings conflict inside the target expiration window
   - VIX-adjusted position sizing
4. Flag existing short-premium positions that are expired/stale, at 50% profit, or at 200% credit stop/defense threshold.
5. Include risk notes and a financial disclaimer.

## Risk Rules

- Max new short-premium allocation uses 5% of portfolio value, adjusted by VIX regime:
  - LOW: 75%
  - NORMAL: 100%
  - ELEVATED: 50%
  - CRISIS: 25%
- Close at 50% max profit; defend or close at 200% of credit.
- Do not open new short-premium trades through a detected earnings event.
- Validate live option chains and buying power before entry.
