"""Backward-compatible command for schema-only race_results inspection.

This file forwards to `_check_race_results.py --schema-only` so older
commands keep working.
"""

from __future__ import annotations

from _check_race_results import main


if __name__ == "__main__":
    raise SystemExit(main(["--schema-only"]))
