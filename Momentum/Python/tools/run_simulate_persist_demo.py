from services.persistence_sqlite import PersistenceSQLite
from services.race_simulation_api import simulate_race


def main():
    db = PersistenceSQLite()
    db.ensure_schema()
    # Ensure there's sample data
    db.seed_sample_data(count=20, force=False)

    drivers = db.list_drivers()
    track = db.get_track(1)
    if not track:
        raise SystemExit("No track found in DB (id=1). Please seed tracks or import circuits.")

    race_id = 9999
    print(f"Running demo race and persisting to race_id={race_id} (this may take a short while)...")

    results = simulate_race(
        drivers=drivers,
        track=track,
        seed=42,
        laps=3,
        race_id=race_id,
        verbose=True,
        db=db
    )

    print("Simulation returned results objects:")
    for r in results[:5]:
        print(r)

    cur = db.conn.cursor()
    cur.execute("SELECT COUNT(1) FROM race_results WHERE race_id = ?", (race_id,))
    cnt = cur.fetchone()[0]
    print(f"Persisted rows for race_id={race_id}: {cnt}")

    cur.execute("SELECT driver_id, position, laps_completed, time_seconds, dnf_reason, status FROM race_results WHERE race_id = ? ORDER BY position", (race_id,))
    rows = cur.fetchall()
    for row in rows:
        print(tuple(row))


if __name__ == '__main__':
    main()
