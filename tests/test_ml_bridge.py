import numpy as np
import pandas as pd

from quantlab.ml_bridge import build_feature_frame, build_labels, iter_walk_forward_windows, make_ml_table


def _sample_ohlcv(n: int = 80) -> pd.DataFrame:
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    close = pd.Series(100 + np.cumsum(np.random.normal(0, 1, n)), index=idx)
    open_ = close.shift(1).fillna(close.iloc[0])
    high = np.maximum(open_, close) + 0.5
    low = np.minimum(open_, close) - 0.5
    volume = pd.Series(1_000_000 + np.random.normal(0, 10_000, n), index=idx)
    return pd.DataFrame({"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume}, index=idx)


def test_feature_and_label_shapes_are_reasonable() -> None:
    df = _sample_ohlcv(120)
    features = build_feature_frame(df)
    labels = build_labels(df)
    table = make_ml_table(df)

    assert len(features) == len(df)
    assert labels.isna().sum() >= 1
    assert table.shape[0] > 50
    assert "ema_diff_over_atr" in table.columns


def test_walk_forward_windows_are_ordered_and_non_empty() -> None:
    df = _sample_ohlcv(260)
    windows = list(iter_walk_forward_windows(df.index, train_months=6, test_months=1))

    assert len(windows) > 0
    for w in windows:
        assert w.train_start <= w.train_end < w.test_start <= w.test_end
