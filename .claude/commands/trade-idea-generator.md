# Trade Idea Generator

**Purpose:** Generate daily trade ideas from the existing portfolio and watchlist, write an output report, and optionally send the summary to Telegram.

Reads:

- `context/portfolio-details.md` for current holdings and concentration context
- `context/watchlist.md` for scored watchlist candidates
- FMP quote, historical price, VIX, and earnings calendar data

Writes:

- `outputs/trade-idea-generator-{DATE}.md`
- `outputs/trade-idea-generator-{DATE}.json`

## Run

```bash
python3 scripts/trade_idea_generator.py
```

## Send to Telegram

Requires:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID` or `--telegram-chat-id`

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

If the channel chat ID is not exported in the environment, pass it explicitly:

```bash
python3 scripts/trade_idea_generator.py --send-telegram --telegram-chat-id 7830722515
```

## Output

The Telegram message includes:

- SPY/VIX snapshot and volatility regime
- Top 5 ranked trade ideas
- Starter entry or cash-secured put strike to evaluate for watchlist candidates
- Position-management notes for concentrated or extended holdings
- Earnings conflict status and risk reminder

All ideas are research outputs only, not order tickets.
