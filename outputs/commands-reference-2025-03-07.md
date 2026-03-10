# Workspace Slash Commands Reference

**Generated:** 2025-03-07

| Command | Arguments | Functionality | Input | Output |
|---------|-----------|---------------|-------|--------|
| `/prime` | None | Initialize session: read CLAUDE.md and context, summarize user/workspace/goals, confirm readiness. | CLAUDE.md, context/ | Chat only |
| `/create-plan` | [request] — what to plan (new command, workflow, structural change, etc.) | Create a detailed implementation plan in plans/ with context, rationale, and step-by-step tasks. | User request; CLAUDE.md, context/, existing patterns | `plans/YYYY-MM-DD-{name}.md` |
| `/implement` | [plan-path] — path to plan file | Execute a plan from /create-plan: read plan, run steps in order, validate, update status. | Plan file path | Chat + plan status updates |
| `/analyze-ticker` | [TICKER] | Comprehensive financial ratio analysis + moat assessment using FMP API. | Ticker; FMP API | `outputs/analysis-{TICKER}-{DATE}.md` + chat summary |
| `/options-scan` | [TICKER] | Scan options chains (FMP + Massive.com), OCA criteria, recommend CSP/covered call/spreads/jade lizard. | Ticker; FMP + Massive API | `outputs/options-scan-{TICKER}-{DATE}.md` + chat |
| `/portfolio-report` | [type] — daily, weekly, monthly, holdings (default: daily) | Portfolio performance and risk report: market summary, watchlist, sector, options, risk dashboard, action items. | Report type; FMP API; portfolio data | `outputs/portfolio-report-{DATE}.md` |
| `/paper-trade` | [details] — ticker, strategy, strike, exp, delta, thesis, edge, etc. | Log paper trade with pre-trade checklist and risk checks; send to Trade Entry Logger webhook or output row for Sheets. | Trade details; risk framework | Webhook/Sheets row + chat |
| `/client-report` | [type] — monthly, quarterly, annual (default: monthly) | Client-facing portfolio report: narrative, performance attribution, risk, options activity, disclosures. | Report type; FMP API; trade/position data | `outputs/client-report-{TYPE}-{DATE}.md` |
| `/thesis` | [TICKER] | Full investment thesis: 5yr financials, DCF, comps, insider/institutional, bull/bear/base, Altamira fit. | Ticker; FMP API | `outputs/thesis-{TICKER}-{DATE}.md` + chat |
| `/moat` | [TICKER] | Morningstar-style economic moat: rating (None/Narrow/Wide), sources, direction; structured report. | Ticker; FMP API; optional research | `outputs/moat-{TICKER}-{DATE}.md` + chat |
| `/stockscore` | [TICKER…] or none (portfolio) | Quality/Growth/Value/Health/Shareholder scores + composite grade via stock-scorer.py. | Ticker(s) or portfolio-details; FMP/Massive | `outputs/stock-score-*.md` or portfolio-scores; chat |
| `/pre-launch` | None | Run pre-launch-check.py: validate strategy docs, commands, FMP, n8n workflows, outputs before go-live. | Script + workspace files | Chat (pass/fail + fixes) |
| `/backtest` | [csp \| momentum \| hedging \| all] (optional) | Run backtest-strategies.py for CSP, momentum, hedging; summarize win rate, Sharpe, drawdown. | Argument; FMP historical | Chat + optional outputs/backtest-results-*.md |
| `/risk-check` | None | Validate portfolio vs risk limits (5% position, 25% sector, 30% options, 15% cash) from portfolio-details. | portfolio-details.md, risk-management-framework.md | Chat (PASS/FAIL + actions) |
| `/earnings-calendar` | [TICKER \| watchlist] or none | Overall earnings (today +14d) or per-ticker/watchlist next earnings; table with date, time, quarter, market cap. | Optional ticker/watchlist; FMP | Chat (table) |
| `/earnings-analysis` | [TICKER] | Full earnings release: report data, press release, transcript highlights + Q&A, sentiment, verdict. | Ticker; FMP stable + v3 | `outputs/earnings-analysis-{TICKER}-{DATE}.md` |
| `/comps` | [TICKER] | Peer comparison: P/E, EV/EBITDA, growth, margins, ROE; implied price from median multiples. | Ticker; FMP | Chat (table + summary) |
| `/company-growth` | [TICKER] | Core four (Revenue, EPS, FCF margin, ROIC) + optional metrics; 3yr CAGR, YoY, grade A–F, metrics to monitor. | Ticker; FMP; optional company_growth_metrics.py | `outputs/company-growth-{TICKER}-{DATE}.md` |
| `/dcf` | [TICKER] | Quick DCF fair value + sensitivity (WACC vs terminal g); runs thesis-generator, extracts valuation only. | Ticker; thesis-generator.py | Chat (fair value, table, verdict) |
| `/watchlist-refresh` | None | Re-score watchlist via stock-scorer; consolidate grades; update context/watchlist.md; flag lows/highs. | watchlist.md or universe; FMP | outputs/portfolio-scores-*.md; context/watchlist.md; chat |
| `/13f-diff` | [CIK] [prior] [current] | Compare 13F holdings between two periods: new buys, sells, size changes. | CIK, dates; outputs/13f/ | Script output + chat summary |
| `/copycat-13f` | [CIKs] —weight value\|equal —consensus-min N | Build copycat portfolio from one or more 13F filers; target weights. | CIKs; ingest-13f data | outputs/copycat-*.json + chat table |
| `/context-refresh` | [scope] (optional) | Refresh holding snapshots, kanban export; remind re current-data/portfolio-details manual updates. | Scripts; optional Sheets/API | context/holding-monthly-snapshots.json, kanban-export.csv; chat |
| `/kanban-sync` | None | Export kanban to context/kanban-export.csv; surface sync instructions for completed tasks (no API task-update). | Kanban API (3005) | context/kanban-export.csv; chat + sync doc |
| `/insider` | [TICKER] | Recent insider transactions: net direction, C-suite, dollar totals, sentiment (Bullish/Neutral/Bearish). | Ticker; FMP | Chat summary |
| `/market-brief` | None | Short snapshot: indices, VIX, sector, "why the market is moving" from headlines, 1–2 sentence narrative. | Market Data API or FMP; FMP news | Chat |
| `/briefing` | [DATE] (optional) | Daily briefing: indices, hot stock/loser, sectors, SPY/QQQ/VIX, earnings, 5D/20D, support/resistance, trend, chart. | FMP v3 + stable | `outputs/briefing-{DATE}.md`, `outputs/briefing-chart-{DATE}.png` |
| `/speak` | text \| file path \| briefing [—out path] [—no-speak] | TTS: speak text or file or last briefing Voice script; optional save MP3. | Text/file/briefing; speak_text.py | Audio + optional outputs/*.mp3 |
| `/wireframe` | [artifact] — e.g. Dashboard, landing page, workflow | Three steps: (1) Generate ASCII wireframe (2) Iterate with 1–2 changes (3) Build from wireframe + stack. | Artifact description | Chat (wireframe then code) |
| `/work-plan` | None | Next 3–5 activities from kanban + recent outputs/current-data; write work-plan. | kanban-export.csv, outputs/, current-data.md | `outputs/work-plan-{DATE}.md` + chat |
| `/estimate-actual` | [TICKER] | Quarterly Revenue & EPS actuals vs estimates, variance %, YoY growth; tables + line charts. | Ticker; FMP stable + v3 | `outputs/estimate-actual-{TICKER}-{DATE}.md` |
| `/eps-estimate` | [TICKER] | Analyst EPS estimates by quarter (Q1 YY, Q2 YY, …); table. | Ticker; FMP | `outputs/eps-estimate-{TICKER}-{DATE}.md` |
| `/activist-investor-analyzer` | [TICKER \| ACTIVIST NAME \| DESCRIPTION] | Pershing Square–style activist situation: thesis vs management, valuation gap, proxy, precedent, probability tree, trade rec. | Ticker/activist/description; FMP; research | `outputs/activist-investor-analyzer-{TICKER}-{DATE}.md` |
| `/portfolio-risk-parity-analyzer` | [portfolio list \| current] | AQR-style risk parity: risk decomposition, equal risk weights, backtest, stress tests, implementation plan. | Portfolio or portfolio-details; risk_parity_analyzer.py | `outputs/portfolio-risk-parity-analyzer-{DATE}.md` |
| `/growth-equity-analyst` | [TICKER] [concerned about valuation \| excited about growth] | Tiger Global–style growth equity: revenue trajectory, Rule of 40, NRR, TAM, moat, valuation, growth score, conviction. | Ticker; FMP; optional research | `outputs/growth-equity-analyst-{TICKER}-{DATE}.md` |
| `/deep-value-analyzer` | [TICKER] [why undervalued] | Baupost-style deep value: asset-based value, earnings power, margin of safety, catalyst, value-trap checklist, position sizing. | Ticker; FMP; optional research | `outputs/deep-value-analyzer-{TICKER}-{DATE}.md` |
| `/global-macro-event-trader` | [EVENT DESCRIPTION] | Soros-style event-driven macro: reflexivity, consensus vs contrarian, asset impact map, analogues, trade implementation. | Event description; optional FMP quotes; research | `outputs/global-macro-event-trader-{event-slug}-{DATE}.md` |
| `/distressed-debt-opportunity-finder` | [COMPANY NAME OR TICKER] | Appaloosa-style distressed: capital structure, recovery by layer, liquidity, restructuring probability, fulcrum, recommendation. | Company/ticker; FMP; research | `outputs/distressed-debt-opportunity-finder-{TICKER}-{DATE}.md` |
| `/portfolio-construction-optimizer` | [positions with conviction and thesis \| current] | Citadel-style: position sizing by conviction, Kelly, correlation-aware, risk budget, stress test, rebalancing triggers. | Positions or portfolio-details; optional FMP | `outputs/portfolio-construction-optimizer-{DATE}.md` |
| `/hedgefund-quantitative-analyzer` | [FUND NAME \| monthly return history] | Renaissance-style factor decomposition: market/size/value/momentum/quality/vol/sector; alpha, R², ETF replication. | Fund name (→ 13F) or pasted returns; factor_decomposition.py | `outputs/hedgefund-quantitative-analyzer-{fund-slug}-{DATE}.md` |
| `/list-commands` | None (optional: custom commands dir) | List all slash commands with arguments, functionality, input, output; write this reference. | .claude/commands/*.md | `outputs/commands-reference-{DATE}.md` + chat |

---

**How to use:** Run `/prime` at session start; use `/create-plan` before structural changes and `/implement` to execute plans. Use `/list-commands` anytime to regenerate this reference.
