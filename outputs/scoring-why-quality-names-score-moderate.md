# Why High-Quality Companies Get Moderate Composite Scores

**Date:** 2026-02-19

---

## Short Answer

The composite score is a **simple average of five pillars**. Many “high quality” names (MSFT, GOOGL, AAPL) score **very high on Quality and Health** but **low on Value, Growth, and Shareholder**. Those three pillars pull the average down, so the **composite looks moderate (C / C-)** even when Quality is A+.

The model is **not broken**—it is **strict by design** and treats “quality” and “cheap/income/growth” separately. You can keep it as-is for discipline, or relax it slightly so more strong-but-expensive names land in C+ / B-.

---

## Why It Happens (Example: MSFT)

| Pillar       | Score  | Grade | Why |
|-------------|--------|-------|-----|
| **Quality** | 89.67  | A+    | Strong ROE, ROA, margin, ROIC, low debt. |
| **Health**  | 79.03  | A-    | Solid liquidity and interest coverage. |
| **Growth**  | 27.57  | F     | Mature mega-cap: single-digit revenue/earnings growth. |
| **Value**   | 33.82  | F     | P/E 36, P/B 11, P/S 13 → premium valuation. |
| **Shareholder** | 43.44 | D+  | Modest dividend and buybacks vs. income benchmarks. |

**Composite = (90 + 28 + 34 + 79 + 43) / 5 ≈ 55 → C.**

So: **the company is graded “high quality” on profitability and balance sheet, but “expensive” and “low growth / low shareholder yield” on the other pillars.** The composite mixes all of that equally, so it ends up in the middle.

Same pattern for **GOOGL** (Quality 91, Health 87, Shareholder 3.8 → composite C) and **AAPL** (Quality 87, Growth/Value/Shareholder weak → C-).

---

## Is the Scoring “Too Harsh”?

- **If the goal is “find great businesses at reasonable prices with growth and shareholder return,”** the current design is **not too harsh**—it correctly penalizes expensive valuations and low growth/dividends.
- **If the goal is “rank companies by how good the business is, even if expensive,”** then the **equal-weight composite is harsh** for quality names, because Value, Growth, and Shareholder are not what make them “high quality” in that sense.

So: **harsh for “quality only” interpretation; fair for “all-around” (quality + value + growth + shareholder) interpretation.**

---

## Options to Recalibrate

### 1. **Relax grade thresholds (modest)**

- Lower each grade cutoff by **2–3 points** (e.g. C+ from 55 → 52, C from 50 → 47).
- **Effect:** Names like MSFT (54.7) move from C to **C+**; more “good but not perfect” names get C+ or B-.
- **Pros:** Simple, no change to component logic.  
- **Cons:** Every grade shifts up; “C” no longer means the same absolute bar.

### 2. **Add a “Quality-weighted” composite (optional)**

- Keep current composite as **equal-weight**.
- Add a second composite: e.g. **Quality 30%, Growth 20%, Value 20%, Health 15%, Shareholder 15%**.
- **Effect:** Companies with high Quality/Health (MSFT, GOOGL) get a **higher quality-weighted score** and can show B- or B while still showing a stricter equal-weight C.
- **Pros:** One number for “all-around,” one for “quality tilt”; no need to make the main composite softer.  
- **Cons:** Two composites to explain and maintain.

### 3. **Keep as-is and interpret by pillar**

- Don’t change math; **use the report as-is**: look at **Composite for overall**, and **Quality + Health** for “is this a strong business?”
- **Effect:** No code changes; you accept that “high quality” often means “A Quality, C composite” for expensive, mature, low-dividend names.

---

## Recommendation

- **Keep component logic and data as-is**—they are consistent and explainable.
- **Option 1 (relax thresholds by 2–3 points)** is a reasonable compromise if you want more C+ / B- for names like MSFT without changing what each pillar means.
- **Option 2 (quality-weighted composite)** is useful if you want to see both a “strict” and a “quality-friendly” number in the same report.

If you tell me which you prefer (threshold relaxation only, add quality-weighted only, or both), I can outline the exact code/report changes next.
