# /sync-second-brain — Sync Obsidian Second-Brain Repository (NAS ⇄ Local)

Bidirectional sync of the **second-brain Obsidian repository** between the Landino NAS and the local machine. Pulls newer files from the NAS, pushes newer files from local, and parks the older copy of any same-time conflict as a `.conflict-<utc>` sibling so nothing is lost silently.

This command is separate from the workspace vault sync described in `reference/obsidian-integration.md` — it targets the dedicated second-brain repo.

## Repositories

| Side | Path |
|------|------|
| **Local** | `C:\Users\rland\OneDrive\Desktop\second-brain` |
| **NAS**   | `\\Landino-NAS\AI Automation\second-brain` (POSIX form: `//Landino-NAS/AI Automation/second-brain`) |

These are baked in as the defaults. Override with `--local` / `--nas` if needed.

## Instructions

You are running a bidirectional sync of the user's second-brain Obsidian repository. Follow these steps exactly:

### Step 1: Parse arguments

`$ARGUMENTS` may include any of:

- `pull` — one-way, NAS → local only
- `push` — one-way, local → NAS only
- `both` — bidirectional (default if omitted)
- `dry-run` — preview without writing
- `delete` — in `pull` or `push` mode only, also remove files at the target that don't exist at the source (do **not** combine with `both`)
- `--local <path>` / `--nas <path>` — override the default paths
- Anything else — pass through to the script unchanged

If no arguments, default to **bidirectional, no dry-run, no delete**.

### Step 2: Confirm intent on destructive runs

Before running, if the parsed mode is `push --delete` (will delete files on NAS) or `pull --delete` (will delete local files), state plainly:

> "About to run `<mode> --delete`. This will remove files on the **<target>** side that don't exist on the **<source>** side. Reply 'yes' to proceed, or re-issue the command without `delete` for a non-destructive sync."

Wait for confirmation before continuing.

For non-destructive runs (default `both`, plain `pull`, plain `push`, or any `dry-run`), proceed without confirmation.

### Step 3: Run the sync script

Build the command with the second-brain paths and parsed arguments. Use bash on Linux/WSL/Git-Bash, PowerShell on Windows-native:

```bash
python scripts/sync_obsidian_vault.py \
  --local "C:/Users/rland/OneDrive/Desktop/second-brain" \
  --nas   "//Landino-NAS/AI Automation/second-brain" \
  [--mode pull|push|both] [--dry-run] [--delete]
```

PowerShell:

```powershell
python scripts\sync_obsidian_vault.py `
  --local "C:\Users\rland\OneDrive\Desktop\second-brain" `
  --nas   "\\Landino-NAS\AI Automation\second-brain" `
  --mode both
```

### Step 4: Handle errors

- **Exit code 1, "NAS path does not exist"** — the NAS share is not mounted/reachable. Tell the user to map `\\Landino-NAS\AI Automation` (or wake the NAS) and re-run.
- **Exit code 1, "lock at .sync.lock"** — a previous run is still going or was killed. Inspect the lock file's PID line; if no process is alive, delete `<local>/.sync.lock` and re-run.
- **Exit code 2** — partial copy failures. Show the per-file errors the script printed and suggest re-running the failing direction (often a permission or open-file issue on the NAS).
- **Conflicts reported** — list each `.conflict-<utc>` file the script parked. Tell the user to open both versions in Obsidian, merge the wanted edits, then delete the `.conflict-*` file. The next sync will then propagate the merge.

### Step 5: Report

Summarize the script's output:

- **Pulled NAS → local:** N files
- **Pushed local → NAS:** N files
- **Unchanged:** N files
- **Conflicts (parked):** N — list relative paths if any
- **Errors:** N — list if any

If `dry-run`, prefix the summary with **(dry-run, no changes written)**.

## Examples

| Command | What happens |
|---------|--------------|
| `/sync-second-brain` | Bidirectional sync, newer-mtime wins, conflicts parked. |
| `/sync-second-brain dry-run` | Preview only — list every file that would be pulled, pushed, or parked. |
| `/sync-second-brain pull` | One-way pull from NAS to local; no changes go back to the NAS. |
| `/sync-second-brain push` | One-way push from local to NAS. |
| `/sync-second-brain push delete` | Mirror local to NAS, removing files on the NAS that I deleted locally. Asks for confirmation first. |

## Context

- **Sync engine:** `scripts/sync_obsidian_vault.py` — newer-mtime wins; `.conflict-<utc>` sibling on same-time divergence; `.sync.lock` prevents concurrent runs; default include/exclude tuned for Obsidian (`*.md`, `.obsidian/**`, etc.).
- **Workspace vault sync (different command target):** `reference/obsidian-integration.md` §8 — same script, different paths, for the workspace-as-vault case.
