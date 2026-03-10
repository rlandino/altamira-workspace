# Leveraging Obsidian for Altamira Work

Use Obsidian as your **second screen** for strategy, research, and execution — same files Claude and Cursor use, so nothing is duplicated.

---

## 1. One place to start: your “control note”

Create a single note that you open first (e.g. **`context/Altamira-Dashboard.md`** or **`context/README.md`**). Use it as a **dashboard** that links to everything you touch daily.

**Suggested content (copy and adapt):**

```markdown
# Altamira — Control Note

## Today / This week
- [ ] Check [[current-data]] for metrics and deliverables
- [ ] Review [[strategy]] — Q1 priorities
- [ ] If trading: [[paper-trade]] checklist, [[risk-check]]

## Strategy & context
- [[strategy]] — Priorities, $5M AUM, Q1 focus
- [[current-data]] — Metrics, deliverables, portfolio snapshot
- [[portfolio-details]] — Holdings, sector, targets
- [[outputs/altamira-investment-thesis]] — Philosophy and edge

## Research & reports
- **Scores:** `outputs/stock-score-*.md` — Search "stock-score" in Obsidian
- **Theses:** `outputs/thesis-*.md` — Search "thesis-"
- **Options:** `outputs/options-scan-*.md`
- **Portfolio report:** Run `/portfolio-report` in Cursor; output in `outputs/`

## Execution
- [[reference/paper-trading-plan]] — Go-live criteria
- [[outputs/risk-management-framework]] — Limits (5%, 25%, 30%, 15%)
- Kanban: http://localhost:3004 — Tasks in `context/kanban-export.csv` or sync via `/kanban-sync`

## Quick links
- [[reference/obsidian-integration]] — How this vault is set up
- [[reference/next-steps-deploy-summary]] — Deploy checklist
```

**Why it helps:** One note ties strategy → context → research → execution. Open it in Obsidian when you start work; use the links instead of hunting folders.

---

## 2. Daily workflows

### Morning: market and positions

1. **Open** `context/Altamira-Dashboard.md` (or your control note).
2. **Check** `context/current-data.md` — metrics, portfolio snapshot, deliverables. In Obsidian you can leave it open in a tab.
3. **Optional:** Run `/market-brief` in Cursor and paste the result into a daily note (e.g. `context/daily/YYYY-MM-DD.md`) so you have a one-line market view in the vault.
4. **If you’re considering a trade:** Open `outputs/risk-management-framework.md` and `reference/paper-trading-plan` in Obsidian; run `/risk-check` and `/paper-trade` in Cursor when you have the trade details.

### Research: tickers and theses

1. **After running** `/stockscore GOOGL` or `/thesis MSFT` in Cursor, the report is in `outputs/` (e.g. `outputs/stock-score-GOOGL-2026-02-23.md`, `outputs/thesis-MSFT-2026-02-23.md`).
2. **In Obsidian:** Open that note. Add a line at the top: `#ticker/GOOGL` or `#report/thesis` so you can filter by tag later.
3. **Link from your control note or a “Tickers” note:** e.g. `[[stock-score-GOOGL-2026-02-23]]` or `[[thesis-MSFT-2026-02-23]]`. Later you can open the note from the graph or backlinks.
4. **Earnings:** Run `/earnings-calendar` or `/earnings-calendar GOOGL` in Cursor; if you paste the result into a note (e.g. `context/earnings-watch.md`), you can link it from the dashboard.

### Execution: paper trades and risk

1. **Before a trade:** In Obsidian open `outputs/risk-management-framework.md` and skim limits (5% position, 25% sector, 30% options, 15% cash). In Cursor run `/risk-check`.
2. **Logging the trade:** Run `/paper-trade ...` in Cursor with full details. Optionally add a short note in Obsidian (e.g. `context/trades/2026-02.md`) with the ticker and thesis and link to the report that justified it: `[[stock-score-AAPL-2026-02-20]]`.
3. **After the trade:** No need to duplicate the log; the canonical log is the webhook/Sheets. Obsidian is for your own notes and links (e.g. “why I took this trade”).

### Client and reporting

1. **Before a client report:** Open `context/current-data.md` and any recent `outputs/portfolio-report-*.md` or `outputs/client-report-*.md` in Obsidian for narrative and numbers.
2. **Run** `/client-report monthly` (or quarterly/annual) in Cursor; output goes to `outputs/`. Open that file in Obsidian to review or copy from.
3. **Link** the report from your control note or a “Reports” note so you can pull up past reports quickly.

---

## 3. Weekly and periodic

- **Strategy check:** Open `context/strategy.md` and `context/current-data.md`. Update “Key Decisions or Open Questions” or metrics in Obsidian if you prefer editing there; Claude will see the same file.
- **Kanban:** Run `/kanban-sync` in Cursor to refresh the board or get sync instructions. In Obsidian you can open `outputs/kanban-q1-sync-instructions.md` or `context/kanban-export.csv` (if you use a CSV plugin) to see tasks.
- **Watchlist and scores:** Run `/watchlist-refresh` in Cursor; new scores appear in `outputs/`. In Obsidian search for `portfolio-scores` or `stock-score` to open the latest; link the best candidates from your dashboard.
- **Deploy and ops:** Use `reference/next-steps-deploy-summary.md` in Obsidian as a checklist; run the actual scripts (CSP deploy, context refresh) in Cursor.

---

## 4. Making links work for you

- **Wikilinks:** From any note, type `[[` and start typing a filename (e.g. `strategy`, `stock-score-GOOGL`). Obsidian will suggest files. Pick one to create a link. Clicking the link opens that note.
- **Backlinks:** In Obsidian, open the “Backlinks” pane (right sidebar). When you open a note (e.g. a thesis or a stock score), you’ll see which other notes link to it — useful to see “where this ticker or report is referenced.”
- **Graph:** Use the local graph (focus on one note) to see what a given note links to and what links to it. Use the global graph to see how strategy, context, outputs, and plans connect.
- **Search:** Use Obsidian search (Ctrl/Cmd + Shift + F) for a ticker (e.g. `GOOGL`), a phrase (“fair value”, “CSP”), or a tag (`#ticker/GOOGL`). All markdown in the vault is searchable.

---

## 5. Optional: a “Tickers” map of content

Create **`context/Tickers-MOC.md`** (MOC = map of content) and list tickers you care about with links to their latest score and thesis:

```markdown
# Tickers — Map of Content

- **GOOGL** — [[stock-score-GOOGL-2026-02-23]] | [[thesis-GOOGL-2026-02-23]]
- **MSFT** — (run /stockscore MSFT and /thesis MSFT, then link here)
- **AAPL** — ...
```

When you run `/stockscore` or `/thesis` in Cursor, add one line to this MOC. Then in Obsidian you always have one note that points to the latest research per ticker.

---

## 6. What to do in Obsidian vs Cursor

| Do in **Obsidian** | Do in **Cursor** (with Claude) |
|--------------------|--------------------------------|
| Browse and open context, outputs, plans | Run commands: `/stockscore`, `/thesis`, `/risk-check`, `/paper-trade`, etc. |
| Link notes (dashboard, MOCs, daily notes) | Execute scripts and automations |
| Read and edit strategy, current-data, portfolio-details | Deploy workflows, run backtests, ingest 13F |
| Search and graph across all markdown | Write code, update commands, modify scripts |
| Add your own notes and tags | Generate reports that land in `outputs/` |

Same files, two views: Obsidian for **navigation and narrative**, Cursor for **execution and generation**.

---

## 7. Quick reference

- **Control note:** `context/Altamira-Dashboard.md` (or similar) — your one starting page.
- **Strategy and metrics:** `context/strategy.md`, `context/current-data.md`.
- **Risk and trading:** `outputs/risk-management-framework.md`, `reference/paper-trading-plan.md`; run `/risk-check` and `/paper-trade` in Cursor.
- **Research:** Search `outputs/` for `stock-score`, `thesis`, `options-scan`; link them from a Tickers MOC or dashboard.
- **Setup:** `reference/obsidian-integration.md` — how the vault is configured.

Use Obsidian to **stay oriented** and **connect** strategy, research, and execution; use Cursor + Claude to **run** the work. That’s how you leverage Obsidian at Altamira.
