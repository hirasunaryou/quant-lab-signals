"""quantlab package for visualization-first signal research."""

from .data import fetch_ohlc
from .indicators import atr, ema
from .plot import plot_atr_regime, plot_cross_points, plot_price_ema
from .rules import make_signal

__all__ = [
    "fetch_ohlc",
    "ema",
    "atr",
    "make_signal",
    "plot_price_ema",
    "plot_atr_regime",
    "plot_cross_points",
]
