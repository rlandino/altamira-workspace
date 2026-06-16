# /trade-idea-generator — Portfolio + Watchlist Trade Ideas

Generate a daily trade-idea report from the existing portfolio and watchlist, then optionally send the concise summary to Telegram.

## Usage

```bash
python3 scripts/trade_idea_generator.py --send-telegram
```

Optional arguments:

- `--no-telegram` — write the report only
- `--chat-id CHAT_ID` — override `TELEGRAM_CHAT_ID`
- `--max-tickers N` — cap the portfolio/watchlist universe evaluated
- `--max-ideas N` — cap the number of ideas in the report and Telegram summary
- `--out outputs/custom-report.md` — override the output path

## Inputs

- `context/portfolio-details.md` — current holdings, weights, gains/losses
- `context/options-positions.md` — open short-premium positions to avoid stacking risk
- `context/watchlist.md` — watchlist candidates and scores
- FMP quote/history/earnings data via `FMP_API_KEY` (environment preferred; local workspace legacy constants are used only as a fallback)
- Massive.com option snapshots via `MASSIVE_API_KEY` (environment preferred; local workspace legacy constants are used only as a fallback)
- Telegram via `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`; if `TELEGRAM_CHAT_ID` is missing, the script falls back to the fixed CSP scan target in `outputs/csp-daily-scan-fixed.json`

## Output

Writes:

```text
outputs/trade-idea-generator-{DATE}.md
```

The report includes:

1. Market regime and VIX sizing guidance
2. Top portfolio/watchlist trade ideas
3. Option contract candidates where liquid chain data is available
4. Portfolio concentration context
5. Watchlist and earnings-window filters
6. Short-premium management notes
7. Financial disclaimer

## Method

The generator scores candidates using:

- Trend: price vs 50-day and 200-day moving averages
- Momentum: RSI and 20-day return
- Watchlist score/status
- Portfolio concentration and existing short-premium exposure
- Earnings dates inside the 45-day option window
- Basic option liquidity filters for 25-60 DTE, roughly 0.20-0.30 delta contracts

Strategy selection favors:

- Covered calls for concentrated or extended existing holdings
- Bull put spreads for technology/index exposure or higher-volatility regimes
- Cash-secured puts for lower-concentration quality entries when assignment risk is acceptable
- "Manage existing premium" notes when a ticker already has open short-premium exposure

## Risk Rules

- Keep trade sizing within Altamira risk limits
- Avoid fresh short-premium exposure through unplanned earnings
- Close short premium near 50% profit; stop/adjust near 200% of credit
- Use defined-risk spreads when VIX is elevated/crisis or portfolio concentration is high
- Always review before trading; this is not financial advice
