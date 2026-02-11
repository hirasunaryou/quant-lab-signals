from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

from quantlab.contract import Metrics, SignalReport, SymbolSignal
from quantlab.data import fetch_ohlc
from quantlab.io import to_json
from quantlab.rules import make_signal

ENGINE_VERSION = "v0"


def jst_now_iso() -> str:
    jst = timezone(timedelta(hours=9))
    return datetime.now(jst).isoformat(timespec="seconds")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate EMA/ATR signal JSON for one symbol")
    parser.add_argument("--symbol", required=True, help="Ticker symbol (e.g., 1306.T, QQQ)")
    parser.add_argument("--period", default="2y", help="yfinance period (default: 2y)")
    parser.add_argument("--interval", default="1d", help="yfinance interval (default: 1d)")
    parser.add_argument("--out", default="outputs/signals.json", help="Output JSON path")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    df = fetch_ohlc(args.symbol, period=args.period, interval=args.interval)
    signal_data = make_signal(df)
    as_of = str(df.index[-1])

    # Contract object is explicit so we can evolve fields safely without ad-hoc dict edits.
    symbol_signal = SymbolSignal(
        symbol=args.symbol,
        period=args.period,
        interval=args.interval,
        last_close=float(signal_data["last_close"]),
        prev_close=float(signal_data["prev_close"]),
        pct_change_1d=float(signal_data["pct_change_1d"]),
        active=bool(signal_data["active"]),
        signal=str(signal_data["signal"]),
        reasons=list(signal_data["reasons"]),
        metrics=Metrics(**signal_data["metrics"]),
    )
    report = SignalReport(
        generated_at=jst_now_iso(),
        engine_version=ENGINE_VERSION,
        as_of=as_of,
        signal=symbol_signal,
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(to_json(report), encoding="utf-8")

    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
