# Trade Idea Generator - 2026-06-18

Generated from the current repository portfolio and watchlist using FMP quotes and Massive options snapshots.

## Scan Context

- Run time: 2026-06-18 06:05 EDT
- Portfolio holdings scanned: 19
- Watchlist tickers scanned: 26
- Quotes returned: 45 of 45 symbols
- Options contracts reviewed: 522 puts, 644 calls
- VIX regime: 17.01 (NORMAL), sizing multiplier 100%
- Earnings exclusions inside 2026-07-18 to 2026-08-17: AAPL, ABBV, ABT, ACN, AMAT, AMZN, ANET, ASML, CDNS, CMG, FICO, GD, GOOGL, ISRG, JPM, KLAC, KMI, LLY, LRCX, MA, MELI, META, MSCI, MSFT, NFLX, NOW, PANW, PLTR, SPGI, TMO, TSLA, TSM, V, WM

## Top Ideas

| Rank | Strategy | Ticker | Contract | Credit | Delta | Ann. Yield | Score | Rationale |
|---:|---|---|---|---:|---:|---:|---:|---|
| 1 | Cash-secured put | NVDA | 2026-07-24 195.00 P | $5.10 | -0.29 | 26.5% | 66.0 | Top/quality watchlist or underweight holding; no earnings found inside scan window. |
| 2 | Cash-secured put | ADBE | 2026-07-24 185.00 P | $4.35 | -0.28 | 23.8% | 53.0 | Top/quality watchlist or underweight holding; no earnings found inside scan window. |
| 3 | Cash-secured put | CRWD | 2026-07-24 610.00 P | $13.45 | -0.21 | 22.4% | 52.8 | Top/quality watchlist or underweight holding; no earnings found inside scan window. |
| 4 | Covered call | AVGO | 2026-07-24 440.00 C | $7.80 | 0.28 | 18.0% | 48.8 | Existing holding (16.7% weight, 606 shares); harvest premium against inventory. |
| 5 | Covered call | GOOGL | 2026-07-31 395.00 C | $7.75 | 0.30 | 16.7% | 48.7 | Existing holding (13.8% weight, 551 shares); harvest premium against inventory. |

## Detail

### 1. NVDA - Cash-secured put

- Trade: STO PUT NVDA 2026-07-24 195.00
- Underlying price: $204.65
- Credit: $5.10 bid / $5.25 ask
- Delta: -0.29; IV: 40.5%
- DTE: 36; OI: 2349; volume: 218
- Breakeven: $189.90; sample contracts: 1; collateral: $19,500
- Management: target 50% profit; stop/adjust if option value reaches ~2x credit or short strike is tested.

### 2. ADBE - Cash-secured put

- Trade: STO PUT ADBE 2026-07-24 185.00
- Underlying price: $196.28
- Credit: $4.35 bid / $5.55 ask
- Delta: -0.28; IV: 41.8%
- DTE: 36; OI: 76; volume: 6
- Breakeven: $180.65; sample contracts: 1; collateral: $18,500
- Management: target 50% profit; stop/adjust if option value reaches ~2x credit or short strike is tested.

### 3. CRWD - Cash-secured put

- Trade: STO PUT CRWD 2026-07-24 610.00
- Underlying price: $682.96
- Credit: $13.45 bid / $16.20 ask
- Delta: -0.21; IV: 52.7%
- DTE: 36; OI: 54; volume: 2
- Breakeven: $596.55; sample contracts: 1; collateral: $61,000
- Management: target 50% profit; stop/adjust if option value reaches ~2x credit or short strike is tested.

### 4. AVGO - Covered call

- Trade: STO CALL AVGO 2026-07-24 440.00
- Underlying price: $392.90
- Credit: $7.80 bid / $9.10 ask
- Delta: 0.28; IV: 39.8%
- DTE: 36; OI: 196; volume: 55
- If-called return through expiration: 14.0%; sample contracts: 3; premium: $2,340
- Management: target 50% profit; stop/adjust if option value reaches ~2x credit or short strike is tested.

### 5. GOOGL - Covered call

- Trade: STO CALL GOOGL 2026-07-31 395.00
- Underlying price: $363.79
- Credit: $7.75 bid / $9.35 ask
- Delta: 0.30; IV: 37.6%
- DTE: 43; OI: 338; volume: 210
- If-called return through expiration: 10.7%; sample contracts: 3; premium: $2,325
- Management: target 50% profit; stop/adjust if option value reaches ~2x credit or short strike is tested.

## Risk Notes

- Verify live bid/ask, open interest, and earnings dates before trading; this is decision support, not financial advice.
- Position sizing should remain inside the portfolio risk framework: max 5% per position, sector caps, and options allocation limits.
- Repository options table contains 5 expired contracts as of today; they were treated as stale context, not active positions.

