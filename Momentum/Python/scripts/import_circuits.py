"""Import circuits JSON into the project's SQLite tracks table.

Default behaviour is safe to run repeatedly: update existing rows or
insert new rows by matching `name` + `country`.

Usage:
    python import_circuits.py [--db /path/to/db] [--mode upsert|insert]
"""
import argparse
import json
import sys
from pathlib import Path


_SURFACE_GRIP_DEFAULTS = {
    "asphalt": 1.0,
    "concrete": 0.9,
    "mixed": 0.8,
    "gravel": 0.6,
    "dirt": 0.55,
    "sand": 0.5,
    "snow": 0.4,
    "ice": 0.3,
}


def _parse_int(value, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _parse_float(value, default: float) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _normalise_surface(surface: str) -> str:
    s = (surface or "asphalt").strip().lower()
    return s if s else "asphalt"


def _build_track_payload(rec: dict) -> dict:
    surface = _normalise_surface(str(rec.get("surface", "asphalt")))
    return {
        "name": rec.get("name") or "",
        "country": rec.get("country") or "",
        "primary_discipline": rec.get("primary_discipline") or rec.get("discipline") or "SINGLE_SEATER",
        "geometry_json": json.dumps(rec, ensure_ascii=False),
        "length_km": _parse_float(rec.get("length_km"), 3.2),
        "turns": _parse_int(rec.get("turns"), 12),
        "avg_speed_kmh": _parse_float(rec.get("avg_speed_kmh"), 160.0),
        "longest_straight_m": _parse_float(rec.get("longest_straight_m"), 700.0),
        "tightest_corner_radius_m": _parse_float(rec.get("tightest_corner_radius_m"), 30.0),
        "left_turns": _parse_int(rec.get("left_turns"), 6),
        "right_turns": _parse_int(rec.get("right_turns"), 6),
        "drs_zones": _parse_int(rec.get("drs_zones"), 1),
        "surface": surface,
        "surface_type": surface,
        "surface_grip": _parse_float(rec.get("surface_grip"), _SURFACE_GRIP_DEFAULTS.get(surface, 0.9)),
        "climate": rec.get("climate") or "temperate",
    }


def _get_track_columns(conn) -> set:
    return {r[1] for r in conn.execute("PRAGMA table_info(tracks)").fetchall()}


def _upsert_tracks(conn, circuits) -> tuple:
    inserted = 0
    updated = 0
    upsert_columns = [
        "name",
        "country",
        "primary_discipline",
        "geometry_json",
        "length_km",
        "turns",
        "avg_speed_kmh",
        "longest_straight_m",
        "tightest_corner_radius_m",
        "left_turns",
        "right_turns",
        "drs_zones",
        "surface",
        "surface_type",
        "surface_grip",
        "climate",
    ]
    available_columns = [c for c in upsert_columns if c in _get_track_columns(conn)]

    for rec in circuits:
        payload = _build_track_payload(rec)
        name = payload["name"]
        country = payload["country"]
        cur = conn.execute(
            "SELECT id FROM tracks WHERE name = ? AND country = ? COLLATE NOCASE",
            (name, country),
        ).fetchone()
        if cur:
            existing = conn.execute(
                f"SELECT {', '.join(available_columns)} FROM tracks WHERE id = ?",
                (cur["id"],),
            ).fetchone()
            changed = any(existing[col] != payload[col] for col in available_columns)
            if changed:
                set_clause = ", ".join(f"{c} = ?" for c in available_columns)
                values = [payload[c] for c in available_columns]
                conn.execute(
                    f"UPDATE tracks SET {set_clause} WHERE id = ?",
                    (*values, cur["id"]),
                )
                updated += 1
        else:
            insert_columns = ", ".join(available_columns)
            value_slots = ", ".join("?" for _ in available_columns)
            values = [payload[c] for c in available_columns]
            conn.execute(
                f"INSERT INTO tracks ({insert_columns}) VALUES ({value_slots})",
                values,
            )
            inserted += 1

    return inserted, updated


def _insert_tracks(conn, circuits) -> tuple:
    inserted = 0
    for c in circuits:
        try:
            name = c.get("name") or f"Circuit {c.get('circuit_id', '')}"
            country = c.get("country") or ""
            primary = c.get("primary_discipline") or c.get("discipline") or "SINGLE_SEATER"
            geometry = json.dumps(c)
            conn.execute(
                "INSERT INTO tracks (name, country, primary_discipline, geometry_json) VALUES (?, ?, ?, ?)",
                (name, country, primary, geometry),
            )
            inserted += 1
        except Exception as e:
            print(f"Failed to insert circuit {c.get('circuit_id')}: {e}")
    return inserted, 0


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", help="Path to SQLite DB file. If omitted uses config.DATABASE_PATH from package.")
    parser.add_argument(
        "--mode",
        choices=["upsert", "insert"],
        default="upsert",
        help="Import mode: upsert (default: update if found, insert if missing) or insert (append only).",
    )
    args = parser.parse_args(argv)

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
        return 1

    with open(data_file, "r", encoding="utf-8") as f:
        circuits = json.load(f)

    with mgr.get_connection() as conn:
        if args.mode == "upsert":
            inserted, updated = _upsert_tracks(conn, circuits)
        else:
            inserted, updated = _insert_tracks(conn, circuits)
        conn.commit()

    print(f"Imported circuits into DB: {db_path} (mode={args.mode}, inserted={inserted}, updated={updated}, total_json={len(circuits)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
