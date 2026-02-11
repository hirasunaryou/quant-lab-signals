from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from .indicators import atr, ema


def _with_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Small helper so all plot functions share identical indicator definitions."""
    work = df.copy()
    work["EMA12"] = ema(work["Close"], 12)
    work["EMA26"] = ema(work["Close"], 26)
    work["ATR14"] = atr(work, 14)
    work["ATR14_MED60"] = work["ATR14"].rolling(60).median()
    work["ACTIVE"] = work["ATR14"] > work["ATR14_MED60"]
    return work


def plot_price_ema(df: pd.DataFrame):
    """Plot Close with EMA12 and EMA26 for trend inspection."""
    work = _with_indicators(df)

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(work.index, work["Close"], label="Close", linewidth=1.4)
    ax.plot(work.index, work["EMA12"], label="EMA12", linewidth=1.2)
    ax.plot(work.index, work["EMA26"], label="EMA26", linewidth=1.2)
    ax.set_title("Price with EMA12 / EMA26")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    return fig, ax


def plot_atr_regime(df: pd.DataFrame):
    """Plot ATR14 and median60, and shade active volatility regions."""
    work = _with_indicators(df)

    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(work.index, work["ATR14"], label="ATR14", color="tab:orange")
    ax.plot(work.index, work["ATR14_MED60"], label="Median60", color="tab:blue", linestyle="--")

    # Fill regions where ATR is above its rolling median.
    ax.fill_between(
        work.index,
        work["ATR14"],
        work["ATR14_MED60"],
        where=work["ACTIVE"].fillna(False),
        color="tomato",
        alpha=0.25,
        label="Active",
    )

    ax.set_title("ATR Regime (Active when ATR14 > Median60)")
    ax.set_xlabel("Date")
    ax.set_ylabel("ATR")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    return fig, ax


def plot_cross_points(df: pd.DataFrame):
    """Mark BUY/SELL EMA cross points on top of Close price."""
    work = _with_indicators(df)
    work["EMA_DIFF"] = work["EMA12"] - work["EMA26"]

    prev = work["EMA_DIFF"].shift(1)
    crossed_up = (prev <= 0) & (work["EMA_DIFF"] > 0)
    crossed_down = (prev >= 0) & (work["EMA_DIFF"] < 0)

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(work.index, work["Close"], label="Close", linewidth=1.2, color="black")

    # BUY markers: upward triangle.
    ax.scatter(
        work.index[crossed_up.fillna(False)],
        work.loc[crossed_up.fillna(False), "Close"],
        marker="^",
        color="green",
        s=70,
        label="BUY cross",
        zorder=3,
    )

    # SELL markers: downward triangle.
    ax.scatter(
        work.index[crossed_down.fillna(False)],
        work.loc[crossed_down.fillna(False), "Close"],
        marker="v",
        color="red",
        s=70,
        label="SELL cross",
        zorder=3,
    )

    ax.set_title("EMA Cross Points")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    return fig, ax
