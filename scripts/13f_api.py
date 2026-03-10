#!/usr/bin/env python3
"""
Altamira Capital — 13F API Bridge
=================================
FastAPI server that runs 13F scripts (subprocess) and returns JSON for dashboard consumption.
Optional in-memory cache (default 5 min TTL). CORS enabled for local dashboard (3001, 8501).

Usage:
  uvicorn scripts.13f_api:app --reload --host 0.0.0.0 --port 8000
  # Or from workspace root:
  python -m uvicorn scripts.13f_api:app --host 0.0.0.0 --port 8000

Endpoints:
  GET /api/13f/filers          — list filers and periods
  GET /api/13f/holdings        — holdings for cik + period (?cik=&period=&cusip=)
  GET /api/13f/diff            — holdings diff (?cik=&prior=&current=)
  GET /api/13f/copycat         — copycat portfolio (?ciks=&weight=value|equal&consensus_min=)
  GET /api/13f/screener        — stock screener (?min_filers=&min_value=)
  GET /api/13f/heatmap         — heat map matrix (?top_filers=&top_cusips=)
  GET /api/13f/fund-metrics    — fund metrics (?cik=&prior=&current=)
  GET /api/13f/health          — health check
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
SCRIPTS = WORKSPACE / "scripts"
DATA_DIR = WORKSPACE / "outputs" / "13f"
CACHE_TTL = int(os.environ.get("13F_API_CACHE_TTL", "300"))  # seconds

# In-memory cache: key -> (payload, expiry_ts)
_cache: dict[str, tuple[object, float]] = {}


def _cache_key(prefix: str, **kwargs) -> str:
    h = hashlib.sha256(json.dumps(sorted(kwargs.items()), sort_keys=True).encode()).hexdigest()[:16]
    return f"{prefix}:{h}"


def _get_cached(key: str) -> object | None:
    if key not in _cache:
        return None
    payload, expiry = _cache[key]
    if time.time() > expiry:
        del _cache[key]
        return None
    return payload


def _set_cache(key: str, payload: object) -> None:
    _cache[key] = (payload, time.time() + CACHE_TTL)


def _run_json(cmd: list[str], cwd: Path | None = None) -> tuple[object | None, str]:
    """Run command; return (parsed JSON from stdout, stderr). If JSON fails, return (None, stderr)."""
    cwd = cwd or WORKSPACE
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        err = (result.stderr or "").strip()
        out = (result.stdout or "").strip()
        if result.returncode != 0:
            return None, err or out or f"exit {result.returncode}"
        if not out:
            return None, err
        try:
            return json.loads(out), err
        except json.JSONDecodeError:
            return None, err or "Invalid JSON"
    except subprocess.TimeoutExpired:
        return None, "Timeout"
    except Exception as e:
        return None, str(e)


def _run_json_out_file(cmd: list[str], out_path: Path, cwd: Path | None = None) -> tuple[object | None, str]:
    """Run command that writes JSON to out_path; return (parsed JSON, stderr)."""
    cwd = cwd or WORKSPACE
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        err = (result.stderr or "").strip()
        if result.returncode != 0:
            return None, err or (result.stdout or "").strip() or f"exit {result.returncode}"
        if not out_path.exists():
            return None, err or "Output file not created"
        try:
            data = json.loads(out_path.read_text(encoding="utf-8"))
            return data, err
        except Exception as e:
            return None, err or str(e)
        finally:
            try:
                out_path.unlink(missing_ok=True)
            except OSError:
                pass
    except subprocess.TimeoutExpired:
        return None, "Timeout"
    except Exception as e:
        return None, str(e)


try:
    from fastapi import FastAPI, Query
    from fastapi.middleware.cors import CORSMiddleware
except ImportError:
    FastAPI = None  # type: ignore
    Query = None  # type: ignore
    CORSMiddleware = None  # type: ignore

if FastAPI is None:

    def app(*args, **kwargs):  # type: ignore
        raise RuntimeError("Install fastapi and uvicorn: pip install fastapi uvicorn")

else:

    app = FastAPI(title="Altamira 13F API", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3001",
            "http://localhost:8501",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:8501",
        ],
        allow_credentials=True,
        allow_methods=["GET", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.get("/api/13f/health")
    def health():
        return {"status": "ok", "data_dir": str(DATA_DIR), "data_dir_exists": DATA_DIR.exists()}

    @app.get("/api/13f/filers")
    def list_filers(
        data_dir: str | None = Query(None, description="Override data directory"),
    ):
        key = _cache_key("filers", data_dir=data_dir or "")
        if cached := _get_cached(key):
            return cached
        d = data_dir or str(DATA_DIR)
        cmd = [sys_executable(), str(SCRIPTS / "query-13f.py"), "--list", "--data-dir", d]
        data, err = _run_json(cmd)
        if data is None:
            return {"error": err, "filings": []}
        _set_cache(key, data)
        return data

    @app.get("/api/13f/holdings")
    def get_holdings(
        cik: str = Query(..., description="Filer CIK"),
        period: str = Query(..., description="Period end YYYY-MM-DD or YYYYMMDD"),
        cusip: str | None = Query(None),
        data_dir: str | None = Query(None),
    ):
        key = _cache_key("holdings", cik=cik, period=period, cusip=cusip or "", data_dir=data_dir or "")
        if cached := _get_cached(key):
            return cached
        d = data_dir or str(DATA_DIR)
        cmd = [sys_executable(), str(SCRIPTS / "query-13f.py"), "--cik", cik, "--period", period, "--data-dir", d]
        if cusip:
            cmd.extend(["--cusip", cusip])
        data, err = _run_json(cmd)
        if data is None:
            return {"error": err}
        _set_cache(key, data)
        return data

    @app.get("/api/13f/diff")
    def get_diff(
        cik: str = Query(..., description="Filer CIK"),
        prior: str = Query(..., description="Prior period end"),
        current: str = Query(..., description="Current period end"),
        data_dir: str | None = Query(None),
    ):
        key = _cache_key("diff", cik=cik, prior=prior, current=current, data_dir=data_dir or "")
        if cached := _get_cached(key):
            return cached
        d = data_dir or str(DATA_DIR)
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            cmd = [
                sys_executable(),
                str(SCRIPTS / "13f-holdings-diff.py"),
                "--cik", cik,
                "--prior", prior,
                "--current", current,
                "--data-dir", d,
                "--json-out", path,
            ]
            data, err = _run_json_out_file(cmd, Path(path))
        finally:
            try:
                Path(path).unlink(missing_ok=True)
            except OSError:
                pass
        if data is None:
            return {"error": err}
        _set_cache(key, data)
        return data

    @app.get("/api/13f/copycat")
    def get_copycat(
        ciks: str = Query(..., description="Comma-separated CIKs"),
        weight: str = Query("value", description="value or equal"),
        consensus_min: int | None = Query(None),
        period: str | None = Query(None),
        data_dir: str | None = Query(None),
    ):
        key = _cache_key("copycat", ciks=ciks, weight=weight, consensus_min=consensus_min or 0, period=period or "", data_dir=data_dir or "")
        if cached := _get_cached(key):
            return cached
        d = data_dir or str(DATA_DIR)
        cmd = [sys_executable(), str(SCRIPTS / "copycat-13f.py"), "--ciks", ciks, "--weight", weight, "--data-dir", d]
        if consensus_min is not None:
            cmd.extend(["--consensus-min", str(consensus_min)])
        if period:
            cmd.extend(["--period", period])
        data, err = _run_json(cmd)
        if data is None:
            return {"error": err}
        _set_cache(key, data)
        return data

    @app.get("/api/13f/screener")
    def get_screener(
        min_filers: int = Query(1, description="Minimum filers holding"),
        min_value: float = Query(0, description="Minimum aggregate value (thousands)"),
        data_dir: str | None = Query(None),
    ):
        key = _cache_key("screener", min_filers=min_filers, min_value=min_value, data_dir=data_dir or "")
        if cached := _get_cached(key):
            return cached
        d = data_dir or str(DATA_DIR)
        cmd = [
            sys_executable(),
            str(SCRIPTS / "13f-stock-screener.py"),
            "--min-filers", str(min_filers),
            "--min-value", str(min_value),
            "--data-dir", d,
        ]
        data, err = _run_json(cmd)
        if data is None:
            return {"error": err, "holdings": [], "count": 0}
        _set_cache(key, data)
        return data

    @app.get("/api/13f/heatmap")
    def get_heatmap(
        top_filers: int | None = Query(None),
        top_cusips: int | None = Query(None),
        data_dir: str | None = Query(None),
    ):
        key = _cache_key("heatmap", top_filers=top_filers or 0, top_cusips=top_cusips or 0, data_dir=data_dir or "")
        if cached := _get_cached(key):
            return cached
        d = data_dir or str(DATA_DIR)
        cmd = [sys_executable(), str(SCRIPTS / "13f-heatmap-export.py"), "--format", "json", "--data-dir", d]
        if top_filers is not None:
            cmd.extend(["--top-filers", str(top_filers)])
        if top_cusips is not None:
            cmd.extend(["--top-cusips", str(top_cusips)])
        data, err = _run_json(cmd)
        if data is None:
            return {"error": err, "filers": [], "cusips": [], "matrix": []}
        _set_cache(key, data)
        return data

    @app.get("/api/13f/fund-metrics")
    def get_fund_metrics(
        cik: str = Query(..., description="Filer CIK"),
        prior: str | None = Query(None),
        current: str | None = Query(None),
        data_dir: str | None = Query(None),
    ):
        key = _cache_key("fund", cik=cik, prior=prior or "", current=current or "", data_dir=data_dir or "")
        if cached := _get_cached(key):
            return cached
        d = data_dir or str(DATA_DIR)
        cmd = [sys_executable(), str(SCRIPTS / "13f-fund-performance.py"), "--cik", cik, "--data-dir", d]
        if prior and current:
            cmd.extend(["--prior", prior, "--current", current])
        data, err = _run_json(cmd)
        if data is None:
            return {"error": err}
        _set_cache(key, data)
        return data


def sys_executable() -> str:
    return os.environ.get("UVICORN_PYTHON", sys.executable)
