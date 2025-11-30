import os
import sys
import importlib.util

# load modules directly by path to avoid package-relative import issues
PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
spec = importlib.util.spec_from_file_location('mvp.persistence_sqlite', os.path.join(PKG_ROOT, 'persistence_sqlite.py'))
persistence_sqlite = importlib.util.module_from_spec(spec)
spec.loader.exec_module(persistence_sqlite)
PersistenceSQLite = persistence_sqlite.PersistenceSQLite

# load sim_simple by path too
spec2 = importlib.util.spec_from_file_location('mvp.sim_simple', os.path.join(PKG_ROOT, 'sim_simple.py'))
sim_simple = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(sim_simple)
simulate_race = sim_simple.simulate_race


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
