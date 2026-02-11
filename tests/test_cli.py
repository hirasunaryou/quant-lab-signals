from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from quantlab import cli


def _fake_df() -> pd.DataFrame:
    idx = pd.DatetimeIndex(["2026-02-10", "2026-02-11"])
    return pd.DataFrame(
        {
            "Open": [100.0, 101.0],
            "High": [101.0, 103.0],
            "Low": [99.0, 100.0],
            "Close": [100.0, 102.0],
            "Volume": [10, 12],
        },
        index=idx,
    )


def _fake_signal(_: pd.DataFrame) -> dict[str, object]:
    return {
        "last_close": 102.0,
        "prev_close": 100.0,
        "pct_change_1d": 2.0,
        "active": True,
        "signal": "BUY",
        "reasons": ["active", "cross up"],
        "metrics": {"atr": 1.5, "atr_thresh": 1.0, "ema_diff": 0.2},
    }


def test_cli_symbols_file_outputs_bundled_json(tmp_path: Path, monkeypatch) -> None:
    symbols_file = tmp_path / "symbols.json"
    symbols_file.write_text(
        json.dumps({"symbols": [{"symbol": "1306.T", "name": "TOPIX ETF"}, "QQQ"]}),
        encoding="utf-8",
    )
    out_path = tmp_path / "bundle.json"

    fetched_symbols: list[str] = []

    def fake_fetch(symbol: str, period: str, interval: str):
        fetched_symbols.append(symbol)
        return _fake_df()

    monkeypatch.setattr(cli, "fetch_ohlc", fake_fetch)
    monkeypatch.setattr(cli, "make_signal", _fake_signal)
    monkeypatch.setattr(
        "sys.argv",
        [
            "quantlab.cli",
            "--symbols-file",
            str(symbols_file),
            "--period",
            "6mo",
            "--interval",
            "1d",
            "--out",
            str(out_path),
        ],
    )

    cli.main()

    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["timeframe"] == {"period": "6mo", "interval": "1d"}
    assert payload["engine_version"] == cli.ENGINE_VERSION
    assert [row["symbol"] for row in payload["symbols"]] == ["1306.T", "QQQ"]
    assert [row["name"] for row in payload["symbols"]] == ["TOPIX ETF", "QQQ"]
    assert fetched_symbols == ["1306.T", "QQQ"]


def test_parser_requires_symbol_or_symbols_file() -> None:
    parser = cli.build_parser()
    parsed = parser.parse_args(["--symbol", "QQQ"])
    assert parsed.symbol == "QQQ"
    assert parsed.symbols_file is None


def test_parser_rejects_symbol_and_symbols_file_together() -> None:
    parser = cli.build_parser()
    try:
        parser.parse_args(["--symbol", "QQQ", "--symbols-file", "configs/symbols.json"])
        raise AssertionError("Expected parser to reject mutually exclusive args")
    except SystemExit:
        pass
