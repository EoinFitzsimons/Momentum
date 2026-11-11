#!/usr/bin/env python3
"""
Migration script: rename columns and data from tire_* -> tyre_* in SQLite DB.
This is conservative: it reads the CREATE TABLE SQL for each affected table,
produces a modified CREATE TABLE with renamed columns, copies data, and
replaces the old table. Designed for SQLite.

Usage:
    python scripts/migrate_tire_to_tyre.py --db /path/to/momentum.db

It will create backups named <db>.backup before making changes.
"""
import argparse
import os
import shutil
import sqlite3
import re

REPLACE_PATTERNS = [
    (re.compile(r"\btire_", re.IGNORECASE), "tyre_"),
    (re.compile(r"\bTIRE_"), "TYRE_"),
]

AFFECTED_TABLES = ["drivers"]  # Primary table to migrate; extend if needed


def transform_create_sql(create_sql: str) -> str:
    """Return a modified CREATE TABLE SQL with tire->tyre column renames."""
    new_sql = create_sql
    for patt, repl in REPLACE_PATTERNS:
        new_sql = patt.sub(repl, new_sql)
    return new_sql


def run_migration(db_path: str):
    if not os.path.exists(db_path):
        raise FileNotFoundError(db_path)
    backup = db_path + ".backup"
    print(f"Backing up DB to {backup}")
    shutil.copyfile(db_path, backup)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        for table in AFFECTED_TABLES:
            cur.execute(
                "SELECT name, sql FROM sqlite_master WHERE type='table' AND name=?",
                (table,),
            )
            row = cur.fetchone()
            if not row:
                print(f"Table {table} not found, skipping")
                continue
            orig_sql = row["sql"]
            print(f"Original CREATE for {table}:\n{orig_sql}\n")
            new_sql = transform_create_sql(orig_sql)
            if new_sql == orig_sql:
                print(f"No changes required for {table}")
                continue

            temp_old = f"{table}_old_migr_{os.getpid()}"
            print(f"Renaming {table} -> {temp_old}")
            cur.execute(f"ALTER TABLE {table} RENAME TO {temp_old}")

            print(f"Creating new {table} with updated schema")
            cur.execute(new_sql)

            # Determine column lists
            cur.execute(f"PRAGMA table_info({temp_old})")
            old_cols = [r["name"] for r in cur.fetchall()]
            new_cols = []
            for c in old_cols:
                new_c = c
                for patt, repl in REPLACE_PATTERNS:
                    new_c = patt.sub(repl, new_c)
                new_cols.append(new_c)

            # Intersect new table columns to handle any differences
            cur.execute(f"PRAGMA table_info({table})")
            created_cols = [r["name"] for r in cur.fetchall()]

            # Build copy column lists where new column exists in created table
            copy_map_old = []
            copy_map_new = []
            for old_c, new_c in zip(old_cols, new_cols):
                if new_c in created_cols:
                    copy_map_old.append(old_c)
                    copy_map_new.append(new_c)

            if not copy_map_old:
                print(
                    f"No matching columns found to copy for {table}; manual migration required."
                )
                raise RuntimeError("No columns to copy")

            cols_src = ", ".join([f'"{c}"' for c in copy_map_old])
            cols_dst = ", ".join([f'"{c}"' for c in copy_map_new])

            copy_sql = (
                f"INSERT INTO {table} ({cols_dst}) SELECT {cols_src} FROM {temp_old}"
            )
            print(f"Copying data using:\n{copy_sql}\n")
            cur.execute(copy_sql)

            print(f"Dropping old table {temp_old}")
            cur.execute(f"DROP TABLE {temp_old}")

        conn.commit()
        print("Migration completed successfully.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--db", required=True, help="Path to sqlite database file")
    args = p.parse_args()
    run_migration(args.db)
