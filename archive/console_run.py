"""
Console runner for the Basic Race MVP.

- Uses the same persistence and simulator as the GUI.
- Loads the first 20 drivers by ID from the persistent DB, falls back to seeding.
- Prints per-lap standings with driver names and times to the terminal.
- No PyQt required.
"""
from __future__ import annotations

from services.persistence_sqlite import PersistenceSQLite
from sim_simple import simulate_race


def _load_drivers(db):
    """Load drivers from database or seed if empty."""
    drivers = []
    for did in range(1, 21):
        d = db.get_driver(did)
        if d is not None:
            drivers.append(d)

    if len(drivers) == 0:
        print("No drivers found in DB, seeding demo drivers...")
        db.seed_sample_data(count=20)
        drivers = db.list_drivers()

    return drivers


def _print_lap_start(lap_num):
    """Print lap start header."""
    print(f"\n=== Lap {lap_num} start ===")


def _print_standings(lap_num, standings):
    """Print top 10 standings."""
    print(f"Standings (lap {lap_num}):")
    for r in standings[:10]:
        name = r.get('name')
        time_s = r.get('time_seconds')
        pos = r.get('position')
        print(f" {pos:2d}. {name:20s} {time_s:8.2f}s")


def _print_pit(driver_id, lap_num, pit_time):
    """Print pit stop event."""
    print(f"PIT: driver {driver_id} lap {lap_num} (pit_time={pit_time})")


def _print_incident(subtype, driver_id, lap_num):
    """Print incident event."""
    print(f"INCIDENT: {subtype} driver {driver_id} lap {lap_num}")


def _print_race_results(results):
    """Print final race results."""
    print("\nRace finished. Final results:")
    for r in results:
        print(
            f" {
                r.get('position'):2d}. {
                r.get('driver_id'):3d} {
                r.get('time_seconds'):8.2f}s")


def _create_event_callback():
    """Create event callback for race simulation."""
    def evcb(e: dict):
        event_type = e.get("type")
        if event_type == "lap_start":
            _print_lap_start(e.get('lap'))
        elif event_type == "standings":
            _print_standings(e.get('lap'), e.get("standings", []))
        elif event_type == "pit":
            _print_pit(e.get('driver_id'), e.get('lap'), e.get('pit_time'))
        elif event_type == "incident":
            _print_incident(e.get('subtype'), e.get('driver_id'), e.get('lap'))
        elif event_type == "race_finished":
            _print_race_results(e.get('results', []))
    return evcb


def main():
    db = PersistenceSQLite()
    db.ensure_schema()

    drivers = _load_drivers(db)
    track = db.get_track(1)

    print("Loaded drivers:")
    for d in drivers:
        print(f" - {d.id}: {d.name}")
    print("Track:", track.name if track else "(none)")

    evcb = _create_event_callback()

    print("Starting simulation (console)...\n")
    results = simulate_race(
        drivers,
        track,
        seed=None,
        verbose=False,
        event_callback=evcb,
        lap_delay=0.1)

    try:
        db.save_race_results(race_id=1, results=results)
    except Exception as exc:
        print("Warning: failed to save results:", exc)


if __name__ == '__main__':
    main()
