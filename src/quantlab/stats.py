"""Lightweight statistical helpers for financial time-series tutorials."""

from __future__ import annotations

import numpy as np
import pandas as pd


def log_returns(series: pd.Series) -> pd.Series:
    """Compute log returns from a price series.

    Formula:
        r_t = ln(P_t / P_{t-1})

    Parameters
    ----------
    series:
        Price series indexed by date/time.
    """
    # Convert to float so we avoid integer division pitfalls and keep behavior explicit.
    prices = pd.Series(series, copy=False).astype(float)
    return np.log(prices / prices.shift(1))


def rolling_volatility(returns: pd.Series, window: int) -> pd.Series:
    """Compute rolling volatility (standard deviation) for returns.

    Formula:
        sigma_t(window) = std(r_{t-window+1}, ..., r_t)
    """
    if window <= 0:
        raise ValueError("window must be a positive integer")

    # ddof=0 uses population-style std and keeps behavior deterministic across notebooks.
    return pd.Series(returns, copy=False).rolling(window=window).std(ddof=0)


def autocorr(series: pd.Series, max_lag: int) -> pd.Series:
    """Compute a simple sample autocorrelation function up to ``max_lag``.

    This implementation is dependency-light and avoids statsmodels.
    """
    if max_lag < 1:
        raise ValueError("max_lag must be >= 1")

    values = pd.Series(series, copy=False).dropna().astype(float).to_numpy()
    if values.size == 0:
        return pd.Series(dtype=float)

    centered = values - values.mean()
    denom = np.dot(centered, centered)
    if denom == 0:
        return pd.Series([np.nan] * max_lag, index=range(1, max_lag + 1), dtype=float)

    acf_values = []
    for lag in range(1, max_lag + 1):
        if lag >= centered.size:
            acf_values.append(np.nan)
            continue
        numer = np.dot(centered[lag:], centered[:-lag])
        acf_values.append(float(numer / denom))

    return pd.Series(acf_values, index=range(1, max_lag + 1), dtype=float)
