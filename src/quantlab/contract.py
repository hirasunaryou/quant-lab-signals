from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

SignalType = Literal["BUY", "SELL", "HOLD"]


@dataclass(slots=True)
class Metrics:
    """Supplemental metrics used for explainability and downstream automation."""

    atr: float
    atr_thresh: float
    ema_diff: float


@dataclass(slots=True)
class SymbolSignal:
    """A single symbol's signal payload.

    Notes:
    - We keep legacy top-level keys (symbol, signal, reasons, etc.) so existing
      notebook and consumer code does not break.
    - `metrics` is additive and can power richer diagnostics in UI / mobile.
    """

    symbol: str
    period: str
    interval: str
    last_close: float
    prev_close: float
    pct_change_1d: float
    active: bool
    signal: SignalType
    reasons: list[str] = field(default_factory=list)
    metrics: Metrics = field(default_factory=lambda: Metrics(atr=0.0, atr_thresh=0.0, ema_diff=0.0))


@dataclass(slots=True)
class SignalReport:
    """Root contract for `outputs/signals.json`."""

    generated_at: str
    engine_version: str
    as_of: str
    signal: SymbolSignal
