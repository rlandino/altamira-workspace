# Buffett Intrinsic Value Analysis — JPMorgan Chase & Co. (JPM)

**Report date:** 2025-03-07  
**Investment horizon:** 5 years (default)  
**Current price:** $289.48 (source: FMP)

---

## Owner Earnings Calculation

Using **FY 2025** (calendar year ending 2025-12-31) from FMP. All figures in millions USD.

For **banks**, the standard owner-earnings formula is applied with care: capital expenditure is negligible (FMP reports $0), and working-capital changes are driven by balance-sheet growth (loans, deposits, trading assets), not traditional receivables/inventory. We use the formula for consistency and state the bank context.

| Component | Amount ($M) | Note |
|-----------|-------------|------|
| Net Income | 57,048 | Income statement FY 2025 |
| + Depreciation & Amortization | 8,821 | Cash flow statement |
| − Maintenance Capex | 0 | FMP reports no capex; banks have minimal industrial capex |
| − Working capital increase | 13,866 | changeInWorkingCapital FY 2025 positive = WC increase (cash use) |
| **Owner Earnings** | **52,003** | |

**Shares outstanding:** 2,697,032,375 (quote).  
**Owner earnings per share:** $52,003M ÷ 2,697.0M ≈ **$19.28/share**.

*Assumption note:* For banks, net income is often used directly as the sustainable earnings proxy; here we apply the full formula. WC changes at JPM are highly volatile (e.g. FY 2024 large negative release). Using latest-year WC change; a 3–5 year average would smooth but we use FY 2025 for the base. No maintenance capex assumed (FMP capex = 0).

---

## Moat Assessment

**Rating:** **Wide**

| Source | Score (1–5) | Evidence |
|--------|-------------|----------|
| **Brand power** | 5 | JPMorgan Chase is a global leader in investment banking, asset management, and consumer banking; trusted brand with institutional and retail clients. |
| **Switching costs** | 5 | Corporate treasury, prime brokerage, custody, and lending relationships are deeply embedded; high cost to switch banks. |
| **Network effects** | 4 | Strong in investment banking and markets; ecosystem of clients and deal flow; slightly less direct than pure network businesses. |
| **Cost advantages** | 5 | Scale in technology, operations, and funding; industry-leading returns and efficiency. |
| **Efficient scale** | 5 | Systemically important; scale in CIB, CCB, AWM, and commercial banking; few peers can replicate full platform. |

**Summary:** Wide moat from diversification, scale, brand, and switching costs. Main risks are regulatory, credit cycle, and management succession.

---

## Intrinsic Value Range (10-year DCF)

Base-year owner earnings: **$19.28/share**.  
10-year explicit projection, then terminal value. Terminal growth: 2% (bear), 3% (base), 4% (bull).

| Scenario | Growth (yr 1–10) | Discount rate | Terminal g | Intrinsic value (per share) |
|----------|------------------|---------------|------------|-----------------------------|
| Bear     | 3%               | 8%            | 2%         | **$363**                    |
| Base     | 8%               | 10%           | 3%         | **$421**                    |
| Bull     | 15%              | 12%           | 4%         | **$552**                    |

**Range:** $363 bear / $421 base / $552 bull (per share).

*Assumptions:* Owner earnings $19.28/share; 10-year growth and discount rates as in table; terminal value = FCF year 11 × (1 + g_term) / (r − g_term); share count ~2.70B.

---

## Margin of Safety

- **Current price:** $289.48  
- **Base-case intrinsic value:** $421  

**Discount to base case:** ($421 − $289.48) ÷ $421 ≈ **31%** → stock trades at about a **31% discount** to base-case intrinsic value.

- Versus bear ($363): current price is **below** bear-case IV.  
- Versus bull ($552): current price is **below** bull-case IV.

**Buffett 30% rule:** Price is **30%+ below** base-case intrinsic value (31% discount). **Margin-of-safety rule is satisfied.**

---

## Verdict

**Buy** — Wide moat, ~31% discount to base-case intrinsic value, and manageable permanent impairment risks. Leading diversified bank with strong returns and earnings power; current price offers a margin of safety for a value-oriented entry.

---

## Top 3 Permanent Impairment Risks

1. **Regulatory and capital regime change** — materially higher capital or liquidity requirements, or structural reform (e.g. breakup, ring-fencing), could permanently reduce ROE and franchise value.  
2. **Severe credit cycle or systemic crisis** — a deep recession or financial shock could permanently impair loan books and trading positions and damage client trust.  
3. **Management succession and execution** — departure of key leadership (e.g. CEO) without a clear successor or a major strategic misstep could permanently weaken culture and competitive position.

---

## Data sources

- **FMP API:** profile, quote, income statement, cash flow, balance sheet, key metrics, ratios.  
- **Data as of:** FY 2025 (filing 2026-02-13), quote as of report date.

*Disclaimer: Intrinsic value and margin of safety are estimates for research and education only, not investment advice.*
