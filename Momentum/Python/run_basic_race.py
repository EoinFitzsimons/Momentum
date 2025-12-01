from persistence_sqlite import PersistenceSQLite
from sim_simple import simulate_race
from typing import List


def run_mvp(db_path: str | None = None, seed: int = 42, verbose: bool = False) -> List:
    """Run the MVP race and return results (list of RaceResult).

    If `db_path` is provided it will be passed to PersistenceSQLite, otherwise default is used.
    """
    db = PersistenceSQLite(db_path) if db_path else PersistenceSQLite()
    db.ensure_schema()
    db.seed_sample_data()

    drivers = db.list_drivers()
    track = db.get_track(1)
    if not track:
        raise RuntimeError("Track not found")

    results = simulate_race(drivers, track, seed=seed, verbose=verbose)
    db.save_race_results(race_id=1, results=results)
    return results


def main():
    results = run_mvp(seed=42)
    print("Basic race results:")
    from persistence_sqlite import PersistenceSQLite as _PS
    db = _PS()
    for r in results:
        d = db.get_driver(r.driver_id)
        print(f"{r.position}. {d.name} - {r.time_seconds:.2f}s")


if __name__ == "__main__":
    main()
