# /backtest — Run Strategy Backtests

Run the backtest framework for CSP, momentum, and hedging strategies and summarize results.

## Instructions

You are running backtests for Altamira Capital strategy validation. Follow these steps exactly:

### Step 1: Identify scope

The user may provide an optional argument: $ARGUMENTS

- **If no argument:** Run backtest for all strategies (CSP, momentum, hedging).
- **If argument is one of:** `csp`, `momentum`, `hedging`, or `all` — run the corresponding backtest(s). Default: all.

### Step 2: Execute the backtest script

```bash
python scripts/backtest-strategies.py
```

The script uses FMP historical prices and runs CSP (short put), momentum (50-day MA), and hedging (protective puts). Output is printed to stdout; check for a report in `outputs/backtest-results-*.md` if the script writes one.

### Step 3: Summarize results

Report key metrics: win rate (CSP), Sharpe ratio, max drawdown, cumulative return for each strategy. Compare to targets from the investment thesis (e.g. CSP win rate >75%, Sharpe >1.0).

### Step 4: Recommendation

State whether backtest results support proceeding with paper trading. Note any parameter suggestions without changing the script unless the user asks.

## Context

- **Investment thesis:** `outputs/altamira-investment-thesis.md`
- **Benchmark:** SPY
