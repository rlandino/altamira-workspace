# Buffett Intrinsic Value Analysis — Broadcom Inc. (AVGO)

**Report date:** 2025-03-07  
**Investment horizon:** 5 years (default)  
**Current price:** $330.48 (source: FMP)

---

## Owner Earnings Calculation

Using **FY 2025** (fiscal year ending 2025-11-02) from FMP. Post–VMware acquisition year; numbers in millions USD.

| Component | Amount ($M) | Note |
|-----------|-------------|------|
| Net Income | 23,126 | Income statement FY 2025 |
| + Depreciation & Amortization | 8,775 | Cash flow statement (heavy intangibles amortization post-VMware) |
| − Maintenance Capex | 623 | Total capex used (company is asset-light; capex is minimal vs D&A) |
| + Working capital decrease | 8,500 | changeInWorkingCapital FY 2025 negative = WC release (cash source) |
| **Owner Earnings** | **39,778** | |

**Shares outstanding:** 4,741,273,799 (quote).  
**Owner earnings per share:** $39,778M ÷ 4,741M ≈ **$8.39/share** (round to **$8.40** for scenarios).

*Assumption note:* Total capex in FY 2025 was $623M; used in full as maintenance. D&A of $8.8B is largely amortization of intangibles (VMware and prior M&A); no add-back of that for “maintenance” in the sense of physical plant. Working capital release of $8.5B (e.g. receivables, other WC) is included; in a post-acquisition year this can be elevated.

---

## Moat Assessment

**Rating:** **Wide**

| Source | Score (1–5) | Evidence |
|--------|-------------|----------|
| **Brand power** | 4 | Broadcom is a default choice in connectivity, custom ASICs, and infrastructure software; VMware adds enterprise brand. |
| **Switching costs** | 5 | Customers design in chips and software; changing vendors is costly and slow. High lock-in in networking and storage. |
| **Network effects** | 3 | Strong in software (VMware ecosystem); semis are more scale/design-win than classic network effects. |
| **Cost advantages** | 5 | Scale in semis and software R&D; consolidation and operational discipline support margins and ROIC. |
| **Efficient scale** | 4 | Markets (custom silicon, enterprise software) support few scaled players; Broadcom is a consolidator. |

**Summary:** Wide moat from switching costs, cost/scale, and portfolio breadth (semis + VMware). Execution risk and leverage are the main offsets.

---

## Intrinsic Value Range (10-year DCF)

Base-year owner earnings: **$8.40/share** (FY 2025).  
10-year explicit projection, then terminal value. Terminal growth: 2% (bear), 3% (base), 4% (bull).

| Scenario | Growth (yr 1–10) | Discount rate | Terminal g | Intrinsic value (per share) |
|----------|-------------------|---------------|------------|-----------------------------|
| Bear     | 3%                | 8%            | 2%         | **$151**                    |
| Base     | 8%                | 10%           | 3%         | **$167**                    |
| Bull     | 15%               | 12%           | 4%         | **$253**                    |

**Range:** $151 bear / $167 base / $253 bull (per share).

*Assumptions:* Owner earnings $8.40/share; 10-year growth and discount rates as above; terminal value = FCF year 11 / (r − g); share count ~4.74B.

---

## Margin of Safety

- **Current price:** $330.48  
- **Base-case intrinsic value:** $167  

**Discount to base case:** ($167 − $330.48) ÷ $167 ≈ **−98%** → stock trades at about a **98% premium** to base-case intrinsic value.

- Versus bear ($151): large premium.  
- Versus bull ($253): about **31% premium**.

**Buffett 30% rule:** Price is **not** 30%+ below intrinsic value. It is well above base and bear and above bull. **No margin of safety.**

---

## Verdict

**Avoid** — High-quality, wide-moat franchise (semis + VMware) but current price implies no margin of safety. Base and bear cases suggest material overvaluation; even the bull case is below the current quote. Debt and integration add risk. For a value-oriented entry, wait for a meaningful discount to base-case intrinsic value (e.g. 30%+ below $167, or ~$117 and below).

---

## Top 3 Permanent Impairment Risks

1. **VMware integration and leverage** — Large debt load post-VMware; if synergy and free cash flow fall short, refinancing or covenant stress could force asset sales or limit investment and permanently damage the combined franchise.  
2. **Semiconductor downcycle and loss of design wins** — Revenue is tied to data center, networking, and wireless; a prolonged semi downturn or loss of key sockets could compress margins and make the current profit and FCF base unsustainable.  
3. **Regulatory or structural change** — Antitrust or licensing challenges in semis or software could force divestitures, limit M&A, or reduce pricing power and durability of the moat.

---

## Data sources

- **FMP API:** profile, quote, income statement, cash flow, balance sheet, key metrics, ratios.  
- **Data as of:** FY 2025 (filing 2025-12-18), quote as of report date.

*Disclaimer: Intrinsic value and margin of safety are estimates for research and education only, not investment advice.*
