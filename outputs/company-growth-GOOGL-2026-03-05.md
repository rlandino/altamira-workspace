# Company Growth Evaluation — GOOGL (Alphabet Inc.)

**Report date:** 2026-03-05  
**Summary:** Growth evaluation using core four metrics (Revenue, EPS, FCF margin, ROIC) plus margins, Rule of 40, and revenue trajectory.

---

## Core growth metrics (grade drivers)

| Metric | 3yr CAGR % | Latest YoY % | Latest value |
|--------|-------------|---------------|--------------|
| **Revenue** | 12.56 | 15.13 | $403.0B |
| **EPS (GAAP diluted)** | 33.25 | 34.45 | $10.81 |
| **Free cash flow margin** | -4.9* | -2.6 pp | 18.19% |
| **ROIC** | 1.13 | -15.4 | 21.82% |

*FCF margin 3yr CAGR is the CAGR of the margin ratio (18.19% vs 21.22% three years ago); margin stepped down on higher CapEx intensity. FCF = operating cash flow − capital expenditure; margin = FCF / revenue.

---

## Grade

**Grade: A.**

**Reason for grade:** Revenue growth is solid (3yr CAGR 12.6%, latest YoY 15.1%)—in the B band but strong. EPS growth is very strong (3yr CAGR 33.3%, YoY 34.5%), clearly A. FCF margin is high at 18.2% and above 15% despite a step down YoY from heavy CapEx (AI/datacenter), supporting A on level. ROIC at 21.8% is above 20% and above cost of capital, also A despite a YoY decline. With three core metrics in the A band and one (revenue) in B, the composite is A.

---

## Optional metrics

- **Operating margin:** 32.05% (latest); flat YoY (32.10% prior year). 3yr trend: up from 26.46% (FY22) to 32.05%.
- **Net income growth:** 3yr CAGR 30.2%; latest YoY 32.01%.
- **Gross margin:** 59.67% (latest); up from 55.38% (FY22).
- **EBITDA margin:** 44.66% (latest); up from 30.11% (FY22).
- **ROE:** 31.83% (latest); up from 23.41% (FY22).
- **FCF (dollars) growth:** 3yr CAGR 6.9%; latest YoY 0.7% (CapEx step-up in FY25).
- **Rule of 40:** Revenue growth 15.13% + Operating margin 32.05% = **47.2** → **Elite** (≥40).
- **Revenue growth trajectory:** **Accelerating** in recent periods (FY22 9.8%, FY23 8.7%, FY24 13.9%, FY25 15.1%).
- **PEG ratio (approx.):** P/E ~27.8 ÷ ~32% (EPS growth) ≈ 0.87 (growth not fully reflected in multiple by this simplification).
- **Asset turnover:** 0.68 (latest); 3yr trend stable to slightly down as asset base grew.

---

## Metrics to monitor

- **FCF margin and CapEx:** FCF margin stepped down to 18.2% on materially higher CapEx (AI/datacenter); monitor whether CapEx intensity moderates and FCF margin stabilizes or recovers.
- **ROIC trend:** ROIC declined YoY (21.8% vs 25.8%); track that incremental investments earn above cost of capital and ROIC stabilizes.
- **Revenue deceleration risk:** Growth re-accelerated to 15% YoY; watch for any slowdown in Search, Cloud, or YouTube vs consensus.
- **EPS consistency vs consensus:** Strong recent EPS growth; monitor execution vs elevated expectations and buyback support.
- **Rule of 40 sustainability:** Currently Elite; operating margin and revenue growth are the two levers to watch.
- **Regulation and competition:** Antitrust and AI/search competition could affect growth and margins over time.

---

## Caveats

- **Data source:** FMP API v3 (income statement, cash flow, key-metrics, ratios, financial-growth, annual, limit 5). Quote and profile for context.
- **EPS:** FMP provides GAAP diluted EPS; report uses **EPS (GAAP)**. No non-GAAP adjustment applied.
- **FCF margin:** Computed as (operatingCashFlow − capitalExpenditure) / revenue for the same fiscal year. CapEx is investments in property and equipment from cash flow statement.
- **ROIC:** From key-metrics `roic` (decimal). FY25 ROIC declined vs FY24 on higher invested capital (e.g. CapEx, acquisitions).
- For earnings timing run `/earnings-calendar GOOGL`. For trade ideas run `/options-scan GOOGL`.
