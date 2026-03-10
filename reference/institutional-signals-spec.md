# Institutional Signals — Options Chain Analyzer (OCA)

Specification for the 12 institutional signals used in the CSP Daily Scan workflow and options-scan reports.

---

## 1. Put/Call Ratio

**Purpose:** Gauge options market sentiment (put-heavy = bearish/hedging, call-heavy = bullish).

| Variant | Formula | Interpretation |
|--------|---------|----------------|
| **Volume** | Put Volume / Call Volume | Short-term flow; >1 = more put volume |
| **Open Interest** | Put OI / Call OI | Positioning; >1 = more put OI |
| **Dollar-Weighted** | Put $ (premium×vol) / Call $ | Size-weighted flow; >1 = more $ in puts |

**Per-ticker:** Computed over 20–60 DTE options. Pass-through to scorer and Telegram.

---

## 2. Unusual Options Activity (UOA)

**Purpose:** Flag contracts with disproportionate volume vs open interest (potential institutional flow).

| Signal | Rule | Meaning |
|--------|------|--------|
| **Volume/OI** | Volume > 2× Open Interest | Unusual volume relative to existing OI |
| **Large blocks** | Single-trade premium > $100,000 (or notional > threshold) | Institutional-sized trades |

**Output:** Count of unusual contracts per ticker; binary “has UOA” and optional list of strikes.

---

## 3. IV Skew

**Purpose:** Compare OTM put vs OTM call implied volatility (skew reflects demand for downside protection).

| Metric | Definition |
|--------|-------------|
| **25-Delta Put IV** | IV of put with delta ≈ -0.25 |
| **25-Delta Call IV** | IV of call with delta ≈ +0.25 |
| **25-Delta Skew** | Put IV / Call IV (or Put IV − Call IV in vol points) |

**Interpretation:** Skew > 1 (or put IV > call IV) = typical; elevated skew = more put demand / tail hedging.

---

## 4. Dealer Gamma Exposure (GEX)

**Purpose:** Estimate dealer hedging impact (positive gamma = dealers hedge by selling into rallies / buying dips, dampening moves).

| Metric | Formula |
|--------|----------|
| **GEX (per strike)** | Γ × OI × 100 × Spot² (convention: long options = positive gamma for dealer when they are short) |
| **Total GEX** | Sum of GEX across strikes (use same sign convention as your source) |
| **Max Gamma Strike** | Strike where \|GEX\| is largest (often near ATM) |

**Output:** Total GEX (scaled), max-gamma strike, and optional GEX profile by strike for display.

---

## 5. Net Options Sentiment

**Purpose:** Single composite score for “options market sentiment” from -100 (max put/bearish) to +100 (max call/bullish).

**Inputs (normalized and combined):**
- Put/Call ratios (volume, OI, dollar-weighted)
- IV skew (e.g. high put skew → more negative sentiment)
- Unusual activity (e.g. put UOA → more negative)
- Optional: GEX level (e.g. large negative GEX → more negative)

**Formula (example):**
- Map P/C ratios to a -1 to +1 scale (e.g. P/C > 1 → negative).
- Map skew to -1 to +1.
- Weight and sum, then scale to -100 to +100.

**Output:** `netSentiment` integer -100 to +100; optional breakdown by component.

---

## 6. Confidence Score Adjustment (Institutional Flow)

**Purpose:** Adjust the OCA composite score when institutional flow aligns or conflicts with the trade.

| Rule | Adjustment |
|------|------------|
| Selling puts + Net Sentiment bullish (e.g. > 20) | +3 to +5 to composite score |
| Selling puts + Net Sentiment bearish (e.g. < -20) | -3 to -5 |
| Put UOA on same ticker | Optional small negative adjustment |
| Neutral sentiment | 0 |

**Output:** `confidenceAdjustment` (e.g. -5 to +5) applied to composite score before VIX adjustment.

---

## 7. VIX Regime Detection

**Purpose:** Classify current volatility regime for sizing and strategy choice.

| VIX Level | Regime | Label |
|-----------|--------|--------|
| &lt; 15 | Low | LOW |
| 15–25 | Normal | NORMAL |
| 25–35 | Elevated | ELEVATED |
| &gt; 35 | Crisis | CRISIS |

**Source:** FMP quote for ^VIX (or equivalent). Already implemented in Fundamental Quality Screen; pass-through to scorer and signals.

---

## 8. VIX-Adjusted Position Sizing

**Purpose:** Scale max position size by regime (reduce size in high vol).

| Regime | Sizing % |
|--------|----------|
| LOW | 75% |
| NORMAL | 100% |
| ELEVATED | 50% |
| CRISIS | 25% |

**Usage:** `maxAllocation = portfolioValue × maxPositionPct × (sizingPct / 100)`. Already in CSP Opportunity Scorer.

---

## 9. VIX-Adjusted Confidence

**Purpose:** Reduce effective confidence of recommendations in high-vol regimes.

| Regime | Confidence multiplier |
|--------|------------------------|
| LOW | 1.0 |
| NORMAL | 1.0 |
| ELEVATED | 0.90 |
| CRISIS | 0.75 |

**Usage:** `adjustedScore = (compositeScore + confidenceAdjustment) × vixConfidenceMultiplier`.

---

## 10. Regime-Specific Strategies

**Purpose:** Suggest strategy type by regime.

| Regime | Preferred | Avoid / Reduce |
|--------|-----------|-----------------|
| LOW | Naked CSP, covered calls | — |
| NORMAL | CSP, bull put spreads, covered calls | — |
| ELEVATED | Defined-risk spreads, reduce size | Naked CSP |
| CRISIS | Spreads only, minimal size | Naked options, large delta |

**Output:** Short text (e.g. “Prefer spreads; reduce size”) for Telegram and reports.

---

## 11. Liquidity Score (1–10)

**Purpose:** Single 1–10 score for contract/ticker liquidity.

**Inputs:**
- Bid-ask spread as % of mid
- Open interest (tiers)
- Volume (tiers)

**Example mapping:**
- Spread &lt; 5%, OI &gt; 500, Vol &gt; 50 → 9–10
- Spread 5–10%, OI 100–500, Vol 10–50 → 6–8
- Spread &gt; 10% or OI &lt; 50 or Vol &lt; 10 → 1–4

**Output:** Integer 1–10 per contract or per ticker (e.g. best contract in chain).

---

## 12. Backtesting

**Purpose:** Use historical scan results to evaluate signal and strategy performance.

**Data source:** Daily scan results logged to Google Sheets (e.g. “CSP Scans”, “Scan Backtest”):
- Date, VIX, regime, top 3 tickers, strikes, scores, key institutional signals (P/C, net sentiment, GEX, etc.).

**Metrics (run offline, e.g. Python script):**
- Hit rate: % of recommended strikes that would have been profitable (e.g. closed at 50% profit).
- Average return per trade (premium captured vs max loss).
- Performance by VIX regime and by net sentiment bucket.
- Correlation of institutional signals with subsequent P&L.

**Workflow integration:** “Prepare Sheets Row” (and optional “Backtest Snapshot” node) writes one row per scan so that a separate backtest script can read the sheet and compute these metrics.

---

## Implementation Notes

- **Fetch Full Chains (Institutional):** Fetches both calls and puts (20–60 DTE) via Massive.com v3 snapshot API so P/C, UOA, skew, and GEX can be computed.
- **Institutional Signals node:** Consumes full chains + VIX/regime; outputs per-ticker object (P/C ratios, UOA, IV skew, GEX, max gamma strike, net sentiment, liquidity 1–10, confidence adjustment, regime strategy text).
- **CSP Opportunity Scorer:** Reads institutional signals when present; applies confidence adjustment and VIX-adjusted confidence; attaches liquidity 1–10 and regime strategy to each opportunity; passes institutional summary to Telegram/Sheets.
- **Backtesting:** No change to execution path; ensure Sheets columns include at least: Date, VIX, Regime, Ticker1–3, Strike1–3, Score1–3, NetSentiment, PutCallRatioVol, GEX (or equivalent) so backtest scripts can use them.
