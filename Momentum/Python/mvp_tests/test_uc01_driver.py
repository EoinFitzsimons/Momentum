import os
import sys
import importlib.util

# load modules directly by path to avoid package-relative import issues
PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
spec = importlib.util.spec_from_file_location('mvp.persistence_sqlite', os.path.join(PKG_ROOT, 'persistence_sqlite.py'))
persistence_sqlite = importlib.util.module_from_spec(spec)
spec.loader.exec_module(persistence_sqlite)
PersistenceSQLite = persistence_sqlite.PersistenceSQLite


def test_seed_and_get_driver():
    db = PersistenceSQLite()
    db.ensure_schema()
    db.seed_sample_data()
    drivers = db.list_drivers()
    assert len(drivers) >= 3
    d = db.get_driver(1)
    assert d is not None
    assert d.name == 'A. Driver'
