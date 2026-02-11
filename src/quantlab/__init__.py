"""quantlab package for visualization-first signal research."""

from .contract import Metrics, SignalReport, SymbolSignal
from .data import fetch_ohlc
from .indicators import atr, ema
from .io import from_json, to_json
from .ml_bridge import build_feature_frame, build_labels, iter_walk_forward_windows, make_ml_table
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
    "build_feature_frame",
    "build_labels",
    "make_ml_table",
    "iter_walk_forward_windows",
]
