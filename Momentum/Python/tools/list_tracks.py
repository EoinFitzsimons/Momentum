"""List tracks from the project's database for inspection.

Run:
    python Momentum/Python/tools/list_tracks.py

Prints: id, name, has_geometry_json, length_km (if present in geometry)
"""

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(repo_root / "Momentum" / "Python"))

from database.database_manager import DatabaseManager

if __name__ == "__main__":
    db = DatabaseManager()
    with db.get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, geometry_json FROM tracks ORDER BY id"
        ).fetchall()
    print(f"Tracks in DB: {len(rows)}")
    for r in rows:
        tid = r["id"]
        name = r["name"] or ""
        geom = r["geometry_json"]
        has_geom = bool(geom)
        length = None
        if has_geom:
            try:
                import json

                parsed = json.loads(geom) if isinstance(geom, str) else geom
                length = parsed.get("length_km") if isinstance(parsed, dict) else None
            except Exception:
                length = None
        print(f"{tid}: {name!r} | geometry: {has_geom} | length_km: {length}")
