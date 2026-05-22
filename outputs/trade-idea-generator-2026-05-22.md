# Trade Idea Generator - 2026-05-22

> Educational trade planning output. Not financial advice. Verify quotes, liquidity, and portfolio risk before placing trades.

## Market Context

- **As of:** 2026-05-22 10:12 EDT
- **Portfolio value:** $1.21M
- **Universe:** 20 current positions + 26 watchlist names
- **SPY:** $746.23 (0.5% today)
- **VIX:** 16.8

## Top Trade Ideas

### 1. Cash-Secured Put: LRCX

- **Action:** Sell put only if willing to own shares at breakeven
- **Score:** 89.7
- **Price:** $309.59 | **Day change:** 2.4% | **RSI:** 68.3
- Contract: O:LRCX260618P00280000 2026-06-18 $280 PUT @ bid $8.95 (delta -0.26, DTE 27, OI 1259, ann. yield 43.2%)
- **Rationale:**
  - Watchlist grade B with score 67.4 (⭐ Top Candidate).
  - Price $309.59 is above 50-day SMA $255.87.
  - RSI is 68.3; avoids the most extended entry zones.
- **Management:**
  - Size within 5% max position risk and keep total short-premium exposure under 30%.
  - Close at 50% max profit; stop or roll near 200% of credit.

### 2. Cash-Secured Put: TSM

- **Action:** Sell put only if willing to own shares at breakeven
- **Score:** 88.7
- **Price:** $406.92 | **Day change:** -0.1% | **RSI:** 52.0
- Contract: O:TSM260618P00380000 2026-06-18 $380 PUT @ bid $7.10 (delta -0.25, DTE 27, OI 5658, ann. yield 25.3%)
- **Rationale:**
  - Watchlist grade B- with score 61.8 (⭐ Top Candidate).
  - Price $406.92 is above 50-day SMA $373.15.
  - RSI is 52.0; avoids the most extended entry zones.
- **Management:**
  - Size within 5% max position risk and keep total short-premium exposure under 30%.
  - Close at 50% max profit; stop or roll near 200% of credit.

### 3. Cash-Secured Put: KLAC

- **Action:** Sell put only if willing to own shares at breakeven
- **Score:** 88.7
- **Price:** $1891.97 | **Day change:** 2.7% | **RSI:** 62.7
- Contract: O:KLAC260618P01740000 2026-06-18 $1740 PUT @ bid $42.00 (delta -0.26, DTE 27, OI 65, ann. yield 32.6%)
- **Rationale:**
  - Watchlist grade B- with score 61.3 (⭐ Top Candidate).
  - Price $1891.97 is above 50-day SMA $1692.36.
  - RSI is 62.7; avoids the most extended entry zones.
- **Management:**
  - Size within 5% max position risk and keep total short-premium exposure under 30%.
  - Close at 50% max profit; stop or roll near 200% of credit.

### 4. Cash-Secured Put: LLY

- **Action:** Sell put only if willing to own shares at breakeven
- **Score:** 77.8
- **Price:** $1062.07 | **Day change:** 2.0% | **RSI:** 70.2
- Contract: O:LLY260618P01010000 2026-06-18 $1010 PUT @ bid $15.25 (delta -0.27, DTE 27, OI 178, ann. yield 20.4%)
- **Rationale:**
  - Watchlist grade C+ with score 58.7 (Consider).
  - Price $1062.07 is above 50-day SMA $943.31.
  - RSI is 70.2; avoids the most extended entry zones.
- **Management:**
  - Size within 5% max position risk and keep total short-premium exposure under 30%.
  - Close at 50% max profit; stop or roll near 200% of credit.

### 5. Cash-Secured Put: NOW

- **Action:** Sell put only if willing to own shares at breakeven
- **Score:** 76.0
- **Price:** $101.90 | **Day change:** 2.2% | **RSI:** 63.1
- Contract: O:NOW260618P00095000 2026-06-18 $95 PUT @ bid $2.95 (delta -0.29, DTE 27, OI 3069, ann. yield 42.0%)
- **Rationale:**
  - Price $101.90 is above 50-day SMA $98.12.
  - RSI is 63.1; avoids the most extended entry zones.
- **Management:**
  - Size within 5% max position risk and keep total short-premium exposure under 30%.
  - Close at 50% max profit; stop or roll near 200% of credit.

## Earnings Watch

- ADBE: 2026-06-11 (20 days)
- ADSK: 2026-05-28 (6 days)
- AVGO: 2026-06-03 (12 days)
- COST: 2026-05-28 (6 days)
- CRM: 2026-05-27 (5 days)
- CRWD: 2026-06-03 (12 days)
- MRVL: 2026-05-27 (5 days)
- PANW: 2026-06-02 (11 days)

## Process Notes

- Inputs: `context/portfolio-details.md` and `context/watchlist.md`.
- Market data: FMP quotes, historical prices, and earnings calendar.
- Options data: Massive.com snapshots when `MASSIVE_API_KEY` is configured.
- Filters favor 25-55 DTE, liquid contracts, 0.20-0.30 delta, no near-term earnings, and existing Altamira sizing rules.
