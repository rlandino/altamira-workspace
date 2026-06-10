# /trade-idea-generator - Portfolio and Watchlist Trade Ideas

Generate daily trade ideas from the current repository portfolio and watchlist, write a dated markdown report, and optionally send the concise summary to Telegram.

## Instructions

You are generating practical, risk-aware trade ideas for Altamira Capital. Use the existing portfolio and watchlist files in the repository unless the user provides overrides.

### Step 1: Read portfolio and watchlist context

Primary inputs:

- `context/portfolio-details.md` - current equity positions and open short-premium positions.
- `context/watchlist.md` - scored watchlist candidates and statuses.

The generator parses:

- Current holdings, weights, share counts, and context prices.
- Existing short puts and other short-premium positions.
- Watchlist score, grade, company, and status.

### Step 2: Fetch market context

Run:

```bash
python3 scripts/trade_idea_generator.py
```

If `FMP_API_KEY` is set, the script fetches live quotes, VIX, historical prices for technicals, and the upcoming earnings calendar. If it is not set, it falls back to context-only mode and clearly labels the report.

### Step 3: Generate ideas

The script produces a ranked list using these rules:

- Covered calls for existing holdings with enough shares, high portfolio weight, or extended technicals.
- Cash-secured puts or bull put spreads for watchlist candidates, adjusted by VIX regime.
- Management alerts for existing short puts close to or through the strike.
- Risk flags for earnings, concentration, and already-open short-premium exposure.

Generated strikes are model-based unless a live broker/options chain is checked separately. Confirm actual delta, premium, bid/ask spread, and assignment risk before trading.

### Step 4: Output

The report is written to:

```text
outputs/trade-ideas-YYYY-MM-DD.md
```

It includes:

1. Market regime and VIX note.
2. Top trade ideas table.
3. Rationale for each idea.
4. Portfolio concentration context.
5. Existing short-premium risk table.
6. Watchlist focus table.
7. Risk controls and disclaimer.

### Step 5: Send to Telegram

To send the concise summary:

```bash
python3 scripts/trade_idea_generator.py --send-telegram --telegram-chat-id "$TELEGRAM_CHAT_ID"
```

Requirements:

- `TELEGRAM_BOT_TOKEN` must be set.
- `TELEGRAM_CHAT_ID` or `--telegram-chat-id` must identify the destination channel/chat.

Use `--dry-run --send-telegram` to preview without sending.

## Context

- Altamira Capital's primary options strategy is premium selling with controlled risk.
- Keep single-position risk within the 5% rule and total options allocation within the 30% cap.
- Avoid new short-premium entries through unplanned earnings.
- All output must include the research-only disclaimer and require broker confirmation before execution.
