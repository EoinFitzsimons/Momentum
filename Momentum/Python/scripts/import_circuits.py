"""Import circuits database into the project's SQLite tracks table.

This script inserts each JSON circuit object into the `tracks` table using
the `geometry_json` column so the existing `DatabaseManager.get_simple_track`
can consume detailed attributes without schema changes.

Usage:
    python import_circuits.py [--db /path/to/db]
"""
import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", help="Path to SQLite DB file. If omitted uses config.DATABASE_PATH from package.")
    args = parser.parse_args()

    # scripts/import_circuits.py lives under Momentum/Python/scripts,
    # so parents[1] is the Python package root.
    py_pkg = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(py_pkg))

    from database.database_manager import DatabaseManager
    from config import DATABASE_PATH as CONFIG_DB_PATH

    db_path = args.db or CONFIG_DB_PATH
    mgr = DatabaseManager(db_path=str(db_path))

    data_file = py_pkg / "data" / "circuits_database.json"
    if not data_file.exists():
        print("circuits_database.json not found in Momentum/Python/data")
        return

    with open(data_file, "r", encoding="utf-8") as f:
        circuits = json.load(f)

    inserted = 0
    with mgr.get_connection() as conn:
        for c in circuits:
            try:
                name = c.get("name") or f"Circuit {c.get('circuit_id', '')}"
                country = c.get("country") or ""
                primary = c.get("primary_discipline") or c.get("discipline") or "SINGLE_SEATER"
                geometry = json.dumps(c)
                conn.execute(
                    "INSERT INTO tracks (name, country, primary_discipline, geometry_json) VALUES (?, ?, ?, ?)",
                    (name, country, primary, geometry)
                )
                inserted += 1
            except Exception as e:
                print(f"Failed to insert circuit {c.get('circuit_id')}: {e}")
        conn.commit()

    print(f"Imported {inserted} circuits into DB: {db_path}")


if __name__ == "__main__":
    main()
