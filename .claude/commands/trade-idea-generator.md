# /trade-idea-generator

Generate a daily trade idea report from the current portfolio and watchlist in
the repository, then optionally send the concise summary to Telegram.

## Usage

```bash
python3 scripts/trade_idea_generator.py
python3 scripts/trade_idea_generator.py --send-telegram
```

## Instructions

1. Read the source context:
   - `context/portfolio-details.md`
   - `context/watchlist.md`
2. Run:
   ```bash
   python3 scripts/trade_idea_generator.py --send-telegram
   ```
3. Confirm these outputs were created:
   - `outputs/trade-idea-generator-{DATE}.md`
   - `outputs/trade-idea-generator-telegram-{DATE}.txt`
   - `outputs/trade-idea-generator-telegram-status-{DATE}.txt` when sending
4. If Telegram delivery fails because `TELEGRAM_CHAT_ID` is not configured,
   retry with:
   ```bash
   python3 scripts/trade_idea_generator.py --send-telegram --telegram-chat-id CHAT_ID_OR_CHANNEL
   ```

## Behavior

The script:

- Parses current holdings, open short-premium positions, and watchlist entries.
- Fetches live quotes, VIX, earnings calendar, and options chains when API
  credentials are available.
- Prioritizes:
  1. Existing short-premium risk management.
  2. Covered-call candidates on large profitable holdings.
  3. Cash-secured put candidates from top watchlist names.
  4. Concentration trim ideas.
- Writes a markdown report and a Telegram-sized text summary.

## Risk Rules

- Avoids new CSP and covered-call ideas when earnings are inside the relevant
  event window.
- Targets 28-52 DTE and 0.20-0.30 delta when option-chain data is available.
- Uses target-only strikes when option chains are unavailable; those require
  manual confirmation before entry.
- Financial calculations are decision support only and are not investment
  advice.
