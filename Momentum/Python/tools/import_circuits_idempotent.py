"""Idempotent importer for circuits_database.json -> tracks table.

Usage:
    python Momentum/Python/tools/import_circuits_idempotent.py

Behavior:
- For each circuit in `Momentum/Python/data/circuits_database.json`:
    - If a track with the same `name` and `country` exists, update geometry and core
        physical/surface fields used by TrackMap/simulation.
    - Otherwise insert a new row with those same fields populated.
"""
import json
from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(repo_root / 'Momentum' / 'Python'))

from database.database_manager import DatabaseManager


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
    """Build DB payload for simulation-relevant track columns."""
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
        "climate": (rec.get("climate") or "temperate"),
    }


def _get_track_columns(conn) -> set[str]:
    return {r[1] for r in conn.execute("PRAGMA table_info(tracks)").fetchall()}


def load_json(path: Path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def upsert_tracks(json_path: Path):
    data = load_json(json_path)
    db = DatabaseManager()
    inserted = 0
    updated = 0
    with db.get_connection() as conn:
        track_columns = _get_track_columns(conn)
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
        available_columns = [c for c in upsert_columns if c in track_columns]

        for rec in data:
            payload = _build_track_payload(rec)
            name = payload["name"]
            country = payload["country"]

            # find existing by name+country (case-insensitive)
            cur = conn.execute("SELECT id, geometry_json FROM tracks WHERE name = ? AND country = ? COLLATE NOCASE", (name, country)).fetchone()
            if cur:
                # keep idempotence: update changed values only
                existing = conn.execute(
                    f"SELECT {', '.join(available_columns)} FROM tracks WHERE id = ?",
                    (cur["id"],),
                ).fetchone()
                changed = False
                for column in available_columns:
                    if existing[column] != payload[column]:
                        changed = True
                        break

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
                placeholders = ", ".join("?" for _ in available_columns)
                values = [payload[c] for c in available_columns]
                conn.execute(
                    f"INSERT INTO tracks ({insert_columns}) VALUES ({placeholders})",
                    values,
                )
                inserted += 1
        conn.commit()

    print(f"Imported circuits: inserted={inserted}, updated={updated}, total={len(data)}")


if __name__ == '__main__':
    repo_root = Path(__file__).resolve().parents[3]
    p = repo_root / 'Momentum' / 'Python' / 'data' / 'circuits_database.json'
    if not p.exists():
        print(f"circuits file not found: {p}")
        sys.exit(1)
    upsert_tracks(p)
