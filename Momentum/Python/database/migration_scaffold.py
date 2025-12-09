"""
Migration scaffold for Momentum SQLite database.

This script is safe to run in a test environment. It provides the following modes:
 - dry-run: show planned SQL and actions without applying
 - apply: perform backup, ALTER TABLE to add `attributes_extra`, create
   `driver_career_stats`, and optionally backfill simple aggregates.

Always back up your DB before running in `apply` mode. Use `--db-path`
to point to your database file.
"""
import argparse
import shutil
import sqlite3
import os
import json
from datetime import datetime


def backup_db(db_path: str) -> str:
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"DB not found: {db_path}")
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dest = f"{db_path}.backup.{stamp}"
    shutil.copy2(db_path, dest)
    return dest


def run_sql(conn: sqlite3.Connection, sql: str):
    cur = conn.cursor()
    cur.executescript(sql)
    conn.commit()


CREATE_DRIVER_CAREER_STATS_SQL = '''
CREATE TABLE IF NOT EXISTS driver_career_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    driver_id INTEGER UNIQUE NOT NULL,
    career_wins INTEGER DEFAULT 0,
    career_podiums INTEGER DEFAULT 0,
    career_points INTEGER DEFAULT 0,
    career_starts INTEGER DEFAULT 0,
    career_dnf INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_id) REFERENCES drivers (id)
);
'''


# attributes_extra column is deprecated and removed from codebase; migration
# to drop the column should be performed manually if desired. The scaffold no
# longer attempts to add this column.



def create_career_stats(conn: sqlite3.Connection):
    run_sql(conn, CREATE_DRIVER_CAREER_STATS_SQL)


def simple_backfill_career_stats(conn: sqlite3.Connection):
    cur = conn.cursor()
    # If race_results exists, aggregate simple counts. Otherwise initialize rows.
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='race_results'")
    if cur.fetchone():
        # Aggregate from race_results
        agg_sql = '''
        INSERT OR IGNORE INTO driver_career_stats (driver_id, career_starts, career_wins, career_podiums, career_points, career_dnf)
        SELECT driver_id,
            COUNT(*) as starts,
            SUM(CASE WHEN position=1 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN position<=3 AND position>0 THEN 1 ELSE 0 END) as podiums,
            SUM(points) as points,
            SUM(CASE WHEN position IS NULL THEN 1 ELSE 0 END) as dnfs
        FROM race_results
        GROUP BY driver_id;
        '''
        run_sql(conn, agg_sql)
    else:
        # Initialize empty stats for existing drivers
        run_sql(conn, "INSERT OR IGNORE INTO driver_career_stats (driver_id, career_wins, career_podiums, career_points, career_starts, career_dnf) SELECT id,0,0,0,0,0 FROM drivers;")


def main():
    parser = argparse.ArgumentParser(description='Migration scaffold for Momentum DB')
    parser.add_argument('--db-path', required=True, help='Path to SQLite DB file')
    parser.add_argument('--mode', choices=['dry-run', 'apply'], default='dry-run')
    parser.add_argument('--backfill', action='store_true', help='Backfill simple career stats from race_results')
    args = parser.parse_args()

    db = args.db_path
    actions = []

    actions.append(('Create driver_career_stats table', CREATE_DRIVER_CAREER_STATS_SQL))

    print(f"Planned actions for DB: {db}")
    for title, sql in actions:
        print(f"- {title}")

    if args.mode == 'dry-run':
        print('Dry-run mode; not applying changes.')
        return

    # apply mode
    print('Applying migration - creating backup')
    backup = backup_db(db)
    print(f'Backup created at: {backup}')

    conn = sqlite3.connect(db)
    try:
        create_career_stats(conn)
        if args.backfill:
            print('Backfilling simple career stats...')
            simple_backfill_career_stats(conn)
            print('Backfill complete')
    finally:
        conn.close()

    print('Migration apply complete. Verify results.')


if __name__ == '__main__':
    main()
