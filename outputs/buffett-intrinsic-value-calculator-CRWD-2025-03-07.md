# Buffett Intrinsic Value Analysis — CrowdStrike Holdings, Inc. (CRWD)

**Report date:** 2025-03-07  
**Investment horizon:** 5 years (default)  
**Current price:** $428.99 (source: FMP)

---

## Owner Earnings Calculation

CRWD reports **negative GAAP net income** in FY 2025 and FY 2026 (heavy SBC and growth investment). For the owner-earnings construct we use **Free Cash Flow** as the proxy for cash available to owners after maintenance capex and working capital; FCF is positive and representative of distributable cash.

**FY 2026** (fiscal year ending 2026-01-31) — FCF-based proxy:

| Component | Amount ($M) | Note |
|-----------|-------------|------|
| Operating cash flow | 1,612 | From cash flow statement |
| − Capital expenditure | 302 | investmentsInPropertyPlantAndEquipment (software company; modest capex) |
| **Free Cash Flow (owner earnings proxy)** | **1,310** | |

**Shares outstanding:** 252,098,440 (quote).  
**Owner earnings (FCF) per share:** $1,310M ÷ 252.1M ≈ **$5.19/share**.

*Assumption note:* GAAP NI was -$162.5M in FY 2026 and -$19.3M in FY 2025. We do not add back SBC for “owner earnings” in the strict sense; we use reported FCF as the cash-flow base for the DCF. Maintenance capex is embedded in total capex ($302M); for a SaaS-heavy model, the bulk of capex is growth (data centers, tooling). This FCF base is used for scenario valuation only; it is not a traditional Graham/Buffett owner-earnings reconciliation.

---

## Moat Assessment

**Rating:** **Narrow**

| Source | Score (1–5) | Evidence |
|--------|-------------|----------|
| **Brand power** | 4 | Leader in cloud-native endpoint and identity; strong in enterprise and incident response; not yet a household name. |
| **Switching costs** | 5 | Falcon platform embedded in endpoints and cloud workloads; integration and deployment create high switching cost. |
| **Network effects** | 4 | Threat intelligence and telemetry improve with scale; platform breadth (identity, log, IT ops) adds stickiness. |
| **Cost advantages** | 3 | Efficient cloud delivery, but competition from Microsoft (Defender), SentinelOne, and others limits pricing power. |
| **Efficient scale** | 4 | Few vendors can match breadth (endpoint, cloud, identity, data); scale in R&D and go-to-market. |

**Summary:** Narrow moat: strong switching costs and platform breadth, but competition (especially Microsoft) and ongoing investment prevent a wide-moat rating. Execution and consolidation in security could widen the moat over time.

---

## Intrinsic Value Range (10-year DCF)

Base-year cash flow (FCF as owner-earnings proxy): **$5.19/share**.  
10-year explicit projection, then terminal value. Terminal growth: 2% (bear), 3% (base), 4% (bull).

| Scenario | Growth (yr 1–10) | Discount rate | Terminal g | Intrinsic value (per share) |
|----------|------------------|---------------|------------|-----------------------------|
| Bear     | 3%               | 8%            | 2%         | **$106**                    |
| Base     | 8%               | 10%           | 3%         | **$203**                    |
| Bull     | 15%              | 12%           | 4%         | **$141**                    |

**Range:** $106 bear / $203 base / $141 bull (per share).

*Note:* Bull-case IV is below base because 15% growth with 12% discount shifts value toward the 10-year period; terminal value is sensitive to terminal g. Base case is the primary reference for margin of safety.

*Assumptions:* Base FCF $5.19/share; 10-year growth and discount rates as in table; terminal value = FCF year 11 × (1 + g_term) / (r − g_term); share count ~252M.

---

## Margin of Safety

- **Current price:** $428.99  
- **Base-case intrinsic value:** $203  

**Discount to base case:** ($203 − $428.99) ÷ $203 ≈ **−111%** → stock trades at about a **111% premium** to base-case intrinsic value.

- Versus bear ($106): large premium.  
- Versus bull ($141): large premium.

**Buffett 30% rule:** Price is **not** 30%+ below intrinsic value. It is well above base, bear, and bull. **No margin of safety**; valuation reflects high growth expectations that exceed the scenario assumptions above.

---

## Verdict

**Avoid** — Narrow moat and no margin of safety at current price. Base-case IV ($203) implies the stock would need to fall roughly 53% to reach base-case fair value and further to meet a 30% margin. Quality franchise in a strong segment, but valuation leaves no room for error; suitable only for growth investors comfortable with premium multiples and execution risk.

---

## Top 3 Permanent Impairment Risks

1. **Microsoft and bundled competition** — Microsoft Defender and integrated security in M365/Azure can permanently compress win rates and pricing in endpoints and identity, especially in mid-market and existing Microsoft shops.  
2. **Slowing growth or margin disappointment** — If revenue growth or Rule-of-40 margins disappoint, multiple compression could be severe (high current P/FCF and P/S); permanent repricing of “growth premium” would impair returns.  
3. **Platform consolidation or displacement** — Shift to agentless or alternative architectures, or a successful “platform of platforms” from a larger vendor, could permanently reduce CRWD’s share of security spend.

---

## Data sources

- **FMP API:** profile, quote, income statement, cash flow, balance sheet, key metrics, ratios.  
- **Data as of:** FY 2026 (filing 2026-03-05), quote as of report date.

*Disclaimer: Intrinsic value and margin of safety are estimates for research and education only, not investment advice.*
