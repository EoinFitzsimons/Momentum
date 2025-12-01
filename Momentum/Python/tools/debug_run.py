from persistence_sqlite import PersistenceSQLite
from sim_simple import simulate_race

if __name__ == '__main__':
    # Default to using the file-backed persistent DB. This will load the
    # first 20 drivers by id from the archive if available. If none are
    # present the script falls back to seeding a demo set.
    db = PersistenceSQLite()
    db.ensure_schema()

    drivers = []
    for did in range(1, 21):
        d = db.get_driver(did)
        if d is not None:
            drivers.append(d)

    if len(drivers) == 0:
        db.seed_sample_data()
        drivers = db.list_drivers()
    track = db.get_track(1)
    print('drivers:', [d.id for d in drivers])
    print('track id:', track.id if track else None)

    events = []
    def cb(e):
        events.append(e)
        print('ev cb:', e)

    results = simulate_race(drivers, track, seed=1, verbose=False, event_callback=cb)
    print('results count', len(results))
    print('events captured', len(events))
    for r in results:
        print('res', r.driver_id, getattr(r, 'time_seconds', None), r.position)
