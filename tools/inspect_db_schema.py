"""Inspect the Momentum SQLite database and print tables, schemas, and row counts.

Run from repository root with PYTHONPATH set:
  python tools/inspect_db_schema.py
"""

from pathlib import Path
import sqlite3
import sys

DB_PATH = Path(__file__).resolve().parents[1] / "momentum" / "database" / "momentum.db"


def main():
    print(f"Inspecting DB at: {DB_PATH}")
    if not DB_PATH.exists():
        print("Database file not found.")
        sys.exit(2)

    print(f"File size: {DB_PATH.stat().st_size} bytes")
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    # List tables (exclude sqlite internal)
    cur.execute(
        "SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )
    tables = cur.fetchall()
    if not tables:
        print("No user tables found in database.")
        conn.close()
        return

    for name, sql in tables:
        print("\n-- TABLE:", name)
        print(sql or "<no create statement available>")
        try:
            cur.execute(f'SELECT COUNT(*) FROM "{name}"')
            cnt = cur.fetchone()[0]
        except Exception as e:
            cnt = f"ERROR: {e}"
        print("rows:", cnt)
        # print columns
        try:
            cur.execute(f"PRAGMA table_info('{name}')")
            cols = cur.fetchall()
            if cols:
                print("columns:")
                for c in cols:
                    # c: cid, name, type, notnull, dflt_value, pk
                    print(
                        f"  - {c[1]} ({c[2]}) notnull={bool(c[3])} pk={bool(c[5])} default={c[4]}"
                    )
        except Exception:
            pass

    conn.close()


if __name__ == "__main__":
    main()
