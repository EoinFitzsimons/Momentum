from services.persistence_sqlite import PersistenceSQLite
from sim_simple import simulate_race


def test_telemetry_events_and_determinism():
    db = PersistenceSQLite(":memory:")
    db.ensure_schema()
    db.seed_sample_data()
    drivers = db.list_drivers()
    track = db.get_track(1)

    events = []

    def cb(e):
        # record a reduced view for easier deterministic comparison
        if 'driver_id' in e:
            events.append((e.get('type'), e.get('subtype'), e.get('lap'), e.get('driver_id')))
        else:
            events.append((e.get('type'), None, e.get('lap'), None))

    _ = simulate_race(drivers, track, seed=2025, event_callback=cb)
    seq1 = list(events)

    # run again with same seed and ensure identical event sequence
    events.clear()
    _ = simulate_race(drivers, track, seed=2025, event_callback=cb)
    seq2 = list(events)

    assert seq1 == seq2
    assert len(seq1) > 0

    # ensure race_finished event is present (last event type should be 'race_finished')
    assert seq1[-1][0] == 'race_finished' or seq2[-1][0] == 'race_finished'
