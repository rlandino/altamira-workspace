# Obsidian Integration — Altamira Workspace

Use Obsidian on this workspace so you can browse, link, and edit the same markdown files (context, outputs, plans, reference) from a second brain / note-taking workflow.

**→ For day-to-day workflows at Altamira:** see **[[obsidian-workflows-altamira]]** (how to leverage Obsidian for strategy, research, trading, and reporting). Start with **[[context/Altamira-Dashboard]]** in Obsidian as your control note.

---

## 1. Open this workspace as an Obsidian vault

1. **Install Obsidian** (if needed): [obsidian.md](https://obsidian.md) — download for Windows/Mac/Linux.
2. **Open vault from folder:**
   - In Obsidian: **Open folder as vault** (or File → Open folder as vault).
   - Choose this workspace folder: **`X:\Claude\altamira-workspace`** (or your actual path, e.g. `\\Landino-NAS\AI Automation\Claude\altamira-workspace`).
3. Obsidian will treat the entire workspace as the vault. All markdown (`.md`) files under `context/`, `outputs/`, `plans/`, `reference/`, `.claude/commands/`, and the root will appear in the file explorer and graph.

**Important:** Editing a file in Obsidian edits the same file on disk; Claude and other tools (Cursor, scripts) see the same content. No sync step is required.

---

## 2. Recommended folder usage

| Folder | Use in Obsidian |
|--------|------------------|
| **context/** | Core context: strategy, current-data, portfolio-details, watchlist. Good for daily notes and links. |
| **outputs/** | Reports, theses, stock scores, workflow JSONs. Link to specific reports from context or plans. |
| **plans/** | Implementation plans from `/create-plan`. Use as project notes. |
| **reference/** | Templates, guides (like this file), reusable patterns. Use as reference notes. |
| **.claude/commands/** | Command definitions (for reference or copy-paste). Usually read-only. |
| **Root** | CLAUDE.md, README, etc. Link from context when needed. |

You can create **new** notes anywhere (e.g. `context/daily-notes/` or `outputs/notes/`). To keep the workspace clean, prefer `context/` for personal/organizational notes and `outputs/` for generated or dated content.

---

## 3. Linking and discovery

- **Wikilinks:** In any `.md` file, use `[[filename]]` or `[[path/filename]]` to link. Example: `[[strategy]]` or `[[context/strategy]]`, `[[stock-score-GOOGL-2026-02-23]]` in outputs.
- **Graph:** Use Obsidian’s graph view to see how context, outputs, and plans connect.
- **Search:** Obsidian search works across all markdown; use it to find tickers, project names, or phrases.
- **Tags:** You can add tags (e.g. `#ticker/GOOGL`, `#report`, `#plan`) in frontmatter or inline; Obsidian will index them.

---

## 4. Optional: default new-note location

In Obsidian: **Settings → Files & links → Default location for new notes**. Set to **“Same folder as current file”** or a specific folder (e.g. `context/notes`) so new notes don’t clutter the root.

---

## 5. Optional: plugins

- **Dataview** — Query markdown (e.g. list all reports in `outputs/` or all plans in `plans/`) with simple queries.
- **Templater** — Templates for daily notes or report stubs that match workspace conventions.
- **Calendar** — If you add daily notes under `context/daily/`, Calendar gives a calendar view.

Install from **Settings → Community plugins → Browse** (and enable “Safe mode” off to allow community plugins).

---

## 6. .obsidian folder (vault config)

The workspace includes a minimal **`.obsidian`** folder so Obsidian recognizes it as a vault and applies light defaults. You can change any setting in **Settings**; Obsidian will update `.obsidian/app.json` (and related files) in this workspace.

- **Version control:** If you use git, consider ignoring `.obsidian/workspace.json` and `.obsidian/workspace-mobile.json` (per-device UI state) and committing the rest so others get the same base config.
- **This doc:** `reference/obsidian-integration.md` — update this file if you add conventions or move folders.

---

## 7. Quick start checklist

- [ ] Install Obsidian.
- [ ] Open folder as vault → select `altamira-workspace` (or your full path).
- [ ] Confirm you see `context/`, `outputs/`, `plans/`, `reference/` in the file explorer.
- [ ] Open `context/strategy.md` or `outputs/altamira-investment-thesis.md` and try a wikilink to another note.
- [ ] (Optional) Set default location for new notes and install Dataview or Templater.

You’re integrated: the vault is the workspace, and Claude/Cursor and Obsidian work on the same files.
