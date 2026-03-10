# Company Growth Evaluation — JPM (JPMorgan Chase & Co.)

**Report date:** 2026-03-05  
**Summary:** Growth evaluation using core four metrics (Revenue, EPS, FCF margin, ROIC) plus margins, Rule of 40, and trajectory. **Note:** JPM is a bank; FCF and ROIC from FMP are volatile and less comparable to non-financials.

---

## Core growth metrics (grade drivers)

| Metric | 3yr CAGR % | Latest YoY % | Latest value |
|--------|------------|--------------|--------------|
| **Revenue** | 22.0 | 3.31 | $279.7B |
| **EPS (GAAP diluted)** | 18.35 | 1.52 | $20.05 |
| **Free cash flow margin** | -20.2* | N/M† | 36.1% |
| **ROIC** | -31.0 | -71.5 | 1.29% |

*FCF margin 3yr CAGR is the CAGR of the margin ratio (36.1% vs 69.6% three years ago); FY24 OCF was negative, so margin was not defined that year.  
†N/M = not meaningful (prior year FCF negative).

---

## Grade

**Grade: F.**

**Reason for grade:** Revenue and EPS growth are strong: revenue 3yr CAGR 22.0% (A) and EPS 3yr CAGR 18.4% (A). The composite is pulled to F by the other two core metrics. FCF margin declined from a very high level three years ago and was negative in FY24 due to bank balance-sheet movements (lending/deposits), then recovered to 36.1% in FY25—trend and volatility warrant D. ROIC from FMP is 1.29% (latest), below 5%—F band. Under the worst-of rule, one F caps the grade at F. **For context:** Banks are capital-intensive and report under different accounting; FCF and ROIC from standard screens are often volatile or not comparable to non-financials. Excluding those two, revenue and EPS alone would support an A; the F reflects strict application of the core-four scale to reported data.

---

## Optional metrics

- **Operating margin:** 25.95% (latest); down from 27.73% (FY24) and 30.01% (FY22); compressed as interest expense rose with rates.
- **Net income growth:** 3yr CAGR 14.8%; latest YoY -2.4%.
- **Gross margin:** 59.91% (latest); bank revenue mix (interest vs non-interest) makes this less comparable across years.
- **EBITDA margin:** 29.10% (latest); down from 30.66% (FY24).
- **ROE:** 15.74% (latest); stable vs 16.96% (FY24) and 12.89% (FY22).
- **FCF (dollars) growth:** Not meaningful over 3 years due to FY24 negative OCF; latest year FCF $100.9B.
- **Rule of 40:** Revenue growth 3.31% + Operating margin 25.95% = **29.3** → **Solid** (20–40). (Less relevant for banks.)
- **Revenue growth trajectory:** **Decelerating** — FY23 +53.6%, FY24 +14.6%, FY25 +3.3%; rate cycle and comps.
- **PEG ratio (approx.):** P/E ~15.8 ÷ ~18% (EPS 3yr CAGR) ≈ 0.9.
- **Asset turnover:** 0.063 (latest); stable vs prior years.

---

## Metrics to monitor

- **Net interest margin (NIM) and rate sensitivity:** Revenue and earnings sensitivity to Fed policy and curve; deposit betas and loan pricing.
- **Credit quality and provisions:** Reserve levels, NCOs, and impact on net income.
- **Capital and returns:** CET1, ROTCE, and buybacks vs regulatory and strategic needs.
- **Operating leverage:** Expense growth vs revenue; efficiency ratio and branch/digital mix.
- **FCF/OCF volatility:** Balance-sheet-driven swings in reported OCF; focus on earnings and capital distribution.
- **ROIC/ROE:** For banks, ROE and ROTCE are more standard than ROIC; monitor capital allocation and hurdle rates.

---

## Caveats

- **Data source:** FMP API v3 (income statement, cash flow, key-metrics, ratios, financial-growth, annual, limit 5). Quote and profile for context.
- **EPS:** FMP provides GAAP diluted EPS; report uses **EPS (GAAP)**.
- **Banks:** JPM is a diversified bank. Revenue includes interest and non-interest income; cost of revenue and operating expenses are not directly comparable to non-financials. **FCF:** Bank operating cash flow is heavily influenced by changes in loans, deposits, and trading positions; FY24 OCF was negative ($42B), FY25 positive ($100.9B). FCF margin is therefore volatile and not a stable growth metric. **ROIC:** FMP’s ROIC for banks uses invested capital that can produce very low or negative ratios; ROE or ROTCE are more commonly used for banks.
- **Grade interpretation:** The F grade is driven strictly by reported ROIC (<5%) and FCF margin volatility/decline. Revenue and EPS growth are strong; for bank analysis, NIM, credit, capital, and ROE are more relevant than FCF margin and ROIC.
- For earnings timing run `/earnings-calendar JPM`. For trade ideas run `/options-scan JPM`.
