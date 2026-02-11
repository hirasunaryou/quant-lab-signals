from __future__ import annotations

import numpy as np
import pandas as pd

from quantlab.indicators import atr, ema
from quantlab.rules import make_signal


def _synthetic_df(close: np.ndarray, spike_last: bool = True) -> pd.DataFrame:
    high = close + 1.0
    low = close - 1.0
    if spike_last:
        # Inflate last candle range so ATR regime becomes active in tests.
        high[-1] = close[-1] + 15.0
        low[-1] = close[-1] - 15.0
    idx = pd.date_range("2024-01-01", periods=len(close), freq="D")
    return pd.DataFrame(
        {
            "Open": close,
            "High": high,
            "Low": low,
            "Close": close,
            "Volume": 1_000,
        },
        index=idx,
    )


def test_ema_shape_matches_input() -> None:
    s = pd.Series(np.linspace(10, 20, 100))
    out = ema(s, 12)
    assert out.shape == s.shape
    assert out.notna().all()


def test_atr_is_non_negative() -> None:
    close = np.linspace(100, 120, 130)
    df = _synthetic_df(close, spike_last=False)
    out = atr(df, period=14)
    assert (out.dropna() >= 0).all()


def test_cross_detection_buy_on_synthetic_series() -> None:
    # Keep most history soft/downward, then jump to force EMA12 > EMA26 on the last bar.
    close = np.concatenate(
        [
            np.linspace(100, 90, 126),
            np.array([90.0, 90.0, 90.0, 150.0]),
        ]
    )
    df = _synthetic_df(close, spike_last=True)

    signal = make_signal(df)
    assert signal["signal"] == "BUY"
    assert len(signal["reasons"]) == 3
