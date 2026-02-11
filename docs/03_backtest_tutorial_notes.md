# Backtest Tutorial Notes (Notebook 03)

Notebook: [`notebooks/03_backtest.ipynb`](../notebooks/03_backtest.ipynb)

## Key takeaways

- A leakage-safe daily backtest should decide signals at close of day *t* and apply positions to returns from day *t+1*.
- In pandas, the core no-look-ahead formula is:
  - `daily_return = close.pct_change()`
  - `strat_ret = position.shift(1) * daily_return`
- Comparing EMA-only vs EMA+ATR-active filtering helps reveal the return/drawdown/turnover trade-offs.
- Minimal but practical metrics include total return, annualized return/vol, Sharpe-like ratio (rf=0), max drawdown, turnover, and win/loss statistics.
- Visual diagnostics (equity curve, drawdown curve, return histogram) are essential for catching unstable behavior that aggregate metrics can hide.

## Suggested study flow

1. Run Notebook 03 as-is.
2. Record metrics for Variant A and Variant B.
3. Change EMA/ATR parameters in the mini exercise section.
4. Compare whether improvements come from true robustness or just reduced trading frequency.
