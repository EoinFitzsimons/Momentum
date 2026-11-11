"""Export every name in the seed world for browsing in a database viewer.

The seeder used to keep a 29 MB ``used_names.db`` in the repository purely so
the generated names could be read by hand. This writes the same thing on
demand from whichever database you point it at, as a small SQLite file (or
CSV) under ``build/``.

    python tools/export_used_names.py
    python tools/export_used_names.py --db path/to/save.db --format csv
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from momentum.config import DATABASE_PATH  # noqa: E402

SOURCES = (
    ("driver", "SELECT name, nationality FROM drivers ORDER BY name"),
    ("staff", "SELECT name, NULL FROM staff_members ORDER BY name"),
    ("team", "SELECT name, nationality FROM teams ORDER BY name"),
)


def collect(db_path: Path) -> list[tuple[str, str, str | None]]:
    rows: list[tuple[str, str, str | None]] = []
    with sqlite3.connect(db_path) as conn:
        for kind, query in SOURCES:
            rows.extend((kind, name, nationality) for name, nationality in conn.execute(query))
    return rows


def write_sqlite(rows, out: Path) -> None:
    if out.exists():
        out.unlink()
    with sqlite3.connect(out) as conn:
        conn.execute("CREATE TABLE used_names (kind TEXT, name TEXT, nationality TEXT)")
        conn.executemany("INSERT INTO used_names VALUES (?, ?, ?)", rows)


def write_csv(rows, out: Path) -> None:
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["kind", "name", "nationality"])
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--db", default=DATABASE_PATH, help="SQLite database to read (default: the seed world)")
    parser.add_argument("--format", choices=("sqlite", "csv"), default="sqlite")
    parser.add_argument("--out", help="Output path (default: build/used_names.db or .csv)")
    args = parser.parse_args(argv)

    rows = collect(Path(args.db))
    out = Path(args.out) if args.out else REPO_ROOT / "build" / f"used_names.{'db' if args.format == 'sqlite' else 'csv'}"
    out.parent.mkdir(parents=True, exist_ok=True)
    (write_sqlite if args.format == "sqlite" else write_csv)(rows, out)
    print(f"{len(rows)} names written to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
