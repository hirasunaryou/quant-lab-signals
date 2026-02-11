from __future__ import annotations

import pandas as pd


def ema(series: pd.Series, span: int) -> pd.Series:
    """Exponential moving average with Pandas EWM.

    Using adjust=False mirrors trading-style recursive EMA calculations.
    """
    return series.ewm(span=span, adjust=False).mean()


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average True Range (ATR).

    True range is the max of:
    1) high-low
    2) abs(high-prev_close)
    3) abs(low-prev_close)
    """
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    prev_close = close.shift(1)

    tr = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    return tr.rolling(period).mean()
