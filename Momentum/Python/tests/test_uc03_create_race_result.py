from persistence_sqlite import PersistenceSQLite
from sim_simple import simulate_race


def test_simulate_and_save_results():
    db = PersistenceSQLite()
    db.ensure_schema()
    db.seed_sample_data()
    drivers = db.list_drivers()
    track = db.get_track(1)
    results = simulate_race(drivers, track, seed=1)
    assert len(results) == len(drivers)
    db.save_race_results(42, results)
    # basic verification: re-save doesn't crash and ordering is valid
    assert results[0].position == 1
