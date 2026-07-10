# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## What This Is

This is a **Claude Workspace Template** — a structured environment designed for working with Claude Code as a powerful agent assistant across sessions. The user will spin up fresh Claude Code sessions repeatedly, using `/prime` at the start of each to load essential context without bloat.

**This file (CLAUDE.md) is the foundation.** It is automatically loaded at the start of every session. Keep it current — it is the single source of truth for how Claude should understand and operate within this workspace.

---

## The Claude-User Relationship

Claude operates as an **agent assistant** with access to the workspace folders, context files, commands, and outputs. The relationship is:

- **User**: Ricardo Landino — Founder, Altamira Capital. Defines goals, provides context, and directs work through commands
- **Claude**: Reads context, understands objectives, executes commands, produces outputs, and maintains workspace consistency

Claude should always orient itself through `/prime` at session start, then act with full awareness of who the user is, what they're trying to achieve, and how this workspace supports that.

---

## Workspace Structure

```
.
├── CLAUDE.md              # This file — core context, always loaded
├── .claude/
│   ├── commands/          # Slash commands Claude can execute
│   │   ├── prime.md       # /prime — session initialization
│   │   ├── list-commands.md # /list-commands — list all commands (args, I/O)
│   │   ├── create-plan.md # /create-plan — create implementation plans
│   │   ├── implement.md   # /implement — execute plans
│   │   ├── 0DTE-SPX-credit-spread-scanner.md # /0DTE-SPX-credit-spread-scanner — 0DTE SPX credit spread setup (Tastytrade-style)
│   │   ├── analyze-ticker.md  # /analyze-ticker — financial ratio analysis
│   │   ├── options-scan.md    # /options-scan — options chain scanning
│   │   ├── portfolio-report.md # /portfolio-report — portfolio reports
│   │   ├── paper-trade.md     # /paper-trade — log paper trades
│   │   ├── client-report.md   # /client-report — client-facing portfolio reports
│   │   ├── thesis.md          # /thesis — investment thesis generator
│   │   ├── moat.md            # /moat — economic moat analysis (Morningstar-style)
│   │   ├── stockscore.md      # /stockscore — stock scoring system
│   │   ├── pre-launch.md      # /pre-launch — paper trading readiness check
│   │   ├── backtest.md        # /backtest — strategy backtests
│   │   ├── risk-check.md      # /risk-check — portfolio risk limit validation
│   │   ├── sector-rotation-timer.md # /sector-rotation-timer — cycle phase, sector RS, overweights/underweights, ETF playbook
│   │   ├── two-sigma-probability-strike-selection.md # /two-sigma-probability-strike-selection — probability-based strike selection (delta, SD, expected move, today's strikes)
│   │   ├── earnings-calendar.md  # /earnings-calendar — earnings calendar
│   │   ├── earnings-analysis.md     # /earnings-analysis — full earnings release analysis (transcript, Q&A, sentiment)
│   │   ├── pre-earnings-options-strategist.md # /pre-earnings-options-strategist — pre-earnings implied move, IV, strategy
│   │   ├── comps.md           # /comps — comparable company analysis
│   │   ├── catalyst-map-builder.md # /catalyst-map-builder — 12-month catalyst map, probability-weighted EV, overweights/hedges
│   │   ├── citadel-market-regime-classifier.md # /citadel-market-regime-classifier — market regime (VIX, term structure, trend, IV/realized, verdict GREEN/YELLOW/RED)
│   │   ├── company-growth.md  # /company-growth — company growth evaluation (Revenue, EPS, FCF margin, ROIC + optional metrics, grade, metrics to monitor)
│   │   ├── dcf.md             # /dcf — quick DCF fair value
│   │   ├── buffett-intrinsic-value-calculator.md # /buffett-intrinsic-value-calculator — Buffett-style owner earnings, moat, 10yr DCF, margin of safety
│   │   ├── earnings-quality-investigator.md # /earnings-quality-investigator — Sloan accrual, Beneish M-Score, cash conversion, earnings quality rating
│   │   ├── compounder-screen.md # /compounder-screen — compounder quality screen (7-point checklist) for watchlist candidates
│   │   ├── DE-shaw-iron-condor-income-machine.md # /DE-shaw-iron-condor-income-machine — systematic iron condor (SPX/SPY/QQQ/IWM), sizing, adjustments, income
│   │   ├── watchlist-refresh.md # /watchlist-refresh — refresh and score watchlist
│   │   ├── wolverine-trading-risk-management-system.md # /wolverine-trading-risk-management-system — theta risk manual, limits, roll/close, daily checklist
│   │   ├── 13f-diff.md        # /13f-diff — 13F holdings diff
│   │   ├── copycat-13f.md     # /copycat-13f — 13F copycat portfolio
│   │   ├── context-refresh.md # /context-refresh — refresh context files
│   │   ├── kanban-sync.md     # /kanban-sync — kanban export and sync
│   │   ├── insider.md         # /insider — insider transaction summary
│   │   ├── imc-trading-earnings-theta-crusher.md # /imc-trading-earnings-theta-crusher — earnings IV crush plan, entry timing, strategy, exit protocol
│   │   ├── Jane-Street-pre-market-edge-analyzer.md # /Jane-Street-pre-market-edge-analyzer — 8 AM pre-market theta plan, gap/IV/calendar, S/R, scenario playbook
│   │   ├── institutional-flow-decoder.md # /institutional-flow-decoder — institutional ownership flow analysis
│   │   ├── macro-tail-head-wind-scanner.md # /macro-tail-head-wind-scanner — macro tailwind/headwind by factor, net score, positioning
│   │   ├── management-quality-evaluator.md # /management-quality-evaluator — management quality (capital allocation, compensation, insider, communication, strategy)
│   │   ├── market-brief.md    # /market-brief — short market snapshot
│   │   ├── briefing.md        # /briefing — daily market briefing (Market Commenter style)
│   │   ├── daily-market-recap.md # /daily-market-recap — daily recap markdown + Telegram delivery
│   │   ├── speak.md          # /speak — TTS: speak text or briefing aloud / save MP3
│   │   ├── sig-daily-theta-decay-calculator.md # /sig-daily-theta-decay-calculator — theta dashboard (position/portfolio theta, hourly decay, compounding)
│   │   ├── activist-investor-analyzer.md  # /activist-investor-analyzer — Pershing Square-style activist situation analysis
│   │   ├── akuna-capital-volatility-exploiter.md # /akuna-capital-volatility-exploiter — volatility skew analysis, jade lizard, broken wing, ratio spread, trade setups
│   │   ├── portfolio-risk-parity-analyzer.md  # /portfolio-risk-parity-analyzer — AQR-style risk parity analysis
│   │   ├── growth-equity-analyst.md  # /growth-equity-analyst — Tiger Global-style growth equity analysis
│   │   ├── deep-value-analyzer.md  # /deep-value-analyzer — Baupost-style deep value analysis
│   │   ├── short-thesis-generator.md # /short-thesis-generator — short-side thesis (bull case, pillars, catalysts, downside)
│   │   ├── global-macro-event-trader.md  # /global-macro-event-trader — Soros-style event-driven macro analysis
│   │   ├── distressed-debt-opportunity-finder.md  # /distressed-debt-opportunity-finder — Appaloosa-style distressed credit analysis
│   │   ├── portfolio-construction-optimizer.md  # /portfolio-construction-optimizer — Citadel-style portfolio construction framework
│   │   ├── risk-adjusted-portfolio-builder.md   # /risk-adjusted-portfolio-builder — risk-adjusted build from watchlist (Kelly, correlation, tiers, stress test)
│   │   └── hedgefund-quantitative-analyzer.md  # /hedgefund-quantitative-analyzer — Renaissance-style factor decomposition
│   └── skills/            # Workspace-specific skills (kept intentionally minimal)
├── context/               # Background context about the user and project
│                          # (Role, goals, strategies, current data)
├── plans/                 # Implementation plans created by /create-plan
├── outputs/               # Work products, deliverables, n8n workflows, scripts
├── reference/             # Templates, examples, reusable patterns (Obsidian: reference/obsidian-integration.md)
├── .obsidian/             # Obsidian vault config — open this workspace folder as vault in Obsidian
└── scripts/               # Automation and validation scripts
```

**Key directories:**

| Directory    | Purpose                                                                             |
| ------------ | ----------------------------------------------------------------------------------- |
| `context/`   | Who the user is, their role, current priorities, strategies. Read by `/prime`.      |
| `plans/`     | Detailed implementation plans. Created by `/create-plan`, executed by `/implement`. |
| `outputs/`   | Deliverables, analyses, reports, and work products.                                 |
| `reference/` | Helpful docs, templates and patterns. Obsidian: open workspace as vault; see `reference/obsidian-integration.md`. |
| `scripts/`   | Any automation or tooling scripts.                                                  |

---

## Commands

### /prime

**Purpose:** Initialize a new session with full context awareness.

Run this at the start of every session. Claude will:

1. Read CLAUDE.md and context files
2. Summarize understanding of the user, workspace, and goals
3. Confirm readiness to assist

### /list-commands

**Purpose:** List all slash commands with arguments, functionality, input, and output.

Reads every command file in `.claude/commands/`, extracts command name, arguments, functionality, input, and output for each, and writes a single reference table to `outputs/commands-reference-{DATE}.md`. No arguments required.

Example: `/list-commands`

### /create-plan [request]

**Purpose:** Create a detailed implementation plan before making changes.

Use when adding new functionality, commands, scripts, or making structural changes. Produces a thorough plan document in `plans/` that captures context, rationale, and step-by-step tasks.

Example: `/create-plan add a competitor analysis command`

### /implement [plan-path]

**Purpose:** Execute a plan created by /create-plan.

Reads the plan, executes each step in order, validates the work, and updates the plan status.

Example: `/implement plans/2026-02-16-competitor-analysis-command.md`

### /akuna-capital-volatility-exploiter [TICKER] [PRICE] [daily | weekly | monthly]

**Purpose:** Akuna-style volatility skew analysis: put vs call IV at same delta, skew percentile (steep/flat/inverted), put/call skew opportunities, jade lizard, broken wing butterfly, ratio spread, skew mean-reversion, term structure skew, and risk of skew expansion. Strategy recommendations and specific trade setups.

Uses FMP (quote, VIX for indices) and options chain (FMP/Massive) for IV and delta by strike. Writes `outputs/akuna-capital-volatility-exploiter-{TICKER}-{DATE}.md`.

Example: `/akuna-capital-volatility-exploiter SPY 585 weekly` or `/akuna-capital-volatility-exploiter AAPL 230 monthly`

### /analyze-ticker [TICKER]

**Purpose:** Run comprehensive financial ratio analysis on a ticker using live FMP API data.

Pulls income statement, balance sheet, cash flow, key metrics, and ratios from FMP API. Calculates profitability, liquidity, leverage, efficiency, and valuation ratios with 3-year trends. Outputs a full analysis report to `outputs/`.

Example: `/analyze-ticker MSFT`

### /options-scan [TICKER]

**Purpose:** Scan options chains and generate trade recommendations for a ticker.

Fetches real-time options chain, filters by delta/DTE/liquidity, and recommends CSP, covered call, bull put spread, and jade lizard strategies with position sizing. Outputs a scan report to `outputs/`.

Example: `/options-scan AAPL`

### /0DTE-SPX-credit-spread-scanner [optional date]

**Purpose:** Complete 0DTE SPX credit spread setup for today: market conditions (VIX, overnight, economic calendar), SPX expected move (ATM straddle or VIX-based), put/call credit spreads (0.10–0.15 delta, 5–10 pt width), iron condor if conditions favor, premium target $0.50–$1.00 and min 1:3 R:R, entry 9:45–10:30 AM ET, stop-loss at 2× premium or short-strike breach, exit at 50% profit before 2 PM or expire worthless. Tastytrade-style trade ticket with exact strikes when chain available.

Uses FMP (quote ^VIX, ^GSPC, economic calendar); optional FMP/Massive SPX 0DTE options chain. Writes `outputs/0DTE-SPX-credit-spread-scanner-{DATE}.md`.

Example: `/0DTE-SPX-credit-spread-scanner` or `/0DTE-SPX-credit-spread-scanner for 2025-03-10`

### /DE-shaw-iron-condor-income-machine [UNDERLYING] [PRICE] [ACCOUNT SIZE] [daily | weekly]

**Purpose:** D.E. Shaw-style systematic iron condor on SPX/SPY/QQQ/IWM: underlying selection (IV and trend), expected range, put/call at 0.10–0.15 delta (5–10 pt width), total premium, max loss, breakevens, position sizing (2–5% max risk), adjustment triggers (roll if within 30% of short strike), profit taking (50% max profit), and daily income projection.

Uses FMP (quote, VIX, historical prices for trend, economic calendar); optional options chain (FMP/Massive). Writes `outputs/DE-shaw-iron-condor-income-machine-{UNDERLYING}-{DATE}.md`.

Example: `/DE-shaw-iron-condor-income-machine SPY 500000 weekly` or `/DE-shaw-iron-condor-income-machine QQQ 100000 daily`

### /portfolio-report [type]

**Purpose:** Generate a portfolio performance and risk report.

Types: `daily` (default), `weekly`, `monthly`, `holdings`. Covers market summary, watchlist performance, sector exposure, options landscape, risk dashboard, and action items. Outputs to `outputs/`.

Example: `/portfolio-report weekly`

### /paper-trade [details]

**Purpose:** Log a paper trade with pre-trade checklist validation and risk checks.

Collects trade details (ticker, strategy, strike, delta, thesis, edge), runs the 6-point pre-trade checklist, validates against risk limits, and logs to the Trade Entry Logger webhook or outputs Google Sheets row data for manual entry.

Example: `/paper-trade AAPL CSP STO 225 strike 2026-04-17 exp -0.22 delta $3.20 credit`

### /client-report [type]

**Purpose:** Generate a professional, client-facing portfolio performance report.

Types: `monthly` (default), `quarterly`, `annual`. Produces a polished, narrative-driven report with executive summary, performance attribution by strategy and ticker, risk dashboard, options activity, market commentary, and disclosures. Suitable for sharing with investors or stakeholders.

Example: `/client-report quarterly`

### /thesis [TICKER]

**Purpose:** Generate a comprehensive investment thesis with DCF valuation, comps analysis, and buy/hold/avoid recommendation.

Pulls 5 years of financials, runs DCF with sensitivity analysis, compares against sector peers, analyzes insider/institutional ownership, and produces a full publishable thesis document with bull/bear/base cases and Altamira fit assessment. Deeper than `/analyze-ticker`.

Example: `/thesis AVGO`

### /moat [TICKER]

**Purpose:** Run a Morningstar-style economic moat analysis for a given ticker (rating, sources, direction) and write the report to `outputs/moat-{TICKER}-{DATE}.md`.

Assesses moat rating (None / Narrow / Wide), source(s) of moat (Network Effects, Switching Costs, Low-Cost Producer, Intangible Assets, Counter Positioning), and moat direction (Shrinking / Stable / Widening). Uses FMP API data and optional research; produces a structured markdown report and a short chat summary.

Example: `/moat GOOGL`

### /stockscore [TICKER]

**Purpose:** Calculate comprehensive stock scores (Quality, Growth, Value, Health, Shareholder) and composite grade for tickers using FMP API data.

Calculates five component scores (0-100 each) based on weighted financial metrics, combines into composite score, assigns letter grade (A+ to F), and identifies strengths/weaknesses. Scores all current portfolio holdings if no ticker provided, or evaluates new entrants before adding to portfolio. Outputs scoring reports to `outputs/`.

Example: `/stockscore` (scores all holdings) or `/stockscore MSFT` (scores single ticker)

### /pre-launch

**Purpose:** Run the paper trading pre-launch readiness check.

Executes `scripts/pre-launch-check.py` and summarizes pass/fail for strategy docs, commands, FMP key, n8n workflows, and output files. Use before Mar 1 go-live.

### /backtest [strategy]

**Purpose:** Run strategy backtests (CSP, momentum, hedging) and summarize results.

Executes `scripts/backtest-strategies.py`; reports win rate, Sharpe, drawdown, and cumulative return. Optional argument: `csp`, `momentum`, `hedging`, or `all`.

### /risk-check

**Purpose:** Validate current portfolio against risk limits (5% position, 25% sector, 30% options, 15% cash).

Reads `context/portfolio-details.md` (or current-data) and `outputs/risk-management-framework.md`; reports PASS/FAIL per rule and action items if any fail.

### /sector-rotation-timer [optional date or horizon]

**Purpose:** Determine current economic cycle phase, sector relative strength vs S&P 500 (3m/6m/12m), cycle-aligned overweights/underweights, dislocation flags, and a rotation playbook with specific sector ETF tickers.

Uses FMP historical-price-full for SPY and sector ETFs (XLF, XLY, XLK, XLI, XLB, XLE, XLU, XLP, XLV) for relative strength; optional research for ISM PMI, yield curve, Fed stance, credit spreads, initial claims. Writes `outputs/sector-rotation-timer-{DATE}.md`.

Example: `/sector-rotation-timer` or `/sector-rotation-timer next 12 months`

### /earnings-calendar [TICKER | watchlist]

**Purpose:** With **no argument:** overall view of earnings coming up (today through next 14 days) — table: Ticker, Company, Date, Time (BMO/AMC), Quarter Ending, Market Cap. With **argument:** upcoming earnings for that ticker (next 2–4 dates) or for the core watchlist (Ticker | Next Earnings Date | Days from today; flags within 14 days). Uses FMP earning_calendar and quote (or profile) for names/market cap. Reminds to avoid holding options through unplanned earnings.

### /earnings-analysis [TICKER]

**Purpose:** Full analysis of a company's latest earnings release: report data, press release, earnings call transcript (highlights + Q&A visibility), and sentiment analysis of management's answers.

Uses FMP stable (transcript, transcript-dates, earnings, press releases) and FMP v3 (quote, profile, earnings-surprises, analyst-estimates). Writes `outputs/earnings-analysis-{TICKER}-{DATE}.md`. For upcoming dates only, use `/earnings-calendar TICKER`.

Example: `/earnings-analysis COST`

### /pre-earnings-options-strategist [TICKER]

**Purpose:** Pre-earnings options analysis: implied earnings move vs historical realized, IV assessment, skew, and recommended strategy with full trade construction.

Calculates implied move from ATM straddle (Massive.com options chain) and current price; compares to average of last 8 realized earnings moves from FMP historical prices; assesses IV Rank/Percentile and put vs call skew; recommends one of short vol (iron condor/strangle), long vol (straddle/debit spread), or directional vertical with max profit, max loss, and breakevens. Uses FMP quote, historical/earning_calendar, historical-price-full; Massive.com options snapshot. Writes `outputs/pre-earnings-options-strategist-{TICKER}-{DATE}.md` with structured summary block.

Example: `/pre-earnings-options-strategist NVDA`

### /comps [TICKER]

**Purpose:** Comparable company analysis only (peers, multiples, implied price).

Uses FMP stock_peers and key metrics; builds peer table (P/E, EV/EBITDA, growth, margins, ROE) and implied price from median multiples. Lighter than full thesis.

### /catalyst-map-builder [TICKER]

**Purpose:** Build a 12-month catalyst map: catalog catalysts (earnings, product, corporate, regulatory, management, macro), probability-weight each (High/Medium/Low), estimate bull/bear impact, compute expected value, identify highest-EV catalyst and biggest downside risk, net catalyst score, and position sizing recommendation.

Uses FMP (profile, quote, earning_calendar, analyst-estimates, earnings-surprises; optional press releases); optional research for product, corporate, regulatory, management, and macro events. Writes `outputs/catalyst-map-builder-{TICKER}-{DATE}.md`.

Example: `/catalyst-map-builder COST`

### /citadel-market-regime-classifier [optional date]

**Purpose:** Classify market conditions into regimes before options trading: VIX regime (low/normal/elevated/crisis), VIX term structure (contango/backwardation), trend (trending vs range-bound), realized vs implied vol, correlation, overnight gap risk, economic event density, put-call ratio, market breadth. Output regime verdict GREEN (sell premium aggressively) / YELLOW (sell conservatively, wider strikes) / RED (sit in cash) with specific strategy recommendation.

Uses FMP (quote ^VIX, ^GSPC, SPY; historical-price-full for trend and realized vol; economic calendar); optional research for term structure, gap, put-call, breadth. Writes `outputs/citadel-market-regime-classifier-{DATE}.md` with dashboard summary and strategy for today.

Example: `/citadel-market-regime-classifier` or `/citadel-market-regime-classifier for 2025-03-10`

### /company-growth [TICKER]

**Purpose:** Evaluate a company's growth using core four metrics (Revenue, Adjusted EPS, FCF margin, ROIC) with 3yr CAGR and latest YoY, plus optional metrics (margins, Rule of 40, ROE, FCF $ growth, revenue trajectory). Assigns a letter grade (A–F), explains the reason, and lists metrics to monitor.

Uses FMP (income statement, cash flow, key-metrics, ratios, financial-growth, balance sheet; optional quote, profile, analyst-estimates). Writes `outputs/company-growth-{TICKER}-{DATE}.md`. Optionally run `python scripts/company_growth_metrics.py --ticker TICKER` for consistent CAGR/grade numbers.

Example: `/company-growth AVGO`

### /dcf [TICKER]

**Purpose:** Quick DCF fair value and sensitivity (no full thesis).

Runs `scripts/thesis-generator.py` and extracts valuation section: fair value, current price, upside/downside %, and WACC vs terminal growth sensitivity table.

### /buffett-intrinsic-value-calculator [TICKER] [price] [horizon]

**Purpose:** Buffett-style intrinsic value analysis: owner earnings, economic moat (5 sources, 1–5 score), 10-year DCF (bear/base/bull), margin of safety, verdict, top 3 permanent impairment risks.

Calculates owner earnings (Net Income + D&A − Maintenance Capex ± Working Capital). Runs 10-year DCF with bear (3% growth, 8% discount), base (8%, 10%), bull (15%, 12%). Flags buy only if price ≥30% below intrinsic value. Uses FMP API for financials and quote. Writes `outputs/buffett-intrinsic-value-calculator-{TICKER}-{DATE}.md`.

Example: `/buffett-intrinsic-value-calculator COST` or `/buffett-intrinsic-value-calculator AAPL 10 years`

### /earnings-quality-investigator [TICKER]

**Purpose:** Forensic earnings quality investigation: Sloan Accrual Ratio, Beneish M-Score, cash conversion (OCF vs NI), revenue recognition and other red flags, earnings quality rating, action recommendation.

Uses FMP income statement, cash flow, and balance sheet (3–5 years). Flags Sloan accrual >5%, Beneish M > −2.22 (probable manipulator). Writes `outputs/earnings-quality-investigator-{TICKER}-{DATE}.md`.

Example: `/earnings-quality-investigator COST`

### /compounder-screen [TICKER ...]

**Purpose:** Identify compounder-quality companies for the watchlist using a 7-point checklist and FMP data.

Scores each ticker on: (1) Strong franchise durability / pricing power, (2) High ROIC/ROCE vs cost of capital, (3) Recurring revenue, (4) FCF yield 4–6%, (5) Debt &lt; 3× EBITDA, (6) Low cyclicality, (7) Returns capital (dividends and/or buybacks). Uses FMP profile, income, balance sheet, cash flow, key-metrics, ratios, revenue segmentation, dividends. Outputs `outputs/compounder-screen-{TICKER}-{DATE}.md` with Pass/Partial/Fail per criterion, overall verdict (Add to watchlist / Consider / Do not add), and optional pointers to `/moat`, `/stockscore`, `/company-growth`, `/buffett-intrinsic-value-calculator` for deeper analysis.

Example: `/compounder-screen COST` or `/compounder-screen COST MSFT AVGO`

### /watchlist-refresh

**Purpose:** Re-score watchlist tickers and update watchlist context.

Runs `scripts/stock-scorer.py` for portfolio/watchlist tickers; consolidates scores and optionally updates `context/watchlist.md` with grades and notes. Flags low scores and high-score candidates.

### /wireframe [ARTIFACT]

**Purpose:** Three-step flow: (1) Generate — output only an ASCII wireframe of the artifact using box-drawing characters and arrows, no code. (2) Iterate — apply 1–2 specific changes and redraw the wireframe only. (3) Build — implement the artifact from the pasted wireframe and stack/requirements, matching the wireframe exactly. Artifacts: Dashboard, slides, workflows, schemas, landing pages (or short description).

Example: `/wireframe Dashboard` or `/wireframe landing page for signup`

### /wolverine-trading-risk-management-system [ACCOUNT_SIZE] [DAILY_LOSS_LIMIT]

**Purpose:** Wolverine-style risk management system for daily theta strategy: daily/weekly loss limits, position size cap (2–5%), correlation check, tail risk protection, VIX spike protocol, buying power (≤50%), roll-vs-close decision tree, recovery protocol, monthly drawdown circuit breaker (10%), and daily risk checklist.

Uses positions from `context/options-positions.md` for correlation and position-size checks and current portfolio risk snapshot; account size from $ARGUMENTS or `context/portfolio-details.md` / `context/current-data.md`. Writes `outputs/wolverine-trading-risk-management-system-{DATE}.md`.

Example: `/wolverine-trading-risk-management-system` or `/wolverine-trading-risk-management-system 100000 2000`

### /13f-diff [CIK] [prior] [current]

**Purpose:** 13F holdings diff between two periods (new buys, sells, size changes).

Runs `scripts/13f-holdings-diff.py` for a filer; summarizes new buys, sells, increased/decreased positions. Requires 13F data ingested to `outputs/13f/`.

### /copycat-13f [CIKs]

**Purpose:** Build copycat portfolio from one or more 13F filers.

Runs `scripts/copycat-13f.py`; outputs target portfolio (tickers, weights). Optional: --weight value|equal, --consensus-min N. Use with ingest-13f first.

### /context-refresh

**Purpose:** Refresh key context files (holding snapshots, kanban export).

Runs `scripts/build-holding-monthly-snapshots.py`; exports kanban to `context/kanban-export.csv` if API (port 3005) is running. Notes manual updates for current-data and portfolio-details.

### /kanban-sync

**Purpose:** Export kanban board to CSV and/or surface sync instructions for completed tasks.

Exports board to `context/kanban-export.csv` via API, or points to `outputs/kanban-q1-sync-instructions.md` for moving completed Q1 tasks to Done in the UI (no API task-update).

### /insider [TICKER]

**Purpose:** Recent insider transaction summary for a ticker.

Fetches FMP insider-trading; summarizes net buying/selling, notable C-suite transactions, and sentiment (Bullish/Neutral/Bearish).

### /imc-trading-earnings-theta-crusher [TICKER] [EARNINGS_DATE] [CURRENT_IV] [bullish | bearish | neutral]

**Purpose:** IMC-style earnings IV crush strategy: pre-earnings IV expansion timing, optimal entry (1–3 days before), historical IV crush magnitude (last 8), strategy selection (iron condor/strangle/single-side), strike placement, premium vs historical move, position sizing (1–2%), post-earnings close-at-open protocol, assignment risk, and next 5 earnings events with optimal entry dates.

Uses FMP (quote, earning_calendar, historical-price-full for realized move); options chain (FMP/Massive) for implied move and IV. Writes `outputs/imc-trading-earnings-theta-crusher-{TICKER}-{DATE}.md`.

Example: `/imc-trading-earnings-theta-crusher AAPL 2025-04-24 42 neutral` or `/imc-trading-earnings-theta-crusher NVDA bullish`

### /Jane-Street-pre-market-edge-analyzer [SPX_FUTURES] [VIX] [NEWS_OR_EVENTS]

**Purpose:** Jane Street-style 8 AM pre-market analysis for optimal theta strategy: overnight futures movement and gap hold/fade, pre-market IV vs yesterday, economic calendar impact, earnings exposure, Globex range, opening gap strategy, IV crush opportunity, previous close analysis, three support/resistance levels, and exact trade plan with scenario playbook (bull, bear, neutral).

Uses FMP (quote ^GSPC/SPY/^VIX, historical prior-day OHLC, economic_calendar, earning_calendar); optional user input for SPX futures and VIX. Writes `outputs/Jane-Street-pre-market-edge-analyzer-{DATE}.md`.

Example: `/Jane-Street-pre-market-edge-analyzer 5850 18.5` or `/Jane-Street-pre-market-edge-analyzer` (full fetch)

### /institutional-flow-decoder [TICKER]

**Purpose:** Decode institutional ownership flow: accumulation vs distribution, top holders, concentration risk, insider alignment, and smart money signal.

Maps top 20 institutional holders (ownership %, QoQ where available), identifies highest-conviction adders and fund types (value/growth/quant/activist), computes top-5 concentration, decodes 12-month insider activity (open market vs options), and flags unusual volume. Uses FMP institutional-holder, insider-trading, quote, profile; optional FMP stable for QoQ. Writes `outputs/institutional-flow-decoder-{TICKER}-{DATE}.md` with structured summary block and overall Bullish/Neutral/Bearish smart money signal.

Example: `/institutional-flow-decoder AAPL`

### /management-quality-evaluator [TICKER]

**Purpose:** Evaluate management quality for long-horizon investors: capital allocation (M&A, buybacks, dividends, R&D/capex), compensation alignment, insider ownership (grants vs open-market), communication integrity, and strategic vision. Outputs overall rating (Exceptional / Above Average / Average / Below Average / Avoid) and primary concern.

Uses FMP (profile, quote, income, cash flow, key metrics, ratios, insider-trading; optional executive-compensation); optional research for compensation, guidance, and strategy. Writes `outputs/management-quality-evaluator-{TICKER}-{DATE}.md`.

Example: `/management-quality-evaluator COST`

### /macro-tail-head-wind-scanner [TICKER]

**Purpose:** Analyze current macro environment impact on a company: score interest rates, currency, inflation/costs, demand cycle, credit, regulation, and geopolitics as headwind/neutral/tailwind; produce net macro score and positioning recommendation (Overweight/Neutral/Underweight).

Uses FMP (profile, quote, income, balance sheet, cash flow, key metrics, ratios, revenue segmentation); optional research for current rates, FX, inflation, demand, credit, regulation, geopolitics. Writes `outputs/macro-tail-head-wind-scanner-{TICKER}-{DATE}.md`.

Example: `/macro-tail-head-wind-scanner COST`

### /market-brief

**Purpose:** Short market snapshot (indices, VIX, one- to two-sentence narrative).

Uses Market Data API (port 8001) or FMP for indices and VIX; presents levels and day change; writes a brief narrative. Fallback when Market Commenter workflow has not run.

### /briefing

**Purpose:** Daily market briefing (Market Commenter style): indices, hot stock/biggest loser, sectors, SPY/QQQ/VIX, earnings calendar, index vs 5D/20D, support/resistance, trend, commentary, index chart.

Uses FMP API (v3 + stable) for quotes, gainers/losers, sector snapshot, earnings calendar, and historical EOD. Computes 5D/20D averages, support/resistance, and trend (Bullish/Bearish/Mixed). Writes `outputs/briefing-{DATE}.md` and optionally runs `scripts/briefing_chart.py` for `outputs/briefing-chart-{DATE}.png`. To hear the summary as audio after a briefing, run `/speak briefing`.

### /daily-market-recap

**Purpose:** Generate Altamira Capital's daily market recap, write `outputs/daily-market-recap-{DATE}.md`, and send both a short summary and the Markdown file to the configured Telegram channel.

Runs `python3 scripts/daily_market_recap.py --send-telegram`. Uses FMP data for index levels, VIX, leaders/laggards, sectors, news, earnings, and S&P 500 technicals. Telegram delivery requires `TELEGRAM_BOT_TOKEN` or `TELEGRAM_API_TOKEN` plus `TELEGRAM_CHAT_ID` unless a chat ID is passed explicitly.

### /speak [text | file path | briefing]

**Purpose:** Run TTS to speak text aloud or save to MP3. Use with inline text, a file path (e.g. `outputs/briefing-voice-2025-02-23.txt`), or the shortcut `briefing` to speak the last briefing’s Voice script. Combines with `/briefing`, `/market-brief`, or any command whose output you want as audio.

Run from workspace root: `python scripts/speak_text.py --text "..."` or `--file <path>`; add `--out outputs/...mp3` to save (uses edge-tts). See `.claude/commands/speak.md`.

### /activist-investor-analyzer [TICKER | ACTIVIST NAME | DESCRIPTION]

**Purpose:** Pershing Square-style activist situation analysis: activist profile, thesis vs management, valuation gap, proxy probability, precedent, timeline, institutional alignment, probability tree, and trade recommendation.

Resolve ticker/activist from arguments; fetch FMP (profile, quote, institutional-holder, DCF); optionally use research for activist bio, 13D/thesis, proxy dates. Writes `outputs/activist-investor-analyzer-{TICKER}-{DATE}.md` with 12 sections and outcome-weighted return projection.

Example: `/activist-investor-analyzer TGT` or `/activist-investor-analyzer TGT Elliott Management`

### /portfolio-risk-parity-analyzer [MY PORTFOLIO | current]

**Purpose:** AQR-style risk parity analysis: allocate by risk contribution so no single holding dominates portfolio risk. Risk decomposition, equal risk allocation weights, backtest vs current weights, stress tests (2008, 2020, 2022), and implementation plan.

Uses `scripts/risk_parity_analyzer.py` with FMP historical prices. Portfolio from $ARGUMENTS (list of holdings with weights and total value) or from `context/portfolio-details.md` (Current Positions table). Writes `outputs/portfolio-risk-parity-analyzer-{DATE}.md` with risk contribution tables, optimal weights, leverage analysis, rebalancing frequency, and exact position changes to move to risk parity.

Example: `/portfolio-risk-parity-analyzer` (uses workspace portfolio) or `/portfolio-risk-parity-analyzer SPY 30%, AGG 40%, GLD 30%, total $500K`

### /growth-equity-analyst [TICKER] [concerned about valuation | excited about growth]

**Purpose:** Tiger Global-style growth equity analysis for high-growth tech at premium valuations: revenue trajectory, Rule of 40, NRR, TAM, unit economics, moat, path to profitability, insider/institutional trends, valuation reality check, and growth durability score (1–10).

Uses FMP (income statement, key-metrics, ratios, cash flow, analyst-estimates, insider-trading, institutional-holder, profile, quote); optional research for NRR, TAM, unit economics. Writes `outputs/growth-equity-analyst-{TICKER}-{DATE}.md` with growth scorecard, valuation framework, and conviction rating (Buy/Hold/Reduce/Avoid).

Example: `/growth-equity-analyst CRWD` or `/growth-equity-analyst SNOW concerned about valuation`

### /deep-value-analyzer [TICKER] [WHY YOU THINK IT MIGHT BE UNDERVALUED]

**Purpose:** Baupost-style deep value analysis for beaten-down stocks: asset-based valuation, earnings power value, margin of safety, catalyst identification, value trap checklist (7 warning signs), balance sheet fortress test, insider buying, short interest, historical comps, and position sizing.

Uses FMP (balance sheet, income statement, cash flow, key-metrics, ratios, insider-trading, institutional-holder, profile, quote, DCF); optional research for catalyst, short interest, and historical pattern. Writes `outputs/deep-value-analyzer-{TICKER}-{DATE}.md` with margin of safety calculation, catalyst timeline, and risk-adjusted position recommendation.

Example: `/deep-value-analyzer BBBY` or `/deep-value-analyzer WBA oversold on sector rotation, hidden real estate`

### /short-thesis-generator [TICKER]

**Purpose:** Build a complete short thesis: consensus bull case, three pillars stress-tested with counter-evidence, business model flaws, financial vulnerabilities, catalyst calendar, downside target, and risks to the short.

Uses FMP (profile, quote, income annual/quarterly, balance sheet, cash flow, key-metrics, ratios, analyst-estimates, earnings-surprises, insider-trading, institutional-holder, DCF, stock_peers, revenue-product-segmentation, rating/price-target); optional research for debt maturities, regulatory, competitive, key-man, lockup. Writes `outputs/short-thesis-generator-{TICKER}-{DATE}.md` with structured summary block and disclaimer.

Example: `/short-thesis-generator SNOW`

### /global-macro-event-trader [EVENT DESCRIPTION]

**Purpose:** Soros-style event-driven macro analysis: reflexivity, consensus vs contrarian scenarios, asset class impact map, historical analogues, first-mover trades, second-order effects, risk management, and specific trade implementation.

Uses optional FMP quotes (indices, VIX, SPY, TLT, etc.) for current levels; research for consensus, positioning, and historical analogues. Writes `outputs/global-macro-event-trader-{event-slug}-{DATE}.md` with scenario analysis, probability-weighted returns, and exact instruments, sizes, and exit rules.

Example: `/global-macro-event-trader Fed meeting March 2026 — will they cut or hold?` or `/global-macro-event-trader US election 2026 tariff and fiscal impact`

### /distressed-debt-opportunity-finder [COMPANY NAME OR TICKER]

**Purpose:** Appaloosa-style distressed credit analysis for companies in financial trouble: capital structure map, recovery analysis by layer, liquidity timeline, restructuring probability, fulcrum security, asset value floor, catalyst for recovery, comparable situations, management/board changes, and risk–reward assessment.

Uses FMP (balance sheet, income statement, cash flow, key-metrics, ratios, profile, quote, insider, institutional-holder); research for capital structure detail, recovery rates, comps, and restructuring news. Writes `outputs/distressed-debt-opportunity-finder-{TICKER}-{DATE}.md` with capital structure waterfall, recovery estimates, and risk-adjusted recommendation.

Example: `/distressed-debt-opportunity-finder Revlon` or `/distressed-debt-opportunity-finder WBA`

### /portfolio-construction-optimizer [POSITIONS WITH CONVICTION AND THESIS | current]

**Purpose:** Citadel-style portfolio construction: position sizing by conviction and risk, Kelly Criterion, correlation-aware allocation, risk budget, gross/net exposure, concentration limits, liquidity-adjusted sizing, 5-regime stress test, rebalancing triggers, and performance attribution framework.

Uses optional FMP batch quote (volume, market cap) for liquidity; optional risk-parity script output for correlation. Positions from $ARGUMENTS (ticker, conviction HIGH/MEDIUM/LOW, thesis) or from `context/portfolio-details.md`. Writes `outputs/portfolio-construction-optimizer-{DATE}.md` with position sizing tables, risk budget allocations, and stress test dashboard.

Example: `/portfolio-construction-optimizer current` or `/portfolio-construction-optimizer AAPL HIGH quality compounder, SPY 15% MEDIUM core, NVDA 5% LOW momentum`

### /risk-adjusted-portfolio-builder [watchlist | TICKER1 TICKER2 ...]

**Purpose:** Build a risk-adjusted portfolio from the watchlist (or ticker list): optimize for Sharpe > 1.5, control max drawdown and correlation. Classification (sector, factor, cap, geography), pairwise correlation flags (>0.70), half-Kelly position sizing, three tiers (Core 50–60%, Tactical 25–35%, Speculative 10–15%), stress tests (2008, 2022, sector disruption), portfolio stats (Sharpe, Beta, max DD), and recommended adjustments.

Uses FMP (profile, quote, key-metrics, ratios, historical-price-full 12M) for returns, correlation, vol, Beta; optional `scripts/risk_parity_analyzer.py` output for correlation/vol. Writes `outputs/risk-adjusted-portfolio-builder-{DATE}.md`.

Example: `/risk-adjusted-portfolio-builder` (watchlist) or `/risk-adjusted-portfolio-builder AAPL COST MSFT NVDA`

### /sig-daily-theta-decay-calculator [positions list | current]

**Purpose:** SIG-style theta decay dashboard for short premium positions: position-level and portfolio daily theta, hourly decay curve, acceleration zone, theta-to-delta ratio, weekend theta capture, theta vs gamma risk, optimal closing time, daily/weekly/monthly income projection, and compounding growth over 30/60/90 days.

Positions from $ARGUMENTS (ticker, strike, exp, credit, current value, contracts; optional theta/delta) or from `context/options-positions.md`, `context/theta-positions.md`, or Options section in `context/portfolio-details.md`. Uses FMP for underlying price when estimating theta from time value. Writes `outputs/sig-daily-theta-decay-calculator-{DATE}.md`.

Example: `/sig-daily-theta-decay-calculator AAPL 150P 2025-03-21 2.50 1.20 10` or paste table; `/sig-daily-theta-decay-calculator current` if context file exists

### /two-sigma-probability-strike-selection [UNDERLYING] [PRICE] [TARGET WIN RATE %]

**Purpose:** Two Sigma-style probability-based strike selection for credit spreads: delta→probability, 1.0/1.5/2.0 SD mapping, expected move (1d/1w/1m) from IV, historical accuracy of implied move, strike optimization, win rate by delta (0.10≈90%, 0.15≈85%, 0.20≈80%, 0.30≈70%), premium decay by delta, gap risk and skew adjustments, and today's exact short/long strikes.

Uses FMP (quote, historical-price-full 100 sessions, economic calendar, earnings); optional options chain (FMP/Massive) or VIX for IV. Writes `outputs/two-sigma-probability-strike-selection-{UNDERLYING}-{DATE}.md`.

Example: `/two-sigma-probability-strike-selection SPX 5850 90%` or `/two-sigma-probability-strike-selection AAPL 85%`

### /hedgefund-quantitative-analyzer [FUND NAME | MONTHLY RETURN HISTORY]

**Purpose:** Renaissance-style factor decomposition: decompose a fund's return stream into factor exposures (market, size, value, momentum, quality, volatility, sector), isolate true alpha, report R², and suggest ETF replication.

Supports: (1) hedge fund name → resolve to 13F filer CIK, build monthly returns from 13F + FMP via `scripts/factor_decomposition.py`; (2) pasted monthly returns or CSV file. Writes `outputs/hedgefund-quantitative-analyzer-{fund-slug}-{DATE}.md` with regression tables, factor exposure summary, and replication strategy.

Example: `/hedgefund-quantitative-analyzer Berkshire Hathaway` or `/hedgefund-quantitative-analyzer 0.02,-0.01,0.03,...`

---

## Key Deliverables

Strategy and operational documents in `outputs/`:

| Document | File | Status |
|----------|------|--------|
| Investment Thesis v2.0 | `altamira-investment-thesis.md` | Final |
| Risk Management Framework | `risk-management-framework.md` | Final |
| Portfolio Allocation Model | `portfolio-allocation-model.md` | Final |
| Paper Trading Launch Plan | `paper-trading-plan.md` | Final |
| E-Trade API Setup Guide | `etrade-api-setup-guide.md` | Final |
| Market Monitoring Workflows | `market-monitoring-workflows.md` | Designed — awaiting n8n deployment |
| Backtest Results (2Y) | `backtest-results-2026-02-18.md` | Complete |

n8n workflow JSON files ready to import (in `outputs/`):

| Workflow | File | Trigger |
|----------|------|---------|
| Daily Portfolio Snapshot | `n8n-workflow-1-daily-portfolio-snapshot.json` | 4:15 PM ET daily |
| Trade Entry Logger | `n8n-workflow-2-trade-entry-logger.json` | Webhook |
| Weekly Metrics Calculator | `n8n-workflow-3-weekly-metrics-calculator.json` | Sunday 6 PM ET |
| Risk Limit Monitor | `n8n-workflow-4-risk-limit-monitor.json` | Every 30 min |
| Watchlist Alert System | `n8n-workflow-watchlist-alert-system.json` | Every 15 min |
| Volatility Regime Monitor | `n8n-workflow-volatility-regime-hedging.json` | Every 30 min |
| CSP Daily Scan | `n8n-workflow-csp-daily-scan.json` | 10:30 AM ET weekdays |

**CSP Daily Scan deploy:** Import `outputs/n8n-workflow-csp-daily-scan.json` in n8n, then follow `outputs/csp-daily-scan-deploy-guide.md` for credentials, env vars (TELEGRAM_CHAT_ID, GOOGLE_SHEET_ID), and activation.

Google Sheets setup: `outputs/paper-trading-workbook.gs` — paste into Apps Script and run `setupPaperTradingWorkbook()`

## Local Services

| Service | URL | How to Start | Restart Guide |
|---------|-----|-------------|---------------|
| Altamira Dashboard | http://localhost:3001 | Docker (MongoDB) + `next dev -p 3001` | `reference/altamira-dashboard-restart-guide.md` |
| Kanban Board | http://localhost:3004 | `npm run dev:all` | `reference/kanban-dashboard.md` |

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/backtest-strategies.py` | Run backtests for CSP, momentum, and hedging strategies | `python scripts/backtest-strategies.py` |
| `scripts/pre-launch-check.py` | Validate all paper trading prerequisites before Mar 1 launch | `python scripts/pre-launch-check.py` |
| `scripts/daily_market_recap.py` | Generate daily market recap Markdown and optionally send summary + file to Telegram | `python3 scripts/daily_market_recap.py --send-telegram` |
| `scripts/deploy-csp-workflow-to-n8n.py` | Deploy CSP Daily Scan workflow to n8n cloud via REST API | Set `N8N_API_KEY` (and optional `N8N_API_URL`), then `python scripts/deploy-csp-workflow-to-n8n.py` |
| `scripts/ingest-13f.py` | Ingest SEC 13F-HR filings into JSON (EDGAR or sample) | `python scripts/ingest-13f.py --cik 1067983` or `--sample`; set `SEC_EDGAR_USER_AGENT` if 403 |
| `scripts/query-13f.py` | Query ingested 13F JSON by filer, period, CUSIP | `python scripts/query-13f.py --list` or `--cik X --period Y` |
| `scripts/13f-holdings-diff.py` | Compare 13F holdings between two periods (new buys, sells, increased/decreased) | `python scripts/13f-holdings-diff.py --cik CIK --prior YYYY-MM-DD --current YYYY-MM-DD` (optional `--out report.md`, `--json-out diff.json`) |
| `scripts/copycat-13f.py` | Build copycat portfolio from 1+ filers (value/equal weight, consensus) | `python scripts/copycat-13f.py --ciks CIK1,CIK2 [--weight value|equal] [--consensus-min N] [--out file.json]` |
| `scripts/13f-fund-performance.py` | 13F fund metrics: concentration, holdings count, overlap % | `python scripts/13f-fund-performance.py --cik CIK [--prior P --current C] [--out file.json]` |
| `scripts/13f-stock-screener.py` | Screen by institutional ownership (aggregate value, filer count) | `python scripts/13f-stock-screener.py [--min-filers N] [--format json|csv] [--out file]` |
| `scripts/13f-heatmap-export.py` | Export 13F matrix (filers x CUSIPs) for heat map | `python scripts/13f-heatmap-export.py [--format json|csv] [--out file]` |
| `scripts/13f-backtest.py` | Backtest copycat/13F strategy (FMP prices) | `python scripts/13f-backtest.py --portfolio copycat.json --from YYYY-MM-DD --to YYYY-MM-DD` or `--cik CIK` |
| **13F API (Option B)** | FastAPI bridge for dashboard (run scripts, return JSON, 5 min cache) | `pip install fastapi uvicorn` then `uvicorn scripts.13f_api:app --host 0.0.0.0 --port 8000` — base URL `http://localhost:8000/api/13f/` |
| **Market Data API** | FastAPI bridge to FMP for dashboard (quotes, indices, earnings) | `uvicorn scripts.market_data_api:app --host 0.0.0.0 --port 8001` — base URL `http://localhost:8001/api/market/` (alt-dash-06) |
| `scripts/streamlit_13f.py` | Streamlit 13F section for dashboard (copy or import into app; calls 13F API) | `streamlit run scripts/streamlit_13f.py` for standalone preview; see `reference/13f-dashboard-integration.md` |
| `scripts/build-holding-monthly-snapshots.py` | Build monthly snapshot per holding for Holding Snapshot dashboard | `python scripts/build-holding-monthly-snapshots.py --sheets` or `--file context/position-history-export.csv`; writes `context/holding-monthly-snapshots.json` |
| `scripts/streamlit_holding_snapshot.py` | Streamlit Holding Snapshot section for page /a (copy or import into app) | `streamlit run scripts/streamlit_holding_snapshot.py` for standalone preview; see `reference/holding-snapshot-dashboard.md` |
| `scripts/deploy-holding-snapshot-to-app.py` | Deploy Holding Snapshot to Streamlit app (copy fragment + JSON, inject into page /a) | `python scripts/deploy-holding-snapshot-to-app.py --app-dir "X:\path\to\streamlit-app"`; use `--snippet-only` to print paste snippet |

**13F hardening:** CUSIP→ticker in `reference/cusip-to-ticker.json`; loader `scripts/cusip_loader.py`. Curated filers: `context/13f-filers.txt` (use with `ingest-13f.py --cik-list`). SEC ingest retries once on 403.

| `scripts/kanban-import-13f.py` | Import 13F project + 10 tasks to kanban board (POST to localhost:3005) | `python scripts/kanban-import-13f.py` (kanban app must be running) |
| `scripts/kanban-update-13f-status.py` | Report which 13F tasks should be Done; write sync instructions (API has no task-update endpoint) | `python scripts/kanban-update-13f-status.py` then move tasks to Done in UI at http://localhost:3004 |

---

## Critical Instruction: Maintain This File

**Whenever Claude makes changes to the workspace, Claude MUST consider whether CLAUDE.md needs updating.**

After any change — adding commands, scripts, workflows, or modifying structure — ask:

1. Does this change add new functionality users need to know about?
2. Does it modify the workspace structure documented above?
3. Should a new command be listed?
4. Does context/ need new files to capture this?

If yes to any, update the relevant sections. This file must always reflect the current state of the workspace so future sessions have accurate context.

**Examples of changes requiring CLAUDE.md updates:**

- Adding a new slash command → add to Commands section
- Creating a new output type → document in Workspace Structure or create a section
- Adding a script → document its purpose and usage
- Changing workflow patterns → update relevant documentation

---

## Session Workflow

1. **Start**: Run `/prime` to load context
2. **Work**: Use commands or direct Claude with tasks
3. **Plan changes**: Use `/create-plan` before significant additions
4. **Execute**: Use `/implement` to execute plans
5. **Maintain**: Claude updates CLAUDE.md and context/ as the workspace evolves

---

## Notes

- Keep context minimal but sufficient — avoid bloat
- Plans live in `plans/` with dated filenames for history
- Outputs are organized by type/purpose in `outputs/`
- Reference materials go in `reference/` for reuse
