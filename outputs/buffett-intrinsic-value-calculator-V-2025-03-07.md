# Buffett Intrinsic Value Analysis — Visa Inc. (V)

**Report date:** 2025-03-07  
**Investment horizon:** 5 years (default)  
**Current price:** $317.36 (source: FMP)

---

## Owner Earnings Calculation

Using **FY 2025** (fiscal year ending 2025-09-30) from FMP. All figures in millions USD.

| Component | Amount ($M) | Note |
|-----------|-------------|------|
| Net Income | 20,058 | Income statement FY 2025 |
| + Depreciation & Amortization | 1,220 | Cash flow statement |
| − Maintenance Capex | 1,220 | Assumed equal to D&A (total capex $1,482M; D&A as maintenance proxy for asset-light network) |
| + Working capital decrease | 11,788 | changeInWorkingCapital FY 2025 negative = WC release (cash source) |
| **Owner Earnings** | **31,846** | |

**Shares outstanding:** 1,928,039,548 (quote).  
**Owner earnings per share:** $31,846M ÷ 1,928.0M ≈ **$16.52/share**.

*Assumption note:* Visa’s working-capital change is heavily influenced by client funds and settlement balances; the large release in FY 2025 may not repeat at the same level. Maintenance capex is taken as D&A; total capex is modest relative to operating cash flow.

---

## Moat Assessment

**Rating:** **Wide**

| Source | Score (1–5) | Evidence |
|--------|-------------|----------|
| **Brand power** | 5 | Visa is the default card brand globally; merchants and consumers associate it with acceptance and trust. |
| **Switching costs** | 5 | Issuers and acquirers are embedded in VisaNet; changing networks is costly and operationally complex. |
| **Network effects** | 5 | More merchants and cardholders increase value for all participants; two-sided network with strong scale. |
| **Cost advantages** | 5 | Scale in transaction processing and technology; very high margins and returns on capital. |
| **Efficient scale** | 5 | Few global card networks; natural duopoly (with Mastercard) in a scale-driven industry. |

**Summary:** Wide moat from the global payments network, two-sided network effects, and high switching costs. Main risks are regulatory (interchange) and competitive/technological (new rails, disintermediation).

---

## Intrinsic Value Range (10-year DCF)

Base-year owner earnings: **$16.52/share**.  
10-year explicit projection, then terminal value. Terminal growth: 2% (bear), 3% (base), 4% (bull).

| Scenario | Growth (yr 1–10) | Discount rate | Terminal g | Intrinsic value (per share) |
|----------|------------------|---------------|------------|-----------------------------|
| Bear     | 3%               | 8%            | 2%         | **$311**                    |
| Base     | 8%               | 10%           | 3%         | **$361**                    |
| Bull     | 15%              | 12%           | 4%         | **$473**                    |

**Range:** $311 bear / $361 base / $473 bull (per share).

*Assumptions:* Owner earnings $16.52/share; 10-year growth and discount rates as in table; terminal value = FCF year 11 × (1 + g_term) / (r − g_term); share count ~1.93B.

---

## Margin of Safety

- **Current price:** $317.36  
- **Base-case intrinsic value:** $361  

**Discount to base case:** ($361 − $317.36) ÷ $361 ≈ **12%** → stock trades at about a **12% discount** to base-case intrinsic value.

- Versus bear ($311): current price is **above** bear-case IV.  
- Versus bull ($473): current price is **below** bull-case IV.

**Buffett 30% rule:** Price is **not** 30%+ below base-case intrinsic value. **Margin-of-safety rule is not satisfied.**

---

## Verdict

**Hold** — Wide moat and exceptional franchise, but current price offers only a modest discount (~12%) to base-case intrinsic value; no 30% margin of safety for a value buy. Wait for a larger pullback before adding on a strict margin-of-safety basis.

---

## Top 3 Permanent Impairment Risks

1. **Interchange and fee regulation** — Legislation or regulation that permanently caps interchange or network fees (e.g. Durbin-style or international equivalents) could permanently compress revenue and margins without a commensurate cut in costs.  
2. **Disintermediation by new payment rails** — Real-time payments, CBDCs, or bank-led networks that bypass card networks could permanently reduce transaction volume and relevance of the traditional card rail.  
3. **Loss of critical issuer or acquirer partnerships** — A major bank or market shifting volume to a competitor or in-house rail could permanently impair scale and network effects in that region.

---

## Data sources

- **FMP API:** profile, quote, income statement, cash flow, balance sheet, key metrics, ratios.  
- **Data as of:** FY 2025 (filing 2025-11-06), quote as of report date.

*Disclaimer: Intrinsic value and margin of safety are estimates for research and education only, not investment advice.*
