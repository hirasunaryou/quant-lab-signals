from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from quantlab.data import fetch_ohlc
from quantlab.rules import make_signal


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
    signal = make_signal(df)

    payload = {
        "generated_at": jst_now_iso(),
        "symbol": args.symbol,
        "period": args.period,
        "interval": args.interval,
        **signal,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
