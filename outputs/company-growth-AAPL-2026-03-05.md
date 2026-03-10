# Company Growth Evaluation — AAPL (Apple Inc.)

**Report date:** 2026-03-05  
**Summary:** Growth evaluation using core four metrics (Revenue, EPS, FCF margin, ROIC) plus margins, Rule of 40, and revenue trajectory.

---

## Core growth metrics (grade drivers)

| Metric | 3yr CAGR % | Latest YoY % | Latest value |
|--------|------------|--------------|--------------|
| **Revenue** | 1.82 | 6.43 | $416.2B |
| **EPS (GAAP diluted)** | 6.88 | 22.70 | $7.46 |
| **Free cash flow margin** | -5.6* | -4.10 pp | 23.73% |
| **ROIC** | 4.82 | 17.3 | 51.97% |

*FCF margin 3yr CAGR is the CAGR of the margin ratio (23.73% vs 28.25% three years ago); margin declined as revenue grew and FCF stepped down in FY25.

---

## Grade

**Grade: D.**

**Reason for grade:** Revenue growth is weak on a 3yr basis (CAGR 1.8%)—in the D band (0–5%), though latest YoY improved to 6.4%. EPS growth is modest (3yr CAGR 6.9%)—C band; latest YoY is strong (22.7%) on buybacks and margin. FCF margin remains high at 23.7% and above 15%, but has declined YoY (−4.1 pp) and over three years, so trend is not expanding (B on level, D on trend). ROIC is excellent at 52.0% and improved YoY—clearly A. Per the worst-of rule, revenue in the D band caps the composite grade at D.

---

## Optional metrics

- **Operating margin:** 31.97% (latest); up from 31.51% (FY24) and 30.29% (FY22). 3yr trend: improving.
- **Net income growth:** 3yr CAGR 3.9%; latest YoY 19.5%.
- **Gross margin:** 46.91% (latest); up from 46.21% (FY24) and 43.31% (FY22).
- **EBITDA margin:** 34.70% (latest); up from 34.51% (FY24) and 33.76% (FY22).
- **ROE:** 151.9% (latest; key-metrics ratio—elevated by low equity from buybacks); trend strong.
- **FCF (dollars) growth:** 3yr CAGR −4.0%; latest YoY −9.3% (lower OCF and higher CapEx in FY25).
- **Rule of 40:** Revenue growth 6.43% + Operating margin 31.97% = **38.4** → **Solid** (20–40), just below Elite.
- **Revenue growth trajectory:** **Decelerating** over the period (FY22 7.8%, FY23 −2.8%, FY24 2.0%, FY25 6.4%); recent re-acceleration from a low base.
- **PEG ratio (approx.):** P/E ~34.1 (key-metrics FY25) ÷ ~7% (EPS 3yr CAGR) ≈ 4.9; forward growth higher; use with caution.
- **Asset turnover:** 1.16 (latest); up from 1.07 (FY24) and 1.12 (FY22).

---

## Metrics to monitor

- **Revenue re-acceleration:** 3yr revenue CAGR is low (1.8%); watch iPhone, Services, and geographic mix for sustained mid-single-digit or better growth.
- **FCF margin sustainability:** FCF margin stepped down to 23.7% on lower OCF and higher CapEx; monitor whether it stabilizes or recovers toward prior-year levels.
- **ROIC vs capital allocation:** ROIC is very high (52%); track that buybacks and investments continue to earn above cost of capital.
- **EPS consistency vs consensus:** Strong FY25 EPS growth (22.7% YoY); monitor execution and buyback pace vs expectations.
- **Rule of 40:** Currently Solid (38.4); revenue growth is the main lever to reach Elite (≥40).
- **Product cycle and Services:** iPhone and Services growth and margin drive revenue and profit trajectory.

---

## Caveats

- **Data source:** FMP API v3 (income statement, cash flow, key-metrics, ratios, financial-growth, annual, limit 5). Quote and profile for context.
- **EPS:** FMP provides GAAP diluted EPS; report uses **EPS (GAAP)**. No non-GAAP adjustment applied.
- **FCF margin:** Computed as (operatingCashFlow − capitalExpenditure) / revenue. FY25 OCF declined and CapEx increased vs FY24.
- **ROIC:** From key-metrics `roic` (decimal). Apple’s ROIC is elevated by capital-light model and substantial buybacks (reduced equity).
- For earnings timing run `/earnings-calendar AAPL`. For trade ideas run `/options-scan AAPL`.
