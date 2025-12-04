import os
import sys
import importlib.util

# load modules directly by path to avoid package-relative import issues
PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# Load persistence implementation from services/
spec = importlib.util.spec_from_file_location('services.persistence_sqlite', os.path.join(PKG_ROOT, 'services', 'persistence_sqlite.py'))
persistence_sqlite = importlib.util.module_from_spec(spec)
spec.loader.exec_module(persistence_sqlite)
PersistenceSQLite = persistence_sqlite.PersistenceSQLite

# Load the real-time race engine implementation
spec2 = importlib.util.spec_from_file_location('services.race_simulation_api', os.path.join(PKG_ROOT, 'services', 'race_simulation_api.py'))
sim_api = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(sim_api)
simulate_race = sim_api.simulate_race
# Load Team dataclass for creating minimal teams dict
spec3 = importlib.util.spec_from_file_location('database.models', os.path.join(PKG_ROOT, 'database', 'models.py'))
models_mod = importlib.util.module_from_spec(spec3)
spec3.loader.exec_module(models_mod)
Team = models_mod.Team


def test_simulate_and_save_results():
    db = PersistenceSQLite()
    db.ensure_schema()
    db.seed_sample_data()
    drivers = db.list_drivers()
    track = db.get_track(1)

    # Build a minimal teams dict for the engine (use driver.current_team_id)
    teams = {}
    for d in drivers:
        # Use actual current_team_id (may be None) so engine finds teams correctly
        tid = d.current_team_id
        if tid not in teams:
            teams[tid] = Team(id=tid, name=f"Team {tid}", nationality="UNK", founded_year=2020,
                              discipline="formula", tier="tier2", budget=100.0, headquarters="", team_principal="")

    # Run simulation via the public race simulation API (GUI/backed)
    results = simulate_race(
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

    # The API returns a list of RaceResult-like objects
    assert len(results) == len(drivers)
    # Persist results using persistence layer
    db.save_race_results(42, results)
    # basic verification: first finisher has position 1
    first = results[0]
    pos = getattr(first, 'position', None) if not isinstance(first, dict) else first.get('position')
    assert pos == 1
