from persistence_sqlite import PersistenceSQLite
from sim_simple import simulate_race


def main():
    db = PersistenceSQLite()
    db.ensure_schema()
    db.seed_sample_data()

    drivers = db.list_drivers()
    track = db.get_track(1)
    if not track:
        print("Track not found")
        return

    results = simulate_race(drivers, track, seed=42)
    db.save_race_results(race_id=1, results=results)

    print("Basic race results:")
    for r in results:
        d = db.get_driver(r.driver_id)
        print(f"{r.position}. {d.name} - {r.time_seconds:.2f}s")


if __name__ == "__main__":
    main()
