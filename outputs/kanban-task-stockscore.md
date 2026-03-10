# Kanban Task: Stock Scoring System (/stockscore command)

**Task ID:** stockscore-001  
**Created:** 2026-02-18  
**Status:** Ready for Implementation  
**Priority:** High  
**Category:** Financial Analysis / Portfolio Management

---

## Task Description

Develop a comprehensive stock scoring system (`/stockscore` command) that calculates Quality, Growth, Value, Health, and Shareholder scores for tickers using FMP API data. Score all current portfolio holdings and evaluate new entrants before adding to portfolio.

---

## Requirements

1. **Scoring Components** (each 0-100):
   - Quality Score: ROE (0.25), ROA (0.20), Margin (0.20), ROIC (0.20), Debt/Capital (0.15)
   - Growth Score: Revenue (0.30), Earnings (0.30), FCF (0.25), FCF/Share (0.15)
   - Value Score: PE (0.25), PB (0.20), PS (0.15), FCF Yield (0.15), Margin of Safety (0.25)
   - Health Score: Debt (0.30), Liquidity (0.35), Coverage (0.35)
   - Shareholder Score: Div Yield (0.30), Div Growth (0.25), Buyback Yield (0.25), Debt Paydown (0.20)

2. **Composite Score & Grade**:
   - Composite = average of 5 component scores
   - Grade: A+ (90+), A (85+), A- (80+), B+ (75+), B (70+), B- (65+), C+ (60+), C (55+), C- (50+), D+ (45+), D (40+), F (<40)

3. **Strengths/Weaknesses**:
   - Strength threshold: >= 70
   - Weakness threshold: < 50

4. **Functionality**:
   - Score all current portfolio holdings (from `context/portfolio-details.md`)
   - Score new entrants before adding to portfolio
   - Fetch data from FMP API (latest dataset)
   - Generate markdown reports in `outputs/`

---

## Implementation Status

- [x] Command file created: `.claude/commands/stockscore.md`
- [x] Scoring logic implemented: `scripts/stock-scorer.py` (Python script)
- [x] FMP API integration tested (working with all endpoints)
- [x] All current holdings scored (21 tickers: SPY, AVGO, GOOGL, AMAT, MSFT, AMZN, AAPL, CRWD, COST, ABBV, GD, V, JPM, KMI, WM, FFOLX, QQQ, NOW, SPGI, NFLX)
- [x] Reports generated: `outputs/stock-score-{TICKER}-{DATE}.md` and `outputs/portfolio-scores-{DATE}.md`
- [x] Documentation updated: Command file references script, reference document created

---

## Related Files

- Command: `.claude/commands/stockscore.md`
- Portfolio holdings: `context/portfolio-details.md`
- FMP API key: `FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz`
- Reference scoring logic: See screenshots/images provided

---

## Acceptance Criteria

- [x] `/stockscore` command executes successfully (via `python scripts/stock-scorer.py`)
- [x] All 21 current portfolio holdings scored (including ETFs/indices)
- [x] Reports generated in `outputs/stock-score-{TICKER}-{DATE}.md` format
- [x] Portfolio summary report: `outputs/portfolio-scores-{DATE}.md`
- [x] Composite scores and grades calculated correctly (5 component scores → composite → letter grade)
- [x] Strengths/weaknesses identified per thresholds (>=70 strength, <50 weakness)
- [x] New entrants can be evaluated before portfolio addition (`python scripts/stock-scorer.py TICKER`)

**Status:** ✅ **COMPLETE** — All acceptance criteria met. Script operational and tested.

---

**Add to kanban board:** This task should be added to the Financial Data Automation project on the kanban board (localhost:3004). Priority: High — supports portfolio optimization and $5M AUM growth goal.
