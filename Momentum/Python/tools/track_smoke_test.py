"""Smoke test for Track system
Loads a simple track from the database manager and constructs a TrackMap
to validate corners, surface_grip propagation and basic metrics.

Run from repository root:
python Momentum/Python/tools/track_smoke_test.py
"""

import json
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[3]
py_pkg = repo_root / "Momentum" / "Python"
sys.path.insert(0, str(py_pkg))
sys.path.insert(0, str(repo_root))

from database.database_manager import DatabaseManager
from RaceLogic.track_physics import TrackMap


def main():
    db = DatabaseManager()
    print("Loaded DB at:", db.db_path)

    # Get a simple track (creates a default one if none exist)
    st = db.get_simple_track()
    print("SimpleTrack:")
    print(json.dumps(st.__dict__, indent=2, default=str))

    # Build TrackMap
    try:
        tm = TrackMap(st)
    except Exception as e:
        print("ERROR: failed to build TrackMap:", e)
        raise

    print("TrackMap build successful")
    print("Corners:", len(tm.corners))
    # Print first 5 corners info
    for i, corner in enumerate(tm.corners[:5]):
        print(
            f"  Corner {i+1}: apex_speed_kmh={corner.apex_speed_kmh:.1f}, grip_level={corner.grip_level}"
        )


if __name__ == "__main__":
    main()
