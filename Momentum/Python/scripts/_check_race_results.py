import argparse
import sqlite3
from pathlib import Path


def _default_db() -> Path:
    return Path(__file__).resolve().parents[1] / "database" / "momentum.db"


def _print_schema(cur) -> bool:
    cur.execute("PRAGMA table_info('race_results')")
    cols = cur.fetchall()
    if not cols:
        print("Table 'race_results' not found or has no columns.")
        return False

    print(f"Found {len(cols)} columns in 'race_results':")
    for cid, name, ctype, notnull, dflt_value, pk in cols:
        print(f"- {name} : {ctype}  (pk={pk}, notnull={notnull}, default={dflt_value})")
    return True


def _print_summary(cur, race_id: int | None, max_rows: int) -> None:
    total = cur.execute("SELECT COUNT(1) FROM race_results").fetchone()[0]
    distinct = cur.execute(
        "SELECT COUNT(DISTINCT race_id) FROM race_results"
    ).fetchone()[0]
    latest_race_id = cur.execute("SELECT MAX(race_id) FROM race_results").fetchone()[0]
    selected_race_id = race_id if race_id is not None else latest_race_id

    print(
        f"total_rows={total}, distinct_race_ids={distinct}, latest_race_id={latest_race_id}"
    )
    if selected_race_id is None:
        print("No race_results rows found")
        return

    rows = cur.execute(
        "SELECT race_id, driver_id, position, status, dnf_reason, time_seconds FROM race_results WHERE race_id = ? ORDER BY position",
        (selected_race_id,),
    ).fetchall()
    print(f"\nSample rows for race_id={selected_race_id}")
    for row in rows[:max_rows]:
        print(row)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect race_results schema and row samples."
    )
    parser.add_argument(
        "--db",
        default=str(_default_db()),
        help="SQLite DB path (default: Momentum/Python/database/momentum.db)",
    )
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Only print race_results schema columns.",
    )
    parser.add_argument(
        "--race-id",
        type=int,
        help="Race ID to print rows for (defaults to latest race_id).",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=40,
        help="Maximum rows to print for selected race (default: 40).",
    )
    args = parser.parse_args(argv)

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"DB not found at: {db_path}")
        return 1

    con = sqlite3.connect(str(db_path))
    cur = con.cursor()
    try:
        if not _print_schema(cur):
            return 1
        if not args.schema_only:
            _print_summary(cur, args.race_id, args.max_rows)
    except Exception as e:
        print(f"ERROR reading race_results data: {e}")
        return 1
    finally:
        con.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
