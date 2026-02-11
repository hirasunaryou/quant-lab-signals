from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from quantlab.contract import Metrics, SignalReport, SymbolSignal
from quantlab.data import fetch_ohlc
from quantlab.io import to_json
from quantlab.rules import make_signal

ENGINE_VERSION = "v0"


def jst_now_iso() -> str:
    jst = timezone(timedelta(hours=9))
    return datetime.now(jst).isoformat(timespec="seconds")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate EMA/ATR signal JSON")
    symbol_group = parser.add_mutually_exclusive_group(required=True)
    symbol_group.add_argument("--symbol", help="Ticker symbol (e.g., 1306.T, QQQ)")
    symbol_group.add_argument("--symbols-file", help="Path to JSON symbols list (e.g., configs/symbols.json)")
    parser.add_argument("--period", default="2y", help="yfinance period (default: 2y)")
    parser.add_argument("--interval", default="1d", help="yfinance interval (default: 1d)")
    parser.add_argument("--out", default="outputs/signals.json", help="Output JSON path")
    return parser


def _build_symbol_signal(symbol: str, period: str, interval: str) -> tuple[SymbolSignal, str]:
    """Run the existing data->rule pipeline and return contract + as_of timestamp."""
    df = fetch_ohlc(symbol, period=period, interval=interval)
    signal_data = make_signal(df)
    as_of = str(df.index[-1])

    signal = SymbolSignal(
        symbol=symbol,
        period=period,
        interval=interval,
        last_close=float(signal_data["last_close"]),
        prev_close=float(signal_data["prev_close"]),
        pct_change_1d=float(signal_data["pct_change_1d"]),
        active=bool(signal_data["active"]),
        signal=str(signal_data["signal"]),
        reasons=list(signal_data["reasons"]),
        metrics=Metrics(**signal_data["metrics"]),
    )
    return signal, as_of


def _load_symbols(symbols_file: str) -> list[dict[str, str]]:
    """Load symbols from JSON.

    Supported shapes:
    - ["1306.T", "QQQ"]
    - {"symbols": ["1306.T", "QQQ"]}
    - {"symbols": [{"symbol": "1306.T", "name": "TOPIX"}]}
    """
    data: Any = json.loads(Path(symbols_file).read_text(encoding="utf-8"))
    entries = data.get("symbols", data) if isinstance(data, dict) else data
    if not isinstance(entries, list):
        raise ValueError("symbols-file must contain a JSON array or an object with a 'symbols' array")

    symbols: list[dict[str, str]] = []
    for entry in entries:
        if isinstance(entry, str):
            symbols.append({"symbol": entry, "name": entry})
            continue
        if isinstance(entry, dict) and isinstance(entry.get("symbol"), str):
            # name is optional; defaulting keeps output uniform for all symbol rows.
            name = str(entry.get("name", entry["symbol"]))
            symbols.append({"symbol": entry["symbol"], "name": name})
            continue
        raise ValueError("Each symbol entry must be a string or an object with a 'symbol' field")

    return symbols


def _write_bundled_report(args: argparse.Namespace, out_path: Path) -> None:
    symbols = _load_symbols(args.symbols_file)
    bundled_symbols: list[dict[str, Any]] = []

    for item in symbols:
        signal, _ = _build_symbol_signal(item["symbol"], period=args.period, interval=args.interval)
        # The bundle intentionally nests per-symbol payloads for portfolio-style consumption.
        bundled_symbols.append({"symbol": signal.symbol, "name": item["name"], **asdict(signal)})

    payload = {
        "generated_at": jst_now_iso(),
        "timeframe": {"period": args.period, "interval": args.interval},
        "engine_version": ENGINE_VERSION,
        "symbols": bundled_symbols,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.symbols_file:
        _write_bundled_report(args, out_path)
    else:
        symbol_signal, as_of = _build_symbol_signal(args.symbol, period=args.period, interval=args.interval)
        report = SignalReport(
            generated_at=jst_now_iso(),
            engine_version=ENGINE_VERSION,
            as_of=as_of,
            signal=symbol_signal,
        )
        out_path.write_text(to_json(report), encoding="utf-8")

    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
