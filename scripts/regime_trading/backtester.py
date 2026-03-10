"""
Backtester for regime-based strategy.
Supports configurable capital, transaction costs, slippage; outputs Sharpe/Sortino.
"""

import pandas as pd
import numpy as np
from .data_loader import load_ohlcv, load_spy_hourly
from .hmm_engine import fit_hmm, identify_bull_bear_states, FEATURE_RETURNS
from .strategy import prepare_strategy_df, can_enter, should_exit, DEFAULT_CONFIG

STARTING_CAPITAL = 10_000.0
TRANSACTION_COST_BPS = 0.0
SLIPPAGE_BPS = 0.0
BARS_PER_YEAR_HOURLY = 24 * 252


def run_backtest(
    ticker: str | None = None,
    period: str | None = None,
    interval: str | None = None,
    strategy_config: dict | None = None,
    backtest_config: dict | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    Run full simulation. Returns (trades_df, equity_curve_df, metrics_dict).
    - trades_df: columns [entry_time, exit_time, entry_price, exit_price, pnl_pct, pnl_dollars]
    - equity_curve_df: index=datetime, columns [equity, position_held]
    - metrics_dict: total_return, alpha_vs_bh, win_rate, max_drawdown
    """
    raw = load_spy_hourly()
    model, df_regime, _ = fit_hmm(raw)
    bull_state, bear_state = identify_bull_bear_states(df_regime)
    df_regime = df_regime.copy()
    df_regime[FEATURE_RETURNS] = df_regime["close"].pct_change()
    strategy_df = prepare_strategy_df(df_regime, returns_col=FEATURE_RETURNS)
    strategy_df = strategy_df.dropna(subset=["Votes", "ADX", "EMA50", "EMA200", "MACD", "MACD_Signal"])

    equity = STARTING_CAPITAL
    position: float | None = None
    entry_price: float | None = None
    entry_time = None
    entry_bar_idx: int | None = None
    cooldown_until = -1
    trades: list[dict] = []
    equity_curve: list[dict] = []

    for i, (idx, row) in enumerate(strategy_df.iterrows()):
        price = float(row["close"])
        if position is not None:
            if should_exit(row, bear_state):
                slip_exit = 1 - (slip_bps / 10_000)
                exit_price_adj = price * slip_exit
                exit_pnl_pct = (exit_price_adj - entry_price) / entry_price
                exit_pnl_dollars = position * exit_pnl_pct
                cost_dollars = 2 * position * (cost_bps / 10_000)
                equity += exit_pnl_dollars - cost_dollars
                regime_entry = int(strategy_df.loc[entry_time, "Regime"]) if entry_time in strategy_df.index else None
                regime_exit = int(row["Regime"])
                try:
                    hold_hours = (idx - entry_time).total_seconds() / 3600.0
                except Exception:
                    hold_hours = (i - entry_bar_idx) if entry_bar_idx is not None else np.nan
                trades.append({
                    "entry_time": entry_time,
                    "exit_time": idx,
                    "entry_price": entry_price,
                    "exit_price": price,
                    "pnl_pct": exit_pnl_pct,
                    "pnl_dollars": exit_pnl_dollars,
                    "regime_at_entry": regime_entry,
                    "regime_at_exit": regime_exit,
                    "hold_hours": hold_hours,
                })
                position = None
                entry_price = None
                entry_bar_idx = None
                cooldown_until = i + cooldown_hours
            else:
                unrealized_pct = (price - entry_price) / entry_price
                equity_curve.append({"time": idx, "equity": equity + position * unrealized_pct, "position_held": 1})
                continue
        else:
            if i > cooldown_until and can_enter(row, bull_state, strat_cfg):
                slip_ent = 1 + (slip_bps / 10_000)
                entry_price = price * slip_ent
                position = equity
                entry_time = idx
                entry_bar_idx = i
                equity_curve.append({"time": idx, "equity": equity, "position_held": 1})
                continue

        equity_curve.append({"time": idx, "equity": equity, "position_held": 0})

    if position is not None and entry_price is not None:
        last_idx = strategy_df.index[-1]
        last_price = float(strategy_df["close"].iloc[-1])
        slip_exit = 1 - (slip_bps / 10_000)
        last_price_adj = last_price * slip_exit
        exit_pnl_pct = (last_price_adj - entry_price) / entry_price
        cost_dollars = 2 * position * (cost_bps / 10_000)
        equity += position * exit_pnl_pct - cost_dollars
        regime_entry = int(strategy_df.loc[entry_time, "Regime"]) if entry_time in strategy_df.index else None
        regime_exit = int(strategy_df.loc[last_idx, "Regime"])
        hold_hours = (last_idx - entry_time).total_seconds() / 3600.0 if hasattr(last_idx - entry_time, "total_seconds") else np.nan
        trades.append({
            "entry_time": entry_time,
            "exit_time": last_idx,
            "entry_price": entry_price,
            "exit_price": last_price,
            "pnl_pct": exit_pnl_pct,
            "pnl_dollars": position * exit_pnl_pct,
            "regime_at_entry": regime_entry,
            "regime_at_exit": regime_exit,
            "hold_hours": hold_hours,
        })

    last_bar_idx = len(strategy_df) - 1
    in_position = position is not None
    cooldown_remaining_bars = max(0, cooldown_until - last_bar_idx) if not in_position and cooldown_until > last_bar_idx else 0

    trades_df = pd.DataFrame(trades) if trades else pd.DataFrame(
        columns=["entry_time", "exit_time", "entry_price", "exit_price", "pnl_pct", "pnl_dollars", "regime_at_entry", "regime_at_exit", "hold_hours"]
    )
    equity_df = pd.DataFrame(equity_curve).set_index("time")

    total_return = (equity - cap) / cap
    first_close = float(strategy_df["close"].iloc[0])
    last_close = float(strategy_df["close"].iloc[-1])
    bh_return = (last_close / first_close) - 1.0
    alpha_vs_bh = total_return - bh_return
    wins = sum(1 for t in trades if t["pnl_dollars"] > 0)
    win_rate = wins / len(trades) if trades else 0.0
    eq_series = equity_df["equity"]
    rolling_max = eq_series.expanding().max()
    drawdown = (eq_series - rolling_max) / rolling_max.replace(0, np.nan)
    max_drawdown = float(drawdown.min()) if len(drawdown) else 0.0

    returns_series = eq_series.pct_change().dropna()
    n_bars = len(returns_series)
    sharpe = sortino = 0.0
    if n_bars >= 2 and returns_series.std() > 0:
        ann_factor = np.sqrt(BARS_PER_YEAR_HOURLY / max(1, n_bars))
        sharpe = float(returns_series.mean() / returns_series.std() * ann_factor)
        downside = returns_series[returns_series < 0]
        sortino = float(returns_series.mean() / downside.std() * ann_factor) if len(downside) and downside.std() > 0 else sharpe

    metrics = {
        "total_return": total_return,
        "alpha_vs_bh": alpha_vs_bh,
        "win_rate": win_rate,
        "max_drawdown": max_drawdown,
        "buy_hold_return": bh_return,
        "final_equity": equity,
        "num_trades": len(trades),
        "position_state": "LONG" if in_position else "FLAT",
        "cooldown_remaining_bars": cooldown_remaining_bars,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
    }
    return trades_df, equity_df, metrics


if __name__ == "__main__":
    trades_df, equity_df, metrics = run_backtest()
    print("Trades:")
    print(trades_df.to_string())
    print("\nMetrics:", metrics)
