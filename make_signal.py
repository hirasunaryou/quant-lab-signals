"""Backward-compatible entry point.

Use the new modular CLI instead:
    PYTHONPATH=src python -m cli --symbol 1306.T --period 2y --out outputs/signals.json
"""

from cli import main


if __name__ == "__main__":
    main()
