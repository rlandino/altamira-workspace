# Trade Idea Generator - Portfolio + Watchlist

**Report date:** 2026-06-25
**Universe:** 20 portfolio symbols + 26 watchlist symbols from repository context files
**Data source:** FMP live quotes/history/earnings; option prices are Black-Scholes model estimates because configured options-chain providers were unavailable during execution.

> Educational analysis only. Not financial advice. Confirm live option chains, liquidity, bid/ask spreads, earnings dates, and account risk before entering any order.

---

## Market / Risk Context

- **VIX:** 19.10 (NORMAL); sizing guide: 100% of normal. Standard premium-selling environment; defined risk still preferred due existing short-put notional.
- **Existing short-put notional:** approximately $1,320,000 (109.3% of $1.207M portfolio value from context).
- **Technology equity weight:** approximately 45.4% (plus index exposure 17.8%).
- **Risk posture:** prioritize covered calls, defined-risk put spreads, and hedges; avoid adding naked CSP exposure until current short-put notional/cash availability is reconciled.

## Top Trade Ideas

### 1. AMAT Covered Call - harvest premium on existing shares
- **Underlying:** AMAT @ $617.68 | portfolio weight 12.6% | RSI 66
- **Model trade:** Sell 2x 35 DTE $745.00 call(s) against existing shares.
- **Estimated credit:** $16.09 per share ($3,217 total). If-called return from spot: 23.2%.
- **Management:** Buy back at 50% of credit; roll/close if underlying gaps through strike or before earnings.

### 2. CRWD Put Credit Spread - defined-risk entry candidate
- **Underlying:** CRWD @ $684.99 | sector Technology.
- **Model trade:** Sell $570.00 put / buy $550.00 put, ~35 DTE.
- **Estimated credit:** $2.67 per share ($267/spread); max loss approximately $1,733; credit/width 13.3%.
- **Management:** Defined risk only; skip if live credit is below one-third of model estimate or bid/ask is wide. Close at 50% profit or 2x credit loss.

### 3. PANW Put Credit Spread - defined-risk entry candidate
- **Underlying:** PANW @ $289.88 | watchlist C- / 47.4 | sector Technology.
- **Model trade:** Sell $242.50 put / buy $235.00 put, ~35 DTE.
- **Estimated credit:** $0.98 per share ($98/spread); max loss approximately $652; credit/width 13.0%.
- **Management:** Defined risk only; skip if live credit is below one-third of model estimate or bid/ask is wide. Close at 50% profit or 2x credit loss.

### 4. QQQ Protective Put Spread - portfolio concentration hedge
- **Underlying:** QQQ @ $711.31; trigger is tech concentration (45.4%) and high short-put notional.
- **Model trade:** Buy $680.00 put / sell $665.00 put, ~35 DTE.
- **Estimated debit:** $3.78 per share ($378/spread); max spread value $1,500.
- **Management:** Use as tactical hedge only while concentration/short-put exposure remains elevated.

## Near-Term Earnings Exclusions

AAPL (2026-07-30), ABBV (2026-07-30), ABT (2026-07-16), AMZN (2026-07-30), ANET (2026-08-04), ASML (2026-07-15), CDNS (2026-07-27), CMG (2026-07-29), FICO (2026-07-29), GD (2026-07-29), GOOGL (2026-07-22), ISRG (2026-07-16), JPM (2026-07-14), KLAC (2026-07-30), KMI (2026-07-15), LLY (2026-08-05), LRCX (2026-07-29), MA (2026-07-30), MELI (2026-08-05), META (2026-07-29), +11 more

## Scanned Universe Snapshot

| Symbol | Source | Price | 50D | 200D | RSI | Watch Grade | Weight | Earnings |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| SPY | Portfolio | $734.22 | $732.97 | $689.72 | 37 |  | 17.1% |  |
| AVGO | Portfolio | $376.23 | $412.64 | $361.01 | 38 |  | 16.7% |  |
| GOOGL | Portfolio | $341.00 | $369.05 | $312.82 | 29 |  | 13.8% | 2026-07-22 |
| AMAT | Portfolio | $617.68 | $458.11 | $324.51 | 66 |  | 12.6% |  |
| MSFT | Portfolio | $358.45 | $412.54 | $449.34 | 16 |  | 6.7% | 2026-07-29 |
| AMZN | Portfolio | $228.63 | $256.89 | $232.84 | 30 |  | 4.9% | 2026-07-30 |
| AAPL | Portfolio | $279.56 | $290.82 | $269.03 | 24 |  | 4.6% | 2026-07-30 |
| CRWD | Portfolio | $684.99 | $582.62 | $493.34 | 40 |  | 4.3% |  |
| COST | Portfolio | $953.27 | $998.26 | $957.95 | 40 |  | 4.1% |  |
| ABBV | Portfolio | $240.82 | $213.23 | $220.88 | 65 |  | 3.8% | 2026-07-30 |
| GD | Portfolio | $351.06 | $341.46 | $344.26 | 54 |  | 2.2% | 2026-07-29 |
| V | Portfolio | $337.09 | $322.34 | $328.80 | 65 |  | 2.2% | 2026-07-28 |
| JPM | Portfolio | $340.27 | $310.17 | $307.61 | 74 |  | 2.1% | 2026-07-14 |
| KMI | Portfolio | $33.01 | $32.10 | $29.86 | 64 |  | 1.8% | 2026-07-15 |
| WM | Portfolio | $225.04 | $220.72 | $221.27 | 57 |  | 0.8% | 2026-07-27 |
| QQQ | Portfolio | $711.31 | $699.66 | $630.84 | 41 |  | 0.7% |  |
| NOW | Portfolio | $91.29 | $99.66 | $135.46 | 16 |  | 0.5% | 2026-07-22 |
| SPGI | Portfolio | $410.51 | $422.72 | $466.83 | 44 |  | 0.5% | 2026-07-30 |
| NFLX | Portfolio | $72.77 | $87.41 | $97.57 | 24 |  | 0.0% | 2026-07-16 |
| ABT | Watch | $93.77 | $89.43 | $112.99 | 57 | D | 0.0% | 2026-07-16 |
| ACN | Watch | $128.97 | $174.27 | $224.20 | 11 | C+ | 0.0% |  |
| ADBE | Watch | $197.07 | $239.53 | $293.03 | 8 | B- | 0.0% |  |
| ADSK | Watch | $192.77 | $230.49 | $267.80 | 15 | D+ | 0.0% |  |
| ANET | Watch | $161.94 | $159.60 | $142.55 | 45 | C- | 0.0% | 2026-08-04 |
| ASML | Watch | $1,793.23 | $1,600.86 | $1,283.61 | 52 | C+ | 0.0% | 2026-07-15 |
| CDNS | Watch | $370.61 | $359.83 | $326.79 | 30 | C- | 0.0% | 2026-07-27 |
| CMG | Watch | $31.95 | $32.47 | $35.67 | 69 | F | 0.0% | 2026-07-29 |
| CRM | Watch | $152.38 | $177.06 | $214.90 | 8 | C | 0.0% |  |
| FICO | Watch | $1,157.14 | $1,126.72 | $1,423.56 | 48 | D+ | 0.0% | 2026-07-29 |
| INTU | Watch | $259.99 | $347.98 | $517.16 | 23 | - | 0.0% |  |
| ISRG | Watch | $411.98 | $436.60 | $489.92 | 39 | D+ | 0.0% | 2026-07-16 |
| KLAC | Watch | $246.47 | $198.34 | $146.87 | 59 | B- | 0.0% | 2026-07-30 |
| LLY | Watch | $1,122.35 | $1,021.13 | $971.68 | 48 | C+ | 0.0% | 2026-08-05 |
| LRCX | Watch | $375.25 | $305.48 | $214.34 | 58 | B | 0.0% | 2026-07-29 |
| MA | Watch | $500.79 | $498.01 | $533.28 | 60 | C- | 0.0% | 2026-07-30 |
| MELI | Watch | $1,649.67 | $1,702.88 | $1,962.10 | 50 | C- | 0.0% | 2026-08-05 |
| META | Watch | $549.91 | $617.72 | $652.14 | 26 | C- | 0.0% | 2026-07-29 |
| MRVL | Watch | $269.48 | $207.62 | $116.43 | 41 | D | 0.0% |  |
| MSCI | Watch | $577.21 | $591.79 | $569.67 | 26 | D+ | 0.0% | 2026-07-21 |
| NVDA | Watch | $194.59 | $210.23 | $190.39 | 31 | B | 0.0% |  |
| PANW | Watch | $289.88 | $232.13 | $197.56 | 57 | C- | 0.0% |  |
| PLTR | Watch | $107.98 | $137.61 | $159.34 | 17 | D | 0.0% | 2026-08-03 |
| TMO | Watch | $512.92 | $475.17 | $525.61 | 60 | D | 0.0% | 2026-07-22 |
| TSLA | Watch | $375.97 | $404.79 | $417.66 | 36 | F | 0.0% | 2026-07-22 |
| TSM | Watch | $438.88 | $410.40 | $338.32 | 47 | B- | 0.0% | 2026-07-16 |

---

**Execution note:** Massive options snapshot returned unauthorized and FMP options-chain returned no contracts in this environment, so live chain confirmation is mandatory before order entry.
