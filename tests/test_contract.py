from __future__ import annotations

from quantlab.contract import Metrics, SignalReport, SymbolSignal
from quantlab.io import from_json, to_json


def test_contract_roundtrip_serialization() -> None:
    report = SignalReport(
        generated_at="2026-02-11T09:00:00+09:00",
        engine_version="v1",
        as_of="2026-02-10 00:00:00",
        signal=SymbolSignal(
            symbol="1306.T",
            period="2y",
            interval="1d",
            last_close=3000.0,
            prev_close=2950.0,
            pct_change_1d=1.6949,
            active=True,
            signal="BUY",
            reasons=["active", "cross up", "risk ok"],
            metrics=Metrics(atr=45.0, atr_thresh=30.0, ema_diff=12.3),
        ),
    )

    raw = to_json(report)
    restored = from_json(raw)

    assert restored == report


def test_from_json_legacy_compatible_defaults() -> None:
    legacy_plus = """{
      \"generated_at\": \"2026-02-11T09:00:00+09:00\",
      \"symbol\": \"QQQ\",
      \"period\": \"2y\",
      \"interval\": \"1d\",
      \"last_close\": 500.0,
      \"prev_close\": 490.0,
      \"pct_change_1d\": 2.04,
      \"active\": true,
      \"signal\": \"BUY\",
      \"reasons\": [\"sample\"]
    }"""

    restored = from_json(legacy_plus)

    assert restored.engine_version == "v0"
    assert restored.signal.metrics.atr == 0.0
