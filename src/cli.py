"""Backward-compatible wrapper.

Historically the project used `python -m cli`.
Preferred entrypoint is now `python -m quantlab.cli`.
"""

from quantlab.cli import main


if __name__ == "__main__":
    main()
