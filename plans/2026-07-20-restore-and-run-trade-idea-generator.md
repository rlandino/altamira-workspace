# Plan: Restore and Run the Trade Idea Generator

**Created:** 2026-07-20
**Status:** In Progress
**Request:** Execute the repository's portfolio/watchlist trade idea generator and deliver the result to Telegram.

---

## Overview

### What This Plan Accomplishes

Restore the established `/trade-idea-generator` files that are absent from the current branch, run the generator against repository portfolio/watchlist context, and deliver its concise report to the configured Telegram destination.

### Why This Matters

The command supports Altamira Capital's goal of producing daily actionable portfolio intelligence while preserving an auditable repository output.

---

## Current State

### Relevant Existing Structure

- Portfolio and watchlist inputs exist in `context/`.
- Prior repository history contains a proven generator implementation.
- Telegram credentials and delivery behavior are supported by that implementation.

### Gaps or Problems Being Addressed

- `.claude/commands/trade-idea-generator.md` and `scripts/trade_idea_generator.py` are absent from this branch.
- `CLAUDE.md` does not currently register the command.

---

## Proposed Changes

### Summary of Changes

- Restore the command definition and generator script from the latest proven repository revision.
- Register the restored command in `CLAUDE.md`.
- Generate and commit today's Markdown/JSON audit artifacts.
- Send the generated summary to Telegram.

### New Files to Create

| File Path | Purpose |
| --- | --- |
| `.claude/commands/trade-idea-generator.md` | Command usage and input/output contract |
| `scripts/trade_idea_generator.py` | Portfolio/watchlist analysis and Telegram delivery |
| `outputs/trade-idea-generator-2026-07-20.md` | Human-readable daily report |
| `outputs/trade-idea-generator-2026-07-20.json` | Structured daily report |

### Files to Modify

| File Path | Changes |
| --- | --- |
| `CLAUDE.md` | Register the restored command |

### Files to Delete (if any)

None.

---

## Design Decisions

### Key Decisions Made

1. **Restore the proven implementation:** This preserves established filtering, stale-data disclosures, and Telegram behavior.
2. **Use repository context as requested:** The generator reads the existing portfolio, watchlist, and option-position files.
3. **Retain an audit trail:** Daily Markdown and JSON outputs record the analysis sent externally.

### Alternatives Considered

Writing an ad hoc Telegram message was rejected because it would bypass the requested command and its safety/disclosure logic.

### Open Questions (if any)

None; prior automation history identifies the configured Telegram destination and command behavior.

---

## Step-by-Step Tasks

### Step 1: Restore the Command

Restore the command and script from the latest matching repository history and add the command references to `CLAUDE.md`.

**Files affected:**

- `.claude/commands/trade-idea-generator.md`
- `scripts/trade_idea_generator.py`
- `CLAUDE.md`

---

### Step 2: Validate and Execute

Compile the script, verify its CLI, and run it with options-chain enrichment and Telegram delivery.

**Files affected:**

- `outputs/trade-idea-generator-2026-07-20.md`
- `outputs/trade-idea-generator-2026-07-20.json`

---

### Step 3: Verify Delivery and Persist Results

Confirm successful Telegram API response, inspect output disclosures, then commit and push the generated artifacts.

**Files affected:**

- `outputs/trade-idea-generator-2026-07-20.md`
- `outputs/trade-idea-generator-2026-07-20.json`

---

## Connections & Dependencies

### Files That Reference This Area

- `CLAUDE.md`
- `context/portfolio-details.md`
- `context/watchlist.md`
- `context/options-positions.md`

### Updates Needed for Consistency

The command list and detailed command section in `CLAUDE.md` must both include `/trade-idea-generator`.

### Impact on Existing Workflows

This restores an existing daily workflow without changing unrelated commands.

---

## Validation Checklist

- [ ] Script compiles and `--help` succeeds.
- [ ] Generator writes today's Markdown and JSON outputs.
- [ ] Expired static option rows are excluded and disclosed.
- [ ] Telegram delivery returns a successful message identifier.
- [ ] Changes are committed and pushed on the designated branch.

---

## Success Criteria

1. Today's trade ideas are generated from repository portfolio/watchlist context.
2. The Telegram summary is delivered successfully.
3. The restoration and generated audit outputs are committed and pushed.

---

## Notes

The repository inputs are static snapshots. The report must preserve the generator's live-data status and financial disclaimer so recipients can distinguish live analysis from fallback context.
