# Current Data

> This file holds metrics, data points, and current state information relevant to your role and strategy. It provides Claude with concrete context for analysis and decision-making.

---

## How This Connects

- **business-info.md** provides organizational context
- **personal-info.md** defines what you're responsible for
- **strategy.md** outlines what you're optimizing toward
- **This file** gives Claude the numbers behind the narrative

---

## Key Metrics

| Metric | Current Value | Target | Notes |
| ------ | ------------- | ------ | ----- |
| Active n8n workflows | ~15 | 30+ | Daily financial, newsletters, idea generator |
| Claude skills built | ~25 | 50+ | Financial, SEO, social media, reporting. 7 financial commands deployed (analyze-ticker, options-scan, portfolio-report, paper-trade, client-report, thesis, stockscore) |
| Kanban board projects | 25+ | — | Financial data automation projects queued |
| Daily automated reports | 1 | 5+ | Financial analysis workflow |
| Options strategies automated | 0 | 3+ | Put-selling, earnings, hedging — thesis and infra checklist complete |

## Deliverables

| Document | Path | Created | Status |
|----------|------|---------|--------|
| Investment Thesis v2.0 | `outputs/altamira-investment-thesis.md` | 2026-02-18 | **Final v2.0** — backtest-validated, 6 principles, circuit breakers, updated roadmap |
| Trading Infrastructure Checklist | `outputs/trading-infrastructure-setup.md` | 2026-02-17 | Draft v1.0 — addresses alt-task-01 |
| Risk Management Framework | `outputs/risk-management-framework.md` | 2026-02-18 | **Final v1.0** — position sizing formulas, drawdown tiers, circuit breakers, stress tests, scaling $100K→$5M |
| Portfolio Allocation Model | `outputs/portfolio-allocation-model.md` | 2026-02-18 | **Final v1.0** — 5-sleeve model (Options 35%, Momentum 20%, Conviction 15%, Hedging 0-3%, Cash 20%), VIX regimes, rebalancing rules |
| Paper Trading Launch Plan | `outputs/paper-trading-plan.md` | 2026-02-18 | **Final v1.0** — 4-week phased rollout (Mar 1–28), 15 go-live criteria, 38 action items, Google Sheets spec, n8n workflows |
| E-Trade API Setup Guide | `outputs/etrade-api-setup-guide.md` | 2026-02-18 | **Final v1.0** — 7-section action guide: account config, API keys, OAuth 1.0a testing, endpoint testing, paper trading, n8n credential setup, troubleshooting |
| Market Monitoring Workflows | `outputs/market-monitoring-workflows.md` | 2026-02-18 | **Designed** — 5 n8n workflows (watchlist alerts, IV monitor, sector rotation, risk dashboard, vol regime). Awaiting deployment. |
| Market Commenter v3.1 | Deployed to n8n cloud (workflow `OzFzqZUVv9cFAwYL`) | 2026-02-17 | Live — addresses task-mkt-34 through task-mkt-39 |
| Financial Analysis Commands | `.claude/commands/analyze-ticker.md`, `options-scan.md`, `portfolio-report.md` | 2026-02-17 | Operational — addresses alt-task-07 |
| Paper Trade Command | `.claude/commands/paper-trade.md` | 2026-02-18 | Operational — 6-point pre-trade checklist, risk limit validation, webhook logging |
| Client Report Command | `.claude/commands/client-report.md` | 2026-02-18 | Operational — professional client-facing reports (monthly/quarterly/annual). Addresses alt-task-09 |
| Investment Thesis Command | `.claude/commands/thesis.md` | 2026-02-18 | Operational — DCF valuation, comps analysis, 13-section thesis, buy/hold/avoid verdict. Addresses tg-1 through tg-3 |
| CSP Daily Scan Workflow | `outputs/n8n-workflow-csp-daily-scan.json` | 2026-02-18 | Ready to import — 17-node workflow, 10:30 AM ET scan, Massive.com + FMP, scored recommendations. Addresses csp-1 through csp-3 |
| Backtest Framework | `scripts/backtest-strategies.py` | 2026-02-18 | Operational — addresses alt-task-02. 3 strategies tested: CSP, momentum, hedging |
| Backtest Results (2Y) | `outputs/backtest-results-2026-02-18.md` | 2026-02-18 | CSP: 83% win/1.34 Sharpe; Momentum: 34.6% return/0.68 Sharpe; Hedging: minimal impact (bull mkt) |

## Current State

- **Kanban board**: 25 financial data automation projects loaded with 255 tasks, accessible at **http://localhost:3004** (app runs separately — not in this workspace). If you see *ERR_CONNECTION_REFUSED*, start the kanban app via the **Kanban Board** desktop shortcut or from the app’s project folder. See `reference/kanban-dashboard.md`.
- **Kanban export**: `context/kanban-export.csv` (exported 2026-02-17 from `localhost:3005/api/board/export`)
- **n8n workflows**: Daily financial analysis, idea generator (with Google Sheets + Telegram), AI newsletters deployed
- **Market Commenter v3.1**: Deployed 2026-02-17 — index dashboard, intraday chart, hot stock/loser, sector highlights, period performance (WTD/MTD/QTD/YTD)
- **$5M AUM growth target**: Added to goals.yaml on 2026-02-17 as key result under Goal 1
- **Skills Factory repo**: Primary development workspace with skills, workflows, and automation tools
- **Desktop shortcuts**: FinceptTerminal and Kanban Board launch scripts on desktop
- **World Monitor app**: Cloned and running at localhost:3000

## Portfolio (Dashboard)

**Source of truth:** **http://localhost:8501/Portfolio** — the local Streamlit app is the canonical view for portfolio snapshot and positions. Keep this section in sync by copying from the app into the table below, or by running `scripts/refresh-portfolio-context.py` if the app exposes a JSON API or you export data to a file.

**Latest dashboard snapshot** (from the Portfolio app):

| Field | Value | Notes |
| ----- | ----- | ----- |
| Date | 2026-02-18 | YYYY-MM-DD of snapshot |
| Portfolio Value | 102,500.50 | Total account value |
| Daily P&L ($) | 150.25 | vs previous close |
| Daily P&L (%) | 0.15% | |
| Cumulative P&L ($) | 2,500.50 | vs $100K starting capital |
| Cumulative P&L (%) | 2.50% | |
| Net Delta Exposure | 12.50 | Target range -30 to +50 per $100K |
| Daily Theta Income | 45.00 | Target positive (income) |
| Open CSP Count | 2 | Short put contracts |
| Open Equity Positions | 3 | Long stock count |
| Cash % | 22.50% | Target ≥ 15% |
| VIX Close | 14.20 | |
| SPY Close | 502.75 | |

**Current positions** (position-level): view in **http://localhost:8501/Portfolio**. For rebalancing, sector limits, and optimization use the positions shown there; copy a summary here if needed for quick reference.

_To refresh from the same data that feeds the app: run `python scripts/refresh-portfolio-context.py --sheets` (reads last row from Google Sheet “Daily Dashboard”) or `--local` (tries context/portfolio-export.json, context/daily-dashboard.json, outputs/portfolio/latest.json)._

---

## Data Sources

- Financial Modeling Prep (FMP) API — fundamentals, earnings, ratios, SEC filings
- Massive.com — real-time OPRA options feed, greeks, IV, historical tick data
- n8n cloud instance — workflow execution and monitoring
- **Portfolio (source of truth)** — http://localhost:8501/Portfolio (local Streamlit app)
- Google Sheets — paper trading workbook (Trade Log, Daily Dashboard, Position History), idea tracking, reporting outputs
- Telegram — notifications and approval workflows

---

## Automation Note

_This file works as a static snapshot, but can be enhanced with scripts that pull live data. Once comfortable with the workspace, consider adding a script to `scripts/` that refreshes this file from your data sources (dashboards, APIs, spreadsheets, etc.)._

---

_Update regularly — stale data limits Claude's usefulness as an analytical partner._
