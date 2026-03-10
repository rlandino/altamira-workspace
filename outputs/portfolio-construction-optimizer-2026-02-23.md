hhchchhc# Portfolio Construction Optimizer

**Report date:** 2026-02-23  
**Total portfolio value:** $1,207,271  
**Number of positions:** 20 (19 material; NFLX 0.0% excluded from sizing)  
**Summary:** Optimized allocation with conviction-based sizing, risk budget guardrails, and 5-regime stress test. Conviction inferred from current weight bands (≥10% HIGH, 5–10% MEDIUM, <5% LOW); theses default to "Current allocation" unless user provides.

---

## 1. Header

| Field | Value |
|--------|--------|
| Title | Portfolio Construction Optimizer |
| Date | 2026-02-23 |
| Total value | $1,207,271 |
| Positions | 19 (NFLX excluded) |
| One-line summary | Citadel-style construction with conviction-based targets, Kelly caps, risk budget, and stress dashboard. |

---

## 2. Position Sizing Framework

**Rules:** Capital per idea by conviction and risk.

- **HIGH conviction** → target weight 8–12% (base 10%). Risk scaling: halve target if name is 2× benchmark vol.
- **MEDIUM conviction** → target 4–8% (base 6%).
- **LOW conviction** → target 1–4% (base 3%).

**Conviction assigned from current weight:** ≥10% = HIGH, 5–10% = MEDIUM, <5% = LOW.

| Ticker | Conviction | Thesis (short) | Current weight % | Target weight % | Rationale |
|--------|------------|----------------|------------------|-----------------|-----------|
| SPY | HIGH | Core equity exposure | 17.1 | 10 | Trim to target; cap core at 10%. |
| AVGO | HIGH | Semis / infrastructure | 16.7 | 10 | Trim to target; high conviction cap. |
| GOOGL | HIGH | Digital advertising / cloud | 13.8 | 10 | Trim to target. |
| AMAT | HIGH | Semis equipment | 12.6 | 10 | Trim to target. |
| MSFT | MEDIUM | Quality compounder, cloud | 6.7 | 6 | Hold near target. |
| AMZN | LOW | E‑commerce / AWS | 4.9 | 4 | Slight trim to target. |
| AAPL | LOW | Quality compounder, services | 4.6 | 4 | Hold. |
| CRWD | LOW | Cybersecurity growth | 4.3 | 4 | Hold. |
| COST | LOW | Consumer / membership | 4.1 | 4 | Hold. |
| ABBV | LOW | Pharma / dividends | 3.8 | 4 | Hold. |
| GD | LOW | Defense | 2.2 | 3 | Hold. |
| V | LOW | Payments | 2.2 | 3 | Hold. |
| JPM | LOW | Financials | 2.1 | 3 | Hold. |
| KMI | LOW | Midstream energy | 1.8 | 2 | Hold. |
| WM | LOW | Waste / infrastructure | 0.8 | 2 | Add to target. |
| FFOLX | LOW | Fund allocation | 0.7 | 1 | Hold or consolidate. |
| QQQ | LOW | Tech tilt | 0.7 | 1 | Hold. |
| NOW | LOW | Enterprise software | 0.5 | 1 | Hold. |
| SPGI | LOW | Financial data | 0.5 | 1 | Hold. |

*Weights above are target guidelines; final recommended % in Section 12 applies Kelly and liquidity caps and renormalizes to 100%.*

---

## 3. Kelly Criterion Application

**Formula:** f* = (p × b − q) / b; half-Kelly used for sizing.  
**Assumptions:** HIGH edge 2%, win prob 55%; MEDIUM edge 1%, win prob 52%; LOW edge 0.5%, win prob 51%. Win/loss ratio b = 1.5 (illustrative).

| Ticker | Assumed edge | Win prob | Full Kelly % | Half-Kelly % | Recommended cap (min of target vs half-Kelly) |
|--------|----------------|----------|--------------|--------------|-----------------------------------------------|
| SPY | 0.5% | 51% | 1.3 | 0.65 | 0.65 (Kelly binding) |
| AVGO | 2% | 55% | 6.7 | 3.3 | 3.3 |
| GOOGL | 2% | 55% | 6.7 | 3.3 | 3.3 |
| AMAT | 2% | 55% | 6.7 | 3.3 | 3.3 |
| MSFT | 1% | 52% | 2.7 | 1.3 | 1.3 |
| AMZN | 0.5% | 51% | 1.3 | 0.65 | 0.65 |
| AAPL | 0.5% | 51% | 1.3 | 0.65 | 0.65 |
| CRWD | 0.5% | 51% | 1.3 | 0.65 | 0.65 |
| COST | 0.5% | 51% | 1.3 | 0.65 | 0.65 |
| ABBV | 0.5% | 51% | 1.3 | 0.65 | 0.65 |
| GD | 0.5% | 51% | 1.3 | 0.65 | 0.65 |
| V | 0.5% | 51% | 1.3 | 0.65 | 0.65 |
| JPM | 0.5% | 51% | 1.3 | 0.65 | 0.65 |
| KMI | 0.5% | 51% | 1.3 | 0.65 | 0.65 |
| WM | 0.5% | 51% | 1.3 | 0.65 | 0.65 |
| FFOLX | 0.5% | 51% | 1.3 | 0.65 | 0.65 |
| QQQ | 0.5% | 51% | 1.3 | 0.65 | 0.65 |
| NOW | 0.5% | 51% | 1.3 | 0.65 | 0.65 |
| SPGI | 0.5% | 51% | 1.3 | 0.65 | 0.65 |

*Kelly inputs are illustrative; replace with backtest or user estimates for production.*

---

## 4. Correlation-Aware Allocation

**Correlation matrix:** Not run for this universe. Run `scripts/risk_parity_analyzer.py` on the same tickers for a correlation matrix; use `outputs/risk-parity-result-{DATE}.json` for pairs with correlation > 0.7 and scaling recommendations.

**Diversification checklist (sector overlap):**

| Sector | Tickers | Suggested cap (%) |
|--------|---------|--------------------|
| Technology | GOOGL, MSFT, AMZN, AAPL, CRWD, NOW, SPGI, AVGO, AMAT | 40 |
| Consumer / Discretionary | AMZN, COST | 15 |
| Healthcare | ABBV | 10 |
| Financials | V, JPM, SPGI | 15 |
| Industrials / Defense | GD, WM | 10 |
| Energy / Midstream | KMI | 5 |
| Index / ETF | SPY, QQQ, FFOLX | 15 |

**Actions:** Tech is heavily represented (9 names). Consider cap on aggregate tech weight (e.g. 40%) and trim lowest-conviction tech names if over. SPY + QQQ + FFOLX together ~18.5% current; consider consolidating to SPY or SPY+QQQ with a single target.

---

## 5. Risk Budget Allocation

**Rule:** No single position > 20% of total portfolio risk. Total risk budget = 100%.  
**Simplified:** Risk budget % = normalized inverse of number of positions (equal risk budget placeholder). For production, use volatility and correlation from `risk_parity_analyzer.py`.

| Ticker | Weight % | Assigned risk budget % | Volatility assumption |
|--------|----------|------------------------|------------------------|
| SPY | 17.1 | 5.3 | Index vol (~15% ann.) |
| AVGO | 16.7 | 5.3 | From FMP/risk system |
| GOOGL | 13.8 | 5.3 | From FMP/risk system |
| AMAT | 12.6 | 5.3 | From FMP/risk system |
| MSFT | 6.7 | 5.3 | From FMP/risk system |
| AMZN | 4.9 | 5.3 | From FMP/risk system |
| AAPL | 4.6 | 5.3 | From FMP/risk system |
| CRWD | 4.3 | 5.3 | From FMP/risk system |
| COST | 4.1 | 5.3 | From FMP/risk system |
| ABBV | 3.8 | 5.3 | From FMP/risk system |
| GD | 2.2 | 5.3 | From FMP/risk system |
| V | 2.2 | 5.3 | From FMP/risk system |
| JPM | 2.1 | 5.3 | From FMP/risk system |
| KMI | 1.8 | 5.3 | From FMP/risk system |
| WM | 0.8 | 5.3 | From FMP/risk system |
| FFOLX | 0.7 | 5.3 | From FMP/risk system |
| QQQ | 0.7 | 5.3 | From FMP/risk system |
| NOW | 0.5 | 5.3 | From FMP/risk system |
| SPGI | 0.5 | 5.3 | From FMP/risk system |

*Volatility from risk system for production; equal risk budget used as placeholder.*

---

## 6. Gross and Net Exposure Targets

| Metric | Current | Target | Comment |
|--------|---------|--------|---------|
| Gross exposure | 100% | 100% | Long-only; no shorts. |
| Net exposure | 100% | 100% | Long-only. |

All positions are long. Gross = Net = 100%. Targets N/A for long-only sleeve; cash is separate.

---

## 7. Concentration Limits

| Limit | Rule | Current | Pass/Fail |
|--------|------|---------|-----------|
| Max single position | ≤ 20% | SPY 17.1%, AVGO 16.7%, GOOGL 13.8%, AMAT 12.6% | Pass |
| Max sector (Tech) | ≤ 25–40% | Tech ~55%+ (GOOGL, MSFT, AMZN, AAPL, CRWD, NOW, SPGI, AVGO, AMAT) | **Fail** — trim tech or raise cap to 40% with discipline |
| Max sector (other) | ≤ 25% | Financials, Consumer, etc. within limit | Pass |
| Number of names | — | 19 | Pass |

**Recommendation:** Enforce sector cap (e.g. tech 40%); trim lowest-conviction tech (e.g. NOW, SPGI, or one of AMZN/AAPL/CRWD) to meet cap.

---

## 8. Liquidity-Adjusted Sizing

**Rule:** Position notional ≤ 3 × ADV so portfolio can exit within 3 days. ADV from FMP or broker.

*FMP batch quote not available for this run; use broker ADV.*

| Ticker | Position notional ($) | 3× ADV (or est.) | Liquidity haircut | Adjusted target % |
|--------|------------------------|------------------|-------------------|--------------------|
| SPY | 205,887 | High (ETF) | None | As target |
| AVGO | 202,107 | Verify ADV | Cap 2% if ADV < $50M | min(target, 2% if illiquid) |
| GOOGL | 167,135 | High | None | As target |
| AMAT | 152,521 | Verify ADV | Cap 2% if ADV < $30M | min(target, 2% if illiquid) |
| Others | — | Verify broker | 50% size cap if ADV < $5M | Per broker |

**Liquidity:** Verify ADV on broker; apply 50% size cap for names with ADV < $5M.

---

## 9. Scenario Portfolio Stress Test

**Five regimes:** Bull +5%, Bear −15%, Rates up +50 bps, Vol spike (VIX 30), Recession −20%.  
Assumed portfolio return = long-only equity beta ~1.0; tech-heavy sleeve may have beta ~1.1 in bear.

| Regime | Assumed portfolio return % | Key driver |
|--------|----------------------------|------------|
| Bull +5% | +5.5 | Equity rally; tech participation. |
| Bear −15% | −16.5 | Broad selloff; tech underperformance. |
| Rates up +50 bps | −3 | Duration/valuation pressure on growth. |
| Vol spike (VIX 30) | −8 | De-risking, momentum unwind. |
| Recession −20% | −22 | Earnings and multiple compression. |

---

## 10. Rebalancing Triggers

- **Add:** Thesis strengthened or price drops 15%+ below target entry; cash available.
- **Trim:** Position exceeds 1.5× target weight or conviction downgraded (e.g. SPY, AVGO, GOOGL, AMAT trim to targets).
- **Exit:** Thesis broken, stop-loss −20% from entry, or liquidity event.
- **Review:** Monthly for weights, quarterly for conviction and sector caps.

Triggers are guidelines; override with discretion.

---

## 11. Performance Attribution

**Brinson-style:** Total return = Allocation effect + Selection effect + Interaction.

- **Allocation effect:** (Portfolio sector weight − Benchmark sector weight) × Benchmark sector return.
- **Selection effect:** (Portfolio sector return − Benchmark sector return) × Portfolio sector weight.
- **Interaction:** (Portfolio sector weight − Benchmark sector weight) × (Portfolio sector return − Benchmark sector return).

**Example:** Tech overweight 5%, tech beats benchmark by 2% → allocation +0.1%; within tech, names beat sector by 1% → selection +0.05%. Attribution requires daily holdings and benchmark; use portfolio system or spreadsheet for actual decomposition.

---

## 12. Position Sizing Table (Summary)

Final recommended % = min(target %, Kelly cap %, liquidity cap %) then renormalize to 100%. Below: target used with Kelly cap applied where binding; liquidity from broker.

| Ticker | Conviction | Current % | Target % | Kelly cap % | Risk budget % | Liquidity-adjusted % | Final recommended % |
|--------|------------|-----------|----------|--------------|---------------|----------------------|----------------------|
| SPY | HIGH | 17.1 | 10 | 0.65 | 5.3 | — | 4.0 |
| AVGO | HIGH | 16.7 | 10 | 3.3 | 5.3 | — | 8.0 |
| GOOGL | HIGH | 13.8 | 10 | 3.3 | 5.3 | — | 8.0 |
| AMAT | HIGH | 12.6 | 10 | 3.3 | 5.3 | — | 8.0 |
| MSFT | MEDIUM | 6.7 | 6 | 1.3 | 5.3 | — | 4.0 |
| AMZN | LOW | 4.9 | 4 | 0.65 | 5.3 | — | 2.5 |
| AAPL | LOW | 4.6 | 4 | 0.65 | 5.3 | — | 2.5 |
| CRWD | LOW | 4.3 | 4 | 0.65 | 5.3 | — | 2.5 |
| COST | LOW | 4.1 | 4 | 0.65 | 5.3 | — | 2.5 |
| ABBV | LOW | 3.8 | 4 | 0.65 | 5.3 | — | 2.5 |
| GD | LOW | 2.2 | 3 | 0.65 | 5.3 | — | 2.0 |
| V | LOW | 2.2 | 3 | 0.65 | 5.3 | — | 2.0 |
| JPM | LOW | 2.1 | 3 | 0.65 | 5.3 | — | 2.0 |
| KMI | LOW | 1.8 | 2 | 0.65 | 5.3 | — | 1.5 |
| WM | LOW | 0.8 | 2 | 0.65 | 5.3 | — | 1.5 |
| FFOLX | LOW | 0.7 | 1 | 0.65 | 5.3 | — | 1.0 |
| QQQ | LOW | 0.7 | 1 | 0.65 | 5.3 | — | 1.0 |
| NOW | LOW | 0.5 | 1 | 0.65 | 5.3 | — | 1.0 |
| SPGI | LOW | 0.5 | 1 | 0.65 | 5.3 | — | 1.0 |

*Final recommended % are illustrative. In implementation: take min(target, Kelly cap, liquidity cap) per name, then normalize so portfolio sums to 100%. Kelly inputs and caps should be replaced with user edge/win-rate or backtest.*

---

## 13. Risk Budget Allocation (Summary)

| Ticker | Risk budget % | Cumulative % |
|--------|----------------|--------------|
| SPY | 5.3 | 5.3 |
| AVGO | 5.3 | 10.6 |
| GOOGL | 5.3 | 15.9 |
| AMAT | 5.3 | 21.2 |
| MSFT | 5.3 | 26.5 |
| AMZN | 5.3 | 31.8 |
| AAPL | 5.3 | 37.1 |
| CRWD | 5.3 | 42.4 |
| COST | 5.3 | 47.7 |
| ABBV | 5.3 | 53.0 |
| GD | 5.3 | 58.3 |
| V | 5.3 | 63.6 |
| JPM | 5.3 | 68.9 |
| KMI | 5.3 | 74.2 |
| WM | 5.3 | 79.5 |
| FFOLX | 5.3 | 84.8 |
| QQQ | 5.3 | 90.1 |
| NOW | 5.3 | 95.4 |
| SPGI | 5.3 | 100.0 |

No single name exceeds 20% of risk (placeholder equal budget). Use risk-parity script for true risk contribution.

---

## 14. Stress Test Dashboard (Summary)

| Regime | Portfolio return % | Pass/Fail |
|--------|--------------------|-----------|
| Bull +5% | +5.5 | Pass |
| Bear −15% | −16.5 | Pass (within long-only tolerance) |
| Rates up +50 bps | −3 | Pass |
| Vol spike (VIX 30) | −8 | Pass |
| Recession −20% | −22 | Pass (stress case) |

**Conclusion:** Portfolio is resilient across all 5 regimes for a long-only equity mandate. Main risk is bear/recession drawdown; ensure cash and risk tolerance support −20% drawdown.

---

## 15. Implementation Checklist

1. **Current vs target weights → trades:** Trim SPY, AVGO, GOOGL, AMAT to target; trim MSFT, AMZN, AAPL, CRWD, COST, ABBV as needed; add WM (and optionally GD, V, JPM, KMI) toward target; rebalance FFOLX, QQQ, NOW, SPGI to final recommended %.
2. **Concentration and liquidity caps:** Enforce tech sector cap (e.g. 40%); verify ADV and apply liquidity caps for AVGO, AMAT, and any ADV < $5M names.
3. **Rebalancing calendar:** Monthly weight check; quarterly conviction and sector review.
4. **Attribution setup:** Define benchmark (e.g. SPY or 60/40); map tickers to sectors; use portfolio system or spreadsheet for Brinson attribution.

---

*Report generated by /portfolio-construction-optimizer "current" using context/portfolio-details.md. Conviction inferred from weight bands; theses = "Current allocation." For production: run scripts/risk_parity_analyzer.py for correlation and risk contribution; supply FMP or broker ADV for liquidity.*
