"""ML bridge utilities for turning OHLCV market data into safe features/labels.

The goal of this module is educational and practical:
- centralize feature engineering in one place,
- make label construction explicit,
- and provide leakage-safe walk-forward splits.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generator, Literal

import numpy as np
import pandas as pd

LabelMethod = Literal["next_day_direction", "return_threshold", "return_quantile"]


@dataclass(frozen=True)
class WalkForwardWindow:
    """Container that describes one walk-forward train/test slice."""

    train_start: pd.Timestamp
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp



def _require_ohlcv(df: pd.DataFrame) -> None:
    required = {"Open", "High", "Low", "Close", "Volume"}
    missing = required.difference(df.columns)
    if missing:
        missing_cols = ", ".join(sorted(missing))
        raise ValueError(f"OHLCV columns are required. Missing: {missing_cols}")



def build_feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Build a feature frame from OHLCV with only past/current information.

    Notes
    -----
    - Every rolling/EMA transform only uses information available up to each row.
    - No future values are referenced.
    """

    _require_ohlcv(df)
    out = pd.DataFrame(index=df.index)

    close = df["Close"].astype(float)
    high = df["High"].astype(float)
    low = df["Low"].astype(float)
    volume = df["Volume"].astype(float)

    # Returns and rolling statistics (trend/volatility basics)
    out["ret_1d"] = close.pct_change()
    out["ret_5d"] = close.pct_change(5)
    out["roll_mean_5"] = out["ret_1d"].rolling(5).mean()
    out["roll_std_5"] = out["ret_1d"].rolling(5).std()
    out["roll_std_20"] = out["ret_1d"].rolling(20).std()

    # EMA spread as trend/momentum proxy
    ema_fast = close.ewm(span=12, adjust=False).mean()
    ema_slow = close.ewm(span=26, adjust=False).mean()
    out["ema_diff"] = ema_fast - ema_slow

    # True Range / ATR as volatility regime proxy
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    out["atr_14"] = tr.rolling(14).mean()

    # Price range / volume changes (micro regime hints)
    out["range_close"] = (high - low) / close.replace(0.0, np.nan)
    out["volume_change_1d"] = volume.pct_change()

    # Normalized signal: scale trend by prevailing volatility
    out["ema_diff_over_atr"] = out["ema_diff"] / out["atr_14"].replace(0.0, np.nan)

    return out



def build_labels(
    df: pd.DataFrame,
    *,
    method: LabelMethod = "next_day_direction",
    threshold: float = 0.0,
    quantile: float = 0.6,
) -> pd.Series:
    """Build a supervised-learning label from Close prices.

    Labels are aligned to timestamp *t* and use the return from t -> t+1.
    """

    _require_ohlcv(df)
    next_ret = df["Close"].astype(float).pct_change().shift(-1)

    if method == "next_day_direction":
        label = (next_ret > 0).astype("float")
    elif method == "return_threshold":
        label = (next_ret > threshold).astype("float")
    elif method == "return_quantile":
        q = float(next_ret.dropna().quantile(quantile))
        label = (next_ret > q).astype("float")
    else:
        raise ValueError(f"Unsupported method: {method}")

    # Last timestamp has no next-day return, so remove it explicitly.
    label[next_ret.isna()] = np.nan
    return label.rename(f"label_{method}")



def make_ml_table(
    df: pd.DataFrame,
    *,
    label_method: LabelMethod = "next_day_direction",
    label_threshold: float = 0.0,
    label_quantile: float = 0.6,
) -> pd.DataFrame:
    """Return one table with features + label, dropping incomplete rows."""

    features = build_feature_frame(df)
    label = build_labels(
        df,
        method=label_method,
        threshold=label_threshold,
        quantile=label_quantile,
    )
    table = features.join(label)
    return table.dropna().copy()



def iter_walk_forward_windows(
    index: pd.DatetimeIndex,
    *,
    train_months: int = 6,
    test_months: int = 1,
) -> Generator[WalkForwardWindow, None, None]:
    """Yield rolling walk-forward windows over a DatetimeIndex.

    Each window is [train_months] followed by [test_months], then rolled forward
    by test_months.
    """

    if not isinstance(index, pd.DatetimeIndex):
        raise TypeError("index must be a pandas.DatetimeIndex")
    if len(index) == 0:
        return

    dates = pd.Series(index).sort_values().reset_index(drop=True)
    start = dates.iloc[0]
    end = dates.iloc[-1]
    cursor = start

    while True:
        train_end = cursor + pd.DateOffset(months=train_months) - pd.Timedelta(days=1)
        test_end = train_end + pd.DateOffset(months=test_months)

        if test_end > end:
            break

        train_mask = (dates >= cursor) & (dates <= train_end)
        test_mask = (dates > train_end) & (dates <= test_end)
        if train_mask.sum() == 0 or test_mask.sum() == 0:
            cursor = cursor + pd.DateOffset(months=test_months)
            continue

        yield WalkForwardWindow(
            train_start=pd.Timestamp(dates[train_mask].iloc[0]),
            train_end=pd.Timestamp(dates[train_mask].iloc[-1]),
            test_start=pd.Timestamp(dates[test_mask].iloc[0]),
            test_end=pd.Timestamp(dates[test_mask].iloc[-1]),
        )

        cursor = cursor + pd.DateOffset(months=test_months)
