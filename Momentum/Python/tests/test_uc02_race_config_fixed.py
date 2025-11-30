import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from persistence_sqlite import PersistenceSQLite


def test_seed_and_get_track_fixed():
    db = PersistenceSQLite()
    db.ensure_schema()
    db.seed_sample_data()
    t = db.get_track(1)
    assert t is not None
    assert t.name == 'Short Circuit'
