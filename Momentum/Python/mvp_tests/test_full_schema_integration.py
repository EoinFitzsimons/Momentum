from services.persistence_sqlite import PersistenceSQLite
from sim_simple import simulate_race


def test_monotonic_raw_speed_effect():
    db = PersistenceSQLite(":memory:")
    db.ensure_schema()
    db.seed_sample_data()

    drivers = db.list_drivers()
    track = db.get_track(1)
    assert track is not None

    # Run with seeded RNG
    results = simulate_race(drivers, track, seed=42)
    # winner should be the driver with highest raw_speed (A. Driver id=1)
    winner_id = results[0].driver_id
    assert winner_id == 1

    # Now boost driver 3's raw_speed to be the highest
    cur = db.conn.cursor()
    cur.execute("UPDATE drivers SET raw_speed = ? WHERE id = ?", (99.0, 3))
    db.conn.commit()

    drivers2 = db.list_drivers()
    results2 = simulate_race(drivers2, track, seed=42)
    # With higher raw_speed driver 3 should win now
    assert results2[0].driver_id == 3


def test_deterministic_with_seed():
    db = PersistenceSQLite(":memory:")
    db.ensure_schema()
    db.seed_sample_data()
    drivers = db.list_drivers()
    track = db.get_track(1)

    r1 = simulate_race(drivers, track, seed=12345)
    r2 = simulate_race(drivers, track, seed=12345)

    times1 = [getattr(x, 'time_seconds', None) for x in r1]
    times2 = [getattr(x, 'time_seconds', None) for x in r2]
    assert times1 == times2
