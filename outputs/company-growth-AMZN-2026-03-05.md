# Company Growth Evaluation — AMZN (Amazon.com, Inc.)

**Report date:** 2026-03-05  
**Summary:** Growth evaluation using core four metrics (Revenue, EPS, FCF margin, ROIC) plus margins, Rule of 40, and revenue trajectory.

---

## Core growth metrics (grade drivers)

| Metric | 3yr CAGR % | Latest YoY % | Latest value |
|--------|------------|--------------|--------------|
| **Revenue** | 11.72 | 12.38 | $716.9B |
| **EPS (GAAP diluted)** | N/A* | 29.66 | $7.17 |
| **Free cash flow margin** | N/A** | -4.08 pp | 1.07% |
| **ROIC** | 79.5*** | -19.7 | 10.70% |

*EPS 3yr CAGR not computed: FY22 was a loss year (negative base).  
**FCF margin 3yr CAGR not computed: FY22 FCF was negative.  
***ROIC 3yr CAGR is the CAGR of the ROIC ratio from a very low FY22 base (1.83%) to 10.70%.

---

## Grade

**Grade: D.**

**Reason for grade:** Revenue growth is solid (3yr CAGR 11.7%, latest YoY 12.4%)—B band. EPS cannot receive a 3yr CAGR sub-grade because the base year (FY22) was a loss; latest YoY EPS growth is strong (29.7%). FCF margin is the main drag: at 1.07% it sits in the 0–5% band and declined 4.1 pp YoY as CapEx stepped up sharply ($131.8B in FY25 vs $83.0B in FY24), so FCF margin is D. ROIC at 10.7% is in the C band (≥10%) but declined 19.7% YoY. With FCF margin at D and the command’s worst-of rule (any D caps the grade at D), the composite grade is D.

---

## Optional metrics

- **Operating margin:** 11.16% (latest); up from 10.75% (FY24) and 6.41% (FY23). 3yr trend: material improvement from a low base.
- **Net income growth:** 3yr CAGR N/A (FY22 loss); latest YoY 31.1%.
- **Gross margin:** 50.29% (latest); up from 48.85% (FY24) and 43.81% (FY22).
- **EBITDA margin:** 23.06% (latest); up from 19.41% (FY24) and 7.46% (FY22).
- **ROE:** 18.89% (latest); up from 20.72% (FY24); FY22 was negative.
- **FCF (dollars) growth:** 3yr CAGR N/A (FY22 FCF negative); latest YoY −76.6% (CapEx step-up in FY25).
- **Rule of 40:** Revenue growth 12.38% + Operating margin 11.16% = **23.5** → **Solid** (20–40).
- **Revenue growth trajectory:** **Stable to slightly accelerating** (FY22 9.4%, FY23 11.8%, FY24 11.0%, FY25 12.4%).
- **PEG ratio (approx.):** P/E ~31.8 ÷ ~30% (EPS growth) ≈ 1.1; forward estimates imply continued growth.
- **Asset turnover:** 0.88 (latest); down from 1.11 (FY22) as asset base grew (PP&E, fulfillment, AWS).

---

## Metrics to monitor

- **FCF margin and CapEx:** FCF margin fell to 1.07% on a large CapEx increase ($131.8B in FY25); monitor whether CapEx moderates and FCF margin recovers toward prior-year levels (e.g. 5%+).
- **ROIC sustainability:** ROIC improved from a low FY22 base but declined YoY (10.7% vs 13.3%); track that incremental investments earn above cost of capital.
- **Revenue deceleration:** Growth ~12% YoY; watch AWS, ads, and retail for any slowdown vs consensus.
- **EPS consistency vs consensus:** Strong recent EPS recovery from FY22 loss; monitor execution and margin expansion vs expectations.
- **Rule of 40:** Currently Solid (23.5); operating margin expansion is the main lever alongside revenue growth.
- **Capital intensity:** Fulfillment, AWS, and other investments may keep CapEx elevated; balance growth and FCF conversion.

---

## Caveats

- **Data source:** FMP API v3 (income statement, cash flow, key-metrics, ratios, financial-growth, annual, limit 5). Quote and profile for context.
- **EPS:** FMP provides GAAP diluted EPS; report uses **EPS (GAAP)**. FY22 was a net loss; 3yr CAGR for EPS is not computed (negative base).
- **FCF margin:** Computed as (operatingCashFlow − capitalExpenditure) / revenue. FY25 CapEx increased materially (investments in property, plant & equipment). FY22 and FY21 FCF were negative.
- **ROIC:** From key-metrics `roic` (decimal). FY22 ROIC was very low (1.83%); 3yr CAGR of the ratio reflects recovery from that base.
- For earnings timing run `/earnings-calendar AMZN`. For trade ideas run `/options-scan AMZN`.
