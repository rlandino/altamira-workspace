# Portfolio Details (Workspace Context Export)

> Exported for Claude and scripts. **Source:** Local Streamlit app at http://localhost:8501/Portfolio (dashboard export below). Also synced from Google Sheet "Daily Dashboard" + "Position History" or `context/portfolio-export.json` via `python scripts/refresh-portfolio-context.py --sheets` or `--local`.

---

## Portfolio Summary (from app dashboard)

**Altamira Capital goal:** Grow this portfolio to **$5M AUM**. Current AUM ~$1.21M (~24% of goal).

| Metric | Value |
|--------|--------|
| **Total MKT VALUE** | $1,207,271 |
| **Total COST BASIS** | $717,653 |
| **Total P&L** | +$489,618 (+68.2%) |
| **Total DAY CHG** | +$7,887 (+0.7%) |
| **Total WEIGHT** | 100.0% |

---

## Source Data

| Source | Location | Updated |
|--------|----------|--------|
| **Daily Dashboard** | Google Sheet (same as n8n) or `context/portfolio-export.json` | n8n @ 4:15 PM ET or manual export |
| **Position History** | Google Sheet "Position History" | n8n @ 4:15 PM ET |
| **Streamlit app** | http://localhost:8501/Portfolio (app source not in this workspace) | Displays the above |

---

## Latest Dashboard Snapshot

| Field | Value |
| ----- | ----- |
| Date | 2026-02-18 |
| Portfolio Value | 102,500.50 |
| Daily P&L ($) | 150.25 |
| Daily P&L (%) | 15.00% |
| Cumulative P&L ($) | 2,500.50 |
| Cumulative P&L (%) | 2.50 |
| Net Delta Exposure | 12.50 |
| Daily Theta Income | 45.00 |
| Open CSP Count | 2 |
| Open Equity Positions | 3 |
| Cash % | 22.50 |
| VIX Close | 14.20 |
| SPY Close | 502.75 |

---

## Current Positions (from app dashboard)

*(Sorted by MKT VALUE descending.)*

| SYMBOL | QTY | AVG. PRICE | CURRENT | MKT VALUE | COST BASIS | P&L ($, %) | DAY CHG ($, %) | WEIGHT |
|--------|-----|------------|---------|-----------|------------|------------|----------------|--------|
| SPY | 300.00 | $479.00 | $686.29 | $205,887 | $143,700 | +$62,187 (+43.3%) | +$1,032 (+0.5%) | 17.1% |
| AVGO | 606.00 | $121.11 | $333.51 | $202,107 | $73,393 | +$128,714 (+175.4%) | +$588 (+0.3%) | 16.7% |
| GOOGL | 551.00 | $174.33 | $303.33 | $167,135 | $96,056 | +$71,079 (+74.0%) | +$722 (+0.4%) | 13.8% |
| AMAT | 413.00 | $184.18 | $369.30 | $152,521 | $76,066 | +$76,455 (+100.5%) | +$4,200 (+2.8%) | 12.6% |
| MSFT | 201.00 | $328.29 | $399.60 | $80,320 | $65,986 | +$14,333 (+21.7%) | +$551 (+0.7%) | 6.7% |
| AMZN | 288.00 | $113.32 | $204.79 | $58,980 | $32,636 | +$26,343 (+80.7%) | +$1,048 (+1.8%) | 4.9% |
| AAPL | 212.00 | $181.50 | $264.35 | $56,042 | $38,478 | +$17,564 (+45.6%) | +$100 (+0.2%) | 4.6% |
| CRWD | 126.00 | $354.91 | $415.76 | $52,386 | $44,719 | +$7,667 (+17.1%) | +$186 (+0.4%) | 4.3% |
| COST | 50.00 | $741.38 | $996.08 | $49,804 | $37,069 | +$12,735 (+34.4%) | -$798 (-1.6%) | 4.1% |
| ABBV | 202.00 | $133.85 | $228.72 | $46,201 | $27,038 | +$19,164 (+70.9%) | -$836 (-1.8%) | 3.8% |
| GD | 76.00 | $176.92 | $349.49 | $26,561 | $13,446 | +$13,115 (+97.5%) | +$530 (+2.0%) | 2.2% |
| V | 82.00 | $234.77 | $320.28 | $26,263 | $19,251 | +$7,012 (+36.4%) | +$64 (+0.2%) | 2.2% |
| JPM | 82.00 | $114.18 | $308.78 | $25,320 | $9,363 | +$15,957 (+170.4%) | +$135 (+0.5%) | 2.1% |
| KMI | 661.00 | $16.80 | $32.29 | $21,344 | $11,105 | +$10,239 (+92.2%) | +$106 (+0.5%) | 1.8% |
| WM | 40.00 | $90.07 | $234.06 | $9,362 | $3,603 | +$5,760 (+159.9%) | -$46 (-0.5%) | 0.8% |
| FFOLX | 250.21 | $20.77 | $32.08 | $8,027 | $5,197 | +$2,830 (+54.5%) | +$33 (+0.4%) | 0.7% |
| QQQ | 13.00 | $426.42 | $605.79 | $7,875 | $5,543 | +$2,332 (+42.1%) | +$58 (+0.7%) | 0.7% |
| NOW | 52.00 | $167.77 | $107.81 | $5,606 | $8,724 | -$3,118 (-35.7%) | +$99 (+1.8%) | 0.5% |
| SPGI | 13.00 | $475.95 | $419.38 | $5,452 | $6,187 | -$735 (-11.9%) | +$116 (+2.2%) | 0.5% |
| NFLX | 1.00 | $93.40 | $77.99 | $78 | $93 | -$15 (-16.5%) | +$1 (+1.2%) | 0.0% |

**Totals:** MKT VALUE $1,207,271 · COST BASIS $717,653 · P&L +$489,618 (+68.2%) · DAY CHG +$7,887 (+0.7%)

---

## Options / Short Premium Positions

*(For theta and options context. Credit/Current in $ per share; ×100 = per contract.)*

| Ticker | Strike | Type | Expiration | Credit | Current | Contracts |
|--------|--------|------|------------|--------|---------|-----------|
| MSFT | 430 | Put | 2026-03-20 | 8.70 | 22.40 | 5 |
| MSFT | 380 | Put | 2026-05-15 | 10.12 | 11.80 | 5 |
| AVGO | 310 | Put | 2026-03-20 | 12.60 | 5.00 | 5 |
| SPY | 620 | Put | 2026-05-15 | 6.92 | 10.16 | 5 |
| COST | 900 | Put | 2026-05-15 | 11.00 | 12.40 | 5 |

**Last updated:** 2025-03-07. See `context/options-positions.md` for the same list used by `/sig-daily-theta-decay-calculator`.

---

*Portfolio summary and positions: from local app dashboard (http://localhost:8501/Portfolio). Snapshot section: from context/portfolio-export.json or script. Re-export from the app to refresh positions; run `python scripts/refresh-portfolio-context.py --sheets` or `--local` to refresh snapshot.*
