# SIG Daily Theta Decay Calculator — 2025-03-07

**Report date:** 2025-03-07  
**Positions:** 5 short premium (all short puts)  
**Data source:** User (positions); FMP (underlying price for intrinsic/theta estimate)

---

## Dashboard Summary

| Metric | Value |
|--------|--------|
| Portfolio theta (daily) | $46.20 |
| Weekly projection (5d) | $231.00 |
| Monthly projection (21d) | $970.20 |
| Peak theta hour | 3:00–4:00 PM ET |
| Regime | All positions 378–434 DTE; no acceleration zone |

## Position-Level Theta

| Ticker | Strike | Type | Exp | Contracts | Credit | Current | DTE | Theta/day ($) |
|--------|--------|------|-----|------------|--------|---------|-----|---------------|
| MSFT | 430 | Put | 2026-03-20 | 5 | 8.70 | 22.40 | 378 | 0.00 |
| MSFT | 380 | Put | 2026-05-15 | 5 | 10.12 | 11.80 | 434 | 13.59 |
| AVGO | 310 | Put | 2026-03-20 | 5 | 12.60 | 5.00 | 378 | 6.61 |
| SPY | 620 | Put | 2026-05-15 | 5 | 6.92 | 10.16 | 434 | 11.71 |
| COST | 900 | Put | 2026-05-15 | 5 | 11.00 | 12.40 | 434 | 14.29 |

**Notes:** Credit/Current in $ per share (×100 = per contract). MSFT 430P is ITM (spot 404.90 < strike 430); remaining time value set to 0 for theta (option trading near/below intrinsic). Theta estimated from time value / DTE; use broker theta when available.

## Portfolio Theta and Income

- **Total daily theta:** $46.20
- **Weekly (5 trading days):** $231.00
- **Monthly (21 trading days):** $970.20

## Hourly Decay Curve

| Time (ET) | % of daily theta | $ (portfolio) | Cumulative $ |
|-----------|------------------|----------------|--------------|
| 9:30–10:30 | 8% | 3.71 | 3.71 |
| 10:30–11:30 | 8% | 3.71 | 7.42 |
| 11:30–12:30 | 12% | 5.57 | 13.00 |
| 12:30–1:30 | 12% | 5.57 | 18.56 |
| 1:30–2:30 | 18% | 8.35 | 26.91 |
| 2:30–3:30 | 22% | 10.21 | 37.12 |
| 3:30–4:00 | 20% | 9.24 | 46.20 |

**Peak theta hours:** 2:30–4:00 PM ET (largest decay per hour in the afternoon).

*Hourly allocation is model-based; actual decay depends on moneyness and IV.*

## Acceleration Zone

**No positions are in the acceleration zone.** All expirations are 378–434 days out (Mar/May 2026). Theta accelerates in the **last 2–3 trading hours** on expiration day and the **last 1–2 DTE**; consider closing or tightening risk in that window when these dates approach.

## Theta-to-Delta Ratio

Delta was not provided. **Theta/Delta ratio:** Delta from broker required for theta/delta ratio; omit or use placeholder. Target for quality premium is often **>$1–2 per delta per day** when delta is in contract terms (e.g. |delta| × 100).

## Weekend Theta Capture

No positions expire on a Friday in the near term (expirations 2026). For any **Friday expiration** in the future: holding through the weekend captures ~3 calendar days of theta (Fri close → Mon open); only hold if risk is acceptable (e.g. far OTM).

## Theta vs Gamma Risk

Underlying vs short strike (all puts; flag if price within 2% of strike):

| Position | Underlying | Strike | Distance | Note |
|----------|------------|--------|----------|------|
| MSFT 430P | 404.90 | 430 | 6.2% below | ITM; monitor for assignment/roll |
| MSFT 380P | 404.90 | 380 | 6.6% above | OTM, comfortable |
| AVGO 310P | 331.40 | 310 | 6.5% above | OTM, comfortable |
| SPY 620P | 663.81 | 620 | 6.6% above | OTM, comfortable |
| COST 900P | 994.19 | 900 | 9.5% above | OTM, comfortable |

**MSFT 430P** is already ITM (price below strike); gamma and assignment risk are elevated. Consider rolling or closing; theta is negligible. When price is within **1–2% of short strike**, gamma often outweighs theta—close or roll.

## Optimal Closing Time

**Mathematically ideal:** Close when **remaining time value &lt; 25–30% of credit collected**, or **before 2 PM ET on expiration day** if near the money. Otherwise let expire for full theta capture. For these LEAPS (378–434 DTE), 50% profit (buy back at half of credit) is a common target; re-evaluate as expiration approaches.

## Daily / Weekly / Monthly Income Projection

At current position sizes:
- **Per day:** $46.20
- **Per week:** $231.00 (5 trading days)
- **Per month:** $970.20 (21 trading days)

## Compounding Growth Projection

**Assumptions:** Starting account **$100,000**; daily theta **$46.20**; **100% reinvested** (theta used to size up or add positions). Daily growth rate = 46.20 / 100000 = 0.0462%.

| Horizon | Projected account | % growth |
|---------|-------------------|----------|
| 30 days | $101,403 | 1.40% |
| 60 days | $102,832 | 2.83% |
| 90 days | $104,287 | 4.29% |

*Assumes theta reinvested daily; no drawdowns; for illustration only. Actual results will vary.*

---

## Data and disclaimer

- **Positions:** From user. Underlying prices from FMP (2025-03-07) for intrinsic and theta estimate.
- **Disclaimer:** Theta estimates are model-based (time value / DTE). Actual decay depends on IV, moneyness, and market moves. For educational and research use only; not investment advice.
