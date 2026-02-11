import numpy as np
import pandas as pd

from quantlab.stats import autocorr, log_returns, rolling_volatility


def test_log_returns_matches_manual_formula() -> None:
    prices = pd.Series([100.0, 110.0, 121.0])
    got = log_returns(prices)
    expected = pd.Series([np.nan, np.log(1.1), np.log(1.1)])
    pd.testing.assert_series_equal(got, expected)


def test_rolling_volatility_basic_window() -> None:
    returns = pd.Series([0.01, -0.01, 0.02, -0.02])
    got = rolling_volatility(returns, window=2)
    expected = returns.rolling(2).std(ddof=0)
    pd.testing.assert_series_equal(got, expected)


def test_autocorr_positive_lag1_for_ar_like_series() -> None:
    series = pd.Series([1, 2, 3, 4, 5], dtype=float)
    got = autocorr(series, max_lag=2)
    assert got.index.tolist() == [1, 2]
    assert got.iloc[0] > 0
