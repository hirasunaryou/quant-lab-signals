# quant-lab-signals

Visualization-first signal research package built around **EMA cross + ATR regime**.

## Requirements
- Python 3.12

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For local development, add `src` to your import path:
```bash
export PYTHONPATH=src
```

## Package layout
- `configs/`: symbol list and rule/notification configs
- `src/quantlab/contract.py`: stable JSON contract dataclasses
- `src/quantlab/io.py`: contract serialization (`to_json`, `from_json`)
- `src/quantlab/cli.py`: command line entry point
- `notebooks/`: visualize / diagnostics / backtest notebooks
- `outputs/`: generated files (ignored except `.gitkeep`)

## Run CLI
Generate a signal JSON for one symbol (existing output format is unchanged):
```bash
PYTHONPATH=src python -m quantlab.cli --symbol 1306.T --period 2y --out outputs/signals.json
```

Generate a bundled signal JSON for multiple symbols from a file:
```bash
PYTHONPATH=src python -m quantlab.cli --symbols-file configs/symbols.json --period 2y --interval 1d --out outputs/signals_bundle.json
```

`--symbols-file` accepts either:
- `{"symbols": ["1306.T", "QQQ"]}`
- `{"symbols": [{"symbol": "1306.T", "name": "TOPIX ETF"}, "QQQ"]}`
- ` ["1306.T", "QQQ"] `

Backward compatibility wrapper also exists:
```bash
PYTHONPATH=src python -m cli --symbol 1306.T
```

## Signal JSON contract
`outputs/signals.json` keeps legacy keys and adds:
- `engine_version`
- `as_of`
- `metrics: { atr, atr_thresh, ema_diff }`

## Run tests
```bash
PYTHONPATH=src pytest -q
```
