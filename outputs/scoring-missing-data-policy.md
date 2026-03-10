# Stock Scoring — Missing Data Policy

**Date:** 2026-02-19

---

## Policy: Missing Data Is Never Counted Against the Company

- **No metric is assigned a score when data is missing.**  
  If a metric (e.g. ROIC, revenue growth, dividend yield) is unavailable (`None` or not present), that metric is **excluded** from its component. It is never given 0 or a low score.

- **Weights are redistributed among available metrics only.**  
  For each component (Quality, Growth, Value, Health, Shareholder), the weight of any excluded metric is redistributed proportionally to the metrics that *are* available. So the component score is based only on what we have.

- **If a component has no available metrics, it returns 50.0 (neutral).**  
  So missing data does not pull the composite down; at worst it leaves that pillar neutral.

- **We never treat “missing” as “zero” for scoring.**  
  In code, we use `.get(key)` (no default) for metrics that feed into scores, so missing stays `None` and is excluded. We avoid `.get(key, 0)` for such metrics so that missing is not interpreted as 0% growth, 0 ROE, etc.

---

## Implementation Summary

| Area | Behavior |
|------|----------|
| **Quality** | ROE, ROA, margin, ROIC, debt/equity: only added to `available_metrics` when we have a value. If missing, we try to calculate from statements; if still missing, we exclude and redistribute. |
| **Growth** | Revenue growth, earnings growth, FCF growth, FCF/share growth: only added when we have data (from API or calculated). No default 0 for growth. |
| **Value** | P/E, P/B, P/S, FCF yield, margin of safety: only included when available. FCF yield is only included when positive (0 is excluded so “missing” isn’t scored as 0). |
| **Health** | Debt, liquidity, coverage: only included when we have a value; otherwise we try to calculate from statements, then exclude if still missing. |
| **Shareholder** | Div yield, div growth, buyback yield, debt paydown: only included when we have data. Div yield `None` = excluded (no penalty). |
| **normalize_score** | If `value` is `None`, returns 50.0 (neutral). We still only call it when we have decided to include the metric, so missing metrics are excluded before normalization. |
| **is_growth_company** | Uses `.get("returnOnEquity")` and `.get("revenueGrowth")` without default 0 so missing is not treated as 0% growth or 0 ROE. |

---

## Changes Made (2026-02-19)

1. **is_growth_company:** ROE and revenue growth now use `.get(key)` without default 0; missing is handled as `None` and not used.
2. **Quality score docstring:** Explicit “missing data policy” added (exclude + redistribute; no score for missing).
3. **Report footer:** Added sentence: “Missing data: excluded; weights redistributed (no penalty).”
4. **This document:** Written so the policy is clear and auditable.

---

*Low scores are therefore driven by **reported** fundamentals (e.g. high P/E, low growth, no dividend), not by lack of data.*
