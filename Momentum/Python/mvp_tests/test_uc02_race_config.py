import os
import importlib.util

# load modules directly by path to avoid package-relative import issues
PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
spec = importlib.util.spec_from_file_location(
    'mvp.persistence_sqlite', os.path.join(
        PKG_ROOT, 'persistence_sqlite.py'))
assert spec is not None and spec.loader is not None, 'Failed to load persistence_sqlite spec'
persistence_sqlite = importlib.util.module_from_spec(spec)
spec.loader.exec_module(persistence_sqlite)
PersistenceSQLite = persistence_sqlite.PersistenceSQLite


def test_seed_and_get_track():
    db = PersistenceSQLite()
    db.ensure_schema()
    db.seed_sample_data()
    t = db.get_track(1)
    assert t is not None
    assert t.name == 'Short Circuit'
