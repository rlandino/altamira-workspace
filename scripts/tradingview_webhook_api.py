#!/usr/bin/env python3
"""
Altamira Capital — TradingView Webhook Bridge
==============================================
FastAPI server that receives alert webhooks from the TradingView desktop app
(or web) and exposes them to the Altamira Dashboard (Next.js, :3001) and any
other local consumers.

The TradingView desktop app is a Chromium wrapper around the web app; the only
programmatic hook it exposes is the **Webhook URL** field on an Alert. When an
alert fires, TradingView's servers POST a JSON payload to that URL — so this
service must be reachable from the public internet (use ngrok or cloudflared
in front of it; the dashboard reads from localhost directly).

Usage:
  python -m uvicorn scripts.tradingview_webhook_api:app --host 0.0.0.0 --port 8002
  # Or: uvicorn scripts.tradingview_webhook_api:app --reload --host 0.0.0.0 --port 8002

Env:
  TRADINGVIEW_WEBHOOK_SECRET — optional shared secret. If set, every inbound
                               alert must include the same value as either the
                               X-TV-Secret header or a top-level "secret" field
                               in the JSON body, otherwise it is rejected with
                               401. TradingView does not let you set custom
                               headers, so put the secret in the message body.

Endpoints:
  POST /api/tradingview/webhook                  — receive an alert (TradingView -> here)
  GET  /api/tradingview/alerts?limit=&symbol=    — list recent alerts (dashboard -> here)
  GET  /api/tradingview/alerts/latest?symbol=    — most recent alert (optional symbol filter)
  DELETE /api/tradingview/alerts                 — clear the alert log (?confirm=yes)
  GET  /api/tradingview/health                   — health check

Storage:
  Alerts are appended to outputs/tradingview-alerts.jsonl as newline-delimited
  JSON. Each line is a single alert record. Tail with `tail -f` for a live feed.
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

WORKSPACE = Path(__file__).resolve().parent.parent
ALERTS_FILE = WORKSPACE / "outputs" / "tradingview-alerts.jsonl"
SECRET = os.environ.get("TRADINGVIEW_WEBHOOK_SECRET", "").strip()

app = FastAPI(
    title="Altamira TradingView Webhook Bridge",
    version="1.0.0",
    description="Receives TradingView alert webhooks and exposes them to the Altamira Dashboard.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "http://localhost:8501",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _ensure_alerts_file() -> None:
    ALERTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not ALERTS_FILE.exists():
        ALERTS_FILE.touch()


def _append_alert(record: dict[str, Any]) -> None:
    _ensure_alerts_file()
    with ALERTS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _read_alerts() -> list[dict[str, Any]]:
    if not ALERTS_FILE.exists():
        return []
    out: list[dict[str, Any]] = []
    with ALERTS_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def _check_secret(header_secret: str | None, body_secret: str | None) -> None:
    if not SECRET:
        return
    provided = (header_secret or body_secret or "").strip()
    if provided != SECRET:
        raise HTTPException(status_code=401, detail="invalid or missing webhook secret")


@app.get("/api/tradingview/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "tradingview-webhook-bridge",
        "secret_required": bool(SECRET),
        "alerts_file": str(ALERTS_FILE),
        "alerts_file_exists": ALERTS_FILE.exists(),
        "timestamp": time.time(),
    }


@app.post("/api/tradingview/webhook")
async def receive_webhook(
    request: Request,
    x_tv_secret: str | None = Header(default=None, alias="X-TV-Secret"),
) -> dict[str, Any]:
    """Receive an alert from TradingView. Body is JSON or plain text."""
    raw = await request.body()
    text = raw.decode("utf-8", errors="replace").strip()

    payload: Any
    try:
        payload = json.loads(text) if text else {}
    except json.JSONDecodeError:
        payload = {"message": text}

    body_secret = None
    if isinstance(payload, dict):
        body_secret = payload.pop("secret", None)
    _check_secret(x_tv_secret, body_secret)

    record = {
        "received_at": _now_iso(),
        "source_ip": request.client.host if request.client else None,
        "payload": payload,
        "raw_text": text if not isinstance(payload, dict) else None,
    }

    if isinstance(payload, dict):
        for key in ("ticker", "symbol", "strategy", "action", "side", "price", "time"):
            if key in payload:
                record[key] = payload[key]
        if "ticker" in payload and "symbol" not in record:
            record["symbol"] = payload["ticker"]

    _append_alert(record)
    return {"status": "received", "received_at": record["received_at"]}


@app.get("/api/tradingview/alerts")
def list_alerts(
    limit: int = Query(50, ge=1, le=1000),
    symbol: str | None = Query(None, description="Filter by symbol/ticker (case-insensitive)"),
) -> dict[str, Any]:
    """Return recent alerts, newest first."""
    alerts = _read_alerts()
    if symbol:
        s = symbol.strip().upper()
        alerts = [
            a for a in alerts
            if str(a.get("symbol") or a.get("ticker") or "").upper() == s
        ]
    alerts.reverse()
    return {"count": len(alerts), "alerts": alerts[:limit]}


@app.get("/api/tradingview/alerts/latest")
def latest_alert(
    symbol: str | None = Query(None, description="Filter by symbol/ticker (case-insensitive)"),
) -> dict[str, Any]:
    alerts = _read_alerts()
    if symbol:
        s = symbol.strip().upper()
        alerts = [
            a for a in alerts
            if str(a.get("symbol") or a.get("ticker") or "").upper() == s
        ]
    if not alerts:
        return {"alert": None}
    return {"alert": alerts[-1]}


@app.delete("/api/tradingview/alerts")
def clear_alerts(confirm: str = Query("", description="Must equal 'yes' to clear")) -> dict[str, Any]:
    if confirm != "yes":
        raise HTTPException(status_code=400, detail="pass ?confirm=yes to clear the alert log")
    if ALERTS_FILE.exists():
        ALERTS_FILE.unlink()
    _ensure_alerts_file()
    return {"status": "cleared", "alerts_file": str(ALERTS_FILE)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
