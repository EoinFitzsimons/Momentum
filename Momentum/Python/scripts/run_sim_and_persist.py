import traceback
import os
import sys

# Ensure the package root (Momentum/Python) is on sys.path so `services` imports work
_this_dir = os.path.dirname(__file__)
_pkg_root = os.path.normpath(os.path.join(_this_dir, '..'))
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)

from services.persistence_sqlite import PersistenceSQLite
from services import race_simulation_api as simmod


def main():
    try:
        db = PersistenceSQLite()
        print("DB path:", db.db_path)
        db.ensure_schema()
        # Seed sample data when the database is empty.
        drivers = db.list_drivers()
        if not drivers:
            db.seed_sample_data()
        drivers = db.list_drivers()
        print("drivers len:", len(drivers))
        track = db.get_track(1)
        print("track id:", getattr(track, 'id', None))

        results = simmod.simulate_race(
            drivers,
            track,
            seed=1,
            laps=1,
            verbose=False,
            event_callback=None,
            stop_event=None,
            db=db,
            track_points=None,
        )

        print("results len:", len(results))
        first = results[0]
        pos = getattr(first, 'position', None) if not isinstance(first, dict) else first.get('position')
        print("first pos:", pos)

        db.save_race_results(42, results)
        import sqlite3

        conn = sqlite3.connect(db.db_path)
        cur = conn.cursor()
        cnt = cur.execute("SELECT COUNT(1) FROM race_results WHERE race_id = 42").fetchone()[0]
        print("rows persisted for race_id=42:", cnt)
        cur.execute("SELECT id, driver_id, position, time_seconds FROM race_results WHERE race_id = 42 LIMIT 5")
        rows = cur.fetchall()
        print("sample rows:")
        for r in rows:
            print(r)
        conn.close()
    except Exception:
        traceback.print_exc()


if __name__ == '__main__':
    main()
