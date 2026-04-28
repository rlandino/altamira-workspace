#!/usr/bin/env python3
"""
Obsidian Vault Sync — NAS ⇄ Local Workspace
=============================================
Bidirectional sync between an Obsidian vault stored on the NAS and the local
workspace clone. Pulls newer files from the NAS, pushes newer files from
local, and parks both copies of a divergence as a `.conflict-<timestamp>`
file when both sides changed within a tight window.

Usage:
  python scripts/sync_obsidian_vault.py [--nas PATH] [--local PATH]
                                        [--mode pull|push|both]
                                        [--dry-run] [--delete]
                                        [--include GLOB ...] [--exclude GLOB ...]
                                        [--quiet]

Defaults:
  --nas    : $OBSIDIAN_NAS_PATH or (Windows) Z:/Claude/altamira-workspace or
             //Landino-NAS/AI Automation/Claude/altamira-workspace
  --local  : workspace root (parent of scripts/)
  --mode   : both
  Includes : *.md, .obsidian/**, context/**, outputs/**, plans/**, reference/**,
             .claude/**, CLAUDE.md, README*, *.code-workspace
  Excludes : .git/**, __pycache__/**, *.pyc, node_modules/**, .venv/**,
             venv/**, .pytest_cache/**, .DS_Store, Thumbs.db, .sync.lock,
             outputs/tradingview-alerts.jsonl

Examples:
  # Dry-run a full bidirectional sync against the NAS env var
  OBSIDIAN_NAS_PATH="/mnt/nas/Claude/altamira-workspace" \
    python scripts/sync_obsidian_vault.py --dry-run

  # Pull only (NAS → local)
  python scripts/sync_obsidian_vault.py --mode pull \
    --nas "//Landino-NAS/AI Automation/Claude/altamira-workspace"

  # Push only (local → NAS), allow deletes to mirror local
  python scripts/sync_obsidian_vault.py --mode push --delete \
    --nas "Z:/Claude/altamira-workspace"

Exit codes:
  0 — success (no errors; conflicts may have been parked)
  1 — fatal error (NAS unreachable, lock held, etc.)
  2 — partial failure (one or more files failed to copy)
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import os
import shutil
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
LOCK_NAME = ".sync.lock"

DEFAULT_INCLUDES = [
    "*.md",
    ".obsidian/**",
    "context/**",
    "outputs/**",
    "plans/**",
    "reference/**",
    ".claude/**",
    "CLAUDE.md",
    "README*",
    "*.code-workspace",
]

DEFAULT_EXCLUDES = [
    ".git/**",
    "__pycache__/**",
    "**/__pycache__/**",
    "*.pyc",
    "node_modules/**",
    "**/node_modules/**",
    ".venv/**",
    "venv/**",
    ".pytest_cache/**",
    ".DS_Store",
    "Thumbs.db",
    LOCK_NAME,
    "outputs/tradingview-alerts.jsonl",
    "**/.conflict-*",
]

# mtime drift tolerance: SMB/exFAT round to 2s, NTFS to 100ns. Treat any
# difference smaller than this as "same time" (manual conflict).
MTIME_TIE_SECONDS = 2.5


@dataclass
class SyncStats:
    pulled: int = 0
    pushed: int = 0
    skipped_same: int = 0
    conflicts: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    deleted_local: int = 0
    deleted_nas: int = 0


def log(msg: str, *, quiet: bool = False, force: bool = False) -> None:
    if force or not quiet:
        print(msg, flush=True)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def matches_any(rel: str, patterns: list[str]) -> bool:
    rel_posix = rel.replace(os.sep, "/")
    for pat in patterns:
        pat_posix = pat.replace(os.sep, "/")
        if fnmatch.fnmatch(rel_posix, pat_posix):
            return True
        # also try matching against basename for simple patterns like *.pyc
        if "/" not in pat_posix and fnmatch.fnmatch(os.path.basename(rel_posix), pat_posix):
            return True
    return False


def should_include(rel: str, includes: list[str], excludes: list[str]) -> bool:
    if matches_any(rel, excludes):
        return False
    if not includes:
        return True
    # match if any include pattern matches the rel path OR any ancestor dir
    rel_posix = rel.replace(os.sep, "/")
    if matches_any(rel_posix, includes):
        return True
    parts = rel_posix.split("/")
    for i in range(1, len(parts)):
        head = "/".join(parts[:i]) + "/"
        if matches_any(head + "*", includes) or matches_any(head + "**", includes):
            return True
    return False


def walk_files(root: Path, includes: list[str], excludes: list[str]) -> dict[str, Path]:
    """Return {relative_posix_path: absolute_path} for files under root."""
    found: dict[str, Path] = {}
    if not root.exists():
        return found
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune excluded directories early for speed
        rel_dir = os.path.relpath(dirpath, root)
        rel_dir_posix = "" if rel_dir == "." else rel_dir.replace(os.sep, "/") + "/"
        # Filter dirnames in-place to avoid descending into excluded trees
        keep_dirs = []
        for d in dirnames:
            sub = (rel_dir_posix + d).rstrip("/")
            if matches_any(sub + "/", excludes) or matches_any(sub, excludes):
                continue
            keep_dirs.append(d)
        dirnames[:] = keep_dirs

        for name in filenames:
            rel = (rel_dir_posix + name) if rel_dir_posix else name
            if not should_include(rel, includes, excludes):
                continue
            found[rel] = Path(dirpath) / name
    return found


def safe_mtime(p: Path) -> float:
    try:
        return p.stat().st_mtime
    except OSError:
        return 0.0


def copy_file(src: Path, dst: Path, *, dry_run: bool) -> None:
    if dry_run:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    # copy2 preserves mtime, which is what the next sync run uses to decide
    shutil.copy2(src, dst)


def park_conflict(target: Path, *, dry_run: bool) -> Path:
    """Move target to target.with .conflict-<utc>.<ext> and return the new path."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    parked = target.with_name(f"{target.name}.conflict-{ts}")
    if dry_run:
        return parked
    target.replace(parked)
    return parked


def acquire_lock(local: Path) -> Path | None:
    lock = local / LOCK_NAME
    if lock.exists():
        return None
    try:
        lock.write_text(
            f"pid={os.getpid()}\nstarted={datetime.now(timezone.utc).isoformat()}\n",
            encoding="utf-8",
        )
        return lock
    except OSError:
        return None


def release_lock(lock: Path | None) -> None:
    if lock and lock.exists():
        try:
            lock.unlink()
        except OSError:
            pass


def default_nas_path() -> str | None:
    env = os.environ.get("OBSIDIAN_NAS_PATH")
    if env:
        return env
    if sys.platform.startswith("win"):
        for candidate in (
            r"Z:\Claude\altamira-workspace",
            r"\\Landino-NAS\AI Automation\Claude\altamira-workspace",
        ):
            if Path(candidate).exists():
                return candidate
    return None


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Sync Obsidian vault between NAS and local workspace.")
    p.add_argument("--nas", default=default_nas_path(),
                   help="NAS vault path (or set OBSIDIAN_NAS_PATH).")
    p.add_argument("--local", default=str(WORKSPACE),
                   help="Local vault path (default: workspace root).")
    p.add_argument("--mode", choices=["pull", "push", "both"], default="both",
                   help="pull (NAS→local), push (local→NAS), both (default).")
    p.add_argument("--dry-run", action="store_true", help="Report without writing.")
    p.add_argument("--delete", action="store_true",
                   help="In pull/push mode, delete files at target that don't exist at source. "
                        "Ignored in 'both' mode for safety.")
    p.add_argument("--include", action="append", default=[],
                   help="Extra include glob (repeatable).")
    p.add_argument("--exclude", action="append", default=[],
                   help="Extra exclude glob (repeatable).")
    p.add_argument("--quiet", action="store_true", help="Only print summary.")
    return p.parse_args()


def reconcile(local_files: dict[str, Path], nas_files: dict[str, Path],
              local_root: Path, nas_root: Path, args: argparse.Namespace,
              stats: SyncStats) -> None:
    all_keys = sorted(set(local_files) | set(nas_files))

    for rel in all_keys:
        l = local_files.get(rel)
        n = nas_files.get(rel)

        # Both sides have the file
        if l and n:
            l_mtime, n_mtime = safe_mtime(l), safe_mtime(n)
            try:
                same_size = l.stat().st_size == n.stat().st_size
            except OSError as e:
                stats.errors.append(f"stat failed for {rel}: {e}")
                continue
            if same_size and sha256_of(l) == sha256_of(n):
                stats.skipped_same += 1
                continue

            delta = n_mtime - l_mtime
            # Tie window with content mismatch → real conflict
            if abs(delta) <= MTIME_TIE_SECONDS:
                stats.conflicts.append(rel)
                log(f"  CONFLICT  {rel}  (both modified within {MTIME_TIE_SECONDS}s)", quiet=args.quiet)
                # Park the older copy on each side so neither version is lost.
                if args.mode in ("pull", "both"):
                    parked = park_conflict(l, dry_run=args.dry_run)
                    log(f"            local parked → {parked.name}", quiet=args.quiet)
                    if args.mode == "pull" or args.mode == "both":
                        try:
                            copy_file(n, l, dry_run=args.dry_run)
                            stats.pulled += 1
                            log(f"            NAS copy installed at local", quiet=args.quiet)
                        except OSError as e:
                            stats.errors.append(f"copy NAS→local failed for {rel}: {e}")
                if args.mode == "push":
                    parked = park_conflict(n, dry_run=args.dry_run)
                    log(f"            NAS parked → {parked.name}", quiet=args.quiet)
                    try:
                        copy_file(l, n, dry_run=args.dry_run)
                        stats.pushed += 1
                        log(f"            local copy installed at NAS", quiet=args.quiet)
                    except OSError as e:
                        stats.errors.append(f"copy local→NAS failed for {rel}: {e}")
                continue

            # Newer wins
            if n_mtime > l_mtime and args.mode in ("pull", "both"):
                try:
                    copy_file(n, l, dry_run=args.dry_run)
                    stats.pulled += 1
                    log(f"  PULL      {rel}", quiet=args.quiet)
                except OSError as e:
                    stats.errors.append(f"copy NAS→local failed for {rel}: {e}")
            elif l_mtime > n_mtime and args.mode in ("push", "both"):
                try:
                    copy_file(l, n, dry_run=args.dry_run)
                    stats.pushed += 1
                    log(f"  PUSH      {rel}", quiet=args.quiet)
                except OSError as e:
                    stats.errors.append(f"copy local→NAS failed for {rel}: {e}")
            else:
                stats.skipped_same += 1
            continue

        # Only NAS has it
        if n and not l:
            if args.mode in ("pull", "both"):
                target = local_root / rel
                try:
                    copy_file(n, target, dry_run=args.dry_run)
                    stats.pulled += 1
                    log(f"  PULL  +   {rel}", quiet=args.quiet)
                except OSError as e:
                    stats.errors.append(f"copy NAS→local failed for {rel}: {e}")
            elif args.mode == "push" and args.delete:
                if not args.dry_run:
                    try:
                        n.unlink()
                    except OSError as e:
                        stats.errors.append(f"delete NAS {rel}: {e}")
                        continue
                stats.deleted_nas += 1
                log(f"  DEL NAS   {rel}", quiet=args.quiet)
            continue

        # Only local has it
        if l and not n:
            if args.mode in ("push", "both"):
                target = nas_root / rel
                try:
                    copy_file(l, target, dry_run=args.dry_run)
                    stats.pushed += 1
                    log(f"  PUSH  +   {rel}", quiet=args.quiet)
                except OSError as e:
                    stats.errors.append(f"copy local→NAS failed for {rel}: {e}")
            elif args.mode == "pull" and args.delete:
                if not args.dry_run:
                    try:
                        l.unlink()
                    except OSError as e:
                        stats.errors.append(f"delete local {rel}: {e}")
                        continue
                stats.deleted_local += 1
                log(f"  DEL LOCAL {rel}", quiet=args.quiet)
            continue


def main() -> int:
    args = parse_args()

    if not args.nas:
        log("ERROR: NAS path not provided. Use --nas or set OBSIDIAN_NAS_PATH.", force=True)
        return 1

    local_root = Path(args.local).resolve()
    nas_root = Path(args.nas).resolve()

    if not local_root.exists():
        log(f"ERROR: local path does not exist: {local_root}", force=True)
        return 1
    if args.mode in ("pull", "both") and not nas_root.exists():
        log(f"ERROR: NAS path does not exist or is unreachable: {nas_root}", force=True)
        return 1
    if args.mode == "push" and not nas_root.exists():
        if args.dry_run:
            log(f"NOTE: NAS path missing (dry-run): {nas_root}")
        else:
            try:
                nas_root.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                log(f"ERROR: could not create NAS path {nas_root}: {e}", force=True)
                return 1

    if args.mode == "both" and args.delete:
        log("NOTE: --delete is ignored in 'both' mode (would be ambiguous).", force=True)
        args.delete = False

    includes = DEFAULT_INCLUDES + args.include
    excludes = DEFAULT_EXCLUDES + args.exclude

    log(f"local : {local_root}", quiet=args.quiet)
    log(f"NAS   : {nas_root}", quiet=args.quiet)
    log(f"mode  : {args.mode}{' (dry-run)' if args.dry_run else ''}", quiet=args.quiet)
    log("", quiet=args.quiet)

    lock = acquire_lock(local_root)
    if lock is None:
        log(f"ERROR: another sync appears to be running (lock at {local_root / LOCK_NAME}). "
            f"Delete the lock file if you're sure no other sync is active.", force=True)
        return 1

    try:
        t0 = time.monotonic()
        log("scanning local…", quiet=args.quiet)
        local_files = walk_files(local_root, includes, excludes)
        log(f"  {len(local_files)} files", quiet=args.quiet)
        log("scanning NAS…", quiet=args.quiet)
        nas_files = walk_files(nas_root, includes, excludes)
        log(f"  {len(nas_files)} files", quiet=args.quiet)
        log("", quiet=args.quiet)

        stats = SyncStats()
        reconcile(local_files, nas_files, local_root, nas_root, args, stats)

        elapsed = time.monotonic() - t0
        log("", quiet=args.quiet, force=True)
        log("─" * 60, force=True)
        log(f"Summary ({elapsed:.1f}s){' [dry-run]' if args.dry_run else ''}", force=True)
        log(f"  pulled    NAS→local : {stats.pulled}", force=True)
        log(f"  pushed    local→NAS : {stats.pushed}", force=True)
        log(f"  unchanged           : {stats.skipped_same}", force=True)
        if args.delete:
            log(f"  deleted   local     : {stats.deleted_local}", force=True)
            log(f"  deleted   NAS       : {stats.deleted_nas}", force=True)
        log(f"  conflicts           : {len(stats.conflicts)}", force=True)
        if stats.conflicts:
            for rel in stats.conflicts[:20]:
                log(f"      ! {rel}", force=True)
            if len(stats.conflicts) > 20:
                log(f"      … and {len(stats.conflicts) - 20} more", force=True)
        if stats.errors:
            log(f"  errors              : {len(stats.errors)}", force=True)
            for msg in stats.errors[:20]:
                log(f"      x {msg}", force=True)
            if len(stats.errors) > 20:
                log(f"      … and {len(stats.errors) - 20} more", force=True)
            return 2
        return 0
    finally:
        release_lock(lock)


if __name__ == "__main__":
    sys.exit(main())
