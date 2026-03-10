# Shell Aliases for Claude Code

Two shell aliases streamline launching Claude Code sessions with this workspace.

## Setup (Windows — Git Bash / PowerShell)

### Git Bash (~/.bashrc)

```bash
alias cs='claude "/prime"'
alias cr='claude --dangerously-skip-permissions "/prime"'
```

Reload: `source ~/.bashrc`

### PowerShell ($PROFILE)

```powershell
function cs { claude "/prime" }
function cr { claude --dangerously-skip-permissions "/prime" }
```

Reload: `. $PROFILE`

## The Aliases

### `cs` — Claude Safe

Launches Claude Code and immediately runs `/prime` to load workspace context. Claude will ask for permission before executing commands, reading sensitive files, or making changes.

**Use when:** Starting a new session where you want to review and approve each action.

### `cr` — Claude Run

Launches Claude Code with permission prompts disabled, then runs `/prime`. Claude can execute commands and make changes without asking for approval.

**Use when:** You trust the task, want faster iteration, or are doing routine work where constant approvals slow you down.

## Why Both?

- **`cs`** gives you oversight — good for unfamiliar tasks, sensitive operations, or when you want to learn what Claude is doing
- **`cr`** gives you speed — good for familiar workflows where you trust Claude to operate autonomously

Both run `/prime` automatically so Claude starts every session fully oriented to your workspace, goals, and context.

## Opening This Workspace in Cursor

```bash
# From any terminal
cursor X:\Claude\cursor-workspace

# Or use the desktop shortcut: "Launch Cursor Workspace.bat"
```
