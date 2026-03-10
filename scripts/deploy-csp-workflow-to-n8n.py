#!/usr/bin/env python3
"""
Deploy CSP Daily Scan workflow to n8n cloud via REST API.

Requires:
  - N8N_API_KEY: API key from n8n (Settings → API in n8n cloud, or env)
  - N8N_API_URL: (optional) Base URL, e.g. https://rlandino.app.n8n.cloud

Usage:
  set N8N_API_KEY=your_key
  python scripts/deploy-csp-workflow-to-n8n.py
"""
import json
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("pip install requests", file=sys.stderr)
    sys.exit(1)

WORKSPACE = Path(__file__).resolve().parent.parent
WORKFLOW_JSON = WORKSPACE / "outputs" / "n8n-workflow-csp-daily-scan.json"
DEPLOY_PAYLOAD = WORKSPACE / "outputs" / "csp-deploy-payload.json"


def main():
    api_key = os.environ.get("N8N_API_KEY")
    base_url = (os.environ.get("N8N_API_URL") or "https://rlandino.app.n8n.cloud").rstrip("/")

    if not api_key:
        print("N8N_API_KEY is not set.", file=sys.stderr)
        print("Create an API key in n8n: Settings → API (or Personal Settings → API Key).", file=sys.stderr)
        print("Then run: set N8N_API_KEY=your_key", file=sys.stderr)
        sys.exit(1)

    # Load payload (credentials already stripped in csp-deploy-payload.json)
    if DEPLOY_PAYLOAD.exists():
        with open(DEPLOY_PAYLOAD) as f:
            payload = json.load(f)
    else:
        with open(WORKFLOW_JSON) as f:
            w = json.load(f)
        for n in w.get("nodes", []):
            n.pop("credentials", None)
        payload = {
            "name": w["name"],
            "nodes": w["nodes"],
            "connections": w["connections"],
            "settings": w.get("settings", {}),
        }

    url = f"{base_url}/api/v1/workflows"
    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    print(f"Deploying to {base_url}...", file=sys.stderr)
    resp = requests.post(url, json=payload, headers=headers, timeout=30)

    if not resp.ok:
        print(f"Error {resp.status_code}: {resp.text}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    wf_id = data.get("id") or data.get("data", {}).get("id")
    wf_name = data.get("name") or data.get("data", {}).get("name", payload.get("name", ""))

    print(f"Created workflow: {wf_name} (id: {wf_id})")
    print(f"Open: {base_url}/workflow/{wf_id}")
    print("Next: Configure credentials (FMP, Telegram, Google Sheets), set TELEGRAM_CHAT_ID and GOOGLE_SHEET_ID, then activate.")


if __name__ == "__main__":
    main()
