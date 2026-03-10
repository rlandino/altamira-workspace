#!/usr/bin/env python3
"""
Deploy the Holding Snapshot section to the Streamlit app that serves /a.

Copies streamlit_holding_snapshot.py and context/holding-monthly-snapshots.json
into the app directory, then optionally injects the section into the page that
serves route /a (e.g. pages/a.py).

Usage:
  # Deploy to app at given path (copy files + try to inject into page /a):
  python scripts/deploy-holding-snapshot-to-app.py --app-dir "X:\\path\\to\\streamlit-app"

  # Only copy files (no injection); get snippet to paste manually:
  python scripts/deploy-holding-snapshot-to-app.py --app-dir "X:\\path\\to\\app" --no-inject

  # Print snippet and instructions only (no copy):
  python scripts/deploy-holding-snapshot-to-app.py --snippet-only
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
FRAGMENT_SRC = WORKSPACE / "scripts" / "streamlit_holding_snapshot.py"
JSON_SRC = WORKSPACE / "context" / "holding-monthly-snapshots.json"

# Streamlit multi-page: pages/a.py -> route /a; pages/1_Portfolio_Snapshots.py -> /Portfolio_Snapshots
PAGE_CANDIDATES = ["a.py", "1_a.py", "Portfolio_Snapshots.py", "1_Portfolio_Snapshots.py", "portfolio_snapshots.py"]

INJECT_MARKER = "render_holding_snapshot"
INJECT_BLOCK = '''
# Holding Snapshot (monthly table per holding)
from streamlit_holding_snapshot import render_holding_snapshot
render_holding_snapshot()
'''


def find_page_for_a(app_dir: Path) -> Path | None:
    """Return path to page that likely serves /a (Portfolio Snapshots)."""
    pages_dir = app_dir / "pages"
    if not pages_dir.is_dir():
        return None
    # Prefer exact name
    for name in PAGE_CANDIDATES:
        p = pages_dir / name
        if p.exists():
            return p
    # Search for "Portfolio" or "Snapshot" in page files
    for f in pages_dir.glob("*.py"):
        try:
            if "Portfolio" in f.read_text(encoding="utf-8") or "Snapshot" in f.read_text(encoding="utf-8"):
                return f
        except Exception:
            continue
    return None


def inject_into_page(page_path: Path) -> bool:
    """Add import and render_holding_snapshot() to page if not already present."""
    try:
        text = page_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Could not read {page_path}: {e}", file=sys.stderr)
        return False
    if INJECT_MARKER in text:
        print(f"Already contains Holding Snapshot: {page_path}")
        return True
    # Prefer inserting after "Portfolio Snapshots" or similar heading
    for pattern in [
        r'(st\.(subheader|title)\s*\(\s*["\']Portfolio Snapshots["\']\s*\)\s*\n)',
        r'(st\.(subheader|title)\s*\(\s*["\']Portfolio["\']\s*\)\s*\n)',
        r'(\n)(def\s+\w+\s*\([^)]*\)\s*:\s*\n\s+st\.)',
    ]:
        m = re.search(pattern, text)
        if m:
            insert_pos = m.end()
            new_text = text[:insert_pos] + INJECT_BLOCK + text[insert_pos:]
            break
    else:
        # Insert before last line or at end of file
        new_text = text.rstrip() + "\n\n" + INJECT_BLOCK.strip() + "\n"
    try:
        page_path.write_text(new_text, encoding="utf-8")
        print(f"Injected Holding Snapshot into: {page_path}")
        return True
    except Exception as e:
        print(f"Could not write {page_path}: {e}", file=sys.stderr)
        return False


def deploy(app_dir: Path, inject: bool) -> None:
    """Copy fragment and JSON to app_dir; optionally inject into page /a."""
    app_dir = app_dir.resolve()
    if not app_dir.is_dir():
        print(f"Not a directory: {app_dir}", file=sys.stderr)
        sys.exit(1)
    if not FRAGMENT_SRC.exists():
        print(f"Fragment not found: {FRAGMENT_SRC}", file=sys.stderr)
        sys.exit(1)

    # Copy fragment
    dest_fragment = app_dir / "streamlit_holding_snapshot.py"
    shutil.copy2(FRAGMENT_SRC, dest_fragment)
    print(f"Copied: {dest_fragment}")

    # Copy JSON so deployed app finds data without env var
    dest_context = app_dir / "context"
    dest_context.mkdir(parents=True, exist_ok=True)
    dest_json = dest_context / "holding-monthly-snapshots.json"
    if JSON_SRC.exists():
        if JSON_SRC.resolve() != dest_json.resolve():
            try:
                shutil.copy2(JSON_SRC, dest_json)
                print(f"Copied: {dest_json}")
            except OSError as e:
                print(f"Warning: could not copy JSON ({e}). Use HOLDING_SNAPSHOT_JSON if needed.", file=sys.stderr)
        else:
            print(f"Data already at: {dest_json}")
    else:
        print(f"Warning: {JSON_SRC} not found. Run build-holding-monthly-snapshots.py first, or set HOLDING_SNAPSHOT_JSON.", file=sys.stderr)

    if inject:
        page = find_page_for_a(app_dir)
        if page:
            inject_into_page(page)
        else:
            print("No page found for /a (pages/a.py or similar). Add the section manually — see snippet below.")
            print_snippet()


def print_snippet() -> None:
    """Print code to paste into the page that serves /a."""
    print("\n--- Paste this into the page that serves Portfolio Snapshots (/a) ---\n")
    print(INJECT_BLOCK.strip())
    print("\n--- End snippet ---\n")
    print("Or set HOLDING_SNAPSHOT_JSON to the full path of context/holding-monthly-snapshots.json.")


def main() -> None:
    ap = argparse.ArgumentParser(description="Deploy Holding Snapshot section to Streamlit app.")
    ap.add_argument("--app-dir", type=Path, help="Path to Streamlit app root (where app.py or pages/ live)")
    ap.add_argument("--no-inject", action="store_true", help="Only copy files; do not inject into page")
    ap.add_argument("--snippet-only", action="store_true", help="Only print snippet and instructions")
    args = ap.parse_args()

    if args.snippet_only:
        print_snippet()
        return

    if not args.app_dir:
        print("Usage: python scripts/deploy-holding-snapshot-to-app.py --app-dir <path-to-streamlit-app>", file=sys.stderr)
        print("Or: --snippet-only to print code to paste manually.", file=sys.stderr)
        sys.exit(1)

    deploy(args.app_dir, inject=not args.no_inject)


if __name__ == "__main__":
    main()
