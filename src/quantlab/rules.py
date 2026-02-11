from __future__ import annotations

from typing import Literal

import pandas as pd

from .indicators import atr, ema

Signal = Literal["BUY", "SELL", "HOLD"]


def make_signal(df: pd.DataFrame) -> dict:
    """Generate a rule-based signal using ATR activity and EMA cross.

    Rule summary:
    - Active regime: ATR(14) > median of ATR(14) over the latest 60 rows.
    - Signal trigger: EMA12/EMA26 cross on latest row, only when active.
    - reasons is trimmed to top 3 for UI readability.

    Returns
    -------
    dict
        Legacy-compatible keys plus `metrics` for richer diagnostics.
    """
    if len(df) < 120:
        raise ValueError("Not enough data (need ~120 trading days).")

    work = df.copy()
    work["EMA12"] = ema(work["Close"], 12)
    work["EMA26"] = ema(work["Close"], 26)
    work["ATR14"] = atr(work, 14)

    last = work.iloc[-1]
    prev = work.iloc[-2]

    atr_window = work["ATR14"].iloc[-60:].dropna()
    fallback = work["ATR14"].dropna().median()
    atr_thresh = float(atr_window.median()) if len(atr_window) else float(fallback)

    atr_last = float(last["ATR14"])
    active = atr_last > atr_thresh

    ema_diff_last = float(last["EMA12"] - last["EMA26"])
    ema_diff_prev = float(prev["EMA12"] - prev["EMA26"])

    signal: Signal = "HOLD"
    reasons: list[str] = [
        f"ATR(14)={atr_last:.4f} vs thresh(median60)={atr_thresh:.4f}",
        f"EMA12-EMA26={ema_diff_last:.4f} (prev {ema_diff_prev:.4f})",
    ]

    if not active:
        reasons.insert(0, "ATR(14) below threshold → Inactive")
        reasons.append("No trade: inactive regime")
    else:
        reasons.insert(0, "ATR(14) above threshold → Active")

        crossed_up = (ema_diff_prev <= 0.0) and (ema_diff_last > 0.0)
        crossed_down = (ema_diff_prev >= 0.0) and (ema_diff_last < 0.0)

        if crossed_up:
            signal = "BUY"
            reasons.append("EMA(12) crossed above EMA(26)")
        elif crossed_down:
            signal = "SELL"
            reasons.append("EMA(12) crossed below EMA(26)")
        else:
            reasons.append("No EMA cross")

    last_close = float(last["Close"])
    prev_close = float(prev["Close"])
    pct_change_1d = (last_close / prev_close - 1.0) * 100.0

    return {
        "last_close": last_close,
        "prev_close": prev_close,
        "pct_change_1d": float(pct_change_1d),
        "active": active,
        "signal": signal,
        "reasons": reasons[:3],
        "metrics": {
            "atr": atr_last,
            "atr_thresh": atr_thresh,
            "ema_diff": ema_diff_last,
        },
    }
