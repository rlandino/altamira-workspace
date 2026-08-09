# /trade-idea-generator

Generate daily trade ideas from the existing portfolio and watchlist in the
repository, write an audit report, and optionally send the Telegram summary.

## Usage

```bash
python3 scripts/trade_idea_generator.py --include-options-chain --send-telegram
```

Optional arguments:

- `--include-options-chain` - Try to include exact option contract candidates
  from FMP options chain data when available.
- `--send-telegram` - Send the short summary to Telegram.
- `--telegram-chat-id CHAT_ID` - Override `TELEGRAM_CHAT_ID` for the
  destination chat/channel.
- `--print-message` - Print the Telegram-ready summary to stdout.

## Required configuration

- `FMP_API_KEY` for live market data. If it is not set, the script reuses the
  local development fallback already exposed by `scripts/market_data_api.py`.
- `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` for Telegram delivery.

## Inputs

- `context/portfolio-details.md`
- `context/watchlist.md`
- `context/options-positions.md`

## Outputs

- `outputs/trade-idea-generator-{DATE}.md`
- `outputs/trade-idea-generator-{DATE}.json`
- Telegram message, when delivery credentials are configured.

## Process

1. Parse current holdings, watchlist scores, and short-premium positions.
2. Fetch live FMP quotes and recent price history.
3. Classify VIX regime and VIX-adjusted sizing.
4. Rank cash-secured put / put-spread candidates from top watchlist names and
   approved portfolio names.
5. Flag covered-call or trim candidates for overweight or extended holdings.
6. Review existing short-premium positions against credit/current value.
7. Include a financial disclaimer and require trade-ticket verification before
   execution.
