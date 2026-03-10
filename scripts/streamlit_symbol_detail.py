"""
Streamlit fragment: Symbol Detail page for the Altamira Dashboard.

Renders full Symbol Detail UI for a given ticker: header (company, logo, market cap,
industry, next earnings, real-time price, market status), Quote Panel with 1W/1M/3M/1Y
chart + volume, Fundamentals, Relative Strength, Forecast, Key Metrics (3 cards),
and Growth sections (Earnings Growth, Sales Growth, ROE, Institutional) with tables
and a shared "Show Graph" chart.

Data: fetched from Market Data API (default http://localhost:8001). Set
MARKET_DATA_API_URL if the API runs elsewhere.

Integration: Use as a fragment by calling render_symbol_detail(symbol). The Symbol
Detail page (e.g. pages/2_Symbol_Detail.py) should read st.query_params.get("ticker")
and call render_symbol_detail(ticker). Other pages make tickers clickable via
st.page_link to the Symbol Detail page with query_params={"ticker": symbol}.
"""

import os
from datetime import date, timedelta

import requests
import streamlit as st

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except ImportError:
    go = None
    make_subplots = None

# API base URL for Market Data API
API_BASE = os.environ.get("MARKET_DATA_API_URL", "http://localhost:8001").rstrip("/")


def _get(path: str):
    """GET from Market Data API; return parsed JSON or None."""
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


@st.cache_data(ttl=300)
def _cached_profile(symbol: str):
    return _get(f"/api/symbol/{symbol}/profile")


@st.cache_data(ttl=60)
def _cached_quote(symbol: str):
    data = _get(f"/api/market/quote?symbol={symbol}")
    if isinstance(data, list) and len(data) > 0:
        return data[0]
    return data if isinstance(data, dict) else None


@st.cache_data(ttl=300)
def _cached_next_earnings(symbol: str):
    return _get(f"/api/symbol/{symbol}/next-earnings")


@st.cache_data(ttl=300)
def _cached_key_metrics(symbol: str):
    data = _get(f"/api/symbol/{symbol}/key-metrics?period=annual&limit=5")
    return data if isinstance(data, list) else []


@st.cache_data(ttl=300)
def _cached_growth(symbol: str):
    return _get(f"/api/symbol/{symbol}/growth")


@st.cache_data(ttl=300)
def _cached_price_target(symbol: str):
    return _get(f"/api/symbol/{symbol}/price-target")


@st.cache_data(ttl=300)
def _cached_analyst_estimates(symbol: str):
    data = _get(f"/api/symbol/{symbol}/analyst-estimates?limit=8")
    return data if isinstance(data, list) else []


@st.cache_data(ttl=120)
def _cached_historical(symbol: str, from_d: str, to_d: str):
    """Historical prices for Quote Panel (2 min cache)."""
    return _get(f"/api/symbol/{symbol}/historical?from={from_d}&to={to_d}")


@st.cache_data(ttl=30)
def _cached_market_status():
    return _get("/api/market/status") or {"market": "unknown"}


def _format_cap(mcap):
    if mcap is None:
        return "—"
    try:
        x = float(mcap)
        if x >= 1e12:
            return f"{x / 1e12:.2f}T"
        if x >= 1e9:
            return f"{x / 1e9:.1f}B"
        if x >= 1e6:
            return f"{x / 1e6:.1f}M"
        return f"{x:,.0f}"
    except (TypeError, ValueError):
        return str(mcap)


def _render_header(symbol: str):
    profile = _cached_profile(symbol)
    quote = _cached_quote(symbol)
    next_earn = _cached_next_earnings(symbol)
    status = _cached_market_status()

    col_logo, col_info, col_price = st.columns([1, 3, 2])
    with col_logo:
        if profile and profile.get("image"):
            st.image(profile["image"], width=64)
        else:
            st.write("")
    with col_info:
        name = (profile or {}).get("companyName") or (quote or {}).get("name") or symbol
        st.markdown(f"**{name}**")
        st.caption(f"{symbol}")
        cap = (profile or {}).get("marketCap") or (quote or {}).get("marketCap")
        industry = (profile or {}).get("industry") or "—"
        next_d = (next_earn or {}).get("nextEarningsDate") or "—"
        st.write(f"Market Cap {_format_cap(cap)}  ·  {industry}  ·  Next earnings {next_d}")
    with col_price:
        if quote:
            price = quote.get("price")
            chg = quote.get("changesPercentage") or quote.get("change")
            chg_pct = quote.get("changesPercentage")
            if price is not None:
                st.metric("Price", f"${float(price):,.2f} USD", f"{chg_pct:+.2f}%" if chg_pct is not None else None)
        else:
            st.write("Price —")
        market = (status or {}).get("market", "unknown")
        if market == "open":
            st.success("Market Open")
        else:
            st.info("Market Closed")


def _render_quote_panel(symbol: str):
    st.subheader("Quote Panel")
    st.caption(f"Updated {date.today().strftime('%B %d, %Y')}")

    today = date.today()
    periods = [
        ("1W", today - timedelta(days=7), "1W"),
        ("1M", today - timedelta(days=30), "1M"),
        ("3M", today - timedelta(days=90), "3M"),
        ("1Y", today - timedelta(days=365), "1Y"),
    ]
    labels_with_key = [p[2] for p in periods]
    tf = st.radio("Period", labels_with_key, horizontal=True, key="quote_tf_radio")
    from_d = next(p[1] for p in periods if p[2] == tf)
    to_s = today.isoformat()
    from_s = from_d.isoformat()
    data = _cached_historical(symbol, from_s, to_s)
    hist = (data or {}).get("historical") or []
    if not hist:
        st.warning("No historical data for the selected period.")
        return

    # Sort by date ascending for chart
    hist = sorted(hist, key=lambda x: x.get("date") or "")
    dates = [h.get("date") for h in hist if h.get("date")]
    closes = [float(h.get("close", 0)) for h in hist]
    volumes = [int(h.get("volume") or 0) for h in hist]

    period_pct = None
    if len(closes) >= 2 and closes[0] != 0:
        period_pct = (closes[-1] - closes[0]) / closes[0] * 100
    if period_pct is not None:
        st.caption(f"{tf} period change: {period_pct:+.2f}%")

    if not go or not make_subplots:
        st.write("Install plotly for charts: pip install plotly")
        return

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
    fig.add_trace(go.Scatter(x=dates, y=closes, name="Price", line=dict(color="rgb(31, 119, 180)", width=2)), row=1, col=1)
    fig.add_trace(go.Bar(x=dates, y=volumes, name="Volume", marker_color="rgba(31, 119, 180, 0.4)"), row=2, col=1)
    fig.update_layout(height=400, showlegend=False, margin=dict(t=20, b=20))
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    st.plotly_chart(fig, use_container_width=True)


def _render_key_metrics(symbol: str):
    st.subheader("Key Metrics")
    profile = _cached_profile(symbol)
    quote = _cached_quote(symbol)
    metrics = _cached_key_metrics(symbol)
    next_earn = _cached_next_earnings(symbol)
    pt = _cached_price_target(symbol)

    if "key_metric_card" not in st.session_state:
        st.session_state["key_metric_card"] = 0
    card = st.session_state["key_metric_card"]

    # Card 0: range, industry, website, sector
    # Card 1: market cap, shares outstanding, float, dividend
    # Card 2: earning date, price target, avg volume, beta
    latest_quote = quote or {}
    latest_metrics = (metrics or [{}])[0] if metrics else {}
    profile = profile or {}

    cards = [
        {
            "Range": f"{latest_quote.get('yearLow', '—')} - {latest_quote.get('yearHigh', '—')}" if latest_quote.get("yearLow") is not None else "—",
            "Industry": profile.get("industry") or "—",
            "Website": profile.get("website") or "—",
            "Sector": profile.get("sector") or "—",
        },
        {
            "Market Cap": _format_cap(profile.get("marketCap") or latest_quote.get("marketCap")),
            "Shares Outstanding": latest_metrics.get("numberOfShares") or "—",
            "Share in Float": latest_metrics.get("sharesOutstanding") or "—",
            "Dividend": latest_quote.get("dividend") or latest_metrics.get("dividendYield") or "—",
        },
        {
            "Earning Date": (next_earn or {}).get("nextEarningsDate") or "—",
            "Price Target": pt.get("adjPriceTarget") or pt.get("priceWhenPosted") or "—",
            "Average Volume": _format_cap(latest_quote.get("avgVolume")) if latest_quote.get("avgVolume") else "—",
            "Beta": latest_metrics.get("beta") or latest_quote.get("beta") or "—",
        },
    ]
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("◀ Prev", key="km_prev"):
            st.session_state["key_metric_card"] = (card - 1) % 3
            st.rerun()
    with col2:
        st.write(f"Card {card + 1} of 3")
    with col3:
        if st.button("Next ▶", key="km_next"):
            st.session_state["key_metric_card"] = (card + 1) % 3
            st.rerun()

    for k, v in cards[card].items():
        st.write(f"**{k}:** {v}")

    dots = " ".join("●" if i == card else "○" for i in range(3))
    st.caption(dots)


def _render_growth_sections(symbol: str):
    data = _cached_growth(symbol)
    if not data:
        st.warning("No growth data available.")
        return

    if "growth_chart" not in st.session_state:
        st.session_state["growth_chart"] = None

    left, right = st.columns([1, 1])

    with left:
        # Earnings Growth
        eg = data.get("earningsGrowth") or []
        st.markdown("**Earnings Growth**")
        if eg:
            rows = [{"Quarter": r.get("label"), "EPS": r.get("eps"), "Growth %": r.get("epsGrowthPct")} for r in eg]
            st.dataframe(rows, use_container_width=True, hide_index=True)
        if st.button("Show Graph", key="g_earnings"):
            st.session_state["growth_chart"] = "earnings"
            st.rerun()

        st.markdown("**Sales Growth**")
        sg = data.get("salesGrowth") or []
        if sg:
            rows = [{"Quarter": r.get("label"), "Revenue": r.get("revenue"), "Growth %": r.get("revenueGrowthPct")} for r in sg]
            st.dataframe(rows, use_container_width=True, hide_index=True)
        if st.button("Show Graph", key="g_sales"):
            st.session_state["growth_chart"] = "sales"
            st.rerun()

        st.markdown("**Return on Equity**")
        roe = data.get("returnOnEquity") or []
        if roe:
            rows = [{"Quarter": r.get("label"), "ROE %": r.get("roe")} for r in roe]
            st.dataframe(rows, use_container_width=True, hide_index=True)
        if st.button("Show Graph", key="g_roe"):
            st.session_state["growth_chart"] = "roe"
            st.rerun()

        st.markdown("**Institutional Ownership**")
        inst = data.get("institutionalOwnership") or []
        if inst:
            rows = [{"Holder": r.get("holder"), "Shares": r.get("shares"), "Weight %": r.get("weight")} for r in inst[:10]]
            st.dataframe(rows, use_container_width=True, hide_index=True)
        if st.button("Show Graph", key="g_inst"):
            st.session_state["growth_chart"] = "institutional"
            st.rerun()

    with right:
        chart_type = st.session_state.get("growth_chart")
        if not go:
            st.caption("Install plotly for growth charts.")
            return
        if chart_type == "earnings" and eg:
            fig = go.Figure()
            labels = [r.get("label") for r in eg]
            vals = [r.get("epsGrowthPct") if r.get("epsGrowthPct") is not None else None for r in eg]
            fig.add_trace(go.Scatter(x=labels, y=vals, mode="lines+markers", name="EPS Growth %"))
            fig.update_layout(title="Earnings Growth", height=350, yaxis_title="Growth %")
            st.plotly_chart(fig, use_container_width=True)
        elif chart_type == "sales" and sg:
            fig = go.Figure()
            labels = [r.get("label") for r in sg]
            vals = [r.get("revenueGrowthPct") if r.get("revenueGrowthPct") is not None else None for r in sg]
            fig.add_trace(go.Scatter(x=labels, y=vals, mode="lines+markers", name="Sales Growth %"))
            fig.update_layout(title="Sales Growth", height=350, yaxis_title="Growth %")
            st.plotly_chart(fig, use_container_width=True)
        elif chart_type == "roe" and roe:
            fig = go.Figure()
            labels = [r.get("label") for r in roe]
            vals = [r.get("roe") for r in roe]
            fig.add_trace(go.Scatter(x=labels, y=vals, mode="lines+markers", name="ROE %"))
            fig.update_layout(title="Return on Equity", height=350, yaxis_title="ROE %")
            st.plotly_chart(fig, use_container_width=True)
        elif chart_type == "institutional" and inst:
            fig = go.Figure()
            holders = [r.get("holder") or "" for r in inst[:10]]
            weights = [float(r.get("weight") or 0) for r in inst[:10]]
            fig.add_trace(go.Bar(x=holders, y=weights))
            fig.update_layout(title="Institutional Ownership", height=350, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Click 'Show Graph' on a growth section to display the chart here.")


def _render_fundamentals(symbol: str):
    st.subheader("Fundamentals")
    metrics = _cached_key_metrics(symbol)
    quote = _cached_quote(symbol)
    m = (metrics or [{}])[0] if metrics else {}
    q = quote or {}
    st.write(f"P/E: {m.get('peRatio') or q.get('pe') or '—'}x")
    st.write(f"P/B: {m.get('priceToBookRatio') or '—'}x")
    st.write(f"P/S: {m.get('priceToSalesRatio') or '—'}x")
    st.write(f"D/E: {m.get('debtToEquity') or '—'}")
    st.write(f"Net Margin: {m.get('netProfitMargin') or '—'}")
    st.write(f"EPS: ${m.get('netIncomePerShare') or q.get('eps') or '—'}")


def _render_forecast(symbol: str):
    st.subheader("Forecast")
    pt = _cached_price_target(symbol)
    est = _cached_analyst_estimates(symbol)
    if pt:
        st.write(f"Price Target: {pt.get('adjPriceTarget') or pt.get('priceWhenPosted') or '—'}")
        st.write(f"Analysts: {pt.get('numberOfAnalysts') or '—'}")
    if est:
        latest = est[0] if est else {}
        st.write(f"Revenue Est: {latest.get('estimatedRevenueAvg') or '—'}")
        st.write(f"EPS Est: {latest.get('estimatedEpsAvg') or '—'}")


def _render_relative_strength(symbol: str):
    st.subheader("Relative Strength")
    st.caption("Symbol price performance (sector/industry comparison can be added later).")
    # Reuse historical for 90d
    today = date.today()
    from_d = (today - timedelta(days=90)).isoformat()
    to_d = today.isoformat()
    data = _cached_historical(symbol, from_d, to_d)
    hist = (data or {}).get("historical") or []
    if not hist or not go:
        st.write("No data.")
        return
    hist = sorted(hist, key=lambda x: x.get("date") or "")
    dates = [h.get("date") for h in hist]
    closes = [float(h.get("close", 0)) for h in hist]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=closes, mode="lines", name=symbol))
    fig.update_layout(height=250, margin=dict(t=20, b=20), yaxis_title="Price")
    st.plotly_chart(fig, use_container_width=True)


def render_symbol_detail(symbol: str):
    """Render the full Symbol Detail UI for the given ticker. Call from the Symbol Detail page."""
    if not symbol or not str(symbol).strip():
        st.warning("No symbol provided. Use query param ?ticker=SYMBOL or select a ticker.")
        return
    sym = str(symbol).strip().upper()

    _render_header(sym)

    st.divider()
    _render_quote_panel(sym)

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        _render_fundamentals(sym)
    with c2:
        _render_relative_strength(sym)
    with c3:
        _render_forecast(sym)

    st.divider()
    _render_key_metrics(sym)

    st.divider()
    st.subheader("Growth")
    _render_growth_sections(sym)


if __name__ == "__main__":
    st.set_page_config(page_title="Symbol Detail", layout="wide")
    ticker = st.query_params.get("ticker") or st.text_input("Ticker", value="WM", key="sym_input")
    if ticker:
        render_symbol_detail(ticker)
    else:
        st.info("Enter a ticker or open this page with ?ticker=SYMBOL")
