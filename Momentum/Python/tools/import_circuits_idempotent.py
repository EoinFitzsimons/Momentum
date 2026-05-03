"""Backward-compatible entry point for repeat-safe circuit import.

This file is a thin pass-through so older commands still work.
The real implementation is in `scripts/import_circuits.py`.
"""

import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    py_pkg = repo_root / "Momentum" / "Python"
    sys.path.insert(0, str(py_pkg))

    from scripts import import_circuits as importer

    return int(importer.main(["--mode", "upsert"]))


if __name__ == "__main__":
    raise SystemExit(main())
