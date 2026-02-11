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
Generate a signal JSON for one symbol:
```bash
PYTHONPATH=src python -m quantlab.cli --symbol 1306.T --period 2y --out outputs/signals.json
```

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
