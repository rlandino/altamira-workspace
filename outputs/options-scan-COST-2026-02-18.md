# Options Scan: Costco Wholesale Corporation (COST)

**Date:** 2026-02-18  
**Analyst:** Altamira Capital (Automated via /options-scan)  
**Data Sources:** FMP API (quotes, technicals, earnings) | Massive.com API (options chain, Greeks, IV)

---

## 1. Market Context

| Field | Value |
|-------|-------|
| Current Price | $998.82 |
| Daily Change | -$13.23 (-1.31%) |
| 52-Week High | $1,071.00 |
| 52-Week Low | $844.06 |
| Distance from High | -6.7% |
| Distance from Low | +18.3% |
| 50-Day MA | $923.22 |
| 200-Day MA | $951.92 |
| Price vs 50-Day | +8.2% (above) |
| Price vs 200-Day | +4.9% (above) |
| VIX Level | 19.44 |
| VIX Regime | **Moderate** (15–25 range) |
| Next Earnings | **2026-03-05** (16 days out) ⚠️ |
| Last Earnings | 2025-12-11: Beat ($4.34 vs $4.27 est) |

### Technical Context (30-day)

- **20-day trend:** Consolidation after pullback from ~$1,018 (Feb 13).
- **Support:** ~$971–978 (tested Feb 10–11).
- **Resistance:** ~$1,022–1,028.
- **Technical bias:** Neutral to slightly bullish (price above 50d/200d MA; earnings nearby).

### Earnings Impact

- **Earnings date:** March 5, 2026 (AMC).
- **Recommendation:** Prefer expirations **after** March 5 (e.g. March 20, April 17) to avoid event risk and capture post–IV crush premium.
- **March 20 expiration:** 31 DTE from scan date, 15 days after earnings — **acceptable** for premium selling.

---

## 2. Options Chain Summary

**Source:** Massive.com API (OPRA).

| Metric | Value |
|--------|--------|
| Expirations analyzed | 2026-03-20, 2026-04-17 |
| Puts in 20–60 DTE | Yes (Mar 20 ≈ 31 DTE, Apr 17 ≈ 59 DTE) |
| Chain filtering | Volume/OI/bid applied; illiquid strikes excluded |
| Underlying (Massive) | $1,000.51 |

**Filtering applied:**
- Expirations 20–60 DTE (focus 30–45 DTE).
- Bid ≥ $0.05; sufficient open interest.
- Delta focus: 0.15–0.35 for premium-selling puts.

---

## 3. Top Recommendations

### 1. Cash-Secured Put (CSP) — Post-Earnings

**Use March 20, 2026 expiration (31 DTE, after earnings).**

| Strike | Delta | Mid (credit) | Breakeven | Max loss (per 100 sh) | Ann. return* |
|--------|--------|--------------|-----------|------------------------|-------------|
| **$940** | 0.20 | **$9.30** | $930.70 | $93,070 | ~11.5% |
| **$950** | 0.24 | **$11.58** | $938.42 | $93,842 | ~14.3% |
| **$960** | 0.28 | **$14.13** | $945.87 | $94,587 | ~17.4% |

*Annualized: (credit / collateral) × (365 / DTE). Collateral = strike × 100.

**Preferred CSP:** **$950 put** — ~0.24 delta, ~$11.58 credit, breakeven $938.42 (~6.0% below spot).  
**Assignment:** If assigned at $950, cost basis = $938.42. About 6.0% below current price and ~11% above 52w low.

---

### 2. Bull Put Spread — Defined Risk

**March 20, 2026 expiration.**

| Short put | Long put | Net credit | Max loss | Breakeven | R:R |
|-----------|----------|------------|----------|-----------|-----|
| **$960** | $950 | **$2.45** | $7.55 | $957.55 | 1 : 3.1 |
| **$965** | $955 | **$2.20** | $7.80 | $962.80 | 1 : 3.5 |
| **$950** | $940 | **$2.88** | $7.12 | $947.12 | 1 : 2.5 |

**Preferred spread:** **$960 / $950** — sell $960 put (~$14.13), buy $950 put (~$11.68); net credit ~**$2.45**; max loss **$7.55**; breakeven **$957.55**.

**Capital per spread:** $1,000 (width × 100). Fits 5% of $100k portfolio (e.g. 5 spreads = $5,000).

---

### 3. Covered Call — If Holding Shares

**March 20, 2026 expiration.**

| Strike | Delta | Mid (premium) | Upside cap | If-called return* |
|--------|--------|---------------|------------|-------------------|
| $1,040 | ~0.20 | ~$15–18 | 4.1% | ~5–6% (cap + premium) |
| $1,050 | ~0.15 | ~$12–14 | 5.1% | ~5–6% |

*If-called return: (strike − current) / current + premium / current (approx).

Use 0.20–0.30 delta calls from the chain for exact strikes and premiums.

---

### 4. Jade Lizard (IV elevated)

**VIX 19.44 — moderate.** IV Rank not in “elevated” regime for this scan; Jade Lizard is **optional**.  
If using: short put (e.g. $950) + short call spread; collect more credit than width of call spread. Re-evaluate when IV Rank > 50%.

---

## 4. Risk Assessment

### Position Sizing (5% rule, $100k portfolio)

- **Max per name:** $5,000.
- **CSP:** 1 contract at $950 = $95,000 collateral → **over** 5% → use **spreads** for sizing.
- **Bull put $960/$950:** 5 spreads = $5,000 at risk → **within** 5%.

### Options Allocation

- Keep total options allocation ≤ 30% of portfolio.
- Check existing book before adding.

### VIX Regime

- **VIX 19.44** — normal sizing (no reduction per thesis).

### Liquidity (Massive.com chain)

- March 20 puts in 940–980 strike: usable bid/ask and OI.
- **Liquidity score:** ~6–7/10 (tight spreads, decent OI).

### Earnings

- **March 5 earnings:** Avoid new **short-dated** positions that expire before or right after earnings.
- **March 20 and April 17 expirations:** After earnings — **OK** for these recommendations.

---

## 5. Risk Flags

| Flag | Severity | Note |
|------|----------|------|
| Earnings in 16 days | Medium | Use March 20+ expirations only. |
| Single-name size | Medium | CSP exceeds 5% rule; use spreads. |
| IV level | Low | IV ~27%; adequate for premium selling, not “elevated.” |

---

## 6. Action Recommendation

### **CONSIDER ENTRY** (post-earnings, defined risk)

**Rationale:**
- Price above key MAs; technicals neutral to slightly bullish.
- March 20 expiration (31 DTE) is **after** March 5 earnings.
- Massive.com chain provides solid put quotes and Greeks.
- Bull put spread fits 5% sizing; CSP does not unless portfolio is larger.

**Suggested action:**
1. **Primary:** After March 5, open **bull put spread $960 / $950** (Mar 20); target net credit ≥ $2.45; size to 5% of portfolio.
2. **Alternative:** If seeking assignment, **CSP $950** (Mar 20) in a size consistent with your capital (e.g. 1 contract per ~$95k allocated).
3. **Avoid:** New short options expiring on or before March 5.

---

**Report generated:** 2026-02-18  
**FMP:** Quote, historical, earnings, VIX, key metrics.  
**Massive.com:** Options chain (puts, March/April expirations), Greeks, IV, quotes.
