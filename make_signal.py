from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Literal

import numpy as np
import pandas as pd
import yfinance as yf

Signal = Literal["BUY", "SELL", "HOLD"]


@dataclass
class SymbolConfig:
    symbol: str
    name: str


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    ATR (Average True Range)
    df: columns must contain High, Low, Close
    """
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    prev_close = close.shift(1)

    tr = pd.concat(
        [
            (high - low),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    return tr.rolling(period).mean()


def make_signal(df: pd.DataFrame) -> dict:
    """
    Rule-based v0
    - Active: ATR(14) > median(ATR(14) over last 60)
    - Signal: EMA12/EMA26 cross (today vs yesterday) when Active
    """
    close = df["Close"]
    high = df["High"]
    low = df["Low"]

    # Basic sanity
    if len(df) < 120:
        raise ValueError("Not enough data (need ~120 trading days).")

    df = df.copy()
    df["EMA12"] = ema(close, 12)
    df["EMA26"] = ema(close, 26)
    df["ATR14"] = atr(df, 14)

    # Use last available day
    last = df.iloc[-1]
    prev = df.iloc[-2]

    # Active threshold: median ATR of last 60 days (excluding NaN)
    atr_window = df["ATR14"].iloc[-60:].dropna()
    atr_thresh = float(atr_window.median()) if len(atr_window) else float(df["ATR14"].dropna().median())

    active = float(last["ATR14"]) > float(atr_thresh)


    # Cross logic
    ema_diff_last = float(last["EMA12"] - last["EMA26"])
    ema_diff_prev = float(prev["EMA12"] - prev["EMA26"])

    signal: Signal = "HOLD"
    reasons: list[str] = []

    # Reasons always include volatility context
    reasons.append(f"ATR(14)={float(last['ATR14']):.4f} vs thresh(median60)={atr_thresh:.4f}")
    reasons.append(f"EMA12-EMA26={ema_diff_last:.4f} (prev {ema_diff_prev:.4f})")

    if not active:
        reasons.insert(0, "ATR(14) below threshold → Inactive")
        signal = "HOLD"
        reasons.append("No trade: inactive regime")
    else:
        reasons.insert(0, "ATR(14) above threshold → Active")

        # Cross up/down
        crossed_up = (ema_diff_prev <= 0.0) and (ema_diff_last > 0.0)
        crossed_down = (ema_diff_prev >= 0.0) and (ema_diff_last < 0.0)

        if crossed_up:
            signal = "BUY"
            reasons.append("EMA(12) crossed above EMA(26)")
        elif crossed_down:
            signal = "SELL"
            reasons.append("EMA(12) crossed below EMA(26)")
        else:
            signal = "HOLD"
            reasons.append("No EMA cross")

    # Simple daily change
    last_close = float(last["Close"])
    prev_close = float(prev["Close"])
    pct_change_1d = (last_close / prev_close - 1.0) * 100.0

    return {
        "last_close": last_close,
        "prev_close": prev_close,
        "pct_change_1d": float(pct_change_1d),
        "active": active,
        "signal": signal,
        "reasons": reasons[:3],  # keep UI clean: top 3
    }


def fetch_ohlc(symbol: str, period: str = "1y") -> pd.DataFrame:
    """
    Fetch daily OHLCV. Uses yfinance.
    """
    df = yf.download(symbol, period=period, interval="1d", auto_adjust=False, progress=False)

    # 1) empty check
    if df is None or df.empty:
        raise ValueError(f"Failed to fetch data for {symbol}")

    # 2) MultiIndex columns -> flatten (e.g., ('Close','1306.T') -> 'Close')
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # 3) keep standard columns only
    need_cols = ["Open", "High", "Low", "Close", "Volume"]
    df = df[[c for c in need_cols if c in df.columns]].copy()

    df = df.dropna()
    return df


def jst_now_iso() -> str:
    JST = timezone(timedelta(hours=9))
    return datetime.now(JST).isoformat(timespec="seconds")


def main() -> None:
    symbols = [
        SymbolConfig(symbol="1306.T", name="TOPIX ETF (1306)"),
        SymbolConfig(symbol="QQQ", name="Invesco QQQ Trust"),
    ]

    out = {
        "generated_at": jst_now_iso(),
        "timeframe": "1d",
        "symbols": [],
    }

    for s in symbols:
        df = fetch_ohlc(s.symbol, period="2y")
        sig = make_signal(df)
        out["symbols"].append(
            {
                "symbol": s.symbol,
                "name": s.name,
                **sig,
            }
        )

    with open("signals.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print("Wrote signals.json")


if __name__ == "__main__":
    main()
