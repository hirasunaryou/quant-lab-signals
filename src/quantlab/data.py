from __future__ import annotations

import pandas as pd
import yfinance as yf


def fetch_ohlc(symbol: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
    """Fetch OHLCV data from yfinance and normalize column layout.

    Notes for learners:
    - yfinance sometimes returns a MultiIndex for columns (field + ticker).
    - We flatten to the field level and retain only standard OHLCV columns.
    - dropna() keeps downstream indicators simple and deterministic.
    """
    df = yf.download(
        symbol,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False,
    )

    if df is None or df.empty:
        raise ValueError(f"Failed to fetch data for {symbol}")

    # MultiIndex example: ('Close', '1306.T') -> 'Close'
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    keep_cols = ["Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in ["High", "Low", "Close"] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required price columns for {symbol}: {missing}")

    out = df[[c for c in keep_cols if c in df.columns]].copy()
    return out.dropna()
