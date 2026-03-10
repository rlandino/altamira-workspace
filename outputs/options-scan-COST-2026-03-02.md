# Options Scan — COST (Costco Wholesale Corporation)
**Scan date:** 2026-03-02

---

## 1. Market Context

| Metric | Value |
|--------|--------|
| **Price** | $1,007.77 |
| **Day change** | +$5.00 (+0.50%) |
| **50-day avg** | $945.37 |
| **200-day avg** | $951.40 |
| **52-week range** | $844.06 – $1,067.08 |
| **VIX** | 22.58 |
| **VIX regime** | **NORMAL** (15–25) |

**Earnings:** Next report **2026-03-05** (AMC). Earnings are in **3 days** — inside the typical 20–60 DTE window for premium selling. IV crush and event risk are high for any short-dated options.

**Technical note:** 30-day history from FMP timed out; quote shows price above 50- and 200-day averages (bullish trend context).

---

## 2. Options Chain Summary

- **Source:** Massive.com API (`/v3/snapshot/options/COST`, limit 250).
- **Result:** 250 contracts returned. Expirations in this snapshot: **2026-03-06** (246 contracts) and **2026-03-13** (4 contracts) — i.e. **4 and 11 DTE** only.
- **Quotes:** All 250 contracts had **bid = 0, ask = 0** in this snapshot (likely delayed or after-hours). No liquid 20–60 DTE expirations were present in the response.
- **Implication:** Chain filtering for 20–60 DTE and institutional signals (P/C, UOA, skew, GEX) could not be computed from this run. Strategy recommendations below are based on market context and parameters only.

---

## 3. Top Recommendations

No 20–60 DTE options with usable quotes were available in the Massive snapshot. **No CSP, bull put spread, or Jade Lizard candidates** are recommended from this scan.

- **30–45 DTE sweet spot:** Not represented in the 250-contract response.
- **Earnings:** With earnings on **2026-03-05**, selling puts that expire 2026-03-06 or 2026-03-13 carries high IV crush and assignment risk. Thesis: avoid selling premium through unplanned earnings.

---

## 4. Risk Flags

| Flag | Severity | Notes |
|------|----------|--------|
| **Earnings in 3 days** | High | 2026-03-05 AMC. Avoid opening new short premium in this expiration window. |
| **No 20–60 DTE chain data** | Medium | Massive snapshot contained only 4 and 11 DTE; no 30–45 DTE data for ranking. |
| **No live quotes in snapshot** | Medium | All bid/ask were zero — re-run during market hours for actionable prices. |
| **VIX elevated vs recent** | Low | VIX 22.58 vs ~17 recent average; NORMAL regime — size at 100% per OCA. |

---

## 5. Action

**Recommendation: AVOID** for new options entries on COST at this scan time.

- **Reason:** (1) Earnings 2026-03-05 — inside expiration window for all contracts in this snapshot. (2) No 20–60 DTE options with live quotes available to run OCA criteria or strategy ranking.
- **Regime strategy:** VIX NORMAL — CSP and spreads allowed at full sizing per thesis; no reduction required.
- **Next step:** After **2026-03-05** (post-earnings), re-run `/options-scan COST` to get 30–45 DTE expirations and institutional signals, or run during regular market hours for non-zero quotes.

---

## 6. Institutional Signals (OCA)

| Signal | Value | Notes |
|--------|--------|--------|
| **Put/Call (volume)** | — | Not computed (no 20–60 DTE chain with quotes). |
| **Put/Call (OI)** | — | Not computed. |
| **UOA** | — | Not computed. |
| **IV skew (25Δ put/call)** | — | Not computed. |
| **Total GEX / max-gamma strike** | — | Not computed. |
| **Net sentiment (-100 to +100)** | — | Not computed. |
| **Confidence adjustment** | — | Not applied. |
| **VIX regime** | NORMAL | 22.58 ∈ [15, 25]. |
| **Regime strategy** | CSP, spreads, CC at full size | Per OCA spec. |
| **Liquidity score** | — | No per-contract quotes. |

**Backtest:** Backtest metrics (hit rate, return by regime/sentiment) use logged scan data per institutional-signals-spec; see CSP Scans sheet / backtest script.

---

**Summary:** COST is in a strong price trend (above 50/200 SMA) with earnings in 3 days. The options snapshot had only 4 and 11 DTE and no live bids — no 20–60 DTE recommendations or OCA signals could be produced. **AVOID** new premium selling until after 2026-03-05; then re-scan for 30–45 DTE and live quotes.
