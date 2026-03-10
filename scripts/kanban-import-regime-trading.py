#!/usr/bin/env python3
"""
Import the Regime Trading Dashboard project and its 10 feature tasks to the kanban board API.
Requires the kanban app running (http://localhost:3004 UI, http://localhost:3005 API).

Usage:
  python scripts/kanban-import-regime-trading.py
  python scripts/kanban-import-regime-trading.py --api-url http://localhost:3005
"""

import argparse
import csv
import json
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

WORKSPACE = Path(__file__).resolve().parent.parent
IMPORT_CSV = WORKSPACE / "outputs" / "kanban-regime-trading-import.csv"
DEFAULT_API = "http://localhost:3005"


def main() -> int:
    ap = argparse.ArgumentParser(description="Import Regime Trading Dashboard project to kanban board via API.")
    ap.add_argument("--api-url", default=DEFAULT_API, help="Kanban API base URL")
    ap.add_argument("--dry-run", action="store_true", help="Print JSON only, do not POST")
    args = ap.parse_args()

    if not requests:
        print("Install requests: pip install requests", file=sys.stderr)
        return 1

    if not IMPORT_CSV.exists():
        print(f"CSV not found: {IMPORT_CSV}", file=sys.stderr)
        return 1

    project_name = None
    tasks = []
    with open(IMPORT_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            proj = (row.get("Project") or "").strip().strip('"')
            if proj:
                project_name = proj
            task_id = (row.get("Task ID") or "").strip().strip('"')
            title = (row.get("Title") or "").strip().strip('"')
            column = (row.get("Column") or "backlog").strip().strip('"').lower().replace(" ", "-")
            priority = (row.get("Priority") or "medium").strip().strip('"').lower()
            desc = (row.get("Description") or "").strip().strip('"')
            tasks.append({
                "id": task_id,
                "title": title,
                "description": desc,
                "columnId": column,
                "priority": priority,
            })

    if not project_name or not tasks:
        print("No project or tasks in CSV.", file=sys.stderr)
        return 1

    payload = {"name": project_name, "tasks": tasks}
    if args.dry_run:
        print(json.dumps(payload, indent=2))
        return 0

    url = f"{args.api_url.rstrip('/')}/api/projects"
    try:
        r = requests.post(url, json=payload, timeout=15)
        r.raise_for_status()
        data = r.json()
        print(f"Created project: {data.get('name', data.get('id', 'OK'))}")
        print(f"Tasks added: {len(tasks)}")
        return 0
    except requests.HTTPError as e:
        print(f"API error: {e.response.status_code}", file=sys.stderr)
        if e.response.text:
            print(e.response.text[:500], file=sys.stderr)
        return 1
    except requests.RequestException as e:
        print(f"Request failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
