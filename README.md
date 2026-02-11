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
- `src/quantlab/data.py`: market data loading (`fetch_ohlc`)
- `src/quantlab/indicators.py`: EMA / ATR indicators
- `src/quantlab/rules.py`: rule-based signal generation
- `src/quantlab/plot.py`: visualization helpers
- `src/cli.py`: command line entry point

## Run CLI
Generate a signal JSON for one symbol:
```bash
PYTHONPATH=src python -m cli --symbol 1306.T --period 2y --out outputs/signals.json
```

## Run notebook
```bash
PYTHONPATH=src jupyter notebook notebooks/01_visualize_signals.ipynb
```

The notebook:
1. Fetches one symbol
2. Computes EMA12/EMA26 and ATR14
3. Draws:
   - `plot_price_ema`
   - `plot_atr_regime`
   - `plot_cross_points`

## Run tests
```bash
PYTHONPATH=src pytest -q
```
