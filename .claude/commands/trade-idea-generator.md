# /trade-idea-generator - Portfolio and Watchlist Trade Ideas

Generate trade ideas from the repository's current portfolio and watchlist context, write a dated report, and optionally send the concise version to Telegram.

## Instructions

Run the local script:

```bash
python scripts/trade_idea_generator.py
```

To send the concise report to Telegram:

```bash
python scripts/trade_idea_generator.py --send-telegram
```

The script reads:

- `context/portfolio-details.md` for current holdings and options rows
- `context/watchlist.md` for watchlist scores and candidate status

It writes:

- `outputs/trade-idea-generator-{DATE}.md`

## Telegram Configuration

The script uses:

- `TELEGRAM_BOT_TOKEN` for the bot token
- `TELEGRAM_CHAT_ID` or `ALTAMIRA_TELEGRAM_CHAT_ID` for the target chat
- A repository fallback chat ID from the existing CSP workflow export when no chat ID environment variable is set

## Output Focus

The report prioritizes:

1. Covered-call or trim overlays for large profitable holdings.
2. Short-put management alerts for active option rows when current marks are near risk triggers.
3. Watchlist CSP candidates scored B- or better and not already held.

All ideas require live quote, option-chain, earnings, liquidity, and risk-limit checks before trading.
