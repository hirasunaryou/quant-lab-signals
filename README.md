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

For notebooks / tests (development environment), install dev dependencies:
```bash
pip install -r requirements-dev.txt
```

> `requirements.txt` keeps runtime dependencies minimal.
> `requirements-dev.txt` includes notebook/test tooling (`jupyter`, `ipykernel`, `pytest`).

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


## Learning path

- 理論ドキュメント: `docs/01_financial_time_series_statistics.md`
- 理論ドキュメント: `docs/02_rule_diagnostics_and_improvements.md`（ルール診断、アブレーション、リーク回避）
- Notebook 04: `notebooks/04_returns_distribution.ipynb`（リターン分布、歪度・尖度、Quantile Plot）
- Notebook 05: `notebooks/05_volatility_clustering.ipynb`（ローリング標準偏差、ATR、|ret| と ret^2 の自己相関）
- Notebook 06: `notebooks/06_autocorr_stationarity_basics.ipynb`（ACF手実装、定常性の直感、任意でADF検定）
- Notebook 07: `notebooks/07_rule_ablation_study.ipynb`（4つのルール変種を比較するアブレーション研究）
- Notebook 08: `notebooks/08_parameter_sweep.ipynb`（EMA/ATR/レジーム窓のパラメータスイープ）

## Run tests
```bash
PYTHONPATH=src pytest -q
```
