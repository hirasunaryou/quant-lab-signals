from __future__ import annotations

import json
from dataclasses import asdict

from .contract import Metrics, SignalReport, SymbolSignal


def to_json(report: SignalReport) -> str:
    """Serialize contract to JSON while preserving legacy top-level fields.

    Compatibility design:
    - Old consumers expect one-symbol flat keys at root (symbol, signal, reasons...)
    - New consumers can additionally rely on engine_version/as_of/metrics.
    """
    flat_signal = asdict(report.signal)
    payload = {
        "generated_at": report.generated_at,
        "engine_version": report.engine_version,
        "as_of": report.as_of,
        **flat_signal,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def from_json(raw: str) -> SignalReport:
    """Deserialize JSON string to contract.

    Accepts the compatibility flat shape emitted by `to_json`.
    """
    data = json.loads(raw)
    metrics_dict = data.get("metrics", {})
    metrics = Metrics(
        atr=float(metrics_dict.get("atr", 0.0)),
        atr_thresh=float(metrics_dict.get("atr_thresh", 0.0)),
        ema_diff=float(metrics_dict.get("ema_diff", 0.0)),
    )
    symbol_signal = SymbolSignal(
        symbol=str(data["symbol"]),
        period=str(data["period"]),
        interval=str(data["interval"]),
        last_close=float(data["last_close"]),
        prev_close=float(data["prev_close"]),
        pct_change_1d=float(data["pct_change_1d"]),
        active=bool(data["active"]),
        signal=str(data["signal"]),
        reasons=list(data.get("reasons", [])),
        metrics=metrics,
    )
    return SignalReport(
        generated_at=str(data["generated_at"]),
        engine_version=str(data.get("engine_version", "v0")),
        as_of=str(data.get("as_of", data["generated_at"])),
        signal=symbol_signal,
    )
