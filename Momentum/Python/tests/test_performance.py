"""Performance and scalability benchmarks for race simulation and database operations."""

from __future__ import annotations

import time
import pytest

from database.database_manager import DatabaseManager
from database.models import Driver
from RaceLogic.base_race_engine import RacingDiscipline
from services.race_simulation_api import simulate_race


@pytest.mark.performance
def test_single_race_simulation_under_threshold(seeded_db):
    """Verify single race simulation completes within 1 second target."""
    track = seeded_db["db"].get_track(seeded_db["track_ids"][0])
    assert track is not None
    drivers = [
        driver
        for driver_id in seeded_db["driver_ids"][:4]
        if (driver := seeded_db["db"].get_driver(driver_id)) is not None
    ]
    assert drivers

    start_time = time.perf_counter()

    results = simulate_race(
        drivers=drivers,
        track=track,
        laps=5,
        seed=42,
    )

    elapsed = time.perf_counter() - start_time

    assert results is not None
    assert len(results) > 0
    assert elapsed < 1.0, f"Single race simulation took {elapsed:.3f}s, expected < 1.0s"


@pytest.mark.performance
def test_batch_race_simulation_performance(seeded_db):
    """Verify batch simulation of 100 races stays under 30 second target."""
    track = seeded_db["db"].get_track(seeded_db["track_ids"][0])
    assert track is not None
    drivers = [
        driver
        for driver_id in seeded_db["driver_ids"][:4]
        if (driver := seeded_db["db"].get_driver(driver_id)) is not None
    ]
    assert drivers

    start_time = time.perf_counter()
    race_count = 100

    for i in range(race_count):
        results = simulate_race(
            drivers=drivers,
            track=track,
            laps=3,
            seed=42 + i,
        )
        assert results is not None

    elapsed = time.perf_counter() - start_time

    assert elapsed < 30.0, f"100 races took {elapsed:.3f}s, expected < 30.0s"
    avg_time = elapsed / race_count
    assert avg_time < 0.3, f"Average race time {avg_time:.3f}s exceeds 0.3s"


@pytest.mark.performance
def test_database_query_performance_driver_retrieval(seeded_db):
    """Verify driver retrieval queries complete within 100ms."""
    db: DatabaseManager = seeded_db["db"]
    driver_ids = seeded_db["driver_ids"]

    start_time = time.perf_counter()

    for driver_id in driver_ids:
        driver = db.get_driver(driver_id)
        assert driver is not None

    elapsed = time.perf_counter() - start_time
    per_query = (elapsed / len(driver_ids)) * 1000  # Convert to milliseconds

    assert elapsed < 0.1, f"Total driver queries took {elapsed:.3f}s, expected < 0.1s"
    assert per_query < 20.0, f"Average query took {per_query:.2f}ms, expected < 20ms"


@pytest.mark.performance
def test_database_query_performance_team_lookup(seeded_db):
    """Verify team lookup queries stay within performance targets."""
    db: DatabaseManager = seeded_db["db"]
    team_ids = seeded_db["team_ids"]

    start_time = time.perf_counter()

    for team_id in team_ids:
        team = db.get_team(team_id)
        assert team is not None

    elapsed = time.perf_counter() - start_time
    per_query = (elapsed / len(team_ids)) * 1000  # Convert to milliseconds

    assert elapsed < 0.1, f"Total team queries took {elapsed:.3f}s, expected < 0.1s"
    assert per_query < 35.0, f"Average query took {per_query:.2f}ms, expected < 35ms"


@pytest.mark.performance
def test_database_bulk_create_performance(seeded_db):
    """Verify bulk driver creation stays within reasonable time bounds."""
    db: DatabaseManager = seeded_db["db"]
    team_ids = seeded_db["team_ids"]

    start_time = time.perf_counter()

    for i in range(50):
        driver = Driver(
            id=0,
            name=f"Perf Test Driver {i}",
            nationality="GBR",
            birth_date="1995-01-01",
            speed=70 + (i % 30),
            racecraft=68 + (i % 30),
            consistency=65 + (i % 30),
            preferred_discipline="SINGLE_SEATER",
            current_team_id=team_ids[i % len(team_ids)],
        )
        db.create_driver(driver)

    elapsed = time.perf_counter() - start_time
    per_insert = (elapsed / 50) * 1000  # Convert to milliseconds

    assert elapsed < 2.0, f"Bulk insert took {elapsed:.3f}s, expected < 2.0s"
    assert per_insert < 40.0, f"Average insert took {per_insert:.2f}ms"


@pytest.mark.slow
@pytest.mark.performance
def test_database_query_consistency_under_load(seeded_db):
    """Verify queries remain consistent under repeated access patterns."""
    db: DatabaseManager = seeded_db["db"]
    driver_id = seeded_db["driver_ids"][0]

    # Retrieve same driver multiple times and verify consistency
    times = []
    for _ in range(100):
        start = time.perf_counter()
        driver = db.get_driver(driver_id)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        assert driver is not None

    avg_time = sum(times) / len(times)
    max_time = max(times)

    # Performance should be relatively consistent (no unexpected spikes)
    assert max_time < 0.05, f"Max query time {max_time:.4f}s exceeds 50ms"
    assert avg_time < 0.02, f"Average query time {avg_time:.4f}s exceeds 20ms"


@pytest.mark.slow
@pytest.mark.performance
def test_race_engine_initialization_performance(seeded_db):
    """Verify race engine initialization completes quickly."""
    from services.race_engine_factory import create_discipline_engine
    from RaceLogic.base_race_engine import RaceContext

    track = seeded_db["db"].get_track(seeded_db["track_ids"][0])
    assert track is not None
    drivers = [
        driver
        for driver_id in seeded_db["driver_ids"][:4]
        if (driver := seeded_db["db"].get_driver(driver_id)) is not None
    ]
    assert drivers
    teams = {
        team_id: seeded_db["db"].get_team(team_id) for team_id in seeded_db["team_ids"]
    }
    teams = {k: v for k, v in teams.items() if v is not None}
    assert teams

    context = RaceContext(
        discipline=RacingDiscipline.SINGLE_SEATER,
        track=track,
        drivers=drivers,
        teams=teams,
        total_laps=5,
    )

    times = []
    for i in range(20):
        start = time.perf_counter()
        engine = create_discipline_engine(context, seed=42 + i)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        assert engine is not None

    avg_time = sum(times) / len(times)
    assert avg_time < 0.05, f"Average engine init {avg_time:.4f}s exceeds 50ms"
