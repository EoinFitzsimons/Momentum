from persistence_sqlite import PersistenceSQLite


def test_seed_and_get_driver():
    db = PersistenceSQLite()
    db.ensure_schema()
    db.seed_sample_data()
    drivers = db.list_drivers()
    assert len(drivers) >= 3
    d = db.get_driver(1)
    assert d is not None
    assert d.name == 'A. Driver'
