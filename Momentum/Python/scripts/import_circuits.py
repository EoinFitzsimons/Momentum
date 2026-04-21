"""Import circuits JSON into the project's SQLite tracks table.

Default behaviour is safe to run repeatedly: update existing rows or
insert new rows by matching `name` + `country`.

Usage:
    python import_circuits.py [--db /path/to/db] [--mode upsert|insert]
"""
import argparse
import hashlib
import json
import math
import random
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
        # Accept both integer-like strings and float-like strings.
        return int(float(value))
    except Exception:
        return default


def _parse_float(value, default: float) -> float:
    try:
        f = float(value)
        if math.isnan(f) or math.isinf(f):
            return default
        return f
    except Exception:
        return default


def _normalise_surface(surface: str) -> str:
    s = (surface or "asphalt").strip().lower()
    return s if s else "asphalt"


def _seeded_rng(rec: dict) -> random.Random:
    """Build deterministic RNG per circuit so imports are stable across runs."""
    seed_key = "|".join(
        [
            str(rec.get("circuit_id", "")),
            str(rec.get("name", "")),
            str(rec.get("country", "")),
            str(rec.get("primary_discipline") or rec.get("discipline") or "SINGLE_SEATER"),
        ]
    )
    digest = hashlib.sha256(seed_key.encode("utf-8")).digest()
    return random.Random(int.from_bytes(digest[:8], "big", signed=False))


def _normalise_weight_list(weights, total: float) -> list:
    """Scale positive weights so their sum equals total."""
    cleaned = [max(0.0001, float(w)) for w in weights]
    current = sum(cleaned)
    if current <= 0.0:
        return [total / max(1, len(cleaned)) for _ in cleaned]
    factor = total / current
    return [w * factor for w in cleaned]


def _build_drag_strip_instructions(length_m: float) -> list:
    """Generate a point-to-point drag strip instruction set."""
    total_m = max(350.0, float(length_m))
    launch = max(140.0, total_m * 0.40)
    mid = max(120.0, total_m * 0.33)
    finish = max(90.0, total_m - launch - mid)
    return [
        {"type": "S", "length_m": int(round(launch))},
        {"type": "S", "length_m": int(round(mid))},
        {"type": "S", "length_m": int(round(finish))},
    ]


def _synthesise_flowing_instructions(rec: dict) -> list:
    """Create varied, closed-loop instructions from compact track metadata.

    The generated profile intentionally varies corner angles/radii/straight lengths
    so circuits do not collapse into near-regular polygons.
    """
    discipline = str(rec.get("primary_discipline") or rec.get("discipline") or "SINGLE_SEATER").upper()
    length_m = max(800.0, _parse_float(rec.get("length_km"), 3.2) * 1000.0)

    if discipline == "DRAG_ACCELERATION" or bool(rec.get("is_point_to_point", False)):
        return _build_drag_strip_instructions(length_m)

    rng = _seeded_rng(rec)
    turns_raw = _parse_int(rec.get("turns"), max(9, int(length_m // 420)))
    turns = max(8, min(20, turns_raw))

    tightest = max(15.0, _parse_float(rec.get("tightest_corner_radius_m"), 30.0))
    avg_from_speed = max(28.0, _parse_float(rec.get("avg_speed_kmh"), 170.0) * 0.28)
    base_radius = max(tightest * 1.15, min(155.0, avg_from_speed))
    longest_straight = max(120.0, _parse_float(rec.get("longest_straight_m"), length_m * 0.16))

    # Build corner-angle weights and normalize to one full loop (360 degrees).
    angle_weights = [0.78 + rng.random() * 0.60 for _ in range(turns)]
    peak_idx = rng.randrange(turns)
    angle_weights[peak_idx] *= 1.22
    angle_weights[(peak_idx + turns // 2) % turns] *= 1.10
    corner_angles = _normalise_weight_list(angle_weights, 360.0)

    corner_radii = []
    for i in range(turns):
        wave = 0.82 + 0.32 * math.sin((2.0 * math.pi * i / turns) + (rng.random() * 0.35))
        jitter = 0.88 + rng.random() * 0.28
        radius = base_radius * wave * jitter
        radius = max(tightest, min(170.0, radius))
        corner_radii.append(radius)

    corner_arcs = [max(7.0, r * math.radians(a)) for r, a in zip(corner_radii, corner_angles)]
    total_corner_len = sum(corner_arcs)

    straight_budget = max(length_m * 0.22, length_m - total_corner_len)
    straight_weights = [0.65 + rng.random() * 0.85 for _ in range(turns)]
    long_idx = rng.randrange(turns)
    straight_weights[long_idx] *= 1.55
    straight_weights[(long_idx + turns // 2) % turns] *= 1.25
    straight_lengths = _normalise_weight_list(straight_weights, straight_budget)

    # Respect headline longest-straight metric without destabilising closure.
    target_long = min(longest_straight, straight_budget * 0.45)
    if target_long > straight_lengths[long_idx]:
        delta = target_long - straight_lengths[long_idx]
        straight_lengths[long_idx] = target_long
        for i in range(turns):
            if i == long_idx:
                continue
            take = min(delta / max(1, turns - 1), max(0.0, straight_lengths[i] - 35.0))
            straight_lengths[i] -= take

    instructions = []
    for i in range(turns):
        straight_len = int(round(max(30.0, straight_lengths[i])))
        angle_deg = float(max(8.0, min(56.0, corner_angles[i])))
        radius_m = float(max(tightest, min(170.0, corner_radii[i])))
        clothoid_len = float(max(8.0, min(46.0, radius_m * (0.20 + 0.10 * rng.random()))))
        k = float(0.00008 + rng.random() * 0.00005)

        instructions.append({"type": "S", "length_m": straight_len})
        instructions.append(
            {
                "type": "C",
                "angle_deg": angle_deg,
                "radius_m": radius_m,
                "clothoid_len": clothoid_len,
                "k": k,
            }
        )

    return instructions


def _build_track_payload(rec: dict) -> dict:
    surface = _normalise_surface(str(rec.get("surface", "asphalt")))
    discipline = rec.get("primary_discipline") or rec.get("discipline") or "SINGLE_SEATER"
    raw_instructions = rec.get("instructions")
    instructions_json = None
    if isinstance(raw_instructions, list):
        instructions_json = json.dumps(raw_instructions, ensure_ascii=False)
    elif isinstance(rec.get("instructions_json"), str):
        instructions_json = rec.get("instructions_json")
    else:
        synthesized = _synthesise_flowing_instructions(rec)
        if synthesized:
            instructions_json = json.dumps(synthesized, ensure_ascii=False)

    is_point_to_point = rec.get("is_point_to_point")
    if is_point_to_point is None:
        is_point_to_point = str(discipline).upper() == "DRAG_ACCELERATION"

    return {
        "name": rec.get("name") or "",
        "country": rec.get("country") or "",
        "primary_discipline": discipline,
        "is_point_to_point": 1 if bool(is_point_to_point) else 0,
        "joker_enabled": 1 if bool(rec.get("joker_enabled", False)) else 0,
        "instructions_json": instructions_json,
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


def _sanitize_payload(payload: dict) -> dict:
    # Keep physically invalid values from entering the DB.
    payload["name"] = str(payload.get("name") or "").strip()
    payload["country"] = str(payload.get("country") or "").strip()
    payload["length_km"] = max(0.1, _parse_float(payload.get("length_km"), 3.2))
    payload["turns"] = max(1, _parse_int(payload.get("turns"), 12))
    payload["avg_speed_kmh"] = max(1.0, _parse_float(payload.get("avg_speed_kmh"), 160.0))
    payload["longest_straight_m"] = max(1.0, _parse_float(payload.get("longest_straight_m"), 700.0))
    payload["tightest_corner_radius_m"] = max(1.0, _parse_float(payload.get("tightest_corner_radius_m"), 30.0))
    payload["left_turns"] = max(0, _parse_int(payload.get("left_turns"), 6))
    payload["right_turns"] = max(0, _parse_int(payload.get("right_turns"), 6))
    payload["drs_zones"] = max(0, _parse_int(payload.get("drs_zones"), 1))
    payload["surface_grip"] = min(1.5, max(0.0, _parse_float(payload.get("surface_grip"), 1.0)))
    return payload


def _load_circuits(data) -> list:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("circuits", "tracks", "items"):
            value = data.get(key)
            if isinstance(value, list):
                return value
    return []


def _get_track_columns(conn) -> set:
    return {r[1] for r in conn.execute("PRAGMA table_info(tracks)").fetchall()}


def _upsert_tracks(conn, circuits) -> tuple:
    inserted = 0
    updated = 0
    skipped = 0
    upsert_columns = [
        "name",
        "country",
        "primary_discipline",
        "is_point_to_point",
        "joker_enabled",
        "instructions_json",
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
        payload = _sanitize_payload(_build_track_payload(rec))
        name = payload["name"]
        country = payload["country"]
        if not name:
            skipped += 1
            continue
        cur = conn.execute(
            "SELECT id FROM tracks WHERE lower(trim(name)) = lower(trim(?)) AND lower(trim(country)) = lower(trim(?))",
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

    return inserted, updated, skipped


def _insert_tracks(conn, circuits) -> tuple:
    inserted = 0
    skipped = 0
    for c in circuits:
        try:
            name = (c.get("name") or f"Circuit {c.get('circuit_id', '')}").strip()
            if not name:
                skipped += 1
                continue
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
    return inserted, 0, skipped


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
        circuits = _load_circuits(json.load(f))

    if not circuits:
        print("No circuits found in JSON payload.")
        return 1

    with mgr.get_connection() as conn:
        if args.mode == "upsert":
            inserted, updated, skipped = _upsert_tracks(conn, circuits)
        else:
            inserted, updated, skipped = _insert_tracks(conn, circuits)
        conn.commit()

    print(
        f"Imported circuits into DB: {db_path} "
        f"(mode={args.mode}, inserted={inserted}, updated={updated}, skipped={skipped}, total_json={len(circuits)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
