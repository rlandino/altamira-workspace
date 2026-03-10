#!/usr/bin/env python3
"""
Altamira Capital — Market Data API Bridge
==========================================
FastAPI server that proxies FMP (Financial Modeling Prep) for dashboard consumption.
Provides real-time quotes, indices, earnings calendar, and Symbol Detail data.
CORS enabled for local dashboard (3001, 8501).

Usage:
  python -m uvicorn scripts.market_data_api:app --reload --host 0.0.0.0 --port 8001
  # Or: uvicorn scripts.market_data_api:app --host 0.0.0.0 --port 8001

Env:
  FMP_API_KEY — FMP API key (default fallback for local dev only; prefer env in production)

Endpoints:
  GET /api/market/quote?symbol=AAPL         — quote for one or more symbols (comma-separated)
  GET /api/market/indices                   — major indices (^GSPC, ^DJI, ^IXIC)
  GET /api/market/earnings?from=...&to=...  — earnings calendar (optional from/to)
  GET /api/market/health                    — health check
  GET /api/market/status                    — US market open/closed
  GET /api/symbol/{symbol}/profile         — company profile (name, logo, sector, industry, website, marketCap)
  GET /api/symbol/{symbol}/historical      — historical prices (from, to query params)
  GET /api/symbol/{symbol}/next-earnings   — next upcoming earnings date
  GET /api/symbol/{symbol}/key-metrics     — key metrics (annual/quarterly)
  GET /api/symbol/{symbol}/price-target    — analyst price target summary
  GET /api/symbol/{symbol}/analyst-estimates — analyst estimates (revenue, EPS, etc.)
  GET /api/symbol/{symbol}/growth          — earnings growth, sales growth, ROE, institutional (for Growth sections)
"""

import os
import time
from datetime import date, datetime, timezone
from pathlib import Path

import requests
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

WORKSPACE = Path(__file__).resolve().parent.parent
FMP_BASE = "https://financialmodelingprep.com/api/v3"
FMP_STABLE = "https://financialmodelingprep.com/stable"
DEFAULT_KEY = os.environ.get("FMP_API_KEY", "FAAjnYQTvfGg8j7RoPSvHYRVtSKTvJyz")

app = FastAPI(
    title="Altamira Market Data API",
    version="1.0.0",
    description="FMP proxy for real-time quotes, indices, and earnings for Altamira Dashboard",
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


def _fmp_get(path: str, params: dict | None = None) -> tuple[list | dict | None, str]:
    """GET FMP API v3; return (data, error_message)."""
    url = f"{FMP_BASE}{path}"
    params = dict(params or {})
    params["apikey"] = DEFAULT_KEY
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        return data, ""
    except requests.RequestException as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)


def _fmp_stable_get(path: str, params: dict | None = None) -> tuple[list | dict | None, str]:
    """GET FMP stable API; return (data, error_message)."""
    url = f"{FMP_STABLE}{path}"
    params = dict(params or {})
    params["apikey"] = DEFAULT_KEY
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        return data, ""
    except requests.RequestException as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)


@app.get("/api/market/health")
def health():
    """Health check."""
    return {"status": "ok", "service": "market-data-api", "timestamp": time.time()}


@app.get("/api/market/quote")
def quote(symbol: str = Query(..., description="Symbol or comma-separated symbols (e.g. AAPL or AAPL,MSFT,GOOGL)")):
    """Real-time quote(s) from FMP. Single symbol or comma-separated list."""
    symbols = ",".join(s.strip().upper() for s in symbol.split(",") if s.strip())
    if not symbols:
        return {"error": "symbol required"}
    data, err = _fmp_get(f"/quote/{symbols}")
    if err:
        return {"error": err}
    return data if isinstance(data, list) else [data]


@app.get("/api/market/indices")
def indices():
    """Major US indices: S&P 500, Dow Jones, Nasdaq (^GSPC, ^DJI, ^IXIC)."""
    data, err = _fmp_get("/quote/^GSPC,^DJI,^IXIC")
    if err:
        return {"error": err}
    return data if isinstance(data, list) else [data]


@app.get("/api/market/earnings")
def earnings(
    from_date: str | None = Query(None, alias="from", description="From date YYYY-MM-DD"),
    to_date: str | None = Query(None, alias="to", description="To date YYYY-MM-DD"),
):
    """Earnings calendar from FMP. Optional from/to (YYYY-MM-DD)."""
    params = {}
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    data, err = _fmp_get("/earning_calendar", params if params else None)
    if err:
        return {"error": err}
    return data if isinstance(data, list) else []


@app.get("/api/market/status")
def market_status():
    """US market open/closed (9:30–16:00 ET, weekdays)."""
    try:
        import zoneinfo
        et = zoneinfo.ZoneInfo("America/New_York")
    except Exception:
        et = timezone.utc  # fallback
    now = datetime.now(et)
    if now.weekday() >= 5:  # Saturday=5, Sunday=6
        return {"market": "closed", "reason": "weekend"}
    open_h, open_m = 9, 30
    close_h, close_m = 16, 0
    now_minutes = now.hour * 60 + now.minute
    open_minutes = open_h * 60 + open_m
    close_minutes = close_h * 60 + close_m
    if open_minutes <= now_minutes < close_minutes:
        return {"market": "open"}
    return {"market": "closed", "reason": "outside regular session"}


# --- Symbol Detail endpoints ---


@app.get("/api/symbol/{symbol}/profile")
def symbol_profile(symbol: str):
    """Company profile: name, image (logo), sector, industry, website, marketCap."""
    sym = symbol.strip().upper()
    if not sym:
        return {"error": "symbol required"}
    data, err = _fmp_get(f"/profile/{sym}")
    if err:
        return {"error": err}
    if isinstance(data, list) and len(data) > 0:
        row = data[0]
        return {
            "companyName": row.get("companyName") or row.get("name"),
            "image": row.get("image"),
            "sector": row.get("sector"),
            "industry": row.get("industry"),
            "website": row.get("website"),
            "marketCap": row.get("mktCap") or row.get("marketCap"),
            "description": row.get("description"),
        }
    return data if isinstance(data, dict) else {"error": "No profile found"}


@app.get("/api/symbol/{symbol}/historical")
def symbol_historical(
    symbol: str,
    from_date: str | None = Query(None, alias="from", description="From date YYYY-MM-DD"),
    to_date: str | None = Query(None, alias="to", description="To date YYYY-MM-DD"),
):
    """Historical daily prices (and volume) for Quote Panel. Uses FMP historical-price-full."""
    sym = symbol.strip().upper()
    if not sym:
        return {"error": "symbol required"}
    params = {}
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    data, err = _fmp_get(f"/historical-price-full/{sym}", params if params else None)
    if err:
        return {"error": err}
    if isinstance(data, dict) and "historical" in data:
        return {"symbol": data.get("symbol"), "historical": data["historical"]}
    return data or {"historical": []}


@app.get("/api/symbol/{symbol}/next-earnings")
def symbol_next_earnings(symbol: str):
    """Next upcoming earnings date for the symbol."""
    sym = symbol.strip().upper()
    if not sym:
        return {"error": "symbol required"}
    data, err = _fmp_get(f"/historical/earning_calendar/{sym}")
    if err:
        return {"error": err}
    if not isinstance(data, list):
        return {"nextEarningsDate": None}
    today = date.isoformat(date.today())
    for row in sorted(data, key=lambda r: (r.get("date") or "")):
        d = row.get("date")
        if d and d >= today:
            return {"nextEarningsDate": d, "symbol": sym}
    return {"nextEarningsDate": None, "symbol": sym}


@app.get("/api/symbol/{symbol}/key-metrics")
def symbol_key_metrics(
    symbol: str,
    period: str = Query("annual", description="annual or quarter"),
    limit: int = Query(5, ge=1, le=20),
):
    """Key metrics for Key Metrics cards (valuation, profitability, per-share)."""
    sym = symbol.strip().upper()
    if not sym:
        return {"error": "symbol required"}
    data, err = _fmp_get(f"/key-metrics/{sym}", {"period": period, "limit": limit})
    if err:
        return {"error": err}
    return data if isinstance(data, list) else []


@app.get("/api/symbol/{symbol}/price-target")
def symbol_price_target(symbol: str):
    """Analyst price target summary (FMP stable)."""
    sym = symbol.strip().upper()
    if not sym:
        return {"error": "symbol required"}
    data, err = _fmp_stable_get("/price-target-summary", {"symbol": sym})
    if err:
        return {"error": err}
    if isinstance(data, list) and len(data) > 0:
        return data[0]
    return data if isinstance(data, dict) else {}


@app.get("/api/symbol/{symbol}/analyst-estimates")
def symbol_analyst_estimates(
    symbol: str,
    limit: int = Query(8, ge=1, le=20),
):
    """Analyst estimates (revenue, EPS) for Forecast panel."""
    sym = symbol.strip().upper()
    if not sym:
        return {"error": "symbol required"}
    data, err = _fmp_get(f"/analyst-estimates/{sym}", {"limit": limit})
    if err:
        return {"error": err}
    return data if isinstance(data, list) else []


def _quarter_label(date_str: str) -> str:
    """Q1.24 from YYYY-MM-DD."""
    if not date_str or len(date_str) < 10:
        return ""
    try:
        y = int(date_str[:4]) % 100
        m = int(date_str[5:7])
        q = (m - 1) // 3 + 1
        return f"Q{q}.{y}"
    except (ValueError, IndexError):
        return ""


@app.get("/api/symbol/{symbol}/growth")
def symbol_growth(symbol: str):
    """Growth data for Symbol Detail: earnings growth, sales growth, ROE, institutional ownership."""
    sym = symbol.strip().upper()
    if not sym:
        return {"error": "symbol required"}

    # FMP stable earnings (revenue, EPS actual/estimated)
    earnings, err = _fmp_stable_get("/earnings", {"symbol": sym})
    if err or not isinstance(earnings, list):
        earnings = []

    # Key metrics for ROE
    metrics, _ = _fmp_get(f"/key-metrics/{sym}", {"period": "quarter", "limit": 12})
    roe_series = []
    if isinstance(metrics, list):
        for m in sorted(metrics, key=lambda x: (x.get("date") or "")):
            d = m.get("date")
            roe = m.get("roe")
            if d and roe is not None:
                try:
                    roe_series.append({"date": d, "label": _quarter_label(d), "roe": float(roe)})
                except (TypeError, ValueError):
                    pass

    # Institutional holders (reported date, shares, weight)
    inst, _ = _fmp_get(f"/institutional-holder/{sym}")
    inst_series = []
    if isinstance(inst, list):
        for h in inst[:20]:
            inst_series.append({
                "holder": h.get("holder"),
                "shares": h.get("shares"),
                "dateReported": h.get("dateReported"),
                "weight": h.get("weight"),
            })

    # Build earnings growth and sales growth from stable earnings
    by_period = {}
    for row in earnings:
        d = row.get("date")
        if not d:
            continue
        label = _quarter_label(d)
        rev_act = row.get("revenueActual")
        rev_est = row.get("revenueEstimated")
        eps_act = row.get("epsActual")
        eps_est = row.get("epsEstimated")
        try:
            rev = float(rev_act) if rev_act is not None else (float(rev_est) if rev_est is not None else None)
            eps = float(eps_act) if eps_act is not None else (float(eps_est) if eps_est is not None else None)
            by_period[d] = {"label": label, "revenue": rev, "eps": eps, "revenueEstimated": float(rev_est) if rev_est is not None else None, "epsEstimated": float(eps_est) if eps_est is not None else None}
        except (TypeError, ValueError):
            pass

    sorted_dates = sorted(by_period.keys())
    earnings_growth = []
    sales_growth = []
    prev_eps = prev_rev = None
    for d in sorted_dates:
        p = by_period[d]
        label = p["label"]
        eps = p["eps"]
        rev = p["revenue"]
        eps_growth_pct = None
        if prev_eps is not None and eps is not None and prev_eps != 0:
            eps_growth_pct = ((eps - prev_eps) / abs(prev_eps)) * 100
        rev_growth_pct = None
        if prev_rev is not None and rev is not None and prev_rev != 0:
            rev_growth_pct = ((rev - prev_rev) / abs(prev_rev)) * 100
        earnings_growth.append({"date": d, "label": label, "eps": eps, "epsGrowthPct": eps_growth_pct, "vs": prev_eps})
        sales_growth.append({"date": d, "label": label, "revenue": rev, "revenueGrowthPct": rev_growth_pct, "vs": prev_rev})
        if eps is not None:
            prev_eps = eps
        if rev is not None:
            prev_rev = rev

    return {
        "earningsGrowth": earnings_growth[-16:],
        "salesGrowth": sales_growth[-16:],
        "returnOnEquity": roe_series[-16:],
        "institutionalOwnership": inst_series,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
