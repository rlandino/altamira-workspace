# Options Scan: COST (Costco Wholesale Corporation)
**Generated:** February 20, 2026  
**Altamira Capital — Quantitative Options Analysis**  
**Data Source:** Massive.com Options API (Real-time)

---

## ⚠️ CRITICAL ALERT: EARNINGS IMMINENT

| Event | Date | Days Away |
|-------|------|-----------|
| **Q2 FY2026 Earnings** | March 5, 2026 | **13 days** |
| EPS Estimate | $4.53 | — |
| Time | After Market Close (AMC) | — |

Per Altamira thesis: **Never hold positions through unplanned earnings.** Standard 30-45 DTE expirations span earnings.

---

## 1. Market Context

| Metric | Value | Analysis |
|--------|-------|----------|
| **Current Price** | $984.91 | +6.7% above 50-SMA |
| **Day Change** | -$2.91 (-0.29%) | Minor pullback |
| **52-Week High** | $1,071.00 | -8.0% from high |
| **52-Week Low** | $844.06 | +16.7% from low |
| **50-Day SMA** | $923.22 | Price ABOVE ✅ |
| **200-Day SMA** | $951.92 | Price ABOVE ✅ |
| **VIX** | 18.97 | Normal regime |

**Technical Bias:** 📈 **BULLISH** — Above all major SMAs, RSI ~58 (healthy)

---

## 2. VIX Regime

| Level | Regime | Position Sizing |
|-------|--------|-----------------|
| **18.97** | NORMAL | **100%** |

---

## 3. Options Chain Analysis

### Expirations Evaluated

| Expiration | DTE | Status | Earnings Impact |
|------------|-----|--------|-----------------|
| Mar 20, 2026 | 28 | ⚠️ Post-earnings | Holds through Mar 5 |
| Mar 27, 2026 | 35 | ⚠️ Post-earnings | Holds through Mar 5 |
| Apr 17, 2026 | 56 | ✅ Best for post-earnings entry | Enter after Mar 5 |

---

## 4. Top CSP Candidates (0.20-0.30 Delta Range)

### 🥇 RECOMMENDED: April 17, 2026 Expiration (56 DTE)
*Use for post-earnings entry on March 6+*

| Strike | Bid | Ask | Mid | Delta | Theta | IV | OI | Liquidity |
|--------|-----|-----|-----|-------|-------|-----|-----|-----------|
| **$920** | $12.85 | $13.90 | $13.38 | -0.221 | -$0.25 | 25.9% | 326 | ✅ Good |
| **$925** | $13.85 | $14.75 | $14.30 | -0.234 | -$0.25 | 25.5% | 193 | ✅ Good |
| **$930** | $15.15 | $15.95 | $15.55 | -0.251 | -$0.26 | 25.3% | 220 | ✅ Good |
| **$935** | $16.40 | $17.30 | $16.85 | -0.268 | -$0.27 | 25.2% | 91 | ⚠️ Moderate |
| **$940** | $17.70 | $18.75 | $18.22 | -0.285 | -$0.27 | 25.1% | 170 | ✅ Good |

### March 20, 2026 Expiration (28 DTE)
*⚠️ SPANS EARNINGS — Not recommended per thesis*

| Strike | Bid | Ask | Delta | IV | OI | Note |
|--------|-----|-----|-------|-----|-----|------|
| $930 | $8.85 | — | -0.206 | 27.8% | 424 | ❌ Earnings risk |
| $940 | $11.10 | — | -0.246 | 27.1% | 484 | ❌ Earnings risk |
| $950 | $13.75 | — | -0.292 | 26.9% | 1,390 | ❌ Earnings risk |

---

## 5. Strategy Recommendations

### 🏆 PRIMARY RECOMMENDATION: Post-Earnings CSP

**Entry:** March 6, 2026 (day after earnings)  
**Contract:** COST April 17 $920 Put  
**Target Credit:** ~$12.00-13.00 (may change post-earnings)

| Metric | Value | Calculation |
|--------|-------|-------------|
| Strike | $920 | 6.6% below current price |
| Delta | -0.221 | ~78% probability of profit |
| Premium (Bid) | $12.85 | Per contract |
| Breakeven | $907.15 | Strike - Premium |
| Max Loss | $90,715 | If assigned at $0 (theoretical) |
| Collateral | $92,000 | Per contract |
| Return on Capital | 14.0% | $12.85 / $920 |
| Annualized Return | **90.9%** | 14.0% × (365/56) |
| Theta Decay | $0.25/day | Time decay working for you |

**Assignment Scenario:**  
If assigned at $920, your cost basis is **$907.15** — a 7.9% discount to current price and below the 50-day SMA ($923). This would be an attractive entry for a high-quality defensive stock.

### Alternative: Bull Put Spread (Defined Risk)

For capital efficiency, consider a spread:

| Leg | Strike | Action | Credit/Debit |
|-----|--------|--------|--------------|
| Short Put | $920 | SELL | +$12.85 |
| Long Put | $870 | BUY | -$3.00 (est.) |
| **Net Credit** | — | — | **~$9.85** |

| Metric | Value |
|--------|-------|
| Spread Width | $50 |
| Max Profit | $985 per spread |
| Max Loss | $4,015 per spread |
| Collateral Required | $5,000 per spread |
| Return on Risk | **24.5%** |
| Breakeven | $910.15 |

---

## 6. Position Sizing ($100K Portfolio)

### CSP Position
| Constraint | Calculation | Result |
|------------|-------------|--------|
| Max Position (5%) | $100,000 × 5% | $5,000 max risk |
| CSP Collateral | $92,000/contract | ❌ Exceeds limit |
| **Recommendation** | Use Bull Put Spread | ✅ |

### Bull Put Spread Position
| Constraint | Calculation | Result |
|------------|-------------|--------|
| Max Position (5%) | $100,000 × 5% | $5,000 max risk |
| Spread Max Loss | $4,015/spread | ✅ Within limit |
| **Contracts** | 1 spread | ✅ Appropriate |
| Total Collateral | $5,000 | 5% of portfolio |

---

## 7. Risk Assessment

### Liquidity Scores

| Contract | Volume | OI | Spread % | Score |
|----------|--------|-----|----------|-------|
| Apr $920 P | Active | 326 | 7.8% | 8/10 ✅ |
| Apr $925 P | Active | 193 | 6.3% | 8/10 ✅ |
| Apr $930 P | Active | 220 | 5.1% | 9/10 ✅ |

### Risk Flags

| Risk | Status | Mitigation |
|------|--------|------------|
| Earnings (Mar 5) | ⚠️ Within DTE | Wait until Mar 6 to enter |
| High Share Price | ⚠️ CSP >$90K collateral | Use spread structure |
| VIX Level | ✅ Normal (18.97) | Full sizing appropriate |
| Technical Trend | ✅ Bullish | Supports put selling |
| IV Level | ✅ ~25-26% | Acceptable premium |

---

## 8. Action Plan

### 🟢 CONSIDER ENTRY — Post-Earnings

**Wait for earnings (March 5), then:**

1. **On March 6:** Check post-earnings price action and IV levels
2. **If IV remains elevated:** Enter bull put spread on Apr 17 expiration
3. **Primary Trade:** Sell $920P / Buy $870P for ~$9-10 credit
4. **Alternative:** If comfortable with full collateral, sell $920 CSP naked

**Trade Management:**
- Close at 50% profit (~$5.00 credit captured)
- Stop loss at 200% of credit received (~$20.00)
- Monitor for any unexpected news

### Pre-Earnings Alternative (Higher Risk)

If you want exposure before earnings:
- Check Feb 28 weekly options (8 DTE, expires before earnings)
- Much lower premium but avoids earnings event
- NOT recommended per standard thesis

---

## 9. Appendix: Greeks Summary

### April 17 $920 Put Greeks

| Greek | Value | Interpretation |
|-------|-------|----------------|
| Delta | -0.221 | ~22% chance of being ITM at expiration |
| Theta | -$0.25 | You earn $25/day in time decay |
| Gamma | ~0.003 | Delta changes slowly |
| Vega | ~1.5 | Each 1% IV change = ~$1.50 premium change |
| IV | 25.9% | Moderate volatility priced in |

### Theta/Delta Ratio (Premium Efficiency)

| Strike | Theta | Delta | Theta/Delta | Efficiency |
|--------|-------|-------|-------------|------------|
| $915 | $0.21 | 0.209 | 1.00 | Good |
| $920 | $0.25 | 0.221 | 1.13 | ✅ Best |
| $925 | $0.25 | 0.234 | 1.07 | Good |
| $930 | $0.26 | 0.251 | 1.04 | Good |

The $920 strike offers the best theta decay per unit of delta risk.

---

*Report generated by Altamira Capital Options Scanner*  
*Data: Massive.com Options API (Real-time)*  
*Market Data: Financial Modeling Prep API*
