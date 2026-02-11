"""Minimal backtesting helpers for tutorial notebooks.

This module intentionally keeps the logic small and dependency-light so it can be
used in educational notebooks without introducing a full backtesting framework.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def generate_positions_from_signals(df: pd.DataFrame) -> pd.Series:
    """Generate a continuous position series from discrete rule signals.

    Expected input columns
    ----------------------
    signal:
        One of ``BUY``, ``SELL``, ``HOLD``. ``HOLD`` means "keep previous
        position", not necessarily flat.

    Returns
    -------
    pd.Series
        Position per timestamp (1.0 for long, -1.0 for short, 0.0 for flat).
    """
    if "signal" not in df.columns:
        raise ValueError("df must contain a 'signal' column")

    # Convert discrete decision events into numeric targets.
    mapped = df["signal"].map({"BUY": 1.0, "SELL": -1.0, "HOLD": np.nan})

    # HOLD keeps the previous exposure. Before first explicit signal, stay flat.
    positions = mapped.ffill().fillna(0.0)
    positions.name = "position"
    return positions.astype(float)


def compute_strategy_returns(df: pd.DataFrame, positions: pd.Series) -> pd.Series:
    """Compute next-day realized strategy returns from positions.

    To avoid future leakage:
    - position at t is decided using information up to t
    - realized return is from close(t) to close(t+1)
    """
    if "Close" not in df.columns:
        raise ValueError("df must contain a 'Close' column")

    aligned_pos = positions.reindex(df.index).astype(float).fillna(0.0)

    # Realized return at index t corresponds to next day's move.
    next_day_returns = df["Close"].pct_change().shift(-1)
    strategy_returns = aligned_pos * next_day_returns
    strategy_returns.name = "strategy_return"
    return strategy_returns


def summarize_performance(returns: pd.Series) -> pd.Series:
    """Summarize key performance metrics for a return stream.

    The output is deterministic and intended for quick side-by-side comparisons
    in ablation and parameter sweep notebooks.
    """
    clean = pd.Series(returns, copy=False).dropna().astype(float)
    if clean.empty:
        return pd.Series(
            {
                "n": 0,
                "mean": np.nan,
                "std": np.nan,
                "hit_rate": np.nan,
                "avg_win": np.nan,
                "avg_loss": np.nan,
                "expectancy": np.nan,
                "sharpe_like": np.nan,
                "cum_return": np.nan,
                "max_drawdown": np.nan,
            },
            dtype=float,
        )

    wins = clean[clean > 0]
    losses = clean[clean < 0]
    p_win = float((clean > 0).mean())
    p_loss = float((clean < 0).mean())

    avg_win = float(wins.mean()) if not wins.empty else 0.0
    avg_loss = float(losses.mean()) if not losses.empty else 0.0
    expectancy = p_win * avg_win + p_loss * avg_loss

    std = float(clean.std(ddof=0))
    sharpe_like = float((clean.mean() / std) * np.sqrt(252.0)) if std > 0 else np.nan

    equity = (1.0 + clean).cumprod()
    running_peak = equity.cummax()
    drawdown = equity / running_peak - 1.0

    return pd.Series(
        {
            "n": int(clean.size),
            "mean": float(clean.mean()),
            "std": std,
            "hit_rate": p_win,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "expectancy": float(expectancy),
            "sharpe_like": sharpe_like,
            "cum_return": float(equity.iloc[-1] - 1.0),
            "max_drawdown": float(drawdown.min()),
        }
    )
