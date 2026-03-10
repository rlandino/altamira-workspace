"""
Streamlit dashboard for regime-based trading app.
Sidebar: ticker, period, strategy/backtest params, theme. Export CSV/JSON, HMM warning, regime stability.
"""

import json
from datetime import datetime, timezone
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

try:
    from .data_loader import load_ohlcv, TICKER_OPTIONS, PERIOD_OPTIONS
    from .hmm_engine import fit_hmm, identify_bull_bear_states, get_regime_labels, FEATURE_RETURNS
    from .strategy import prepare_strategy_df, can_enter, should_exit, votes_for_entry, get_condition_breakdown, DEFAULT_CONFIG
    from .backtester import run_backtest
except ImportError:
    from regime_trading.data_loader import load_ohlcv, TICKER_OPTIONS, PERIOD_OPTIONS
    from regime_trading.hmm_engine import fit_hmm, identify_bull_bear_states, get_regime_labels, FEATURE_RETURNS
    from regime_trading.strategy import prepare_strategy_df, can_enter, should_exit, votes_for_entry, get_condition_breakdown, DEFAULT_CONFIG
    from regime_trading.backtester import run_backtest


@st.cache_data(ttl=3600)
def get_cached_signal_and_regime(ticker: str, period: str, interval: str, _strat_key: tuple, _bt_key: tuple):
    """Cache keyed by (ticker, period, interval, strategy_config, backtest_config). _strat_key/_bt_key are tuple(sorted(config.items()))."""
    strategy_config = dict(_strat_key) if _strat_key else {}
    backtest_config = dict(_bt_key) if _bt_key else {}
    strat = {**DEFAULT_CONFIG, **strategy_config}
    votes_req = strat["votes_required"]

    raw = load_ohlcv(ticker, period, interval)
    model, df_regime, hmm_converged = fit_hmm(raw)
    bull_state, bear_state = identify_bull_bear_states(df_regime)
    labels = get_regime_labels(bull_state, bear_state)
    df_regime = df_regime.copy()
    df_regime[FEATURE_RETURNS] = df_regime["close"].pct_change()
    strategy_df = prepare_strategy_df(df_regime, returns_col=FEATURE_RETURNS)
    strategy_df = strategy_df.dropna(subset=["Votes", "ADX", "EMA50", "EMA200", "MACD", "MACD_Signal"])

    last = strategy_df.iloc[-1]
    current_regime = int(last["Regime"])
    detected_regime = labels.get(current_regime, "Neutral")
    if current_regime == bull_state and votes_for_entry(last, strat) >= votes_req:
        current_signal = "LONG"
    elif current_regime == bear_state:
        current_signal = "EXIT / FLAT"
    else:
        current_signal = "FLAT"

    trades_df, equity_df, metrics = run_backtest(ticker=ticker, period=period, interval=interval, strategy_config=strat, backtest_config=backtest_config)
    regime_switches_last_500 = int((strategy_df["Regime"].tail(500).diff().fillna(0) != 0).sum())
    bars_per_week = 24 * 5
    regime_switches_per_week = regime_switches_last_500 / (500 / bars_per_week) if bars_per_week else 0

    return {
        "strategy_df": strategy_df,
        "bull_state": bull_state,
        "bear_state": bear_state,
        "regime_labels": labels,
        "current_signal": current_signal,
        "detected_regime": detected_regime,
        "metrics": metrics,
        "trades_df": trades_df,
        "equity_df": equity_df,
        "hmm_model": model,
        "hmm_converged": hmm_converged,
        "cache_built_at": datetime.now(timezone.utc).isoformat(),
        "regime_switches_per_week": regime_switches_per_week,
        "ticker": ticker,
        "strategy_config": strat,
    }


def build_candlestick_with_regime(
    df: pd.DataFrame,
    bull_state: int,
    bear_state: int,
    regime_labels: dict,
    last_n: int = 500,
    template: str = "plotly_white",
) -> go.Figure:
    """Plotly candlestick with background color by regime (green=bull, red=bear)."""
    plot_df = df.tail(last_n).copy()
    plot_df = plot_df.reset_index()
    time_col = plot_df.columns[0]
    x = plot_df[time_col].astype(str).tolist()
    open_ = plot_df["open"].values
    high = plot_df["high"].values
    low = plot_df["low"].values
    close = plot_df["close"].values
    regimes = plot_df["Regime"].values

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=x,
                open=open_,
                high=high,
                low=low,
                close=close,
                name="SPY",
                increasing_line_color="#26a69a",
                decreasing_line_color="#ef5350",
            )
        ]
    )

    n = len(x)
    for i in range(n):
        regime = int(regimes[i])
        color = "rgba(0,200,0,0.15)" if regime == bull_state else "rgba(200,0,0,0.15)" if regime == bear_state else "rgba(128,128,128,0.08)"
        fig.add_vrect(
            x0=i - 0.5,
            x1=i + 0.5,
            fillcolor=color,
            line_width=0,
            layer="below",
        )

    fig.update_layout(
        title="Hourly — Regime Background (Green=Bull, Red=Bear)",
        xaxis_title="Time",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        template=template,
        height=500,
    )
    return fig


def main():
    st.set_page_config(page_title="Regime Trading", layout="wide")

    with st.sidebar:
        st.subheader("Data")
        ticker = st.selectbox("Ticker", options=TICKER_OPTIONS, index=0)
        period = st.selectbox("Period", options=list(PERIOD_OPTIONS.keys()), index=3, format_func=lambda x: PERIOD_OPTIONS.get(x, x))
        interval = st.radio("Interval", ["1h", "1d"], index=0, horizontal=True)
        st.subheader("Strategy")
        rsi_max = st.number_input("RSI max", min_value=50, max_value=100, value=int(DEFAULT_CONFIG["rsi_max"]), step=1)
        momentum_min = st.number_input("Momentum min %", min_value=0.0, max_value=10.0, value=DEFAULT_CONFIG["momentum_min_pct"] * 100, step=0.5) / 100
        volatility_max = st.number_input("Volatility max %", min_value=1.0, max_value=20.0, value=DEFAULT_CONFIG["volatility_max_pct"] * 100, step=0.5) / 100
        adx_min = st.number_input("ADX min", min_value=10, max_value=50, value=int(DEFAULT_CONFIG["adx_min"]), step=1)
        votes_required = st.slider("Votes required (of 8)", min_value=5, max_value=8, value=DEFAULT_CONFIG["votes_required"])
        cooldown_hours = st.number_input("Cooldown (hours)", min_value=0, max_value=168, value=int(DEFAULT_CONFIG["cooldown_hours"]), step=1)
        st.subheader("Backtest")
        starting_capital = st.number_input("Starting capital $", min_value=1000, max_value=1_000_000, value=10_000, step=1000)
        cost_bps = st.number_input("Transaction cost (bps)", min_value=0.0, max_value=50.0, value=0.0, step=1.0)
        slippage_bps = st.number_input("Slippage (bps)", min_value=0.0, max_value=20.0, value=0.0, step=0.5)
        st.subheader("Display")
        theme = st.radio("Chart theme", ["Light", "Dark"], index=0, horizontal=True)
    template = "plotly_dark" if theme == "Dark" else "plotly_white"

    strategy_config = {"rsi_max": rsi_max, "momentum_min_pct": momentum_min, "volatility_max_pct": volatility_max, "adx_min": adx_min, "votes_required": votes_required, "cooldown_hours": cooldown_hours}
    backtest_config = {"starting_capital": starting_capital, "transaction_cost_bps": cost_bps, "slippage_bps": slippage_bps}
    _strat_key = tuple(sorted(strategy_config.items()))
    _bt_key = tuple(sorted(backtest_config.items()))

    st.title("Regime-Based Trading Dashboard")

    try:
        data = get_cached_signal_and_regime(ticker, period, interval, _strat_key, _bt_key)
    except Exception as e:
        st.error(f"Failed to load data: {type(e).__name__}: {e}")
        if st.button("Retry"):
            st.cache_data.clear()
            st.rerun()
        return

    strategy_df = data["strategy_df"]
    bull_state = data["bull_state"]
    bear_state = data["bear_state"]
    regime_labels = data["regime_labels"]
    current_signal = data["current_signal"]
    detected_regime = data["detected_regime"]
    metrics = data["metrics"]
    trades_df = data["trades_df"]
    equity_df = data["equity_df"]
    hmm_model = data.get("hmm_model")
    hmm_converged = data.get("hmm_converged", True)
    cache_built_at = data.get("cache_built_at", "")
    regime_switches_per_week = data.get("regime_switches_per_week", 0)
    ticker_display = data.get("ticker", "SPY")
    strat_cfg = data.get("strategy_config") or strategy_config

    if not hmm_converged:
        st.warning("HMM did not fully converge; regime labels may be less stable. Consider re-running or using a different period.")

    # Data freshness + Refresh + Export
    last_ts = strategy_df.index[-1] if hasattr(strategy_df.index[-1], "strftime") else str(strategy_df.index[-1])
    data_through = last_ts.strftime("%Y-%m-%d %H:%M") if hasattr(last_ts, "strftime") else str(last_ts)
    r1, r2 = st.columns([3, 1])
    with r1:
        st.caption(f"Data through: **{data_through}** ({ticker_display} {interval}) · Cache built: **{cache_built_at[:19] if cache_built_at else '—'}** UTC · Regime switches/week (last 500 bars): **{regime_switches_per_week:.1f}**")
    with r2:
        if st.button("Refresh data", help="Clear cache and reload"):
            get_cached_signal_and_regime.clear()
            st.rerun()

    # Last signal change (scan backwards)
    last_signal_change = "—"
    for i in range(len(strategy_df) - 2, max(0, len(strategy_df) - 200) - 1, -1):
        row = strategy_df.iloc[i]
        r = int(row["Regime"])
        v = votes_for_entry(row, strat_cfg)
        sig = "LONG" if (r == bull_state and v >= strat_cfg["votes_required"]) else ("EXIT / FLAT" if r == bear_state else "FLAT")
        if sig != current_signal:
            ts = strategy_df.index[i]
            last_signal_change = f"{sig} → {current_signal} at {ts}" if hasattr(ts, "strftime") else f"{sig} → {current_signal}"
            break
    st.caption(f"**Last signal change:** {last_signal_change}")

    # Top section: current signal + detected regime
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Signal", current_signal)
    with col2:
        st.metric("Detected Regime", detected_regime)
    with col3:
        votes = votes_for_entry(strategy_df.iloc[-1], strat_cfg)
        st.metric("Confirmations (8)", f"{votes}/8")

    # Cooldown / position state
    pos_state = metrics.get("position_state", "—")
    cooldown_bars = metrics.get("cooldown_remaining_bars", 0)
    st.caption(f"**Simulation state:** {pos_state} · Cooldown remaining: **{cooldown_bars}** bars (48h after exit)")

    # Condition breakdown (under the hood: why LONG / FLAT)
    with st.expander("Condition breakdown (current bar — why signal is LONG / FLAT)", expanded=True):
        row = strategy_df.iloc[-1]
        breakdown = get_condition_breakdown(row, strat_cfg)
        disp = []
        for b in breakdown:
            v = b["value"]
            if isinstance(v, float):
                v_str = f"{v:.2f}" if abs(v) < 1e3 else f"{v:.4f}"
            elif isinstance(v, bool):
                v_str = "Yes" if v else "No"
            else:
                v_str = str(v) if v is not None else "—"
            disp.append({
                "Condition": b["name"],
                "Value": v_str,
                "Threshold": b["threshold"],
                "Pass": "Yes" if b["passed"] else "No",
            })
        st.dataframe(pd.DataFrame(disp), use_container_width=True, hide_index=True)

    # Regime summary table (all 7 states)
    with st.expander("Regime summary (all 7 HMM states)", expanded=True):
        g = strategy_df.groupby("Regime")[FEATURE_RETURNS].agg(Mean_Return="mean", Volatility="std", Count="count")
        g = g.reset_index()
        g["Label"] = g["Regime"].map(regime_labels)
        g = g.sort_values("Mean_Return", ascending=False)
        g["Mean_Return"] = g["Mean_Return"].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "—")
        g["Volatility"] = g["Volatility"].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "—")
        st.dataframe(g[["Regime", "Label", "Mean_Return", "Volatility", "Count"]], use_container_width=True, hide_index=True)

    # Regime over time (last 500 bars)
    with st.expander("Regime over time (last 500 hours)", expanded=False):
        plot_regime = strategy_df.tail(500).copy()
        plot_regime = plot_regime.reset_index()
        time_col = plot_regime.columns[0]
        fig_reg = go.Figure()
        fig_reg.add_trace(go.Scatter(
            x=plot_regime[time_col],
            y=plot_regime["Regime"],
            mode="lines",
            line=dict(color="#7f7f7f", width=1),
            fill="tozeroy",
            name="Regime (0–6)",
        ))
        fig_reg.update_layout(
            height=220,
            xaxis_title="Time",
            yaxis_title="Regime",
            yaxis=dict(tickmode="linear", dtick=1, range=[-0.5, 6.5]),
            template=template,
            margin=dict(t=20, b=40),
        )
        st.plotly_chart(fig_reg, use_container_width=True)
        st.caption("Bull = highest mean return state; Bear/Crash = lowest. See regime summary table for state IDs.")

    # Equity curve vs Buy & Hold
    cap = backtest_config.get("starting_capital", 10000)
    st.subheader(f"Equity curve vs Buy & Hold (${cap:,} start)")
    first_close = float(strategy_df["close"].iloc[0])
    bh_equity = cap * (strategy_df["close"] / first_close)
    bh_aligned = bh_equity.reindex(equity_df.index).ffill().bfill()
    fig_eq = go.Figure()
    fig_eq.add_trace(go.Scatter(x=equity_df.index, y=equity_df["equity"], name="Strategy", line=dict(color="#1f77b4")))
    fig_eq.add_trace(go.Scatter(x=equity_df.index, y=bh_aligned, name="Buy & Hold", line=dict(color="#ff7f0e", dash="dash")))
    fig_eq.update_layout(height=350, xaxis_title="Time", yaxis_title="Equity ($)", template=template, legend=dict(orientation="h"))
    st.plotly_chart(fig_eq, use_container_width=True)

    # Drawdown over time
    st.subheader("Drawdown over time")
    eq_series = equity_df["equity"]
    rolling_max = eq_series.expanding().max()
    drawdown_pct = (eq_series - rolling_max) / rolling_max.replace(0, np.nan)
    fig_dd = go.Figure()
    fig_dd.add_trace(go.Scatter(x=equity_df.index, y=drawdown_pct * 100, fill="tozeroy", line=dict(color="#e74c3c"), name="Drawdown %"))
    fig_dd.update_layout(height=280, xaxis_title="Time", yaxis_title="Drawdown (%)", template=template)
    st.plotly_chart(fig_dd, use_container_width=True)

    # HMM transition matrix
    if hmm_model is not None and hasattr(hmm_model, "transmat_"):
        with st.expander("HMM transition matrix (P(next state | current state))", expanded=False):
            trans = hmm_model.transmat_
            n_st = trans.shape[0]
            fig_tm = go.Figure(data=go.Heatmap(
                z=trans,
                x=[f"S{j}" for j in range(n_st)],
                y=[f"S{i}" for i in range(n_st)],
                colorscale="Blues",
                text=[[f"{trans[i, j]:.2f}" for j in range(n_st)] for i in range(n_st)],
                texttemplate="%{text}",
                textfont={"size": 10},
            ))
            fig_tm.update_layout(title="From (row) → To (col)", height=360, xaxis_title="To state", yaxis_title="From state", template=template)
            st.plotly_chart(fig_tm, use_container_width=True)
            st.caption("Bull and Bear state IDs from Regime summary table.")

    # Metrics row
    st.subheader("Backtest Metrics ($10k starting capital)")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Return", f"{metrics['total_return']:.2%}")
    m2.metric("Alpha vs Buy & Hold", f"{metrics['alpha_vs_bh']:+.2%}")
    m3.metric("Win Rate", f"{metrics['win_rate']:.1%}")
    m4.metric("Max Drawdown", f"{metrics['max_drawdown']:.2%}")
    m5.metric("Trades", metrics["num_trades"])

    # Chart: candlestick with regime background
    st.subheader("SPY Hourly — Candlestick by Regime")
    fig = build_candlestick_with_regime(strategy_df, bull_state, bear_state, regime_labels, last_n=500)
    st.plotly_chart(fig, use_container_width=True)

    # Trade log (with regime at entry/exit, hold_hours)
    if not trades_df.empty:
        st.subheader("Trade Log")
        display_df = trades_df.copy()
        display_df["pnl_pct"] = display_df["pnl_pct"].apply(lambda x: f"{x:.2%}")
        display_df["pnl_dollars"] = display_df["pnl_dollars"].apply(lambda x: f"${x:,.2f}")
        display_df["entry_price"] = display_df["entry_price"].apply(lambda x: f"{x:.2f}")
        display_df["exit_price"] = display_df["exit_price"].apply(lambda x: f"{x:.2f}")
        if "regime_at_entry" in display_df.columns:
            display_df["Regime entry"] = display_df["regime_at_entry"].apply(lambda x: regime_labels.get(int(x), str(x)) if pd.notna(x) and x is not None else "—")
        if "regime_at_exit" in display_df.columns:
            display_df["Regime exit"] = display_df["regime_at_exit"].apply(lambda x: regime_labels.get(int(x), str(x)) if pd.notna(x) else "—")
        if "hold_hours" in display_df.columns:
            display_df["Hold (h)"] = display_df["hold_hours"].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "—")
        cols = [c for c in display_df.columns if c not in ("regime_at_entry", "regime_at_exit")]
        st.dataframe(display_df[cols], use_container_width=True)
    else:
        st.info("No trades in backtest period.")

    # Indicator subplots (RSI, MACD, ADX, Price vs EMAs)
    st.subheader("Indicators (last 500 hours)")
    plot_ind = strategy_df.tail(500).copy().reset_index()
    time_col_ind = plot_ind.columns[0]
    tab1, tab2, tab3, tab4 = st.tabs(["RSI", "MACD / Signal", "ADX", "Price vs EMA50/200"])
    with tab1:
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=plot_ind[time_col_ind], y=plot_ind["RSI"], name="RSI", line=dict(color="#3498db")))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="gray")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="gray")
        fig_rsi.update_layout(height=280, xaxis_title="Time", yaxis_title="RSI", template=template)
        st.plotly_chart(fig_rsi, use_container_width=True)
    with tab2:
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=plot_ind[time_col_ind], y=plot_ind["MACD"], name="MACD", line=dict(color="#2ecc71")))
        fig_macd.add_trace(go.Scatter(x=plot_ind[time_col_ind], y=plot_ind["MACD_Signal"], name="Signal", line=dict(color="#e74c3c", dash="dash")))
        fig_macd.update_layout(height=280, xaxis_title="Time", yaxis_title="MACD", template=template)
        st.plotly_chart(fig_macd, use_container_width=True)
    with tab3:
        fig_adx = go.Figure()
        fig_adx.add_trace(go.Scatter(x=plot_ind[time_col_ind], y=plot_ind["ADX"], name="ADX", line=dict(color="#9b59b6")))
        fig_adx.add_hline(y=25, line_dash="dash", line_color="gray")
        fig_adx.update_layout(height=280, xaxis_title="Time", yaxis_title="ADX", template=template)
        st.plotly_chart(fig_adx, use_container_width=True)
    with tab4:
        fig_ema = go.Figure()
        fig_ema.add_trace(go.Scatter(x=plot_ind[time_col_ind], y=plot_ind["close"], name="Close", line=dict(color="#1f77b4")))
        fig_ema.add_trace(go.Scatter(x=plot_ind[time_col_ind], y=plot_ind["EMA50"], name="EMA 50", line=dict(color="#ff7f0e", dash="dash")))
        fig_ema.add_trace(go.Scatter(x=plot_ind[time_col_ind], y=plot_ind["EMA200"], name="EMA 200", line=dict(color="#2ca02c", dash="dot")))
        fig_ema.update_layout(height=280, xaxis_title="Time", yaxis_title="Price", template=template)
        st.plotly_chart(fig_ema, use_container_width=True)


if __name__ == "__main__":
    main()
