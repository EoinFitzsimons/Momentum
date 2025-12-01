"""
Console runner for the Basic Race MVP.

- Uses the same persistence and simulator as the GUI.
- Loads the first 20 drivers by ID from the persistent DB, falls back to seeding.
- Prints per-lap standings with driver names and times to the terminal.
- No PyQt required.
"""
from __future__ import annotations

import time
from persistence_sqlite import PersistenceSQLite
from sim_simple import simulate_race


def main():
    db = PersistenceSQLite()
    db.ensure_schema()

    drivers = []
    for did in range(1, 21):
        d = db.get_driver(did)
        if d is not None:
            drivers.append(d)

    if len(drivers) == 0:
        print("No drivers found in DB, seeding demo drivers...")
        db.seed_sample_data(count=20)
        drivers = db.list_drivers()

    track = db.get_track(1)
    print("Loaded drivers:")
    for d in drivers:
        print(f" - {d.id}: {d.name}")
    print("Track:", track.name if track else "(none)")

    def evcb(e: dict):
        t = e.get("type")
        if t == "lap_start":
            print(f"\n=== Lap {e.get('lap')} start ===")
        elif t == "standings":
            s = e.get("standings", [])
            print(f"Standings (lap {e.get('lap')}):")
            for r in s[:10]:
                name = r.get('name')
                time_s = r.get('time_seconds')
                pos = r.get('position')
                print(f" {pos:2d}. {name:20s} {time_s:8.2f}s")
        elif t == "pit":
            print(f"PIT: driver {e.get('driver_id')} lap {e.get('lap')} (pit_time={e.get('pit_time')})")
        elif t == "incident":
            print(f"INCIDENT: {e.get('subtype')} driver {e.get('driver_id')} lap {e.get('lap')}")
        elif t == "race_finished":
            print("\nRace finished. Final results:")
            res = e.get('results', [])
            for r in res:
                print(f" {r.get('position'):2d}. {r.get('driver_id'):3d} {r.get('time_seconds'):8.2f}s")

    print("Starting simulation (console)...\n")
    results = simulate_race(drivers, track, seed=None, verbose=False, event_callback=evcb, lap_delay=0.1)
    # Save results back to DB (non-destructive)
    try:
        db.save_race_results(race_id=1, results=results)
    except Exception as exc:
        print("Warning: failed to save results:", exc)


if __name__ == '__main__':
    main()
