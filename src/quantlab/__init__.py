"""quantlab package for visualization-first signal research."""

from .contract import Metrics, SignalReport, SymbolSignal
from .data import fetch_ohlc
from .indicators import atr, ema
from .io import from_json, to_json
from .plot import plot_atr_regime, plot_cross_points, plot_price_ema
from .rules import make_signal
from .stats import autocorr, log_returns, rolling_volatility

__all__ = [
    "Metrics",
    "SignalReport",
    "SymbolSignal",
    "fetch_ohlc",
    "ema",
    "atr",
    "make_signal",
    "to_json",
    "from_json",
    "plot_price_ema",
    "plot_atr_regime",
    "plot_cross_points",
    "log_returns",
    "autocorr",
    "rolling_volatility",
]
