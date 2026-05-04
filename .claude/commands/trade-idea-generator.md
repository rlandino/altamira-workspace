# /trade-idea-generator — Portfolio and Watchlist Trade Ideas

Generate the daily Altamira trade idea digest from the current repository portfolio and watchlist context, then optionally send the digest to Telegram.

## Instructions

Run from the workspace root:

```bash
python scripts/trade_idea_generator.py --send-telegram
```

The script:

1. Reads `context/portfolio-details.md` for current equity holdings and short-premium positions.
2. Reads `context/watchlist.md` for watchlist candidates and quality scores.
3. Fetches live FMP quotes plus recent price history for trend and RSI context.
4. Scores:
   - short-premium positions against 50% profit-taking and 200% stop/roll triggers,
   - concentrated holdings for trim, covered-call, or risk-review candidates,
   - quality watchlist names for starter/CSP or pullback-entry candidates.
5. Writes:
   - `outputs/trade-idea-generator-{DATE}.md`
   - `outputs/trade-idea-generator-{DATE}-telegram.txt`
6. Sends the Telegram-ready digest when `--send-telegram` is supplied.

## Environment

- `TELEGRAM_BOT_TOKEN` is required for Telegram delivery.
- `TELEGRAM_CHAT_ID` is optional; the script defaults to the existing market-commenter chat ID used by the workspace if unset.
- `FMP_API_KEY` is optional; the script falls back to the workspace FMP key already used by other scripts.

## Usage

Generate files only:

```bash
python scripts/trade_idea_generator.py
```

Generate files and send to Telegram:

```bash
python scripts/trade_idea_generator.py --send-telegram
```

Send to an explicit channel/chat:

```bash
python scripts/trade_idea_generator.py --send-telegram --chat-id "$TELEGRAM_CHAT_ID"
```

## Output Standard

Telegram output should be concise and actionable:

- Top 6 ideas only.
- Each idea includes ticker, action, score, rationale, and details.
- Include data notes when stale option positions are excluded.
- Always include the financial-advice disclaimer.
