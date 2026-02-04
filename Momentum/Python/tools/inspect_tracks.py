"""Inspect tracks stored in the database and build TrackMap for each.

Prints a concise report per track:
- id, name
- has geometry_json
- fields: surface, surface_grip
- TrackMap built: number of corners, average corner grip

Run:
python Momentum/Python/tools/inspect_tracks.py
"""
import sys
from pathlib import Path
import json

repo_root = Path(__file__).resolve().parents[3]
py_pkg = repo_root / 'Momentum' / 'Python'
sys.path.insert(0, str(py_pkg))
sys.path.insert(0, str(repo_root))

from database.database_manager import DatabaseManager
from RaceLogic.track_physics import TrackMap


def analyze():
    db = DatabaseManager()
    with db.get_connection() as conn:
        # discover available columns on tracks table
        cols = [r[1] for r in conn.execute("PRAGMA table_info(tracks)").fetchall()]
        # choose candidate fields if present
        select_fields = ["id", "name"]
        for c in ("geometry_json", "surface", "surface_grip", "surface_type"):
            if c in cols:
                select_fields.append(c)

        sql = f"SELECT {', '.join(select_fields)} FROM tracks ORDER BY id"
        rows = conn.execute(sql).fetchall()

    if not rows:
        print("No tracks found in database.")
        return

    print(f"Found {len(rows)} tracks in DB: \n")
    for row in rows:
        tid = row[0]
        name = row[1]
        # optional fields
        geom_raw = None
        surface = None
        surface_grip = None
        surface_type = None
        # map values by index based on select_fields
        for idx, field in enumerate(select_fields):
            if field == 'geometry_json':
                geom_raw = row[idx]
            if field == 'surface':
                surface = row[idx]
            if field == 'surface_grip':
                surface_grip = row[idx]
            if field == 'surface_type':
                surface_type = row[idx]

        has_geom = bool(geom_raw)
        print(f"Track {tid}: {name}")
        print(f"  has_geometry_json: {has_geom}")
        print(f"  surface: {surface}  surface_type: {surface_type}  surface_grip: {surface_grip}")

        # Build TrackMap if possible
        try:
            if has_geom:
                # attempt to parse geometry_json into Track object
                # We'll use DatabaseManager.get_track to get a Track dataclass
                t = db.get_track(tid)
            else:
                # fallback to get_simple_track but pass track_id to retrieve row
                t = db.get_track(tid)

            if t:
                tm = TrackMap(t)
                grips = [c.grip_level for c in tm.corners if hasattr(c, 'grip_level')]
                avg_grip = sum(grips) / len(grips) if grips else None
                print(f"  TrackMap corners: {len(tm.corners)}  avg_corner_grip: {avg_grip}")
            else:
                print("  Unable to construct Track object for this row.")
        except Exception as e:
            print("  ERROR building TrackMap:", e)

        print("")


if __name__ == '__main__':
    analyze()
