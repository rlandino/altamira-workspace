# /list-commands — List All Slash Commands

Produce a single reference of every slash command in this workspace: name, arguments, functionality, input, and output.

## Instructions

You are building a **command reference** for the Altamira workspace. Follow these steps exactly.

### Step 1: Enumerate command files

List all `.md` files in `.claude/commands/` (excluding this file, `list-commands.md`). Each file corresponds to one slash command: the command name is the filename with `.md` removed, e.g. `prime.md` → `/prime`, `analyze-ticker.md` → `/analyze-ticker`.

### Step 2: Read and parse each command

For **each** command file:

1. **Read** the full file content.
2. **Extract:**
   - **Command** — Slash command name (e.g. `/prime`, `/analyze-ticker [TICKER]`).
   - **Arguments** — Any documented arguments, placeholders, or options (e.g. `[TICKER]`, `[type]`, `$ARGUMENTS` description). If the file uses "Variables", "argument", or "Options" sections, include those. Use "None" if no arguments.
   - **Functionality** — One to three sentences describing what the command does (from the title or first Instructions section).
   - **Input** — What the user or system provides: user-supplied args, required context files, API keys/env, or "None" if it only uses workspace state.
   - **Output** — Where results go: file path(s) (e.g. `outputs/analysis-{TICKER}-{DATE}.md`), chat summary, webhook, or "Chat only".

### Step 3: Produce the reference

Output a **single markdown document** with:

1. **Title:** `# Workspace Slash Commands Reference`
2. **Generated date** (today).
3. **Table** with columns: **Command** | **Arguments** | **Functionality** | **Input** | **Output**
   - One row per command.
   - Keep functionality and I/O concise but accurate.
4. **Optional:** A short "How to use" line (e.g. "Run `/prime` at session start; use `/create-plan` before structural changes.").

### Step 4: Write and summarize

- Write the reference to **`outputs/commands-reference-{DATE}.md`** (use today's date in YYYY-MM-DD format).
- In chat, provide a brief summary: how many commands were listed and where the full reference was saved.

## Notes

- If a command file is missing or unreadable, list it as "Command name — (parse error)" and continue.
- Preserve exact argument syntax (e.g. `[TICKER]`, `[type]`) where documented.
- This command has **no required arguments**; optional argument: a path to a custom commands directory (default: `.claude/commands/`).
