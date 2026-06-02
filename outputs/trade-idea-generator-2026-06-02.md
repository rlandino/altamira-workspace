# Trade Idea Generator - 2026-06-02

**Generated:** 2026-06-02T10:04:52+00:00

## Market and Portfolio Context

- Portfolio market value: **$1,207,271**
- Holdings parsed: **20**
- Watchlist names parsed: **26**
- FMP quotes received: **46** (missing: none)
- VIX: **16.1 (NORMAL)**; sizing multiplier: **100%**
- Symbols option-scanned: **25** (LRCX, NVDA, KLAC, GOOGL, LLY, SPY, AMAT, AMZN, MSFT, AAPL, QQQ, ABBV, CDNS, ANET, V, CRM, GD, WM, COST, MELI, NOW, SPGI, INTU, META, MA)
- Open short-put tickers: **AVGO, COST, MSFT, SPY**

## Selected Trade Ideas

### 1. Covered call: MSFT 495C 2026-06-26

- Ticker: **MSFT**
- Strike / expiration / DTE: **495 / 2026-06-26 / 24**
- Bid / ask / mid: **$5.90 / $6.10 / $6.00**
- Delta / IV / OI / volume: **0.217 / 43.1% / 20,100 / 606**
- Contracts / premium / collateral: **1 / $590.00 / $0.00**
- Breakeven: **n/a**
- Score: **87.6/100**
- Annualized premium return: **19.5%**
- Rationale: Monetize 6.7% existing position; strike is 7.5% above spot; premium yield annualizes at 19.5%.
- Risk: Shares can be called away above strike; avoid if unwilling to trim the position.
- Management: Close at $2.95 debit (50% profit); roll if delta rises above 0.45 and thesis remains intact.
- Data source: Massive option snapshot + FMP quote/context

### 2. Cash-secured put: LRCX 280P 2026-07-17

- Ticker: **LRCX**
- Strike / expiration / DTE: **280 / 2026-07-17 / 45**
- Bid / ask / mid: **$12.15 / $13.30 / $12.73**
- Delta / IV / OI / volume: **-0.249 / 66.5% / 738 / 160**
- Contracts / premium / collateral: **2 / $2,430 / $56,000**
- Breakeven: **$267.85**
- Score: **86.9/100**
- Annualized premium return: **35.2%**
- Rationale: 11.7% OTM put; 35.2% annualized premium yield; watchlist status: Top Candidate
- Risk: Assignment risk; avoid if earnings date moves into holding window.
- Management: Close at $6.08 debit (50% profit); stop/roll near $24.30 debit or short-strike breach.
- Data source: Massive option snapshot + FMP quote/context

### 3. Cash-secured put: NOW 120P 2026-07-17

- Ticker: **NOW**
- Strike / expiration / DTE: **120 / 2026-07-17 / 45**
- Bid / ask / mid: **$5.80 / $6.10 / $5.95**
- Delta / IV / OI / volume: **-0.308 / 59.0% / 9,594 / 8,569**
- Contracts / premium / collateral: **5 / $2,900 / $60,000**
- Breakeven: **$114.20**
- Score: **86.5/100**
- Annualized premium return: **39.2%**
- Rationale: 11.7% OTM put; 39.2% annualized premium yield; current holding weight 0.5%
- Risk: Assignment risk; avoid if earnings date moves into holding window.
- Management: Close at $2.90 debit (50% profit); stop/roll near $11.60 debit or short-strike breach.
- Data source: Massive option snapshot + FMP quote/context

### 4. Covered call: AMZN 280C 2026-07-17

- Ticker: **AMZN**
- Strike / expiration / DTE: **280 / 2026-07-17 / 45**
- Bid / ask / mid: **$5.60 / $5.70 / $5.65**
- Delta / IV / OI / volume: **0.290 / 36.1% / 9,813 / 33,033**
- Contracts / premium / collateral: **2 / $1,120 / $0.00**
- Breakeven: **n/a**
- Score: **82.6/100**
- Annualized premium return: **17.4%**
- Rationale: Monetize 4.9% existing position; strike is 7.2% above spot; premium yield annualizes at 17.4%.
- Risk: Shares can be called away above strike; avoid if unwilling to trim the position.
- Management: Close at $2.80 debit (50% profit); roll if delta rises above 0.45 and thesis remains intact.
- Data source: Massive option snapshot + FMP quote/context

### 5. Cash-secured put: AMAT 420P 2026-07-17

- Ticker: **AMAT**
- Strike / expiration / DTE: **420 / 2026-07-17 / 45**
- Bid / ask / mid: **$19.50 / $21.15 / $20.32**
- Delta / IV / OI / volume: **-0.290 / 61.0% / 250 / 101**
- Contracts / premium / collateral: **1 / $1,950 / $42,000**
- Breakeven: **$400.50**
- Score: **81.1/100**
- Annualized premium return: **37.7%**
- Rationale: 8.3% OTM put; 37.7% annualized premium yield; current holding weight 12.6%
- Risk: Assignment risk; avoid if earnings date moves into holding window.
- Management: Close at $9.75 debit (50% profit); stop/roll near $39.00 debit or short-strike breach.
- Data source: Massive option snapshot + FMP quote/context

## Risk Summary

- New CSP collateral if all selected ideas are opened: **$158,000 (13.1% of portfolio)**.
- Bid premium if all selected ideas are opened: **$8,990**.
- Earnings exclusions inside 45 days: **ABT, ACN, ADBE, ASML, AVGO, CRWD, JPM, KMI, NFLX, PANW, TSM**.
- Missing quote symbols: **none**.

## Telegram Delivery

- Telegram API response: **ok=true**
- Message ID: **1158**
- Chat ID: **7830722515** (private)
- Response artifact: `outputs/trade-idea-generator-2026-06-02-telegram-response.json`

### Message Body

```text
Altamira Trade Idea Generator - 2026-06-02
Universe: 20 holdings + 26 watchlist names | VIX 16.1 (NORMAL) | sizing 100%
Portfolio context: $1,207,271 market value; open short puts: AVGO, COST, MSFT, SPY

Top trade ideas:
1) Covered call: MSFT 495C 2026-06-26 (24 DTE)
   Credit $5.90 bid / $6.10 ask | delta 0.22 | IV 43.1% | OI 20,100 | vol 606
   1 contract(s), premium $590.00, covered by shares
   Score 87.6/100 | annualized premium 19.5%
   Why: Monetize 6.7% existing position; strike is 7.5% above spot; premium yield annualizes at 19.5%.
   Manage: Close at $2.95 debit (50% profit); roll if delta rises above 0.45 and thesis remains intact.
2) Cash-secured put: LRCX 280P 2026-07-17 (45 DTE)
   Credit $12.15 bid / $13.30 ask | delta -0.25 | IV 66.5% | OI 738 | vol 160
   2 contract(s), premium $2,430, collateral $56,000 | BE $267.85
   Score 86.9/100 | annualized premium 35.2%
   Why: 11.7% OTM put; 35.2% annualized premium yield; watchlist status: Top Candidate
   Manage: Close at $6.08 debit (50% profit); stop/roll near $24.30 debit or short-strike breach.
3) Cash-secured put: NOW 120P 2026-07-17 (45 DTE)
   Credit $5.80 bid / $6.10 ask | delta -0.31 | IV 59.0% | OI 9,594 | vol 8,569
   5 contract(s), premium $2,900, collateral $60,000 | BE $114.20
   Score 86.5/100 | annualized premium 39.2%
   Why: 11.7% OTM put; 39.2% annualized premium yield; current holding weight 0.5%
   Manage: Close at $2.90 debit (50% profit); stop/roll near $11.60 debit or short-strike breach.
4) Covered call: AMZN 280C 2026-07-17 (45 DTE)
   Credit $5.60 bid / $5.70 ask | delta 0.29 | IV 36.1% | OI 9,813 | vol 33,033
   2 contract(s), premium $1,120, covered by shares
   Score 82.6/100 | annualized premium 17.4%
   Why: Monetize 4.9% existing position; strike is 7.2% above spot; premium yield annualizes at 17.4%.
   Manage: Close at $2.80 debit (50% profit); roll if delta rises above 0.45 and thesis remains intact.
5) Cash-secured put: AMAT 420P 2026-07-17 (45 DTE)
   Credit $19.50 bid / $21.15 ask | delta -0.29 | IV 61.0% | OI 250 | vol 101
   1 contract(s), premium $1,950, collateral $42,000 | BE $400.50
   Score 81.1/100 | annualized premium 37.7%
   Why: 8.3% OTM put; 37.7% annualized premium yield; current holding weight 12.6%
   Manage: Close at $9.75 debit (50% profit); stop/roll near $39.00 debit or short-strike breach.

Risk summary:
- New CSP collateral if all selected: $158,000 (13.1% of portfolio; limit 30%).
- Premium at bid if all selected: $8,990.
- Earnings exclusions inside 45 days: ABT, ACN, ADBE, ASML, AVGO, CRWD, JPM, KMI, NFLX, PANW, TSM
- Check existing short-put tickers before adding duplicate downside exposure.

Educational only - not financial advice. Verify live bid/ask, earnings, liquidity, and portfolio limits before trading.
```

## Disclaimer

This output is for education and workflow automation only. It is not financial advice or a recommendation to buy, sell, or hold securities or derivatives. Verify live bid/ask, liquidity, earnings dates, tax impact, and portfolio risk limits before placing any trade.
