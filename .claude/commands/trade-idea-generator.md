# /trade-idea-generator

Generate daily trade ideas from the repository's current portfolio, watchlist, and open short premium context, then send the concise summary to Telegram.

## Usage

```bash
python scripts/trade_idea_generator.py --send-telegram
```

Optional:

```bash
python scripts/trade_idea_generator.py --no-live-data
python scripts/trade_idea_generator.py --as-of 2026-05-29 --send-telegram
```

## Data Sources

- `context/portfolio-details.md` — current holdings and weights
- `context/watchlist.md` — candidate tickers, scores, grades, and status
- `context/options-positions.md` — existing short premium positions
- FMP quote and earnings data when `FMP_API_KEY` or `FINANCIAL_MODELING_PREP_API_KEY` is set

## Telegram Configuration

Set these environment variables before sending:

- `TELEGRAM_BOT_TOKEN` (or `TELEGRAM_TOKEN` / `TELEGRAM_API_TOKEN`)
- `TELEGRAM_CHAT_ID` (or `TELEGRAM_CHANNEL_ID`)

The script writes:

- `outputs/trade-idea-generator-{DATE}.md`
- `outputs/trade-idea-generator-telegram-{DATE}.txt`

## Output

The generator ranks:

1. Existing short premium management actions, including 50% profit-taking and 200% credit stop alerts.
2. Covered call candidates for current share lots, emphasizing concentrated holdings.
3. Watchlist CSP or bull put spread candidates, adjusted for VIX regime and upcoming earnings conflicts.

Always validate live option chains, liquidity, earnings dates, portfolio cash, and options allocation limits before entering any trade. This command is educational analysis only and is not investment advice.
