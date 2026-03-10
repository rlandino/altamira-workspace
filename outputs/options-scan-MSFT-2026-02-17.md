# Options Scan: Microsoft Corporation (MSFT)

**Date:** 2026-02-17
**Analyst:** Altamira Capital (Automated via /options-scan)
**Data Source:** FMP API (quotes, technicals, earnings) | Options chain: Unavailable via FMP — use Massive.com OPRA feed or E-Trade chain

---

## Data Source Note

FMP API `/options-chain/MSFT` returned empty. Options chain data requires Massive.com (OPRA feed) or E-Trade API. This scan provides market context, technical setup, and strategy parameters for manual chain lookup.

---

## 1. Market Context

| Field | Value |
|-------|-------|
| Current Price | $396.86 |
| 52-Week High | $555.45 |
| 52-Week Low | $344.79 |
| Distance from High | -28.6% |
| Distance from Low | +15.1% |
| 50-Day MA | $460.94 |
| 200-Day MA | $487.38 |
| Price vs 50-Day | -13.9% (below) |
| Price vs 200-Day | -18.6% (below) |
| VIX Level | 20.29 |
| VIX Regime | **Elevated** (15-25 range) |
| Next Earnings | **2026-04-29** (71 days out) |
| Last Earnings | 2026-01-28: Beat ($4.14 vs $3.91 est, +5.9%) |

### Technical Setup (30-Day)

**Price action (last 10 sessions):**

| Date | Close | Change |
|------|-------|--------|
| Feb 17 | $396.86 | -1.1% |
| Feb 13 | $401.32 | -0.8% |
| Feb 12 | $401.84 | -0.8% |
| Feb 11 | $404.37 | -2.8% |
| Feb 10 | $413.27 | -1.5% |
| Feb 09 | $413.60 | +2.2% |
| Feb 06 | $401.14 | +0.5% |
| Feb 05 | $393.67 | -3.4% |
| Feb 04 | $411.00* | — |

**30-Day range:** ~$393 - $432
**Recent support:** $393-$395 (tested Feb 5-6, held)
**Recent resistance:** $413-$416

**Technical bias:** Bearish — price below both 50-day and 200-day MAs, downtrending from $432 on Jan 24. Approaching support near $393. RSI likely in 35-40 range (oversold-ish, not extreme).

**Assessment for options:** Elevated implied volatility expected given the pullback and VIX at 20.29. This is **favorable for premium selling** — puts are priced higher than normal.

---

## 2. Earnings Proximity

| Field | Value |
|-------|-------|
| Next report | 2026-04-29 (after market close) |
| Days until earnings | ~71 days |
| Recent beat streak | 4 consecutive beats (last 4 quarters) |
| Last beat magnitude | +5.9% EPS vs estimate |

**Earnings impact on options strategy:**
- 71 days out = safe to sell 30-45 DTE options without earnings risk
- Target expirations: **Mar 20 (31 DTE)** or **Apr 3 (45 DTE)** — both well before earnings
- Avoid Apr 17+ expirations (would include earnings event)

---

## 3. VIX-Adjusted Sizing

| VIX Level | Regime | Sizing Adjustment |
|-----------|--------|-------------------|
| **20.29** | **Elevated (15-25)** | **Standard size** — premium selling attractive |

Per thesis: VIX 15-25 = normal regime, standard position sizing. Premium selling is more attractive with elevated vol. No sizing reduction needed.

---

## 4. Strategy Recommendations

### Strategy 1: Cash-Secured Put (CSP)

**Rationale:** Stock in pullback, trading near support, elevated vol = rich put premiums. Assignment at these levels creates a favorable cost basis.

**Target parameters:**

| Parameter | Value | Notes |
|-----------|-------|-------|
| Expiration | Mar 20, 2026 (31 DTE) | Sweet spot theta decay |
| Delta target | 0.20-0.25 | ~75-80% probability of profit |
| Strike range | $370 - $380 | ~5-7% below current price |
| Estimated premium | $3.00 - $5.00* | Based on typical IV at this VIX level |
| Breakeven | ~$366 - $377 | Near 52-week low support |
| Max loss | ~$37,000 - $38,000 per contract | If stock goes to $0 (theoretical) |
| Annualized return | ~10-16%* on capital at risk |

*Premium estimates based on typical pricing — verify with live chain.*

**Assignment scenario:** If assigned at $375, cost basis ~$371 (strike - premium). That's within 8% of the 52-week low of $344.79, representing strong fundamental value for a $2.9T company with 36% net margins.

**Position sizing (5% of $100K portfolio):**
- Max capital: $5,000
- At $375 strike: 1 contract ($37,500 cash secured) — exceeds 5% limit
- **Adjust:** Use bull put spread instead for defined risk within sizing limits

### Strategy 2: Bull Put Spread (Defined Risk)

**Rationale:** Same directional thesis as CSP but with defined risk that fits position sizing rules.

**Target parameters:**

| Parameter | Value |
|-----------|-------|
| Expiration | Mar 20, 2026 (31 DTE) |
| Sell put strike | $375 (0.20-0.25 delta) |
| Buy put strike | $365 ($10 wide) |
| Estimated net credit | $1.50 - $2.50* |
| Max loss | $10.00 - credit = $7.50 - $8.50 per spread |
| Max profit | $1.50 - $2.50 (credit received) |
| Breakeven | $372.50 - $373.50 |
| Probability of profit | ~75-80% |
| Risk/Reward | ~1:3 to 1:5 |

**Position sizing (5% of $100K = $5,000 max risk):**
- Max risk per spread: ~$800
- **Contracts: 6 spreads** ($4,800 max risk) — within 5% limit
- Max profit: 6 x $200 = $1,200

### Strategy 3: Jade Lizard (If IV Elevated)

**Rationale:** VIX at 20.29 and stock in pullback suggests elevated IV. Jade lizard collects premium from both sides with no upside risk.

**Target parameters:**

| Parameter | Value |
|-----------|-------|
| Expiration | Mar 20, 2026 (31 DTE) |
| Short put | $375 (0.20-0.25 delta) |
| Short call | $430 (above resistance) |
| Long call | $440 ($10 wide call spread) |
| Total credit target | > $10.00 (must exceed call spread width) |
| Max risk | Downside only: $375 - total credit |
| Upside risk | **Zero** if credit > call spread width |

**Note:** Verify that total collected premium exceeds $10.00 (the call spread width) before entering. This is achievable with elevated IV but must be confirmed on the live chain.

### Strategy 4: Covered Call (If Holding Shares)

**Target parameters (if already long MSFT):**

| Parameter | Value |
|-----------|-------|
| Expiration | Mar 20, 2026 (31 DTE) |
| Delta target | 0.25-0.30 |
| Strike range | $420 - $430 |
| Estimated premium | $3.00 - $5.00* |
| Upside cap | $420 - $430 (6-8% above current) |
| If-called return | ~8-12% (appreciation + premium) |

---

## 5. Risk Flags

| Flag | Status | Action |
|------|--------|--------|
| Earnings within DTE | No (71 days out) | Safe for 30-45 DTE |
| VIX > 25 | No (20.29) | Standard sizing |
| Price below 200-day MA | **Yes** (-18.6%) | Trend is bearish; favor put selling over directional longs |
| 52-week low proximity | Moderate (+15%) | Support at $345 provides floor |
| Liquidity | Excellent | MSFT has one of the most liquid options chains |
| Sector concentration | Check portfolio | Don't stack MSFT puts with other tech puts |

---

## 6. Action

**CONSIDER ENTRY** — Bull put spread ($375/$365, Mar 20 expiration)

**Rationale:**
- Stock near 30-day support ($393), 29% below highs
- VIX at 20.29 = elevated premiums for selling
- Earnings 71 days away — safe window
- 4 consecutive earnings beats
- Defined risk fits 5% position sizing limit
- Strong fundamental backing (see analysis-MSFT-2026-02-17.md)

**Next steps:**
1. Pull live options chain from E-Trade or Massive.com
2. Verify premium on $375/$365 bull put spread, Mar 20
3. Confirm total portfolio tech sector exposure < 25%
4. Enter position if premium meets return threshold

---

*Report generated by Altamira Capital /options-scan command. Premium estimates marked with * require live chain verification.*
